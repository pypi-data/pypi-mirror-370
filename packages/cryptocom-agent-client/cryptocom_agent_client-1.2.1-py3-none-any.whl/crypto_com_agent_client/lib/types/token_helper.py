"""
Token mappings for different chains.
"""

from typing import Dict

from web3 import Web3

from crypto_com_agent_client.lib.types.chain_helper import erc20Abi_string, id_string

# Chain ID: 25 (Cronos EVM zkEVM)
CRONOS_MAINNET_TOKENS: Dict[str, str] = {
    "WCRO": "0x5C7F8A570d578ED84E63fdFA7b1eE72dEae1AE23",
    "WETH": "0xe44Fd7fCb2b1581822D0c862B68222998a0c299a",
    "WBTC": "0x062E66477Faf219F25D27dCED647BF57C3107d52",
    "USDC": "0xc21223249CA28397B4B6541dfFaEcC539BfF0c59",
    "USDT": "0x66e428c3f67a68878562e79A0234c1F83c208770",
    "RNDR": "0xEaEA1a708DaB6f732E35F06588293204318ac48F",
    "1INCH": "0xEea900FE18F77593C7D7C105fBa9bd714164AC95",
    "JASMY": "0x227EdF65f866255A0ED4B5b453fe43A41182EC3A",
    "COMP": "0x4Fb1af9D09DB3fbbda96071EaE0aeae6E871F9AC",
    "ANKR": "0x1FE0f470736548794b47AFe5613d3A309d964d3c",
    "YGG": "0xfF9620d9F80F80056cbE4Bb84403a9E9C5174213",
    "PAXG": "0x81749e7258f9e577f61f49ABeeB426b70F561b89",
    "OGN": "0x78E9974A74d6c980De4E3F8039248320c5A2d714",
    "AR": "0xeB6B3AEdA7A2705fAC5e2350fA4D71a64b393b37",
    "GLMR": "0x268B344bF8bbCd9Dd4e4FA68264309B05F15820a",
    "ACA": "0x213E6fb02009c13692bAA23C63FdE8D623d22705",
    "SPS": "0x1B554fda68bA95924E5bbD0BaF8e769F039e775B",
    "CKB": "0x5dEED46f39c485bA03b61d83763d0f6357dc4737",
    "VOXEL": "0x5fdbFE38E050829374001630B8710BDd05Ea55C0",
    "KRL": "0x62E622fa4E180C391f2E089FC1d5eA7AdCB96575",
    "IRIS": "0xd27FC10235E41Ba8c70652Ed833460949Ed2B882",
    "CANTO": "0x83E8B8C435C594e0aBa30910f725c5186B2455a0",
    "TIA": "0x982b59aaE4f0BC66960b4BF06d6fE96b9F33d3F7",
    "JUNO": "0x8f45Cc102D6ad9502CC305E5590b4d5c844b2DD7",
    "CHESS": "0xA263eB1747007111e9801797D711f31D9B734f38",
    "CSPR": "0x15a9e70f166BcaAA7bfF094d865cE5aAa73A2A58",
    "EGLD": "0x5c54Cc9A7abeD2dd102361c142417756Fb157292",
    "EPX": "0x15C65aD983F4E5814595953808C8616f867d061c",
    "ETC": "0xd9ce64C200721a98103102f9ea8e894E347EA287",
    "FIL": "0x7d7130B0B4733D603Cea12628b52067ce8458058",
    "FITFI": "0xcD7d4cB8a8B4810Fb740A42E344513d49e0AC11f",
    "HOD": "0x68D43230470c67BeB61e00a6E8EC869F947365fD",
    "ICX": "0xf6726cEBd173CF30926B69087179E18489183422",
    "JOE": "0xC7f14C5E9365533b151bc29901cbcBF8B07af6e3",
    "BEAT": "0x39B9f8B9c0F37766dB1592F0294E01a39B52D46c",
    "ACS": "0x8011182dE19A1dA2CDAf80a66562b6E4aC746Fe1",
    "MIR": "0x6ED54B7d694625d6652FE801A3e996D70C20fd5d",
    "BOSON": "0x813EFfe620c71Bd1b522a8E6FA74C0e46C80DA2E",
    "RARE": "0xD1c530d427E0421Cc585B23644c8a7A261699e3b",
    "MC": "0x0FBe22186FC31CD4220f81Aea7480bC6cF4FC001",
    "SNT": "0x7e0497443D42Ae5CADcB69740FB80E02be7FDC1f",
    "GAL": "0x13928f9d15698CFb6A29e648219D56606776a906",
    "ACH": "0x4168Ec9022C39d4d41513F26A7b0ca489d73549c",
    "REP": "0xc48b39cD739cF638471082F5574856306943f054",
    "GODS": "0xa63e52B8D4adc613729BaF384b0001A1701Ed0C1",
    "UNFI": "0x920e031B66d2Deb9965618c915Bab3833744078B",
    "MXC": "0x4547f6417499F87BF74193fc7EEde3fF0492AE00",
    "POND": "0x446D15794b136c20595cdc7B4A33A935E1d0B630",
    "LOKA": "0x6BD07C35b4D53613e7B8910B2c457C02A688D58C",
    "OGV": "0x95acd10B399d5679C33d7BE4614a8aD1e8dd33C2",
    "OLE": "0x97a21A4f05b152a5D3cDf6273EE8b1d3D8fa8E40",
    "ANML": "0xdFD509F81864664533351ae0533fc790414fe35d",
    "PRQ": "0x0dE43564B9279fd94b1Fea72694E0D02D69223a0",
    "ZED": "0x06780b8f6625721875e8a0f0397d9377bf1b1b71",
    "BONE": "0xaae84acbfd07c8650dd9dacc99c068ab420d0327",
    "FLOKI": "0xBf2C2a77Be1974853228EFB858e7e0547bbd686D",
    "COS": "0xEb540106a1e006F6010fAe45Dc94ee5F4800D66d",
    "TOMI": "0x0369302aabbbe58443b3f17fa0b0d05d5dc9cb4e",
    "PEPE": "0xf868c454784048AF4f857991583E34243c92Ff48",
    "LMWR": "0x0DdB6540aFD29b14F7E02D1292BD675b5Ceea896",
    "LADYS": "0x8540384C996056F1902c9785D85260612eb9Dc29",
    "AXL": "0xB4E667FE769F36117bc259E05435c906EF4c1EeC",
    "FET": "0xBe2bd41D6b3fBe01eda6e1AddeD7a4b242e04528",
    "AGIX": "0x753053956Bd46cFe000B0968d41f887149B19c41",
    "DORA": "0x96b4C4b43976C6a1453A215AEaC82Ed0eb9B38f2",
    "GOAT": "0xE7a2fFA3463c4e7Cab1907e5Ad8071Fa656d8391",
    "POPCAT": "0xA8D3288f4FE8650EC038c398Fc65B7c93540cc10"
}

