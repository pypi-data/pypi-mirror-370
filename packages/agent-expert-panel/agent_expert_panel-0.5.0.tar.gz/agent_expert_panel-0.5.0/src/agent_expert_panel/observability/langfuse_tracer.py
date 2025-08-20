"""
Langfuse Tracer Implementation

This module provides Langfuse integration for tracing agent conversations and interactions.
"""

import os
import logging
import re
from typing import Optional, Any
from contextlib import contextmanager

import tiktoken
from langfuse import Langfuse

from ..models.observability import (
    ObservabilityConfig,
    DiscussionSession,
    AgentInteraction,
    ConsensusEvent,
    ToolUsageEvent,
)


class LangfuseTracer:
    """
    Langfuse integration for tracing agent expert panel conversations.

    This class handles all Langfuse operations including session tracking,
    agent interaction logging, and performance monitoring.
    """

    def __init__(self, config: Optional[ObservabilityConfig] = None):
        """
        Initialize the Langfuse tracer.

        Args:
            config: Observability configuration. If None, loads from environment.
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or self._load_config_from_env()
        self._client: Optional[Langfuse] = None
        self._current_trace_id: Optional[str] = None
        self._session_spans: dict[str, str] = {}

        if self.config.langfuse_enabled:
            if self._validate_langfuse_config():
                self._initialize_langfuse()
            else:
                self.config.langfuse_enabled = False

    def _load_config_from_env(self) -> ObservabilityConfig:
        """Load observability configuration from environment variables."""
        return ObservabilityConfig(
            enabled=os.getenv("OBSERVABILITY_ENABLED", "true").lower() == "true",
            langfuse_enabled=os.getenv("LANGFUSE_ENABLED", "true").lower() == "true",
            langfuse_public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            langfuse_secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            langfuse_host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
            trace_agent_messages=os.getenv("TRACE_AGENT_MESSAGES", "true").lower()
            == "true",
            trace_tool_usage=os.getenv("TRACE_TOOL_USAGE", "true").lower() == "true",
            trace_consensus_detection=os.getenv(
                "TRACE_CONSENSUS_DETECTION", "true"
            ).lower()
            == "true",
            log_token_usage=os.getenv("LOG_TOKEN_USAGE", "true").lower() == "true",
            log_response_times=os.getenv("LOG_RESPONSE_TIMES", "true").lower()
            == "true",
        )

    def _validate_langfuse_config(self) -> bool:
        """
        Validate Langfuse configuration before initialization.

        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.config.langfuse_public_key:
            self.logger.warning("Langfuse public key not configured")
            return False

        if not self.config.langfuse_secret_key:
            self.logger.warning("Langfuse secret key not configured")
            return False

        if not self.config.langfuse_host:
            # Set default host if not configured
            self.config.langfuse_host = "https://cloud.langfuse.com"

        # Validate host URL format
        if not (
            self.config.langfuse_host.startswith("http://")
            or self.config.langfuse_host.startswith("https://")
        ):
            self.logger.warning(
                f"Invalid Langfuse host URL format: {self.config.langfuse_host}"
            )
            return False

        return True

    def _initialize_langfuse(self) -> None:
        """Initialize the Langfuse client."""
        try:
            self._client = Langfuse(
                public_key=self.config.langfuse_public_key,
                secret_key=self.config.langfuse_secret_key,
                host=self.config.langfuse_host,
            )
            self.logger.info("Langfuse tracer initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Langfuse: {e}")
            self.config.langfuse_enabled = False

    def _sanitize_content(self, content: str) -> str:
        """
        Remove sensitive data patterns before tracing.

        This method sanitizes content by removing common patterns that might
        contain sensitive information like API keys, tokens, passwords, etc.

        Args:
            content: Raw content to sanitize

        Returns:
            Sanitized content with sensitive patterns redacted
        """
        if not isinstance(content, str):
            return content

        # Patterns for common sensitive data
        patterns = [
            # API keys and tokens
            (
                r'(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[\'"]?([a-zA-Z0-9_\-/+]{8,})[\'"]?',
                r"\1: [REDACTED]",
            ),
            # Email addresses
            (
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "[EMAIL_REDACTED]",
            ),
            # Common secret patterns
            (r"(?i)(bearer\s+|basic\s+)?[a-zA-Z0-9_\-/+]{20,}", "[TOKEN_REDACTED]"),
            # Phone numbers (simple pattern)
            (r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE_REDACTED]"),
            # Credit card numbers
            (r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[CARD_REDACTED]"),
        ]

        sanitized = content
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized)

        return sanitized

    def _sanitize_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Sanitize dictionary data recursively.

        Args:
            data: Dictionary to sanitize

        Returns:
            Sanitized dictionary
        """
        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self._sanitize_content(value)
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_content(item)
                    if isinstance(item, str)
                    else self._sanitize_dict(item)
                    if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        return sanitized

    def count_tokens(self, text: str, model: str = "cl100k_base") -> int:
        """
        Count tokens in text using tiktoken.

        Args:
            text: Text to count tokens for
            model: Tokenizer encoding to use (default: cl100k_base for GPT-4)

        Returns:
            Number of tokens in the text
        """
        try:
            encoding = tiktoken.get_encoding(model)
            return len(encoding.encode(text))
        except Exception as e:
            self.logger.warning(f"Failed to count tokens using tiktoken: {e}")
            # Fallback to simple character-based estimation
            return len(text) // 4

    @contextmanager
    def trace_discussion_session(self, session: DiscussionSession):
        """
        Context manager for tracing an entire discussion session.

        Args:
            session: Discussion session metadata
        """
        if not self._is_enabled():
            yield None
            return

        trace_name = f"Expert Panel Discussion: {session.topic[:50]}..."

        try:
            # Create a trace context using the session ID
            from langfuse.types import TraceContext

            trace_context = TraceContext(trace_id=session.session_id)

            # Start the main discussion span with the trace context
            with self._client.start_as_current_span(
                name=trace_name,
                trace_context=trace_context,
                metadata={
                    "topic": session.topic,
                    "pattern": session.pattern,
                    "participants": session.participants,
                    "max_rounds": session.max_rounds,
                    "with_human": session.with_human,
                    "human_name": session.human_name,
                },
            ) as span:
                self._current_trace_id = session.session_id
                self.logger.debug(
                    f"Started tracing discussion session: {session.session_id}"
                )
                yield span

        except Exception as e:
            self.logger.error(f"Error in discussion session tracing: {e}")
            yield None
        finally:
            if self._current_trace_id:
                # Update the current trace with final session data
                try:
                    self._client.update_current_trace(
                        metadata={
                            "topic": session.topic,
                            "pattern": session.pattern,
                            "participants": session.participants,
                            "actual_rounds": session.actual_rounds,
                            "duration_ms": session.duration_ms,
                            "total_tokens": session.total_tokens,
                            "consensus_reached": session.consensus_reached,
                            "with_human": session.with_human,
                            "human_name": session.human_name,
                        },
                    )
                except Exception as e:
                    self.logger.error(f"Error updating trace metadata: {e}")
                finally:
                    self._current_trace_id = None

    def trace_agent_interaction(
        self, interaction: AgentInteraction, session_id: str
    ) -> None:
        """
        Trace an individual agent interaction.

        Args:
            interaction: Agent interaction data
            session_id: ID of the discussion session
        """
        if not self._is_enabled() or not self.config.trace_agent_messages:
            return

        try:
            span = self._client.start_span(
                name=f"{interaction.agent_name} - Round {interaction.message_round}",
                metadata={
                    "agent_name": interaction.agent_name,
                    "agent_role": interaction.agent_role,
                    "message_round": interaction.message_round,
                    "token_count": interaction.token_count,
                    "response_time_ms": interaction.response_time_ms,
                    "tools_used": interaction.tools_used,
                    **interaction.metadata,
                },
                input={
                    "message_content": self._sanitize_content(
                        interaction.message_content
                    )
                },
            )

            # End the span immediately since this is logging an already completed interaction
            span.end()

            self.logger.debug(
                f"Traced agent interaction: {interaction.agent_name} - Round {interaction.message_round}"
            )

        except Exception as e:
            self.logger.error(f"Error tracing agent interaction: {e}")

    def trace_consensus_event(self, event: ConsensusEvent) -> None:
        """
        Trace a consensus detection event.

        Args:
            event: Consensus event data
        """
        if not self._is_enabled() or not self.config.trace_consensus_detection:
            return

        try:
            span = self._client.start_span(
                name="Consensus Detection",
                metadata={
                    "consensus_reached": event.consensus_reached,
                    "confidence_score": event.confidence_score,
                    "participants_in_agreement": event.participants_in_agreement,
                    "dissenting_participants": event.dissenting_participants,
                    "detection_time": event.detection_time.isoformat(),
                },
                input={"summary": self._sanitize_content(event.summary)},
            )
            span.end()

            self.logger.debug(
                f"Traced consensus event: consensus_reached={event.consensus_reached}"
            )

        except Exception as e:
            self.logger.error(f"Error tracing consensus event: {e}")

    def trace_tool_usage(self, event: ToolUsageEvent) -> None:
        """
        Trace a tool usage event.

        Args:
            event: Tool usage event data
        """
        if not self._is_enabled() or not self.config.trace_tool_usage:
            return

        try:
            span = self._client.start_span(
                name=f"Tool: {event.tool_name}",
                metadata={
                    "agent_name": event.agent_name,
                    "tool_name": event.tool_name,
                    "execution_time_ms": event.execution_time_ms,
                    "success": event.success,
                    "error_message": event.error_message,
                    "timestamp": event.timestamp.isoformat(),
                },
                input=self._sanitize_dict(event.tool_input),
                output=self._sanitize_dict(event.tool_output)
                if event.tool_output
                else None,
            )
            span.end()

            self.logger.debug(
                f"Traced tool usage: {event.tool_name} by {event.agent_name}"
            )

        except Exception as e:
            self.logger.error(f"Error tracing tool usage: {e}")

    def flush(self) -> None:
        """Flush all pending traces to Langfuse."""
        if self._client and self.config.langfuse_enabled:
            try:
                self._client.flush()
                self.logger.debug("Flushed traces to Langfuse")
            except Exception as e:
                self.logger.error(f"Error flushing traces: {e}")

    def _is_enabled(self) -> bool:
        """Check if tracing is enabled and client is available."""
        return (
            self.config.enabled
            and self.config.langfuse_enabled
            and self._client is not None
        )

    def get_session_url(self, session_id: str) -> Optional[str]:
        """
        Get the Langfuse URL for a specific session.

        Args:
            session_id: ID of the discussion session

        Returns:
            URL to view the session in Langfuse, or None if not available
        """
        if not self._is_enabled():
            return None

        try:
            # Use the client's get_trace_url method if available
            return self._client.get_trace_url(trace_id=session_id)
        except Exception as e:
            self.logger.error(f"Error generating session URL: {e}")
            # Fallback to manual URL construction
            try:
                base_url = self.config.langfuse_host.rstrip("/")
                return f"{base_url}/trace/{session_id}"
            except Exception as e2:
                self.logger.error(f"Error in fallback URL generation: {e2}")
                return None
