from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import settings

engine = create_async_engine(
    settings.SQLALCHEMY_ASYNCIO_DATABASE_URI,
    future=True,
    echo=True,
)

# expire_on_commit=False will prevent attributes from being expired after commit.
AsyncSessionFactory = async_sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False,
)


# Dependency
async def get_db() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        yield session
