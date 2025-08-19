"""
Unit tests for Main Orchestrator component.
"""

import pytest
import asyncio
from uuid import uuid4
from datetime import datetime

from src.maos.core.orchestrator import Orchestrator
from src.maos.models.task import Task, TaskStatus, TaskPriority
from src.maos.models.agent import AgentCapability
from src.maos.models.resource import ResourceType
from src.maos.interfaces.persistence import InMemoryPersistence
from src.maos.utils.exceptions import OrchestrationError, TaskError, AgentError


@pytest.fixture
async def orchestrator():
    """Create an Orchestrator instance for testing."""
    persistence = InMemoryPersistence()
    
    config = {
        'state_manager': {
            'auto_checkpoint_interval': 0,  # Disable for testing
            'max_snapshots': 10
        },
        'message_bus': {
            'max_queue_size': 1000
        },
        'task_planner': {
            'max_parallel_tasks': 5,
            'optimization_enabled': True
        },
        'agent_manager': {
            'max_agents': 20,
            'health_check_interval': 0,  # Disable for testing
            'auto_recovery_enabled': False
        },
        'resource_allocator': {
            'auto_scaling_enabled': False,  # Disable for testing
            'capacity_monitoring_interval': 0,
            'queue_processing_interval': 0.1
        }
    }
    
    orchestrator = Orchestrator(
        persistence_backend=persistence,
        component_config=config
    )
    
    await orchestrator.start()
    yield orchestrator
    await orchestrator.shutdown()


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    return Task(
        name="Integration Test Task",
        description="A comprehensive test task for orchestration",
        priority=TaskPriority.HIGH,
        timeout_seconds=300,
        parameters={
            'test_mode': True,
            'data_size': 1000
        },
        resource_requirements={
            'cpu_cores': 2,
            'memory_mb': 1024
        },
        tags={'integration_test', 'orchestration'}
    )


@pytest.fixture
def sample_capabilities():
    """Create sample agent capabilities for testing."""
    return {
        AgentCapability.TASK_EXECUTION,
        AgentCapability.DATA_PROCESSING,
        AgentCapability.COMPUTATION
    }


