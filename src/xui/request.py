import json
import base64
from typing import Optional, Dict, List
from httpx import AsyncClient, Response
from src.config import logger
from .types import Inbound, ClientRequest


class XUIRequest:
    @classmethod
    def _get_headers(cls) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
        }

    @classmethod
    def generate_client_identifier(cls, inbound_id: int, client_id: str) -> str:
        return str(inbound_id) + client_id[len(str(inbound_id)) :]

    @classmethod
    async def _send(
        cls,
        url: str,
        method: str = "GET",
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        cookies: Optional[dict] = None,
    ) -> Dict[str, str]:
        try:
            async with AsyncClient(cookies=cookies) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=cls._get_headers(),
                    json=json,
                    params=params,
                )
            response.raise_for_status()
            if not response.json().get("success"):
                logger.error(f"Request to {url} failed [{json}]: {response.json().get('msg', 'Unknown error')}")
            return response.json()
        except Exception as e:
            logger.error(f"Request to {url} failed: {e}")
            return {"success": False, "msg": str(e), "obj": None}

    @classmethod
    async def get_links(cls, host: str) -> List[str]:
        try:
            async with AsyncClient() as client:
                response = await client.get(url=host)
            response.raise_for_status()
            content = response.read()
            try:
                decode = base64.b64decode(content).decode("utf-8")
            except Exception:
                decode = content.decode("utf-8")
            return [link.strip() for link in decode.split("\n") if link.strip()]
        except Exception as e:
            logger.error(f"Request to {host} failed: {e}")
            return []

    @classmethod
    async def login(cls, host: str, username: str, password: str) -> Optional[Response]:
        try:
            async with AsyncClient() as client:
                response = await client.request(
                    method="POST",
                    url=f"{host}/login",
                    headers=cls._get_headers(),
                    json={"username": username, "password": password},
                )
                if response.status_code != 200:
                    return
                return response
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return

    @classmethod
    async def get_inbounds(cls, host: str, cookies: dict) -> Optional[List[Inbound]]:
        inbounds = await cls._send(url=f"{host}/panel/api/inbounds/list", method="GET", cookies=cookies)
        return (
            [Inbound(**item) for item in inbounds["obj"] if item["protocol"] in ["vless", "vmess", "trojan", "shadowsocks"]]
            if inbounds["success"]
            else None
        )

    @classmethod
    async def create_client(
        cls,
        host: str,
        cookies: dict,
        inbound_id: int,
        clients: List[ClientRequest],
    ) -> bool:
        result = await cls._send(
            url=f"{host}/panel/api/inbounds/addClient",
            method="POST",
            cookies=cookies,
            json={
                "id": inbound_id,
                "settings": json.dumps(
                    {
                        "clients": [
                            {
                                "id": cls.generate_client_identifier(inbound_id, client.id),
                                "email": cls.generate_client_identifier(inbound_id, client.id),
                                "password": cls.generate_client_identifier(inbound_id, client.id),
                                "subId": client.id,
                                "expiryTime": 0,
                                "totalGB": 0,
                                "enable": True,
                            }
                            for client in clients
                        ]
                    }
                ),
            },
        )
        return True if result["success"] else False

    @classmethod
    async def deactivate_client(cls, host: str, cookies: dict, inbound_id: int, client_id: str) -> bool:
        target = cls.generate_client_identifier(inbound_id, client_id)
        result = await cls._send(
            url=f"{host}/panel/api/inbounds/updateClient/{target}",
            method="POST",
            cookies=cookies,
            json={
                "id": inbound_id,
                "settings": json.dumps(
                    {
                        "clients": [
                            {
                                "id": target,
                                "email": target,
                                "password": target,
                                "subId": client_id,
                                "expiryTime": 0,
                                "totalGB": 0,
                                "enable": False,
                            }
                        ]
                    }
                ),
            },
        )
        return True if result["success"] else False

    @classmethod
    async def activate_client(cls, host: str, cookies: dict, inbound_id: int, client_id: str) -> bool:
        target = cls.generate_client_identifier(inbound_id, client_id)
        result = await cls._send(
            url=f"{host}/panel/api/inbounds/updateClient/{target}",
            method="POST",
            cookies=cookies,
            json={
                "id": inbound_id,
                "settings": json.dumps(
                    {
                        "clients": [
                            {
                                "id": target,
                                "email": target,
                                "password": target,
                                "subId": client_id,
                                "expiryTime": 0,
                                "totalGB": 0,
                                "enable": True,
                            }
                        ]
                    }
                ),
            },
        )
        return True if result["success"] else False

    @classmethod
    async def revoke_client(
        cls,
        host: str,
        cookies: dict,
        inbound_id: int,
        client_id: str,
        client: ClientRequest,
    ) -> bool:
        target = cls.generate_client_identifier(inbound_id, client_id)
        result = await cls._send(
            url=f"{host}/panel/api/inbounds/updateClient/{target}",
            method="POST",
            cookies=cookies,
            json={
                "id": inbound_id,
                "settings": json.dumps(
                    {
                        "clients": [
                            {
                                "id": target,
                                "email": target,
                                "password": target,
                                "subId": client_id,
                                "enable": client.enable,
                                "expiryTime": 0,
                                "totalGB": 0,
                            }
                        ]
                    }
                ),
            },
        )
        return True if result["success"] else False

    @classmethod
    async def remove_client(cls, host: str, cookies: dict, inbound_id: int, client_id: str) -> bool:
        result = await cls._send(
            url=f"{host}/panel/api/inbounds/{inbound_id}/delClient/{inbound_id}{client_id}",
            method="POST",
            cookies=cookies,
        )
        return True if result["success"] else False

    @classmethod
    async def reset_client(cls, host: str, cookies: dict, inbound_id: int, client_id: str) -> bool:
        result = await cls._send(
            url=f"{host}/panel/api/inbounds/{inbound_id}/resetClientTraffic/{inbound_id}{client_id}",
            method="POST",
            cookies=cookies,
        )
        return True if result["success"] else False
