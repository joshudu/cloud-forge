from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os

class Base(DeclarativeBase):
    pass

DATABASE_URL = os.getenv("DATABASE_URL", "")

engine = None
AsyncSessionLocal = None

if DATABASE_URL and "postgresql" in DATABASE_URL:
    clean_url = DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://"
    ).replace("?sslmode=require", "")

    engine = create_async_engine(
        clean_url,
        echo=False,
        pool_size=5,          # base connections kept open
        max_overflow=10,      # extra connections allowed under load
        pool_timeout=30,      # seconds to wait for a connection
        pool_recycle=1800,    # recycle connections after 30 minutes
        pool_pre_ping=True,   # test connection before using it
                              # this is what allows recovery after DB restart
    )

    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

async def get_db():
    if AsyncSessionLocal is None:
        yield None
        return
    async with AsyncSessionLocal() as session:
        yield session