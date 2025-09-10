from datetime import datetime
from fastapi import APIRouter, Response, HTTPException, Request

from src.db import Subscription, Server
from src.xui import XUIManager
from .dep import get_headers, GetGuard, GetSession

router = APIRouter(
    prefix="/guards",
    tags=["Guards"],
)


@router.get("/{key}")
async def get_subscription(key: str, db: GetSession, request: Request, sub: GetGuard):
    """Handle incoming subscription request from clients."""
    dbsub = await Subscription.get_by_access_key(db, key)
    if not dbsub:
        raise HTTPException(status_code=404)
    dbsub.last_sub_updated_at = datetime.now()
    if not dbsub.is_activate_expire:
        dbsub = await dbsub.activate_expire(db, dbsub)
    servers = await Server.get_all(db)
    if not servers:
        raise HTTPException(status_code=404, detail="No available server")
    links = await XUIManager.get_links(servers=servers, sub=dbsub)
    return Response(
        content="\n".join(links) if links else "",
        media_type="text/plain",
        headers=get_headers(dbsub),
    )
