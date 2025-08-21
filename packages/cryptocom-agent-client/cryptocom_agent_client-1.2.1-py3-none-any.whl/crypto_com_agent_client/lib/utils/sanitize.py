"""
Sanitization Utilities Module.

This module provides utility functions to sanitize sensitive information from the
workflow state, specifically targeting private keys. It ensures that sensitive
data is masked before being persisted to storage or logged.

Functions:
    - mask_private_keys(text): Masks private keys found in a string.
    - sanitize_state(state): Returns a sanitized deep copy of the conversation state.
"""

# Standard library imports
import re
import copy

# Third-party imports
from langchain_core.messages import BaseMessage

# Internal application imports
from crypto_com_agent_client.lib.enums.workflow_enum import Workflow

# Patterns to match sensitive key strings (e.g., private keys)
PRIVATE_KEY_PATTERNS = [
    re.compile(
        r"(private\s*key\s*[:=]?\s*)(0x[a-fA-F0-9]{64})", re.IGNORECASE
    ),  # Labelled key
    re.compile(r"\b0x[a-fA-F0-9]{64}\b"),  # Raw 64-character hex strings
]


def mask_private_keys(text: str) -> str:
    """
    Masks private key patterns in the provided text string.

    Args:
        text (str): The input text potentially containing sensitive keys.

    Returns:
        str: The sanitized text with private keys masked.

    Example:
        >>> mask_private_keys("Private Key: 0xabc123...")
        'Private Key: ****MASKED_PRIVATE_KEY****'
    """
    for pattern in PRIVATE_KEY_PATTERNS:
        text = pattern.sub(r"****MASKED_PRIVATE_KEY****", text)
    return text


def sanitize_state(state: dict) -> dict:
    """
    Returns a deep-copied version of the state with private keys masked in all messages
    and top-level state variables.

    This function ensures that any sensitive blockchain data is redacted from agent state
    before persistence or inspection.

    Args:
        state (dict): The raw state dictionary from the workflow execution.

    Returns:
        dict: A sanitized version of the state dictionary.

    Example:
        >>> sanitized = sanitize_state(state)
        >>> print(sanitized["messages"][1]["content"])
        '...Private Key: ****MASKED_PRIVATE_KEY****'
    """
    sanitized = copy.deepcopy(state)

    # Mask private key at the top-level key
    if Workflow.PrivateKey in sanitized:
        sanitized[Workflow.PrivateKey] = "****MASKED****"

    # Mask any private keys within the messages list
    if Workflow.Messages in sanitized:
        for i, msg in enumerate(sanitized[Workflow.Messages]):
            # Handle BaseMessage format (before serialization)
            if isinstance(msg, BaseMessage) and isinstance(msg.content, str):
                msg.content = mask_private_keys(msg.content)

            # Handle dict-based messages (after serialization or manual creation)
            elif isinstance(msg, dict) and isinstance(msg.get("content"), str):
                sanitized[Workflow.Messages][i]["content"] = mask_private_keys(
                    msg["content"]
                )

            # Mask any additional string values inside `additional_kwargs`
            if isinstance(msg, dict) and "additional_kwargs" in msg:
                for key, val in msg["additional_kwargs"].items():
                    if isinstance(val, str):
                        msg["additional_kwargs"][key] = mask_private_keys(val)

    return sanitized
