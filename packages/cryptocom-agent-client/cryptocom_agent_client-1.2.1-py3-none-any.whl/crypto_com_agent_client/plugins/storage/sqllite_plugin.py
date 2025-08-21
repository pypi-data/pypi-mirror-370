"""
SQLite Plugin Module.

This module provides an implementation of the Storage interface using SQLite
for persistent state management. It includes methods for saving, loading, and
managing conversation states.
"""

# Standard library imports
import json
import sqlite3
from typing import Optional

# Third-party imports
from crypto_com_agent_client.lib.utils.sanitize import sanitize_state
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage, SystemMessage
from langchain_core.messages.ai import ToolCall


class SQLitePlugin:
    """
    SQLite implementation of the Storage interface for state persistence.

    This class uses an SQLite database to store and manage the state of conversations,
    making it possible to persist and retrieve session data efficiently.

    Attributes:
        conn (sqlite3.Connection): The SQLite database connection object.

    Example:
        >>> from lib.plugins.sqlite_plugin import SQLitePlugin
        >>> storage = SQLitePlugin(db_path="custom_agent_state.db")
        >>> state = {"messages": [{"type": "HumanMessage", "content": "Hello!"}]}
        >>> storage.save_state(state, key="session1:thread1")
        >>> loaded_state = storage.load_state(key="session1:thread1")
        >>> print(loaded_state)
        {'messages': [{'type': 'HumanMessage', 'content': 'Hello!', 'additional_kwargs': {}, 'response_metadata': None}]}
    """

    def __init__(self, db_path: str = "agent_state.db") -> None:
        """
        Initialize the SQLite storage backend.

        Args:
            db_path (str): Path to the SQLite database file. Defaults to "agent_state.db".

        Example:
            >>> storage = SQLitePlugin(db_path="custom_agent_state.db")
        """
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._initialize_table()

    def _initialize_table(self) -> None:
        """
        Create the conversation_state table if it doesn't exist.

        Example:
            >>> storage = SQLitePlugin()
            >>> storage._initialize_table()
        """
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_state (
                    key TEXT PRIMARY KEY,
                    state TEXT
                )
            """
            )

    def _serialize_state(self, state: dict) -> str:
        """
        Serialize the state into a JSON string.

        Args:
            state (dict): The state to serialize.

        Returns:
            str: A JSON string representation of the state.

        Example:
            >>> state = {"messages": [{"type": "HumanMessage", "content": "Hello!"}]}
            >>> serialized = storage._serialize_state(state)
            >>> print(serialized)
            '{"messages": [{"type": "HumanMessage", "content": "Hello!", "additional_kwargs": {}, "response_metadata": null}]}'
        """
        # Convert message objects to dictionaries
        messages = [
            {
                "type": message.__class__.__name__,
                "content": message.content,
                "additional_kwargs": message.additional_kwargs,
                "response_metadata": getattr(message, "response_metadata", None),
                "tool_call_id": (
                    getattr(message, "tool_call_id", None)
                    if hasattr(message, "tool_call_id")
                    else None
                ),
            }
            for message in state.get("messages", [])
        ]
        return json.dumps({"messages": messages})

    def _deserialize_state(self, state_str: str) -> dict:
        """
        Deserialize the JSON string into a state dictionary.

        Args:
            state_str (str): The JSON string representation of the state.

        Returns:
            dict: The deserialized state dictionary.

        Example:
            >>> serialized = '{"messages": [{"type": "HumanMessage", "content": "Hello!", "additional_kwargs": {}, "response_metadata": null}]}'
            >>> deserialized = storage._deserialize_state(serialized)
            >>> print(deserialized)
            {'messages': [{'type': 'HumanMessage', 'content': 'Hello!', 'additional_kwargs': {}, 'response_metadata': None}]}
        """
        state = json.loads(state_str)
        messages = []
        last_tool_call_ids = set()

        for msg in state.get("messages", []):
            try:
                msg_type = msg["type"]

                if msg_type == "SystemMessage":
                    messages.append(
                        SystemMessage(
                            content=msg["content"], **msg["additional_kwargs"]
                        )
                    )

                elif msg_type == "HumanMessage":
                    messages.append(
                        HumanMessage(content=msg["content"], **msg["additional_kwargs"])
                    )

                elif msg_type == "AIMessage":
                    kwargs = msg["additional_kwargs"]
                    tool_calls_raw = kwargs.get("tool_calls", [])

                    if tool_calls_raw:
                        kwargs["tool_calls"] = [
                            ToolCall(
                                id=tc["id"],
                                name=tc["name"],
                                args=(
                                    json.loads(tc["args"])
                                    if isinstance(tc["args"], str)
                                    else tc["args"]
                                ),
                            )
                            for tc in tool_calls_raw
                        ]
                        last_tool_call_ids = {tc["id"] for tc in tool_calls_raw}
                    else:
                        last_tool_call_ids = set()

                    messages.append(AIMessage(content=msg["content"], **kwargs))

                elif msg_type == "ToolMessage":
                    tool_call_id = msg.get("tool_call_id")
                    if not tool_call_id:
                        raise ValueError("ToolMessage missing required 'tool_call_id'")

                    if tool_call_id not in last_tool_call_ids:
                        print(
                            f"[SQLitePlugin] Skipping ToolMessage with unmatched tool_call_id: {tool_call_id}"
                        )
                        continue

                    kwargs = msg.get("additional_kwargs", {}).copy()
                    kwargs["tool_call_id"] = tool_call_id
                    messages.append(ToolMessage(content=msg["content"], **kwargs))

                else:
                    raise ValueError(f"Unknown message type: {msg_type}")

            except Exception as e:
                print(f"[SQLitePlugin] Failed to parse message: {msg}. Error: {e}")

        return {"messages": messages}

    def load_state(self, key: str) -> Optional[dict]:
        """
        Load the state for the given key.

        Args:
            key (str): The composite key (session_id:thread_id).

        Returns:
            Optional[dict]: The state if it exists, or {"messages": []} if not.

        Example:
            >>> storage.save_state({"messages": []}, "session1:thread1")
            >>> state = storage.load_state("session1:thread1")
            >>> print(state)
            {'messages': []}
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT state FROM conversation_state WHERE key = ?", (key,))
            result = cursor.fetchone()
            if result:
                state = self._deserialize_state(result[0])
                return state
        except Exception as e:
            print(f"[SQLitePlugin] Failed to load state for {key}: {e}")
        return {"messages": []}

    def save_state(self, state: dict, key: str) -> None:
        """
        Save the state for the given key.

        Args:
            state (dict): The state to save.
            key (str): The composite key (session_id:thread_id).

        Example:
            >>> state = {"messages": [{"type": "HumanMessage", "content": "Hello!"}]}
            >>> storage.save_state(state, key="session1:thread1")
        """
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO conversation_state (key, state)
                VALUES (?, ?)
            """,
                (key, self._serialize_state(sanitize_state(state))),
            )

    def delete_state(self, key: str) -> None:
        """
        Delete the state for the given key.

        Args:
            key (str): The composite key (session_id:thread_id).

        Example:
            >>> storage.save_state({"messages": []}, "session1:thread1")
            >>> storage.delete_state("session1:thread1")
        """
        with self.conn:
            self.conn.execute("DELETE FROM conversation_state WHERE key = ?", (key,))

    def list_keys(self) -> list[str]:
        """
        List all keys in the storage.

        Returns:
            list[str]: A list of all keys in the storage.

        Example:
            >>> storage.save_state({"messages": []}, "session1:thread1")
            >>> storage.save_state({"messages": []}, "session2:thread1")
            >>> keys = storage.list_keys()
            >>> print(keys)
            ['session1:thread1', 'session2:thread1']
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT key FROM conversation_state")
        return [row[0] for row in cursor.fetchall()]

    def close(self) -> None:
        """
        Close the SQLite connection.

        Example:
            >>> storage = SQLitePlugin()
            >>> storage.close()
        """
        self.conn.close()
