from abc import abstractmethod
from decimal import Decimal
from datetime import datetime


class Exchange:

    @abstractmethod
    def ratio(self, day: datetime, max_days_prior_to_check: int = 5) -> Decimal:
        return Decimal(0)
