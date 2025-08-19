"""
Common utilities for the Ingenious framework.

This package contains utility modules that can be used across different
parts of the application, including client builder functions and helper utilities.

The main exports are Azure OpenAI client builder functions that provide
convenient utilities for creating AzureOpenAIChatCompletionClient instances
with different authentication methods and configuration sources.
"""

from .azure_openai_client_builder import (
    create_aoai_chat_completion_client_from_config,
    create_aoai_chat_completion_client_from_params,
    create_aoai_chat_completion_client_from_settings,
)

__all__ = [
    "create_aoai_chat_completion_client_from_config",
    "create_aoai_chat_completion_client_from_params",
    "create_aoai_chat_completion_client_from_settings",
]
