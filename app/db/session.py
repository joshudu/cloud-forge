from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os

class Base(DeclarativeBase):
    pass

def get_engine():
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    # Convert sync URL to async if needed
    if "+asyncpg" not in DATABASE_URL and "postgresql" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://").replace("?sslmode=require", "")
    return create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=5,
        max_overflow=10,
    )

def get_session_maker(engine):
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

async def get_db() -> AsyncSession:
    engine = get_engine()
    AsyncSessionLocal = get_session_maker(engine)
    async with AsyncSessionLocal() as session:
        yield session