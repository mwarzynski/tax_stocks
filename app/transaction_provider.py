from abc import abstractmethod

from .transaction import Transaction


class TransactionProvider:
    @abstractmethod
    def provide_transactions(self) -> list[Transaction]:
        raise NotImplementedError
