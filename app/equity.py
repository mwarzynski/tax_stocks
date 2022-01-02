from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime


@dataclass
class StockEquity:
    quantity: Decimal
    quantity_total: Decimal
    price: Decimal
    date: datetime


@dataclass
class RealizedChange:
    date_buy: datetime
    date_sell: datetime
    quantity: Decimal
    price_buy: Decimal
    price_sell: Decimal
    profit: Decimal
