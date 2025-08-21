import json
from enum import Enum
from pathlib import Path
from typing import Dict, TypedDict

from web3 import Web3


# enum of chain ids
class ChainId(Enum):
    CRONOS_EVM = 25
    CRONOS_EVM_TESTNET = 338
    CRONOS_ZKEVM = 388
    CRONOS_ZKEVM_TESTNET = 240


# Explorer URLs for each chain
EXPLORER_API: Dict[ChainId, str] = {
    ChainId.CRONOS_EVM: "https://explorer-api.cronos.org/mainnet",
    ChainId.CRONOS_EVM_TESTNET: "https://explorer-api.cronos.org/testnet",
    ChainId.CRONOS_ZKEVM: "https://explorer-api.zkevm.cronos.org",
    ChainId.CRONOS_ZKEVM_TESTNET: "https://explorer-api.testnet.zkevm.cronos.org",
}

EXPLORER_URL: Dict[ChainId, str] = {
    ChainId.CRONOS_EVM: "https://explorer.cronos.org",
    ChainId.CRONOS_EVM_TESTNET: "https://explorer.cronos.org/testnet",
    ChainId.CRONOS_ZKEVM: "https://explorer.zkevm.cronos.org",
    ChainId.CRONOS_ZKEVM_TESTNET: "https://explorer.zkevm.cronos.org/testnet",
}

# Default RPC URLs for each chain
DEFAULT_RPC_URLS: Dict[ChainId, str] = {
    ChainId.CRONOS_EVM: "https://evm.cronos.org",
    ChainId.CRONOS_EVM_TESTNET: "https://evm-t3.cronos.org",
    ChainId.CRONOS_ZKEVM: "https://mainnet.zkevm.cronos.org",
    ChainId.CRONOS_ZKEVM_TESTNET: "https://testnet.zkevm.cronos.org",
}

# Router contract addresses for each chain id
ROUTER_ADDRESS: Dict[int, str] = {
    ChainId.CRONOS_EVM: "0x66C0893E38B2a52E1Dc442b2dE75B802CcA49566",  # Mainnet Router
    ChainId.CRONOS_EVM_TESTNET: "0xC74C960708f043E04a84038c6D1136EA7Fcb16a1",  # Testnet Router
    ChainId.CRONOS_ZKEVM: "0x4E792B8c9bcB9E200C3713810C4D6eA8C4230E7c",  # ZK Mainnet Router
    ChainId.CRONOS_ZKEVM_TESTNET: "0x9EB4db2E31259444c5C2123bec8B17a510C4c72B",  # ZK Testnet Router
}

# Wrapped native token contract addresses for each chain id
WRAPPER_ADDRESS: Dict[int, str] = {
    ChainId.CRONOS_EVM: "0x5C7F8A570d578ED84E63fdFA7b1eE72dEae1AE23",  # Mainnet WCRO
    ChainId.CRONOS_EVM_TESTNET: "0x6a3173618859c7cd40faf6921b5e9eb6a76f1fd4",  # Testnet WCRO
    ChainId.CRONOS_ZKEVM: "0xC1bF55EE54E16229d9b369a5502Bfe5fC9F20b6d",  # Mainnet wzkCRO
    ChainId.CRONOS_ZKEVM_TESTNET: "0xeD73b53197189BE3Ff978069cf30eBc28a8B5837",  # Testnet wzkCRO
}


def load_abi(filename: str) -> list:
    path = Path(__file__).parent / filename
    with open(path, "r") as f:
        return json.load(f)


# ABI mapping using JSON files
WRAPPER_ABI_MAPPING: Dict[ChainId, list] = {
    ChainId.CRONOS_EVM: load_abi("wCRO_ABI.json"),
    ChainId.CRONOS_EVM_TESTNET: load_abi("wCRO_ABI.json"),  # Using same ABI for testnet
    ChainId.CRONOS_ZKEVM: load_abi("wzkCRO_ABI.json"),
    ChainId.CRONOS_ZKEVM_TESTNET: load_abi(
        "wzkCRO_ABI.json"
    ),  # Using same ABI for testnet
}

ROUTER_ABI = load_abi("router_ABI.json")
ERC20_ABI = load_abi("erc20_ABI.json")
FACTORY_ABI = load_abi("factory_ABI.json")

id_string = "id"
name_string = "name"
explorerUrl_string = "explorerUrl"
rpc_string = "rpc"
routerAddress_string = "routerAddress"
routerAbi_string = "routerAbi"
wrapperAddress_string = "wrapperAddress"
wrapperAbi_string = "wrapperAbi"
erc20Abi_string = "erc20Abi"
explorerBaseUrl_string = "explorerBaseUrl"
factoryAbi_string = "factoryAbi"


class Chain(TypedDict):
    """Type definition for chain information"""

    id: ChainId
    name: str
    explorerUrl: str
    rpc: str
    routerAddress: str
    routerAbi: list
    wrapperAddress: str
    wrapperAbi: list
    erc20Abi: list
    explorerBaseUrl: str
    factoryAbi: list


