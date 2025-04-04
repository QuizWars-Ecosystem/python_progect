from models import Questions, Options, Categories, Complexity
from database import async_engine, async_session_factory, Base

async def create_tables():
    async with async_engine.begin() as conn:
        conn.run_sync(Base.metadata.drop_all())
        conn.run_sync(Base.metadata.create_all())





