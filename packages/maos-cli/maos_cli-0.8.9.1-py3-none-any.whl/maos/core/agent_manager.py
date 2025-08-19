"""
Agent Manager component for MAOS orchestration system.

This component is responsible for:
- Agent lifecycle management (spawn, monitor, terminate)
- Health monitoring and performance tracking
- Load balancing and resource allocation
- Fault detection and automatic recovery
- Real Claude Code CLI process management
"""

import asyncio
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple, Any, Callable
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum

from ..models.agent import Agent, AgentStatus, AgentCapability, AgentMetrics
from ..models.task import Task, TaskStatus
from ..models.message import Message, MessageType, MessagePriority
from ..models.claude_agent_process import ClaudeAgentProcess, AgentDefinition
from ..agents.templates import create_agent_from_template, get_available_templates
from .claude_cli_manager import ClaudeCodeCLIManager
from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import (
    AgentError, AgentNotFoundError, AgentNotAvailableError,
    AgentCapabilityError, AgentHealthError
)


class LoadBalancingStrategy(Enum):
    """Load balancing strategies for agent assignment."""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    CAPABILITY_BASED = "capability_based"
    PRIORITY_BASED = "priority_based"
    RANDOM = "random"


@dataclass
class AgentPool:
    """Represents a pool of agents with specific capabilities."""
    
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    capabilities: Set[AgentCapability] = field(default_factory=set)
    agents: Dict[UUID, Agent] = field(default_factory=dict)
    max_agents: int = 10
    min_agents: int = 1
    auto_scaling_enabled: bool = True
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_available_agents(self) -> List[Agent]:
        """Get list of available agents in the pool."""
        return [agent for agent in self.agents.values() if agent.is_available()]
    
    def get_total_capacity(self) -> int:
        """Get total task capacity across all agents."""
        return sum(agent.max_concurrent_tasks for agent in self.agents.values())
    
    def get_current_load(self) -> float:
        """Get current load factor for the pool (0.0 to 1.0)."""
        if not self.agents:
            return 0.0
        
        total_capacity = self.get_total_capacity()
        if total_capacity == 0:
            return 1.0
        
        current_tasks = sum(
            (1 if agent.current_task_id else 0) + len(agent.task_queue)
            for agent in self.agents.values()
        )
        
        return current_tasks / total_capacity


