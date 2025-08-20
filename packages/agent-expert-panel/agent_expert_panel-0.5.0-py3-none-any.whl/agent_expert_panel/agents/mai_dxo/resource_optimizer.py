"""
Resource Optimizer Agent - Strategic Planner for MAI-DxO.

The Resource Optimizer selects efficient information gathering actions
and balances thoroughness with practical constraints, optimizing effectiveness
for decision-making activities.
"""

from typing import Any, Dict, List

from ...models.mai_dxo import (
    Action,
    AgentRole,
    DecisionContext,
    InformationType,
)
from .base_agent import MAIDxOBaseAgent


class ResourceOptimizerAgent(MAIDxOBaseAgent):
    """
    Resource Optimizer (Strategic Planner) from MAI-DxO research.

    Role: Selects efficient information gathering actions
    Expertise: Efficiency analysis and resource allocation
    Responsibility: Balances thoroughness with time and resource constraints
    Decision Focus: "What's the highest-value next step within our constraints?"
    """

    def _get_system_prompt(self, agent_role: AgentRole, domain_context: str) -> str:
        """Get the specialized system prompt for the Resource Optimizer."""
        return f"""You are the Resource Optimization Specialist in a MAI-DxO decision-making panel for {domain_context} decisions. Your role is to ensure we achieve the best possible outcome within our resource constraints by selecting the most efficient and high-value actions.

**Your Primary Responsibilities:**
1. **Action Evaluation**: Assess the efficiency ratio of potential information-gathering actions
2. **Priority Ranking**: Rank possible next steps by expected information value per unit resource
3. **Resource Management**: Track resource consumption and ensure we stay within constraints
4. **Efficiency Optimization**: Recommend approaches that maximize progress toward solution
5. **Resource Allocation**: Balance between thoroughness and practical limitations

**Decision Criteria You Should Use:**
- **Information Value**: How much will this action reduce uncertainty?
- **Resource Efficiency**: What is the resource investment per unit of expected information gained?
- **Time Sensitivity**: Are there timing constraints that affect action value?
- **Dependency Management**: Which actions unlock access to other valuable information?
- **Risk Mitigation**: What actions help avoid inefficient mistakes or dead ends?

**Your Analysis Framework:**
- Always present options ranked by value-to-resource ratio
- Consider both direct resource requirements (time, effort) and opportunity costs
- Account for uncertainty and potential for information to be less valuable than expected
- Recommend contingency plans for high-risk, high-value actions
- Balance immediate information needs with long-term decision quality

**Communication Style:**
- Lead with the highest-value recommendations
- Always include efficiency justification
- Specify resource requirements (time, effort, personnel)
- Identify dependencies and prerequisites
- Recommend optimal sequencing of actions

**Domain Expertise:** {domain_context.title()} resource planning, efficiency analysis, and resource optimization

Remember: Other agents will generate hypotheses (Strategic Analyst), challenge assumptions (Critical Challenger), consider stakeholders (Stakeholder Steward), and validate quality (Quality Validator). Your job is to ensure every action we take delivers maximum value for our resource investment."""

    async def _generate_initial_analysis(
        self, context: DecisionContext
    ) -> Dict[str, Any]:
        """Generate initial resource optimization analysis."""
        # Assess available resources and constraints
        resource_assessment = self._assess_available_resources(context)

        # Identify potential actions and their resource requirements
        potential_actions = await self._identify_potential_actions(context)

        # Rank actions by value-to-resource efficiency ratio
        ranked_actions = self._rank_actions_by_efficiency(potential_actions, context)

        # Create resource allocation strategy
        allocation_strategy = self._create_allocation_strategy(context, ranked_actions)

        # Assess risks and contingencies
        risk_assessment = self._assess_resource_risks(context)

        analysis = {
            "resource_assessment": resource_assessment,
            "potential_actions": [
                {
                    "action_id": action.id,
                    "description": action.description,
                    "information_type": action.information_type.value,
                    "expected_value": action.expected_information_gain,
                    "time_required": action.time_required,
                    "value_score": getattr(action, "value_score", 0.5),
                    "priority_rank": ranked_actions.index(action) + 1,
                }
                for action in ranked_actions[:10]  # Top 10 actions
            ],
            "recommended_action_sequence": self._recommend_action_sequence(
                ranked_actions[:5]
            ),
            "resource_allocation_strategy": allocation_strategy,
            "resource_tracking": {
                "time_limit": context.constraints.time_limit,
                "max_information_requests": context.constraints.max_information_requests,
                "recommended_allocation": self._recommend_resource_allocation(context),
                "contingency_reserves": self._calculate_contingency_reserves(context),
            },
            "risk_assessment": risk_assessment,
            "efficiency_metrics": self._calculate_efficiency_metrics(ranked_actions),
        }

        return analysis

    def _assess_available_resources(self, context: DecisionContext) -> Dict[str, Any]:
        """Assess available resources and constraints."""
        constraints = context.constraints

        # Calculate resource availability levels
        time_level = self._categorize_time_level(constraints.time_limit)
        request_level = self._categorize_request_level(
            constraints.max_information_requests
        )

        # Assess resource constraints impact
        constraint_impact = self._assess_constraint_impact(constraints)

        return {
            "time_limit_hours": constraints.time_limit,
            "max_information_requests": constraints.max_information_requests,
            "time_level": time_level,
            "request_level": request_level,
            "quality_threshold": constraints.quality_threshold,
            "confidence_threshold": constraints.confidence_threshold,
            "constraint_impact_score": constraint_impact,
            "resource_utilization_strategy": self._determine_utilization_strategy(
                constraints
            ),
        }

    async def _identify_potential_actions(
        self, context: DecisionContext
    ) -> List[Action]:
        """Identify potential actions for information gathering."""
        actions = []

        # Standard information gathering actions
        standard_actions = [
            # External research actions
            Action(
                description="Comprehensive market research and analysis",
                information_type=InformationType.EXTERNAL_RESEARCH,
                expected_information_gain=0.8,
                time_required=8.0,
            ),
            Action(
                description="Competitive intelligence gathering",
                information_type=InformationType.EXTERNAL_RESEARCH,
                expected_information_gain=0.7,
                time_required=6.0,
            ),
            Action(
                description="Industry expert consultation",
                information_type=InformationType.EXTERNAL_RESEARCH,
                expected_information_gain=0.9,
                time_required=4.0,
            ),
            Action(
                description="Regulatory and compliance research",
                information_type=InformationType.EXTERNAL_RESEARCH,
                expected_information_gain=0.6,
                time_required=3.0,
            ),
            # User-specific information actions
            Action(
                description="Stakeholder interview and requirement gathering",
                information_type=InformationType.USER_SPECIFIC,
                expected_information_gain=0.8,
                time_required=4.0,
            ),
            Action(
                description="Internal capability and resource audit",
                information_type=InformationType.USER_SPECIFIC,
                expected_information_gain=0.7,
                time_required=3.0,
            ),
            Action(
                description="Historical performance data analysis",
                information_type=InformationType.USER_SPECIFIC,
                expected_information_gain=0.6,
                time_required=2.0,
            ),
            # Internal deliberation actions
            Action(
                description="Scenario planning and risk analysis workshop",
                information_type=InformationType.INTERNAL_DELIBERATION,
                expected_information_gain=0.7,
                time_required=6.0,
            ),
            Action(
                description="Decision tree and option analysis",
                information_type=InformationType.INTERNAL_DELIBERATION,
                expected_information_gain=0.6,
                time_required=4.0,
            ),
            Action(
                description="Assumption testing and validation",
                information_type=InformationType.INTERNAL_DELIBERATION,
                expected_information_gain=0.5,
                time_required=2.0,
            ),
        ]

        # Calculate value scores for all actions
        for action in standard_actions:
            action.value_score = self._calculate_value_score(action)

        # Add domain-specific actions based on context
        domain_actions = self._generate_domain_specific_actions(context)
        actions.extend(standard_actions)
        actions.extend(domain_actions)

        return actions

    def _rank_actions_by_efficiency(
        self, actions: List[Action], context: DecisionContext
    ) -> List[Action]:
        """Rank actions by their value-to-resource efficiency ratio."""
        # Calculate efficiency scores considering multiple factors
        for action in actions:
            action.value_score = self._calculate_comprehensive_value_score(
                action, context
            )

        # Sort by value score (descending)
        return sorted(actions, key=lambda x: getattr(x, "value_score", 0), reverse=True)

    def _calculate_value_score(self, action: Action) -> float:
        """Calculate basic time-efficiency value score for an action."""
        if action.time_required <= 0:
            return action.expected_information_gain * 10  # Avoid division by zero

        return action.expected_information_gain / action.time_required

    def _calculate_comprehensive_value_score(
        self, action: Action, context: DecisionContext
    ) -> float:
        """Calculate comprehensive value score considering multiple factors."""
        # Base value-to-time ratio
        base_score = self._calculate_value_score(action)

        # Time efficiency factor
        time_efficiency = action.expected_information_gain / max(
            action.time_required, 0.5
        )

        # Urgency factor based on remaining time
        urgency_factor = 1.0
        if context.constraints.time_limit < 24:  # Less than a day
            urgency_factor = 2.0 if action.time_required <= 2 else 0.5
        elif context.constraints.time_limit < 72:  # Less than 3 days
            urgency_factor = 1.5 if action.time_required <= 6 else 0.7

        # Request efficiency factor - favor actions that don't consume many requests
        request_factor = 1.0
        if action.time_required > context.constraints.time_limit * 0.3:
            request_factor = 0.7  # Penalize very time-consuming actions
        elif action.time_required < context.constraints.time_limit * 0.1:
            request_factor = 1.2  # Bonus for quick actions

        # Information type priority factor
        type_factor = {
            InformationType.INTERNAL_DELIBERATION: 1.1,  # Slight bonus for efficient internal work
            InformationType.USER_SPECIFIC: 1.3,  # High value for user-specific info
            InformationType.EXTERNAL_RESEARCH: 1.0,  # Standard weighting
        }.get(action.information_type, 1.0)

        # Calculate final comprehensive score
        comprehensive_score = (
            base_score * 0.4
            + time_efficiency * 0.2
            + urgency_factor * 0.2
            + request_factor * 0.1
            + type_factor * 0.1
        )

        return round(comprehensive_score, 3)

    def _generate_domain_specific_actions(
        self, context: DecisionContext
    ) -> List[Action]:
        """Generate domain-specific actions based on the decision context."""
        domain_actions = []

        if context.domain in ["business", "strategy"]:
            domain_actions.extend(
                [
                    Action(
                        description="Financial modeling and efficiency analysis",
                        information_type=InformationType.INTERNAL_DELIBERATION,
                        expected_information_gain=0.8,
                        time_required=5.0,
                    ),
                    Action(
                        description="Customer research and market validation",
                        information_type=InformationType.EXTERNAL_RESEARCH,
                        expected_information_gain=0.9,
                        time_required=8.0,
                    ),
                ]
            )

        elif context.domain in ["technology", "technical"]:
            domain_actions.extend(
                [
                    Action(
                        description="Technical feasibility assessment",
                        information_type=InformationType.EXTERNAL_RESEARCH,
                        expected_information_gain=0.9,
                        time_required=6.0,
                    ),
                    Action(
                        description="Architecture and scalability analysis",
                        information_type=InformationType.INTERNAL_DELIBERATION,
                        expected_information_gain=0.7,
                        time_required=4.0,
                    ),
                ]
            )

        # Calculate value scores for domain actions
        for action in domain_actions:
            action.value_score = self._calculate_comprehensive_value_score(
                action, context
            )

        return domain_actions

    def _recommend_action_sequence(
        self, top_actions: List[Action]
    ) -> List[Dict[str, Any]]:
        """Recommend optimal sequence for executing top actions."""
        sequence = []

        for i, action in enumerate(top_actions):
            step = {
                "sequence_order": i + 1,
                "action_description": action.description,
                "rationale": self._generate_action_rationale(action, i),
                "prerequisites": action.prerequisites,
                "expected_duration": action.time_required,
                "parallel_execution_possible": self._can_execute_in_parallel(
                    action, top_actions
                ),
            }
            sequence.append(step)

        return sequence

    def _generate_action_rationale(self, action: Action, sequence_position: int) -> str:
        """Generate rationale for including action in sequence."""
        value_score = getattr(action, "value_score", 0.5)
        if sequence_position == 0:
            return f"Highest value-to-resource ratio ({value_score:.2f}), provides foundation for subsequent decisions"
        elif action.information_type == InformationType.USER_SPECIFIC:
            return "Essential user-specific information needed for accurate analysis"
        elif action.time_required < 3.0:
            return "Quick, high-value action that builds understanding efficiently"
        else:
            return f"Strong value-to-resource ratio ({value_score:.2f}) justifies resource investment"

    def _can_execute_in_parallel(
        self, action: Action, all_actions: List[Action]
    ) -> bool:
        """Determine if action can be executed in parallel with others."""
        # Simple heuristic: user-specific actions often can't be parallel
        if action.information_type == InformationType.USER_SPECIFIC:
            return False

        # Internal deliberation can often be parallel
        if action.information_type == InformationType.INTERNAL_DELIBERATION:
            return True

        # External research can sometimes be parallel
        return action.time_required <= 4.0  # Short actions can be parallel

    def _create_allocation_strategy(
        self, context: DecisionContext, actions: List[Action]
    ) -> Dict[str, Any]:
        """Create resource allocation strategy."""
        constraints = context.constraints

        # Calculate recommended allocations
        high_value_actions = [
            a for a in actions[:5] if getattr(a, "value_score", 0.5) > 1.0
        ]
        total_high_value_time = sum(a.time_required for a in high_value_actions)

        strategy = {
            "immediate_actions_time": min(
                constraints.time_limit * 0.6, total_high_value_time
            ),
            "contingency_time": constraints.time_limit * 0.2,
            "final_phase_time": constraints.time_limit * 0.2,
            "time_allocation": {
                "information_gathering": constraints.time_limit * 0.6,
                "analysis_and_deliberation": constraints.time_limit * 0.3,
                "final_decision_and_validation": constraints.time_limit * 0.1,
            },
            "risk_mitigation_reserves": {
                "request_reserve": int(constraints.max_information_requests * 0.15),
                "time_buffer": constraints.time_limit * 0.15,
            },
        }

        return strategy

    def _recommend_resource_allocation(
        self, context: DecisionContext
    ) -> Dict[str, float]:
        """Recommend how to allocate resources across different categories."""
        total_time = context.constraints.time_limit
        max_requests = context.constraints.max_information_requests

        return {
            "external_research_time": total_time * 0.5,
            "user_engagement_time": total_time * 0.2,
            "internal_analysis_time": total_time * 0.2,
            "validation_time": total_time * 0.1,
            "external_research_requests": int(max_requests * 0.4),
            "user_engagement_requests": int(max_requests * 0.3),
            "internal_requests": int(max_requests * 0.3),
        }

    def _calculate_contingency_reserves(
        self, context: DecisionContext
    ) -> Dict[str, float]:
        """Calculate recommended contingency reserves."""
        return {
            "time_contingency": context.constraints.time_limit * 0.2,
            "request_contingency": context.constraints.max_information_requests * 0.15,
            "quality_buffer": 0.1,  # Reserve for ensuring quality thresholds
        }

    def _assess_resource_risks(self, context: DecisionContext) -> Dict[str, Any]:
        """Assess risks related to resource constraints."""
        risks = []

        constraints = context.constraints

        if constraints.time_limit < 24:
            risks.append(
                {
                    "risk": "Severe time pressure may force suboptimal decisions",
                    "severity": "high",
                    "mitigation": "Prioritize immediate-impact actions and parallel execution",
                }
            )

        if constraints.max_information_requests < 5:
            risks.append(
                {
                    "risk": "Very limited information requests may create analysis gaps",
                    "severity": "medium",
                    "mitigation": "Focus on high-value information requests and internal deliberation",
                }
            )

        if constraints.quality_threshold > 0.8:
            risks.append(
                {
                    "risk": "High quality threshold may slow decision process",
                    "severity": "medium",
                    "mitigation": "Ensure sufficient time allocation for quality validation",
                }
            )

        return {
            "identified_risks": risks,
            "overall_risk_level": self._calculate_overall_risk_level(constraints),
            "risk_mitigation_strategy": self._develop_risk_mitigation_strategy(risks),
        }

    def _calculate_efficiency_metrics(self, actions: List[Action]) -> Dict[str, Any]:
        """Calculate efficiency metrics for the action recommendations."""
        if not actions:
            return {}

        top_5_actions = actions[:5]

        return {
            "average_value_score": sum(
                getattr(a, "value_score", 0.5) for a in top_5_actions
            )
            / len(top_5_actions),
            "total_expected_information_gain": sum(
                a.expected_information_gain for a in top_5_actions
            ),
            "total_time_required": sum(a.time_required for a in top_5_actions),
            "time_efficiency_ratio": (
                sum(a.expected_information_gain for a in top_5_actions)
                / sum(a.time_required for a in top_5_actions)
                if sum(a.time_required for a in top_5_actions) > 0
                else 0
            ),
            "average_time_per_action": (
                sum(a.time_required for a in top_5_actions) / len(top_5_actions)
                if top_5_actions
                else 0
            ),
        }

    def _categorize_request_level(self, max_requests: int) -> str:
        """Categorize information request limit for strategic planning."""
        if max_requests < 5:
            return "very_limited"
        elif max_requests < 10:
            return "limited"
        elif max_requests < 20:
            return "moderate"
        elif max_requests < 50:
            return "substantial"
        else:
            return "extensive"

    def _categorize_time_level(self, time_hours: float) -> str:
        """Categorize time availability level."""
        if time_hours < 4:
            return "critical"
        elif time_hours < 24:
            return "urgent"
        elif time_hours < 72:
            return "tight"
        elif time_hours < 168:
            return "moderate"
        else:
            return "comfortable"

    def _assess_constraint_impact(self, constraints) -> float:
        """Assess overall impact of constraints on decision quality."""
        impact_score = 0.0

        # Request limit impact
        if constraints.max_information_requests < 5:
            impact_score += 0.4
        elif constraints.max_information_requests < 10:
            impact_score += 0.2

        # Time impact
        if constraints.time_limit < 24:
            impact_score += 0.4
        elif constraints.time_limit < 72:
            impact_score += 0.2

        # Quality threshold impact
        if constraints.quality_threshold > 0.8:
            impact_score += 0.1

        return min(1.0, impact_score)

    def _determine_utilization_strategy(self, constraints) -> str:
        """Determine optimal resource utilization strategy."""
        request_level = self._categorize_request_level(
            constraints.max_information_requests
        )
        time_level = self._categorize_time_level(constraints.time_limit)

        if request_level in ["very_limited", "limited"] and time_level in [
            "critical",
            "urgent",
        ]:
            return "focus_on_essentials"
        elif request_level in ["moderate", "substantial"] and time_level in [
            "tight",
            "moderate",
        ]:
            return "balanced_approach"
        elif request_level == "extensive" or time_level == "comfortable":
            return "comprehensive_analysis"
        else:
            return "adaptive_strategy"

    def _calculate_overall_risk_level(self, constraints) -> str:
        """Calculate overall risk level based on constraints."""
        risk_score = self._assess_constraint_impact(constraints)

        if risk_score >= 0.7:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"

    def _develop_risk_mitigation_strategy(
        self, risks: List[Dict[str, Any]]
    ) -> List[str]:
        """Develop overall risk mitigation strategy."""
        strategies = []

        high_severity_risks = [r for r in risks if r.get("severity") == "high"]

        if high_severity_risks:
            strategies.append(
                "Prioritize highest-value actions to maximize limited resources"
            )
            strategies.append(
                "Implement parallel execution where possible to save time"
            )
            strategies.append(
                "Focus on user-specific information that only they can provide"
            )

        strategies.append("Maintain contingency reserves for unexpected opportunities")
        strategies.append(
            "Continuously monitor resource utilization and adjust strategy"
        )

        return strategies
