from typing import List
from pydantic import BaseModel


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
    reset: int


class ClientRequest(BaseModel):
    id: str
    enable: bool = True


class Inbound(BaseModel):
    id: int
    remark: str
    enable: bool
    clientStats: List[ClientStats]
