import csv
from typing import List
import datetime
from decimal import Decimal
from os import listdir
from os.path import isfile, join

from app.transaction import Transaction, Activity


class Revolut:

    folder: str

    def __init__(self, folder: str = "data/investing/revolut", print_invalid_lines: bool = False):
        self.folder = folder
        self.print_invalid_lines = print_invalid_lines

    def provide(self) -> List[Transaction]:
        files = [f for f in listdir(self.folder) if isfile(join(self.folder, f))]
        transactions = []
        for file in files:
            transactions += self._provide_for_file(join(self.folder, file))
        return transactions

    @staticmethod
    def _provide_for_file(file_name: str) -> List[Transaction]:
        transactions = []
        with open(file_name, "r") as f:
            reader = csv.reader(f, delimiter=',')
            try:
                next(reader)  # skip header row (which contains description of columns)
            except StopIteration:
                return []
            for row in reader:
                # Date,Ticker,Type,Quantity,Price per share,Total Amount,Currency,FX Rate
                date = datetime.datetime.strptime(row[0].split(" ")[0], '%d/%m/%Y')

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

                currency = row[6]

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
