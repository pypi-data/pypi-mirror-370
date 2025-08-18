"""
API contracts and schemas for MAOS orchestration system.
"""

from .schemas import (
    TaskSchema, AgentSchema, ResourceSchema, ExecutionPlanSchema,
    TaskSubmissionRequest, TaskResponse, AgentCreateRequest, AgentResponse,
    ResourceCreateRequest, ResourceResponse, SystemStatusResponse,
    MetricsResponse, CheckpointResponse
)

from .rest_api import MAOSRestAPI
from .claude_integration import ClaudeTaskIntegration

__all__ = [
    # Schemas
    "TaskSchema",
    "AgentSchema", 
    "ResourceSchema",
    "ExecutionPlanSchema",
    "TaskSubmissionRequest",
    "TaskResponse",
    "AgentCreateRequest", 
    "AgentResponse",
    "ResourceCreateRequest",
    "ResourceResponse",
    "SystemStatusResponse",
    "MetricsResponse",
    "CheckpointResponse",
    
    # APIs
    "MAOSRestAPI",
    "ClaudeTaskIntegration",
]