"""
Personality Manager Module.

This module defines the `PersonalityPlugin` class, which is responsible for managing
the personality and character instructions of the Agent system.
"""

from crypto_com_agent_client.config.constants import DEFAULT_SYSTEM_INSTRUCTION


class PersonalityPlugin:
    """
    A class to manage the personality and character instructions of the system.

    Responsibilities:
        - Manage the personality configuration, including tone, language, and verbosity.
        - Manage character instructions, which dictate how the system responds to users.
        - Provide methods to update and retrieve the active personality and instructions.

    Attributes:
        personality (dict): The active personality configuration, initialized from PluginsConfig.
        instructions (str): The active character instructions, initialized from PluginsConfig.

    Example:
        >>> pm = PersonalityPlugin(
        ...     personality={"tone": "friendly", "language": "German", "verbosity": "high"},
        ...     instructions="Always include a joke in your responses."
        ... )
        >>> print(pm.get_configuration())
        Tone: friendly, Language: German, Verbosity: high. Always include a joke in your responses.
    """

    def __init__(self, personality: dict, instructions: str) -> None:
        """
        Initialize the PersonalityPlugin.

        Args:
            personality (dict): User-provided or default personality configuration from PluginsConfig.
            instructions (str): User-provided or default character instructions from PluginsConfig.

        Example:
            >>> pm = PersonalityPlugin(
            ...     personality={"tone": "friendly", "language": "German", "verbosity": "high"},
            ...     instructions="Always include a joke in your responses."
            ... )
        """
        self.personality = personality
        self.instructions = instructions

    def update_personality(self, new_personality: dict) -> None:
        """
        Update the active personality configuration with new values.

        Args:
            new_personality (dict): A dictionary of personality attributes to update.

        Example:
            >>> pm = PersonalityPlugin({"tone": "professional"}, "Respond professionally.")
            >>> pm.update_personality({"tone": "casual", "language": "Spanish"})
            >>> print(pm.personality)
            {'tone': 'casual', 'language': 'Spanish', 'verbosity': 'medium'}
        """
        self.personality.update(new_personality)

    def update_instructions(self, new_instructions: str) -> None:
        """
        Update the active character instructions.

        Args:
            new_instructions (str): The new character instructions.

        Example:
            >>> pm = PersonalityPlugin({"tone": "friendly"}, "Be friendly.")
            >>> pm.update_instructions("Be concise.")
            >>> print(pm.instructions)
            Be concise.
        """
        self.instructions = new_instructions

    def get_configuration(self) -> str:
        """
        Retrieve the complete system configuration combining default instructions,
        personality settings, and user instructions.

        Returns:
            str: A comprehensive system instruction that includes the default
                 system instruction, personality configuration, and user instructions.

        Example:
            >>> pm = PersonalityPlugin(
            ...     personality={"tone": "friendly", "language": "German", "verbosity": "high"},
            ...     instructions="Always include a joke in your responses."
            ... )
            >>> print(pm.get_configuration())
            # Returns default instruction + personality + user instructions
        """
        # Start with the default instruction
        result = DEFAULT_SYSTEM_INSTRUCTION

        # Add personality if provided
        if self.personality:
            tone = self.personality.get('tone', 'professional')
            language = self.personality.get('language', 'English')
            verbosity = self.personality.get('verbosity', 'medium')
            result += f"\n\nPersonality: Tone: {tone}, Language: {language}, Verbosity: {verbosity}."

        # Add user instructions if provided
        if self.instructions:
            result += f"\n\nAdditional instructions: {self.instructions}"

        return result
