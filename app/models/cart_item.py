from dataclasses import dataclass

from app.models.base_model import BaseModel


@dataclass(kw_only=True)
class CartItem(BaseModel):
    cart_id: int
    article_id: int
    quantity: int
    unit_price: float
    article_name: str
