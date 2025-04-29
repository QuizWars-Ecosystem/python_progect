import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from pathlib import Path

yaml_path = Path(__file__).parent.parent / "config.yaml"

class JWTConfig(BaseModel):
    secret_key: str = Field(..., min_length=32)
    algorithm: str = Field(default="HS256")

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

    @classmethod
    def from_yaml(cls, path: Path = yaml_path):
        with open(path, "r") as f:
            config_data = yaml.safe_load(f)
        if "api" in config_data:
            api_data = config_data["api"]
            if "run" in api_data:
                api_data.update(api_data.pop("run"))
            if "port" in api_data:
                api_data["port"] = int(api_data["port"])
        return cls(**config_data)

settings = Settings.from_yaml()
