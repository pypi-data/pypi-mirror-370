from enum import Enum


class PluginMode(str, Enum):
    """
    Represents the execution mode of a plugin.

    - PRIMARY: Plugins that control the main user interaction (e.g. Telegram, Discord).
    - SUPPORT: Background plugins that assist or augment functionality (e.g. logging, analytics, storage).
    """

    PRIMARY = "primary"
    SUPPORT = "support"
