"""
Blockchain Config Module.

This module defines the `BlockchainConfig` TypedDict, which represents the
configuration for blockchain-related settings and integrations.
"""

# Third-party imports
from typing import Optional

from pydantic import BaseModel, Field


class BlockchainConfig(BaseModel):
    """
    TypedDict for Blockchain configuration.

    Attributes:
        api_key (str): The API key for the developer platform sdk.
        private_key (Optional[str]): The private key for blockchain transactions.
        sso_wallet_url (Optional[str]): The URL for the SSO wallet service.
        timeout (int): Timeout in seconds for API calls (default: 20).

    Example:
        >>> from lib.types.blockchain_config import BlockchainConfig
        >>> blockchain_config: BlockchainConfig = {
        ...     "api_key": "api-key",
        ...     "sso_wallet_url": "sso-wallet-url",
        ...     "timeout": 30
        ... }
    """

    api_key: str = Field(alias="api-key")
    private_key: Optional[str] = Field(alias="private-key", default=None)
    sso_wallet_url: Optional[str] = Field(alias="sso-wallet-url", default=None)
    timeout: int = Field(default=20, description="Timeout in seconds for API calls")
