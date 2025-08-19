"""
Claude Code Task API integration for MAOS orchestration system.

This module provides integration with the Claude Code Task API,
allowing MAOS to be used as a backend for Claude Code task orchestration.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Callable, Union
from uuid import UUID, uuid4
from datetime import datetime

from ..core.orchestrator import Orchestrator
from ..models.task import Task, TaskStatus, TaskPriority
from ..models.agent import AgentCapability
from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError, TaskError, OrchestrationError


class ClaudeTaskIntegration:
    """
    Integration layer between Claude Code Task API and MAOS orchestration system.
    
    This class provides a bridge that allows Claude Code to use MAOS as a backend
    for distributed task execution and orchestration.
    """
    
    def __init__(
        self,
        orchestrator: Orchestrator,
        task_mapping_config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the Claude Code integration."""
        self.orchestrator = orchestrator
        self.task_mapping_config = task_mapping_config or {}
        self.logger = MAOSLogger("claude_integration", str(uuid4()))
        
        # Task type to MAOS capability mapping
        self._task_capability_map = {
            'file_operations': {AgentCapability.FILE_OPERATIONS},
            'data_processing': {AgentCapability.DATA_PROCESSING},
            'api_calls': {AgentCapability.API_INTEGRATION},
            'computation': {AgentCapability.COMPUTATION},
            'coordination': {AgentCapability.COORDINATION},
            'monitoring': {AgentCapability.MONITORING},
            'generic': {AgentCapability.TASK_EXECUTION},
        }
        
        # Priority mapping
        self._priority_map = {
            'low': TaskPriority.LOW,
            'normal': TaskPriority.MEDIUM,
            'medium': TaskPriority.MEDIUM,
            'high': TaskPriority.HIGH,
            'critical': TaskPriority.CRITICAL,
            'urgent': TaskPriority.CRITICAL
        }
        
        # Task status mapping (MAOS -> Claude Code)
        self._status_map = {
            TaskStatus.PENDING: 'pending',
            TaskStatus.READY: 'ready',
            TaskStatus.RUNNING: 'running',
            TaskStatus.COMPLETED: 'completed',
            TaskStatus.FAILED: 'failed',
            TaskStatus.CANCELLED: 'cancelled',
            TaskStatus.RETRYING: 'retrying'
        }
        
        # Active task tracking
        self._claude_task_mapping: Dict[str, UUID] = {}  # claude_task_id -> maos_task_id
        self._maos_task_mapping: Dict[UUID, str] = {}    # maos_task_id -> claude_task_id
        self._task_callbacks: Dict[str, Callable] = {}   # claude_task_id -> callback
        
        # Setup orchestrator event handlers
        self._setup_event_handlers()
    
    def _setup_event_handlers(self) -> None:
        """Setup event handlers for orchestrator state changes."""
        
        async def on_task_state_changed(category: str, action: str, new_obj: Any, old_obj: Any):
            """Handle task state changes and notify Claude Code."""
            if action == 'updated' and new_obj and hasattr(new_obj, 'status'):
                maos_task_id = new_obj.id
                if maos_task_id in self._maos_task_mapping:
                    claude_task_id = self._maos_task_mapping[maos_task_id]
                    await self._notify_claude_task_update(claude_task_id, new_obj)
        
        # Register the event handler
        self.orchestrator.state_manager.add_change_listener('tasks', on_task_state_changed)
    
    async def submit_task(
        self,
        task_spec: Dict[str, Any],
        callback: Optional[Callable] = None
    ) -> str:
        """
        Submit a task from Claude Code to MAOS orchestration.
        
        Args:
            task_spec: Claude Code task specification
            callback: Optional callback function for task updates
            
        Returns:
            str: Claude Code task ID
        """
        
        try:
            # Generate Claude Code task ID
            claude_task_id = str(uuid4())
            
            # Convert Claude Code task spec to MAOS task
            maos_task = await self._convert_claude_task_to_maos(task_spec)
            
            # Submit to MAOS orchestrator
            execution_plan = await self.orchestrator.submit_task(
                task=maos_task,
                decomposition_strategy=task_spec.get('decomposition_strategy', 'hierarchical')
            )
            
            # Store mapping and callback
            self._claude_task_mapping[claude_task_id] = maos_task.id
            self._maos_task_mapping[maos_task.id] = claude_task_id
            
            if callback:
                self._task_callbacks[claude_task_id] = callback
            
            self.logger.logger.info(
                f"Claude task submitted to MAOS",
                extra={
                    'claude_task_id': claude_task_id,
                    'maos_task_id': str(maos_task.id),
                    'execution_plan_id': str(execution_plan.id)
                }
            )
            
            # Notify callback of submission
            if callback:
                await self._invoke_callback(callback, {
                    'task_id': claude_task_id,
                    'status': 'submitted',
                    'message': 'Task submitted to MAOS orchestrator',
                    'execution_plan_id': str(execution_plan.id)
                })
            
            return claude_task_id
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'submit_task',
                'task_spec': task_spec
            })
            raise TaskError(f"Failed to submit Claude task to MAOS: {str(e)}")
    
    async def get_task_status(self, claude_task_id: str) -> Dict[str, Any]:
        """
        Get task status for a Claude Code task.
        
        Args:
            claude_task_id: Claude Code task ID
            
        Returns:
            Dict containing task status information
        """
        
        if claude_task_id not in self._claude_task_mapping:
            raise TaskError(f"Claude task not found: {claude_task_id}")
        
        maos_task_id = self._claude_task_mapping[claude_task_id]
        
        try:
            # Get task from MAOS
            maos_task = await self.orchestrator.get_task(maos_task_id)
            if not maos_task:
                raise TaskError(f"MAOS task not found: {maos_task_id}")
            
            # Convert to Claude Code format
            return await self._convert_maos_task_to_claude(maos_task, claude_task_id)
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'get_task_status',
                'claude_task_id': claude_task_id,
                'maos_task_id': str(maos_task_id)
            })
            raise
    
    async def cancel_task(self, claude_task_id: str, reason: str = "Cancelled by Claude Code") -> bool:
        """
        Cancel a Claude Code task.
        
        Args:
            claude_task_id: Claude Code task ID
            reason: Cancellation reason
            
        Returns:
            bool: True if successfully cancelled
        """
        
        if claude_task_id not in self._claude_task_mapping:
            raise TaskError(f"Claude task not found: {claude_task_id}")
        
        maos_task_id = self._claude_task_mapping[claude_task_id]
        
        try:
            success = await self.orchestrator.cancel_task(maos_task_id, reason)
            
            if success:
                self.logger.logger.info(
                    f"Claude task cancelled",
                    extra={
                        'claude_task_id': claude_task_id,
                        'maos_task_id': str(maos_task_id),
                        'reason': reason
                    }
                )
                
                # Notify callback if present
                if claude_task_id in self._task_callbacks:
                    callback = self._task_callbacks[claude_task_id]
                    await self._invoke_callback(callback, {
                        'task_id': claude_task_id,
                        'status': 'cancelled',
                        'message': f'Task cancelled: {reason}'
                    })
            
            return success
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'cancel_task',
                'claude_task_id': claude_task_id
            })
            raise
    
    async def get_task_results(self, claude_task_id: str) -> Optional[Any]:
        """
        Get results for a completed Claude Code task.
        
        Args:
            claude_task_id: Claude Code task ID
            
        Returns:
            Task results or None if not available
        """
        
        if claude_task_id not in self._claude_task_mapping:
            raise TaskError(f"Claude task not found: {claude_task_id}")
        
        maos_task_id = self._claude_task_mapping[claude_task_id]
        
        try:
            results = await self.orchestrator.get_task_results(maos_task_id)
            
            if results is not None:
                # Convert MAOS results to Claude Code format
                return await self._convert_maos_results_to_claude(results)
            
            return None
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'get_task_results',
                'claude_task_id': claude_task_id
            })
            raise
    
    async def list_active_tasks(self) -> List[Dict[str, Any]]:
        """
        List all active Claude Code tasks.
        
        Returns:
            List of active task information
        """
        
        try:
            active_tasks = []
            
            for claude_task_id, maos_task_id in self._claude_task_mapping.items():
                try:
                    maos_task = await self.orchestrator.get_task(maos_task_id)
                    if maos_task and not maos_task.is_terminal():
                        claude_task = await self._convert_maos_task_to_claude(maos_task, claude_task_id)
                        active_tasks.append(claude_task)
                except Exception:
                    # Skip tasks that can't be retrieved
                    continue
            
            return active_tasks
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'list_active_tasks'})
            raise
    
    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """
        Get MAOS orchestrator status for Claude Code.
        
        Returns:
            Dict containing orchestrator status
        """
        
        try:
            status = await self.orchestrator.get_system_status()
            metrics = await self.orchestrator.get_system_metrics()
            health = await self.orchestrator.get_component_health()
            
            return {
                'status': 'running' if status['running'] else 'stopped',
                'uptime_seconds': status['uptime_seconds'],
                'components': status['components'],
                'active_executions': status['active_executions'],
                'total_claude_tasks': len(self._claude_task_mapping),
                'health': health,
                'metrics': {
                    'tasks_submitted': metrics['orchestrator'].get('tasks_submitted', 0),
                    'tasks_completed': metrics['orchestrator'].get('tasks_completed', 0),
                    'tasks_failed': metrics['orchestrator'].get('tasks_failed', 0),
                    'agents_created': metrics['orchestrator'].get('agents_created', 0),
                }
            }
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'get_orchestrator_status'})
            raise
    
    # Conversion methods
    async def _convert_claude_task_to_maos(self, task_spec: Dict[str, Any]) -> Task:
        """Convert Claude Code task specification to MAOS task."""
        
        # Extract basic task information
        name = task_spec.get('name', 'Claude Code Task')
        description = task_spec.get('description', '')
        
        # Map priority
        priority_str = task_spec.get('priority', 'normal').lower()
        priority = self._priority_map.get(priority_str, TaskPriority.MEDIUM)
        
        # Extract parameters
        parameters = task_spec.get('parameters', {})
        
        # Add Claude-specific metadata
        metadata = task_spec.get('metadata', {})
        metadata.update({
            'source': 'claude_code',
            'original_spec': task_spec,
            'created_by': 'claude_integration'
        })
        
        # Determine resource requirements
        resource_requirements = task_spec.get('resource_requirements', {})
        if not resource_requirements:
            # Provide defaults based on task type
            task_type = task_spec.get('type', 'generic')
            resource_requirements = self._get_default_resources_for_task_type(task_type)
        
        # Extract timeout and retry settings
        timeout_seconds = task_spec.get('timeout_seconds', 300)
        max_retries = task_spec.get('max_retries', 3)
        
        # Extract tags
        tags = set(task_spec.get('tags', []))
        tags.add('claude_code')
        
        # Create MAOS task
        task = Task(
            name=name,
            description=description,
            priority=priority,
            parameters=parameters,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            resource_requirements=resource_requirements,
            tags=tags,
            metadata=metadata
        )
        
        return task
    
    async def _convert_maos_task_to_claude(self, maos_task: Task, claude_task_id: str) -> Dict[str, Any]:
        """Convert MAOS task to Claude Code format."""
        
        return {
            'id': claude_task_id,
            'name': maos_task.name,
            'description': maos_task.description,
            'status': self._status_map.get(maos_task.status, 'unknown'),
            'priority': maos_task.priority.name.lower(),
            'created_at': maos_task.created_at.isoformat(),
            'started_at': maos_task.started_at.isoformat() if maos_task.started_at else None,
            'completed_at': maos_task.completed_at.isoformat() if maos_task.completed_at else None,
            'updated_at': maos_task.updated_at.isoformat(),
            'timeout_seconds': maos_task.timeout_seconds,
            'retry_count': maos_task.retry_count,
            'max_retries': maos_task.max_retries,
            'parameters': maos_task.parameters,
            'result': maos_task.result,
            'error': maos_task.error,
            'tags': list(maos_task.tags),
            'metadata': maos_task.metadata,
            'maos_task_id': str(maos_task.id),
            'agent_id': str(maos_task.agent_id) if maos_task.agent_id else None,
            'parent_task_id': str(maos_task.parent_task_id) if maos_task.parent_task_id else None,
            'subtasks': [str(tid) for tid in maos_task.subtasks],
            'resource_requirements': maos_task.resource_requirements
        }
    
    async def _convert_maos_results_to_claude(self, results: Any) -> Any:
        """Convert MAOS task results to Claude Code format."""
        
        # If results is a dictionary, check for MAOS-specific fields to convert
        if isinstance(results, dict):
            claude_results = {}
            
            for key, value in results.items():
                # Convert UUID fields to strings
                if isinstance(value, UUID):
                    claude_results[key] = str(value)
                # Convert datetime fields to ISO format
                elif isinstance(value, datetime):
                    claude_results[key] = value.isoformat()
                else:
                    claude_results[key] = value
            
            return claude_results
        
        # For other types, return as-is
        return results
    
    def _get_default_resources_for_task_type(self, task_type: str) -> Dict[str, float]:
        """Get default resource requirements for a task type."""
        
        defaults = {
            'file_operations': {'cpu_cores': 0.5, 'memory_mb': 256, 'disk_mb': 1024},
            'data_processing': {'cpu_cores': 1.0, 'memory_mb': 1024, 'disk_mb': 512},
            'api_calls': {'cpu_cores': 0.25, 'memory_mb': 128, 'network_mbps': 10},
            'computation': {'cpu_cores': 2.0, 'memory_mb': 2048, 'disk_mb': 256},
            'coordination': {'cpu_cores': 0.5, 'memory_mb': 512},
            'monitoring': {'cpu_cores': 0.25, 'memory_mb': 256},
            'generic': {'cpu_cores': 0.5, 'memory_mb': 512, 'disk_mb': 256}
        }
        
        return defaults.get(task_type, defaults['generic'])
    
    async def _notify_claude_task_update(self, claude_task_id: str, maos_task: Task) -> None:
        """Notify Claude Code of task updates."""
        
        try:
            # Get callback if registered
            callback = self._task_callbacks.get(claude_task_id)
            if not callback:
                return
            
            # Prepare update data
            update_data = {
                'task_id': claude_task_id,
                'status': self._status_map.get(maos_task.status, 'unknown'),
                'updated_at': maos_task.updated_at.isoformat(),
                'message': f'Task status updated to {maos_task.status.value}'
            }
            
            # Add additional data based on status
            if maos_task.status == TaskStatus.COMPLETED:
                update_data['result'] = await self._convert_maos_results_to_claude(maos_task.result)
                update_data['completed_at'] = maos_task.completed_at.isoformat()
            elif maos_task.status == TaskStatus.FAILED:
                update_data['error'] = maos_task.error
                update_data['completed_at'] = maos_task.completed_at.isoformat()
            elif maos_task.status == TaskStatus.RUNNING:
                update_data['started_at'] = maos_task.started_at.isoformat()
                update_data['agent_id'] = str(maos_task.agent_id) if maos_task.agent_id else None
            
            # Invoke callback
            await self._invoke_callback(callback, update_data)
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'notify_claude_task_update',
                'claude_task_id': claude_task_id,
                'maos_task_id': str(maos_task.id)
            })
    
    async def _invoke_callback(self, callback: Callable, data: Dict[str, Any]) -> None:
        """Safely invoke a callback function."""
        
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(data)
            else:
                callback(data)
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'invoke_callback',
                'callback': str(callback),
                'data': data
            })
    
    # Task management convenience methods
    async def ensure_agents_available(self, task_type: str, min_agents: int = 1) -> List[str]:
        """
        Ensure that agents with appropriate capabilities are available.
        
        Args:
            task_type: Type of task that needs agents
            min_agents: Minimum number of agents required
            
        Returns:
            List of agent IDs
        """
        
        try:
            # Get required capabilities for task type
            required_capabilities = self._task_capability_map.get(task_type, {AgentCapability.TASK_EXECUTION})
            
            # Get available agents with required capabilities
            available_agents = await self.orchestrator.get_available_agents(required_capabilities)
            
            # If we don't have enough agents, create more
            if len(available_agents) < min_agents:
                agents_needed = min_agents - len(available_agents)
                
                for i in range(agents_needed):
                    agent = await self.orchestrator.create_agent(
                        agent_type=f"claude_{task_type}_agent",
                        capabilities=required_capabilities,
                        configuration={
                            'created_for': 'claude_code',
                            'task_type': task_type,
                            'auto_created': True
                        }
                    )
                    available_agents.append(agent)
            
            return [str(agent.id) for agent in available_agents[:min_agents]]
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'ensure_agents_available',
                'task_type': task_type,
                'min_agents': min_agents
            })
            raise OrchestrationError(f"Failed to ensure agents available: {str(e)}")
    
    async def cleanup_completed_tasks(self, max_age_hours: int = 24) -> int:
        """
        Cleanup completed Claude Code tasks older than specified age.
        
        Args:
            max_age_hours: Maximum age of completed tasks to keep
            
        Returns:
            Number of tasks cleaned up
        """
        
        try:
            from datetime import timedelta
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            cleaned_count = 0
            tasks_to_remove = []
            
            for claude_task_id, maos_task_id in self._claude_task_mapping.items():
                try:
                    maos_task = await self.orchestrator.get_task(maos_task_id)
                    if (maos_task and 
                        maos_task.is_terminal() and 
                        maos_task.completed_at and
                        maos_task.completed_at < cutoff_time):
                        
                        tasks_to_remove.append((claude_task_id, maos_task_id))
                        
                except Exception:
                    # If task can't be retrieved, mark for removal
                    tasks_to_remove.append((claude_task_id, maos_task_id))
            
            # Remove old tasks
            for claude_task_id, maos_task_id in tasks_to_remove:
                del self._claude_task_mapping[claude_task_id]
                del self._maos_task_mapping[maos_task_id]
                
                # Remove callback if present
                if claude_task_id in self._task_callbacks:
                    del self._task_callbacks[claude_task_id]
                
                cleaned_count += 1
            
            if cleaned_count > 0:
                self.logger.logger.info(
                    f"Cleaned up {cleaned_count} completed Claude tasks",
                    extra={'max_age_hours': max_age_hours}
                )
            
            return cleaned_count
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'cleanup_completed_tasks',
                'max_age_hours': max_age_hours
            })
            return 0


# Factory function for easy integration creation
def create_claude_integration(orchestrator: Orchestrator, **kwargs) -> ClaudeTaskIntegration:
    """Factory function to create Claude Code integration."""
    return ClaudeTaskIntegration(orchestrator, **kwargs)