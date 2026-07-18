"""Streamlit dashboard for the Enterprise Security Guardrail Auditor."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from typing import Any

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
PROJECT_VERSION = "1.0.0"

st.set_page_config(
    page_title="Enterprise Security Guardrail Auditor", page_icon="🛡️", layout="wide"
)


@st.cache_data(show_spinner=False)
def get_rules_count() -> int:
    """Return the number of active rules exposed by the backend for the sidebar summary."""
    return 4


def get_api_status() -> str:
    """Return a simple health indicator for the backend API."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=3)
        return "Online" if response.ok else "Offline"
    except requests.RequestException:
        return "Offline"


def get_sqlite_status() -> str:
    """Return a simple connectivity indicator for the local SQLite database."""
    try:
        connection = sqlite3.connect("app/infrastructure/db/guardrail_auditor.db")
        connection.execute("SELECT 1")
        connection.close()
        return "Connected"
    except sqlite3.Error:
        return "Unavailable"


def calculate_risk_score(findings: list[dict[str, Any]]) -> tuple[int, str]:
    """Calculate a lightweight overall score and risk tier from the current findings."""
    if not findings:
        return 0, "LOW"

    weights = {"CRITICAL": 40, "HIGH": 20, "MEDIUM": 10, "LOW": 5}
    total = sum(
        weights.get(finding.get("severity", "").upper(), 0) for finding in findings
    )
    normalized = min(100, round((total / max(1, len(findings) * 40)) * 100))

    if normalized >= 75:
        level = "CRITICAL"
    elif normalized >= 50:
        level = "HIGH"
    elif normalized >= 25:
        level = "MEDIUM"
    else:
        level = "LOW"

    return normalized, level


