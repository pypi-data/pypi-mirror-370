"""
Shared orchestrator instance and initialization for CLI commands.

This module prevents circular imports by providing a central place
for the orchestrator that can be imported by both main.py and commands.
"""

from typing import Optional
from ..core.orchestrator import Orchestrator

# Global orchestrator instance
_orchestrator: Optional[Orchestrator] = None


def init_orchestrator() -> Orchestrator:
    """Initialize or get the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator


def get_orchestrator() -> Optional[Orchestrator]:
    """Get the current orchestrator instance if initialized."""
    return _orchestrator


def reset_orchestrator() -> None:
    """Reset the global orchestrator instance."""
    global _orchestrator
    _orchestrator = None