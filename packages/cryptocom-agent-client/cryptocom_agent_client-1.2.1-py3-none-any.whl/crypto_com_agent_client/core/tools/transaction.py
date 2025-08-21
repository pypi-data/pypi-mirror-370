"""
Transaction-related tools for the Crypto.com developer platform.
"""

from crypto_com_developer_platform_client import Transaction
from langchain_core.tools import tool


@tool
def get_transaction_by_hash(hash: str) -> str:
    """
    Fetch transaction details using a transaction hash.

    This function retrieves transaction details for the specified hash
    from the Crypto.com developer platform.

    Args:
        hash (str): The hash of the transaction to retrieve.

    Returns:
        str: A formatted string containing the transaction details.

    Example:
        >>> transaction_details = get_transaction_by_hash("0xhash...")
        >>> print(transaction_details)
        Transaction Details: {...}
    """
    transaction = Transaction.get_transaction_by_hash(hash)
    return f"Transaction Details: {transaction}"


@tool
def get_transaction_status(hash: str) -> str:
    """
    Get the current status of a transaction.

    This function retrieves the status of a transaction using its hash
    from the Crypto.com developer platform.

    Args:
        hash (str): The hash of the transaction to check.

    Returns:
        str: A formatted string containing the transaction status.

    Example:
        >>> status = get_transaction_status("0xhash...")
        >>> print(status)
        Transaction Status for 0xhash...: {...}
    """
    status = Transaction.get_transaction_status(hash)
    return f"Transaction Status for {hash}: {status}"
