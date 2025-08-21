import numpy as np

from nqs_sdk.bindings.spots.spot_generator import SpotGenerator


class WGNSpotGenerator(SpotGenerator):
    def __init__(self, token_pairs: list[tuple[str, str]], s0: float, mean: float, vol: float) -> None:
        super().__init__(token_pairs)

        n = len(token_pairs)
        self.s0 = np.array(s0) if isinstance(s0, (list, tuple, np.ndarray)) else np.full(n, s0)
        self.mean = np.array(mean) if isinstance(mean, (list, tuple, np.ndarray)) else np.full(n, mean)
        self.vol = np.array(vol) if isinstance(vol, (list, tuple, np.ndarray)) else np.full(n, vol)

    def generate_spot_timestamps(self, ts: list[int]) -> list[tuple[list[int], list[float]]]:
        """
        Generate spot price trajectories for each token pair using a fully vectorized
        geometric Brownian motion model. The noise computation is vectorized over time
        and token pairs.

        Args:
            timestamps: List of timestamps for price generation

        Returns:
            A list of corresponding spot prices for each timestamp
        """
        # Convert timestamps to numpy array and calculate time differences
        timestamps = np.array(ts)
        dt = np.diff(timestamps, prepend=timestamps[0])  # Time intervals between steps
        t = len(timestamps)
        n = len(self.token_pairs)

        # Generate a T x n noise matrix.
        # For each time step, the noise's standard deviation is sqrt(dt); we reshape for broadcasting.
        noise = np.random.normal(loc=0, scale=np.sqrt(dt)[:, None], size=(t, n))

        # Compute spot prices in a single vectorized step.
        # For token pair i and time t:
        #   spot(t,i) = s0[i] * exp((mean[i] - 0.5*vol[i]**2)*dt + vol[i]*noise(t,i))
        spots = self.s0[None, :] * np.exp(
            (self.mean[None, :] - 0.5 * self.vol[None, :] ** 2) * dt[:, None] + self.vol[None, :] * noise
        )

        return [(ts, [float(price) for price in pair_prices]) for pair_prices in spots.T]
