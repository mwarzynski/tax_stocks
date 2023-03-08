from app.exchange import Exchange, Currency
from decimal import Decimal
from datetime import datetime
from typing import Dict

class ExchangeMock(Exchange):

    __ratios: Dict[Currency, Dict[Currency, Decimal]]

    def __init__(self) -> None:
        super().__init__()
        self.__ratios = {}

    def set_ratio(self, c_from: Currency, c_to: Currency, ratio: Decimal) -> None:
        if c_from not in self.__ratios:
            self.__ratios[c_from] = {}
        self.__ratios[c_from][c_to] = ratio

    def ratio(self, day: datetime, c_from: Currency, c_to: Currency, max_days_prior_to_check: int = 5) -> Decimal:
        if c_from in self.__ratios and c_to in self.__ratios[c_from]:
            return self.__ratios[c_from][c_to]
        return Decimal(1)