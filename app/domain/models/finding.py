"""Security finding domain model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Finding:
    """Represents a normalized security finding emitted by the rule engine."""

    rule_id: str
    rule_name: str
    severity: str
    status: str
    resource_id: str
    resource_type: str
    message: str
    remediation: str
