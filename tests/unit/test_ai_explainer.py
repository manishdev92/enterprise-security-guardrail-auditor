from fastapi.testclient import TestClient

from app.api.dependencies.container import get_ai_explainer, get_ai_provider
from app.main import create_app


def test_explain_endpoint_returns_single_explanation() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "findings": [
            {
                "rule_id": "S3-001",
                "rule_name": "S3 bucket allows public read",
                "severity": "HIGH",
                "status": "FAILED",
                "resource_id": "public-bucket",
                "resource_type": "aws_s3_bucket",
                "message": "S3 bucket grants public read or public read/write access.",
                "remediation": "Set the bucket ACL to private.",
            }
        ]
    }

    response = client.post("/explain", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert len(body["explanations"]) == 1
    explanation = body["explanations"][0]
    assert explanation["rule_id"] == "S3-001"
    assert explanation["risk_summary"]
    assert explanation["technical_explanation"]
    assert explanation["business_impact"]
    assert explanation["terraform_fix"]
    assert explanation["cloudformation_fix"]
    assert explanation["best_practice"]
    assert explanation["references"]


def test_explain_endpoint_returns_multiple_explanations() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "findings": [
            {
                "rule_id": "S3-001",
                "rule_name": "S3 bucket allows public read",
                "severity": "HIGH",
                "status": "FAILED",
                "resource_id": "public-bucket",
                "resource_type": "aws_s3_bucket",
                "message": "S3 bucket grants public read or public read/write access.",
                "remediation": "Set the bucket ACL to private.",
            },
            {
                "rule_id": "SG-001",
                "rule_name": "Security group exposes a privileged port to the internet",
                "severity": "CRITICAL",
                "status": "FAILED",
                "resource_id": "web-sg",
                "resource_type": "aws_security_group",
                "message": "Security group allows SSH or RDP from the internet.",
                "remediation": "Restrict ingress to trusted CIDR ranges.",
            },
        ]
    }

    response = client.post("/explain", json=payload)

    assert response.status_code == 200
    assert len(response.json()["explanations"]) == 2


def test_explain_endpoint_returns_empty_list_for_empty_input() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post("/explain", json={"findings": []})

    assert response.status_code == 200
    assert response.json()["explanations"] == []


def test_explain_endpoint_returns_generic_explanation_for_unsupported_rule() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "findings": [
            {
                "rule_id": "CUSTOM-999",
                "rule_name": "Custom rule",
                "severity": "MEDIUM",
                "status": "FAILED",
                "resource_id": "custom",
                "resource_type": "aws_s3_bucket",
                "message": "Custom message",
                "remediation": "Review the resource configuration.",
            }
        ]
    }

    response = client.post("/explain", json=payload)

    assert response.status_code == 200
    explanation = response.json()["explanations"][0]
    assert explanation["rule_id"] == "CUSTOM-999"
    assert "generic" in explanation["risk_summary"].lower()


def test_dependency_injection_provides_provider_and_explainer() -> None:
    provider = get_ai_provider()
    explainer = get_ai_explainer(provider)

    assert provider is not None
    assert explainer is not None
