"""Database setup and utilities.

This project uses synchronous SQLAlchemy (2.x) with a session-per-request pattern.
"""

from __future__ import annotations

from typing import Any, Dict, Generator, List

from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from app.config import settings


Base = declarative_base()


def _create_engine():
    url = settings.DATABASE_URL

    connect_args = {}
    if url.startswith("sqlite"):
        # Needed for SQLite when used with threads (e.g., Uvicorn workers)
        connect_args["check_same_thread"] = False

    engine_kwargs = {
        "echo": getattr(settings, "DATABASE_ECHO", False),
        "pool_pre_ping": getattr(settings, "DATABASE_POOL_PRE_PING", True),
        "connect_args": connect_args,
        "future": True,
    }

    # SQLite uses SingletonThreadPool/StaticPool by default; QueuePool settings
    # like pool_size/max_overflow are not valid there.
    if not url.startswith("sqlite"):
        engine_kwargs.update(
            {
                "pool_size": getattr(settings, "DATABASE_POOL_SIZE", 5),
                "max_overflow": getattr(settings, "DATABASE_MAX_OVERFLOW", 10),
                "pool_recycle": getattr(settings, "DATABASE_POOL_RECYCLE", 3600),
            }
        )
    elif ":memory:" in url:
        # Ensure an in-memory DB survives across multiple connections.
        engine_kwargs["poolclass"] = StaticPool

    return create_engine(url, **engine_kwargs)


engine = _create_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create database tables.

    Imports model modules to ensure metadata is populated.
    """

    # Import models so SQLAlchemy registers them with Base.metadata
    from app.models import contractor as _contractor  # noqa: F401
    from app.models import user as _user  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a DB session."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Return True if a simple query succeeds."""

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_db_info() -> Dict[str, Any]:
    """Basic DB diagnostics used by startup/health checks."""

    info: Dict[str, Any] = {
        "database_url": settings.DATABASE_URL,
        "database_type": engine.dialect.name,
        "table_count": 0,
        "tables": [],
    }

    try:
        tables = list(Base.metadata.tables.keys())
        info["tables"] = tables
        info["table_count"] = len(tables)
    except Exception:
        pass

    return info
