# backend/core/database.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import settings
from typing import AsyncGenerator

# ✅ Use async-compatible engine
engine = create_async_engine(settings.DATABASE_URL_ASYNC, echo=True)

# ✅ Session factory
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# ✅ Base for SQLAlchemy models
Base = declarative_base()

# ✅ Dependency to use in FastAPI routes
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Synchronous engine (for reading table_dictionary in non-async context)
sync_engine = create_engine(settings.DATABASE_URL, echo=True)

# Synchronous session maker
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Dependency for getting a sync session
def get_sync_db():
    return SyncSessionLocal
