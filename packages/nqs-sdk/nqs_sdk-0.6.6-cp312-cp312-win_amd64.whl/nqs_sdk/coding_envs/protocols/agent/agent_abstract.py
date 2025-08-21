from abc import ABC, abstractmethod
from decimal import Decimal


class AgentAbstract(ABC):
    @abstractmethod
    def get_wallet(self) -> dict[str, Decimal]:
        """Get the wallet of the agent

        Returns:
            dict[str, Decimal]: The wallet of the agent
        """

    @abstractmethod
    def get_wallet_holdings(self, token: str) -> Decimal:
        """Get the wallet holdings for a given token

        Args:
            token (str): The token to get the wallet holdings for

        Returns:
            Decimal: The wallet holdings for the given token
        """
        pass

    @abstractmethod
    def get_total_holding(self) -> Decimal:
        """Get the total holding of the agent

        Returns:
            Decimal: The total holding of the agent
        """
        pass

    @abstractmethod
    def get_total_fees(self) -> Decimal:
        """Get the total fees of the agent

        Returns:
            Decimal: The total fees of the agent
        """
        pass
