from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from decimal import Decimal
from typing import List


class Currency(Enum):
    UNKNOWN = 0
    USD = 1
    EUR = 2


class Operation(Enum):
    UNKNOWN = 0
    DEPOSIT = 1
    WITHDRAW = 2


@dataclass
class Transaction:
    time_at: datetime
    operation: Operation
    currency: Currency
    change: Decimal
    comment: str


class TransactionProvider:
    @abstractmethod
    def get_transactions() -> List[Transaction]:
        pass
