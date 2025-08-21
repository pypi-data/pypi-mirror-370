# mypy: disable-error-code="return-value"

from datetime import timedelta
from decimal import Decimal
from typing import List, Optional

import pandas as pd

from nqs_sdk.bindings.protocols.uniswap_v3.tx_generators.uniswap_v3_historical import UniswapV3HistoricalTxGenerator
from nqs_sdk.bindings.protocols.uniswap_v3.uniswap_v3_arbitrager import UniswapV3Arbitrager
from nqs_sdk.bindings.protocols.uniswap_v3.uniswap_v3_factory import UniswapV3Factory
from nqs_sdk.bindings.protocols.uniswap_v3.uniswap_v3_pool import UniswapV3Pool
from nqs_sdk.bindings.protocols.uniswap_v3.uniswap_v3_transactions import (
    BurnTransaction,
    CollectTransaction,
    MintTransaction,
    SwapTransaction,
)
from nqs_sdk.coding_envs.protocols.coding_protocol import CodingProtocol
from nqs_sdk.coding_envs.protocols.uniswap_v3.uniswap_v3_abstract import UniswapV3Protocol
from nqs_sdk.interfaces.protocol_metafactory import ProtocolMetaFactory
from nqs_sdk.interfaces.tx_generator import TxGenerator
from nqs_sdk.utils.logging import local_logger


logger = local_logger(__name__)


