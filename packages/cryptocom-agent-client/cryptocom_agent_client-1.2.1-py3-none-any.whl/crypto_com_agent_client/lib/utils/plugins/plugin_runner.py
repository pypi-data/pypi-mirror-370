import asyncio
import inspect
from typing import List
from crypto_com_agent_client.lib.types.plugin_types import PluginMode
from crypto_com_agent_client.plugins.base import AgentPlugin


def start_plugins(
    plugin_instances: List[AgentPlugin],
) -> None:
    """
    Starts agent plugins based on their declared mode.

    This utility handles two plugin types:
    - Primary plugins (mode="primary") which define a `run()` method (sync or async),
      typically long-lived services (e.g., bots).

    Args:
        plugin_instances (List[AgentPlugin]): A list of plugin instances implementing `AgentPlugin`.
        handler (Optional[InteractionHandler]): Optional handler to be passed into support plugins.

    Behavior:
        - Starts the first primary plugin by calling its `run()` method (sync or async).
        - Logs to console if no primary plugin is found.

    Example:
        >>> start_plugins(self.plugin_instances, self.handler)
    """
    for plugin in plugin_instances:
        if getattr(plugin, "mode", PluginMode.SUPPORT) == PluginMode.PRIMARY:
            if hasattr(plugin, "run") and callable(plugin.run):
                if inspect.iscoroutinefunction(plugin.run):
                    asyncio.run(plugin.run())
                else:
                    plugin.run()
                break
    else:
        print("No runnable plugin found.")
