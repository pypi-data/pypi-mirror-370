"""
Plugins Enum Module.

This module defines the `Plugins` enum, which lists the supported plugin types
available for use in the application. These plugins are used to dynamically configure
and extend the functionality of the application.

"""

# Standard library imports
from enum import Enum


class Plugins(str, Enum):
    """
    Enum for plugin types.

    This enum represents the various plugin types that can be passed to the agent
    during initialization for customizing its behavior and functionality.

    Attributes:
        Personality (str): Represents the personality plugin for the agent.
        Instructions (str): Represents the instructions plugin for customizing agent behavior.
        Tools (str): Represents the tools plugin for extending agent functionality.
        LangFuse (str): Represents the LangFuse plugin for monitoring and telemetry.
        Storage (str): Represents the storage plugin for persistence and state management.

    Example:
        >>> from lib.enums.plugins_enum import Plugins
        >>> plugin = Plugins.Personality
        >>> print(plugin)
        Personality

        >>> if plugin == Plugins.Storage:
        ...     print("Using custom storage for persistence.")
        Using custom storage for persistence.
    """

    Personality = "personality"
    Instructions = "instructions"
    Tools = "tools"
    LangFuse = "langfuse"
    Storage = "storage"
