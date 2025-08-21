from typing import Callable, Optional

import numpy as np

from nqs_sdk.bindings.spots.spot_generator import SpotGenerator


class ItoSpotGenerator(SpotGenerator):
    def __init__(
        self,
        token_pairs: list[tuple[str, str]],
        s0: list[float],
        drift_func: Optional[Callable[[np.ndarray, np.ndarray], np.ndarray]] = None,
        diffusion_func: Optional[Callable[[np.ndarray, np.ndarray], np.ndarray]] = None,
        mean: float = 0.0,
        vol: float = 0.1,
    ) -> None:
        """
        Initialize an Ito process spot price generator.

        Args:
            token_pairs: List of token pairs
            s0: Initial spot price(s)
            drift_func: Custom drift function f(S, t) -> drift. If None, uses GBM default μS.
            diffusion_func: Custom diffusion function f(S, t) -> diffusion. If None, uses GBM default σS.
            mean: Mean parameter (used if default drift function is applied)
            vol: Volatility parameter (used if default diffusion function is applied)
        """
        super().__init__(token_pairs)

        n = len(token_pairs)
        self.s0 = np.array(s0) if isinstance(s0, (list, tuple, np.ndarray)) else np.full(n, s0)
        self.mean = np.array(mean) if isinstance(mean, (list, tuple, np.ndarray)) else np.full(n, mean)
        self.vol = np.array(vol) if isinstance(vol, (list, tuple, np.ndarray)) else np.full(n, vol)

        # Default drift function for GBM: μS
        self.drift_func = drift_func or (lambda s, t: self.mean[None, :] * s)

        # Default diffusion function for GBM: σS
        self.diffusion_func = diffusion_func or (lambda s, t: self.vol[None, :] * s)

    def generate_spot_timestamps(self, ts: list[int]) -> list[tuple[list[int], list[float]]]:
        """
        Generate spot price trajectories for each token pair using a general Ito process.

        The process follows:
        dS(t) = drift_func(S, t)dt + diffusion_func(S, t)dW(t)

        Using Euler-Maruyama discretization.

        Args:
            ts: List of timestamps for price generation

        Returns:
            A list of corresponding spot prices for each timestamp
        """
        # Convert timestamps to numpy array and calculate time differences
        timestamps = np.array(ts)
        dt = np.diff(timestamps, prepend=timestamps[0])  # Time intervals between steps
        t = len(timestamps)
        n = len(self.token_pairs)

        # Initialize the spot price array
        spots = np.zeros((t, n))
        spots[0, :] = self.s0

        # Generate a T x n noise matrix
        dw = np.random.normal(loc=0, scale=np.sqrt(dt)[:, None], size=(t, n))

        # Euler-Maruyama method for numerical solution
        for i in range(1, t):
            current_time = timestamps[i - 1] * np.ones((1, n))

            # Calculate drift and diffusion terms
            drift = self.drift_func(spots[i - 1 : i, :], current_time)
            diffusion = self.diffusion_func(spots[i - 1 : i, :], current_time)

            # Update spot prices using Euler-Maruyama method
            spots[i, :] = spots[i - 1, :] + drift.flatten() * dt[i] + diffusion.flatten() * dw[i, :]

        return [(ts, [float(price) for price in pair_prices]) for pair_prices in spots.T]


class OUSpotGenerator(ItoSpotGenerator):
    def __init__(
        self, token_pairs: list[tuple[str, str]], s0: list[float], mean_reversion: float, equilibrium: float, vol: float
    ) -> None:
        """
        Ornstein-Uhlenbeck process: dS = θ(μ-S)dt + σdW

        Args:
            token_pairs: List of token pairs
            s0: Initial spot price(s)
            mean_reversion: Mean reversion rate (θ)
            equilibrium: Equilibrium level (μ)
            vol: Volatility (σ)
        """
        n = len(token_pairs)
        self.mean_reversion = (
            np.array(mean_reversion)
            if isinstance(mean_reversion, (list, tuple, np.ndarray))
            else np.full(n, mean_reversion)
        )
        self.equilibrium = (
            np.array(equilibrium) if isinstance(equilibrium, (list, tuple, np.ndarray)) else np.full(n, equilibrium)
        )

        # Define OU process drift: θ(μ-S)
        def drift_func(s: np.ndarray, t: np.ndarray) -> np.ndarray:
            return np.array(self.mean_reversion[None, :] * (self.equilibrium[None, :] - s))

        # Define OU process diffusion: σ (constant, not dependent on S)
        def diffusion_func(s: np.ndarray, t: np.ndarray) -> np.ndarray:
            return (
                np.tile(vol, (s.shape[0], 1)) if isinstance(vol, (list, tuple, np.ndarray)) else np.full(s.shape, vol)
            )

        super().__init__(token_pairs, s0, drift_func, diffusion_func)
