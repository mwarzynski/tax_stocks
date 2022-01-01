import csv
import re

from typing import List
import datetime
from decimal import Decimal

from app.transaction import Transaction, Activity


class Revolut:

    def __init__(self, file_name: str = "data.csv", print_invalid_lines: bool = False):
        self.file_name = file_name
        self.print_invalid_lines = print_invalid_lines

    def provide(self) -> List[Transaction]:
        raw_transactions = []
        with open(self.file_name, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                raw_transactions.append(row[0])

        transactions = []
        for rt in raw_transactions:
            m = re.match(r"^(\d\d\/\d\d\/\d\d\d\d) (\d\d\/\d\d\/\d\d\d\d) USD (\w+) (\w+) (.*)"
                         + " ([\d\.\(\)\-]+) ([\d\,\.\(\)]+) ([\d\,\.\(\)]+)$", str(rt))
            if not m:
                if self.print_invalid_lines:
                    print(rt)
                continue

            activity_type = m[3]
            quantity = float(m[6])
            if activity_type == 'SELL':
                quantity *= -1

            amount = m[8].replace(",", "").replace("(", "").replace(")", "")

            trade_date = datetime.datetime.strptime(m[1], '%m/%d/%Y')
            settle_date = datetime.datetime.strptime(m[2], '%m/%d/%Y')

            transactions.append(Transaction(
                trade_date,
                settle_date,
                "USD",          # Currency is hardcoded to USD.
                Activity(activity_type),  # Activity Type
                m[4],           # Symbol (e.g. TSLA)
                Decimal(quantity),
                Decimal(m[7]),
                Decimal(amount),
            ))

        return transactions
