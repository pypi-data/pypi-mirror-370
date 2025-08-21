import math
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, List, Optional, Tuple

from nqs_sdk import MetricName, MutSharedState, SealedParameters, SimulationClock, TxRequest, Wallet
from nqs_sdk.bindings.protocols.cex.cex_transactions import (
    AddMarginCollateralTransaction,
    CheckMarginPositionTransaction,
    CloseMarginPositionTransaction,
    ExchangeTransaction,
    OpenMarginPositionTransaction,
    RebalanceTransaction,
)
from nqs_sdk.interfaces.observable_consumer import ObservableConsumer
from nqs_sdk.interfaces.protocol import Protocol

from .cex_market import CEXMarkets


def compute_cex_target_amounts(
    token0_balance: Decimal,
    token1_balance: Decimal,
    weight_0: Decimal,
    weight_1: Decimal,
    execution_price: Decimal,
    fee: Decimal,
) -> tuple[Decimal, Decimal]:
    total_value_in_token0 = token0_balance + (token1_balance / execution_price)

    target_token0 = total_value_in_token0 * weight_0
    target_token1 = (total_value_in_token0 * weight_1) * execution_price

    # Calculate differences between current and target
    token0_diff = target_token0 - token0_balance
    token1_diff = target_token1 - token1_balance

    if fee > 0:
        fee_amount0 = abs(token0_diff) * fee / Decimal("100.0")
        fee_amount1 = abs(token1_diff) * fee / Decimal("100.0")
        target_token0 -= fee_amount0 if token0_diff > 0 else 0
        target_token1 -= fee_amount1 if token1_diff > 0 else 0

    return target_token0, target_token1


@dataclass
class MarginPosition:
    token_id: str
    margin_token: str
    direction: bool  # True if long, False if short
    margin_amount: Decimal
    collateral_token: str
    collateral_amount: Decimal
    opening_price: Decimal
    opening_timestamp: int
    opening_fee: Decimal
    liquidation_price: Decimal
    maintenance_margin_ratio: Decimal


