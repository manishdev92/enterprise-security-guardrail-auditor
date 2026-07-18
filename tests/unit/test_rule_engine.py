from fastapi.testclient import TestClient

from app.main import create_app


def test_scan_returns_no_findings_for_secure_resources() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "resources": [
            {
                "resource_type": "aws_s3_bucket",
                "resource_name": "secure-bucket",
                "provider": "aws",
                "attributes": {
                    "acl": "private",
                    "server_side_encryption_configuration": {
                        "rule": {
                            "apply_server_side_encryption_by_default": {
                                "sse_algorithm": "AES256"
                            }
                        }
                    },
                },
            },
            {
                "resource_type": "aws_instance",
                "resource_name": "web-server",
                "provider": "aws",
                "attributes": {
                    "tags": {"Environment": "prod"},
                },
            },
        ]
    }

    response = client.post("/scan", json=payload)

    assert response.status_code == 200
    assert response.json()["findings"] == []


def test_scan_returns_findings_for_failing_resources() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "resources": [
            {
                "resource_type": "aws_s3_bucket",
                "resource_name": "public-bucket",
                "provider": "aws",
                "attributes": {"acl": "public-read"},
            },
            {
                "resource_type": "aws_security_group",
                "resource_name": "web-sg",
                "provider": "aws",
                "attributes": {
                    "ingress": [
                        {"from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]}
                    ]
                },
            },
        ]
    }

    response = client.post("/scan", json=payload)

    assert response.status_code == 200
    findings = response.json()["findings"]
    assert len(findings) == 3
    assert findings[0]["status"] == "FAILED"
    assert findings[0]["severity"] in {"HIGH", "CRITICAL"}


def test_scan_returns_multiple_findings_for_multiple_violations() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "resources": [
            {
                "resource_type": "aws_s3_bucket",
                "resource_name": "bucket-one",
                "provider": "aws",
                "attributes": {"acl": "public-read-write"},
            },
            {
                "resource_type": "aws_security_group",
                "resource_name": "db-sg",
                "provider": "aws",
                "attributes": {
                    "ingress": [
                        {
                            "from_port": 3389,
                            "to_port": 3389,
                            "cidr_blocks": ["0.0.0.0/0"],
                        }
                    ]
                },
            },
            {
                "resource_type": "aws_instance",
                "resource_name": "missing-tags",
                "provider": "aws",
                "attributes": {},
            },
        ]
    }

    response = client.post("/scan", json=payload)

    assert response.status_code == 200
    findings = response.json()["findings"]
    assert len(findings) == 4


def test_scan_returns_empty_findings_for_empty_resource_list() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post("/scan", json={"resources": []})

    assert response.status_code == 200
    assert response.json()["findings"] == []
