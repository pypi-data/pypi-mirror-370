"""
Logging Configuration Module.

This module provides utilities for configuring logging throughout the application.
It centralizes logging setup to keep other modules clean and maintainable.
"""

import logging
from crypto_com_agent_client.lib.types.llm_config import LLMConfig


def configure_logging(llm_config: LLMConfig) -> None:
    """
    Configure logging level based on debug_logging setting.

    Args:
        llm_config (LLMConfig): LLM configuration containing debug_logging setting

    Returns:
        None
    """
    if llm_config.debug_logging:
        # Reset root logger configuration and set to INFO level
        root_logger = logging.getLogger()
        # Remove all existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        # Set up fresh logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        # Force root logger level to INFO
        root_logger.setLevel(logging.INFO)
    else:
        # Set WARNING level for minimal logging
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger().setLevel(logging.WARNING)

    # Ensure third-party loggers remain quiet unless debug logging is enabled
    if not llm_config.debug_logging:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("telegram").setLevel(logging.WARNING)
        logging.getLogger("discord").setLevel(logging.WARNING)
        logging.getLogger("aiohttp").setLevel(logging.WARNING)
