"""Terraform parser implementation for .tf and Terraform plan JSON files."""

from __future__ import annotations

import json
import re
from typing import Any

from app.core.exceptions import ParsingError
from app.domain.models.ingestion import NormalizedResource
from app.infrastructure.parsers.base import BaseParser


class TerraformParser(BaseParser):
    """Parse Terraform configuration and Terraform plan JSON into normalized resources."""

    @classmethod
    def supported_extensions(cls) -> tuple[str, ...]:
        return (".tf", ".json")

    def parse(self, content: bytes, filename: str) -> list[NormalizedResource]:
        """Parse the supplied bytes into normalized resources."""
        if not content.strip():
            raise ParsingError("Terraform template content is empty")

        if filename.lower().endswith(".json"):
            return self._parse_plan_json(content)

        return self._parse_hcl(content)

    def _parse_hcl(self, content: bytes) -> list[NormalizedResource]:
        text = content.decode("utf-8")
        resources: list[NormalizedResource] = []
        current_type: str | None = None
        current_name: str | None = None
        current_attributes: list[str] = []
        brace_depth = 0
        in_resource_block = False

        lines = text.splitlines()
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("//"):
                continue

            if not in_resource_block:
                match = re.match(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{', stripped)
                if match:
                    current_type = match.group(1)
                    current_name = match.group(2)
                    in_resource_block = True
                    brace_depth = stripped.count("{") - stripped.count("}")
                    current_attributes = []
                    if brace_depth <= 0:
                        resources.append(
                            NormalizedResource(
                                resource_type=current_type,
                                resource_name=current_name,
                                provider=current_type.split("_", 1)[0],
                                attributes={},
                            )
                        )
                        current_type = None
                        current_name = None
                        current_attributes = []
                        in_resource_block = False
                    continue
                continue

            brace_depth += stripped.count("{") - stripped.count("}")
            current_attributes.append(line)
            if brace_depth <= 0:
                if current_type and current_name:
                    attributes = self._parse_attributes(current_attributes)
                    resources.append(
                        NormalizedResource(
                            resource_type=current_type,
                            resource_name=current_name,
                            provider=current_type.split("_", 1)[0],
                            attributes=attributes,
                        )
                    )
                current_type = None
                current_name = None
                current_attributes = []
                in_resource_block = False

        if in_resource_block:
            raise ParsingError("Terraform resource block is malformed")

        return resources

    def _parse_attributes(self, block_lines: list[str]) -> dict[str, Any]:
        attributes: dict[str, Any] = {}
        for line in block_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("//"):
                continue
            if "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"')
            attributes[key] = value
        return attributes

    def _parse_plan_json(self, content: bytes) -> list[NormalizedResource]:
        try:
            payload = json.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ParsingError("Terraform plan JSON is malformed") from exc

        resource_changes = payload.get("resource_changes")
        if not isinstance(resource_changes, list):
            raise ParsingError("Terraform plan JSON is missing resource_changes")

        resources: list[NormalizedResource] = []
        for item in resource_changes:
            if not isinstance(item, dict):
                continue
            address = str(item.get("address", "unknown"))
            resource_type = str(item.get("type") or address.split(".")[-1])
            resource_name = address.split(".")[-1] if "." in address else address
            change = item.get("change", {})
            attributes = change.get("after", {}) if isinstance(change, dict) else {}
            resources.append(
                NormalizedResource(
                    resource_type=resource_type,
                    resource_name=resource_name,
                    provider=(
                        resource_type.split("_", 1)[0]
                        if "_" in resource_type
                        else "terraform"
                    ),
                    attributes=self._normalize_attributes(attributes),
                )
            )
        return resources