# Chain ID: 338 (Cronos EVM Testnet)
CRONOS_EVM_TESTNET_TOKENS: Dict[str, str] = {
}

# Chain ID: 388 (Cronos zkEVM)
CRONOS_ZKEVM_TOKENS: Dict[str, str] = {
    "WZKCRO": "0xC1bF55EE54E16229d9b369a5502Bfe5fC9F20b6d",
    "YBETH": "0xf226a595b83056ff3D26b827e3d5b0896E4392a9",
    "VUSD": "0x5b91e29Ae5A71d9052620Acb813d5aC25eC7a4A2",
    "VETH": "0x271602A97027ee1dd03b1E6e5dB153eB659A80b1",
    "YBUSD": "0xb1Ece5b548766215272BAFCfa36396B06Cd9e4C9",
}

# Chain ID: 240 (Cronos zkEVM Testnet)
CRONOS_ZKEVM_TESTNET_TOKENS: Dict[str, str] = {
    "WZKCRO": "0xeD73b53197189BE3Ff978069cf30eBc28a8B5837",
    "YBETH": "0x962871c572F9C542Bba2Aa94841516b621A08a79",
    "VUSD": "0x9553dA89510e33BfE65fcD71c1874FF1D6b0dD75",
    "VETH": "0x16a9Df93DEc0A559CdBAC00cB9E3a1BA91Bf6906",
    "YBUSD": "0x7055ee4c4798871B618eD39f01F81906A48C4358",
}

# Mapping of chain IDs to token lists
CHAIN_TOKEN_MAPPINGS = {
    25: CRONOS_MAINNET_TOKENS,
    338: CRONOS_EVM_TESTNET_TOKENS,
    388: CRONOS_ZKEVM_TOKENS,
    240: CRONOS_ZKEVM_TESTNET_TOKENS,
}


def get_token_address_from_mapping(chain_info: dict, symbol: str) -> str:
    """Get token address by chain ID and symbol."""

    if chain_info[id_string] not in CHAIN_TOKEN_MAPPINGS:
        raise ValueError(f"Chain ID {chain_info[id_string]} not supported")

    token_list = CHAIN_TOKEN_MAPPINGS[chain_info[id_string]]

    if symbol.upper() not in token_list:
        raise ValueError(f"Token {symbol} not found on chain {chain_info[id_string]}, try using token address instead")

    return token_list[symbol.upper()]


def get_token_symbol_from_contract(w3: Web3, chain_info: dict, address: str) -> str:
    """Get token symbol by chain ID and address."""
    try:
        token_contract = w3.eth.contract(address=address, abi=chain_info[erc20Abi_string])
    except Exception as e:
        raise ValueError(f"Error getting token {address}, please double check the token address")
    return token_contract.functions.symbol().call()


def parse_token(w3: Web3, chain_info: dict, token_symbol_or_address: str) -> dict:
    """Parse token symbol or address."""
    if Web3.is_address(token_symbol_or_address):
        symbol = get_token_symbol_from_contract(w3, chain_info, token_symbol_or_address)
        token_info = {"chain_id": chain_info[id_string], "address": token_symbol_or_address, "symbol": symbol}
        return token_info
    else:
        address = get_token_address_from_mapping(chain_info, token_symbol_or_address)
        symbol = get_token_symbol_from_contract(w3, chain_info, address)
        token_info = {"chain_id": chain_info[id_string], "address": address, "symbol": symbol}
        return token_info
