import os
from dataclasses import dataclass
from typing import Any

from nqs_sdk import quantlib


DATA_SOURCE = quantlib.QuantlibDataProvider(os.getenv("QUANTLIB_CONFIG"))


# A class to identify arbitrage transactions
class ArbitrageTransaction: ...


# Represents a wrapped event from the build_tx_payload() to be
# parsed in the execute_tx()
class WrappedEvent:
    def __init__(
        self,
        action_type: Any,
        protocol_id: Any,
        protocol: Any,
        args: dict,
    ) -> None:
        self.action_type = action_type
        self.block_number = None
        self.protocol_id = protocol_id
        self.protocol = protocol
        self.args = args

    def map_tx(self) -> dict:
        tx_data = {
            "action_type": self.action_type,
            "block_number": -1,
            "protocol_id": self.protocol_id,
            "protocol": self.protocol,
        }
        tx_data.update(self.args)

        return tx_data


@dataclass
class TokenInfo:
    decimals: int
    symbol: str


def get_all_tokens() -> dict:
    tk_infos = DATA_SOURCE.all_token_info("Ethereum").move_as_dict()
    tokens_metadata = {
        token: TokenInfo(symbol=token, decimals=int(decimals))
        for token, decimals, verified in zip(tk_infos["symbol"], tk_infos["decimals"], tk_infos["verified"])
        if token is not None and verified
    }

    return tokens_metadata
