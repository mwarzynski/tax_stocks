from abc import abstractmethod
from typing import List

from .transaction import Transaction


class TransactionProvider:
    @abstractmethod
    def provide_transactions(self) -> List[Transaction]:
        return []
