import os
from decimal import Decimal
from typing import Optional, Type, TypeVar

from pydantic import BaseModel

from nqs_sdk import quantlib

from ..protocol_infos import ProtocolInfos


T = TypeVar("T", bound="UniswapV3Pool")


class UniswapV3Pool(BaseModel, ProtocolInfos):
    address: Optional[str] = None
    fee_tier: Decimal
    token0: str
    token1: str
    decimals0: int
    decimals1: int
    block_number: Optional[int] = None
    initial_balance: Optional[dict] = None

    @classmethod
    def from_address(cls: Type[T], pool_address: str, block_number: int) -> T:
        data_source = quantlib.QuantlibDataProvider(os.getenv("QUANTLIB_CONFIG"))
        pool_data = data_source.uniswap_v3_pool_info(pool_address)
        decimals0 = pool_data.token0_decimals
        decimals1 = pool_data.token1_decimals

        return cls(
            token0=pool_data.token0_symbol,
            token1=pool_data.token1_symbol,
            fee_tier=pool_data.fee_tier,
            address=pool_address,
            block_number=block_number,
            decimals0=decimals0,
            decimals1=decimals1,
        )

    @classmethod
    def from_params(cls: Type[T], token0: str, token1: str, fee_tier: float | Decimal, block_number: int) -> T:
        # get the address of the pool
        data_source = quantlib.QuantlibDataProvider(os.getenv("QUANTLIB_CONFIG"))
        pool_addresses = data_source.uniswap_v3_token_pair_pools(token0, token1).move_as_dict()
        fee_tiers = pool_addresses["fee_tier"]
        fee_tier_decimal: Decimal = (
            fee_tier if isinstance(fee_tier, Decimal) else Decimal(fee_tier).quantize(Decimal("0.0001"))
        )
        # Get index of the fee tier that matches the input fee_tier
        fee_tier_idx = next((i for i, ft in enumerate(fee_tiers) if ft == fee_tier_decimal), None)
        if fee_tier_idx is None:
            raise ValueError(
                f"Pool address for {token0}/{token1} with fee tier {fee_tier_decimal} not found. "
                f"Possible fee tiers: {fee_tiers}"
            )

        address = pool_addresses["pool_address"][fee_tier_idx]
        token0_symbol = pool_addresses["token0_symbol"][fee_tier_idx]
        token1_symbol = pool_addresses["token1_symbol"][fee_tier_idx]

        decimals0 = pool_addresses["token0_decimals"][fee_tier_idx]
        decimals1 = pool_addresses["token1_decimals"][fee_tier_idx]

        return cls(
            token0=token0_symbol,
            token1=token1_symbol,
            fee_tier=fee_tier_decimal,
            address=address,
            block_number=block_number,
            decimals0=decimals0,
            decimals1=decimals1,
        )

    @classmethod
    def from_custom_params(
        cls: Type[T],
        token0: str,
        token1: str,
        fee_tier: float | Decimal,
        initial_amount: int,
        unit: str,
    ) -> T:
        assert unit in ["token0", "token1"], "Unit must be either token0 or token1"

        data_source = quantlib.QuantlibDataProvider(os.getenv("QUANTLIB_CONFIG"))
        pool_addresses = data_source.uniswap_v3_token_pair_pools(token0, token1).move_as_dict()

        fee_tiers = pool_addresses["fee_tier"]
        fee_tier_decimal: Decimal = (
            fee_tier if isinstance(fee_tier, Decimal) else Decimal(fee_tier).quantize(Decimal("0.0001"))
        )
        # Get index of the fee tier that matches the input fee_tier
        fee_tier_idx = next((i for i, ft in enumerate(fee_tiers) if ft == fee_tier_decimal), None)
        if fee_tier_idx is None:
            raise ValueError(
                f"Pool address for {token0}/{token1} with fee tier {fee_tier_decimal} not found. "
                f"Possible fee tiers: {fee_tiers}"
            )

        address = pool_addresses["pool_address"][fee_tier_idx]
        token0_symbol = pool_addresses["token0_symbol"][fee_tier_idx]
        token1_symbol = pool_addresses["token1_symbol"][fee_tier_idx]

        decimals0 = pool_addresses["token0_decimals"][fee_tier_idx]
        decimals1 = pool_addresses["token1_decimals"][fee_tier_idx]

        return cls(
            token0=token0_symbol,
            token1=token1_symbol,
            fee_tier=fee_tier_decimal,
            address=address,
            initial_balance={"amount": initial_amount, "unit": unit},
            decimals0=decimals0,
            decimals1=decimals1,
        )

    def get_token_infos(self) -> dict[str, int]:
        return {self.token0: self.decimals0, self.token1: self.decimals1}

    @property
    def name(self) -> str:
        fee_tier = str(self.fee_tier).replace(".", "").rstrip("0")
        return f"univ3_{self.token0.lower()}_{self.token1.lower()}_{fee_tier}"

    @property
    def token_pair(self) -> str:
        return f"{self.token0}/{self.token1}"

    @property
    def factory_id(self) -> str:
        return "uniswap_v3"
