from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings


class Base(DeclarativeBase):
    pass


def get_engine():
    settings = get_settings()
    url = settings.database_url
    # SQLite não suporta pool_pre_ping da mesma forma
    if url.startswith("sqlite"):
        return create_async_engine(url, echo=False, connect_args={"check_same_thread": False})
    return create_async_engine(url, echo=False, pool_pre_ping=True)


engine = get_engine()
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
