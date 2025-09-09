from src.db import Server
from .request import XUIRequest
from .types import ClientRequest, Inbound


class XUIManager:
    @classmethod
    async def get_inbounds(cls, server: Server) -> list[Inbound] | None:
        return await XUIRequest.get_inbounds(host=server.host, cookies=server.cookies)

    @classmethod
    async def create(cls, servers: list[Server], uuid: str) -> bool:
        success = 0
        total = 0
        for server in servers:
            inbounds = await cls.get_inbounds(server)
            if not inbounds:
                continue
            total += len(inbounds)
            for inbound in inbounds:
                exists = any(c.id == uuid for c in inbound.clientStats)
                if exists:
                    success += 1
                    continue

                client = await XUIRequest.create_client(
                    host=server.host,
                    cookies=server.cookies,
                    inbound_id=inbound.id,
                    clients=[ClientRequest(id=uuid)],
                )
                if client:
                    success += 1
        return success == total

    @classmethod
    async def deactivate(cls, servers: list[Server], uuid: str) -> bool:
        success = 0
        total = 0
        for server in servers:
            inbounds = await cls.get_inbounds(server)
            if not inbounds:
                continue
            total += len(inbounds)
            for inbound in inbounds:
                target = next((c for c in inbound.clientStats if c.id == uuid), None)
                if target is not None and not target.enable:
                    success += 1
                    continue

                client = await XUIRequest.deactivate_client(
                    host=server.host,
                    cookies=server.cookies,
                    inbound_id=inbound.id,
                    client_id=uuid,
                )
                if client:
                    success += 1
        return success == total

    @classmethod
    async def activate(cls, servers: list[Server], uuid: str) -> bool:
        success = 0
        total = 0
        for server in servers:
            inbounds = await cls.get_inbounds(server)
            if not inbounds:
                continue
            total += len(inbounds)
            for inbound in inbounds:
                target = next((c for c in inbound.clientStats if c.id == uuid), None)
                if target is not None and target.enable:
                    success += 1
                    continue

                client = await XUIRequest.activate_client(
                    host=server.host,
                    cookies=server.cookies,
                    inbound_id=inbound.id,
                    client_id=uuid,
                )
                if client:
                    success += 1
        return success == total

    @classmethod
    async def remove(cls, servers: list[Server], uuid: str) -> bool:
        total = 0
        success = 0
        for server in servers:
            inbounds = await cls.get_inbounds(server)
            if not inbounds:
                continue
            total += len(inbounds)
            for inbound in inbounds:
                client = await XUIRequest.remove_client(
                    host=server.host,
                    cookies=server.cookies,
                    inbound_id=inbound.id,
                    client_id=uuid,
                )
                if client:
                    success += 1
        return success == total

    @classmethod
    async def revoke(cls, servers: list[Server], uuid: str, new_uuid: str, enable: bool) -> bool:
        total = 0
        success = 0
        for server in servers:
            inbounds = await cls.get_inbounds(server)
            if not inbounds:
                continue
            total += len(inbounds)
            for inbound in inbounds:
                client = await XUIRequest.revoke_client(
                    host=server.host,
                    cookies=server.cookies,
                    inbound_id=inbound.id,
                    client_id=new_uuid,
                    client=ClientRequest(id=uuid, enable=enable),
                )
                if client:
                    success += 1
        return success == total
