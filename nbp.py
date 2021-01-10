import csv
import datetime
from typing import Dict
from decimal import Decimal


class Exchange:

    _day_ratio: Dict[datetime.datetime, Decimal]

    def __init__(self, file_name: str = "kurs_usd_nbp.csv"):
        self._day_ratio = {}
        with open(file_name, "r") as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)
            for row in reader:
                date = datetime.datetime.strptime(row[0], '%Y%m%d')
                self._day_ratio[date] = Decimal(row[2].replace(",", "."))

    def ratio(self, day: datetime.datetime, n: int = 5) -> Decimal:
        day = day - datetime.timedelta(days=1)
        try:
            return self._day_ratio[day]
        except KeyError as e:
            if n <= 0:
                raise e
            return self.ratio(day, n=n-1)
