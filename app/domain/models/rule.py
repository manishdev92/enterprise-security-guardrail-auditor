"""Security rule metadata models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RuleMetadata:
    """Describes the static properties of a rule."""

    rule_id: str
    rule_name: str
    description: str
    severity: str
    cloud_provider: str
    resource_types: tuple[str, ...]
