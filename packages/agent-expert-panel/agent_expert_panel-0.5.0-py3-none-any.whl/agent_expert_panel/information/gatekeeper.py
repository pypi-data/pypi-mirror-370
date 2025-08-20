"""
Information Gatekeeper implementation for MAI-DxO.

The Information Gatekeeper serves as the critical interface between agents and external
information sources, implementing strategic information revelation and quality assurance
as proven in the Microsoft Research MAI-DxO study.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..models.mai_dxo import (
    AgentRole,
    InformationResponse,
    InformationType,
    ResourceConstraints,
)


class InformationGatekeeper:
    """Controls strategic information revelation and manages information access.

    Key functions from MAI-DxO research:
    1. Strategic Information Revelation: Controls what information is revealed when
    2. Request Tracking: Monitors information gathering requests for each agent
    3. Access Control: Manages permissions for different types of information requests
    4. Quality Assurance: Validates information reliability and relevance

    Attributes:
        constraints: Resource constraints for the decision-making process
        session_start_time: When the information gathering session started
        information_history: List of all information requests and responses
        agent_request_counts: Number of requests made by each agent role
        quality_thresholds: Minimum quality scores required by information type
    """

    def __init__(self, constraints: ResourceConstraints):
        """Initialize the Information Gatekeeper with resource constraints.

        Args:
            constraints: Resource constraints including time limits and quality thresholds
        """
        self.constraints = constraints
        self.session_start_time = datetime.now()
        self.information_history: List[InformationResponse] = []
        self.agent_request_counts: Dict[AgentRole, int] = {
            role: 0 for role in AgentRole
        }

        # Quality thresholds for different information types
        self.quality_thresholds = {
            InformationType.INTERNAL_DELIBERATION: 0.7,
            InformationType.EXTERNAL_RESEARCH: 0.8,
            InformationType.USER_SPECIFIC: 0.6,
        }

    async def process_information_request(
        self,
        requesting_agent: AgentRole,
        query: str,
        context: Dict[str, Any],
        information_type: InformationType,
        priority: float = 0.5,
    ) -> InformationResponse:
        """Process an information request from an agent.

        Implements the core MAI-DxO gatekeeper pattern:
        1. Validate request authorization and limits
        2. Determine optimal information source
        3. Execute information gathering with request tracking
        4. Quality control and bias checking
        5. Return structured information with metadata

        Args:
            requesting_agent: The agent role making the request
            query: The information query or request
            context: Additional context for the information request
            information_type: Type of information being requested
            priority: Priority level of the request (0.0-1.0)

        Returns:
            InformationResponse containing the gathered information and metadata

        Raises:
            ValueError: If agent is not authorized or request limits are exceeded
        """
        # Step 1: Validate request authorization and limits
        if not self._validate_request_authorization(requesting_agent, information_type):
            raise ValueError(
                f"Agent {requesting_agent} not authorized for {information_type}"
            )

        if not self._check_request_limits(requesting_agent):
            raise ValueError(
                f"Agent {requesting_agent} has exceeded maximum information requests"
            )

        # Step 2: Determine optimal information source
        source_type = self._select_information_source(
            query, information_type, context, priority
        )

        # Step 3: Execute information gathering with request tracking
        information_content = await self._gather_information(
            query, source_type, context, information_type
        )

        # Step 4: Quality control and bias checking
        reliability_score = self._assess_information_reliability(
            information_content, source_type, information_type
        )

        # Validate quality meets threshold
        quality_threshold = self.quality_thresholds.get(information_type, 0.7)
        if reliability_score < quality_threshold:
            # Try alternative source if quality is insufficient
            alternative_source = self._get_alternative_source(
                source_type, information_type
            )
            if alternative_source:
                information_content = await self._gather_information(
                    query, alternative_source, context, information_type
                )
                reliability_score = self._assess_information_reliability(
                    information_content, alternative_source, information_type
                )

        # Step 5: Update tracking and return structured response
        self._update_request_tracking(requesting_agent)

        response = InformationResponse(
            query=query,
            information=information_content,
            source_type=source_type,
            reliability_score=reliability_score,
            metadata={
                "requesting_agent": requesting_agent.value,
                "information_type": information_type.value,
                "priority": priority,
                "quality_threshold_met": reliability_score >= quality_threshold,
                "context_keys": list(context.keys()),
            },
            timestamp=datetime.now().isoformat(),
        )

        self.information_history.append(response)
        return response

    def _validate_request_authorization(
        self, requesting_agent: AgentRole, information_type: InformationType
    ) -> bool:
        """Validate that the requesting agent is authorized for this information type.

        Different agents have different information access permissions based on their
        specialized roles in the MAI-DxO architecture.

        Args:
            requesting_agent: The agent role making the request
            information_type: The type of information being requested

        Returns:
            True if the agent is authorized, False otherwise
        """
        # Different agents have different information access permissions
        permissions = {
            AgentRole.STRATEGIC_ANALYST: [
                InformationType.INTERNAL_DELIBERATION,
                InformationType.EXTERNAL_RESEARCH,
                InformationType.USER_SPECIFIC,
            ],
            AgentRole.RESOURCE_OPTIMIZER: [
                InformationType.EXTERNAL_RESEARCH,
                InformationType.USER_SPECIFIC,
            ],
            AgentRole.CRITICAL_CHALLENGER: [
                InformationType.INTERNAL_DELIBERATION,
                InformationType.EXTERNAL_RESEARCH,
            ],
            AgentRole.STAKEHOLDER_STEWARD: [
                InformationType.EXTERNAL_RESEARCH,
                InformationType.USER_SPECIFIC,
            ],
            AgentRole.QUALITY_VALIDATOR: [
                InformationType.INTERNAL_DELIBERATION,
            ],
        }

        return information_type in permissions.get(requesting_agent, [])

    def _check_request_limits(self, requesting_agent: AgentRole) -> bool:
        """Check if the agent has exceeded maximum information request limits.

        Args:
            requesting_agent: The agent role making the request

        Returns:
            True if under the limit, False if limit exceeded
        """
        current_requests = self.agent_request_counts.get(requesting_agent, 0)
        return current_requests < self.constraints.max_information_requests

    def _select_information_source(
        self,
        query: str,
        information_type: InformationType,
        context: Dict[str, Any],
        priority: float,
    ) -> str:
        """Select the optimal information source based on query and constraints.

        Args:
            query: The information query
            information_type: Type of information being requested
            context: Additional context for the request
            priority: Priority level of the request

        Returns:
            String identifier for the selected information source
        """
        if information_type == InformationType.INTERNAL_DELIBERATION:
            return "internal_knowledge"
        elif information_type == InformationType.USER_SPECIFIC:
            return "user_query"
        else:  # EXTERNAL_RESEARCH
            # Select based on query content and priority
            if any(
                word in query.lower() for word in ["market", "competitor", "industry"]
            ):
                return "market_research"
            elif any(
                word in query.lower() for word in ["regulation", "compliance", "legal"]
            ):
                return "regulatory_lookup"
            elif any(
                word in query.lower() for word in ["database", "data", "statistics"]
            ):
                return "database_query"
            else:
                return "web_search"

    async def _gather_information(
        self,
        query: str,
        source_type: str,
        context: Dict[str, Any],
        information_type: InformationType,
    ) -> str:
        """Gather information from the specified source.

        Args:
            query: The information query
            source_type: The type of information source to use
            context: Additional context for the request
            information_type: Type of information being requested

        Returns:
            String containing the gathered information
        """
        # Simulate information gathering with appropriate delays
        if source_type == "internal_knowledge":
            # Simulate internal knowledge lookup
            await asyncio.sleep(0.1)  # Minimal delay for internal processing
            information = f"Internal analysis result for: {query}"

        elif source_type == "user_query":
            # Simulate user interaction
            await asyncio.sleep(0.5)
            information = f"User response needed for: {query}"

        elif source_type == "web_search":
            # Simulate web search
            await asyncio.sleep(1.0)
            information = f"Web search results for: {query}"

        elif source_type == "database_query":
            # Simulate database lookup
            await asyncio.sleep(0.3)
            information = f"Database query results for: {query}"

        elif source_type == "market_research":
            # Simulate market research
            await asyncio.sleep(2.0)
            information = f"Market research findings for: {query}"

        elif source_type == "regulatory_lookup":
            # Simulate regulatory information lookup
            await asyncio.sleep(0.8)
            information = f"Regulatory information for: {query}"

        else:
            # Default fallback
            information = f"Information gathered for: {query}"

        return information

    def _assess_information_reliability(
        self, information: str, source_type: str, information_type: InformationType
    ) -> float:
        """Assess the reliability of the gathered information.

        Args:
            information: The gathered information content
            source_type: The source type used to gather the information
            information_type: The type of information requested

        Returns:
            Reliability score between 0.0 and 1.0
        """
        # Base reliability scores by source type
        source_reliability = {
            "internal_knowledge": 0.9,
            "user_query": 0.8,
            "database_query": 0.95,
            "regulatory_lookup": 0.98,
            "market_research": 0.85,
            "web_search": 0.75,
            "expert_consultation": 0.9,
        }

        base_score = source_reliability.get(source_type, 0.7)

        # Adjust based on information completeness
        if len(information) < 50:
            base_score -= 0.1
        elif len(information) > 200:
            base_score += 0.05

        # Ensure score is within valid range
        return max(0.0, min(1.0, base_score))

    def _get_alternative_source(
        self, failed_source: str, information_type: InformationType
    ) -> Optional[str]:
        """Get alternative information source if primary source fails quality check.

        Args:
            failed_source: The source that failed the quality check
            information_type: The type of information being requested

        Returns:
            Alternative source identifier, or None if no alternative available
        """
        alternatives = {
            "web_search": "database_query",
            "database_query": "web_search",
            "market_research": "web_search",
        }
        return alternatives.get(failed_source)

    def _update_request_tracking(self, requesting_agent: AgentRole) -> None:
        """Update request tracking for the requesting agent and overall session.

        Args:
            requesting_agent: The agent role that made the request
        """
        self.agent_request_counts[requesting_agent] += 1

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of session activity and resource utilization.

        Returns:
            Dictionary containing session statistics and resource usage
        """
        elapsed_time = (
            datetime.now() - self.session_start_time
        ).total_seconds() / 3600  # hours

        return {
            "elapsed_time_hours": elapsed_time,
            "remaining_time_hours": max(
                0.0, self.constraints.time_limit - elapsed_time
            ),
            "agent_request_counts": dict(self.agent_request_counts),
            "total_information_requests": len(self.information_history),
            "requests_per_agent_avg": (
                len(self.information_history) / len(AgentRole)
                if len(AgentRole) > 0
                else 0.0
            ),
            "quality_threshold_compliance": self._calculate_quality_compliance(),
        }

    def _calculate_quality_compliance(self) -> float:
        """Calculate the percentage of requests that met quality thresholds.

        Returns:
            Percentage of requests meeting quality standards (0.0-1.0)
        """
        if not self.information_history:
            return 1.0

        compliant_count = sum(
            1
            for response in self.information_history
            if response.metadata.get("quality_threshold_met", False)
        )

        return compliant_count / len(self.information_history)

    def get_information_history(self) -> List[InformationResponse]:
        """Get the complete history of information requests and responses.

        Returns:
            List of all InformationResponse objects from the session
        """
        return self.information_history.copy()

    def is_request_limit_reached(self) -> bool:
        """Check if any agent has reached their maximum information request limit.

        Returns:
            True if any agent has reached the limit, False otherwise
        """
        return any(
            count >= self.constraints.max_information_requests
            for count in self.agent_request_counts.values()
        )

    def is_time_exhausted(self) -> bool:
        """Check if the time limit is exhausted.

        Returns:
            True if the time limit has been reached, False otherwise
        """
        elapsed_time = (datetime.now() - self.session_start_time).total_seconds() / 3600
        return elapsed_time >= self.constraints.time_limit

    def get_agent_request_status(self, agent_role: AgentRole) -> Dict[str, Any]:
        """Get request status information for a specific agent.

        Args:
            agent_role: The agent role to get status for

        Returns:
            Dictionary containing the agent's request status and limits
        """
        current_requests = self.agent_request_counts.get(agent_role, 0)

        return {
            "agent_role": agent_role.value,
            "requests_made": current_requests,
            "max_requests": self.constraints.max_information_requests,
            "remaining_requests": max(
                0, self.constraints.max_information_requests - current_requests
            ),
            "at_limit": current_requests >= self.constraints.max_information_requests,
        }
