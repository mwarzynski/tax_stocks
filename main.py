import sys
from typing import List

import app


def help():
    print(
        """tax_stocks: computes the profits (and losses) for stocks transactions and dividends for particular fiscal year.
Example: python main.py 2021"""
    )


def main():
    try:
        year = int(sys.argv[1])
    except (IndexError, ValueError):
        help()
        return

    revolut = app.Revolut()

    # === Stocks ===

    transaction_providers = [
        app.Degiro(),
        revolut,
    ]

    transactions: List[app.TransactionProvider] = []
    for provider in transaction_providers:
        transactions += provider.provide_transactions()

    exchange = app.ExchangeNBP()

    account = app.Account(exchange)
    account.do_transactions(transactions)

    account.print_stocks(show_summary_per_stock=True, year=year)
    account.print_dividends(year=year)

    # # Debug current positions (validate with your portfolio):
    # account.print_current_positions()

    # Print out all taxable transactions (sells) with buy information.
    # This should contain everything you need to evaluate the tax.
    # account.print_stocks_transactions()

    # === Crypto ===

    transfer_providers = [
        revolut,
        app.Binance(),
    ]
    transfers = []
    for provider in transfer_providers:
        transfers += provider.provide_transfers()

    crypto = app.Crypto(transfers, exchange)
    crypto.print_summary(year=year)


if __name__ == "__main__":
    main()