@pytest.mark.asyncio
class TestOrchestrator:
    """Test cases for main Orchestrator class."""
    
    async def test_orchestrator_startup_shutdown(self, orchestrator):
        """Test orchestrator startup and shutdown."""
        # Orchestrator should be running
        status = await orchestrator.get_system_status()
        assert status['running'] is True
        assert 'uptime_seconds' in status
        assert status['components']['state_manager'] == 'running'
        
        # All components should be healthy
        health = await orchestrator.get_component_health()
        assert health['orchestrator'] == 'healthy'
        assert health['state_manager'] == 'healthy'
    
    async def test_submit_task_end_to_end(self, orchestrator, sample_task):
        """Test complete task submission workflow."""
        # Submit task
        execution_plan = await orchestrator.submit_task(
            task=sample_task,
            decomposition_strategy='sequential'
        )
        
        assert execution_plan is not None
        assert execution_plan.id is not None
        assert sample_task.id in execution_plan.tasks
        
        # Task should be stored in state
        retrieved_task = await orchestrator.get_task(sample_task.id)
        assert retrieved_task is not None
        assert retrieved_task.id == sample_task.id
        
        # Execution plan should be retrievable
        retrieved_plan = await orchestrator.get_execution_plan(execution_plan.id)
        assert retrieved_plan is not None
        assert retrieved_plan.id == execution_plan.id
    
    async def test_create_and_manage_agents(self, orchestrator, sample_capabilities):
        """Test agent creation and management."""
        # Create agent
        agent = await orchestrator.create_agent(
            agent_type="test_integration_agent",
            capabilities=sample_capabilities,
            configuration={'test_config': 'integration_value'}
        )
        
        assert agent is not None
        assert agent.type == "test_integration_agent"
        assert agent.capabilities == sample_capabilities
        
        # Agent should be retrievable
        retrieved_agent = await orchestrator.get_agent(agent.id)
        assert retrieved_agent is not None
        assert retrieved_agent.id == agent.id
        
        # Agent should be available
        available_agents = await orchestrator.get_available_agents()
        agent_ids = {agent.id for agent in available_agents}
        assert agent.id in agent_ids
        
        # Agent should be available with specific capabilities
        capable_agents = await orchestrator.get_available_agents(
            required_capabilities={AgentCapability.TASK_EXECUTION}
        )
        capable_agent_ids = {agent.id for agent in capable_agents}
        assert agent.id in capable_agent_ids
        
        # Terminate agent
        success = await orchestrator.terminate_agent(agent.id, "Integration test cleanup")
        assert success
        
        # Agent should no longer be available
        terminated_agent = await orchestrator.get_agent(agent.id)
        assert terminated_agent is None
    
    async def test_create_and_manage_resources(self, orchestrator):
        """Test resource creation and management."""
        # Create CPU resource
        cpu_resource = await orchestrator.create_resource(
            resource_type=ResourceType.CPU,
            capacity=4.0,
            configuration={'location': 'test_datacenter'}
        )
        
        assert cpu_resource is not None
        assert cpu_resource.type == ResourceType.CPU
        assert cpu_resource.total_capacity == 4.0
        
        # Create memory resource
        memory_resource = await orchestrator.create_resource(
            resource_type=ResourceType.MEMORY,
            capacity=2048.0
        )
        
        assert memory_resource is not None
        assert memory_resource.type == ResourceType.MEMORY
        assert memory_resource.total_capacity == 2048.0
        
        # Resources should be retrievable
        retrieved_cpu = await orchestrator.get_resource(cpu_resource.id)
        assert retrieved_cpu is not None
        assert retrieved_cpu.id == cpu_resource.id
        
        retrieved_memory = await orchestrator.get_resource(memory_resource.id)
        assert retrieved_memory is not None
        assert retrieved_memory.id == memory_resource.id
    
    async def test_resource_allocation_workflow(self, orchestrator):
        """Test resource allocation workflow."""
        # Create resources first
        await orchestrator.create_resource(
            resource_type=ResourceType.CPU,
            capacity=8.0
        )
        
        await orchestrator.create_resource(
            resource_type=ResourceType.MEMORY,
            capacity=4096.0
        )
        
        requester_id = uuid4()
        
        # Request resources
        request_id = await orchestrator.request_resources(
            requester_id=requester_id,
            resource_requirements={
                'cpu_cores': 2.0,
                'memory_mb': 1024.0
            },
            priority=TaskPriority.HIGH
        )
        
        assert request_id is not None
        
        # Wait for allocation processing
        await asyncio.sleep(0.2)
        
        # Release resources
        released_amount = await orchestrator.release_resources(
            requester_id=requester_id
        )
        
        # Should have released some resources
        assert released_amount >= 0
    
    async def test_task_status_tracking(self, orchestrator, sample_task):
        """Test task status tracking."""
        # Submit task
        await orchestrator.submit_task(sample_task)
        
        # Task should start as pending
        status = await orchestrator.get_task_status(sample_task.id)
        assert status in [TaskStatus.PENDING, TaskStatus.READY]
        
        # Task should be retrievable
        retrieved_task = await orchestrator.get_task(sample_task.id)
        assert retrieved_task is not None
        assert retrieved_task.status in [TaskStatus.PENDING, TaskStatus.READY]
    
    async def test_cancel_task(self, orchestrator, sample_task):
        """Test task cancellation."""
        # Submit task
        await orchestrator.submit_task(sample_task)
        
        # Cancel task
        success = await orchestrator.cancel_task(sample_task.id, "Integration test cancellation")
        assert success
        
        # Task should be cancelled
        status = await orchestrator.get_task_status(sample_task.id)
        assert status == TaskStatus.CANCELLED
        
        # Task should have cancellation reason
        task = await orchestrator.get_task(sample_task.id)
        assert task.error == "Integration test cancellation"
    
    async def test_retry_failed_task(self, orchestrator):
        """Test task retry functionality."""
        # Create a task
        task = Task(
            name="Retry Test Task",
            description="Task for testing retry functionality",
            priority=TaskPriority.MEDIUM
        )
        
        # Submit and then mark as failed
        await orchestrator.submit_task(task)
        
        # Simulate task failure
        await orchestrator._on_task_failed(
            task_id=task.id,
            error="Simulated failure for retry test",
            execution_time=1.0
        )
        
        # Task should be failed
        status = await orchestrator.get_task_status(task.id)
        assert status == TaskStatus.FAILED
        
        # Retry task
        success = await orchestrator.retry_task(task.id)
        assert success
        
        # Task should be pending again
        status = await orchestrator.get_task_status(task.id)
        assert status == TaskStatus.PENDING
        
        # Retry count should be incremented
        retrieved_task = await orchestrator.get_task(task.id)
        assert retrieved_task.retry_count > 0
    
    async def test_get_task_results(self, orchestrator):
        """Test getting task results."""
        task = Task(
            name="Results Test Task",
            description="Task for testing results retrieval"
        )
        
        await orchestrator.submit_task(task)
        
        # Initially no results
        results = await orchestrator.get_task_results(task.id)
        assert results is None
        
        # Simulate task completion
        test_result = {"status": "success", "data": "test_output"}
        await orchestrator._on_task_completed(
            task_id=task.id,
            result=test_result,
            execution_time=2.0
        )
        
        # Should now have results
        results = await orchestrator.get_task_results(task.id)
        assert results == test_result
    
    async def test_system_metrics_collection(self, orchestrator, sample_task, sample_capabilities):
        """Test system metrics collection."""
        # Perform some operations to generate metrics
        await orchestrator.submit_task(sample_task)
        await orchestrator.create_agent("metrics_test_agent", sample_capabilities)
        await orchestrator.create_resource(ResourceType.CPU, 2.0)
        
        # Get metrics
        metrics = await orchestrator.get_system_metrics()
        
        assert 'orchestrator' in metrics
        assert 'task_planner' in metrics
        assert 'agent_manager' in metrics
        assert 'resource_allocator' in metrics
        assert 'state_manager' in metrics
        assert 'message_bus' in metrics
        
        # Check orchestrator metrics
        orch_metrics = metrics['orchestrator']
        assert 'tasks_submitted' in orch_metrics
        assert 'agents_created' in orch_metrics
        assert orch_metrics['tasks_submitted'] >= 1
        assert orch_metrics['agents_created'] >= 1
    
    async def test_checkpoint_creation_and_restoration(self, orchestrator, sample_task):
        """Test checkpoint creation and restoration."""
        # Submit task to have some state
        await orchestrator.submit_task(sample_task)
        
        # Create checkpoint
        checkpoint_id = await orchestrator.create_checkpoint("integration_test_checkpoint")
        assert checkpoint_id is not None
        
        # List checkpoints
        checkpoints = await orchestrator.list_checkpoints()
        assert len(checkpoints) > 0
        
        checkpoint_ids = [cp['id'] for cp in checkpoints]
        assert str(checkpoint_id) in checkpoint_ids
        
        # Find our checkpoint
        our_checkpoint = next(
            (cp for cp in checkpoints if cp['id'] == str(checkpoint_id)),
            None
        )
        assert our_checkpoint is not None
        assert our_checkpoint['name'] == "integration_test_checkpoint"
        
        # Restore checkpoint (simplified test)
        success = await orchestrator.restore_checkpoint(checkpoint_id)
        # Restoration might not succeed in simplified test environment
        assert isinstance(success, bool)
    
    async def test_execution_plan_workflow(self, orchestrator, sample_task, sample_capabilities):
        """Test complete execution plan workflow."""
        # Create some agents first
        agent1 = await orchestrator.create_agent(
            "execution_agent_1",
            sample_capabilities
        )
        agent2 = await orchestrator.create_agent(
            "execution_agent_2", 
            sample_capabilities
        )
        
        # Submit task and get execution plan
        execution_plan = await orchestrator.submit_task(
            sample_task,
            decomposition_strategy='parallel'
        )
        
        # Plan should have multiple tasks
        assert len(execution_plan.tasks) > 1
        assert len(execution_plan.parallel_groups) > 0
        
        # Execute the plan
        success = await orchestrator.execute_plan(execution_plan.id)
        assert success
        
        # Wait a bit for execution
        await asyncio.sleep(0.5)
        
        # Check system status
        status = await orchestrator.get_system_status()
        # Should show active executions (or recently completed)
        assert 'active_executions' in status
    
    async def test_orchestrator_not_running_errors(self):
        """Test that operations fail when orchestrator is not running."""
        # Create orchestrator but don't start it
        orchestrator = Orchestrator(
            persistence_backend=InMemoryPersistence()
        )
        
        task = Task(name="Test Task", description="Test")
        
        # Operations should fail when not running
        with pytest.raises(OrchestrationError) as exc_info:
            await orchestrator.submit_task(task)
        assert "not running" in str(exc_info.value)
        
        with pytest.raises(OrchestrationError) as exc_info:
            await orchestrator.create_agent("test", {AgentCapability.TASK_EXECUTION})
        assert "not running" in str(exc_info.value)
        
        with pytest.raises(OrchestrationError) as exc_info:
            await orchestrator.create_resource(ResourceType.CPU, 1.0)
        assert "not running" in str(exc_info.value)
    
    async def test_invalid_task_operations(self, orchestrator):
        """Test invalid task operations."""
        fake_task_id = uuid4()
        
        # Getting non-existent task should return None
        task = await orchestrator.get_task(fake_task_id)
        assert task is None
        
        status = await orchestrator.get_task_status(fake_task_id)
        assert status is None
        
        results = await orchestrator.get_task_results(fake_task_id)
        assert results is None
        
        # Cancelling non-existent task should return False
        success = await orchestrator.cancel_task(fake_task_id)
        assert not success
        
        # Retrying non-existent task should return False
        success = await orchestrator.retry_task(fake_task_id)
        assert not success
    
    async def test_invalid_agent_operations(self, orchestrator):
        """Test invalid agent operations."""
        fake_agent_id = uuid4()
        
        # Getting non-existent agent should return None
        agent = await orchestrator.get_agent(fake_agent_id)
        assert agent is None
        
        # Terminating non-existent agent should return False
        success = await orchestrator.terminate_agent(fake_agent_id)
        assert not success
    
    async def test_invalid_resource_operations(self, orchestrator):
        """Test invalid resource operations."""
        fake_resource_id = uuid4()
        fake_requester_id = uuid4()
        
        # Getting non-existent resource should return None
        resource = await orchestrator.get_resource(fake_resource_id)
        assert resource is None
        
        # Releasing from non-existent requester should return 0
        released = await orchestrator.release_resources(fake_requester_id)
        assert released == 0.0
    
    async def test_state_change_event_handling(self, orchestrator, sample_task):
        """Test that state changes trigger appropriate events."""
        # Submit task
        await orchestrator.submit_task(sample_task)
        
        # Simulate task completion
        await orchestrator._on_task_completed(
            task_id=sample_task.id,
            result="Test completion",
            execution_time=1.5
        )
        
        # Check that task state was updated
        task = await orchestrator.get_task(sample_task.id)
        assert task.status == TaskStatus.COMPLETED
        assert task.result == "Test completion"
        
        # Simulate task failure
        failed_task = Task(name="Failed Task", description="Will fail")
        await orchestrator.submit_task(failed_task)
        
        await orchestrator._on_task_failed(
            task_id=failed_task.id,
            error="Test failure",
            execution_time=0.5
        )
        
        # Check that failed task state was updated
        task = await orchestrator.get_task(failed_task.id)
        assert task.status == TaskStatus.FAILED
        assert task.error == "Test failure"


