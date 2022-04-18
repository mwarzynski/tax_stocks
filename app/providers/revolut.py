import csv
from typing import List
import datetime
from decimal import Decimal
from os import listdir, stat
from os.path import isfile, join

from app.transaction import Transaction, Activity
from app.transfer import Operation, Transfer
from app.exchange import Currency


class Revolut:

    folder: str

    def __init__(self, folder: str = "data/investing/revolut", print_invalid_lines: bool = False):
        self.folder = folder
        self.print_invalid_lines = print_invalid_lines

    def provide_transfers(self) -> List[Transfer]:
        files = [f for f in listdir(self.folder) if isfile(join(self.folder, f))]
        transfers = []
        for file in files:
            if "crypto" not in file:
                continue
            transfers += self._provide_transfers_from(join(self.folder, file))
        return transfers

    def provide_transactions(self) -> List[Transaction]:
        files = [f for f in listdir(self.folder) if isfile(join(self.folder, f))]
        transactions = []
        for file in files:
            if "crypto" in file:
                continue
            transactions += self._provide_transactions_from(join(self.folder, file))
        return transactions

    @staticmethod
    def _provide_transfers_from(file_name: str) -> List[Transfer]:
        transfers = []
        with open(file_name, "r") as f:
            reader = csv.reader(f, delimiter=",")
            try:
                next(reader)  # skip header row (which contains description of columns)
            except StopIteration:
                return []
            for row in reader:
                # Date, Operation, Money out, Fee, From, To
                # Note: This is my custom format that I manually created.
                #   For this reason, there is no easy way to extract information from Revolut for this Provider.
                #   Feel free to create your own file to provide crypto transfers data.
                date = datetime.datetime.strptime(row[0], "%d-%m-%Y")
                operation = Operation.WITHDRAW
                value = Decimal(row[6])
                currency = Currency.PLN
                transfers.append(
                    Transfer(
                        time_at=date,
                        operation=operation,
                        currency=currency,
                        change=value,
                        comment="",
                    )
                )
        return transfers

    @staticmethod
    def _provide_transactions_from(file_name: str) -> List[Transaction]:
        transactions = []
        with open(file_name, "r") as f:
            reader = csv.reader(f, delimiter=",")
            try:
                next(reader)  # skip header row (which contains description of columns)
            except StopIteration:
                return []
            for row in reader:
                # Date,Ticker,Type,Quantity,Price per share,Total Amount,Currency,FX Rate
                date = datetime.datetime.strptime(row[0].split(" ")[0], "%d/%m/%Y")

                try:
                    activity = Activity(row[2])
                except ValueError:
                    continue

                if activity is Activity.DIV:
                    quantity = Decimal(0)
                    price = Decimal(0)
                    amount = Decimal(row[5])
                    # Note: assumption here is that only US stocks were bought, therefore 15% tax.
                    original_value = round((amount / Decimal(85.0)) * 100, 2)
                    dividend_tax_deducted = round(original_value - amount, 2)
                elif activity is Activity.SSP:
                    quantity = Decimal(row[3])
                    price = Decimal(0)
                    amount = Decimal(0)
                    dividend_tax_deducted = Decimal(0)
                else:
                    quantity = Decimal(row[3])
                    price = Decimal(row[4])
                    amount = Decimal(row[5])
                    dividend_tax_deducted = Decimal(0)

                currency = Currency(row[6])

                transaction = Transaction(
                    trade_date=date,  # 20/04/1969
                    settle_date=date,  # 20/04/1969
                    currency=currency,  # USD
                    activity=activity,  # BUY,SELL
                    symbol=row[1],  # AAPL
                    quantity=quantity,  # 100
                    price=price,  # 420.69
                    amount=amount,  # 42069
                    dividend_tax_deducted=dividend_tax_deducted,
                )

                transactions.append(transaction)

        return transactions
