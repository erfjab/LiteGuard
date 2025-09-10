import asyncio
import base64
import json
import urllib
from v2share import V2Data
from src.db import Server, Subscription, Setting
from .request import XUIRequest
from .types import ClientRequest, Inbound


class XUIManager:
    @classmethod
    def _find_client(cls, inbound: Inbound, uuid: str):
        for c in inbound.clientStats:
            if c.subId == uuid:
                return c
        return None

    @classmethod
    async def get_inbounds(cls, server: Server) -> list[Inbound] | None:
        return await XUIRequest.get_inbounds(host=server.api_host, cookies=server.cookies)

    @classmethod
    async def create(cls, servers: list[Server], uuid: str) -> bool:
        inbounds_per_server = await asyncio.gather(*[cls.get_inbounds(s) for s in servers])

        tasks = []
        planned = 0

        for server, inbounds in zip(servers, inbounds_per_server):
            if not inbounds:
                continue
            for inbound in inbounds:
                if cls._find_client(inbound, uuid):
                    continue
                planned += 1
                tasks.append(
                    XUIRequest.create_client(
                        host=server.api_host,
                        cookies=server.cookies,
                        inbound_id=inbound.id,
                        clients=[ClientRequest(id=uuid)],
                    )
                )

        if not tasks:
            return True

        results = await asyncio.gather(*tasks)
        success_created = sum(1 for r in results if r)

        return success_created == planned

    @classmethod
    async def deactivate(cls, servers: list[Server], uuid: str) -> bool:
        inbounds_per_server = await asyncio.gather(*[cls.get_inbounds(s) for s in servers])

        tasks = []
        planned = 0

        for server, inbounds in zip(servers, inbounds_per_server):
            if not inbounds:
                continue
            for inbound in inbounds:
                client = cls._find_client(inbound, uuid)
                if not client:
                    continue
                if not client.enable:
                    continue
                planned += 1
                tasks.append(
                    XUIRequest.deactivate_client(
                        host=server.api_host,
                        cookies=server.cookies,
                        inbound_id=inbound.id,
                        client_id=uuid,
                    )
                )

        if not tasks:
            return True

        results = await asyncio.gather(*tasks)
        success_deactivated = sum(1 for r in results if r)

        return success_deactivated == planned

    @classmethod
    async def activate(cls, servers: list[Server], uuid: str) -> bool:
        inbounds_per_server = await asyncio.gather(*[cls.get_inbounds(s) for s in servers])

        tasks = []
        planned = 0

        for server, inbounds in zip(servers, inbounds_per_server):
            if not inbounds:
                continue
            for inbound in inbounds:
                client = cls._find_client(inbound, uuid)
                if not client:
                    continue
                if client.enable:
                    continue
                planned += 1
                tasks.append(
                    XUIRequest.activate_client(
                        host=server.api_host,
                        cookies=server.cookies,
                        inbound_id=inbound.id,
                        client_id=uuid,
                    )
                )

        if not tasks:
            return True

        results = await asyncio.gather(*tasks)
        success_activated = sum(1 for r in results if r)

        return success_activated == planned

    @classmethod
    async def remove(cls, servers: list[Server], uuid: str) -> bool:
        inbounds_per_server = await asyncio.gather(*[cls.get_inbounds(s) for s in servers])

        tasks = []
        planned = 0

        for server, inbounds in zip(servers, inbounds_per_server):
            if not inbounds:
                continue
            for inbound in inbounds:
                client = cls._find_client(inbound, uuid)
                if not client:
                    continue
                planned += 1
                tasks.append(
                    XUIRequest.remove_client(
                        host=server.api_host,
                        cookies=server.cookies,
                        inbound_id=inbound.id,
                        client_id=uuid,
                    )
                )
        if not tasks:
            return True

        results = await asyncio.gather(*tasks)
        success_removed = sum(1 for r in results if r)

        return success_removed == planned

    @classmethod
    async def revoke(cls, servers: list[Server], uuid: str, new_uuid: str, enable: bool) -> bool:
        inbounds_per_server = await asyncio.gather(*[cls.get_inbounds(s) for s in servers])

        tasks = []
        planned = 0

        for server, inbounds in zip(servers, inbounds_per_server):
            if not inbounds:
                continue
            for inbound in inbounds:
                client = cls._find_client(inbound, uuid)
                if not client or new_uuid == uuid:
                    continue
                planned += 1
                tasks.append(
                    XUIRequest.revoke_client(
                        host=server.api_host,
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

        return success_revoked == planned

    @classmethod
    async def get_links(cls, servers: list[Server], sub: Subscription, setting: Setting) -> list[str]:
        links = []
        sub_info = sub.config_format()
        if sub.availabled:
            links.extend(
                (V2Data(protocol="vless", remark=info.format(**sub_info), address="127.0.0.0", port=1)).to_link()
                for info in setting.informations
            )
            if servers:
                for server in servers:
                    links.extend(await XUIRequest.get_links(f"{server.sub_host}/{sub.server_key}"))
        else:
            links.extend(
                (V2Data(protocol="vless", remark=placeholder.format(**sub_info), address="127.0.0.0", port=1)).to_link()
                for placeholder in setting.placeholders
            )
        return links

    @classmethod
    def rename(cls, link: str, server_id: int, server_key: str) -> str:
        try:

            def process_remark(remark: str) -> str:
                cleaned_remark = remark.replace(server_key, "").strip()
                if "-" in cleaned_remark:
                    return cleaned_remark.split("-")[0]
                return cleaned_remark

            if link.startswith("vmess://"):
                encoded_config = link[8:]
                config_json = json.loads(base64.b64decode(encoded_config).decode())
                remark = config_json.get("ps", "")
                new_remark = f"[{server_id}] {process_remark(remark)}"
                config_json["ps"] = new_remark
                new_encoded = base64.b64encode(json.dumps(config_json).encode()).decode()
                return f"vmess://{new_encoded}"

            elif link.startswith(("vless://", "trojan://", "ss://")):
                if "#" in link:
                    base_link, remark_part = link.split("#", 1)
                    remark = urllib.parse.unquote(remark_part)
                    new_remark = f"[{server_id}] {process_remark(remark)}"
                    return f"{base_link}#{urllib.parse.quote(new_remark)}"
                else:
                    return f"{link}#[{server_id}]"

            return link
        except Exception:
            return link
