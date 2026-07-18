"""AI explanation REST endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies.container import get_ai_explainer
from app.api.schemas.explain import ExplainRequest, ExplainResponse, ExplanationResponse
from app.domain.ai.explainer import AIExplainer
from app.domain.models.finding import Finding

router = APIRouter(tags=["explanations"])


@router.post(
    "/explain",
    response_model=ExplainResponse,
    summary="Generate AI-guided remediation explanations",
)
def explain_findings(
    request: ExplainRequest,
    explainer: Annotated[AIExplainer, Depends(get_ai_explainer)],
) -> ExplainResponse:
    """Translate standardized findings into human-readable security guidance."""
    findings = [
        Finding(
            rule_id=item.rule_id,
            rule_name=item.rule_name,
            severity=item.severity,
            status=item.status,
            resource_id=item.resource_id,
            resource_type=item.resource_type,
            message=item.message,
            remediation=item.remediation,
        )
        for item in request.findings
    ]
    explanations = explainer.explain_findings(findings)

    return ExplainResponse(
        explanations=[
            ExplanationResponse(
                rule_id=explanation.rule_id,
                severity=explanation.severity,
                risk_summary=explanation.risk_summary,
                technical_explanation=explanation.technical_explanation,
                business_impact=explanation.business_impact,
                terraform_fix=explanation.terraform_fix,
                cloudformation_fix=explanation.cloudformation_fix,
                best_practice=explanation.best_practice,
                references=explanation.references,
            )
            for explanation in explanations
        ]
    )
