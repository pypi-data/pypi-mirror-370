"""
Agent template system for MAOS Claude Code integration.

This module provides pre-defined agent templates that can be used to create
specialized Claude Code agents for different types of tasks.
"""

from .agent_templates import (
    AgentTemplateRegistry,
    create_agent_from_template,
    get_available_templates,
    register_custom_template
)

__all__ = [
    "AgentTemplateRegistry",
    "create_agent_from_template", 
    "get_available_templates",
    "register_custom_template"
]