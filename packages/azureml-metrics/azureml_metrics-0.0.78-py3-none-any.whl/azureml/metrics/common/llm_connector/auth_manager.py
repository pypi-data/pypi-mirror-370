# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Auth manager for Key-based, KeyVault-based and AAD-based auth methods

Classes:
    KeyAuthManager: Auth manager for Key-based auth methods
    KeyVaultAuthManager: Auth manager for KeyVault-based auth methods
    AADAuthManager: Auth manager for AAD-based auth methods
    TokenScope: Enum for token scopes
"""
import os
import time
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Union, Any

from azureml.metrics.common.exceptions import MissingDependencies

try:
    from azure.identity import ManagedIdentityCredential, AzureCliCredential
    from azure.keyvault.secrets import SecretClient

except ImportError:
    safe_message = "Relevant RAG Evaluation packages are not available. " \
                   "Please run pip install azureml-metrics[rag-evaluation]"
    raise MissingDependencies(
        safe_message, safe_message=safe_message
    )

AZURE_TOKEN_REFRESH_INTERVAL = 600  # seconds

logger = logging.getLogger(__name__)


class TokenScope(Enum):
    """Enum for token scopes

    Attributes:
        AZURE_ENDPOINT: Azure endpoint - https://ml.azure.com
        AZURE_OPENAI_API: Azure OpenAI API - https://cognitiveservices.azure.com
    """
    AZURE_ENDPOINT = "https://ml.azure.com"
    AZURE_OPENAI_API = "https://cognitiveservices.azure.com"
    MIR_ENDPOINT = "https://ml.azure.com/.default"


class AuthHeaderType(Enum):
    BEARER = " Bearer"
    API_KEY = "api-key"


class AuthManager(ABC):

    @abstractmethod
    def get_auth_header(self) -> Dict[str, Any]:
        """Get auth header for the auth method"""


class KeyAuthManager(AuthManager):
    """Auth manager for Key-based auth methods

    Attributes:
        api_key (str): API key
    """

    def __init__(self, key):
        self.api_key = key

    def get_auth_header(self) -> Dict[str, Any]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "ocp-apim-subscription-key": self.api_key,
            "api-key": self.api_key,
        }


class AADAuthManager(AuthManager, ABC):
    """Abstract class for AAD Auth Manager

    Attributes:
        credential (Union[AzureCliCredential, ManagedIdentityCredential]): Credential for AAD
        token (str): Token for AAD
        auth_header (AuthHeaderType): Auth header type
        require_ocp_subscription_key (bool): Whether to require ocp subscription key
    """

    def __init__(self, auth_header: AuthHeaderType, require_ocp_subscription_key: bool):
        self.credential = self.get_aad_credential()
        self.token = None
        self.auth_header = auth_header
        self.require_ocp_subscription_key = require_ocp_subscription_key

    def get_aad_credential(self) -> Union[AzureCliCredential, ManagedIdentityCredential]:
        identity_client_id = os.environ.get("DEFAULT_IDENTITY_CLIENT_ID", None)
        if identity_client_id is not None:
            logger.info("Using DEFAULT_IDENTITY_CLIENT_ID")
            credential = ManagedIdentityCredential(
                client_id=identity_client_id)
        else:
            # Good for local testing.
            logger.info(
                "Environment variable DEFAULT_IDENTITY_CLIENT_ID is not set, using AzureCliCredential")
            credential = AzureCliCredential()
        return credential

    def get_auth_header(self) -> Dict[str, Any]:
        token = self.get_token()
        headers = {
            "Content-Type": "application/json",
        }
        if self.auth_header == AuthHeaderType.BEARER:
            headers["Authorization"] = f"Bearer {token}"
        elif self.auth_header == AuthHeaderType.API_KEY:
            headers["api-key"] = token

        if self.require_ocp_subscription_key:
            headers["ocp-apim-subscription-key"] = token

        return headers

    @abstractmethod
    def get_token(self) -> str:
        """Get token/key for the specifed auth method"""


class KeyVaultAuthManager(AADAuthManager):

    def __init__(self, kv_url: str, secret_name: str, require_ocp_subscription_key: bool = True):
        """
        Auth manager for KeyVault-based auth methods

        :param kv_url: Key Vault URL
        :param secret_name: Secret name
        :param require_ocp_subscription_key: Whether to require ocp subscription key
        """

        super().__init__(AuthHeaderType.API_KEY, require_ocp_subscription_key)

        # Get Open AI API key from Key Vault and set it
        secret_client = SecretClient(
            vault_url=kv_url, credential=self.credential)
        openai_api_secret = secret_client.get_secret(secret_name)
        logger.info(
            "Retrieved API key: {} from Azure Key Vault".format(openai_api_secret.name))
        self.token = openai_api_secret.value

    def get_token(self):
        return self.token


class ManagedIdentityAuthManager(AADAuthManager):

    def __init__(self, token_scope: TokenScope = TokenScope.AZURE_ENDPOINT,
                 require_ocp_subscription_key: bool = True):
        """
        Auth manager for AAD-based auth methods

        :param token_scope: Token scope
        :param require_ocp_subscription_key: Whether to require ocp subscription key
        """
        super().__init__(AuthHeaderType.BEARER, require_ocp_subscription_key)
        self.token_scope = token_scope
        self.last_refresh_time = 0

    def get_token(self):
        if self.token is None or \
                time.time() - self.last_refresh_time > AZURE_TOKEN_REFRESH_INTERVAL:
            self.last_refresh_time = time.time()
            self.token = self.credential.get_token(
                self.token_scope.value).token
            logger.info("Refreshed Azure endpoint token.")
        return self.token


class MIRModelType(Enum):
    GPT_35_Turbo = "main"
    GPT_4 = "gpt4"


class MIRAuthManager(ManagedIdentityAuthManager):

    def __init__(self, model_type: MIRModelType, use_chat_completion: bool = False):
        super().__init__(TokenScope.MIR_ENDPOINT)
        self.model_type = model_type
        self.use_chat_completion = use_chat_completion

    def get_auth_header(self) -> Dict[str, Any]:
        token = self.get_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "azureml-model-deployment": self.model_type.value
        }

        if self.use_chat_completion:
            if self.model_type == MIRModelType.GPT_35_Turbo:
                extra_headers = {
                    "Openai-Internal-AllowedSpecialTokens": "<|im_start|>,<|im_sep|>,<|im_end|>",
                    "Openai-Internal-AllowedOutputSpecialTokens": "<|im_start|>,<|im_sep|>,<|im_end|>",
                    "Openai-Internal-AllowChatCompletion": "1",
                    "Openai-Internal-HarmonyVersion": "harmony_v3",
                }
            else:
                extra_headers = {
                    "Openai-Internal-AllowedSpecialTokens": "1",
                    "Openai-Internal-AllowedOutputSpecialTokens": "1",
                    "Openai-Internal-AllowChatCompletion": "1",
                    "Openai-Internal-HarmonyVersion": "harmony_v4.0_no_system_message_content_type",
                }
            headers = {**headers, **extra_headers}
        return headers
