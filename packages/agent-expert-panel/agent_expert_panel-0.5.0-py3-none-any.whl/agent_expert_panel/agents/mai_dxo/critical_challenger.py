"""
Critical Challenger Agent - Devil's Advocate for MAI-DxO.

The Critical Challenger systematically prevents bias and tests assumptions,
challenging popular hypotheses and identifying blind spots in reasoning.
"""

from typing import Any, Dict, List

from ...models.mai_dxo import (
    AgentRole,
    BiasType,
    BiasWarning,
    DecisionContext,
    Hypothesis,
)
from .base_agent import MAIDxOBaseAgent


class CriticalChallengerAgent(MAIDxOBaseAgent):
    """
    Critical Challenger (Devil's Advocate) from MAI-DxO research.

    Role: Systematic bias prevention and assumption testing
    Expertise: Cognitive bias detection and alternative scenario analysis
    Responsibility: Challenges popular hypotheses and identifies blind spots
    Decision Focus: "What could we be missing or getting wrong?"
    """

    def _get_system_prompt(self, agent_role: AgentRole, domain_context: str) -> str:
        """Get the specialized system prompt for the Critical Challenger."""
        return f"""You are the Critical Challenger in a MAI-DxO decision-making panel for {domain_context} decisions. Your mission is to identify weaknesses, biases, and blind spots in our reasoning process. Your role is essential for preventing mistakes and ensuring we consider all possibilities before reaching conclusions.

**Your Primary Responsibilities:**
1. **Bias Detection**: Identify cognitive biases affecting our reasoning (anchoring, confirmation bias, availability bias, etc.)
2. **Alternative Theories**: Propose alternative explanations that challenge the popular hypotheses
3. **Assumption Testing**: Question underlying assumptions we may be taking for granted
4. **Weakness Identification**: Point out vulnerabilities or gaps in our current approach
5. **Red Team Analysis**: Consider how our solution/conclusion might fail or be wrong

**Cognitive Biases to Watch For:**
- **Anchoring Bias**: Are we too influenced by initial information or assumptions?
- **Confirmation Bias**: Are we seeking evidence that supports our preferred conclusion?
- **Availability Bias**: Are we overweighting recent or memorable examples?
- **Overconfidence Bias**: Are we more certain than the evidence warrants?
- **Group Think**: Are we avoiding dissenting opinions or challenging perspectives?

**Your Analysis Approach:**
- Challenge the most popular or confident hypotheses first
- Ask "What if we're wrong about..." for key assumptions
- Look for missing perspectives or unconsidered stakeholders
- Identify potential failure modes and unintended consequences
- Test the robustness of conclusions under different scenarios

**Communication Style:**
- Lead with the most significant challenges or concerns
- Provide specific evidence or reasoning for your challenges
- Offer alternative explanations, not just criticism
- Quantify uncertainty and risk where possible
- Suggest ways to test or mitigate identified concerns

**Domain Expertise:** {domain_context.title()} risk analysis, critical thinking, and systematic challenge

Remember: Your job is not to be negative but to be systematically skeptical. Other agents will develop solutions (Strategic Analyst), optimize resources (Resource Optimizer), consider stakeholders (Stakeholder Steward), and validate quality (Quality Validator). Your crucial role is to ensure we don't fall into cognitive traps or miss critical risks."""

    async def _generate_initial_analysis(
        self, context: DecisionContext
    ) -> Dict[str, Any]:
        """Generate initial bias detection and challenge analysis."""
        # Detect potential biases in the problem framing
        framing_biases = self._detect_problem_framing_biases(context)

        # Identify critical assumptions that need testing
        critical_assumptions = self._identify_critical_assumptions(context)

        # Generate alternative problem interpretations
        alternative_interpretations = self._generate_alternative_interpretations(
            context
        )

        # Assess uncertainty and risk factors
        uncertainty_assessment = self._assess_uncertainty_factors(context)

        # Identify potential failure modes
        failure_modes = self._identify_potential_failure_modes(context)

        analysis = {
            "bias_detection": {
                "identified_framing_biases": framing_biases,
                "risk_level": self._calculate_bias_risk_level(framing_biases),
                "mitigation_recommendations": self._recommend_bias_mitigations(
                    framing_biases
                ),
            },
            "assumption_challenges": [
                {
                    "assumption": assumption,
                    "challenge_level": self._assess_assumption_risk(assumption),
                    "testing_approach": self._suggest_assumption_test(assumption),
                    "consequence_if_wrong": self._assess_assumption_consequences(
                        assumption
                    ),
                }
                for assumption in critical_assumptions
            ],
            "alternative_interpretations": alternative_interpretations,
            "uncertainty_assessment": uncertainty_assessment,
            "potential_failure_modes": failure_modes,
            "red_team_questions": self._generate_red_team_questions(context),
            "challenge_priorities": self._prioritize_challenges(
                framing_biases, critical_assumptions, failure_modes
            ),
        }

        return analysis

    def challenge_hypotheses(self, hypotheses: List[Hypothesis]) -> Dict[str, Any]:
        """Challenge a set of hypotheses for biases and weaknesses."""
        challenges = []

        for hyp in hypotheses:
            hypothesis_challenges = {
                "hypothesis_id": hyp.id,
                "hypothesis_description": hyp.description,
                "bias_warnings": self._detect_hypothesis_biases(hyp),
                "assumption_challenges": self._challenge_hypothesis_assumptions(hyp),
                "alternative_explanations": self._generate_alternative_explanations(
                    hyp
                ),
                "failure_scenarios": self._identify_hypothesis_failure_scenarios(hyp),
                "confidence_challenges": self._challenge_confidence_level(hyp),
                "evidence_gaps": self._identify_evidence_gaps(hyp),
            }
            challenges.append(hypothesis_challenges)

        # Overall assessment
        overall_assessment = {
            "hypothesis_challenges": challenges,
            "systemic_issues": self._identify_systemic_issues(hypotheses),
            "diversity_assessment": self._assess_hypothesis_diversity(hypotheses),
            "groupthink_risk": self._assess_groupthink_risk(hypotheses),
            "recommendations": self._generate_challenge_recommendations(hypotheses),
        }

        return overall_assessment

    def _detect_problem_framing_biases(
        self, context: DecisionContext
    ) -> List[BiasWarning]:
        """Detect biases in how the problem is framed."""
        warnings = []

        problem_desc = context.problem_description.lower()

        # Check for anchoring bias in problem description
        if any(word in problem_desc for word in ["should", "must", "need to"]):
            warnings.append(
                BiasWarning(
                    bias_type=BiasType.ANCHORING,
                    description="Problem description may be anchored to a predetermined solution",
                    severity=0.6,
                    mitigation_strategy="Reframe problem without solution implications",
                )
            )

        # Check for availability bias
        if any(word in problem_desc for word in ["recently", "just", "latest"]):
            warnings.append(
                BiasWarning(
                    bias_type=BiasType.AVAILABILITY,
                    description="Problem may be overly influenced by recent events",
                    severity=0.5,
                    mitigation_strategy="Consider historical patterns and long-term trends",
                )
            )

        # Check for confirmation bias in success criteria
        if len(context.success_criteria) == 1:
            warnings.append(
                BiasWarning(
                    bias_type=BiasType.CONFIRMATION,
                    description="Single success criterion may indicate narrow perspective",
                    severity=0.4,
                    mitigation_strategy="Expand success criteria to include multiple perspectives",
                )
            )

        # Check for overconfidence in constraints
        if context.constraints.confidence_threshold > 0.9:
            warnings.append(
                BiasWarning(
                    bias_type=BiasType.OVERCONFIDENCE,
                    description="Very high confidence threshold may indicate overconfidence in process",
                    severity=0.7,
                    mitigation_strategy="Lower confidence threshold and plan for uncertainty",
                )
            )

        return warnings

    def _identify_critical_assumptions(self, context: DecisionContext) -> List[str]:
        """Identify critical assumptions that need testing."""
        assumptions = []

        # Standard business assumptions to challenge
        if context.domain in ["business", "strategy"]:
            assumptions.extend(
                [
                    "Market conditions will remain stable during implementation",
                    "Stakeholders will support the chosen approach",
                    "Required resources will be available when needed",
                    "Implementation will proceed according to plan",
                    "Competitive landscape will not change significantly",
                    "Customer preferences and behavior will remain consistent",
                ]
            )

        # Technology assumptions
        if context.domain in ["technology", "technical"]:
            assumptions.extend(
                [
                    "Technical requirements are accurately understood",
                    "Chosen technology will remain viable long-term",
                    "Integration with existing systems will be smooth",
                    "Team has necessary technical expertise",
                    "Performance and scalability requirements are realistic",
                ]
            )

        # Resource-based assumptions
        if context.constraints.max_information_requests < 10:
            assumptions.append(
                "Limited information requests are sufficient for quality analysis"
            )

        if context.constraints.time_limit < 168:  # Less than a week
            assumptions.append(
                "Tight timeline allows for adequate analysis and planning"
            )

        # Stakeholder assumptions
        if len(context.stakeholders) > 5:
            assumptions.append("All stakeholders can be aligned despite complexity")

        return assumptions[:8]  # Return most critical assumptions

    def _generate_alternative_interpretations(
        self, context: DecisionContext
    ) -> List[Dict[str, Any]]:
        """Generate alternative ways to interpret the problem."""
        alternatives = []

        # Alternative problem framings
        alternatives.append(
            {
                "interpretation": "Symptoms vs Root Cause",
                "description": "What if the stated problem is actually a symptom of a deeper issue?",
                "investigation_approach": "Conduct root cause analysis using 5-whys or fishbone diagram",
                "implications": "May need to address underlying issues rather than surface problems",
            }
        )

        alternatives.append(
            {
                "interpretation": "Opportunity vs Problem",
                "description": "What if this 'problem' is actually an opportunity in disguise?",
                "investigation_approach": "Reframe as opportunity assessment and value creation",
                "implications": "Could lead to innovation rather than just problem-solving",
            }
        )

        alternatives.append(
            {
                "interpretation": "Internal vs External Origin",
                "description": "What if the real drivers are external forces rather than internal factors?",
                "investigation_approach": "Analyze external environment, market forces, regulatory changes",
                "implications": "May need adaptive strategy rather than control-based approach",
            }
        )

        # Domain-specific alternatives
        if context.domain in ["business", "strategy"]:
            alternatives.append(
                {
                    "interpretation": "Competitive Disadvantage vs Market Evolution",
                    "description": "What if this isn't about our weaknesses but about market evolution?",
                    "investigation_approach": "Study market evolution patterns and future trends",
                    "implications": "May need transformation rather than improvement",
                }
            )

        return alternatives

    def _assess_uncertainty_factors(self, context: DecisionContext) -> Dict[str, Any]:
        """Assess factors that contribute to uncertainty."""
        uncertainty_factors = []

        # Time-based uncertainty
        if context.constraints.time_limit < 72:
            uncertainty_factors.append(
                {
                    "factor": "Time Pressure",
                    "impact": "high",
                    "description": "Limited time increases risk of overlooking important factors",
                }
            )

        # Information uncertainty
        if not context.initial_information:
            uncertainty_factors.append(
                {
                    "factor": "Limited Initial Information",
                    "impact": "high",
                    "description": "Lack of baseline information increases decision risk",
                }
            )

        # Stakeholder uncertainty
        if len(context.stakeholders) > 3:
            uncertainty_factors.append(
                {
                    "factor": "Multiple Stakeholders",
                    "impact": "medium",
                    "description": "Complex stakeholder dynamics create implementation uncertainty",
                }
            )

        # Domain uncertainty
        if context.domain in ["technology", "innovation"]:
            uncertainty_factors.append(
                {
                    "factor": "Technology Evolution",
                    "impact": "medium",
                    "description": "Rapid technology change creates future viability uncertainty",
                }
            )

        return {
            "identified_factors": uncertainty_factors,
            "overall_uncertainty_level": self._calculate_uncertainty_level(
                uncertainty_factors
            ),
            "uncertainty_mitigation_strategies": self._suggest_uncertainty_mitigations(
                uncertainty_factors
            ),
        }

    def _identify_potential_failure_modes(
        self, context: DecisionContext
    ) -> List[Dict[str, Any]]:
        """Identify ways the decision or implementation could fail."""
        failure_modes = []

        # Resource failure modes
        failure_modes.append(
            {
                "failure_mode": "Resource Overrun",
                "probability": 0.3,
                "impact": "high",
                "description": "Resource requirements exceed availability due to unforeseen complications",
                "early_warning_signs": [
                    "Scope creep",
                    "Higher than expected resource needs",
                    "Resource competition",
                ],
                "mitigation": "Maintain contingency reserves and regular resource monitoring",
            }
        )

        failure_modes.append(
            {
                "failure_mode": "Timeline Slippage",
                "probability": 0.4,
                "impact": "medium",
                "description": "Implementation takes longer than planned",
                "early_warning_signs": [
                    "Dependency delays",
                    "Complexity underestimation",
                    "Resource unavailability",
                ],
                "mitigation": "Build buffer time and identify critical path dependencies",
            }
        )

        # Stakeholder failure modes
        if len(context.stakeholders) > 2:
            failure_modes.append(
                {
                    "failure_mode": "Stakeholder Resistance",
                    "probability": 0.35,
                    "impact": "high",
                    "description": "Key stakeholders withdraw support or actively resist",
                    "early_warning_signs": [
                        "Reduced engagement",
                        "Conflicting priorities",
                        "Communication breakdown",
                    ],
                    "mitigation": "Regular stakeholder engagement and alignment verification",
                }
            )

        # Assumption failure modes
        failure_modes.append(
            {
                "failure_mode": "Critical Assumption Violation",
                "probability": 0.25,
                "impact": "very_high",
                "description": "A fundamental assumption proves incorrect",
                "early_warning_signs": [
                    "Contradictory evidence",
                    "Changed conditions",
                    "Unexpected results",
                ],
                "mitigation": "Regular assumption testing and contingency planning",
            }
        )

        return failure_modes

    def _detect_hypothesis_biases(self, hypothesis: Hypothesis) -> List[BiasWarning]:
        """Detect biases in a specific hypothesis."""
        warnings = []

        # Check for overconfidence bias
        if hypothesis.probability > 0.8:
            warnings.append(
                BiasWarning(
                    bias_type=BiasType.OVERCONFIDENCE,
                    description=f"High probability ({hypothesis.probability}) may indicate overconfidence",
                    severity=0.6,
                    mitigation_strategy="Seek disconfirming evidence and alternative explanations",
                )
            )

        # Check for confirmation bias in supporting evidence
        if len(hypothesis.supporting_evidence) > 0:
            all_positive = all(
                evidence.reliability_score > 0.7
                for evidence in hypothesis.supporting_evidence
            )
            if all_positive:
                warnings.append(
                    BiasWarning(
                        bias_type=BiasType.CONFIRMATION,
                        description="All supporting evidence is highly positive - may indicate confirmation bias",
                        severity=0.5,
                        mitigation_strategy="Actively seek contradictory evidence and alternative sources",
                    )
                )

        # Check for anchoring to description keywords
        common_anchors = ["best", "optimal", "proven", "guaranteed", "simple"]
        if any(anchor in hypothesis.description.lower() for anchor in common_anchors):
            warnings.append(
                BiasWarning(
                    bias_type=BiasType.ANCHORING,
                    description="Hypothesis description contains potentially anchoring language",
                    severity=0.4,
                    mitigation_strategy="Reframe hypothesis in neutral, testable terms",
                )
            )

        return warnings

    def _challenge_hypothesis_assumptions(self, hypothesis: Hypothesis) -> List[str]:
        """Challenge key assumptions underlying a hypothesis."""
        challenges = []

        # Standard assumption challenges
        challenges.append(
            f"What if the success criteria for '{hypothesis.description}' are different than expected?"
        )
        challenges.append(
            f"What if implementation of '{hypothesis.description}' creates unintended consequences?"
        )
        challenges.append(
            f"What if the required resources for '{hypothesis.description}' are unavailable?"
        )

        # Probability-based challenges
        if hypothesis.probability > 0.7:
            challenges.append(
                f"What evidence would lower the {hypothesis.probability * 100:.0f}% confidence in this hypothesis?"
            )

        # Resource-based challenges
        if hypothesis.resource_requirements:
            high_resource_keys = [
                k
                for k, v in hypothesis.resource_requirements.items()
                if isinstance(v, str) and v in ["high", "very high"]
            ]
            if high_resource_keys:
                challenges.append(
                    f"What if {', '.join(high_resource_keys)} resources are more constrained than assumed?"
                )

        return challenges

    def _generate_alternative_explanations(self, hypothesis: Hypothesis) -> List[str]:
        """Generate alternative explanations that could explain the same observations."""
        alternatives = []

        # Generic alternative patterns
        alternatives.append(
            "The same outcome could be achieved through a completely different approach"
        )
        alternatives.append(
            "What appears to support this hypothesis might actually support the opposite conclusion"
        )
        alternatives.append(
            "External factors, not internal actions, might be the real drivers"
        )

        # Hypothesis-specific alternatives based on content
        if "market" in hypothesis.description.lower():
            alternatives.append(
                "Market conditions may be fundamentally different than assumed"
            )

        if "technology" in hypothesis.description.lower():
            alternatives.append("Technology solution may be solving the wrong problem")

        if (
            "invest" in hypothesis.description.lower()
            or "resource" in hypothesis.description.lower()
        ):
            alternatives.append(
                "Hidden resource requirements may make this approach unfeasible"
            )

        return alternatives[:4]  # Return top alternatives

    def _generate_red_team_questions(self, context: DecisionContext) -> List[str]:
        """Generate red team questions to stress-test the approach."""
        questions = [
            "What would an expert critic say is fundamentally wrong with our approach?",
            "If this decision fails spectacularly, what will the post-mortem reveal we missed?",
            "What assumption, if proven wrong, would completely invalidate our analysis?",
            "How would our strongest competitor exploit any weaknesses in this approach?",
            "What are we not seeing because we're too close to the problem?",
            "If we had unlimited time and resources, how would our approach change?",
            "What would someone with the opposite perspective recommend?",
            "What early warning signs should trigger us to abandon this approach?",
        ]

        # Add domain-specific red team questions
        if context.domain in ["business", "strategy"]:
            questions.extend(
                [
                    "How could this decision backfire and damage our competitive position?",
                    "What customer reaction are we not anticipating?",
                    "How might regulatory changes affect this approach?",
                ]
            )

        return questions[:10]  # Return top questions

    def _prioritize_challenges(
        self,
        biases: List[BiasWarning],
        assumptions: List[str],
        failure_modes: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Prioritize challenges by impact and likelihood."""
        challenges = []

        # Add bias challenges
        for bias in biases:
            challenges.append(
                {
                    "type": "bias",
                    "priority": bias.severity,
                    "description": bias.description,
                    "mitigation": bias.mitigation_strategy,
                }
            )

        # Add assumption challenges (high priority)
        for assumption in assumptions[:3]:  # Top 3 assumptions
            challenges.append(
                {
                    "type": "assumption",
                    "priority": 0.8,  # High priority
                    "description": f"Challenge assumption: {assumption}",
                    "mitigation": f"Test assumption: {assumption}",
                }
            )

        # Add failure mode challenges
        for failure_mode in failure_modes:
            if failure_mode["impact"] in ["high", "very_high"]:
                challenges.append(
                    {
                        "type": "failure_mode",
                        "priority": failure_mode["probability"],
                        "description": f"Mitigate risk: {failure_mode['failure_mode']}",
                        "mitigation": failure_mode["mitigation"],
                    }
                )

        # Sort by priority (descending)
        return sorted(challenges, key=lambda x: x["priority"], reverse=True)[:8]

    def _calculate_bias_risk_level(self, biases: List[BiasWarning]) -> str:
        """Calculate overall bias risk level."""
        if not biases:
            return "low"

        avg_severity = sum(bias.severity for bias in biases) / len(biases)

        if avg_severity >= 0.7:
            return "high"
        elif avg_severity >= 0.4:
            return "medium"
        else:
            return "low"

    def _recommend_bias_mitigations(self, biases: List[BiasWarning]) -> List[str]:
        """Recommend specific bias mitigation strategies."""
        mitigations = []

        bias_types_found = {bias.bias_type for bias in biases}

        if BiasType.ANCHORING in bias_types_found:
            mitigations.append("Use multiple starting points and compare conclusions")

        if BiasType.CONFIRMATION in bias_types_found:
            mitigations.append("Actively seek disconfirming evidence")

        if BiasType.OVERCONFIDENCE in bias_types_found:
            mitigations.append("Use confidence intervals and uncertainty ranges")

        if BiasType.AVAILABILITY in bias_types_found:
            mitigations.append("Consider base rates and historical patterns")

        # Add general mitigations
        mitigations.extend(
            [
                "Implement structured decision processes",
                "Use external perspectives and devil's advocate",
                "Document assumptions and test them systematically",
            ]
        )

        return mitigations[:5]  # Return top mitigations

    def _assess_assumption_risk(self, assumption: str) -> str:
        """Assess risk level of a specific assumption."""
        # Simple heuristic based on assumption content
        high_risk_words = ["stable", "remain", "will", "continue", "maintain"]
        medium_risk_words = ["available", "support", "able", "can", "possible"]

        assumption_lower = assumption.lower()

        if any(word in assumption_lower for word in high_risk_words):
            return "high"
        elif any(word in assumption_lower for word in medium_risk_words):
            return "medium"
        else:
            return "low"

    def _suggest_assumption_test(self, assumption: str) -> str:
        """Suggest how to test a specific assumption."""
        assumption_lower = assumption.lower()

        if "market" in assumption_lower:
            return "Conduct market research and trend analysis"
        elif "stakeholder" in assumption_lower:
            return "Survey stakeholders and assess commitment levels"
        elif "resource" in assumption_lower:
            return "Audit resource availability and create contingency plans"
        elif "technical" in assumption_lower:
            return "Prototype key technical components and validate feasibility"
        else:
            return "Gather evidence through research, testing, or expert consultation"

    def _assess_assumption_consequences(self, assumption: str) -> str:
        """Assess consequences if assumption proves wrong."""
        return f"If '{assumption}' proves incorrect, may require significant replanning and resource reallocation"

    def _calculate_uncertainty_level(self, factors: List[Dict[str, Any]]) -> str:
        """Calculate overall uncertainty level."""
        if not factors:
            return "low"

        high_impact_count = sum(
            1 for factor in factors if factor.get("impact") == "high"
        )

        if high_impact_count >= 2:
            return "high"
        elif high_impact_count >= 1 or len(factors) >= 3:
            return "medium"
        else:
            return "low"

    def _suggest_uncertainty_mitigations(
        self, factors: List[Dict[str, Any]]
    ) -> List[str]:
        """Suggest ways to mitigate uncertainty."""
        mitigations = []

        for factor in factors:
            if factor.get("impact") == "high":
                mitigations.append(
                    f"Address {factor['factor']}: {factor['description']}"
                )

        # Add general uncertainty mitigations
        mitigations.extend(
            [
                "Build flexibility and adaptability into plans",
                "Create multiple scenarios and contingency plans",
                "Implement early warning systems and monitoring",
                "Maintain decision reversibility where possible",
            ]
        )

        return mitigations[:5]

    def _identify_systemic_issues(self, hypotheses: List[Hypothesis]) -> List[str]:
        """Identify systemic issues across all hypotheses."""
        issues = []

        if not hypotheses:
            return ["No hypotheses generated - may indicate analysis paralysis"]

        # Check probability distribution
        probabilities = [h.probability for h in hypotheses]
        if max(probabilities) - min(probabilities) < 0.2:
            issues.append(
                "All hypotheses have similar probabilities - may lack discriminating analysis"
            )

        # Check evidence distribution
        evidence_counts = [len(h.supporting_evidence) for h in hypotheses]
        if all(count == 0 for count in evidence_counts):
            issues.append(
                "No supporting evidence for any hypothesis - conclusions may be premature"
            )

        # Check resource requirements
        if all(h.resource_requirements for h in hypotheses):
            high_resource_count = sum(
                1
                for h in hypotheses
                if any(
                    str(v).lower() in ["high", "very high"]
                    for v in h.resource_requirements.values()
                    if isinstance(v, str)
                )
            )
            if high_resource_count == len(hypotheses):
                issues.append(
                    "All hypotheses require high resources - may need more efficient alternatives"
                )

        return issues

    def _assess_hypothesis_diversity(
        self, hypotheses: List[Hypothesis]
    ) -> Dict[str, Any]:
        """Assess diversity of hypotheses."""
        if len(hypotheses) < 2:
            return {
                "diversity_level": "insufficient",
                "recommendation": "Generate more diverse alternatives",
            }

        # Simple diversity assessment based on description keywords
        keywords = []
        for h in hypotheses:
            keywords.extend(h.description.lower().split())

        unique_keywords = set(keywords)
        diversity_ratio = len(unique_keywords) / len(keywords) if keywords else 0

        if diversity_ratio > 0.7:
            diversity_level = "high"
        elif diversity_ratio > 0.5:
            diversity_level = "medium"
        else:
            diversity_level = "low"

        return {
            "diversity_level": diversity_level,
            "diversity_ratio": diversity_ratio,
            "recommendation": self._get_diversity_recommendation(diversity_level),
        }

    def _get_diversity_recommendation(self, diversity_level: str) -> str:
        """Get recommendation based on diversity level."""
        if diversity_level == "low":
            return "Generate more diverse hypothesis alternatives using different approaches"
        elif diversity_level == "medium":
            return "Consider additional perspectives or stakeholder viewpoints"
        else:
            return "Good diversity - continue with current hypothesis set"

    def _assess_groupthink_risk(self, hypotheses: List[Hypothesis]) -> Dict[str, Any]:
        """Assess risk of groupthink in hypothesis generation."""
        risk_indicators = []

        # Check for similar probability clustering
        probabilities = [h.probability for h in hypotheses]
        if len(set(round(p, 1) for p in probabilities)) < len(probabilities) * 0.7:
            risk_indicators.append("Similar probability clustering")

        # Check for similar resource requirements
        if len(hypotheses) > 1:
            resource_patterns = [str(h.resource_requirements) for h in hypotheses]
            if len(set(resource_patterns)) < len(resource_patterns) * 0.7:
                risk_indicators.append("Similar resource requirement patterns")

        risk_level = (
            "high"
            if len(risk_indicators) >= 2
            else "medium"
            if risk_indicators
            else "low"
        )

        return {
            "risk_level": risk_level,
            "risk_indicators": risk_indicators,
            "mitigation": "Seek external perspectives and challenge consensus thinking"
            if risk_level != "low"
            else "Continue current approach",
        }

    def _generate_challenge_recommendations(
        self, hypotheses: List[Hypothesis]
    ) -> List[str]:
        """Generate overall recommendations for challenging the hypothesis set."""
        recommendations = []

        # Analysis-based recommendations
        recommendations.extend(
            [
                "Test the most confident hypothesis with contradictory evidence",
                "Explore completely different approaches not yet considered",
                "Seek perspectives from stakeholders not yet consulted",
                "Consider what conditions would make each hypothesis fail",
            ]
        )

        # Evidence-based recommendations
        if hypotheses:
            max_evidence = max(len(h.supporting_evidence) for h in hypotheses)
            if max_evidence == 0:
                recommendations.append(
                    "Gather supporting evidence before finalizing any hypothesis"
                )

        return recommendations[:5]

    def _identify_evidence_gaps(self, hypothesis: Hypothesis) -> List[str]:
        """Identify evidence gaps for a specific hypothesis."""
        gaps = []

        if not hypothesis.supporting_evidence:
            gaps.append("No supporting evidence provided")

        if hypothesis.probability > 0.7 and len(hypothesis.supporting_evidence) < 2:
            gaps.append("High confidence with insufficient evidence")

        # Check evidence quality
        if hypothesis.supporting_evidence:
            low_quality_evidence = [
                e for e in hypothesis.supporting_evidence if e.reliability_score < 0.6
            ]
            if low_quality_evidence:
                gaps.append(
                    f"{len(low_quality_evidence)} pieces of low-quality evidence"
                )

        return gaps

    def _challenge_confidence_level(self, hypothesis: Hypothesis) -> List[str]:
        """Challenge the confidence level of a hypothesis."""
        challenges = []

        if hypothesis.probability > 0.8:
            challenges.append(
                "Extremely high confidence - what could prove this wrong?"
            )

        if hypothesis.probability < 0.3:
            challenges.append("Low confidence - why include this hypothesis?")

        # Evidence-confidence mismatch
        evidence_count = len(hypothesis.supporting_evidence)
        if hypothesis.probability > 0.7 and evidence_count < 2:
            challenges.append("High confidence not supported by evidence quantity")

        return challenges

    def _identify_hypothesis_failure_scenarios(
        self, hypothesis: Hypothesis
    ) -> List[str]:
        """Identify scenarios where hypothesis could fail."""
        scenarios = []

        # Resource-based failures
        if hypothesis.resource_requirements:
            high_reqs = [
                k
                for k, v in hypothesis.resource_requirements.items()
                if isinstance(v, str) and "high" in v.lower()
            ]
            if high_reqs:
                scenarios.append(
                    f"Failure if {', '.join(high_reqs)} become unavailable"
                )

        # Assumption-based failures
        scenarios.extend(
            [
                "Failure if market conditions change unexpectedly",
                "Failure if stakeholder support is withdrawn",
                "Failure if implementation proves more complex than anticipated",
            ]
        )

        return scenarios[:3]
