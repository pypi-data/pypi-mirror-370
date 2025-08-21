# mypy: disable-error-code="return-value"

from datetime import timedelta
from decimal import Decimal
from typing import Optional

from nqs_sdk.bindings.protocols.cex.cex_factory import CEXFactory
from nqs_sdk.bindings.protocols.cex.cex_market import CEXMarkets
from nqs_sdk.bindings.protocols.cex.cex_transactions import (
    RebalanceTransaction,
)
from nqs_sdk.coding_envs.protocols.cex.cex_abstract import CexProtocol
from nqs_sdk.coding_envs.protocols.coding_protocol import CodingProtocol
from nqs_sdk.interfaces.protocol_metafactory import ProtocolMetaFactory
from nqs_sdk.interfaces.tx_generator import TxGenerator
from nqs_sdk.utils.logging import local_logger


logger = local_logger(__name__)


class CEXCodingProtocol(CodingProtocol, CexProtocol):
    def __init__(self, markets: CEXMarkets) -> None:
        super().__init__(markets)

        self.margin_positions: dict[str, tuple[str, str]] = {}
        self.available_pairs = {(pair.token0, pair.token1): pair for pair in markets.pairs}

    def id(self) -> str:
        return "cex"

    def get_protocol_factory(self) -> ProtocolMetaFactory:
        return CEXFactory

    def get_protocol_description(self) -> tuple[str, str, list[str]]:
        import inspect

        return (
            (
                "CEX is a protocol that allows users to trade on a centralized exchange."
                "It allows users to swap tokens, trade with margin and leverage, and rebalance a portfolio."
            ),
            (
                "The following pairs are available in this exchange for trading:\n".join(
                    [f"{pair.token0}/{pair.token1}" for pair in self.protocol.pairs]
                )
            ),
            [inspect.getsource(CexProtocol)],
        )

    def get_tx_generators(self) -> list[TxGenerator]:
        return []

    def get_observables_names(self) -> list[str]:
        metrics_str = []

        for pair in self.protocol.pairs:
            metrics_str.append(f'common.market_spot:{{pair="{pair.token0}/{pair.token1}"}}')
            metrics_str.append(f'common.market_spot:{{pair="{pair.token1}/{pair.token0}"}}')

            for agent in self.all_agents:
                metrics_str.append(f'{agent}.all.wallet_holdings:{{token="{pair.token0}"}}')
                metrics_str.append(f'{agent}.all.wallet_holdings:{{token="{pair.token1}"}}')

        for agent in self.all_agents:
            metrics_str.append(f"{agent}.all.total_holding")
            metrics_str.append(f"{agent}.all.total_fees")

        return metrics_str

    def is_pair_available(self, token0: str, token1: str) -> bool:
        return (token0, token1) in self.available_pairs

    def pair_max_leverage(self, token0: str, token1: str) -> int:
        return self.available_pairs[(token0, token1)].max_leverage

    def pair_opening_fee(self, token0: str, token1: str) -> float:
        return self.available_pairs[(token0, token1)].opening_fee

    def pair_maintenance_margin_ratio(self, token0: str, token1: str) -> float:
        return self.available_pairs[(token0, token1)].maintenance_margin_ratio

    def pair_spot(self, token0: str, token1: str, lookback: Optional[timedelta] = None) -> Optional[Decimal]:
        data = self.observables.get(f'common.market_spot:{{pair="{token0}/{token1}"}}', None)

        if data is None or len(data) < 2:
            return None

        # return the penultimate price, not the last one as it is forward looking relative to other protocols
        return data.iloc[-2]

    def is_margin_position_exists(self, token_id: str) -> bool:
        return token_id in self.protocol.margin_positions

    def rebalance(self, token0: str, token1: str, weight0: float | Decimal, weight1: float | Decimal) -> None:
        weight0 = Decimal(weight0)
        weight1 = Decimal(weight1)

        current_price = self.pair_spot(token0, token1)

        # if current price is not available, do nothing
        if current_price is None:
            return

        rebalance_txn = RebalanceTransaction(
            token0=token0,
            token1=token1,
            weight0=weight0,
            weight1=weight1,
            current_price=current_price,
        )

        self.register_transaction(self.current_agent, rebalance_txn)

    def margin_buy(self, token: str, amount: float, collateral: str, collateral_amount: float) -> None:
        pass

    def margin_sell(self, token: str, amount: float, collateral: str, collateral_amount: float) -> None:
        pass

    def add_margin_collateral(self, token_id: str, amount: float) -> None:
        pass

    def close_margin_position(self, token_id: str) -> None:
        pass

    def buy(self, token0: str, token1: str, amount: float) -> None:
        pass

    def sell(self, token0: str, token1: str, amount: float) -> None:
        pass
