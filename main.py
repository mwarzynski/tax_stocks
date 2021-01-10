import sys
import revolut
from typing import List
from dataclasses import dataclass
from transaction import *
from nbp import *


@dataclass
class Dividend:
    value: Decimal
    tax_deducted: Decimal
    date: datetime

    def tax_to_pay(self) -> Decimal:
        tax_total = self.value*Decimal(0.19)
        payable = tax_total - self.tax_deducted
        if payable <= 0:
            return 0
        return payable

    def net(self) -> Decimal:
        tax = self.tax_deducted + self.tax_to_pay()
        return self.value - tax


@dataclass
class PositionAction:
    quantity: Decimal
    price: Decimal
    date: datetime


@dataclass
class RealizedChange:
    date_buy: datetime
    date_sell: datetime
    quantity: Decimal
    price_buy: Decimal
    price_sell: Decimal

    profit: Decimal


class AccountPosition:

    symbol: str
    _current_positions: List[PositionAction]
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
        self._current_positions.append(PositionAction(quantity, price, date))

    def _sell_i(self, sell_quantity: Decimal, sell_price: Decimal, sell_date: datetime) -> (Decimal, Decimal):
        if len(self._current_positions) == 0:
            raise Exception(f"symbol={self.symbol}: you can't sell stock that you don't own")

        quantity_sold = min(self._current_positions[0].quantity, sell_quantity)
        buy_price = self._current_positions[0].price * self._exchange.ratio(self._current_positions[0].date)
        sell_price_ratio = sell_price * self._exchange.ratio(sell_date)
        change = (sell_price_ratio - buy_price) * quantity_sold

        self.realized_changes.append(RealizedChange(
            self._current_positions[0].date,
            sell_date,
            quantity_sold,
            self._current_positions[0].price,
            sell_price,
            change
        ))

        self._current_positions[0].quantity -= quantity_sold
        # If we sold all quantity from the earliest position, remove it.
        if round(self._current_positions[0].quantity, 15) == 0:
            self._current_positions.pop(0)

        return change, quantity_sold

    def sell(self, sell_quantity: Decimal, sell_price: Decimal, sell_date: datetime) -> Decimal:
        change = Decimal(0)
        while not round(sell_quantity, 15) == 0:
            change_i, quantity_sold_i = self._sell_i(sell_quantity, sell_price, sell_date)
            change += change_i
            sell_quantity -= quantity_sold_i
        return change

    def stock_split(self, ratio: Decimal):
        for i, _ in enumerate(self._current_positions):
            self._current_positions[i].quantity = self._current_positions[i].quantity*ratio
            self._current_positions[i].price = self._current_positions[i].price/ratio

    def dividend(self, value: Decimal, date: datetime):
        self._dividends.append(Dividend(value, 0, date))

    def dividend_tax(self, value: Decimal):
        if self._dividends[-1].tax_deducted != 0:
            raise Exception("invalid dividends values")
        self._dividends[-1].tax_deducted = value

    def dividends_received(self) -> (Decimal, Decimal, Decimal):
        total = Decimal(0)
        tax_to_pay = Decimal(0)
        net = Decimal(0)

        for d in self._dividends:
            ratio = self._exchange.ratio(d.date)
            total += d.value * ratio
            tax_to_pay += d.tax_to_pay() * ratio
            net += d.net() * ratio

        return total, tax_to_pay, net


class Account:

    _positions: Dict[str, AccountPosition]
    _realized_change: Dict[str, Decimal]
    _dividends: Dict[str, Decimal]
    _exchange: Exchange

    def __init__(self, exchange):
        self._positions = {}
        self._realized_change = {}
        self._dividends = {}
        self._exchange = exchange

    def _get_position(self, symbol: str) -> AccountPosition:
        try:
            return self._positions[symbol]
        except KeyError:
            return AccountPosition(symbol, self._exchange)

    def _save_position(self, position: AccountPosition):
        self._positions[position.symbol] = position

    def _add_change(self, symbol: str, change: decimal):
        try:
            self._realized_change[symbol] += change
        except KeyError:
            self._realized_change[symbol] = change

    def _evaluate_stock_split_ratio(self, transaction: Transaction) -> Decimal:
        if transaction.quantity <= 0:
            return Decimal(1)
        ratio = 1
        if transaction.symbol == 'AAPL' and transaction.settle_date.strftime('%Y-%m-%d') == '2020-05-12':
            ratio = 4
        if transaction.symbol == 'TSLA' and transaction.settle_date.strftime('%Y-%m-%d') == '2020-09-01':
            ratio = 5
        return Decimal(ratio)

    def do_transaction(self, transaction: Transaction):
        position = self._get_position(transaction.symbol)
        if transaction.activity == Activity.BUY:
            position.buy(transaction.quantity, transaction.price, transaction.trade_date)
        elif transaction.activity == Activity.SELL:
            change = position.sell(transaction.quantity, transaction.price, transaction.trade_date)
            self._add_change(transaction.symbol, change)
        elif transaction.activity == Activity.SSP:
            ratio = self._evaluate_stock_split_ratio(transaction)
            position.stock_split(ratio)
        elif transaction.activity == Activity.DIV:
            position.dividend(transaction.amount, transaction.trade_date)
        elif transaction.activity == Activity.DIVNRA:
            position.dividend_tax(transaction.amount)
        self._save_position(position)

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


def main():
    transactions = revolut.parse(sys.argv[1])

    exchange = Exchange()
    account = Account(exchange)

    transactions.sort(key=lambda x: x.trade_date)
    for t in transactions:
        account.do_transaction(t)

    profits = [(x[0], x[1]) for x in account.get_profit_per_symbol().items()]
    profits.sort(key=lambda x: x[1], reverse=True)
    for p in profits:
        print(f"{p[0]}: \t{round(p[1],4)} PLN")

    print(f"\nNet   =\t{round(account.get_profit()*Decimal(0.81), 4)} PLN")
    print(f"Total = {round(account.get_profit(),4)} PLN, Tax = {round(account.get_profit()*Decimal(0.19), 4)} PLN")

    # # Debug evaluations for a particular symbol:
    # symbol = "AAPL"
    # print(f"\nTransactions for '{symbol}':")
    # for c in account.position(symbol).realized_changes:
    #     print(f"{c.date_buy.date()} - {c.date_sell.date()}: {c.price_buy} USD -> {c.price_sell} USD (*{round(c.quantity, 2)})"
    #           f"\t= {round(c.profit, 2)} PLN")
    #     print(f"{c.date_buy.date()}: 1 PLN = {exchange.ratio(c.date_buy)} USD")
    #     print(f"{c.date_sell.date()}: 1 PLN = {exchange.ratio(c.date_sell)} USD\n")

    # # Debug current positions (validate with your portfolio):
    # print("\nCurrent positions:")
    # account.print_current_positions()

    dividend_total, dividend_tax, dividend_net = account.dividends()
    print(f"\nDividend: {round(dividend_total, 4)} PLN, Net: {round(dividend_net, 4)} PLN, Tax to pay: {round(dividend_tax, 4)} PLN")


if __name__ == "__main__":
    main()
