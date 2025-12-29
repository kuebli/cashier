from dataclasses import dataclass, field
from datetime import datetime


@dataclass(kw_only=True)
class BaseModel:
    id: int
    created_at: datetime | None = field(default=None, compare=False)
    updated_at: datetime | None = field(default=None, compare=False)
