# MAOS Code Architecture and Design Patterns

## Overview

This document provides an in-depth look at MAOS code architecture, design patterns, and implementation details. It serves as a guide for developers to understand the codebase structure and maintain consistency across contributions.

## Architectural Principles

### 1. Separation of Concerns

MAOS follows a layered architecture with clear separation between different concerns:

```python
# Clean separation example
class TaskOrchestrator:
    """Orchestrates task execution without knowing implementation details."""
    
    def __init__(
        self,
        task_planner: TaskPlanner,
        agent_manager: AgentManager,
        resource_allocator: ResourceAllocator,
        state_manager: StateManager
    ):
        self.task_planner = task_planner
        self.agent_manager = agent_manager
        self.resource_allocator = resource_allocator
        self.state_manager = state_manager
    
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute task using composed services."""
        # Planning (what to do)
        execution_plan = await self.task_planner.create_plan(task)
        
        # Resource allocation (what resources needed)
        resources = await self.resource_allocator.allocate(execution_plan)
        
        # Agent management (who will do it)
        agents = await self.agent_manager.assign_agents(execution_plan, resources)
        
        # State coordination (how to coordinate)
        coordination_context = await self.state_manager.create_context(execution_plan)
        
        # Execution
        return await self._execute_with_coordination(
            execution_plan, agents, coordination_context
        )
```

### 2. Dependency Inversion

High-level modules depend on abstractions, not concrete implementations:

```python
# Abstract interface
class AgentInterface(ABC):
    """Abstract interface for all agent implementations."""
    
    @abstractmethod
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute a task and return the result."""
        pass
    
    @abstractmethod
    async def get_capabilities(self) -> List[str]:
        """Return agent capabilities."""
        pass

# High-level orchestrator depends on abstraction
class TaskExecutor:
    def __init__(self, agents: List[AgentInterface]):
        self.agents = agents  # Depends on interface, not implementation
    
    async def execute_with_best_agent(self, task: Task) -> TaskResult:
        """Select and execute task with most suitable agent."""
        best_agent = await self._select_best_agent(task)
        return await best_agent.execute_task(task)

# Concrete implementations
class ResearcherAgent(AgentInterface):
    async def execute_task(self, task: Task) -> TaskResult:
        # Research-specific implementation
        pass

class CoderAgent(AgentInterface):
    async def execute_task(self, task: Task) -> TaskResult:
        # Coding-specific implementation
        pass
```

### 3. Single Responsibility Principle

Each class has a single, well-defined responsibility:

```python
# Good: Single responsibility
class TaskDecomposer:
    """Responsible only for decomposing tasks into subtasks."""
    
    def __init__(self, strategies: List[DecompositionStrategy]):
        self.strategies = strategies
    
    async def decompose(self, task: Task) -> List[Task]:
        """Decompose task using available strategies."""
        for strategy in self.strategies:
            if await strategy.can_handle(task):
                return await strategy.decompose(task)
        
        raise DecompositionError(f"No strategy found for task type: {task.type}")

class TaskScheduler:
    """Responsible only for scheduling task execution."""
    
    def __init__(self, priority_algorithm: PriorityAlgorithm):
        self.priority_algorithm = priority_algorithm
        self.task_queue = PriorityQueue()
    
    async def schedule(self, tasks: List[Task]) -> None:
        """Schedule tasks for execution."""
        for task in tasks:
            priority = await self.priority_algorithm.calculate_priority(task)
            await self.task_queue.put((priority, task))

# Avoid: Multiple responsibilities in one class
class TaskManager:
    """AVOID: Too many responsibilities."""
    
    async def decompose_task(self, task: Task) -> List[Task]:
        pass  # Decomposition responsibility
    
    async def schedule_tasks(self, tasks: List[Task]) -> None:
        pass  # Scheduling responsibility
    
    async def execute_task(self, task: Task) -> TaskResult:
        pass  # Execution responsibility
    
    async def store_result(self, result: TaskResult) -> None:
        pass  # Storage responsibility
```

### 4. Open/Closed Principle

Software entities are open for extension but closed for modification:

