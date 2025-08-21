from decimal import ROUND_DOWN, Decimal

from nqs_sdk import TxRequest
from nqs_sdk.bindings.protocols.uniswap_v3.uniswap_utils import (
    get_tick_spacing,
    price_to_tick,
)
from nqs_sdk.bindings.protocols.uniswap_v3.uniswap_v3_pool import UniswapV3Pool
from nqs_sdk.bindings.tx_generators.abstract_transaction import Transaction


class RawMintTransaction(Transaction):
    tick_lower: int | str
    tick_upper: int | str
    amount: int | str
    token_id: str | None

    def __init__(self, tick_lower: int | str, tick_upper: int | str, amount: int | str, token_id: str | None = None):
        super().__init__()

        self.tick_lower = tick_lower
        self.tick_upper = tick_upper
        self.amount = amount
        self.token_id = token_id

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        payload = {
            "name": "raw_mint",
            "args": {
                "tick_lower": self.tick_lower,
                "tick_upper": self.tick_upper,
                "amount": self.amount,
            },
        }
        if self.token_id:
            payload["args"]["token_id"] = self.token_id  # type: ignore

        return TxRequest.new_with_order(protocol=protocol, sender=sender, source=source, payload=payload, order=order)


class UserMintTransaction(Transaction):
    tick_lower: int | str
    tick_upper: int | str
    amount0: Decimal
    amount1: Decimal
    token_id: str | None

    def __init__(
        self,
        tick_lower: int | str,
        tick_upper: int | str,
        amount0: Decimal,
        amount1: Decimal,
        token_id: str | None = None,
    ):
        self.tick_lower = tick_lower
        self.tick_upper = tick_upper
        self.amount0 = amount0
        self.amount1 = amount1
        self.token_id = token_id

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        args: dict[str, object] = {
            "tick_lower": self.tick_lower,
            "tick_upper": self.tick_upper,
        }
        args["amount0_desired"] = str(self.amount0)
        args["amount1_desired"] = str(self.amount1)
        args["amount0_min"] = 0  # not yet used but available in Rust
        args["amount1_min"] = 0

        if self.token_id:
            args["token_id"] = self.token_id
        payload = {
            "name": "mint",
            "args": args,
        }
        return TxRequest.new_with_order(protocol=protocol, sender=sender, source=source, payload=payload, order=order)


class MintTransaction(Transaction):
    price_lower: Decimal
    price_upper: Decimal
    current_price: Decimal
    max_token0: Decimal
    max_token1: Decimal
    pool: UniswapV3Pool
    token_id: str | None

    def __init__(
        self,
        price_lower: float | Decimal,
        price_upper: float | Decimal,
        current_price: float | Decimal,
        max_token0: float | Decimal,
        max_token1: float | Decimal,
        pool: UniswapV3Pool,
        token_id: str | None = None,
    ):
        super().__init__()

        self.price_lower = Decimal(price_lower)
        self.price_upper = Decimal(price_upper)
        self.current_price = Decimal(current_price)
        self.max_token0 = Decimal(max_token0)
        self.max_token1 = Decimal(max_token1)
        self.pool = pool
        self.token_id = token_id

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        tick_spacing = get_tick_spacing(self.pool.fee_tier)

        tick_lower = price_to_tick(self.price_lower, self.pool.decimals0, self.pool.decimals1, tick_spacing, True)
        tick_upper = price_to_tick(self.price_upper, self.pool.decimals0, self.pool.decimals1, tick_spacing, False)

        # FIXME done on Rust side ??
        token0_quantized = Decimal(10) ** (-self.pool.decimals0)
        token1_quantized = Decimal(10) ** (-self.pool.decimals1)
        max_token0 = Decimal(self.max_token0).quantize(token0_quantized, rounding=ROUND_DOWN)
        max_token1 = Decimal(self.max_token1).quantize(token1_quantized, rounding=ROUND_DOWN)

        tx = UserMintTransaction(tick_lower, tick_upper, amount0=max_token0, amount1=max_token1, token_id=self.token_id)
        return tx.to_tx_request(self.pool.name, source, sender, order)


class RawBurnTransaction(Transaction):
    tick_lower: int | str
    tick_upper: int | str
    amount: int | str

    def __init__(self, tick_lower: int | str, tick_upper: int | str, amount: int | str):
        super().__init__()

        self.tick_lower = tick_lower
        self.tick_upper = tick_upper
        self.amount = amount

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        payload = {
            "name": "raw_burn",
            "args": {"tick_lower": self.tick_lower, "tick_upper": self.tick_upper, "amount": self.amount},
        }

        return TxRequest.new_with_order(protocol=protocol, sender=sender, source=source, payload=payload, order=order)


class UserBurnTransaction(Transaction):
    tick_lower: int | str
    tick_upper: int | str
    amount_ratio: Decimal

    def __init__(self, tick_lower: int | str, tick_upper: int | str, amount_ratio: Decimal):
        self.tick_lower = tick_lower
        self.tick_upper = tick_upper
        self.amount_ratio = amount_ratio

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        payload = {
            "name": "burn",
            "args": {
                "tick_lower": self.tick_lower,
                "tick_upper": self.tick_upper,
                "amount_ratio": str(self.amount_ratio),
            },
        }
        return TxRequest.new_with_order(protocol=protocol, sender=sender, source=source, payload=payload, order=order)


