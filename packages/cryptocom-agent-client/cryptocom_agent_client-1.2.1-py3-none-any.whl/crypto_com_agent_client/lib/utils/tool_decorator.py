"""
Decorators Module.

This module provides custom wrappers for LangChain decorators to make them
appear as part of the Agent library.
"""

# Third-party imports
from langchain_core.tools import tool as langchain_tool


def tool(func):
    """
    Custom tool decorator that wraps the LangChain `@tool` decorator.

    This decorator allows you to define custom tool functions that can be integrated
    into the Agent's workflow. It serves as a wrapper around the LangChain's `@tool`
    decorator to align with the Agent library's interface.

    Args:
        func (callable): The function to decorate as a tool.

    Returns:
        callable: The decorated function, now compatible with LangChain workflows.

    Example:
        >>> from agent.decorators import tool
        >>>
        >>> @tool
        >>> def greet_user(name: str) -> str:
        >>>     \"\"\"
        >>>     A simple greeting tool.
        >>>
        >>>     Args:
        >>>         name (str): The name of the user to greet.
        >>>
        >>>     Returns:
        >>>         str: A greeting message.
        >>>     \"\"\"
        >>>     return f"Hello, {name}! How can I assist you today?"
        >>>
        >>> # The function can now be used as a LangChain tool.
        >>> print(greet_user("Alice"))
        Hello, Alice! How can I assist you today?
    """
    return langchain_tool(func)
