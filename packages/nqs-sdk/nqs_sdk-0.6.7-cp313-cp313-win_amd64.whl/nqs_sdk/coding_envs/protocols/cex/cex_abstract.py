from abc import ABC, abstractmethod
from datetime import timedelta
from decimal import Decimal
from typing import Optional


class CexProtocol(ABC):
    """Cex Protocol"""

    @abstractmethod
    def is_pair_available(self, token0: str, token1: str) -> bool:
        """Check if a pair is available."""
        pass

    @abstractmethod
    def pair_max_leverage(self, token0: str, token1: str) -> Optional[int]:
        """Get the maximum leverage for a pair or None if not available."""
        pass

    @abstractmethod
    def pair_opening_fee(self, token0: str, token1: str) -> Optional[float]:
        """Get the opening fee for a pair or None if not available."""
        pass

    @abstractmethod
    def pair_maintenance_margin_ratio(self, token0: str, token1: str) -> Optional[float]:
        """Get the maintenance margin ratio for a pair or None if not available."""
        pass

    @abstractmethod
    def is_margin_position_exists(self, token_id: str) -> bool:
        """Check if the margin position exists.

        Args:
            token_id (str): Token ID of the margin position

        Returns:
            bool: True if the position exists, False otherwise
        """
        pass

    @abstractmethod
    def pair_spot(self, token0: str, token1: str, lookback: Optional[timedelta] = None) -> list[Optional[float]]:
        """Get the spot price of a pair.

        Args:
            token0 (str): Token0
            token1 (str): Token1
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
                If None, returns only the current volume.

        Returns:
            list[Optional[float]]: List of spot prices for the specified pair (values are None if not available)
        """
        pass

    @abstractmethod
    def rebalance(self, token0: str, token1: str, weight0: float | Decimal, weight1: float | Decimal) -> None:
        """Rebalance the portfolio.

        Args:
            token0 (str): Token0
            token1 (str): Token1
            weight0 (float | Decimal): Weight of token0
            weight1 (float | Decimal): Weight of token1

        Returns:
            None
        """
        pass

    @abstractmethod
    def margin_buy(self, token: str, amount: float, collateral: str, collateral_amount: float, token_id: str) -> None:
        """Margin buy a token using a second token as collateral - NOT IMPLEMENTED

        Args:
            token (str): Token to buy
            amount (float): Amount of token to buy
            collateral (str): Collateral token
            collateral_amount (float): Amount of collateral to use
            token_id (str): Token ID of the margin position
        """
        pass

    @abstractmethod
    def add_margin_collateral(self, token_id: str, amount: float) -> None:
        """Add margin collateral - NOT IMPLEMENTED

        Args:
            token_id (str): Token ID of the margin position
            amount (float): Amount of collateral to add
        """
        pass

    @abstractmethod
    def margin_sell(self, token: str, amount: float, collateral: str, collateral_amount: float, token_id: str) -> None:
        """Margin sell a token - NOT IMPLEMENTED

        Args:
            token (str): Token to sell
            amount (float): Amount of token to sell
            collateral (str): Collateral token
            collateral_amount (float): Amount of collateral to use
            token_id (str): Token ID of the margin position
        """
        pass

    @abstractmethod
    def close_margin_position(self, token_id: str) -> None:
        """Close a margin position - NOT IMPLEMENTED

        Args:
            token_id (str): Token ID of the margin position
        """
        pass

    @abstractmethod
    def buy(self, token0: str, token1: str, amount: float) -> None:
        """Buy token0 by selling token1.

        Args:
            token0 (str): Token0
            token1 (str): Token1
            amount (float): Amount of token0 to buy
        """
        pass

    @abstractmethod
    def sell(self, token0: str, token1: str, amount: float) -> None:
        """Sell token0 by buying token1.

        Args:
            token0 (str): Token0
            token1 (str): Token1
            amount (float): Amount of token0 to sell
        """
        pass
