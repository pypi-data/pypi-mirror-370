from abc import ABC, abstractmethod
from typing import Any

from nqs_sdk.nqs_sdk import MutSharedState, SimulationClock, TxRequest


class Protocol(ABC):
    @abstractmethod
    def id(self) -> str: ...

    @abstractmethod
    def build_tx_payload(self, source: str, sender: str, call: Any) -> TxRequest: ...

    @abstractmethod
    def execute_tx(self, clock: SimulationClock, states: MutSharedState, tx: TxRequest) -> None: ...
