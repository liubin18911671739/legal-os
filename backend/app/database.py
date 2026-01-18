from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
import os

from app.core.config import settings

# Create async engine
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


# Dependency injection for FastAPI
async def get_db() -> AsyncSession:
    """
    Get database session.
    
    Usage in FastAPI:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Database initialization
async def init_db():
    """
    Initialize database - create all tables.
    Call this on application startup.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Database health check
async def check_db_connection() -> bool:
    """
    Check database connection health.
    
    Returns:
        bool: True if connection is healthy
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False


# Close database connections
async def close_db():
    """
    Close all database connections.
    Call this on application shutdown.
    """
    await async_engine.dispose()
