"""Value object for AI-generated security explanations."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class AIExplanation:
    """Represents human-readable guidance emitted for a security finding."""

    rule_id: str
    severity: str
    risk_summary: str
    technical_explanation: str
    business_impact: str
    terraform_fix: str
    cloudformation_fix: str
    best_practice: str
    references: list[str] = field(default_factory=list)
