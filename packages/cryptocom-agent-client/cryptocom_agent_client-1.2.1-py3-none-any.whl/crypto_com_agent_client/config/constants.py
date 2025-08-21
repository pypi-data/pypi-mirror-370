"""
Service Configuration Module.

This module handles the configuration and environment variable loading required for the application.
It sets up constants such as the default AI service provider, the default AI model, and the API client
key for interacting with Crypto.com services.

Constants:
    PROVIDER_DEFAULT (Provider): The default provider for AI services, set to OpenAI.
    MODEL_DEFAULT (str): The default model for AI operations, set to GPT-4.
    LLAMA4_MODEL (str): The default Llama 4 model for Groq provider.
    VERTEXAI_LOCATION_DEFAULT (str): The default location for Vertex AI operations.
"""

# Third-party imports
from dotenv import load_dotenv

# Internal application imports
from crypto_com_agent_client.lib.enums.provider_enum import Provider

# Load environment variables from a .env file
load_dotenv()


PROVIDER_DEFAULT = Provider.OpenAI
"""
The default provider for AI services.

This constant defines the default provider for AI services in the application. By default,
it is set to OpenAI. This value can be overridden by specifying a different provider during
initialization.

Example:
    >>> from lib.enums.model_enum import Provider
    >>> print(PROVIDER_DEFAULT)
    OpenAI
"""

MODEL_DEFAULT = "gpt-4"
"""
The default model to be used for AI operations.

This constant specifies the default AI model to be used in the application. It is set to GPT-4
for the OpenAI provider. This value can be overridden by specifying a different model during
initialization.

Example:
    >>> print(MODEL_DEFAULT)
    gpt-4
"""

LLAMA4_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

VERTEXAI_LOCATION_DEFAULT = "us-west1"
DEFAULT_SYSTEM_INSTRUCTION = """You are an AI assistant specialized in blockchain and cryptocurrency operations, powered by Crypto.com's developer platform. You are helpful, accurate, and secure.

Key capabilities:
- Blockchain/crypto operations: Use tool_dispatcher for wallet operations, balances, transactions, token management
- Tool listing: When asked about capabilities, use tool_dispatcher with list_tools function
- Custom queries: Use the appropriate tool for the query

Always prioritize user security and provide clear warnings for sensitive operations like private keys or transactions."""
"""
The default system instruction for the AI agent.

This constant defines the immutable default system instruction that provides the core
identity and capabilities of the AI agent. It establishes the agent as a blockchain and
cryptocurrency specialist powered by Crypto.com's developer platform.

The instruction covers:
- Core identity as a helpful, accurate, and secure AI assistant
- Key capabilities including blockchain operations and general queries
- Security guidelines for sensitive operations

This instruction serves as the foundation that can be extended with personality settings
and user-specific instructions without compromising the core system behavior.
"""
