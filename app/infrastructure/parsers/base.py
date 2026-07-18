"""Parser abstractions for converting IaC templates into normalized resources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.domain.models.ingestion import NormalizedResource


class BaseParser(ABC):
    """Abstract interface for parsers that normalize infrastructure templates."""

    @abstractmethod
    def parse(self, content: bytes, filename: str) -> list[NormalizedResource]:
        """Parse template content into normalized resources."""

    @classmethod
    def supported_extensions(cls) -> tuple[str, ...]:
        """Return the file extensions supported by the parser."""
        return ()

    @staticmethod
    def _normalize_attributes(raw_attributes: Any) -> dict[str, Any]:
        """Normalize attribute payloads into a plain dictionary."""
        if isinstance(raw_attributes, dict):
            return {str(key): value for key, value in raw_attributes.items()}
        return {}
