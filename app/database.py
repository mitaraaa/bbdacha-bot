from contextlib import asynccontextmanager
from typing import AsyncGenerator

from async_lru import alru_cache
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    connect_args={"server_settings": {"jit": "off"}},
)


@alru_cache()
async def get_session_maker():
    return sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session_maker = await get_session_maker()
    async with session_maker() as session:
        yield session
