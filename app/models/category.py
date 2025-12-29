from dataclasses import dataclass

from app.models.base_model import BaseModel


@dataclass
class Category(BaseModel):
    name: str
