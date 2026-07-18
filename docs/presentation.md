# Enterprise Security Guardrail Auditor
## Graduate Vibe Coding Challenge Presentation

---

## Slide 1 — Project Title
- Project Title: Enterprise Security Guardrail Auditor
- Graduate Vibe Coding Challenge
- Candidate Name: [Insert Candidate Name]
- Project Overview: An API-first platform for auditing Infrastructure-as-Code templates and surfacing actionable security findings

> Speaker notes: This presentation summarizes the implemented solution for the challenge and highlights how the project moves from upload to remediation guidance in a structured workflow.

---

## Slide 2 — Challenge Statement
- Problem being solved: Security risks in Infrastructure-as-Code templates are often hard to identify quickly and consistently.
- Objective: Provide a practical, local-first workflow to review Terraform and CloudFormation templates for common security weaknesses.
- Outcome: Convert uploaded templates into normalized resources, evaluate them with a rule engine, and provide deterministic security guidance.

> Speaker notes: The project focuses on making security review more accessible by turning IaC templates into browsable findings and actionable recommendations.

---

## Slide 3 — Solution Architecture
- Clean Architecture structure across API, domain, infrastructure, and UI layers
- API-first design with FastAPI routes and schema-driven request handling
- Separation of concerns between ingestion, rule evaluation, explanation, and dashboard presentation
- Implementation references: app/main.py, app/api, app/domain, app/infrastructure, app/ui

> Speaker notes: The architecture was designed to remain modular and extensible while keeping the implementation focused on the challenge requirements.

---

## Slide 4 — Technology Stack
- Python as the primary implementation language
- FastAPI for the backend API layer
- Streamlit for the interactive dashboard
- SQLite and SQLAlchemy for local persistence
- Pydantic for request and response validation
- Pytest for regression testing
- Black and Ruff for formatting and linting
- GitHub Copilot as the AI-assisted development partner

> Speaker notes: The stack was selected to support rapid development, local testing, and a clear demonstration of the end-to-end workflow.

---

## Slide 5 — End-to-End Workflow
- Upload: Accept Terraform and CloudFormation templates
- Parse: Normalize resources into structured objects
- Rule Engine: Evaluate resources against security rules
- AI Explanation: Generate deterministic remediation guidance
- Dashboard: Present findings and explanations in a simple UI

> Speaker notes: The solution follows a straightforward flow from input to insight, making the project easy to understand and demonstrate.

---

## Slide 6 — Key Features
- Terraform and CloudFormation support
- Security rule engine for common misconfigurations
- AI-powered explanation and remediation guidance
- Risk score visualization in the dashboard
- OpenAPI documentation for the API
- Local Streamlit experience for interactive review

> Speaker notes: The implemented features directly match the project scope and provide a complete proof of concept for the challenge.

---

## Slide 7 — REST APIs
- Health endpoints: /health and /ready
- Upload and parse: /uploads/parse
- Scan endpoint: /scan
- Explanation endpoint: /explain
- OpenAPI docs available at /docs and /redoc
- Screenshot placeholder: openapi-screenshot.png

> Speaker notes: The API layer exposes a small but complete surface area for the end-to-end review experience and is documented through FastAPI.

---

## Slide 8 — Dashboard Experience
- Parsing summary with resource counts and provider details
- Security findings table with severity and status
- Risk score panel for a quick security overview
- AI explanation panel for remediation guidance
- Screenshot placeholders:
  - dashboard-home.png
  - dashboard-risk-score.png
  - dashboard-findings.png
  - dashboard-ai-explanation.png

> Speaker notes: The dashboard was built to make findings easy to review visually without requiring direct interaction with the API.

---

## Slide 9 — Testing and Quality
- Regression tests implemented with Pytest
- Black used for formatting consistency
- Ruff used for linting and cleanup
- Clean Architecture applied throughout the implementation
- AI explanations remain deterministic and offline

> Speaker notes: Quality was treated as a core requirement, and the project was validated through automated checks and structural review.

---

## Slide 10 — Vibe Coding Workflow
- Lead Architect
- GitHub Copilot
- Implementation
- Review
- Testing
- Prompt Audit

> Speaker notes: The workflow followed a collaborative AI-assisted pattern in which the lead architect defined requirements, GitHub Copilot generated the implementation, and the project was reviewed and tested before submission. No manual code edits were intentionally performed, and the prompt history is captured in prompts.md.

---

## Slide 11 — Future Enhancements
- Expand coverage to Azure and GCP resources
- Integrate a real LLM provider while preserving the abstraction
- Add authentication and user management
- Introduce scan history and persisted reports
- Generate PDF reports for review and sharing

> Speaker notes: The current implementation is a strong foundation for further expansion, particularly for enterprise environments and richer reporting workflows.

---

## Slide 12 — Conclusion
- Built a complete local-first security auditing workflow for IaC templates
- Delivered backend APIs, parsing, rule evaluation, structured explanation, and a dashboard
- Kept the architecture modular, testable, and aligned to the challenge scope
- Thank you

> Speaker notes: The project demonstrates a practical and polished implementation that is ready for review and submission.
