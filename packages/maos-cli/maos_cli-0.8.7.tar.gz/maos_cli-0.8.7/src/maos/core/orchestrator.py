"""
Main Orchestrator component for MAOS orchestration system.

This component coordinates between all other MAOS components:
- Task Planner: For task decomposition and planning
- Agent Manager: For agent lifecycle and assignments  
- Resource Allocator: For resource management
- State Manager: For state persistence and recovery
- Message Bus: For inter-component communication
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Tuple
from uuid import UUID, uuid4

from ..interfaces.orchestrator_interface import OrchestratorInterface
from ..interfaces.state_manager import StateManager
from ..interfaces.message_bus import MessageBus, EventHandler
from ..interfaces.persistence import PersistenceInterface, FilePersistence
# Optional Redis imports
try:
    from ..interfaces.redis_persistence import RedisPersistence
    from ..interfaces.redis_message_bus import RedisMessageBus
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    RedisPersistence = None
    RedisMessageBus = None

from ..core.task_planner import TaskPlanner, ExecutionPlan
from ..core.agent_manager import AgentManager
from ..core.resource_allocator import ResourceAllocator
from ..core.context_manager import ContextManager, ContextType, ContextStrategy
from ..core.swarm_coordinator import SwarmCoordinator, SwarmConfiguration, SwarmPattern, CoordinationStrategy
from ..interfaces.claude_commands import ClaudeCommandInterface

from ..models.task import Task, TaskStatus, TaskPriority
from ..models.agent import Agent, AgentCapability
from ..models.resource import Resource, ResourceType
from ..models.message import Message, MessageType, MessagePriority
from ..models.checkpoint import Checkpoint, CheckpointType

from ..utils.logging_config import MAOSLogger, setup_logging
from ..utils.exceptions import (
    MAOSError, TaskError, AgentError, ResourceError,
    OrchestrationError
)


class MAOSEventHandler(EventHandler):
    """Event handler for MAOS orchestrator internal events."""
    
    def __init__(self, orchestrator: 'Orchestrator'):
        self.orchestrator = orchestrator
        self.logger = MAOSLogger("maos_event_handler")
    
    async def handle_message(self, message: Message) -> None:
        """Handle incoming messages."""
        try:
            if message.type == MessageType.TASK_COMPLETION:
                await self._handle_task_completion(message)
            elif message.type == MessageType.TASK_FAILURE:
                await self._handle_task_failure(message)
            elif message.type == MessageType.HEARTBEAT:
                await self._handle_heartbeat(message)
            elif message.type == MessageType.ERROR_REPORT:
                await self._handle_error_report(message)
            elif message.type == MessageType.RESOURCE_REQUEST:
                await self._handle_resource_request(message)
            elif message.type == MessageType.STATUS_UPDATE:
                await self._handle_status_update(message)
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'handle_message',
                'message_type': message.type.value,
                'message_id': str(message.id)
            })
    
    def get_supported_message_types(self) -> Set[MessageType]:
        """Get supported message types."""
        return {
            MessageType.TASK_COMPLETION,
            MessageType.TASK_FAILURE,
            MessageType.HEARTBEAT,
            MessageType.ERROR_REPORT,
            MessageType.RESOURCE_REQUEST,
            MessageType.STATUS_UPDATE
        }
    
    async def _handle_task_completion(self, message: Message) -> None:
        """Handle task completion event."""
        task_id = message.payload.get('task_id')
        result = message.payload.get('result')
        execution_time = message.payload.get('execution_time', 0.0)
        
        if task_id:
            task_uuid = UUID(task_id)
            await self.orchestrator._on_task_completed(task_uuid, result, execution_time)
    
    async def _handle_task_failure(self, message: Message) -> None:
        """Handle task failure event."""
        task_id = message.payload.get('task_id')
        error = message.payload.get('error')
        execution_time = message.payload.get('execution_time', 0.0)
        
        if task_id:
            task_uuid = UUID(task_id)
            await self.orchestrator._on_task_failed(task_uuid, error, execution_time)
    
    async def _handle_heartbeat(self, message: Message) -> None:
        """Handle agent heartbeat."""
        agent_id = message.sender_id
        cpu_usage = message.payload.get('cpu_usage', 0.0)
        memory_usage = message.payload.get('memory_usage', 0.0)
        
        if agent_id:
            agent = await self.orchestrator.agent_manager.get_agent(agent_id)
            if agent:
                agent.update_heartbeat(cpu_usage, memory_usage)
    
    async def _handle_error_report(self, message: Message) -> None:
        """Handle error reports."""
        error_type = message.payload.get('error_type')
        error_message = message.payload.get('error_message')
        component = message.payload.get('component')
        
        self.logger.logger.error(
            f"Error report received: {error_message}",
            extra={
                'error_type': error_type,
                'component': component,
                'reporter_id': str(message.sender_id) if message.sender_id else None
            }
        )
    
    async def _handle_resource_request(self, message: Message) -> None:
        """Handle resource allocation requests."""
        requester_id = message.sender_id
        requirements = message.payload.get('requirements', {})
        priority_str = message.payload.get('priority', 'MEDIUM')
        
        if requester_id and requirements:
            try:
                priority = TaskPriority(priority_str)
                request_id = await self.orchestrator.resource_allocator.request_allocation(
                    requester_id=requester_id,
                    resource_requirements=requirements,
                    priority=priority
                )
                
                # Send response
                await self.orchestrator.message_bus.send_direct(
                    recipient_id=requester_id,
                    message_type=MessageType.RESOURCE_ALLOCATION,
                    payload={'request_id': str(request_id)},
                    correlation_id=message.id
                )
                
            except Exception as e:
                self.logger.log_error(e, {
                    'operation': 'handle_resource_request',
                    'requester_id': str(requester_id)
                })
    
    async def _handle_status_update(self, message: Message) -> None:
        """Handle status updates from components."""
        component = message.payload.get('component')
        status = message.payload.get('status')
        
        self.logger.logger.debug(
            f"Status update: {component} = {status}",
            extra={
                'component': component,
                'status': status,
                'sender_id': str(message.sender_id) if message.sender_id else None
            }
        )


class Orchestrator(OrchestratorInterface):
    """
    Main orchestrator for the MAOS system.
    
    Coordinates between all components to provide a unified orchestration interface.
    """
    
    def __init__(
        self,
        persistence_backend: Optional[PersistenceInterface] = None,
        logging_config: Optional[Dict[str, Any]] = None,
        component_config: Optional[Dict[str, Any]] = None,
        use_redis: Optional[bool] = None
    ):
        """Initialize the MAOS orchestrator."""
        
        # Setup logging
        if logging_config:
            setup_logging(**logging_config)
        
        self.logger = MAOSLogger("orchestrator", str(uuid4()))
        
        # Configuration
        self.component_config = component_config or {}
        
        # Determine if Redis should be used
        if use_redis is None:
            # Check for Redis configuration in environment or config
            import os
            use_redis = (
                os.getenv('REDIS_URL') is not None or 
                self.component_config.get('use_redis', False)
            )
        
        self.use_redis = use_redis
        
        # Initialize persistence backend
        if persistence_backend is None:
            if self.use_redis and REDIS_AVAILABLE:
                # Use Redis persistence
                redis_config = self.component_config.get('redis', {})
                persistence_backend = RedisPersistence(
                    redis_url=redis_config.get('url'),
                    enable_cluster=redis_config.get('cluster_mode', False),
                    enable_compression=redis_config.get('compression', True),
                    memory_pool_size_gb=redis_config.get('memory_pool_gb', 10)
                )
                self.logger.logger.info("Using Redis persistence backend")
            else:
                # Use file persistence
                if self.use_redis and not REDIS_AVAILABLE:
                    self.logger.logger.warning("Redis requested but not available. Using file persistence instead.")
                storage_dir = self.component_config.get('storage_directory', './maos_storage')
                persistence_backend = FilePersistence(storage_directory=storage_dir)
                self.logger.logger.info("Using file persistence backend")
        
        # Initialize core components
        self.state_manager = StateManager(
            persistence_backend=persistence_backend,
            **self.component_config.get('state_manager', {})
        )
        
        # Initialize message bus
        if self.use_redis and REDIS_AVAILABLE:
            # Use Redis-backed message bus
            redis_config = self.component_config.get('redis', {})
            self.message_bus = RedisMessageBus(
                redis_url=redis_config.get('url'),
                channel_prefix=redis_config.get('channel_prefix', 'maos'),
                **self.component_config.get('message_bus', {})
            )
            self.logger.logger.info("Using Redis message bus")
        else:
            # Use in-memory message bus
            self.message_bus = MessageBus(
                **self.component_config.get('message_bus', {})
            )
            self.logger.logger.info("Using in-memory message bus")
        
        self.task_planner = TaskPlanner(
            **self.component_config.get('task_planner', {})
        )
        
        # Extract Claude configuration
        claude_config = self.component_config.get('claude_integration', {})
        agent_manager_config = self.component_config.get('agent_manager', {})
        
        # Merge Claude settings into agent manager config
        if claude_config.get('enabled', False):
            agent_manager_config.update({
                'enable_claude_integration': True,
                'claude_cli_path': claude_config.get('cli_command', 'claude'),
                'claude_working_dir': claude_config.get('working_directory', './claude_workspaces'),
                'max_agents': min(
                    agent_manager_config.get('max_agents', 20),
                    claude_config.get('max_processes', 10)
                )
            })
        
        self.agent_manager = AgentManager(**agent_manager_config)
        
        self.resource_allocator = ResourceAllocator(
            **self.component_config.get('resource_allocator', {})
        )
        
        # Claude Command Interface (initialized after agent manager starts)
        self.claude_command_interface: Optional[ClaudeCommandInterface] = None
        
        # Context Manager (initialized after Claude interface is ready)
        self.context_manager: Optional[ContextManager] = None
        
        # Swarm Coordinator (initialized after other components)
        self.swarm_coordinator: Optional[SwarmCoordinator] = None
        
        # Internal state
        self._running = False
        self._startup_time: Optional[datetime] = None
        self._execution_plans: Dict[UUID, ExecutionPlan] = {}
        self._active_executions: Dict[UUID, asyncio.Task] = {}
        
        # Event handler
        self._event_handler = MAOSEventHandler(self)
        
        # Metrics
        self._metrics = {
            'tasks_submitted': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'agents_created': 0,
            'resources_allocated': 0,
            'uptime_seconds': 0
        }
    
    async def start(self) -> None:
        """Start the orchestrator and all sub-components."""
        if self._running:
            return
        
        self.logger.logger.info("Starting MAOS Orchestrator")
        
        try:
            # Initialize Redis if needed
            if self.use_redis:
                if hasattr(self.state_manager.persistence_backend, 'initialize'):
                    await self.state_manager.persistence_backend.initialize()
                    self.logger.logger.info("Redis persistence initialized")
            
            # Start core components
            await self.state_manager.start()
            await self.message_bus.start()
            await self.agent_manager.start()
            await self.resource_allocator.start()
            
            # Initialize Claude Command Interface if Claude integration is enabled
            if (hasattr(self.agent_manager, 'claude_cli_manager') and 
                self.agent_manager.claude_cli_manager is not None):
                self.claude_command_interface = ClaudeCommandInterface(
                    cli_manager=self.agent_manager.claude_cli_manager,
                    **self.component_config.get('claude_command_interface', {})
                )
                self.logger.logger.info("Claude Command Interface initialized")
                
                # Initialize Context Manager
                context_config = self.component_config.get('context_manager', {})
                self.context_manager = ContextManager(
                    claude_command_interface=self.claude_command_interface,
                    claude_cli_manager=self.agent_manager.claude_cli_manager,
                    checkpoint_dir=context_config.get('checkpoint_dir', './maos_checkpoints'),
                    auto_save_interval=context_config.get('auto_save_interval', 300),
                    max_checkpoints_per_agent=context_config.get('max_checkpoints_per_agent', 10),
                    context_strategy=ContextStrategy(context_config.get('strategy', 'hybrid'))
                )
                await self.context_manager.start()
                self.logger.logger.info("Context Manager initialized")
            
            # Initialize Swarm Coordinator
            self.swarm_coordinator = SwarmCoordinator(
                agent_manager=self.agent_manager,
                orchestrator=self,
                message_bus=self.message_bus,
                context_manager=self.context_manager,
                enable_monitoring=self.component_config.get('swarm_coordinator', {}).get('enable_monitoring', True)
            )
            self.logger.logger.info("Swarm Coordinator initialized")
            
            # Register event handler
            self.message_bus.register_handler(self._event_handler)
            
            # Setup state change listeners
            self.state_manager.add_change_listener('tasks', self._on_task_state_changed)
            self.state_manager.add_change_listener('agents', self._on_agent_state_changed)
            
            self._running = True
            self._startup_time = datetime.utcnow()
            
            # Create initial checkpoint
            await self._create_startup_checkpoint()
            
            self.logger.logger.info("MAOS Orchestrator started successfully")
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'start_orchestrator'})
            await self.shutdown()
            raise OrchestrationError(f"Failed to start orchestrator: {str(e)}")
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the orchestrator."""
        if not self._running:
            return
        
        self.logger.logger.info("Shutting down MAOS Orchestrator")
        
        try:
            # Cancel active executions
            for execution_task in self._active_executions.values():
                execution_task.cancel()
            
            # Wait for executions to complete
            if self._active_executions:
                await asyncio.gather(
                    *self._active_executions.values(),
                    return_exceptions=True
                )
            
            # Create shutdown checkpoint
            await self._create_shutdown_checkpoint()
            
            # Shutdown Context Manager
            if self.context_manager:
                await self.context_manager.stop()
            
            # Shutdown components
            await self.resource_allocator.shutdown()
            await self.agent_manager.shutdown()
            await self.message_bus.stop()
            await self.state_manager.shutdown()
            
            # Shutdown Redis if needed
            if self.use_redis:
                if hasattr(self.state_manager.persistence_backend, 'shutdown'):
                    await self.state_manager.persistence_backend.shutdown()
                    self.logger.logger.info("Redis persistence shutdown")
            
            self._running = False
            
            self.logger.logger.info("MAOS Orchestrator shutdown complete")
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'shutdown_orchestrator'})
    
    # Task Management Implementation
    
    async def submit_task(
        self,
        task: Task,
        decomposition_strategy: Optional[str] = None
    ) -> ExecutionPlan:
        """Submit a task for execution."""
        if not self._running:
            raise OrchestrationError("Orchestrator is not running")
        
        try:
            # Store task in state
            await self.state_manager.store_object('tasks', task)
            
            # Create execution plan
            plan = await self.task_planner.create_execution_plan(
                root_task=task,
                decomposition_strategy=decomposition_strategy or 'hierarchical'
            )
            
            # Store execution plan
            self._execution_plans[plan.id] = plan
            await self.state_manager.store_object('execution_plans', plan)
            
            self._metrics['tasks_submitted'] += 1
            
            self.logger.log_task_event(
                "submitted",
                str(task.id),
                plan_id=str(plan.id),
                decomposition_strategy=decomposition_strategy
            )
            
            # Publish task submission event
            await self.message_bus.publish_to_topic(
                'task_events',
                MessageType.TASK_ASSIGNMENT,
                {
                    'task_id': str(task.id),
                    'plan_id': str(plan.id),
                    'event': 'task_submitted'
                }
            )
            
            return plan
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'submit_task',
                'task_id': str(task.id)
            })
            raise TaskError(
                f"Failed to submit task: {str(e)}",
                task_id=task.id,
                error_code="TASK_SUBMISSION_FAILED"
            )
    
    async def submit_task_to_claude_agent(
        self,
        task: Task,
        agent_id: Optional[UUID] = None,
        agent_template: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submit a task directly to a Claude Code agent for execution.
        
        Args:
            task: Task to execute
            agent_id: Specific agent ID to use (optional)
            agent_template: Template to use for spawning new agent (optional)
            context: Additional context for task execution
            
        Returns:
            Task execution results including response and metadata
        """
        if not self._running:
            raise OrchestrationError("Orchestrator is not running")
        
        if not self.claude_command_interface:
            raise OrchestrationError("Claude integration is not enabled")
        
        try:
            # If no agent specified, spawn one using template or find available
            if not agent_id:
                if agent_template:
                    # Spawn new Claude agent using template
                    agent = await self.agent_manager.spawn_claude_agent(
                        template_name=agent_template,
                        agent_name=f"{agent_template}-{int(time.time())}"
                    )
                    agent_id = agent.id
                else:
                    # Find available Claude agent
                    available_agents = self.agent_manager.get_available_agents()
                    claude_agents = [
                        agent for agent in available_agents 
                        if agent.id in self.agent_manager._claude_agents
                    ]
                    
                    if not claude_agents:
                        # Default to spawning a general-purpose agent
                        agent = await self.agent_manager.spawn_claude_agent(
                            template_name="web-developer",
                            agent_name=f"general-agent-{int(time.time())}"
                        )
                        agent_id = agent.id
                    else:
                        agent_id = claude_agents[0].id
            
            # Store task in state
            await self.state_manager.store_object('tasks', task)
            
            # Enable auto-save for the agent if context manager is available
            if self.context_manager:
                await self.enable_agent_auto_save(agent_id)
            
            # Execute task using Claude agent
            results = await self.agent_manager.execute_task_with_claude_agent(
                agent_id=agent_id,
                task=task
            )
            
            # Create a task completion checkpoint if successful
            if self.context_manager and results.get("success", False):
                await self.create_context_checkpoint(
                    agent_id=agent_id,
                    checkpoint_name=f"task_completed_{task.name}_{int(time.time())}",
                    context_type=ContextType.TASK_CONTEXT,
                    description=f"Context after completing task: {task.name}"
                )
            
            # Add orchestrator metadata
            results.update({
                'orchestrator_id': str(self.logger.session_id),
                'execution_method': 'claude_direct',
                'agent_id': str(agent_id),
                'task_id': str(task.id),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            self.logger.log_task_event(
                "claude_task_submitted",
                str(task.id),
                agent_id=str(agent_id),
                template_used=agent_template,
                success=results.get("success", False)
            )
            
            return results
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'submit_task_to_claude_agent',
                'task_id': str(task.id),
                'agent_id': str(agent_id) if agent_id else None,
                'agent_template': agent_template
            })
            raise TaskError(
                f"Failed to submit task to Claude agent: {str(e)}",
                task_id=task.id,
                error_code="CLAUDE_TASK_SUBMISSION_FAILED"
            )
    
    async def orchestrate_parallel_claude_tasks(
        self,
        tasks: List[Task],
        agent_templates: Optional[Dict[str, str]] = None,
        max_parallel: int = 5
    ) -> Dict[str, Any]:
        """
        Orchestrate multiple tasks in parallel using Claude agents.
        
        Args:
            tasks: List of tasks to execute
            agent_templates: Map of task_id to agent template (optional)
            max_parallel: Maximum number of parallel executions
            
        Returns:
            Aggregated results from all task executions
        """
        if not self._running:
            raise OrchestrationError("Orchestrator is not running")
        
        if not tasks:
            return {"results": [], "summary": {"total": 0, "success": 0, "failed": 0}}
        
        try:
            # Limit parallel executions
            semaphore = asyncio.Semaphore(max_parallel)
            
            async def execute_single_task(task: Task) -> Dict[str, Any]:
                async with semaphore:
                    template = agent_templates.get(str(task.id)) if agent_templates else None
                    return await self.submit_task_to_claude_agent(
                        task=task,
                        agent_template=template
                    )
            
            # Execute all tasks in parallel
            execution_tasks = [execute_single_task(task) for task in tasks]
            results = await asyncio.gather(*execution_tasks, return_exceptions=True)
            
            # Process results
            successful_results = []
            failed_results = []
            
            for i, result in enumerate(results):
                task_result = {
                    "task_id": str(tasks[i].id),
                    "task_name": tasks[i].name
                }
                
                if isinstance(result, Exception):
                    task_result.update({
                        "success": False,
                        "error": str(result),
                        "result": None
                    })
                    failed_results.append(task_result)
                else:
                    task_result.update(result)
                    if result.get("success", False):
                        successful_results.append(task_result)
                    else:
                        failed_results.append(task_result)
            
            summary = {
                "total": len(tasks),
                "success": len(successful_results),
                "failed": len(failed_results),
                "success_rate": len(successful_results) / len(tasks) if tasks else 0.0,
                "execution_time": max(
                    result.get("execution_time", 0) for result in successful_results + failed_results
                    if isinstance(result, dict)
                ) if (successful_results or failed_results) else 0.0
            }
            
            self.logger.logger.info(
                f"Parallel Claude task orchestration completed",
                extra={
                    "total_tasks": len(tasks),
                    "successful": len(successful_results),
                    "failed": len(failed_results),
                    "success_rate": summary["success_rate"]
                }
            )
            
            return {
                "results": successful_results + failed_results,
                "successful": successful_results,
                "failed": failed_results,
                "summary": summary
            }
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'orchestrate_parallel_claude_tasks',
                'task_count': len(tasks)
            })
            raise OrchestrationError(f"Failed to orchestrate parallel tasks: {str(e)}")
    
    async def get_task(self, task_id: UUID) -> Optional[Task]:
        """Get a task by ID."""
        return await self.state_manager.get_object('tasks', task_id)
    
    async def get_task_status(self, task_id: UUID) -> Optional[TaskStatus]:
        """Get the status of a task."""
        task = await self.get_task(task_id)
        return task.status if task else None
    
    async def cancel_task(self, task_id: UUID, reason: str = "Cancelled") -> bool:
        """Cancel a task."""
        try:
            task = await self.get_task(task_id)
            if not task:
                return False
            
            if task.is_terminal():
                return False  # Cannot cancel completed/failed tasks
            
            # Update task status
            task.update_status(TaskStatus.CANCELLED)
            task.error = reason
            await self.state_manager.store_object('tasks', task)
            
            # Cancel execution if running
            if task_id in self._active_executions:
                execution_task = self._active_executions[task_id]
                execution_task.cancel()
                del self._active_executions[task_id]
            
            self.logger.log_task_event(
                "cancelled",
                str(task_id),
                reason=reason
            )
            
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'cancel_task',
                'task_id': str(task_id)
            })
            return False
    
    async def retry_task(self, task_id: UUID) -> bool:
        """Retry a failed task."""
        try:
            task = await self.get_task(task_id)
            if not task or not task.can_retry():
                return False
            
            # Reset task state for retry
            task.update_status(TaskStatus.PENDING)
            task.error = None
            task.result = None
            task.retry_count += 1
            
            await self.state_manager.store_object('tasks', task)
            
            self.logger.log_task_event(
                "retrying",
                str(task_id),
                retry_count=task.retry_count
            )
            
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'retry_task',
                'task_id': str(task_id)
            })
            return False
    
    async def get_task_results(self, task_id: UUID) -> Optional[Any]:
        """Get the results of a completed task."""
        task = await self.get_task(task_id)
        if task and task.status == TaskStatus.COMPLETED:
            return task.result
        return None
    
    # Claude Agent Management Methods
    
    async def get_claude_agent_status(self, agent_id: UUID) -> Optional[Dict[str, Any]]:
        """Get detailed status of a Claude agent."""
        if not self.claude_command_interface:
            return None
        
        return self.agent_manager.get_claude_agent_status(agent_id)
    
    async def list_claude_agents(self) -> List[Dict[str, Any]]:
        """List all Claude agents with their status."""
        if not self.claude_command_interface:
            return []
        
        return self.agent_manager.list_claude_agents()
    
    async def spawn_specialized_claude_agent(
        self,
        template_name: str,
        agent_name: Optional[str] = None,
        **template_params
    ) -> Agent:
        """
        Spawn a specialized Claude agent using a template.
        
        Args:
            template_name: Name of the agent template
            agent_name: Custom name for the agent
            **template_params: Additional template parameters
            
        Returns:
            Spawned Claude agent
        """
        if not self._running:
            raise OrchestrationError("Orchestrator is not running")
        
        if not self.claude_command_interface:
            raise OrchestrationError("Claude integration is not enabled")
        
        try:
            agent = await self.agent_manager.spawn_claude_agent(
                template_name=template_name,
                agent_name=agent_name,
                **template_params
            )
            
            # Store agent in state
            await self.state_manager.store_object('agents', agent)
            
            self.logger.log_agent_event(
                "specialized_claude_agent_spawned",
                str(agent.id),
                template_name=template_name,
                agent_name=agent_name or template_name
            )
            
            return agent
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'spawn_specialized_claude_agent',
                'template_name': template_name,
                'agent_name': agent_name
            })
            raise AgentError(f"Failed to spawn specialized Claude agent: {str(e)}")
    
    # Context Management Methods
    
    async def create_context_checkpoint(
        self,
        agent_id: UUID,
        checkpoint_name: Optional[str] = None,
        context_type: ContextType = ContextType.AGENT_SESSION,
        description: Optional[str] = None
    ) -> Optional[UUID]:
        """
        Create a context checkpoint for an agent.
        
        Args:
            agent_id: Agent to create checkpoint for
            checkpoint_name: Optional name for the checkpoint
            context_type: Type of context to save
            description: Optional description
            
        Returns:
            Checkpoint ID if successful, None otherwise
        """
        if not self.context_manager:
            self.logger.logger.warning("Context Manager not available for checkpoint creation")
            return None
        
        # Find the Claude agent process
        if agent_id not in self.agent_manager._claude_agents:
            raise AgentError(f"Agent {agent_id} is not a Claude agent")
        
        claude_agent = self.agent_manager._claude_agents[agent_id]
        process_id = claude_agent.process_id
        
        try:
            checkpoint = await self.context_manager.create_checkpoint(
                agent_id=agent_id,
                process_id=process_id,
                context_type=context_type,
                name=checkpoint_name,
                description=description,
                metadata={
                    'orchestrator_session': str(self.logger.session_id),
                    'agent_template': getattr(claude_agent.agent_definition, 'type', 'unknown')
                }
            )
            
            if checkpoint.saved_successfully:
                self.logger.log_agent_event(
                    "context_checkpoint_created",
                    str(agent_id),
                    checkpoint_id=str(checkpoint.id),
                    checkpoint_name=checkpoint.name
                )
                return checkpoint.id
            else:
                return None
                
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'create_context_checkpoint',
                'agent_id': str(agent_id)
            })
            return None
    
    async def restore_context_checkpoint(
        self,
        checkpoint_id: UUID,
        target_agent_id: Optional[UUID] = None
    ) -> bool:
        """
        Restore a context checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint to restore
            target_agent_id: Agent to restore to (if different from original)
            
        Returns:
            True if restoration was successful
        """
        if not self.context_manager:
            self.logger.logger.warning("Context Manager not available for checkpoint restoration")
            return False
        
        try:
            # Get checkpoint info
            checkpoint = self.context_manager.get_checkpoint(checkpoint_id)
            if not checkpoint:
                self.logger.logger.error(f"Checkpoint not found: {checkpoint_id}")
                return False
            
            # Determine target agent and process
            agent_id = target_agent_id or checkpoint.agent_id
            
            if agent_id not in self.agent_manager._claude_agents:
                self.logger.logger.error(f"Target agent not found or not a Claude agent: {agent_id}")
                return False
            
            claude_agent = self.agent_manager._claude_agents[agent_id]
            target_process_id = claude_agent.process_id
            
            success = await self.context_manager.restore_checkpoint(
                checkpoint_id=checkpoint_id,
                target_process_id=target_process_id
            )
            
            if success:
                self.logger.log_agent_event(
                    "context_checkpoint_restored",
                    str(agent_id),
                    checkpoint_id=str(checkpoint_id),
                    original_agent_id=str(checkpoint.agent_id)
                )
            
            return success
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'restore_context_checkpoint',
                'checkpoint_id': str(checkpoint_id),
                'target_agent_id': str(target_agent_id) if target_agent_id else None
            })
            return False
    
    async def enable_agent_auto_save(
        self,
        agent_id: UUID,
        interval_seconds: Optional[int] = None
    ) -> bool:
        """
        Enable automatic context saving for an agent.
        
        Args:
            agent_id: Agent to enable auto-save for
            interval_seconds: Save interval (uses default if None)
            
        Returns:
            True if auto-save was enabled successfully
        """
        if not self.context_manager:
            return False
        
        if agent_id not in self.agent_manager._claude_agents:
            return False
        
        try:
            claude_agent = self.agent_manager._claude_agents[agent_id]
            process_id = claude_agent.process_id
            
            await self.context_manager.enable_auto_save(
                agent_id=agent_id,
                process_id=process_id,
                interval_seconds=interval_seconds
            )
            
            self.logger.log_agent_event(
                "auto_save_enabled",
                str(agent_id),
                interval_seconds=interval_seconds
            )
            
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'enable_agent_auto_save',
                'agent_id': str(agent_id)
            })
            return False
    
    async def share_agent_context(
        self,
        source_agent_id: UUID,
        target_agent_ids: List[UUID],
        context_key: str,
        context_data: Dict[str, Any]
    ) -> bool:
        """
        Share context between agents.
        
        Args:
            source_agent_id: Agent sharing the context
            target_agent_ids: Agents receiving the context
            context_key: Key for the shared context
            context_data: Context data to share
            
        Returns:
            True if sharing was successful
        """
        if not self.context_manager:
            return False
        
        try:
            success = await self.context_manager.share_context(
                source_agent_id=source_agent_id,
                target_agent_ids=target_agent_ids,
                context_key=context_key,
                context_data=context_data,
                access_rules={'shared_via': 'orchestrator'}
            )
            
            if success:
                self.logger.logger.info(
                    f"Context shared between agents",
                    extra={
                        'source_agent_id': str(source_agent_id),
                        'target_agent_count': len(target_agent_ids),
                        'context_key': context_key
                    }
                )
            
            return success
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'share_agent_context',
                'source_agent_id': str(source_agent_id),
                'context_key': context_key
            })
            return False
    
    async def get_agent_checkpoints(self, agent_id: UUID) -> List[Dict[str, Any]]:
        """Get all checkpoints for an agent."""
        if not self.context_manager:
            return []
        
        checkpoints = self.context_manager.get_agent_checkpoints(agent_id)
        
        return [
            {
                'id': str(checkpoint.id),
                'name': checkpoint.name,
                'context_type': checkpoint.context_type.value,
                'created_at': checkpoint.created_at.isoformat(),
                'size_bytes': checkpoint.size_bytes,
                'description': checkpoint.description,
                'saved_successfully': checkpoint.saved_successfully,
                'restoration_tested': checkpoint.restoration_tested
            }
            for checkpoint in checkpoints
        ]
    
    # Swarm Coordination Methods
    
    async def create_agent_swarm(
        self,
        name: str,
        pattern: SwarmPattern = SwarmPattern.HUB_AND_SPOKE,
        strategy: CoordinationStrategy = CoordinationStrategy.CAPABILITY_BASED,
        agent_templates: Optional[List[str]] = None,
        min_agents: int = 2,
        max_agents: int = 10
    ) -> UUID:
        """
        Create a new agent swarm for distributed task execution.
        
        Args:
            name: Name of the swarm
            pattern: Coordination pattern to use
            strategy: Task distribution strategy
            agent_templates: Templates for specialized agents
            min_agents: Minimum number of agents
            max_agents: Maximum number of agents
            
        Returns:
            Swarm ID
        """
        if not self.swarm_coordinator:
            raise OrchestrationError("Swarm coordinator not initialized")
        
        configuration = SwarmConfiguration(
            pattern=pattern,
            strategy=strategy,
            min_agents=min_agents,
            max_agents=max_agents,
            agent_templates=agent_templates or [],
            enable_consensus=pattern == SwarmPattern.CONSENSUS,
            enable_recovery=True
        )
        
        swarm_id = await self.swarm_coordinator.create_swarm(
            name=name,
            configuration=configuration
        )
        
        self.logger.logger.info(
            f"Created agent swarm: {name}",
            extra={
                'swarm_id': str(swarm_id),
                'pattern': pattern.value,
                'strategy': strategy.value,
                'min_agents': min_agents
            }
        )
        
        return swarm_id
    
    async def execute_swarm_task(
        self,
        swarm_id: UUID,
        task: Task,
        execution_mode: str = "parallel"
    ) -> Dict[str, Any]:
        """
        Execute a task using a swarm of agents.
        
        Args:
            swarm_id: ID of the swarm
            task: Task to execute
            execution_mode: Mode of execution (parallel, pipeline, map_reduce)
            
        Returns:
            Execution results
        """
        if not self.swarm_coordinator:
            raise OrchestrationError("Swarm coordinator not initialized")
        
        if execution_mode == "parallel":
            # Break task into subtasks if possible
            subtasks = self._decompose_task(task)
            if len(subtasks) > 1:
                results = await self.swarm_coordinator.coordinate_parallel_execution(
                    swarm_id=swarm_id,
                    tasks=subtasks
                )
            else:
                swarm_task = await self.swarm_coordinator.submit_swarm_task(
                    swarm_id=swarm_id,
                    task=task
                )
                results = {'swarm_task_id': str(swarm_task.id)}
                
        elif execution_mode == "pipeline":
            # Create pipeline stages
            pipeline_tasks = self._create_pipeline_tasks(task)
            results = await self.swarm_coordinator.coordinate_pipeline_execution(
                swarm_id=swarm_id,
                tasks=pipeline_tasks
            )
            
        elif execution_mode == "map_reduce":
            # Extract map and reduce tasks
            map_task, reduce_task, data_chunks = self._prepare_map_reduce(task)
            results = await self.swarm_coordinator.coordinate_map_reduce(
                swarm_id=swarm_id,
                map_task=map_task,
                reduce_task=reduce_task,
                data_chunks=data_chunks
            )
            
        elif execution_mode == "consensus":
            # Execute with consensus
            results = await self.swarm_coordinator.coordinate_with_consensus(
                swarm_id=swarm_id,
                task=task,
                min_agents=3
            )
            
        else:
            # Default to single task submission
            swarm_task = await self.swarm_coordinator.submit_swarm_task(
                swarm_id=swarm_id,
                task=task
            )
            results = {'swarm_task_id': str(swarm_task.id)}
        
        return results
    
    async def get_swarm_status(self, swarm_id: UUID) -> Optional[Dict[str, Any]]:
        """Get status of a swarm."""
        if not self.swarm_coordinator:
            return None
        
        return await self.swarm_coordinator.get_swarm_status(swarm_id)
    
    async def shutdown_swarm(self, swarm_id: UUID) -> None:
        """Shutdown a swarm."""
        if not self.swarm_coordinator:
            return
        
        await self.swarm_coordinator.shutdown_swarm(swarm_id)
    
    def _decompose_task(self, task: Task) -> List[Task]:
        """Decompose a task into subtasks for parallel execution."""
        subtasks = []
        
        # Check if task has explicit subtasks
        if 'subtasks' in task.metadata:
            for subtask_data in task.metadata['subtasks']:
                subtask = Task(
                    name=subtask_data.get('name', f"{task.name}_sub"),
                    description=subtask_data.get('description', ''),
                    priority=task.priority,
                    metadata={
                        'parent_task': str(task.id),
                        **subtask_data.get('metadata', {})
                    }
                )
                subtasks.append(subtask)
        
        # If no subtasks, return original task
        if not subtasks:
            subtasks = [task]
        
        return subtasks
    
    def _create_pipeline_tasks(self, task: Task) -> List[Task]:
        """Create pipeline stages from a task."""
        stages = []
        
        # Check for pipeline stages in metadata
        if 'pipeline_stages' in task.metadata:
            for i, stage_data in enumerate(task.metadata['pipeline_stages']):
                stage_task = Task(
                    name=stage_data.get('name', f"{task.name}_stage_{i+1}"),
                    description=stage_data.get('description', ''),
                    priority=task.priority,
                    metadata={
                        'parent_task': str(task.id),
                        'stage_number': i+1,
                        **stage_data.get('metadata', {})
                    }
                )
                stages.append(stage_task)
        else:
            # Default: single stage
            stages = [task]
        
        return stages
    
    def _prepare_map_reduce(self, task: Task) -> Tuple[Task, Task, List[Any]]:
        """Prepare map-reduce components from a task."""
        # Extract from metadata or use defaults
        map_config = task.metadata.get('map_task', {})
        reduce_config = task.metadata.get('reduce_task', {})
        data_chunks = task.metadata.get('data_chunks', [])
        
        map_task = Task(
            name=map_config.get('name', f"{task.name}_map"),
            description=map_config.get('description', 'Map phase'),
            priority=task.priority,
            metadata=map_config.get('metadata', {})
        )
        
        reduce_task = Task(
            name=reduce_config.get('name', f"{task.name}_reduce"),
            description=reduce_config.get('description', 'Reduce phase'),
            priority=task.priority,
            metadata=reduce_config.get('metadata', {})
        )
        
        # If no data chunks, create a single chunk
        if not data_chunks:
            data_chunks = [task.metadata.get('data', {})]
        
        return map_task, reduce_task, data_chunks
    
    # Agent Management Implementation
    
    async def create_agent(
        self,
        agent_type: str,
        capabilities: Set[AgentCapability],
        configuration: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """Create a new agent."""
        if not self._running:
            raise OrchestrationError("Orchestrator is not running")
        
        try:
            agent = await self.agent_manager.spawn_agent(
                agent_type=agent_type,
                capabilities=capabilities,
                configuration=configuration
            )
            
            # Store agent in state
            await self.state_manager.store_object('agents', agent)
            
            self._metrics['agents_created'] += 1
            
            return agent
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'create_agent',
                'agent_type': agent_type
            })
            raise AgentError(f"Failed to create agent: {str(e)}")
    
    async def get_agent(self, agent_id: UUID) -> Optional[Agent]:
        """Get an agent by ID."""
        return await self.state_manager.get_object('agents', agent_id)
    
    async def get_available_agents(
        self,
        required_capabilities: Optional[Set[AgentCapability]] = None
    ) -> List[Agent]:
        """Get list of available agents."""
        all_agents = await self.state_manager.get_objects('agents')
        
        if required_capabilities:
            return [
                agent for agent in all_agents 
                if agent.is_available() and agent.can_handle_task(required_capabilities)
            ]
        else:
            return [agent for agent in all_agents if agent.is_available()]
    
    async def terminate_agent(
        self,
        agent_id: UUID,
        reason: str = "Manual termination"
    ) -> bool:
        """Terminate an agent."""
        try:
            success = await self.agent_manager.terminate_agent(agent_id, reason)
            
            if success:
                # Remove from state
                await self.state_manager.remove_object('agents', agent_id)
            
            return success
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'terminate_agent',
                'agent_id': str(agent_id)
            })
            return False
    
    # Resource Management Implementation
    
    async def create_resource(
        self,
        resource_type: ResourceType,
        capacity: float,
        configuration: Optional[Dict[str, Any]] = None
    ) -> Resource:
        """Create a new resource."""
        if not self._running:
            raise OrchestrationError("Orchestrator is not running")
        
        try:
            resource = await self.resource_allocator.create_resource(
                resource_type=resource_type,
                capacity=capacity,
                **(configuration or {})
            )
            
            # Store resource in state
            await self.state_manager.store_object('resources', resource)
            
            return resource
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'create_resource',
                'resource_type': resource_type.value
            })
            raise ResourceError(f"Failed to create resource: {str(e)}")
    
    async def get_resource(self, resource_id: UUID) -> Optional[Resource]:
        """Get a resource by ID."""
        return await self.state_manager.get_object('resources', resource_id)
    
    async def request_resources(
        self,
        requester_id: UUID,
        resource_requirements: Dict[str, float],
        priority: TaskPriority = TaskPriority.MEDIUM
    ) -> UUID:
        """Request resource allocation."""
        try:
            request_id = await self.resource_allocator.request_allocation(
                requester_id=requester_id,
                resource_requirements=resource_requirements,
                priority=priority
            )
            
            self._metrics['resources_allocated'] += 1
            
            return request_id
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'request_resources',
                'requester_id': str(requester_id)
            })
            raise ResourceError(f"Failed to request resources: {str(e)}")
    
    async def release_resources(
        self,
        requester_id: UUID,
        resource_id: Optional[UUID] = None
    ) -> float:
        """Release allocated resources."""
        try:
            return await self.resource_allocator.release_allocation(
                requester_id=requester_id,
                resource_id=resource_id
            )
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'release_resources',
                'requester_id': str(requester_id)
            })
            raise ResourceError(f"Failed to release resources: {str(e)}")
    
    # Execution Plan Implementation
    
    async def get_execution_plan(self, plan_id: UUID) -> Optional[ExecutionPlan]:
        """Get an execution plan by ID."""
        return self._execution_plans.get(plan_id)
    
    async def execute_plan(self, plan_id: UUID) -> bool:
        """Execute a planned workflow."""
        if not self._running:
            raise OrchestrationError("Orchestrator is not running")
        
        plan = await self.get_execution_plan(plan_id)
        if not plan:
            raise OrchestrationError(f"Execution plan not found: {plan_id}")
        
        if plan_id in self._active_executions:
            return False  # Already executing
        
        try:
            # Start execution task
            execution_task = asyncio.create_task(self._execute_plan_task(plan))
            self._active_executions[plan_id] = execution_task
            
            self.logger.logger.info(
                f"Started execution of plan {plan_id}",
                extra={'plan_id': str(plan_id)}
            )
            
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'execute_plan',
                'plan_id': str(plan_id)
            })
            return False
    
    async def _execute_plan_task(self, plan: ExecutionPlan) -> None:
        """Execute a plan asynchronously."""
        try:
            completed_tasks = set()
            
            # Execute parallel groups sequentially
            for group in plan.parallel_groups:
                # Get ready tasks from this group
                ready_tasks = [
                    task_id for task_id in group
                    if task_id not in completed_tasks and 
                    plan.tasks[task_id].is_ready()
                ]
                
                if ready_tasks:
                    # Execute tasks in parallel
                    execution_tasks = []
                    for task_id in ready_tasks:
                        task = plan.tasks[task_id]
                        execution_tasks.append(self._execute_task(task))
                    
                    # Wait for all tasks in group to complete
                    results = await asyncio.gather(*execution_tasks, return_exceptions=True)
                    
                    # Process results
                    for i, result in enumerate(results):
                        task_id = ready_tasks[i]
                        if isinstance(result, Exception):
                            await self._on_task_failed(task_id, str(result), 0.0)
                        else:
                            await self._on_task_completed(task_id, result, 0.0)
                            completed_tasks.add(task_id)
        
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'execute_plan_task',
                'plan_id': str(plan.id)
            })
        finally:
            # Remove from active executions
            if plan.id in self._active_executions:
                del self._active_executions[plan.id]
    
    async def _execute_task(self, task: Task) -> Any:
        """Execute a single task."""
        try:
            # Update task status
            task.update_status(TaskStatus.RUNNING)
            await self.state_manager.store_object('tasks', task)
            
            # Assign to available agent
            available_agents = await self.get_available_agents()
            if not available_agents:
                raise TaskError("No available agents for task execution")
            
            agent = available_agents[0]  # Simple assignment strategy
            agent_id = await self.agent_manager.assign_task(task)
            
            # Simulate task execution
            await asyncio.sleep(1)  # Placeholder for actual work
            
            # Complete task
            result = f"Task {task.id} completed successfully"
            task.result = result
            task.update_status(TaskStatus.COMPLETED)
            await self.state_manager.store_object('tasks', task)
            
            # Complete assignment in agent manager
            await self.agent_manager.complete_task(task.id, True, 1.0, result)
            
            return result
            
        except Exception as e:
            task.error = str(e)
            task.update_status(TaskStatus.FAILED)
            await self.state_manager.store_object('tasks', task)
            raise
    
    # System Status and Metrics Implementation
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        uptime = (
            (datetime.utcnow() - self._startup_time).total_seconds()
            if self._startup_time else 0
        )
        
        return {
            'running': self._running,
            'uptime_seconds': uptime,
            'startup_time': self._startup_time.isoformat() if self._startup_time else None,
            'components': {
                'state_manager': 'running' if self.state_manager else 'stopped',
                'message_bus': 'running' if self.message_bus._running else 'stopped',
                'task_planner': 'running',
                'agent_manager': 'running',
                'resource_allocator': 'running'
            },
            'active_executions': len(self._active_executions),
            'execution_plans': len(self._execution_plans)
        }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        # Update uptime
        if self._startup_time:
            self._metrics['uptime_seconds'] = (
                datetime.utcnow() - self._startup_time
            ).total_seconds()
        
        # Collect metrics from all components
        component_metrics = {
            'orchestrator': self._metrics,
            'task_planner': self.task_planner.get_metrics(),
            'agent_manager': self.agent_manager.get_metrics(),
            'resource_allocator': self.resource_allocator.get_metrics(),
            'state_manager': self.state_manager.get_metrics(),
            'message_bus': self.message_bus.get_metrics()
        }
        
        # Add context manager metrics if available
        if self.context_manager:
            component_metrics['context_manager'] = self.context_manager.get_metrics()
        
        return component_metrics
    
    async def get_component_health(self) -> Dict[str, str]:
        """Get health status of all components."""
        health_status = {
            'orchestrator': 'healthy' if self._running else 'unhealthy',
            'state_manager': 'healthy',
            'message_bus': 'healthy' if self.message_bus._running else 'unhealthy',
            'task_planner': 'healthy',
            'agent_manager': 'healthy',
            'resource_allocator': 'healthy'
        }
        
        # Add context manager health if available
        if self.context_manager:
            health_status['context_manager'] = 'healthy'
        
        return health_status
    
    # State Management Implementation
    
    async def create_checkpoint(self, name: Optional[str] = None) -> UUID:
        """Create a system checkpoint."""
        try:
            checkpoint = await self.state_manager.create_checkpoint(
                CheckpointType.SYSTEM_STATE,
                name=name or f"manual-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
            )
            return checkpoint.id
        except Exception as e:
            self.logger.log_error(e, {'operation': 'create_checkpoint'})
            raise OrchestrationError(f"Failed to create checkpoint: {str(e)}")
    
    async def restore_checkpoint(self, checkpoint_id: UUID) -> bool:
        """Restore system state from checkpoint."""
        try:
            # Get checkpoint
            checkpoint = await self.state_manager.get_object('checkpoints', checkpoint_id)
            if not checkpoint:
                return False
            
            # Create snapshot from checkpoint data
            snapshot = await self.state_manager.create_snapshot(
                name=f"restore-{checkpoint.name}",
                metadata={'restored_from': str(checkpoint_id)}
            )
            snapshot.state_data = checkpoint.state_data
            
            # Restore from snapshot
            return await self.state_manager.restore_from_snapshot(snapshot.id)
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'restore_checkpoint',
                'checkpoint_id': str(checkpoint_id)
            })
            return False
    
    async def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List available checkpoints."""
        checkpoints = await self.state_manager.get_objects('checkpoints')
        
        return [
            {
                'id': str(checkpoint.id),
                'name': checkpoint.name,
                'type': checkpoint.type.value,
                'created_at': checkpoint.created_at.isoformat(),
                'size_bytes': checkpoint.size_bytes
            }
            for checkpoint in sorted(checkpoints, key=lambda c: c.created_at, reverse=True)
        ]
    
    # Event Handlers
    
    async def _on_task_completed(self, task_id: UUID, result: Any, execution_time: float) -> None:
        """Handle task completion event."""
        self._metrics['tasks_completed'] += 1
        
        # Update task state
        task = await self.get_task(task_id)
        if task:
            task.result = result
            task.update_status(TaskStatus.COMPLETED)
            await self.state_manager.store_object('tasks', task)
        
        self.logger.log_task_event(
            "completed",
            str(task_id),
            execution_time=execution_time
        )
    
    async def _on_task_failed(self, task_id: UUID, error: str, execution_time: float) -> None:
        """Handle task failure event."""
        self._metrics['tasks_failed'] += 1
        
        # Update task state
        task = await self.get_task(task_id)
        if task:
            task.error = error
            task.update_status(TaskStatus.FAILED)
            await self.state_manager.store_object('tasks', task)
        
        self.logger.log_task_event(
            "failed",
            str(task_id),
            error=error,
            execution_time=execution_time
        )
    
    async def _on_task_state_changed(self, category: str, action: str, new_obj: Any, old_obj: Any) -> None:
        """Handle task state changes."""
        if action == 'updated' and new_obj and hasattr(new_obj, 'status'):
            self.logger.log_task_event(
                f"status_changed_to_{new_obj.status.value}",
                str(new_obj.id)
            )
    
    async def _on_agent_state_changed(self, category: str, action: str, new_obj: Any, old_obj: Any) -> None:
        """Handle agent state changes."""
        if action == 'updated' and new_obj and hasattr(new_obj, 'status'):
            self.logger.log_agent_event(
                f"status_changed_to_{new_obj.status.value}",
                str(new_obj.id)
            )
    
    async def _create_startup_checkpoint(self) -> None:
        """Create checkpoint at system startup."""
        try:
            await self.create_checkpoint("startup")
        except Exception as e:
            self.logger.log_error(e, {'operation': 'create_startup_checkpoint'})
    
    async def _create_shutdown_checkpoint(self) -> None:
        """Create checkpoint before system shutdown."""
        try:
            await self.create_checkpoint("shutdown")
        except Exception as e:
            self.logger.log_error(e, {'operation': 'create_shutdown_checkpoint'})