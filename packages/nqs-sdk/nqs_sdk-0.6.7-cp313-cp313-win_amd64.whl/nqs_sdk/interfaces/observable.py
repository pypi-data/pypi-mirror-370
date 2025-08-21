from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional

from nqs_sdk.nqs_sdk import (
    MetricName,
    ObservableDescription,
    Parameters,
    RefSharedState,
    SealedParameters,
    SimulationClock,
)


class Observable(ABC):
    @abstractmethod
    def register(self, parameter: Parameters) -> None: ...

    @abstractmethod
    def describe(self, parameter: SealedParameters) -> ObservableDescription: ...

    @abstractmethod
    def observe(
        self, metrics: Optional[List[MetricName]], clock: SimulationClock, state: RefSharedState
    ) -> dict[MetricName, Decimal]: ...
