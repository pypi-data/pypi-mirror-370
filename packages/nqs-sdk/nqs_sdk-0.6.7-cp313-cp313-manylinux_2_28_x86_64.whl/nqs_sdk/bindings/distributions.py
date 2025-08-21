from abc import ABC, abstractmethod
from typing import Any, Union

import numpy as np
from pydantic import BaseModel


class Distribution(BaseModel, ABC):
    name: str
    dtype: str

    @abstractmethod
    def sample(self) -> Any:
        pass


class UniformDistribution(Distribution):
    name: str = "uniform"
    min: float
    max: float

    def sample(self) -> Union[int, float]:
        if self.dtype == "int":
            return np.random.randint(int(self.min), int(self.max) + 1)
        elif self.dtype == "float":
            return np.random.uniform(self.min, self.max)
        else:
            raise ValueError(f"Invalid dtype: {self.dtype}")


class PoissonDistribution(Distribution):
    name: str = "poisson"
    lam: float

    def sample(self) -> int:
        assert self.dtype == "int", f"Poisson distribution must be of type int, got {self.dtype}"
        return np.random.poisson(self.lam)


class NormalDistribution(Distribution):
    name: str = "normal"
    mean: float
    std: float

    def sample(self) -> float:
        assert self.dtype == "float", f"Normal distribution must be of type float, got {self.dtype}"
        return np.random.normal(self.mean, self.std)


class ExponentialDistribution(Distribution):
    name: str = "exponential"
    lamb: float

    def sample(self) -> float:
        assert self.dtype == "float", f"Exponential distribution must be of type float, got {self.dtype}"
        return np.random.exponential(self.lamb)


class BinomialDistribution(Distribution):
    name: str = "binomial"
    n: int
    p: float

    def sample(self) -> int:
        assert self.dtype == "int", f"Binomial distribution must be of type int, got {self.dtype}"
        return np.random.binomial(self.n, self.p)
