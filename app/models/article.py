from dataclasses import dataclass

from app.models.category import Category


@dataclass
class Article:
    id: int
    name: str
    price: float
    category_id: int

    def __init__(self, id: int, name: str, price: float, category_id: int) -> None:
        self.id = id
        self.name = name
        self.price = price
        self.category_id = category_id
