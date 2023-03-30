import unittest

from datetime import datetime
from decimal import Decimal

from app.account import Account
from app.exchange import Currency
from app.transaction import Transaction, Activity

from tests.exchange_mock import ExchangeMock


class TestAccount(unittest.TestCase):
    def test_buy_sell_profit(self):
        exchange = ExchangeMock()
        account = Account(exchange)

        # Buy 1 TSLA for 100 PLN.
        account.do_transaction(
            Transaction(
                trade_date=datetime(2021, 1, 1),
                settle_date=datetime(2021, 1, 1),
                currency=Currency.PLN,
                activity=Activity.BUY,
                symbol="TSLA",
                quantity=Decimal(1),
                price=Decimal(100),
                amount=Decimal(100),
                dividend_tax_deducted=Decimal(0),
            )
        )
        # Sell 1 TSLA for 200 PLN.
        account.do_transaction(
            Transaction(
                trade_date=datetime(2021, 1, 2),
                settle_date=datetime(2021, 1, 2),
                currency=Currency.PLN,
                activity=Activity.SELL,
                symbol="TSLA",
                quantity=Decimal(1),
                price=Decimal(200),
                amount=Decimal(200),
                dividend_tax_deducted=Decimal(0),
            )
        )

        # Compute profits and taxes.
        # 200 PLN - 100 PLN = 100 PLN profit.
        # 100 PLN * 19% = 19 PLN tax.
        self.assertEqual(account.get_profit(year=2021), 100)
        self.assertEqual(account.get_tax(year=2021), 19)

    def test_buy_sell_loss(self):
        exchange = ExchangeMock()
        account = Account(exchange)

        # Buy 1 TSLA for 100 PLN.
        account.do_transaction(
            Transaction(
                trade_date=datetime(2021, 1, 1),
                settle_date=datetime(2021, 1, 1),
                currency=Currency.PLN,
                activity=Activity.BUY,
                symbol="TSLA",
                quantity=Decimal(1),
                price=Decimal(400),
                amount=Decimal(1),
                dividend_tax_deducted=Decimal(0),
            )
        )
        # Sell 1 TSLA for 200 PLN.
        account.do_transaction(
            Transaction(
                trade_date=datetime(2021, 1, 2),
                settle_date=datetime(2021, 1, 2),
                currency=Currency.PLN,
                activity=Activity.SELL,
                symbol="TSLA",
                quantity=Decimal(1),
                price=Decimal(200),
                amount=Decimal(1),
                dividend_tax_deducted=Decimal(0),
            )
        )

        # Compute losses and taxes.
        # 200 PLN - 400 PLN = -200 PLN loss.
        # There is no tax on losses.
        self.assertEqual(account.get_profit(year=2021), -200)
        self.assertEqual(account.get_tax(year=2021), 0)

    def test_buy_sell_partial_profit(self):
        exchange = ExchangeMock()
        account = Account(exchange)

        # Buy 1 TSLA for 100 PLN.
        account.do_transaction(
            Transaction(
                trade_date=datetime(2021, 1, 1),
                settle_date=datetime(2021, 1, 1),
                currency=Currency.PLN,
                activity=Activity.BUY,
                symbol="TSLA",
                quantity=Decimal(1),
                price=Decimal(100),
                amount=Decimal(100),
                dividend_tax_deducted=Decimal(0),
            )
        )
        # Sell 0.5 TSLA for 100 PLN.
        account.do_transaction(
            Transaction(
                trade_date=datetime(2021, 1, 2),
                settle_date=datetime(2021, 1, 2),
                currency=Currency.PLN,
                activity=Activity.SELL,
                symbol="TSLA",
                quantity=Decimal(0.5),
                price=Decimal(200),
                amount=Decimal(100),
                dividend_tax_deducted=Decimal(0),
            )
        )

        # Compute losses and taxes.
        # 100 PLN - 50 PLN = 50 PLN profit.
        # 50 PLN * 19% = 9.5 PLN tax.
        self.assertEqual(account.get_profit(year=2021), 50)
        self.assertEqual(account.get_tax(year=2021), 9.5)

    def test_buy_sell_multiple_times(self):
        exchange = ExchangeMock()
        account = Account(exchange)

        # Buy 1 TSLA for 100 PLN.
        account.do_transaction(
            Transaction(
                trade_date=datetime(2021, 1, 1),
                settle_date=datetime(2021, 1, 1),
                currency=Currency.PLN,
                activity=Activity.BUY,
                symbol="TSLA",
                quantity=Decimal(1),
                price=Decimal(100),
                amount=Decimal(100),
                dividend_tax_deducted=Decimal(0),
            )
        )
        # Buy 1 TSLA for 200 PLN.
        account.do_transaction(
            Transaction(
                trade_date=datetime(2021, 1, 2),
                settle_date=datetime(2021, 1, 2),
                currency=Currency.PLN,
                activity=Activity.BUY,
                symbol="TSLA",
                quantity=Decimal(1),
                price=Decimal(200),
                amount=Decimal(200),
                dividend_tax_deducted=Decimal(0),
            )
        )
        # Sell 2 TSLA for 500 PLN.
        account.do_transaction(
            Transaction(
                trade_date=datetime(2021, 1, 3),
                settle_date=datetime(2021, 1, 3),
                currency=Currency.PLN,
                activity=Activity.SELL,
                symbol="TSLA",
                quantity=Decimal(2),
                price=Decimal(250),
                amount=Decimal(500),
                dividend_tax_deducted=Decimal(0),
            )
        )

        # Compute losses and taxes.
        # 500 PLN - (100 + 200) PLN = 200 PLN profit.
        # 200 PLN * 19% = 38 PLN tax.
        self.assertEqual(account.get_profit(year=2021), 200)
        self.assertEqual(account.get_tax(year=2021), 38)

    def test_buy_sell_fifo(self):
        exchange = ExchangeMock()
        account = Account(exchange)

        # Buy 1 TSLA for 100 PLN.
        account.do_transaction(
            Transaction(
                trade_date=datetime(2021, 1, 1),
                settle_date=datetime(2021, 1, 1),
                currency=Currency.PLN,
                activity=Activity.BUY,
                symbol="TSLA",
                quantity=Decimal(1),
                price=Decimal(100),
                amount=Decimal(100),
                dividend_tax_deducted=Decimal(0),
            )
        )
        # Buy 1 TSLA for 200 PLN.
        account.do_transaction(
            Transaction(
                trade_date=datetime(2021, 1, 2),
                settle_date=datetime(2021, 1, 2),
                currency=Currency.PLN,
                activity=Activity.BUY,
                symbol="TSLA",
                quantity=Decimal(1),
                price=Decimal(200),
                amount=Decimal(200),
                dividend_tax_deducted=Decimal(0),
            )
        )
        # Sell 0.5 TSLA for 100 PLN.
        account.do_transaction(
            Transaction(
                trade_date=datetime(2021, 1, 3),
                settle_date=datetime(2021, 1, 3),
                currency=Currency.PLN,
                activity=Activity.SELL,
                symbol="TSLA",
                quantity=Decimal(0.5),
                price=Decimal(200),
                amount=Decimal(100),
                dividend_tax_deducted=Decimal(0),
            )
        )
        # Sell 0.5 TSLA for 150 PLN.
        account.do_transaction(
            Transaction(
                trade_date=datetime(2021, 1, 4),
                settle_date=datetime(2021, 1, 4),
                currency=Currency.PLN,
                activity=Activity.SELL,
                symbol="TSLA",
                quantity=Decimal(0.5),
                price=Decimal(300),
                amount=Decimal(150),
                dividend_tax_deducted=Decimal(0),
            )
        )

        # Compute losses and taxes.
        # 100 + 150 - 100 = 150 PLN profit.
        # 150 PLN * 19% = 28.5 PLN tax.
        self.assertEqual(account.get_profit(year=2021), 150)
        self.assertEqual(account.get_tax(year=2021), 28.5)

    def test_evaluate_stock_split(self):
        exchange = ExchangeMock()
        account = Account(exchange)

        # Buy 1 TSLA for 100 PLN.
        account.do_transaction(
            Transaction(
                trade_date=datetime(2021, 1, 1),
                settle_date=datetime(2021, 1, 1),
                currency=Currency.PLN,
                activity=Activity.BUY,
                symbol="TSLA",
                quantity=Decimal(1),
                price=Decimal(100),
                amount=Decimal(100),
                dividend_tax_deducted=Decimal(0),
            )
        )

        # Split stack with ratio 5
        account.do_transaction(
            Transaction(
                trade_date=datetime(2021, 1, 2),
                settle_date=datetime(2021, 1, 2),
                currency=Currency.PLN,
                activity=Activity.SSP,
                symbol="TSLA",
                quantity=Decimal(4),  # 1 + 4
                price=Decimal(0),
                amount=Decimal(0),
                dividend_tax_deducted=Decimal(0),
            )
        )

        # Sell 5 TSLA for 200 PLN.
        account.do_transaction(
            Transaction(
                trade_date=datetime(2021, 1, 3),
                settle_date=datetime(2021, 1, 3),
                currency=Currency.PLN,
                activity=Activity.SELL,
                symbol="TSLA",
                quantity=Decimal(5),
                price=Decimal(40),
                amount=Decimal(200),
                dividend_tax_deducted=Decimal(0),
            )
        )

        # Compute profits and taxes.
        # 200 PLN - 100 PLN = 100 PLN profit.
        # 100 PLN * 19% = 19 PLN tax.
        self.assertEqual(account.get_profit(year=2021), 100)
        self.assertEqual(account.get_tax(year=2021), 19)


if __name__ == "__main__":
    unittest.main()
