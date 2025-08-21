"""
Exchange-related tools for the Crypto.com Exchange platform.
"""

from crypto_com_developer_platform_client import Exchange
from langchain_core.tools import tool


@tool
def get_all_tickers() -> str:
    """
    Get all available tickers from the Crypto.com Exchange.

    This function retrieves information about all available trading pairs
    and their current market data from the Crypto.com Exchange.

    Returns:
        str: A formatted string containing information about all available tickers.

    Example:
        >>> tickers = get_all_tickers()
        >>> print(tickers)
        All tickers: {...}
    """
    tickers = Exchange.get_all_tickers()
    return f"All tickers: {tickers}"


@tool
def get_ticker_by_instrument(instrument_name: str) -> str:
    """
    Get ticker information for a specific trading instrument.

    This function retrieves current market data for a specified trading instrument
    from the Crypto.com Exchange.

    Args:
        instrument_name (str): The name of the trading instrument (e.g., "BTC_USDT").

    Returns:
        str: A formatted string containing the ticker information for the specified instrument.

    Raises:
        ValueError: If instrument_name is empty or None.

    Example:
        >>> ticker = get_ticker_by_instrument("BTC_USDT")
        >>> print(ticker)
        Ticker information for BTC_USDT: {...}
    """
    if not instrument_name:
        raise ValueError("Instrument name is required")

    ticker = Exchange.get_ticker_by_instrument(instrument_name)
    return f"Ticker information for {instrument_name}: {ticker}"
