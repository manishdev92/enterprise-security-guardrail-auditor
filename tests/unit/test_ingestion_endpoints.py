from fastapi.testclient import TestClient

from app.core.config import settings as app_settings
from app.main import create_app


def _make_client(tmp_path):
    app_settings.upload_dir = str(tmp_path / "uploads")
    app_settings.max_upload_size_bytes = 5 * 1024 * 1024
    return TestClient(create_app())


def test_upload_and_parse_successful_terraform(tmp_path) -> None:
    client = _make_client(tmp_path)
    payload = b'resource "aws_s3_bucket" "example" { bucket = "demo-bucket" }'

    response = client.post(
        "/uploads/parse",
        files={"file": ("example.tf", payload, "text/plain")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "example.tf"
    assert body["resource_count"] == 1
    assert body["resources"][0]["resource_type"] == "aws_s3_bucket"
    assert body["resources"][0]["resource_name"] == "example"


def test_upload_rejects_unsupported_file_type(tmp_path) -> None:
    client = _make_client(tmp_path)

    response = client.post(
        "/uploads/parse",
        files={"file": ("notes.txt", b"not an IaC template", "text/plain")},
    )

    assert response.status_code == 400
    assert "unsupported" in response.json()["detail"].lower()


def test_upload_rejects_empty_file(tmp_path) -> None:
    client = _make_client(tmp_path)

    response = client.post(
        "/uploads/parse",
        files={"file": ("empty.tf", b"", "application/octet-stream")},
    )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_rejects_malformed_template(tmp_path) -> None:
    client = _make_client(tmp_path)
    payload = b'resource "aws_s3_bucket" "example" { bucket = "demo"'

    response = client.post(
        "/uploads/parse",
        files={"file": ("bad.tf", payload, "text/plain")},
    )

    assert response.status_code == 400
    assert "parse" in response.json()["detail"].lower()


def test_upload_stores_file_and_returns_metadata(tmp_path) -> None:
    client = _make_client(tmp_path)
    payload = b"Resources:\n  ExampleBucket:\n    Type: AWS::S3::Bucket\n"

    response = client.post(
        "/uploads",
        files={"file": ("template.yaml", payload, "application/x-yaml")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "template.yaml"
    assert body["stored"] is True
    assert body["size_bytes"] == len(payload)
