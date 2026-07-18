"""SQLAlchemy declarative base definitions for persistence models."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Common base class for all ORM models in the application."""

    pass
