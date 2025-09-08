from eiogram import Router
from .middlewares import Middleware
from . import commands, fallback  # noqa
from .servers import setup_server_handlers


def setup_handlers() -> Router:
    router = Router()
    router.middleware.register(Middleware())
    router.include_router(commands.router)
    setup_server_handlers(router=router)
    return router


__all__ = ["setup_handlers"]
