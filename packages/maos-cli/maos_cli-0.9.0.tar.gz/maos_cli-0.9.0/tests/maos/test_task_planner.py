"""
Unit tests for Task Planner component.
"""

import pytest
import asyncio
from uuid import uuid4
from datetime import datetime

from src.maos.core.task_planner import TaskPlanner, ExecutionPlan
from src.maos.models.task import Task, TaskStatus, TaskPriority
from src.maos.utils.exceptions import TaskError, ValidationError


@pytest.fixture
async def task_planner():
    """Create a TaskPlanner instance for testing."""
    planner = TaskPlanner(
        max_parallel_tasks=4,
        default_task_timeout=60,
        optimization_enabled=True
    )
    yield planner
    await planner.shutdown()


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    return Task(
        name="Test Task",
        description="A test task for unit testing",
        priority=TaskPriority.HIGH,
        timeout_seconds=120,
        parameters={
            'input_data': 'test_data',
            'processing_type': 'batch'
        },
        tags={'test', 'batch_processing'}
    )


@pytest.mark.asyncio
class TestTaskPlanner:
    """Test cases for TaskPlanner class."""
    
    async def test_create_execution_plan_sequential(self, task_planner, sample_task):
        """Test creating an execution plan with sequential decomposition."""
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='sequential'
        )
        
        assert isinstance(plan, ExecutionPlan)
        assert plan.id is not None
        assert sample_task.id in plan.tasks
        assert len(plan.tasks) > 1  # Should have subtasks
        assert len(plan.parallel_groups) > 0
        assert len(plan.critical_path) > 0
        assert plan.estimated_duration > 0
    
    async def test_create_execution_plan_parallel(self, task_planner, sample_task):
        """Test creating an execution plan with parallel decomposition."""
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='parallel'
        )
        
        assert isinstance(plan, ExecutionPlan)
        assert sample_task.id in plan.tasks
        assert len(plan.tasks) > 1
        
        # Should have parallel groups with multiple tasks
        parallel_task_count = sum(len(group) for group in plan.parallel_groups)
        assert parallel_task_count >= 4  # At least the 4 parallel components + aggregation
    
    async def test_create_execution_plan_pipeline(self, task_planner, sample_task):
        """Test creating an execution plan with pipeline decomposition."""
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='pipeline'
        )
        
        assert isinstance(plan, ExecutionPlan)
        assert len(plan.tasks) > 1
        
        # Pipeline should have sequential dependencies
        task_ids = list(plan.tasks.keys())
        root_task_id = sample_task.id
        subtask_ids = [tid for tid in task_ids if tid != root_task_id]
        
        # Check that subtasks have proper sequential dependencies
        for i, subtask_id in enumerate(subtask_ids[1:], 1):
            subtask = plan.tasks[subtask_id]
            assert len(subtask.dependencies) == 1  # Should depend on previous task
    
    async def test_create_execution_plan_fan_out_fan_in(self, task_planner, sample_task):
        """Test creating an execution plan with fan-out/fan-in decomposition."""
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='fan_out_fan_in'
        )
        
        assert isinstance(plan, ExecutionPlan)
        assert len(plan.tasks) >= 6  # fan-out + 4 parallel + fan-in + root
        
        # Should have fan-out, parallel, and fan-in tasks
        subtasks = [task for task in plan.tasks.values() if task.id != sample_task.id]
        fan_out_tasks = [t for t in subtasks if 'fan_out' in t.tags]
        fan_in_tasks = [t for t in subtasks if 'fan_in' in t.tags]
        parallel_tasks = [t for t in subtasks if any(f'parallel_{i}' in t.tags for i in range(1, 5))]
        
        assert len(fan_out_tasks) == 1
        assert len(fan_in_tasks) == 1
        assert len(parallel_tasks) == 4
    
    async def test_create_execution_plan_hierarchical(self, task_planner, sample_task):
        """Test creating an execution plan with hierarchical decomposition."""
        # Add pipeline tag to trigger pipeline decomposition
        sample_task.tags.add('pipeline')
        
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='hierarchical'
        )
        
        assert isinstance(plan, ExecutionPlan)
        assert len(plan.tasks) > 1
    
    async def test_create_execution_plan_invalid_strategy(self, task_planner, sample_task):
        """Test creating an execution plan with invalid decomposition strategy."""
        with pytest.raises(ValidationError) as exc_info:
            await task_planner.create_execution_plan(
                root_task=sample_task,
                decomposition_strategy='invalid_strategy'
            )
        
        assert "Unknown decomposition strategy" in str(exc_info.value)
    
    async def test_execution_plan_validation(self, task_planner, sample_task):
        """Test execution plan validation."""
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='sequential'
        )
        
        issues = await task_planner.validate_plan(plan)
        assert isinstance(issues, list)
        # Should have no issues for a properly created plan
        assert len(issues) == 0
    
    async def test_get_execution_plan(self, task_planner, sample_task):
        """Test retrieving an execution plan by ID."""
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='sequential'
        )
        
        retrieved_plan = task_planner.get_execution_plan(plan.id)
        assert retrieved_plan is not None
        assert retrieved_plan.id == plan.id
        
        # Test non-existent plan
        non_existent_plan = task_planner.get_execution_plan(uuid4())
        assert non_existent_plan is None
    
    async def test_task_registration(self, task_planner, sample_task):
        """Test task registration and retrieval."""
        task_planner.register_task(sample_task)
        
        retrieved_task = task_planner.get_task(sample_task.id)
        assert retrieved_task is not None
        assert retrieved_task.id == sample_task.id
        assert retrieved_task.name == sample_task.name
    
    async def test_resource_requirement_calculation(self, task_planner, sample_task):
        """Test resource requirement calculation."""
        # Set specific resource requirements
        sample_task.resource_requirements = {
            'cpu_cores': 2.0,
            'memory_mb': 1024,
            'disk_mb': 500
        }
        
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='parallel'
        )
        
        assert 'cpu_cores' in plan.resource_requirements
        assert 'memory_mb' in plan.resource_requirements
        assert 'disk_mb' in plan.resource_requirements
        
        # Should take the maximum requirement across all tasks
        assert plan.resource_requirements['cpu_cores'] >= 2.0
        assert plan.resource_requirements['memory_mb'] >= 1024
    
    async def test_plan_optimization(self, task_planner, sample_task):
        """Test execution plan optimization."""
        # Create a plan that should be optimized
        sample_task.priority = TaskPriority.CRITICAL
        
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='parallel',
            optimization_options={'optimize_critical_path': True}
        )
        
        # Check that critical path tasks have higher priority
        critical_tasks = [plan.tasks[tid] for tid in plan.critical_path]
        for task in critical_tasks:
            assert task.priority.value >= TaskPriority.HIGH.value
    
    async def test_parallel_group_size_limit(self, task_planner, sample_task):
        """Test that parallel groups respect the maximum size limit."""
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='parallel'
        )
        
        # Check that no parallel group exceeds the max_parallel_tasks limit
        for group in plan.parallel_groups:
            assert len(group) <= task_planner.max_parallel_tasks
    
    async def test_metrics_collection(self, task_planner, sample_task):
        """Test that metrics are properly collected."""
        initial_metrics = task_planner.get_metrics()
        initial_plans = initial_metrics['plans_created']
        initial_tasks = initial_metrics['tasks_planned']
        
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='sequential'
        )
        
        final_metrics = task_planner.get_metrics()
        
        assert final_metrics['plans_created'] == initial_plans + 1
        assert final_metrics['tasks_planned'] > initial_tasks
        assert final_metrics['planning_time_ms'] > 0
    
    async def test_optimization_rule_addition(self, task_planner):
        """Test adding custom optimization rules."""
        rule_called = False
        
        async def custom_rule(plan, options):
            nonlocal rule_called
            rule_called = True
            return plan
        
        task_planner.add_optimization_rule(custom_rule)
        
        sample_task = Task(
            name="Test Task",
            description="Test task",
            priority=TaskPriority.MEDIUM
        )
        
        await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='sequential'
        )
        
        assert rule_called


