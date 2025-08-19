"""
Main orchestrator interface for MAOS orchestration system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Set
from uuid import UUID

from ..models.task import Task, TaskStatus, TaskPriority
from ..models.agent import Agent, AgentCapability
from ..models.resource import Resource, ResourceType
from ..core.task_planner import ExecutionPlan


class OrchestratorInterface(ABC):
    """
    Abstract interface for the main orchestrator component.
    
    This interface defines the contract for the MAOS orchestrator,
    which coordinates between all other components.
    """
    
    @abstractmethod
    async def start(self) -> None:
        """Start the orchestrator and all sub-components."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Gracefully shutdown the orchestrator."""
        pass
    
    # Task Management
    @abstractmethod
    async def submit_task(
        self,
        task: Task,
        decomposition_strategy: Optional[str] = None
    ) -> ExecutionPlan:
        """Submit a task for execution."""
        pass
    
    @abstractmethod
    async def get_task(self, task_id: UUID) -> Optional[Task]:
        """Get a task by ID."""
        pass
    
    @abstractmethod
    async def get_task_status(self, task_id: UUID) -> Optional[TaskStatus]:
        """Get the status of a task."""
        pass
    
    @abstractmethod
    async def cancel_task(self, task_id: UUID, reason: str = "Cancelled") -> bool:
        """Cancel a task."""
        pass
    
    @abstractmethod
    async def retry_task(self, task_id: UUID) -> bool:
        """Retry a failed task."""
        pass
    
    @abstractmethod
    async def get_task_results(self, task_id: UUID) -> Optional[Any]:
        """Get the results of a completed task."""
        pass
    
    # Agent Management
    @abstractmethod
    async def create_agent(
        self,
        agent_type: str,
        capabilities: Set[AgentCapability],
        configuration: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """Create a new agent."""
        pass
    
    @abstractmethod
    async def get_agent(self, agent_id: UUID) -> Optional[Agent]:
        """Get an agent by ID."""
        pass
    
    @abstractmethod
    async def get_available_agents(
        self,
        required_capabilities: Optional[Set[AgentCapability]] = None
    ) -> List[Agent]:
        """Get list of available agents."""
        pass
    
    @abstractmethod
    async def terminate_agent(
        self,
        agent_id: UUID,
        reason: str = "Manual termination"
    ) -> bool:
        """Terminate an agent."""
        pass
    
    # Resource Management
    @abstractmethod
    async def create_resource(
        self,
        resource_type: ResourceType,
        capacity: float,
        configuration: Optional[Dict[str, Any]] = None
    ) -> Resource:
        """Create a new resource."""
        pass
    
    @abstractmethod
    async def get_resource(self, resource_id: UUID) -> Optional[Resource]:
        """Get a resource by ID."""
        pass
    
    @abstractmethod
    async def request_resources(
        self,
        requester_id: UUID,
        resource_requirements: Dict[str, float],
        priority: TaskPriority = TaskPriority.MEDIUM
    ) -> UUID:
        """Request resource allocation."""
        pass
    
    @abstractmethod
    async def release_resources(
        self,
        requester_id: UUID,
        resource_id: Optional[UUID] = None
    ) -> float:
        """Release allocated resources."""
        pass
    
    # Execution Plans
    @abstractmethod
    async def get_execution_plan(self, plan_id: UUID) -> Optional[ExecutionPlan]:
        """Get an execution plan by ID."""
        pass
    
    @abstractmethod
    async def execute_plan(self, plan_id: UUID) -> bool:
        """Execute a planned workflow."""
        pass
    
    # System Status and Metrics
    @abstractmethod
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        pass
    
    @abstractmethod
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        pass
    
    @abstractmethod
    async def get_component_health(self) -> Dict[str, str]:
        """Get health status of all components."""
        pass
    
    # State Management
    @abstractmethod
    async def create_checkpoint(self, name: Optional[str] = None) -> UUID:
        """Create a system checkpoint."""
        pass
    
    @abstractmethod
    async def restore_checkpoint(self, checkpoint_id: UUID) -> bool:
        """Restore system state from checkpoint."""
        pass
    
    @abstractmethod
    async def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List available checkpoints."""
        pass