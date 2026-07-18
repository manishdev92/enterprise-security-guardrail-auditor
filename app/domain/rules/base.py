"""Abstractions for the security rule engine."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.models.finding import Finding
from app.domain.models.ingestion import NormalizedResource


@dataclass(slots=True)
class BaseRule(ABC):
    """Base contract for all security rules."""

    rule_id: str
    rule_name: str
    description: str
    severity: str
    cloud_provider: str
    resource_types: tuple[str, ...]

    def evaluate(self, resource: NormalizedResource) -> Finding | None:
        """Evaluate a single normalized resource and return a finding when violated."""
        if resource.provider.lower() != self.cloud_provider.lower():
            return None
        if resource.resource_type not in self.resource_types:
            return None
        return self._evaluate(resource)

    @abstractmethod
    def _evaluate(self, resource: NormalizedResource) -> Finding | None:
        """Implement the rule-specific logic for a matching resource."""
