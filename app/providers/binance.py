import csv
from os import listdir
from os.path import isfile, join

from app.crypto import *


class Binance(TransactionProvider):

    _transactions = List[Transaction]

    def __init__(self, folder: str = "data/investing/binance") -> None:
        super().__init__()
        self._transactions = self._parse_folder(folder)

    def _parse_folder(self, folder: str) -> List[Transaction]:
        files = [f for f in listdir(folder) if isfile(join(folder, f))]
        transactions = []
        for file in files:
            transactions += self._parse_file(join(folder, file))
        return transactions

    def _parse_file(self, file_name: str) -> List[Transaction]:
        transactions: List[Transaction] = []
        with open(file_name, "r") as f:
            reader = csv.reader(f, delimiter=",")
            try:
                next(reader)  # skip header row (which contains description of columns)
            except StopIteration:
                return []
            for row in reader:
                time_at = datetime.strptime(row[1].split(" ")[0], "%Y-%m-%d")  # 2021-01-04 15:14:23
                operation = self._parse_operation(row[3])
                currency = self._parse_currency(row[4])
                change = Decimal(row[5])
                if operation == Operation.UNKNOWN or currency == Currency.UNKNOWN:
                    continue
                transactions.append(
                    Transaction(time_at=time_at, operation=operation, currency=currency, change=change, comment=row[6])
                )
        return transactions

    @staticmethod
    def _parse_operation(v: str) -> Operation:
        if v == "Deposit":
            return Operation.DEPOSIT
        elif v == "Withdraw":
            return Operation.WITHDRAW
        return Operation.UNKNOWN

    @staticmethod
    def _parse_currency(v: str) -> Currency:
        if v == "EUR":
            return Currency.EUR
        elif v == "USD":
            return Currency.USD
        return Currency.UNKNOWN

    def get_transactions(self) -> List[Transaction]:
        return self._transactions
