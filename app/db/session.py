from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os

class Base(DeclarativeBase):
    pass

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# Only create engine if we have a real URL
if DATABASE_URL and "postgresql" in DATABASE_URL:
    engine = create_async_engine(
        DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://").replace("?sslmode=require", ""),
        echo=False,
        pool_size=5,
        max_overflow=10,
    )
else:
    engine = None

async def get_db() -> AsyncSession:
    if engine is None:
        return None
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with AsyncSessionLocal() as session:
        yield session