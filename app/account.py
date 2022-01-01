from typing import Dict, List
from decimal import Decimal
from datetime import datetime

from .equity import StockEquity, RealizedChange
from .dividend import Dividend
from .exchange import Exchange, Currency
from .transaction import Transaction, Activity


# Revolut Premium provides 8 transactions per month for free.
# Every next one costs 4 PLN.
FREE_TRADES_PER_MONTH = 8


class AccountPosition:

    symbol: str
    _current_positions: List[StockEquity]
    _exchange: Exchange
    realized_changes: List[RealizedChange]
    _dividends: List[Dividend]
    _cost: Decimal

    def __init__(self, symbol: str, exchange: Exchange):
        self.symbol = symbol
        self._current_positions = []
        self._exchange = exchange
        self.realized_changes = []
        self._dividends = []
        self._cost = Decimal(0)

    def _add_cost(self, fee: Decimal):
        self._cost += fee

    def buy(self, quantity: Decimal, price: Decimal, date: datetime, fee: Decimal = Decimal(0)):
        self._current_positions.append(StockEquity(quantity, quantity, price, date, fee))

    def _sell_i(self, sell_quantity: Decimal, sell_price: Decimal, sell_date: datetime) -> (Decimal, Decimal):
        if len(self._current_positions) == 0:
            raise Exception(f"symbol={self.symbol}: you can't sell stock that you don't own")

        quantity_sold = min(self._current_positions[0].quantity, sell_quantity)
        buy_price = self._current_positions[0].price * self._exchange.ratio(self._current_positions[0].date, Currency.USD, Currency.PLN)
        sell_price_ratio = sell_price * self._exchange.ratio(sell_date, Currency.USD, Currency.PLN)
        change = (sell_price_ratio - buy_price) * quantity_sold

        self.realized_changes.append(RealizedChange(
            self._current_positions[0].date,
            sell_date,
            quantity_sold,
            self._current_positions[0].price,
            sell_price,
            change
        ))

        fee_buy = (quantity_sold / self._current_positions[0].quantity_total) * self._current_positions[0].fee_buy
        self._add_cost(fee_buy)

        self._current_positions[0].quantity -= quantity_sold
        # If we sold all quantity from the earliest position, remove it.
        if round(self._current_positions[0].quantity, 15) == 0:
            self._current_positions.pop(0)

        return change, quantity_sold

    def sell(self, sell_quantity: Decimal, sell_price: Decimal, sell_date: datetime, fee: Decimal = Decimal(0)) -> Decimal:
        change = Decimal(0)
        while not round(sell_quantity, 15) == 0:
            change_i, quantity_sold_i = self._sell_i(sell_quantity, sell_price, sell_date)
            change += change_i
            sell_quantity -= quantity_sold_i
        self._add_cost(fee)
        return change

    def stock_split(self, ratio: Decimal):
        for i, _ in enumerate(self._current_positions):
            self._current_positions[i].quantity = self._current_positions[i].quantity*ratio
            self._current_positions[i].price = self._current_positions[i].price/ratio

    def dividend(self, value: Decimal, tax_deducted: Decimal, date: datetime):
        self._dividends.append(Dividend(value, tax_deducted, date))

    def dividends_received(self) -> (Decimal, Decimal, Decimal):
        total = Decimal(0)
        tax_to_pay = Decimal(0)
        net = Decimal(0)

        for d in self._dividends:
            ratio = self._exchange.ratio(d.date, Currency.USD, Currency.PLN)
            total += d.value * ratio
            tax_to_pay += d.tax_to_pay() * ratio
            net += d.net() * ratio

        return total, tax_to_pay, net

    def cost(self) -> Decimal:
        return self._cost


