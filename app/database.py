from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
from app.config import DATABASE_URL

# Use asyncpg driver (e.g., postgresql+asyncpg://...)
# echo=False: SQL echo logs bound parameters (raw emails/PII) to stdout,
# bypassing the mask_email() protection applied in app/logger.py.
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        # Create all tables defined in models
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
