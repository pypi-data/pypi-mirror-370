"""
Task Planner component for MAOS orchestration system.

This component is responsible for:
- DAG-based task decomposition
- Dependency resolution and parallel execution planning  
- Resource estimation and optimization
- Integration with Claude Code Task API
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple, Any, Callable
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from collections import defaultdict

from ..models.task import Task, TaskStatus, TaskPriority, TaskDependency
from ..models.agent import Agent, AgentCapability
from ..models.resource import Resource, ResourceType
from ..utils.logging_config import MAOSLogger
from ..utils.dag_utils import DAGBuilder, DAGValidator, TaskNode
from ..utils.exceptions import (
    TaskError, TaskDependencyError, DAGError, CircularDependencyError,
    ValidationError
)


@dataclass
class ExecutionPlan:
    """Represents an execution plan for a set of tasks."""
    
    id: UUID = field(default_factory=uuid4)
    tasks: Dict[UUID, Task] = field(default_factory=dict)
    dag: Dict[UUID, TaskNode] = field(default_factory=dict)
    parallel_groups: List[List[UUID]] = field(default_factory=list)
    critical_path: List[UUID] = field(default_factory=list)
    estimated_duration: int = 0
    resource_requirements: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_ready_tasks(self, completed_tasks: Set[UUID]) -> List[UUID]:
        """Get tasks that are ready to execute."""
        return DAGValidator.get_ready_tasks(self.dag, completed_tasks)
    
    def is_complete(self, completed_tasks: Set[UUID]) -> bool:
        """Check if execution plan is complete."""
        return completed_tasks.issuperset(set(self.tasks.keys()))


class TaskPlanner:
    """
    Task Planner component for orchestrating complex workflows.
    
    This component handles:
    - Task decomposition using DAG structures
    - Dependency resolution and validation
    - Resource requirement analysis
    - Parallel execution optimization
    - Integration with Claude Code Task API
    """
    
    def __init__(
        self,
        max_parallel_tasks: int = 10,
        default_task_timeout: int = 300,
        optimization_enabled: bool = True
    ):
        """Initialize the Task Planner."""
        self.max_parallel_tasks = max_parallel_tasks
        self.default_task_timeout = default_task_timeout
        self.optimization_enabled = optimization_enabled
        
        self.logger = MAOSLogger("task_planner", str(uuid4()))
        
        # Internal state
        self._execution_plans: Dict[UUID, ExecutionPlan] = {}
        self._task_registry: Dict[UUID, Task] = {}
        self._decomposition_strategies: Dict[str, Callable] = {}
        self._optimization_rules: List[Callable] = []
        
        # Metrics
        self._metrics = {
            'plans_created': 0,
            'tasks_planned': 0,
            'optimization_time_ms': 0,
            'planning_time_ms': 0
        }
        
        # Register default decomposition strategies
        self._register_default_strategies()
    
    def _register_default_strategies(self) -> None:
        """Register default task decomposition strategies."""
        
        self._decomposition_strategies.update({
            'sequential': self._decompose_sequential,
            'parallel': self._decompose_parallel,
            'pipeline': self._decompose_pipeline,
            'fan_out_fan_in': self._decompose_fan_out_fan_in,
            'hierarchical': self._decompose_hierarchical
        })
    
    async def create_execution_plan(
        self,
        root_task: Task,
        decomposition_strategy: str = 'hierarchical',
        optimization_options: Optional[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        """
        Create an execution plan for a complex task.
        
        Args:
            root_task: The root task to decompose and plan
            decomposition_strategy: Strategy to use for task decomposition
            optimization_options: Options for plan optimization
            
        Returns:
            ExecutionPlan: Complete execution plan with DAG and scheduling
        """
        start_time = time.time()
        
        try:
            self.logger.log_task_event(
                "plan_creation_started",
                str(root_task.id),
                strategy=decomposition_strategy
            )
            
            # Step 1: Decompose the root task into subtasks
            subtasks = await self._decompose_task(root_task, decomposition_strategy)
            
            # Step 2: Build the DAG
            dag_builder = DAGBuilder()
            all_tasks = {root_task.id: root_task}
            
            # Add root task
            dag_builder.add_task(
                root_task.id,
                priority=root_task.priority.value,
                estimated_duration=root_task.estimate_duration(),
                metadata={'type': 'root'}
            )
            
            # Add subtasks and build dependency graph
            for subtask in subtasks:
                all_tasks[subtask.id] = subtask
                
                dag_builder.add_task(
                    subtask.id,
                    priority=subtask.priority.value,
                    estimated_duration=subtask.estimate_duration(),
                    metadata={'type': 'subtask', 'parent_id': str(subtask.parent_task_id)}
                )
                
                # Add dependencies
                for dep in subtask.dependencies:
                    dag_builder.add_dependency(subtask.id, dep.task_id)
            
            # Step 3: Validate and build the DAG
            dag = dag_builder.build()
            
            # Step 4: Calculate execution groups and critical path
            parallel_groups = DAGValidator.get_parallel_groups(dag)
            critical_path, estimated_duration = DAGValidator.find_critical_path(dag)
            
            # Step 5: Calculate resource requirements
            resource_requirements = self._calculate_resource_requirements(all_tasks)
            
            # Step 6: Create execution plan
            plan = ExecutionPlan(
                tasks=all_tasks,
                dag=dag,
                parallel_groups=parallel_groups,
                critical_path=critical_path,
                estimated_duration=estimated_duration,
                resource_requirements=resource_requirements,
                metadata={
                    'decomposition_strategy': decomposition_strategy,
                    'optimization_options': optimization_options or {}
                }
            )
            
            # Step 7: Optimize the plan if enabled
            if self.optimization_enabled:
                plan = await self._optimize_execution_plan(plan, optimization_options)
            
            # Step 8: Store the plan
            self._execution_plans[plan.id] = plan
            
            # Update metrics
            planning_time = (time.time() - start_time) * 1000
            self._metrics['plans_created'] += 1
            self._metrics['tasks_planned'] += len(all_tasks)
            self._metrics['planning_time_ms'] += planning_time
            
            self.logger.log_task_event(
                "plan_created",
                str(root_task.id),
                plan_id=str(plan.id),
                task_count=len(all_tasks),
                estimated_duration=estimated_duration,
                planning_time_ms=planning_time
            )
            
            return plan
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'create_execution_plan',
                'task_id': str(root_task.id),
                'strategy': decomposition_strategy
            })
            raise TaskError(
                f"Failed to create execution plan: {str(e)}",
                task_id=root_task.id,
                error_code="PLAN_CREATION_FAILED"
            )
    
    async def _decompose_task(
        self,
        task: Task,
        strategy: str
    ) -> List[Task]:
        """Decompose a task using the specified strategy."""
        
        if strategy not in self._decomposition_strategies:
            raise ValidationError(
                f"Unknown decomposition strategy: {strategy}",
                field_name="strategy",
                field_value=strategy
            )
        
        strategy_func = self._decomposition_strategies[strategy]
        return await strategy_func(task)
    
    async def _decompose_sequential(self, task: Task) -> List[Task]:
        """Decompose task into sequential subtasks."""
        subtasks = []
        
        # Example sequential decomposition
        phases = ['preparation', 'execution', 'validation', 'cleanup']
        
        for i, phase in enumerate(phases):
            subtask = Task(
                name=f"{task.name} - {phase.title()}",
                description=f"{phase.title()} phase of {task.description}",
                priority=task.priority,
                parent_task_id=task.id,
                parameters={**task.parameters, 'phase': phase},
                timeout_seconds=task.timeout_seconds // len(phases),
                tags=task.tags | {f"phase_{phase}"},
                metadata={**task.metadata, 'phase': phase, 'sequence': i}
            )
            
            # Add dependency on previous task (except first)
            if i > 0:
                subtask.add_dependency(subtasks[i-1].id)
            
            subtasks.append(subtask)
            task.add_subtask(subtask.id)
        
        return subtasks
    
    async def _decompose_parallel(self, task: Task) -> List[Task]:
        """Decompose task into parallel subtasks."""
        subtasks = []
        
        # Example parallel decomposition
        components = ['component_a', 'component_b', 'component_c', 'component_d']
        
        for component in components:
            subtask = Task(
                name=f"{task.name} - {component.title()}",
                description=f"Process {component} for {task.description}",
                priority=task.priority,
                parent_task_id=task.id,
                parameters={**task.parameters, 'component': component},
                timeout_seconds=task.timeout_seconds,
                tags=task.tags | {f"component_{component}"},
                metadata={**task.metadata, 'component': component}
            )
            
            subtasks.append(subtask)
            task.add_subtask(subtask.id)
        
        # Add a final aggregation task that depends on all parallel tasks
        aggregation_task = Task(
            name=f"{task.name} - Aggregation",
            description=f"Aggregate results from parallel processing of {task.description}",
            priority=task.priority,
            parent_task_id=task.id,
            parameters={**task.parameters, 'phase': 'aggregation'},
            timeout_seconds=task.timeout_seconds // 4,
            tags=task.tags | {"aggregation"},
            metadata={**task.metadata, 'phase': 'aggregation'}
        )
        
        # Make aggregation depend on all parallel tasks
        for subtask in subtasks:
            aggregation_task.add_dependency(subtask.id)
        
        subtasks.append(aggregation_task)
        task.add_subtask(aggregation_task.id)
        
        return subtasks
    
    async def _decompose_pipeline(self, task: Task) -> List[Task]:
        """Decompose task into pipeline stages."""
        subtasks = []
        
        # Example pipeline decomposition
        stages = [
            ('input_processing', 'Process input data'),
            ('transformation', 'Transform data'),  
            ('analysis', 'Analyze transformed data'),
            ('output_generation', 'Generate output')
        ]
        
        for i, (stage_name, stage_desc) in enumerate(stages):
            subtask = Task(
                name=f"{task.name} - {stage_name.replace('_', ' ').title()}",
                description=f"{stage_desc} for {task.description}",
                priority=task.priority,
                parent_task_id=task.id,
                parameters={**task.parameters, 'stage': stage_name},
                timeout_seconds=task.timeout_seconds // len(stages),
                tags=task.tags | {f"stage_{stage_name}"},
                metadata={**task.metadata, 'stage': stage_name, 'stage_index': i}
            )
            
            # Each stage depends on the previous one
            if i > 0:
                subtask.add_dependency(subtasks[i-1].id)
            
            subtasks.append(subtask)
            task.add_subtask(subtask.id)
        
        return subtasks
    
    async def _decompose_fan_out_fan_in(self, task: Task) -> List[Task]:
        """Decompose task into fan-out/fan-in pattern."""
        subtasks = []
        
        # Step 1: Fan-out preparation
        fan_out_task = Task(
            name=f"{task.name} - Fan-out Preparation",
            description=f"Prepare data for parallel processing of {task.description}",
            priority=task.priority,
            parent_task_id=task.id,
            parameters={**task.parameters, 'phase': 'fan_out'},
            timeout_seconds=task.timeout_seconds // 10,
            tags=task.tags | {"fan_out"},
            metadata={**task.metadata, 'phase': 'fan_out'}
        )
        subtasks.append(fan_out_task)
        task.add_subtask(fan_out_task.id)
        
        # Step 2: Parallel processing tasks
        parallel_tasks = []
        for i in range(4):  # Create 4 parallel processing tasks
            parallel_task = Task(
                name=f"{task.name} - Parallel Process {i+1}",
                description=f"Parallel processing unit {i+1} for {task.description}",
                priority=task.priority,
                parent_task_id=task.id,
                parameters={**task.parameters, 'parallel_unit': i+1},
                timeout_seconds=task.timeout_seconds // 2,
                tags=task.tags | {f"parallel_{i+1}"},
                metadata={**task.metadata, 'parallel_unit': i+1}
            )
            
            # Depend on fan-out task
            parallel_task.add_dependency(fan_out_task.id)
            
            parallel_tasks.append(parallel_task)
            subtasks.append(parallel_task)
            task.add_subtask(parallel_task.id)
        
        # Step 3: Fan-in aggregation
        fan_in_task = Task(
            name=f"{task.name} - Fan-in Aggregation",
            description=f"Aggregate results from parallel processing of {task.description}",
            priority=task.priority,
            parent_task_id=task.id,
            parameters={**task.parameters, 'phase': 'fan_in'},
            timeout_seconds=task.timeout_seconds // 10,
            tags=task.tags | {"fan_in"},
            metadata={**task.metadata, 'phase': 'fan_in'}
        )
        
        # Depend on all parallel tasks
        for parallel_task in parallel_tasks:
            fan_in_task.add_dependency(parallel_task.id)
        
        subtasks.append(fan_in_task)
        task.add_subtask(fan_in_task.id)
        
        return subtasks
    
    async def _decompose_hierarchical(self, task: Task) -> List[Task]:
        """Decompose task using hierarchical approach based on task complexity."""
        
        # Determine decomposition strategy based on task characteristics
        if len(task.parameters.get('data_sources', [])) > 1:
            return await self._decompose_parallel(task)
        elif 'pipeline' in task.tags or 'sequential' in task.tags:
            return await self._decompose_pipeline(task) 
        elif task.priority == TaskPriority.HIGH:
            return await self._decompose_fan_out_fan_in(task)
        else:
            return await self._decompose_sequential(task)
    
    def _calculate_resource_requirements(self, tasks: Dict[UUID, Task]) -> Dict[str, float]:
        """Calculate aggregate resource requirements for all tasks."""
        
        requirements = defaultdict(float)
        
        for task in tasks.values():
            task_reqs = task.resource_requirements
            
            # Default resource requirements if not specified
            if not task_reqs:
                task_reqs = {
                    'cpu_cores': 0.5,
                    'memory_mb': 256,
                    'disk_mb': 100
                }
            
            for resource_type, amount in task_reqs.items():
                requirements[resource_type] = max(requirements[resource_type], amount)
        
        return dict(requirements)
    
    async def _optimize_execution_plan(
        self,
        plan: ExecutionPlan,
        options: Optional[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        """Optimize the execution plan for better performance."""
        
        start_time = time.time()
        
        try:
            # Apply optimization rules
            for rule in self._optimization_rules:
                plan = await rule(plan, options)
            
            # Resource balancing optimization
            plan = await self._optimize_resource_balance(plan)
            
            # Critical path optimization  
            plan = await self._optimize_critical_path(plan)
            
            # Parallel group optimization
            plan = await self._optimize_parallel_groups(plan)
            
            # Update metrics
            optimization_time = (time.time() - start_time) * 1000
            self._metrics['optimization_time_ms'] += optimization_time
            
            self.logger.logger.info(
                "Execution plan optimized",
                extra={
                    'plan_id': str(plan.id),
                    'optimization_time_ms': optimization_time,
                    'original_duration': plan.estimated_duration,
                }
            )
            
            return plan
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'optimize_execution_plan',
                'plan_id': str(plan.id)
            })
            # Return original plan if optimization fails
            return plan
    
    async def _optimize_resource_balance(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Optimize resource allocation across parallel tasks."""
        
        # Analyze resource usage patterns in parallel groups
        for group in plan.parallel_groups:
            if len(group) <= 1:
                continue
            
            # Calculate resource requirements for each task in the group
            group_resources = {}
            for task_id in group:
                task = plan.tasks[task_id]
                group_resources[task_id] = task.resource_requirements or {}
            
            # Balance resources by adjusting task priorities
            # Tasks with higher resource requirements get slightly lower priority
            # to prevent resource contention
            for task_id, resources in group_resources.items():
                task = plan.tasks[task_id]
                resource_weight = sum(resources.values()) if resources else 1.0
                
                # Adjust priority based on resource weight
                if resource_weight > 2.0:  # High resource usage
                    if task.priority == TaskPriority.HIGH:
                        task.priority = TaskPriority.MEDIUM
                elif resource_weight < 0.5:  # Low resource usage
                    if task.priority == TaskPriority.MEDIUM:
                        task.priority = TaskPriority.HIGH
        
        return plan
    
    async def _optimize_critical_path(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Optimize tasks on the critical path."""
        
        # Increase priority for critical path tasks
        for task_id in plan.critical_path:
            task = plan.tasks[task_id]
            if task.priority == TaskPriority.MEDIUM:
                task.priority = TaskPriority.HIGH
            elif task.priority == TaskPriority.LOW:
                task.priority = TaskPriority.MEDIUM
        
        return plan
    
    async def _optimize_parallel_groups(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Optimize parallel task groups for better load balancing."""
        
        # Limit parallel group size to max_parallel_tasks
        optimized_groups = []
        
        for group in plan.parallel_groups:
            if len(group) <= self.max_parallel_tasks:
                optimized_groups.append(group)
            else:
                # Split large groups into smaller chunks
                for i in range(0, len(group), self.max_parallel_tasks):
                    chunk = group[i:i + self.max_parallel_tasks]
                    optimized_groups.append(chunk)
        
        plan.parallel_groups = optimized_groups
        return plan
    
    def get_execution_plan(self, plan_id: UUID) -> Optional[ExecutionPlan]:
        """Get an execution plan by ID."""
        return self._execution_plans.get(plan_id)
    
    def get_task(self, task_id: UUID) -> Optional[Task]:
        """Get a task by ID."""
        return self._task_registry.get(task_id)
    
    def register_task(self, task: Task) -> None:
        """Register a task in the task registry."""
        self._task_registry[task.id] = task
    
    def add_optimization_rule(self, rule: Callable) -> None:
        """Add a custom optimization rule."""
        self._optimization_rules.append(rule)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get task planner metrics."""
        return self._metrics.copy()
    
    async def validate_plan(self, plan: ExecutionPlan) -> List[str]:
        """Validate an execution plan and return any issues found."""
        issues = []
        
        try:
            # Validate DAG structure
            dag_issues = DAGValidator.validate_dag(plan.dag)
            issues.extend(dag_issues)
            
            # Validate task relationships
            for task_id, task in plan.tasks.items():
                # Check if all dependencies exist
                for dep in task.dependencies:
                    if dep.task_id not in plan.tasks:
                        issues.append(f"Task {task_id} depends on non-existent task {dep.task_id}")
                
                # Check if all subtasks exist
                for subtask_id in task.subtasks:
                    if subtask_id not in plan.tasks:
                        issues.append(f"Task {task_id} references non-existent subtask {subtask_id}")
            
            # Validate parallel groups
            all_grouped_tasks = set()
            for group in plan.parallel_groups:
                for task_id in group:
                    if task_id in all_grouped_tasks:
                        issues.append(f"Task {task_id} appears in multiple parallel groups")
                    all_grouped_tasks.add(task_id)
                    
                    if task_id not in plan.tasks:
                        issues.append(f"Parallel group references non-existent task {task_id}")
            
            # Validate critical path
            for task_id in plan.critical_path:
                if task_id not in plan.tasks:
                    issues.append(f"Critical path references non-existent task {task_id}")
            
        except Exception as e:
            issues.append(f"Validation error: {str(e)}")
        
        return issues
    
    async def shutdown(self) -> None:
        """Shutdown the task planner and cleanup resources."""
        self.logger.logger.info(
            "Task planner shutting down",
            extra={
                'plans_created': self._metrics['plans_created'],
                'tasks_planned': self._metrics['tasks_planned']
            }
        )
        
        # Clear internal state
        self._execution_plans.clear()
        self._task_registry.clear()