```python
# Base strategy that's closed for modification
class DecompositionStrategy(ABC):
    """Base strategy for task decomposition."""
    
    @abstractmethod
    async def can_handle(self, task: Task) -> bool:
        """Check if strategy can handle the task."""
        pass
    
    @abstractmethod
    async def decompose(self, task: Task) -> List[Task]:
        """Decompose task into subtasks."""
        pass

# Extended strategies without modifying base
class ResearchDecompositionStrategy(DecompositionStrategy):
    """Strategy for decomposing research tasks."""
    
    async def can_handle(self, task: Task) -> bool:
        return task.type == TaskType.RESEARCH
    
    async def decompose(self, task: Task) -> List[Task]:
        """Decompose research task into parallel research streams."""
        research_aspects = await self._identify_research_aspects(task)
        
        subtasks = []
        for aspect in research_aspects:
            subtask = Task(
                description=f"Research {aspect} for {task.description}",
                type=TaskType.RESEARCH,
                parent_id=task.id
            )
            subtasks.append(subtask)
        
        return subtasks

class CodingDecompositionStrategy(DecompositionStrategy):
    """Strategy for decomposing coding tasks."""
    
    async def can_handle(self, task: Task) -> bool:
        return task.type == TaskType.CODING
    
    async def decompose(self, task: Task) -> List[Task]:
        """Decompose coding task into development phases."""
        phases = ["design", "implementation", "testing", "documentation"]
        
        subtasks = []
        for phase in phases:
            subtask = Task(
                description=f"{phase.title()} phase for {task.description}",
                type=TaskType.CODING,
                parent_id=task.id,
                metadata={"phase": phase}
            )
            subtasks.append(subtask)
        
        return subtasks
```

## Core Design Patterns

### 1. Strategy Pattern

Used extensively for pluggable algorithms and behaviors:

```python
# Strategy interface
class LoadBalancingStrategy(ABC):
    """Interface for agent load balancing strategies."""
    
    @abstractmethod
    async def select_agent(self, agents: List[Agent], task: Task) -> Agent:
        """Select the best agent for the task."""
        pass

# Concrete strategies
class RoundRobinStrategy(LoadBalancingStrategy):
    def __init__(self):
        self._current_index = 0
    
    async def select_agent(self, agents: List[Agent], task: Task) -> Agent:
        """Select agent using round-robin algorithm."""
        if not agents:
            raise NoAgentsAvailableError()
        
        selected = agents[self._current_index % len(agents)]
        self._current_index += 1
        return selected

class WeightedStrategy(LoadBalancingStrategy):
    async def select_agent(self, agents: List[Agent], task: Task) -> Agent:
        """Select agent based on performance weights."""
        if not agents:
            raise NoAgentsAvailableError()
        
        # Calculate weights based on agent performance
        weights = [await self._calculate_weight(agent, task) for agent in agents]
        
        # Weighted random selection
        selected_agent = random.choices(agents, weights=weights, k=1)[0]
        return selected_agent
    
    async def _calculate_weight(self, agent: Agent, task: Task) -> float:
        """Calculate agent weight based on performance metrics."""
        performance = await agent.get_performance_metrics()
        
        # Weight based on success rate and average completion time
        success_weight = performance.success_rate * 100
        speed_weight = max(0, 100 - performance.avg_completion_time)
        
        return (success_weight + speed_weight) / 2

# Context using strategy
class AgentSelector:
    def __init__(self, strategy: LoadBalancingStrategy):
        self.strategy = strategy
    
    async def select_agent(self, agents: List[Agent], task: Task) -> Agent:
        """Select agent using configured strategy."""
        return await self.strategy.select_agent(agents, task)
    
    def set_strategy(self, strategy: LoadBalancingStrategy):
        """Change load balancing strategy at runtime."""
        self.strategy = strategy
```

### 2. Observer Pattern

Used for event-driven communication and monitoring:

