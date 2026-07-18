"""AWS-specific security rules for the rule engine."""

from __future__ import annotations

from typing import Any

from app.domain.models.finding import Finding
from app.domain.models.ingestion import NormalizedResource
from app.domain.rules.base import BaseRule


class S3PublicReadRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            rule_id="S3-001",
            rule_name="S3 bucket allows public read",
            description="S3 buckets should not grant public read access.",
            severity="HIGH",
            cloud_provider="aws",
            resource_types=("aws_s3_bucket",),
        )

    def _evaluate(self, resource: NormalizedResource) -> Finding | None:
        acl = str(resource.attributes.get("acl", "")).strip().lower()
        if acl in {"public-read", "public-read-write"}:
            return Finding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                severity=self.severity,
                status="FAILED",
                resource_id=resource.resource_name,
                resource_type=resource.resource_type,
                message="S3 bucket grants public read or public read/write access.",
                remediation="Set the bucket ACL to private and enforce bucket policies that restrict access.",
            )
        return None


class S3EncryptionDisabledRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            rule_id="S3-002",
            rule_name="S3 bucket encryption disabled",
            description="S3 buckets should enforce server-side encryption.",
            severity="HIGH",
            cloud_provider="aws",
            resource_types=("aws_s3_bucket",),
        )

    def _evaluate(self, resource: NormalizedResource) -> Finding | None:
        attrs = resource.attributes or {}
        encryption_config = attrs.get(
            "server_side_encryption_configuration"
        ) or attrs.get("bucket_encryption")
        if encryption_config is None:
            return Finding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                severity=self.severity,
                status="FAILED",
                resource_id=resource.resource_name,
                resource_type=resource.resource_type,
                message="S3 bucket does not define server-side encryption configuration.",
                remediation="Enable default server-side encryption for the bucket.",
            )
        return None


class SecurityGroupOpenToInternetRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            rule_id="SG-001",
            rule_name="Security group exposes a privileged port to the internet",
            description="Security groups should not expose SSH or RDP to 0.0.0.0/0.",
            severity="CRITICAL",
            cloud_provider="aws",
            resource_types=("aws_security_group", "AWS::EC2::SecurityGroup"),
        )

    def _evaluate(self, resource: NormalizedResource) -> Finding | None:
        for ingress in self._iter_ingress_entries(resource.attributes):
            from_port = ingress.get("from_port")
            to_port = ingress.get("to_port")
            cidr_blocks = ingress.get("cidr_blocks") or []
            cidr_ip = ingress.get("cidr_ip") or ingress.get("CidrIp")
            if cidr_ip is not None:
                cidr_blocks = [cidr_ip]

            if self._is_privileged_port(from_port, to_port) and self._is_open_to_world(
                cidr_blocks
            ):
                return Finding(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    severity=self.severity,
                    status="FAILED",
                    resource_id=resource.resource_name,
                    resource_type=resource.resource_type,
                    message="Security group allows SSH or RDP from the internet.",
                    remediation="Restrict ingress to trusted CIDR ranges and remove public access.",
                )
        return None

    def _iter_ingress_entries(self, attributes: dict[str, Any]) -> list[dict[str, Any]]:
        for key in ("ingress", "SecurityGroupIngress", "IpPermissions"):
            value = attributes.get(key)
            if isinstance(value, list):
                return [entry for entry in value if isinstance(entry, dict)]
        return []

    def _is_privileged_port(self, from_port: Any, to_port: Any) -> bool:
        if from_port is None or to_port is None:
            return False
        try:
            from_value = int(from_port)
            to_value = int(to_port)
        except (TypeError, ValueError):
            return False
        return (
            from_value == 22
            and to_value == 22
            or from_value == 3389
            and to_value == 3389
        )

    def _is_open_to_world(self, cidr_blocks: list[Any]) -> bool:
        return any(str(cidr).strip() == "0.0.0.0/0" for cidr in cidr_blocks)


class MissingEc2TagsRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            rule_id="EC2-001",
            rule_name="EC2 instance is missing tags",
            description="EC2 instances should include tags for ownership and environment.",
            severity="MEDIUM",
            cloud_provider="aws",
            resource_types=("aws_instance", "AWS::EC2::Instance"),
        )

    def _evaluate(self, resource: NormalizedResource) -> Finding | None:
        attrs = resource.attributes or {}
        tags = attrs.get("tags") or attrs.get("Tags") or {}
        if not isinstance(tags, dict) or not tags:
            return Finding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                severity=self.severity,
                status="FAILED",
                resource_id=resource.resource_name,
                resource_type=resource.resource_type,
                message="EC2 instance does not define any tags.",
                remediation="Add required tags such as Environment and Owner.",
            )
        return None


def build_default_rules() -> list[BaseRule]:
    return [
        S3PublicReadRule(),
        S3EncryptionDisabledRule(),
        SecurityGroupOpenToInternetRule(),
        MissingEc2TagsRule(),
    ]
