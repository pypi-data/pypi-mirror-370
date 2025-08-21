from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from nqs_sdk.nqs_sdk import MetricName, SealedParameters, SimulationClock


class ObservableConsumer(ABC):
    @abstractmethod
    def initialize(self, parameters: SealedParameters) -> None: ...

    @abstractmethod
    def consume(
        self, parameters: SealedParameters, clock: SimulationClock
    ) -> Tuple[List[MetricName], Optional[int]]: ...