```python
# Observer interface
class TaskObserver(ABC):
    """Interface for observing task events."""
    
    @abstractmethod
    async def on_task_started(self, task: Task) -> None:
        """Called when a task starts."""
        pass
    
    @abstractmethod
    async def on_task_completed(self, task: Task, result: TaskResult) -> None:
        """Called when a task completes."""
        pass
    
    @abstractmethod
    async def on_task_failed(self, task: Task, error: Exception) -> None:
        """Called when a task fails."""
        pass

# Concrete observers
class MetricsCollector(TaskObserver):
    """Collects task execution metrics."""
    
    def __init__(self):
        self.metrics = defaultdict(list)
    
    async def on_task_started(self, task: Task) -> None:
        """Record task start metrics."""
        self.metrics['started_tasks'].append({
            'task_id': task.id,
            'timestamp': time.time(),
            'task_type': task.type
        })
    
    async def on_task_completed(self, task: Task, result: TaskResult) -> None:
        """Record task completion metrics."""
        execution_time = result.completed_at - result.started_at
        
        self.metrics['completed_tasks'].append({
            'task_id': task.id,
            'execution_time': execution_time,
            'success': result.success,
            'agents_used': len(result.agents_used)
        })

class AlertingService(TaskObserver):
    """Sends alerts for task events."""
    
    def __init__(self, alert_client: AlertClient):
        self.alert_client = alert_client
    
    async def on_task_failed(self, task: Task, error: Exception) -> None:
        """Send alert for failed tasks."""
        if task.priority == TaskPriority.CRITICAL:
            await self.alert_client.send_critical_alert(
                title=f"Critical task failed: {task.id}",
                description=f"Task '{task.description}' failed with error: {error}",
                task_id=task.id
            )

# Subject that manages observers
class TaskExecutionSubject:
    """Subject that notifies observers about task events."""
    
    def __init__(self):
        self._observers: List[TaskObserver] = []
    
    def attach(self, observer: TaskObserver) -> None:
        """Attach an observer."""
        self._observers.append(observer)
    
    def detach(self, observer: TaskObserver) -> None:
        """Detach an observer."""
        self._observers.remove(observer)
    
    async def notify_task_started(self, task: Task) -> None:
        """Notify observers that a task started."""
        await asyncio.gather(
            *[observer.on_task_started(task) for observer in self._observers],
            return_exceptions=True
        )
    
    async def notify_task_completed(self, task: Task, result: TaskResult) -> None:
        """Notify observers that a task completed."""
        await asyncio.gather(
            *[observer.on_task_completed(task, result) for observer in self._observers],
            return_exceptions=True
        )
    
    async def notify_task_failed(self, task: Task, error: Exception) -> None:
        """Notify observers that a task failed."""
        await asyncio.gather(
            *[observer.on_task_failed(task, error) for observer in self._observers],
            return_exceptions=True
        )
```

### 3. Command Pattern

Used for task execution and undo/redo operations:

```python
# Command interface
class Command(ABC):
    """Interface for executable commands."""
    
    @abstractmethod
    async def execute(self) -> Any:
        """Execute the command."""
        pass
    
    @abstractmethod
    async def undo(self) -> None:
        """Undo the command if possible."""
        pass
    
    @abstractmethod
    def can_undo(self) -> bool:
        """Check if command can be undone."""
        pass

# Concrete commands
class SpawnAgentCommand(Command):
    """Command to spawn a new agent."""
    
    def __init__(self, agent_manager: AgentManager, agent_type: str, config: Dict):
        self.agent_manager = agent_manager
        self.agent_type = agent_type
        self.config = config
        self.spawned_agent: Optional[Agent] = None
    
    async def execute(self) -> Agent:
        """Spawn the agent."""
        self.spawned_agent = await self.agent_manager.spawn_agent(
            self.agent_type, **self.config
        )
        return self.spawned_agent
    
    async def undo(self) -> None:
        """Terminate the spawned agent."""
        if self.spawned_agent:
            await self.agent_manager.terminate_agent(self.spawned_agent.id)
            self.spawned_agent = None
    
    def can_undo(self) -> bool:
        """Can undo if agent was spawned and is still active."""
        return (self.spawned_agent is not None and 
                self.spawned_agent.status != AgentStatus.TERMINATED)

class ExecuteTaskCommand(Command):
    """Command to execute a task."""
    
    def __init__(self, task_executor: TaskExecutor, task: Task):
        self.task_executor = task_executor
        self.task = task
        self.execution_result: Optional[TaskResult] = None
    
    async def execute(self) -> TaskResult:
        """Execute the task."""
        self.execution_result = await self.task_executor.execute(self.task)
        return self.execution_result
    
    async def undo(self) -> None:
        """Cancel the task if still running."""
        if self.task.status == TaskStatus.RUNNING:
            await self.task_executor.cancel_task(self.task.id)
    
    def can_undo(self) -> bool:
        """Can undo if task is still running."""
        return self.task.status == TaskStatus.RUNNING

# Command invoker
class CommandInvoker:
    """Invokes commands and maintains command history."""
    
    def __init__(self):
        self.command_history: List[Command] = []
        self.current_position = -1
    
    async def execute_command(self, command: Command) -> Any:
        """Execute a command and add to history."""
        result = await command.execute()
        
        # Remove any commands after current position (for redo)
        self.command_history = self.command_history[:self.current_position + 1]
        
        # Add new command
        self.command_history.append(command)
        self.current_position += 1
        
        return result
    
    async def undo(self) -> bool:
        """Undo the last command."""
        if self.current_position >= 0:
            command = self.command_history[self.current_position]
            if command.can_undo():
                await command.undo()
                self.current_position -= 1
                return True
        return False
    
    async def redo(self) -> bool:
        """Redo the next command."""
        if self.current_position < len(self.command_history) - 1:
            self.current_position += 1
            command = self.command_history[self.current_position]
            await command.execute()
            return True
        return False
```

