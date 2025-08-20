#!/usr/bin/env python3
"""
Agent Expert Panel - Main CLI Interface

Run multi-agent expert panel discussions from the command line.
Inspired by Microsoft's MAI-DxO and Hugging Face's Consilium.
"""

import asyncio
import logging
import os
import yaml
from pathlib import Path
from typing import Optional
from enum import Enum
from datetime import datetime

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel as RichPanel
from rich.markdown import Markdown

from agent_expert_panel.panel import ExpertPanel
from agent_expert_panel.virtual_panel import VirtualExpertPanel
from agent_expert_panel.models import DiscussionPattern, APIKeyError, AgentConfig
from agent_expert_panel.models.virtual_panel import VirtualPanelResult
from agent_expert_panel.models.file_attachment import FileProcessingError
from agent_expert_panel.utils.file_attachment_cli import (
    FileAttachmentCLI,
    create_file_attachment_input_func,
)
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken


logger = logging.getLogger(__name__)


# Create the main Typer app
app = typer.Typer(
    name="agent-panel",
    help="🧠 Agent Expert Panel - Multi-agent discussion system",
    epilog="""
Examples:

  🎯 Interactive mode (includes option for human participation):
  $ agent-panel

  🤖 Batch mode:
  $ agent-panel discuss "Should we adopt microservices architecture?" --pattern round-robin --rounds 3

  👥 Batch mode with human participation:
  $ agent-panel discuss "Product roadmap planning" --pattern structured-debate --rounds 2 --with-human

  🧠 Virtual Expert Panel mode (Microsoft MAI-DxO inspired):
  $ agent-panel virtual-solve "How can we improve our customer retention?"
  
  🎯 With automatic domain inference (analyzes your query):
  $ agent-panel virtual-solve "Should we migrate to microservices?"

  ⚙️ With custom config directory:
  $ agent-panel discuss "AI ethics in healthcare" --config-dir ./my-configs

  📋 List available agents:
  $ agent-panel list-agents

  ℹ️ Show agent details:
  $ agent-panel show-agent advocate
    """,
    rich_markup_mode="rich",
    no_args_is_help=False,  # Allow running without args for interactive mode
)


class DiscussionPatternEnum(str, Enum):
    """Discussion patterns available for the panel."""

    round_robin = "round-robin"
    structured_debate = "structured-debate"
    open_floor = "open-floor"


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    # Check for DEBUG environment variable
    debug_mode = os.getenv("DEBUG", "").lower() in ("true", "1", "yes", "on")

    # Set basic logging level
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Suppress verbose autogen logs unless in debug mode
    if not debug_mode:
        # Set autogen loggers to WARNING level to reduce noise
        logging.getLogger("autogen_core.events").setLevel(logging.WARNING)
        logging.getLogger("autogen_core").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)

        # Only show our application logs and errors/warnings from dependencies
        logging.getLogger("agent_expert_panel").setLevel(level)


def display_welcome() -> None:
    """Display welcome message and panel overview."""
    console = Console()

    welcome_text = """
    # 🧠 Agent Expert Panel

    Welcome to the multi-agent expert panel discussion system!

    **Your Expert Panel consists of:**
    - 🥊 **Advocate**: Champions ideas with conviction and evidence
    - 🔍 **Critic**: Rigorous quality assurance and risk analysis
    - ⚡ **Pragmatist**: Practical implementation focus
    - 📚 **Research Specialist**: Fact-finding and evidence gathering
    - 💡 **Innovator**: Creative disruption and breakthrough solutions

    These AI experts will collaborate to provide comprehensive insights on your topics.
    """

    console.print(
        RichPanel(Markdown(welcome_text), title="Welcome", border_style="blue")
    )


def display_agents(panel: ExpertPanel) -> None:
    """Display information about available agents."""
    console = Console()

    table = Table(title="Available Experts")
    table.add_column("Expert", style="cyan")
    table.add_column("Role", style="green")
    table.add_column("Description", style="white")

    descriptions = panel.get_agent_descriptions()

    roles = {
        "advocate": "🥊 Champion",
        "critic": "🔍 Quality Assurance",
        "pragmatist": "⚡ Implementation",
        "research_specialist": "📚 Research & Evidence",
        "innovator": "💡 Creative Disruption",
    }

    for agent_name, description in descriptions.items():
        role = roles.get(agent_name, "Expert")
        table.add_row(
            agent_name.title(),
            role,
            description[:80] + "..." if len(description) > 80 else description,
        )

    console.print(table)


