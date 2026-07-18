"""Factory for selecting the appropriate parser for uploaded IaC files."""

from __future__ import annotations

from pathlib import Path

from app.core.exceptions import ParsingError, UploadError
from app.infrastructure.parsers.base import BaseParser
from app.infrastructure.parsers.cloudformation import CloudFormationParser
from app.infrastructure.parsers.terraform import TerraformParser


class ParserFactory:
    """Select a parser based on the uploaded filename and content."""

    def __init__(self) -> None:
        self._parsers: list[BaseParser] = [TerraformParser(), CloudFormationParser()]

    def get_parser(self, filename: str, content: bytes | None = None) -> BaseParser:
        """Return the parser that best matches the supplied file."""
        suffix = Path(filename).suffix.lower()
        if suffix in {".tf"}:
            return TerraformParser()
        if suffix in {".yaml", ".yml"}:
            return CloudFormationParser()
        if suffix == ".json":
            if content is None:
                return TerraformParser()
            try:
                decoded = content.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ParsingError("Uploaded JSON is not valid UTF-8") from exc
            if "resource_changes" in decoded:
                return TerraformParser()
            return CloudFormationParser()

        raise UploadError("Unsupported file type")
