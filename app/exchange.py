from abc import abstractmethod
from decimal import Decimal
from datetime import datetime
from enum import Enum


class Currency(Enum):
    PLN = 1
    EUR = 2
    USD = 3


class Exchange:

    @abstractmethod
    def ratio(self, day: datetime, currency_from: Currency, currency_to: Currency, max_days_prior_to_check: int = 5) -> Decimal:
        return Decimal(0)
