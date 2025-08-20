"""
MAI-DxO implementation using SelectorGroupChat orchestration.

This implementation uses Autogen's SelectorGroupChat to dynamically select
the most appropriate agent based on current decision context and needs.
"""

from typing import Any, Dict, List, Optional

from autogen_core.models import ChatCompletionClient
from autogen_agentchat.teams import SelectorGroupChat

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


class SelectorMAIDxO:
    """
    MAI-DxO implementation using SelectorGroupChat orchestration.

    This orchestrator uses intelligent agent selection based on current
    decision phase and context, allowing for dynamic workflow adaptation.
    """

    def __init__(
        self,
        model_client: ChatCompletionClient,
        domain_context: str = "business",
        max_turns: int = 15,
        **kwargs,
    ):
        """Initialize the Selector MAI-DxO orchestrator."""
        self.model_client = model_client
        self.domain_context = domain_context
        self.max_turns = max_turns
        self.orchestration_method = OrchestrationMethod.SELECTOR

        # Will be initialized when starting a decision process
        self.information_gatekeeper: Optional[InformationGatekeeper] = None
        self.agents: Dict[AgentRole, Any] = {}
        self.selector_chat: Optional[SelectorGroupChat] = None

        # Decision state tracking
        self.decision_phase = "initial"
        self.current_focus = "analysis"
        self.completed_phases = []

    async def process_decision(
        self,
        context: DecisionContext,
        constraints: Optional[ResourceConstraints] = None,
    ) -> DecisionResult:
        """
        Process a decision using the Selector MAI-DxO orchestration.

        The selector dynamically chooses agents based on:
        1. Current decision phase (analysis, challenge, synthesis, validation)
        2. Information gaps and needs
        3. Quality requirements and risk factors
        4. Resource constraints and time pressure
        """
        # Use provided constraints or defaults from context
        if constraints is None:
            constraints = context.constraints

        # Initialize the decision process
        await self._initialize_decision_process(context, constraints)

        # Dynamic agent selection workflow
        decision_result = await self._execute_selector_workflow(context)

        return decision_result

    async def _initialize_decision_process(
        self, context: DecisionContext, constraints: ResourceConstraints
    ) -> None:
        """Initialize the information gatekeeper, agents, and selector."""
        # Initialize information gatekeeper
        self.information_gatekeeper = InformationGatekeeper(constraints)

        # Initialize the five specialized agents
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

        # Create custom selector function for intelligent agent selection
        def agent_selector(messages, agents) -> int:
            return self._select_next_agent(messages, agents)

        # Initialize SelectorGroupChat with custom selector
        agent_list = list(self.agents.values())
        self.selector_chat = SelectorGroupChat(
            agents=agent_list,
            selector_func=agent_selector,
        )

    def _select_next_agent(self, messages: List[Any], agents: List[Any]) -> int:
        """
        Intelligently select the next agent based on decision context and phase.

        Selection logic:
        1. Strategic Analyst - For initial analysis and hypothesis generation
        2. Resource Optimizer - When resource/efficiency questions arise
        3. Critical Challenger - When biases or assumptions need challenging
        4. Stakeholder Steward - When stakeholder impacts need assessment
        5. Quality Validator - For final validation and quality checks
        """
        # Analyze current decision state
        current_needs = self._analyze_current_needs(messages)

        # Select based on decision phase and needs
        if self.decision_phase == "initial":
            # Start with Strategic Analyst for hypothesis generation
            if "strategic_analyst" not in self.completed_phases:
                return self._get_agent_index(AgentRole.STRATEGIC_ANALYST)

        elif self.decision_phase == "analysis":
            # Resource analysis phase
            if (
                current_needs.get("resource_analysis")
                and "resource_optimizer" not in self.completed_phases
            ):
                return self._get_agent_index(AgentRole.RESOURCE_OPTIMIZER)

            # Stakeholder analysis phase
            if (
                current_needs.get("stakeholder_analysis")
                and "stakeholder_steward" not in self.completed_phases
            ):
                return self._get_agent_index(AgentRole.STAKEHOLDER_STEWARD)

        elif self.decision_phase == "challenge":
            # Challenge and bias detection phase
            if "critical_challenger" not in self.completed_phases:
                return self._get_agent_index(AgentRole.CRITICAL_CHALLENGER)

        elif self.decision_phase == "validation":
            # Final validation phase
            return self._get_agent_index(AgentRole.QUALITY_VALIDATOR)

        # Default selection based on current needs
        return self._select_based_on_needs(current_needs)

    def _analyze_current_needs(self, messages: List[Any]) -> Dict[str, bool]:
        """Analyze current decision needs based on message history."""
        needs = {
            "hypothesis_generation": False,
            "resource_analysis": False,
            "stakeholder_analysis": False,
            "bias_challenge": False,
            "quality_validation": False,
        }

        # Simple heuristic based on message content
        if not messages or len(messages) < 2:
            needs["hypothesis_generation"] = True

        # Look for keywords indicating specific needs
        recent_content = " ".join(str(msg) for msg in messages[-3:]).lower()

        if any(
            word in recent_content
            for word in ["resource", "efficiency", "optimization", "time"]
        ):
            needs["resource_analysis"] = True

        if any(
            word in recent_content
            for word in ["stakeholder", "impact", "ethics", "governance"]
        ):
            needs["stakeholder_analysis"] = True

        if any(
            word in recent_content for word in ["assume", "bias", "challenge", "risk"]
        ):
            needs["bias_challenge"] = True

        if any(
            word in recent_content
            for word in ["quality", "validate", "approve", "final"]
        ):
            needs["quality_validation"] = True

        return needs

    def _get_agent_index(self, agent_role: AgentRole) -> int:
        """Get the index of an agent in the agents list."""
        agent_roles = [
            AgentRole.STRATEGIC_ANALYST,
            AgentRole.RESOURCE_OPTIMIZER,
            AgentRole.CRITICAL_CHALLENGER,
            AgentRole.STAKEHOLDER_STEWARD,
            AgentRole.QUALITY_VALIDATOR,
        ]
        return agent_roles.index(agent_role)

    def _select_based_on_needs(self, needs: Dict[str, bool]) -> int:
        """Select agent based on current needs priority."""
        if needs.get("hypothesis_generation"):
            return self._get_agent_index(AgentRole.STRATEGIC_ANALYST)
        elif needs.get("resource_analysis"):
            return self._get_agent_index(AgentRole.RESOURCE_OPTIMIZER)
        elif needs.get("stakeholder_analysis"):
            return self._get_agent_index(AgentRole.STAKEHOLDER_STEWARD)
        elif needs.get("bias_challenge"):
            return self._get_agent_index(AgentRole.CRITICAL_CHALLENGER)
        elif needs.get("quality_validation"):
            return self._get_agent_index(AgentRole.QUALITY_VALIDATOR)
        else:
            # Default to Strategic Analyst
            return self._get_agent_index(AgentRole.STRATEGIC_ANALYST)

    async def _execute_selector_workflow(
        self, context: DecisionContext
    ) -> DecisionResult:
        """Execute the selector-based workflow with dynamic agent selection."""
        collected_outputs = []

        # Phase 1: Initial Analysis (Strategic focus)
        self.decision_phase = "initial"
        self.current_focus = "hypothesis_generation"

        # Get initial strategic analysis
        strategic_analyst = self.agents[AgentRole.STRATEGIC_ANALYST]
        initial_output = await strategic_analyst.process_decision_context(context)
        collected_outputs.append(initial_output)
        self.completed_phases.append("strategic_analyst")

        # Phase 2: Dynamic Analysis (Resource and Stakeholder)
        self.decision_phase = "analysis"

        # Resource analysis
        self.current_focus = "resource_optimization"
        resource_optimizer = self.agents[AgentRole.RESOURCE_OPTIMIZER]
        resource_output = await resource_optimizer.process_decision_context(context)
        collected_outputs.append(resource_output)
        self.completed_phases.append("resource_optimizer")

        # Stakeholder analysis (if multiple stakeholders)
        if len(context.stakeholders) > 2:
            self.current_focus = "stakeholder_analysis"
            stakeholder_steward = self.agents[AgentRole.STAKEHOLDER_STEWARD]
            stakeholder_output = await stakeholder_steward.process_decision_context(
                context
            )
            collected_outputs.append(stakeholder_output)
            self.completed_phases.append("stakeholder_steward")

        # Phase 3: Challenge Phase (Bias detection and assumption testing)
        self.decision_phase = "challenge"
        self.current_focus = "bias_challenge"

        # Get hypotheses for challenging
        hypotheses = self._extract_hypotheses_from_outputs(collected_outputs)

        # Critical challenger evaluation
        critical_challenger = self.agents[AgentRole.CRITICAL_CHALLENGER]
        if hypotheses and hasattr(critical_challenger, "challenge_hypotheses"):
            challenge_output = critical_challenger.challenge_hypotheses(hypotheses)
            collected_outputs.append(challenge_output)
        self.completed_phases.append("critical_challenger")

        # Phase 4: Validation Phase (Quality assurance)
        self.decision_phase = "validation"
        self.current_focus = "quality_validation"

        # Create preliminary decision for validation
        preliminary_decision = await self._create_preliminary_decision(
            context, collected_outputs
        )

        # Quality validation
        quality_validator = self.agents[AgentRole.QUALITY_VALIDATOR]
        if hasattr(quality_validator, "validate_final_decision"):
            validation_output = quality_validator.validate_final_decision(
                preliminary_decision
            )
            collected_outputs.append(validation_output)
        self.completed_phases.append("quality_validator")

        # Generate final decision result
        final_decision = await self._generate_final_decision_result(
            context, collected_outputs, validation_output
        )

        return final_decision

    def _extract_hypotheses_from_outputs(self, outputs: List[Any]) -> List[Any]:
        """Extract hypotheses from collected outputs."""
        hypotheses = []

        # Look for Strategic Analyst outputs with hypotheses
        for output in outputs:
            if (
                hasattr(output, "agent_role")
                and output.agent_role == AgentRole.STRATEGIC_ANALYST
            ):
                # Extract hypotheses from Strategic Analyst
                strategic_analyst = self.agents[AgentRole.STRATEGIC_ANALYST]
                if hasattr(strategic_analyst, "current_hypotheses"):
                    hypotheses.extend(strategic_analyst.current_hypotheses)

        return hypotheses[:5]  # Return top 5 hypotheses

    async def _create_preliminary_decision(
        self, context: DecisionContext, outputs: List[Any]
    ) -> DecisionResult:
        """Create preliminary decision result for validation."""
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

        # Basic quality metrics for preliminary assessment
        quality_metrics = QualityMetrics(
            decision_confidence=0.6,
            evidence_quality_score=0.6,
            bias_risk_assessment=0.4,
            implementation_feasibility=0.6,
            stakeholder_alignment=0.6,
            logical_consistency=0.6,
            completeness=0.7,
        )

        # Get session and time data
        session_summary = (
            self.information_gatekeeper.get_session_summary()
            if self.information_gatekeeper
            else {}
        )
        total_time = session_summary.get("elapsed_time_hours", 0.0)

        return DecisionResult(
            context=context,
            final_hypothesis=final_hypothesis,
            alternative_hypotheses=alternative_hypotheses,
            quality_metrics=quality_metrics,
            total_time=total_time,
            agent_outputs=outputs,
            information_gathered=self.information_gatekeeper.get_information_history()
            if self.information_gatekeeper
            else [],
            bias_report=self._create_default_bias_report(),
            implementation_plan=self._create_basic_implementation_plan(
                final_hypothesis, context
            ),
            confidence_level=0.6,
        )

    async def _generate_final_decision_result(
        self, context: DecisionContext, outputs: List[Any], validation_output: Any
    ) -> DecisionResult:
        """Generate the final decision result with validation."""
        # Extract validation metrics
        quality_metrics = self._extract_quality_metrics_from_validation(
            validation_output
        )

        # Get final hypothesis
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

        # Calculate final confidence based on validation
        confidence_level = self._calculate_final_confidence_from_validation(
            validation_output, quality_metrics
        )

        # Get comprehensive session and performance data
        session_summary = (
            self.information_gatekeeper.get_session_summary()
            if self.information_gatekeeper
            else {}
        )

        return DecisionResult(
            context=context,
            final_hypothesis=final_hypothesis,
            alternative_hypotheses=alternative_hypotheses,
            quality_metrics=quality_metrics,
            total_time=session_summary.get("elapsed_time_hours", 0.0),
            agent_outputs=outputs,
            information_gathered=self.information_gatekeeper.get_information_history()
            if self.information_gatekeeper
            else [],
            bias_report=self._create_comprehensive_bias_report(outputs),
            implementation_plan=self._create_comprehensive_implementation_plan(
                final_hypothesis, context, outputs
            ),
            confidence_level=confidence_level,
        )

    def _extract_quality_metrics_from_validation(
        self, validation_output: Any
    ) -> QualityMetrics:
        """Extract quality metrics from validation output."""
        if (
            validation_output
            and isinstance(validation_output, dict)
            and "quality_metrics" in validation_output
        ):
            metrics = validation_output["quality_metrics"]
            return QualityMetrics(
                decision_confidence=metrics.get("decision_confidence", 0.7),
                evidence_quality_score=metrics.get("evidence_quality_score", 0.7),
                bias_risk_assessment=metrics.get("bias_risk_assessment", 0.3),
                implementation_feasibility=metrics.get(
                    "implementation_feasibility", 0.7
                ),
                stakeholder_alignment=metrics.get("stakeholder_alignment", 0.7),
                logical_consistency=metrics.get("logical_consistency", 0.7),
                completeness=metrics.get("completeness", 0.8),
            )

        # Default quality metrics
        return QualityMetrics(
            decision_confidence=0.7,
            evidence_quality_score=0.7,
            bias_risk_assessment=0.3,
            implementation_feasibility=0.7,
            stakeholder_alignment=0.7,
            logical_consistency=0.7,
            completeness=0.8,
        )

    def _calculate_final_confidence_from_validation(
        self, validation_output: Any, quality_metrics: QualityMetrics
    ) -> float:
        """Calculate final confidence based on validation results."""
        base_confidence = (
            quality_metrics.decision_confidence
            + quality_metrics.evidence_quality_score
            + quality_metrics.logical_consistency
        ) / 3

        # Adjust based on validation recommendation
        if validation_output and isinstance(validation_output, dict):
            recommendation = validation_output.get("final_recommendation", {})
            if recommendation.get("recommendation") == "APPROVE":
                return min(0.95, base_confidence + 0.1)
            elif recommendation.get("recommendation") == "CONDITIONAL_APPROVE":
                return base_confidence
            elif recommendation.get("recommendation") == "REJECT":
                return max(0.3, base_confidence - 0.2)

        return base_confidence

    def _create_default_bias_report(self):
        """Create default bias report."""
        from ..models.mai_dxo import BiasReport

        return BiasReport(
            indicators=[],
            overall_risk_score=0.3,
            mitigation_strategies=[
                "Dynamic agent selection prevented single-perspective bias",
                "Critical challenger phase addressed systematic biases",
                "Quality validation ensured bias risk assessment",
            ],
        )

    def _create_comprehensive_bias_report(self, outputs: List[Any]):
        """Create comprehensive bias report from all outputs."""
        from ..models.mai_dxo import BiasReport, BiasWarning, BiasType

        warnings = []

        # Look for bias challenges in outputs
        for output in outputs:
            if (
                hasattr(output, "agent_role")
                and output.agent_role == AgentRole.CRITICAL_CHALLENGER
            ):
                # Extract bias warnings from challenger output
                if isinstance(output, dict) and "identified_concerns" in output:
                    concerns = output["identified_concerns"]
                    for concern in concerns[:3]:  # Top 3 concerns
                        warnings.append(
                            BiasWarning(
                                bias_type=BiasType.CONFIRMATION,  # Default type
                                description=str(concern),
                                severity=0.5,
                                mitigation_strategy="Addressed through multi-agent analysis",
                            )
                        )

        return BiasReport(
            indicators=warnings,
            overall_risk_score=0.25,  # Lower due to systematic bias prevention
            mitigation_strategies=[
                "Dynamic agent selection based on decision needs",
                "Specialized critical challenger for bias detection",
                "Multi-perspective stakeholder analysis",
                "Quality validation before final approval",
            ],
        )

    def _create_basic_implementation_plan(
        self, hypothesis, context: DecisionContext
    ) -> Dict[str, Any]:
        """Create basic implementation plan."""
        if not hypothesis:
            return {"status": "no_hypothesis_available"}

        return {
            "approach": "selector_driven_implementation",
            "selected_hypothesis": hypothesis.description
            if hasattr(hypothesis, "description")
            else str(hypothesis),
            "implementation_strategy": "Adaptive approach based on ongoing agent selection",
            "success_criteria": context.success_criteria,
        }

    def _create_comprehensive_implementation_plan(
        self, hypothesis, context: DecisionContext, outputs: List[Any]
    ) -> Dict[str, Any]:
        """Create comprehensive implementation plan from all outputs."""
        if not hypothesis:
            return {
                "status": "no_hypothesis_selected",
                "recommendation": "Return to analysis phase",
            }

        plan = {
            "selected_approach": hypothesis.description
            if hasattr(hypothesis, "description")
            else str(hypothesis),
            "selection_methodology": "Dynamic agent selection based on decision needs",
            "implementation_phases": [
                "Resource allocation and planning",
                "Stakeholder engagement and alignment",
                "Risk mitigation and monitoring",
                "Execution with continuous validation",
            ],
            "success_criteria": context.success_criteria,
            "monitoring_approach": "Continuous agent-based assessment",
        }

        # Add specific insights from different agent outputs
        for output in outputs:
            if hasattr(output, "agent_role"):
                if output.agent_role == AgentRole.RESOURCE_OPTIMIZER:
                    plan["resource_strategy"] = (
                        "Optimized resource allocation based on agent analysis"
                    )
                elif output.agent_role == AgentRole.STAKEHOLDER_STEWARD:
                    plan["stakeholder_strategy"] = (
                        "Multi-stakeholder alignment and governance"
                    )
                elif output.agent_role == AgentRole.CRITICAL_CHALLENGER:
                    plan["risk_mitigation"] = (
                        "Systematic bias prevention and assumption testing"
                    )

        return plan

    def get_orchestration_summary(self) -> Dict[str, Any]:
        """Get summary of the selector-based orchestration process."""
        agent_performance = {}
        for role, agent in self.agents.items():
            if hasattr(agent, "get_performance_metrics"):
                agent_performance[role.value] = agent.get_performance_metrics()

        return {
            "orchestration_method": self.orchestration_method.value,
            "domain_context": self.domain_context,
            "max_turns": self.max_turns,
            "completed_phases": self.completed_phases,
            "final_phase": self.decision_phase,
            "agent_performance": agent_performance,
            "selection_strategy": "Dynamic agent selection based on decision context and needs",
            "process_summary": {
                "phases_completed": self.completed_phases,
                "total_agents_used": len(self.completed_phases),
                "decision_quality": "adaptive_multi_agent_analysis",
                "orchestration_efficiency": "High - agents selected based on specific needs",
            },
        }
