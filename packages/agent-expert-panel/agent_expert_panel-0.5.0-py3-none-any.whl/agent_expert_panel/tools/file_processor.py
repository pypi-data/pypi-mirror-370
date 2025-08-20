"""
File processing tools for handling file attachments.

This module provides tools to read and process different file types,
converting them to text content for use in agent discussions.
"""

import json
import csv
import logging
from pathlib import Path
import yaml

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from ..models.file_attachment import FileAttachment, FileType, FileProcessingError


logger = logging.getLogger(__name__)


class FileProcessor:
    """Main file processor that handles different file types."""

    @staticmethod
    def process_file(file_attachment: FileAttachment) -> FileAttachment:
        """
        Process a file attachment and extract its text content.

        Args:
            file_attachment: The file attachment to process

        Returns:
            FileAttachment with populated content field

        Raises:
            FileProcessingError: If file processing fails
        """
        try:
            content = FileProcessor._extract_content(file_attachment)
            file_attachment.content = content
            return file_attachment
        except Exception as e:
            raise FileProcessingError(
                file_attachment.file_path,
                f"Failed to process {file_attachment.file_type.value} file",
                e,
            )

    @staticmethod
    def _extract_content(file_attachment: FileAttachment) -> str:
        """Extract text content based on file type."""
        file_type = file_attachment.file_type
        file_path = file_attachment.file_path
        if file_type == FileType.TEXT:
            return FileProcessor._read_text_file(file_path)
        elif file_type == FileType.MARKDOWN:
            return FileProcessor._read_text_file(file_path)
        elif file_type == FileType.CSV:
            return FileProcessor._read_csv_file(file_path)
        elif file_type == FileType.JSON:
            return FileProcessor._read_json_file(file_path)
        elif file_type == FileType.PDF:
            return FileProcessor._read_pdf_file(file_path)
        elif file_type == FileType.YAML:
            return FileProcessor._read_yaml_file(file_path)
        elif file_type == FileType.PYTHON:
            return FileProcessor._read_text_file(file_path)
        elif file_type == FileType.XML:
            return FileProcessor._read_text_file(file_path)
        elif file_type == FileType.HTML:
            return FileProcessor._read_text_file(file_path)
        else:
            # Fallback to text reading
            return FileProcessor._read_text_file(file_path)

    @staticmethod
    def _read_text_file(file_path: Path) -> str:
        """Read a plain text file."""
        # Try multiple encodings
        encodings = ["utf-8", "utf-16", "latin-1", "ascii"]

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except UnicodeError:
                # This includes UTF-16 BOM errors and other Unicode-related issues
                continue
            except Exception as e:
                # If we get a non-encoding error (like FileNotFoundError),
                # don't try other encodings
                raise FileProcessingError(file_path, f"Failed to read text file: {e}")

        # If all encodings fail, read as binary and replace invalid chars
        try:
            with open(file_path, "rb") as f:
                content = f.read()
                return content.decode("utf-8", errors="replace")
        except Exception as e:
            raise FileProcessingError(file_path, f"Failed to read text file: {e}")

    @staticmethod
    def _read_csv_file(file_path: Path) -> str:
        """Read a CSV file and convert to formatted text."""
        try:
            content_lines = []
            with open(file_path, "r", encoding="utf-8", newline="") as f:
                # Try to detect delimiter
                sample = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                try:
                    delimiter = sniffer.sniff(sample).delimiter
                except csv.Error:
                    delimiter = ","

                reader = csv.reader(f, delimiter=delimiter)

                # Read and format rows
                rows = list(reader)
                if not rows:
                    return "Empty CSV file"

                # Add header
                content_lines.append(f"CSV File: {file_path.name}")
                content_lines.append(
                    f"Rows: {len(rows)}, Columns: {len(rows[0]) if rows else 0}"
                )

                content_lines.append("")

                # Add column headers
                if rows:
                    headers = rows[0]
                    content_lines.append("| " + " | ".join(headers) + " |")
                    content_lines.append(
                        "| " + " | ".join(["---"] * len(headers)) + " |"
                    )

                    # Add data rows (limit to first 10 for readability)
                    for i, row in enumerate(rows[1:11], 1):
                        # Pad row to match header length
                        padded_row = row + [""] * (len(headers) - len(row))
                        content_lines.append(
                            "| " + " | ".join(padded_row[: len(headers)]) + " |"
                        )

                    if len(rows) > 11:
                        content_lines.append(f"... and {len(rows) - 11} more rows")

                return "\n".join(content_lines)

        except Exception as e:
            raise FileProcessingError(file_path, f"Failed to read CSV file: {e}")

    @staticmethod
    def _read_json_file(file_path: Path) -> str:
        """Read a JSON file and convert to formatted text."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Pretty format the JSON
            formatted_json = json.dumps(data, indent=2, ensure_ascii=False)

            return f"JSON File: {file_path.name}\n\n{formatted_json}"

        except json.JSONDecodeError as e:
            raise FileProcessingError(file_path, f"Invalid JSON format: {e}")
        except Exception as e:
            raise FileProcessingError(file_path, f"Failed to read JSON file: {e}")

    @staticmethod
    def _read_pdf_file(file_path: Path) -> str:
        """Read a PDF file and extract text."""
        if not pdfplumber and not PyPDF2:
            raise FileProcessingError(
                file_path,
                "PDF support not available. Install pdfplumber or PyPDF2: pip install pdfplumber",
            )

        try:
            # Try pdfplumber first (better text extraction)
            if pdfplumber:
                return FileProcessor._read_pdf_with_pdfplumber(file_path)
            else:
                return FileProcessor._read_pdf_with_pypdf2(file_path)
        except Exception as e:
            raise FileProcessingError(file_path, f"Failed to read PDF file: {e}")

    @staticmethod
    def _read_pdf_with_pdfplumber(file_path: Path) -> str:
        """Read PDF using pdfplumber."""

        content_lines = [f"PDF File: {file_path.name}\n"]
        with pdfplumber.open(file_path) as pdf:
            content_lines.append(f"Pages: {len(pdf.pages)}\n")

            for i, page in enumerate(pdf.pages[:10], 1):  # Limit to first 10 pages
                text = page.extract_text()
                if text:
                    content_lines.append(f"--- Page {i} ---")
                    content_lines.append(text.strip())
                    content_lines.append("")

            if len(pdf.pages) > 10:
                content_lines.append(f"... and {len(pdf.pages) - 10} more pages")

        return "\n".join(content_lines)

    @staticmethod
    def _read_pdf_with_pypdf2(file_path: Path) -> str:
        """Read PDF using PyPDF2 (fallback)."""
        content_lines = [f"PDF File: {file_path.name}\n"]

        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            content_lines.append(f"Pages: {len(reader.pages)}\n")
            for i, page in enumerate(reader.pages[:10], 1):  # Limit to first 10 pages
                text = page.extract_text()
                if text:
                    content_lines.append(f"--- Page {i} ---")
                    content_lines.append(text.strip())
                    content_lines.append("")

            if len(reader.pages) > 10:
                content_lines.append(f"... and {len(reader.pages) - 10} more pages")

        return "\n".join(content_lines)

    @staticmethod
    def _read_yaml_file(file_path: Path) -> str:
        """Read a YAML file and convert to formatted text."""
        if not yaml:
            raise FileProcessingError(
                file_path,
                "YAML support not available. Install PyYAML: pip install PyYAML",
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Convert to formatted YAML
            formatted_yaml = yaml.dump(data, default_flow_style=False, indent=2)

            return f"YAML File: {file_path.name}\n\n{formatted_yaml}"

        except yaml.YAMLError as e:
            raise FileProcessingError(file_path, f"Invalid YAML format: {e}")
        except Exception as e:
            raise FileProcessingError(file_path, f"Failed to read YAML file: {e}")


def process_file_attachment(file_path: str | Path) -> FileAttachment:
    """
    Convenience function to create and process a file attachment.

    Args:
        file_path: Path to the file to attach

    Returns:
        Processed FileAttachment with content

    Raises:
        FileProcessingError: If file processing fails
    """
    attachment = FileAttachment.from_path(file_path)
    return FileProcessor.process_file(attachment)


def get_supported_extensions() -> list[str]:
    """Get list of supported file extensions."""
    return [
        ".txt",
        ".md",
        ".markdown",
        ".csv",
        ".json",
        ".yaml",
        ".yml",
        ".py",
        ".xml",
        ".html",
        ".htm",
        ".pdf",
    ]


def is_supported_file(file_path: Path | str) -> bool:
    """Check if a file is supported for attachment."""
    path = Path(file_path)
    return path.suffix.lower() in get_supported_extensions()
