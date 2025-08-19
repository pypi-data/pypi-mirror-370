"""
Swarm Coordination Mechanism for MAOS.

This module provides advanced coordination patterns for multiple Claude agents
working together on complex, distributed tasks.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass, field
import json

from ..models.task import Task, TaskStatus, TaskPriority
from ..models.agent import Agent, AgentStatus, AgentCapability
from ..models.message import Message, MessageType, MessagePriority
from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError


class SwarmPattern(Enum):
    """Coordination patterns for agent swarms."""
    HUB_AND_SPOKE = "hub_and_spoke"      # Central coordinator with worker agents
    PIPELINE = "pipeline"                  # Sequential processing chain
    PARALLEL = "parallel"                  # Independent parallel execution
    MAP_REDUCE = "map_reduce"             # Map tasks, reduce results
    HIERARCHICAL = "hierarchical"         # Multi-level delegation
    CONSENSUS = "consensus"               # Voting-based decisions
    MESH = "mesh"                         # Peer-to-peer coordination
    DYNAMIC = "dynamic"                   # Self-organizing swarm


class CoordinationStrategy(Enum):
    """Strategies for coordinating agent work."""
    ROUND_ROBIN = "round_robin"           # Distribute tasks evenly
    LOAD_BALANCED = "load_balanced"       # Based on agent load
    CAPABILITY_BASED = "capability_based" # Match tasks to capabilities
    PRIORITY_BASED = "priority_based"     # High priority first
    ADAPTIVE = "adaptive"                 # Learn optimal distribution
    AUCTION = "auction"                   # Agents bid for tasks


@dataclass
class SwarmTask:
    """Represents a task within a swarm operation."""
    id: UUID = field(default_factory=uuid4)
    parent_task_id: Optional[UUID] = None
    task: Task = None
    assigned_agents: List[UUID] = field(default_factory=list)
    dependencies: List[UUID] = field(default_factory=list)  # Other task IDs
    status: TaskStatus = TaskStatus.PENDING
    results: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    coordination_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SwarmConfiguration:
    """Configuration for a swarm operation."""
    pattern: SwarmPattern = SwarmPattern.HUB_AND_SPOKE
    strategy: CoordinationStrategy = CoordinationStrategy.CAPABILITY_BASED
    min_agents: int = 1
    max_agents: int = 10
    agent_templates: List[str] = field(default_factory=list)
    timeout_seconds: int = 3600
    checkpoint_interval: int = 300
    enable_consensus: bool = False
    consensus_threshold: float = 0.66  # 2/3 majority
    enable_redundancy: bool = False
    redundancy_factor: int = 2
    enable_recovery: bool = True
    max_retries: int = 3


@dataclass
class SwarmMetrics:
    """Metrics for swarm operations."""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    active_agents: int = 0
    total_agents_spawned: int = 0
    average_task_time: float = 0.0
    coordination_overhead: float = 0.0
    success_rate: float = 0.0
    throughput: float = 0.0  # Tasks per second


class SwarmCoordinator:
    """
    Coordinates swarms of Claude agents for complex distributed tasks.
    
    Features:
    - Multiple coordination patterns (hub-spoke, pipeline, map-reduce)
    - Dynamic agent spawning and management
    - Task dependency resolution
    - Consensus mechanisms for critical decisions
    - Fault tolerance and recovery
    - Performance optimization
    """
    
    def __init__(
        self,
        agent_manager,
        orchestrator,
        message_bus,
        context_manager=None,
        enable_monitoring: bool = True
    ):
        """
        Initialize the Swarm Coordinator.
        
        Args:
            agent_manager: Agent manager instance
            orchestrator: Orchestrator instance
            message_bus: Message bus for communication
            context_manager: Optional context manager for checkpointing
            enable_monitoring: Enable performance monitoring
        """
        self.agent_manager = agent_manager
        self.orchestrator = orchestrator
        self.message_bus = message_bus
        self.context_manager = context_manager
        self.enable_monitoring = enable_monitoring
        
        # Swarm tracking
        self._active_swarms: Dict[UUID, Dict[str, Any]] = {}
        self._swarm_tasks: Dict[UUID, List[SwarmTask]] = {}
        self._agent_assignments: Dict[UUID, UUID] = {}  # agent_id -> swarm_id
        
        # Coordination state
        self._task_queue: asyncio.Queue = asyncio.Queue()
        self._result_aggregator: Dict[UUID, List[Any]] = {}
        self._consensus_votes: Dict[str, Dict[UUID, Any]] = {}
        
        # Background tasks
        self._coordinator_task: Optional[asyncio.Task] = None
        self._monitor_task: Optional[asyncio.Task] = None
        
        # Metrics
        self._swarm_metrics: Dict[UUID, SwarmMetrics] = {}
        
        # Logging
        self.logger = MAOSLogger("swarm_coordinator", str(uuid4()))
    
    async def create_swarm(
        self,
        name: str,
        configuration: SwarmConfiguration,
        initial_task: Optional[Task] = None
    ) -> UUID:
        """
        Create a new agent swarm.
        
        Args:
            name: Name of the swarm
            configuration: Swarm configuration
            initial_task: Optional initial task
            
        Returns:
            Swarm ID
        """
        swarm_id = uuid4()
        
        try:
            # Initialize swarm state
            swarm = {
                'id': swarm_id,
                'name': name,
                'configuration': configuration,
                'status': 'initializing',
                'agents': [],
                'created_at': datetime.utcnow(),
                'pattern_handler': self._get_pattern_handler(configuration.pattern)
            }
            
            self._active_swarms[swarm_id] = swarm
            self._swarm_tasks[swarm_id] = []
            self._swarm_metrics[swarm_id] = SwarmMetrics()
            
            # Spawn initial agents based on configuration
            initial_agents = await self._spawn_initial_agents(swarm_id, configuration)
            swarm['agents'] = initial_agents
            swarm['status'] = 'active'
            
            # Submit initial task if provided
            if initial_task:
                await self.submit_swarm_task(swarm_id, initial_task)
            
            self.logger.logger.info(
                f"Created swarm: {name}",
                extra={
                    'swarm_id': str(swarm_id),
                    'pattern': configuration.pattern.value,
                    'agent_count': len(initial_agents)
                }
            )
            
            return swarm_id
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'create_swarm',
                'swarm_name': name
            })
            raise MAOSError(f"Failed to create swarm: {str(e)}")
    
    async def submit_swarm_task(
        self,
        swarm_id: UUID,
        task: Task,
        dependencies: Optional[List[UUID]] = None
    ) -> SwarmTask:
        """
        Submit a task to a swarm for execution.
        
        Args:
            swarm_id: ID of the swarm
            task: Task to execute
            dependencies: Optional task dependencies
            
        Returns:
            SwarmTask object
        """
        if swarm_id not in self._active_swarms:
            raise MAOSError(f"Swarm not found: {swarm_id}")
        
        swarm = self._active_swarms[swarm_id]
        configuration = swarm['configuration']
        
        # Create swarm task
        swarm_task = SwarmTask(
            task=task,
            dependencies=dependencies or [],
            coordination_metadata={
                'pattern': configuration.pattern.value,
                'strategy': configuration.strategy.value
            }
        )
        
        self._swarm_tasks[swarm_id].append(swarm_task)
        
        # Update metrics
        metrics = self._swarm_metrics[swarm_id]
        metrics.total_tasks += 1
        
        # Route task based on pattern
        pattern_handler = swarm['pattern_handler']
        await pattern_handler(swarm_id, swarm_task)
        
        self.logger.logger.info(
            f"Submitted task to swarm",
            extra={
                'swarm_id': str(swarm_id),
                'task_id': str(swarm_task.id),
                'task_name': task.name
            }
        )
        
        return swarm_task
    
    async def coordinate_parallel_execution(
        self,
        swarm_id: UUID,
        tasks: List[Task],
        max_parallel: int = 5
    ) -> Dict[str, Any]:
        """
        Coordinate parallel execution of multiple tasks.
        
        Args:
            swarm_id: Swarm ID
            tasks: List of tasks to execute
            max_parallel: Maximum parallel executions
            
        Returns:
            Aggregated results
        """
        swarm = self._active_swarms.get(swarm_id)
        if not swarm:
            raise MAOSError(f"Swarm not found: {swarm_id}")
        
        results = {
            'successful': [],
            'failed': [],
            'total_time': 0.0
        }
        
        start_time = time.time()
        
        # Create swarm tasks
        swarm_tasks = []
        for task in tasks:
            swarm_task = await self.submit_swarm_task(swarm_id, task)
            swarm_tasks.append(swarm_task)
        
        # Execute in parallel with semaphore
        semaphore = asyncio.Semaphore(max_parallel)
        
        async def execute_with_limit(swarm_task: SwarmTask):
            async with semaphore:
                return await self._execute_swarm_task(swarm_id, swarm_task)
        
        # Execute all tasks
        execution_results = await asyncio.gather(
            *[execute_with_limit(st) for st in swarm_tasks],
            return_exceptions=True
        )
        
        # Process results
        for i, result in enumerate(execution_results):
            if isinstance(result, Exception):
                results['failed'].append({
                    'task_id': str(swarm_tasks[i].id),
                    'error': str(result)
                })
            else:
                results['successful'].append({
                    'task_id': str(swarm_tasks[i].id),
                    'result': result
                })
        
        results['total_time'] = time.time() - start_time
        results['success_rate'] = len(results['successful']) / len(tasks) if tasks else 0.0
        
        # Update metrics
        metrics = self._swarm_metrics[swarm_id]
        metrics.completed_tasks += len(results['successful'])
        metrics.failed_tasks += len(results['failed'])
        metrics.success_rate = results['success_rate']
        
        return results
    
    async def coordinate_pipeline_execution(
        self,
        swarm_id: UUID,
        tasks: List[Task],
        agent_sequence: Optional[List[str]] = None
    ) -> Any:
        """
        Coordinate pipeline execution where output of one task feeds into the next.
        
        Args:
            swarm_id: Swarm ID
            tasks: Ordered list of tasks
            agent_sequence: Optional sequence of agent templates
            
        Returns:
            Final pipeline result
        """
        swarm = self._active_swarms.get(swarm_id)
        if not swarm:
            raise MAOSError(f"Swarm not found: {swarm_id}")
        
        result = None
        previous_output = None
        
        for i, task in enumerate(tasks):
            # Add previous output to task context
            if previous_output is not None:
                task.metadata['previous_output'] = previous_output
            
            # Select agent for this stage
            if agent_sequence and i < len(agent_sequence):
                agent_template = agent_sequence[i]
                # Spawn specialized agent if needed
                agent = await self._ensure_agent_with_template(
                    swarm_id,
                    agent_template
                )
                assigned_agent = agent.id
            else:
                # Use round-robin assignment
                assigned_agent = swarm['agents'][i % len(swarm['agents'])]
            
            # Execute task
            swarm_task = SwarmTask(
                task=task,
                assigned_agents=[assigned_agent]
            )
            
            result = await self._execute_swarm_task(swarm_id, swarm_task)
            previous_output = result
            
            self.logger.logger.debug(
                f"Pipeline stage {i+1}/{len(tasks)} completed",
                extra={
                    'swarm_id': str(swarm_id),
                    'task_name': task.name,
                    'agent_id': str(assigned_agent)
                }
            )
        
        return result
    
    async def coordinate_map_reduce(
        self,
        swarm_id: UUID,
        map_task: Task,
        reduce_task: Task,
        data_chunks: List[Any]
    ) -> Any:
        """
        Coordinate map-reduce pattern execution.
        
        Args:
            swarm_id: Swarm ID
            map_task: Task to map across data
            reduce_task: Task to reduce results
            data_chunks: Data to process
            
        Returns:
            Reduced result
        """
        swarm = self._active_swarms.get(swarm_id)
        if not swarm:
            raise MAOSError(f"Swarm not found: {swarm_id}")
        
        # Map phase - create tasks for each chunk
        map_tasks = []
        for chunk in data_chunks:
            chunk_task = Task(
                name=f"{map_task.name}_chunk_{len(map_tasks)}",
                description=map_task.description,
                priority=map_task.priority,
                metadata={
                    **map_task.metadata,
                    'data_chunk': chunk,
                    'phase': 'map'
                }
            )
            map_tasks.append(chunk_task)
        
        # Execute map tasks in parallel
        map_results = await self.coordinate_parallel_execution(
            swarm_id,
            map_tasks,
            max_parallel=len(swarm['agents'])
        )
        
        # Collect successful results
        mapped_data = []
        for result in map_results['successful']:
            mapped_data.append(result['result'])
        
        # Reduce phase
        reduce_task.metadata['mapped_data'] = mapped_data
        reduce_task.metadata['phase'] = 'reduce'
        
        reduce_swarm_task = await self.submit_swarm_task(swarm_id, reduce_task)
        reduced_result = await self._execute_swarm_task(swarm_id, reduce_swarm_task)
        
        return reduced_result
    
    async def coordinate_with_consensus(
        self,
        swarm_id: UUID,
        task: Task,
        min_agents: int = 3
    ) -> Dict[str, Any]:
        """
        Coordinate task execution with consensus mechanism.
        
        Args:
            swarm_id: Swarm ID
            task: Task requiring consensus
            min_agents: Minimum agents for consensus
            
        Returns:
            Consensus result
        """
        swarm = self._active_swarms.get(swarm_id)
        if not swarm:
            raise MAOSError(f"Swarm not found: {swarm_id}")
        
        configuration = swarm['configuration']
        
        # Ensure we have enough agents
        while len(swarm['agents']) < min_agents:
            new_agent = await self._spawn_agent_for_swarm(swarm_id)
            swarm['agents'].append(new_agent.id)
        
        # Submit task to multiple agents
        consensus_id = str(uuid4())
        self._consensus_votes[consensus_id] = {}
        
        # Execute task with multiple agents
        agent_tasks = []
        for agent_id in swarm['agents'][:min_agents]:
            swarm_task = SwarmTask(
                task=task,
                assigned_agents=[agent_id],
                coordination_metadata={
                    'consensus_id': consensus_id,
                    'consensus_required': True
                }
            )
            agent_tasks.append(swarm_task)
        
        # Gather results
        results = await asyncio.gather(
            *[self._execute_swarm_task(swarm_id, st) for st in agent_tasks],
            return_exceptions=True
        )
        
        # Analyze consensus
        valid_results = [r for r in results if not isinstance(r, Exception)]
        
        if len(valid_results) < min_agents * configuration.consensus_threshold:
            return {
                'consensus_reached': False,
                'reason': 'Insufficient valid responses',
                'results': results
            }
        
        # Find majority agreement (simplified - could be more sophisticated)
        result_hashes = {}
        for result in valid_results:
            result_str = json.dumps(result, sort_keys=True, default=str)
            result_hash = hash(result_str)
            
            if result_hash not in result_hashes:
                result_hashes[result_hash] = []
            result_hashes[result_hash].append(result)
        
        # Find majority
        for result_hash, matching_results in result_hashes.items():
            if len(matching_results) >= len(valid_results) * configuration.consensus_threshold:
                return {
                    'consensus_reached': True,
                    'consensus_result': matching_results[0],
                    'agreement_ratio': len(matching_results) / len(valid_results),
                    'all_results': results
                }
        
        return {
            'consensus_reached': False,
            'reason': 'No majority agreement',
            'results': results
        }
    
    async def execute_hierarchical_task(
        self,
        swarm_id: UUID,
        root_task: Task,
        decomposition_strategy: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Execute task using hierarchical decomposition.
        
        Args:
            swarm_id: Swarm ID
            root_task: Root task to decompose
            decomposition_strategy: Optional custom decomposition
            
        Returns:
            Hierarchical execution results
        """
        swarm = self._active_swarms.get(swarm_id)
        if not swarm:
            raise MAOSError(f"Swarm not found: {swarm_id}")
        
        # Default decomposition if not provided
        if not decomposition_strategy:
            decomposition_strategy = self._default_task_decomposition
        
        # Decompose task
        subtasks = await decomposition_strategy(root_task)
        
        # Create task hierarchy
        hierarchy = {
            'root': root_task,
            'levels': [],
            'results': {}
        }
        
        # Execute level by level
        current_level = subtasks
        level_num = 0
        
        while current_level:
            level_num += 1
            hierarchy['levels'].append(current_level)
            
            # Execute current level in parallel
            level_results = await self.coordinate_parallel_execution(
                swarm_id,
                current_level
            )
            
            hierarchy['results'][f'level_{level_num}'] = level_results
            
            # Check if we need to go deeper
            next_level = []
            for task in current_level:
                if task.metadata.get('requires_decomposition'):
                    subtasks = await decomposition_strategy(task)
                    next_level.extend(subtasks)
            
            current_level = next_level
        
        return hierarchy
    
    async def get_swarm_status(self, swarm_id: UUID) -> Dict[str, Any]:
        """Get detailed status of a swarm."""
        if swarm_id not in self._active_swarms:
            return None
        
        swarm = self._active_swarms[swarm_id]
        metrics = self._swarm_metrics.get(swarm_id, SwarmMetrics())
        
        # Get agent statuses
        agent_statuses = []
        for agent_id in swarm['agents']:
            agent = self.agent_manager.get_agent(agent_id)
            if agent:
                agent_statuses.append({
                    'id': str(agent_id),
                    'status': agent.status.value,
                    'capabilities': [cap.value for cap in agent.capabilities]
                })
        
        # Get task statuses
        task_statuses = {}
        for status in TaskStatus:
            count = sum(
                1 for task in self._swarm_tasks.get(swarm_id, [])
                if task.status == status
            )
            task_statuses[status.value] = count
        
        return {
            'id': str(swarm_id),
            'name': swarm['name'],
            'status': swarm['status'],
            'pattern': swarm['configuration'].pattern.value,
            'strategy': swarm['configuration'].strategy.value,
            'created_at': swarm['created_at'].isoformat(),
            'agents': agent_statuses,
            'task_statuses': task_statuses,
            'metrics': {
                'total_tasks': metrics.total_tasks,
                'completed_tasks': metrics.completed_tasks,
                'failed_tasks': metrics.failed_tasks,
                'success_rate': metrics.success_rate,
                'active_agents': len(agent_statuses)
            }
        }
    
    async def shutdown_swarm(self, swarm_id: UUID) -> None:
        """Shutdown a swarm and cleanup resources."""
        if swarm_id not in self._active_swarms:
            return
        
        swarm = self._active_swarms[swarm_id]
        
        # Create final checkpoint if context manager available
        if self.context_manager:
            for agent_id in swarm['agents']:
                await self.orchestrator.create_context_checkpoint(
                    agent_id=agent_id,
                    checkpoint_name=f"swarm_{swarm['name']}_final_{int(time.time())}",
                    description=f"Final checkpoint for swarm {swarm['name']}"
                )
        
        # Clean up state
        del self._active_swarms[swarm_id]
        del self._swarm_tasks[swarm_id]
        del self._swarm_metrics[swarm_id]
        
        # Remove agent assignments
        self._agent_assignments = {
            k: v for k, v in self._agent_assignments.items()
            if v != swarm_id
        }
        
        self.logger.logger.info(
            f"Swarm shutdown complete",
            extra={'swarm_id': str(swarm_id)}
        )
    
    # Private helper methods
    
    async def _spawn_initial_agents(
        self,
        swarm_id: UUID,
        configuration: SwarmConfiguration
    ) -> List[UUID]:
        """Spawn initial agents for a swarm."""
        agents = []
        
        # Spawn minimum required agents
        for i in range(configuration.min_agents):
            # Use template if specified
            if i < len(configuration.agent_templates):
                template = configuration.agent_templates[i]
            else:
                template = "web-developer"  # Default template
            
            agent = await self._spawn_agent_for_swarm(swarm_id, template)
            agents.append(agent.id)
        
        return agents
    
    async def _spawn_agent_for_swarm(
        self,
        swarm_id: UUID,
        template: str = "web-developer"
    ) -> Agent:
        """Spawn a new agent for a swarm."""
        agent = await self.orchestrator.spawn_specialized_claude_agent(
            template_name=template,
            agent_name=f"swarm_{swarm_id}_agent_{int(time.time())}"
        )
        
        self._agent_assignments[agent.id] = swarm_id
        
        metrics = self._swarm_metrics[swarm_id]
        metrics.total_agents_spawned += 1
        metrics.active_agents += 1
        
        return agent
    
    async def _ensure_agent_with_template(
        self,
        swarm_id: UUID,
        template: str
    ) -> Agent:
        """Ensure swarm has an agent with specific template."""
        swarm = self._active_swarms[swarm_id]
        
        # Check existing agents
        for agent_id in swarm['agents']:
            agent = self.agent_manager.get_agent(agent_id)
            if agent and agent.metadata.get('template') == template:
                return agent
        
        # Spawn new agent with template
        return await self._spawn_agent_for_swarm(swarm_id, template)
    
    async def _execute_swarm_task(
        self,
        swarm_id: UUID,
        swarm_task: SwarmTask
    ) -> Any:
        """Execute a single swarm task."""
        swarm_task.started_at = datetime.utcnow()
        swarm_task.status = TaskStatus.IN_PROGRESS
        
        try:
            # Select agent if not assigned
            if not swarm_task.assigned_agents:
                swarm = self._active_swarms[swarm_id]
                strategy = swarm['configuration'].strategy
                agent_id = await self._select_agent(swarm_id, swarm_task, strategy)
                swarm_task.assigned_agents = [agent_id]
            else:
                agent_id = swarm_task.assigned_agents[0]
            
            # Execute task
            result = await self.orchestrator.submit_task_to_claude_agent(
                task=swarm_task.task,
                agent_id=agent_id
            )
            
            swarm_task.status = TaskStatus.COMPLETED
            swarm_task.completed_at = datetime.utcnow()
            swarm_task.results = result
            
            # Update metrics
            metrics = self._swarm_metrics[swarm_id]
            task_time = (swarm_task.completed_at - swarm_task.started_at).total_seconds()
            metrics.average_task_time = (
                (metrics.average_task_time * metrics.completed_tasks + task_time) /
                (metrics.completed_tasks + 1)
            )
            
            return result
            
        except Exception as e:
            swarm_task.status = TaskStatus.FAILED
            swarm_task.completed_at = datetime.utcnow()
            swarm_task.results = {'error': str(e)}
            
            self.logger.log_error(e, {
                'swarm_id': str(swarm_id),
                'task_id': str(swarm_task.id)
            })
            
            raise
    
    async def _select_agent(
        self,
        swarm_id: UUID,
        swarm_task: SwarmTask,
        strategy: CoordinationStrategy
    ) -> UUID:
        """Select an agent based on strategy."""
        swarm = self._active_swarms[swarm_id]
        agents = swarm['agents']
        
        if not agents:
            raise MAOSError("No agents available in swarm")
        
        if strategy == CoordinationStrategy.ROUND_ROBIN:
            # Simple round-robin
            index = swarm.get('next_agent_index', 0)
            swarm['next_agent_index'] = (index + 1) % len(agents)
            return agents[index]
            
        elif strategy == CoordinationStrategy.CAPABILITY_BASED:
            # Match task requirements to agent capabilities
            required_capabilities = swarm_task.task.metadata.get('required_capabilities', [])
            
            for agent_id in agents:
                agent = self.agent_manager.get_agent(agent_id)
                if agent and all(cap in agent.capabilities for cap in required_capabilities):
                    return agent_id
            
            # Fallback to first agent
            return agents[0]
            
        else:
            # Default to first agent
            return agents[0]
    
    def _get_pattern_handler(self, pattern: SwarmPattern) -> Callable:
        """Get the handler function for a coordination pattern."""
        handlers = {
            SwarmPattern.HUB_AND_SPOKE: self._handle_hub_and_spoke,
            SwarmPattern.PIPELINE: self._handle_pipeline,
            SwarmPattern.PARALLEL: self._handle_parallel,
            SwarmPattern.MAP_REDUCE: self._handle_map_reduce,
            SwarmPattern.HIERARCHICAL: self._handle_hierarchical,
            SwarmPattern.CONSENSUS: self._handle_consensus,
            SwarmPattern.MESH: self._handle_mesh,
            SwarmPattern.DYNAMIC: self._handle_dynamic
        }
        return handlers.get(pattern, self._handle_parallel)
    
    async def _handle_hub_and_spoke(
        self,
        swarm_id: UUID,
        swarm_task: SwarmTask
    ) -> None:
        """Handle hub-and-spoke coordination pattern."""
        # Central coordinator delegates to workers
        await self._task_queue.put((swarm_id, swarm_task))
    
    async def _handle_pipeline(
        self,
        swarm_id: UUID,
        swarm_task: SwarmTask
    ) -> None:
        """Handle pipeline coordination pattern."""
        # Add to pipeline queue
        await self._task_queue.put((swarm_id, swarm_task))
    
    async def _handle_parallel(
        self,
        swarm_id: UUID,
        swarm_task: SwarmTask
    ) -> None:
        """Handle parallel coordination pattern."""
        # Direct execution
        asyncio.create_task(self._execute_swarm_task(swarm_id, swarm_task))
    
    async def _handle_map_reduce(
        self,
        swarm_id: UUID,
        swarm_task: SwarmTask
    ) -> None:
        """Handle map-reduce coordination pattern."""
        # Add to appropriate phase queue
        await self._task_queue.put((swarm_id, swarm_task))
    
    async def _handle_hierarchical(
        self,
        swarm_id: UUID,
        swarm_task: SwarmTask
    ) -> None:
        """Handle hierarchical coordination pattern."""
        # Decompose and delegate
        await self._task_queue.put((swarm_id, swarm_task))
    
    async def _handle_consensus(
        self,
        swarm_id: UUID,
        swarm_task: SwarmTask
    ) -> None:
        """Handle consensus coordination pattern."""
        # Multiple agent execution for consensus
        await self._task_queue.put((swarm_id, swarm_task))
    
    async def _handle_mesh(
        self,
        swarm_id: UUID,
        swarm_task: SwarmTask
    ) -> None:
        """Handle mesh coordination pattern."""
        # Peer-to-peer coordination
        await self._task_queue.put((swarm_id, swarm_task))
    
    async def _handle_dynamic(
        self,
        swarm_id: UUID,
        swarm_task: SwarmTask
    ) -> None:
        """Handle dynamic coordination pattern."""
        # Self-organizing based on metrics
        await self._task_queue.put((swarm_id, swarm_task))
    
    async def _default_task_decomposition(self, task: Task) -> List[Task]:
        """Default task decomposition strategy."""
        # Simple decomposition - could be made more sophisticated
        subtasks = []
        
        # Example: Break down by steps in description
        if 'steps' in task.metadata:
            for i, step in enumerate(task.metadata['steps']):
                subtask = Task(
                    name=f"{task.name}_step_{i+1}",
                    description=step,
                    priority=task.priority,
                    metadata={
                        'parent_task': str(task.id),
                        'step_number': i+1
                    }
                )
                subtasks.append(subtask)
        
        return subtasks