class UniswapV3CodingProtocol(CodingProtocol, UniswapV3Protocol):
    def __init__(self, pool: UniswapV3Pool, generators: list[str | TxGenerator] = []) -> None:
        super().__init__(pool)

        self.agents_positions: dict[str, dict[str, dict[str, int]]] = {}

        self.pool: UniswapV3Pool = pool

        self.generators: list[str | TxGenerator] = generators

    def id(self) -> str:
        return self.pool.name

    def get_protocol_factory(self) -> Optional[ProtocolMetaFactory]:
        return UniswapV3Factory

    def get_protocol_description(self) -> tuple[str, str, list[str]]:
        import inspect

        return (
            (
                "Uniswap V3 is a decentralized exchange protocol that allows users to swap tokens "
                "or provide/remove liquidity to the pool. It features concentrated liquidity, "
                "allowing liquidity providers to specify price ranges for their capital. "
                "Users can earn fees from trades that occur within their specified price ranges. "
                "The pool has two tokens, token0 and token1, and a fee tier. "
                "The fee tier is the fee that is charged for each trade. "
                "Common fee tiers are 0.05%, 0.3%, or 1%."
            ),
            (
                f"{self.pool.name} is the pool with the following parameters: "
                f"token0: {self.pool.token0}, token1: {self.pool.token1}, fee tier: {self.pool.fee_tier}."
            ),
            [inspect.getsource(UniswapV3Protocol)],
        )

    def get_tx_generators(self) -> List[TxGenerator]:
        tx_generators: List[TxGenerator] = []
        for gen in self.generators:
            if isinstance(gen, str):
                if gen == "historical":
                    tx_generators.append(UniswapV3HistoricalTxGenerator(self.pool))
                elif gen == "arbitrager":
                    tx_generators.append(UniswapV3Arbitrager([self.pool]))
                else:
                    raise ValueError(f"Unknown data generator: {gen}")
            elif isinstance(gen, TxGenerator):
                tx_generators.append(gen)
            else:
                raise ValueError(f"Unknown data generator: {gen}")

        return tx_generators

    def get_observables_names(self) -> list[str]:
        metrics_str = []

        # protocol metrics
        metrics_str.append(f"{self.pool.name}.dex_spot")
        metrics_str.append(f"{self.pool.name}.liquidity")
        metrics_str.append(f"{self.pool.name}.total_fees")
        metrics_str.append(f"{self.pool.name}.total_volume_numeraire")
        metrics_str.append(f'{self.pool.name}.total_volume:{{token="{self.pool.token0}"}}')
        metrics_str.append(f'{self.pool.name}.total_volume:{{token="{self.pool.token1}"}}')
        metrics_str.append(f"{self.pool.name}.current_tick")
        metrics_str.append(f'{self.pool.name}.total_holdings:{{token="{self.pool.token0}"}}')
        metrics_str.append(f'{self.pool.name}.total_holdings:{{token="{self.pool.token1}"}}')
        metrics_str.append(f'{self.pool.name}.total_fees:{{token="{self.pool.token0}"}}')
        metrics_str.append(f'{self.pool.name}.total_fees:{{token="{self.pool.token1}"}}')
        metrics_str.append(f"{self.protocol.name}.total_value_locked")

        # agent metrics
        for agent in self.all_agents:
            # agent-level metrics (without position)
            metrics_str.append(f"{agent}.{self.pool.name}.active_liquidity")
            metrics_str.append(f'{agent}.{self.pool.name}.token_amount:{{token="{self.pool.token0}"}}')
            metrics_str.append(f'{agent}.{self.pool.name}.token_amount:{{token="{self.pool.token1}"}}')
            metrics_str.append(f"{agent}.{self.pool.name}.fees_collected")
            metrics_str.append(f'{agent}.{self.pool.name}.fees_collected:{{token="{self.pool.token0}"}}')
            metrics_str.append(f'{agent}.{self.pool.name}.fees_collected:{{token="{self.pool.token1}"}}')
            metrics_str.append(f"{agent}.{self.pool.name}.fees_not_collected")
            metrics_str.append(f'{agent}.{self.pool.name}.fees_not_collected:{{token="{self.pool.token0}"}}')
            metrics_str.append(f'{agent}.{self.pool.name}.fees_not_collected:{{token="{self.pool.token1}"}}')
            metrics_str.append(f"{agent}.{self.pool.name}.abs_impermanent_loss")
            metrics_str.append(f"{agent}.{self.pool.name}.perc_impermanent_loss")
            metrics_str.append(f"{agent}.{self.pool.name}.static_ptf_value")
            metrics_str.append(f"{agent}.{self.pool.name}.permanent_loss")
            metrics_str.append(f"{agent}.{self.pool.name}.loss_versus_rebalancing")
            metrics_str.append(f"{agent}.{self.pool.name}.total_fees_relative_to_lvr")

            # position related metrics
            if agent in self.agents_positions:
                for token_id in self.agents_positions[agent]:
                    position = token_id + "_" + str(self.agents_positions[agent][token_id]["token_id_index"])
                    metrics_str.append(f'{agent}.{self.pool.name}.active_liquidity:{{position="{position}"}}')
                    metrics_str.append(f'{agent}.{self.pool.name}.liquidity:{{position="{position}"}}')
                    metrics_str.append(
                        f'{agent}.{self.pool.name}.token_amount:{{position="{position}", token="{self.pool.token0}"}}'
                    )
                    metrics_str.append(
                        f'{agent}.{self.pool.name}.token_amount:{{position="{position}", token="{self.pool.token1}"}}'
                    )
                    metrics_str.append(f'{agent}.{self.pool.name}.net_position:{{position="{position}"}}')
                    metrics_str.append(f'{agent}.{self.pool.name}.fees_collected:{{position="{position}"}}')
                    metrics_str.append(
                        f'{agent}.{self.pool.name}.fees_collected:{{position="{position}", token="{self.pool.token0}"}}'
                    )
                    metrics_str.append(
                        f'{agent}.{self.pool.name}.fees_collected:{{position="{position}", token="{self.pool.token1}"}}'
                    )
                    metrics_str.append(f'{agent}.{self.pool.name}.fees_not_collected:{{position="{position}"}}')
                    metrics_str.append(
                        f'{agent}.{self.pool.name}.fees_not_collected:{{position="{position}", token="{self.pool.token0}"}}'  # noqa: E501
                    )
                    metrics_str.append(
                        f'{agent}.{self.pool.name}.fees_not_collected:{{position="{position}", token="{self.pool.token1}"}}'  # noqa: E501
                    )
                    metrics_str.append(f'{agent}.{self.pool.name}.abs_impermanent_loss:{{position="{position}"}}')
                    metrics_str.append(f'{agent}.{self.pool.name}.perc_impermanent_loss:{{position="{position}"}}')
                    metrics_str.append(f'{agent}.{self.pool.name}.static_ptf_value:{{position="{position}"}}')
                    metrics_str.append(f'{agent}.{self.pool.name}.permanent_loss:{{position="{position}"}}')
                    metrics_str.append(f'{agent}.{self.pool.name}.loss_versus_rebalancing:{{position="{position}"}}')
                    metrics_str.append(f'{agent}.{self.pool.name}.total_fees_relative_to_lvr:{{position="{position}"}}')
                    metrics_str.append(f'{agent}.{self.pool.name}.upper_bound_price:{{position="{position}"}}')
                    metrics_str.append(f'{agent}.{self.pool.name}.lower_bound_price:{{position="{position}"}}')

        return metrics_str

    @property
    def token0(self) -> str:
        return self.pool.token0

    @property
    def token1(self) -> str:
        return self.pool.token1

    @property
    def fee_tier(self) -> float:
        return self.pool.fee_tier

    def is_position_exists(self, token_id: str) -> bool:
        if self.current_agent not in self.agents_positions or token_id not in self.agents_positions[self.current_agent]:
            return False

        liquidity = self.position_liquidity(token_id)
        return liquidity is not None and liquidity > 0

    def dex_spot(self, lookback: Optional[timedelta] = None) -> pd.Series:
        metric = f"{self.protocol.name}.dex_spot"
        return self._get_obs_timeserie(metric, lookback)

    def liquidity(self, lookback: Optional[timedelta] = None) -> pd.Series:
        metric = f"{self.protocol.name}.liquidity"
        return self._get_obs_timeserie(metric, lookback)

    def total_volume_numeraire(self, lookback: Optional[timedelta] = None) -> pd.Series:
        metric = f"{self.protocol.name}.total_volume_numeraire"
        return self._get_obs_timeserie(metric, lookback)

    def total_volume(self, token: bool, lookback: Optional[timedelta] = None) -> pd.Series:
        metric = f"{self.protocol.name}.total_volume"
        token_str = self.pool.token1 if token else self.pool.token0
        metric += f':{{token="{token_str}"}}'
        return self._get_obs_timeserie(metric, lookback)

    def total_holdings(self, token: bool, lookback: Optional[timedelta] = None) -> pd.Series:
        metric = f"{self.protocol.name}.total_holdings"
        token_str = self.pool.token1 if token else self.pool.token0
        metric += f':{{token="{token_str}"}}'
        return self._get_obs_timeserie(metric, lookback)

    def total_fees(self, token: Optional[bool] = None, lookback: Optional[timedelta] = None) -> pd.Series:
        metric = f"{self.protocol.name}.total_fees"
        if token is not None:
            token_str = self.pool.token1 if token else self.pool.token0
            metric += f':{{token="{token_str}"}}'
        return self._get_obs_timeserie(metric, lookback)

    def total_value_locked(self, lookback: Optional[timedelta] = None) -> pd.Series:
        metric: str = f"{self.protocol.name}.total_value_locked"
        return self._get_obs_timeserie(metric, lookback)

    def get_tick(self, lookback: Optional[timedelta] = None) -> pd.Series:
        metric: str = f"{self.protocol.name}.current_tick"
        return self._get_obs_timeserie(metric, lookback)

    def swap(self, amount: float, token: bool, price_limit: Optional[float] = None) -> None:
        price_limit_decimal = Decimal(price_limit) if price_limit is not None else None

        swap_txn = SwapTransaction(
            amount=amount,
            zero_for_one=not token,
            price_limit=price_limit_decimal,
            pool=self.pool,
        )

        self.register_transaction(self.current_agent, swap_txn)

    def mint(
        self,
        price_lower: float | Decimal,
        price_upper: float | Decimal,
        max_token0: float | Decimal,
        max_token1: float | Decimal,
        token_id: str,
    ) -> Optional[dict[str, Decimal]]:
        if self.current_agent not in self.agents_positions:
            self.agents_positions[self.current_agent] = {}

        if token_id not in self.agents_positions[self.current_agent]:
            self.agents_positions[self.current_agent][token_id] = {"token_id_index": 0}
        else:
            self.agents_positions[self.current_agent][token_id]["token_id_index"] += 1

        current_price = self.dex_spot().iloc[-1]

        mint_txn = MintTransaction(
            pool=self.pool,
            price_lower=price_lower,
            price_upper=price_upper,
            current_price=current_price,
            max_token0=max_token0,
            max_token1=max_token1,
            token_id=self._position_id(token_id),
        )

        self.register_transaction(self.current_agent, mint_txn)

    def burn(self, amount_ratio: float, token_id: str) -> None:
        position_bounds = self.position_bounds(token_id)

        # If the position is not initialized, do not burn
        if not self.is_position_exists(token_id):
            logger.warning(f"Position {token_id} is not initialized, skipping burn")
            return

        fee_not_collected_0 = self.fees_not_collected(token=self.pool.token0, token_id=token_id)
        fee_not_collected_1 = self.fees_not_collected(token=self.pool.token1, token_id=token_id)

        token0_amount = self.token_amount(self.pool.token0, token_id)
        token1_amount = self.token_amount(self.pool.token1, token_id)

        burn_txn = BurnTransaction(
            price_lower=position_bounds[0],
            price_upper=position_bounds[1],
            amount_ratio=Decimal(amount_ratio),
            pool=self.pool,
        )

        collect_txn = CollectTransaction(
            price_lower=position_bounds[0],
            price_upper=position_bounds[1],
            amount_0=token0_amount + fee_not_collected_0,
            amount_1=token1_amount + fee_not_collected_1,
            pool=self.pool,
        )

        self.register_transaction(self.current_agent, burn_txn)
        self.register_transaction(self.current_agent, collect_txn)

    def _position_id(self, token_id: str) -> str:
        token_id_index = self.agents_positions[self.current_agent][token_id]["token_id_index"]
        position = token_id + "_" + str(token_id_index)
        return position

    def active_liquidity(self, token_id: Optional[str] = None) -> Optional[Decimal]:
        metric = f"{self.current_agent}.{self.protocol.name}.active_liquidity"
        if token_id is not None and token_id in self.agents_positions[self.current_agent]:
            position = self._position_id(token_id)
            metric += f':{{position="{position}"}}'

        series = self._get_obs_timeserie(metric, None)
        return series.iloc[-1] if series is not None and not series.empty else None

    def position_liquidity(self, token_id: Optional[str] = None) -> Optional[Decimal]:
        metric = f"{self.current_agent}.{self.protocol.name}.liquidity"
        if token_id is not None and token_id in self.agents_positions[self.current_agent]:
            position = self._position_id(token_id)
            metric += f':{{position="{position}"}}'

        series = self._get_obs_timeserie(metric, None)
        return series.iloc[-1] if series is not None and not series.empty else None

    def token_amount(self, token: str, token_id: Optional[str] = None) -> Optional[Decimal]:
        if token_id is None:
            metric = f'{self.current_agent}.{self.protocol.name}.token_amount:{{token="{token}"}}'
        else:
            position = self._position_id(token_id)
            # FIXME you should not build MetricName by hand!!
            metric = (
                f'{self.current_agent}.{self.protocol.name}.token_amount:{{position="{position}", token="{token}"}}'
            )

        series = self._get_obs_timeserie(metric, None)
        return series.iloc[-1] if not series.empty else None

    def net_position(self, token_id: str) -> Optional[Decimal]:
        position = self._position_id(token_id)
        metric = f'{self.current_agent}.{self.protocol.name}.net_position:{{position="{position}"}}'
        series = self._get_obs_timeserie(metric, None)
        return series.iloc[-1] if not series.empty else None

    def fees_collected(self, token: Optional[str] = None, token_id: Optional[str] = None) -> Optional[Decimal]:
        metric = f"{self.current_agent}.{self.protocol.name}.fees_collected"
        if token_id is not None and token is None:
            position = self._position_id(token_id)
            metric += f':{{position="{position}"}}'
        elif token_id is None and token is not None:
            metric += f':{{token="{token}"}}'
        elif token_id is not None and token is not None:
            position = self._position_id(token_id)
            metric += f':{{position="{position}", token="{token}"}}'

        series = self._get_obs_timeserie(metric, None)
        return series.iloc[-1] if not series.empty else None

    def fees_not_collected(self, token: Optional[str] = None, token_id: Optional[str] = None) -> Optional[Decimal]:
        metric = f"{self.current_agent}.{self.protocol.name}.fees_not_collected"
        if token_id is not None and token is None and token_id in self.agents_positions[self.current_agent]:
            position = self._position_id(token_id)
            metric += f':{{position="{position}"}}'
        elif token_id is None and token is not None:
            metric += f':{{token="{token}"}}'
        elif token_id is not None and token is not None and token_id in self.agents_positions[self.current_agent]:
            position = self._position_id(token_id)
            metric += f':{{position="{position}", token="{token}"}}'

        series = self._get_obs_timeserie(metric, None)
        return series.iloc[-1] if not series.empty else None

    def abs_impermanent_loss(self, token_id: Optional[str] = None) -> Optional[Decimal]:
        metric = self.current_agent + "." + self.protocol.name + ".abs_impermanent_loss"
        if token_id is not None and token_id in self.agents_positions[self.current_agent]:
            position = self._position_id(token_id)
            metric += f':{{position="{position}"}}'

        series = self._get_obs_timeserie(metric, None)
        return series.iloc[-1] if not series.empty else None

    def perc_impermanent_loss(self, token_id: Optional[str] = None) -> Optional[Decimal]:
        metric = self.current_agent + "." + self.protocol.name + ".perc_impermanent_loss"
        if token_id is not None and token_id in self.agents_positions[self.current_agent]:
            position = self._position_id(token_id)
            metric += f':{{position="{position}"}}'

        series = self._get_obs_timeserie(metric, None)
        return series.iloc[-1] if not series.empty else None

    def static_ptf_value(self, token_id: Optional[str] = None) -> Optional[Decimal]:
        metric = self.current_agent + "." + self.protocol.name + ".static_ptf_value"
        if token_id is not None and token_id in self.agents_positions[self.current_agent]:
            position = self._position_id(token_id)
            metric += f':{{position="{position}"}}'

        series = self._get_obs_timeserie(metric, None)
        return series.iloc[-1] if not series.empty else None

    def permanent_loss(self, token_id: Optional[str] = None) -> Optional[Decimal]:
        metric = self.current_agent + "." + self.protocol.name + ".permanent_loss"
        if token_id is not None and token_id in self.agents_positions[self.current_agent]:
            position = self._position_id(token_id)
            metric += f':{{position="{position}"}}'

        series = self._get_obs_timeserie(metric, None)
        return series.iloc[-1] if not series.empty else None

    def loss_versus_rebalancing(self, token_id: Optional[str] = None) -> Optional[Decimal]:
        metric = self.current_agent + "." + self.protocol.name + ".loss_versus_rebalancing"
        if token_id is not None and token_id in self.agents_positions[self.current_agent]:
            position = self._position_id(token_id)
            metric += f':{{position="{position}"}}'

        series = self._get_obs_timeserie(metric, None)
        return series.iloc[-1] if not series.empty else None

    def total_fees_relative_to_lvr(self, token_id: Optional[str] = None) -> Optional[Decimal]:
        metric = self.current_agent + "." + self.protocol.name + ".total_fees_relative_to_lvr"
        if token_id is not None and token_id in self.agents_positions[self.current_agent]:
            position = self._position_id(token_id)
            metric += f':{{position="{position}"}}'

        series = self._get_obs_timeserie(metric, None)
        return series.iloc[-1] if not series.empty else None

    def position_bounds(self, token_id: str) -> tuple[Optional[Decimal], Optional[Decimal]]:
        position = self._position_id(token_id)
        upper_bound = self._get_obs_timeserie(
            f'{self.current_agent}.{self.protocol.name}.upper_bound_price:{{position="{position}"}}', None
        ).iloc[-1]
        lower_bound = self._get_obs_timeserie(
            f'{self.current_agent}.{self.protocol.name}.lower_bound_price:{{position="{position}"}}', None
        ).iloc[-1]
        return lower_bound, upper_bound
