"""
Initializer Module.

This module defines the `Initializer` class, which is responsible for setting up
the necessary components for the LangGraph-based workflow. It handles the initialization
of tools, language models, and workflows, ensuring all configurations are validated
and properly integrated.
"""

# Standard library imports
from typing import Any, Callable, List, Optional, Self

# Third-party imports
from crypto_com_developer_platform_client import Client
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langfuse.callback.langchain import LangchainCallbackHandler
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

# Internal application imports
from crypto_com_agent_client.core.model import Model
from crypto_com_agent_client.core.tools import built_in_tools
from crypto_com_agent_client.core.tools.tool_registry import (
    ToolDispatcher,
    ToolRegistry,
)
from crypto_com_agent_client.core.workflows import GraphWorkflow
from crypto_com_agent_client.lib.types.blockchain_config import BlockchainConfig
from crypto_com_agent_client.lib.types.llm_config import LLMConfig
from crypto_com_agent_client.lib.types.plugins_config import PluginsConfig
from crypto_com_agent_client.lib.valdiation.config_validator import ConfigValidator
from crypto_com_agent_client.plugins.personality.personality_plugin import (
    PersonalityPlugin,
)


class Initializer:
    """
    The `Initializer` class is responsible for setting up and configuring all components
    required for the LangGraph-based workflow.

    This class handles the initialization of tools, language models, and workflows,
    ensuring all configurations are validated and properly integrated. It serves as
    the central orchestrator for setting up the Agent's operational environment.

    Responsibilities:
        - Validate LLM, blockchain, and plugin configurations.
        - Initialize tools, including built-in and custom tools.
        - Set up the language model with the specified provider and configuration.
        - Configure the LangGraph workflow with all necessary components.
        - Integrate optional features like LangFuse monitoring and personality settings.

    Attributes:
        llm_config (LLMConfig): Configuration for the language model.
        blockchain_config (BlockchainConfig): Configuration for blockchain interactions.
        plugins (PluginsConfig): Configuration for plugins and additional features.
        langfuse (LangchainCallbackHandler): Optional LangFuse handler for monitoring.
        personality (PersonalityPlugin): Plugin for managing agent personality and instructions.
        tools (List[BaseTool]): List of initialized tools for the workflow.
        workflow (CompiledStateGraph): The compiled LangGraph workflow.
        tool_registry (ToolRegistry): Embedded tool registry instance.

    Example:
        >>> from crypto_com_agent_client.lib.initializer import Initializer
        >>> from crypto_com_agent_client.lib.types.llm_config import LLMConfig
        >>> from crypto_com_agent_client.lib.types.blockchain_config import BlockchainConfig
        >>> from crypto_com_agent_client.lib.types.plugins_config import PluginsConfig
        >>>
        >>> initializer = Initializer(
        ...     llm_config=LLMConfig(
        ...         provider="OpenAI",
        ...         model="gpt-4",
        ...         provider_api_key="your-api-key",
        ...     ),
        ...     blockchain_config=BlockchainConfig(
        ...         api_key="developer-sdk-key",
        ...     ),
        ...     plugins=PluginsConfig(
        ...         personality="friendly",
        ...         tools=[custom_tool],
        ...     ),
        ... )
        >>> workflow = initializer.workflow
    """

    def __init__(
        self: Self,
        llm_config: LLMConfig,
        blockchain_config: BlockchainConfig,
        plugins: Optional[PluginsConfig] = None,
    ) -> None:
        """
        Initialize the Initializer with the provided configurations.

        This constructor validates all provided configurations, sets up the necessary
        components, and compiles the workflow graph for execution.

        Args:
            llm_config (LLMConfig): Configuration for the language model, including
                                    provider, model name, API key, and other settings.
            blockchain_config (BlockchainConfig): Configuration for blockchain interactions,
                                                  API keys, and wallet settings.
            plugins (Optional[PluginsConfig]): Optional configuration for plugins, including
                                               personality settings, custom tools, and monitoring.

        Raises:
            ValidationError: If any of the provided configurations are invalid.
            ImportError: If required dependencies for the specified provider are not available.

        Example:
            >>> from crypto_com_agent_client.lib.types.plugins_config import PluginsConfig
            >>> from crypto_com_agent_client.lib.types.llm_config import LLMConfig
            >>> from crypto_com_agent_client.lib.types.blockchain_config import BlockchainConfig
            >>>
            >>> initializer = Initializer(
            ...     llm_config=LLMConfig(
            ...         provider="OpenAI",
            ...         model="gpt-4",
            ...         provider_api_key="your-api-key",
            ...     ),
            ...     blockchain_config=BlockchainConfig(
            ...         api_key="developer-sdk-key",
            ...     ),
            ...     plugins=PluginsConfig(
            ...         personality="friendly",
            ...         tools=[custom_tool],
            ...     ),
            ... )
        """
        # Validate and store configurations
        self.llm_config: LLMConfig = ConfigValidator.validate_llm_config(llm_config)
        self.blockchain_config: BlockchainConfig = (
            ConfigValidator.validate_blockchain_config(blockchain_config)
        )
        self.plugins = ConfigValidator.validate_plugins_config(plugins)
        plugins.langfuse = ConfigValidator.validate_langfuse_config(plugins.langfuse)

        # Initialize langfuse manager
        self.langfuse: Optional[LangchainCallbackHandler] = plugins.langfuse

        # Initialize personality manager
        self.personality: PersonalityPlugin = PersonalityPlugin(
            personality=plugins.personality,
            instructions=plugins.instructions,
        )

        # Initialize embedded tool registry
        self.tool_registry: ToolRegistry = ToolRegistry()

        # Initialize tools and workflow
        self.tools: List[BaseTool] = self._initialize_tools(plugins.tools)
        self.workflow: CompiledStateGraph = self._initialize_graph_workflow()

    def _initialize_tools(
        self: Self, tools: Optional[List[Callable[..., Any]]]
    ) -> List[BaseTool]:
        """
        Initialize and return a list of tools for the workflow.

        This method sets up the tools required for the LangGraph workflow by:
            - Initializing the blockchain client with the provided configuration.
            - Combining built-in tools with any user-provided custom tools.

        Args:
            tools (Optional[List[Callable[..., Any]]]): A list of user-defined tool functions.

        Returns:
            List[BaseTool]: A list of initialized tools ready for use in the workflow.

        Example:
            >>> tools = initializer._initialize_tools([custom_tool])
            >>> print(tools)
        """
        # Initialize the blockchain client
        Client.init(
            api_key=self.blockchain_config.api_key,
        )

        # Toggle between tool registry and default approach based on optimise_token_usage
        if self.llm_config.optimise_token_usage:
            # Register custom tools in the embedded tool registry
            if tools:
                self.tool_registry.register_custom_tools(tools)

            return [ToolDispatcher(self.tool_registry)]
        else:
            # Include built-in and custom tools
            return built_in_tools + (tools or [])

    def _initialize_graph_workflow(self: Self) -> CompiledStateGraph:
        """
        Initialize and return the compiled GraphWorkflow instance.

        This method sets up the LangGraph workflow graph by:
            - Integrating tools for tool interactions.
            - Configuring the language model with the specified provider.
            - Optionally incorporating a LangFuse handler for monitoring.

        Returns:
            CompiledStateGraph: The compiled workflow graph ready for execution.

        Example:
            >>> workflow = initializer._initialize_graph_workflow()
            >>> print(workflow)
        """
        # Wrap tools in a ToolNode
        tool_node: ToolNode = ToolNode(self.tools)

        # Load personality and instructions
        instructions = self.personality.get_configuration()

        # Initialize the language model with the specified provider and API key
        model_handler: Model = Model(
            api_key=self.llm_config.provider_api_key,
            provider=self.llm_config.provider,
            model=self.llm_config.model,
            temperature=self.llm_config.temperature,
            project_id=self.llm_config.project_id,
            location_id=self.llm_config.location_id,
        )

        # Bind tools to the language model
        workflow_model: Runnable[LanguageModelInput, BaseMessage] = (
            model_handler.bind_tools(self.tools)
        )

        # Set up the LangGraph workflow
        graph_workflow: GraphWorkflow = GraphWorkflow(
            model=workflow_model,
            instructions=instructions,
            langfuse=self.langfuse,
            tool_node=tool_node,
            debug_logging=self.llm_config.debug_logging,
        )

        # Compile the workflow and return it
        return graph_workflow.compile(checkpointer=MemorySaver())
