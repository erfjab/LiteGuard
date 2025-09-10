import logging
from copy import deepcopy
from uvicorn import Config, Server
from uvicorn.config import LOGGING_CONFIG
from src.config import (
    UVICORN_SSL_CERTFILE,
    UVICORN_SSL_KEYFILE,
    UVICORN_HOST,
    UVICORN_PORT,
    BOT,
    DP,
    TELEGRAM_WEBHOOK_HOST,
    TELEGRAM_WEBHOOK_SECRET_KEY,
)
from src.api import API
from src.utils.state import DatabaseStorage
from src.handlers import setup_handlers
from src.tasks import TaskManager

logger = logging.getLogger(__name__)


def get_log_config():
    log_config = deepcopy(LOGGING_CONFIG)
    default_fmt = "[%(asctime)s] %(levelprefix)s %(message)s"
    date_fmt = "%m/%d %H:%M:%S"
    log_config["formatters"]["default"]["fmt"] = default_fmt
    log_config["formatters"]["default"]["datefmt"] = date_fmt
    log_config["formatters"]["access"]["fmt"] = default_fmt
    log_config["formatters"]["access"]["datefmt"] = date_fmt
    return log_config


async def main():
    cfg = Config(
        app=API,
        host=UVICORN_HOST,
        port=UVICORN_PORT,
        workers=1,
        log_config=get_log_config(),
    )
    if UVICORN_SSL_CERTFILE and UVICORN_SSL_KEYFILE:
        cfg.ssl_certfile = UVICORN_SSL_CERTFILE
        cfg.ssl_keyfile = UVICORN_SSL_KEYFILE

    server = Server(cfg)
    await server.serve()


@API.on_event("startup")
async def startup_event():
    await TaskManager.start()
    await BOT.set_webhook(
        url=f"{TELEGRAM_WEBHOOK_HOST}/api/telegram/webhook",
        secret_token=TELEGRAM_WEBHOOK_SECRET_KEY,
        allowed_updates=[
            "message",
            "callback_query",
        ],
    )
    DP.include_router(setup_handlers())
    DP.storage = DatabaseStorage()
    username = (await BOT.get_me()).username
    logger.info(f"Bot [@{username}] started successfully")


@API.on_event("shutdown")
async def shutdown_event():
    await TaskManager.stop()
    logger.info("Bot stopped successfully")
