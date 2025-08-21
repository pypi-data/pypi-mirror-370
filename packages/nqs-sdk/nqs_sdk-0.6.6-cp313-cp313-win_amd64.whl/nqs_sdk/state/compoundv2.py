from typing import Any, Dict, Optional

from nqs_sdk.nqs_sdk import TokenMetadata


class StateCERC20(TokenMetadata):
    def __new__(
        cls,
        name: str,
        symbol: str,
        decimals: int,
        underlying_symbol: str,
        underlying_address: str,
        comptroller_id: str,
        total_supply: Optional[int] = None,
        block_number: Optional[int] = None,
        block_timestamp: Optional[int] = None,
    ) -> TokenMetadata:
        instance = super().__new__(cls, name=name, symbol=symbol, decimals=decimals)
        return instance

    def __init__(
        self,
        name: str,
        symbol: str,
        decimals: int,
        underlying_symbol: str,
        underlying_address: str,
        comptroller_id: str,
        total_supply: Optional[int] = None,
        block_number: Optional[int] = None,
        block_timestamp: Optional[int] = None,
    ):
        self.underlying_symbol = underlying_symbol
        self.underlying_address = underlying_address
        self.comptroller_id = comptroller_id
        self.total_supply = total_supply
        self.block_number = block_number
        self.block_timestamp = block_timestamp

    # Override the TokenMetadata__getstate__
    def __getstate__(self) -> dict:
        state = self.__dict__
        return state

    # Override the TokenMetadata__setstate__
    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__dict__.update(state)

    # Prepare the arguments passed to StateCERC20__new__ during the unpickle process
    def __getnewargs__(self) -> tuple:
        # StateCERC20 is created with empty underlying_symbol, underlying_address and comptroller_id,
        # they will be set by __setstate__
        return (self.name, self.symbol, self.decimals, "", "", "")

    # Override the TokenMetadata__repr__
    def __repr__(self) -> str:
        return (
            "StateCERC20(name={}, ".format(self.name)
            + "symbol={}, ".format(self.symbol)
            + "decimals={}, ".format(self.decimals)
            + "underlying_symbol={}, ".format(self.underlying_symbol)
            + "underlying_address={}, ".format(self.underlying_address)
            + "comptroller_id={}, ".format(self.comptroller_id)
            + "total_supply={}, ".format(self.total_supply)
            + "block_number={}, ".format(self.block_number)
            + "block_timestamp={})".format(self.block_timestamp)
        )

    # Override the TokenMetadata__str__
    def __str__(self) -> str:
        return self.__repr__()
