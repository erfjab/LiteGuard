from src.xui import XUIRequest
from src.db import Server, GetDB
from src.config import logger


async def access_generate():
    async with GetDB() as db:
        servers = await Server.get_all(db=db)
        for server in servers:
            if not server.need_update_access:
                continue
            access = await XUIRequest.login(
                host=server.config["host"],
                username=server.config["username"],
                password=server.config["password"],
            )
            if not access:
                logger.warning("Failed to generate access: %s", server.remark)
                continue
            await Server.upsert_access(db, server.id, access=dict(access.cookies))
            logger.info("%s generate access.", server.remark.title())
