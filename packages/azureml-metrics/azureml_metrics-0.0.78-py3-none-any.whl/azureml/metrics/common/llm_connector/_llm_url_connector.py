# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import json
import ssl
import os
import urllib.request

from typing import Optional, List
from azureml.metrics.common.exceptions import ClientException, InvalidUserInputException
from azureml.metrics import constants

logger = logging.getLogger(__name__)


class LLMUrlConnector:
    def __init__(self,
                 llm_params: Optional[dict] = None,
                 llm_api_batch_size: Optional[int] = 20,
                 llm_use_chat_completion_payload : Optional[bool] = False,):
        """
        Initialisation of LLMUrlConnector to connect to LLM through their endpoint

        :param llm_params: Dictionary containing url and api_key for connecting to llm endpoint.
        :param llm_api_batch_size: batch size of input payload for llm endpoint.
        """
        self.llm_params = llm_params
        self.llm_api_batch_size = llm_api_batch_size
        self.llm_use_chat_completion_payload = llm_use_chat_completion_payload
        self.system_prompt = constants.DefaultValues.DEFAULT_SYSTEM_PROMPT

    def get_llm_prediction(self, prompt_list: list) -> List[str]:
        """
        Get prediction from LLM endpoint.

        :param prompt_list: constructed prompt for generating GPT similarity.
        :param llm_params: Dictionary containing credentials for llm endpoint.
        """
        results = []

        # updating the deployment_id if it's not set in openai_params
        if isinstance(self.llm_params, dict):
            max_new_tokens = self.llm_params.get("max_new_tokens", 2)
            # default value of 0 is used inorder to generate a deterministic result
            temperature = self.llm_params.get("temperature", 0.01)
            return_full_text = self.llm_params.get("return_full_text", False)

            llm_url = self.llm_params.get("llm_url", None)
            llm_api_key = self.llm_params.get("llm_api_key", None)
            azureml_model_deployment = self.llm_params.get("azureml_model_deployment", "default")
        else:
            logger.warning("LLM related metrics need llm_params in a dictionary.")
            return results

        for index in range(0, len(prompt_list), self.llm_api_batch_size):
            prompt_batch = list(prompt_list[index: index + self.llm_api_batch_size])

            if self.llm_use_chat_completion_payload is True:
                updated_prompt_batch = []
                for user_prompt in prompt_batch:
                    messages = [{"role": "system", "content": self.system_prompt},
                                {"role": "user", "content": user_prompt}]
                    updated_prompt_batch.append(messages)
            else:
                updated_prompt_batch = prompt_batch

            input_payload_type = self.llm_params.get("input_payload_type", "azure_maap")
            if input_payload_type == "azure_maap":
                data = {
                    "input_data": {
                        "input_string": updated_prompt_batch,
                        "parameters": {
                            "max_new_tokens": max_new_tokens,
                            "temperature": temperature,
                            "return_full_text": return_full_text,
                        }
                    }
                }
            elif self.llm_use_chat_completion_payload is False:
                # Azure MaaS - Text Generation
                data = {
                    "prompt": updated_prompt_batch,
                    "max_tokens": max_new_tokens,
                    "temperature": temperature,
                    "return_full_text": return_full_text,
                }
            else:
                # Azure MaaS - Chat Completion
                data = {
                    "messages": updated_prompt_batch,
                    "max_tokens": max_new_tokens,
                    "temperature": temperature,
                    "return_full_text": return_full_text,
                }

            # start and end index of batch to be used in case of exception
            batch_start_index = index
            batch_end_index = min(len(prompt_list), index + self.llm_api_batch_size)

            try:
                api_output = LLMUrlConnector.get_llm_completion(data, llm_url, llm_api_key,
                                                                azureml_model_deployment)
            except Exception as e:
                api_output = []
                predicted_result = e.__class__.__name__
                logger.warning("Could not compute metric because of the following exception : " + str(e))
                for row_index in range(batch_start_index, batch_end_index):
                    api_output.append(predicted_result)

            results.extend(api_output)

        return results

    @staticmethod
    def get_llm_completion(data, llm_url, llm_api_key, azureml_model_deployment):

        def allowSelfSignedHttps(allowed):
            # bypass the server certificate verification on client side
            if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context',
                                                                                   None):
                ssl._create_default_https_context = ssl._create_unverified_context

        allowSelfSignedHttps(True)

        body = str.encode(json.dumps(data))

        if llm_url is None or llm_api_key is None:
            safe_message = "A key should be provided to invoke the LLM endpoint."
            raise InvalidUserInputException(safe_message, target="llm_url_connector",
                                            reference_code="llm_url_connector.get_llm_completion",
                                            safe_message=safe_message)

        # The azureml-model-deployment header will force the request to go to a specific deployment.
        # Remove this header to have the request observe the endpoint traffic rules
        headers = {'Content-Type': 'application/json', 'Authorization': ('Bearer ' + llm_api_key),
                   'azureml-model-deployment': azureml_model_deployment}

        req = urllib.request.Request(llm_url, body, headers)

        try:
            response = urllib.request.urlopen(req)
            result_obj = response.read()
            result = json.loads(result_obj)
            if len(result) == 1:
                llm_scores = [score.strip().lower() for score in result[0].values()]
                return llm_scores
            else:
                safe_message = "Not able to retrieve score for corresponding LLM based metric"
                raise ClientException(safe_message, target="llm_url_connector",
                                      reference_code="llm_url_connector.get_llm_completion",
                                      safe_message=safe_message)
        except urllib.error.HTTPError as error:
            logger.warning("The request to LLM model failed with status code: " + str(error.code))
            logger.warning(error.info())
            logger.warning(error.read().decode("utf8", 'ignore'))
            safe_message = "Not able to obtain http response from provided LLM api details."
            raise ClientException(safe_message, target="llm_url_connector",
                                  reference_code="llm_url_connector.get_llm_completion",
                                  safe_message=safe_message)
