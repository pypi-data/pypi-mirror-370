"""
Information management module for MAI-DxO.

This module implements the Information Gatekeeper pattern from the MAI-DxO research,
which controls strategic information revelation, session tracking, and quality assurance.
"""

from .gatekeeper import InformationGatekeeper

__all__ = ["InformationGatekeeper"]
