from dataclasses import dataclass

from app.models.base_model import BaseModel


@dataclass
class Article(BaseModel):
    name: str
    price: float
    category_id: int
