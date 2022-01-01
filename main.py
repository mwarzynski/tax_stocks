import sys

import app


def main():
    revolut = app.Revolut(sys.argv[1])

    transactions = revolut.provide()

    exchange = app.ExchangeNBP()

    account = app.Account(exchange)

    transactions.sort(key=lambda x: x.trade_date)
    for t in transactions:
        account.do_transaction(t)

    account.print_stocks(show_summary_per_stock=True)
    account.print_dividends()

    # # Debug current positions (validate with your portfolio):
    # account.print_current_positions()

    # Print out all taxable transactions (sells) with buy information.
    # This should contain everything you need to evaluate the tax.
    account.print_stocks_transactions()


if __name__ == "__main__":
    main()
