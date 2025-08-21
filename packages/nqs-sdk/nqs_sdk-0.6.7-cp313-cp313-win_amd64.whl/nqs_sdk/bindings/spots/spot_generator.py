import os
from abc import ABC, abstractmethod

from nqs_sdk import BlockNumberOrTimestamp, quantlib


DATA_SOURCE = quantlib.QuantlibDataProvider(os.getenv("QUANTLIB_CONFIG"))


class SpotGenerator(ABC):
    def __init__(self, token_pairs: list[tuple[str, str]]) -> None:
        self.token_pairs = token_pairs

    @property
    def names(self) -> list[str]:
        return [f"{pair[0]}/{pair[1]}" for pair in self.token_pairs]

    @abstractmethod
    def generate_spot_timestamps(self, timestamps: list[int]) -> list[tuple[list[int], list[float]]]:
        pass

    def generate_spot(self, start_block: int, end_block: int) -> list[tuple[list[int], list[float]]]:
        time = DATA_SOURCE.blocks_from_interval(
            "Ethereum",
            begin=BlockNumberOrTimestamp.block_number(start_block),
            end=BlockNumberOrTimestamp.block_number(end_block),
        ).move_as_dict()

        timestamps = time["timestamp"]

        return self.generate_spot_timestamps(timestamps)
