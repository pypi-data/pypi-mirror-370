"""
Custom exceptions for MAOS orchestration system.
"""

from typing import Optional, Dict, Any
from uuid import UUID


class MAOSError(Exception):
    """Base exception for MAOS orchestration system."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}
    
    def __str__(self) -> str:
        base_message = super().__str__()
        if self.error_code:
            return f"[{self.error_code}] {base_message}"
        return base_message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary representation."""
        return {
            'error_type': self.__class__.__name__,
            'message': str(self),
            'error_code': self.error_code,
            'context': self.context
        }


class TaskError(MAOSError):
    """Exception related to task operations."""
    
    def __init__(
        self, 
        message: str, 
        task_id: Optional[UUID] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context)
        self.task_id = task_id
        if task_id:
            self.context['task_id'] = str(task_id)


class TaskNotFoundError(TaskError):
    """Exception raised when a task cannot be found."""
    
    def __init__(self, task_id: UUID):
        super().__init__(
            f"Task not found: {task_id}",
            task_id=task_id,
            error_code="TASK_NOT_FOUND"
        )


class TaskDependencyError(TaskError):
    """Exception related to task dependency issues."""
    
    def __init__(
        self, 
        message: str, 
        task_id: Optional[UUID] = None,
        dependency_task_id: Optional[UUID] = None
    ):
        context = {}
        if dependency_task_id:
            context['dependency_task_id'] = str(dependency_task_id)
        
        super().__init__(
            message,
            task_id=task_id,
            error_code="TASK_DEPENDENCY_ERROR",
            context=context
        )
        self.dependency_task_id = dependency_task_id


class TaskExecutionError(TaskError):
    """Exception raised during task execution."""
    
    def __init__(
        self, 
        message: str, 
        task_id: Optional[UUID] = None,
        agent_id: Optional[UUID] = None,
        original_error: Optional[Exception] = None
    ):
        context = {}
        if agent_id:
            context['agent_id'] = str(agent_id)
        if original_error:
            context['original_error'] = str(original_error)
            context['original_error_type'] = type(original_error).__name__
        
        super().__init__(
            message,
            task_id=task_id,
            error_code="TASK_EXECUTION_ERROR",
            context=context
        )
        self.agent_id = agent_id
        self.original_error = original_error


class AgentError(MAOSError):
    """Exception related to agent operations."""
    
    def __init__(
        self, 
        message: str, 
        agent_id: Optional[UUID] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context)
        self.agent_id = agent_id
        if agent_id:
            self.context['agent_id'] = str(agent_id)


class AgentNotFoundError(AgentError):
    """Exception raised when an agent cannot be found."""
    
    def __init__(self, agent_id: UUID):
        super().__init__(
            f"Agent not found: {agent_id}",
            agent_id=agent_id,
            error_code="AGENT_NOT_FOUND"
        )


class AgentNotAvailableError(AgentError):
    """Exception raised when an agent is not available for task assignment."""
    
    def __init__(self, agent_id: UUID, reason: str = "Agent not available"):
        super().__init__(
            f"Agent not available: {agent_id} - {reason}",
            agent_id=agent_id,
            error_code="AGENT_NOT_AVAILABLE",
            context={'reason': reason}
        )


class AgentCapabilityError(AgentError):
    """Exception related to agent capability mismatches."""
    
    def __init__(
        self, 
        message: str, 
        agent_id: Optional[UUID] = None,
        required_capabilities: Optional[list] = None,
        available_capabilities: Optional[list] = None
    ):
        context = {}
        if required_capabilities:
            context['required_capabilities'] = required_capabilities
        if available_capabilities:
            context['available_capabilities'] = available_capabilities
        
        super().__init__(
            message,
            agent_id=agent_id,
            error_code="AGENT_CAPABILITY_ERROR",
            context=context
        )


class AgentHealthError(AgentError):
    """Exception related to agent health issues."""
    
    def __init__(
        self, 
        message: str, 
        agent_id: Optional[UUID] = None,
        health_score: Optional[float] = None,
        status: Optional[str] = None
    ):
        context = {}
        if health_score is not None:
            context['health_score'] = health_score
        if status:
            context['status'] = status
        
        super().__init__(
            message,
            agent_id=agent_id,
            error_code="AGENT_HEALTH_ERROR",
            context=context
        )


class ResourceError(MAOSError):
    """Exception related to resource operations."""
    
    def __init__(
        self, 
        message: str, 
        resource_id: Optional[UUID] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context)
        self.resource_id = resource_id
        if resource_id:
            self.context['resource_id'] = str(resource_id)


class ResourceNotFoundError(ResourceError):
    """Exception raised when a resource cannot be found."""
    
    def __init__(self, resource_id: UUID):
        super().__init__(
            f"Resource not found: {resource_id}",
            resource_id=resource_id,
            error_code="RESOURCE_NOT_FOUND"
        )


class ResourceAllocationError(ResourceError):
    """Exception related to resource allocation issues."""
    
    def __init__(
        self, 
        message: str, 
        resource_id: Optional[UUID] = None,
        requested_amount: Optional[float] = None,
        available_amount: Optional[float] = None,
        agent_id: Optional[UUID] = None
    ):
        context = {}
        if requested_amount is not None:
            context['requested_amount'] = requested_amount
        if available_amount is not None:
            context['available_amount'] = available_amount
        if agent_id:
            context['agent_id'] = str(agent_id)
        
        super().__init__(
            message,
            resource_id=resource_id,
            error_code="RESOURCE_ALLOCATION_ERROR",
            context=context
        )


class ResourceExhaustionError(ResourceError):
    """Exception raised when resources are exhausted."""
    
    def __init__(
        self, 
        resource_type: str,
        requested_amount: float,
        available_amount: float
    ):
        super().__init__(
            f"Resource exhausted: {resource_type} - requested {requested_amount}, available {available_amount}",
            error_code="RESOURCE_EXHAUSTED",
            context={
                'resource_type': resource_type,
                'requested_amount': requested_amount,
                'available_amount': available_amount
            }
        )


class OrchestrationError(MAOSError):
    """Exception related to orchestration operations."""
    
    def __init__(
        self, 
        message: str, 
        operation: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context)
        self.operation = operation
        if operation:
            self.context['operation'] = operation


class DAGError(OrchestrationError):
    """Exception related to DAG operations."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            operation="dag_operation",
            error_code="DAG_ERROR",
            context=context
        )


class CircularDependencyError(DAGError):
    """Exception raised when circular dependencies are detected."""
    
    def __init__(self, cycle_path: list):
        super().__init__(
            f"Circular dependency detected: {' -> '.join(str(task_id) for task_id in cycle_path)}",
            context={'cycle_path': [str(task_id) for task_id in cycle_path]}
        )


class ConfigurationError(MAOSError):
    """Exception related to configuration issues."""
    
    def __init__(
        self, 
        message: str, 
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None
    ):
        context = {}
        if config_key:
            context['config_key'] = config_key
        if config_value is not None:
            context['config_value'] = config_value
        
        super().__init__(
            message,
            error_code="CONFIGURATION_ERROR",
            context=context
        )


class ValidationError(MAOSError):
    """Exception related to data validation issues."""
    
    def __init__(
        self, 
        message: str, 
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        validation_rule: Optional[str] = None
    ):
        context = {}
        if field_name:
            context['field_name'] = field_name
        if field_value is not None:
            context['field_value'] = field_value
        if validation_rule:
            context['validation_rule'] = validation_rule
        
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            context=context
        )