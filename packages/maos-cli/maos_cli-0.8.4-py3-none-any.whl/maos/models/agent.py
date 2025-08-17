"""
Agent data model and related enums for MAOS orchestration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Any
from uuid import UUID, uuid4


class AgentStatus(Enum):
    """Agent operational status."""
    INITIALIZING = "initializing"
    IDLE = "idle"
    BUSY = "busy"
    OVERLOADED = "overloaded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    TERMINATED = "terminated"


class AgentType(Enum):
    """Agent type classifications."""
    DEVELOPER = "developer"
    TESTER = "tester"
    REVIEWER = "reviewer"
    ARCHITECT = "architect"
    ANALYST = "analyst"
    COORDINATOR = "coordinator"
    MONITOR = "monitor"
    GENERAL = "general"


class AgentCapability(Enum):
    """Agent capability types."""
    TASK_EXECUTION = "task_execution"
    DATA_PROCESSING = "data_processing"
    API_INTEGRATION = "api_integration"
    FILE_OPERATIONS = "file_operations"
    COMPUTATION = "computation"
    COMMUNICATION = "communication"
    MONITORING = "monitoring"
    COORDINATION = "coordination"
    ANALYSIS = "analysis"
    DEPLOYMENT = "deployment"


@dataclass
class AgentMetrics:
    """Agent performance metrics."""
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    success_rate: float = 1.0
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    health_score: float = 1.0
    
    def update_success_rate(self) -> None:
        """Update success rate based on completed and failed tasks."""
        total_tasks = self.tasks_completed + self.tasks_failed
        if total_tasks > 0:
            self.success_rate = self.tasks_completed / total_tasks
    
    def update_average_execution_time(self) -> None:
        """Update average execution time."""
        if self.tasks_completed > 0:
            self.average_execution_time = self.total_execution_time / self.tasks_completed


@dataclass
class Agent:
    """
    Core Agent model representing an autonomous agent in the orchestration system.
    
    Attributes:
        id: Unique agent identifier
        name: Human-readable agent name
        type: Agent type/classification
        status: Current operational status
        capabilities: Set of agent capabilities
        current_task_id: ID of currently executing task
        task_queue: Queue of assigned task IDs
        max_concurrent_tasks: Maximum tasks the agent can handle
        resource_limits: Resource consumption limits
        configuration: Agent-specific configuration
        metadata: Additional agent metadata
        created_at: Agent creation timestamp
        started_at: Agent start timestamp
        last_seen: Last activity timestamp
        metrics: Performance metrics
        tags: Agent classification tags
        health_check_interval: Health check frequency in seconds
        heartbeat_timeout: Maximum time without heartbeat before marking unhealthy
    """
    
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    type: str = "generic"
    status: AgentStatus = AgentStatus.INITIALIZING
    capabilities: Set[AgentCapability] = field(default_factory=set)
    current_task_id: Optional[UUID] = None
    task_queue: List[UUID] = field(default_factory=list)
    max_concurrent_tasks: int = 1
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    last_seen: datetime = field(default_factory=datetime.utcnow)
    metrics: AgentMetrics = field(default_factory=AgentMetrics)
    tags: Set[str] = field(default_factory=set)
    health_check_interval: int = 30  # seconds
    heartbeat_timeout: int = 90  # seconds
    
    def __post_init__(self):
        """Post-initialization setup."""
        if not self.name:
            self.name = f"Agent-{str(self.id)[:8]}"
        
        # Set default resource limits
        if not self.resource_limits:
            self.resource_limits = {
                'cpu_percent': 80.0,
                'memory_mb': 1024,
                'disk_mb': 5120
            }
    
    def is_available(self) -> bool:
        """Check if agent is available for new tasks."""
        return (
            self.status in {AgentStatus.IDLE, AgentStatus.BUSY} and
            len(self.task_queue) < self.max_concurrent_tasks and
            self.is_healthy()
        )
    
    def is_healthy(self) -> bool:
        """Check if agent is healthy based on heartbeat and metrics."""
        now = datetime.utcnow()
        heartbeat_age = (now - self.metrics.last_heartbeat).total_seconds()
        
        return (
            self.status not in {AgentStatus.UNHEALTHY, AgentStatus.OFFLINE, AgentStatus.TERMINATED} and
            heartbeat_age < self.heartbeat_timeout and
            self.metrics.health_score > 0.5
        )
    
    def can_handle_task(self, required_capabilities: Set[AgentCapability]) -> bool:
        """Check if agent can handle a task with specific capability requirements."""
        return (
            self.is_available() and
            required_capabilities.issubset(self.capabilities)
        )
    
    def assign_task(self, task_id: UUID) -> bool:
        """Assign a task to the agent."""
        if not self.is_available():
            return False
        
        if len(self.task_queue) == 0 and self.current_task_id is None:
            self.current_task_id = task_id
            self.status = AgentStatus.BUSY
        else:
            self.task_queue.append(task_id)
        
        self.last_seen = datetime.utcnow()
        return True
    
    def complete_task(self, task_id: UUID, execution_time: float, success: bool) -> None:
        """Mark a task as completed and update metrics."""
        if self.current_task_id == task_id:
            self.current_task_id = None
            
            # Move next task from queue if available
            if self.task_queue:
                self.current_task_id = self.task_queue.pop(0)
            else:
                self.status = AgentStatus.IDLE
        else:
            # Remove from queue if present
            if task_id in self.task_queue:
                self.task_queue.remove(task_id)
        
        # Update metrics
        if success:
            self.metrics.tasks_completed += 1
        else:
            self.metrics.tasks_failed += 1
        
        self.metrics.total_execution_time += execution_time
        self.metrics.update_success_rate()
        self.metrics.update_average_execution_time()
        self.last_seen = datetime.utcnow()
    
    def update_heartbeat(self, cpu_usage: float = 0.0, memory_usage: float = 0.0) -> None:
        """Update agent heartbeat with system metrics."""
        self.metrics.last_heartbeat = datetime.utcnow()
        self.metrics.cpu_usage_percent = cpu_usage
        self.metrics.memory_usage_mb = memory_usage
        self.last_seen = self.metrics.last_heartbeat
        
        # Calculate health score based on various factors
        health_factors = []
        
        # Resource usage health
        cpu_health = max(0, 1 - (cpu_usage / 100))
        memory_health = max(0, 1 - (memory_usage / self.resource_limits.get('memory_mb', 1024)))
        health_factors.extend([cpu_health, memory_health])
        
        # Success rate health
        health_factors.append(self.metrics.success_rate)
        
        # Calculate overall health score
        self.metrics.health_score = sum(health_factors) / len(health_factors)
        
        # Update status based on health and load
        if self.metrics.health_score < 0.3:
            self.status = AgentStatus.UNHEALTHY
        elif cpu_usage > 95 or len(self.task_queue) >= self.max_concurrent_tasks:
            self.status = AgentStatus.OVERLOADED
        elif self.current_task_id is not None:
            self.status = AgentStatus.BUSY
        else:
            self.status = AgentStatus.IDLE
    
    def add_capability(self, capability: AgentCapability) -> None:
        """Add a capability to the agent."""
        self.capabilities.add(capability)
    
    def remove_capability(self, capability: AgentCapability) -> None:
        """Remove a capability from the agent."""
        self.capabilities.discard(capability)
    
    def get_load_factor(self) -> float:
        """Calculate current load factor (0.0 to 1.0+)."""
        current_tasks = (1 if self.current_task_id else 0) + len(self.task_queue)
        return current_tasks / self.max_concurrent_tasks if self.max_concurrent_tasks > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            'id': str(self.id),
            'name': self.name,
            'type': self.type,
            'status': self.status.value,
            'capabilities': [cap.value for cap in self.capabilities],
            'current_task_id': str(self.current_task_id) if self.current_task_id else None,
            'task_queue': [str(task_id) for task_id in self.task_queue],
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'resource_limits': self.resource_limits,
            'configuration': self.configuration,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'last_seen': self.last_seen.isoformat(),
            'metrics': {
                'tasks_completed': self.metrics.tasks_completed,
                'tasks_failed': self.metrics.tasks_failed,
                'total_execution_time': self.metrics.total_execution_time,
                'average_execution_time': self.metrics.average_execution_time,
                'cpu_usage_percent': self.metrics.cpu_usage_percent,
                'memory_usage_mb': self.metrics.memory_usage_mb,
                'success_rate': self.metrics.success_rate,
                'last_heartbeat': self.metrics.last_heartbeat.isoformat(),
                'health_score': self.metrics.health_score
            },
            'tags': list(self.tags),
            'health_check_interval': self.health_check_interval,
            'heartbeat_timeout': self.heartbeat_timeout
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Create agent from dictionary representation."""
        # Convert string UUIDs back to UUID objects
        if 'id' in data:
            data['id'] = UUID(data['id'])
        if 'current_task_id' in data and data['current_task_id']:
            data['current_task_id'] = UUID(data['current_task_id'])
        if 'task_queue' in data:
            data['task_queue'] = [UUID(task_id) for task_id in data['task_queue']]
        
        # Convert status enum
        if 'status' in data:
            data['status'] = AgentStatus(data['status'])
        
        # Convert capabilities
        if 'capabilities' in data:
            data['capabilities'] = {AgentCapability(cap) for cap in data['capabilities']}
        
        # Convert datetime strings
        for field_name in ['created_at', 'started_at', 'last_seen']:
            if field_name in data and data[field_name]:
                data[field_name] = datetime.fromisoformat(data[field_name])
        
        # Convert metrics
        if 'metrics' in data:
            metrics_data = data['metrics']
            metrics_data['last_heartbeat'] = datetime.fromisoformat(metrics_data['last_heartbeat'])
            data['metrics'] = AgentMetrics(**metrics_data)
        
        # Convert tags to set
        if 'tags' in data:
            data['tags'] = set(data['tags'])
        
        return cls(**data)