### 4. Factory Pattern

Used for creating agents and tasks with different configurations:

```python
# Abstract factory
class AgentFactory(ABC):
    """Abstract factory for creating agents."""
    
    @abstractmethod
    async def create_agent(self, config: AgentConfig) -> Agent:
        """Create an agent with the given configuration."""
        pass
    
    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """Get list of agent types this factory supports."""
        pass

# Concrete factories
class ResearcherAgentFactory(AgentFactory):
    """Factory for creating researcher agents."""
    
    async def create_agent(self, config: AgentConfig) -> Agent:
        """Create a researcher agent."""
        # Validate configuration
        if config.agent_type != "researcher":
            raise ValueError(f"Expected researcher config, got {config.agent_type}")
        
        # Create base agent
        agent = Agent(
            id=self._generate_agent_id(),
            type=AgentType.RESEARCHER,
            capabilities=config.capabilities or ["web_search", "data_analysis"],
            resources=config.resources
        )
        
        # Initialize researcher-specific components
        agent.search_engine = await self._create_search_engine(config)
        agent.analysis_tools = await self._create_analysis_tools(config)
        
        return agent
    
    def get_supported_types(self) -> List[str]:
        """Return supported agent types."""
        return ["researcher"]
    
    async def _create_search_engine(self, config: AgentConfig):
        """Create search engine component."""
        # Implementation details
        pass

class CoderAgentFactory(AgentFactory):
    """Factory for creating coder agents."""
    
    async def create_agent(self, config: AgentConfig) -> Agent:
        """Create a coder agent."""
        if config.agent_type != "coder":
            raise ValueError(f"Expected coder config, got {config.agent_type}")
        
        agent = Agent(
            id=self._generate_agent_id(),
            type=AgentType.CODER,
            capabilities=config.capabilities or ["code_generation", "testing", "debugging"],
            resources=config.resources
        )
        
        # Initialize coder-specific components
        agent.code_generator = await self._create_code_generator(config)
        agent.test_runner = await self._create_test_runner(config)
        
        return agent
    
    def get_supported_types(self) -> List[str]:
        """Return supported agent types."""
        return ["coder"]

# Factory registry
class AgentFactoryRegistry:
    """Registry for managing agent factories."""
    
    def __init__(self):
        self._factories: Dict[str, AgentFactory] = {}
    
    def register_factory(self, factory: AgentFactory) -> None:
        """Register an agent factory."""
        for agent_type in factory.get_supported_types():
            self._factories[agent_type] = factory
    
    async def create_agent(self, agent_type: str, config: AgentConfig) -> Agent:
        """Create an agent using the appropriate factory."""
        if agent_type not in self._factories:
            raise UnsupportedAgentTypeError(f"No factory for agent type: {agent_type}")
        
        factory = self._factories[agent_type]
        return await factory.create_agent(config)
    
    def get_supported_types(self) -> List[str]:
        """Get all supported agent types."""
        return list(self._factories.keys())

# Usage example
registry = AgentFactoryRegistry()
registry.register_factory(ResearcherAgentFactory())
registry.register_factory(CoderAgentFactory())

# Create agents using registry
researcher_config = AgentConfig(agent_type="researcher", capabilities=["web_search"])
researcher = await registry.create_agent("researcher", researcher_config)

coder_config = AgentConfig(agent_type="coder", capabilities=["python", "testing"])
coder = await registry.create_agent("coder", coder_config)
```

### 5. Decorator Pattern

Used for adding cross-cutting concerns like logging, caching, and metrics:

