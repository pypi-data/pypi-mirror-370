"""
File attachment models for the Expert Panel system.

This module provides models and utilities for handling file attachments
in agent-expert-panel discussions.
"""

from enum import Enum
from pathlib import Path
from typing import Optional, Any
from pydantic import BaseModel, Field, validator


class FileType(Enum):
    """Supported file types for attachments."""

    TEXT = "text"
    MARKDOWN = "markdown"
    CSV = "csv"
    JSON = "json"
    PDF = "pdf"
    YAML = "yaml"
    PYTHON = "python"
    XML = "xml"
    HTML = "html"


class FileAttachment(BaseModel):
    """Model representing a file attachment."""

    file_path: Path = Field(..., description="Path to the attached file")
    filename: str = Field(..., description="Original filename")
    file_type: FileType = Field(..., description="Type of the attached file")
    file_size: int = Field(..., description="File size in bytes")
    content: Optional[str] = Field(
        None, description="Processed text content of the file"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional file metadata"
    )

    @validator("file_path")
    def validate_file_exists(cls, v, values):
        """Validate that the file exists."""
        # Skip validation if explicitly disabled for testing
        if hasattr(cls, "_skip_file_validation") and cls._skip_file_validation:
            return v
        if not v.exists():
            raise ValueError(f"File does not exist: {v}")
        if not v.is_file():
            raise ValueError(f"Path is not a file: {v}")
        return v

    @validator("file_size")
    def validate_file_size(cls, v):
        """Validate file size limits."""
        max_size = 50 * 1024 * 1024  # 50MB limit
        if v > max_size:
            raise ValueError(
                f"File size {v} bytes exceeds maximum allowed size of {max_size} bytes"
            )
        return v

    @classmethod
    def from_path(cls, file_path: Path | str) -> "FileAttachment":
        """Create a FileAttachment from a file path."""
        path = Path(file_path)

        # Determine file type from extension
        file_type = cls._detect_file_type(path)
        file_size = path.stat().st_size

        return cls(
            file_path=path,
            filename=path.name,
            file_type=file_type,
            file_size=file_size,
            metadata={
                "extension": path.suffix.lower(),
                "created_at": path.stat().st_ctime,
                "modified_at": path.stat().st_mtime,
            },
        )

    @staticmethod
    def _detect_file_type(path: Path) -> FileType:
        """Detect file type from file extension."""
        extension = path.suffix.lower()

        type_mapping = {
            ".txt": FileType.TEXT,
            ".md": FileType.MARKDOWN,
            ".markdown": FileType.MARKDOWN,
            ".csv": FileType.CSV,
            ".json": FileType.JSON,
            ".pdf": FileType.PDF,
            ".yaml": FileType.YAML,
            ".yml": FileType.YAML,
            ".py": FileType.PYTHON,
            ".xml": FileType.XML,
            ".html": FileType.HTML,
            ".htm": FileType.HTML,
        }

        return type_mapping.get(extension, FileType.TEXT)

    def get_content_preview(self, max_chars: int = 500) -> str:
        """Get a preview of the file content."""
        if not self.content:
            return f"[File: {self.filename} ({self.file_type.value}, {self.file_size} bytes)]"

        if len(self.content) <= max_chars:
            return self.content

        return (
            self.content[:max_chars]
            + f"... [truncated, full content: {len(self.content)} chars]"
        )


class AttachedMessage(BaseModel):
    """Model representing a message with file attachments."""

    content: str = Field(..., description="The text content of the message")
    attachments: list[FileAttachment] = Field(
        default_factory=list, description="List of attached files"
    )
    source: str = Field(
        ..., description="Source of the message (user, agent name, etc.)"
    )

    def get_full_content(self, include_file_content: bool = True) -> str:
        """Get the full message content including file attachments."""
        full_content = self.content

        if self.attachments:
            full_content += "\n\n--- Attached Files ---\n"

            for attachment in self.attachments:
                full_content += f"\n**File: {attachment.filename}** ({attachment.file_type.value})\n"

                if include_file_content and attachment.content:
                    full_content += f"```\n{attachment.content}\n```\n"
                else:
                    full_content += f"[File size: {attachment.file_size} bytes]\n"

        return full_content

    def has_attachments(self) -> bool:
        """Check if the message has any attachments."""
        return len(self.attachments) > 0

    def get_attachment_summary(self) -> str:
        """Get a summary of all attachments."""
        if not self.attachments:
            return "No attachments"

        summaries = []
        for attachment in self.attachments:
            summaries.append(f"{attachment.filename} ({attachment.file_type.value})")

        return f"{len(self.attachments)} file(s): {', '.join(summaries)}"


class FileProcessingError(Exception):
    """Exception raised when file processing fails."""

    def __init__(
        self, file_path: Path, message: str, original_error: Optional[Exception] = None
    ):
        self.file_path = file_path
        self.original_error = original_error
        super().__init__(f"Error processing file {file_path}: {message}")
