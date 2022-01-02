import sys

import app


def help():
    print("""tax_stocks: computes the profits (and losses) for stocks transactions and dividends for particular fiscal year.
Example: python main.py 2021""")


def main():
    try:
        year = int(sys.argv[1])
    except (IndexError, ValueError):
        help()
        return

    providers = [
        app.Degiro(),
        app.Revolut(),
    ]

    transactions = []
    for provider in providers:
        transactions += provider.provide()

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


if __name__ == "__main__":
    main()
