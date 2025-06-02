import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.config import settings
from api.handlers import router as jobs_rout, job_scheduler
from db.fn import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables() # Инициализация БД
    await job_scheduler.start() # Запуск планировщика
    yield

app = FastAPI(root_path=settings.api.root_path, lifespan=lifespan)
app.include_router(jobs_rout)


if __name__ == "__main__":
    uvicorn.run(app="run:app", host=settings.api.host, port=settings.api.port)
