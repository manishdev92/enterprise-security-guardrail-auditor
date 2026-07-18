"""Request and response schemas for AI explainability endpoints."""

from __future__ import annotations


from pydantic import BaseModel, ConfigDict, Field


class FindingInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str
    rule_name: str
    severity: str
    status: str
    resource_id: str
    resource_type: str
    message: str
    remediation: str


class ExplainRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    findings: list[FindingInput] = Field(default_factory=list)


class ExplanationResponse(BaseModel):
    rule_id: str
    severity: str
    risk_summary: str
    technical_explanation: str
    business_impact: str
    terraform_fix: str
    cloudformation_fix: str
    best_practice: str
    references: list[str]


class ExplainResponse(BaseModel):
    explanations: list[ExplanationResponse]
