from typing import Any, List, Optional, Tuple

from nqs_sdk import Metrics, MutBuilderSharedState, MutSharedState, SimulationClock, TxRequest
from nqs_sdk.bindings.protocols.protocol_infos import ProtocolInfos
from nqs_sdk.interfaces.protocol import Protocol
from nqs_sdk.interfaces.protocol_factory import ProtocolFactory
from nqs_sdk.interfaces.protocol_metafactory import ProtocolMetaFactory
from nqs_sdk.interfaces.tx_generator import TxGenerator

from .cex_market import CEXMarkets
from .cex_protocol import CEX


class CEXMarginCheckTxGenerator(TxGenerator):
    def __init__(self, markets: CEXMarkets) -> None:
        self.previous_price = None
        self.markets = markets

    def id(self) -> str:
        return "cex_margin_check"

    def next(
        self, clock: SimulationClock, state: MutSharedState, metrics: Metrics
    ) -> Tuple[List[TxRequest], Optional[int]]:
        # generate a transaction with the current price at each block
        """parameters = states.get_parameters()
        #metric_spots
        current_price = metrics.get(
        previous_price = self.previous_price
        self.previous_price = current_price
        check_tx = CheckMarginPositionTransaction(previous_price)
        return [check_tx.to_tx_request(protocol="cex", source="cex", sender=agent_id)], 1"""
        return [], None


class CEXDefaultFactory(ProtocolFactory):
    def __init__(self, markets: dict[str, CEXMarkets]) -> None:
        self.name = "cex"
        self.markets = markets

    def id(self) -> str:
        return self.name

    def build(
        self,
        clock: SimulationClock,
        builder_state: MutBuilderSharedState,
        common_config: Any,
        backtest: bool,
        config: Any,
    ) -> Tuple[List[Protocol], List[TxGenerator]]:
        return [CEX(markets) for markets in self.markets.values()], [
            CEXMarginCheckTxGenerator(markets) for markets in self.markets.values()
        ]


class CEXFactory(ProtocolMetaFactory):
    def __init__(self) -> None:
        self.name = "cex"
        self.protocols: dict[str, CEXMarkets] = {}

    def register_protocol(self, protocol: ProtocolInfos) -> None:
        assert isinstance(protocol, CEXMarkets), "Protocol must be an instance of UniswapV3Pool"
        assert protocol.name not in self.protocols, "Protocol already registered"

        self.protocols[protocol.name] = protocol

    def id(self) -> str:
        return self.name

    def get_config(self) -> dict[str, Any]:
        config: dict[str, Any] = {
            "cex": {},
        }

        return config

    def get_factories(self) -> list[Any]:
        return [CEXDefaultFactory(self.protocols)]
