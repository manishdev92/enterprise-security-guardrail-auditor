"""Health, readiness, and root routes for the API service."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies.container import AppContainer, get_container
from app.api.schemas.health import HealthResponse, RootResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Application health")
def health_check() -> HealthResponse:
    """Return the overall health status for the service."""
    return HealthResponse(status="ok")


@router.get("/ready", response_model=HealthResponse, summary="Application readiness")
def readiness_check() -> HealthResponse:
    """Return the readiness status for the service."""
    return HealthResponse(status="ready")


@router.get("/", response_model=RootResponse, summary="Service root")
def root(container: Annotated[AppContainer, Depends(get_container)]) -> RootResponse:
    """Return basic metadata identifying the deployed service."""
    return RootResponse(name=container.settings.app_name, status="ok")
