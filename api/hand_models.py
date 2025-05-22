from datetime import datetime
from pydantic import BaseModel
from typing import Literal, Optional, List

class JobBase(BaseModel):
    name: str
    url: str
    state: Literal["WORKING", "PAUSED", "STOPED"]
    mode: Literal["CRON", "TIMER"]

class JobCreate(JobBase):
    schedule: Optional[str] = None
    interval: Optional[int] = None

class JobResponse(JobBase):
    id: int
    schedule: Optional[str] = None
    interval: Optional[int] = None
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None

class JobsResponse(BaseModel):
    jobs: List[JobResponse]

class JobModeUpdate(BaseModel):
    mode: Literal["CRON", "TIMER"]
    schedule: Optional[str] = None  # if CRON
    interval: Optional[int] = None  # if TIMER (milliseconds)

class JobSettingsUpdate(BaseModel):
    schedule: Optional[str] = None  # for CRON
    interval: Optional[int] = None  # for TIMER

class JobStateUpdate(BaseModel):
    action: Literal["START", "PAUSE", "STOP"]
    start_at: Optional[datetime] = None  # if PAUSE