# Complete chain information
CHAIN_INFO: Dict[ChainId, Chain] = {
    ChainId.CRONOS_EVM: {
        id_string: ChainId.CRONOS_EVM.value,
        name_string: "Cronos EVM Mainnet",
        explorerUrl_string: EXPLORER_API[ChainId.CRONOS_EVM],
        rpc_string: DEFAULT_RPC_URLS[ChainId.CRONOS_EVM],
        routerAddress_string: ROUTER_ADDRESS[ChainId.CRONOS_EVM],
        routerAbi_string: ROUTER_ABI,
        wrapperAddress_string: WRAPPER_ADDRESS[ChainId.CRONOS_EVM],
        wrapperAbi_string: WRAPPER_ABI_MAPPING[ChainId.CRONOS_EVM],
        erc20Abi_string: ERC20_ABI,
        explorerBaseUrl_string: EXPLORER_URL[ChainId.CRONOS_EVM],
        factoryAbi_string: FACTORY_ABI,
    },
    ChainId.CRONOS_EVM_TESTNET: {
        id_string: ChainId.CRONOS_EVM_TESTNET.value,
        name_string: "Cronos EVM Testnet",
        explorerUrl_string: EXPLORER_API[ChainId.CRONOS_EVM_TESTNET],
        rpc_string: DEFAULT_RPC_URLS[ChainId.CRONOS_EVM_TESTNET],
        routerAddress_string: ROUTER_ADDRESS[ChainId.CRONOS_EVM_TESTNET],
        routerAbi_string: ROUTER_ABI,
        wrapperAddress_string: WRAPPER_ADDRESS[ChainId.CRONOS_EVM_TESTNET],
        wrapperAbi_string: WRAPPER_ABI_MAPPING[ChainId.CRONOS_EVM_TESTNET],
        erc20Abi_string: ERC20_ABI,
        explorerBaseUrl_string: EXPLORER_URL[ChainId.CRONOS_EVM_TESTNET],
        factoryAbi_string: FACTORY_ABI,
    },
    ChainId.CRONOS_ZKEVM: {
        id_string: ChainId.CRONOS_ZKEVM.value,
        name_string: "Cronos ZK EVM Mainnet",
        explorerUrl_string: EXPLORER_API[ChainId.CRONOS_ZKEVM],
        rpc_string: DEFAULT_RPC_URLS[ChainId.CRONOS_ZKEVM],
        routerAddress_string: ROUTER_ADDRESS[ChainId.CRONOS_ZKEVM],
        routerAbi_string: ROUTER_ABI,
        wrapperAddress_string: WRAPPER_ADDRESS[ChainId.CRONOS_ZKEVM],
        wrapperAbi_string: WRAPPER_ABI_MAPPING[ChainId.CRONOS_ZKEVM],
        erc20Abi_string: ERC20_ABI,
        explorerBaseUrl_string: EXPLORER_URL[ChainId.CRONOS_ZKEVM],
        factoryAbi_string: FACTORY_ABI,
    },
    ChainId.CRONOS_ZKEVM_TESTNET: {
        id_string: ChainId.CRONOS_ZKEVM_TESTNET.value,
        name_string: "Cronos ZK EVM Testnet",
        explorerUrl_string: EXPLORER_API[ChainId.CRONOS_ZKEVM_TESTNET],
        rpc_string: DEFAULT_RPC_URLS[ChainId.CRONOS_ZKEVM_TESTNET],
        routerAddress_string: ROUTER_ADDRESS[ChainId.CRONOS_ZKEVM_TESTNET],
        routerAbi_string: ROUTER_ABI,
        wrapperAddress_string: WRAPPER_ADDRESS[ChainId.CRONOS_ZKEVM_TESTNET],
        wrapperAbi_string: WRAPPER_ABI_MAPPING[ChainId.CRONOS_ZKEVM_TESTNET],
        erc20Abi_string: ERC20_ABI,
        explorerBaseUrl_string: EXPLORER_URL[ChainId.CRONOS_ZKEVM_TESTNET],
        factoryAbi_string: FACTORY_ABI,
    },
}


def get_chain_helpers(state: dict):
    """
    Get chain helpers using the chain_id from state.

    Args:
        state (dict): The workflow state containing chain_id and private_key

    Returns:
        tuple: (Web3 instance, Account instance, chain info)
    """
    chain_id = state["chain_id"]
    private_key = state["private_key"]

    # If chain id is not an integer or not in [e.value for e in ChainId]
    if not isinstance(int(chain_id), int) or int(chain_id) not in [
        e.value for e in ChainId
    ]:
        raise ValueError(
            f"Chain ID {chain_id} is not a valid ChainId, only {[e.value for e in ChainId]} are supported"
        )

    chain_info = CHAIN_INFO[ChainId(int(chain_id))]
    rpc_url = chain_info[rpc_string]

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    account = w3.eth.account.from_key(private_key)
    return w3, account, chain_info
