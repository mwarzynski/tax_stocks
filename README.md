# Revolut Stock

Script allows to compute realized gains based on the Revolut statements data.

NOTE1: it uses Polish tax law and PLN as a currency.
NOTE2: it assumes all transactions were made in 2020.

## How to run

First of all, you need to create a file which contains the transactions data.
The easiest way would be to download Statements from Revolut and place all
of the activity records to a CSV.

Example:
```
05/06/2020 05/08/2020 USD BUY TSLA - TESLA INC COM - TRD TSLA B 100 at 769.49 Principal. 100 769.49 (76949)
08/28/2020 09/01/2020 USD SSP TSLA - TESLA INC COM - CA-SSP. Surrender old shs. -0.1 2292.10 0.00
08/28/2020 09/01/2020 USD SSP TSLA - TESLA INC COM - CA-SSP. Add New shs.(TSLA:1->5) 0.5 458.42 0.00
12/18/2020 12/18/2020 USD SELL TSLA - TESLA INC COM - TRD TSLA S 500 at 690.64 Principal. -500 690.64 345320
```

(Let's say name of the file is `data.csv`.)

Having the transactions in the expected format, it's sufficient to run the script:
```
$ python main.py data.csv
TSLA: 	929299.0557 PLN

Netto =	752732.2351 PLN
Total = 929299.0557 PLN, Tax = 176566.8206 PLN
```
