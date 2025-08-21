import os
from typing import Optional

from nqs_sdk import BlockNumberOrTimestamp, quantlib
from nqs_sdk.bindings.protocols.uniswap_v3.uniswap_v3_pool import UniswapV3Pool
from nqs_sdk.bindings.protocols.uniswap_v3.uniswap_v3_transactions import (
    RawBurnTransaction,
    RawCollectTransaction,
    RawMintTransaction,
    RawSwapTransaction,
)
from nqs_sdk.bindings.tx_generators.abstract_transaction import Transaction
from nqs_sdk.bindings.tx_generators.historical_tx_generator import HistoricalTxGenerator


DATA_SOURCE = quantlib.QuantlibDataProvider(os.getenv("QUANTLIB_CONFIG"))


class UniswapV3HistoricalTxGenerator(HistoricalTxGenerator):
    def __init__(self, pool: UniswapV3Pool) -> None:
        super().__init__()

        self.pool = pool
        self.transactions: dict[int, list[Transaction]] = {}

    def get_transactions(self, start_block: int, end_block: int) -> list[Transaction]:
        txns = []
        for block in range(start_block, end_block + 1):
            if block in self.transactions:
                txns += self.transactions[block]

        return txns

    def cache_transactions(self, start_block: int, end_block: int) -> None:
        formatted_begin = BlockNumberOrTimestamp.block_number(start_block)
        formatted_end = BlockNumberOrTimestamp.block_number(end_block)
        data = DATA_SOURCE.uniswap_v3_pool_calls(contract=self.pool.address, begin=formatted_begin, end=formatted_end)
        data_calls: dict = data.move_as_dict()
        call_names = data_calls["call_name"]
        blocks = data_calls["block_number"]
        index = data_calls["trace_index"]
        data_vec = data_calls["data"]

        orders: dict[int, list[int]] = {}
        for i, call_name in enumerate(call_names):
            call_block = blocks[i]

            if call_block not in self.transactions:
                self.transactions[call_block] = []
                orders[call_block] = []

            data = data_vec[i]  # JSON map

            if call_name == "Swap":
                self.transactions[call_block].append(
                    RawSwapTransaction(
                        amount=data["amountSpecified"],
                        zero_for_one=data["zeroForOne"],
                        sqrt_price_limit_x96=data["sqrtPriceLimitX96"],
                    )
                )
                orders[call_block].append(index[i])
            elif call_name == "Mint":
                self.transactions[call_block].append(
                    RawMintTransaction(
                        amount=data["amount"], tick_lower=data["tickLower"], tick_upper=data["tickUpper"]
                    )
                )
                orders[call_block].append(index[i])
            elif call_name == "Burn":
                self.transactions[call_block].append(
                    RawBurnTransaction(
                        amount=data["amount"], tick_lower=data["tickLower"], tick_upper=data["tickUpper"]
                    )
                )
                orders[call_block].append(index[i])
            elif call_name == "Collect":
                self.transactions[call_block].append(
                    RawCollectTransaction(
                        amount_0_requested=data["amount0Requested"],
                        amount_1_requested=data["amount1Requested"],
                        tick_lower=data["tickLower"],
                        tick_upper=data["tickUpper"],
                    )
                )
                orders[call_block].append(int(index[i]))

        for block in range(start_block, end_block + 1):
            if block in self.transactions:
                self.transactions[block] = sorted(
                    self.transactions[block], key=lambda x: orders[block][self.transactions[block].index(x)]
                )

    def get_next_block(self, current_block: int) -> Optional[int]:
        return None

    @property
    def protocol_id(self) -> str:
        return self.pool.name
