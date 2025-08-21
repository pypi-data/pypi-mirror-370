import math
from decimal import Decimal
from typing import Tuple


# Maximum tick value for Uniswap V3 pools
MAX_TICK = 887272


class InvalidPriceError(ValueError):
    """Raised when price value is invalid (not strictly positive and finite)."""

    pass


def price_to_tick(price: Decimal, decimals0: int, decimals1: int, tick_spacing: int = 1, lower: bool = True) -> int:
    """
    Convert a price to a tick value for Uniswap V3.

    Args:
        price: The price to convert (must be strictly positive and finite)
        decimals0: Number of decimals for token0
        decimals1: Number of decimals for token1
        tick_spacing: Spacing between valid ticks (default: 1)
        lower: Whether to round down (True) or up (False) when between ticks

    Returns:
        The corresponding tick value

    Raises:
        InvalidPriceError: When the price is not strictly positive and finite
                          (e.g., negative, zero, infinity, or NaN)
    """
    # Validate that price is strictly positive and finite
    if price <= 0 or not price.is_finite():
        raise InvalidPriceError(f"Price must be strictly positive and finite, got: {price}")

    # Compute tick as log base sqrt(1.0001) of sqrt_price
    ic = price.scaleb(decimals1 - decimals0).sqrt().ln() / Decimal("1.0001").sqrt().ln()

    if lower:
        tick = max(math.floor(round(ic) / tick_spacing) * tick_spacing, -MAX_TICK)
    else:
        tick = min(math.ceil(round(ic) / tick_spacing) * tick_spacing, MAX_TICK)

    return tick


def tick_to_price(tick: int, decimals0: int, decimals1: int) -> Decimal:
    return (Decimal(1.0001) ** tick).scaleb(-(decimals1 - decimals0))


def price_to_sqrtp(p: Decimal) -> int:
    return int(p.sqrt() * Decimal("2") ** 96)


def calculate_max_amounts(
    price_lower: Decimal, price: Decimal, price_upper: Decimal, amount0: Decimal, amount1: Decimal
) -> Decimal:
    """
    Calculate the maximum liquidity that can be minted for a Uniswap V3 position.

    This function determines the maximum amount of liquidity that can be created
    from the available token amounts (amount0 and amount1) for a concentrated
    liquidity position with specified price bounds.

    Args:
        price_lower (Decimal): Lower price bound of the position (must be positive)
        price (Decimal): Current price of the pool (must be positive)
        price_upper (Decimal): Upper price bound of the position (must be > price_lower)
        amount0 (Decimal): Available amount of token0 (must be >= 0)
        amount1 (Decimal): Available amount of token1 (must be >= 0)

    Returns:
        Decimal: Maximum liquidity that can be minted with the given token amounts

    Raises:
        AssertionError: If any of the following conditions are not met:
            - amount0 >= 0
            - amount1 >= 0
            - price_lower < price_upper
            - calculated liquidity >= 0

    Notes:
        The calculation depends on where the current price falls relative to the position bounds:

        - If price <= price_lower: Only token0 is needed, liquidity is limited by amount0
        - If price_lower < price < price_upper: Both tokens are needed, liquidity is limited
          by whichever token provides less liquidity
        - If price >= price_upper: Only token1 is needed, liquidity is limited by amount1

        This follows the standard Uniswap V3 concentrated liquidity formulas:
        - L = Δx / (1/√P - 1/√P_upper) for token0
        - L = Δy / (√P - √P_lower) for token1

    Example:
        >>> from decimal import Decimal
        >>> price_lower = Decimal('1.5')
        >>> price = Decimal('2.0')
        >>> price_upper = Decimal('2.5')
        >>> amount0 = Decimal('100')
        >>> amount1 = Decimal('200')
        >>> liquidity = calculate_max_amounts(price_lower, price, price_upper, amount0, amount1)
    """
    assert amount0 >= 0
    assert amount1 >= 0

    sqrt_price_lower = price_lower.sqrt()
    sqrt_price = price.sqrt()
    sqrt_price_upper = price_upper.sqrt()

    assert sqrt_price_lower < sqrt_price_upper

    if sqrt_price <= sqrt_price_lower:
        liquidity = amount0 / (1 / sqrt_price_lower - 1 / sqrt_price_upper)
    elif sqrt_price < sqrt_price_upper:
        liquidity_0 = amount0 / (1 / sqrt_price - 1 / sqrt_price_upper)
        liquidity_1 = amount1 / (sqrt_price - sqrt_price_lower)
        liquidity = min(liquidity_0, liquidity_1)
    else:
        liquidity = amount1 / (sqrt_price_upper - sqrt_price_lower)

    assert liquidity >= 0

    return liquidity


def token_amounts_from_liquidity(
    price_lower: Decimal, price: Decimal, price_upper: Decimal, liquidity_amount: Decimal
) -> Tuple[Decimal, Decimal]:
    assert liquidity_amount >= 0

    sqrt_price_lower = price_lower.sqrt()
    sqrt_price = price.sqrt()
    sqrt_price_upper = price_upper.sqrt()

    token0_amount = Decimal(0)
    token1_amount = Decimal(0)

    if sqrt_price <= sqrt_price_lower:
        token0_amount = liquidity_amount * (1 / sqrt_price_lower - 1 / sqrt_price_upper)
    elif sqrt_price >= sqrt_price_upper:
        token1_amount = liquidity_amount * (sqrt_price_upper - sqrt_price_lower)
    else:
        token0_amount = liquidity_amount * (1 / sqrt_price - 1 / sqrt_price_upper)
        token1_amount = liquidity_amount * (sqrt_price - sqrt_price_lower)

    return token0_amount, token1_amount


def calculate_optimal_rebalancing(
    price_lower: Decimal, price: Decimal, price_upper: Decimal, amount0: Decimal, amount1: Decimal
) -> tuple[Decimal, Decimal]:
    sqrt_price_lower = price_lower.sqrt()
    sqrt_price = price.sqrt()
    sqrt_price_upper = price_upper.sqrt()

    x_unit = (sqrt_price_upper - sqrt_price) / (sqrt_price * sqrt_price_upper)
    y_unit = sqrt_price - sqrt_price_lower

    v_wallet = amount0 * price + amount1
    v_unit = x_unit * price + y_unit
    n_units = v_wallet / v_unit

    x_pos = n_units * x_unit
    y_pos = n_units * y_unit

    return x_pos, y_pos


def get_tick_spacing(fee_tier: Decimal) -> int:
    """
    Get the tick spacing for a given fee tier using string formatting with controlled precision.
    """
    # cf https://support.uniswap.org/hc/en-us/articles/20904283758349-What-are-fee-tiers
    fee_to_tick_spacing = {
        Decimal("0.01"): 1,  # 0.01%
        Decimal("0.05"): 10,  # 0.05%
        Decimal("0.30"): 60,  # 0.3%
        Decimal("1.00"): 200,  # 1%
    }

    if fee_tier in fee_to_tick_spacing:
        return fee_to_tick_spacing[fee_tier]

    valid_fees = ", ".join(str(key) for key in fee_to_tick_spacing.keys())
    raise ValueError(f"Unrecognized fee tier: {fee_tier}. Valid fee tiers are: [{valid_fees}]")
