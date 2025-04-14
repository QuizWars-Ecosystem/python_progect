from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

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
    run: RunConfig = RunConfig()
    db: Database = Database()

    model_config = SettingsConfigDict(env_file="./Demo/.env")

settings = Settings()

