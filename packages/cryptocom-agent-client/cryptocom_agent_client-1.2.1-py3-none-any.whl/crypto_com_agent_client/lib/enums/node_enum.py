"""
Node Enum Module.

This module defines the `Node` enum, which lists the nodes in the workflow graph.
It is used to identify and interact with specific nodes in the LangGraph workflow.
"""

# Standard library imports
from enum import Enum


class Node(str, Enum):
    """
    Enum for workflow nodes.

    This enum represents the key nodes in the workflow graph, such as the agent
    node and the tools node. These nodes define the primary functional units
    in the LangGraph workflow.

    Attributes:
        Agent (str): Represents the agent node, responsible for interacting
                     with the language model and processing user input.
        Tools (str): Represents the tools node, responsible for handling tool
                     execution and interactions.

    Example:
        >>> from lib.enums.node_enum import Node
        >>> current_node = Node.Agent
        >>> print(current_node)
        agent

        >>> if current_node == Node.Tools:
        ...     print("Processing tools node.")
        ... else:
        ...     print("Processing agent node.")
        Processing agent node.
    """

    Agent = "agent"
    Tools = "tools"