class AgentManager:
    """
    Agent Manager component for orchestrating agent lifecycle and operations.
    
    This component handles:
    - Agent creation, monitoring, and termination
    - Health checks and performance tracking
    - Load balancing and task assignment
    - Fault detection and recovery
    - Resource allocation and scaling
    """
    
    def __init__(
        self,
        max_agents: int = 50,
        health_check_interval: int = 30,
        heartbeat_timeout: int = 90,
        auto_recovery_enabled: bool = True,
        performance_monitoring_enabled: bool = True,
        claude_cli_path: str = "claude",
        claude_working_dir: str = "/tmp/maos_claude",
        enable_claude_integration: bool = True
    ):
        """Initialize the Agent Manager."""
        self.max_agents = max_agents
        self.health_check_interval = health_check_interval
        self.heartbeat_timeout = heartbeat_timeout
        self.auto_recovery_enabled = auto_recovery_enabled
        self.performance_monitoring_enabled = performance_monitoring_enabled
        self.enable_claude_integration = enable_claude_integration
        
        self.logger = MAOSLogger("agent_manager", str(uuid4()))
        
        # Claude Code integration
        if self.enable_claude_integration:
            self.claude_cli_manager = ClaudeCodeCLIManager(
                max_processes=max_agents,
                claude_cli_path=claude_cli_path,
                base_working_dir=claude_working_dir
            )
        else:
            self.claude_cli_manager = None
        
        # Internal state
        self._agents: Dict[UUID, Agent] = {}
        self._agent_pools: Dict[UUID, AgentPool] = {}
        self._task_assignments: Dict[UUID, UUID] = {}  # task_id -> agent_id
        self._agent_tasks: Dict[UUID, Set[UUID]] = defaultdict(set)  # agent_id -> task_ids
        
        # Claude agent processes
        self._claude_agents: Dict[UUID, ClaudeAgentProcess] = {}  # agent_id -> claude_process
        
        # Load balancing
        self._round_robin_counters: Dict[UUID, int] = {}  # pool_id -> counter
        
        # Health monitoring
        self._health_check_task: Optional[asyncio.Task] = None
        self._performance_monitor_task: Optional[asyncio.Task] = None
        
        # Recovery strategies
        self._recovery_strategies: Dict[str, Callable] = {}
        
        # Metrics
        self._metrics = {
            'agents_spawned': 0,
            'agents_terminated': 0,
            'tasks_assigned': 0,
            'health_checks_performed': 0,
            'recovery_actions_taken': 0,
            'average_response_time_ms': 0.0,
            'average_success_rate': 0.0,
            'claude_processes_spawned': 0,
            'claude_tasks_executed': 0
        }
        
        # Register default recovery strategies
        self._register_default_recovery_strategies()
    
    async def start(self) -> None:
        """Start the agent manager and background tasks."""
        self.logger.logger.info("Starting Agent Manager")
        
        # Start Claude CLI manager if enabled
        if self.claude_cli_manager:
            await self.claude_cli_manager.start()
            self.logger.logger.info("Claude CLI Manager started")
        
        # Start health monitoring
        if self.health_check_interval > 0:
            self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        # Start performance monitoring
        if self.performance_monitoring_enabled:
            self._performance_monitor_task = asyncio.create_task(self._performance_monitor_loop())
    
    async def stop(self) -> None:
        """Stop the agent manager and cleanup resources."""
        self.logger.logger.info("Stopping Agent Manager")
        
        # Cancel monitoring tasks
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        if self._performance_monitor_task:
            self._performance_monitor_task.cancel()
            try:
                await self._performance_monitor_task
            except asyncio.CancelledError:
                pass
        
        # Terminate all Claude agents
        for agent_id in list(self._claude_agents.keys()):
            try:
                await self.terminate_agent(agent_id, "Manager shutdown", force=True)
            except Exception as e:
                self.logger.log_error(e, {
                    'operation': 'shutdown_claude_agent',
                    'agent_id': str(agent_id)
                })
        
        # Stop Claude CLI manager
        if self.claude_cli_manager:
            await self.claude_cli_manager.stop()
            self.logger.logger.info("Claude CLI Manager stopped")
        
        self.logger.logger.info("Agent Manager stopped")
    
    async def spawn_claude_agent(
        self,
        template_name: str,
        agent_name: Optional[str] = None,
        pool_id: Optional[UUID] = None,
        configuration: Optional[Dict[str, Any]] = None,
        **template_params
    ) -> Agent:
        """
        Spawn a new Claude Code agent using a template.
        
        Args:
            template_name: Name of the agent template to use
            agent_name: Custom name for the agent
            pool_id: Pool to add agent to (optional)
            configuration: Agent-specific configuration
            **template_params: Additional parameters for template
            
        Returns:
            Agent: The newly spawned Claude agent
        """
        
        if not self.claude_cli_manager:
            raise AgentError("Claude integration not enabled")
        
        if len(self._agents) >= self.max_agents:
            raise AgentError(
                f"Maximum agent limit reached ({self.max_agents})",
                error_code="MAX_AGENTS_EXCEEDED"
            )
        
        try:
            # Create agent definition from template
            agent_definition = create_agent_from_template(
                template_name=template_name,
                agent_name=agent_name,
                **template_params
            )
            
            # Determine capabilities from template
            available_templates = get_available_templates()
            template_info = next(
                (t for t in available_templates if t["name"] == template_name),
                None
            )
            
            if not template_info:
                raise AgentError(f"Template '{template_name}' not found")
            
            capabilities = {AgentCapability(cap) for cap in template_info["capabilities"]}
            
            # Create MAOS agent
            agent = Agent(
                name=agent_definition.name,
                type=agent_definition.type,
                capabilities=capabilities,
                configuration=configuration or {},
                status=AgentStatus.INITIALIZING,
                started_at=datetime.utcnow()
            )
            
            # Add to internal registry
            self._agents[agent.id] = agent
            
            # Add to pool if specified
            if pool_id and pool_id in self._agent_pools:
                pool = self._agent_pools[pool_id]
                pool.agents[agent.id] = agent
            
            # Create Claude agent process
            claude_agent = ClaudeAgentProcess(
                cli_manager=self.claude_cli_manager,
                agent=agent,
                agent_definition=agent_definition,
                working_dir=None  # Use default working dir
            )
            
            # Initialize Claude agent
            await claude_agent.initialize()
            
            # Store Claude agent reference
            self._claude_agents[agent.id] = claude_agent
            
            # Update agent status
            agent.status = AgentStatus.IDLE
            agent.update_heartbeat()
            
            self._metrics['agents_spawned'] += 1
            self._metrics['claude_processes_spawned'] += 1
            
            self.logger.log_agent_event(
                "claude_agent_spawned",
                str(agent.id),
                agent_type=agent_definition.type,
                template_name=template_name,
                capabilities=[cap.value for cap in capabilities]
            )
            
            return agent
            
        except Exception as e:
            # Clean up on failure
            if agent.id in self._agents:
                del self._agents[agent.id]
            if agent.id in self._claude_agents:
                try:
                    await self._claude_agents[agent.id].terminate()
                except:
                    pass
                del self._claude_agents[agent.id]
            
            self.logger.log_error(e, {
                'operation': 'spawn_claude_agent',
                'template_name': template_name,
                'agent_name': agent_name
            })
            raise AgentError(f"Failed to spawn Claude agent: {str(e)}")

    async def spawn_agent(
        self,
        agent_type: str,
        capabilities: Set[AgentCapability],
        pool_id: Optional[UUID] = None,
        configuration: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """
        Spawn a new agent with specified capabilities.
        
        Args:
            agent_type: Type of agent to spawn
            capabilities: Set of agent capabilities
            pool_id: Pool to add agent to (optional)
            configuration: Agent-specific configuration
            
        Returns:
            Agent: The newly spawned agent
        """
        
        if len(self._agents) >= self.max_agents:
            raise AgentError(
                f"Maximum agent limit reached ({self.max_agents})",
                error_code="MAX_AGENTS_EXCEEDED"
            )
        
        try:
            # Create agent
            agent = Agent(
                name=f"{agent_type}-{len(self._agents) + 1}",
                type=agent_type,
                capabilities=capabilities,
                configuration=configuration or {},
                status=AgentStatus.INITIALIZING,
                started_at=datetime.utcnow()
            )
            
            # Add to internal registry
            self._agents[agent.id] = agent
            
            # Add to pool if specified
            if pool_id and pool_id in self._agent_pools:
                pool = self._agent_pools[pool_id]
                pool.agents[agent.id] = agent
            
            # Initialize agent (mark as idle once ready)
            await self._initialize_agent(agent)
            
            self._metrics['agents_spawned'] += 1
            
            self.logger.log_agent_event(
                "spawned",
                str(agent.id),
                agent_type=agent_type,
                capabilities=[cap.value for cap in capabilities]
            )
            
            return agent
        
        except Exception as e:
            self.logger.log_error(e, {'operation': 'spawn_agent', 'agent_type': agent_type})
            raise AgentError(f"Failed to spawn agent: {str(e)}")
    
    async def execute_task_with_claude_agent(
        self,
        agent_id: UUID,
        task: Task
    ) -> Dict[str, Any]:
        """
        Execute a task using a Claude Code agent.
        
        Args:
            agent_id: ID of the Claude agent to use
            task: Task to execute
            
        Returns:
            Task execution results
        """
        
        if agent_id not in self._agents:
            raise AgentNotFoundError(agent_id)
        
        if agent_id not in self._claude_agents:
            raise AgentError(f"Agent {agent_id} is not a Claude agent")
        
        agent = self._agents[agent_id]
        claude_agent = self._claude_agents[agent_id]
        
        if not agent.is_available():
            raise AgentNotAvailableError(agent_id)
        
        try:
            # Update task assignment
            self._task_assignments[task.id] = agent_id
            self._agent_tasks[agent_id].add(task.id)
            
            # Execute task using Claude agent
            results = await claude_agent.execute_task(task)
            
            # Update metrics
            self._metrics['tasks_assigned'] += 1
            self._metrics['claude_tasks_executed'] += 1
            
            self.logger.log_agent_event(
                "task_executed",
                str(agent_id),
                task_id=str(task.id),
                success=results.get("success", False)
            )
            
            return results
            
        except Exception as e:
            # Clean up task assignment
            if task.id in self._task_assignments:
                del self._task_assignments[task.id]
            if agent_id in self._agent_tasks:
                self._agent_tasks[agent_id].discard(task.id)
            
            self.logger.log_error(e, {
                'operation': 'execute_task_with_claude_agent',
                'agent_id': str(agent_id),
                'task_id': str(task.id)
            })
            
            raise TaskError(f"Task execution failed: {str(e)}")
        
        finally:
            # Clean up task assignment on completion
            if task.id in self._task_assignments:
                del self._task_assignments[task.id]
            if agent_id in self._agent_tasks:
                self._agent_tasks[agent_id].discard(task.id)
    
    def get_claude_agent_status(self, agent_id: UUID) -> Optional[Dict[str, Any]]:
        """Get detailed status of a Claude agent."""
        if agent_id not in self._claude_agents:
            return None
        
        claude_agent = self._claude_agents[agent_id]
        return claude_agent.get_status()
    
    def list_claude_agents(self) -> List[Dict[str, Any]]:
        """List all Claude agents with their status."""
        return [
            self.get_claude_agent_status(agent_id)
            for agent_id in self._claude_agents.keys()
        ]
    
    async def _initialize_agent(self, agent: Agent) -> None:
        """Initialize an agent and prepare it for work."""
        
        try:
            # Perform initialization tasks
            await asyncio.sleep(0.1)  # Simulate initialization time
            
            # Set agent as idle and ready for work
            agent.status = AgentStatus.IDLE
            agent.update_heartbeat()
            
            self.logger.log_agent_event("initialized", str(agent.id))
            
        except Exception as e:
            agent.status = AgentStatus.UNHEALTHY
            raise AgentError(
                f"Agent initialization failed: {str(e)}",
                agent_id=agent.id,
                error_code="AGENT_INIT_FAILED"
            )
    
    async def terminate_agent(
        self,
        agent_id: UUID,
        reason: str = "Manual termination",
        force: bool = False
    ) -> bool:
        """
        Terminate an agent.
        
        Args:
            agent_id: ID of agent to terminate
            reason: Reason for termination
            force: Whether to force termination even if agent has active tasks
            
        Returns:
            bool: True if agent was successfully terminated
        """
        
        if agent_id not in self._agents:
            raise AgentNotFoundError(agent_id)
        
        agent = self._agents[agent_id]
        
        try:
            # Check if agent has active tasks
            if not force and (agent.current_task_id or agent.task_queue):
                raise AgentError(
                    f"Agent has active tasks and force=False",
                    agent_id=agent_id,
                    error_code="AGENT_HAS_ACTIVE_TASKS"
                )
            
            # Reassign any active tasks if force termination
            if force:
                await self._reassign_agent_tasks(agent_id)
            
            # Terminate Claude agent if it exists
            if agent_id in self._claude_agents:
                claude_agent = self._claude_agents[agent_id]
                await claude_agent.terminate()
                del self._claude_agents[agent_id]
                self.logger.log_agent_event(
                    "claude_agent_terminated",
                    str(agent_id),
                    reason=reason
                )
            
            # Update agent status
            agent.status = AgentStatus.TERMINATED
            
            # Remove from pools
            for pool in self._agent_pools.values():
                if agent_id in pool.agents:
                    del pool.agents[agent_id]
            
            # Remove from internal registry
            del self._agents[agent_id]
            
            # Cleanup task assignments
            if agent_id in self._agent_tasks:
                del self._agent_tasks[agent_id]
            
            self._metrics['agents_terminated'] += 1
            
            self.logger.log_agent_event(
                "terminated",
                str(agent_id),
                reason=reason,
                force=force
            )
            
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'terminate_agent',
                'agent_id': str(agent_id)
            })
            return False
    
    async def assign_task(
        self,
        task: Task,
        preferred_agent_id: Optional[UUID] = None,
        required_capabilities: Optional[Set[AgentCapability]] = None
    ) -> UUID:
        """
        Assign a task to an available agent.
        
        Args:
            task: Task to assign
            preferred_agent_id: Preferred agent ID (optional)
            required_capabilities: Required capabilities (optional)
            
        Returns:
            UUID: ID of assigned agent
        """
        
        try:
            # Determine required capabilities
            if not required_capabilities:
                required_capabilities = {AgentCapability.TASK_EXECUTION}
            
            # Try preferred agent first
            if preferred_agent_id:
                agent = self._agents.get(preferred_agent_id)
                if agent and agent.can_handle_task(required_capabilities):
                    if agent.assign_task(task.id):
                        await self._record_task_assignment(task.id, agent.id)
                        return agent.id
            
            # Find suitable agent using load balancing
            agent = await self._find_suitable_agent(required_capabilities, task)
            
            if not agent:
                raise AgentNotAvailableError(
                    UUID('00000000-0000-0000-0000-000000000000'),  # Placeholder
                    "No suitable agents available"
                )
            
            # Assign task
            if not agent.assign_task(task.id):
                raise AgentError(
                    "Failed to assign task to agent",
                    agent_id=agent.id,
                    error_code="TASK_ASSIGNMENT_FAILED"
                )
            
            await self._record_task_assignment(task.id, agent.id)
            
            self._metrics['tasks_assigned'] += 1
            
            self.logger.log_agent_event(
                "task_assigned",
                str(agent.id),
                task_id=str(task.id),
                task_name=task.name
            )
            
            return agent.id
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'assign_task',
                'task_id': str(task.id)
            })
            raise
    
    async def _find_suitable_agent(
        self,
        required_capabilities: Set[AgentCapability],
        task: Task
    ) -> Optional[Agent]:
        """Find a suitable agent for the task using load balancing strategy."""
        
        # Get agents with required capabilities
        suitable_agents = [
            agent for agent in self._agents.values()
            if agent.can_handle_task(required_capabilities)
        ]
        
        if not suitable_agents:
            return None
        
        # Apply load balancing strategy (default to least loaded)
        strategy = LoadBalancingStrategy.LEAST_LOADED
        
        if strategy == LoadBalancingStrategy.LEAST_LOADED:
            # Select agent with lowest load factor
            return min(suitable_agents, key=lambda a: a.get_load_factor())
        
        elif strategy == LoadBalancingStrategy.PRIORITY_BASED:
            # Select based on task priority and agent availability
            if task.priority.value >= 3:  # High priority
                # Find idle agents first
                idle_agents = [a for a in suitable_agents if a.status == AgentStatus.IDLE]
                if idle_agents:
                    return min(idle_agents, key=lambda a: a.get_load_factor())
            
            return min(suitable_agents, key=lambda a: a.get_load_factor())
        
        elif strategy == LoadBalancingStrategy.ROUND_ROBIN:
            # Simple round-robin selection
            if suitable_agents:
                return suitable_agents[0]  # Simplified for now
        
        return suitable_agents[0] if suitable_agents else None
    
    async def _record_task_assignment(self, task_id: UUID, agent_id: UUID) -> None:
        """Record task assignment for tracking."""
        self._task_assignments[task_id] = agent_id
        self._agent_tasks[agent_id].add(task_id)
    
    async def complete_task(
        self,
        task_id: UUID,
        success: bool,
        execution_time: float,
        result: Any = None,
        error: Optional[str] = None
    ) -> None:
        """
        Mark a task as completed and update agent state.
        
        Args:
            task_id: ID of completed task
            success: Whether task completed successfully
            execution_time: Task execution time in seconds
            result: Task result (optional)
            error: Error message if task failed (optional)
        """
        
        agent_id = self._task_assignments.get(task_id)
        if not agent_id or agent_id not in self._agents:
            return
        
        agent = self._agents[agent_id]
        
        try:
            # Update agent state
            agent.complete_task(task_id, execution_time, success)
            
            # Clean up assignments
            if task_id in self._task_assignments:
                del self._task_assignments[task_id]
            
            if agent_id in self._agent_tasks:
                self._agent_tasks[agent_id].discard(task_id)
            
            self.logger.log_agent_event(
                "task_completed",
                str(agent_id),
                task_id=str(task_id),
                success=success,
                execution_time=execution_time
            )
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'complete_task',
                'task_id': str(task_id),
                'agent_id': str(agent_id)
            })
    
    async def create_agent_pool(
        self,
        name: str,
        capabilities: Set[AgentCapability],
        min_agents: int = 1,
        max_agents: int = 10,
        auto_scaling_enabled: bool = True
    ) -> AgentPool:
        """Create a new agent pool with specified capabilities."""
        
        pool = AgentPool(
            name=name,
            capabilities=capabilities,
            min_agents=min_agents,
            max_agents=max_agents,
            auto_scaling_enabled=auto_scaling_enabled
        )
        
        self._agent_pools[pool.id] = pool
        self._round_robin_counters[pool.id] = 0
        
        # Create minimum number of agents for the pool
        for i in range(min_agents):
            agent = await self.spawn_agent(
                agent_type=f"{name.lower()}_agent",
                capabilities=capabilities,
                pool_id=pool.id
            )
        
        self.logger.logger.info(
            f"Agent pool created: {name}",
            extra={
                'pool_id': str(pool.id),
                'capabilities': [cap.value for cap in capabilities],
                'min_agents': min_agents,
                'max_agents': max_agents
            }
        )
        
        return pool
    
    async def _health_check_loop(self) -> None:
        """Background task for performing health checks."""
        
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'health_check_loop'})
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on all agents."""
        
        unhealthy_agents = []
        
        for agent in self._agents.values():
            try:
                # Check heartbeat
                if not agent.is_healthy():
                    unhealthy_agents.append(agent.id)
                    continue
                
                # Update system metrics if monitoring is enabled
                if self.performance_monitoring_enabled:
                    cpu_usage = psutil.cpu_percent(interval=0.1)
                    memory_info = psutil.virtual_memory()
                    agent.update_heartbeat(cpu_usage, memory_info.used / 1024 / 1024)
                
            except Exception as e:
                self.logger.log_error(e, {
                    'operation': 'health_check',
                    'agent_id': str(agent.id)
                })
                unhealthy_agents.append(agent.id)
        
        # Handle unhealthy agents
        if unhealthy_agents and self.auto_recovery_enabled:
            await self._handle_unhealthy_agents(unhealthy_agents)
        
        self._metrics['health_checks_performed'] += 1
    
    async def _handle_unhealthy_agents(self, unhealthy_agent_ids: List[UUID]) -> None:
        """Handle unhealthy agents with recovery strategies."""
        
        for agent_id in unhealthy_agent_ids:
            if agent_id not in self._agents:
                continue
            
            agent = self._agents[agent_id]
            
            try:
                # Apply recovery strategy based on agent status
                if agent.status == AgentStatus.UNHEALTHY:
                    await self._recover_unhealthy_agent(agent)
                elif agent.status == AgentStatus.OFFLINE:
                    await self._recover_offline_agent(agent)
                
            except Exception as e:
                self.logger.log_error(e, {
                    'operation': 'handle_unhealthy_agent',
                    'agent_id': str(agent_id)
                })
    
    async def _recover_unhealthy_agent(self, agent: Agent) -> None:
        """Recover an unhealthy agent."""
        
        self.logger.log_agent_event("recovery_started", str(agent.id), reason="unhealthy")
        
        # Try to restart the agent
        try:
            # Reassign active tasks
            await self._reassign_agent_tasks(agent.id)
            
            # Reset agent state
            agent.status = AgentStatus.INITIALIZING
            agent.current_task_id = None
            agent.task_queue.clear()
            
            # Reinitialize agent
            await self._initialize_agent(agent)
            
            self._metrics['recovery_actions_taken'] += 1
            self.logger.log_agent_event("recovery_completed", str(agent.id))
            
        except Exception as e:
            # If recovery fails, terminate the agent
            self.logger.log_agent_event("recovery_failed", str(agent.id), error=str(e))
            await self.terminate_agent(agent.id, "Recovery failed", force=True)
    
    async def _recover_offline_agent(self, agent: Agent) -> None:
        """Recover an offline agent."""
        
        self.logger.log_agent_event("recovery_started", str(agent.id), reason="offline")
        
        # For offline agents, terminate and potentially spawn replacement
        await self.terminate_agent(agent.id, "Agent offline", force=True)
        
        # Check if we need to spawn replacement in any pools
        for pool in self._agent_pools.values():
            if len(pool.agents) < pool.min_agents:
                await self.spawn_agent(
                    agent_type=f"{pool.name.lower()}_agent",
                    capabilities=pool.capabilities,
                    pool_id=pool.id
                )
    
    async def _reassign_agent_tasks(self, agent_id: UUID) -> None:
        """Reassign tasks from a failed agent to other agents."""
        
        if agent_id not in self._agent_tasks:
            return
        
        task_ids = self._agent_tasks[agent_id].copy()
        
        for task_id in task_ids:
            try:
                # Create a placeholder task for reassignment
                # In production, this would fetch the actual task from task store
                task = Task(
                    id=task_id,
                    name="Reassigned Task",
                    status=TaskStatus.PENDING
                )
                
                # Try to assign to another agent
                new_agent_id = await self.assign_task(task)
                
                self.logger.log_agent_event(
                    "task_reassigned",
                    str(new_agent_id),
                    original_agent_id=str(agent_id),
                    task_id=str(task_id)
                )
                
            except Exception as e:
                self.logger.log_error(e, {
                    'operation': 'reassign_task',
                    'task_id': str(task_id),
                    'failed_agent_id': str(agent_id)
                })
    
    async def _performance_monitor_loop(self) -> None:
        """Background task for monitoring performance metrics."""
        
        while True:
            try:
                await asyncio.sleep(60)  # Monitor every minute
                await self._update_performance_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'performance_monitor_loop'})
    
    async def _update_performance_metrics(self) -> None:
        """Update aggregated performance metrics."""
        
        if not self._agents:
            return
        
        # Calculate average success rate
        success_rates = [agent.metrics.success_rate for agent in self._agents.values()]
        self._metrics['average_success_rate'] = sum(success_rates) / len(success_rates)
        
        # Calculate average execution time
        execution_times = [
            agent.metrics.average_execution_time 
            for agent in self._agents.values() 
            if agent.metrics.average_execution_time > 0
        ]
        
        if execution_times:
            self._metrics['average_response_time_ms'] = (
                sum(execution_times) / len(execution_times) * 1000
            )
    
    def _register_default_recovery_strategies(self) -> None:
        """Register default agent recovery strategies."""
        
        self._recovery_strategies.update({
            'restart': self._recover_unhealthy_agent,
            'terminate': self._recover_offline_agent,
            'reassign_tasks': self._reassign_agent_tasks
        })
    
    def get_agent(self, agent_id: UUID) -> Optional[Agent]:
        """Get an agent by ID."""
        return self._agents.get(agent_id)
    
    def get_all_agents(self) -> List[Agent]:
        """Get all agents."""
        return list(self._agents.values())
    
    def get_available_agents(self) -> List[Agent]:
        """Get all available agents."""
        return [agent for agent in self._agents.values() if agent.is_available()]
    
    def get_agent_pool(self, pool_id: UUID) -> Optional[AgentPool]:
        """Get an agent pool by ID."""
        return self._agent_pools.get(pool_id)
    
    def get_all_pools(self) -> List[AgentPool]:
        """Get all agent pools."""
        return list(self._agent_pools.values())
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent manager metrics."""
        metrics = self._metrics.copy()
        metrics.update({
            'total_agents': len(self._agents),
            'available_agents': len(self.get_available_agents()),
            'total_pools': len(self._agent_pools),
            'active_assignments': len(self._task_assignments)
        })
        return metrics
    
    async def shutdown(self) -> None:
        """Shutdown the agent manager and cleanup resources."""
        
        self.logger.logger.info("Agent manager shutting down")
        
        # Cancel background tasks
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        if self._performance_monitor_task:
            self._performance_monitor_task.cancel()
            try:
                await self._performance_monitor_task
            except asyncio.CancelledError:
                pass
        
        # Terminate all agents
        agent_ids = list(self._agents.keys())
        for agent_id in agent_ids:
            await self.terminate_agent(agent_id, "System shutdown", force=True)
        
        # Clear state
        self._agents.clear()
        self._agent_pools.clear()
        self._task_assignments.clear()
        self._agent_tasks.clear()