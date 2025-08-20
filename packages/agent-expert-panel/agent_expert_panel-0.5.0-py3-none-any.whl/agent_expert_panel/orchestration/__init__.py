"""
MAI-DxO orchestration implementations using different Autogen patterns.

This module provides multiple implementations of the MAI-DxO architecture
using different orchestration patterns from the Autogen framework.

Each orchestration pattern offers unique benefits:
- RoundRobin: Sequential structured analysis
- Selector: Dynamic agent selection based on needs
- MagenticOne: Central coordination with specialist delegation
- MixtureOfAgents: Parallel execution with weighted synthesis
- MultiAgentDebate: Adversarial discourse and argument testing
- SocietyOfMind: Hierarchical cognitive architecture with emergent intelligence
"""

from .magentic_one import MagenticOneMAIDxO
from .mixture_of_agents import MixtureOfAgentsMAIDxO
from .multi_agent_debate import MultiAgentDebateMAIDxO
from .round_robin import RoundRobinMAIDxO
from .selector import SelectorMAIDxO
from .society_of_mind import SocietyOfMindMAIDxO

__all__ = [
    "RoundRobinMAIDxO",
    "SelectorMAIDxO",
    "MagenticOneMAIDxO",
    "MixtureOfAgentsMAIDxO",
    "MultiAgentDebateMAIDxO",
    "SocietyOfMindMAIDxO",
]
