from decimal import Decimal

from nqs_sdk import TxRequest
from nqs_sdk.bindings.tx_generators.abstract_transaction import Transaction


class RebalanceTransaction(Transaction):
    token0: str
    token1: str
    weight0: Decimal
    weight1: Decimal
    execution_price: Decimal

    def __init__(
        self,
        token0: str,
        token1: str,
        weight0: float | Decimal,
        weight1: float | Decimal,
        current_price: float | Decimal,
    ) -> None:
        super().__init__()

        self.token0 = token0
        self.token1 = token1
        self.weight0 = Decimal(weight0)
        self.weight1 = Decimal(weight1)
        self.execution_price = Decimal(current_price)

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        return TxRequest.new_with_order(protocol="cex", sender=sender, source=source, payload=self, order=order)


class OpenMarginPositionTransaction(Transaction):
    token: str
    direction: bool
    amount: Decimal
    collateral: str
    collateral_amount: Decimal
    token_id: str

    def __init__(
        self,
        token: str,
        direction: bool,
        amount: float | Decimal,
        collateral: str,
        collateral_amount: float | Decimal,
        execution_price: float | Decimal,
        token_id: str,
    ) -> None:
        super().__init__()

        self.token = token
        self.direction = direction
        self.amount = Decimal(amount)
        self.collateral = collateral
        self.collateral_amount = Decimal(collateral_amount)
        self.execution_price = Decimal(execution_price)
        self.token_id = token_id

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        return TxRequest.new_with_order(protocol="cex", sender=sender, source=source, payload=self, order=order)


class CheckMarginPositionTransaction(Transaction):
    current_prices: list[Decimal]
    maintenance_fees: dict[str, Decimal]

    def __init__(self, current_prices: list[float | Decimal], maintenance_fees: dict[str, float | Decimal]) -> None:
        super().__init__()

        self.current_prices = [Decimal(price) for price in current_prices]
        self.maintenance_fees = {token: Decimal(fee) for token, fee in maintenance_fees.items()}

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        return TxRequest.new_with_order(protocol="cex", sender=sender, source=source, payload=self, order=order)


class CloseMarginPositionTransaction(Transaction):
    token_id: str
    execution_price: Decimal

    def __init__(self, token_id: str, execution_price: float | Decimal, price_history: list[float | Decimal]) -> None:
        super().__init__()

        self.token_id = token_id
        self.execution_price = Decimal(execution_price)
        self.price_history = [Decimal(price) for price in price_history]

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        return TxRequest.new_with_order(protocol="cex", sender=sender, source=source, payload=self, order=order)


class AddMarginCollateralTransaction(Transaction):
    token_id: str
    amount: Decimal

    def __init__(self, token_id: str, amount: float | Decimal) -> None:
        super().__init__()

        self.token_id = token_id
        self.amount = Decimal(amount)

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        return TxRequest.new_with_order(protocol="cex", sender=sender, source=source, payload=self, order=order)


class ExchangeTransaction(Transaction):
    token0: str
    token1: str
    direction: bool
    amount: Decimal
    execution_price: Decimal

    def __init__(
        self, token0: str, token1: str, direction: bool, amount: float | Decimal, execution_price: float | Decimal
    ) -> None:
        super().__init__()

        self.token0 = token0
        self.token1 = token1
        self.direction = direction
        self.amount = Decimal(amount)
        self.execution_price = Decimal(execution_price)

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        return TxRequest.new_with_order(protocol="cex", sender=sender, source=source, payload=self, order=order)
