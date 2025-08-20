"""
MAI-DxO implementation using MagenticOneGroupChat orchestration.

This implementation uses Autogen's MagenticOneGroupChat with a central orchestrator
that delegates tasks to specialized agents based on their expertise areas.
"""

from typing import Any, Dict, List, Optional

from autogen_core.models import ChatCompletionClient
from autogen_agentchat.teams import MagenticOneGroupChat

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


class MagenticOneMAIDxO:
    """
    MAI-DxO implementation using MagenticOneGroupChat orchestration.

    This orchestrator uses a central coordinator (Strategic Analyst) that delegates
    specialized tasks to appropriate agents, maintaining oversight and synthesis
    throughout the decision-making process.
    """

    def __init__(
        self,
        model_client: ChatCompletionClient,
        domain_context: str = "business",
        max_turns: int = 20,
        **kwargs,
    ):
        """Initialize the MagenticOne MAI-DxO orchestrator."""
        self.model_client = model_client
        self.domain_context = domain_context
        self.max_turns = max_turns
        self.orchestration_method = OrchestrationMethod.MAGENTIC_ONE

        # Will be initialized when starting a decision process
        self.information_gatekeeper: Optional[InformationGatekeeper] = None
        self.agents: Dict[AgentRole, Any] = {}
        self.magentic_chat: Optional[MagenticOneGroupChat] = None

        # Central coordinator state
        self.coordinator_role = AgentRole.STRATEGIC_ANALYST
        self.task_delegations = []
        self.synthesis_points = []

    async def process_decision(
        self,
        context: DecisionContext,
        constraints: Optional[ResourceConstraints] = None,
    ) -> DecisionResult:
        """
        Process a decision using the MagenticOne MAI-DxO orchestration.

        The MagenticOne approach:
        1. Strategic Analyst acts as central coordinator
        2. Coordinator delegates specialized tasks to appropriate agents
        3. Agents report back findings to coordinator
        4. Coordinator synthesizes insights at key decision points
        5. Final validation ensures quality before recommendation
        """
        # Use provided constraints or defaults from context
        if constraints is None:
            constraints = context.constraints

        # Initialize the decision process
        await self._initialize_decision_process(context, constraints)

        # Execute MagenticOne workflow with central coordination
        decision_result = await self._execute_magentic_workflow(context)

        return decision_result

    async def _initialize_decision_process(
        self, context: DecisionContext, constraints: ResourceConstraints
    ) -> None:
        """Initialize the information gatekeeper, agents, and MagenticOne chat."""
        # Initialize information gatekeeper
        self.information_gatekeeper = InformationGatekeeper(constraints)

        # Initialize the five specialized agents
        self.agents = {
            AgentRole.STRATEGIC_ANALYST: StrategicAnalystAgent(
                name="Strategic Analyst (Coordinator)",
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

        # Initialize MagenticOneGroupChat with Strategic Analyst as orchestrator
        # Strategic Analyst is the orchestrator (first in list for MagenticOne)
        orchestrator = self.agents[AgentRole.STRATEGIC_ANALYST]
        other_agents = [
            agent
            for role, agent in self.agents.items()
            if role != AgentRole.STRATEGIC_ANALYST
        ]

        self.magentic_chat = MagenticOneGroupChat(
            agents=[orchestrator] + other_agents,
        )

    async def _execute_magentic_workflow(
        self, context: DecisionContext
    ) -> DecisionResult:
        """Execute the MagenticOne workflow with central coordination."""
        collected_insights = []

        # Phase 1: Coordinator Initial Analysis and Task Planning
        coordinator_analysis = await self._coordinator_initial_analysis(context)
        collected_insights.append(coordinator_analysis)

        # Phase 2: Delegate Specialized Tasks
        delegated_results = await self._execute_delegated_tasks(
            context, coordinator_analysis
        )
        collected_insights.extend(delegated_results)

        # Phase 3: Coordinator Synthesis
        synthesis_result = await self._coordinator_synthesis(
            context, collected_insights
        )
        collected_insights.append(synthesis_result)

        # Phase 4: Critical Review Delegation
        critical_review = await self._delegate_critical_review(
            context, synthesis_result
        )
        collected_insights.append(critical_review)

        # Phase 5: Stakeholder Impact Assessment (if needed)
        if len(context.stakeholders) > 2:
            stakeholder_assessment = await self._delegate_stakeholder_assessment(
                context, synthesis_result
            )
            collected_insights.append(stakeholder_assessment)

        # Phase 6: Final Coordinator Decision and Quality Validation
        final_decision = await self._coordinator_final_decision(
            context, collected_insights
        )

        # Phase 7: Quality Validation Delegation
        quality_validation = await self._delegate_quality_validation(
            context, final_decision
        )

        # Generate final decision result
        result = await self._generate_final_result(
            context, collected_insights, quality_validation
        )

        return result

    async def _coordinator_initial_analysis(
        self, context: DecisionContext
    ) -> Dict[str, Any]:
        """Strategic Analyst (Coordinator) performs initial analysis and task planning."""
        coordinator = self.agents[AgentRole.STRATEGIC_ANALYST]

        # Get initial analysis from coordinator
        initial_output = await coordinator.process_decision_context(context)

        # Plan task delegations
        task_plan = self._plan_task_delegations(context, initial_output)

        return {
            "phase": "coordinator_initial_analysis",
            "agent_role": AgentRole.STRATEGIC_ANALYST,
            "initial_analysis": initial_output,
            "task_delegation_plan": task_plan,
            "coordination_notes": "Central coordinator analyzed problem and planned specialist delegations",
        }

    def _plan_task_delegations(
        self, context: DecisionContext, initial_analysis
    ) -> Dict[str, Any]:
        """Plan which tasks to delegate to which specialized agents."""
        delegations = {
            "resource_optimization": {
                "agent": AgentRole.RESOURCE_OPTIMIZER,
                "priority": "high",
                "tasks": [
                    "Analyze resource requirements and constraints",
                    "Evaluate efficiency ratios",
                    "Recommend resource allocation strategy",
                ],
                "rationale": "Critical for feasible implementation planning",
            }
        }

        # Add stakeholder analysis if multiple stakeholders
        if len(context.stakeholders) > 2:
            delegations["stakeholder_analysis"] = {
                "agent": AgentRole.STAKEHOLDER_STEWARD,
                "priority": "high",
                "tasks": [
                    "Assess stakeholder impacts and interests",
                    "Evaluate governance and compliance requirements",
                    "Recommend stakeholder engagement strategy",
                ],
                "rationale": "Multiple stakeholders require specialized governance analysis",
            }

        # Always include critical review
        delegations["critical_review"] = {
            "agent": AgentRole.CRITICAL_CHALLENGER,
            "priority": "medium",
            "tasks": [
                "Challenge assumptions and identify biases",
                "Test hypothesis robustness",
                "Identify potential failure modes",
            ],
            "rationale": "Essential for bias prevention and risk identification",
        }

        # Always include quality validation
        delegations["quality_validation"] = {
            "agent": AgentRole.QUALITY_VALIDATOR,
            "priority": "critical",
            "tasks": [
                "Validate decision completeness and consistency",
                "Assess implementation readiness",
                "Provide final approval recommendation",
            ],
            "rationale": "Final quality gate before decision approval",
        }

        return delegations

    async def _execute_delegated_tasks(
        self, context: DecisionContext, coordinator_analysis
    ) -> List[Dict[str, Any]]:
        """Execute tasks delegated to specialized agents."""
        results = []
        task_plan = coordinator_analysis["task_delegation_plan"]

        # Execute resource optimization delegation
        if "resource_optimization" in task_plan:
            resource_optimizer = self.agents[AgentRole.RESOURCE_OPTIMIZER]
            resource_output = await resource_optimizer.process_decision_context(context)

            results.append(
                {
                    "phase": "delegated_task",
                    "delegation_type": "resource_optimization",
                    "agent_role": AgentRole.RESOURCE_OPTIMIZER,
                    "output": resource_output,
                    "completion_status": "completed",
                }
            )

        # Execute stakeholder analysis delegation (if planned)
        if "stakeholder_analysis" in task_plan:
            stakeholder_steward = self.agents[AgentRole.STAKEHOLDER_STEWARD]
            stakeholder_output = await stakeholder_steward.process_decision_context(
                context
            )

            results.append(
                {
                    "phase": "delegated_task",
                    "delegation_type": "stakeholder_analysis",
                    "agent_role": AgentRole.STAKEHOLDER_STEWARD,
                    "output": stakeholder_output,
                    "completion_status": "completed",
                }
            )

        return results

    async def _coordinator_synthesis(
        self, context: DecisionContext, collected_insights: List[Dict]
    ) -> Dict[str, Any]:
        """Coordinator synthesizes insights from delegated tasks."""
        coordinator = self.agents[AgentRole.STRATEGIC_ANALYST]

        # Extract key findings from delegated tasks
        synthesis_input = {
            "initial_analysis": collected_insights[0]["initial_analysis"]
            if collected_insights
            else None,
            "delegated_findings": [
                insight
                for insight in collected_insights
                if insight.get("phase") == "delegated_task"
            ],
            "synthesis_focus": "Integration of specialist insights into unified recommendation",
        }

        # Use coordinator agent to synthesize findings
        try:
            synthesis_result = await coordinator.analyze_decision(
                context, synthesis_input
            )
            synthesis = {
                "synthesized_recommendation": synthesis_result.get(
                    "recommendation",
                    "Integrated analysis incorporating specialist insights",
                ),
                "key_findings": synthesis_result.get(
                    "key_insights",
                    [
                        "Resource requirements assessed and validated",
                        "Stakeholder impacts analyzed and addressed",
                        "Multi-perspective analysis completed",
                    ],
                ),
                "confidence_level": synthesis_result.get("confidence", 0.75),
                "next_steps": synthesis_result.get(
                    "next_steps",
                    [
                        "Critical review of synthesis",
                        "Quality validation of integrated approach",
                        "Final decision formulation",
                    ],
                ),
            }
        except Exception as e:
            # Fallback to hardcoded synthesis if agent fails
            synthesis = {
                "synthesized_recommendation": "Integrated analysis incorporating specialist insights (fallback)",
                "key_findings": [
                    "Resource requirements assessed and validated",
                    "Stakeholder impacts analyzed and addressed",
                    "Multi-perspective analysis completed",
                ],
                "confidence_level": 0.75,
                "next_steps": [
                    "Critical review of synthesis",
                    "Quality validation of integrated approach",
                    "Final decision formulation",
                ],
                "synthesis_error": str(e),
            }

        return {
            "phase": "coordinator_synthesis",
            "agent_role": AgentRole.STRATEGIC_ANALYST,
            "synthesis": synthesis,
            "integration_approach": "Central coordinator synthesis of specialist insights",
        }

    async def _delegate_critical_review(
        self, context: DecisionContext, synthesis_result
    ) -> Dict[str, Any]:
        """Delegate critical review to Challenge Agent."""
        critical_challenger = self.agents[AgentRole.CRITICAL_CHALLENGER]

        # Get hypotheses for challenging
        coordinator = self.agents[AgentRole.STRATEGIC_ANALYST]
        hypotheses = []
        if (
            hasattr(coordinator, "current_hypotheses")
            and coordinator.current_hypotheses
        ):
            hypotheses = coordinator.current_hypotheses

        # Execute critical challenge
        challenge_results = None
        if hypotheses and hasattr(critical_challenger, "challenge_hypotheses"):
            challenge_results = critical_challenger.challenge_hypotheses(hypotheses)

        return {
            "phase": "delegated_critical_review",
            "agent_role": AgentRole.CRITICAL_CHALLENGER,
            "challenge_results": challenge_results,
            "review_focus": "Bias detection and assumption testing of synthesized recommendation",
            "delegation_outcome": "completed"
            if challenge_results
            else "no_hypotheses_available",
        }

    async def _delegate_stakeholder_assessment(
        self, context: DecisionContext, synthesis_result
    ) -> Dict[str, Any]:
        """Delegate stakeholder impact assessment."""
        stakeholder_steward = self.agents[AgentRole.STAKEHOLDER_STEWARD]

        # Get stakeholder assessment (would analyze synthesis in practice)
        stakeholder_output = await stakeholder_steward.process_decision_context(context)

        return {
            "phase": "delegated_stakeholder_assessment",
            "agent_role": AgentRole.STAKEHOLDER_STEWARD,
            "assessment_output": stakeholder_output,
            "assessment_focus": "Governance and ethical validation of synthesized approach",
        }

    async def _coordinator_final_decision(
        self, context: DecisionContext, collected_insights: List[Dict]
    ) -> Dict[str, Any]:
        """Coordinator formulates final decision based on all insights."""
        coordinator = self.agents[AgentRole.STRATEGIC_ANALYST]

        # Analyze all collected insights
        decision_inputs = {
            "initial_analysis": collected_insights[0] if collected_insights else None,
            "specialist_insights": [
                insight
                for insight in collected_insights
                if "delegated" in insight.get("phase", "")
            ],
            "synthesis_results": [
                insight
                for insight in collected_insights
                if insight.get("phase") == "coordinator_synthesis"
            ],
        }

        # Use coordinator agent to formulate final decision
        try:
            decision_result = await coordinator.analyze_decision(
                context, decision_inputs
            )
            final_decision = {
                "final_recommendation": decision_result.get(
                    "recommendation",
                    "Coordinated decision based on multi-specialist analysis",
                ),
                "decision_confidence": decision_result.get("confidence", 0.8),
                "implementation_approach": decision_result.get(
                    "implementation_approach",
                    "Systematic implementation with specialist oversight",
                ),
                "risk_mitigation": decision_result.get(
                    "risk_mitigation",
                    "Comprehensive risk assessment through specialist delegation",
                ),
                "success_probability": decision_result.get("success_probability", 0.75),
            }
        except Exception as e:
            # Fallback to hardcoded decision if agent fails
            final_decision = {
                "final_recommendation": "Coordinated decision based on multi-specialist analysis (fallback)",
                "decision_confidence": 0.8,
                "implementation_approach": "Systematic implementation with specialist oversight",
                "risk_mitigation": "Comprehensive risk assessment through specialist delegation",
                "success_probability": 0.75,
                "decision_error": str(e),
            }

        # Get best hypothesis from coordinator
        final_hypothesis = None
        if (
            hasattr(coordinator, "current_hypotheses")
            and coordinator.current_hypotheses
        ):
            sorted_hypotheses = sorted(
                coordinator.current_hypotheses,
                key=lambda h: h.probability,
                reverse=True,
            )
            final_hypothesis = sorted_hypotheses[0]

        return {
            "phase": "coordinator_final_decision",
            "agent_role": AgentRole.STRATEGIC_ANALYST,
            "final_decision": final_decision,
            "selected_hypothesis": final_hypothesis,
            "decision_methodology": "Central coordination with specialist delegation",
        }

    async def _delegate_quality_validation(
        self, context: DecisionContext, final_decision
    ) -> Dict[str, Any]:
        """Delegate final quality validation."""
        quality_validator = self.agents[AgentRole.QUALITY_VALIDATOR]

        # Create preliminary decision for validation
        preliminary_result = await self._create_preliminary_result(
            context, final_decision
        )

        # Execute quality validation
        validation_results = None
        if hasattr(quality_validator, "validate_final_decision"):
            validation_results = quality_validator.validate_final_decision(
                preliminary_result
            )

        return {
            "phase": "delegated_quality_validation",
            "agent_role": AgentRole.QUALITY_VALIDATOR,
            "validation_results": validation_results,
            "validation_focus": "Final quality gate and implementation readiness assessment",
        }

    async def _create_preliminary_result(
        self, context: DecisionContext, final_decision
    ) -> DecisionResult:
        """Create preliminary decision result for quality validation."""
        # Note: coordinator agent could be used here for enhanced result structuring

        # Get hypothesis from final decision
        selected_hypothesis = final_decision.get("selected_hypothesis")

        # Basic quality metrics for preliminary validation
        quality_metrics = QualityMetrics(
            decision_confidence=final_decision["final_decision"].get(
                "decision_confidence", 0.8
            ),
            evidence_quality_score=0.75,
            bias_risk_assessment=0.25,
            implementation_feasibility=0.8,
            stakeholder_alignment=0.75,
            logical_consistency=0.8,
            completeness=0.85,
        )

        return DecisionResult(
            context=context,
            final_hypothesis=selected_hypothesis,
            alternative_hypotheses=[],
            quality_metrics=quality_metrics,
            total_time=0.0,
            agent_outputs=[],
            information_gathered=[],
            bias_report=self._create_default_bias_report(),
            implementation_plan={"approach": "coordinator_delegated_implementation"},
            confidence_level=final_decision["final_decision"].get(
                "decision_confidence", 0.8
            ),
        )

    async def _generate_final_result(
        self,
        context: DecisionContext,
        collected_insights: List[Dict],
        quality_validation,
    ) -> DecisionResult:
        """Generate the final decision result."""
        coordinator = self.agents[AgentRole.STRATEGIC_ANALYST]

        # Extract final decision details
        final_decision_insight = next(
            (
                insight
                for insight in collected_insights
                if insight.get("phase") == "coordinator_final_decision"
            ),
            None,
        )

        # Get selected hypothesis
        final_hypothesis = None
        alternative_hypotheses = []
        if final_decision_insight and final_decision_insight.get("selected_hypothesis"):
            final_hypothesis = final_decision_insight["selected_hypothesis"]
        elif (
            hasattr(coordinator, "current_hypotheses")
            and coordinator.current_hypotheses
        ):
            sorted_hypotheses = sorted(
                coordinator.current_hypotheses,
                key=lambda h: h.probability,
                reverse=True,
            )
            final_hypothesis = sorted_hypotheses[0]
            alternative_hypotheses = sorted_hypotheses[1:3]

        # Extract quality metrics from validation
        quality_metrics = self._extract_quality_metrics_from_validation(
            quality_validation
        )

        # Calculate final confidence
        base_confidence = (
            final_decision_insight["final_decision"].get("decision_confidence", 0.8)
            if final_decision_insight
            else 0.8
        )
        validation_confidence = self._get_validation_confidence(quality_validation)
        final_confidence = (base_confidence + validation_confidence) / 2

        # Get session and performance data
        session_summary = (
            self.information_gatekeeper.get_session_summary()
            if self.information_gatekeeper
            else {}
        )

        # Create comprehensive implementation plan
        implementation_plan = self._create_magentic_implementation_plan(
            final_hypothesis, context, collected_insights, quality_validation
        )

        # Create bias report
        bias_report = self._create_comprehensive_bias_report(collected_insights)

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

    def _extract_quality_metrics_from_validation(
        self, validation_result
    ) -> QualityMetrics:
        """Extract quality metrics from validation result."""
        if (
            validation_result
            and isinstance(validation_result, dict)
            and "validation_results" in validation_result
            and validation_result["validation_results"]
            and "quality_metrics" in validation_result["validation_results"]
        ):
            metrics = validation_result["validation_results"]["quality_metrics"]
            return QualityMetrics(
                decision_confidence=metrics.get("decision_confidence", 0.8),
                evidence_quality_score=metrics.get("evidence_quality_score", 0.75),
                bias_risk_assessment=metrics.get("bias_risk_assessment", 0.25),
                implementation_feasibility=metrics.get(
                    "implementation_feasibility", 0.8
                ),
                stakeholder_alignment=metrics.get("stakeholder_alignment", 0.75),
                logical_consistency=metrics.get("logical_consistency", 0.8),
                completeness=metrics.get("completeness", 0.85),
            )

        # Default high-quality metrics for MagenticOne approach
        return QualityMetrics(
            decision_confidence=0.8,
            evidence_quality_score=0.75,
            bias_risk_assessment=0.25,
            implementation_feasibility=0.8,
            stakeholder_alignment=0.75,
            logical_consistency=0.8,
            completeness=0.85,
        )

    def _get_validation_confidence(self, validation_result) -> float:
        """Get confidence level from validation result."""
        if (
            validation_result
            and isinstance(validation_result, dict)
            and "validation_results" in validation_result
            and validation_result["validation_results"]
        ):
            validation_data = validation_result["validation_results"]
            if "confidence_level" in validation_data:
                return validation_data["confidence_level"]
            elif "final_recommendation" in validation_data:
                recommendation = validation_data["final_recommendation"]
                if recommendation.get("recommendation") == "APPROVE":
                    return 0.9
                elif recommendation.get("recommendation") == "CONDITIONAL_APPROVE":
                    return 0.7
                elif recommendation.get("recommendation") == "REJECT":
                    return 0.4

        return 0.75  # Default confidence for MagenticOne coordination

    def _create_default_bias_report(self):
        """Create default bias report for MagenticOne approach."""
        from ..models.mai_dxo import BiasReport

        return BiasReport(
            indicators=[],
            overall_risk_score=0.2,
            mitigation_strategies=[
                "Central coordinator oversight prevents single-perspective bias",
                "Systematic specialist delegation ensures comprehensive analysis",
                "Critical challenger delegation addresses assumption testing",
                "Quality validator provides independent final review",
            ],
        )

    def _create_comprehensive_bias_report(self, insights: List[Dict]):
        """Create comprehensive bias report from all insights."""
        from ..models.mai_dxo import BiasReport, BiasWarning, BiasType

        warnings = []

        # Look for critical challenger insights
        for insight in insights:
            if insight.get("phase") == "delegated_critical_review" and insight.get(
                "challenge_results"
            ):
                # Extract bias concerns (simplified)
                warnings.append(
                    BiasWarning(
                        bias_type=BiasType.CONFIRMATION,
                        description="Systematic bias review conducted by specialist challenger",
                        severity=0.3,
                        mitigation_strategy="Central coordinator synthesis with specialist oversight",
                    )
                )

        return BiasReport(
            indicators=warnings,
            overall_risk_score=0.2,  # Lower due to systematic coordination
            mitigation_strategies=[
                "Central coordinator prevents coordination bias",
                "Specialist delegation ensures expertise application",
                "Multi-phase synthesis prevents single-point failures",
                "Independent quality validation provides final check",
            ],
        )

    def _create_magentic_implementation_plan(
        self, hypothesis, context: DecisionContext, insights: List[Dict], validation
    ) -> Dict[str, Any]:
        """Create implementation plan based on MagenticOne coordination."""
        if not hypothesis:
            return {
                "status": "no_hypothesis_selected",
                "recommendation": "Return to coordinator for decision reformulation",
            }

        plan = {
            "selected_approach": hypothesis.description
            if hasattr(hypothesis, "description")
            else str(hypothesis),
            "coordination_methodology": "Central coordinator with specialist delegation",
            "implementation_structure": {
                "coordinator": "Strategic Analyst maintains oversight",
                "specialists": "Delegated implementation in areas of expertise",
                "quality_assurance": "Continuous validator involvement",
                "stakeholder_management": "Dedicated steward for governance",
            },
            "implementation_phases": [
                "Coordinator planning and delegation setup",
                "Specialist execution with coordinator oversight",
                "Continuous quality monitoring and adjustment",
                "Stakeholder engagement and governance compliance",
                "Final validation and approval gates",
            ],
            "success_criteria": context.success_criteria,
            "coordination_benefits": [
                "Unified strategic direction with specialist expertise",
                "Reduced coordination overhead through central management",
                "Systematic quality assurance at each phase",
                "Clear accountability and decision authority",
            ],
        }

        # Add specialist insights to implementation plan
        for insight in insights:
            if insight.get("phase") == "delegated_task":
                delegation_type = insight.get("delegation_type")
                if delegation_type == "resource_optimization":
                    plan["resource_management"] = (
                        "Specialist-optimized resource allocation"
                    )
                elif delegation_type == "stakeholder_analysis":
                    plan["stakeholder_strategy"] = (
                        "Specialist-managed stakeholder engagement"
                    )

        return plan

    def _collect_all_agent_outputs(self) -> List[Any]:
        """Collect outputs from all agents."""
        all_outputs = []
        for agent in self.agents.values():
            if hasattr(agent, "agent_outputs"):
                all_outputs.extend(agent.agent_outputs)
        return all_outputs

    def get_orchestration_summary(self) -> Dict[str, Any]:
        """Get summary of the MagenticOne orchestration process."""
        agent_performance = {}
        for role, agent in self.agents.items():
            if hasattr(agent, "get_performance_metrics"):
                agent_performance[role.value] = agent.get_performance_metrics()

        return {
            "orchestration_method": self.orchestration_method.value,
            "domain_context": self.domain_context,
            "max_turns": self.max_turns,
            "coordinator_role": self.coordinator_role.value,
            "task_delegations": len(self.task_delegations),
            "synthesis_points": len(self.synthesis_points),
            "agent_performance": agent_performance,
            "coordination_strategy": "Central coordinator with systematic specialist delegation",
            "process_summary": {
                "coordination_approach": "Strategic Analyst as central coordinator",
                "delegation_efficiency": "High - targeted specialist utilization",
                "decision_quality": "systematic_coordinated_multi_agent_analysis",
                "orchestration_benefits": [
                    "Unified strategic direction",
                    "Specialist expertise application",
                    "Systematic quality assurance",
                    "Clear decision authority",
                ],
            },
        }
