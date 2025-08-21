"""
Wallet-related tools for the Crypto.com developer platform.
"""

from typing import Annotated

from crypto_com_developer_platform_client import Wallet
from langgraph.prebuilt import InjectedState

from crypto_com_agent_client.lib.enums.workflow_enum import Workflow
from langchain_core.tools import tool


@tool
def create_wallet() -> str:
    """
    Create a new wallet and return its address and private key.

    This function interacts with the Crypto.com developer platform to create a new
    blockchain wallet. It retrieves the wallet's address and private key.

    Returns:
        str: A formatted string containing the wallet's address and private key.

    Example:
        >>> wallet_info = create_wallet()
        >>> print(wallet_info)
        Wallet created! Address: 0x123..., Private Key: abcd...
    """
    wallet = Wallet.create_wallet()
    return f"Wallet created! Address: {wallet['data']['address']}, Private Key: {wallet['data']['privateKey']}"


@tool
def get_wallet_balance(address: str) -> str:
    """
    Get the balance of a wallet.

    This function retrieves the balance of a specified wallet address
    using the Crypto.com developer platform.

    Args:
        address (str): The address to get the balance for (e.g., "xyz.cro").

    Returns:
        str: A formatted string containing the wallet balance.

    Example:
        >>> balance = get_wallet_balance("0x123...")
        >>> print(balance)
        Balance for wallet 0x123...: {...}
    """
    balance = Wallet.get_balance(address)
    return f"Balance for wallet {address}: {balance}"


@tool
def send_ssowallet(
    state: Annotated[dict, InjectedState], receiver: str, amount: int, data: str = "0x"
) -> str:
    """
    Generate a URL for SSO wallet transfer.

    This function generates a URL that can be used to initiate a token transfer
    through the SSO wallet interface. If "null" is specified as the receiver,
    it will use the null address (0x0000000000000000000000000000000000000000).

    Args:
        receiver (str): The recipient's blockchain address or "null" for null address.
        amount (int): The amount of tokens to transfer in Wei.
        data (str, optional): Additional data for the transfer. Defaults to "0x".

    Returns:
        str: A formatted URL for the SSO wallet transfer.

    Example:
        >>> url = send_ssowallet("null", 1)  # Send 1 Wei to null address
        >>> print(url)
        http://your-sso-wallet-url/transfer-token?recipient=0x0000000000000000000000000000000000000000&amount=1&data=0x
        >>> url = send_ssowallet("0x123...", 1000000000000000000)  # 1 ETH in Wei
        >>> print(url)
        http://your-sso-wallet-url/transfer-token?recipient=0x123...&amount=1000000000000000000&data=0x
    """
    sso_wallet_url = state[Workflow.SSOWalletURL]
    base_url = f"{sso_wallet_url}/transfer-token"

    # Handle null address case
    if receiver.lower() == "null":
        receiver = "0x" + "0" * 40  # Creates 0x0000000000000000000000000000000000000000

    url = f"{base_url}?recipient={receiver}&amount={amount}&data={data}"
    return url
