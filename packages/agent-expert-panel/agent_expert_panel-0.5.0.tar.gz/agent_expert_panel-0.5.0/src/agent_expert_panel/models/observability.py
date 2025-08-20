"""
Observability Models

Pydantic models for tracing and observability in the agent expert panel.
"""

from datetime import datetime
from typing import Any, Optional
from enum import Enum

from pydantic import BaseModel, Field


class TraceEventType(str, Enum):
    """Types of trace events that can be recorded."""

    DISCUSSION_START = "discussion_start"
    DISCUSSION_END = "discussion_end"
    AGENT_MESSAGE = "agent_message"
    CONSENSUS_DETECTION = "consensus_detection"
    TOOL_USAGE = "tool_usage"
    RECOMMENDATION_SYNTHESIS = "recommendation_synthesis"
    HUMAN_INTERACTION = "human_interaction"


class AgentInteraction(BaseModel):
    """Model for tracking individual agent interactions."""

    agent_name: str = Field(description="Name of the agent")
    agent_role: str = Field(description="Role/type of the agent")
    message_content: str = Field(description="Content of the agent's message")
    message_round: int = Field(description="Round number in the discussion")
    token_count: Optional[int] = Field(
        default=None, description="Number of tokens in the message"
    )
    response_time_ms: Optional[float] = Field(
        default=None, description="Response time in milliseconds"
    )
    tools_used: Optional[list[str]] = Field(
        default_factory=list, description="Tools used by the agent"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class DiscussionSession(BaseModel):
    """Model for tracking entire discussion sessions."""

    session_id: str = Field(description="Unique identifier for the discussion session")
    topic: str = Field(description="Discussion topic")
    pattern: str = Field(description="Discussion pattern used")
    participants: list[str] = Field(description="List of participating agents")
    max_rounds: int = Field(description="Maximum number of rounds configured")
    actual_rounds: int = Field(description="Actual number of rounds completed")
    start_time: datetime = Field(description="When the discussion started")
    end_time: Optional[datetime] = Field(
        default=None, description="When the discussion ended"
    )
    duration_ms: Optional[float] = Field(
        default=None, description="Total discussion duration in milliseconds"
    )
    total_tokens: Optional[int] = Field(
        default=None, description="Total tokens used in discussion"
    )
    consensus_reached: bool = Field(
        default=False, description="Whether consensus was reached"
    )
    with_human: bool = Field(default=False, description="Whether human participated")
    human_name: Optional[str] = Field(
        default=None, description="Name of human participant"
    )


class ConsensusEvent(BaseModel):
    """Model for tracking consensus detection events."""

    session_id: str = Field(description="Discussion session identifier")
    consensus_reached: bool = Field(description="Whether consensus was detected")
    confidence_score: Optional[float] = Field(
        default=None, description="Confidence in consensus detection"
    )
    participants_in_agreement: list[str] = Field(description="Agents that agreed")
    dissenting_participants: list[str] = Field(
        default_factory=list, description="Agents that disagreed"
    )
    summary: str = Field(description="Summary of the consensus")
    detection_time: datetime = Field(description="When consensus was detected")


class ToolUsageEvent(BaseModel):
    """Model for tracking tool usage events."""

    session_id: str = Field(description="Discussion session identifier")
    agent_name: str = Field(description="Agent that used the tool")
    tool_name: str = Field(description="Name of the tool used")
    tool_input: dict[str, Any] = Field(description="Input parameters to the tool")
    tool_output: Optional[dict[str, Any]] = Field(
        default=None, description="Output from the tool"
    )
    execution_time_ms: Optional[float] = Field(
        default=None, description="Tool execution time in milliseconds"
    )
    success: bool = Field(
        default=True, description="Whether tool execution was successful"
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if tool failed"
    )
    timestamp: datetime = Field(description="When the tool was used")


class ObservabilityConfig(BaseModel):
    """Configuration for observability settings."""

    enabled: bool = Field(default=True, description="Whether observability is enabled")
    langfuse_enabled: bool = Field(
        default=True, description="Whether Langfuse tracing is enabled"
    )
    langfuse_public_key: Optional[str] = Field(
        default=None, description="Langfuse public key"
    )
    langfuse_secret_key: Optional[str] = Field(
        default=None, description="Langfuse secret key"
    )
    langfuse_host: Optional[str] = Field(default=None, description="Langfuse host URL")
    trace_agent_messages: bool = Field(
        default=True, description="Whether to trace individual agent messages"
    )
    trace_tool_usage: bool = Field(
        default=True, description="Whether to trace tool usage"
    )
    trace_consensus_detection: bool = Field(
        default=True, description="Whether to trace consensus detection"
    )
    log_token_usage: bool = Field(
        default=True, description="Whether to log token usage"
    )
    log_response_times: bool = Field(
        default=True, description="Whether to log response times"
    )
