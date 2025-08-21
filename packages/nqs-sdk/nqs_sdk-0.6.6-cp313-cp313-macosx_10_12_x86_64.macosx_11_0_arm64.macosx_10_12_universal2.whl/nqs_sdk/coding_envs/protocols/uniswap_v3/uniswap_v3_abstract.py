import datetime
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional

import pandas


class UniswapV3Protocol(ABC):
    """Uniswap V3 Protocol"""

    @property
    @abstractmethod
    def token0(self) -> str:
        """Get the name of the token0 of the pool."""
        pass

    @property
    @abstractmethod
    def token1(self) -> str:
        """Get the name of the token1 of the pool."""

    @property
    @abstractmethod
    def fee_tier(self) -> float:
        """Get the fee tier of the pool."""
        pass

    @abstractmethod
    def is_position_exists(self, token_id: str) -> bool:
        """Check if the position exists.

        Args:
            token_id (str): Token ID of the position

        Returns:
            bool: True if the position exists, False otherwise
        """
        pass

    @abstractmethod
    def dex_spot(self, lookback: Optional[datetime.timedelta] = None) -> Optional[pandas.Series]:
        """Get the price of token0 in units of token1.

        Args:
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
                If None, returns only the current price.

        Returns:
            pandas.Series: the series of spot prices (i.e. the price of token0 in units of token1)
                (None if not available).
        """
        pass

    @abstractmethod
    def liquidity(self, lookback: Optional[datetime.timedelta] = None) -> Optional[pandas.Series]:
        """Get the liquidity parameter in the pool for the current tick.

        Args:
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
                If None, returns only the current liquidity.

        Returns:
            pandas.Series: the series of liquidity values (None if not available)
        """
        pass

    @abstractmethod
    def total_volume_numeraire(self, lookback: Optional[datetime.timedelta] = None) -> Optional[pandas.Series]:
        """Get the total volume of swaps in the pool in units of the user numeraire.

        Args:
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
            If None, returns only the current volume.

        Returns:
            pandas.Series: Series of total volume in numeraire (None if not available)
        """
        pass

    @abstractmethod
    def total_volume(self, token: bool, lookback: Optional[datetime.timedelta] = None) -> Optional[pandas.Series]:
        """Get the total volume of swaps in the pool for the specified token.

        Args:
            token (bool): False for token0, True for token1
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
                If None, returns only the current volume.

        Returns:
            pandas.Series: Series of total volume for the specified token (None if not available)
        """
        pass

    @abstractmethod
    def total_holdings(self, token: bool, lookback: Optional[datetime.timedelta] = None) -> Optional[pandas.Series]:
        """Get the total holdings of the specified token in the pool.

        Args:
            token (bool): False for token0, True for token1
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
                If None, returns only the current volume.

        Returns:
            pandas.Series: Series of total holdings for the specified token (None if not available)
        """
        pass

    @abstractmethod
    def total_fees(
        self, token: Optional[bool] = None, lookback: Optional[datetime.timedelta] = None
    ) -> Optional[pandas.Series]:
        """Get the total fees in the pool.

        Args:
            token (Optional[bool]): False for token0, True for token1. If None, returns fees in numeraire.
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
                If None, returns only the current fees.

        Returns:
            pandas.Series: Series of total fees (in token units if token specified, otherwise in numeraire)
                (None if not available).
        """
        pass

    @abstractmethod
    def total_value_locked(self, lookback: Optional[datetime.timedelta] = None) -> Optional[pandas.Series]:
        """Get the total value locked in the pool in units of the user numeraire.

        Args:
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
                If None, returns only the current value locked.

        Returns:
            pandas.Series: Series of total value locked (None if not available)
        """
        pass

    @abstractmethod
    def get_tick(self, lookback: Optional[datetime.timedelta] = None) -> Optional[pandas.Series]:
        """Get the tick of the pool.

        Args:
            lookback (Optional[datetime.timedelta]): Return all data included in the lookback period.
            If None, returns only the current tick.

        Returns:
            pandas.Series: Series of tick values (None if not available)
        """
        pass

    @abstractmethod
    def swap(
        self,
        amount: float,
        token: bool,
        price_limit: Optional[float] = None,
        wallet: Optional[dict[str, Decimal]] = None,
    ) -> Optional[dict[str, Decimal]]:
        """Swap or exchange tokens in the pool. At least one of the arguments should be provided.

        Args:
            amount (float): The amount of token to be swapped.
            token (bool): True for swapping token1 to token0, False for swapping token0 to token1.
            price_limit (Optional[float]): The price limit for the swap. If None, the swap is done at the current price.
        """
        pass

    @abstractmethod
    def mint(
        self,
        price_lower: float | Decimal,
        price_upper: float | Decimal,
        max_token0: float | Decimal,
        max_token1: float | Decimal,
        token_id: str,
    ) -> Optional[dict[str, Decimal]]:
        """Uniswap V3 minting enables users to provide (add) liquidity within specific price ranges.

        Args:
            price_lower (float): The lower price of the liquidity range.
            price_upper (float): The upper price of the liquidity range.
            max_token0 (float): The maximum amount of token0 to be used.
            max_token1 (float): The maximum amount of token1 to be used.
            token_id (str): A string identifier of the position.
        """
        pass

    @abstractmethod
    def burn(self, amount_ratio: float, token_id: str) -> None:
        """Uniswap v3 burn is the burning of LP tokens, when users can effectively withdraw liquidity
        from specific price ranges within Uniswap V3 liquidity pools.

        Args:
            amount_ratio (float): Amount of liquidity to be burned (between 0.0 and 1.0 where 1.0 represent all
            the liquidity of the position).
            token_id (str): The id of position to be burned.
        """
        pass

    @abstractmethod
    def active_liquidity(self, position: Optional[str] = None) -> Optional[Decimal]:
        """Get liquidity that is currently active in the pool.

        Args:
            position (str, optional): Position ID to get specific position's active liquidity.
                If None, returns user's total active liquidity.

        Returns:
            Decimal: Active liquidity amount at the requested block number
        """
        pass

    @abstractmethod
    def position_liquidity(self, position: str) -> Optional[Decimal]:
        """Get total liquidity allocated in the pool

        Args:
            position (str): Position ID to get specific user position's active liquidity.

        Returns:
            Optional[Decimal]: Total liquidity amount for the pool or a specific user position
                (None if not available)
        """
        pass

    @abstractmethod
    def token_amount(self, token: str, position: Optional[str] = None) -> Optional[Decimal]:
        """Get actual token amount in the pool.

        Args:
            token (str): str to query amount for
            position (str, optional): Position ID to get specific position's token amount.
                If None, returns user's total token amount.

        Returns:
            Decimal: Amount of specified token at the requested block number
        """
        pass

    @abstractmethod
    def net_position(self, position: str) -> Optional[Decimal]:
        """Get the value of agent's position in the pool.

        Args:
            position (str): Position ID to query

        Returns:
            Decimal: Position value in units of numeraire at the requested block number
        """
        pass

    @abstractmethod
    def fees_collected(self, token: Optional[str] = None, position: Optional[str] = None) -> Optional[Decimal]:
        """Get collected fees.

        Args:
            token (str, optional): str to query fees for
            position (str, optional): Position ID to get specific position's fees.
                If None, returns user's total collected fees.

        Returns:
            Decimal: Amount of collected fees in specified token or numeraire at the requested block number
        """
        pass

    @abstractmethod
    def fees_not_collected(self, token: Optional[str] = None, position: Optional[str] = None) -> Optional[Decimal]:
        """Get uncollected fees.

        Args:
            token (str, optional): str to query fees for
            position (str, optional): Position ID to get specific position's fees.
                If None, returns user's total uncollected fees.

        Returns:
            Decimal: Amount of uncollected fees in specified token or numeraire at the requested block number
        """
        pass

    @abstractmethod
    def abs_impermanent_loss(self, position: Optional[str] = None) -> Optional[Decimal]:
        """Get absolute impermanent loss.

        Args:
            position (str, optional): Position ID to get specific position's IL.
                If None, returns IL for all user's open positions.

        Returns:
            Decimal: Impermanent loss in units of numeraire at the requested block number
        """
        pass

    @abstractmethod
    def perc_impermanent_loss(self, position: Optional[str] = None) -> Optional[Decimal]:
        """Get impermanent loss as a percentage.

        Args:
            position (str, optional): Position ID to get specific position's IL.
                If None, returns IL percentage for all user's open positions.
        Returns:
            Decimal: Impermanent loss as a percentage
        """
        pass

    @abstractmethod
    def static_ptf_value(self, position: Optional[str] = None) -> Optional[Decimal]:
        """Get value of the static portfolio.

        Args:
            position (str, optional): Position ID to get specific position's value.
                If None, returns value for all user's open positions.

        Returns:
            Decimal: Static portfolio value in numeraire at the requested block number
        """
        pass

    @abstractmethod
    def permanent_loss(self, position: Optional[str] = None) -> Optional[Decimal]:
        """Get realized/permanent loss.

        Args:
            position (str, optional): Position ID to get specific position's loss.
                If None, returns loss for all user's open positions.

        Returns:
            Decimal: Permanent loss in units of numeraire at the requested block number
        """
        pass

    @abstractmethod
    def loss_versus_rebalancing(self, position: Optional[str] = None) -> Optional[Decimal]:
        """Get loss compared to rebalancing strategy.

        Args:
            position (str, optional): Position ID to get specific position's LVR.
                If None, returns LVR for all user's open positions.

        Returns:
            Decimal: Loss versus rebalancing in units of numeraire at the requested block number
        """
        pass

    @abstractmethod
    def total_fees_relative_to_lvr(self, position: Optional[str] = None) -> Optional[Decimal]:
        """Get total accumulated fees as percentage of LVR.

        Args:
            position (str, optional): Position ID to get specific position's relative fees.
                If None, returns relative fees for all user's open positions.

        Returns:
            Decimal: Fees as percentage of loss versus rebalancing at the requested block number
        """
        pass

    @abstractmethod
    def position_bounds(self, position: str) -> tuple[Optional[Decimal], Optional[Decimal]]:
        """Get price bounds of a position.

        Args:
            position (str): Position ID to query

        Returns:
            tuple[Decimal, Decimal]: Lower and upper price bounds of the position
        """
        pass
