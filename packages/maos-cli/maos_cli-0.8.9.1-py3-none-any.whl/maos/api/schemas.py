"""
API schemas and data contracts for MAOS orchestration system.
"""

from typing import Dict, List, Optional, Any, Set, Union
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum

# Enums for API
class TaskStatusAPI(str, Enum):
    """Task status for API responses."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriorityAPI(str, Enum):
    """Task priority for API requests/responses."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentStatusAPI(str, Enum):
    """Agent status for API responses."""
    INITIALIZING = "initializing"
    IDLE = "idle"
    BUSY = "busy"
    OVERLOADED = "overloaded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    TERMINATED = "terminated"


class AgentCapabilityAPI(str, Enum):
    """Agent capabilities for API requests/responses."""
    TASK_EXECUTION = "task_execution"
    DATA_PROCESSING = "data_processing"
    API_INTEGRATION = "api_integration"
    FILE_OPERATIONS = "file_operations"
    COMPUTATION = "computation"
    COMMUNICATION = "communication"
    MONITORING = "monitoring"
    COORDINATION = "coordination"


class ResourceTypeAPI(str, Enum):
    """Resource types for API requests/responses."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    CUSTOM = "custom"


# Base schemas
class TaskDependencySchema(BaseModel):
    """Schema for task dependencies."""
    task_id: UUID
    dependency_type: str = "completion"
    required: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskSchema(BaseModel):
    """Schema for task representation."""
    id: UUID
    name: str
    description: Optional[str] = None
    status: TaskStatusAPI
    priority: TaskPriorityAPI
    agent_id: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None
    dependencies: List[TaskDependencySchema] = Field(default_factory=list)
    subtasks: List[UUID] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3
    resource_requirements: Dict[str, Any] = Field(default_factory=dict)
    tags: Set[str] = Field(default_factory=set)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentMetricsSchema(BaseModel):
    """Schema for agent performance metrics."""
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    success_rate: float = 1.0
    last_heartbeat: datetime
    health_score: float = 1.0


class AgentSchema(BaseModel):
    """Schema for agent representation."""
    id: UUID
    name: str
    type: str
    status: AgentStatusAPI
    capabilities: Set[AgentCapabilityAPI]
    current_task_id: Optional[UUID] = None
    task_queue: List[UUID] = Field(default_factory=list)
    max_concurrent_tasks: int = 1
    resource_limits: Dict[str, Any] = Field(default_factory=dict)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    started_at: Optional[datetime] = None
    last_seen: datetime
    metrics: AgentMetricsSchema
    tags: Set[str] = Field(default_factory=set)
    health_check_interval: int = 30
    heartbeat_timeout: int = 90


class ResourceAllocationSchema(BaseModel):
    """Schema for resource allocation representation."""
    agent_id: UUID
    amount: float
    allocated_at: datetime
    released_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResourceSchema(BaseModel):
    """Schema for resource representation."""
    id: UUID
    name: str
    type: ResourceTypeAPI
    total_capacity: float
    available_capacity: float
    allocated_capacity: float
    reserved_capacity: float = 0.0
    unit: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    allocations: List[ResourceAllocationSchema] = Field(default_factory=list)
    tags: Set[str] = Field(default_factory=set)
    location: str = "local"
    health_status: str = "healthy"
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    cost_per_unit: float = 0.0
    minimum_allocation: float = 0.0
    maximum_allocation: float = 0.0


class ExecutionPlanSchema(BaseModel):
    """Schema for execution plan representation."""
    id: UUID
    tasks: Dict[UUID, TaskSchema]
    parallel_groups: List[List[UUID]]
    critical_path: List[UUID]
    estimated_duration: int
    resource_requirements: Dict[str, float]
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Request schemas
class TaskSubmissionRequest(BaseModel):
    """Schema for task submission requests."""
    name: str
    description: Optional[str] = None
    priority: TaskPriorityAPI = TaskPriorityAPI.MEDIUM
    parameters: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = 300
    max_retries: int = 3
    resource_requirements: Dict[str, Any] = Field(default_factory=dict)
    tags: Set[str] = Field(default_factory=set)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    decomposition_strategy: Optional[str] = None
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Task name cannot be empty')
        return v.strip()


class AgentCreateRequest(BaseModel):
    """Schema for agent creation requests."""
    agent_type: str
    capabilities: Set[AgentCapabilityAPI]
    configuration: Dict[str, Any] = Field(default_factory=dict)
    max_concurrent_tasks: int = 1
    resource_limits: Dict[str, Any] = Field(default_factory=dict)
    tags: Set[str] = Field(default_factory=set)
    
    @validator('agent_type')
    def agent_type_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Agent type cannot be empty')
        return v.strip()
    
    @validator('capabilities')
    def capabilities_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Agent must have at least one capability')
        return v


class ResourceCreateRequest(BaseModel):
    """Schema for resource creation requests."""
    resource_type: ResourceTypeAPI
    capacity: float
    name: Optional[str] = None
    unit: Optional[str] = None
    location: str = "local"
    cost_per_unit: float = 0.0
    minimum_allocation: Optional[float] = None
    maximum_allocation: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: Set[str] = Field(default_factory=set)
    
    @validator('capacity')
    def capacity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Resource capacity must be positive')
        return v


class ResourceAllocationRequest(BaseModel):
    """Schema for resource allocation requests."""
    resource_requirements: Dict[str, float]
    priority: TaskPriorityAPI = TaskPriorityAPI.MEDIUM
    max_wait_time: int = 300
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('resource_requirements')
    def requirements_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Resource requirements cannot be empty')
        return v


# Response schemas
class TaskResponse(BaseModel):
    """Schema for task API responses."""
    task: TaskSchema
    execution_plan_id: Optional[UUID] = None
    message: Optional[str] = None


class AgentResponse(BaseModel):
    """Schema for agent API responses."""
    agent: AgentSchema
    message: Optional[str] = None


class ResourceResponse(BaseModel):
    """Schema for resource API responses."""
    resource: ResourceSchema
    message: Optional[str] = None


class AllocationResponse(BaseModel):
    """Schema for resource allocation responses."""
    request_id: UUID
    status: str
    allocated_resources: Dict[str, float] = Field(default_factory=dict)
    message: Optional[str] = None


class SystemStatusResponse(BaseModel):
    """Schema for system status responses."""
    running: bool
    uptime_seconds: float
    startup_time: Optional[datetime] = None
    components: Dict[str, str]
    active_executions: int
    execution_plans: int
    total_tasks: int
    total_agents: int
    total_resources: int
    message: Optional[str] = None


class MetricsResponse(BaseModel):
    """Schema for system metrics responses."""
    orchestrator: Dict[str, Any]
    task_planner: Dict[str, Any]
    agent_manager: Dict[str, Any]
    resource_allocator: Dict[str, Any]
    state_manager: Dict[str, Any]
    message_bus: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CheckpointSchema(BaseModel):
    """Schema for checkpoint representation."""
    id: UUID
    name: str
    type: str
    created_at: datetime
    size_bytes: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CheckpointResponse(BaseModel):
    """Schema for checkpoint API responses."""
    checkpoints: List[CheckpointSchema] = Field(default_factory=list)
    checkpoint: Optional[CheckpointSchema] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema for API error responses."""
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


