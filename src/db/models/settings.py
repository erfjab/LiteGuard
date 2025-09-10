from copy import deepcopy
from typing import Optional, ClassVar
from sqlalchemy import Integer, Boolean, JSON
from sqlalchemy.sql import select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from ..core import Base


class Setting(Base):
    __tablename__ = "setting"
    _cache: ClassVar[Optional["Setting"]] = None

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shuffle: Mapped[bool] = mapped_column(Boolean, nullable=True)
    placeholders: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    informations: Mapped[list[str]] = mapped_column(JSON, nullable=True)

    def format(self) -> dict:
        newline = "\n"
        return {
            "id": self.id,
            "shuffle": self.shuffle,
            "placeholders": f"\n<pre>{newline.join(self.placeholders)}</pre>" if self.placeholders else "➖",
            "informations": f"\n<pre>{newline.join(self.informations)}</pre>" if self.informations else "➖",
        }

    @classmethod
    async def get(cls, db: AsyncSession, cache: bool = True) -> "Setting":
        if cls._cache is None or cache is False:
            result = await db.execute(select(cls))
            cls._cache = deepcopy(result.scalars().first())

        return cls._cache

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        shuffle: Optional[bool] = None,
        placeholders: Optional[list[str]] = None,
        informations: Optional[list[str]] = None,
    ) -> "Setting":
        result = await db.execute(select(cls))
        setting = result.scalars().first()

        if shuffle is not None:
            setting.shuffle = shuffle
        if placeholders is not None:
            setting.placeholders = placeholders
        if informations is not None:
            setting.informations = informations

        await db.flush()
        cls._cache = deepcopy(setting)
        return setting
