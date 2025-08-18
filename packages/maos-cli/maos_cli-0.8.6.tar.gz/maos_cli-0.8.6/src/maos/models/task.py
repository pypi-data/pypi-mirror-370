"""
Task data model and related enums for MAOS orchestration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Any
from uuid import UUID, uuid4


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TaskDependency:
    """Represents a task dependency relationship."""
    task_id: UUID
    dependency_type: str = "completion"  # completion, data, resource
    required: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """
    Core Task model representing a unit of work in the orchestration system.
    
    Attributes:
        id: Unique task identifier
        name: Human-readable task name
        description: Detailed task description
        status: Current execution status
        priority: Task priority level
        agent_id: ID of agent assigned to this task
        parent_task_id: ID of parent task (for subtasks)
        dependencies: List of task dependencies
        subtasks: List of subtask IDs
        parameters: Task-specific parameters
        result: Task execution result
        error: Error information if task failed
        created_at: Task creation timestamp
        started_at: Task execution start timestamp
        completed_at: Task completion timestamp
        updated_at: Last update timestamp
        timeout_seconds: Maximum execution time
        retry_count: Number of retry attempts
        max_retries: Maximum number of retries allowed
        resource_requirements: Required resources for execution
        tags: Task classification tags
        metadata: Additional task metadata
    """
    
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    agent_id: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None
    dependencies: List[TaskDependency] = field(default_factory=list)
    subtasks: List[UUID] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime = field(default_factory=datetime.utcnow)
    timeout_seconds: int = 300  # 5 minutes default
    retry_count: int = 0
    max_retries: int = 3
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation."""
        if not self.name:
            self.name = f"Task-{str(self.id)[:8]}"
        self.updated_at = datetime.utcnow()
    
    def is_ready(self) -> bool:
        """Check if task is ready for execution."""
        return (
            self.status == TaskStatus.PENDING and
            all(dep.task_id for dep in self.dependencies if dep.required)
        )
    
    def is_terminal(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in {
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED
        }
    
    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return (
            self.status == TaskStatus.FAILED and
            self.retry_count < self.max_retries
        )
    
    def update_status(self, status: TaskStatus) -> None:
        """Update task status with timestamp tracking."""
        old_status = self.status
        self.status = status
        self.updated_at = datetime.utcnow()
        
        if status == TaskStatus.RUNNING and old_status != TaskStatus.RUNNING:
            self.started_at = self.updated_at
        elif status in {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}:
            self.completed_at = self.updated_at
    
    def add_dependency(self, task_id: UUID, dependency_type: str = "completion", 
                      required: bool = True, **metadata) -> None:
        """Add a task dependency."""
        dependency = TaskDependency(
            task_id=task_id,
            dependency_type=dependency_type,
            required=required,
            metadata=metadata
        )
        self.dependencies.append(dependency)
        self.updated_at = datetime.utcnow()
    
    def remove_dependency(self, task_id: UUID) -> bool:
        """Remove a task dependency."""
        original_count = len(self.dependencies)
        self.dependencies = [dep for dep in self.dependencies if dep.task_id != task_id]
        self.updated_at = datetime.utcnow()
        return len(self.dependencies) < original_count
    
    def add_subtask(self, task_id: UUID) -> None:
        """Add a subtask ID."""
        if task_id not in self.subtasks:
            self.subtasks.append(task_id)
            self.updated_at = datetime.utcnow()
    
    def estimate_duration(self) -> int:
        """Estimate task duration in seconds based on historical data."""
        # Placeholder implementation - in production, this would use ML models
        # or historical execution data
        base_duration = self.timeout_seconds // 2
        
        # Adjust based on priority
        if self.priority == TaskPriority.CRITICAL:
            return int(base_duration * 0.8)
        elif self.priority == TaskPriority.LOW:
            return int(base_duration * 1.2)
        
        return base_duration
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.value,
            'agent_id': str(self.agent_id) if self.agent_id else None,
            'parent_task_id': str(self.parent_task_id) if self.parent_task_id else None,
            'dependencies': [
                {
                    'task_id': str(dep.task_id),
                    'dependency_type': dep.dependency_type,
                    'required': dep.required,
                    'metadata': dep.metadata
                } for dep in self.dependencies
            ],
            'subtasks': [str(task_id) for task_id in self.subtasks],
            'parameters': self.parameters,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat(),
            'timeout_seconds': self.timeout_seconds,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'resource_requirements': self.resource_requirements,
            'tags': list(self.tags),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary representation."""
        # Convert string UUIDs back to UUID objects
        if 'id' in data:
            data['id'] = UUID(data['id'])
        if 'agent_id' in data and data['agent_id']:
            data['agent_id'] = UUID(data['agent_id'])
        if 'parent_task_id' in data and data['parent_task_id']:
            data['parent_task_id'] = UUID(data['parent_task_id'])
        
        # Convert status and priority enums
        if 'status' in data:
            data['status'] = TaskStatus(data['status'])
        if 'priority' in data:
            data['priority'] = TaskPriority(data['priority'])
        
        # Convert datetime strings
        for field_name in ['created_at', 'started_at', 'completed_at', 'updated_at']:
            if field_name in data and data[field_name]:
                data[field_name] = datetime.fromisoformat(data[field_name])
        
        # Convert dependencies
        if 'dependencies' in data:
            dependencies = []
            for dep_data in data['dependencies']:
                dependencies.append(TaskDependency(
                    task_id=UUID(dep_data['task_id']),
                    dependency_type=dep_data['dependency_type'],
                    required=dep_data['required'],
                    metadata=dep_data['metadata']
                ))
            data['dependencies'] = dependencies
        
        # Convert subtasks
        if 'subtasks' in data:
            data['subtasks'] = [UUID(task_id) for task_id in data['subtasks']]
        
        # Convert tags to set
        if 'tags' in data:
            data['tags'] = set(data['tags'])
        
        return cls(**data)