# Pagination schemas
class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Base schema for paginated responses."""
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedTaskResponse(PaginatedResponse):
    """Schema for paginated task responses."""
    items: List[TaskSchema]


class PaginatedAgentResponse(PaginatedResponse):
    """Schema for paginated agent responses."""
    items: List[AgentSchema]


class PaginatedResourceResponse(PaginatedResponse):
    """Schema for paginated resource responses."""
    items: List[ResourceSchema]


# Search and filter schemas
class TaskFilterParams(BaseModel):
    """Schema for task filtering parameters."""
    status: Optional[TaskStatusAPI] = None
    priority: Optional[TaskPriorityAPI] = None
    agent_id: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    search: Optional[str] = None


class AgentFilterParams(BaseModel):
    """Schema for agent filtering parameters."""
    status: Optional[AgentStatusAPI] = None
    agent_type: Optional[str] = None
    capabilities: Optional[List[AgentCapabilityAPI]] = None
    tags: Optional[List[str]] = None
    available_only: bool = False
    search: Optional[str] = None


class ResourceFilterParams(BaseModel):
    """Schema for resource filtering parameters."""
    resource_type: Optional[ResourceTypeAPI] = None
    location: Optional[str] = None
    health_status: Optional[str] = None
    tags: Optional[List[str]] = None
    min_available_capacity: Optional[float] = None
    search: Optional[str] = None


# Bulk operation schemas
class BulkTaskOperation(BaseModel):
    """Schema for bulk task operations."""
    task_ids: List[UUID]
    operation: str  # "cancel", "retry", "delete"
    reason: Optional[str] = None
    
    @validator('task_ids')
    def task_ids_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Task IDs list cannot be empty')
        return v


class BulkOperationResponse(BaseModel):
    """Schema for bulk operation responses."""
    successful_operations: int
    failed_operations: int
    total_operations: int
    results: List[Dict[str, Any]]
    message: Optional[str] = None


# Health check schemas
class HealthCheckResponse(BaseModel):
    """Schema for health check responses."""
    status: str  # "healthy", "unhealthy", "degraded"
    components: Dict[str, str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime_seconds: float
    version: Optional[str] = None


# Configuration schemas
class ComponentConfig(BaseModel):
    """Schema for component configuration."""
    component: str
    configuration: Dict[str, Any]
    
    @validator('component')
    def component_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Component name cannot be empty')
        return v.strip()


class ConfigurationResponse(BaseModel):
    """Schema for configuration responses."""
    configurations: Dict[str, Dict[str, Any]]
    message: Optional[str] = None