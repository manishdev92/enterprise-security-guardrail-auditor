"""Dependency injection helpers for application services and repositories."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.domain.ai.base import BaseAIProvider
from app.domain.ai.explainer import AIExplainer
from app.domain.ai.provider import MockAIProvider
from app.domain.services.ingestion_service import IngestionService
from app.infrastructure.db.session import SessionLocal


@dataclass(slots=True)
class AppContainer:
    """Simple container for shared application dependencies."""

    settings: Settings


container = AppContainer(settings=get_settings())


def get_container() -> AppContainer:
    """Return the shared dependency container."""
    return container


def get_db_session() -> Generator[Session, None, None]:
    """Provide a database session for request-scoped dependency injection."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_ingestion_service() -> IngestionService:
    """Create or return the ingestion service for upload and parsing workflows."""
    return IngestionService(settings=container.settings)


def get_ai_provider() -> BaseAIProvider:
    """Provide the offline AI provider implementation for explanation workflows."""
    return MockAIProvider()


def get_ai_explainer(
    provider: Annotated[BaseAIProvider, Depends(get_ai_provider)],
) -> AIExplainer:
    """Create an explainer service using the injected provider implementation."""
    return AIExplainer(provider=provider)
