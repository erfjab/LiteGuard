from typing import Annotated
from fastapi import Depends, HTTPException

from src.db import GetDB, AsyncSession, Subscription, Server, Setting


async def _get_db():
    async with GetDB() as db:
        yield db


async def get_servers(db: AsyncSession = Depends(_get_db)):
    servers = await Server.get_all(db, availabled=True)
    if not servers:
        raise HTTPException(status_code=404, detail="Hosting not found")
    return servers


async def get_settings(db: AsyncSession = Depends(_get_db)):
    setting = await Setting.get(db)
    if not setting:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return setting


async def _get_guard(key: str, db: AsyncSession = Depends(_get_db)) -> Subscription:
    sub = await Subscription.get_by_access_key(db, key)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub


def get_headers(sub: Subscription) -> dict:
    subscription_userinfo = {
        "upload": 0,
        "download": sub.current_usage,
        "total": sub.limit_usage,
        "expire": (sub.expire if sub.expire > 0 else 0),
    }
    response_headers = {
        "content-disposition": "",
        "profile-web-page-url": sub.link,
        "support-url": "",
        "profile-title": "Guard Sub",
        "profile-update-interval": "1",
        "subscription-userinfo": "; ".join(f"{key}={val}" for key, val in subscription_userinfo.items()),
    }
    return response_headers


GetSession = Annotated[AsyncSession, Depends(_get_db)]
GetGuard = Annotated[Subscription, Depends(_get_guard)]
GetSetting = Annotated[Setting, Depends(get_settings)]
GetServers = Annotated[list[Server], Depends(get_servers)]
