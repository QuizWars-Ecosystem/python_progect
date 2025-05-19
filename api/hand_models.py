import datetime
from pydantic import BaseModel
from typing import Literal, Optional, List

class JobResponse(BaseModel):
    name: str
    url: str
    state: Literal["WORKING", "PAUSED", "STOPPED"]
    mode: Literal["CRON", "TIMER"]
    schedule: Optional[str] = None
    interval: Optional[int] = None
    nextRunAt: Optional[datetime] = None
    lastRunAt: Optional[datetime] = None

class JobsResponse(BaseModel):
    jobs: List[JobResponse]


