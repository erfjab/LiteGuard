from datetime import datetime, timedelta
from typing import Optional, Dict, TYPE_CHECKING, List
from sqlalchemy import (
    String,
    DateTime,
    Integer,
    BigInteger,
    Boolean,
    select,
    ForeignKey,
    func,
)
from sqlalchemy.orm import mapped_column, Mapped, relationship, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.hybrid import hybrid_property

from src.config import SUBSCRIPTION_DOMAIN_PREFIX
from src.utils.times import time_diff
from src.utils.pagination import Pagination
from ..core import Base

if TYPE_CHECKING:
    from .user import User


class SubscriptionUsage(Base):
    __tablename__ = "subscription_usages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    sub_id: Mapped[int] = mapped_column(Integer, ForeignKey("subscriptions.id"), nullable=False, index=True)
    server_id: Mapped[int] = mapped_column(Integer, ForeignKey("servers.id"), nullable=False, index=True)
    inbound_id: Mapped[int] = mapped_column(Integer, nullable=True, index=True)
    client_id: Mapped[int] = mapped_column(Integer, nullable=True, index=True)

    usage: Mapped[BigInteger] = mapped_column(BigInteger, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)
    activated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)
    removed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    remark: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    server_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    access_key: Mapped[str] = mapped_column(String(16), nullable=False, index=True)

    owner: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True, index=True)

    expire: Mapped[int] = mapped_column(BigInteger, nullable=False)
    limit_usage: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    offset_usage: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    last_sub_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.now, nullable=True)

    user: Mapped[Optional["User"]] = relationship("User", back_populates=None, lazy="selectin")
    usages: Mapped[List["SubscriptionUsage"]] = relationship("SubscriptionUsage", uselist=True, lazy="selectin")

    @hybrid_property
    def online_at(self) -> Optional[datetime]:
        if not self.usages:
            return None
        latest_usage = max(self.usages, key=lambda u: u.updated_at or u.created_at)
        return latest_usage.updated_at

    @online_at.expression
    def online_at(cls):
        if not cls.usages:
            return None
        latest_usage = max(cls.usages, key=lambda u: u.updated_at or u.created_at)
        return latest_usage.updated_at

    @hybrid_property
    def current_usage(self) -> int:
        if not self.usages:
            return 0
        return self.lifetime_usage - self.offset_usage

    @current_usage.expression
    def current_usage(cls):
        if not cls.usages:
            return 0
        return cls.lifetime_usage - cls.offset_usage

    @hybrid_property
    def is_inactive(self) -> bool:
        return self.expired or self.limited

    @is_inactive.expression
    def is_inactive(cls):
        return cls.expired or cls.limited

    @hybrid_property
    def lifetime_usage(self) -> int:
        return sum(usage.usage for usage in self.usages) if self.usages else 0

    @lifetime_usage.expression
    def lifetime_usage(cls):
        return sum(usage.usage for usage in cls.usages) if cls.usages else 0

    @hybrid_property
    def left_usage(self) -> int:
        return self.limit_usage - self.current_usage if self.limit_usage != 0 else 0

    @left_usage.expression
    def left_usage(cls):
        return cls.limit_usage - cls.current_usage if cls.limit_usage != 0 else 0

    @hybrid_property
    def is_active(self) -> bool:
        return self.activated and self.enabled and not self.limited and not self.expired and not self.removed

    @is_active.expression
    def is_active(cls):
        return cls.activated and cls.enabled and not cls.limited and not cls.expired and not cls.removed

    @hybrid_property
    def is_activate_expire(self) -> bool:
        return self.expire >= 0

    @is_activate_expire.expression
    def is_activate_expire(cls):
        return cls.expire >= 0

    @property
    def emoji(self) -> str:
        return "🟢" if self.is_active else "🔴"

    @property
    def owner_name(self) -> str:
        return self.user.full_name if self.user else "➖"

    @property
    def kb_remark(self) -> str:
        return f"{self.emoji} {self.remark} [{self.owner_name}]"

    @hybrid_property
    def availabled(self) -> bool:
        return self.enabled and self.activated and not self.removed and not self.expired and not self.limited

    @availabled.expression
    def availabled(cls):
        return cls.enabled and cls.activated and not cls.removed and not cls.expired and not cls.limited

    @property
    def link(self) -> str:
        return f"{SUBSCRIPTION_DOMAIN_PREFIX}/guards/{self.access_key}"

    @property
    def expire_day(self) -> str:
        if self.expire == 0:
            expire = "unlimited time"
        elif self.expire > 0:
            expire = time_diff(datetime.fromtimestamp(self.expire))
        elif self.expire < 0:
            expire = f"{int(abs(self.expire) / 86400)} Day"
        return expire

    @hybrid_property
    def limited(self) -> bool:
        return self.limit_usage != 0 and int(self.limit_usage - self.current_usage) <= 0

    @limited.expression
    def limited(cls):
        return cls.limit_usage != 0 and int(cls.limit_usage - cls.current_usage) <= 0

    @hybrid_property
    def expired(self) -> bool:
        return self.expire > 0 and int(datetime.now().timestamp()) > self.expire

    @expired.expression
    def expired(cls):
        return cls.expire > 0 and int(datetime.now().timestamp()) > cls.expire

    @property
    def left_usage_gb(self) -> str:
        return f"{round((self.left_usage / (1024**3)), 3)} GB" if self.limit_usage else "➖"

    def format(self) -> Dict:
        server_usages = {}
        for usage in self.usages:
            if usage.server_id not in server_usages:
                server_usages[usage.server_id] = {
                    "server": usage.server,
                    "total_usage": 0,
                }
            server_usages[usage.server_id]["total_usage"] += usage.usage

        server_usage_str = (
            "\n".join(
                f"{data['server'].remark} -> {round(data['total_usage'] / (1024**3), 3)} GB" for data in server_usages.values()
            )
            if server_usages
            else "No usage data"
        )
        now = datetime.now()
        return {
            "id": self.id,
            "remark": self.remark,
            "access_key": self.access_key,
            "server_key": self.server_key,
            "owner": self.owner_name,
            "enabled": self.enabled,
            "activated": self.activated,
            "availabled": self.availabled,
            "expire": self.expire_day,
            "link": self.link,
            "limit_usage": f"{round((self.limit_usage / (1024**3)), 3)} GB" if self.limit_usage else "➖",
            "current_usage": f"{round((self.current_usage / (1024**3)), 3)} GB" if self.current_usage else "➖",
            "lifetime_usage": f"{round((self.lifetime_usage / (1024**3)), 3)} GB" if self.lifetime_usage else "➖",
            "left_usage": self.left_usage_gb,
            "created_at": time_diff(self.created_at, now),
            "updated_at": time_diff(self.updated_at, now),
            "last_sub_updated_at": time_diff(self.last_sub_updated_at, now),
            "online_at": time_diff(self.online_at, now),
            "server_usages": server_usage_str,
        }

    @classmethod
    def generate_server_key(cls) -> str:
        from uuid import uuid4

        return str(uuid4())

    @classmethod
    def generate_access_key(cls) -> str:
        from secrets import token_hex

        return str(token_hex(8))

    @classmethod
    def generate_expire(cls, expire: int, after_first_use: bool) -> int:
        if after_first_use:
            return int((datetime.now() + timedelta(seconds=expire)).timestamp())
        return expire

    @classmethod
    async def activate_expire(cls, db: AsyncSession, sub: "Subscription") -> "Subscription":
        if sub.expire < 0:
            sub.expire = int((datetime.now() + timedelta(seconds=abs(sub.expire))).timestamp())
            await db.commit()
        return sub

    @classmethod
    async def get_by_server_key(cls, db: AsyncSession, key: str) -> Optional["Subscription"]:
        result = await db.execute(
            select(cls)
            .options(selectinload(cls.usages), selectinload(cls.user))
            .where(cls.server_key == key)
            .where(cls.removed == False)  # noqa
        )
        return result.scalars().first()

    @classmethod
    async def get_by_access_key(cls, db: AsyncSession, key: str) -> Optional["Subscription"]:
        result = await db.execute(
            select(cls)
            .options(selectinload(cls.usages), selectinload(cls.user))
            .where(cls.access_key == key)
            .where(cls.removed == False)  # noqa
        )
        return result.scalars().first()

    @classmethod
    async def get_by_id(cls, db: AsyncSession, id: int) -> Optional["Subscription"]:
        result = await db.execute(
            select(cls)
            .options(selectinload(cls.usages), selectinload(cls.user))
            .where(cls.id == id)
            .where(cls.removed == False)  # noqa
        )
        return result.scalars().first()

    @classmethod
    async def get_by_remark(cls, db: AsyncSession, remark: str) -> Optional["Subscription"]:
        result = await db.execute(
            select(cls)
            .options(selectinload(cls.usages), selectinload(cls.user))
            .where(cls.remark == remark)
            .where(cls.removed == False)  # noqa
        )
        return result.scalars().first()

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        *,
        remark: str,
        access_key: str,
        server_key: str,
        expire: int,
        limit_usage: int,
        owner: Optional[int] = None,
    ) -> "Subscription":
        item = cls(
            remark=remark,
            server_key=server_key,
            access_key=access_key,
            expire=expire,
            limit_usage=limit_usage,
            owner=owner,
        )
        db.add(item)
        await db.flush()
        return item

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        *,
        sub: "Subscription",
        remark: Optional[str] = None,
        expire: Optional[int] = None,
        limit_usage: Optional[int] = None,
        server_key: Optional[str] = None,
        enabled: Optional[bool] = None,
        activated: Optional[bool] = None,
        removed: Optional[bool] = None,
    ) -> Optional["Subscription"]:
        if remark is not None:
            sub.remark = remark
        if expire is not None:
            sub.expire = expire
        if limit_usage is not None:
            sub.limit_usage = limit_usage
        if enabled is not None:
            sub.enabled = enabled
        if activated is not None:
            sub.activated = activated
        if removed is not None:
            sub.removed = removed
        if server_key is not None:
            sub.server_key = server_key

        await db.flush()
        return sub

    @classmethod
    async def revoke(cls, db: AsyncSession, sub: "Subscription") -> "Subscription":
        sub.access_key = cls.generate_key()
        await db.flush()
        return sub

    @classmethod
    async def remove(cls, db: AsyncSession, sub: "Subscription") -> None:
        sub.removed = True
        await db.flush()

    @classmethod
    async def get_all(
        cls,
        db: AsyncSession,
    ) -> List["Subscription"]:
        query = select(cls).options(selectinload(cls.usages), selectinload(cls.user)).order_by(cls.created_at.desc())
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_paginated(cls, db: AsyncSession, page: int, limit: int = 20) -> Pagination:
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
        return Pagination(items=items, total=total_pages, current=current, back=back, next=next)

    @classmethod
    async def upsert_usage(
        cls,
        db: AsyncSession,
        *,
        sub_id: int,
        server_id: int,
        inbound_id: int,
        client_id: int,
        usage: int,
    ) -> None:
        existing = await db.execute(
            select(SubscriptionUsage)
            .where(SubscriptionUsage.sub_id == sub_id)
            .where(SubscriptionUsage.server_id == server_id)
            .where(SubscriptionUsage.inbound_id == inbound_id)
            .where(SubscriptionUsage.client_id == client_id)
        )
        existing = existing.scalars().first()

        if existing:
            if existing.usage == usage:
                return
            existing.usage = usage
            existing.updated_at = datetime.now()
        else:
            if usage <= 0:
                return
            existing = SubscriptionUsage(
                sub_id=sub_id,
                server_id=server_id,
                inbound_id=inbound_id,
                client_id=client_id,
                usage=usage,
            )
            db.add(existing)
        return

    @classmethod
    async def reset_usage(cls, db: AsyncSession, sub: "Subscription") -> "Subscription":
        sub.offset_usage = sub.lifetime_usage
        await db.flush()
        return sub
