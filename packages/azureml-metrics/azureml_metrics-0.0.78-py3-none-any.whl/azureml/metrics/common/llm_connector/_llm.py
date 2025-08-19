# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module to encapsulate large language models for generation

Classes:
    LLM: Base class for large language models for generation
    GPTEndpoint: GPT endpoint for generation
    StreamingGPTEndpoint: GPT endpoint with streaming support
"""

from abc import ABC, abstractmethod
import dataclasses
import json
import logging
from typing import (
    Any,
    AsyncIterable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union
)

from azureml.metrics.common.exceptions import (
    OAIClientException, MissingDependencies, MetricsException, MetricsSystemException
)

try:
    import aiohttp
    import requests
    from .auth_manager import AuthManager, KeyAuthManager, ManagedIdentityAuthManager
    from .llm_utils import LLMState, handle_finish_reason, OAIGenerationConfig
    from .http_connection_utils import async_post_with_session, sync_post
except ImportError:
    safe_message = "Relevant RAG Evaluation packages are not available. " \
                   "Please run pip install azureml-metrics[rag-evaluation]"
    raise MissingDependencies(
        safe_message, safe_message=safe_message
    )


logger = logging.getLogger(__name__)


T = TypeVar("T", AsyncIterable, Iterable, str, List, covariant=True)


class LLM(ABC, Generic[T]):
    """class to encapsulate llm models.
    Implement LLM to support generation using local or endpoint based large language models"""

    use_chat_completion = False

    @abstractmethod
    def get_config(self) -> OAIGenerationConfig:
        """Return the config being used"""

    @abstractmethod
    def set_llm_state(self, llm_state: LLMState) -> None:
        """Set the LLMState to be shared with calling service"""

    def set_timeout(self, timeout_sec: float):
        """Set the timeout for async calls"""
        pass

    @abstractmethod
    def generate(self, prompt: Union[str, List]) -> T:
        """Use a llm to complete a prompt response"""

    @abstractmethod
    async def async_generate(self, prompt: Union[str, List]) -> T:
        """Async: Use a llm to complete a prompt response"""

    @abstractmethod
    def update_stop_string(self, stop_strings: List[str]) -> None:
        """Update stop string based on template and prompt crafter"""


MAX_STOP_TOKENS = 4


class StreamingGPTEndpoint(LLM[Iterable[str]]):
    """GPT endpoint for streaming
    """

    def set_llm_state(self, llm_state: LLMState) -> None:
        self.llm_state = llm_state

    def set_timeout(self, timeout_sec: float):
        raise MetricsException("Streaming endpoint does not support timeout")

    def get_config(self) -> OAIGenerationConfig:
        return self.oai_config

    def __init__(self, api_key: Optional[str], api_url: str, oai_config: OAIGenerationConfig,
                 auth_manager: Optional[AuthManager] = None,
                 llm_state: Optional[LLMState] = None,
                 use_chat_completion: Optional[bool] = None
                 ):
        """

        :param api_key: key for accessing key-based auth endpoint for chatgpt
        :param api_url: url hosting the chatgpt model
        :param stop: List of stop tokens used to stop chatgpt generation
        :param hyperparams: additional hyperparams defined in tpromptlib.prompts.models.llm.OAIConfig
        """
        self.api_key = api_key
        self.api_url = api_url
        self.oai_config = oai_config
        if not auth_manager and not api_key:
            raise MetricsException(
                "Please provide api_key for key based endpoint or AuthManager for KeyVault/Managed Identity")
        if not auth_manager:
            self.auth_manager = KeyAuthManager(api_key)
        else:
            self.auth_manager = auth_manager

        self.llm_state = llm_state
        if use_chat_completion is None:
            self.use_chat_completion = "/chat/completions?" in self.api_url \
                                       and "deployments/chat/completions" not in self.api_url
        else:
            self.use_chat_completion = use_chat_completion

    def _get_streaming_text(self, resp: requests.Response) -> Iterable[str]:
        for line in resp.iter_lines():
            streamed_line = self._process_event_line(line)
            if streamed_line is not None:
                yield streamed_line

    def _process_event_line(self, bytes_line: bytes) -> Optional[str]:
        """Process a line from the streaming response."""
        if not bytes_line:
            return None
        try:
            line = bytes_line.decode("utf-8")
            line = line.split("data:", 1)[1].strip()
            if line == "[DONE]":
                return None
            if self.use_chat_completion:
                response = json.loads(line)

                finish_reason = handle_finish_reason(response, self.llm_state)
                if finish_reason and finish_reason == 'stop':
                    return None
                if "content" in response["choices"][0]["delta"]:
                    data = response["choices"][0]["delta"]["content"]
                else:
                    data = ""
            else:
                response = json.loads(line)
                handle_finish_reason(response, self.llm_state)
                data = response["choices"][0]["text"]
            return data
        except OAIClientException as e:
            raise e
        except Exception as e:
            logger.error(
                "Error processing line: {} with error: {}".format(bytes_line, e))
            return None

    def generate(self, prompt: Union[str, List]) -> Iterable[str]:
        oai_body, oai_headers = get_payload_and_headers(
            prompt=prompt,
            stream=True,
            oai_config=self.oai_config,
            auth_manager=self.auth_manager,
            use_chat_completion=self.use_chat_completion
        )
        resp = requests.post(
            self.api_url, headers=oai_headers, json=oai_body, stream=True
        )
        resp.raise_for_status()
        yield from self._get_streaming_text(resp)

    async def async_generate_helper(self, prompt: Union[str, List]) -> AsyncIterable[str]:
        oai_body, oai_headers = get_payload_and_headers(
            prompt, stream=True, oai_config=self.oai_config, auth_manager=self.auth_manager,
            use_chat_completion=self.use_chat_completion
        )
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url, headers=oai_headers, json=oai_body, raise_for_status=True
                ) as response:
                    response.raise_for_status()
                    event = b""
                    while True:
                        line = await response.content.readline()
                        if not line:
                            break
                        event += line
                        if event.endswith(b"\n\n"):
                            result = self._process_event_line(event)
                            if result is None:
                                break
                            yield result
                            event = b""
        except aiohttp.ClientError as e:
            raise MetricsSystemException("{}\n{}".format(e, self._get_exception_message())) from e

    async def async_generate(self, prompt: Union[str, List]) -> AsyncIterable[str]:
        return self.async_generate_helper(prompt)

    def update_stop_string(self, stop_strings: List[str]) -> None:
        update_stop_string_in_config(
            config=self.oai_config, stop_strings=stop_strings)

    def _get_exception_message(self):
        return "Call to LLM failed. "


class GPTEndpoint(LLM[str]):

    def set_llm_state(self, llm_state: LLMState) -> None:
        self.llm_state = llm_state

    def set_timeout(self, timeout_sec: float):
        self.timeout_secs = timeout_sec

    def get_config(self) -> OAIGenerationConfig:
        return self.config

    def __init__(self, api_key: Optional[str], api_url: str,
                 oai_config: OAIGenerationConfig,
                 auth_manager: Optional[AuthManager] = None,
                 timeout_secs: float = 300,
                 llm_state: Optional[LLMState] = None,
                 use_chat_completion: Optional[bool] = None):
        """GPT endpoint interface

        :param auth_manager: AuthManager object to access keys
        :param api_key: key for accessing key-based auth endpoint for chatgpt
        :param api_url: url hosting the chatgpt model
        :param stop: List of stop tokens used to stop chatgpt generation
        :param hyperparams: additional hyperparams defined in tpromptlib.prompts.models.llm.OAIConfig
        """
        self.config = oai_config
        if not auth_manager and not api_key:
            raise MetricsException(
                "Please provide api_key for key based endpoint or AuthManager for KeyVault/Managed Identity")
        if not auth_manager:
            self.auth_manager = KeyAuthManager(api_key)
        else:
            self.auth_manager = auth_manager
        self.api_url = api_url
        self.timeout_secs = timeout_secs
        self.llm_state = llm_state
        if use_chat_completion is None:
            self.use_chat_completion = "/chat/" in self.api_url
        else:
            self.use_chat_completion = use_chat_completion

    def _extract_response(self, response: Dict[str, Any]) -> str:
        handle_finish_reason(response, self.llm_state)
        if self.use_chat_completion:
            return response["choices"][0]["message"]["content"]
        else:
            return response["choices"][0]["text"]

    def generate(self, prompt: Union[str, List]) -> str:
        """
        Generate output from an endpoint with key-based authentication. Does not support streaming api.
        :param prompt: Input prompt string
        :return: response from chatgpt model
        """
        oai_body, oai_headers = get_payload_and_headers(
            prompt, stream=False, oai_config=self.config, auth_manager=self.auth_manager,
            use_chat_completion=self.use_chat_completion
        )
        resp_data = sync_post(
            url=self.api_url, headers=oai_headers, body=oai_body)

        oai_reply = self._extract_response(resp_data)
        return oai_reply

    async def async_generate(self, prompt: Union[str, List]) -> str:
        oai_body, oai_headers = get_payload_and_headers(
            prompt, stream=False, oai_config=self.config, auth_manager=self.auth_manager,
            use_chat_completion=self.use_chat_completion
        )

        resp_data = await async_post_with_session(
            url=self.api_url, headers=oai_headers, body=oai_body, timeout_sec=self.timeout_secs
        )
        oai_reply = self._extract_response(resp_data)
        return oai_reply

    def update_stop_string(self, stop_strings=List[str]) -> None:
        update_stop_string_in_config(
            config=self.config, stop_strings=stop_strings)


def get_payload_and_headers(
    prompt: Union[str, List], oai_config: OAIGenerationConfig, stream: bool, auth_manager: AuthManager,
        use_chat_completion: bool
) -> Tuple[Dict, Dict]:
    oai_body = dataclasses.asdict(oai_config)
    oai_body.pop("is_streaming")
    oai_body["stream"] = stream
    oai_headers = get_oai_headers(auth_manager)
    if use_chat_completion:
        oai_body['messages'] = prompt
    else:
        oai_body["prompt"] = prompt

    return oai_body, oai_headers


def get_oai_headers(auth_manager: AuthManager) -> Dict[str, str]:

    auth_header = auth_manager.get_auth_header()
    extra_headers = {
        "Openai-Internal-ResampleUnstableTokens": "true",
    }
    return {**auth_header, **extra_headers}


def update_stop_string_in_config(
    config: OAIGenerationConfig, stop_strings: List[str]
) -> None:
    if config.stop is None:
        config.stop = stop_strings
    else:
        for stop in stop_strings:
            if stop not in config.stop:
                config.stop.append(stop)

    if len(config.stop) == 0:
        raise ValueError(
            "Please provide a default stop string in prompt using 'stop_strings' property")

    if len(config.stop) > MAX_STOP_TOKENS:
        raise ValueError(
            """total number of stop strings should be <= {},
             including {} default stop strings""".format(MAX_STOP_TOKENS, len(stop_strings))
        )


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


def setup_llm(api_base: str,
              api_version: str,
              deployment_id: str = "gpt-35-turbo",
              api_key: str = "",
              use_chat_completion: bool = None):
    if api_base != "" and api_version != "":
        if not api_base.endswith("/"):
            api_base = api_base + "/"
        if not api_base.startswith("https://"):
            api_base = "https://" + api_base
        if use_chat_completion:
            llm_url = api_base + "openai/deployments/" + deployment_id + "/chat/completions?api-version=" + api_version
            llm = init_llm(model_url=llm_url, model_key=api_key)
        else:
            llm_url = api_base + "openai/deployments/" + deployment_id + "/completions?api-version=" + api_version
            llm = init_llm(model_url=llm_url, model_key=api_key)
        return llm

    else:
        raise MetricsException("Please provide a valid api_base, api_version and deployment_id")


def init_llm(model_url: str = "", model_key: Optional[str] = ""):
    """
    initialize a LLM for generating response or metrics
    :param model_url: llm model url
    :param model_key: llm model key; leave it empty if using managed identity
    """
    if model_url != "" and model_key != "":
        oai_config = OAIGenerationConfig()
        llm = GPTEndpoint(api_url=model_url, api_key=model_key, oai_config=oai_config)

    elif model_url != "":
        oai_config = OAIGenerationConfig()
        llm = GPTEndpoint(api_url=model_url, api_key=None, oai_config=oai_config,
                          auth_manager=ManagedIdentityAuthManager())

    else:
        raise NotImplementedError

    return llm
