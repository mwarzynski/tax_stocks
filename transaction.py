import decimal
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class Activity(Enum):
    BUY = "BUY"        # Buy
    SELL = "SELL"      # Sell
    DIV = "DIV"        # Dividend
    DIVNRA = "DIVNRA"  # Dividend tax
    SSP = "SSP"        # Stock Split


@dataclass
class Transaction:
    trade_date: datetime
    settle_date: datetime
    currency: str              # 'USD'
    activity: Activity
    symbol: str                # 'TSLA'
    quantity: decimal.Decimal
    price: decimal.Decimal
    amount: decimal.Decimal

