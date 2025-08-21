import os

from nqs_sdk import BlockNumberOrTimestamp, quantlib
from nqs_sdk.bindings.protocols.uniswap_v3.uniswap_v3_pool import UniswapV3Pool
from nqs_sdk.bindings.spots.spot_generator import SpotGenerator


DATA_SOURCE = quantlib.QuantlibDataProvider(os.getenv("QUANTLIB_CONFIG"))


class HistoricalSpotGenerator(SpotGenerator):
    def __init__(self, pools: list[UniswapV3Pool]) -> None:
        super().__init__([(pool.token0, pool.token1) for pool in pools])

        self.pools = pools

    def generate_spot_timestamps(self, timestamps: list[int]) -> list[tuple[list[int], list[float]]]:
        spots = []
        for pool in self.pools:
            data = DATA_SOURCE.uniswap_v3_pool_exchange_rate(
                pool.address,
                BlockNumberOrTimestamp.timestamp(timestamps[0]),
                BlockNumberOrTimestamp.timestamp(timestamps[-1]),
            ).move_as_dict()

            timestamp = data["timestamp"]
            spot = data["exchange_rate"]

            spots.append((timestamp, spot))

        return spots
