import nqs_sdk.nqs_sdk
from nqs_sdk.nqs_sdk import ProtocolFactoryAdapter


class UniswapV3Factory:
    def __new__(cls) -> ProtocolFactoryAdapter:
        return nqs_sdk.nqs_sdk.implementations.uniswap_v3_rust_factory()
