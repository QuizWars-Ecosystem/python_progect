from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from typing import Dict, Any, Optional

from db.fn import update_job_timestamps, get_all_jobs, change_mode_by_id, change_state_job_by_id
from parser.trivia_api import trivia_main


class JobScheduler:

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs: Dict[int, Dict[str, Any]] = {}


    async def start(self):
        await self.load_jobs_from_db()
        self.scheduler.start()


    async def load_jobs_from_db(self):
        db_jobs = await get_all_jobs()
        if not db_jobs:
            return

        for job_data in db_jobs:
            await self.add_job_to_scheduler(
                job_id=job_data['id'],
                name=job_data['name'],
                url=job_data['url'],
                state=job_data['state'],
                mode=job_data['mode'],
                schedule=job_data['schedule'],
                interval=job_data['interval'],
                next_run=job_data['next_run'],
                last_run=job_data['last_run'])


    async def add_job_to_scheduler(
            self,
            job_id: int,
            name: str,
            url: str,
            state: str,
            mode: str,
            schedule: Optional[str] = None,
            interval: Optional[int] = None,
            next_run: Optional[datetime] = None,
            last_run: Optional[datetime] = None):
        """Добавляет задачу в планировщик"""
        self.jobs[job_id] = {
            "name": name,
            "url": url,
            "state": state,
            "mode": mode,
            "schedule": schedule,
            "interval": interval,
            "next_run": next_run,
            "last_run": last_run,
            "job_instance": None}

        if state == "WORKING":
            await self._schedule_job(job_id)


    async def _schedule_job(self, job_id: int):
        """Создает задачу в APScheduler"""
        job_data = self.jobs[job_id]

        if job_data["mode"] == "CRON":
            trigger = CronTrigger.from_crontab(job_data["schedule"])
        else:
            trigger = IntervalTrigger(milliseconds=job_data["interval"])

        async def job_wrapper():
            await self._execute_job(job_id)

        job_instance = self.scheduler.add_job(
            job_wrapper,
            trigger=trigger,
            id=str(job_id))

        # Обновляем next_run в БД
        await update_job_timestamps(
            id=job_id,
            last_run=job_data["last_run"] or datetime.now(),
            next_run=job_instance.next_run_time)

        self.jobs[job_id]["job_instance"] = job_instance
        self.jobs[job_id]["next_run"] = job_instance.next_run_time


    async def _execute_job(self, job_id: int):
        """Выполняет задачу и обновляет метки времени"""
        print(f"Executing job {job_id} - {self.jobs[job_id]['name']}")

        await trivia_main() # сюда парсеры!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        await update_job_timestamps(
            id=job_id,
            last_run=datetime.now(),
            next_run=self.jobs[job_id]["job_instance"].next_run_time)

        self.jobs[job_id]["last_run"] = datetime.now()


    async def update_job_mode(self, job_id: int, mode_data: dict):
        """Обновляет режим задачи"""

        success = await change_mode_by_id(
            id=job_id,
            mode=mode_data["mode"],
            schedule=mode_data.get("schedule"),
            interval=mode_data.get("interval"))

        if success and job_id in self.jobs:
            self.jobs[job_id].update(mode_data)
            if self.jobs[job_id]["state"] == "WORKING":
                if self.jobs[job_id]["job_instance"]:
                    self.jobs[job_id]["job_instance"].remove()
                await self._schedule_job(job_id)


    async def update_job_state(self, job_id: int, state: str, start_at: Optional[datetime] = None):
        """Обновляет состояние задачи"""

        success = await change_state_job_by_id(
            id=job_id,
            action=state,
            start_at=start_at
        )

        if success and job_id in self.jobs:
            self.jobs[job_id]["state"] = state

            if state == "WORKING":
                await self._schedule_job(job_id)
            elif state == "PAUSED" and self.jobs[job_id]["job_instance"]:
                self.jobs[job_id]["job_instance"].pause()
            elif state == "STOPED" and self.jobs[job_id]["job_instance"]:
                self.jobs[job_id]["job_instance"].remove()
                self.jobs[job_id]["job_instance"] = None
