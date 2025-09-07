from copy import deepcopy
from typing import Optional, ClassVar
from sqlalchemy import Integer
from sqlalchemy.sql import select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from ..core import Base


class Setting(Base):
    __tablename__ = "setting"
    _cache: ClassVar[Optional["Setting"]] = None

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    @classmethod
    async def get(cls, db: AsyncSession, cache: bool = True) -> "Setting":
        if cls._cache is None or cache is False:
            result = await db.execute(select(cls))
            cls._cache = deepcopy(result.scalars().first())

        return cls._cache