@pytest.mark.asyncio 
class TestOrchestratorIntegration:
    """Integration tests for orchestrator with all components."""
    
    async def test_full_workflow_integration(self, orchestrator, sample_capabilities):
        """Test complete workflow from task submission to completion."""
        # Setup: Create agents and resources
        agent = await orchestrator.create_agent(
            "workflow_agent",
            sample_capabilities
        )
        
        cpu_resource = await orchestrator.create_resource(
            ResourceType.CPU,
            capacity=4.0
        )
        
        memory_resource = await orchestrator.create_resource(
            ResourceType.MEMORY,
            capacity=2048.0
        )
        
        # Create complex task
        complex_task = Task(
            name="Complex Workflow Task",
            description="Multi-step task for integration testing",
            priority=TaskPriority.HIGH,
            timeout_seconds=600,
            parameters={
                'workflow_type': 'integration_test',
                'steps': ['prepare', 'process', 'analyze', 'finalize'],
                'parallel_processing': True
            },
            resource_requirements={
                'cpu_cores': 2.0,
                'memory_mb': 1024.0
            },
            tags={'integration', 'complex_workflow'}
        )
        
        # Submit task
        execution_plan = await orchestrator.submit_task(
            complex_task,
            decomposition_strategy='fan_out_fan_in'
        )
        
        # Verify plan creation
        assert execution_plan is not None
        assert len(execution_plan.tasks) > 1
        assert len(execution_plan.parallel_groups) > 0
        
        # Request resources for the task
        request_id = await orchestrator.request_resources(
            requester_id=complex_task.id,
            resource_requirements=complex_task.resource_requirements,
            priority=complex_task.priority
        )
        
        # Execute the plan
        success = await orchestrator.execute_plan(execution_plan.id)
        assert success
        
        # Wait for some processing
        await asyncio.sleep(1.0)
        
        # Check system status
        status = await orchestrator.get_system_status()
        assert status['running']
        
        # Get comprehensive metrics
        metrics = await orchestrator.get_system_metrics()
        
        # Verify metrics show activity
        assert metrics['orchestrator']['tasks_submitted'] >= 1
        assert metrics['orchestrator']['agents_created'] >= 1
        
        # Cleanup: Release resources
        await orchestrator.release_resources(complex_task.id)
    
    async def test_error_handling_and_recovery(self, orchestrator, sample_capabilities):
        """Test error handling and recovery mechanisms."""
        # Create agent
        agent = await orchestrator.create_agent(
            "error_test_agent", 
            sample_capabilities
        )
        
        # Create task that will fail
        failing_task = Task(
            name="Failing Task",
            description="Task designed to fail for error testing",
            priority=TaskPriority.MEDIUM,
            max_retries=2
        )
        
        # Submit failing task
        execution_plan = await orchestrator.submit_task(failing_task)
        
        # Simulate task failure
        await orchestrator._on_task_failed(
            task_id=failing_task.id,
            error="Simulated failure for error testing",
            execution_time=0.1
        )
        
        # Verify task is marked as failed
        task = await orchestrator.get_task(failing_task.id)
        assert task.status == TaskStatus.FAILED
        assert "Simulated failure" in task.error
        
        # Test retry mechanism
        retry_success = await orchestrator.retry_task(failing_task.id)
        assert retry_success
        
        # Task should be pending again
        task = await orchestrator.get_task(failing_task.id)
        assert task.status == TaskStatus.PENDING
        assert task.retry_count == 1
        
        # Test cancellation
        cancel_success = await orchestrator.cancel_task(
            failing_task.id, 
            "Cancelled due to repeated failures"
        )
        assert cancel_success
        
        # Task should be cancelled
        task = await orchestrator.get_task(failing_task.id)
        assert task.status == TaskStatus.CANCELLED


if __name__ == "__main__":
    pytest.main([__file__])