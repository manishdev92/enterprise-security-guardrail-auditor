"""Upload and parse routes for Infrastructure-as-Code templates."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.dependencies.container import get_ingestion_service
from app.api.schemas.upload import (
    ParsedUploadResponse,
    ResourceResponse,
    UploadResponse,
)
from app.domain.services.ingestion_service import IngestionService

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post(
    "", response_model=UploadResponse, summary="Store an uploaded IaC template"
)
async def upload_template(
    file: Annotated[UploadFile, File(...)],
    ingestion_service: Annotated[IngestionService, Depends(get_ingestion_service)],
) -> UploadResponse:
    """Validate and persist an uploaded IaC file to disk."""
    storage_path, size_bytes = ingestion_service.store_upload(file)
    return UploadResponse(
        filename=file.filename or "unknown",
        stored=True,
        size_bytes=size_bytes,
        stored_path=str(storage_path),
    )


@router.post(
    "/parse",
    response_model=ParsedUploadResponse,
    summary="Parse an uploaded IaC template",
)
async def parse_template(
    file: Annotated[UploadFile, File(...)],
    ingestion_service: Annotated[IngestionService, Depends(get_ingestion_service)],
) -> ParsedUploadResponse:
    """Store the uploaded file and return normalized parsed resources."""
    storage_path, resources = await ingestion_service.ingest_upload(file)
    return ParsedUploadResponse(
        filename=file.filename or "unknown",
        stored=True,
        resource_count=len(resources),
        resources=[
            ResourceResponse(
                resource_type=resource.resource_type,
                resource_name=resource.resource_name,
                provider=resource.provider,
                attributes=resource.attributes,
            )
            for resource in resources
        ],
    )
