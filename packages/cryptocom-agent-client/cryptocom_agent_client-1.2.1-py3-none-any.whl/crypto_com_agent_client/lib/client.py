"""
Agent Module.

This module defines the `Agent` class, which serves as the primary interface
for interacting with the LangGraph-based workflow. The Agent encapsulates
the workflow graph and provides high-level methods for initialization and
user interaction.
"""

# Standard library imports
from typing import Optional, Self

# Internal application imports
from crypto_com_agent_client.config.logging_config import configure_logging
from crypto_com_agent_client.core.handlers.interaction_handler import InteractionHandler
from crypto_com_agent_client.lib.initializer import Initializer
from crypto_com_agent_client.lib.types.blockchain_config import BlockchainConfig
from crypto_com_agent_client.lib.types.llm_config import LLMConfig
from crypto_com_agent_client.lib.types.plugin_types import PluginMode
from crypto_com_agent_client.lib.types.plugins_config import PluginsConfig
from crypto_com_agent_client.lib.utils.plugins.plugin_runner import start_plugins
from crypto_com_agent_client.lib.utils.storage import Storage
from crypto_com_agent_client.plugins.social.discord_plugin import DiscordPlugin
from crypto_com_agent_client.plugins.storage.sqllite_plugin import SQLitePlugin
from crypto_com_agent_client.plugins.base import AgentPlugin


class Agent:
    """
    The `Agent` class encapsulates the LangGraph workflow and provides a
    high-level interface for managing interactions. It supports initialization
    with LLM, blockchain, and optional LangFuse configurations.

    Attributes:
        handler (InteractionHandler): The interaction handler that manages user input and workflow state.

    Example:
        >>> from lib.client import Agent
        >>> agent = Agent.init(
        ...     llm_config={
        ...         "provider": "OpenAI",
        ...         "model": "gpt-4",
        ...         "provider-api-key": "your-api-key",
        ...     },
        ...     blockchain_config={
        ...         "api-key": "developer-sdk-api-key",
        ...     },
        ...     plugins={
        ...         "personality": {
        ...             "tone": "friendly",
        ...             "language": "English",
        ...             "verbosity": "high",
        ...         },
        ...         "instructions": "You are a humorous assistant.",
        ...         "storage": custom_storage,
        ...     },
        ... )
        >>> response = agent.interact("Hello! What can you do?")
        >>> print(response)
    """

    def __init__(
        self: Self,
        handler: InteractionHandler,
        discord_plugin: Optional[DiscordPlugin] = None,
        plugin_instances: Optional[list[AgentPlugin]] = None,
    ) -> None:
        """
        Initializes the Agent instance.

        Args:
            handler (InteractionHandler): The interaction handler that processes user input
                and manages workflow state.

        Example:
            >>> from core.handlers.interaction_handler import InteractionHandler
            >>> handler = InteractionHandler(app=compiled_workflow, storage=custom_storage)
            >>> agent = Agent(handler=handler)
        """
        self.handler: InteractionHandler = handler
        self.discord_plugin = discord_plugin
        self.plugin_instances = plugin_instances or []

    @staticmethod
    def init(
        llm_config: LLMConfig = None,
        blockchain_config: BlockchainConfig = None,
        plugins: PluginsConfig = None,
        plugin_instances: Optional[list[AgentPlugin]] = None,
    ) -> "Agent":
        """
        Initializes the Agent with LLM, blockchain, and plugin configurations.

        Args:
            llm_config (LLMConfig): Configuration for the LLM provider.
                Example:
                    {
                        "provider": "OpenAI",
                        "model": "gpt-4",
                        "provider-api-key": "your-api-key"
                    }
            blockchain_config (BlockchainConfig): Configuration for the blockchain client.
                Example:
                    {
                        "api-key": "developer-sdk-api-key"
                    }
            plugins (PluginsConfig): Additional configurations and integrations.
                Example:
                    {
                        "personality": {
                            "tone": "friendly",
                            "language": "English",
                            "verbosity": "high",
                        },
                        "instructions": "You are a humorous assistant.",
                        "storage": custom_storage,
                    }

        Returns:
            Agent: An initialized `Agent` instance with the workflow configured.

        Raises:
            ValueError: If any required configurations are missing or invalid.

        Example:
            >>> agent = Agent.init(
            ...     llm_config={
            ...         "provider": "OpenAI",
            ...         "model": "gpt-4",
            ...         "provider-api-key": "your-api-key",
            ...         "temperature": 0,
            ...     },
            ...     blockchain_config={
            ...         "api-key": "developer-sdk--api-key",
            ...     },
            ...     plugins={
            ...         "personality": {
            ...             "tone": "friendly",
            ...             "language": "English",
            ...             "verbosity": "high",
            ...         },
            ...         "instructions": "You are a humorous assistant.",
            ...         "storage": custom_storage,
            ...     },
            ... )
        """
        # Convert to types
        llm_config = LLMConfig(**(llm_config))
        blockchain_config = BlockchainConfig(**(blockchain_config))
        plugins = PluginsConfig(**(plugins or {}))

        # Configure logging
        configure_logging(llm_config)

        # Use Initializer to set up the workflow
        initializer = Initializer(
            llm_config=llm_config,
            blockchain_config=blockchain_config,
            plugins=plugins,
        )

        # Initialize storage
        storage: SQLitePlugin | Storage = plugins.storage

        # Create InteractionHandler
        handler = InteractionHandler(
            app=initializer.workflow,
            storage=storage,
            blockchain_config=blockchain_config,
            debug_logging=llm_config.debug_logging,
        )

        discord_plugin = None

        if plugins.discord and isinstance(plugins.discord, dict):
            bot_token = plugins.discord.get("bot_token")
            if bot_token:
                discord_plugin = DiscordPlugin(bot_token=bot_token, agent=handler)

        # Set up all discovered plugin instances
        for plugin in plugin_instances or []:
            plugin.setup(handler)

            # For support-mode plugins, trigger on_ready() lifecycle method
            # This allows things like logging, analytics, or storage hooks to initialize
            if getattr(plugin, "mode", PluginMode.SUPPORT) == PluginMode.PRIMARY:
                if hasattr(plugin, "on_ready") and callable(plugin.on_ready):
                    plugin.on_ready(handler)

        return Agent(
            handler=handler,
            discord_plugin=discord_plugin,
            plugin_instances=plugin_instances,
        )

    def interact(self: Self, input: str, thread_id: Optional[int] = None) -> str:
        """
        Processes user input through the workflow and returns the generated response.

        Args:
            input (str): The user's input message.
            thread_id (int, optional): A thread ID for contextual execution.

        Returns:
            str: The response generated by the workflow.

        Example:
            >>> response = agent.interact("Hello, what can you do?")
            >>> print(response)
        """
        return self.handler.interact(user_input=input, thread_id=thread_id)

    def start_discord(self):
        """
        Starts the Discord bot if it has been configured.
        """
        if self.discord_plugin:
            print("Starting Discord bot...")
            self.discord_plugin.run()
        else:
            raise ValueError(
                "Discord bot is not configured. Provide 'bot_token' in the plugin config."
            )

    def start(self):
        """
        Starts all plugins based on their declared `mode`.

        This method delegates to `start_plugins()` to handle:
        - Starting the first primary plugin (mode="primary") that defines a `run()` method.
        Only one primary plugin can run at a time (e.g., Telegram, Discord).

        Args:
            None. Uses internal `plugin_instances` and `handler`.

        Behavior:
            - Launches the first available primary plugin that has a `run()` method.
            - Supports both synchronous and asynchronous primary plugins.
        """
        start_plugins(self.plugin_instances)
