"""
Role Enum Module.

This module defines the `Role` enum, which lists the roles used in the workflow.
The roles help define the context and responsibility of each participant or component
within the LangGraph workflow, such as the agent, system, or user.
"""

# Standard library imports
from enum import Enum


class Role(str, Enum):
    """
    Enum for roles in the workflow.

    This enum represents the various roles involved in the workflow, such as
    the agent, system, and user. These roles are used to categorize messages,
    manage context, and facilitate interactions within the LangGraph framework.

    Attributes:
        Agent (str): Represents the agent role, typically the AI assistant
                     responsible for processing user inputs and providing responses.
        System (str): Represents the system role, providing instructions, configurations,
                      or system-level context to the agent.
        User (str): Represents the user role, representing the end-user interacting
                    with the workflow.

    Example:
        >>> from lib.enums.role_enum import Role
        >>> current_role = Role.User
        >>> print(current_role)
        user

        >>> if current_role == Role.User:
        ...     print("Handling user input.")
        Executing user tasks.
    """

    Agent = "agent"
    System = "system"
    User = "user"
