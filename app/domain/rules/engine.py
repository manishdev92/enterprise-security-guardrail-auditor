"""Rule engine orchestration for security scanning."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from app.domain.models.finding import Finding
from app.domain.models.ingestion import NormalizedResource
from app.domain.rules.aws_rules import build_default_rules
from app.domain.rules.base import BaseRule


@dataclass(slots=True)
class RuleRegistry:
    """Registers and exposes the active set of rules."""

    rules: list[BaseRule] = field(default_factory=list)

    def register(self, rule: BaseRule) -> None:
        self.rules.append(rule)


@dataclass(slots=True)
class RuleEngine:
    """Evaluates normalized resources against all registered rules."""

    registry: RuleRegistry = field(
        default_factory=lambda: RuleRegistry(build_default_rules())
    )

    def evaluate_resources(
        self, resources: Sequence[NormalizedResource]
    ) -> list[Finding]:
        findings: list[Finding] = []
        for resource in resources:
            for rule in self.registry.rules:
                finding = rule.evaluate(resource)
                if finding is not None:
                    findings.append(finding)
        return findings
