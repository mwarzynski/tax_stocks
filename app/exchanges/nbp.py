import csv
import datetime
from typing import Dict
from decimal import Decimal


class NBP:

    """
    NBP Exchange stands for "National Bank of Poland" exchange.
    It provides the 'standard' exchange rates for currencies (applicable for Polish citizens).
    """

    _day_ratio: Dict[datetime.datetime, Decimal]

    def __init__(self, file_name: str = "data/nbp/2020.csv"):
        self._day_ratio = {}
        with open(file_name, "r") as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)  # skip header row (which contains description of columns)
            for row in reader:
                date = datetime.datetime.strptime(row[0], '%Y%m%d')
                self._day_ratio[date] = Decimal(row[2])

    def ratio_pln_usd(self, day: datetime.datetime, max_days_prior_to_check: int = 5) -> Decimal:
        day = day - datetime.timedelta(days=1)
        try:
            return self._day_ratio[day]
        except KeyError as e:
            if max_days_prior_to_check <= 0:
                raise e
            return self.ratio_pln_usd(day, max_days_prior_to_check=max_days_prior_to_check - 1)
