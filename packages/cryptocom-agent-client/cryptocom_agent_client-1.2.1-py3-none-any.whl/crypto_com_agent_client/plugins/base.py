from abc import ABC, abstractmethod
from typing import Literal

from crypto_com_agent_client.lib.types.plugin_types import PluginMode


class AgentPlugin(ABC):
    """
    Abstract base class for all agent plugins.

    Plugins must inherit from this class and implement the `setup()` method
    at a minimum. Optionally, plugins can define additional lifecycle methods
    such as `run()` (for active/primary plugins) or `on_ready()` (for passive/support plugins).

    Attributes:
        mode (PluginMode): Indicates the execution role of the plugin.
            - PluginMode.PRIMARY: Runs as the main interactive interface (e.g., Telegram, Discord).
            - PluginMode.SUPPORT: Provides side features (e.g., logging, storage) and does not initiate control flow.
    """

    mode: Literal[PluginMode.PRIMARY, PluginMode.SUPPORT] = PluginMode.SUPPORT

    @abstractmethod
    def setup(self, handler) -> None:
        """
        Initializes the plugin with the agent's interaction handler.

        This method is called during the agent's bootstrapping phase, giving
        the plugin access to core interaction capabilities. Implementations may
        register callbacks, event handlers, or prepare internal state.

        Args:
            handler: An instance of InteractionHandler used to process input/output
                through the agent's workflow engine.
        """
        pass
