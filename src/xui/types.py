import json
from typing import List
from pydantic import BaseModel, model_validator


class InboundClientSetting(BaseModel):
    email: str
    enable: bool
    subId: str = ""


class InboundSettings(BaseModel):
    clients: List[InboundClientSetting]


class ClientStats(BaseModel):
    id: int
    inboundId: int
    email: str
    enable: bool
    expiryTime: int
    up: int
    down: int
    total: int
    allTime: int
    subId: str
    reset: int


class ClientRequest(BaseModel):
    id: str
    enable: bool = True


class Inbound(BaseModel):
    id: int
    remark: str
    enable: bool
    clientStats: List[ClientStats]
    settings: str

    @model_validator(mode="before")
    @classmethod
    def merge_client_enable_status(cls, data):
        if "settings" in data and isinstance(data["settings"], str):
            settings_data = json.loads(data["settings"])
            inbound_settings = InboundSettings.model_validate(settings_data)

            settings_clients_map = {client.email: client for client in inbound_settings.clients}

            if "clientStats" in data:
                for client_stat in data["clientStats"]:
                    if client_stat["email"] in settings_clients_map:
                        client_setting = settings_clients_map[client_stat["email"]]
                        client_stat["enable"] = client_setting.enable
                        client_stat["subId"] = client_setting.subId

        return data
