"""
Panel-related models and enums for the Expert Panel system.
"""

from enum import Enum
from typing import Any
from pydantic import BaseModel


class DiscussionPattern(Enum):
    """Available discussion patterns for agent interaction."""

    ROUND_ROBIN = "round_robin"
    OPEN_FLOOR = "open_floor"
    STRUCTURED_DEBATE = "structured_debate"


class PanelResult(BaseModel):
    """Results from a panel discussion."""

    topic: str
    discussion_pattern: DiscussionPattern
    agents_participated: list[str]
    discussion_history: list[dict[str, Any]]
    consensus_reached: bool
    final_recommendation: str
    total_rounds: int
