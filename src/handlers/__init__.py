from eiogram import Router
from .middlewares import Middleware
from . import commands, fallback  # noqa


def setup_handlers() -> Router:
    router = Router()
    router.middleware.register(Middleware())
    router.include_router(commands.router)
    return router


__all__ = ["setup_handlers"]
