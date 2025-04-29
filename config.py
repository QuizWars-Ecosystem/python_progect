import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path

yaml_path = Path(__file__).parent / "config.yaml"

class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8080

class Database(BaseModel):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    echo: bool = True
    pool_size: int = 20
    max_overflow: int = 10

    @property
    def DB_URL(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")


class Settings(BaseSettings):
    run: RunConfig
    db: Database

    @classmethod
    def from_yaml(cls, path: Path = yaml_path):
        with open(path, "r") as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)

settings = Settings.from_yaml()

