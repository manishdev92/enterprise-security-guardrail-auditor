"""Pydantic response models for health and readiness endpoints."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """Simple status response for liveness and readiness probes."""

    model_config = ConfigDict(extra="forbid")

    status: str


class RootResponse(BaseModel):
    """Root endpoint response with basic service metadata."""

    model_config = ConfigDict(extra="forbid")

    name: str
    status: str
