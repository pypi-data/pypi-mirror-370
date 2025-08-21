import os
from decimal import Decimal

from nqs_sdk import quantlib

from ..protocol_infos import ProtocolInfos


class CEXPair:
    token0: str
    token1: str
    decimals0: int
    decimals1: int
    opening_fee: Decimal
    max_leverage: int
    maintenance_margin_ratio: Decimal

    def __init__(
        self,
        token0: str,
        token1: str,
        opening_fee: float | Decimal,
        max_leverage: int,
        maintenance_margin_ratio: float | Decimal,
    ) -> None:
        data_source = quantlib.QuantlibDataProvider(os.getenv("QUANTLIB_CONFIG"))
        token0_info = data_source.token_info("Ethereum", token0)
        token1_info = data_source.token_info("Ethereum", token1)

        assert token0_info is not None, f"Token {token0} not found"
        assert token1_info is not None, f"Token {token1} not found"

        self.decimals1 = int(token1_info.decimals)
        self.decimals0 = int(token0_info.decimals)

        self.token0 = token0
        self.token1 = token1
        self.opening_fee = Decimal(opening_fee)
        self.max_leverage = max_leverage
        self.maintenance_margin_ratio = Decimal(maintenance_margin_ratio)


class CEXMarkets(ProtocolInfos):
    pairs: list[CEXPair]

    def __init__(self, pairs: list[CEXPair]) -> None:
        self.pairs = pairs

    @property
    def name(self) -> str:
        return "cex"

    @property
    def factory_id(self) -> str:
        return "cex"

    def get_token_infos(self) -> dict[str, int]:
        return {pair.token0: pair.decimals0 for pair in self.pairs} | {
            pair.token1: pair.decimals1 for pair in self.pairs
        }
