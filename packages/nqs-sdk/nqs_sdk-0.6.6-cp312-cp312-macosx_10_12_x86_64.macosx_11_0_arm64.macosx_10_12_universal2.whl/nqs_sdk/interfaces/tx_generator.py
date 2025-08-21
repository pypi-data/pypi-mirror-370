from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from nqs_sdk.nqs_sdk import Metrics, MutSharedState, SimulationClock, TxRequest


class TxGenerator(ABC):
    @abstractmethod
    def id(self) -> str: ...

    @abstractmethod
    def next(
        self, clock: SimulationClock, state: MutSharedState, metrics: Metrics
    ) -> Tuple[List[TxRequest], Optional[int]]: ...
