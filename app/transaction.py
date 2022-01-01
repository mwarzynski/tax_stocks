from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class Activity(Enum):
    BUY = "BUY"          # Buy
    SELL = "SELL"        # Sell
    DIV = "DIVIDEND"     # Dividend
    SSP = "STOCK SPLIT"  # Stock Split


@dataclass
class Transaction:
    trade_date: datetime
    settle_date: datetime
    currency: str              # 'USD'
    activity: Activity
    symbol: str                # 'TSLA'
    quantity: Decimal
    price: Decimal
    amount: Decimal
    dividend_tax_deducted: Decimal
