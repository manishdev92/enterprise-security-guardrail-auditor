"""Pydantic schemas for ingestion and parsing endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class ResourceResponse(BaseModel):
    """Response schema for a single normalized resource."""

    model_config = ConfigDict(extra="forbid")

    resource_type: str
    resource_name: str
    provider: str
    attributes: dict[str, Any]


class UploadResponse(BaseModel):
    """Response payload for file upload success."""

    model_config = ConfigDict(extra="forbid")

    filename: str
    stored: bool
    size_bytes: int
    stored_path: str


class ParsedUploadResponse(BaseModel):
    """Response payload for parsed upload success."""

    model_config = ConfigDict(extra="forbid")

    filename: str
    stored: bool
    resource_count: int
    resources: list[ResourceResponse]
