from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from decimal import Decimal
from .exchange import Exchange, Currency
from typing import List, Dict


class Operation(Enum):
    UNKNOWN = 0
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


@dataclass
class Transfer:
    time_at: datetime
    operation: Operation
    currency: Currency
    change: Decimal
    comment: str


class TransferProvider:
    @abstractmethod
    def provide_transfers(self) -> list[Transfer]:
        pass


class TransferSummary:
    _transfers: List[Transfer]
    _exchange: Exchange

    def __init__(self, transfers: List[Transfer], exchange: Exchange) -> None:
        self._transfers = transfers
        self._exchange = exchange

    def summary(self, year: int) -> Dict[Operation, Decimal]:
        result = {
            Operation.DEPOSIT: Decimal(0),
            Operation.WITHDRAW: Decimal(0),
        }
        for transfer in self._transfers:
            if transfer.time_at.year != year:
                continue
            ratio = self._exchange.ratio(
                day=transfer.time_at,
                c_from=transfer.currency,
                c_to=Currency.PLN,
            )
            value = transfer.change * ratio
            if transfer.operation == Operation.DEPOSIT:
                result[transfer.operation] += value
            elif transfer.operation == Operation.WITHDRAW:
                result[transfer.operation] += value
        return result


class Crypto(TransferSummary):
    def print_summary(self, year: int):
        print("\n\n=== Crypto\n")

        r = self.summary(year)
        for operation, change in r.items():
            print(f"{str(operation.name).title()} \t = {round(change, 4)} PLN")
