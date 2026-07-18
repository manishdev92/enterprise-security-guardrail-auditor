"""Domain models for normalized ingestion results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class NormalizedResource:
    """Represents a normalized IaC resource extracted from a template."""

    resource_type: str
    resource_name: str
    provider: str
    attributes: dict[str, Any] = field(default_factory=dict)
