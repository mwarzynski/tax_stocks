import csv
import re
from typing import Optional
from typing import List
from typing import Tuple
from datetime import datetime
from decimal import Decimal
from os import listdir
from os.path import isfile, join

from app.transaction import Transaction, Activity
from app.transaction_provider import TransactionProvider
from app.exchange import Currency


class DegiroRowIgnorable(BaseException):
    pass


class Degiro(TransactionProvider):
    folder: str

    _product_to_symbol_map = {
        "TESLA": "TSLA",
        "INVITAE CORPORATION": "NVTA",
        "PALANTIR": "PLTR",
        "COINBASE": "COIN",
        "TATTOOED CHEF": "TTCF",
        "GAMESTOP": "GME",  # xD
        "SQUARE": "SQ",
        "NORDSTROM": "JWN",
        "ENPHASE ENERGY": "ENPH",
        "DROPBOX": "DBX",
        "WALGREENS BOOTS ALLIAN": "WBA",
        "NIO INC": "NIO",
        "APPLE INC": "AAPL",
        "LEMONADE INC": "LMND",
        "META PLATFORMS INC": "META",
        "SHIFT TECHNOLOGIES INC": "SFT",
        "ETSY": "ETSY",
        "PFIZER": "PFE",
        "NOKIA": "NOK",
        "AMC": "AMC",
        "MICROSOFT CORPORATION": "MSFT",
        "PELOTON": "PTON",
        "REDFIN": "RDFN",
        "CORSAIR GAMING": "CRSR",
        "TMC THE METALS CO": "TMC",
        "SUMO LOGIC": "SUMO",
        "ROCKET COMPANIES": "RKT",
        "FASTLY": "FSLY",
        "NVIDIA CORPORATION": "NVDA",
        "CD PROJEKT RED": "CDP",
        "ALPHABET INC. - CLASS A": "GOOGL",
        "INTEL CORPORATION - CO": "INTC",
        "AMBRA SA": "AMB",
        "HONEST CO INC/THE": "HNST",
    }

    def __init__(self, folder: str = "data/investing/degiro", print_invalid_lines: bool = False):
        self.folder = folder
        self.print_invalid_lines = print_invalid_lines

    def _product_to_symbol(self, product: str) -> str:
        for p, symbol in self._product_to_symbol_map.items():
            if p in product:
                return symbol
        raise Exception(f"unknown product {product}")

    def provide_transactions(self) -> List[Transaction]:
        files = [f for f in listdir(self.folder) if isfile(join(self.folder, f))]
        transactions = []
        for file in files:
            transactions += self._provide_for_file(join(self.folder, file))
        return transactions

    def _description_to_action(self, description: str) -> Tuple[Activity, Decimal, Decimal, Currency]:
        m = re.search("(Sprzedaż|Kupno) ([\d ]+) (.*)@([0-9,\\xa0]+) ([A-Z]+)", description)
        if not m or len(m.groups()) != 5:
            raise DegiroRowIgnorable()
        groups = m.groups()

        activity = Activity.BUY
        if groups[0] == "Sprzedaż":
            activity = Activity.SELL
        quantity = Decimal(groups[1].replace("\xa0", ""))
        price = Decimal(groups[3].replace(",", ".").replace("\xa0", ""))
        currency = Currency(groups[4])

        return activity, quantity, price, currency

    _dividend: Optional[Transaction]

    def _parse_dates(self, row: List[str]) -> Tuple[datetime, datetime]:
        settle_date = datetime.strptime(row[0], "%d-%m-%Y")
        trade_date = datetime.strptime(row[2], "%d-%m-%Y")
        trade_date_time_hour = int(row[1].split(":")[0])
        trade_date_time_minutes = int(row[1].split(":")[1])
        trade_date = trade_date.replace(hour=trade_date_time_hour, minute=trade_date_time_minutes)
        return trade_date, settle_date

    def _parse_dividend(self, row: List[str]) -> Optional[Transaction]:
        if "Dywidend" not in row[5]:
            return None

        if row[5] == "Dywidenda":
            settle_date, trade_date = self._parse_dates(row)
            self._dividend = Transaction(
                trade_date=trade_date,  # 20/04/1969
                settle_date=settle_date,  # 20/04/1969
                currency=Currency(row[7]),  # USD
                activity=Activity.DIV,  # BUY,SELL
                symbol=self._product_to_symbol(row[3]),  # AAPL
                quantity=Decimal(0),  # 100
                price=Decimal(0),  # 420.69
                amount=Decimal(row[8].replace(",", ".")),  # 42069
                dividend_tax_deducted=Decimal(0),
            )
            return None

        if row[5] == "Podatek Dywidendowy":
            transaction = self._dividend
            transaction.dividend_tax_deducted = Decimal(row[8].replace(",", ".")) * -1  # type: ignore[union-attr]
            return transaction

        return None

    def _parse_fundshare_cash_fund(self, row: List[str]) -> Optional[Transaction]:
        if "FUNDSHARE UCITS EUR CASH FUND" not in row[3]:
            return None
        if "Konwersja funduszu gotówkowego: " not in row[5]:
            return None
        action_description = row[5].replace("Konwersja funduszu gotówkowego: ", "")

        m = re.search("(Sprzedaż|Zakup) (.*) przy (.*) EUR", action_description)
        if not m or len(m.groups()) != 3:
            return None

        groups = m.groups()
        v1 = Decimal(groups[1].replace("\xa0", "").replace(",", "."))
        v2 = Decimal(groups[2].replace("\xa0", "").replace(",", "."))
        activity = Activity.SELL
        if groups[0] == "Zakup":
            activity = Activity.BUY

        trade_date, settle_date = self._parse_dates(row)

        transaction = Transaction(
            trade_date=trade_date,  # 20/04/1969
            settle_date=settle_date,  # 20/04/1969
            currency=Currency.EUR,  # EUR
            activity=activity,  # BUY,SELL
            symbol="#EUR",
            quantity=v1,  # 100
            price=v2,  # 420.69
            amount=v1 * v2,  # 42069
            dividend_tax_deducted=Decimal(0),
        )

        return transaction

    def _provide_for_file(self, file_name: str) -> List[Transaction]:
        transactions = []
        with open(file_name, "r") as f:
            reader = csv.reader(f, delimiter=",")
            try:
                next(reader)  # skip header row (which contains description of columns)
            except StopIteration:
                return []
            for row in reader:
                # Data,Czas,Data,Produkt,ISIN,Opis,Kurs,Zmiana,,Saldo,,Identyfikator zlecenia
                transaction = self._parse_dividend(row)
                if transaction:
                    transactions.append(transaction)
                    continue

                transaction = self._parse_fundshare_cash_fund(row)
                if transaction:
                    transactions.append(transaction)
                    continue

                try:
                    activity, quantity, price, currency = self._description_to_action(row[5])
                    symbol = self._product_to_symbol(row[3])
                except DegiroRowIgnorable:
                    continue
                except KeyError:
                    print("Missing stock name translation to symbol. See app/providers/degiro.py file.", row[3])
                    continue
                except IndexError:
                    print("ERR_INDEX", row)
                    continue
                except Exception as e:
                    print("EXCEPTION", row, e)
                    raise e

                trade_date, settle_date = self._parse_dates(row)

                transaction = Transaction(
                    trade_date=trade_date,  # 20/04/1969
                    settle_date=settle_date,  # 20/04/1969
                    currency=currency,  # USD
                    activity=activity,  # BUY,SELL
                    symbol=symbol,  # AAPL
                    quantity=quantity,  # 100
                    price=price,  # 420.69
                    amount=quantity * price,  # 42069
                    dividend_tax_deducted=Decimal(0),
                )

                transactions.append(transaction)

        return transactions
