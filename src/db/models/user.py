import logging
from datetime import datetime
from typing import Optional, Dict, Any, Union
from eiogram.types import User as EioUser, Message, CallbackQuery
from sqlalchemy import String, BigInteger, DateTime, Integer, Text, JSON, func
from sqlalchemy.sql import select, delete
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import BOT, TELEGRAM_ADMINS_ID
from src.utils.times import time_diff
from src.utils.pagination import Pagination
from ..core import Base, GetDB


class UserState(Base):
    __tablename__ = "user_states"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    state: Mapped[str] = mapped_column(Text, nullable=True)
    data: Mapped[dict] = mapped_column(JSON, nullable=True)


class UserMessage(Base):
    __tablename__ = "user_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    message_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now())

    @classmethod
    async def _get_user_id(cls, update: Union[Message, CallbackQuery]) -> int:
        message = update.message if isinstance(update, CallbackQuery) else update
        return message.chat.id

    @classmethod
    async def add(cls, update: Union[Message, CallbackQuery]) -> None:
        async with GetDB() as db:
            message = update.message if isinstance(update, CallbackQuery) else update
            db.add(UserMessage(user_id=message.chat.id, message_id=message.message_id))

    @classmethod
    async def clear(
        cls, update: Union[Message, CallbackQuery], *, keep_current: bool = False
    ) -> None:
        async with GetDB() as db:
            user_id = await cls._get_user_id(update)
            message_id = getattr(
                update.message if isinstance(update, CallbackQuery) else update,
                "message_id",
                None,
            )
            delete_condition = UserMessage.user_id == user_id
            if keep_current and message_id:
                delete_condition &= UserMessage.message_id != message_id
            messages = await db.execute(
                select(UserMessage.message_id).where(delete_condition)
            )
            message_ids = [msg[0] for msg in messages.all()]
            if message_ids:
                try:
                    await BOT.delete_messages(chat_id=user_id, message_ids=message_ids)
                except Exception as e:
                    logging.warning(f"Failed to delete messages: {e}")
            await db.execute(delete(UserMessage).where(delete_condition))
            message = update.message if isinstance(update, CallbackQuery) else update
            db.add(UserMessage(user_id=message.chat.id, message_id=message.message_id))

    def __repr__(self) -> str:
        return f"<UserMessage(id={self.id})>"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    join_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)
    online_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)

    @property
    def emoji(self) -> str:
        return "🟢" if self.has_access else "🔴"

    @property
    def kb_remark(self) -> str:
        return f"{self.emoji} {self.full_name} [{self.id}]"

    @property
    def mention(self) -> str:
        if self.username:
            return f"@{self.username}"
        return f"<a href='tg://user?id={self.id}'>{self.full_name}</a>"

    @property
    def has_access(self) -> bool:
        return self.id in TELEGRAM_ADMINS_ID

    def formatter(self) -> Dict[str, Any]:
        now = datetime.now()
        return {
            "id": self.id,
            "full_name": self.full_name,
            "username": f"@{self.username}" if self.username else "➖",
            "join_at": time_diff(self.join_at, now),
            "online_at": time_diff(self.online_at, now),
        }

    @classmethod
    async def get_by_id(cls, db: AsyncSession, id: int) -> Optional["User"]:
        result = await db.execute(select(cls).where(cls.id == id))
        return result.scalars().first()

    @classmethod
    async def get_by_username(cls, db: AsyncSession, username: str) -> Optional["User"]:
        result = await db.execute(select(cls).where(cls.username == username))
        return result.scalars().first()

    @classmethod
    async def get_by_fullname(
        cls, db: AsyncSession, full_name: str
    ) -> Optional["User"]:
        result = await db.execute(select(cls).where(cls.full_name == full_name))
        return result.scalars().first()

    @classmethod
    async def get_paginated(
        cls, db: AsyncSession, page: int, limit: int = 20
    ) -> Pagination:
        total_result = await db.execute(select(func.count()).select_from(cls))  # noqa
        total_items = total_result.scalar() or 0
        total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0
        if total_pages == 0:
            return Pagination(items=[], total=0, current=1, back=None, next=None)
        current = max(1, min(page, total_pages))
        query = (
            select(cls)
            .order_by(cls.join_at.desc())
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
    async def upsert(cls, db: AsyncSession, *, user: EioUser) -> Optional["User"]:
        dbuser = await cls.get_by_id(db, user.id)
        if dbuser:
            dbuser.full_name = user.full_name
            dbuser.username = user.username
            dbuser.online_at = datetime.now()
        else:
            dbuser = cls(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
            )
            db.add(dbuser)
        await db.flush()
        return dbuser

    def __repr__(self) -> str:
        return f"<User(id={self.id})>"
