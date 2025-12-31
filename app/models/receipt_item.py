from dataclasses import dataclass


@dataclass(frozen=True)
class ReceiptItem:
    article_name: str
    quantity: int
    unit_price: float

    def line_total(self) -> float:
        return self.quantity * self.unit_price
