"""
Multi-Agent Orchestration System (MAOS)
Core orchestration layer for distributed agent management.
"""

__version__ = "1.0.0"
__author__ = "MAOS Development Team"

from .core.orchestrator import Orchestrator
from .core.task_planner import TaskPlanner
from .core.agent_manager import AgentManager
from .core.resource_allocator import ResourceAllocator

__all__ = [
    "Orchestrator",
    "TaskPlanner", 
    "AgentManager",
    "ResourceAllocator",
]