from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime

from .equity import StockEquity, RealizedChange
from .dividend import Dividend
from .exchange import Exchange, Currency
from .transaction import Transaction, Activity


class AccountPosition:

    symbol: str
    _current_positions: List[StockEquity]
    _exchange: Exchange
    realized_changes: List[RealizedChange]
    _dividends: List[Dividend]

    def __init__(self, symbol: str, exchange: Exchange):
        self.symbol = symbol
        self._current_positions = []
        self._exchange = exchange
        self.realized_changes = []
        self._dividends = []

    def buy(self, quantity: Decimal, price: Decimal, date: datetime):
        self._current_positions.append(StockEquity(quantity, quantity, price, date))

    def _sell_i(self, sell_quantity: Decimal, sell_price: Decimal, sell_date: datetime) -> RealizedChange:
        if len(self._current_positions) == 0:
            raise Exception(f"symbol={self.symbol}: you can't sell stock that you don't own")

        quantity_sold = min(self._current_positions[0].quantity, sell_quantity)
        buy_price = self._current_positions[0].price * self._exchange.ratio(self._current_positions[0].date, Currency.USD, Currency.PLN)
        sell_price_ratio = sell_price * self._exchange.ratio(sell_date, Currency.USD, Currency.PLN)
        change = (sell_price_ratio - buy_price) * quantity_sold

        rc = RealizedChange(
            self._current_positions[0].date,
            sell_date,
            quantity_sold,
            self._current_positions[0].price,
            sell_price,
            change
        )
        self.realized_changes.append(rc)

        self._current_positions[0].quantity -= quantity_sold
        # If we sold all quantity from the earliest position, remove it.
        if round(self._current_positions[0].quantity, 15) == 0:
            self._current_positions.pop(0)

        return rc

    def sell(self, sell_quantity: Decimal, sell_price: Decimal, sell_date: datetime) -> [RealizedChange]:
        realized_changes = []
        while not round(sell_quantity, 15) == 0:
            rc = self._sell_i(sell_quantity, sell_price, sell_date)
            realized_changes.append(rc)
            sell_quantity -= rc.quantity
        return realized_changes

    def stock_split(self, ratio: Decimal):
        for i, _ in enumerate(self._current_positions):
            self._current_positions[i].quantity = self._current_positions[i].quantity*ratio
            self._current_positions[i].price = self._current_positions[i].price/ratio

    def dividend(self, value: Decimal, tax_deducted: Decimal, date: datetime):
        self._dividends.append(Dividend(value, tax_deducted, date))

    def dividends_received(self, year: Optional[int]) -> (Decimal, Decimal, Decimal):
        total = Decimal(0)
        tax_to_pay = Decimal(0)
        net = Decimal(0)

        for d in self._dividends:
            if year and d.date.year != year:
                continue
            ratio = self._exchange.ratio(d.date, Currency.USD, Currency.PLN)
            total += d.value * ratio
            tax_to_pay += d.tax_to_pay() * ratio
            net += d.net() * ratio

        return total, tax_to_pay, net


