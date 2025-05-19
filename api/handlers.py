import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, DecodeError

from api.config import settings
from hand_models import JobResponse, JobsResponse


router = APIRouter(prefix="/jobs", tags=['Jobs'])
security = HTTPBearer()

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

@router.get("/", response_model=JobsResponse)
async def get_all_jobs():
    """Запрос на получение всех задач сервера."""
    jobs = []
    for job in settings.jobs:
        jobs.append(JobResponse(
            name=job.name,
            url=job.url,
            state=job.state,
            mode=job.mode,
            schedule=job.schedule,
            interval=job.interval,
            # nextRunAt=job.,
            # lastRunAt=job.
        ))
    return JobsResponse(jobs=jobs)

@router.put("/{jobId}/mode")
async def change_job_mode():
    """Запрос на изменение режима существующей задачи и присвоение ей новой конфигурации."""
    pass

@router.put("/{jobId}/settings")
async def update_job_settings():
    """Запрос на изменение только настроек выполнения уже существующей задачи."""
    pass

@router.put("/{jobId}/state")
async def change_job_state():
    """Запрос с возможностью останавливать, перезапускать либо ставить на паузу существующие задачи."""
    pass

