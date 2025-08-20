"""
Observability Manager

Central manager for all observability and tracing activities in the agent expert panel.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional, Any, Callable
from contextlib import contextmanager

from ..models.observability import (
    ObservabilityConfig,
    DiscussionSession,
    AgentInteraction,
    ConsensusEvent,
    ToolUsageEvent,
)
from .langfuse_tracer import LangfuseTracer


class ObservabilityManager:
    """
    Central manager for observability and tracing.

    This class coordinates tracing across different providers and provides
    a unified interface for recording observability events.
    """

    def __init__(self, config: Optional[ObservabilityConfig] = None):
        """
        Initialize the observability manager.

        Args:
            config: Observability configuration. If None, loads from environment.
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or ObservabilityConfig()

        # Initialize tracers
        self.langfuse_tracer = (
            LangfuseTracer(self.config) if self.config.langfuse_enabled else None
        )

        # Current session tracking
        self._current_session: Optional[DiscussionSession] = None
        self._session_start_time: Optional[datetime] = None
        # Optional callback invoked on each agent interaction; set by host app (e.g., backend)
        self.on_agent_message: Optional[Callable[[AgentInteraction], None]] = None

        self.logger.info(
            f"Observability manager initialized. "
            f"Langfuse: {'enabled' if self.langfuse_tracer else 'disabled'}"
        )

    def create_discussion_session(
        self,
        topic: str,
        pattern: str,
        participants: list[str],
        max_rounds: int,
        with_human: bool = False,
        human_name: Optional[str] = None,
    ) -> DiscussionSession:
        """
        Create a new discussion session for tracing.

        Args:
            topic: Discussion topic
            pattern: Discussion pattern
            participants: List of participating agents
            max_rounds: Maximum number of rounds
            with_human: Whether human is participating
            human_name: Name of human participant

        Returns:
            DiscussionSession object
        """
        session_id = str(uuid.uuid4())
        start_time = datetime.now()

        session = DiscussionSession(
            session_id=session_id,
            topic=topic,
            pattern=pattern,
            participants=participants,
            max_rounds=max_rounds,
            actual_rounds=0,
            start_time=start_time,
            with_human=with_human,
            human_name=human_name,
        )

        self._current_session = session
        self._session_start_time = start_time

        self.logger.info(f"Created discussion session: {session_id}")
        return session

    @contextmanager
    def trace_discussion(self, session: DiscussionSession):
        """
        Context manager for tracing a complete discussion session.

        Args:
            session: Discussion session to trace
        """
        if not self.config.enabled:
            yield None
            return

        self.logger.info(f"Starting discussion tracing: {session.session_id}")

        # Start tracing with all enabled tracers
        trace_contexts = []

        if self.langfuse_tracer:
            langfuse_ctx = self.langfuse_tracer.trace_discussion_session(session)
            trace_contexts.append(langfuse_ctx)

        try:
            # Enter all trace contexts
            trace_clients = []
            for ctx in trace_contexts:
                trace_client = ctx.__enter__()
                trace_clients.append(trace_client)

            yield trace_clients[0] if trace_clients else None

        except Exception as e:
            self.logger.error(f"Error in discussion tracing: {e}")
            raise
        finally:
            # Exit all trace contexts
            for ctx in reversed(trace_contexts):
                try:
                    ctx.__exit__(None, None, None)
                except Exception as e:
                    self.logger.error(f"Error closing trace context: {e}")

            self.logger.info(f"Completed discussion tracing: {session.session_id}")

    def record_agent_interaction(
        self,
        agent_name: str,
        agent_role: str,
        message_content: str,
        message_round: int,
        token_count: Optional[int] = None,
        response_time_ms: Optional[float] = None,
        tools_used: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Record an agent interaction event.

        Args:
            agent_name: Name of the agent
            agent_role: Role/type of the agent
            message_content: Content of the agent's message
            message_round: Round number in the discussion
            token_count: Number of tokens in the message
            response_time_ms: Response time in milliseconds
            tools_used: List of tools used by the agent
            metadata: Additional metadata
        """
        if not self.config.enabled or not self._current_session:
            return

        interaction = AgentInteraction(
            agent_name=agent_name,
            agent_role=agent_role,
            message_content=message_content,
            message_round=message_round,
            token_count=token_count,
            response_time_ms=response_time_ms,
            tools_used=tools_used or [],
            metadata=metadata or {},
        )

        # Send to all enabled tracers
        if self.langfuse_tracer:
            self.langfuse_tracer.trace_agent_interaction(
                interaction, self._current_session.session_id
            )

        self.logger.debug(
            f"Recorded agent interaction: {agent_name} - Round {message_round}"
        )

        # Host application hook for real-time streaming (e.g., Redis pub/sub)
        try:
            if self.on_agent_message:
                self.on_agent_message(interaction)
        except Exception as e:
            # Ensure observability callbacks never disrupt the main flow
            self.logger.warning(f"on_agent_message callback raised: {e}")

    def record_consensus_event(
        self,
        consensus_reached: bool,
        participants_in_agreement: list[str],
        summary: str,
        confidence_score: Optional[float] = None,
        dissenting_participants: Optional[list[str]] = None,
    ) -> None:
        """
        Record a consensus detection event.

        Args:
            consensus_reached: Whether consensus was detected
            participants_in_agreement: Agents that agreed
            summary: Summary of the consensus
            confidence_score: Confidence in consensus detection
            dissenting_participants: Agents that disagreed
        """
        if not self.config.enabled or not self._current_session:
            return

        event = ConsensusEvent(
            session_id=self._current_session.session_id,
            consensus_reached=consensus_reached,
            confidence_score=confidence_score,
            participants_in_agreement=participants_in_agreement,
            dissenting_participants=dissenting_participants or [],
            summary=summary,
            detection_time=datetime.now(),
        )

        # Send to all enabled tracers
        if self.langfuse_tracer:
            self.langfuse_tracer.trace_consensus_event(event)

        self.logger.debug(
            f"Recorded consensus event: consensus_reached={consensus_reached}"
        )

    def record_tool_usage(
        self,
        agent_name: str,
        tool_name: str,
        tool_input: dict[str, Any],
        tool_output: Optional[dict[str, Any]] = None,
        execution_time_ms: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Record a tool usage event.

        Args:
            agent_name: Agent that used the tool
            tool_name: Name of the tool used
            tool_input: Input parameters to the tool
            tool_output: Output from the tool
            execution_time_ms: Tool execution time in milliseconds
            success: Whether tool execution was successful
            error_message: Error message if tool failed
        """
        if not self.config.enabled or not self._current_session:
            return

        event = ToolUsageEvent(
            session_id=self._current_session.session_id,
            agent_name=agent_name,
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output,
            execution_time_ms=execution_time_ms,
            success=success,
            error_message=error_message,
            timestamp=datetime.now(),
        )

        # Send to all enabled tracers
        if self.langfuse_tracer:
            self.langfuse_tracer.trace_tool_usage(event)

        self.logger.debug(f"Recorded tool usage: {tool_name} by {agent_name}")

    def finalize_session(
        self,
        actual_rounds: int,
        total_tokens: Optional[int] = None,
        consensus_reached: bool = False,
    ) -> None:
        """
        Finalize the current discussion session.

        Args:
            actual_rounds: Number of rounds actually completed
            total_tokens: Total tokens used in the discussion
            consensus_reached: Whether consensus was reached
        """
        if not self._current_session or not self._session_start_time:
            return

        end_time = datetime.now()
        duration_ms = (end_time - self._session_start_time).total_seconds() * 1000

        # Update session with final data
        self._current_session.actual_rounds = actual_rounds
        self._current_session.end_time = end_time
        self._current_session.duration_ms = duration_ms
        self._current_session.total_tokens = total_tokens
        self._current_session.consensus_reached = consensus_reached

        self.logger.info(
            f"Finalized session {self._current_session.session_id}: "
            f"{actual_rounds} rounds, {duration_ms:.0f}ms, "
            f"consensus: {consensus_reached}"
        )

        # Clear current session
        self._current_session = None
        self._session_start_time = None

    def flush_traces(self) -> None:
        """Flush all pending traces."""
        if self.langfuse_tracer:
            self.langfuse_tracer.flush()

    def get_session_url(self) -> Optional[str]:
        """
        Get the URL to view the current session in the tracing UI.

        Returns:
            URL string or None if no session or tracing disabled
        """
        if not self._current_session or not self.langfuse_tracer:
            return None

        return self.langfuse_tracer.get_session_url(self._current_session.session_id)

    def is_enabled(self) -> bool:
        """Check if observability is enabled."""
        return self.config.enabled

    def get_current_session_id(self) -> Optional[str]:
        """Get the current session ID."""
        return self._current_session.session_id if self._current_session else None
