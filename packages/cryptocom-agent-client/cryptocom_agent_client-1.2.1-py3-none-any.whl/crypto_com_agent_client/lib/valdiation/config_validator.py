"""
Config Validator Module.

This module defines the `ConfigValidator` class, which provides utility methods
to validate configurations for LLM, blockchain, and plugin setups. It ensures that all
required parameters are present and applies default values where applicable.
"""

# Standard library imports
from typing import Dict, Optional

# Third-party imports
from langfuse.callback.langchain import LangchainCallbackHandler

# Internal application imports
from crypto_com_agent_client.lib.types.blockchain_config import BlockchainConfig
from crypto_com_agent_client.lib.types.llm_config import LLMConfig
from crypto_com_agent_client.lib.types.plugins_config import PluginsConfig
from crypto_com_agent_client.lib.utils.storage import Storage
from crypto_com_agent_client.plugins.storage.sqllite_plugin import SQLitePlugin
from crypto_com_agent_client.lib.enums.provider_enum import Provider


class ConfigValidator:
    """
    The `ConfigValidator` class validates configuration dictionaries for LLM, blockchain,
    and plugin setups, ensuring that all required parameters are present and valid.

    Responsibilities:
        - Validate the presence and correctness of required keys in configurations.
        - Apply default values for optional parameters.
        - Validate optional plugins for additional customization.

    Example:
        >>> from lib.validation.config_validator import ConfigValidator
        >>> llm_config = LLMConfig(
        ...     provider="OpenAI",
        ...     provider_api_key="your-api-key"
        ... )
        >>> validated_llm_config = ConfigValidator.validate_llm_config(llm_config)
        >>> print(validated_llm_config)

        >>> blockchain_config = BlockchainConfig(
        ...     api_key="blockchain-api-key"
        ... )
        >>> validated_blockchain_config = ConfigValidator.validate_blockchain_config(blockchain_config)
        >>> print(validated_blockchain_config)

        >>> plugins_config = PluginsConfig(
        ...     personality={"tone": "friendly"},
        ...     instructions="You are a helpful assistant.",
        ...     tools=[custom_tool],
        ...     storage=custom_storage,
        ...     langfuse=custom_langfuse
        ... )
        >>> validated_plugins = ConfigValidator.validate_plugins_config(plugins_config)
        >>> print(validated_plugins)
    """

    @staticmethod
    def validate_llm_config(llm_config: Optional[LLMConfig]) -> LLMConfig:
        """
        Validate the LLM (Large Language Model) configuration.

        Ensures that all required keys are present in the LLM configuration dictionary.
        Applies default values for optional keys if they are missing.

        Args:
            llm_config (LLMConfig): The LLM configuration object.

        Returns:
            LLMConfig: The validated and updated LLM configuration.

        Raises:
            ValueError: If the configuration is missing or any required parameter is invalid.
        """
        if not llm_config:
            raise ValueError("LLM configuration is required and cannot be empty.")

        # For Vertex AI, we don't require an API key since it uses Google Cloud authentication
        if llm_config.provider != Provider.VertexAI:
            # Ensure the provider API key is present and valid for non-Vertex AI providers
            if not llm_config.provider_api_key:
                raise ValueError(
                    "The 'provider_api_key' is required in LLM configuration for non-Vertex AI providers."
                )

        # Validate Vertex AI specific parameters
        if llm_config.provider == Provider.VertexAI:
            if not llm_config.project_id:
                raise ValueError(
                    "The 'project_id' is required for Vertex AI configuration."
                )
            if not llm_config.location_id:
                raise ValueError(
                    "The 'location_id' is required for Vertex AI configuration."
                )

        return llm_config

    @staticmethod
    def validate_blockchain_config(
        blockchain_config: Optional[BlockchainConfig],
    ) -> BlockchainConfig:
        """
        Validate the blockchain configuration.

        Ensures that all required keys are present in the blockchain configuration object.

        Args:
            blockchain_config (BlockchainConfig): The blockchain configuration object.

        Returns:
            BlockchainConfig: The validated blockchain configuration.

        Raises:
            ValueError: If the configuration is missing or any required parameter is invalid.
        """
        if not blockchain_config:
            raise ValueError(
                "Blockchain configuration is required and cannot be empty."
            )

        # Ensure all required keys are present and valid
        if not blockchain_config.api_key:
            raise ValueError("The 'api_key' is required in blockchain configuration.")

        return blockchain_config

    @staticmethod
    def validate_plugins_config(plugins: Optional[PluginsConfig]) -> PluginsConfig:
        """
        Validate the plugins configuration.

        Ensures that all optional plugins (e.g., personality, tools, storage, langfuse) are valid.

        Args:
            plugins (PluginsConfig): The plugins configuration object.

        Returns:
            PluginsConfig: The validated plugins configuration.

        Example:
            >>> plugins = PluginsConfig(
            ...     personality={"tone": "friendly"},
            ...     instructions="You are a helpful assistant.",
            ...     tools=[custom_tool],
            ...     storage=custom_storage,
            ...     langfuse=custom_langfuse
            ... )
            >>> validated_plugins = ConfigValidator.validate_plugins_config(plugins)
            >>> print(validated_plugins)
        """
        if not plugins:
            return PluginsConfig()

        # Validate storage
        if plugins.storage and not isinstance(plugins.storage, (SQLitePlugin, Storage)):
            raise ValueError(
                "The 'storage' plugin must be an instance of either the SQLitePlugin or Storage class."
            )

        # Validate LangFuse
        if plugins.langfuse and not isinstance(plugins.langfuse, dict):
            raise ValueError(
                "The 'langfuse' plugin must be an instance of LangchainCallbackHandler."
            )

        # Validate tools
        if plugins.tools and not isinstance(plugins.tools, list):
            raise ValueError("The 'tools' plugin must be a list of callable tools.")

        return plugins

    @staticmethod
    def validate_langfuse_config(
        langfuse_config: Optional[Dict[str, str]],
    ) -> Optional[LangchainCallbackHandler]:
        """
        Validate and convert the Langfuse configuration into a LangchainCallbackHandler.

        Args:
            langfuse_config (dict, optional): Langfuse configuration dictionary.
                Example:
                    {
                        "public-key": "user-public-key",
                        "secret-key": "user-secret-key",
                        "host": "https://langfuse.example.com",
                    }

        Returns:
            LangchainCallbackHandler: The initialized handler if configuration is valid, or None.

        Raises:
            ValueError: If the configuration is invalid or missing required keys.
        """
        if not langfuse_config:
            return None

        required_keys = {"public-key", "secret-key", "host"}
        missing_keys = required_keys - langfuse_config.keys()

        if missing_keys:
            raise ValueError(
                f"Langfuse configuration is missing required keys: {', '.join(missing_keys)}"
            )

        return LangchainCallbackHandler(
            public_key=langfuse_config["public-key"],
            secret_key=langfuse_config["secret-key"],
            host=langfuse_config["host"],
        )
