# Tax Stocks

Script allows to compute realized gains based on the Revolut statements data.

NOTE1: it uses Polish tax law and PLN as a currency.

NOTE2: it assumes all transactions were made in 2020.

## How to run

You need to create a file which contains the transactions data.
The easiest way would be to download Statements from Revolut and place all of the activity records to a CSV.

Example:
```
06/05/2020 14:16:38,TSLA,BUY,1,769.49,769.49,USD,0.237530678
18/05/2020 18:39:48,TSLA,SELL,1,807.01,807.01,USD,0.239085135
```

(Let's say name of the file is `data/investing/2020_revolut.csv`.)

Having the transactions in the expected format, it's sufficient to run the script:
```
$ python main.py data/investing/2020_revolut.csv
TSLA: 	929299.0557 PLN

Netto =	752732.2351 PLN
Total = 929299.0557 PLN, Tax = 176566.8206 PLN
```

## Other

Helpful links:
 - https://podatki.gov.pl
 - https://kalkulatorgieldowy.pl

