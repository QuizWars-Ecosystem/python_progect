import asyncio
from typing import Dict, Any
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from api.config import settings
from parser.trivia_api import trivia_main
from db.fn import (db_create_new_job, db_get_all_jobs, db_change_mode,
db_change_state_job)



class JobScheduler:

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs: Dict[int, Dict[str, Any]] = {}
        self.running_tasks: Dict[int, asyncio.Task] = {}

    async def start(self):
        try:
            if self.scheduler.running:
                return

            db_jobs = await db_get_all_jobs() # DB
            db_job_names = {job["name"] for job in db_jobs} if db_jobs else set()

            for job_config in settings.jobs: # YAML
                if job_config.name not in db_job_names:
                    job_id = await db_create_new_job(
                        name=job_config.name,
                        url=job_config.url,
                        state=job_config.state,
                        mode=job_config.mode,
                        schedule=job_config.schedule,
                        interval=job_config.interval,
                        next_run=job_config.next_run,
                        last_run=job_config.last_run)
                    if job_id:
                        db_jobs.append({
                            "id": job_id,
                            "name": job_config.name,
                            "url": job_config.url,
                            "state": job_config.state,
                            "mode": job_config.mode,
                            "schedule": job_config.schedule,
                            "interval": job_config.interval,
                            "next_run": job_config.next_run,
                            "last_run": job_config.last_run})

            for job in db_jobs:
                await self.schedule_job(job)

            self.scheduler.start()

        except Exception as e:
            raise Exception(f"Error from start: {e}")


    async def schedule_job(self, job: Dict[str, Any]):
        job_id = job["id"]
        self.jobs[job_id] = job

        if job["state"] != "WORKING":
            return

        try:
            if job["mode"] == "CRON" and job["schedule"]:
                trigger = CronTrigger.from_crontab(job["schedule"])
            elif job["mode"] == "TIMER" and job["interval"]:
                trigger = IntervalTrigger(seconds=job["interval"])

            if job["mode"] != "CRON" and job["mode"] != "TIMER":
                raise ValueError("Invalid jobs mode")
            if not job["schedule"] and not job["interval"]:
                raise ValueError("Need to pass a schedule or interval")

            self.scheduler.add_job(func=self.run_job, trigger=trigger,
                                   args=[job_id], id=str(job_id),
                                   next_run_time=datetime.now(),
                                   replace_existing=True)
            # logs
            # jobs_in_scheduler = self.scheduler.get_jobs()
            # print(f"Всего задач в планировщике: {len(jobs_in_scheduler)}")
            # for j in jobs_in_scheduler:
            #     print(f"Задача: id={j.id}, next_run_time={j.next_run_time}")
            # logs

        except Exception as e:
            print(f"Error scheduling job {job["name"]}: {e}")


    async def run_job(self, job_id: int):
        # print("run_job РАБОТАЕТ!!!!!!!!!!!!!!!!!!!!!!!!!")
        job = self.jobs.get(job_id)
        if not job:
            return
        if job["state"] != "WORKING":
            return

        try:
            if job["name"] == "trivia-api":
                await trivia_main()
        except Exception as e:
            print(f"Job {job_id} failed: {e}")


    async def update_job_mode(self, job_id: int, mode_data: Dict[str, Any]):
        """Обновляет режим задачи"""
        success = await db_change_mode(
            job_id,
            mode_data["mode"],
            mode_data.get("schedule"),
            mode_data.get("interval"))
        if success:
            print(success)
            # Обновляем локальный кэш
            if job_id in self.jobs:
                self.jobs[job_id].update(mode_data)
            await self.reschedule_job(job_id)
        return success


    async def update_job_state(self, job_id: int, state: str, start_at: Optional[datetime] = None):
        """Обновляет состояние задачи"""
        success = await db_change_state_job(job_id, state, start_at)
        if success:
            # Обновляем локальный кэш
            if job_id in self.jobs:
                self.jobs[job_id]["state"] = state
                if start_at:
                    self.jobs[job_id]["next_run"] = start_at
            await self.reschedule_job(job_id)
        return success


    async def reschedule_job(self, job_id: int):
        """Перезапускает задачу с новыми параметрами"""
        job = await self.get_job_from_db(job_id)
        if job:
            self.scheduler.remove_job(str(job_id))
            if job_id in self.running_tasks:
                self.running_tasks[job_id].cancel()
                self.running_tasks.pop(job_id, None)
            await self.schedule_job(job)


    async def get_job_from_db(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Получает задачу из БД"""
        jobs = await db_get_all_jobs()
        return next((job for job in jobs if job['id'] == job_id), None)

