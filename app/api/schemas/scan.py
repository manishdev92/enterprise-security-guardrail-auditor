"""Request and response schemas for security scanning."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ScanResourceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resource_type: str
    resource_name: str
    provider: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class ScanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resources: list[ScanResourceRequest]


class FindingResponse(BaseModel):
    rule_id: str
    rule_name: str
    severity: str
    status: str
    resource_id: str
    resource_type: str
    message: str
    remediation: str


class ScanResponse(BaseModel):
    findings: list[FindingResponse]
