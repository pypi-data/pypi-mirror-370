import time
from abc import abstractmethod

from nqs_sdk import TxRequest


class Transaction:
    timestamp: int

    def __init__(self) -> None:
        self.timestamp = int(time.time_ns())

    @abstractmethod
    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest: ...