@pytest.mark.asyncio
class TestExecutionPlan:
    """Test cases for ExecutionPlan class."""
    
    async def test_execution_plan_ready_tasks(self, task_planner, sample_task):
        """Test getting ready tasks from execution plan."""
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='sequential'
        )
        
        # Initially, only tasks with no dependencies should be ready
        ready_tasks = plan.get_ready_tasks(set())
        assert len(ready_tasks) > 0
        
        # All ready tasks should have no unsatisfied dependencies
        for task_id in ready_tasks:
            task_node = plan.dag[task_id]
            assert len(task_node.dependencies) == 0
    
    async def test_execution_plan_completion_check(self, task_planner, sample_task):
        """Test execution plan completion checking."""
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='sequential'
        )
        
        # Plan should not be complete initially
        assert not plan.is_complete(set())
        
        # Plan should be complete when all tasks are marked complete
        all_task_ids = set(plan.tasks.keys())
        assert plan.is_complete(all_task_ids)
    
    async def test_execution_plan_critical_path(self, task_planner, sample_task):
        """Test critical path calculation in execution plan."""
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='pipeline'
        )
        
        # Critical path should include the root task
        assert sample_task.id in plan.critical_path or any(
            task.parent_task_id == sample_task.id 
            for task_id in plan.critical_path 
            for task in [plan.tasks[task_id]]
        )
        
        # Critical path should have at least one task
        assert len(plan.critical_path) > 0


