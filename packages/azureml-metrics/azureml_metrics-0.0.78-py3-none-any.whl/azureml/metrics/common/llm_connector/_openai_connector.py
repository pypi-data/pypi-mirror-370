# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import copy
import random
import logging
import time

import numpy as np

from typing import List, Optional
from azureml.metrics.common.exceptions import MissingDependencies, InvalidUserInputException
from azureml.metrics.common.llm_connector.llm_utils import LLMState
from azureml.metrics import constants

try:
    import openai
    from azureml.metrics.common.llm_connector.async_utils import get_async_completion, \
        get_async_chat_completion, gather_with_concurrency

    from azureml.metrics.common.llm_connector.llm_utils import async_retry_with_exponential_backoff

    if openai.__version__ < "1.0.0":
        from openai.error import RateLimitError
        # setting the logging level for openai library
        openai.util.logger.setLevel(logging.ERROR)
    else:
        from openai import RateLimitError
        os.environ["OPENAI_LOG"] = "error"

except ImportError:
    safe_message = "Relevant GPT Star metrics packages are not available. " \
                   "Please run pip install azureml-metrics[prompt-flow]"
    raise MissingDependencies(
        safe_message, safe_message=safe_message
    )

logger = logging.getLogger(__name__)


class OpenAIConnector:
    """class to handle connection with OpenAI, including retry, batching, parsing, etc."""
    def __init__(self,
                 openai_params: dict,
                 openai_api_batch_size: int = 20,
                 # setting the value of using chat completion api to True
                 use_chat_completion_api: bool = None,
                 max_concurrent_requests: int = constants.ConcurrencyConstants.MAX_CONCURRENT_REQUESTS,
                 llm_state: Optional[LLMState] = None,
                 compute_custom_metric: Optional[bool] = False,
                 use_openai_endpoint: Optional[bool] = False,):
        """
        Initialize the instance of OpenAIConnector.

        :param openai_params (dict): A dictionary containing the openai API credentials and other parameters.
        :param openai_api_batch_size (int): The batch size for openai API calls (applicable only when
        completion API is supported).
        :param use_chat_completion_api (bool): A flag to indicate whether to use chat completion API.
        :param max_concurrent_requests (int): The maximum number of concurrent requests to be made to openai API.
        :param llm_state (LLMState): The instance of LLMState to be used for logging and other purposes.
        :param compute_custom_metric (bool): A flag to indicate whether to compute custom metric.
        :param use_openai_endpoint (bool): A flag to indicate whether to use openai endpoint.

        :raises InvalidUserInputException: If openai_params is not a dictionary.
        """
        self.openai_params = openai_params
        self.openai_api_batch_size = openai_api_batch_size
        self.use_chat_completion_api = use_chat_completion_api
        self.llm_state = llm_state
        self.compute_custom_metric = compute_custom_metric

        self.openai_client = None
        self.openai_v1_kwargs = None
        self.max_concurrent_requests = max_concurrent_requests
        self.use_openai_endpoint = use_openai_endpoint
        # process the openai_params to compute GPT star metrics
        self.process_openai_params()

    def process_openai_params(self):
        """
        Process the parameters in openai_params dict.
        """
        config_temperature = 0  # inorder to generate a deterministic result

        if self.compute_custom_metric is True:
            config_max_tokens = constants.DefaultValues.DEFAULT_MAX_TOKENS_CUSTOM_METRIC
        else:
            # we need 1 token to produce the numerical output of score
            config_max_tokens = 1

        default_model = constants.DefaultValues.DEFAULT_GPT_MODEL
        model = default_model
        # updating the deployment_id if it's not set in openai_params
        if isinstance(self.openai_params, dict):
            if "max_tokens" not in self.openai_params.keys():
                self.openai_params["max_tokens"] = config_max_tokens
            if "temperature" not in self.openai_params.keys():
                self.openai_params["temperature"] = config_temperature

            if "api_key" not in self.openai_params.keys():
                if self.use_openai_endpoint:
                    self.openai_params["api_key"] = os.getenv("OPENAI_API_KEY", None)
                else:
                    self.openai_params["api_key"] = os.getenv("AZURE_OPENAI_KEY", None)

            if openai.__version__ < "1.0.0":
                if "deployment_id" not in self.openai_params.keys() and self.use_openai_endpoint is False:
                    self.openai_params["deployment_id"] = default_model
                    logger.info("Using {} for openai deployment_id as "
                                "deployment_id is not provided in openai_params".format(default_model))

                if "azure_endpoint" in self.openai_params.keys() or "base_url" in self.openai_params.keys():
                    self.openai_params["api_base"] = self.openai_params.pop("azure_endpoint",
                                                                            self.openai_params.pop("base_url", None))
            else:
                self.migrate_openai_params(default_model)

            # retrieving the model metric_name or deployment metric_name when model is None
            model = self.openai_params.get("model", self.openai_params.get("deployment_id", default_model))
        else:
            logger.info("GPT related metrics need openai_params in a dictionary.")

        # chooses between openai completion vs chat completion API
        # can be overriden using use_chat_completion_api parameter
        self.choose_openai_api(model)

    def choose_openai_api(self, model):
        if self.use_chat_completion_api is None:
            if OpenAIConnector.is_chat_completion_api(model):
                self.use_chat_completion_api = True
                # currently, batching is not supported in chat completion api.
                # so, setting the batch size to 1
                self.openai_api_batch_size = 1
            else:
                self.use_chat_completion_api = False
        elif self.use_chat_completion_api is True:
            # currently, batching is not supported in chat completion api.
            # so, setting the batch size to 1
            self.openai_api_batch_size = 1

    def migrate_openai_params(self, default_model):
        """
            Migrate openai params to support the latest version of openai package.
        """
        if "deployment_id" in self.openai_params.keys():
            self.openai_params["model"] = self.openai_params.pop("deployment_id", None)
        elif "model" not in self.openai_params.keys():
            self.openai_params["model"] = default_model
        if "api_base" in self.openai_params.keys():
            self.openai_params["azure_endpoint"] = self.openai_params.pop("api_base", None)
        if "api_type" in self.openai_params.keys():
            self.openai_params.pop("api_type")

        self.instantiate_openai_client()

    def instantiate_openai_client(self):
        self.openai_v1_kwargs = copy.deepcopy(self.openai_params)
        try:
            if self.use_openai_endpoint is True:
                from openai import OpenAI

                self.openai_client = OpenAI(
                    api_key=self.openai_v1_kwargs.pop("api_key", os.getenv("OPENAI_API_KEY"))
                )
            else:
                from openai import AzureOpenAI

                self.openai_client = AzureOpenAI(
                    azure_endpoint=self.openai_v1_kwargs.pop("azure_endpoint",
                                                             self.openai_params.pop("base_url",
                                                                                    os.getenv(
                                                                                        "AZURE_OPENAI_ENDPOINT"))),
                    api_key=self.openai_v1_kwargs.pop("api_key", os.getenv("AZURE_OPENAI_KEY")),
                    api_version=self.openai_v1_kwargs.pop("api_version", os.getenv("AZURE_OPENAI_VERSION")),
                )

            if "seed" not in self.openai_v1_kwargs:
                self.openai_v1_kwargs["seed"] = constants.DefaultValues.DEFAULT_OPENAI_SEED

            if "best_of" in self.openai_v1_kwargs:
                del self.openai_v1_kwargs["best_of"]

        except Exception:
            safe_message = ("Not able to initialize openAI client. Please verify the credentials of openai_params,"
                            " if using openAI endpoint, please set use_openai_endpoint to True.")
            raise InvalidUserInputException(safe_message, safe_message=safe_message)

    def compute_gpt_based_metrics(self, prompt_list, system_prompt=None):
        prompt_batch_list = self.get_prompt_batches(prompt_list)

        if self.openai_params is None or not isinstance(self.openai_params, dict):
            safe_message = "Please set openai_params as dictionary having openai API credentials."
            raise InvalidUserInputException(safe_message, safe_message=safe_message)

        predictions = [float(np.nan) for batch in prompt_batch_list for _ in batch]
        results_map = []
        if self.use_chat_completion_api is True:
            openai_params_chat_api = copy.deepcopy(self.openai_params)

            # use default system prompt in case if system_prompt is None
            if system_prompt is None:
                system_prompt = constants.DefaultValues.DEFAULT_SYSTEM_PROMPT

            for index, prompt_batch in enumerate(prompt_batch_list):
                # batching is not supported in chat completion api.
                # so, we set the batch size to 1 and access the first element.
                user_prompt = prompt_batch[0]
                messages = [{"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}]
                openai_params_chat_api['messages'] = messages

                if 'best_of' in openai_params_chat_api:
                    del openai_params_chat_api['best_of']

                result = self.get_chat_completion(index, **openai_params_chat_api)
                results_map.append(result)

        else:
            openai_params_completion_api = copy.deepcopy(self.openai_params)
            for index, prompt_batch in enumerate(prompt_batch_list):
                openai_params_completion_api['prompt'] = prompt_batch
                result = self.get_completion(index, **openai_params_completion_api)
                results_map.append(result)

        self.post_process_results(predictions, results_map)
        return predictions

    def get_chat_completion(self, index, **kwargs):
        """Making a call to openai chatcompletion API"""
        # add random delay between 10 ms to 100 ms
        delay = random.uniform(0.01, 0.1)
        time.sleep(delay)

        if openai.__version__ < "1.0.0":
            chat_completion_resp = openai.ChatCompletion.create(**kwargs)
        else:
            chat_completion_resp = self.openai_client.chat.completions.create(
                messages=kwargs.get("messages"),
                **self.openai_v1_kwargs,
            )

        return {index: chat_completion_resp}

    def get_completion(self, index, **kwargs):
        """Making a call to openai chatcompletion API"""
        # add random delay between 10 ms to 100 ms
        delay = random.uniform(0.01, 0.1)
        time.sleep(delay)

        if openai.__version__ < "1.0.0":
            completion_resp = openai.Completion.create(**kwargs)
        else:
            completion_resp = self.openai_client.completions.create(
                prompt=kwargs.get("prompt"),
                **self.openai_v1_kwargs,
            )

        return {index: completion_resp}

    def post_process_results(self, predictions, results_map):
        for result in results_map:
            index = list(result.keys())[0]
            api_output = result[index]
            if self.use_chat_completion_api is True:
                if openai.__version__ < "1.0.0":
                    result = api_output['choices'][0]['message']['content']
                else:
                    result = api_output.choices[0].message.content
                predictions[index] = result
            else:
                if openai.__version__ < "1.0.0":
                    batch_result = [resp["text"] for resp in api_output["choices"]]
                else:
                    batch_result = [resp.text for resp in api_output.choices]
                start_index = index * self.openai_api_batch_size
                end_index = start_index + len(batch_result)
                predictions[start_index: end_index] = batch_result

    def get_prompt_batches(self, prompt_list) -> List[List[str]]:
        """
        Divide prompt_batch_list into batches where each batch is a list of prompts with a size of
        openai_api_batch_size.

        :param prompt_list: A list of prompts to be divided into batches.
        :type prompt_list: list
        :return: A list of batches where each batch is a list of prompts with a size of openai_api_batch_size.
        :rtype: list
        """
        prompt_batches = []
        for index in range(0, len(prompt_list), self.openai_api_batch_size):
            prompt_batches.append(prompt_list[index:index + self.openai_api_batch_size])
        return prompt_batches

    @async_retry_with_exponential_backoff(max_retries=constants.ChatCompletionConstants.MAX_RETRIES,
                                          delay_factor=constants.ChatCompletionConstants.DELAY_FACTOR,
                                          max_delay=constants.ChatCompletionConstants.MAX_DELAY)
    async def get_async_prediction(self, prompt_batch_list: List[List[str]], system_prompt: str = None):
        """
        Get the prediction from openai API for the given prompt_batch_list.

        if use_chat_completion_api is True, then we use openai async chat completion API.
        else we use openai completion API.
        """
        if self.openai_params is None or not isinstance(self.openai_params, dict):
            safe_message = "Please set openai_params as dictionary having openai API credentials."
            raise InvalidUserInputException(safe_message, safe_message=safe_message)

        predictions = [float(np.nan) for batch in prompt_batch_list for _ in batch]
        coroutines = []

        if self.use_chat_completion_api is True:
            openai_params_chat_api = copy.deepcopy(self.openai_params)

            # use default system prompt in case if system_prompt is None
            if system_prompt is None:
                system_prompt = constants.DefaultValues.DEFAULT_SYSTEM_PROMPT

            for index, prompt_batch in enumerate(prompt_batch_list):
                # batching is not supported in chat completion api.
                # so, we set the batch size to 1 and access the first element.
                user_prompt = prompt_batch[0]
                messages = [{"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}]
                openai_params_chat_api['messages'] = messages

                if 'best_of' in openai_params_chat_api:
                    del openai_params_chat_api['best_of']

                coroutine = get_async_chat_completion(index, self.openai_client,
                                                      self.openai_v1_kwargs,
                                                      **openai_params_chat_api)
                coroutines.append(coroutine)

        else:
            openai_params_completion_api = copy.deepcopy(self.openai_params)
            for index, prompt_batch in enumerate(prompt_batch_list):
                openai_params_completion_api['prompt'] = prompt_batch
                coroutine = get_async_completion(index, self.openai_client,
                                                 self.openai_v1_kwargs,
                                                 **openai_params_completion_api)
                coroutines.append(coroutine)

        results_map = []
        try:
            results_map = await gather_with_concurrency(self.max_concurrent_requests, *coroutines)
        except RateLimitError:
            self.max_concurrent_requests = max(self.max_concurrent_requests - 1, 1)
            logger.warning("Rate limit error occurred. Reducing the max concurrent requests to {}"
                           .format(self.max_concurrent_requests))
            raise
        except Exception as e:
            logger.warning("Computing gpt based metrics failed with the exception : {}".format(str(e)))
            raise
        finally:
            await self.async_post_process_results(predictions, results_map)

        return predictions

    async def async_post_process_results(self, predictions, results_map):
        for result in results_map:
            index = list(result.keys())[0]
            api_output = result[index]
            if self.use_chat_completion_api is True:
                if openai.__version__ < "1.0.0":
                    if isinstance(api_output, str):
                        result = api_output
                    else:
                        result = api_output['choices'][0]['message']['content']
                else:
                    if isinstance(api_output, str):
                        result = api_output
                    else:
                        result = api_output.choices[0].message.content
                predictions[index] = result
            else:
                if openai.__version__ < "1.0.0":
                    batch_result = [resp["text"] for resp in api_output["choices"]]
                else:
                    batch_result = [resp.text for resp in api_output.choices]
                start_index = index * self.openai_api_batch_size
                end_index = start_index + len(batch_result)
                predictions[start_index: end_index] = batch_result

    @staticmethod
    def is_chat_completion_api(model):
        """
        Check if we need openai chat completion or completion API for inference.

        :param model : model metric_name to perform openai inference call.
        :return: True if we need to use chat-completion API.
        """
        return model.startswith("gpt-35-turbo") or model.startswith("gpt-3.5-turbo")\
            or model.startswith("gpt4") or model.startswith("gpt-4")
