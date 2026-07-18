"""Database session management and initialization for SQLite-backed persistence."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.infrastructure.db.base import Base

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


def init_db() -> None:
    """Create all database tables for the current metadata."""
    Base.metadata.create_all(bind=engine)


def get_db_session() -> Session:
    """Create a synchronous database session for repository and service use."""
    return SessionLocal()
