"""
Integration tests for multi-agent coordination workflows.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

from src.maos.core.orchestrator import Orchestrator
from src.maos.models.task import Task, TaskStatus, TaskPriority
from src.maos.models.agent import Agent, AgentCapability
from tests.utils.test_helpers import TestDataFactory, AsyncTestRunner, StateVerifier, TestScenarioBuilder


@pytest.mark.integration
class TestMultiAgentCoordination:
    """Integration tests for multi-agent coordination scenarios."""

    async def test_parallel_task_execution(self, orchestrator, load_generator):
        """Test parallel execution of independent tasks by multiple agents."""
        # Create multiple tasks that can run in parallel
        tasks = load_generator.generate_tasks(5)
        
        # Create agents with different capabilities
        agents = []
        for i in range(3):
            agent = TestDataFactory.create_agent(
                name=f"Worker Agent {i}",
                capabilities={AgentCapability.TASK_EXECUTION, AgentCapability.DATA_PROCESSING}
            )
            agents.append(agent)
        
        # Register agents
        for agent in agents:
            await orchestrator.create_agent(
                agent_type=agent.type,
                capabilities=agent.capabilities
            )
        
        # Submit all tasks
        execution_plans = []
        for task in tasks:
            plan = await orchestrator.submit_task(task)
            execution_plans.append(plan)
        
        # Execute all plans concurrently
        start_time = datetime.utcnow()
        execution_tasks = []
        for plan in execution_plans:
            execution_tasks.append(orchestrator.execute_plan(plan.id))
        
        # Wait for all executions to start
        await asyncio.gather(*execution_tasks)
        
        # Wait for tasks to complete
        completed_tasks = []
        timeout = 30.0  # 30 seconds
        
        while len(completed_tasks) < len(tasks) and (datetime.utcnow() - start_time).total_seconds() < timeout:
            for task in tasks:
                if task.id not in [t.id for t in completed_tasks]:
                    updated_task = await orchestrator.get_task(task.id)
                    if updated_task and updated_task.status == TaskStatus.COMPLETED:
                        completed_tasks.append(updated_task)
            
            await asyncio.sleep(0.1)
        
        # Verify all tasks completed
        assert len(completed_tasks) == len(tasks)
        
        # Verify execution time was reasonable (parallel should be faster)
        total_execution_time = (datetime.utcnow() - start_time).total_seconds()
        assert total_execution_time < 20.0, f"Parallel execution took too long: {total_execution_time}s"

    async def test_sequential_dependent_workflow(self, orchestrator):
        """Test execution of tasks with dependencies."""
        scenario = TestScenarioBuilder().build_sequential_workflow(4).tasks
        
        # Create agent
        agent = await orchestrator.create_agent(
            agent_type="sequential_worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        # Submit tasks in order (dependencies should be handled automatically)
        execution_plans = []
        for task in scenario:
            plan = await orchestrator.submit_task(task)
            execution_plans.append(plan)
        
        # Execute the workflow
        for plan in execution_plans:
            await orchestrator.execute_plan(plan.id)
        
        # Wait for completion and verify execution order
        await AsyncTestRunner.wait_for_condition(
            lambda: all(
                orchestrator.get_task(task.id) and 
                orchestrator.get_task(task.id).status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
                for task in scenario
            ),
            timeout=30.0
        )
        
        # Verify tasks completed in dependency order
        completion_times = []
        for task in scenario:
            updated_task = await orchestrator.get_task(task.id)
            assert updated_task.status == TaskStatus.COMPLETED
            completion_times.append(updated_task.completed_at)
        
        # Verify chronological order
        for i in range(1, len(completion_times)):
            assert completion_times[i] >= completion_times[i-1], \
                "Tasks did not complete in dependency order"

    async def test_diamond_dependency_workflow(self, orchestrator):
        """Test diamond-shaped dependency workflow execution."""
        scenario = TestScenarioBuilder().build_diamond_workflow()
        
        # Create multiple agents for parallel execution
        agents = []
        for i in range(3):
            agent = await orchestrator.create_agent(
                agent_type="diamond_worker",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
            agents.append(agent)
        
        # Submit all tasks
        execution_plans = []
        for task in scenario.tasks:
            plan = await orchestrator.submit_task(task)
            execution_plans.append(plan)
        
        # Execute workflow
        execution_tasks = []
        for plan in execution_plans:
            execution_tasks.append(orchestrator.execute_plan(plan.id))
        
        await asyncio.gather(*execution_tasks)
        
        # Wait for completion
        await AsyncTestRunner.wait_for_condition(
            lambda: all(
                orchestrator.get_task(task.id) and 
                orchestrator.get_task(task.id).status == TaskStatus.COMPLETED
                for task in scenario.tasks
            ),
            timeout=30.0
        )
        
        # Verify execution pattern
        start_task = scenario.tasks[0]
        middle_tasks = scenario.tasks[1:3]
        end_task = scenario.tasks[3]
        
        start_completed = await orchestrator.get_task(start_task.id)
        middle_completed = [await orchestrator.get_task(task.id) for task in middle_tasks]
        end_completed = await orchestrator.get_task(end_task.id)
        
        # Start should complete before middle tasks
        for middle_task in middle_completed:
            assert start_completed.completed_at <= middle_task.started_at
        
        # Middle tasks should complete before end task
        latest_middle_completion = max(task.completed_at for task in middle_completed)
        assert latest_middle_completion <= end_completed.started_at

    async def test_agent_load_balancing(self, orchestrator, load_generator):
        """Test that tasks are distributed evenly across available agents."""
        num_tasks = 20
        num_agents = 4
        
        # Create agents with different capacities
        agents = []
        for i in range(num_agents):
            agent = await orchestrator.create_agent(
                agent_type="load_balanced_worker",
                capabilities={AgentCapability.TASK_EXECUTION},
                configuration={"max_concurrent_tasks": 2}
            )
            agents.append(agent)
        
        # Generate many tasks
        tasks = load_generator.generate_tasks(num_tasks)
        
        # Submit all tasks
        for task in tasks:
            await orchestrator.submit_task(task)
        
        # Wait for all tasks to complete
        await AsyncTestRunner.wait_for_condition(
            lambda: all(
                orchestrator.get_task(task.id) and 
                orchestrator.get_task(task.id).status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
                for task in tasks
            ),
            timeout=60.0
        )
        
        # Check load distribution
        agent_task_counts = {}
        for task in tasks:
            updated_task = await orchestrator.get_task(task.id)
            if updated_task.agent_id:
                agent_task_counts[updated_task.agent_id] = agent_task_counts.get(
                    updated_task.agent_id, 0
                ) + 1
        
        # Verify reasonably balanced distribution
        task_counts = list(agent_task_counts.values())
        avg_tasks = sum(task_counts) / len(task_counts)
        max_deviation = max(abs(count - avg_tasks) for count in task_counts)
        
        # Allow for some variance but ensure reasonable balance
        assert max_deviation <= avg_tasks * 0.5, \
            f"Load balancing poor: counts={task_counts}, avg={avg_tasks}"

    async def test_agent_failure_recovery(self, orchestrator, chaos_injection):
        """Test system recovery when an agent fails during execution."""
        # Create agents
        agents = []
        for i in range(3):
            agent = await orchestrator.create_agent(
                agent_type="failure_test_agent",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
            agents.append(agent)
        
        # Create long-running tasks
        tasks = []
        for i in range(5):
            task = TestDataFactory.create_task(
                name=f"Long Task {i}",
                timeout_seconds=30
            )
            tasks.append(task)
        
        # Submit tasks
        for task in tasks:
            await orchestrator.submit_task(task)
        
        # Let tasks start executing
        await asyncio.sleep(1.0)
        
        # Simulate agent failure
        failing_agent = agents[0]
        await chaos_injection.inject_agent_failure(failing_agent, "crash")
        
        # System should recover and reassign tasks
        await AsyncTestRunner.wait_for_condition(
            lambda: all(
                orchestrator.get_task(task.id) and 
                orchestrator.get_task(task.id).status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
                for task in tasks
            ),
            timeout=60.0
        )
        
        # Verify most tasks still completed
        completed_count = 0
        for task in tasks:
            updated_task = await orchestrator.get_task(task.id)
            if updated_task.status == TaskStatus.COMPLETED:
                completed_count += 1
        
        # Should recover and complete most tasks
        assert completed_count >= len(tasks) * 0.6, \
            f"Too many tasks failed after agent failure: {completed_count}/{len(tasks)}"

    async def test_resource_contention_handling(self, orchestrator):
        """Test handling of resource contention between agents."""
        # Create resource-intensive tasks
        resource_heavy_tasks = []
        for i in range(3):
            task = TestDataFactory.create_task(
                name=f"Resource Heavy Task {i}",
                resource_requirements={
                    "cpu": 2.0,
                    "memory": 1024,
                    "gpu": 1.0  # Limited resource
                }
            )
            resource_heavy_tasks.append(task)
        
        # Create limited resources
        await orchestrator.create_resource(
            resource_type="gpu",
            capacity=2.0  # Only enough for 2 tasks
        )
        
        # Create agents
        for i in range(3):
            await orchestrator.create_agent(
                agent_type="resource_intensive_agent",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
        
        # Submit all tasks
        start_time = datetime.utcnow()
        for task in resource_heavy_tasks:
            await orchestrator.submit_task(task)
        
        # Wait for completion
        await AsyncTestRunner.wait_for_condition(
            lambda: all(
                orchestrator.get_task(task.id) and 
                orchestrator.get_task(task.id).status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
                for task in resource_heavy_tasks
            ),
            timeout=60.0
        )
        
        # Verify resource contention was handled properly
        completed_tasks = []
        for task in resource_heavy_tasks:
            updated_task = await orchestrator.get_task(task.id)
            if updated_task.status == TaskStatus.COMPLETED:
                completed_tasks.append(updated_task)
        
        # Should handle resource constraints gracefully
        assert len(completed_tasks) >= 2, "Resource contention not handled properly"
        
        # Execution should be serialized due to resource constraints
        total_time = (datetime.utcnow() - start_time).total_seconds()
        assert total_time > 5.0, "Tasks executed too quickly (resource constraints not applied)"

    async def test_priority_based_scheduling(self, orchestrator):
        """Test that high priority tasks are executed before low priority tasks."""
        # Create mixed priority tasks
        low_priority_tasks = []
        high_priority_tasks = []
        
        for i in range(3):
            low_task = TestDataFactory.create_task(
                name=f"Low Priority Task {i}",
                priority=TaskPriority.LOW
            )
            high_task = TestDataFactory.create_task(
                name=f"High Priority Task {i}",
                priority=TaskPriority.HIGH
            )
            low_priority_tasks.append(low_task)
            high_priority_tasks.append(high_task)
        
        # Create single agent to force sequential execution
        await orchestrator.create_agent(
            agent_type="priority_test_agent",
            capabilities={AgentCapability.TASK_EXECUTION},
            configuration={"max_concurrent_tasks": 1}
        )
        
        # Submit low priority tasks first
        for task in low_priority_tasks:
            await orchestrator.submit_task(task)
        
        # Then submit high priority tasks
        for task in high_priority_tasks:
            await orchestrator.submit_task(task)
        
        # Wait for completion
        all_tasks = low_priority_tasks + high_priority_tasks
        await AsyncTestRunner.wait_for_condition(
            lambda: all(
                orchestrator.get_task(task.id) and 
                orchestrator.get_task(task.id).status == TaskStatus.COMPLETED
                for task in all_tasks
            ),
            timeout=30.0
        )
        
        # Verify high priority tasks started before low priority
        high_start_times = []
        low_start_times = []
        
        for task in high_priority_tasks:
            updated_task = await orchestrator.get_task(task.id)
            high_start_times.append(updated_task.started_at)
        
        for task in low_priority_tasks:
            updated_task = await orchestrator.get_task(task.id)
            low_start_times.append(updated_task.started_at)
        
        # High priority tasks should start before any low priority task
        earliest_high = min(high_start_times)
        latest_low_before_high = max([t for t in low_start_times if t < earliest_high], default=None)
        
        # At least some high priority tasks should execute before low priority
        high_priority_first_count = sum(
            1 for h_time in high_start_times
            if all(h_time <= l_time for l_time in low_start_times)
        )
        
        assert high_priority_first_count > 0, "High priority tasks did not execute first"

    async def test_checkpoint_and_recovery(self, orchestrator):
        """Test checkpointing and recovery of multi-agent workflows."""
        # Create a complex workflow
        scenario = TestScenarioBuilder().build_diamond_workflow()
        
        # Create agents
        for i in range(2):
            await orchestrator.create_agent(
                agent_type="checkpoint_test_agent",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
        
        # Submit initial tasks
        for task in scenario.tasks[:2]:  # Submit first 2 tasks
            await orchestrator.submit_task(task)
        
        # Create checkpoint
        checkpoint_id = await orchestrator.create_checkpoint("mid_workflow")
        
        # Submit remaining tasks
        for task in scenario.tasks[2:]:
            await orchestrator.submit_task(task)
        
        # Wait for some progress
        await asyncio.sleep(2.0)
        
        # Simulate system recovery
        checkpoint_data = await orchestrator.list_checkpoints()
        assert len(checkpoint_data) >= 1
        
        # Restore from checkpoint (in a real scenario, this would be a new orchestrator instance)
        restore_success = await orchestrator.restore_checkpoint(checkpoint_id)
        assert restore_success is True
        
        # Verify system state is consistent
        system_status = await orchestrator.get_system_status()
        assert system_status["running"] is True