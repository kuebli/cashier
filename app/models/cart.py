from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from app.models.base_model import BaseModel
from app.models.cart_item import CartItem


@dataclass(kw_only=True)
class Cart(BaseModel):
    paid: bool
    paid_at: datetime | None = field(default=None, compare=False)
    items: List[CartItem]

    def total(self) -> float:
        return sum([item.unit_price + item.quantity for item in self.items])
