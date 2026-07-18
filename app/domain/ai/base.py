"""Abstract interface for AI-powered security explanation providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.ai.explanation import AIExplanation
from app.domain.models.finding import Finding


class BaseAIProvider(ABC):
    """Contract for producing security guidance from a standardized finding."""

    @abstractmethod
    def generate_explanation(
        self, finding: Finding, prompt: str | None = None
    ) -> AIExplanation:
        """Create a deterministic or provider-specific explanation for a finding."""