```python
# Base component
class TaskExecutor(ABC):
    """Base interface for task execution."""
    
    @abstractmethod
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute a task."""
        pass

# Concrete component
class BasicTaskExecutor(TaskExecutor):
    """Basic task executor implementation."""
    
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute task with basic logic."""
        # Basic execution logic
        return TaskResult(
            task_id=task.id,
            success=True,
            result="Task completed successfully"
        )

# Decorators
class LoggingTaskExecutor(TaskExecutor):
    """Decorator that adds logging to task execution."""
    
    def __init__(self, executor: TaskExecutor):
        self.executor = executor
        self.logger = logging.getLogger(__name__)
    
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute task with logging."""
        self.logger.info(f"Starting execution of task {task.id}: {task.description}")
        
        start_time = time.time()
        try:
            result = await self.executor.execute_task(task)
            execution_time = time.time() - start_time
            
            self.logger.info(
                f"Task {task.id} completed successfully in {execution_time:.2f}s"
            )
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"Task {task.id} failed after {execution_time:.2f}s: {e}"
            )
            raise

class CachingTaskExecutor(TaskExecutor):
    """Decorator that adds caching to task execution."""
    
    def __init__(self, executor: TaskExecutor, cache_ttl: int = 3600):
        self.executor = executor
        self.cache: Dict[str, Tuple[TaskResult, float]] = {}
        self.cache_ttl = cache_ttl
    
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute task with caching."""
        cache_key = self._get_cache_key(task)
        
        # Check cache
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_result
        
        # Execute and cache
        result = await self.executor.execute_task(task)
        self.cache[cache_key] = (result, time.time())
        
        return result
    
    def _get_cache_key(self, task: Task) -> str:
        """Generate cache key for task."""
        return f"{task.type}:{hash(task.description)}"

class MetricsTaskExecutor(TaskExecutor):
    """Decorator that collects metrics for task execution."""
    
    def __init__(self, executor: TaskExecutor, metrics_collector: MetricsCollector):
        self.executor = executor
        self.metrics_collector = metrics_collector
    
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute task with metrics collection."""
        start_time = time.time()
        
        # Record start metrics
        self.metrics_collector.increment_counter('tasks_started', {
            'task_type': task.type,
            'priority': task.priority.value
        })
        
        try:
            result = await self.executor.execute_task(task)
            execution_time = time.time() - start_time
            
            # Record success metrics
            self.metrics_collector.increment_counter('tasks_completed', {
                'task_type': task.type,
                'status': 'success'
            })
            self.metrics_collector.record_histogram('task_execution_time', 
                                                   execution_time, {
                'task_type': task.type
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Record failure metrics
            self.metrics_collector.increment_counter('tasks_completed', {
                'task_type': task.type,
                'status': 'failure'
            })
            self.metrics_collector.record_histogram('task_execution_time', 
                                                   execution_time, {
                'task_type': task.type
            })
            
            raise

# Usage: Stack decorators
base_executor = BasicTaskExecutor()
logged_executor = LoggingTaskExecutor(base_executor)
cached_executor = CachingTaskExecutor(logged_executor)
metrics_executor = MetricsTaskExecutor(cached_executor, metrics_collector)

# All decorators are applied when executing
result = await metrics_executor.execute_task(task)
```

## Async Programming Patterns

### 1. Async Context Managers

Used for resource management and cleanup:

```python
class AgentSession:
    """Async context manager for agent sessions."""
    
    def __init__(self, agent_manager: AgentManager, agent_type: str):
        self.agent_manager = agent_manager
        self.agent_type = agent_type
        self.agent: Optional[Agent] = None
    
    async def __aenter__(self) -> Agent:
        """Enter context - spawn agent."""
        self.agent = await self.agent_manager.spawn_agent(self.agent_type)
        await self.agent.initialize()
        return self.agent
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context - cleanup agent."""
        if self.agent:
            try:
                await self.agent.cleanup()
                await self.agent_manager.terminate_agent(self.agent.id)
            except Exception as e:
                logger.error(f"Error cleaning up agent {self.agent.id}: {e}")

# Usage
async def execute_research_task(task: Task) -> TaskResult:
    """Execute research task with managed agent session."""
    async with AgentSession(agent_manager, "researcher") as agent:
        return await agent.execute_task(task)
```

### 2. Async Generators for Streaming

Used for real-time progress updates and result streaming:

