from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger


class JobScheduler:

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs = {}

    async def start(self):
        self.scheduler.start()

    async def add_job(self, ):
        pass
