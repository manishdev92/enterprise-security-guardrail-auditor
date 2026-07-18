"""Application service for validating, storing, and parsing uploaded IaC files."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import Settings
from app.core.exceptions import ParsingError, UploadError
from app.core.logging import get_logger
from app.domain.models.ingestion import NormalizedResource
from app.infrastructure.parsers.factory import ParserFactory


class IngestionService:
    """Coordinate secure upload validation, storage, and parsing."""

    def __init__(
        self, settings: Settings, parser_factory: ParserFactory | None = None
    ) -> None:
        self.settings = settings
        self.parser_factory = parser_factory or ParserFactory()
        self.logger = get_logger("app.ingestion_service")

    async def ingest_upload(
        self, file: UploadFile
    ) -> tuple[Path, list[NormalizedResource]]:
        """Validate, persist, and parse an uploaded IaC file."""
        if not file.filename:
            raise UploadError("Uploaded file is missing a filename")

        suffix = Path(file.filename).suffix.lower()
        if suffix not in {".tf", ".json", ".yaml", ".yml"}:
            raise UploadError("Unsupported file type")

        contents = await file.read()
        if not contents.strip():
            raise UploadError("Uploaded file is empty")
        if len(contents) > self.settings.max_upload_size_bytes:
            raise UploadError("Uploaded file exceeds the maximum supported size")

        safe_name = self._safe_filename(file.filename)
        storage_path = self._store_upload(contents, safe_name)
        try:
            parser = self.parser_factory.get_parser(safe_name, contents)
            resources = parser.parse(contents, safe_name)
        except ParsingError as exc:
            self.logger.warning(
                "Upload parse failed",
                extra={"upload_name": safe_name, "details": str(exc)},
            )
            raise UploadError(f"Parse failed: {exc}") from exc

        self.logger.info(
            "Upload ingested successfully",
            extra={
                "upload_name": safe_name,
                "resource_count": len(resources),
                "stored_path": str(storage_path),
            },
        )
        return storage_path, resources

    def store_upload(self, file: UploadFile) -> tuple[Path, int]:
        """Persist an uploaded file without parsing it."""
        if not file.filename:
            raise UploadError("Uploaded file is missing a filename")

        suffix = Path(file.filename).suffix.lower()
        if suffix not in {".tf", ".json", ".yaml", ".yml"}:
            raise UploadError("Unsupported file type")

        contents = self._read_upload_bytes(file)
        if not contents.strip():
            raise UploadError("Uploaded file is empty")
        if len(contents) > self.settings.max_upload_size_bytes:
            raise UploadError("Uploaded file exceeds the maximum supported size")

        safe_name = self._safe_filename(file.filename)
        storage_path = self._store_upload(contents, safe_name)
        return storage_path, len(contents)

    def _read_upload_bytes(self, file: UploadFile) -> bytes:
        contents = file.file.read() if hasattr(file, "file") else b""
        if not contents:
            return b""
        return contents

    def _store_upload(self, contents: bytes, filename: str) -> Path:
        upload_dir = Path(self.settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        unique_name = f"{uuid.uuid4().hex}-{filename}"
        storage_path = upload_dir / unique_name
        storage_path.write_bytes(contents)
        return storage_path

    def _safe_filename(self, filename: str) -> str:
        raw_name = Path(filename).name
        stem = Path(raw_name).stem
        suffix = Path(raw_name).suffix.lower()
        sanitized_stem = "".join(
            char if char.isalnum() or char in {"-", "_"} else "_" for char in stem
        )
        sanitized_stem = sanitized_stem or "upload"
        return f"{sanitized_stem}{suffix}" if suffix else sanitized_stem