```python
class TaskProgressStreamer:
    """Streams task progress updates in real-time."""
    
    def __init__(self, task_executor: TaskExecutor):
        self.task_executor = task_executor
    
    async def stream_task_progress(self, task: Task) -> AsyncIterator[TaskProgress]:
        """Stream task progress updates."""
        
        # Initial progress
        yield TaskProgress(
            task_id=task.id,
            status=TaskStatus.STARTING,
            progress_percent=0.0,
            message="Task starting..."
        )
        
        # Start task execution in background
        execution_task = asyncio.create_task(
            self.task_executor.execute_task(task)
        )
        
        # Stream progress while task is running
        progress = 0.0
        while not execution_task.done():
            await asyncio.sleep(1)  # Update interval
            
            # Get current progress from task
            current_progress = await self._get_task_progress(task.id)
            
            if current_progress > progress:
                progress = current_progress
                yield TaskProgress(
                    task_id=task.id,
                    status=TaskStatus.RUNNING,
                    progress_percent=progress,
                    message=f"Task {progress:.1f}% complete"
                )
        
        # Final progress
        try:
            result = await execution_task
            yield TaskProgress(
                task_id=task.id,
                status=TaskStatus.COMPLETED,
                progress_percent=100.0,
                message="Task completed successfully",
                result=result
            )
        except Exception as e:
            yield TaskProgress(
                task_id=task.id,
                status=TaskStatus.FAILED,
                progress_percent=progress,
                message=f"Task failed: {e}"
            )
    
    async def _get_task_progress(self, task_id: str) -> float:
        """Get current progress for a task."""
        # Implementation to get actual progress
        pass

# Usage
async def monitor_task_execution(task: Task):
    """Monitor task execution with real-time updates."""
    streamer = TaskProgressStreamer(task_executor)
    
    async for progress in streamer.stream_task_progress(task):
        print(f"Task {progress.task_id}: {progress.message}")
        
        if progress.status == TaskStatus.COMPLETED:
            print(f"Task completed with result: {progress.result}")
            break
        elif progress.status == TaskStatus.FAILED:
            print(f"Task failed: {progress.message}")
            break
```

### 3. Task Groups for Concurrent Execution

Used for managing multiple concurrent operations:

```python
class ConcurrentTaskExecutor:
    """Executes multiple tasks concurrently with proper error handling."""
    
    async def execute_tasks_concurrently(
        self, 
        tasks: List[Task],
        max_concurrency: int = 10
    ) -> List[TaskResult]:
        """Execute tasks concurrently with limited concurrency."""
        
        semaphore = asyncio.Semaphore(max_concurrency)
        results = []
        
        async def execute_single_task(task: Task) -> TaskResult:
            """Execute a single task with semaphore control."""
            async with semaphore:
                return await self._execute_task_with_retry(task)
        
        # Use TaskGroup for proper exception handling
        async with asyncio.TaskGroup() as tg:
            task_handles = [
                tg.create_task(execute_single_task(task), name=f"task_{task.id}")
                for task in tasks
            ]
        
        # Collect results
        for handle in task_handles:
            try:
                results.append(handle.result())
            except Exception as e:
                # Handle individual task failures
                results.append(TaskResult.failed(str(e)))
        
        return results
    
    async def _execute_task_with_retry(
        self, 
        task: Task, 
        max_retries: int = 3
    ) -> TaskResult:
        """Execute task with retry logic."""
        
        for attempt in range(max_retries + 1):
            try:
                return await self.task_executor.execute_task(task)
            
            except RetryableError as e:
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise
            
            except Exception as e:
                # Non-retryable error
                raise
```

## Error Handling Patterns

### 1. Exception Hierarchy

Well-defined exception hierarchy for different error types:

```python
# Base exception
class MAOSException(Exception):
    """Base exception for all MAOS errors."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        super().__init__(message)

# Category exceptions
class AgentError(MAOSException):
    """Base class for agent-related errors."""
    pass

class TaskError(MAOSException):
    """Base class for task-related errors."""
    pass

class ResourceError(MAOSException):
    """Base class for resource-related errors."""
    pass

# Specific exceptions
class AgentSpawnError(AgentError):
    """Raised when agent spawning fails."""
    
    def __init__(self, agent_type: str, reason: str, details: Optional[Dict] = None):
        self.agent_type = agent_type
        self.reason = reason
        message = f"Failed to spawn {agent_type} agent: {reason}"
        super().__init__(message, details)

class TaskTimeoutError(TaskError):
    """Raised when task execution times out."""
    
    def __init__(self, task_id: str, timeout: float, details: Optional[Dict] = None):
        self.task_id = task_id
        self.timeout = timeout
        message = f"Task {task_id} timed out after {timeout} seconds"
        super().__init__(message, details)

class ResourceExhaustionError(ResourceError):
    """Raised when system resources are exhausted."""
    
    def __init__(self, resource_type: str, available: float, requested: float):
        self.resource_type = resource_type
        self.available = available
        self.requested = requested
        message = f"Insufficient {resource_type}: {available} available, {requested} requested"
        super().__init__(message)

# Retryable vs non-retryable errors
class RetryableError(MAOSException):
    """Base class for errors that should be retried."""
    pass

class NonRetryableError(MAOSException):
    """Base class for errors that should not be retried."""
    pass

class TemporaryResourceError(RetryableError):
    """Temporary resource unavailability."""
    pass

class InvalidConfigurationError(NonRetryableError):
    """Invalid configuration that cannot be retried."""
    pass
```

