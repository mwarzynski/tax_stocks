# tax_stocks

The application calculates profits (and losses) from stock and dividend transactions for a given tax year.

Polish translation (for SEO): aplikacja licząca podatek od akcji i dywidend.

## Why?

Most applications that provide stock trading functions for retail investors generate tax forms automatically.
At least they do if you are a citizen of one of the larger countries with a higher concentration of customers.
I am a citizen of Poland, and for me, neither Degiro nor Revolut prepares a tax form related to gains (or losses) on stocks.

Have you ever tried to manually assess taxes for stock transactions?
It is an extremely repetitive process to say the least, so I decided to automate it.

**Disclaimer: there is NO assurance that this application works correctly.**

There are certain assumptions:
 - the principles of Polish tax law are hard-coded (e.g., 19% income tax, no long-term capital gains)
 - currency exchange rates based on the National Bank of Poland
 - the only currencies supported are USD, EUR and PLN

## Supported platforms

The current implementation supports two platforms: Revolut and Degiro.
Transaction providers are implemented via an interface, so adding implementations for other platforms should be relatively simple.

The application uses the following code structure to keep the CSV files fairly organized: `data/investing/{platform}/{year}.csv`.

### Degiro

 1. Log in to the `Degiro` through Web Browser,
 2. Activity (left panel) -> Account Statement,
 3. Select "start date" and "end date" which contain all transactions,
 4. Export (CSV),
 5. Save downloaded file to `data/investing/degiro/{year}.csv`.

### Revolut

 1. Open `Revolut` application,
 2. Go to `Stocks` section,
 3. Click on `...` button next to `+ Add money`,
 4. Choose `Statements`,
 5. Change format to `Excel`,
 6. Select "starting on" and "ending on" dates to include full fiscal year (e.g. January 2021 -> December 2021),
 7. Click on "Get statement",
 8. Download the statement and convert to CSV,
 9. Save converted file to  `data/investing/revolut/{year}.csv`.

### Binance

 1. `Wallet` -> `Overview`,
 2. `Transaction History` in the left panel,
 3. Click on `Generate all statements` in the top right,
 4. Choose time range related to desired fiscal year,

## How to run

First, you need to save the transactions from the platforms you use (instructions above).

```
$ ls -al data/investing/degiro
.rw-r--r--     0 mwarzynski  2 Jan 00:00  .keep
.rw-r--r--    1k mwarzynski  2 Jan 00:00  2020.csv
.rw-r--r--    1k mwarzynski  2 Jan 00:00  2021.csv
$ ls -al data/investing/revolut
.rw-r--r--     0 mwarzynski  2 Jan 00:00  .keep
.rw-r--r--    1k mwarzynski  2 Jan 00:00  2020.csv
.rw-r--r--    1k mwarzynski  2 Jan 00:00  2021.csv
```

If you already have this data, just run the script as follows:
```
$ python main.py
tax_stocks: computes the profits (and losses) for stocks transactions and dividends for particular fiscal year.
Example: python main.py 2020

$ python main.py 2020
Year: 2020

=== Stocks

Profit = 50420.6969 PLN
Tax    = 9579.9324 PLN
Sell: 120480.12 PLN, Buy: 70059.4231 PLN

	TSLA: 	50420.6969 PLN

=== Dividends

Total      = 0.0000 PLN
Net        = 0.0000 PLN
Tax        = 0.0000 PLN
Tax (paid) = 0.0000 PLN

$ python main.py 2021
Year: 2021

=== Stocks

Profit = 100420.6969 PLN
Tax    = 19079.9324 PLN
Sell: 1000463.3938 PLN, Buy: 900042.6969 PLN

	TSLA: 	100420.6969 PLN

=== Dividends

Total      = 1718.9905 PLN
Net        = 1392.3820 PLN
Tax        = 326.6080 PLN
Tax (paid) = 258.0565 PLN
```

## Other

Helpful links:
 - https://podatki.gov.pl
 - https://kalkulatorgieldowy.pl

