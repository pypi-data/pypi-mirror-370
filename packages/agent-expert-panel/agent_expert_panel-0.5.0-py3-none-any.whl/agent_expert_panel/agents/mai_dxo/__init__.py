"""
MAI-DxO specialized agent implementations.

This module contains the five specialized agents from the Microsoft Research
MAI-DxO study that achieved 80% diagnostic accuracy (4x better than human experts).

The five specialized agent roles:
1. Strategic Analyst (Primary Reasoner)
2. Resource Optimizer (Strategic Planner)
3. Critical Challenger (Devil's Advocate)
4. Stakeholder Steward (Governance Specialist)
5. Quality Validator (Final Checker)
"""

from .base_agent import MAIDxOBaseAgent
from .critical_challenger import CriticalChallengerAgent
from .quality_validator import QualityValidatorAgent
from .resource_optimizer import ResourceOptimizerAgent
from .stakeholder_steward import StakeholderStewardAgent
from .strategic_analyst import StrategicAnalystAgent

__all__ = [
    "MAIDxOBaseAgent",
    "StrategicAnalystAgent",
    "ResourceOptimizerAgent",
    "CriticalChallengerAgent",
    "StakeholderStewardAgent",
    "QualityValidatorAgent",
]
