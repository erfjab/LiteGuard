from eiogram import Router
from . import create, info, menu, update


def setup_subscription_handlers(router: Router) -> None:
    router.include_router(create.router)
    router.include_router(info.router)
    router.include_router(menu.router)
    router.include_router(update.router)


__all__ = ["setup_subscription_handlers"]
