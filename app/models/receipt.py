from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from app.models.receipt_item import ReceiptItem


@dataclass(frozen=True)
class Receipt:
    paid_at: datetime = field(compare=False)
    items: List[ReceiptItem]

    def total(self) -> float:
        return sum([item.line_total() for item in self.items])
