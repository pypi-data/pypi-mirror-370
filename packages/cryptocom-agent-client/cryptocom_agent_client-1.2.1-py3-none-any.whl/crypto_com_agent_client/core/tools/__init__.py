"""
Crypto.com developer platform Module.

This module provides tools for interacting with the Crypto.com developer platform.
These tools enable operations such as wallet creation, token balance retrieval,
transaction lookups, token transfers, and ERC20 balance queries. Each tool is
decorated with the `@tool` decorator, making it compatible with LangChain workflows.

Tools:
    Block Tools:
        - get_block_by_tag: Get block information by tag.

    Contract Tools:

    CronosID Tools:
        - resolve_cronosid_name: Resolve a CronosID name to an address.
        - lookup_cronosid_address: Lookup address for a CronosID.

    DeFi Tools:
        - get_all_farms: Get information about all available farms.
        - get_farm_by_symbol: Get farm information by symbol.
        - get_whitelisted_tokens: Get list of whitelisted tokens.

    Exchange Tools:
        - get_all_tickers: Get all available tickers.
        - get_ticker_by_instrument: Get ticker information by instrument.

    General Tools:
        - list_tools: List all available tools with descriptions.

    Token Tools:
        - get_erc20_balance: Get ERC20 token balance for an address.
        - get_native_balance: Get native token balance for an address.
        - swap_token: Swap between tokens.
        - transfer_erc20_token: Transfer ERC20 tokens.
        - transfer_native_token: Transfer native tokens.
        - wrap_token: Wrap tokens.

    Transaction Tools:
        - get_transaction_by_hash: Get transaction details by hash.
        - get_transaction_status: Get transaction status.

    Wallet Tools:
        - create_wallet: Create a new blockchain wallet.
        - get_wallet_balance: Get wallet balance.
        - send_ssowallet: Send using SSO wallet.

Example:
    >>> from core.tools import create_wallet, get_native_balance
    >>> wallet_info = create_wallet()
    >>> print(wallet_info)
    Wallet created! Address: 0x123..., Private Key: abcd...

    >>> balance = get_native_balance("0x123...")
    >>> print(balance)
    The native balance for address 0x123... is 100.0.
"""

from typing import List

from langchain_core.tools import BaseTool

from .block import get_block_by_tag
from .cronosid import lookup_cronosid_address, resolve_cronosid_name
from .defi import get_all_farms, get_farm_by_symbol, get_whitelisted_tokens
from .exchange import get_all_tickers, get_ticker_by_instrument
from .token import (
    get_erc20_balance,
    get_native_balance,
    swap_token,
    transfer_erc20_token,
    transfer_native_token,
    wrap_token,
)
from .transaction import (
    get_transaction_by_hash,
    get_transaction_status,
)
from .wallet import create_wallet, get_wallet_balance, send_ssowallet

# List of all built-in tools
built_in_tools: List[BaseTool] = [
    # Block tools
    get_block_by_tag,
    # CronosID tools
    resolve_cronosid_name,
    lookup_cronosid_address,
    # DeFi tools
    get_all_farms,
    get_farm_by_symbol,
    get_whitelisted_tokens,
    # Exchange tools
    get_all_tickers,
    get_ticker_by_instrument,
    # Token tools
    get_erc20_balance,
    get_native_balance,
    swap_token,
    transfer_erc20_token,
    transfer_native_token,
    wrap_token,
    # Transaction tools
    get_transaction_by_hash,
    get_transaction_status,
    # Wallet tools
    create_wallet,
    get_wallet_balance,
    send_ssowallet,
]
