from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from src.config import logger
from .items import access_generate, remove_expire_messages, subs_checkers


class SimpleScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def start(self):
        """Start the scheduler and add the job"""
        await access_generate()
        self.scheduler.add_job(
            self._wrap_coroutine(remove_expire_messages),
            trigger=CronTrigger(minute=0),
            id="remove_expire_messages",
            replace_existing=False,
        )
        self.scheduler.add_job(
            self._wrap_coroutine(access_generate),
            trigger=IntervalTrigger(hours=8),
            id="access_generate",
            replace_existing=False,
        )
        self.scheduler.add_job(
            self._wrap_coroutine(subs_checkers),
            trigger=IntervalTrigger(seconds=100),
            id="subs_checkers",
            replace_existing=False,
        )
        self.scheduler.start()

    async def stop(self):
        """Stop the scheduler"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()

    def _wrap_coroutine(self, coro):
        """Wrapper async"""

        async def wrapper():
            try:
                await coro()
            except Exception as e:
                logger.error({e})

        return wrapper


TaskManager = SimpleScheduler()
