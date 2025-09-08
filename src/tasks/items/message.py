from datetime import datetime, timedelta
from sqlalchemy import delete
from src.db import GetDB, UserMessage


async def remove_expire_messages():
    async with GetDB() as db:
        threshold = datetime.now() - timedelta(hours=48)
        await db.execute(delete(UserMessage).where(UserMessage.created_at < threshold))
