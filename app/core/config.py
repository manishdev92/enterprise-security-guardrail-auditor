"""Application configuration and environment loading for the backend service."""

from __future__ import annotations

import os

from pydantic import BaseModel, ConfigDict, Field


class Settings(BaseModel):
    """Central application configuration with environment override support."""

    model_config = ConfigDict(extra="ignore")

    app_name: str = Field(default="Enterprise Security Guardrail Auditor")
    app_version: str = Field(default="0.1.0")
    app_environment: str = Field(default="development")
    debug: bool = Field(default=False)
    database_url: str = Field(default="sqlite:///./app.db")
    log_level: str = Field(default="INFO")
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    upload_dir: str = Field(default="/tmp/guardrail-auditor/uploads")
    max_upload_size_bytes: int = Field(default=5 * 1024 * 1024)
    openapi_title: str = Field(default="Enterprise Security Guardrail Auditor API")
    openapi_description: str = Field(
        default="API-first platform for auditing Terraform and CloudFormation security guardrails."
    )
    contact_name: str = Field(default="Platform Engineering")
    contact_email: str = Field(default="platform@example.com")

    @classmethod
    def from_env(cls) -> "Settings":
        """Build settings from environment variables with sensible defaults."""
        cors_origins_raw = os.getenv("CORS_ORIGINS", "*")
        cors_origins = [
            item.strip() for item in cors_origins_raw.split(",") if item.strip()
        ]

        return cls(
            app_name=os.getenv("APP_NAME", cls.model_fields["app_name"].default),
            app_version=os.getenv(
                "APP_VERSION", cls.model_fields["app_version"].default
            ),
            app_environment=os.getenv(
                "APP_ENV", cls.model_fields["app_environment"].default
            ),
            debug=os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"},
            database_url=os.getenv(
                "DATABASE_URL", cls.model_fields["database_url"].default
            ),
            log_level=os.getenv(
                "LOG_LEVEL", cls.model_fields["log_level"].default
            ).upper(),
            cors_origins=cors_origins or ["*"],
            upload_dir=os.getenv("UPLOAD_DIR", cls.model_fields["upload_dir"].default),
            max_upload_size_bytes=int(
                os.getenv(
                    "MAX_UPLOAD_SIZE_BYTES",
                    str(cls.model_fields["max_upload_size_bytes"].default),
                )
            ),
            openapi_title=os.getenv(
                "OPENAPI_TITLE", cls.model_fields["openapi_title"].default
            ),
            openapi_description=os.getenv(
                "OPENAPI_DESCRIPTION", cls.model_fields["openapi_description"].default
            ),
            contact_name=os.getenv(
                "CONTACT_NAME", cls.model_fields["contact_name"].default
            ),
            contact_email=os.getenv(
                "CONTACT_EMAIL", cls.model_fields["contact_email"].default
            ),
        )


settings = Settings.from_env()


def get_settings() -> Settings:
    """Return the shared settings instance for dependency injection."""
    return settings
