import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional, Literal, List, Dict

yaml_path = Path(__file__).parent.parent / "config.yaml"

class JWTConfig(BaseModel):
    secret_key: str = Field(..., min_length=32)
    algorithm: str = Field(default="HS256")

class JobConfig(BaseModel):
    name: str = Field(...)
    url: str = Field(...)
    mode: Literal["CRON", "TIMER"] = Field(default="CRON")
    schedule: Optional[str] = Field(default=None)
    interval: Optional[int] = Field(default=None)
    state: Literal["WORKING", "PAUSED", "STOPPED"] = Field(default="WORKING")

class SendConfig(BaseModel):
    batch_size: int = Field(default=5, ge=1)
    check_interval: int = Field(default=30, ge=1)
    min_questions: int = Field(default=200, ge=1)
    cron_schedule: str = Field(default="0 */6 * * *")
    api_key: str = Field(...)
    main_server_url: str = Field(...) # endpoint для отправки

class APIConfig(BaseModel):
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8080)
    root_path: str = Field(default="/api")
    jwt: JWTConfig


class Database(BaseModel):
    DB_HOST: str = Field(...)
    DB_PORT: int = Field(...)
    DB_USER: str = Field(...)
    DB_PASS: str = Field(...)
    DB_NAME: str = Field(...)

    echo: bool = Field(default=False)
    pool_size: int = Field(default=20, ge=1, le=100)
    max_overflow: int = Field(default=1, ge=0)

    @property
    def DB_URL(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")


class Settings(BaseSettings):
    api: APIConfig
    db: Database
    jobs: List[JobConfig]
    send: SendConfig

    _jobs_by_name: Dict[str, JobConfig] = {}

    @classmethod
    def from_yaml(cls, path: Path = yaml_path):
        with open(path, "r") as f:
            config_data = yaml.safe_load(f)
        if "api" in config_data and "run" in config_data["api"]:
            config_data["api"].update(config_data["api"].pop("run"))
        settings = cls(**config_data)
        settings._jobs_by_name = {job.name: job for job in settings.jobs}
        return settings

    def get_job(self, name: str) -> Optional[JobConfig]:
        """Получить job по имени"""
        return self._jobs_by_name.get(name)

settings = Settings.from_yaml()
