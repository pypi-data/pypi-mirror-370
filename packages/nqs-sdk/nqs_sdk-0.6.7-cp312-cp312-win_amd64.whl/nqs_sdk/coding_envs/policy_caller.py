from abc import ABC, abstractmethod

from .protocols.coding_protocol import CodingProtocol


class PolicyCaller(ABC):
    @abstractmethod
    def policy(self, block: int, agent: CodingProtocol, protocols: dict[str, CodingProtocol]) -> None:
        pass