class CEX(Protocol, ObservableConsumer):
    def __init__(
        self,
        markets: CEXMarkets,
    ) -> None:
        self.markets = markets
        self.available_pairs = {(pair.token0, pair.token1): pair for pair in markets.pairs}
        self.margin_positions: dict[str, MarginPosition] = {}

    def id(self) -> str:
        return "cex"

    def initialize(self, parameters: SealedParameters) -> None:
        return

    def consume(self, parameters: SealedParameters, clock: SimulationClock) -> Tuple[List[MetricName], Optional[int]]:
        metrics_str = []
        for pair in self.available_pairs.keys():
            metrics_str.append(f'common.market_spot:{{pair="{pair[0]}/{pair[1]}"}}')

        metrics = []
        for metric in metrics_str:
            metrics.append(parameters.str_to_metric(metric))

        return metrics, None

    def build_tx_payload(self, source: str, sender: str, call: Any) -> TxRequest:
        pass

    def execute_tx(self, clock: SimulationClock, state: MutSharedState, tx: TxRequest) -> None:
        transaction = tx.payload

        wallet = state.get_wallet(tx.sender)
        holdings = {key: Decimal(wallet.get_balance_of_float(key)) for key in wallet.holdings.keys()}

        if isinstance(transaction, RebalanceTransaction):
            token0 = transaction.token0
            token1 = transaction.token1
            weight0 = transaction.weight0
            weight1 = transaction.weight1
            execution_price = transaction.execution_price  # price of token0 in terms of token1

            assert (token0, token1) in self.available_pairs, f"Pair {token0}/{token1} is not available."
            fee = self.available_pairs[(token0, token1)].opening_fee

            # normalize weights
            weight0 = weight0 / (weight0 + weight1)
            weight1 = weight1 / (weight0 + weight1)

            # Use self.fee instead of transaction.fee which doesn't exist in CEXRebalanceTransaction
            token0_balance = holdings[token0]
            token1_balance = holdings[token1]

            target_token0, target_token1 = compute_cex_target_amounts(
                token0_balance, token1_balance, weight0, weight1, execution_price, fee
            )

            # Update holdings with new balanced amounts
            holdings[token0] = target_token0
            holdings[token1] = target_token1

        elif isinstance(transaction, OpenMarginPositionTransaction):
            token = transaction.token
            amount = transaction.amount
            direction = transaction.direction
            collateral = transaction.collateral
            collateral_amount = transaction.collateral_amount
            execution_price = transaction.execution_price
            token_id = transaction.token_id

            # check if collateral is allowed
            assert (token, collateral) in self.available_pairs, f"Pair {token}/{collateral} is not available."
            assert token_id not in self.margin_positions, f"Token {token_id} already has a margin position"

            opening_fee = self.available_pairs[(token, collateral)].opening_fee

            allowed_leverage = self.available_pairs[(token, collateral)].max_leverage
            assert allowed_leverage > 1, f"Margin is not allowed for the pair {token}/{collateral}."

            maintenance_margin_ratio = self.available_pairs[(token, collateral)].maintenance_margin_ratio

            # compute the leverage of the position
            # leverage = total_position_value / collateral_amount
            position_value = amount * execution_price
            leverage = position_value / collateral_amount
            assert math.ceil(leverage) <= allowed_leverage, (
                f"Leverage {leverage} is not allowed for the pair {token}/{collateral}."
            )

            # compute the liquidation price
            if direction:  # long position
                liquidation_price = execution_price * (Decimal("1.0") / leverage + maintenance_margin_ratio)
            else:  # short position
                liquidation_price = execution_price + execution_price * (
                    Decimal("1.0") / leverage + maintenance_margin_ratio
                )

            # compute the opening fee
            fees = position_value * opening_fee

            # check if the collateral is available in the wallet and take it
            assert collateral_amount + fees <= holdings[collateral], f"Not enough {collateral} available in the wallet."
            holdings[collateral] -= collateral_amount + fees

            # create a margin position
            self.margin_positions[token_id] = MarginPosition(
                token_id=token_id,
                margin_token=token,
                direction=direction,
                margin_amount=amount,
                collateral_token=collateral,
                collateral_amount=collateral_amount,
                opening_price=execution_price,
                opening_timestamp=clock.current_time(),
                opening_fee=opening_fee,
                liquidation_price=liquidation_price,
                maintenance_margin_ratio=maintenance_margin_ratio,
            )

        elif isinstance(transaction, AddMarginCollateralTransaction):
            token_id = transaction.token_id
            amount = transaction.amount

            assert token_id in self.margin_positions, f"Token {token_id} does not have a margin position"

            margin_position = self.margin_positions[token_id]

            # check if the collateral is available in the wallet and take it
            assert amount <= holdings[margin_position.collateral_token], (
                f"Not enough {margin_position.collateral_token} available in the wallet."
            )
            holdings[margin_position.collateral_token] -= amount

            # update the margin position
            margin_position.collateral_amount += amount

            position_value = margin_position.margin_amount * margin_position.opening_price
            leverage = position_value / margin_position.collateral_amount

            if margin_position.direction:  # long position
                margin_position.liquidation_price = margin_position.opening_price * (
                    Decimal("1.0") / leverage + margin_position.maintenance_margin_ratio
                )
            else:  # short position
                margin_position.liquidation_price = margin_position.opening_price + margin_position.opening_price * (
                    Decimal("1.0") / leverage + margin_position.maintenance_margin_ratio
                )

        elif isinstance(transaction, CheckMarginPositionTransaction):
            # spot_prices = transaction.current_prices
            # maintenance_fees = transaction.maintenance_fees
            pass

        elif isinstance(transaction, CloseMarginPositionTransaction):
            token_id = transaction.token_id
            execution_price = transaction.execution_price

            assert token_id in self.margin_positions, f"Token {token_id} does not have a margin position"

            pnl = max(0, (execution_price - margin_position.opening_price) * margin_position.margin_amount)
            if not margin_position.direction:  # short position
                pnl *= -1.0

            # update the holdings
            holdings[margin_position.collateral_token] += pnl + margin_position.collateral_amount

            # delete position
            del self.margin_positions[token_id]

        elif isinstance(transaction, ExchangeTransaction):
            direction = transaction.direction
            token0 = transaction.token0 if direction else transaction.token1
            token1 = transaction.token1 if direction else transaction.token0
            amount = transaction.amount
            execution_price = transaction.execution_price

            assert (token0, token1) in self.available_pairs, f"Pair {token0}/{token1} is not available."

            # check if the token0 is available in the wallet and take it
            assert amount <= holdings[token1], f"Not enough {token0} available in the wallet."

            holdings[token1] -= amount
            holdings[token0] += amount / execution_price

        # update the wallet
        new_wallet = Wallet(
            holdings=holdings,
            tokens_metadata=wallet.tokens_metadata,
            erc721_tokens=wallet.get_erc721_tokens(),
            agent_name=wallet.agent_name,
        )
        state.insert_wallet(tx.sender, new_wallet)
