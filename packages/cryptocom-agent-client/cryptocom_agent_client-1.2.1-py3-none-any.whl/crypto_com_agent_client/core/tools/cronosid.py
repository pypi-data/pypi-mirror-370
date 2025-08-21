"""
CronosId-related tools for the Crypto.com developer platform.
"""

from crypto_com_developer_platform_client import CronosId
from langchain_core.tools import tool


@tool
def resolve_cronosid_name(name: str) -> str:
    """
    Resolve a CronosId name to its corresponding blockchain address.

    This function resolves a given CronosId name to its associated blockchain
    address using the Crypto.com developer platform.

    Args:
        name (str): The CronosId name to resolve (e.g., "xyz.cro").

    Returns:
        str: A formatted string containing the resolved blockchain address.

    Example:
        >>> address = resolve_cronosid_name("xyz.cro")
        >>> print(address)
        Resolved address for xyz.cro: {...}
    """
    address = CronosId.resolve_name(name)
    return f"Resolved address for {name}: {address}"


@tool
def lookup_cronosid_address(address: str) -> str:
    """
    Lookup a blockchain address to find its associated CronosId name.

    This function looks up a given blockchain address to find the associated
    CronosId name using the Crypto.com developer platform.

    Args:
        address (str): The blockchain address to lookup.

    Returns:
        str: A formatted string containing the CronosId name.

    Example:
        >>> cronosid = lookup_cronosid_address("0x123...")
        >>> print(cronosid)
        CronosId for address 0x123...: {...}
    """
    cronosid = CronosId.lookup_address(address)
    return f"CronosId for address {address}: {cronosid}"
