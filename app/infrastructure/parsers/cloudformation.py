"""CloudFormation parser implementation for YAML and JSON templates."""

from __future__ import annotations

import json

import yaml

from app.core.exceptions import ParsingError
from app.domain.models.ingestion import NormalizedResource
from app.infrastructure.parsers.base import BaseParser


class CloudFormationParser(BaseParser):
    """Parse CloudFormation YAML and JSON templates into normalized resources."""

    @classmethod
    def supported_extensions(cls) -> tuple[str, ...]:
        return (".yaml", ".yml", ".json")

    def parse(self, content: bytes, filename: str) -> list[NormalizedResource]:
        """Parse the supplied bytes into normalized resources."""
        if not content.strip():
            raise ParsingError("CloudFormation template content is empty")

        try:
            if filename.lower().endswith((".yaml", ".yml")):
                payload = yaml.safe_load(content.decode("utf-8"))
            else:
                payload = json.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, ValueError, yaml.YAMLError) as exc:
            raise ParsingError("CloudFormation template is malformed") from exc

        if not isinstance(payload, dict):
            raise ParsingError("CloudFormation template must be a mapping")

        resources_payload = payload.get("Resources")
        if not isinstance(resources_payload, dict):
            raise ParsingError("CloudFormation template is missing Resources")

        resources: list[NormalizedResource] = []
        for name, definition in resources_payload.items():
            if not isinstance(definition, dict):
                continue
            resource_type = str(definition.get("Type", "Unknown"))
            properties = definition.get("Properties") or {}
            resources.append(
                NormalizedResource(
                    resource_type=resource_type,
                    resource_name=str(name),
                    provider=(
                        resource_type.split("::", 1)[0].lower()
                        if "::" in resource_type
                        else "cloudformation"
                    ),
                    attributes=self._normalize_attributes(properties),
                )
            )
        return resources
