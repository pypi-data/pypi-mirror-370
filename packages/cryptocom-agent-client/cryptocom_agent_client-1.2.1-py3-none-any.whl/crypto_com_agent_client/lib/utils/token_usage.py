"""
Token Usage and Debug Logging Utilities.

This module provides utilities for tracking token usage and debug logging
for LLM interactions in the Crypto.com Agent Client.
"""

from typing import Any, Dict, List, Optional

from langchain_core.messages import BaseMessage


def get_content_preview(content: str, max_length: int = 100) -> str:
    """
    Create a preview of message content with truncation if needed.

    Args:
        content (str): The message content to preview
        max_length (int): Maximum length before truncation (default: 100)

    Returns:
        str: Content preview with "..." if truncated
    """
    return content[:max_length] + "..." if len(content) > max_length else content


def print_model_debug_info(
    selected_messages: List[BaseMessage],
    response: BaseMessage,
    debug_logging: bool = False
) -> None:
    """
    Print debug information about model input and response.

    This function provides detailed logging of messages sent to the LLM,
    including message types, content previews, tool calls, and token usage.

    Args:
        selected_messages (List[BaseMessage]): List of messages sent to the model
        response (BaseMessage): Response received from the model
        debug_logging (bool): Whether to enable debug logging output

    Example:
        >>> from crypto_com_agent_client.lib.utils.token_usage import print_model_debug_info
        >>> print_model_debug_info(messages, response, debug_logging=True)
    """
    if not debug_logging:
        return

    print(f"\n{'=' * 50}")
    print(f"Messages sent to model ({len(selected_messages)} messages):")
    print(f"{'=' * 50}")

    # Track seen messages to avoid duplicates
    seen_messages = set()

    for i, message in enumerate(selected_messages):
        message_type = type(message).__name__

        # Create a unique identifier for the message to detect duplicates
        message_id = f"{message_type}_{hash(str(message.content)[:100])}"

        # Skip if we've already seen this exact message
        if message_id in seen_messages:
            continue
        seen_messages.add(message_id)

        if message_type == "AIMessage":
            # Check if this is a tool call or content response
            if hasattr(message, 'tool_calls') and message.tool_calls:
                # This is a tool call AIMessage
                print(f"   {i+1}. [AIMessage - Tool Call]")
                for j, tool_call in enumerate(message.tool_calls):
                    print(f"        - Function: {tool_call.get('name', 'Unknown')} | Args: {tool_call.get('args', {})} | ID: {tool_call.get('id', 'N/A')}")
            else:
                # This is a content response AIMessage
                content_preview = get_content_preview(message.content)
                print(f"   {i+1}. [AIMessage] {content_preview}")
        elif message_type == "ToolMessage":
            # This is a tool execution result
            content_preview = get_content_preview(message.content)
            print(f"   {i+1}. [ToolMessage] {content_preview}")
        else:
            # Handle other message types (SystemMessage, HumanMessage, etc.)
            content_preview = get_content_preview(message.content)
            print(f"   {i+1}. [{message_type}] {content_preview}")

    # Extract input token count from response metadata
    input_tokens = response.response_metadata.get("token_usage", {}).get("prompt_tokens", "N/A")
    output_tokens = response.response_metadata.get("token_usage", {}).get("completion_tokens", "N/A")

    print("-" * 50)
    print(f"INPUT TOKENS:  {input_tokens}")
    print(f"OUTPUT TOKENS: {output_tokens}")


def print_workflow_token_usage(new_messages: List[BaseMessage]) -> None:
    """
    Print token usage from new messages and log the summary.

    This function is only called when debug logging is enabled, so it always
    logs the token usage summary.

    Args:
        new_messages (List[BaseMessage]): New messages from the current workflow execution

    Example:
        >>> from crypto_com_agent_client.lib.utils.token_usage import print_workflow_token_usage
        >>> print_workflow_token_usage(new_messages)
    """
    # Initialize cumulative usage for this request
    total_input_tokens = 0
    total_output_tokens = 0
    model_call_count = 0

    # Accumulate token usage from new messages
    for message in new_messages:
        usage_metadata = getattr(message, 'usage_metadata', {})
        if usage_metadata:
            input_tokens = usage_metadata.get('input_tokens', 0)
            output_tokens = usage_metadata.get('output_tokens', 0)

            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            model_call_count += 1

    # Log summary (always enabled since this function is only called when debug_logging=True)
    print('\n')
    print("=" * 50)
    print("📊 Cumulative Token Usage Summary")
    print("=" * 50)
    total_tokens = total_input_tokens + total_output_tokens
    print(f"TOTAL INPUT TOKENS:  {total_input_tokens}")
    print(f"TOTAL OUTPUT TOKENS: {total_output_tokens}")
    print(f"TOTAL TOKENS:        {total_tokens}")
    print(f"MODEL CALL COUNT:    {model_call_count}")

    if model_call_count > 0:
        avg_input = total_input_tokens / model_call_count
        avg_output = total_output_tokens / model_call_count
        print(f"AVG INPUT/CALL:      {avg_input:.1f}")
        print(f"AVG OUTPUT/CALL:     {avg_output:.1f}")

    print("+" * 50)
    print("🏁 WORKFLOW COMPLETED")
    print("+" * 50)
    print('\n')
