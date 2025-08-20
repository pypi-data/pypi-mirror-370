"""
CLI utilities for handling file attachments.

This module provides CLI-specific utilities for handling file attachments
in the agent-expert-panel system.
"""

from pathlib import Path
from typing import Optional, Callable

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel as RichPanel

from ..models.file_attachment import (
    FileAttachment,
    AttachedMessage,
    FileProcessingError,
)
from ..tools.file_processor import (
    process_file_attachment,
    get_supported_extensions,
    is_supported_file,
)


class FileAttachmentCLI:
    """CLI handler for file attachments."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def process_file_arguments(self, files: list[str] | None) -> list[FileAttachment]:
        """
        Process file arguments from CLI and return FileAttachment objects.

        Args:
            files: List of file paths from CLI arguments

        Returns:
            List of processed FileAttachment objects

        Raises:
            FileProcessingError: If any file processing fails
        """
        if not files:
            return []

        attachments = []

        for file_path_str in files:
            file_path = Path(file_path_str)

            # Validate file exists
            if not file_path.exists():
                self.console.print(f"[red]Error: File not found: {file_path}[/red]")
                continue

            # Validate file type
            if not is_supported_file(file_path):
                self.console.print(
                    f"[yellow]Warning: Unsupported file type: {file_path}[/yellow]"
                )
                self.console.print(
                    f"Supported extensions: {', '.join(get_supported_extensions())}"
                )

                if not Confirm.ask(
                    f"Attempt to process {file_path.name} as text file?", default=False
                ):
                    continue

            try:
                # Process the file
                self.console.print(f"[dim]Processing file: {file_path.name}...[/dim]")
                attachment = process_file_attachment(file_path)
                attachments.append(attachment)
                self.console.print(f"[green]✓ Processed: {file_path.name}[/green]")

            except FileProcessingError as e:
                self.console.print(f"[red]Error processing {file_path.name}: {e}[/red]")
                continue
            except PermissionError as e:
                self.console.print(
                    f"[red]Permission denied accessing {file_path.name}: {e}[/red]"
                )
                continue

        return attachments

    def interactive_file_selection(self) -> list[FileAttachment]:
        """
        Interactive file selection for CLI users.

        Returns:
            List of selected and processed FileAttachment objects
        """
        if not Confirm.ask(
            "Would you like to attach files to your message?", default=False
        ):
            return []

        attachments = []

        self.console.print("\n[bold]File Attachment Options:[/bold]")
        self.console.print("1. Enter file path(s) manually")
        self.console.print("2. Browse current directory")
        self.console.print("3. Skip file attachments")

        choice = Prompt.ask("Choose option", choices=["1", "2", "3"], default="1")

        if choice == "1":
            attachments = self._manual_file_input()
        elif choice == "2":
            attachments = self._browse_directory()
        else:
            return []

        if attachments:
            self._display_attachment_summary(attachments)

        return attachments

    def _manual_file_input(self) -> list[FileAttachment]:
        """Handle manual file path input."""
        attachments = []

        self.console.print(
            f"\n[dim]Supported file types: {', '.join(get_supported_extensions())}[/dim]"
        )

        while True:
            file_path_str = Prompt.ask(
                "Enter file path (or 'done' to finish)", default="done"
            )

            if file_path_str.lower() == "done":
                break

            file_path = Path(file_path_str).expanduser().resolve()

            if not file_path.exists():
                self.console.print(f"[red]File not found: {file_path}[/red]")
                continue

            if not file_path.is_file():
                self.console.print(f"[red]Not a file: {file_path}[/red]")
                continue

        if attachments:
            self._display_attachment_summary(attachments)

        return attachments

    def _manual_file_input(self) -> list[FileAttachment]:
        """Handle manual file path input."""
        attachments = []

        self.console.print(
            f"\n[dim]Supported file types: {', '.join(get_supported_extensions())}[/dim]"
        )

        while True:
            file_path_str = Prompt.ask(
                "Enter file path (or 'done' to finish)", default="done"
            )

            if file_path_str.lower() == "done":
                break

            file_path = Path(file_path_str).expanduser().resolve()

            if not file_path.exists():
                self.console.print(f"[red]File not found: {file_path}[/red]")
                continue

            if not file_path.is_file():
                self.console.print(f"[red]Not a file: {file_path}[/red]")
                continue

            try:
                attachment = process_file_attachment(file_path)
                attachments.append(attachment)
                self.console.print(f"[green]✓ Added: {attachment.filename}[/green]")

            except FileProcessingError as e:
                self.console.print(f"[red]Error: {e}[/red]")
                continue

        return attachments

    def _browse_directory(self) -> list[FileAttachment]:
        """Browse current directory for file selection."""
        current_dir = Path.cwd()
        supported_files = []
        # Find supported files in current directory
        for file_path in current_dir.iterdir():
            if file_path.is_file() and is_supported_file(file_path):
                supported_files.append(file_path)

        if not supported_files:
            self.console.print(
                "[yellow]No supported files found in current directory.[/yellow]"
            )
            return []

        # Display files in a table
        table = Table(title=f"Supported Files in {current_dir.name}")
        table.add_column("#", style="cyan")
        table.add_column("Filename", style="green")
        table.add_column("Size", style="white")
        table.add_column("Type", style="yellow")

        for i, file_path in enumerate(supported_files, 1):
            file_size = file_path.stat().st_size
            size_str = self._format_file_size(file_size)
            file_type = file_path.suffix.lower() or "no extension"

            table.add_row(str(i), file_path.name, size_str, file_type)

        self.console.print(table)

        # Let user select files
        attachments = []
        while True:
            choice = Prompt.ask(
                f"Select file number (1-{len(supported_files)}) or 'done' to finish",
                default="done",
            )

            if choice.lower() == "done":
                break

            try:
                file_index = int(choice) - 1
                if 0 <= file_index < len(supported_files):
                    file_path = supported_files[file_index]

                    # Check if already selected
                    if any(att.file_path == file_path for att in attachments):
                        self.console.print(
                            f"[yellow]File already selected: {file_path.name}[/yellow]"
                        )
                        continue

                    try:
                        attachment = process_file_attachment(file_path)
                        attachments.append(attachment)
                        self.console.print(
                            f"[green]✓ Added: {attachment.filename}[/green]"
                        )

                    except FileProcessingError as e:
                        self.console.print(
                            f"[red]Error processing {file_path.name}: {e}[/red]"
                        )
                        continue

                else:
                    self.console.print(
                        f"[red]Invalid selection. Choose 1-{len(supported_files)}[/red]"
                    )

            except ValueError:
                self.console.print("[red]Invalid input. Enter a number or 'done'[/red]")

        return attachments

    def _display_attachment_summary(self, attachments: list[FileAttachment]) -> None:
        """Display a summary of selected attachments."""
        if not attachments:
            return

        self.console.print(
            f"\n[bold green]Selected {len(attachments)} file(s):[/bold green]"
        )

        total_size = 0
        for attachment in attachments:
            size_str = self._format_file_size(attachment.file_size)
            total_size += attachment.file_size
            preview = attachment.get_content_preview(100)
            preview_lines = preview.count("\n") + 1

            self.console.print(
                f"  • {attachment.filename} ({attachment.file_type.value}, {size_str}, ~{preview_lines} lines)"
            )

        total_size_str = self._format_file_size(total_size)
        self.console.print(f"[dim]Total size: {total_size_str}[/dim]")

    def create_attached_message(
        self, content: str, attachments: list[FileAttachment], source: str = "user"
    ) -> AttachedMessage:
        """

        Create an AttachedMessage from content and attachments.

        Args:
            content: The text content of the message
            attachments: List of file attachments
            source: Message source identifier

        Returns:
            AttachedMessage object
        """

        return AttachedMessage(content=content, attachments=attachments, source=source)

    def display_message_preview(self, message: AttachedMessage) -> None:
        """Display a preview of the message with attachments."""
        if not message.has_attachments():
            return

        # Show attachment summary
        summary = message.get_attachment_summary()
        self.console.print(
            f"\n[bold blue]Message with attachments:[/bold blue] {summary}"
        )

        # Show content preview
        preview_content = message.get_full_content(include_file_content=False)
        if len(preview_content) > 500:
            preview_content = preview_content[:500] + "..."

        panel = RichPanel(preview_content, title="Message Preview", border_style="blue")
        self.console.print(panel)

    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def create_file_attachment_input_func(
    attachments: list[FileAttachment], console: Optional[Console] = None
) -> Callable[[str], str]:
    """
    Create a custom input function that includes file attachments.

    This function can be used as the human_input_func in panel discussions
    to include file attachments in human responses.

    Args:
        attachments: List of file attachments to include
        console: Optional console for output

    Returns:
        Custom input function that includes file content
    """
    console = console or Console()

    def attachment_input_func(prompt: str) -> str:
        """Custom input function that includes file attachments."""
        # Display the prompt
        console.print(f"\n[bold yellow]{prompt}[/bold yellow]")

        # Show attachment info
        if attachments:
            console.print(
                f"[dim]Available attachments: {len(attachments)} file(s)[/dim]"
            )
            for attachment in attachments:
                console.print(
                    f"  - {attachment.filename} ({attachment.file_type.value})"
                )

        # Get user input
        response = input("\nYour response: ")

        # Create attached message and return full content
        attached_message = AttachedMessage(
            content=response, attachments=attachments, source="human"
        )

        return attached_message.get_full_content()

    return attachment_input_func