### 2. Error Recovery Strategies

Implement different recovery strategies based on error types:

```python
class ErrorRecoveryManager:
    """Manages error recovery strategies."""
    
    def __init__(self):
        self.recovery_strategies = {
            AgentSpawnError: self._recover_agent_spawn_error,
            TaskTimeoutError: self._recover_task_timeout_error,
            ResourceExhaustionError: self._recover_resource_exhaustion_error,
        }
    
    async def handle_error(self, error: Exception, context: Dict) -> bool:
        """Handle error with appropriate recovery strategy."""
        
        error_type = type(error)
        
        # Find recovery strategy
        for exception_type, strategy in self.recovery_strategies.items():
            if issubclass(error_type, exception_type):
                try:
                    return await strategy(error, context)
                except Exception as recovery_error:
                    logger.error(f"Recovery failed: {recovery_error}")
                    return False
        
        # No recovery strategy found
        logger.warning(f"No recovery strategy for error type: {error_type}")
        return False
    
    async def _recover_agent_spawn_error(
        self, 
        error: AgentSpawnError, 
        context: Dict
    ) -> bool:
        """Recover from agent spawn error."""
        
        # Try spawning different agent type
        if error.reason == "insufficient_memory":
            # Try with lower memory requirements
            reduced_config = context['agent_config'].copy()
            reduced_config['memory_limit'] = min(
                reduced_config.get('memory_limit', 1024), 512
            )
            
            try:
                agent = await context['agent_manager'].spawn_agent(
                    error.agent_type, reduced_config
                )
                context['recovered_agent'] = agent
                return True
            except Exception:
                pass
        
        # Try spawning on different node
        if hasattr(context.get('agent_manager'), 'spawn_on_different_node'):
            try:
                agent = await context['agent_manager'].spawn_on_different_node(
                    error.agent_type, context['agent_config']
                )
                context['recovered_agent'] = agent
                return True
            except Exception:
                pass
        
        return False
    
    async def _recover_task_timeout_error(
        self, 
        error: TaskTimeoutError, 
        context: Dict
    ) -> bool:
        """Recover from task timeout error."""
        
        task = context.get('task')
        if not task:
            return False
        
        # Try breaking task into smaller chunks
        if task.complexity > 5:
            try:
                subtasks = await context['task_planner'].decompose_task(task)
                context['recovery_subtasks'] = subtasks
                return True
            except Exception:
                pass
        
        # Try with more agents
        if task.max_agents < 8:
            task.max_agents = min(task.max_agents * 2, 8)
            context['modified_task'] = task
            return True
        
        return False
    
    async def _recover_resource_exhaustion_error(
        self, 
        error: ResourceExhaustionError, 
        context: Dict
    ) -> bool:
        """Recover from resource exhaustion error."""
        
        # Wait for resources to become available
        if error.resource_type in ['memory', 'cpu']:
            await asyncio.sleep(30)  # Wait 30 seconds
            
            # Check if resources are now available
            current_resources = await context['resource_monitor'].get_available_resources()
            if current_resources.get(error.resource_type, 0) >= error.requested:
                return True
        
        # Scale down other operations to free resources
        if error.resource_type == 'memory':
            freed = await context['resource_manager'].free_memory(error.requested)
            return freed >= error.requested
        
        return False
```

## Configuration and Dependency Injection

### 1. Configuration Management

Centralized configuration with validation and type safety:

