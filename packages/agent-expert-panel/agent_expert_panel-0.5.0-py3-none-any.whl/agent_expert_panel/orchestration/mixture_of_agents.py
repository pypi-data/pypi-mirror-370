"""
MAI-DxO implementation using Mixture of Agents pattern.

This implementation runs all five specialized agents in parallel, then uses
an aggregation layer to synthesize their outputs into a final decision.
"""

import asyncio
from typing import Any, Dict, List, Optional

from autogen_core.models import ChatCompletionClient

from ..agents.mai_dxo import (
    CriticalChallengerAgent,
    QualityValidatorAgent,
    ResourceOptimizerAgent,
    StakeholderStewardAgent,
    StrategicAnalystAgent,
)
from ..information.gatekeeper import InformationGatekeeper
from ..models.mai_dxo import (
    AgentRole,
    DecisionContext,
    DecisionResult,
    OrchestrationMethod,
    QualityMetrics,
    ResourceConstraints,
)


class MixtureOfAgentsMAIDxO:
    """
    MAI-DxO implementation using Mixture of Agents pattern.

    This orchestrator runs all specialized agents in parallel, then uses
    sophisticated aggregation and synthesis techniques to combine their
    diverse perspectives into a robust final decision.
    """

    def __init__(
        self,
        model_client: ChatCompletionClient,
        domain_context: str = "business",
        aggregation_method: str = "weighted_synthesis",
        confidence_threshold: float = 0.7,
        **kwargs,
    ):
        """Initialize the Mixture of Agents MAI-DxO orchestrator."""
        self.model_client = model_client
        self.domain_context = domain_context
        self.aggregation_method = aggregation_method
        self.confidence_threshold = confidence_threshold
        self.orchestration_method = OrchestrationMethod.MIXTURE_OF_AGENTS

        # Will be initialized when starting a decision process
        self.information_gatekeeper: Optional[InformationGatekeeper] = None
        self.agents: Dict[AgentRole, Any] = {}

        # Mixture of Agents specific settings
        self.agent_weights = self._initialize_agent_weights()
        self.consensus_threshold = 0.6
        self.parallel_execution = True

    def _initialize_agent_weights(self) -> Dict[AgentRole, float]:
        """Initialize weights for each agent in the mixture."""
        return {
            AgentRole.STRATEGIC_ANALYST: 0.25,  # Primary reasoner gets higher weight
            AgentRole.RESOURCE_OPTIMIZER: 0.20,  # Resource efficiency is crucial
            AgentRole.CRITICAL_CHALLENGER: 0.20,  # Bias prevention is critical
            AgentRole.STAKEHOLDER_STEWARD: 0.20,  # Governance and ethics matter
            AgentRole.QUALITY_VALIDATOR: 0.15,  # Final validation role
        }

    async def process_decision(
        self,
        context: DecisionContext,
        constraints: Optional[ResourceConstraints] = None,
    ) -> DecisionResult:
        """
        Process a decision using the Mixture of Agents MAI-DxO orchestration.

        The Mixture of Agents approach:
        1. Initialize all agents with shared information access
        2. Run agents in parallel for independent analysis
        3. Collect and normalize agent outputs
        4. Apply weighted aggregation to synthesize perspectives
        5. Validate consensus and handle disagreements
        6. Generate final decision with confidence assessment
        """
        # Use provided constraints or defaults from context
        if constraints is None:
            constraints = context.constraints

        # Initialize the decision process
        await self._initialize_decision_process(context, constraints)

        # Execute Mixture of Agents workflow
        decision_result = await self._execute_mixture_workflow(context)

        return decision_result

    async def _initialize_decision_process(
        self, context: DecisionContext, constraints: ResourceConstraints
    ) -> None:
        """Initialize the information gatekeeper and all agents."""
        # Initialize shared information gatekeeper
        self.information_gatekeeper = InformationGatekeeper(constraints)

        # Initialize all five specialized agents with shared resources
        self.agents = {
            AgentRole.STRATEGIC_ANALYST: StrategicAnalystAgent(
                name="Strategic Analyst",
                model_client=self.model_client,
                agent_role=AgentRole.STRATEGIC_ANALYST,
                domain_context=self.domain_context,
                information_gatekeeper=self.information_gatekeeper,
            ),
            AgentRole.RESOURCE_OPTIMIZER: ResourceOptimizerAgent(
                name="Resource Optimizer",
                model_client=self.model_client,
                agent_role=AgentRole.RESOURCE_OPTIMIZER,
                domain_context=self.domain_context,
                information_gatekeeper=self.information_gatekeeper,
            ),
            AgentRole.CRITICAL_CHALLENGER: CriticalChallengerAgent(
                name="Critical Challenger",
                model_client=self.model_client,
                agent_role=AgentRole.CRITICAL_CHALLENGER,
                domain_context=self.domain_context,
                information_gatekeeper=self.information_gatekeeper,
            ),
            AgentRole.STAKEHOLDER_STEWARD: StakeholderStewardAgent(
                name="Stakeholder Steward",
                model_client=self.model_client,
                agent_role=AgentRole.STAKEHOLDER_STEWARD,
                domain_context=self.domain_context,
                information_gatekeeper=self.information_gatekeeper,
            ),
            AgentRole.QUALITY_VALIDATOR: QualityValidatorAgent(
                name="Quality Validator",
                model_client=self.model_client,
                agent_role=AgentRole.QUALITY_VALIDATOR,
                domain_context=self.domain_context,
                information_gatekeeper=self.information_gatekeeper,
            ),
        }

    async def _execute_mixture_workflow(
        self, context: DecisionContext
    ) -> DecisionResult:
        """Execute the Mixture of Agents workflow."""
        # Phase 1: Parallel Agent Execution
        agent_outputs = await self._execute_agents_in_parallel(context)

        # Phase 2: Output Normalization and Analysis
        normalized_outputs = self._normalize_agent_outputs(agent_outputs)

        # Phase 3: Cross-Agent Consensus Analysis
        consensus_analysis = self._analyze_consensus(normalized_outputs)

        # Phase 4: Weighted Aggregation
        aggregated_decision = self._aggregate_agent_perspectives(
            normalized_outputs, consensus_analysis
        )

        # Phase 5: Disagreement Resolution (if needed)
        if consensus_analysis["consensus_level"] < self.consensus_threshold:
            resolved_decision = await self._resolve_disagreements(
                context, normalized_outputs, consensus_analysis, aggregated_decision
            )
        else:
            resolved_decision = aggregated_decision

        # Phase 6: Final Validation and Confidence Assessment
        final_result = await self._finalize_mixture_decision(
            context, resolved_decision, normalized_outputs
        )

        return final_result

    async def _execute_agents_in_parallel(
        self, context: DecisionContext
    ) -> Dict[AgentRole, Any]:
        """Execute all agents in parallel for independent analysis."""
        if self.parallel_execution:
            # Run all agents concurrently
            tasks = []
            for role, agent in self.agents.items():
                task = asyncio.create_task(agent.process_decision_context(context))
                tasks.append((role, task))

            # Wait for all agents to complete
            agent_outputs = {}
            for role, task in tasks:
                try:
                    output = await task
                    agent_outputs[role] = output
                    print(f"✓ {role.value} completed analysis")
                except Exception as e:
                    print(f"✗ {role.value} failed: {e}")
                    agent_outputs[role] = None
        else:
            # Run agents sequentially (fallback)
            agent_outputs = {}
            for role, agent in self.agents.items():
                try:
                    output = await agent.process_decision_context(context)
                    agent_outputs[role] = output
                except Exception as e:
                    print(f"✗ {role.value} failed: {e}")
                    agent_outputs[role] = None

        return agent_outputs

    def _normalize_agent_outputs(
        self, agent_outputs: Dict[AgentRole, Any]
    ) -> Dict[str, Any]:
        """Normalize agent outputs for aggregation."""
        normalized = {
            "agent_perspectives": {},
            "hypothesis_rankings": {},
            "confidence_levels": {},
            "key_insights": {},
            "risk_assessments": {},
            "resource_evaluations": {},
        }

        for role, output in agent_outputs.items():
            if output is None:
                continue

            # Extract normalized data from each agent output
            agent_data = {
                "agent_role": role,
                "confidence": getattr(output, "confidence_level", 0.5),
                "insights": self._extract_insights_from_output(output, role),
                "recommendations": self._extract_recommendations_from_output(
                    output, role
                ),
                "concerns": self._extract_concerns_from_output(output, role),
            }

            normalized["agent_perspectives"][role.value] = agent_data
            normalized["confidence_levels"][role.value] = agent_data["confidence"]
            normalized["key_insights"][role.value] = agent_data["insights"]

        return normalized

    def _extract_insights_from_output(self, output: Any, role: AgentRole) -> List[str]:
        """Extract key insights from agent output."""
        insights = []

        if hasattr(output, "content") and isinstance(output.content, dict):
            content = output.content

            if role == AgentRole.STRATEGIC_ANALYST:
                if "initial_hypotheses" in content:
                    insights.append(
                        f"Generated {len(content['initial_hypotheses'])} strategic hypotheses"
                    )
                if "confidence_assessment" in content:
                    conf = content["confidence_assessment"].get("overall_confidence", 0)
                    insights.append(f"Strategic confidence level: {conf:.1%}")

            elif role == AgentRole.RESOURCE_OPTIMIZER:
                if "resource_tracking" in content:
                    insights.append("Resource optimization analysis completed")
                if "efficiency_metrics" in content:
                    insights.append("Resource efficiency evaluated")

            elif role == AgentRole.CRITICAL_CHALLENGER:
                if "bias_detection" in content:
                    biases = content["bias_detection"].get(
                        "identified_framing_biases", []
                    )
                    insights.append(f"Identified {len(biases)} potential biases")
                if "challenge_priorities" in content:
                    challenges = content["challenge_priorities"]
                    insights.append(
                        f"Prioritized {len(challenges)} critical challenges"
                    )

            elif role == AgentRole.STAKEHOLDER_STEWARD:
                if "stakeholder_mapping" in content:
                    mapping = content["stakeholder_mapping"]
                    primary = len(mapping.get("primary_stakeholders", {}))
                    insights.append(f"Analyzed {primary} primary stakeholder groups")
                if "ethical_assessment" in content:
                    insights.append("Ethical and governance assessment completed")

            elif role == AgentRole.QUALITY_VALIDATOR:
                if "quality_criteria" in content:
                    insights.append("Quality validation framework established")
                if "validation_methodology" in content:
                    insights.append("Systematic validation methodology defined")

        # Default insight if none extracted
        if not insights:
            insights.append(
                f"{role.value.replace('_', ' ').title()} analysis completed"
            )

        return insights

    def _extract_recommendations_from_output(
        self, output: Any, role: AgentRole
    ) -> List[str]:
        """Extract recommendations from agent output."""
        recommendations = []

        if hasattr(output, "content") and isinstance(output.content, dict):
            content = output.content

            # Look for common recommendation patterns
            if "recommended_next_steps" in content:
                next_steps = content["recommended_next_steps"]
                if isinstance(next_steps, list):
                    recommendations.extend(
                        [
                            step.get("information_needed", str(step))
                            for step in next_steps[:3]
                        ]
                    )

            if "governance_recommendations" in content:
                gov_recs = content["governance_recommendations"]
                if isinstance(gov_recs, list):
                    recommendations.extend(gov_recs[:2])

        # Default recommendation if none found
        if not recommendations:
            recommendations.append(
                f"Continue with {role.value.replace('_', ' ')} approach"
            )

        return recommendations[:3]  # Limit to top 3

    def _extract_concerns_from_output(self, output: Any, role: AgentRole) -> List[str]:
        """Extract concerns from agent output."""
        concerns = []

        if hasattr(output, "content") and isinstance(output.content, dict):
            content = output.content

            if role == AgentRole.CRITICAL_CHALLENGER:
                if "red_team_questions" in content:
                    questions = content["red_team_questions"]
                    concerns.extend(
                        questions[:2] if isinstance(questions, list) else []
                    )

            # Look for risk assessments
            if "risk_assessment" in content:
                risk_data = content["risk_assessment"]
                if isinstance(risk_data, dict) and "identified_risks" in risk_data:
                    risks = risk_data["identified_risks"]
                    concerns.extend([risk.get("risk", str(risk)) for risk in risks[:2]])

        return concerns[:2]  # Limit to top 2 concerns

    def _analyze_consensus(self, normalized_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze consensus across agent perspectives."""
        agent_perspectives = normalized_outputs["agent_perspectives"]
        confidence_levels = normalized_outputs["confidence_levels"]

        # Calculate consensus metrics
        confidence_values = list(confidence_levels.values())
        avg_confidence = (
            sum(confidence_values) / len(confidence_values) if confidence_values else 0
        )
        confidence_variance = (
            sum((c - avg_confidence) ** 2 for c in confidence_values)
            / len(confidence_values)
            if confidence_values
            else 0
        )

        # Assess agreement level
        agreement_threshold = 0.2  # Confidence levels within 0.2 considered aligned
        aligned_agents = sum(
            1
            for c in confidence_values
            if abs(c - avg_confidence) <= agreement_threshold
        )
        consensus_level = (
            aligned_agents / len(confidence_values) if confidence_values else 0
        )

        # Analyze agent perspectives for content similarity and thematic alignment
        perspective_analysis = self._analyze_perspective_content(agent_perspectives)

        # Identify outliers
        outliers = []
        for agent_role, confidence in confidence_levels.items():
            if abs(confidence - avg_confidence) > agreement_threshold:
                outliers.append(
                    {
                        "agent": agent_role,
                        "confidence": confidence,
                        "deviation": abs(confidence - avg_confidence),
                        "perspective_summary": agent_perspectives.get(
                            agent_role, {}
                        ).get("summary", "No summary available"),
                    }
                )

        return {
            "consensus_level": consensus_level,
            "average_confidence": avg_confidence,
            "confidence_variance": confidence_variance,
            "aligned_agents": aligned_agents,
            "total_agents": len(confidence_values),
            "outliers": outliers,
            "perspective_analysis": perspective_analysis,
            "agreement_assessment": "high"
            if consensus_level >= 0.8
            else "medium"
            if consensus_level >= 0.6
            else "low",
        }

    def _analyze_perspective_content(
        self, agent_perspectives: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze agent perspectives for content similarity and thematic alignment."""
        if not agent_perspectives:
            return {"similarity_score": 0, "common_themes": [], "divergent_points": []}

        # Extract key themes and recommendations from each perspective
        all_themes = []
        all_recommendations = []
        agent_summaries = {}

        for agent_role, perspective in agent_perspectives.items():
            # Extract themes (simplified keyword extraction)
            if isinstance(perspective, dict):
                summary = perspective.get("summary", "")
                recommendations = perspective.get("recommendations", [])
                # key_points could be used for future enhanced analysis
            else:
                summary = str(perspective)
                recommendations = []

            agent_summaries[agent_role] = summary

            # Simple theme extraction (in practice, this could use NLP)
            themes = self._extract_themes_from_text(summary)
            all_themes.extend(themes)
            all_recommendations.extend(
                recommendations if isinstance(recommendations, list) else []
            )

        # Find common themes (themes mentioned by multiple agents)
        theme_counts = {}
        for theme in all_themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1

        common_themes = [theme for theme, count in theme_counts.items() if count > 1]

        # Calculate similarity score based on common themes
        total_themes = len(set(all_themes))
        similarity_score = len(common_themes) / total_themes if total_themes > 0 else 0

        # Identify divergent points (themes mentioned by only one agent)
        divergent_points = [
            theme for theme, count in theme_counts.items() if count == 1
        ]

        return {
            "similarity_score": similarity_score,
            "common_themes": common_themes[:5],  # Top 5 common themes
            "divergent_points": divergent_points[:5],  # Top 5 divergent points
            "theme_distribution": theme_counts,
            "perspective_alignment": "high"
            if similarity_score >= 0.7
            else "medium"
            if similarity_score >= 0.4
            else "low",
            "total_unique_themes": total_themes,
        }

    def _extract_themes_from_text(self, text: str) -> List[str]:
        """Extract key themes from text (simplified implementation)."""
        if not text:
            return []

        # Simple keyword-based theme extraction
        # In practice, this could use more sophisticated NLP
        keywords = [
            "risk",
            "opportunity",
            "stakeholder",
            "resource",
            "timeline",
            "cost",
            "benefit",
            "implementation",
            "strategy",
            "compliance",
            "efficiency",
            "quality",
            "innovation",
            "sustainability",
            "scalability",
            "security",
            "performance",
            "user",
            "customer",
        ]

        text_lower = text.lower()
        found_themes = []

        for keyword in keywords:
            if keyword in text_lower:
                found_themes.append(keyword)

        return found_themes

    def _aggregate_agent_perspectives(
        self, normalized_outputs: Dict[str, Any], consensus_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Aggregate agent perspectives using weighted synthesis."""
        agent_perspectives = normalized_outputs["agent_perspectives"]

        # Apply weighted aggregation based on agent weights and confidence
        weighted_insights = []
        weighted_recommendations = []
        total_confidence = 0
        total_weight = 0

        for agent_role_str, perspective in agent_perspectives.items():
            agent_role = AgentRole(agent_role_str)
            base_weight = self.agent_weights.get(agent_role, 0.2)
            confidence = perspective["confidence"]

            # Adjust weight based on confidence
            adjusted_weight = base_weight * (0.5 + confidence)
            total_weight += adjusted_weight
            total_confidence += confidence * adjusted_weight

            # Weight insights and recommendations
            for insight in perspective["insights"]:
                weighted_insights.append(
                    {
                        "insight": insight,
                        "weight": adjusted_weight,
                        "agent": agent_role_str,
                    }
                )

            for rec in perspective["recommendations"]:
                weighted_recommendations.append(
                    {
                        "recommendation": rec,
                        "weight": adjusted_weight,
                        "agent": agent_role_str,
                    }
                )

        # Calculate aggregate confidence
        aggregate_confidence = (
            total_confidence / total_weight if total_weight > 0 else 0
        )

        # Sort insights and recommendations by weight
        top_insights = sorted(
            weighted_insights, key=lambda x: x["weight"], reverse=True
        )[:8]
        top_recommendations = sorted(
            weighted_recommendations, key=lambda x: x["weight"], reverse=True
        )[:5]

        return {
            "aggregation_method": self.aggregation_method,
            "aggregate_confidence": aggregate_confidence,
            "consensus_level": consensus_analysis["consensus_level"],
            "top_insights": top_insights,
            "top_recommendations": top_recommendations,
            "synthesis_quality": "high"
            if consensus_analysis["consensus_level"] >= 0.7
            else "medium",
        }

    async def _resolve_disagreements(
        self,
        context: DecisionContext,
        normalized_outputs: Dict[str, Any],
        consensus_analysis: Dict[str, Any],
        aggregated_decision: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Resolve disagreements when consensus is low."""
        outliers = consensus_analysis["outliers"]

        # Strategy 1: Give more weight to higher-confidence agents
        high_confidence_agents = [
            agent
            for agent in outliers
            if agent["confidence"] > consensus_analysis["average_confidence"]
        ]

        if high_confidence_agents:
            # Boost weight of high-confidence outliers
            adjusted_decision = aggregated_decision.copy()
            adjusted_decision["disagreement_resolution"] = "high_confidence_boost"
            adjusted_decision["confidence_adjustment"] = +0.1
            return adjusted_decision

        # Strategy 2: Conservative approach when uncertainty is high
        if consensus_analysis["confidence_variance"] > 0.1:
            conservative_decision = aggregated_decision.copy()
            conservative_decision["aggregate_confidence"] *= 0.8  # Reduce confidence
            conservative_decision["disagreement_resolution"] = "conservative_adjustment"
            conservative_decision["recommendation"] = (
                "Additional analysis recommended due to agent disagreement"
            )
            return conservative_decision

        # Default: Return original aggregated decision
        return aggregated_decision

    async def _finalize_mixture_decision(
        self,
        context: DecisionContext,
        resolved_decision: Dict[str, Any],
        normalized_outputs: Dict[str, Any],
    ) -> DecisionResult:
        """Finalize the mixture decision into a complete DecisionResult."""
        # Get best hypothesis from Strategic Analyst
        strategic_analyst = self.agents[AgentRole.STRATEGIC_ANALYST]
        final_hypothesis = None
        alternative_hypotheses = []

        if (
            hasattr(strategic_analyst, "current_hypotheses")
            and strategic_analyst.current_hypotheses
        ):
            sorted_hypotheses = sorted(
                strategic_analyst.current_hypotheses,
                key=lambda h: h.probability,
                reverse=True,
            )
            final_hypothesis = sorted_hypotheses[0]
            alternative_hypotheses = sorted_hypotheses[1:3]

        # Create quality metrics based on mixture analysis
        quality_metrics = self._create_mixture_quality_metrics(
            resolved_decision, normalized_outputs
        )

        # Calculate final confidence
        base_confidence = resolved_decision.get("aggregate_confidence", 0.7)
        consensus_bonus = resolved_decision.get("consensus_level", 0.6) * 0.1
        confidence_adjustment = resolved_decision.get("confidence_adjustment", 0.0)
        final_confidence = min(
            0.95, base_confidence + consensus_bonus + confidence_adjustment
        )

        # Get session and performance data
        session_summary = (
            self.information_gatekeeper.get_session_summary()
            if self.information_gatekeeper
            else {}
        )

        # Create implementation plan
        implementation_plan = self._create_mixture_implementation_plan(
            final_hypothesis, context, resolved_decision, normalized_outputs
        )

        # Create bias report
        bias_report = self._create_mixture_bias_report(normalized_outputs)

        return DecisionResult(
            context=context,
            final_hypothesis=final_hypothesis,
            alternative_hypotheses=alternative_hypotheses,
            quality_metrics=quality_metrics,
            total_time=session_summary.get("elapsed_time_hours", 0.0),
            agent_outputs=self._collect_all_agent_outputs(),
            information_gathered=self.information_gatekeeper.get_information_history()
            if self.information_gatekeeper
            else [],
            bias_report=bias_report,
            implementation_plan=implementation_plan,
            confidence_level=final_confidence,
        )

    def _create_mixture_quality_metrics(
        self, resolved_decision: Dict[str, Any], normalized_outputs: Dict[str, Any]
    ) -> QualityMetrics:
        """Create quality metrics based on mixture analysis."""
        base_confidence = resolved_decision.get("aggregate_confidence", 0.7)
        consensus_level = resolved_decision.get("consensus_level", 0.6)

        return QualityMetrics(
            decision_confidence=base_confidence,
            evidence_quality_score=0.75,  # High due to multiple perspectives
            bias_risk_assessment=0.2,  # Lower due to mixture approach
            implementation_feasibility=0.7 + (consensus_level * 0.1),
            stakeholder_alignment=0.7,
            logical_consistency=0.7 + (consensus_level * 0.15),
            completeness=0.85,  # High due to comprehensive multi-agent analysis
        )

    def _create_mixture_implementation_plan(
        self,
        hypothesis,
        context: DecisionContext,
        resolved_decision: Dict[str, Any],
        normalized_outputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create implementation plan based on mixture analysis."""
        if not hypothesis:
            return {
                "status": "no_hypothesis_available",
                "recommendation": "Insufficient consensus for decision - require additional analysis",
            }

        top_recommendations = resolved_decision.get("top_recommendations", [])

        plan = {
            "selected_approach": hypothesis.description
            if hasattr(hypothesis, "description")
            else str(hypothesis),
            "synthesis_methodology": f"Mixture of {len(normalized_outputs['agent_perspectives'])} specialized agents",
            "consensus_level": resolved_decision.get("consensus_level", 0.6),
            "aggregation_confidence": resolved_decision.get(
                "aggregate_confidence", 0.7
            ),
            "implementation_strategy": "Multi-perspective validated approach",
            "top_recommendations": [
                rec["recommendation"] for rec in top_recommendations
            ],
            "contributing_agents": list(
                normalized_outputs["agent_perspectives"].keys()
            ),
            "implementation_phases": [
                "Multi-agent synthesis validation",
                "Consensus-based planning execution",
                "Parallel specialist monitoring",
                "Continuous mixture-based optimization",
            ],
            "success_criteria": context.success_criteria,
            "mixture_benefits": [
                "Multiple independent perspectives reduce single-point bias",
                "Parallel analysis increases decision robustness",
                "Weighted aggregation optimizes expertise utilization",
                "Consensus analysis ensures decision reliability",
            ],
        }

        # Add disagreement resolution info if applicable
        if "disagreement_resolution" in resolved_decision:
            plan["disagreement_resolution"] = resolved_decision[
                "disagreement_resolution"
            ]
            plan["consensus_notes"] = (
                "Disagreements resolved through systematic weighting"
            )

        return plan

    def _create_mixture_bias_report(self, normalized_outputs: Dict[str, Any]):
        """Create bias report based on mixture analysis."""
        from ..models.mai_dxo import BiasReport, BiasWarning, BiasType

        warnings = []
        agent_perspectives = normalized_outputs["agent_perspectives"]

        # Look for challenger insights
        if "critical_challenger" in agent_perspectives:
            challenger_insights = agent_perspectives["critical_challenger"]["insights"]
            for insight in challenger_insights[:2]:
                warnings.append(
                    BiasWarning(
                        bias_type=BiasType.CONFIRMATION,
                        description=f"Challenger identified: {insight}",
                        severity=0.4,
                        mitigation_strategy="Addressed through mixture consensus analysis",
                    )
                )

        return BiasReport(
            indicators=warnings,
            overall_risk_score=0.15,  # Very low due to mixture approach
            mitigation_strategies=[
                "Multiple independent agent perspectives prevent single-point bias",
                "Parallel execution eliminates sequential influence bias",
                "Weighted aggregation balances diverse viewpoints",
                "Consensus analysis identifies and resolves disagreements",
                "Critical challenger specifically addresses systematic biases",
            ],
        )

    def _collect_all_agent_outputs(self) -> List[Any]:
        """Collect outputs from all agents."""
        all_outputs = []
        for agent in self.agents.values():
            if hasattr(agent, "agent_outputs"):
                all_outputs.extend(agent.agent_outputs)
        return all_outputs

    def get_orchestration_summary(self) -> Dict[str, Any]:
        """Get summary of the Mixture of Agents orchestration process."""
        agent_performance = {}
        for role, agent in self.agents.items():
            if hasattr(agent, "get_performance_metrics"):
                agent_performance[role.value] = agent.get_performance_metrics()

        return {
            "orchestration_method": self.orchestration_method.value,
            "domain_context": self.domain_context,
            "aggregation_method": self.aggregation_method,
            "agent_weights": {
                role.value: weight for role, weight in self.agent_weights.items()
            },
            "consensus_threshold": self.consensus_threshold,
            "confidence_threshold": self.confidence_threshold,
            "parallel_execution": self.parallel_execution,
            "agent_performance": agent_performance,
            "mixture_strategy": "Parallel multi-agent execution with weighted consensus aggregation",
            "process_summary": {
                "execution_approach": "All agents run in parallel for independent analysis",
                "aggregation_quality": "Weighted synthesis with consensus validation",
                "decision_quality": "robust_multi_perspective_analysis",
                "orchestration_benefits": [
                    "Multiple independent perspectives",
                    "Parallel execution efficiency",
                    "Systematic bias prevention",
                    "Consensus-based validation",
                    "Weighted expertise optimization",
                ],
            },
        }
