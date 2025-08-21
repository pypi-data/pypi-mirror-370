"""
Block-related tools for the Crypto.com developer platform.
"""

from crypto_com_developer_platform_client import Block
from langchain_core.tools import tool


@tool
def get_block_by_tag(tag: str, tx_detail: str = "false") -> str:
    """
    Get block data by tag.

    This function retrieves block data for a specified tag from the
    Crypto.com developer platform.

    Args:
        tag (str): Integer of a block number in hex, or the string "earliest", "latest" or "pending".
        tx_detail (str, optional): If "true", returns full transaction objects; if "false", only transaction hashes.

    Returns:
        str: A formatted string containing the block data.

    Example:
        >>> block_data = get_block_by_tag("latest")
        >>> print(block_data)
        Block data for tag latest: {...}
    """
    block_data = Block.get_by_tag(tag, tx_detail)
    return f"Block data for tag {tag}: {block_data}"
