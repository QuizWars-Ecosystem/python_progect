from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080

class Database(BaseModel):
    url: str = f"postgresql+asyncpg://user:password@host:port/dbname"
    echo: bool = True
    pool_size: int = 20
    max_overflow: int = 10

class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    db: Database = Database()

    model_config = SettingsConfigDict(env_file="name_env_file")

settings = Settings()

