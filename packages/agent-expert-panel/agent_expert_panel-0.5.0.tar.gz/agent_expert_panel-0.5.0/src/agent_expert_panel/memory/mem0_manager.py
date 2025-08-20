"""
Mem0 Memory Manager for Agent Expert Panel

This module implements intelligent memory management using Mem0 to help agents:
- Learn from past conversation patterns that worked well
- Remember user preferences and context
- Optimize research strategies based on historical success
- Maintain knowledge continuity across sessions
"""

import logging
import uuid
from datetime import datetime
from typing import Any
from pathlib import Path

from pydantic import BaseModel, Field
import importlib.util

from ..models.virtual_panel import VirtualPanelResult, ResearchTask

# Check if Mem0 is available
MEM0_AVAILABLE = False
Mem0Memory = None
MemoryContent = None

if importlib.util.find_spec("autogen_ext.memory.mem0") is not None:
    from autogen_ext.memory.mem0 import Mem0Memory
    from autogen_core.memory import MemoryContent

    MEM0_AVAILABLE = True

logger = logging.getLogger(__name__)


class MemoryEntry(BaseModel):
    """Structure for a memory entry in the system."""

    content: str
    category: str  # conversation_pattern, user_preference, research_strategy, domain_knowledge
    domain: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    session_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Mem0Manager:
    """
    Enhanced Mem0 memory manager for the Agent Expert Panel system.

    This manager provides intelligent memory capabilities to help agents:
    - Learn successful conversation patterns
    - Remember user context and preferences
    - Optimize research and decision-making strategies
    - Maintain knowledge continuity across sessions
    """

    def __init__(
        self,
        user_id: str | None = None,
        memory_path: Path | None = None,
        enable_cloud: bool = False,
        api_key: str | None = None,
    ):
        """
        Initialize the Mem0 memory manager.

        Args:
            user_id: Unique identifier for the user (for memory isolation)
            memory_path: Path for local memory storage (if using local mode)
            enable_cloud: Whether to use cloud-based Mem0 (requires API key)
            api_key: API key for cloud-based Mem0
        """
        self.logger = logging.getLogger(__name__)
        self.user_id = user_id or f"user_{uuid.uuid4().hex[:8]}"
        self.enable_cloud = enable_cloud
        self.api_key = api_key

        # Configure memory storage
        if memory_path:
            self.memory_path = Path(memory_path)
            self.memory_path.mkdir(parents=True, exist_ok=True)
            self.config = {"path": str(self.memory_path / "mem0.db")}
        else:
            # Use in-memory storage for local development
            self.config = {"path": ":memory:"}

        self.memory: Mem0Memory | None = None
        self.is_initialized = False

        self.logger.info(f"Mem0 Manager initialized for user: {self.user_id}")

    async def initialize(self) -> bool:
        """
        Initialize the Mem0 memory system.

        Returns:
            True if initialization was successful, False otherwise
        """
        if not MEM0_AVAILABLE:
            self.logger.warning(
                "Mem0 is not available. Install with: pip install autogen-ext[mem0-local]"
            )
            return False

        try:
            if self.enable_cloud:
                if not self.api_key:
                    self.logger.error("API key required for cloud-based Mem0")
                    return False

                self.memory = Mem0Memory(
                    user_id=self.user_id, is_cloud=True, api_key=self.api_key
                )
            else:
                self.memory = Mem0Memory(
                    user_id=self.user_id, is_cloud=False, config=self.config
                )

            self.is_initialized = True
            self.logger.info("Mem0 memory system initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Mem0: {e}")
            self.is_initialized = False
            return False

    async def add_conversation_pattern(
        self,
        pattern_description: str,
        outcome_quality: str,  # "successful", "partially_successful", "failed"
        domain: str,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Store a conversation pattern and its outcome for future learning.

        Args:
            pattern_description: Description of the conversation pattern
            outcome_quality: Quality of the outcome
            domain: Domain context (business, technology, etc.)
            session_id: Session identifier
            metadata: Additional context data

        Returns:
            True if successfully stored
        """
        if not self.is_initialized:
            await self.initialize()
            if not self.is_initialized:
                return False

        try:
            content = f"Conversation pattern in {domain}: {pattern_description}. Outcome: {outcome_quality}"

            entry = MemoryEntry(
                content=content,
                category="conversation_pattern",
                domain=domain,
                confidence=self._calculate_pattern_confidence(outcome_quality),
                session_id=session_id,
                metadata=metadata or {},
            )

            memory_content = MemoryContent(
                content=entry.model_dump_json(), mime_type="application/json"
            )
            await self.memory.add(memory_content)

            self.logger.info(
                f"Added conversation pattern for domain '{domain}': {outcome_quality}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to add conversation pattern: {e}")
            return False

    async def add_user_preference(
        self,
        preference: str,
        context: str,
        domain: str | None = None,
        confidence: float = 1.0,
    ) -> bool:
        """
        Store user preferences for personalized interactions.

        Args:
            preference: The user preference
            context: Context in which this preference applies
            domain: Relevant domain
            confidence: Confidence in this preference (0.0-1.0)

        Returns:
            True if successfully stored
        """
        if not self.is_initialized:
            await self.initialize()
            if not self.is_initialized:
                return False

        try:
            content = f"User preference: {preference}. Context: {context}"
            if domain:
                content += f". Domain: {domain}"

            entry = MemoryEntry(
                content=content,
                category="user_preference",
                domain=domain,
                confidence=confidence,
            )

            memory_content = MemoryContent(
                content=entry.model_dump_json(), mime_type="application/json"
            )
            await self.memory.add(memory_content)

            self.logger.info(f"Added user preference: {preference}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add user preference: {e}")
            return False

    async def add_research_strategy(
        self,
        query: str,
        strategy: str,
        effectiveness_score: float,
        domain: str,
        research_results: dict[str, Any] | None = None,
    ) -> bool:
        """
        Store research strategies and their effectiveness for optimization.

        Args:
            query: Original research query
            strategy: Research strategy used
            effectiveness_score: Score indicating how effective the strategy was (0.0-1.0)
            domain: Problem domain
            research_results: Optional research results metadata

        Returns:
            True if successfully stored
        """
        if not self.is_initialized:
            await self.initialize()
            if not self.is_initialized:
                return False

        try:
            content = (
                f"Research strategy for query '{query}' in {domain}: {strategy}. "
                f"Effectiveness: {effectiveness_score:.2f}"
            )

            metadata = {"effectiveness_score": effectiveness_score}
            if research_results:
                metadata["results_summary"] = research_results

            entry = MemoryEntry(
                content=content,
                category="research_strategy",
                domain=domain,
                confidence=effectiveness_score,
                metadata=metadata,
            )

            memory_content = MemoryContent(
                content=entry.model_dump_json(), mime_type="application/json"
            )
            await self.memory.add(memory_content)

            self.logger.info(
                f"Added research strategy with effectiveness {effectiveness_score:.2f}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to add research strategy: {e}")
            return False

    async def add_domain_knowledge(
        self, knowledge: str, domain: str, source: str, confidence: float = 1.0
    ) -> bool:
        """
        Store domain-specific knowledge for future reference.

        Args:
            knowledge: The knowledge to store
            domain: Domain context
            source: Source of the knowledge
            confidence: Confidence in the knowledge (0.0-1.0)

        Returns:
            True if successfully stored
        """
        if not self.is_initialized:
            await self.initialize()
            if not self.is_initialized:
                return False

        try:
            content = f"Domain knowledge in {domain}: {knowledge}. Source: {source}"

            entry = MemoryEntry(
                content=content,
                category="domain_knowledge",
                domain=domain,
                confidence=confidence,
                metadata={"source": source},
            )

            memory_content = MemoryContent(
                content=entry.model_dump_json(), mime_type="application/json"
            )
            await self.memory.add(memory_content)

            self.logger.info(f"Added domain knowledge for {domain}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add domain knowledge: {e}")
            return False

    async def query_conversation_patterns(
        self, domain: str, query: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant conversation patterns for the given domain and query.

        Args:
            domain: Domain context
            query: Query to search for relevant patterns
            limit: Maximum number of patterns to return

        Returns:
            List of relevant conversation patterns
        """
        if not self.is_initialized:
            await self.initialize()
            if not self.is_initialized:
                return []

        try:
            search_query = f"conversation patterns in {domain} for {query}"
            results = await self.memory.query(search_query, limit=limit)

            patterns = []
            for result in results:
                if "conversation_pattern" in result.content:
                    patterns.append(
                        {
                            "content": result.content,
                            "relevance": getattr(result, "score", 1.0),
                        }
                    )

            self.logger.info(
                f"Retrieved {len(patterns)} conversation patterns for {domain}"
            )
            return patterns

        except Exception as e:
            self.logger.error(f"Failed to query conversation patterns: {e}")
            return []

    async def query_user_preferences(
        self, context: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Retrieve user preferences relevant to the given context.

        Args:
            context: Context to search for relevant preferences
            limit: Maximum number of preferences to return

        Returns:
            List of relevant user preferences
        """
        if not self.is_initialized:
            await self.initialize()
            if not self.is_initialized:
                return []

        try:
            search_query = f"user preferences for {context}"
            results = await self.memory.query(search_query, limit=limit)

            preferences = []
            for result in results:
                if "user_preference" in result.content:
                    preferences.append(
                        {
                            "content": result.content,
                            "relevance": getattr(result, "score", 1.0),
                        }
                    )

            self.logger.info(f"Retrieved {len(preferences)} user preferences")
            return preferences

        except Exception as e:
            self.logger.error(f"Failed to query user preferences: {e}")
            return []

    async def query_research_strategies(
        self, domain: str, query_type: str, limit: int = 3
    ) -> list[dict[str, Any]]:
        """
        Retrieve effective research strategies for the given domain and query type.

        Args:
            domain: Problem domain
            query_type: Type of query or research needed
            limit: Maximum number of strategies to return

        Returns:
            List of effective research strategies
        """
        if not self.is_initialized:
            await self.initialize()
            if not self.is_initialized:
                return []

        try:
            search_query = f"research strategies for {query_type} in {domain}"
            results = await self.memory.query(search_query, limit=limit)

            strategies = []
            for result in results:
                if "research_strategy" in result.content:
                    strategies.append(
                        {
                            "content": result.content,
                            "relevance": getattr(result, "score", 1.0),
                        }
                    )

            # Sort by effectiveness score if available
            strategies.sort(key=lambda x: x.get("relevance", 0), reverse=True)

            self.logger.info(
                f"Retrieved {len(strategies)} research strategies for {domain}"
            )
            return strategies

        except Exception as e:
            self.logger.error(f"Failed to query research strategies: {e}")
            return []

    async def query_domain_knowledge(
        self, domain: str, topic: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Retrieve domain-specific knowledge relevant to the topic.

        Args:
            domain: Domain context
            topic: Specific topic to search for
            limit: Maximum number of knowledge entries to return

        Returns:
            List of relevant domain knowledge
        """
        if not self.is_initialized:
            await self.initialize()
            if not self.is_initialized:
                return []

        try:
            search_query = f"domain knowledge about {topic} in {domain}"
            results = await self.memory.query(search_query, limit=limit)

            knowledge = []
            for result in results:
                if "domain_knowledge" in result.content:
                    knowledge.append(
                        {
                            "content": result.content,
                            "relevance": getattr(result, "score", 1.0),
                        }
                    )

            self.logger.info(
                f"Retrieved {len(knowledge)} domain knowledge entries for {topic}"
            )
            return knowledge

        except Exception as e:
            self.logger.error(f"Failed to query domain knowledge: {e}")
            return []

    async def learn_from_session(
        self, session_result: VirtualPanelResult, user_feedback: str | None = None
    ) -> bool:
        """
        Learn from a completed session to improve future performance.

        Args:
            session_result: Results from a completed virtual panel session
            user_feedback: Optional user feedback on the session quality

        Returns:
            True if learning was successful
        """
        if not self.is_initialized:
            await self.initialize()
            if not self.is_initialized:
                return False

        try:
            # Determine outcome quality from the session
            outcome_quality = self._assess_session_quality(
                session_result, user_feedback
            )

            # Extract and store conversation patterns
            pattern_description = self._extract_conversation_pattern(session_result)
            await self.add_conversation_pattern(
                pattern_description=pattern_description,
                outcome_quality=outcome_quality,
                domain=session_result.knowledge_artifacts[0]
                if session_result.knowledge_artifacts
                else "general",
                session_id=str(session_result.start_time),
                metadata={
                    "total_rounds": session_result.total_rounds,
                    "participants": session_result.participants,
                    "user_feedback": user_feedback,
                },
            )

            # Store research effectiveness
            for task in session_result.research_tasks:
                if task.status == "completed" and task.results:
                    effectiveness = self._calculate_research_effectiveness(task)
                    await self.add_research_strategy(
                        query=task.description,
                        strategy=f"Agent: {task.agent_assigned}",
                        effectiveness_score=effectiveness,
                        domain=session_result.knowledge_artifacts[0]
                        if session_result.knowledge_artifacts
                        else "general",
                        research_results=task.results,
                    )

            self.logger.info(
                f"Learned from session with {len(session_result.research_tasks)} research tasks"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to learn from session: {e}")
            return False

    async def clear_memory(self, category: str | None = None) -> bool:
        """
        Clear memory entries, optionally filtered by category.

        Args:
            category: Optional category to filter deletion

        Returns:
            True if successful
        """
        if not self.is_initialized:
            await self.initialize()
            if not self.is_initialized:
                return False

        try:
            if category:
                # Note: Mem0 doesn't have category-specific deletion, so this is a limitation
                self.logger.warning(
                    "Category-specific deletion not supported by Mem0, clearing all memory"
                )

            await self.memory.clear()
            self.logger.info("Memory cleared successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to clear memory: {e}")
            return False

    def _calculate_pattern_confidence(self, outcome_quality: str) -> float:
        """Calculate confidence score based on outcome quality."""
        quality_scores = {"successful": 1.0, "partially_successful": 0.7, "failed": 0.3}
        return quality_scores.get(outcome_quality, 0.5)

    def _assess_session_quality(
        self, session_result: VirtualPanelResult, user_feedback: str | None
    ) -> str:
        """Assess the quality of a session based on results and feedback."""
        # Simple heuristic - can be enhanced with more sophisticated analysis
        if user_feedback and any(
            word in user_feedback.lower() for word in ["excellent", "great", "perfect"]
        ):
            return "successful"
        elif user_feedback and any(
            word in user_feedback.lower() for word in ["poor", "bad", "terrible"]
        ):
            return "failed"
        elif session_result.final_solution and len(session_result.final_solution) > 100:
            return "successful"
        elif session_result.total_rounds > 10:
            return "failed"  # Too many rounds might indicate confusion
        else:
            return "partially_successful"

    def _extract_conversation_pattern(self, session_result: VirtualPanelResult) -> str:
        """Extract meaningful conversation patterns from session results."""
        pattern_elements = []

        # Analyze action sequence
        action_sequence = [
            action.action_type.value for action in session_result.actions_taken
        ]
        pattern_elements.append(f"Action sequence: {' -> '.join(action_sequence)}")

        # Analyze research tasks
        if session_result.research_tasks:
            research_agents = [
                task.agent_assigned for task in session_result.research_tasks
            ]
            pattern_elements.append(
                f"Research agents used: {', '.join(set(research_agents))}"
            )

        # Analyze rounds
        pattern_elements.append(f"Completed in {session_result.total_rounds} rounds")

        return "; ".join(pattern_elements)

    def _calculate_research_effectiveness(self, task: ResearchTask) -> float:
        """Calculate the effectiveness of a research task."""
        # Simple heuristic based on results quality
        if not task.results:
            return 0.0

        # Check for key indicators of good research
        effectiveness = 0.5  # Base score

        if "key_findings" in task.results and task.results["key_findings"]:
            effectiveness += 0.3

        if "sources" in task.results and len(task.results.get("sources", [])) > 2:
            effectiveness += 0.2

        return min(effectiveness, 1.0)


# Factory function for easy initialization
async def create_mem0_manager(
    user_id: str | None = None,
    memory_path: Path | None = None,
    enable_cloud: bool = False,
    api_key: str | None = None,
) -> Mem0Manager | None:
    """
    Create and initialize a Mem0 memory manager.

    Args:
        user_id: Unique identifier for the user
        memory_path: Path for local memory storage
        enable_cloud: Whether to use cloud-based Mem0
        api_key: API key for cloud-based Mem0

    Returns:
        Initialized Mem0Manager or None if unavailable
    """
    manager = Mem0Manager(
        user_id=user_id,
        memory_path=memory_path,
        enable_cloud=enable_cloud,
        api_key=api_key,
    )

    success = await manager.initialize()
    if success:
        return manager
    else:
        logger.warning("Mem0 not available, memory features will be disabled")
        return None
