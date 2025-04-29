from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from api.config import settings


async_engine = create_async_engine(
    url=settings.db.DB_URL,
    echo=settings.db.echo,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow)

async_session_factory = async_sessionmaker(async_engine)


class Base(DeclarativeBase):
    pass
