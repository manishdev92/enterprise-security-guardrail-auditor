"""Offline, deterministic AI provider implementation for security explanations."""

from __future__ import annotations

from app.domain.ai.base import BaseAIProvider
from app.domain.ai.explanation import AIExplanation
from app.domain.models.finding import Finding


class MockAIProvider(BaseAIProvider):
    """Provides deterministic, offline security explanations for known rule IDs."""

    def generate_explanation(
        self, finding: Finding, prompt: str | None = None
    ) -> AIExplanation:
        """Generate a deterministic explanation for a known rule or a generic fallback response."""
        if finding.rule_id == "S3-001":
            return AIExplanation(
                rule_id=finding.rule_id,
                severity=finding.severity,
                risk_summary="Public read access on an S3 bucket exposes sensitive objects to unauthorized users and materially increases the chance of data leakage, reputational damage, and policy violations.",
                technical_explanation="The bucket ACL or bucket policy grants anonymous or broadly scoped read permissions. This bypasses the intended least-privilege access model and may allow public enumeration of stored content.",
                business_impact="An exposed bucket can lead to information disclosure, compliance exceptions, and downstream customer trust issues that affect operations and brand reputation.",
                terraform_fix='resource "aws_s3_bucket" "secure" {\n  acl = "private"\n  bucket = "example-secure-bucket"\n}\n\nresource "aws_s3_bucket_public_access_block" "secure" {\n  bucket = aws_s3_bucket.secure.id\n  block_public_acls = true\n  block_public_policy = true\n  ignore_public_acls = true\n  restrict_public_buckets = true\n}',
                cloudformation_fix="Resources:\n  SecureBucket:\n    Type: AWS::S3::Bucket\n    Properties:\n      AccessControl: Private\n      PublicAccessBlockConfiguration:\n        BlockPublicAcls: true\n        BlockPublicPolicy: true\n        IgnorePublicAcls: true\n        RestrictPublicBuckets: true",
                best_practice="Keep S3 buckets private by default, enforce public access blocking, and review bucket policies and ACLs during every change window.",
                references=[
                    "AWS S3 Security Best Practices",
                    "CIS Amazon Web Services Foundations Benchmark",
                ],
            )

        if finding.rule_id == "SG-001":
            return AIExplanation(
                rule_id=finding.rule_id,
                severity=finding.severity,
                risk_summary="Allowing SSH or RDP from 0.0.0.0/0 exposes privileged management services directly to the internet and significantly expands the attack surface.",
                technical_explanation="The ingress rule permits inbound traffic from any source address to well-known administrative ports, making brute-force and credential-stuffing attacks more feasible.",
                business_impact="Publicly exposed administrative services increase the likelihood of compromise, which can result in operational disruption and potential data loss.",
                terraform_fix='resource "aws_security_group" "admin" {\n  ingress {\n    from_port   = 22\n    to_port     = 22\n    protocol    = "tcp"\n    cidr_blocks = ["10.0.0.0/24"]\n  }\n}',
                cloudformation_fix="Resources:\n  AdminSecurityGroup:\n    Type: AWS::EC2::SecurityGroup\n    Properties:\n      SecurityGroupIngress:\n        - IpProtocol: tcp\n          FromPort: 22\n          ToPort: 22\n          CidrIp: 10.0.0.0/24",
                best_practice="Restrict administrative access to trusted internal ranges or VPN-connected addresses, and remove world-open rules from production environments.",
                references=[
                    "AWS Security Group Best Practices",
                    "CIS Amazon Web Services Foundations Benchmark",
                ],
            )

        if finding.rule_id == "EC2-001":
            return AIExplanation(
                rule_id=finding.rule_id,
                severity=finding.severity,
                risk_summary="Missing tags on EC2 instances reduce visibility, governance, and accountability across the environment, especially during incident response and cost review.",
                technical_explanation="The instance lacks operational metadata that helps teams determine ownership, environment, and lifecycle state. This makes automation and policy enforcement more difficult.",
                business_impact="Untagged resources increase the effort required for audits, owner identification, incident response, and proper cost allocation.",
                terraform_fix='resource "aws_instance" "app" {\n  ami           = "ami-123456"\n  instance_type = "t3.micro"\n\n  tags = {\n    Environment = "prod"\n    Owner       = "platform-team"\n    Project     = "guardrail-auditor"\n  }\n}',
                cloudformation_fix="Resources:\n  AppInstance:\n    Type: AWS::EC2::Instance\n    Properties:\n      Tags:\n        - Key: Environment\n          Value: prod\n        - Key: Owner\n          Value: platform-team\n        - Key: Project\n          Value: guardrail-auditor",
                best_practice="Adopt a consistent tagging standard for ownership, environment, cost center, and lifecycle so that governance controls remain enforceable.",
                references=[
                    "AWS Tagging Best Practices",
                    "CIS Amazon Web Services Foundations Benchmark",
                ],
            )

        return AIExplanation(
            rule_id=finding.rule_id,
            severity=finding.severity,
            risk_summary="Generic explanation: this finding highlights a control gap that should be reviewed and remediated according to the organization’s baseline security posture.",
            technical_explanation="The deployed configuration does not meet the expected security standards. The remediation should align with the intended access model, network controls, and least-privilege requirements.",
            business_impact="Unaddressed findings can increase the likelihood of unauthorized access, non-compliance, or operational disruption.",
            terraform_fix="Review the Terraform resource definition and apply the required security hardening change to the affected configuration.",
            cloudformation_fix="Review the CloudFormation template and update the insecure resource property to align with the recommended security posture.",
            best_practice="Use least-privilege access, enforce encryption, and reduce the attack surface wherever possible.",
            references=["AWS Security Best Practices", "CIS Benchmarks"],
        )
