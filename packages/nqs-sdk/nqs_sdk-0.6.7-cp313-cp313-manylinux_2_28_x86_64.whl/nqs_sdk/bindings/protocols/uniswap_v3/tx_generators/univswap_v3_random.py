import random
from typing import Optional

from pydantic import BaseModel

from nqs_sdk.bindings.distributions import Distribution
from nqs_sdk.bindings.protocols.uniswap_v3.uniswap_v3_pool import UniswapV3Pool
from nqs_sdk.bindings.protocols.uniswap_v3.uniswap_v3_transactions import (
    RawBurnTransaction,
    RawMintTransaction,
    RawSwapTransaction,
)
from nqs_sdk.bindings.tx_generators.abstract_transaction import Transaction
from nqs_sdk.bindings.tx_generators.random_tx_generator import RandomTxGenerator


class UniswapV3Distribution(BaseModel):
    frequency: Distribution
    params: dict[str, Distribution]


class UniswapV3RandomTxGenerator(RandomTxGenerator):
    def __init__(
        self,
        pool: UniswapV3Pool,
        mint_distribution: UniswapV3Distribution,
        burn_distribution: UniswapV3Distribution,
        swap_distribution: UniswapV3Distribution,
    ) -> None:
        """
        Initialize the random transaction generator for Uniswap V3.
        """
        super().__init__()

        self.mint_distribution = mint_distribution
        self.burn_distribution = burn_distribution
        self.swap_distribution = swap_distribution
        self.minted_positions: list[tuple[int, dict]] = []
        self.pool = pool

    def _generate_params(self, distribution: UniswapV3Distribution) -> dict:
        params = {}
        for param_name in distribution.params:
            params[param_name] = distribution.params[param_name].sample()

        return params

    def get_transactions(self, start_block: int, end_block: int) -> list[Transaction]:
        """
        For each block in the given range, sample the number of transactions from a Poisson distribution
        and create that many dummy transactions.
        """
        transactions: list[tuple[int, Transaction]] = []

        # parse burn transactions first to get token ids from previous blocks
        for block in range(start_block, end_block + 1):
            # Determine the number of transactions for the block
            n_tx = self.burn_distribution.frequency.sample()
            for _ in range(n_tx):
                if not self.minted_positions:
                    break
                params = self._generate_params(self.burn_distribution)
                position = self.minted_positions.pop(random.randint(0, len(self.minted_positions) - 1))
                burn_txn = RawBurnTransaction(
                    tick_lower=position[1]["tick_lower"],
                    tick_upper=position[1]["tick_upper"],
                    amount=position[1]["amount"],
                )
                transactions.append((block, burn_txn))

        # parse mint transactions
        for block in range(start_block, end_block + 1):
            # Determine the number of transactions for the block
            n_tx = self.mint_distribution.frequency.sample()
            for _ in range(n_tx):
                params = self._generate_params(self.mint_distribution)
                mint_txn = RawMintTransaction(**params)
                self.minted_positions.append((block, params))
                transactions.append((block, mint_txn))

        # parse swap transactions
        for block in range(start_block, end_block + 1):
            # Determine the number of transactions for the block
            n_tx = self.swap_distribution.frequency.sample()
            for _ in range(n_tx):
                params = self._generate_params(self.swap_distribution)
                swap_txn = RawSwapTransaction(amount=params["amount"], zero_for_one=params["token_0"])
                transactions.append((block, swap_txn))

        # shuffle burn mint swap and resort by block number
        random.shuffle(transactions)
        transactions.sort(key=lambda txn: txn[0])

        return [txn[1] for txn in transactions]

    def get_next_block(self, current_block: int) -> Optional[int]:
        return None

    @property
    def protocol_id(self) -> str:
        return self.pool.name
