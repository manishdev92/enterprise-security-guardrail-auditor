"""Security scanning routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.schemas.scan import FindingResponse, ScanRequest, ScanResponse
from app.domain.models.ingestion import NormalizedResource
from app.domain.rules.engine import RuleEngine

router = APIRouter(tags=["scans"])


def get_rule_engine() -> RuleEngine:
    return RuleEngine()


@router.post("/scan", response_model=ScanResponse)
def scan_resources(
    request: ScanRequest,
    engine: Annotated[RuleEngine, Depends(get_rule_engine)],
) -> ScanResponse:
    normalized_resources = [
        NormalizedResource(
            resource_type=item.resource_type,
            resource_name=item.resource_name,
            provider=item.provider,
            attributes=item.attributes,
        )
        for item in request.resources
    ]
    findings = engine.evaluate_resources(normalized_resources)

    return ScanResponse(
        findings=[
            FindingResponse(
                rule_id=finding.rule_id,
                rule_name=finding.rule_name,
                severity=finding.severity,
                status=finding.status,
                resource_id=finding.resource_id,
                resource_type=finding.resource_type,
                message=finding.message,
                remediation=finding.remediation,
            )
            for finding in findings
        ]
    )