async def interactive_mode() -> int:
    """Run in interactive mode with prompts."""
    console = Console()
    display_welcome()

    try:
        # Initialize the panel (no model overrides in interactive mode for now)
        console.print("\n[yellow]Initializing expert panel...[/yellow]")
        panel = ExpertPanel()
        console.print("[green]✓ Expert panel ready![/green]\n")

        # Show available agents
        if Confirm.ask("Would you like to see the expert panel details?", default=True):
            display_agents(panel)
            console.print()

        while True:
            # Get topic from user
            topic = Prompt.ask(
                "\n[bold cyan]What topic would you like the experts to discuss?[/bold cyan]"
            )

            if topic.lower() in ["quit", "exit", "q"]:
                break

            # Handle file attachments
            file_cli = FileAttachmentCLI(console)
            file_attachments = file_cli.interactive_file_selection()

            # Create enhanced topic with file content
            enhanced_topic = topic
            if file_attachments:
                from agent_expert_panel.models.file_attachment import AttachedMessage

                attached_msg = AttachedMessage(
                    content=topic, attachments=file_attachments, source="user"
                )
                enhanced_topic = attached_msg.get_full_content()

            # Choose discussion pattern
            console.print("\n[yellow]Available discussion patterns:[/yellow]")
            patterns = list(DiscussionPattern)
            for i, pattern in enumerate(patterns, 1):
                console.print(f"  {i}. {pattern.value.replace('_', ' ').title()}")

            pattern_choice = Prompt.ask(
                "Choose discussion pattern",
                choices=[str(i) for i in range(1, len(patterns) + 1)],
                default="1",
            )
            selected_pattern = patterns[int(pattern_choice) - 1]

            # Get max rounds
            max_rounds = int(Prompt.ask("Maximum discussion rounds", default="3"))

            # Ask if human wants to participate
            include_human = Confirm.ask(
                "Would you like to participate in the discussion as a human expert?",
                default=False,
            )

            # Run discussion
            if include_human:
                display_message = (
                    selected_pattern.value.replace("_", " ")
                    + " discussion with human participation"
                )
                if file_attachments:
                    display_message += f" ({len(file_attachments)} file(s) attached)"

                console.print(f"\n[green]Starting {display_message}...[/green]\n")
                console.print(
                    "[yellow]You will be prompted for input during your turns in the discussion.[/yellow]\n"
                )

                # Create custom input function that includes file attachments for human responses
                human_input_func = None
                if file_attachments:
                    human_input_func = create_file_attachment_input_func(
                        file_attachments, console
                    )
                    console.print(
                        "[dim]Note: Attached files will be available in your responses[/dim]\n"
                    )

                result = await panel.discuss(
                    topic=enhanced_topic,
                    pattern=selected_pattern,
                    max_rounds=max_rounds,
                    with_human=True,
                    human_name="Human Expert",
                    human_input_func=human_input_func,
                )
            else:
                display_message = (
                    selected_pattern.value.replace("_", " ") + " discussion"
                )
                if file_attachments:
                    display_message += f" ({len(file_attachments)} file(s) attached)"

                console.print(f"\n[green]Starting {display_message}...[/green]\n")

                result = await panel.discuss(
                    topic=enhanced_topic,
                    pattern=selected_pattern,
                    max_rounds=max_rounds,
                )

            # Display results
            console.print(
                RichPanel(
                    f"[bold]Topic:[/bold] {result.topic}\n"
                    f"[bold]Pattern:[/bold] {result.discussion_pattern.value}\n"
                    f"[bold]Participants:[/bold] {', '.join(result.agents_participated)}\n"
                    f"[bold]Rounds:[/bold] {result.total_rounds}\n"
                    f"[bold]Consensus:[/bold] {'✓ Yes' if result.consensus_reached else '✗ No'}\n\n"
                    f"[bold]Final Recommendation:[/bold]\n{result.final_recommendation}",
                    title="Discussion Results",
                    border_style="green",
                )
            )

            if not Confirm.ask(
                "\nWould you like to discuss another topic?", default=True
            ):
                break

    except KeyboardInterrupt:
        console.print("\n[yellow]Discussion interrupted by user.[/yellow]")
        return 1
    except APIKeyError as e:
        console.print(f"\n[red]Configuration Error:[/red]\n{e}")
        console.print(
            "\n[yellow]💡 Quick fix: Run 'agent-panel configure' to set up your API key[/yellow]"
        )
        return 1
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        return 1

    console.print("\n[blue]Thank you for using Agent Expert Panel![/blue]")
    return 0


