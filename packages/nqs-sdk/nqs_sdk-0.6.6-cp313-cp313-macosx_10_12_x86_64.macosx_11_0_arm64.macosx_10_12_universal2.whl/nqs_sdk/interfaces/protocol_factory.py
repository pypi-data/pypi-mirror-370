from abc import ABC, abstractmethod
from typing import Any, List, Tuple

from nqs_sdk.nqs_sdk import MutBuilderSharedState, SimulationClock

from .protocol import Protocol
from .tx_generator import TxGenerator


class ProtocolFactory(ABC):
    @abstractmethod
    def id(self) -> str: ...

    def simulation_schema(self) -> str:
        return "{}"

    def backtest_schema(self) -> str:
        return "{}"

    def common_schema(self) -> str:
        return "{}"

    @abstractmethod
    def build(
        self,
        clock: SimulationClock,
        builder_state: MutBuilderSharedState,
        common_config: Any,
        backtest: bool,
        config: Any,
    ) -> Tuple[List[Protocol], List[TxGenerator]]: ...
