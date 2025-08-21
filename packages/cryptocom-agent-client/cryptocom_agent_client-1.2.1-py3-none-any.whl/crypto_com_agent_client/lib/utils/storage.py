"""
Storage Module.

This module provides the storage module for internal memorys to store
data in memory and storage structures.
"""

# Standard library imports
from threading import Lock
from typing import Dict, Optional, Self

# Internal application imports
from crypto_com_agent_client.lib.enums.workflow_enum import Workflow
from crypto_com_agent_client.lib.utils.sanitize import sanitize_state


class Storage:
    """
    Base class for storage backends.

    Provides an interface for managing state persistence. This class acts as an
    in-memory storage mechanism and can be extended to implement custom storage
    solutions, such as database-backed or distributed storage systems.

    Responsibilities:
        - Load, save, and delete state associated with specific keys.
        - Maintain thread safety for concurrent access.
        - Provide a mechanism to list all stored keys.

    Attributes:
        _store (dict): Internal dictionary for storing state data.
        _lock (Lock): Threading lock to ensure thread-safe operations.

    Example:
        >>> from lib.utils.storage import Storage
        >>> storage = Storage()
        >>> key = "session123:thread1"
        >>> state = {Workflow.Messages: [{"role": "user", "content": "Hello"}]}
        >>> storage.save_state(state, key)
        >>> loaded_state = storage.load_state(key)
        >>> print(loaded_state)
        {'messages': [{'role': 'user', 'content': 'Hello'}]}
    """

    def __init__(self: Self):
        """
        Initialize the Storage instance.

        This constructor sets up an in-memory storage dictionary and a threading
        lock to ensure thread-safe operations.

        Example:
            >>> storage = Storage()
            >>> print(storage.list_keys())
            []
        """
        self._store: Dict[str, dict] = {}
        self._lock = Lock()

    def load_state(self: Self, key: str) -> Optional[dict]:
        """
        Load the state for the given key.

        Args:
            key (str): The composite key (e.g., session_id:thread_id) used to identify the state.

        Returns:
            Optional[dict]: The state if it exists, or an empty dictionary with
                            a default `Workflow.Messages` key if not found.

        Example:
            >>> storage = Storage()
            >>> state = storage.load_state("nonexistent_key")
            >>> print(state)
            {'messages': []}
        """
        with self._lock:
            return self._store.get(key, {Workflow.Messages: []})

    def save_state(self: Self, state: dict, key: str) -> None:
        """
        Save the state for the given key.

        Args:
            state (dict): The state to save.
            key (str): The composite key (e.g., session_id:thread_id) used to identify the state.

        Example:
            >>> storage = Storage()
            >>> state = {Workflow.Messages: [{"role": "user", "content": "Hello"}]}
            >>> storage.save_state(state, "session123:thread1")
            >>> print(storage.load_state("session123:thread1"))
            {'messages': [{'role': 'user', 'content': 'Hello'}]}
        """
        with self._lock:
            self._store[key] = sanitize_state(state)

    def delete_state(self: Self, key: str) -> None:
        """
        Delete the state for the given key.

        Args:
            key (str): The composite key (e.g., session_id:thread_id) to delete from storage.

        Example:
            >>> storage = Storage()
            >>> state = {Workflow.Messages: [{"role": "user", "content": "Hello"}]}
            >>> storage.save_state(state, "session123:thread1")
            >>> storage.delete_state("session123:thread1")
            >>> print(storage.load_state("session123:thread1"))
            {'messages': []}
        """
        with self._lock:
            if key in self._store:
                del self._store[key]

    def list_keys(self: Self) -> list[str]:
        """
        List all keys in the storage.

        Returns:
            list[str]: A list of all keys currently stored.

        Example:
            >>> storage = Storage()
            >>> storage.save_state({}, "session123:thread1")
            >>> storage.save_state({}, "session124:thread2")
            >>> print(storage.list_keys())
            ['session123:thread1', 'session124:thread2']
        """
        with self._lock:
            return list(self._store.keys())
