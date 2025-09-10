from src.db import GetDB, Subscription, Server
from src.xui import XUIRequest, ClientRequest
from src.config import logger


async def subs_checkers() -> None:
    async with GetDB() as db:
        subs = await Subscription.get_all(db, removed=None)
        if not subs:
            logger.info("No subscriptions found")
            return
        servers = await Server.get_all(db)
        if not servers:
            logger.info("No servers found")
            return
        for server in servers:
            inbounds = await XUIRequest.get_inbounds(host=server.api_host, cookies=server.cookies)
            if not inbounds:
                logger.warning(f"No inbounds found for server {server.id}")
                continue
            for inbound in inbounds:
                clients = {client.subId: client for client in inbound.clientStats}
                for sub in subs:
                    client = clients.get(sub.server_key, None)
                    if not client:
                        if not sub.availabled:
                            continue
                        logger.info(f"Creating client for subscription {sub} on server {server.id}")
                        success = await XUIRequest.create_client(
                            host=server.api_host,
                            cookies=server.cookies,
                            inbound_id=inbound.id,
                            clients=[ClientRequest(id=sub.server_key)],
                        )
                        if success:
                            logger.info(f"Client for subscription {sub} created successfully on server {server.id}")
                        continue
                    await Subscription.upsert_usage(
                        db, sub_id=sub.id, server_id=server.id, inbound_id=inbound.id, client_id=client.id, usage=client.allTime
                    )
                    if client and sub.removed:
                        success = await XUIRequest.remove_client(
                            host=server.api_host,
                            cookies=server.cookies,
                            inbound_id=inbound.id,
                            client_id=client.subId,
                        )
                        if success:
                            logger.info(f"Client for removed subscription {sub} deleted successfully on server {server.id}")
                        continue
                    if client.enable and not sub.availabled:
                        success = await XUIRequest.deactivate_client(
                            host=server.api_host,
                            cookies=server.cookies,
                            inbound_id=inbound.id,
                            client_id=client.subId,
                        )
                        if success:
                            logger.info(f"Client for subscription {sub} deactivated successfully on server {server.id}")
                        continue
                    if not client.enable and sub.availabled:
                        success = await XUIRequest.activate_client(
                            host=server.api_host,
                            cookies=server.cookies,
                            inbound_id=inbound.id,
                            client_id=client.subId,
                        )
                        if success:
                            logger.info(f"Client for subscription {sub} re-activated successfully on server {server.id}")
                        continue
