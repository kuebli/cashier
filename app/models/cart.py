from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from app.models.article import Article
from app.models.base_model import BaseModel


@dataclass(kw_only=True)
class Cart(BaseModel):
    total: float
    paid: bool
    paid_at: datetime | None = field(default=None, compare=False)
    articles: List[Article]
