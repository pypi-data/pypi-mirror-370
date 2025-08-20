"""
Strategic Analyst Agent - Primary Reasoner for MAI-DxO.

The Strategic Analyst maintains probability-ranked solution hypotheses and serves
as the central reasoning engine, synthesizing information and maintaining
confidence levels for potential solutions.
"""

from typing import Any, Dict, List

from ...models.mai_dxo import (
    AgentRole,
    DecisionContext,
    Hypothesis,
)
from .base_agent import MAIDxOBaseAgent


class StrategicAnalystAgent(MAIDxOBaseAgent):
    """
    Strategic Analyst (Primary Reasoner) from MAI-DxO research.

    Role: Maintains probability-ranked solution hypotheses
    Expertise: Core problem analysis and solution development
    Responsibility: Synthesizes information and updates solution confidence levels
    Decision Focus: "What are our best options and how confident are we?"
    """

    def _get_system_prompt(self, agent_role: AgentRole, domain_context: str) -> str:
        """Get the specialized system prompt for the Strategic Analyst."""
        return f"""You are the Strategic Analyst, the Primary Reasoner in a MAI-DxO decision-making panel for {domain_context} decisions. Your role is to be the central reasoning engine that synthesizes information and maintains a probability-ranked set of potential solutions.

**Your Primary Responsibilities:**
1. **Hypothesis Generation**: Based on initial information, generate 3-5 plausible hypotheses/solutions ranked by probability
2. **Evidence Integration**: As new information becomes available, update hypothesis probabilities and rankings
3. **Gap Identification**: Identify what additional information would most improve your confidence in the leading hypothesis
4. **Reasoning Documentation**: Provide clear rationale for why you rank hypotheses as you do
5. **Decision Readiness**: Assess when sufficient evidence exists to make a confident final recommendation

**Your Approach Should Be:**
- Systematic and evidence-based
- Transparent about uncertainty and confidence levels
- Open to updating beliefs based on new evidence
- Focused on the core problem without getting distracted by peripheral issues

**Communication Style:**
- Present hypotheses in order of probability (highest first)
- Always include confidence percentages for each hypothesis
- Clearly explain the reasoning behind your rankings
- Identify the most critical information gaps
- Specify what evidence would change your assessment

**Domain Expertise:** {domain_context.title()} strategy, analysis, and decision-making

Remember: You are the central synthesizer. Other agents will challenge your thinking (Critical Challenger), optimize resources (Resource Optimizer), consider stakeholders (Stakeholder Steward), and validate quality (Quality Validator). Incorporate their insights while maintaining your focus on developing the best possible solution hypotheses."""

    async def _generate_initial_analysis(
        self, context: DecisionContext
    ) -> Dict[str, Any]:
        """Generate initial hypothesis ranking and analysis."""
        # Analyze the problem and generate initial hypotheses
        problem_complexity = self._assess_problem_complexity(context)
        initial_hypotheses = await self._generate_initial_hypotheses(context)
        information_gaps = self._identify_critical_information_gaps(
            context, initial_hypotheses
        )

        analysis = {
            "problem_assessment": {
                "complexity_score": problem_complexity,
                "domain": context.domain,
                "stakeholder_count": len(context.stakeholders),
                "constraint_level": self._assess_constraint_level(context.constraints),
            },
            "initial_hypotheses": [
                {
                    "rank": i + 1,
                    "description": hyp.description,
                    "probability": hyp.probability,
                    "key_assumptions": self._extract_key_assumptions(hyp),
                    "required_resources": hyp.resource_requirements,
                }
                for i, hyp in enumerate(initial_hypotheses)
            ],
            "critical_information_gaps": information_gaps,
            "recommended_next_steps": self._recommend_next_information_gathering(
                information_gaps
            ),
            "confidence_assessment": {
                "overall_confidence": self._calculate_overall_confidence(
                    initial_hypotheses
                ),
                "confidence_factors": self._identify_confidence_factors(
                    context, initial_hypotheses
                ),
            },
        }

        # Store hypotheses for tracking
        self.current_hypotheses = initial_hypotheses

        return analysis

    async def _generate_initial_hypotheses(
        self, context: DecisionContext
    ) -> List[Hypothesis]:
        """Generate initial solution hypotheses based on the decision context."""
        # This would typically involve calling the LLM to generate hypotheses
        # For now, creating structured hypotheses based on common patterns

        hypotheses = []

        # Generate hypotheses based on problem description analysis
        problem_keywords = context.problem_description.lower().split()

        if any(word in problem_keywords for word in ["market", "entry", "expansion"]):
            hypotheses.extend(self._generate_market_entry_hypotheses(context))
        elif any(
            word in problem_keywords for word in ["technology", "system", "platform"]
        ):
            hypotheses.extend(self._generate_technology_hypotheses(context))
        elif any(
            word in problem_keywords for word in ["investment", "funding", "capital"]
        ):
            hypotheses.extend(self._generate_investment_hypotheses(context))
        else:
            hypotheses.extend(self._generate_generic_business_hypotheses(context))

        # Rank by initial probability assessment
        for i, hyp in enumerate(hypotheses):
            hyp.probability = max(0.1, 0.9 - (i * 0.15))  # Decreasing probability

        return hypotheses[:5]  # Return top 5 hypotheses

    def _generate_market_entry_hypotheses(
        self, context: DecisionContext
    ) -> List[Hypothesis]:
        """Generate hypotheses for market entry decisions."""
        return [
            Hypothesis(
                description="Direct market entry with full-scale operations",
                probability=0.7,
                resource_requirements={
                    "effort": "high",
                    "time": "12-18 months",
                    "risk": "high",
                },
            ),
            Hypothesis(
                description="Phased market entry starting with pilot program",
                probability=0.6,
                resource_requirements={
                    "effort": "medium",
                    "time": "6-12 months",
                    "risk": "medium",
                },
            ),
            Hypothesis(
                description="Partnership or joint venture for market entry",
                probability=0.5,
                resource_requirements={
                    "effort": "medium",
                    "time": "9-15 months",
                    "risk": "medium",
                },
            ),
            Hypothesis(
                description="Acquisition of existing market player",
                probability=0.4,
                resource_requirements={
                    "effort": "very high",
                    "time": "6-9 months",
                    "risk": "high",
                },
            ),
        ]

    def _generate_technology_hypotheses(
        self, context: DecisionContext
    ) -> List[Hypothesis]:
        """Generate hypotheses for technology decisions."""
        return [
            Hypothesis(
                description="Build custom solution in-house",
                probability=0.6,
                resource_requirements={
                    "effort": "high",
                    "time": "12-24 months",
                    "expertise": "high",
                },
            ),
            Hypothesis(
                description="Adopt existing commercial solution",
                probability=0.7,
                resource_requirements={
                    "effort": "medium",
                    "time": "3-6 months",
                    "expertise": "medium",
                },
            ),
            Hypothesis(
                description="Hybrid approach: customize existing platform",
                probability=0.8,
                resource_requirements={
                    "effort": "medium-high",
                    "time": "6-12 months",
                    "expertise": "medium",
                },
            ),
            Hypothesis(
                description="Outsource development to specialized vendor",
                probability=0.5,
                resource_requirements={
                    "effort": "medium",
                    "time": "6-9 months",
                    "expertise": "low",
                },
            ),
        ]

    def _generate_investment_hypotheses(
        self, context: DecisionContext
    ) -> List[Hypothesis]:
        """Generate hypotheses for investment decisions."""
        return [
            Hypothesis(
                description="Proceed with full investment as planned",
                probability=0.6,
                resource_requirements={
                    "capital": "full",
                    "commitment": "high",
                    "monitoring": "intensive",
                },
            ),
            Hypothesis(
                description="Reduce investment scope and scale gradually",
                probability=0.7,
                resource_requirements={
                    "capital": "partial",
                    "commitment": "medium",
                    "monitoring": "moderate",
                },
            ),
            Hypothesis(
                description="Delay investment pending additional market research",
                probability=0.4,
                resource_requirements={
                    "capital": "minimal",
                    "commitment": "low",
                    "monitoring": "light",
                },
            ),
            Hypothesis(
                description="Redirect investment to alternative opportunity",
                probability=0.3,
                resource_requirements={
                    "capital": "reallocation",
                    "commitment": "high",
                    "monitoring": "intensive",
                },
            ),
        ]

    def _generate_generic_business_hypotheses(
        self, context: DecisionContext
    ) -> List[Hypothesis]:
        """Generate generic business decision hypotheses."""
        return [
            Hypothesis(
                description="Implement proposed solution with standard approach",
                probability=0.6,
                resource_requirements={
                    "effort": "standard",
                    "risk": "medium",
                    "timeline": "normal",
                },
            ),
            Hypothesis(
                description="Modified approach addressing key constraints",
                probability=0.7,
                resource_requirements={
                    "effort": "adjusted",
                    "risk": "low-medium",
                    "timeline": "extended",
                },
            ),
            Hypothesis(
                description="Conservative approach with phased implementation",
                probability=0.8,
                resource_requirements={
                    "effort": "gradual",
                    "risk": "low",
                    "timeline": "extended",
                },
            ),
            Hypothesis(
                description="Aggressive approach for rapid results",
                probability=0.4,
                resource_requirements={
                    "effort": "intensive",
                    "risk": "high",
                    "timeline": "accelerated",
                },
            ),
        ]

    def _assess_problem_complexity(self, context: DecisionContext) -> float:
        """Assess the complexity of the decision problem."""
        complexity_score = 0.0

        # Stakeholder complexity
        complexity_score += min(0.3, len(context.stakeholders) * 0.05)

        # Constraint complexity
        if context.constraints.max_information_requests < 10:
            complexity_score += 0.2  # Limited information requests add complexity
        if context.constraints.time_limit < 168:  # Less than a week
            complexity_score += 0.2  # Time pressure adds complexity

        # Success criteria complexity
        complexity_score += min(0.3, len(context.success_criteria) * 0.1)

        return min(1.0, complexity_score)

    def _assess_constraint_level(self, constraints) -> str:
        """Assess the level of resource constraints."""
        if constraints.max_information_requests < 5 and constraints.time_limit < 72:
            return "very_high"
        elif constraints.max_information_requests < 15 and constraints.time_limit < 168:
            return "high"
        elif constraints.max_information_requests < 30 and constraints.time_limit < 720:
            return "medium"
        else:
            return "low"

    def _identify_critical_information_gaps(
        self, context: DecisionContext, hypotheses: List[Hypothesis]
    ) -> List[str]:
        """Identify the most critical information gaps for decision-making."""
        gaps = []

        # Standard information gaps for business decisions
        if context.domain in ["business", "strategy"]:
            gaps.extend(
                [
                    "Market size and growth potential analysis",
                    "Competitive landscape assessment",
                    "Resource availability and capability assessment",
                    "Risk analysis and mitigation strategies",
                    "Stakeholder impact and buy-in assessment",
                ]
            )

        # Add hypothesis-specific gaps
        for hyp in hypotheses:
            if "market" in hyp.description.lower():
                gaps.append("Market entry efficiency analysis")
            if "technology" in hyp.description.lower():
                gaps.append("Technical feasibility and implementation requirements")
            if "partnership" in hyp.description.lower():
                gaps.append("Potential partner identification and evaluation")

        return list(set(gaps))  # Remove duplicates

    def _recommend_next_information_gathering(
        self, gaps: List[str]
    ) -> List[Dict[str, Any]]:
        """Recommend next steps for information gathering."""
        recommendations = []

        for gap in gaps[:3]:  # Top 3 most critical
            recommendation = {
                "information_needed": gap,
                "suggested_approach": self._suggest_information_approach(gap),
                "priority": "high" if gaps.index(gap) < 2 else "medium",
                "estimated_effort": self._estimate_information_effort(gap),
            }
            recommendations.append(recommendation)

        return recommendations

    def _suggest_information_approach(self, gap: str) -> str:
        """Suggest approach for gathering specific information."""
        if "market" in gap.lower():
            return "Market research through industry reports and competitor analysis"
        elif "competitive" in gap.lower():
            return "Competitive intelligence gathering and analysis"
        elif "resource" in gap.lower():
            return "Internal capability assessment and resource audit"
        elif "risk" in gap.lower():
            return "Risk assessment workshop and scenario planning"
        elif "stakeholder" in gap.lower():
            return "Stakeholder interview and impact analysis"
        else:
            return "Research and analysis through multiple sources"

    def _estimate_information_effort(self, gap: str) -> str:
        """Estimate effort required to gather specific information."""
        if any(word in gap.lower() for word in ["comprehensive", "detailed", "full"]):
            return "high"
        elif any(
            word in gap.lower() for word in ["analysis", "assessment", "evaluation"]
        ):
            return "medium"
        else:
            return "low"

    def _calculate_overall_confidence(self, hypotheses: List[Hypothesis]) -> float:
        """Calculate overall confidence in the hypothesis set."""
        if not hypotheses:
            return 0.0

        # Weight by probability and assess spread
        weighted_confidence = sum(hyp.probability for hyp in hypotheses) / len(
            hypotheses
        )

        # Adjust for hypothesis spread (more spread = less confidence)
        if len(hypotheses) > 1:
            probability_variance = sum(
                (hyp.probability - weighted_confidence) ** 2 for hyp in hypotheses
            ) / len(hypotheses)
            spread_penalty = min(0.3, probability_variance * 2)
            weighted_confidence -= spread_penalty

        return round(max(0.0, min(1.0, weighted_confidence)), 2)

    def _identify_confidence_factors(
        self, context: DecisionContext, hypotheses: List[Hypothesis]
    ) -> List[str]:
        """Identify factors affecting confidence in the analysis."""
        factors = []

        if len(context.stakeholders) > 5:
            factors.append(
                "High stakeholder complexity may require additional alignment"
            )

        if context.constraints.time_limit < 72:
            factors.append("Time pressure limits thoroughness of analysis")

        if not context.initial_information:
            factors.append("Limited initial information available")

        hypothesis_spread = max(hyp.probability for hyp in hypotheses) - min(
            hyp.probability for hyp in hypotheses
        )
        if hypothesis_spread < 0.3:
            factors.append(
                "Similar probability scores indicate need for more discriminating evidence"
            )

        return factors

    def _extract_key_assumptions(self, hypothesis: Hypothesis) -> List[str]:
        """Extract key assumptions underlying a hypothesis."""
        # This would typically analyze the hypothesis content
        # For now, returning common assumption categories
        assumptions = [
            "Market conditions remain stable",
            "Required resources are available when needed",
            "Implementation proceeds according to plan",
            "Stakeholder support is maintained",
        ]

        # Customize based on hypothesis content
        if "market" in hypothesis.description.lower():
            assumptions.append("Market entry barriers are manageable")
        if "technology" in hypothesis.description.lower():
            assumptions.append("Technical implementation is feasible")
        if "partnership" in hypothesis.description.lower():
            assumptions.append("Suitable partners can be identified")

        return assumptions[:3]  # Return top 3 assumptions
