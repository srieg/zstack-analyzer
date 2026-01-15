from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os
from typing import AsyncGenerator
from pathlib import Path

# Support both PostgreSQL and SQLite for easy demo
DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    # Default to SQLite for easy local development/demo
    db_path = Path(__file__).parent.parent.parent / "data" / "zstack.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"

# Configure engine based on database type
is_sqlite = DATABASE_URL.startswith("sqlite")

engine_kwargs = {
    "echo": os.getenv("DEBUG", "").lower() == "true",
}

if not is_sqlite:
    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 0,
    })

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

async def get_database() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()