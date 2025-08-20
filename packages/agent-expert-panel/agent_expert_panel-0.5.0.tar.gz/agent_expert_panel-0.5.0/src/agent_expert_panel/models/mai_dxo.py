"""
MAI-DxO (Multi-Agent Intelligence Diagnostic Orchestrator) models and data structures.

Based on Microsoft Research's breakthrough multi-agent architecture that achieved
80% diagnostic accuracy (4x better than human experts) through systematic multi-agent analysis.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """The five specialized agent roles from MAI-DxO research.

    Each role represents a specialized perspective in the decision-making process:
    - STRATEGIC_ANALYST: Primary reasoner and hypothesis generator
    - RESOURCE_OPTIMIZER: Strategic planner and efficiency specialist
    - CRITICAL_CHALLENGER: Devil's advocate and bias detector
    - STAKEHOLDER_STEWARD: Governance specialist and ethics guardian
    - QUALITY_VALIDATOR: Final checker and validation specialist
    """

    STRATEGIC_ANALYST = "strategic_analyst"
    RESOURCE_OPTIMIZER = "resource_optimizer"
    CRITICAL_CHALLENGER = "critical_challenger"
    STAKEHOLDER_STEWARD = "stakeholder_steward"
    QUALITY_VALIDATOR = "quality_validator"


class MessageType(str, Enum):
    """Types of messages agents can send to each other.

    Defines the different categories of communication between agents
    during the decision-making process.
    """

    ANALYSIS = "analysis"
    CHALLENGE = "challenge"
    INFORMATION_REQUEST = "information_request"
    CONSENSUS = "consensus"
    QUALITY_CHECK = "quality_check"
    RESOURCE_EVALUATION = "resource_evaluation"
    STAKEHOLDER_ASSESSMENT = "stakeholder_assessment"


class BiasType(str, Enum):
    """Types of cognitive biases that can affect decision-making.

    Based on research-identified biases that the MAI-DxO system
    is designed to detect and mitigate.
    """

    ANCHORING = "anchoring"
    CONFIRMATION = "confirmation"
    AVAILABILITY = "availability"
    OVERCONFIDENCE = "overconfidence"
    GROUPTHINK = "groupthink"


class InformationType(str, Enum):
    """Types of information that can be requested.

    Categorizes information requests by their source and processing requirements.
    """

    INTERNAL_DELIBERATION = "internal_deliberation"
    EXTERNAL_RESEARCH = "external_research"
    USER_SPECIFIC = "user_specific"


class Evidence(BaseModel):
    """Evidence supporting a hypothesis or decision.

    Attributes:
        id: Unique identifier for the evidence
        source: Source of the evidence (e.g., 'internal_analysis', 'external_research')
        content: The actual evidence content
        reliability_score: Score indicating reliability of the evidence (0.0-1.0)
        relevance_score: Score indicating relevance to the decision (0.0-1.0)
        timestamp: When the evidence was gathered
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    source: str
    content: str
    reliability_score: float = Field(ge=0.0, le=1.0)
    relevance_score: float = Field(ge=0.0, le=1.0)
    timestamp: str


class Hypothesis(BaseModel):
    """A potential solution or diagnosis with associated confidence.

    Attributes:
        id: Unique identifier for the hypothesis
        description: Detailed description of the hypothesis
        probability: Probability/confidence score for this hypothesis (0.0-1.0)
        supporting_evidence: List of evidence supporting this hypothesis
        challenges: List of challenges or concerns raised against this hypothesis
        resource_requirements: Required resources for implementing this hypothesis
        stakeholder_impact: Impact assessment for different stakeholders
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    probability: float = Field(ge=0.0, le=1.0)
    supporting_evidence: List[Evidence] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    resource_requirements: Dict[str, Any] = Field(default_factory=dict)
    stakeholder_impact: Dict[str, Any] = Field(default_factory=dict)


class Action(BaseModel):
    """A potential action for information gathering or analysis.

    Attributes:
        id: Unique identifier for the action
        description: Description of what the action entails
        information_type: Type of information this action will gather
        expected_information_gain: Expected value of information gained (0.0-1.0)
        time_required: Estimated time required in hours
        prerequisites: List of prerequisite actions or conditions
        priority_score: Priority score for action execution
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    information_type: InformationType
    expected_information_gain: float = Field(ge=0.0, le=1.0)
    time_required: float = Field(ge=0.0)  # in hours
    prerequisites: List[str] = Field(default_factory=list)
    priority_score: Optional[float] = None


