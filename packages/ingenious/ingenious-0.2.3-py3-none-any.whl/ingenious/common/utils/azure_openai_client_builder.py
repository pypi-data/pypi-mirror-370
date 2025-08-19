"""
Azure OpenAI Client Builder Utilities

This module provides builder functions for creating AzureOpenAIChatCompletionClient instances
with different configuration sources and authentication methods.

Builder Functions:
- create_aoai_chat_completion_client_from_config(): Build from ModelConfig object
- create_aoai_chat_completion_client_from_settings(): Build from ModelSettings object
- create_aoai_chat_completion_client_from_params(): Build from direct parameters

These functions handle multiple authentication strategies:
- DEFAULT_CREDENTIAL: Uses Azure DefaultAzureCredential
- TOKEN: Uses API key authentication
- MSI: Uses Managed Identity (system or user-assigned)
- CLIENT_ID_AND_SECRET: Uses Service Principal authentication

Example usage:
    from ingenious.common.utils import create_aoai_chat_completion_client_from_config

    client = create_aoai_chat_completion_client_from_config(model_config)

    # Or with parameters directly:
    client = create_aoai_chat_completion_client_from_params(
        model="gpt-4",
        base_url="https://your-endpoint.openai.azure.com/",
        api_version="2024-02-01",
        authentication_method=AuthenticationMethod.DEFAULT_CREDENTIAL
    )
"""

from typing import Any, Dict, Optional

from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from azure.identity import (
    ClientSecretCredential,
    DefaultAzureCredential,
    ManagedIdentityCredential,
    get_bearer_token_provider,
)

from ingenious.common.enums import AuthenticationMethod
from ingenious.config.models import ModelSettings
from ingenious.models.config import ModelConfig

# Builder Pattern Implementation
# These functions implement the Builder pattern by providing static utility functions
# that construct AzureOpenAIChatCompletionClient objects step-by-step with different
# parameter sources and authentication configurations.


def create_aoai_chat_completion_client_from_config(
    model_config: ModelConfig,
) -> AzureOpenAIChatCompletionClient:
    """
    Builder function to create an AzureOpenAIChatCompletionClient instance from ModelConfig.

    Args:
        model_config (ModelConfig): Configuration object containing model settings

    Returns:
        AzureOpenAIChatCompletionClient: Configured client instance

    Raises:
        ValueError: If required configuration is missing
    """
    return create_aoai_chat_completion_client_from_params(
        model=model_config.model,
        base_url=model_config.base_url,
        api_version=model_config.api_version,
        deployment=model_config.deployment,
        api_key=model_config.api_key,
        authentication_method=model_config.authentication_method,
        client_id=model_config.client_id,
        client_secret=model_config.client_secret,
        tenant_id=model_config.tenant_id,
    )


def create_aoai_chat_completion_client_from_settings(
    model_settings: ModelSettings,
) -> AzureOpenAIChatCompletionClient:
    """
    Builder function to create an AzureOpenAIChatCompletionClient from ModelSettings.

    Args:
        model_settings (ModelSettings): Model settings object containing configuration

    Returns:
        AzureOpenAIChatCompletionClient: Configured client instance

    Raises:
        ValueError: If required configuration is missing
    """
    return create_aoai_chat_completion_client_from_params(
        model=model_settings.model,
        base_url=model_settings.base_url,
        api_version=model_settings.api_version,
        deployment=model_settings.deployment,
        api_key=model_settings.api_key,
        authentication_method=model_settings.authentication_method,
        client_id=model_settings.client_id,
        client_secret=model_settings.client_secret,
        tenant_id=model_settings.tenant_id,
    )


def create_aoai_chat_completion_client_from_params(
    model: str,
    base_url: str,
    api_version: str,
    deployment: Optional[str] = None,
    api_key: Optional[str] = None,
    authentication_method: AuthenticationMethod = AuthenticationMethod.DEFAULT_CREDENTIAL,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> AzureOpenAIChatCompletionClient:
    """
    Builder function to create an AzureOpenAIChatCompletionClient with custom parameters.

    This function is useful when you don't have a ModelConfig object but want to
    create a client with specific parameters.

    Args:
        model (str): Model name (e.g., "gpt-4", "gpt-3.5-turbo")
        base_url (str): Azure OpenAI endpoint URL
        api_version (str): Azure OpenAI API version
        deployment (Optional[str]): Azure deployment name. If None, uses model name
        api_key (Optional[str]): API key for authentication. Required if not using default credential
        authentication_method (str): Authentication mode ("default_credential", "token", "msi", or "client_id_and_secret")
        client_id (Optional[str]): Client ID for MSI or CLIENT_ID_AND_SECRET authentication
        client_secret (Optional[str]): Client secret for CLIENT_ID_AND_SECRET authentication
        tenant_id (Optional[str]): Tenant ID for CLIENT_ID_AND_SECRET authentication (will fallback to AZURE_TENANT_ID env var)

    Returns:
        AzureOpenAIChatCompletionClient: Configured client instance

    Raises:
        ValueError: If required parameters are missing
    """
    if not model:
        raise ValueError("Model name is required")
    if not base_url:
        raise ValueError("Base URL is required")
    if not api_version:
        raise ValueError("API version is required")

    # Prepare the configuration dictionary with only the supported parameters
    azure_config: Dict[str, Any] = {
        "model": model,
        "azure_endpoint": base_url,
        "azure_deployment": deployment or model,
        "api_version": api_version,
    }

    # Handle authentication based on authentication method
    if authentication_method == AuthenticationMethod.DEFAULT_CREDENTIAL:
        # Use Azure Default Credential for authentication
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )
        azure_config["azure_ad_token_provider"] = token_provider
    elif authentication_method == AuthenticationMethod.MSI:
        # Use Managed Service Identity for authentication
        credential = (
            ManagedIdentityCredential(client_id=client_id)
            if client_id
            else ManagedIdentityCredential()
        )
        token_provider = get_bearer_token_provider(
            credential, "https://cognitiveservices.azure.com/.default"
        )
        azure_config["azure_ad_token_provider"] = token_provider
    elif authentication_method == AuthenticationMethod.CLIENT_ID_AND_SECRET:
        # Use Client Secret Credential for authentication
        if not client_id:
            raise ValueError(
                "client_id is required when using CLIENT_ID_AND_SECRET authentication"
            )
        if not client_secret:
            raise ValueError(
                "client_secret is required when using CLIENT_ID_AND_SECRET authentication"
            )

        # Handle tenant_id: use provided value or fallback to environment variable
        effective_tenant_id = tenant_id
        if not effective_tenant_id:
            import os

            effective_tenant_id = os.getenv("AZURE_TENANT_ID")

        if not effective_tenant_id:
            raise ValueError(
                "tenant_id is required when using CLIENT_ID_AND_SECRET authentication. "
                "Provide tenant_id in configuration or set AZURE_TENANT_ID environment variable"
            )

        credential = ClientSecretCredential(
            tenant_id=effective_tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )
        token_provider = get_bearer_token_provider(
            credential, "https://cognitiveservices.azure.com/.default"
        )
        azure_config["azure_ad_token_provider"] = token_provider
    else:
        # Use API key authentication (TOKEN method)
        if not api_key:
            raise ValueError(
                "API key is required when not using default credential authentication"
            )
        azure_config["api_key"] = api_key

    return AzureOpenAIChatCompletionClient(**azure_config)