class Account:

    _positions: Dict[str, AccountPosition]
    _realized_change: Dict[str, List[RealizedChange]]
    _dividends: Dict[str, Decimal]
    _exchange: Exchange

    _transactions_per_month: Dict[str, int]

    def __init__(self, exchange):
        self._positions = {}
        self._realized_change = {}
        self._dividends = {}
        self._exchange = exchange
        self._cost = Decimal(0)
        self._transactions_per_month = {}

    def _get_position(self, symbol: str) -> AccountPosition:
        try:
            return self._positions[symbol]
        except KeyError:
            return AccountPosition(symbol, self._exchange)

    def _save_position(self, position: AccountPosition):
        self._positions[position.symbol] = position

    def _add_change(self, symbol: str, changes: List[RealizedChange]):
        for change in changes:
            try:
                self._realized_change[symbol].append(change)
            except KeyError:
                self._realized_change[symbol] = [change]

    def _evaluate_stock_split_ratio(self, transaction: Transaction) -> Decimal:
        ratio = 1
        if transaction.symbol == 'AAPL' and transaction.settle_date.strftime('%Y-%m-%d') == '2020-08-31':
            ratio = 4
        if transaction.symbol == 'TSLA' and transaction.settle_date.strftime('%Y-%m-%d') == '2020-08-31':
            ratio = 5
        return Decimal(ratio)

    def do_transaction(self, transaction: Transaction):
        position = self._get_position(transaction.symbol)
        if transaction.activity == Activity.BUY:
            position.buy(transaction.quantity, transaction.price, transaction.settle_date)
        elif transaction.activity == Activity.SELL:
            realized_changes = position.sell(transaction.quantity, transaction.price, transaction.settle_date)
            self._add_change(transaction.symbol, realized_changes)
        elif transaction.activity == Activity.SSP:
            ratio = self._evaluate_stock_split_ratio(transaction)
            position.stock_split(ratio)
        elif transaction.activity == Activity.DIV:
            position.dividend(transaction.amount, transaction.dividend_tax_deducted, transaction.settle_date)
        self._save_position(position)

    def do_transactions(self, transactions: List[Transaction]):
        transactions.sort(key=lambda x: x.trade_date)
        for transaction in transactions:
            self.do_transaction(transaction)

    def get_profit_per_symbol(self, year: Optional[int] = None) -> Dict[str, Decimal]:
        profits: Dict[str, Decimal] = {}
        for symbol, changes in self._realized_change.items():
            for change in changes:
                if year and change.date_sell.year != year:
                    continue
                try:
                    profits[symbol] += change.profit
                except KeyError:
                    profits[symbol] = change.profit
        return profits

    def get_profit(self, year: Optional[int] = None) -> Decimal:
        profit = Decimal(0)
        for _, rcs in self._realized_change.items():
            for rc in rcs:
                if year and rc.date_sell.year != year:
                    continue
                profit += rc.profit
        return profit

    def position(self, symbol: str) -> AccountPosition:
        return self._positions[symbol]

    def dividends(self, year: Optional[int]) -> (Decimal, Decimal, Decimal):
        total = Decimal(0)
        tax_to_pay = Decimal(0)
        net = Decimal(0)
        for _, position in self._positions.items():
            a,b,c = position.dividends_received(year)
            total += a
            tax_to_pay += b
            net += c
        return total, tax_to_pay, net

    def print_current_positions(self):
        for _, position in self._positions.items():
            if len(position._current_positions) == 0:
                continue
            quantity = sum([p.quantity for p in position._current_positions])
            print(f"{position.symbol}: {round(quantity, 2)}")

    def print_stocks(self, show_summary_per_stock: bool = False, year: Optional[int] = None):
        if year:
            print(f"Year: {year}\n")
        print(f"STOCKS: Total  = {round((self.get_profit(year)), 4)} PLN")
        print(f"STOCKS: Tax    = {round((self.get_profit(year))*Decimal(0.19), 4)} PLN")
        cost, profit = self.get_profits(year)
        print(f"STOCKS: Profit: {round(profit, 2)} PLN, Cost: {round(cost, 2)} PLN")
        print("\nSTOCKS summary:")

        if not show_summary_per_stock:
            return

        profits = [(x[0], x[1]) for x in self.get_profit_per_symbol(year).items()]
        profits.sort(key=lambda x: x[1], reverse=True)
        for p in profits:
            print(f"\t{p[0]}: \t{round(p[1],4)} PLN")

    def print_dividends(self, year: Optional[int] = None):
        dividend_total, dividend_tax, dividend_net = self.dividends(year)
        print(f"\nDIVIDENDS: Total      = {round(dividend_total, 4)} PLN")
        print(f"DIVIDENDS: Net        = {round(dividend_net, 4)} PLN")
        print(f"DIVIDENDS: Tax        = {round(float(dividend_total)*.19, 4)} PLN")
        print(f"DIVIDENDS: Tax (paid) = {round(float(dividend_total)*.19 - float(dividend_tax), 4)} PLN")

    def get_profits(self, year: Optional[int] = None):
        a, b = Decimal(0), Decimal(0)
        for symbol, position in self._positions.items():
            for c in position.realized_changes:
                if year and c.date_sell.year != year:
                    continue
                a += c.price_buy * c.quantity * self._exchange.ratio(c.date_buy, Currency.USD, Currency.PLN)
                b += c.price_sell * c.quantity * self._exchange.ratio(c.date_sell, Currency.USD, Currency.PLN)
        return a, b

    def print_stocks_transactions(self, symbol: str = "", year: Optional[int] = None):
        symbols = []
        if symbol != "":
            symbols = [symbol]
        else:
            symbols = [s for s, _ in self._positions.items()]
        print("\nTransactions:")
        for symbol in symbols:
            for c in self.position(symbol).realized_changes:
                if year and c.date_sell.year != year:
                    continue
                print(f"{symbol}: {c.date_buy.date()} - {c.date_sell.date()}: {c.price_buy} USD -> {c.price_sell} USD (*{round(c.quantity, 8)})"
                      f" = {round(c.profit, 2)} PLN")
                print(f"{c.date_buy.date()}: 1 PLN = {self._exchange.ratio(c.date_buy, Currency.USD, Currency.PLN)} USD")
                print(f"{c.date_sell.date()}: 1 PLN = {self._exchange.ratio(c.date_sell, Currency.USD, Currency.PLN)} USD")