```python
@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    echo: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.pool_size < 1:
            raise ValueError("pool_size must be at least 1")
        if self.max_overflow < 0:
            raise ValueError("max_overflow cannot be negative")

@dataclass
class RedisConfig:
    """Redis configuration."""
    url: str
    max_connections: int = 100
    retry_on_timeout: bool = True
    health_check_interval: int = 30
    
    def __post_init__(self):
        """Validate configuration."""
        if self.max_connections < 1:
            raise ValueError("max_connections must be at least 1")

@dataclass
class SystemConfig:
    """System-level configuration."""
    max_agents: int = 20
    checkpoint_interval: int = 30
    log_level: str = "INFO"
    environment: str = "development"
    
    def __post_init__(self):
        """Validate configuration."""
        if self.max_agents < 1:
            raise ValueError("max_agents must be at least 1")
        if self.checkpoint_interval < 1:
            raise ValueError("checkpoint_interval must be at least 1")
        
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ValueError(f"log_level must be one of: {valid_log_levels}")

@dataclass
class MAOSConfig:
    """Main MAOS configuration."""
    system: SystemConfig
    database: DatabaseConfig
    redis: RedisConfig
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'MAOSConfig':
        """Create configuration from dictionary."""
        return cls(
            system=SystemConfig(**config_dict.get('system', {})),
            database=DatabaseConfig(**config_dict['database']),
            redis=RedisConfig(**config_dict['redis'])
        )
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'MAOSConfig':
        """Load configuration from file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            if config_path.suffix.lower() == '.yaml':
                config_dict = yaml.safe_load(f)
            elif config_path.suffix.lower() == '.json':
                config_dict = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration format: {config_path.suffix}")
        
        return cls.from_dict(config_dict)
```

### 2. Dependency Injection

Simple dependency injection container for managing dependencies:

```python
class DIContainer:
    """Simple dependency injection container."""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register_singleton(self, service_type: Type, instance: Any) -> None:
        """Register a singleton instance."""
        self._singletons[service_type] = instance
    
    def register_factory(self, service_type: Type, factory: Callable) -> None:
        """Register a factory function for creating instances."""
        self._factories[service_type] = factory
    
    def register_type(self, service_type: Type, implementation_type: Type) -> None:
        """Register a type mapping."""
        self._services[service_type] = implementation_type
    
    def get(self, service_type: Type) -> Any:
        """Get an instance of the requested service type."""
        
        # Check singletons first
        if service_type in self._singletons:
            return self._singletons[service_type]
        
        # Check factories
        if service_type in self._factories:
            factory = self._factories[service_type]
            return factory(self)
        
        # Check type mappings
        if service_type in self._services:
            implementation_type = self._services[service_type]
            return self._create_instance(implementation_type)
        
        # Try to create directly
        return self._create_instance(service_type)
    
    def _create_instance(self, cls: Type) -> Any:
        """Create instance with dependency injection."""
        import inspect
        
        # Get constructor signature
        signature = inspect.signature(cls.__init__)
        parameters = signature.parameters
        
        # Build arguments
        args = {}
        for param_name, param in parameters.items():
            if param_name == 'self':
                continue
            
            param_type = param.annotation
            if param_type != inspect.Parameter.empty:
                args[param_name] = self.get(param_type)
        
        return cls(**args)

# Usage example
def setup_dependency_container(config: MAOSConfig) -> DIContainer:
    """Set up the dependency injection container."""
    container = DIContainer()
    
    # Register configuration
    container.register_singleton(MAOSConfig, config)
    container.register_singleton(SystemConfig, config.system)
    container.register_singleton(DatabaseConfig, config.database)
    container.register_singleton(RedisConfig, config.redis)
    
    # Register database factory
    def database_factory(container: DIContainer) -> Database:
        db_config = container.get(DatabaseConfig)
        return Database(db_config.url, pool_size=db_config.pool_size)
    
    container.register_factory(Database, database_factory)
    
    # Register Redis factory
    def redis_factory(container: DIContainer) -> Redis:
        redis_config = container.get(RedisConfig)
        return Redis.from_url(
            redis_config.url,
            max_connections=redis_config.max_connections
        )
    
    container.register_factory(Redis, redis_factory)
    
    # Register service types
    container.register_type(TaskPlanner, DefaultTaskPlanner)
    container.register_type(AgentManager, DefaultAgentManager)
    container.register_type(ResourceAllocator, DefaultResourceAllocator)
    
    return container

# Application startup
def create_application(config_path: Path) -> MAOSApplication:
    """Create the MAOS application with all dependencies."""
    config = MAOSConfig.from_file(config_path)
    container = setup_dependency_container(config)
    
    # Create main application with injected dependencies
    return container.get(MAOSApplication)
```

This comprehensive architecture guide provides the foundation for understanding and contributing to the MAOS codebase. The patterns and principles outlined here ensure maintainability, testability, and extensibility as the system evolves.