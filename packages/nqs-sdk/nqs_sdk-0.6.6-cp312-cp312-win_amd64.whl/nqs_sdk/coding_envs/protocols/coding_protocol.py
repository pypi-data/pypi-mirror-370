from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from nqs_sdk.bindings.protocols.protocol_infos import ProtocolInfos
from nqs_sdk.bindings.tx_generators.abstract_transaction import Transaction
from nqs_sdk.interfaces.protocol_metafactory import ProtocolMetaFactory
from nqs_sdk.interfaces.tx_generator import TxGenerator


class CodingProtocol(ABC):
    def __init__(self, protocol: ProtocolInfos) -> None:
        self.observables: dict[str, list[pd.Series]] = {}
        self.protocol = protocol

        self.transactions: dict[str, list[Transaction]] = {}

        self.all_agents: list[str] = []

        # variables representing the current state
        self.current_agent: str = ""
        self.current_block: int = 0
        self.current_time: Optional[datetime] = None

    @abstractmethod
    def id(self) -> str:
        """Returns the id of the protocol"""
        pass

    @abstractmethod
    def get_protocol_factory(self) -> Optional[ProtocolMetaFactory]:
        """Returns the protocol factory"""
        pass

    @abstractmethod
    def get_protocol_description(self) -> tuple[str, str, list[str]]:
        """Returns the description of the protocol, the market description and the coding interface"""
        pass

    @abstractmethod
    def get_tx_generators(self) -> list[TxGenerator]:
        """Returns the list of all tx generators"""
        pass

    @abstractmethod
    def get_observables_names(self) -> list[str]:
        """Returns the list of all observables names"""
        pass

    def _get_obs_timeserie(self, observable: str, lookback: Optional[timedelta] = None) -> pd.Series:
        if self.current_time is None:
            return pd.Series()

        lookback_time = self.current_time
        if lookback is not None:
            lookback_time = self.current_time - lookback

        data = self.observables.get(observable, None)
        if data is None:
            return pd.Series()

        return data.loc[lookback_time:]

    def get_transactions(self) -> dict[str, list[Transaction]]:
        return self.transactions

    def clear_transactions(self) -> None:
        self.transactions.clear()

    def register_transaction(self, agent_name: str, transaction: Transaction) -> None:
        if agent_name not in self.transactions:
            self.transactions[agent_name] = []
        self.transactions[agent_name].append(transaction)

    def set_all_agents(self, all_agents: list[str]) -> None:
        self.all_agents = all_agents

    def set_current_agent(self, agent: str) -> None:
        self.current_agent = agent

    def set_current_block(self, block: int) -> None:
        self.current_block = block

    def set_current_time(self, time: datetime) -> None:
        self.current_time = time

    def update_observables(self, observables: dict[str, pd.Series]) -> None:
        self.observables = observables