class ResourceConstraints(BaseModel):
    """Resource constraints for the decision-making process.

    Attributes:
        time_limit: Maximum time allowed for decision-making in hours
        quality_threshold: Minimum quality score required (0.0-1.0)
        confidence_threshold: Minimum confidence level required (0.0-1.0)
        max_information_requests: Maximum number of information requests allowed
    """

    time_limit: float = Field(ge=0.0)  # in hours
    quality_threshold: float = Field(ge=0.0, le=1.0)
    confidence_threshold: float = Field(ge=0.0, le=1.0)
    max_information_requests: int = Field(ge=1, default=20)


class BiasWarning(BaseModel):
    """Warning about potential cognitive bias.

    Attributes:
        bias_type: Type of bias detected
        description: Description of the bias concern
        severity: Severity level of the bias (0.0-1.0)
        mitigation_strategy: Recommended strategy to mitigate the bias
    """

    bias_type: BiasType
    description: str
    severity: float = Field(ge=0.0, le=1.0)
    mitigation_strategy: str


class BiasReport(BaseModel):
    """Report of detected biases and mitigation strategies.

    Attributes:
        indicators: List of bias warnings detected during the process
        overall_risk_score: Overall bias risk assessment (0.0-1.0)
        mitigation_strategies: List of strategies used to mitigate biases
    """

    indicators: List[BiasWarning] = Field(default_factory=list)
    overall_risk_score: float = Field(ge=0.0, le=1.0)
    mitigation_strategies: List[str] = Field(default_factory=list)


class AgentOutput(BaseModel):
    """Output from an individual agent.

    Attributes:
        agent_role: The role of the agent generating this output
        message_type: Type of message being sent
        content: The actual content of the agent's output
        confidence_level: Agent's confidence in their output (0.0-1.0)
        supporting_evidence: List of evidence supporting this output
        timestamp: When this output was generated
        reasoning: Explanation of the agent's reasoning process
    """

    agent_role: AgentRole
    message_type: MessageType
    content: Dict[str, Any]
    confidence_level: float = Field(ge=0.0, le=1.0)
    supporting_evidence: List[Evidence] = Field(default_factory=list)
    timestamp: str
    reasoning: str


class AgentMessage(BaseModel):
    """Message sent between agents.

    Attributes:
        id: Unique identifier for the message
        sender: Agent role sending the message
        recipient: Agent role receiving the message, or "ALL" for broadcast
        message_type: Type of message being sent
        content: Message content
        confidence_level: Sender's confidence in the message (0.0-1.0)
        supporting_evidence: Evidence supporting the message
        timestamp: When the message was sent
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    sender: AgentRole
    recipient: Union[AgentRole, str]  # "ALL" for broadcast
    message_type: MessageType
    content: Dict[str, Any]
    confidence_level: float = Field(ge=0.0, le=1.0)
    supporting_evidence: List[Evidence] = Field(default_factory=list)
    timestamp: str


class InformationResponse(BaseModel):
    """Response from the Information Gatekeeper.

    Attributes:
        query: The original information request query
        information: The information content returned
        source_type: Type of source (e.g., 'database', 'web_search', 'user_input')
        reliability_score: Reliability of the information source (0.0-1.0)
        metadata: Additional metadata about the information
        timestamp: When the information was retrieved
    """

    query: str
    information: str
    source_type: str
    reliability_score: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str


class DecisionContext(BaseModel):
    """Context for a decision-making session.

    Attributes:
        id: Unique identifier for the decision context
        problem_description: Detailed description of the problem to solve
        domain: Domain context (e.g., 'business', 'technical', 'medical')
        stakeholders: List of stakeholders affected by the decision
        constraints: Resource and quality constraints for the decision process
        initial_information: Any initial information provided
        success_criteria: Criteria that define successful decision outcomes
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    problem_description: str
    domain: str
    stakeholders: List[str] = Field(default_factory=list)
    constraints: ResourceConstraints
    initial_information: Dict[str, Any] = Field(default_factory=dict)
    success_criteria: List[str] = Field(default_factory=list)


