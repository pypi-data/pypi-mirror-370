from decimal import Decimal
from typing import Any


def to_decimal_exp(n: int, base: int) -> Decimal:
    return Decimal(n).scaleb(-base)


def rescale_to_int(n: float, base: int) -> int:
    return round(Decimal(n).scaleb(base))


def convert_to_int(n: Decimal, base: int) -> int:
    return round(n.scaleb(base))


def to_int(n: Any) -> int:
    try:
        return int(n, 0)
    except TypeError:
        if isinstance(n, int):
            return n
        else:
            return 0
