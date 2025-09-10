from eiogram import Router
from . import menu, update


def setup_settings_handlers(router: Router) -> None:
    router.include_router(menu.router)
    router.include_router(update.router)


__all__ = ["setup_settings_handlers"]