class QualityMetrics(BaseModel):
    """Quality metrics for evaluating decisions.

    Attributes:
        decision_confidence: Confidence in the final decision (0.0-1.0)
        evidence_quality_score: Quality of supporting evidence (0.0-1.0)
        bias_risk_assessment: Risk of bias affecting the decision (0.0-1.0)
        implementation_feasibility: Feasibility of implementing the decision (0.0-1.0)
        stakeholder_alignment: Level of stakeholder alignment (0.0-1.0)
        logical_consistency: Logical consistency of the reasoning (0.0-1.0)
        completeness: Completeness of the analysis (0.0-1.0)
        interaction_strength: Strength score of the interaction between the agents (0.0-1.0)
    """

    decision_confidence: float = Field(ge=0.0, le=1.0)
    evidence_quality_score: float = Field(ge=0.0, le=1.0)
    bias_risk_assessment: float = Field(ge=0.0, le=1.0)
    implementation_feasibility: float = Field(ge=0.0, le=1.0)
    stakeholder_alignment: float = Field(ge=0.0, le=1.0)
    logical_consistency: float = Field(ge=0.0, le=1.0)
    completeness: float = Field(ge=0.0, le=1.0)
    interaction_strength: float = Field(ge=0.0, le=1.0)


class DecisionResult(BaseModel):
    """Final result of the MAI-DxO decision process.

    Attributes:
        context: The original decision context
        final_hypothesis: The recommended final decision/hypothesis
        alternative_hypotheses: Alternative options considered
        quality_metrics: Quality assessment metrics for the decision
        total_time: Total time spent on the decision process in hours
        agent_outputs: All outputs generated by agents during the process
        information_gathered: Information collected during the process
        bias_report: Analysis of biases detected and mitigated
        implementation_plan: Plan for implementing the decision
        confidence_level: Overall confidence in the final decision (0.0-1.0)
    """

    context: DecisionContext
    final_hypothesis: Hypothesis
    alternative_hypotheses: List[Hypothesis] = Field(default_factory=list)
    quality_metrics: QualityMetrics
    total_time: float = Field(ge=0.0)
    agent_outputs: List[AgentOutput] = Field(default_factory=list)
    information_gathered: List[InformationResponse] = Field(default_factory=list)
    bias_report: BiasReport
    implementation_plan: Dict[str, Any] = Field(default_factory=dict)
    confidence_level: float = Field(ge=0.0, le=1.0)


class OrchestrationMethod(str, Enum):
    """Different methods for orchestrating the agent panel.

    Each method provides a different approach to coordinating the five specialized agents:
    - ROUND_ROBIN: Sequential agent execution
    - SELECTOR: Dynamic agent selection based on context
    - MAGENTIC_ONE: Central coordinator with delegation
    - MIXTURE_OF_AGENTS: Parallel execution with synthesis
    - MULTI_AGENT_DEBATE: Adversarial discourse and argument
    - SOCIETY_OF_MIND: Hierarchical cognitive architecture
    """

    ROUND_ROBIN = "round_robin"
    SELECTOR = "selector"
    MAGENTIC_ONE = "magentic_one"
    MIXTURE_OF_AGENTS = "mixture_of_agents"
    MULTI_AGENT_DEBATE = "multi_agent_debate"
    SOCIETY_OF_MIND = "society_of_mind"
