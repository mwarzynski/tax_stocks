# Tax Stocks

Script allows to compute realized gains based on the Revolut statements data.

NOTE1: it uses Polish tax law and PLN as a currency.

## How to run

You need to create a file which contains the transactions data.
The easiest way would be to download Statements from Revolut and place all of the activity records to a CSV.

Example:
```
06/05/2020 14:16:38,TSLA,BUY,1,769.49,769.49,USD,0.237530678
18/05/2020 18:39:48,TSLA,SELL,1,807.01,807.01,USD,0.239085135
```

(Let's say name of the file is `data/investing/revolut/2020.csv`.)

Having the transactions in the expected format, it's sufficient to run the script:
```
$ python main.py
tax_stocks: allows to compute realized gains based on the Revolut statements data.
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
```

## Other

Helpful links:
 - https://podatki.gov.pl
 - https://kalkulatorgieldowy.pl

