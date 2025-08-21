from typing import List, Optional, Tuple

from nqs_sdk import MetricName, Metrics, RefSharedState, SealedParameters, SimulationClock, TxRequest
from nqs_sdk.bindings.protocols.uniswap_v3.uniswap_v3_pool import UniswapV3Pool
from nqs_sdk.bindings.protocols.uniswap_v3.uniswap_v3_transactions import SwapTransaction
from nqs_sdk.interfaces.observable_consumer import ObservableConsumer
from nqs_sdk.interfaces.tx_generator import TxGenerator


class UniswapV3Arbitrager(TxGenerator, ObservableConsumer):
    def __init__(self, pools: list[UniswapV3Pool]) -> None:
        self.pools: list[UniswapV3Pool] = pools

    def id(self) -> str:
        return "uniswap_v3_arbitrager"

    def initialize(self, parameters: SealedParameters) -> None:
        return

    def consume(self, parameters: SealedParameters, clock: SimulationClock) -> Tuple[List[MetricName], Optional[int]]:
        metrics_names = []

        for pool in self.pools:
            current_spot_obs = f"{pool.name}.dex_spot"
            market_spot_obs = f'common.market_spot:{{pair="{pool.token0}/{pool.token1}"}}'
            liquidity_obs = f"{pool.name}.liquidity"

            metrics_names.append(parameters.str_to_metric(current_spot_obs))
            metrics_names.append(parameters.str_to_metric(market_spot_obs))
            metrics_names.append(parameters.str_to_metric(liquidity_obs))

        return metrics_names, None

    def next(
        self,
        clock: SimulationClock,
        state: RefSharedState,
        metrics: Metrics,
    ) -> Tuple[List[TxRequest], Optional[int]]:
        txns: list[TxRequest] = []

        for pool in self.pools:
            pool_fee = pool.fee_tier

            parameters = state.get_parameters()

            current_spot_metric = parameters.str_to_metric(f"{pool.name}.dex_spot")
            market_spot_metric = parameters.str_to_metric(f'common.market_spot:{{pair="{pool.token0}/{pool.token1}"}}')
            total_liquidity = parameters.str_to_metric(f"{pool.name}.liquidity")

            current_spot = metrics.get(current_spot_metric)
            market_spot = metrics.get(market_spot_metric)

            liquidity = metrics.get(total_liquidity)

            if current_spot is None or market_spot is None or liquidity is None:
                continue

            swap_tx = None
            if (current_spot / market_spot > (1.0 + float(pool_fee))) and liquidity > 0:
                swap_tx = SwapTransaction(
                    amount=liquidity,
                    zero_for_one=True,
                    pool=pool,
                    price_limit=market_spot,
                )
            elif (current_spot / market_spot < (1.0 - float(pool_fee))) and liquidity > 0:
                swap_tx = SwapTransaction(
                    amount=liquidity,
                    zero_for_one=False,
                    pool=pool,
                    price_limit=market_spot,
                )

            if swap_tx is not None:
                # Order 0.0 for user transactions, 1.0 for historical or random, and 2.0 for arbitrage orders
                tx = swap_tx.to_tx_request(
                    protocol=pool.name, source="Arb", sender="0xABA8888888888888888888888888888888888888", order=2.0
                )
                txns.append(tx)

        return txns, None
