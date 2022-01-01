from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime


@dataclass
class Dividend:

    value: Decimal
    tax_deducted: Decimal
    date: datetime

    def tax_to_pay(self) -> Decimal:
        tax_total = self.value*Decimal(0.19)
        payable = tax_total - self.tax_deducted
        if payable <= 0:
            return Decimal(0)
        return payable

    def net(self) -> Decimal:
        tax = self.tax_deducted + self.tax_to_pay()
        return self.value - tax
