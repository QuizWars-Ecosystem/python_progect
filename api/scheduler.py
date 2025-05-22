import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Dict, Any

from api.config import settings
from db.fn import (create_new_scheduler_job, get_all_jobs, change_mode_by_id,
change_parameters_by_id, change_state_job_by_id, update_job_timestamps)



class JobScheduler:

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs: Dict[int, Dict[str, Any]] = {}
        self.running_tasks: Dict[int, asyncio.Task] = {}

    async def start(self):
        db_jobs = await get_all_jobs()
        db_job_names = {job["name"] for job in db_jobs} if db_jobs else set()

        for job_config in settings.jobs:
            if job_config.name not in db_job_names:
                job = await create_new_scheduler_job(
                name=job_config.name,
                url=job_config.url,
                state=job_config.state,
                mode=job_config.mode,
                schedule=job_config.schedule,
                interval=job_config.interval,
                next_run=None,
                last_run=None)
                db_jobs.append(job)

        for task in db_jobs:
            pass

        print()
                

