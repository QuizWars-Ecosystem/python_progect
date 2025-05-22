from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, DecodeError

from api.config import settings
from api.sheduler import JobScheduler
from api.hand_models import (JobResponse,
                             JobsResponse,
                             JobModeUpdate,
                             JobSettingsUpdate,
                             JobStateUpdate)
from db.fn import ( get_all_jobs,
                    change_mode_by_id,
                    change_parameters_by_id,
                    change_state_job_by_id)


router = APIRouter(prefix="/jobs", tags=['Jobs'])
security = HTTPBearer()
job_scheduler = JobScheduler()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},)
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.api.jwt.secret_key, algorithms=[settings.api.jwt.algorithm])
        print(payload)
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"})
    except (InvalidTokenError, DecodeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"})
# test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30"
# test_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=test_token)
# asyncio.run(get_current_user(test_credentials))

@router.on_event("startup")
async def startup_event():
    await job_scheduler.start()


@router.get("/", response_model=JobsResponse)
async def get_all_jobs(jwt: dict = Depends(get_current_user)):
    """Запрос на получение всех задач сервера."""
    db_jobs = await get_all_jobs()
    if not db_jobs:
        return JobsResponse(jobs=[])
    return JobsResponse(jobs=[JobResponse(**job) for job in db_jobs])

@router.put("/{jobId}/mode")
async def change_job_mode(job_id: int, mode_data: JobModeUpdate,
                          jwt: dict = Depends(get_current_user)):
    """Запрос на изменение режима существующей задачи и присвоение ей новой конфигурации."""
    await job_scheduler.update_job_mode(job_id, mode_data.dict())
    return {"status": "success"}

@router.put("/{jobId}/settings")
async def update_job_settings(job_id: int, settings_data: JobSettingsUpdate,
                              jwt: dict = Depends(get_current_user)):
    """Запрос на изменение только настроек выполнения уже существующей задачи."""
    success = await change_parameters_by_id(
        id=job_id,
        schedule=settings_data.schedule,
        interval=settings_data.interval)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update settings")

    if job_id in job_scheduler.jobs:
        if settings_data.schedule:
            job_scheduler.jobs[job_id]["schedule"] = settings_data.schedule
        if settings_data.interval:
            job_scheduler.jobs[job_id]["interval"] = settings_data.interval

    return {"status": "success"}

@router.put("/{jobId}/state")
async def change_job_state(job_id: int, state_data: JobStateUpdate,
                           jwt: dict = Depends(get_current_user)):
    """Запрос с возможностью останавливать, перезапускать либо ставить на паузу существующие задачи."""
    await job_scheduler.update_job_state(
        job_id=job_id,
        state=state_data.action,
        start_at=state_data.start_at)
    return {"status": "success"}

