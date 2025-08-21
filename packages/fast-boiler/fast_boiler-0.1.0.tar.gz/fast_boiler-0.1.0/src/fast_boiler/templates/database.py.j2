from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

# UPDATED: Use aiosqlite for async SQLite connection
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./app.db"

# UPDATED: Switched to async engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

# UPDATED: Switched to async session factory
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

# UPDATED: Async dependency to get a DB session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session