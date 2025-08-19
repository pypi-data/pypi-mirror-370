# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import json
import ssl
import os

from typing import List
from azureml.metrics.common.exceptions import MissingDependencies, InvalidUserInputException, \
    ClientException

try:
    import urllib.request

    logging.getLogger("urllib3").setLevel(logging.ERROR)

except ImportError:
    safe_message = "Relevant GPT Star metrics packages are not available. " \
                   "Please run pip install azureml-metrics[prompt-flow]"
    raise MissingDependencies(
        safe_message, safe_message=safe_message
    )

logger = logging.getLogger(__name__)


def get_llm_prediction(prompt_list: list, llm_params: dict, llm_batch_size: int = 20) -> List[str]:
    """
    Get prediction from LLM endpoint.

    :param prompt_list: constructed prompt for generating GPT similarity.
    :param llm_params: Dictionary containing credentials for llm endpoint.
    :param llm_batch_size: number of prompts to be batched in one LLM call
    """
    results = []

    # updating the deployment_id if it's not set in openai_params
    if isinstance(llm_params, dict):
        max_new_tokens = llm_params.get("max_new_tokens", 2)
        # default value of 0 is used inorder to generate a deterministic result
        temperature = llm_params.get("temperature", 0.01)
        return_full_text = llm_params.get("return_full_text", False)

        llm_url = llm_params.get("llm_url", None)
        llm_api_key = llm_params.get("llm_api_key", None)
    else:
        logger.warning("LLM related metrics need llm_params in a dictionary.")
        return results

    for index in range(0, len(prompt_list), llm_batch_size):
        prompt_batch = list(prompt_list[index: index + llm_batch_size])

        data = {
            "input_data": {
                "input_string": prompt_batch,
                "parameters": {
                    "max_new_tokens": max_new_tokens,
                    "temperature": temperature,
                    "return_full_text": return_full_text,
                }
            }
        }

        # start and end index of batch to be used in case of exception
        batch_start_index = index
        batch_end_index = min(len(prompt_list), index + llm_batch_size)

        try:
            api_output = get_llm_completion(data, llm_url, llm_api_key)
        except Exception as e:
            api_output = []
            predicted_result = e.__class__.__name__
            logger.warning("Could not compute metric because of the following exception : " + str(e))
            for row_index in range(batch_start_index, batch_end_index):
                api_output.append(predicted_result)

        results.extend(api_output)

    return results


def get_llm_completion(data, llm_url, llm_api_key):
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
                                        reference_code="_similarity_utils.get_llm_completion",
                                        safe_message=safe_message)

    # The azureml-model-deployment header will force the request to go to a specific deployment.
    # Remove this header to have the request observe the endpoint traffic rules
    headers = {'Content-Type': 'application/json', 'Authorization': ('Bearer ' + llm_api_key),
               'azureml-model-deployment': 'default'}

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
                                  reference_code="_similarity_utils.get_llm_completion",
                                  safe_message=safe_message)
    except urllib.error.HTTPError as error:
        logger.warning("The request to llm model failed with status code: " + str(error.code))
        logger.warning(error.info())
        logger.warning(error.read().decode("utf8", 'ignore'))
        safe_message = "Not able to obtain http response from provided LLM api details."
        raise ClientException(safe_message, target="llm_url_connector",
                              reference_code="_similarity_utils.get_llm_completion",
                              safe_message=safe_message)


def is_chat_completion_api(model):
    """
    Check if we need openai chat completion or completion API for inference.

    :param model : model name to perform openai inference call.
    :return: True if we need to use chat-completion API.
    """
    # TODO : check if we need to update model_ids based on different endpoints.
    return model.startswith("gpt-35-turbo") or \
        model.startswith("gpt-3.5-turbo") or \
        model.startswith("gpt4") or \
        model.startswith("gpt-4")
