from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

from .exchange import Currency


@dataclass
class StockEquity:
    quantity: Decimal
    quantity_total: Decimal
    price: Decimal
    date: datetime
    currency: Currency


@dataclass
class RealizedChange:
    date_buy: datetime
    date_sell: datetime
    quantity: Decimal
    price_buy: Decimal
    price_sell: Decimal
    profit: Decimal
    currency: Currency