@pytest.mark.asyncio
class TestTaskDecomposition:
    """Test cases for task decomposition strategies."""
    
    async def test_task_subtask_relationships(self, task_planner, sample_task):
        """Test that subtask relationships are properly established."""
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='sequential'
        )
        
        root_task = plan.tasks[sample_task.id]
        
        # Root task should have subtasks
        assert len(root_task.subtasks) > 0
        
        # All subtasks should exist in the plan
        for subtask_id in root_task.subtasks:
            assert subtask_id in plan.tasks
            subtask = plan.tasks[subtask_id]
            assert subtask.parent_task_id == sample_task.id
    
    async def test_dependency_resolution(self, task_planner, sample_task):
        """Test that task dependencies are properly resolved."""
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='pipeline'
        )
        
        # Check that dependencies are properly established
        for task_id, task in plan.tasks.items():
            for dep in task.dependencies:
                # All dependencies should exist in the plan
                assert dep.task_id in plan.tasks
    
    async def test_task_parameter_inheritance(self, task_planner, sample_task):
        """Test that subtasks inherit relevant parameters."""
        sample_task.parameters = {
            'global_param': 'global_value',
            'processing_mode': 'batch'
        }
        
        plan = await task_planner.create_execution_plan(
            root_task=sample_task,
            decomposition_strategy='sequential'
        )
        
        # Check that subtasks inherit some parameters
        root_task = plan.tasks[sample_task.id]
        for subtask_id in root_task.subtasks:
            subtask = plan.tasks[subtask_id]
            # Subtasks should have some inherited parameters
            assert len(subtask.parameters) > 0
    
    async def test_task_priority_propagation(self, task_planner):
        """Test that task priority is properly propagated to subtasks."""
        high_priority_task = Task(
            name="High Priority Task",
            description="A high priority task",
            priority=TaskPriority.CRITICAL
        )
        
        plan = await task_planner.create_execution_plan(
            root_task=high_priority_task,
            decomposition_strategy='sequential'
        )
        
        root_task = plan.tasks[high_priority_task.id]
        
        # Subtasks should inherit or maintain high priority
        for subtask_id in root_task.subtasks:
            subtask = plan.tasks[subtask_id]
            assert subtask.priority.value >= TaskPriority.MEDIUM.value


if __name__ == "__main__":
    pytest.main([__file__])