from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from nqs_sdk import Metrics, RefSharedState, SimulationClock, TxRequest
from nqs_sdk.bindings.tx_generators.abstract_transaction import Transaction
from nqs_sdk.interfaces.tx_generator import TxGenerator


class HistoricalTxGenerator(TxGenerator, ABC):
    def __init__(self) -> None:
        self.run_cache: bool = False
        self.previous_block: Optional[int] = None

    def id(self) -> str:
        return self.protocol_id

    @property
    @abstractmethod
    def protocol_id(self) -> str:
        pass

    @abstractmethod
    def get_transactions(self, start_block: int, end_block: int) -> list[Transaction]:
        pass

    @abstractmethod
    def cache_transactions(self, start_block: int, end_block: int) -> None:
        pass

    @abstractmethod
    def get_next_block(self, current_block: int) -> Optional[int]:
        pass

    def next(
        self, clock: SimulationClock, state: RefSharedState, metrics: Metrics
    ) -> Tuple[List[TxRequest], Optional[int]]:
        current_block = clock.current_block()

        if self.previous_block is None:
            self.previous_block = current_block

        if not self.run_cache:
            simulation_time = clock.simulation_time()
            self.cache_transactions(start_block=simulation_time.start_block(), end_block=simulation_time.stop_block())
            self.run_cache = True

        txns = []
        for tx in self.get_transactions(start_block=self.previous_block, end_block=current_block):
            txns.append(
                tx.to_tx_request(
                    protocol=self.protocol_id,
                    source="Masao",
                    sender="0x999999cf1046e68e36E1aA2E0E07105eDDD1f08E",
                    order=2.0,  # order is 0.0 for arbitrage, 1.0 for agents and 2.0 for random
                )
            )

        self.previous_block = current_block

        return (
            txns,
            self.get_next_block(current_block),
        )

    def __str__(self) -> str:
        return f"{self.protocol_id}_historical_tx_generator"
