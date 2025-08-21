"""
InteractionHandler Module.

This module defines the `InteractionHandler` class, which handles user interaction
logic for the LangGraph-based workflow.
"""

# Standard library imports
import os
import signal
from typing import Optional

# Third-party imports
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from crypto_com_developer_platform_client import Client, Network

# Internal application imports
from crypto_com_agent_client.lib.enums.workflow_enum import Workflow
from crypto_com_agent_client.lib.types.blockchain_config import BlockchainConfig
from crypto_com_agent_client.lib.utils.storage import Storage
from crypto_com_agent_client.lib.utils.token_usage import print_workflow_token_usage


class InteractionHandler:
    """
    The `InteractionHandler` class manages user interactions with the LangGraph workflow.
    It handles state management, user input processing, and response generation.

    Attributes:
        app (CompiledStateGraph): The compiled LangGraph workflow.
        storage (Storage): The storage backend for persisting workflow state.
        blockchain_config (BlockchainConfig): Configuration for blockchain interactions.
        debug_logging (bool): Flag to control debug logging output.

    Example:
        >>> handler = InteractionHandler(
        ...     app=compiled_workflow,
        ...     storage=storage_instance,
        ...     blockchain_config=blockchain_config,
        ...     debug_logging=True
        ... )
        >>> response = handler.interact("Hello!", thread_id=42)
    """

    def __init__(
        self,
        app: CompiledStateGraph,
        storage: Storage,
        blockchain_config: BlockchainConfig,
        debug_logging: bool = False,
    ) -> None:
        """
        Initialize the InteractionHandler.

        Args:
            app (CompiledStateGraph): The compiled LangGraph workflow.
            storage (Storage): The storage backend for persisting workflow state.
            blockchain_config (BlockchainConfig): Configuration for blockchain interactions.
            debug_logging (bool): Enable/disable debug logging for interactions.
        """
        self.app: CompiledStateGraph = app
        self.storage: Storage = storage
        self.blockchain_config: BlockchainConfig = blockchain_config
        self.debug_logging: bool = debug_logging

    def _get_chain_id_from_developer_platform(self) -> Optional[str]:
        """
        Get chain ID from Crypto.com Developer Platform with configurable timeout.

        Returns:
            Optional[str]: The chain ID if successful, None otherwise.
        """

        def timeout_handler(signum, frame):
            raise TimeoutError("API call timed out")

        try:
            # Get API key from blockchain config
            api_key = self.blockchain_config.api_key

            if not api_key:
                if self.debug_logging:
                    print("Warning: API key is not available in blockchain config")
                return None

            # Initialize the client with the API key
            Client.init(api_key=api_key)

            # Set up timeout using the configurable timeout from blockchain_config
            timeout_seconds = self.blockchain_config.timeout
            original_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)

            if self.debug_logging:
                print(
                    f"Using timeout of {timeout_seconds} seconds for developer platform API call"
                )

            try:
                # Get the chain ID
                chain_id_response = Network.chain_id()

                # Cancel the timeout
                signal.alarm(0)
                signal.signal(signal.SIGALRM, original_handler)

                if self.debug_logging:
                    print(
                        f"Chain ID response from developer platform: {chain_id_response}"
                    )

                # Extract the actual chain ID from the response
                # Expected response format: {'status': 'Success', 'data': {'chainId': '338'}}
                if isinstance(chain_id_response, dict):
                    # Check if the response has a 'data' field with 'chainId'
                    if "data" in chain_id_response and isinstance(
                        chain_id_response["data"], dict
                    ):
                        chain_id = chain_id_response["data"].get("chainId")
                    else:
                        chain_id = chain_id_response.get("chainId")

                    if chain_id is None:
                        if self.debug_logging:
                            print(
                                f"Could not extract chainId from response: {chain_id_response}"
                            )
                        return None

                    return str(chain_id)
                else:
                    # If it's already a simple value, return it as string
                    return str(chain_id_response)

            except (TimeoutError, Exception) as e:
                # Cancel the timeout
                signal.alarm(0)
                signal.signal(signal.SIGALRM, original_handler)
                raise e

        except Exception as e:
            if self.debug_logging:
                print(f"Error getting chain ID from developer platform: {e}")
            return None

    def interact(self, user_input: str, thread_id: int) -> str:
        """
        Processes user input and returns the generated response.

        Args:
            user_input (str): The user's input message.
            thread_id (int, optional): A thread ID for contextual execution.

        Returns:
            str: The response generated by the workflow.

        Raises:
            ValueError: If the workflow graph is not initialized.
        """
        if not self.app:
            raise ValueError("The workflow graph is not initialized.")

        # Load state from storage or initialize it
        state = self.storage.load_state(thread_id)

        # Track initial message count to identify new messages
        initial_message_count = len(state.get("messages", []))

        # Add user input as a HumanMessage
        state[Workflow.Messages].append(HumanMessage(content=user_input))

        # Initialise other state variables
        # Get chainId from the developer platform via api-key
        chain_id = self._get_chain_id_from_developer_platform()
        if chain_id is None:
            # Fallback to blockchain config if developer platform is unavailable
            chain_id = getattr(self.blockchain_config, "chainId", None)
            if self.debug_logging:
                print("Using fallback chain ID from blockchain config")

            # If still None, use a reasonable default (Cronos EVM Testnet)
            if chain_id is None:
                chain_id = "338"  # Cronos EVM Testnet
                if self.debug_logging:
                    print(f"Using default chain ID fallback: {chain_id}")

        state[Workflow.ChainID] = chain_id
        state[Workflow.PrivateKey] = self.blockchain_config.private_key
        state[Workflow.SSOWalletURL] = self.blockchain_config.sso_wallet_url

        # Debug log to confirm chain_id is set correctly
        if self.debug_logging:
            print(f"State chain_id set to: {chain_id}")

        # Optional workflow configuration
        config = (
            {Workflow.Configurable: {Workflow.ThreadID: thread_id}}
            if thread_id
            else {Workflow.ThreadID: 42}
        )

        # Show workflow start marker if debug logging is enabled
        if self.debug_logging:
            print("+" * 50)
            print("🚀 WORKFLOW STARTED")
            print("+" * 50)

        # Execute the workflow
        final_state = self.app.invoke(state, config=config)

        # Track token usage for this user request only
        messages = final_state.get("messages", [])
        new_messages = messages[initial_message_count:]

        # Only track and log token usage if debug logging is enabled
        if self.debug_logging:
            print_workflow_token_usage(new_messages)

        # Save updated state to storage
        self.storage.save_state(final_state, thread_id)

        # Extract and return the final response
        return final_state[Workflow.Messages][-1].content
