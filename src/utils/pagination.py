from typing import List, Any
from dataclasses import dataclass


@dataclass
class Pagination:
    items: List[Any]
    total: int
    current: int
    back: int | None
    next: int | None
