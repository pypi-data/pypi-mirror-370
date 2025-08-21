from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from nqs_sdk import Metrics, RefSharedState, SimulationClock, TxRequest
from nqs_sdk.bindings.tx_generators.abstract_transaction import Transaction
from nqs_sdk.interfaces.tx_generator import TxGenerator


class RandomTxGenerator(TxGenerator, ABC):
    def __init__(self) -> None:
        self.run_cache: bool = False

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
    def get_next_block(self, current_block: int) -> Optional[int]:
        pass

    def next(
        self, clock: SimulationClock, state: RefSharedState, metrics: Metrics
    ) -> Tuple[List[TxRequest], Optional[int]]:
        current_block = clock.current_block()

        txns = []
        for tx in self.get_transactions(start_block=current_block, end_block=current_block):
            # use fixed address for performance reasons
            txns.append(
                tx.to_tx_request(
                    protocol=self.protocol_id,
                    source="Masao",
                    sender="0xD1CECA5E0907304f45Af5cAf3B0cbeC84CF9c92f",
                    order=2.0,  # order is 0.0 for arbitrage, 1.0 for agents and 2.0 for random
                )
            )
        return txns, None

    def __str__(self) -> str:
        return f"{self.protocol_id}_random_tx_generator"
