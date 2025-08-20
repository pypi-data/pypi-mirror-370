"""
Virtual Expert Panel models and enums.

This module defines the data models for the Virtual Expert Panel-style orchestrator,
inspired by Microsoft's MAI-DxO pattern but generalized for any domain.
"""

from enum import Enum
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class VirtualPanelAction(Enum):
    """Available actions for the Virtual Panel to take."""

    ASK_QUESTION = "ask_question"  # Request user-specific information not available through research
    REQUEST_TEST = "request_test"  # Perform web research to fill knowledge base gaps
    PROVIDE_SOLUTION = "provide_solution"  # Give final answer/solution


class ConversationState(Enum):
    """Current state of the virtual panel conversation."""

    INITIALIZING = "initializing"  # Setting up the discussion
    DELIBERATING = "deliberating"  # Agents discussing internally
    AWAITING_USER = "awaiting_user"  # Waiting for user response
    RESEARCHING = "researching"  # Performing research/tests
    CONCLUDING = "concluding"  # Providing final solution


class PanelAction(BaseModel):
    """Represents a single action taken by the Virtual Panel."""

    action_type: VirtualPanelAction
    content: str  # The question, test description, or solution
    reasoning: str  # Why this action was chosen
    timestamp: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)  # Additional context/data


class ResearchTask(BaseModel):
    """Represents a research or analysis task to be performed."""

    task_id: str
    description: str  # What needs to be researched
    agent_assigned: str  # Which agent will handle this
    status: str = "pending"  # pending, in_progress, completed, failed
    results: dict[str, Any] = Field(default_factory=dict)  # Research findings
    timestamp: datetime = Field(default_factory=datetime.now)


class VirtualPanelResult(BaseModel):
    """Result of a Virtual Panel discussion session."""

    original_query: str  # The user's original question/problem
    final_solution: str | None  # Final answer if reached
    conversation_history: list[dict[str, Any]]  # Full conversation log
    actions_taken: list[PanelAction]  # All panel actions
    research_tasks: list[ResearchTask]  # All research performed
    knowledge_artifacts: list[str]  # Documents/data collected
    session_state: ConversationState
    total_rounds: int
    participants: list[str]  # Agent names involved
    metadata: dict[str, Any] = Field(default_factory=dict)
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: datetime | None = None


class KnowledgeBase(BaseModel):
    """Represents the dynamic knowledge base for a session."""

    domain: str  # Problem domain (e.g., "medical", "technology")
    documents: list[dict[str, Any]] = Field(
        default_factory=list
    )  # Retrieved/analyzed documents
    web_research: list[dict[str, Any]] = Field(
        default_factory=list
    )  # Web search results and analysis
    facts: list[dict[str, Any]] = Field(
        default_factory=list
    )  # Extracted facts and insights
    entities: list[dict[str, Any]] = Field(
        default_factory=list
    )  # Key entities and relationships
    summary: str = ""  # Overall knowledge summary
    confidence_score: float = 0.0  # Confidence in knowledge completeness

    def add_document(
        self,
        title: str,
        content: str,
        source: str,
        metadata: dict[str, Any] | None = None,
    ):
        """Add a document to the knowledge base."""
        doc = {
            "title": title,
            "content": content,
            "source": source,
            "timestamp": datetime.now(),
            "metadata": metadata or {},
        }
        self.documents.append(doc)

    def add_web_result(self, query: str, results: list[dict[str, Any]]):
        """Add web search results to the knowledge base."""
        web_entry = {"query": query, "results": results, "timestamp": datetime.now()}
        self.web_research.append(web_entry)

    def extract_fact(self, fact: str, source: str, confidence: float = 1.0):
        """Extract and store a fact."""
        fact_entry = {
            "fact": fact,
            "source": source,
            "confidence": confidence,
            "timestamp": datetime.now(),
        }
        self.facts.append(fact_entry)


class OrchestratorDecision(BaseModel):
    """Represents a decision made by the orchestrator agent."""

    decision: VirtualPanelAction
    rationale: str  # Why this decision was made
    confidence: float  # Confidence in the decision (0.0-1.0)
    panel_consensus: bool  # Whether panel reached consensus
    dissenting_opinions: list[str] = Field(
        default_factory=list
    )  # Any dissenting agent opinions
    required_info: list[str] = Field(
        default_factory=list
    )  # What info is needed (for ask_question)
    research_plan: list[str] = Field(
        default_factory=list
    )  # Research steps (for request_test)
