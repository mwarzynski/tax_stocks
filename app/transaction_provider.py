from abc import abstractmethod
from typing import List

from .transaction import Transaction


class TransactionProvider:

    @abstractmethod
    def provide(self) -> List[Transaction]:
        return []
