from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings

engine = create_async_engine(settings.database_url, pool_size=5, max_overflow=10)
session_factory = async_sessionmaker(engine, expire_on_commit=False)
