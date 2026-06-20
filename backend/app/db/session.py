"""Async database session management using SQLAlchemy.

Provides the async engine, session factory, and a FastAPI dependency
for injecting database sessions into route handlers.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for the duration of a single request.

    This is a FastAPI dependency. It yields a session, and guarantees
    the session is closed afterward, committing on success and rolling
    back on any unhandled exception.

    Yields:
        An active AsyncSession bound to the configured database engine.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            logger.error("db_session_rolled_back", exc_info=True)
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    """Verify the database is reachable by executing a trivial query.

    Used at application startup and in health check endpoints to confirm
    the database connection is alive before serving requests.

    Returns:
        True if the connection succeeds, False otherwise.
    """
    try:
        async with engine.connect() as connection:
            await connection.execute(__import__("sqlalchemy").text("SELECT 1"))
        logger.info("db_connection_check_succeeded")
        return True
    except Exception as exc:
        logger.error("db_connection_check_failed", error=str(exc))
        return False