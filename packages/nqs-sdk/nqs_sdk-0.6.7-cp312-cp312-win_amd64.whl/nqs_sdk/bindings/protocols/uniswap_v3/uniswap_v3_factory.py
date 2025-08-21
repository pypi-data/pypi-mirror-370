from typing import Any

import nqs_sdk
from nqs_sdk.bindings.protocols.protocol_infos import ProtocolInfos
from nqs_sdk.bindings.utils.utils import get_all_tokens
from nqs_sdk.interfaces.protocol_metafactory import ProtocolMetaFactory

from .uniswap_v3_pool import UniswapV3Pool


class UniswapV3Factory(ProtocolMetaFactory):
    def __init__(self) -> None:
        self.protocols: dict[str, UniswapV3Pool] = {}
        self.tokens_metadata = get_all_tokens()

    def register_protocol(self, protocol: ProtocolInfos) -> None:
        assert isinstance(protocol, UniswapV3Pool), "Protocol must be an instance of UniswapV3Pool"
        assert protocol.name not in self.protocols, "Protocol already registered"
        self.protocols[protocol.name] = protocol

    def id(self) -> str:
        return "uniswap_v3"

    def get_config(self) -> dict:
        historical_pools: list[dict[str, Any]] = []
        custom_pools: list[dict[str, Any]] = []

        for protocol in self.protocols.values():
            if protocol.initial_balance is not None:
                custom_pools.append(
                    {
                        "pool_name": protocol.name,
                        "symbol_token0": protocol.token0,
                        "symbol_token1": protocol.token1,
                        "fee_tier": protocol.fee_tier,
                        "initial_balance": {
                            "amount": protocol.initial_balance["amount"],
                            "unit": protocol.initial_balance["unit"],
                        },
                    }
                )
            else:
                historical_pools.append(
                    {
                        "pool_name": protocol.name,
                        "symbol_token0": protocol.token0,
                        "symbol_token1": protocol.token1,
                        "address": protocol.address,
                    }
                )

        config = {
            "uniswap_v3": {
                "initial_state": {
                    "custom_state": {"pools": custom_pools},
                    "historical_state": {"pools": historical_pools},
                }
            }
        }

        return config

    def get_factories(self) -> list[Any]:
        factories: list[Any] = []

        factories.append(nqs_sdk.implementations.uniswap_v3_rust_factory())

        return factories
