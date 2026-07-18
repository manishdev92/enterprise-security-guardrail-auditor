"""Prompt construction for AI explanation generation."""

from __future__ import annotations

from app.domain.models.finding import Finding


class PromptBuilder:
    """Builds structured prompts from standardized security findings."""

    def build_prompt(self, finding: Finding) -> str:
        """Create a deterministic prompt that instructs the provider to explain the finding."""
        return (
            "You are a senior cloud security engineer. Explain the following finding in a concise but detailed way. "
            "Return the response in sections: Risk Summary, Technical Explanation, Business Impact, Terraform Fix, "
            "CloudFormation Fix, Best Practice, and References.\n\n"
            f"Rule ID: {finding.rule_id}\n"
            f"Rule Name: {finding.rule_name}\n"
            f"Severity: {finding.severity}\n"
            f"Status: {finding.status}\n"
            f"Resource ID: {finding.resource_id}\n"
            f"Resource Type: {finding.resource_type}\n"
            f"Message: {finding.message}\n"
            f"Remediation: {finding.remediation}"
        )
