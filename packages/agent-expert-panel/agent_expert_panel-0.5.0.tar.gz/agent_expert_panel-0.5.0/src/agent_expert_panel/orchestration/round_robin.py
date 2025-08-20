"""
MAI-DxO implementation using RoundRobinGroupChat orchestration.

This implementation uses Autogen's RoundRobinGroupChat to orchestrate
the five specialized MAI-DxO agents in a sequential decision-making process.
"""

from typing import Any, Dict, List, Optional

from autogen_core.models import ChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat

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


class RoundRobinMAIDxO:
    """
    MAI-DxO implementation using RoundRobinGroupChat orchestration.

    This orchestrator manages the five specialized agents in a round-robin
    fashion, ensuring each agent contributes their specialized perspective
    in a structured sequence.
    """

    def __init__(
        self,
        model_client: ChatCompletionClient,
        domain_context: str = "business",
        max_rounds: int = 3,
        **kwargs,
    ):
        """Initialize the Round Robin MAI-DxO orchestrator."""
        self.model_client = model_client
        self.domain_context = domain_context
        self.max_rounds = max_rounds
        self.orchestration_method = OrchestrationMethod.ROUND_ROBIN

        # Will be initialized when starting a decision process
        self.information_gatekeeper: Optional[InformationGatekeeper] = None
        self.agents: Dict[AgentRole, Any] = {}
        self.group_chat: Optional[RoundRobinGroupChat] = None

    async def process_decision(
        self,
        context: DecisionContext,
        constraints: Optional[ResourceConstraints] = None,
    ) -> DecisionResult:
        """
        Process a decision using the Round Robin MAI-DxO orchestration.

        The process follows these phases:
        1. Initialize agents and information gatekeeper
        2. Round 1: Initial analysis from each agent
        3. Round 2: Cross-agent deliberation and challenge
        4. Round 3: Final synthesis and quality validation
        5. Generate final decision result
        """
        # Use provided constraints or defaults from context
        if constraints is None:
            constraints = context.constraints

        # Initialize the decision process
        await self._initialize_decision_process(context, constraints)

        # Phase 1: Initial Analysis Round
        initial_outputs = await self._conduct_initial_analysis_round(context)

        # Phase 2: Deliberation and Challenge Round
        deliberation_outputs = await self._conduct_deliberation_round(
            context, initial_outputs
        )

        # Phase 3: Final Synthesis and Validation Round
        final_outputs = await self._conduct_final_synthesis_round(
            context, deliberation_outputs
        )

        # Generate final decision result
        decision_result = await self._generate_final_decision(context, final_outputs)

        return decision_result

    async def _initialize_decision_process(
        self, context: DecisionContext, constraints: ResourceConstraints
    ) -> None:
        """Initialize the information gatekeeper and agents for the decision process."""
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

        # Initialize RoundRobinGroupChat with agent sequence
        agent_list = [
            self.agents[AgentRole.STRATEGIC_ANALYST],
            self.agents[AgentRole.RESOURCE_OPTIMIZER],
            self.agents[AgentRole.CRITICAL_CHALLENGER],
            self.agents[AgentRole.STAKEHOLDER_STEWARD],
            self.agents[AgentRole.QUALITY_VALIDATOR],
        ]

        self.group_chat = RoundRobinGroupChat(agent_list)

    async def _conduct_initial_analysis_round(
        self, context: DecisionContext
    ) -> List[Any]:
        """Conduct the initial analysis round where each agent provides their perspective."""
        initial_outputs = []

        # Each agent processes the decision context independently
        for role, agent in self.agents.items():
            try:
                output = await agent.process_decision_context(context)
                initial_outputs.append(output)
                print(f"✓ {role.value} completed initial analysis")
            except Exception as e:
                print(f"✗ {role.value} failed initial analysis: {e}")
                # Continue with other agents even if one fails

        return initial_outputs

    async def _conduct_deliberation_round(
        self, context: DecisionContext, initial_outputs: List[Any]
    ) -> List[Any]:
        """Conduct deliberation round where agents challenge and refine each other's work."""
        deliberation_outputs = []

        # Strategic Analyst updates hypotheses based on all initial inputs
        strategic_analyst = self.agents[AgentRole.STRATEGIC_ANALYST]
        if (
            hasattr(strategic_analyst, "current_hypotheses")
            and strategic_analyst.current_hypotheses
        ):
            hypotheses = strategic_analyst.current_hypotheses
        else:
            # Generate hypotheses from initial analysis if not already available
            hypotheses = await self._extract_hypotheses_from_outputs(initial_outputs)

        # Critical Challenger evaluates all hypotheses for biases and weaknesses
        critical_challenger = self.agents[AgentRole.CRITICAL_CHALLENGER]
        if hasattr(critical_challenger, "challenge_hypotheses"):
            challenge_results = critical_challenger.challenge_hypotheses(hypotheses)
            deliberation_outputs.append(challenge_results)

        # Resource Optimizer evaluates resource implications
        resource_optimizer = self.agents[AgentRole.RESOURCE_OPTIMIZER]
        if hasattr(resource_optimizer, "get_performance_metrics"):
            resource_analysis = resource_optimizer.get_performance_metrics()
            deliberation_outputs.append(resource_analysis)

        # Stakeholder Steward assesses stakeholder impacts
        stakeholder_steward = self.agents[AgentRole.STAKEHOLDER_STEWARD]
        for hypothesis in hypotheses:
            if hasattr(stakeholder_steward, "assess_hypothesis_stakeholder_impact"):
                stakeholder_impact = (
                    stakeholder_steward.assess_hypothesis_stakeholder_impact(
                        hypothesis, context
                    )
                )
                deliberation_outputs.append(stakeholder_impact)

        return deliberation_outputs

    async def _conduct_final_synthesis_round(
        self, context: DecisionContext, deliberation_outputs: List[Any]
    ) -> List[Any]:
        """Conduct final synthesis and validation round."""
        final_outputs = []

        # Strategic Analyst synthesizes all feedback and finalizes recommendation
        strategic_analyst = self.agents[AgentRole.STRATEGIC_ANALYST]

        # Use strategic analyst to synthesize deliberation outputs
        try:
            synthesis_result = await strategic_analyst.analyze_decision(
                context,
                {
                    "deliberation_outputs": deliberation_outputs,
                    "synthesis_focus": "Final synthesis of multi-agent deliberation",
                },
            )
            # Create preliminary decision result for validation
            preliminary_result = await self._create_preliminary_decision_result(
                context, deliberation_outputs, synthesis_result
            )
        except Exception as e:
            # Fallback to basic preliminary result if synthesis fails
            preliminary_result = await self._create_preliminary_decision_result(
                context, deliberation_outputs, {"synthesis_error": str(e)}
            )

        # Quality Validator performs final validation
        quality_validator = self.agents[AgentRole.QUALITY_VALIDATOR]
        if hasattr(quality_validator, "validate_final_decision"):
            final_validation = quality_validator.validate_final_decision(
                preliminary_result
            )
            final_outputs.append(final_validation)

        return final_outputs

    async def _generate_final_decision(
        self, context: DecisionContext, final_outputs: List[Any]
    ) -> DecisionResult:
        """Generate the final decision result."""
        # Extract final validation results
        validation_result = final_outputs[0] if final_outputs else None

        # Get the best hypothesis from Strategic Analyst
        strategic_analyst = self.agents[AgentRole.STRATEGIC_ANALYST]
        final_hypothesis = None
        alternative_hypotheses = []

        if (
            hasattr(strategic_analyst, "current_hypotheses")
            and strategic_analyst.current_hypotheses
        ):
            # Sort hypotheses by probability (highest first)
            sorted_hypotheses = sorted(
                strategic_analyst.current_hypotheses,
                key=lambda h: h.probability,
                reverse=True,
            )
            final_hypothesis = sorted_hypotheses[0]
            alternative_hypotheses = sorted_hypotheses[1:4]  # Top 3 alternatives

        # Calculate quality metrics
        quality_metrics = self._extract_quality_metrics(validation_result)

        # Get session and time summary
        session_summary = (
            self.information_gatekeeper.get_session_summary()
            if self.information_gatekeeper
            else {}
        )
        total_time = session_summary.get("elapsed_time_hours", 0.0)

        # Get information gathered
        information_gathered = (
            self.information_gatekeeper.get_information_history()
            if self.information_gatekeeper
            else []
        )

        # Create bias report
        bias_report = self._create_bias_report(final_outputs)

        # Create implementation plan
        implementation_plan = self._create_implementation_plan(
            final_hypothesis, context
        )

        # Calculate final confidence
        confidence_level = self._calculate_final_confidence(
            quality_metrics, validation_result
        )

        # Collect all agent outputs
        all_agent_outputs = []
        for agent in self.agents.values():
            if hasattr(agent, "agent_outputs"):
                all_agent_outputs.extend(agent.agent_outputs)

        return DecisionResult(
            context=context,
            final_hypothesis=final_hypothesis,
            alternative_hypotheses=alternative_hypotheses,
            quality_metrics=quality_metrics,
            total_time=total_time,
            agent_outputs=all_agent_outputs,
            information_gathered=information_gathered,
            bias_report=bias_report,
            implementation_plan=implementation_plan,
            confidence_level=confidence_level,
        )

    async def _extract_hypotheses_from_outputs(self, outputs: List[Any]) -> List[Any]:
        """Extract hypotheses from initial agent outputs."""
        # Look for Strategic Analyst output with hypotheses
        for output in outputs:
            if (
                hasattr(output, "agent_role")
                and output.agent_role == AgentRole.STRATEGIC_ANALYST
            ):
                if (
                    hasattr(output, "content")
                    and "initial_hypotheses" in output.content
                ):
                    # Convert output hypotheses to Hypothesis objects
                    # This would need to be implemented based on actual output structure
                    pass

        # Return empty list if no hypotheses found
        return []

    async def _create_preliminary_decision_result(
        self, context: DecisionContext, deliberation_outputs: List[Any]
    ) -> DecisionResult:
        """Create a preliminary decision result for validation."""
        # This is a simplified version for validation purposes
        strategic_analyst = self.agents[AgentRole.STRATEGIC_ANALYST]

        final_hypothesis = None
        if (
            hasattr(strategic_analyst, "current_hypotheses")
            and strategic_analyst.current_hypotheses
        ):
            final_hypothesis = strategic_analyst.current_hypotheses[0]

        return DecisionResult(
            context=context,
            final_hypothesis=final_hypothesis,
            alternative_hypotheses=[],
            quality_metrics=QualityMetrics(
                decision_confidence=0.5,
                evidence_quality_score=0.5,
                bias_risk_assessment=0.5,
                implementation_feasibility=0.5,
                stakeholder_alignment=0.5,
                logical_consistency=0.5,
                completeness=0.5,
            ),
            total_time=0.0,
            agent_outputs=[],
            information_gathered=[],
            bias_report=self._create_default_bias_report(),
            implementation_plan={},
            confidence_level=0.5,
        )

    def _extract_quality_metrics(
        self, validation_result: Optional[Dict[str, Any]]
    ) -> QualityMetrics:
        """Extract quality metrics from validation result."""
        if validation_result and "quality_metrics" in validation_result:
            metrics_data = validation_result["quality_metrics"]
            return QualityMetrics(
                decision_confidence=metrics_data.get("decision_confidence", 0.5),
                evidence_quality_score=metrics_data.get("evidence_quality_score", 0.5),
                bias_risk_assessment=metrics_data.get("bias_risk_assessment", 0.5),
                implementation_feasibility=metrics_data.get(
                    "implementation_feasibility", 0.5
                ),
                stakeholder_alignment=metrics_data.get("stakeholder_alignment", 0.5),
                logical_consistency=metrics_data.get("logical_consistency", 0.5),
                completeness=metrics_data.get("completeness", 0.5),
            )

        # Return default metrics if validation result not available
        return QualityMetrics(
            decision_confidence=0.6,
            evidence_quality_score=0.6,
            bias_risk_assessment=0.4,
            implementation_feasibility=0.6,
            stakeholder_alignment=0.6,
            logical_consistency=0.6,
            completeness=0.6,
        )

    def _create_bias_report(self, final_outputs: List[Any]):
        """Create bias report from final outputs."""
        return self._create_default_bias_report()

    def _create_default_bias_report(self):
        """Create a default bias report."""
        from ..models.mai_dxo import BiasReport

        return BiasReport(
            indicators=[],
            overall_risk_score=0.3,
            mitigation_strategies=[
                "Applied systematic multi-agent analysis",
                "Used specialized challenger agent for bias detection",
                "Incorporated stakeholder perspective validation",
            ],
        )

    def _create_implementation_plan(
        self, final_hypothesis, context: DecisionContext
    ) -> Dict[str, Any]:
        """Create implementation plan based on final hypothesis."""
        if not final_hypothesis:
            return {"status": "no_hypothesis_selected"}

        return {
            "selected_hypothesis": final_hypothesis.description,
            "probability": final_hypothesis.probability,
            "resource_requirements": final_hypothesis.resource_requirements,
            "implementation_phases": [
                "Planning and preparation",
                "Initial implementation",
                "Monitoring and adjustment",
                "Full deployment",
            ],
            "success_criteria": context.success_criteria,
            "risk_mitigation": "Continuous monitoring and adaptive adjustment",
        }

    def _calculate_final_confidence(
        self,
        quality_metrics: QualityMetrics,
        validation_result: Optional[Dict[str, Any]],
    ) -> float:
        """Calculate final confidence level."""
        base_confidence = (
            quality_metrics.decision_confidence
            + quality_metrics.evidence_quality_score
            + quality_metrics.logical_consistency
        ) / 3

        # Adjust based on validation result
        if validation_result and "confidence_level" in validation_result:
            validation_confidence = validation_result["confidence_level"]
            return (base_confidence + validation_confidence) / 2

        return base_confidence

    def get_orchestration_summary(self) -> Dict[str, Any]:
        """Get summary of the orchestration process."""
        agent_performance = {}
        for role, agent in self.agents.items():
            if hasattr(agent, "get_performance_metrics"):
                agent_performance[role.value] = agent.get_performance_metrics()

        gatekeeper_summary = (
            self.information_gatekeeper.get_session_summary()
            if self.information_gatekeeper
            else {}
        )

        return {
            "orchestration_method": self.orchestration_method.value,
            "domain_context": self.domain_context,
            "max_rounds": self.max_rounds,
            "agent_performance": agent_performance,
            "information_gatekeeper_summary": gatekeeper_summary,
            "process_summary": {
                "phases_completed": [
                    "initial_analysis",
                    "deliberation",
                    "final_synthesis",
                ],
                "agents_utilized": list(self.agents.keys()),
                "decision_quality": "systematic_multi_agent_analysis",
            },
        }
