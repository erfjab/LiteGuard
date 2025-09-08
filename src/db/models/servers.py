import json
from datetime import datetime
from typing import Optional, List, Dict

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    Boolean,
    JSON,
    select,
    and_,
    func,
)
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.hybrid import hybrid_property

from src.utils.times import time_diff
from src.utils.pagination import Pagination
from ..core import Base


class ServerAccess(Base):
    __tablename__ = "servers_access"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    access: Mapped[dict] = mapped_column(JSON)
    server_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("servers.id"), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, onupdate=datetime.now, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    remark: Mapped[str] = mapped_column(String(128), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    removed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    config: Mapped[Dict] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now())

    server_access: Mapped[Optional["ServerAccess"]] = relationship(
        "ServerAccess", uselist=False, lazy="joined", cascade="all, delete-orphan"
    )

    @property
    def cookies(self) -> Optional[dict]:
        if not self.server_access:
            return None
        value = self.server_access.access
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return parsed if isinstance(parsed, dict) else None
            except Exception:
                return None
        return None

    @property
    def host(self) -> Optional[str]:
        return self.config.get("host") if self.config else None

    @hybrid_property
    def availabled(self) -> bool:
        return self.enabled and not self.removed

    @availabled.expression
    def availabled(cls) -> bool:
        return and_(cls.enabled == True, cls.removed == False)  # noqa

    @property
    def emoji(self) -> str:
        return "🟢" if self.availabled else "🔴"

    @property
    def kb_remark(self) -> str:
        return f"{self.emoji} {self.remark} [{self.id}]"

    @property
    def access(self) -> Optional[str]:
        return self.server_access.access if self.server_access else None

    def format(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "enabled": self.enabled,
            "availabled": self.availabled,
            "remark": self.remark,
            "created_at": time_diff(self.created_at),
            "config": "\n".join(f"{k}:{v}" for k, v in self.config.items()),
        }

    @classmethod
    async def get_by_id(cls, db: AsyncSession, key: int) -> Optional["Server"]:
        result = await db.execute(
            select(cls).where(cls.id == key).where(cls.removed == False)  # noqa
        )
        return result.scalars().first()

    @classmethod
    async def get_by_remark(cls, db: AsyncSession, remark: str) -> Optional["Server"]:
        result = await db.execute(
            select(cls).where(cls.remark == remark).where(cls.removed == False)  # noqa
        )
        return result.scalars().first()

    @classmethod
    async def get_paginated(
        cls, db: AsyncSession, page: int, limit: int = 20
    ) -> Pagination:
        total_result = await db.execute(
            select(func.count()).where(cls.removed == False).select_from(cls)  # noqa
        )
        total_items = total_result.scalar() or 0
        total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0
        if total_pages == 0:
            return Pagination(items=[], total=0, current=1, back=None, next=None)
        current = max(1, min(page, total_pages))
        query = (
            select(cls)
            .where(cls.removed == False)  # noqa
            .order_by(cls.created_at.desc())
            .offset((current - 1) * limit)
            .limit(limit)
        )
        result = await db.execute(query)
        items = result.scalars().all()
        back = current - 1 if current > 1 else None
        next = current + 1 if current < total_pages else None
        return Pagination(
            items=items, total=total_pages, current=current, back=back, next=next
        )

    @classmethod
    async def get_all(
        cls,
        db: AsyncSession,
        *,
        page: Optional[int] = None,
        availabled: Optional[bool] = None,
        removed: bool = False,
    ) -> List["Server"]:
        query = (
            select(cls).where(cls.removed == removed).order_by(cls.created_at.desc())
        )

        if availabled is not None:
            query = query.filter(cls.availabled == availabled)

        if page is not None:
            query = query.offset((page - 1) * 20).limit(20)

        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        *,
        remark: str,
        config: Dict,
    ) -> "Server":
        item = cls(
            remark=remark,
            config=config,
        )
        db.add(item)
        await db.flush()
        return item

    @classmethod
    async def upsert_access(
        cls, db: AsyncSession, server_id: int, access: dict
    ) -> "ServerAccess":
        result = await db.execute(
            select(ServerAccess).where(ServerAccess.server_id == server_id)
        )
        server_access = result.scalars().first()

        if server_access:
            server_access.access = access
        else:
            server_access = ServerAccess(server_id=server_id, access=access)
            db.add(server_access)

        await db.flush()
        return server_access

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        *,
        server: "Server",
        remark: Optional[str] = None,
        enabled: Optional[bool] = None,
        config: Optional[Dict] = None,
    ) -> Optional["Server"]:
        if remark is not None:
            server.remark = remark
        if enabled is not None:
            server.enabled = enabled
        if config is not None:
            server.config = config

        await db.flush()
        return server

    @classmethod
    async def remove(cls, db: AsyncSession, *, server: "Server") -> None:
        server.removed = True
        await db.flush()
