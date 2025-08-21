"""
Plugins Module.

This module defines the `Plugins` TypedDict, which encapsulates additional
configurations and integrations for extending the functionality of the agent.
"""

# Standard library imports
from typing import Any, Callable, List, Optional, Union

# Third-party imports
from pydantic import BaseModel, Field

# Internal application imports
from crypto_com_agent_client.lib.utils.storage import Storage
from crypto_com_agent_client.plugins.storage.sqllite_plugin import SQLitePlugin


class PluginsConfig(BaseModel):
    """
    TypedDict for Plugins configuration.

    Attributes:
        personality (Optional[dict]): Personality settings for the agent. Includes tone, language, and verbosity.
            Example:
                {
                    "tone": "friendly",
                    "language": "English",
                    "verbosity": "high"
                }
        instructions (Optional[str]): Custom instructions to guide the agent's behavior.
            Example:
                "You are a humorous assistant that includes a joke in every response."
        storage (Optional[Storage]): A custom storage implementation for persisting state.
            Example:
                storage = SQLitePlugin(db_path="state.db")
        langfuse (Optional[LangchainCallbackHandler]): A LangFuse handler for monitoring interactions.
            Example:
                langfuse = LangchainCallbackHandler(
                    public_key="public-key",
                    secret_key="secret-key",
                    host="https://langfuse.example.com",
                )
        tools (Optional[List[Callable[..., Any]]]): A list of callable tool functions for extending agent functionality.
            Example:
                tools = [greet_user, calculate_sum]

    Example:
        >>> from lib.types.plugins import Plugins
        >>> plugins: Plugins = {
        ...     "personality": {
        ...         "tone": "friendly",
        ...         "language": "English",
        ...         "verbosity": "high"
        ...     },
        ...     "instructions": "You are a humorous assistant.",
        ...     "storage": SQLitePlugin(db_path="state.db"),
        ...     "langfuse": LangchainCallbackHandler(
        ...         public_key="public-key",
        ...         secret_key="secret-key",
        ...         host="https://langfuse.example.com",
        ...     ),
        ...     "tools": [greet_user, calculate_sum]
        ...     "telegram": {"bot_token": os.getenv("TELEGRAM_BOT_TOKEN")} {"bot_token": os.getenv("TELEGRAM_BOT_TOKEN")}
        ... }
    """

    personality: Optional[dict] = Field(
        default={
            "tone": "professional",
            "language": "English",
            "verbosity": "medium",
        }
    )
    instructions: Optional[str] = Field(
        default="You are an AI assistant designed to provide helpful, accurate, and professional responses."
    )
    storage: Optional[Union[SQLitePlugin, Storage]] = Field(default_factory=Storage)
    langfuse: Optional[dict] = Field(default=None)
    tools: Optional[List[Callable[..., Any]]] = Field(default=[])
    discord: Optional[dict] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True
