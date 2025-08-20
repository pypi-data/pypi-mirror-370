"""
Expert Panel Orchestrator

This module provides the main orchestration for running multi-agent expert panel discussions.
Inspired by Microsoft's MAI-DxO and Hugging Face's Consilium approaches to multi-agent collaboration.
"""

import logging
import re
from pathlib import Path
from typing import Any, Union, Callable, List, Dict, Optional

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.ui import RichConsole
from autogen_agentchat.base import TaskResult
from autogen_core import CancellationToken

from .agents.create_agent import create_agent
from .models.config import AgentConfig
from .models.consensus import Consensus
from .models.panel import PanelResult, DiscussionPattern
from .models.observability import ObservabilityConfig
from .observability import ObservabilityManager
from .tools import (
    BUILTIN_TOOLS,
    load_tools_from_directory,
    add_library_tools_to_dict,
    create_library_tool,
)


class ExpertPanel:
    """
    Main orchestrator for the 5-agent expert panel discussions.

    The panel consists of:
    - Advocate: Champions ideas with conviction and evidence
    - Critic: Rigorous quality assurance and risk analysis
    - Pragmatist: Practical implementation focus
    - Research Specialist: Fact-finding and evidence gathering
    - Innovator: Creative disruption and breakthrough solutions
    """

    @staticmethod
    def _clean_think_tokens(text: str) -> str:
        """
        Remove <think></think> tokens from text content.

        Args:
            text: The text content to clean

        Returns:
            Text with think tokens removed
        """
        if not text:
            return text

        # Remove <think>...</think> blocks (including multiline)
        cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

        # Clean up extra whitespace that might be left
        cleaned = re.sub(
            r"\n\s*\n\s*\n", "\n\n", cleaned
        )  # Multiple newlines to double
        cleaned = cleaned.strip()

        return cleaned

    def __init__(
        self,
        config_dir: Path | None = None,
        tools_dir: Path | None = None,
        observability_config: Optional[ObservabilityConfig] = None,
        model_overrides: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the expert panel.

        Args:
            config_dir: Directory containing agent configuration files
            tools_dir: Directory containing custom tool definitions
            observability_config: Configuration for observability and tracing
            model_overrides: Dictionary containing model configuration overrides
                            Keys: 'model_name', 'openai_base_url', 'openai_api_key'
        """
        self.config_dir = config_dir or self._get_default_config_dir()
        self.tools_dir = tools_dir
        self.model_overrides = model_overrides or {}
        self.agents: dict[str, AssistantAgent] = {}
        self.logger = logging.getLogger(__name__)

        # Initialize observability manager
        self.observability = ObservabilityManager(observability_config)

        # Load available tools (built-in + custom)
        self.available_tools = BUILTIN_TOOLS.copy()
        if self.tools_dir and Path(self.tools_dir).exists():
            try:
                custom_tools = load_tools_from_directory(self.tools_dir)
                self.available_tools.update(custom_tools)
                self.logger.info(
                    f"Loaded {len(custom_tools)} custom tools from {self.tools_dir}"
                )
            except Exception as e:
                self.logger.warning(f"Failed to load custom tools: {e}")

        # Load all agents
        self._load_agents()

    def _get_default_config_dir(self) -> Path:
        """
        Get the default configuration directory with fallback logic.

        First tries to find configs in the package directory, then falls back
        to the repository root configs directory.

        Returns:
            Path to the configuration directory
        """
        # Try package-bundled configs first
        package_configs = Path(__file__).parent / "configs"
        if package_configs.exists() and any(package_configs.glob("*.yaml")):
            return package_configs

        # Fall back to repository root configs (for development)
        repo_configs = Path(__file__).parent.parent.parent / "configs"
        if repo_configs.exists() and any(repo_configs.glob("*.yaml")):
            return repo_configs

        # If neither exists, return the package location anyway
        # This will cause an error later which is appropriate
        return package_configs

    def _create_human_agent(
        self,
        human_name: str,
        input_func: Union[
            Callable[[str], str], Callable[[str, CancellationToken | None], str]
        ]
        | None = None,
    ) -> UserProxyAgent:
        """
        Create a UserProxyAgent for human participation.

        Args:
            human_name: Name for the human participant
            input_func: Optional custom input function

        Returns:
            UserProxyAgent configured for the panel discussion
        """
        description = (
            f"Human expert '{human_name}' participating in the panel discussion"
        )

        return UserProxyAgent(
            name=human_name, description=description, input_func=input_func
        )

    def _load_agents(self) -> None:
        """Load all expert agents from their configuration files."""
        agent_names = [
            "advocate",
            "critic",
            "pragmatist",
            "research_specialist",
            "innovator",
            "web_research_specialist",
        ]

        for agent_name in agent_names:
            config_file = self.config_dir / f"{agent_name}.yaml"
            if not config_file.exists():
                # Skip web_research_specialist if not present (for backward compatibility)
                if agent_name == "web_research_specialist":
                    self.logger.info(
                        f"Web research specialist config not found at {config_file}, skipping"
                    )
                    continue
                raise FileNotFoundError(f"Configuration file not found: {config_file}")

            try:
                config = AgentConfig.from_yaml(config_file)

                # Apply CLI overrides if provided
                if self.model_overrides:
                    if "model_name" in self.model_overrides:
                        config.model_name = self.model_overrides["model_name"]
                        self.logger.info(
                            f"Overriding {agent_name} model_name to: {config.model_name}"
                        )

                    if "openai_base_url" in self.model_overrides:
                        config.openai_base_url = self.model_overrides["openai_base_url"]
                        self.logger.info(
                            f"Overriding {agent_name} openai_base_url to: {config.openai_base_url}"
                        )

                    if "openai_api_key" in self.model_overrides:
                        config.openai_api_key = self.model_overrides["openai_api_key"]
                        self.logger.info(f"Overriding {agent_name} openai_api_key")

                agent = create_agent(config, available_tools=self.available_tools)
                self.agents[agent_name] = agent
                self.logger.info(f"Loaded {agent_name} agent successfully")
            except Exception as e:
                self.logger.error(f"Failed to load {agent_name} agent: {e}")
                raise

    def add_library_tools(self, library_tools: dict[str, str]) -> None:
        """
        Add library tools to the available tools for all agents.

        Args:
            library_tools: Dictionary mapping tool names to import paths
                          e.g., {"read_csv": "pandas.read_csv", "parse_json": "json.loads"}
        """
        add_library_tools_to_dict(self.available_tools, library_tools)

    def add_tools_to_agent(
        self, agent_name: str, tools: list[Union[str, Callable]]
    ) -> None:
        """
        Add tools to a specific agent.

        Args:
            agent_name: Name of the agent
            tools: List of tool names (strings), library import paths, or tool functions
                  Examples:
                  - "web_search" (built-in tool)
                  - "pandas.read_csv" (library import)
                  - my_function (direct function reference)
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found")

        agent_tools = []

        for tool in tools:
            if isinstance(tool, str):
                if tool in self.available_tools:
                    # Found in available tools
                    agent_tools.append(self.available_tools[tool])
                elif "." in tool:
                    # Looks like a library import - try to import it
                    try:
                        library_tool = create_library_tool(tool)
                        agent_tools.append(library_tool)
                    except Exception as e:
                        print(f"Warning: Could not import tool '{tool}': {e}")
                else:
                    print(f"Warning: Tool '{tool}' not found in available tools")
            elif callable(tool):
                # Direct function reference
                agent_tools.append(tool)

        # Add tools to the agent's existing tools
        current_tools = getattr(self.agents[agent_name], "tools", []) or []
        current_tools.extend(agent_tools)
        self.agents[agent_name].tools = current_tools

    async def discuss(
        self,
        topic: str,
        pattern: DiscussionPattern = DiscussionPattern.ROUND_ROBIN,
        max_rounds: int = 3,
        participants: list[str] | None = None,
        with_human: bool = False,
        human_name: str = "Human",
        human_input_func: Union[
            Callable[[str], str], Callable[[str, CancellationToken | None], str]
        ]
        | None = None,
    ) -> PanelResult:
        """
        Run a panel discussion on the given topic.

        Args:
            topic: The topic or question for the panel to discuss
            pattern: The discussion pattern to use
            max_rounds: Maximum number of discussion rounds
            participants: Specific agents to include (default: all 5)
            with_human: Whether to include human participant
            human_name: Name for the human participant (default: "Human")
            human_input_func: Optional custom input function for human interaction.
                            If not provided, uses standard input()

        Returns:
            PanelResult containing the discussion outcomes
        """
        participants = participants or list(self.agents.keys())
        participating_agents = [self.agents[name] for name in participants]

        # Add human participant if requested or if human parameters are provided
        human_agent = None
        # Auto-enable human participation if human_name or human_input_func is provided
        if with_human or human_name != "Human" or human_input_func is not None:
            human_agent = self._create_human_agent(human_name, human_input_func)
            participating_agents.append(human_agent)
            participants.append(human_name)
            with_human = True

        self.logger.info(f"Starting panel discussion on: {topic}")
        self.logger.info(f"Pattern: {pattern.value}, Participants: {participants}")
        if with_human:
            self.logger.info(f"Human participant '{human_name}' included in discussion")

        # Create discussion session for tracing
        session = self.observability.create_discussion_session(
            topic=topic,
            pattern=pattern.value,
            participants=participants,
            max_rounds=max_rounds,
            with_human=with_human,
            human_name=human_name if with_human else None,
        )

        # Log session URL if available
        session_url = self.observability.get_session_url()
        if session_url:
            self.logger.info(f"View discussion tracing: {session_url}")

        try:
            with self.observability.trace_discussion(session):
                if pattern == DiscussionPattern.ROUND_ROBIN:
                    result = await self._run_round_robin_discussion(
                        topic,
                        participating_agents,
                        max_rounds,
                    )
                elif pattern == DiscussionPattern.STRUCTURED_DEBATE:
                    result = await self._run_structured_debate(
                        topic,
                        participating_agents,
                        max_rounds,
                    )
                else:
                    raise NotImplementedError(
                        f"Discussion pattern {pattern} not yet implemented"
                    )

                # Finalize session with results
                self.observability.finalize_session(
                    actual_rounds=result.total_rounds,
                    consensus_reached=result.consensus_reached,
                )

                return result

        finally:
            # Ensure traces are flushed
            self.observability.flush_traces()

    async def _run_round_robin_discussion(
        self,
        topic: str,
        agents: list[Union[AssistantAgent, UserProxyAgent]],
        max_rounds: int,
    ) -> PanelResult:
        """Run a round-robin style discussion."""

        # Create the round-robin group chat
        group_chat = RoundRobinGroupChat(agents, max_turns=max_rounds * len(agents))

        # Create enhanced topic prompt that encourages collaboration
        enhanced_prompt = f"""
        Welcome to the Expert Panel Discussion!

        Topic: {topic}

        Instructions for the panel:
        - Each expert should provide their unique perspective based on their specialization
        - Build upon or challenge previous speakers' points constructively
        - Aim for a collaborative solution that incorporates diverse viewpoints
        """

        discussion_history = []

        # Run the discussion using RichConsole for nice output
        task_result: TaskResult = await RichConsole(
            group_chat.run_stream(task=enhanced_prompt)
        )

        # Parse the actual discussion history from the task result
        discussion_history = self._extract_discussion_history(task_result)

        # Extract agent names from the agents list
        agent_names = [agent.name for agent in agents]

        # Extract final recommendation and consensus
        (
            final_recommendation,
            consensus_reached,
        ) = await self._analyze_discussion_results(task_result)

        # Calculate actual rounds from the discussion
        actual_rounds = self._calculate_discussion_rounds(
            discussion_history, len(agents)
        )

        result = PanelResult(
            topic=topic,
            discussion_pattern=DiscussionPattern.ROUND_ROBIN,
            agents_participated=agent_names,
            discussion_history=discussion_history,
            consensus_reached=consensus_reached,
            final_recommendation=final_recommendation,
            total_rounds=actual_rounds,
        )

        return result

    async def _run_structured_debate(
        self,
        topic: str,
        agents: list[Union[AssistantAgent, UserProxyAgent]],
        max_rounds: int,
    ) -> PanelResult:
        """Run a structured debate with specific phases."""

        # For structured debate, we'll run the full discussion as one session
        # but structure the prompt to encourage debate phases
        structured_prompt = f"""
        Welcome to the Structured Expert Panel Debate!

        Topic: {topic}

        This debate will proceed through structured phases:
        1. Initial Position Statements - Each participant states their position
        2. Evidence and Analysis Phase - Present supporting evidence
        3. Challenge and Rebuttal Phase - Challenge other positions
        4. Synthesis and Consensus Building - Work toward agreement
        """

        # Create the group chat for structured debate
        group_chat = RoundRobinGroupChat(agents, max_turns=max_rounds * len(agents))

        # Run the structured debate
        task_result: TaskResult = await RichConsole(
            group_chat.run_stream(task=structured_prompt)
        )

        # Parse the discussion history and results
        discussion_history = self._extract_discussion_history(task_result)

        # Extract agent names from the agents list
        agent_names = [agent.name for agent in agents]

        (
            final_recommendation,
            consensus_reached,
        ) = await self._analyze_discussion_results(task_result)
        actual_rounds = self._calculate_discussion_rounds(
            discussion_history, len(agents)
        )

        result = PanelResult(
            topic=topic,
            discussion_pattern=DiscussionPattern.STRUCTURED_DEBATE,
            agents_participated=agent_names,
            discussion_history=discussion_history,
            consensus_reached=consensus_reached,
            final_recommendation=final_recommendation,
            total_rounds=actual_rounds,
        )

        return result

    def _get_phase_instructions(self, phase_name: str) -> str:
        """Get specific instructions for each debate phase."""
        instructions = {
            "Initial Position Statements": "State your initial position and key arguments",
            "Evidence and Analysis Phase": "Provide supporting evidence and detailed analysis",
            "Challenge and Rebuttal Phase": "Challenge other positions and defend your own",
            "Synthesis and Consensus Building": "Work toward synthesis and common ground",
        }
        return instructions.get(phase_name, "Participate according to your expertise")

    def get_agent_descriptions(self) -> dict[str, str]:
        """Get descriptions of all agents in the panel."""
        descriptions = {}
        for name, agent in self.agents.items():
            # Get description from config if available, otherwise use agent name
            config_file = self.config_dir / f"{name}.yaml"
            if config_file.exists():
                config = AgentConfig.from_yaml(config_file)
                descriptions[name] = config.description
            else:
                descriptions[name] = f"{name.title()} agent"
        return descriptions

    async def quick_consensus(self, question: str) -> str:
        """
        Get a quick consensus from all agents on a simple question.

        Args:
            question: A straightforward question requiring expert input

        Returns:
            A synthesized response from all experts
        """
        result = await self.discuss(
            topic=question, pattern=DiscussionPattern.ROUND_ROBIN, max_rounds=1
        )
        return result.final_recommendation

    async def discuss_with_human(
        self,
        topic: str,
        pattern: DiscussionPattern = DiscussionPattern.ROUND_ROBIN,
        max_rounds: int = 3,
        participants: list[str] | None = None,
        human_name: str = "Human Expert",
        human_input_func: Union[
            Callable[[str], str], Callable[[str, CancellationToken | None], str]
        ]
        | None = None,
    ) -> PanelResult:
        """
        Convenience method to run a panel discussion with human participation.

        Args:
            topic: The topic or question for the panel to discuss
            pattern: The discussion pattern to use
            max_rounds: Maximum number of discussion rounds
            participants: Specific agents to include (default: all 5)
            human_name: Name for the human participant
            human_input_func: Optional custom input function for human interaction

        Returns:
            PanelResult containing the discussion outcomes
        """
        return await self.discuss(
            topic=topic,
            pattern=pattern,
            max_rounds=max_rounds,
            participants=participants,
            with_human=True,
            human_name=human_name,
            human_input_func=human_input_func,
        )

    def _extract_discussion_history(
        self, task_result: TaskResult
    ) -> list[dict[str, Any]]:
        """
        Extract discussion history from the TaskResult.

        Args:
            task_result: The result from the group chat discussion

        Returns:
            List of discussion entries with speaker, content, and metadata
        """
        history = []

        for i, message in enumerate(task_result.messages):
            # Extract content using the standard to_text() method
            content = message.to_text()

            # Clean think tokens from content
            content = self._clean_think_tokens(content)

            # Skip empty messages and system messages
            if content and content.strip() and not content.startswith("System:"):
                entry = {
                    "round": i + 1,
                    "speaker": message.source,
                    "content": content.strip(),
                    "timestamp": message.created_at,
                }
                history.append(entry)

                # Record agent interaction for observability
                self._record_agent_interaction(
                    agent_name=message.source,
                    message_content=content.strip(),
                    message_round=i + 1,
                    timestamp=message.created_at,
                )

        self.logger.debug(
            f"Extracted {len(history)} discussion entries from TaskResult"
        )

        return history

    async def _analyze_discussion_results(
        self, task_result: TaskResult
    ) -> tuple[str, bool]:
        """
        Analyze the discussion results to extract final recommendation and consensus.

        Args:
            task_result: The result from the group chat discussion

        Returns:
            Tuple of (final_recommendation, consensus_reached)
        """
        # Initialize defaults
        final_recommendation = (
            "Discussion completed - see individual agent responses above."
        )
        consensus_reached = False
        all_messages: list[str] = []
        for message in task_result.messages:
            model_message: str = ""
            if hasattr(message, "to_model_text"):
                model_message: str = message.to_model_text()

            # Clean think tokens from the message before processing
            model_message = self._clean_think_tokens(model_message)

            all_messages.append(model_message)

        consensus: Consensus = await self._detect_consensus(all_messages)
        consensus_reached = consensus.consensus_reached

        # Create a comprehensive final recommendation
        final_recommendation: str = await self._synthesize_recommendation(all_messages)

        return final_recommendation, consensus_reached

    def _calculate_discussion_rounds(
        self, discussion_history: List[Dict[str, Any]], num_agents: int
    ) -> int:
        """
        Calculate the number of discussion rounds based on the history.

        Args:
            discussion_history: List of discussion entries
            num_agents: Number of participating agents

        Returns:
            Number of complete discussion rounds
        """
        if not discussion_history or num_agents == 0:
            return 0

        # Simple calculation: total messages divided by number of agents
        # This gives an approximate number of rounds
        return max(1, len(discussion_history) // num_agents)

    async def _detect_consensus(self, messages: list[str]) -> Consensus:
        """
        Detect if consensus was reached in the discussion by asking the first agent.

        Args:
            messages: List of message dictionaries with speaker and content

        Returns:
            True if consensus appears to have been reached
        """

        consensus: Consensus = Consensus(
            consensus_reached=False, summary="", participants=[]
        )
        if len(messages) < 2:
            return consensus

        # Get the first agent to evaluate consensus
        if not self.agents:
            return consensus

        first_agent: AssistantAgent = list(self.agents.values())[0]

        consensus_agent: AssistantAgent = AssistantAgent(
            name="consensus_agent",
            description="A consensus agent that will evaluate if the participants reached a consensus.",
            model_client=first_agent._model_client,
            system_message=(
                "You are an expert at reviewing discussions and determining if a consensus was reached. "
                "You will be given a discussion and you will need to determine if the participants reached a consensus. "
                "A consensus means the participants generally agree on the main points and recommendations. "
                "You will need to consider the following: "
                "1. The participants' positions and arguments "
                "2. The evidence and analysis provided by the participants "
                "3. The challenge and rebuttal of other positions "
                "4. The synthesis and consensus building efforts "
                "You will need to return the following information: "
                "    1. consensus_reached: True if the participants reached a consensus, False otherwise. "
                "    2. summary: A summary of the discussion. "
                "    3. participants: A list of the participants who reached a consensus. "
            ),
            output_content_type=Consensus,
            reflect_on_tool_use=True,
        )

        discussion_summary = "\n".join(messages)
        response: TaskResult = await RichConsole(
            consensus_agent.run_stream(task=discussion_summary)
        )

        consensus: Consensus = response.messages[-1].content

        # Record consensus event for observability
        self.observability.record_consensus_event(
            consensus_reached=consensus.consensus_reached,
            participants_in_agreement=consensus.participants,
            summary=consensus.summary,
            dissenting_participants=[],  # TODO: Extract dissenting participants if available
        )

        return consensus

    async def _synthesize_recommendation(self, messages: list[str]) -> str:
        """
        Synthesize a final recommendation from all agent messages.

        Args:
            messages: List of message dictionaries with speaker and content

        Returns:
            Synthesized final recommendation
        """
        if not messages:
            return "No discussion content available."

        # If there's only one message or the last message is comprehensive, use it
        if len(messages) == 1 or len(messages[-1]) > 200:
            return f"Final Panel Recommendation:\n\n{messages[-1]}"

        # Create a structured summary
        recommendation = "## Expert Panel Final Recommendation\n\n"

        first_agent: AssistantAgent = list(self.agents.values())[0]

        summary_agent: AssistantAgent = AssistantAgent(
            name="summary_agent",
            description="A summary agent that will summarize the discussion.",
            model_client=first_agent._model_client,
            system_message="You are an expert at summarizing discussions.",
        )

        summary_prompt = "Summarize the following discussion:\n\n" + "\n".join(messages)

        summary: TaskResult = await RichConsole(
            summary_agent.run_stream(task=summary_prompt)
        )
        recommendation: str = summary.messages[-1].content

        return recommendation

    def _record_agent_interaction(
        self,
        agent_name: str,
        message_content: str,
        message_round: int,
        timestamp: Optional[Any] = None,
    ) -> None:
        """
        Record an agent interaction for observability.

        Args:
            agent_name: Name of the agent
            message_content: Content of the agent's message
            message_round: Round number in the discussion
            timestamp: Timestamp of the message
        """
        # Determine agent role from agent configuration
        agent_role = "unknown"
        if agent_name in self.agents:
            # Try to get role from agent config
            config_file = self.config_dir / f"{agent_name}.yaml"
            if config_file.exists():
                try:
                    AgentConfig.from_yaml(config_file)
                    agent_role = agent_name  # Use agent name as role for now
                except Exception:
                    agent_role = agent_name
            else:
                agent_role = agent_name
        elif agent_name == "Human" or "Human" in agent_name:
            agent_role = "human"
        else:
            agent_role = agent_name

        # Count tokens using proper tokenization if available
        if self.observability.langfuse_tracer and hasattr(
            self.observability.langfuse_tracer, "count_tokens"
        ):
            estimated_tokens = self.observability.langfuse_tracer.count_tokens(
                message_content
            )
        else:
            # Fallback to simple character-based estimation
            estimated_tokens = len(message_content) // 4

        # Record the interaction
        self.observability.record_agent_interaction(
            agent_name=agent_name,
            agent_role=agent_role,
            message_content=message_content,
            message_round=message_round,
            token_count=estimated_tokens,
            metadata={"timestamp": str(timestamp) if timestamp else None},
        )

    def trace_tool_usage(
        self,
        agent_name: str,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: Optional[Dict[str, Any]] = None,
        execution_time_ms: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Trace tool usage for observability.

        This method can be called from tool implementations to record tool usage events.

        Args:
            agent_name: Name of the agent using the tool
            tool_name: Name of the tool being used
            tool_input: Input parameters passed to the tool
            tool_output: Output returned by the tool
            execution_time_ms: Execution time in milliseconds
            success: Whether the tool execution was successful
            error_message: Error message if the tool failed
        """
        self.observability.record_tool_usage(
            agent_name=agent_name,
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output,
            execution_time_ms=execution_time_ms,
            success=success,
            error_message=error_message,
        )
