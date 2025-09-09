import asyncio

from src.db import Server
from .request import XUIRequest
from .types import ClientRequest, Inbound


class XUIManager:
    @classmethod
    async def get_inbounds(cls, server: Server) -> list[Inbound] | None:
        return await XUIRequest.get_inbounds(host=server.host, cookies=server.cookies)

    @classmethod
    async def create(cls, servers: list[Server], uuid: str) -> bool:
        inbounds_per_server = await asyncio.gather(*[cls.get_inbounds(s) for s in servers])

        tasks = []
        total = 0

        for server, inbounds in zip(servers, inbounds_per_server):
            if not inbounds:
                continue
            total += len(inbounds)
            for inbound in inbounds:
                tasks.append(
                    XUIRequest.create_client(
                        host=server.host,
                        cookies=server.cookies,
                        inbound_id=inbound.id,
                        clients=[ClientRequest(id=uuid)],
                    )
                )

        if not tasks:
            return True

        results = await asyncio.gather(*tasks)
        success_created = sum(1 for r in results if r)

        return success_created == total

    @classmethod
    async def deactivate(cls, servers: list[Server], uuid: str) -> bool:
        inbounds_per_server = await asyncio.gather(*[cls.get_inbounds(s) for s in servers])

        tasks = []
        total = 0

        for server, inbounds in zip(servers, inbounds_per_server):
            if not inbounds:
                continue
            total += len(inbounds)
            for inbound in inbounds:
                tasks.append(
                    XUIRequest.deactivate_client(
                        host=server.host,
                        cookies=server.cookies,
                        inbound_id=inbound.id,
                        client_id=uuid,
                    )
                )

        if not tasks:
            return True

        results = await asyncio.gather(*tasks)
        success_deactivated = sum(1 for r in results if r)

        return success_deactivated == total

    @classmethod
    async def activate(cls, servers: list[Server], uuid: str) -> bool:
        inbounds_per_server = await asyncio.gather(*[cls.get_inbounds(s) for s in servers])

        tasks = []
        total = 0

        for server, inbounds in zip(servers, inbounds_per_server):
            if not inbounds:
                continue
            total += len(inbounds)
            for inbound in inbounds:
                tasks.append(
                    XUIRequest.activate_client(
                        host=server.host,
                        cookies=server.cookies,
                        inbound_id=inbound.id,
                        client_id=uuid,
                    )
                )

        if not tasks:
            return True

        results = await asyncio.gather(*tasks)
        success_activated = sum(1 for r in results if r)

        return success_activated == total

    @classmethod
    async def remove(cls, servers: list[Server], uuid: str) -> bool:
        inbounds_per_server = await asyncio.gather(*[cls.get_inbounds(s) for s in servers])

        tasks = []
        total = 0

        for server, inbounds in zip(servers, inbounds_per_server):
            if not inbounds:
                continue
            total += len(inbounds)
            for inbound in inbounds:
                tasks.append(
                    XUIRequest.remove_client(
                        host=server.host,
                        cookies=server.cookies,
                        inbound_id=inbound.id,
                        client_id=uuid,
                    )
                )
        if not tasks:
            return True

        results = await asyncio.gather(*tasks)
        success_removed = sum(1 for r in results if r)

        return success_removed == total

    @classmethod
    async def revoke(cls, servers: list[Server], uuid: str, new_uuid: str, enable: bool) -> bool:
        inbounds_per_server = await asyncio.gather(*[cls.get_inbounds(s) for s in servers])

        tasks = []
        total = 0

        for server, inbounds in zip(servers, inbounds_per_server):
            if not inbounds:
                continue
            total += len(inbounds)
            for inbound in inbounds:
                tasks.append(
                    XUIRequest.revoke_client(
                        host=server.host,
                        cookies=server.cookies,
                        inbound_id=inbound.id,
                        client_id=new_uuid,
                        client=ClientRequest(id=uuid, enable=enable),
                    )
                )
        if not tasks:
            return True

        results = await asyncio.gather(*tasks)
        success_revoked = sum(1 for r in results if r)

        return success_revoked == total
