from nqs_sdk.bindings.spots.spot_generator import SpotGenerator


class FixedSpotGenerator(SpotGenerator):
    def __init__(self, token_pairs: list[tuple[str, str]], values: list[float]) -> None:
        super().__init__(token_pairs)

        self.values = values

    def generate_spot_timestamps(self, ts: list[int]) -> list[tuple[list[int], list[float]]]:
        return [(ts, [self.values[i] for _ in range(len(ts))]) for i in range(len(self.token_pairs))]