class BurnTransaction(Transaction):
    price_lower: Decimal
    price_upper: Decimal
    amount_ratio: Decimal
    pool: UniswapV3Pool

    def __init__(
        self,
        price_lower: float | Decimal,
        price_upper: float | Decimal,
        amount_ratio: float | Decimal,
        pool: UniswapV3Pool,
    ):
        super().__init__()

        self.price_lower = Decimal(price_lower)
        self.price_upper = Decimal(price_upper)
        self.amount_ratio = Decimal(amount_ratio)
        self.pool = pool

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        # Use high-level PyUniswapV3Action::Burn with AmountRatio and tick bounds via UserBurnTransaction
        tick_spacing = get_tick_spacing(self.pool.fee_tier)
        tick_lower = price_to_tick(self.price_lower, self.pool.decimals0, self.pool.decimals1, tick_spacing, True)
        tick_upper = price_to_tick(self.price_upper, self.pool.decimals0, self.pool.decimals1, tick_spacing, False)

        tx = UserBurnTransaction(tick_lower, tick_upper, self.amount_ratio)
        return tx.to_tx_request(self.pool.name, source, sender, order)


class RawSwapTransaction(Transaction):
    amount: int | str
    zero_for_one: bool
    sqrt_price_limit_x96: int | str | None

    def __init__(self, amount: int | str, zero_for_one: bool, sqrt_price_limit_x96: int | str | None = None):
        super().__init__()

        self.zero_for_one = zero_for_one
        self.amount = amount
        self.sqrt_price_limit_x96 = sqrt_price_limit_x96

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        payload = {
            "name": "raw_swap",
            "args": {"amount_specified": self.amount, "zero_for_one": self.zero_for_one},
        }

        if self.sqrt_price_limit_x96 is not None:
            payload["args"]["sqrt_price_limit_x96"] = self.sqrt_price_limit_x96  # type: ignore

        return TxRequest.new_with_order(protocol=protocol, sender=sender, source=source, payload=payload, order=order)


class SwapTransaction(Transaction):
    price_limit: Decimal | None
    amount: Decimal
    pool: UniswapV3Pool
    zero_for_one: bool

    def __init__(
        self,
        amount: float | Decimal,
        zero_for_one: bool,
        pool: UniswapV3Pool,
        price_limit: float | Decimal | None = None,
    ):
        super().__init__()

        self.price_limit = Decimal(price_limit) if price_limit is not None else None
        self.amount = Decimal(amount)
        self.zero_for_one = zero_for_one
        self.pool = pool

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        # convert price_limit to x96 format
        sqrt_price_limit_x96 = None
        if self.price_limit is not None:
            sqrt_price_limit_x96 = int(self.price_limit.sqrt() * (2**96))

        if self.zero_for_one:
            amount_specified = int(self.amount.scaleb(self.pool.decimals0))
        else:
            amount_specified = int(self.amount.scaleb(self.pool.decimals1))

        tx = RawSwapTransaction(
            str(amount_specified),
            self.zero_for_one,
            str(sqrt_price_limit_x96) if sqrt_price_limit_x96 is not None else None,
        )

        return tx.to_tx_request(self.pool.name, source, sender, order)


class RawCollectTransaction(Transaction):
    amount_0_requested: int | str
    amount_1_requested: int | str
    tick_lower: int | str
    tick_upper: int | str

    def __init__(
        self, tick_lower: int | str, tick_upper: int | str, amount_0_requested: int | str, amount_1_requested: int | str
    ):
        super().__init__()

        self.tick_lower = tick_lower
        self.tick_upper = tick_upper
        self.amount_0_requested = amount_0_requested
        self.amount_1_requested = amount_1_requested

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        payload = {
            "name": "raw_collect",
            "args": {
                "amount_0_requested": self.amount_0_requested,
                "amount_1_requested": self.amount_1_requested,
                "tick_lower": self.tick_lower,
                "tick_upper": self.tick_upper,
            },
        }

        return TxRequest.new_with_order(protocol=protocol, sender=sender, source=source, payload=payload, order=order)


class CollectTransaction(Transaction):
    price_lower: Decimal
    price_upper: Decimal
    amount_0: Decimal
    amount_1: Decimal
    pool: UniswapV3Pool

    def __init__(
        self,
        price_lower: float | Decimal,
        price_upper: float | Decimal,
        amount_0: float | Decimal,
        amount_1: float | Decimal,
        pool: UniswapV3Pool,
    ):
        super().__init__()

        self.price_lower = Decimal(price_lower)
        self.price_upper = Decimal(price_upper)
        self.amount_0 = Decimal(amount_0)
        self.amount_1 = Decimal(amount_1)
        self.pool = pool

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        tick_spacing = get_tick_spacing(self.pool.fee_tier)

        tick_lower = price_to_tick(self.price_lower, self.pool.decimals0, self.pool.decimals1, tick_spacing, True)
        tick_upper = price_to_tick(self.price_upper, self.pool.decimals0, self.pool.decimals1, tick_spacing, False)

        amount0_scaled = int(self.amount_0.scaleb(self.pool.decimals0))
        amount1_scaled = int(self.amount_1.scaleb(self.pool.decimals1))

        tx = RawCollectTransaction(tick_lower, tick_upper, str(amount0_scaled), str(amount1_scaled))

        return tx.to_tx_request(self.pool.name, source, sender, order)
