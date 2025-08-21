from decimal import Decimal
from typing import Optional

from nqs_sdk.coding_envs.protocols.coding_protocol import CodingProtocol
from nqs_sdk.interfaces.protocol_metafactory import ProtocolMetaFactory
from nqs_sdk.interfaces.tx_generator import TxGenerator

from .agent_abstract import AgentAbstract


class AgentProtocol(CodingProtocol, AgentAbstract):
    def __init__(self, tokens_list: list[str]):
        super().__init__(None)

        self.tokens_list = tokens_list

    def id(self) -> str:
        return "agent"

    def get_protocol_factory(self) -> Optional[ProtocolMetaFactory]:
        return None

    def get_protocol_description(self) -> tuple[str, str, list[str]]:
        import inspect

        return (
            ("Agent is a protocol that allows users to get general information about the status of an agent."),
            (),
            [inspect.getsource(AgentAbstract)],
        )

    def get_tx_generators(self) -> list[TxGenerator]:
        return []

    def get_observables_names(self) -> list[str]:
        metrics_str = []

        for agent in self.all_agents:
            for token in self.tokens_list:
                metrics_str.append(f'{agent}.all.wallet_holdings:{{token="{token}"}}')
            metrics_str.append(f"{agent}.all.total_holding")
            metrics_str.append(f"{agent}.all.total_fees")

        return metrics_str

    def get_wallet(self) -> dict[str, Decimal]:
        """Get the wallet of the agent

        Returns:
            dict[str, Decimal]: The wallet of the agent
        """
        wallet = {}
        for token in self.tokens_list:
            wallet[token] = self.get_wallet_holdings(token)

        return wallet

    def get_wallet_holdings(self, token: str) -> Optional[Decimal]:
        metric = f'{self.current_agent}.all.wallet_holdings:{{token="{token}"}}'
        data = self.observables.get(metric, None)

        if data is None:
            return None

        return data.iloc[-1]

    def get_total_holding(self) -> Optional[Decimal]:
        """Get the total holding of the agent

        Returns:
            Decimal: The total holding of the agent (None if not available)
        """
        total_holding = self._get_obs_timeserie(f"{self.agent_name}.all.total_holding")

        return total_holding.iloc[-1]

    def get_total_fees(self) -> Optional[Decimal]:
        """Get the total fees of the agent

        Returns:
            Decimal: The total fees of the agent (None if not available)
        """
        total_fees = self._get_obs_timeserie(f"{self.agent_name}.all.total_fees")

        return total_fees.iloc[-1]