def call_api(
    path: str,
    payload: dict[str, Any] | None = None,
    files: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call the backend API and raise a user-friendly error for failed requests."""
    try:
        if files is not None:
            response = requests.post(f"{API_BASE_URL}{path}", files=files, timeout=10)
        else:
            response = requests.post(
                f"{API_BASE_URL}{path}", json=payload or {}, timeout=10
            )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")
        return {}


def render_sidebar() -> None:
    """Render the dashboard sidebar with high-level status information."""
    st.sidebar.title("Enterprise Security Guardrail Auditor")
    st.sidebar.caption("Security posture review from IaC templates")
    st.sidebar.metric("Project Version", PROJECT_VERSION)
    st.sidebar.metric("Framework", "FastAPI + Streamlit")
    st.sidebar.metric("FastAPI Status", get_api_status())
    st.sidebar.metric("SQLite Status", get_sqlite_status())
    st.sidebar.metric("Loaded Rules", get_rules_count())
    st.sidebar.metric("Dashboard Status", "Active")
    st.sidebar.caption(
        f"Current Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )


def render_upload_section() -> dict[str, Any] | None:
    """Render the upload UI and return parsed results when available."""
    st.header("A. Upload Template")
    uploaded_file = st.file_uploader(
        "Upload a Terraform (.tf) or CloudFormation template (.yaml/.yml/.json)",
        type=["tf", "yaml", "yml", "json"],
        accept_multiple_files=False,
    )

    if uploaded_file is None:
        return None

    if st.button("Parse Template"):
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type or "application/octet-stream",
            )
        }
        payload = call_api("/uploads/parse", files=files)
        if not payload:
            return None

        st.success("Template parsed successfully")
        return payload

    return None


def render_risk_score(findings: list[dict[str, Any]]) -> None:
    """Render a summary risk score card near the top of the dashboard."""
    score, level = calculate_risk_score(findings)
    color = {
        "LOW": "#28a745",
        "MEDIUM": "#f1c40f",
        "HIGH": "#f0ad4e",
        "CRITICAL": "#d9534f",
    }.get(level, "#6c757d")

    st.markdown(
        f"<div style='padding:14px;border:2px solid {color};border-radius:8px;background-color:#f8f9fa;margin-bottom:16px;'>"
        f"<h3 style='margin:0;color:{color};'>Risk Score: {score} / 100</h3>"
        f"<p style='margin:4px 0 0 0;'><strong>Overall Risk:</strong> {level}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_parsing_summary(parsed_payload: dict[str, Any] | None) -> None:
    """Render the parsing summary section."""
    st.header("B. Parsing Summary")
    if not parsed_payload:
        st.info("Upload a template and parse it to see the resource inventory.")
        return

    resources = parsed_payload.get("resources", [])
    number_of_resources = len(resources)
    resource_types = sorted(
        {resource.get("resource_type", "unknown") for resource in resources}
    )
    providers = sorted({resource.get("provider", "unknown") for resource in resources})

    col1, col2, col3 = st.columns(3)
    col1.metric("Resources", number_of_resources)
    col2.metric(
        "Resource Types", ", ".join(resource_types) if resource_types else "None"
    )
    col3.metric("Providers", ", ".join(providers) if providers else "None")

    if resources:
        st.dataframe(resources, use_container_width=True)


def render_findings_section(
    parsed_payload: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Render findings from the scan endpoint and return the list of findings."""
    st.header("C. Security Findings")
    if not parsed_payload:
        st.info("No parsed resources available yet.")
        return []

    resources = parsed_payload.get("resources", [])
    if not resources:
        st.info("The uploaded template did not yield any normalized resources.")
        return []

    scan_payload = {"resources": resources}
    scan_response = call_api("/scan", scan_payload)
    findings = scan_response.get("findings", [])

    if not findings:
        st.success("No security findings were detected for the uploaded template.")
        return findings

    severity_colors = {
        "CRITICAL": "#d9534f",
        "HIGH": "#f0ad4e",
        "MEDIUM": "#f1c40f",
        "LOW": "#5cb85c",
    }

    rows = []
    for finding in findings:
        severity = finding.get("severity", "").upper()
        color = severity_colors.get(severity, "#6c757d")
        rows.append(
            f"<tr><td>{finding.get('rule_id', '')}</td><td><span style='color:{color};font-weight:bold;'>{severity}</span></td>"
            f"<td>{finding.get('resource_id', '')}</td><td>{finding.get('status', '')}</td><td>{finding.get('message', '')}</td></tr>"
        )

    st.markdown(
        "<table style='width:100%;border-collapse:collapse;'><thead><tr>"
        "<th style='text-align:left;border-bottom:1px solid #ddd;padding:6px;'>Rule ID</th>"
        "<th style='text-align:left;border-bottom:1px solid #ddd;padding:6px;'>Severity</th>"
        "<th style='text-align:left;border-bottom:1px solid #ddd;padding:6px;'>Resource</th>"
        "<th style='text-align:left;border-bottom:1px solid #ddd;padding:6px;'>Status</th>"
        "<th style='text-align:left;border-bottom:1px solid #ddd;padding:6px;'>Message</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>",
        unsafe_allow_html=True,
    )

    return findings


def render_explanation_section(findings: list[dict[str, Any]]) -> None:
    """Render the AI explanation section for the selected finding."""
    st.header("D. AI Explanation")
    if not findings:
        st.info("No findings are available to explain yet.")
        return

    selected_rule_id = st.selectbox(
        "Select a finding", [finding.get("rule_id", "") for finding in findings]
    )
    selected_finding = next(
        (finding for finding in findings if finding.get("rule_id") == selected_rule_id),
        None,
    )
    if not selected_finding:
        return

    explain_payload = {"findings": [selected_finding]}
    explain_response = call_api("/explain", explain_payload)
    if not explain_response:
        return

    explanation = explain_response.get("explanations", [{}])[0]
    st.subheader(selected_finding.get("rule_id", ""))
    st.write("**Risk Summary**")
    st.write(explanation.get("risk_summary", ""))
    st.write("**Technical Explanation**")
    st.write(explanation.get("technical_explanation", ""))
    st.write("**Business Impact**")
    st.write(explanation.get("business_impact", ""))
    st.write("**Terraform Remediation Example**")
    st.write(explanation.get("terraform_fix", ""))
    st.write("**CloudFormation Remediation Example**")
    st.write(explanation.get("cloudformation_fix", ""))
    st.write("**Security Best Practice**")
    st.write(explanation.get("best_practice", ""))
    st.write("**References**")
    for reference in explanation.get("references", []):
        st.write(f"- {reference}")


def main() -> None:
    """Render the full dashboard application."""
    render_sidebar()
    parsed_payload = render_upload_section()
    render_risk_score([] if parsed_payload is None else [])
    render_parsing_summary(parsed_payload)
    findings = render_findings_section(parsed_payload)
    render_risk_score(findings)
    render_explanation_section(findings)


if __name__ == "__main__":
    main()
