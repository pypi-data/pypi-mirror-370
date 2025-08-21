"""
DeFi-related tools for the Crypto.com developer platform.
"""
from crypto_com_developer_platform_client import Defi
from crypto_com_developer_platform_client.interfaces.defi_interfaces import DefiProtocol
from langchain_core.tools import tool

from ..types.defi import ProtocolSchema, ProtocolSymbolSchema


@tool(args_schema=ProtocolSchema)
def get_whitelisted_tokens(protocol: str) -> str:
    """
    Get whitelisted tokens for a specific DeFi protocol.

    This function retrieves a list of whitelisted tokens for the specified
    DeFi protocol from the Crypto.com developer platform.

    Args:
        protocol (str): The DeFi protocol name (e.g., "H2", "VVS").

    Returns:
        str: A formatted string containing the list of whitelisted tokens.

    Example:
        >>> tokens = get_whitelisted_tokens("H2")
        >>> print(tokens)
        Whitelisted tokens for H2: {...}
    """
    protocol_enum = DefiProtocol[protocol.upper()]
    tokens = Defi.get_whitelisted_tokens(protocol_enum)
    return f"Whitelisted tokens for {protocol}: {tokens}"


@tool(args_schema=ProtocolSchema)
def get_all_farms(protocol: str) -> str:
    """
    Get all farms for a specific DeFi protocol.

    This function retrieves information about all available farms for the
    specified DeFi protocol from the Crypto.com developer platform.

    Args:
        protocol (str): The DeFi protocol name (e.g., "H2", "VVS").

    Returns:
        str: A formatted string containing information about all farms.

    Example:
        >>> farms = get_all_farms("H2")
        >>> print(farms)
        All farms for H2: {...}
    """
    protocol_enum = DefiProtocol[protocol.upper()]
    farms = Defi.get_all_farms(protocol_enum)
    return f"All farms for {protocol}: {farms}"


@tool(args_schema=ProtocolSymbolSchema)
def get_farm_by_symbol(protocol: str, symbol: str) -> str:
    """
    Get information about a specific farm by its symbol.

    This function retrieves detailed information about a specific farm
    identified by its symbol for the specified DeFi protocol.

    Args:
        protocol (str): The DeFi protocol name (e.g., "H2", "VVS").
        symbol (str): The farm symbol (e.g., "zkCRO-MOON", "CRO-GOLD").

    Returns:
        str: A formatted string containing information about the specific farm.

    Example:
        >>> farm = get_farm_by_symbol("H2", "zkCRO-MOON")
        >>> print(farm)
        Farm information for zkCRO-MOON in H2: {...}
    """
    protocol_enum = DefiProtocol[protocol.upper()]
    farm = Defi.get_farm_by_symbol(protocol_enum, symbol)
    return f"Farm information for {symbol} in {protocol}: {farm}"
