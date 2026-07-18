"""Application service that orchestrates AI explanation generation."""

from __future__ import annotations

from typing import Sequence

from app.core.logging import get_logger
from app.domain.ai.base import BaseAIProvider
from app.domain.ai.explanation import AIExplanation
from app.domain.ai.prompt_builder import PromptBuilder
from app.domain.models.finding import Finding


class AIExplainer:
    """Converts standardized findings into guidance using a provider-agnostic interface."""

    def __init__(
        self, provider: BaseAIProvider, prompt_builder: PromptBuilder | None = None
    ) -> None:
        self.provider = provider
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.logger = get_logger("app.ai.explainer")

    def explain_findings(self, findings: Sequence[Finding]) -> list[AIExplanation]:
        """Build explanations for a list of findings while staying resilient to unexpected errors."""
        if not findings:
            return []

        explanations: list[AIExplanation] = []
        for finding in findings:
            try:
                prompt = self.prompt_builder.build_prompt(finding)
                explanation = self.provider.generate_explanation(finding, prompt=prompt)
            except Exception as exc:  # pragma: no cover - defensive fallback path
                self.logger.exception(
                    "AI explanation generation failed",
                    extra={
                        "error_type": exc.__class__.__name__,
                        "details": str(exc),
                        "rule_id": finding.rule_id,
                    },
                )
                explanation = self.provider.generate_explanation(finding, prompt=None)

            explanations.append(explanation)

        return explanations