class Account:

    _positions: Dict[str, AccountPosition]
    _realized_change: Dict[str, Decimal]
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

    def _add_change(self, symbol: str, change: Decimal):
        try:
            self._realized_change[symbol] += change
        except KeyError:
            self._realized_change[symbol] = change

    def _evaluate_stock_split_ratio(self, transaction: Transaction) -> Decimal:
        ratio = 1
        if transaction.symbol == 'AAPL' and transaction.settle_date.strftime('%Y-%m-%d') == '2020-08-31':
            ratio = 4
        if transaction.symbol == 'TSLA' and transaction.settle_date.strftime('%Y-%m-%d') == '2020-08-31':
            ratio = 5
        return Decimal(ratio)

    def _evaluate_cost(self, date: datetime) -> Decimal:
        month = date.strftime("%m%y")
        try:
            number_of_transactions = self._transactions_per_month[month]
        except KeyError:
            number_of_transactions = 0
        number_of_transactions += 1
        self._transactions_per_month[month] = number_of_transactions

        fee = Decimal(0)
        if number_of_transactions > FREE_TRADES_PER_MONTH:
            fee = Decimal(4)
        return fee

    def do_transaction(self, transaction: Transaction):
        position = self._get_position(transaction.symbol)
        if transaction.activity == Activity.BUY:
            position.buy(transaction.quantity, transaction.price, transaction.settle_date, fee=self._evaluate_cost(transaction.settle_date))
        elif transaction.activity == Activity.SELL:
            change = position.sell(transaction.quantity, transaction.price, transaction.settle_date, fee=self._evaluate_cost(transaction.settle_date))
            self._add_change(transaction.symbol, change)
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

    def get_profit_per_symbol(self) -> Dict[str, Decimal]:
        return self._realized_change

    def get_profit(self) -> Decimal:
        profit = Decimal(0)
        for _, p in self._realized_change.items():
            profit += p
        return profit

    def position(self, symbol: str) -> AccountPosition:
        return self._positions[symbol]

    def dividends(self) -> (Decimal, Decimal, Decimal):
        total = Decimal(0)
        tax_to_pay = Decimal(0)
        net = Decimal(0)
        for _, position in self._positions.items():
            a,b,c = position.dividends_received()
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

    def cost(self):
        total_cost = Decimal(0)
        for _, position in self._positions.items():
            total_cost += position.cost()
        return total_cost

    def print_stocks(self, show_summary_per_stock: bool = False):
        print(f"STOCKS: Total  = {round(self.get_profit(),4)} PLN")
        print(f"STOCKS: Net    = {round((self.get_profit()-self.cost()), 4)} PLN")
        print(f"STOCKS: Tax    = {round((self.get_profit()-self.cost())*Decimal(0.19), 4)} PLN")
        print(f"STOCKS: Commission  = {round(self.cost(), 4)} PLN [4 PLN]")
        cost, profit = self.get_profits()
        print(f"STOCKS: Profit: {round(profit, 2)} PLN, Cost: {round(cost, 2)} PLN")
        print("\nSTOCKS summary (gain/loss):")

        if not show_summary_per_stock:
            return

        profits = [(x[0], x[1]) for x in self.get_profit_per_symbol().items()]
        profits.sort(key=lambda x: x[1], reverse=True)
        for p in profits:
            print(f"\t{p[0]}: \t{round(p[1],4)} PLN")

    def print_dividends(self):
        dividend_total, dividend_tax, dividend_net = self.dividends()
        print(f"\nDIVIDENDS: Total      = {round(dividend_total, 4)} PLN")
        print(f"DIVIDENDS: Net        = {round(dividend_net, 4)} PLN")
        print(f"DIVIDENDS: Tax        = {round(float(dividend_total)*.19, 4)} PLN")
        print(f"DIVIDENDS: Tax (paid) = {round(float(dividend_total)*.19 - float(dividend_tax), 4)} PLN")
        print("")

    def get_profits(self):
        a, b = Decimal(0), Decimal(0)
        for symbol, position in self._positions.items():
            for c in position.realized_changes:
                a += c.price_buy * c.quantity * self._exchange.ratio(c.date_buy, Currency.USD, Currency.PLN)
                b += c.price_sell * c.quantity * self._exchange.ratio(c.date_sell, Currency.USD, Currency.PLN)
        return a, b

    def print_stocks_transactions(self, symbol: str = ""):
        symbols = []
        if symbol != "":
            symbols = [symbol]
        else:
            symbols = [s for s, _ in self._positions.items()]
        print("\nTransactions:")
        for symbol in symbols:
            for c in self.position(symbol).realized_changes:
                print(f"{symbol}: {c.date_buy.date()} - {c.date_sell.date()}: {c.price_buy} USD -> {c.price_sell} USD (*{round(c.quantity, 8)})"
                      f" = {round(c.profit, 2)} PLN")
                print(f"{c.date_buy.date()}: 1 PLN = {self._exchange.ratio(c.date_buy, Currency.USD, Currency.PLN)} USD")
                print(f"{c.date_sell.date()}: 1 PLN = {self._exchange.ratio(c.date_sell, Currency.USD, Currency.PLN)} USD")
