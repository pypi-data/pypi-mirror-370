"""
Model Initialization Module.

This module provides the `Model` class for dynamically initializing and managing
Large Language Model (LLM) instances based on a specified provider. Supported providers
include OpenAI, Anthropic, Mistral, Fireworks, Google Generative AI, Grok and Groq.
"""

# Standard library imports
from typing import Any, Optional, Self, Union

# Third-party imports
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_anthropic import ChatAnthropic
from langchain_fireworks import ChatFireworks
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from langchain_xai import ChatXAI
from langchain_groq import ChatGroq
from langchain_google_vertexai import ChatVertexAI
import vertexai

# Internal application imports
from crypto_com_agent_client.config.constants import (
    MODEL_DEFAULT,
    PROVIDER_DEFAULT,
    LLAMA4_MODEL,
)
from crypto_com_agent_client.lib.enums.provider_enum import Provider


class Model:
    """
    A class to handle dynamic initialization and management of Large Language Model (LLM) instances.

    This class supports multiple providers and ensures the correct model is initialized
    with appropriate configurations and API keys. It also supports optional tool binding
    for enhanced functionality.

    Supported providers:
        - OpenAI
        - Anthropic
        - Mistral
        - Fireworks
        - Google Generative AI
        - Grok
        - Groq
        - Vertex AI

    Attributes:
        provider (Provider): The specified provider for the model.
        api_key (str): The API key used for authentication with the provider.
        temeprature: The model temperature parameter.
        model (Optional[str]): The specific model name (optional). If not provided,
                               default models for the provider will be used.
        model_instance (Union[ChatOpenAI, ChatAnthropic, ChatMistralAI, ChatFireworks, ChatGoogleGenerativeAI, ChatXAI, ChatGroq, ChatVertexAI]):
            The initialized LLM instance.

    Example:
        >>> from lib.enums.model_enum import Provider
        >>> from core.model import Model
        >>>
        >>> model = Model(provider=Provider.OpenAI, api_key="your-api-key", model="gpt-4", temeprature=0)
        >>> print(model.model)
    """

    def __init__(
        self,
        api_key: str,
        temperature: int = 1,
        provider: Provider = PROVIDER_DEFAULT,
        model: Optional[str] = MODEL_DEFAULT,
        project_id: Optional[str] = None,
        location_id: Optional[str] = None,
    ) -> None:
        """
        Initialize the Model instance.

        Args:
            provider (Provider): The provider enum (e.g., `Provider.OpenAI`, `Provider.Anthropic`).
            api_key (str): The API key for authenticating with the provider.
            model (Optional[str]): The specific model name (optional). If not provided,
                                   default models for the provider will be used.
            project_id (Optional[str]): The Google Cloud project ID (required for Vertex AI).
            location_id (Optional[str]): The Google Cloud location ID (required for Vertex AI).

        Example:
            >>> from lib.enums.model_enum import Provider
            >>> model = Model(provider=Provider.OpenAI, api_key="your-api-key")
        """
        self.provider: Provider = provider
        self.api_key: str = api_key
        self.temperature: int = temperature
        self.model: str = model
        self.project_id: Optional[str] = project_id
        self.location_id: Optional[str] = location_id
        self.model_instance: Union[
            ChatOpenAI,
            ChatAnthropic,
            ChatMistralAI,
            ChatFireworks,
            ChatGoogleGenerativeAI,
            ChatXAI,
            ChatGroq,
            ChatVertexAI,
        ] = self.initialize_model()

    def initialize_model(self: Self) -> Union[
        ChatOpenAI,
        ChatAnthropic,
        ChatMistralAI,
        ChatFireworks,
        ChatGoogleGenerativeAI,
        ChatXAI,
        ChatGroq,
        ChatVertexAI,
    ]:
        """
        Dynamically initializes the model based on the provider and optional model name.

        This method validates the provider and returns a model instance with default
        or user-specified configurations.

        Returns:

            Union[ChatOpenAI, ChatAnthropic, ChatMistralAI, ChatFireworks, ChatGoogleGenerativeAI, ChatXAI, ChatGroq, ChatVertexAI]:
                An initialized LLM instance corresponding to the provider.

        Raises:
            ValueError: If the provider is unsupported or required configuration is missing.

        Example:
            >>> model = Model(provider=Provider.Anthropic, api_key="your-api-key")
            >>> model_instance = model.initialize_model()
        """
        if self.provider == Provider.OpenAI:
            return ChatOpenAI(
                model=self.model or "gpt-4",
                temperature=self.temperature,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                api_key=self.api_key,
            )

        elif self.provider == Provider.Anthropic:
            return ChatAnthropic(
                model=self.model or "claude-3-5-sonnet-20240620",
                temperature=self.temperature,
                max_tokens=1024,
                timeout=None,
                max_retries=2,
                api_key=self.api_key,
            )

        elif self.provider == Provider.Mistral:
            return ChatMistralAI(
                model=self.model or "mistral-large-latest",
                temperature=self.temperature,
                max_retries=2,
                api_key=self.api_key,
            )

        elif self.provider == Provider.Fireworks:
            return ChatFireworks(
                model=self.model or "accounts/fireworks/models/llama-v3-70b-instruct",
                temperature=self.temperature,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                api_key=self.api_key,
            )

        elif self.provider == Provider.GoogleGenAI:
            return ChatGoogleGenerativeAI(
                model=self.model or "gemini-1.5-pro",
                temperature=self.temperature,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                api_key=self.api_key,
            )

        elif self.provider == Provider.Grok:
            return ChatXAI(
                model=self.model or "grok-3",
                xai_api_key=self.api_key,
                temperature=self.temperature,
            )

        elif self.provider == Provider.Groq:
            return ChatGroq(
                model=self.model or LLAMA4_MODEL,
                temperature=self.temperature,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                api_key=self.api_key,
            )
        elif self.provider == Provider.VertexAI:
            if not self.project_id or not self.location_id:
                raise ValueError(
                    "project_id and location_id are required for Vertex AI"
                )

            try:
                # Initialize Vertex AI
                vertexai.init(project=self.project_id, location=self.location_id)

                return ChatVertexAI(
                    model_name=self.model
                    or "publishers/google/models/gemini-2.0-flash-001",
                    project=self.project_id,
                    location=self.location_id,
                    temperature=self.temperature,
                    max_retries=2,
                )
            except Exception as e:
                raise ValueError(f"Failed to initialize Vertex AI: {str(e)}")

        else:
            raise ValueError(f"Unsupported provider: {self.provider.value}")

    def bind_tools(self: Self, tools: Any) -> Runnable[LanguageModelInput, BaseMessage]:
        """
        Binds additional tools to the model if supported by the provider.

        Certain models support integrating tools (e.g., for enhanced functionality).
        This method checks if the model instance supports tool binding and performs
        the operation. If not supported, it raises a `NotImplementedError`.

        Args:
            tools (Any): A collection of tools to bind to the model.

        Returns:
            Runnable[LanguageModelInput, BaseMessage]: The result of the tool binding operation if supported.

        Raises:
            NotImplementedError: If the model does not support tool binding.

        Example:
            >>> from langchain_core.tools import BaseTool
            >>> model = Model(provider=Provider.OpenAI, api_key="your-api-key")
            >>> bound_model = model.bind_tools([some_tool])
        """
        if hasattr(self.model_instance, "bind_tools"):
            return self.model_instance.bind_tools(tools)
        raise NotImplementedError(
            f"Tool binding not supported for {self.provider.value}."
        )
