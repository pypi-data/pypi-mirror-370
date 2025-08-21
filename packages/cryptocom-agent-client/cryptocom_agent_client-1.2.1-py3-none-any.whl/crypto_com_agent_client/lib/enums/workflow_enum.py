"""
Workflow Enum Module.

This module defines the `Workflow` enum, which lists the keys used in the workflow
for managing state and configuration. These keys serve as identifiers for various
aspects of the workflow, including messages, roles, and configuration options.
"""

# Standard library imports
from enum import Enum


class Workflow(str, Enum):
    """
    Enum for workflow keys.

    This enum provides a standardized set of keys used within the workflow
    to manage state, configuration, and interactions. These keys ensure
    consistent identification and handling of various workflow components.

    Attributes:
        Messages (str): Represents the key for the messages list in the workflow state.
                        This list contains all exchanged messages between components.
        Role (str): Represents the key for identifying the role in the workflow state.
                    Roles include agent, system, and user, which dictate the context of interactions.
        ThreadID (str): Represents the key for thread identification. This is used to
                        differentiate or isolate workflows in concurrent sessions.
        Configurable (str): Represents the key for additional configurable settings in the workflow.
                            These settings can include thread-specific or global configurations.
        Content (str): Represents the key for message content, storing the text or
                       information within a message.
        Callbacks (str): Represents the key for callbacks in the workflow. This is used
                         to manage event-driven or asynchronous behavior during the workflow.

    Example:
        >>> from lib.enums.workflow_enum import Workflow
        >>> message_key = Workflow.Messages
        >>> print(message_key)
        messages

        >>> if Workflow.ThreadID in workflow_state:
        ...     print("Thread ID is configured in the workflow.")
        Thread ID is configured in the workflow.
    """

    Messages = "messages"
    Role = "role"
    ThreadID = "thread_id"
    Configurable = "configurable"
    Content = "content"
    Callbacks = "callbacks"
    ChainID = "chain_id"
    PrivateKey = "private_key"
    SSOWalletURL = "sso_wallet_url"