@app.command()
def discuss(
    topic: str = typer.Argument(..., help="Topic for the expert panel to discuss"),
    pattern: DiscussionPatternEnum = typer.Option(
        DiscussionPatternEnum.round_robin,
        "--pattern",
        "-p",
        help="Discussion pattern to use",
    ),
    rounds: int = typer.Option(
        3, "--rounds", "-r", help="Maximum number of discussion rounds", min=1, max=10
    ),
    config_dir: Optional[Path] = typer.Option(
        None,
        "--config-dir",
        "-c",
        help="Directory containing agent configuration files",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    with_human: bool = typer.Option(
        False,
        "--with-human/--no-human",
        help="Include human participation in the discussion",
    ),
    participants: Optional[list[str]] = typer.Option(
        None,
        "--participants",
        help="Specific agents to include (e.g., --participants advocate --participants critic)",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Save discussion results to a JSON file at the specified path",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    files: Optional[list[str]] = typer.Option(
        None,
        "--file",
        "-f",
        help="Attach files to the discussion topic (e.g., --file data.csv --file prompt.md)",
    ),
    override_model: Optional[str] = typer.Option(
        None,
        "--override-model",
        "-m",
        help="Override the model name for all agents (e.g., 'gpt-4o', 'qwen3:4b')",
    ),
    override_base_url: Optional[str] = typer.Option(
        None,
        "--override-base-url",
        "-b",
        help="Override the OpenAI base URL for all agents (e.g., 'http://localhost:11434/v1')",
    ),
    override_api_key: Optional[str] = typer.Option(
        None,
        "--override-api-key",
        "-k",
        help="Override the OpenAI API key for all agents",
    ),
) -> None:
    """
    🎯 Run a panel discussion on a specific topic.

    This command runs a single discussion in batch mode with the specified parameters.
    Perfect for automation, scripting, or when you know exactly what you want to discuss.
    """

    async def run_discussion():
        console = Console()

        # Setup logging
        setup_logging(verbose)
        logger.debug(f"Starting discussion on topic: {topic}")

        try:
            # Parse pattern
            discussion_pattern = DiscussionPattern(pattern.value.replace("-", "_"))

            # Build model overrides dictionary
            model_overrides = {}
            if override_model:
                model_overrides["model_name"] = override_model
            if override_base_url:
                model_overrides["openai_base_url"] = override_base_url
            if override_api_key:
                model_overrides["openai_api_key"] = override_api_key

            # Initialize panel
            console.print("[yellow]Initializing expert panel...[/yellow]")
            panel = ExpertPanel(config_dir=config_dir, model_overrides=model_overrides)
            console.print("[green]✓ Expert panel ready![/green]\n")

            # Process file attachments if provided
            file_attachments = []
            enhanced_topic = topic

            if files:
                try:
                    console.print("[yellow]Processing file attachments...[/yellow]")
                    file_cli = FileAttachmentCLI(console)
                    file_attachments = file_cli.process_file_arguments(files)

                    if file_attachments:
                        # Create attached message to get enhanced topic with file content
                        from agent_expert_panel.models.file_attachment import (
                            AttachedMessage,
                        )

                        attached_msg = AttachedMessage(
                            content=topic, attachments=file_attachments, source="user"
                        )
                        enhanced_topic = attached_msg.get_full_content()
                        console.print(
                            f"[green]✓ Processed {len(file_attachments)} file(s)[/green]"
                        )

                        # Display attachment summary
                        file_cli._display_attachment_summary(file_attachments)
                    else:
                        console.print(
                            "[yellow]No files were successfully processed[/yellow]"
                        )

                except FileProcessingError as e:
                    console.print(f"[red]File processing error: {e}[/red]")
                    raise typer.Exit(1)

            # Run discussion
            if with_human:
                display_topic = topic
                if file_attachments:
                    display_topic += f" (with {len(file_attachments)} attached file(s))"

                console.print(
                    f"[green]Starting discussion on: {display_topic} (with human participation)[/green]\n"
                )
                console.print(
                    "[yellow]You will be prompted for input during your turns in the discussion.[/yellow]\n"
                )

                # Create custom input function that includes file attachments for human responses
                human_input_func = None
                if file_attachments:
                    human_input_func = create_file_attachment_input_func(
                        file_attachments, console
                    )
                    console.print(
                        "[dim]Note: Attached files will be available in your responses[/dim]\n"
                    )

                result = await panel.discuss(
                    topic=enhanced_topic,
                    pattern=discussion_pattern,
                    max_rounds=rounds,
                    participants=participants,
                    with_human=True,
                    human_name="HumanExpert",
                    human_input_func=human_input_func,
                )
            else:
                display_topic = topic
                if file_attachments:
                    display_topic += f" (with {len(file_attachments)} attached file(s))"

                console.print(
                    f"[green]Starting discussion on: {display_topic}[/green]\n"
                )

                result = await panel.discuss(
                    topic=enhanced_topic,
                    pattern=discussion_pattern,
                    max_rounds=rounds,
                    participants=participants,
                )

            # Output results
            console.print(
                RichPanel(
                    f"[bold]Topic:[/bold] {result.topic}\n"
                    f"[bold]Pattern:[/bold] {result.discussion_pattern.value}\n"
                    f"[bold]Participants:[/bold] {', '.join(result.agents_participated)}\n"
                    f"[bold]Rounds:[/bold] {result.total_rounds}\n"
                    f"[bold]Consensus:[/bold] {'✓ Yes' if result.consensus_reached else '✗ No'}\n\n"
                    f"[bold]Final Recommendation:[/bold]\n{result.final_recommendation}",
                    title="Discussion Results",
                    border_style="green",
                )
            )

            # Save to file if output path specified
            if output:
                from agent_expert_panel.utils.export import DiscussionExporter

                try:
                    DiscussionExporter.to_json(result, output)
                    console.print(
                        f"\n[green]✓ Discussion results saved to: {output}[/green]"
                    )
                except Exception as e:
                    console.print(f"\n[red]✗ Failed to save results: {e}[/red]")

        except APIKeyError as e:
            console.print(f"[red]Configuration Error:[/red]\n{e}")
            console.print(
                "\n[yellow]💡 Quick fix: Run 'agent-panel configure' to set up your API key[/yellow]"
            )
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(run_discussion())


@app.command("list-agents")
def list_agents(
    config_dir: Optional[Path] = typer.Option(
        None,
        "--config-dir",
        "-c",
        help="Directory containing agent configuration files",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    override_model: Optional[str] = typer.Option(
        None,
        "--override-model",
        "-m",
        help="Override the model name for all agents (e.g., 'gpt-4o', 'qwen3:4b')",
    ),
    override_base_url: Optional[str] = typer.Option(
        None,
        "--override-base-url",
        "-b",
        help="Override the OpenAI base URL for all agents (e.g., 'http://localhost:11434/v1')",
    ),
    override_api_key: Optional[str] = typer.Option(
        None,
        "--override-api-key",
        "-k",
        help="Override the OpenAI API key for all agents",
    ),
) -> None:
    """
    📋 List all available expert agents and their roles.

    Shows a detailed table of all expert agents in the panel,
    including their names, roles, and descriptions.
    """
    console = Console()

    # Setup logging
    setup_logging(verbose)

    try:
        # Build model overrides dictionary
        model_overrides = {}
        if override_model:
            model_overrides["model_name"] = override_model
        if override_base_url:
            model_overrides["openai_base_url"] = override_base_url
        if override_api_key:
            model_overrides["openai_api_key"] = override_api_key

        # Initialize panel
        if config_dir:
            console.print(
                f"[yellow]Loading expert panel from custom config directory: {config_dir}[/yellow]"
            )
        else:
            console.print("[yellow]Loading expert panel...[/yellow]")
        panel = ExpertPanel(config_dir=config_dir, model_overrides=model_overrides)
        console.print("[green]✓ Expert panel loaded![/green]\n")

        # Display agents
        display_agents(panel)

    except APIKeyError as e:
        console.print(f"[red]Configuration Error:[/red]\n{e}")
        console.print(
            "\n[yellow]💡 Quick fix: Run 'agent-panel configure' to set up your API key[/yellow]"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error loading agents: {e}[/red]")
        raise typer.Exit(1)


@app.command("show-agent")
def show_agent(
    agent_name: str = typer.Argument(..., help="Name of the agent to show details for"),
    config_dir: Optional[Path] = typer.Option(
        None,
        "--config-dir",
        "-c",
        help="Directory containing agent configuration files",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    override_model: Optional[str] = typer.Option(
        None,
        "--override-model",
        "-m",
        help="Override the model name for all agents (e.g., 'gpt-4o', 'qwen3:4b')",
    ),
    override_base_url: Optional[str] = typer.Option(
        None,
        "--override-base-url",
        "-b",
        help="Override the OpenAI base URL for all agents (e.g., 'http://localhost:11434/v1')",
    ),
    override_api_key: Optional[str] = typer.Option(
        None,
        "--override-api-key",
        "-k",
        help="Override the OpenAI API key for all agents",
    ),
) -> None:
    """
    ℹ️ Show detailed information about a specific expert agent.

    Displays comprehensive details about an agent including its configuration,
    role, and capabilities.
    """
    console = Console()

    # Setup logging
    setup_logging(verbose)

    try:
        # Build model overrides dictionary
        model_overrides = {}
        if override_model:
            model_overrides["model_name"] = override_model
        if override_base_url:
            model_overrides["openai_base_url"] = override_base_url
        if override_api_key:
            model_overrides["openai_api_key"] = override_api_key

        # Initialize panel
        if config_dir:
            console.print(
                f"[yellow]Loading expert panel from custom config directory: {config_dir}[/yellow]"
            )
        else:
            console.print("[yellow]Loading expert panel...[/yellow]")
        panel = ExpertPanel(config_dir=config_dir, model_overrides=model_overrides)

        # Get agent descriptions
        descriptions = panel.get_agent_descriptions()

        if agent_name.lower() not in descriptions:
            available_agents = ", ".join(descriptions.keys())
            console.print(f"[red]Agent '{agent_name}' not found.[/red]")
            console.print(f"[yellow]Available agents: {available_agents}[/yellow]")
            raise typer.Exit(1)

        # Display agent details
        agent_desc = descriptions[agent_name.lower()]

        roles = {
            "advocate": "🥊 Champion",
            "critic": "🔍 Quality Assurance",
            "pragmatist": "⚡ Implementation",
            "research_specialist": "📚 Research & Evidence",
            "innovator": "💡 Creative Disruption",
        }

        role = roles.get(agent_name.lower(), "Expert")

        console.print(
            RichPanel(
                f"[bold]Name:[/bold] {agent_name.title()}\n"
                f"[bold]Role:[/bold] {role}\n\n"
                f"[bold]Description:[/bold]\n{agent_desc}",
                title=f"Agent Details: {agent_name.title()}",
                border_style="cyan",
            )
        )

    except APIKeyError as e:
        console.print(f"[red]Configuration Error:[/red]\n{e}")
        console.print(
            "\n[yellow]💡 Quick fix: Run 'agent-panel configure' to set up your API key[/yellow]"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error loading agent details: {e}[/red]")
        raise typer.Exit(1)


@app.command("quick-consensus")
def quick_consensus(
    question: str = typer.Argument(..., help="Question to get quick consensus on"),
    config_dir: Optional[Path] = typer.Option(
        None,
        "--config-dir",
        "-c",
        help="Directory containing agent configuration files",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Save consensus results to a JSON file at the specified path",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    override_model: Optional[str] = typer.Option(
        None,
        "--override-model",
        "-m",
        help="Override the model name for all agents (e.g., 'gpt-4o', 'qwen3:4b')",
    ),
    override_base_url: Optional[str] = typer.Option(
        None,
        "--override-base-url",
        "-b",
        help="Override the OpenAI base URL for all agents (e.g., 'http://localhost:11434/v1')",
    ),
    override_api_key: Optional[str] = typer.Option(
        None,
        "--override-api-key",
        "-k",
        help="Override the OpenAI API key for all agents",
    ),
) -> None:
    """
    ⚡ Get a quick consensus from all experts on a simple question.

    Runs a single round of discussion to get rapid input from all experts
    on a straightforward question or decision.
    """

    async def run_quick_consensus():
        console = Console()

        # Setup logging
        setup_logging(verbose)

        try:
            # Build model overrides dictionary
            model_overrides = {}
            if override_model:
                model_overrides["model_name"] = override_model
            if override_base_url:
                model_overrides["openai_base_url"] = override_base_url
            if override_api_key:
                model_overrides["openai_api_key"] = override_api_key

            # Initialize panel
            console.print("[yellow]Initializing expert panel...[/yellow]")
            panel = ExpertPanel(config_dir=config_dir, model_overrides=model_overrides)
            console.print("[green]✓ Expert panel ready![/green]\n")

            console.print(f"[green]Getting quick consensus on: {question}[/green]\n")

            # Get consensus (using full discuss method to capture all metadata)
            panel_result = await panel.discuss(
                topic=question, pattern=DiscussionPattern.ROUND_ROBIN, max_rounds=1
            )

            # Display result
            console.print(
                RichPanel(
                    panel_result.final_recommendation,
                    title="Quick Consensus",
                    border_style="green",
                )
            )

            # Save to file if output path specified
            if output:
                from agent_expert_panel.utils.export import DiscussionExporter

                try:
                    DiscussionExporter.to_json(panel_result, output)
                    console.print(
                        f"\n[green]✓ Consensus results saved to: {output}[/green]"
                    )
                except Exception as e:
                    console.print(f"\n[red]✗ Failed to save results: {e}[/red]")

        except APIKeyError as e:
            console.print(f"[red]Configuration Error:[/red]\n{e}")
            console.print(
                "\n[yellow]💡 Quick fix: Run 'agent-panel configure' to set up your API key[/yellow]"
            )
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(run_quick_consensus())


@app.command("configure")
def configure() -> None:
    """
    🔧 Help configure API keys and settings for agent-expert-panel.

    Guides users through setting up their OpenAI API key or local LLM server.
    """
    console = Console()

    # Welcome message
    console.print(
        RichPanel.fit(
            "[bold blue]Agent Expert Panel Configuration[/bold blue]\n\n"
            "This will help you configure API access for your expert panel.",
            border_style="blue",
        )
    )

    console.print("\n[yellow]Choose your setup option:[/yellow]\n")
    console.print("1. Use OpenAI API (requires API key)")
    console.print("2. Use local LLM server (like Ollama)")
    console.print("3. Show current environment variables")
    console.print("4. Exit")

    choice = Prompt.ask(
        "\nEnter your choice", choices=["1", "2", "3", "4"], default="1"
    )

    if choice == "1":
        configure_openai_api(console)
    elif choice == "2":
        configure_local_llm(console)
    elif choice == "3":
        show_current_config(console)
    else:
        console.print("[yellow]Configuration cancelled.[/yellow]")


def configure_openai_api(console: Console) -> None:
    """Configure OpenAI API key."""
    console.print("\n[bold]Setting up OpenAI API[/bold]")
    console.print("You'll need an API key from: https://platform.openai.com/api-keys")

    api_key = Prompt.ask("\nEnter your OpenAI API key", password=True)

    if api_key:
        console.print(
            "\n[green]✓ Add this to your shell profile (~/.bashrc, ~/.zshrc, etc.):[/green]"
        )
        console.print(f"[code]export OPENAI_API_KEY='{api_key}'[/code]")
        console.print("\n[yellow]Then restart your terminal or run:[/yellow]")
        console.print("[code]source ~/.bashrc[/code]  # or ~/.zshrc")

        # Test if it works
        os.environ["OPENAI_API_KEY"] = api_key
        console.print("\n[green]✓ Testing configuration...[/green]")

        _ = ExpertPanel()
        console.print("[green]✓ Configuration successful![/green]")


def configure_local_llm(console: Console) -> None:
    """Configure local LLM server."""
    console.print("\n[bold]Setting up Local LLM Server[/bold]")
    console.print(
        "Popular options: Ollama (http://localhost:11434/v1), LM Studio, etc."
    )

    base_url = Prompt.ask(
        "Enter your LLM server URL", default="http://localhost:11434/v1"
    )

    console.print("\n[green]✓ Add this to your shell profile:[/green]")
    console.print(f"[code]export OPENAI_BASE_URL='{base_url}'[/code]")
    console.print("[code]export OPENAI_API_KEY='dummy-key'[/code]")

    console.print("\n[yellow]Make sure your LLM server is running first![/yellow]")


async def infer_domain_from_query(query: str) -> tuple[str, float]:
    """
    Infer the problem domain from the user's query using AI.

    Args:
        query: The user's problem or question

    Returns:
        Tuple of (inferred_domain, confidence_score)
    """
    try:
        # Create a simple model client for domain inference
        model_client = OpenAIChatCompletionClient(
            model="gpt-4o-mini",
            api_key=None,  # Will use environment variable
        )

        # Create a domain classifier agent
        domain_classifier = AssistantAgent(
            name="domain_classifier",
            model_client=model_client,
            system_message="""
            You are a domain classification expert. Analyze the user's query and determine the most appropriate problem domain.
            
            Available domains:
            - business: Strategy, pricing, market analysis, revenue, growth, partnerships, funding
            - technology: Architecture, infrastructure, engineering, security, platforms, tools, coding
            - product: Features, roadmap, user experience, design, product-market fit, launches
            - finance: Investment, budgeting, financial planning, costs, ROI, accounting
            - operations: Process improvement, efficiency, workflows, team management, scaling
            - marketing: Campaigns, branding, customer acquisition, content, analytics
            - legal: Compliance, contracts, intellectual property, regulations, risk
            - hr: Hiring, culture, performance, compensation, team building
            - general: Questions that don't fit clearly into other categories
            
            Respond with exactly this format:
            DOMAIN: [domain_name]
            CONFIDENCE: [0.0-1.0]
            REASONING: [brief explanation of why this domain was chosen]
            
            Focus on the primary decision type, not just keywords. For example:
            - "Should we migrate to microservices?" → technology (architecture decision)
            - "How do we price our SaaS product?" → business (pricing strategy)
            - "What features should we prioritize?" → product (feature planning)
            """,
        )

        # Get classification
        message = TextMessage(content=f"Classify this query: '{query}'", source="user")
        response = await domain_classifier.on_messages([message], CancellationToken())

        if hasattr(response, "chat_message") and hasattr(
            response.chat_message, "content"
        ):
            content = response.chat_message.content

            # Parse the response
            domain = "general"
            confidence = 0.5

            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("DOMAIN:"):
                    domain = line.split(":", 1)[1].strip().lower()
                elif line.startswith("CONFIDENCE:"):
                    try:
                        confidence = float(line.split(":", 1)[1].strip())
                    except ValueError:
                        confidence = 0.5

            return domain, confidence

    except Exception:
        # Fallback to keyword-based classification
        query_lower = query.lower()

        # Business keywords
        if any(
            word in query_lower
            for word in [
                "pricing",
                "revenue",
                "business model",
                "strategy",
                "market",
                "competitor",
                "funding",
                "investment",
                "growth",
                "customer",
                "profit",
                "freemium",
                "premium",
            ]
        ):
            return "business", 0.7

        # Technology keywords
        elif any(
            word in query_lower
            for word in [
                "architecture",
                "microservices",
                "database",
                "api",
                "infrastructure",
                "security",
                "deployment",
                "server",
                "cloud",
                "technical",
                "engineering",
                "code",
                "framework",
            ]
        ):
            return "technology", 0.7

        # Product keywords
        elif any(
            word in query_lower
            for word in [
                "feature",
                "product",
                "user",
                "roadmap",
                "design",
                "launch",
                "mvp",
                "user experience",
                "interface",
                "functionality",
                "prioritize",
            ]
        ):
            return "product", 0.7

        # Default fallback
        return "general", 0.3


async def get_user_domain_choice(console: Console, suggested_domain: str) -> str:
    """
    Let the user choose or confirm the domain.

    Args:
        console: Rich console for output
        suggested_domain: The AI-suggested domain

    Returns:
        User's chosen domain
    """
    domains = [
        "business",
        "technology",
        "product",
        "finance",
        "operations",
        "marketing",
        "legal",
        "hr",
        "general",
    ]

    console.print("\n[bold]Available domains:[/bold]")
    for i, domain in enumerate(domains, 1):
        marker = "👉" if domain == suggested_domain else "  "
        console.print(f"{marker} {i}. [cyan]{domain}[/cyan]")

    console.print(f"\n[dim]Suggested: {suggested_domain}[/dim]")

    while True:
        choice = Prompt.ask(
            "Choose domain number or type custom domain name",
            default=str(domains.index(suggested_domain) + 1),
        )

        # Check if it's a number (domain selection)
        try:
            domain_index = int(choice) - 1
            if 0 <= domain_index < len(domains):
                chosen_domain = domains[domain_index]
                console.print(
                    f"✅ Using domain: [bold green]{chosen_domain}[/bold green]\n"
                )
                return chosen_domain
            else:
                console.print(
                    "[red]Invalid number. Please choose 1-9 or enter a custom domain.[/red]"
                )
        except ValueError:
            # It's a custom domain name
            if choice.strip():
                custom_domain = choice.strip().lower().replace(" ", "_")
                console.print(
                    f"✅ Using custom domain: [bold green]{custom_domain}[/bold green]\n"
                )
                return custom_domain
            else:
                console.print("[red]Please enter a valid domain.[/red]")


def show_current_config(console: Console) -> None:
    """Show current environment configuration."""
    console.print("\n[bold]Current Environment Variables:[/bold]")

    api_key = os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL", "")

    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        console.print(f"[green]✓[/green] OPENAI_API_KEY: {masked_key}")
    else:
        console.print("[red]✗[/red] OPENAI_API_KEY: Not set")

    if base_url:
        console.print(f"[green]✓[/green] OPENAI_BASE_URL: {base_url}")
    else:
        console.print(
            "[yellow]ℹ[/yellow] OPENAI_BASE_URL: Not set (will use OpenAI default)"
        )


@app.command("validate-config")
def validate_config(
    config_dir: Path = typer.Argument(
        ...,
        help="Directory containing agent configuration files to validate",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """
    🔍 Validate a directory of agent configuration files.

    Checks that all required agent configuration files exist, are valid YAML,
    and contain the necessary fields for the expert panel to function.
    """
    console = Console()
    setup_logging(verbose)

    console.print(
        f"[yellow]Validating configuration directory: {config_dir}[/yellow]\n"
    )

    required_agents = [
        "advocate",
        "critic",
        "pragmatist",
        "research_specialist",
        "innovator",
    ]
    required_fields = ["name", "model_name", "description", "system_message"]

    errors = []
    warnings = []
    valid_configs = 0

    for agent_name in required_agents:
        config_file = config_dir / f"{agent_name}.yaml"

        # Check if file exists
        if not config_file.exists():
            errors.append(f"❌ Missing configuration file: {config_file}")
            continue

        # Check if file is readable
        if not config_file.is_file():
            errors.append(f"❌ Not a file: {config_file}")
            continue

        try:
            # Try to parse YAML
            with open(config_file, "r") as f:
                config_data = yaml.safe_load(f)

            if not isinstance(config_data, dict):
                errors.append(f"❌ {agent_name}.yaml: Not a valid YAML dictionary")
                continue

            # Check required fields
            missing_fields = []
            for field in required_fields:
                if field not in config_data:
                    missing_fields.append(field)
                elif not config_data[field]:
                    missing_fields.append(f"{field} (empty)")

            if missing_fields:
                errors.append(
                    f"❌ {agent_name}.yaml: Missing required fields: {', '.join(missing_fields)}"
                )
                continue

            # Check name matches filename
            if config_data.get("name") != agent_name:
                warnings.append(
                    f"⚠️  {agent_name}.yaml: Name field '{config_data.get('name')}' doesn't match filename"
                )

            # Try to load as AgentConfig
            try:
                _ = AgentConfig.from_yaml(config_file)
                console.print(f"✅ {agent_name}.yaml: Valid configuration")
                valid_configs += 1
            except Exception as e:
                errors.append(
                    f"❌ {agent_name}.yaml: Failed to load as AgentConfig: {e}"
                )

        except yaml.YAMLError as e:
            errors.append(f"❌ {agent_name}.yaml: Invalid YAML syntax: {e}")
        except Exception as e:
            errors.append(f"❌ {agent_name}.yaml: Error reading file: {e}")

    # Display summary
    console.print("\n[bold]Validation Summary:[/bold]")
    console.print(f"✅ Valid configurations: {valid_configs}/{len(required_agents)}")

    if warnings:
        console.print(f"\n[yellow]Warnings ({len(warnings)}):[/yellow]")
        for warning in warnings:
            console.print(f"  {warning}")

    if errors:
        console.print(f"\n[red]Errors ({len(errors)}):[/red]")
        for error in errors:
            console.print(f"  {error}")

        console.print(
            "\n[red]❌ Configuration directory is not valid for use with agent-panel[/red]"
        )
        raise typer.Exit(1)
    else:
        console.print(
            "\n[green]🎉 Configuration directory is valid and ready to use![/green]"
        )
        console.print(
            f"\n[dim]Usage: agent-panel list-agents --config-dir {config_dir}[/dim]"
        )


@app.command()
def virtual_solve(
    query: str = typer.Argument(
        ..., help="Problem or question to solve using Virtual Expert Panel"
    ),
    domain: Optional[str] = typer.Option(
        None,
        "--domain",
        "-d",
        help="Problem domain (e.g., 'business', 'technology', 'product'). If not provided, will be inferred from your query.",
    ),
    max_iterations: int = typer.Option(
        10, "--max-iterations", "-i", help="Maximum number of decision iterations"
    ),
    config_dir: Optional[Path] = typer.Option(
        None, "--config-dir", "-c", help="Custom config directory"
    ),
    enable_memory: bool = typer.Option(
        False, "--memory", help="Enable conversation memory"
    ),
    memory_type: str = typer.Option(
        "simple", "--memory-type", help="Memory system type (simple, mem0)"
    ),
    enable_graphrag: bool = typer.Option(
        True,
        "--graphrag/--no-graphrag",
        help="Enable GraphRAG for persistent knowledge storage",
    ),
    graphrag_workspace: Optional[Path] = typer.Option(
        None,
        "--graphrag-workspace",
        help="Custom workspace directory for GraphRAG data",
    ),
    persist_knowledge: bool = typer.Option(
        True, "--persist/--no-persist", help="Persist knowledge across sessions"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--non-interactive", help="Allow interactive user input"
    ),
    override_model: Optional[str] = typer.Option(
        None,
        "--override-model",
        "-m",
        help="Override the model name for all agents (e.g., 'gpt-4o', 'qwen3:4b')",
    ),
    override_base_url: Optional[str] = typer.Option(
        None,
        "--override-base-url",
        "-b",
        help="Override the OpenAI base URL for all agents (e.g., 'http://localhost:11434/v1')",
    ),
    override_api_key: Optional[str] = typer.Option(
        None,
        "--override-api-key",
        "-k",
        help="Override the OpenAI API key for all agents",
    ),
):
    """
    🧠 Solve problems using the Virtual Expert Panel (inspired by Microsoft's MAI-DxO).

    This command orchestrates 5 expert agents through a structured decision process:
    - ASK_QUESTION: Request clarification from user
    - REQUEST_TEST: Perform web research and analysis with Tavily
    - PROVIDE_SOLUTION: Give final answer

    Features:
    - GraphRAG-powered persistent knowledge storage
    - Real-time web research with Tavily integration
    - Multi-agent collaboration (Advocate, Critic, Pragmatist, Research Specialist, Innovator)
    - Knowledge persistence across sessions
    - Interactive user input for context-specific decisions

    Perfect for isolated decision-makers like CEOs, CTOs, Head of Product, and Startup Founders.
    """

    async def run_virtual_solve():
        console = Console()

        if verbose:
            logging.basicConfig(level=logging.INFO)

        console.print(
            "\n🧠 [bold blue]Virtual Expert Panel - Problem Solving Mode[/bold blue]"
        )
        console.print(
            "Inspired by Microsoft's MAI-DxO pattern, generalized for any domain\n"
        )

        # Infer domain if not provided
        final_domain = domain
        if not domain:
            console.print(
                "🔍 [dim]Analyzing your query to determine the problem domain...[/dim]"
            )
            try:
                inferred_domain, confidence = await infer_domain_from_query(query)

                # Format confidence as percentage
                confidence_pct = int(confidence * 100)

                # Show inference result
                confidence_color = (
                    "green"
                    if confidence >= 0.7
                    else "yellow"
                    if confidence >= 0.5
                    else "red"
                )
                console.print(
                    f"🎯 Inferred domain: [bold {confidence_color}]{inferred_domain}[/bold {confidence_color}] (confidence: {confidence_pct}%)"
                )

                # Ask for user confirmation if interactive
                if interactive:
                    if confidence >= 0.8:
                        # High confidence - just confirm
                        if Confirm.ask(
                            f"Use '{inferred_domain}' domain?", default=True
                        ):
                            final_domain = inferred_domain
                            console.print(
                                f"✅ Using domain: [bold green]{final_domain}[/bold green]\n"
                            )
                        else:
                            # Let user choose alternative
                            final_domain = await get_user_domain_choice(
                                console, inferred_domain
                            )
                    else:
                        # Lower confidence - offer choice
                        console.print(
                            f"\n[yellow]I'm {confidence_pct}% confident this is a '{inferred_domain}' question.[/yellow]"
                        )
                        final_domain = await get_user_domain_choice(
                            console, inferred_domain
                        )
                else:
                    # Non-interactive mode - use inference
                    final_domain = inferred_domain
                    console.print(
                        f"✅ Using inferred domain: [bold green]{final_domain}[/bold green]\n"
                    )

            except Exception as e:
                console.print(
                    f"⚠️  [yellow]Could not infer domain ({e}), using 'general'[/yellow]"
                )
                final_domain = "general"

        # Show what we're solving
        console.print(f"[bold]Problem:[/bold] {query}")
        console.print(f"[bold]Domain:[/bold] {final_domain}")
        console.print(f"[bold]Max Iterations:[/bold] {max_iterations}")
        console.print(
            f"[bold]Memory Enabled:[/bold] {'Yes' if enable_memory else 'No'}"
        )
        console.print(
            f"[bold]GraphRAG Enabled:[/bold] {'Yes' if enable_graphrag else 'No'}"
        )
        console.print(
            f"[bold]Persist Knowledge:[/bold] {'Yes' if persist_knowledge else 'No'}"
        )
        console.print()

        try:
            # Build model overrides dictionary
            model_overrides = {}
            if override_model:
                model_overrides["model_name"] = override_model
            if override_base_url:
                model_overrides["openai_base_url"] = override_base_url
            if override_api_key:
                model_overrides["openai_api_key"] = override_api_key

            # Initialize the Virtual Expert Panel
            console.print("🔧 [dim]Initializing Virtual Expert Panel...[/dim]")
            virtual_panel = VirtualExpertPanel(
                config_dir=config_dir,
                enable_memory=enable_memory,
                memory_type=memory_type,
                enable_graphrag=enable_graphrag,
                graphrag_workspace=graphrag_workspace,
                persist_knowledge=persist_knowledge,
                model_overrides=model_overrides,
            )

            # Define user input function for interactive mode
            def get_user_input(question: str) -> str:
                if not interactive:
                    return "Non-interactive mode - no additional information provided."

                console.print("\n" + "=" * 60)
                console.print(
                    "🤔 [bold yellow]The panel needs your input:[/bold yellow]"
                )
                console.print(question)
                console.print("=" * 60)

                response = Prompt.ask("Your response")
                return response

            # Run the virtual panel
            console.print(
                "🚀 [bold green]Starting Virtual Expert Panel session...[/bold green]\n"
            )

            # Run the panel with the inferred/chosen domain
            result: VirtualPanelResult = await virtual_panel.solve_problem(
                query=query,
                domain=final_domain,
                max_iterations=max_iterations,
                user_input_func=get_user_input if interactive else None,
            )

            # Display results
            console.print("\n" + "=" * 60)
            console.print("📋 [bold green]Virtual Expert Panel Results[/bold green]")
            console.print("=" * 60)

            # Show final solution
            if result.final_solution:
                solution_panel = RichPanel(
                    result.final_solution,
                    title="[bold green]🎯 Final Solution[/bold green]",
                    border_style="green",
                )
                console.print(solution_panel)
            else:
                console.print(
                    "[yellow]⚠️ No final solution reached within iteration limit[/yellow]"
                )

            # Show session metadata
            console.print("\n[bold]Session Summary:[/bold]")
            console.print(f"• Total Rounds: {result.total_rounds}")
            console.print(f"• Actions Taken: {len(result.actions_taken)}")
            console.print(f"• Research Tasks: {len(result.research_tasks)}")
            console.print(f"• Knowledge Artifacts: {len(result.knowledge_artifacts)}")
            console.print(f"• Participants: {', '.join(result.participants)}")
            console.print(f"• Session State: {result.session_state.value}")

            if result.start_time and result.end_time:
                duration = result.end_time - result.start_time
                console.print(f"• Duration: {duration.total_seconds():.1f} seconds")

            # Show action history
            if result.actions_taken:
                console.print("\n[bold]Action History:[/bold]")
                for i, action in enumerate(result.actions_taken, 1):
                    action_emoji = {
                        "ask_question": "❓",
                        "request_test": "🔬",
                        "provide_solution": "💡",
                    }.get(action.action_type.value, "📝")

                    console.print(
                        f"{i}. {action_emoji} {action.action_type.value.upper()}"
                    )
                    console.print(
                        f"   [dim]{action.content[:100]}{'...' if len(action.content) > 100 else ''}[/dim]"
                    )

            # Show research summary
            if result.research_tasks:
                console.print("\n[bold]Research Summary:[/bold]")
                completed_tasks = [
                    t for t in result.research_tasks if t.status == "completed"
                ]
                failed_tasks = [
                    t for t in result.research_tasks if t.status == "failed"
                ]

                console.print(f"• Completed: {len(completed_tasks)}")
                console.print(f"• Failed: {len(failed_tasks)}")

                for task in completed_tasks[:3]:  # Show first 3 completed tasks
                    console.print(
                        f"  - [green]✓[/green] {task.description[:60]}{'...' if len(task.description) > 60 else ''}"
                    )

            # Offer to export results
            if interactive and Confirm.ask(
                "\nWould you like to export the detailed results?", default=False
            ):
                export_format = Prompt.ask(
                    "Export format", choices=["json", "markdown"], default="json"
                )

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"virtual_panel_results_{timestamp}.{export_format}"

                try:
                    if export_format == "json":
                        import json

                        with open(filename, "w") as f:
                            # Convert result to dict for JSON serialization
                            result_dict = {
                                "original_query": result.original_query,
                                "final_solution": result.final_solution,
                                "total_rounds": result.total_rounds,
                                "session_state": result.session_state.value,
                                "participants": result.participants,
                                "actions_taken": [
                                    {
                                        "action_type": action.action_type.value,
                                        "content": action.content,
                                        "reasoning": action.reasoning,
                                        "timestamp": action.timestamp.isoformat(),
                                        "metadata": action.metadata,
                                    }
                                    for action in result.actions_taken
                                ],
                                "research_tasks": [
                                    {
                                        "task_id": task.task_id,
                                        "description": task.description,
                                        "agent_assigned": task.agent_assigned,
                                        "status": task.status,
                                        "results": task.results,
                                        "timestamp": task.timestamp.isoformat(),
                                    }
                                    for task in result.research_tasks
                                ],
                            }
                            json.dump(result_dict, f, indent=2, default=str)

                    else:  # markdown
                        with open(filename, "w") as f:
                            f.write("# Virtual Expert Panel Results\n\n")
                            f.write(f"**Query:** {result.original_query}\n\n")
                            f.write(f"**Final Solution:**\n{result.final_solution}\n\n")
                            f.write("**Session Summary:**\n")
                            f.write(f"- Total Rounds: {result.total_rounds}\n")
                            f.write(f"- Actions: {len(result.actions_taken)}\n")
                            f.write(f"- Research Tasks: {len(result.research_tasks)}\n")
                            f.write(
                                f"- Participants: {', '.join(result.participants)}\n\n"
                            )

                            if result.actions_taken:
                                f.write("## Action History\n\n")
                                for i, action in enumerate(result.actions_taken, 1):
                                    f.write(
                                        f"{i}. **{action.action_type.value.upper()}**\n"
                                    )
                                    f.write(f"   {action.content}\n\n")

                    console.print(f"[green]✓[/green] Results exported to: {filename}")

                except Exception as e:
                    console.print(f"[red]❌ Export failed: {e}[/red]")

            console.print(
                "\n🎉 [bold green]Virtual Expert Panel session completed![/bold green]"
            )

        except APIKeyError:
            console.print(
                "[red]❌ API Key Error: Please set your OPENAI_API_KEY environment variable[/red]"
            )
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            if verbose:
                console.print_exception()
            raise typer.Exit(1)

    # Run the async function
    asyncio.run(run_virtual_solve())


@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """
    🧠 Agent Expert Panel - Multi-agent discussion system

    A sophisticated multi-agent discussion framework that orchestrates AI experts
    to solve complex problems through collaborative reasoning.

    Run without any commands to start interactive mode, or use specific commands
    for batch operations.
    """
    # Setup logging
    setup_logging(verbose)

    # If no command is provided, run interactive mode
    if ctx.invoked_subcommand is None:
        result = asyncio.run(interactive_mode())
        raise typer.Exit(result)


if __name__ == "__main__":
    app()
