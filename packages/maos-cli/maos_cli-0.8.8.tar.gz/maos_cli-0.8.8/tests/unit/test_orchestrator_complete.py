"""
Comprehensive unit tests for the Orchestrator component.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import UUID, uuid4
from datetime import datetime
import tempfile
import os

from maos.core.orchestrator import Orchestrator, MAOSEventHandler
from maos.models.task import Task, TaskStatus, TaskPriority
from maos.models.agent import Agent, AgentStatus, AgentCapability
from maos.models.resource import Resource, ResourceType
from maos.models.message import Message, MessageType, MessagePriority
from maos.core.swarm_coordinator import SwarmPattern, CoordinationStrategy
from maos.interfaces.persistence import FilePersistence
from maos.utils.exceptions import (
    OrchestrationError, TaskError, AgentError, ResourceError
)


@pytest.fixture
async def temp_storage():
    """Create temporary storage directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
async def orchestrator(temp_storage):
    """Create an orchestrator instance for testing."""
    config = {
        'storage_directory': temp_storage,
        'state_manager': {
            'auto_checkpoint_interval': 300,
            'max_snapshots': 5
        },
        'agent_manager': {
            'max_agents': 10,
            'enable_monitoring': False
        },
        'task_planner': {
            'max_depth': 3,
            'max_subtasks': 10
        }
    }
    
    orchestrator = Orchestrator(
        persistence_backend=FilePersistence(temp_storage),
        component_config=config,
        use_redis=False
    )
    
    await orchestrator.start()
    yield orchestrator
    await orchestrator.shutdown()


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    return Task(
        name="Test Task",
        description="A test task for unit testing",
        priority=TaskPriority.MEDIUM,
        metadata={'test': True}
    )


@pytest.fixture
def sample_agent():
    """Create a sample agent for testing."""
    return Agent(
        name="Test Agent",
        type="test",
        capabilities={AgentCapability.TASK_EXECUTION},
        metadata={'test': True}
    )


class TestOrchestratorInitialization:
    """Test orchestrator initialization and configuration."""
    
    async def test_init_with_default_config(self, temp_storage):
        """Test initialization with default configuration."""
        orchestrator = Orchestrator(
            persistence_backend=FilePersistence(temp_storage)
        )
        
        assert orchestrator is not None
        assert not orchestrator._running
        assert orchestrator.state_manager is not None
        assert orchestrator.message_bus is not None
        assert orchestrator.task_planner is not None
        assert orchestrator.agent_manager is not None
        assert orchestrator.resource_allocator is not None
    
    async def test_init_with_custom_config(self, temp_storage):
        """Test initialization with custom configuration."""
        config = {
            'state_manager': {'auto_checkpoint_interval': 600},
            'agent_manager': {'max_agents': 20},
            'use_redis': False
        }
        
        orchestrator = Orchestrator(
            persistence_backend=FilePersistence(temp_storage),
            component_config=config
        )
        
        assert orchestrator.component_config == config
        assert not orchestrator.use_redis
    
    async def test_start_and_shutdown(self, orchestrator):
        """Test orchestrator start and shutdown."""
        assert orchestrator._running
        assert orchestrator._startup_time is not None
        
        await orchestrator.shutdown()
        assert not orchestrator._running
    
    async def test_double_start(self, orchestrator):
        """Test that starting an already running orchestrator is safe."""
        await orchestrator.start()  # Should be a no-op
        assert orchestrator._running
    
    async def test_double_shutdown(self, orchestrator):
        """Test that shutting down twice is safe."""
        await orchestrator.shutdown()
        await orchestrator.shutdown()  # Should be a no-op
        assert not orchestrator._running


class TestTaskManagement:
    """Test task management functionality."""
    
    async def test_submit_task(self, orchestrator, sample_task):
        """Test submitting a task for execution."""
        plan = await orchestrator.submit_task(sample_task)
        
        assert plan is not None
        assert plan.id is not None
        assert sample_task.id in plan.tasks
        assert orchestrator._metrics['tasks_submitted'] == 1
    
    async def test_submit_task_when_not_running(self, temp_storage, sample_task):
        """Test submitting task when orchestrator is not running."""
        orchestrator = Orchestrator(
            persistence_backend=FilePersistence(temp_storage)
        )
        
        with pytest.raises(OrchestrationError, match="not running"):
            await orchestrator.submit_task(sample_task)
    
    async def test_get_task(self, orchestrator, sample_task):
        """Test retrieving a task by ID."""
        await orchestrator.submit_task(sample_task)
        
        retrieved_task = await orchestrator.get_task(sample_task.id)
        assert retrieved_task is not None
        assert retrieved_task.id == sample_task.id
        assert retrieved_task.name == sample_task.name
    
    async def test_get_nonexistent_task(self, orchestrator):
        """Test getting a task that doesn't exist."""
        task = await orchestrator.get_task(uuid4())
        assert task is None
    
    async def test_get_task_status(self, orchestrator, sample_task):
        """Test getting task status."""
        await orchestrator.submit_task(sample_task)
        
        status = await orchestrator.get_task_status(sample_task.id)
        assert status == TaskStatus.PENDING
    
    async def test_cancel_task(self, orchestrator, sample_task):
        """Test canceling a task."""
        await orchestrator.submit_task(sample_task)
        
        success = await orchestrator.cancel_task(sample_task.id, "Test cancellation")
        assert success
        
        task = await orchestrator.get_task(sample_task.id)
        assert task.status == TaskStatus.CANCELLED
        assert task.error == "Test cancellation"
    
    async def test_cancel_nonexistent_task(self, orchestrator):
        """Test canceling a task that doesn't exist."""
        success = await orchestrator.cancel_task(uuid4())
        assert not success
    
    async def test_retry_failed_task(self, orchestrator, sample_task):
        """Test retrying a failed task."""
        await orchestrator.submit_task(sample_task)
        
        # Manually fail the task
        task = await orchestrator.get_task(sample_task.id)
        task.update_status(TaskStatus.FAILED)
        task.error = "Test failure"
        await orchestrator.state_manager.store_object('tasks', task)
        
        # Retry the task
        success = await orchestrator.retry_task(sample_task.id)
        assert success
        
        task = await orchestrator.get_task(sample_task.id)
        assert task.status == TaskStatus.PENDING
        assert task.retry_count == 1
        assert task.error is None
    
    async def test_get_task_results(self, orchestrator, sample_task):
        """Test getting results of a completed task."""
        await orchestrator.submit_task(sample_task)
        
        # Complete the task
        task = await orchestrator.get_task(sample_task.id)
        task.update_status(TaskStatus.COMPLETED)
        task.result = {"success": True, "data": "test"}
        await orchestrator.state_manager.store_object('tasks', task)
        
        results = await orchestrator.get_task_results(sample_task.id)
        assert results == {"success": True, "data": "test"}
    
    async def test_get_results_of_incomplete_task(self, orchestrator, sample_task):
        """Test getting results of an incomplete task."""
        await orchestrator.submit_task(sample_task)
        
        results = await orchestrator.get_task_results(sample_task.id)
        assert results is None


class TestAgentManagement:
    """Test agent management functionality."""
    
    async def test_create_agent(self, orchestrator):
        """Test creating a new agent."""
        agent = await orchestrator.create_agent(
            agent_type="test",
            capabilities={AgentCapability.TASK_EXECUTION},
            configuration={'test': True}
        )
        
        assert agent is not None
        assert agent.id is not None
        assert agent.type == "test"
        assert AgentCapability.TASK_EXECUTION in agent.capabilities
        assert orchestrator._metrics['agents_created'] == 1
    
    async def test_create_agent_when_not_running(self, temp_storage):
        """Test creating agent when orchestrator is not running."""
        orchestrator = Orchestrator(
            persistence_backend=FilePersistence(temp_storage)
        )
        
        with pytest.raises(OrchestrationError, match="not running"):
            await orchestrator.create_agent(
                agent_type="test",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
    
    async def test_get_agent(self, orchestrator):
        """Test retrieving an agent by ID."""
        agent = await orchestrator.create_agent(
            agent_type="test",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        retrieved_agent = await orchestrator.get_agent(agent.id)
        assert retrieved_agent is not None
        assert retrieved_agent.id == agent.id
    
    async def test_get_available_agents(self, orchestrator):
        """Test getting available agents."""
        # Create multiple agents
        agents = []
        for i in range(3):
            agent = await orchestrator.create_agent(
                agent_type=f"test_{i}",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
            agents.append(agent)
        
        available = await orchestrator.get_available_agents()
        assert len(available) == 3
    
    async def test_get_agents_with_capabilities(self, orchestrator):
        """Test getting agents with specific capabilities."""
        # Create agents with different capabilities
        agent1 = await orchestrator.create_agent(
            agent_type="test1",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        agent2 = await orchestrator.create_agent(
            agent_type="test2",
            capabilities={AgentCapability.TASK_EXECUTION, AgentCapability.MONITORING}
        )
        
        # Get agents with monitoring capability
        available = await orchestrator.get_available_agents(
            required_capabilities={AgentCapability.MONITORING}
        )
        
        assert len(available) == 1
        assert available[0].id == agent2.id
    
    async def test_terminate_agent(self, orchestrator):
        """Test terminating an agent."""
        agent = await orchestrator.create_agent(
            agent_type="test",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        success = await orchestrator.terminate_agent(agent.id, "Test termination")
        assert success
        
        # Verify agent is removed from state
        retrieved_agent = await orchestrator.get_agent(agent.id)
        assert retrieved_agent is None


class TestResourceManagement:
    """Test resource management functionality."""
    
    async def test_create_resource(self, orchestrator):
        """Test creating a new resource."""
        resource = await orchestrator.create_resource(
            resource_type=ResourceType.CPU,
            capacity=4.0,
            configuration={'cores': 4}
        )
        
        assert resource is not None
        assert resource.id is not None
        assert resource.type == ResourceType.CPU
        assert resource.capacity == 4.0
    
    async def test_get_resource(self, orchestrator):
        """Test retrieving a resource by ID."""
        resource = await orchestrator.create_resource(
            resource_type=ResourceType.MEMORY,
            capacity=8.0
        )
        
        retrieved = await orchestrator.get_resource(resource.id)
        assert retrieved is not None
        assert retrieved.id == resource.id
        assert retrieved.capacity == 8.0
    
    async def test_request_resources(self, orchestrator):
        """Test requesting resource allocation."""
        # Create resources
        await orchestrator.create_resource(
            resource_type=ResourceType.CPU,
            capacity=4.0
        )
        
        # Request allocation
        requester_id = uuid4()
        request_id = await orchestrator.request_resources(
            requester_id=requester_id,
            resource_requirements={'cpu': 2.0},
            priority=TaskPriority.HIGH
        )
        
        assert request_id is not None
        assert orchestrator._metrics['resources_allocated'] == 1
    
    async def test_release_resources(self, orchestrator):
        """Test releasing allocated resources."""
        # Create and allocate resources
        resource = await orchestrator.create_resource(
            resource_type=ResourceType.CPU,
            capacity=4.0
        )
        
        requester_id = uuid4()
        request_id = await orchestrator.request_resources(
            requester_id=requester_id,
            resource_requirements={'cpu': 2.0}
        )
        
        # Release resources
        released = await orchestrator.release_resources(
            requester_id=requester_id,
            resource_id=resource.id
        )
        
        assert released >= 0


class TestEventHandler:
    """Test event handler functionality."""
    
    async def test_handle_task_completion(self, orchestrator):
        """Test handling task completion event."""
        task = Task(name="Test", description="Test task")
        await orchestrator.state_manager.store_object('tasks', task)
        
        message = Message(
            type=MessageType.TASK_COMPLETION,
            payload={
                'task_id': str(task.id),
                'result': {'success': True},
                'execution_time': 1.5
            }
        )
        
        await orchestrator._event_handler.handle_message(message)
        
        # Verify task was updated
        updated_task = await orchestrator.get_task(task.id)
        assert updated_task.status == TaskStatus.COMPLETED
        assert updated_task.result == {'success': True}
    
    async def test_handle_task_failure(self, orchestrator):
        """Test handling task failure event."""
        task = Task(name="Test", description="Test task")
        await orchestrator.state_manager.store_object('tasks', task)
        
        message = Message(
            type=MessageType.TASK_FAILURE,
            payload={
                'task_id': str(task.id),
                'error': 'Test error',
                'execution_time': 0.5
            }
        )
        
        await orchestrator._event_handler.handle_message(message)
        
        # Verify task was updated
        updated_task = await orchestrator.get_task(task.id)
        assert updated_task.status == TaskStatus.FAILED
        assert updated_task.error == 'Test error'
    
    async def test_handle_heartbeat(self, orchestrator):
        """Test handling agent heartbeat."""
        agent = await orchestrator.create_agent(
            agent_type="test",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        message = Message(
            type=MessageType.HEARTBEAT,
            sender_id=agent.id,
            payload={
                'cpu_usage': 25.5,
                'memory_usage': 512.0
            }
        )
        
        await orchestrator._event_handler.handle_message(message)
        
        # Verify agent metrics were updated
        retrieved_agent = await orchestrator.get_agent(agent.id)
        assert retrieved_agent.metrics.cpu_usage == 25.5
        assert retrieved_agent.metrics.memory_usage == 512.0
    
    async def test_get_supported_message_types(self, orchestrator):
        """Test getting supported message types."""
        supported = orchestrator._event_handler.get_supported_message_types()
        
        assert MessageType.TASK_COMPLETION in supported
        assert MessageType.TASK_FAILURE in supported
        assert MessageType.HEARTBEAT in supported
        assert MessageType.ERROR_REPORT in supported
        assert MessageType.RESOURCE_REQUEST in supported
        assert MessageType.STATUS_UPDATE in supported


class TestSystemStatus:
    """Test system status and metrics functionality."""
    
    async def test_get_system_status(self, orchestrator):
        """Test getting system status."""
        status = await orchestrator.get_system_status()
        
        assert status['running'] is True
        assert status['uptime_seconds'] >= 0
        assert status['startup_time'] is not None
        assert 'components' in status
        assert status['components']['state_manager'] == 'running'
        assert status['components']['message_bus'] == 'running'
    
    async def test_get_system_metrics(self, orchestrator):
        """Test getting system metrics."""
        # Generate some activity
        task = Task(name="Test", description="Test task")
        await orchestrator.submit_task(task)
        
        metrics = await orchestrator.get_system_metrics()
        
        assert 'orchestrator' in metrics
        assert metrics['orchestrator']['tasks_submitted'] >= 1
        assert 'task_planner' in metrics
        assert 'agent_manager' in metrics
        assert 'resource_allocator' in metrics
        assert 'state_manager' in metrics
        assert 'message_bus' in metrics
    
    async def test_get_component_health(self, orchestrator):
        """Test getting component health status."""
        health = await orchestrator.get_component_health()
        
        assert health['orchestrator'] == 'healthy'
        assert health['state_manager'] == 'healthy'
        assert health['message_bus'] == 'healthy'
        assert health['task_planner'] == 'healthy'
        assert health['agent_manager'] == 'healthy'
        assert health['resource_allocator'] == 'healthy'


class TestCheckpointManagement:
    """Test checkpoint and state management functionality."""
    
    async def test_create_checkpoint(self, orchestrator):
        """Test creating a checkpoint."""
        checkpoint_id = await orchestrator.create_checkpoint("test-checkpoint")
        
        assert checkpoint_id is not None
        assert isinstance(checkpoint_id, UUID)
    
    async def test_list_checkpoints(self, orchestrator):
        """Test listing checkpoints."""
        # Create multiple checkpoints
        await orchestrator.create_checkpoint("checkpoint-1")
        await orchestrator.create_checkpoint("checkpoint-2")
        
        checkpoints = await orchestrator.list_checkpoints()
        
        assert len(checkpoints) >= 2
        assert all('id' in cp for cp in checkpoints)
        assert all('name' in cp for cp in checkpoints)
        assert all('created_at' in cp for cp in checkpoints)
    
    async def test_restore_checkpoint(self, orchestrator):
        """Test restoring from a checkpoint."""
        # Create initial state
        task = Task(name="Test", description="Test task")
        await orchestrator.submit_task(task)
        
        # Create checkpoint
        checkpoint_id = await orchestrator.create_checkpoint("test-restore")
        
        # Modify state
        task2 = Task(name="Test2", description="Another task")
        await orchestrator.submit_task(task2)
        
        # Restore checkpoint
        success = await orchestrator.restore_checkpoint(checkpoint_id)
        assert success


class TestSwarmCoordination:
    """Test swarm coordination functionality."""
    
    async def test_create_agent_swarm(self, orchestrator):
        """Test creating an agent swarm."""
        swarm_id = await orchestrator.create_agent_swarm(
            name="test-swarm",
            pattern=SwarmPattern.HUB_AND_SPOKE,
            strategy=CoordinationStrategy.CAPABILITY_BASED,
            min_agents=2,
            max_agents=5
        )
        
        assert swarm_id is not None
        assert isinstance(swarm_id, UUID)
    
    async def test_execute_swarm_task(self, orchestrator, sample_task):
        """Test executing a task with a swarm."""
        swarm_id = await orchestrator.create_agent_swarm(
            name="test-swarm",
            pattern=SwarmPattern.STAR,
            min_agents=2
        )
        
        results = await orchestrator.execute_swarm_task(
            swarm_id=swarm_id,
            task=sample_task,
            execution_mode="parallel"
        )
        
        assert results is not None
        assert 'swarm_task_id' in results or 'results' in results
    
    async def test_get_swarm_status(self, orchestrator):
        """Test getting swarm status."""
        swarm_id = await orchestrator.create_agent_swarm(
            name="test-swarm",
            min_agents=1
        )
        
        status = await orchestrator.get_swarm_status(swarm_id)
        assert status is not None
    
    async def test_shutdown_swarm(self, orchestrator):
        """Test shutting down a swarm."""
        swarm_id = await orchestrator.create_agent_swarm(
            name="test-swarm",
            min_agents=1
        )
        
        await orchestrator.shutdown_swarm(swarm_id)
        
        # Verify swarm is shut down
        status = await orchestrator.get_swarm_status(swarm_id)
        assert status is None or status.get('active') is False


class TestExecutionPlans:
    """Test execution plan functionality."""
    
    async def test_get_execution_plan(self, orchestrator, sample_task):
        """Test retrieving an execution plan."""
        plan = await orchestrator.submit_task(sample_task)
        
        retrieved_plan = await orchestrator.get_execution_plan(plan.id)
        assert retrieved_plan is not None
        assert retrieved_plan.id == plan.id
    
    async def test_execute_plan(self, orchestrator, sample_task):
        """Test executing a plan."""
        plan = await orchestrator.submit_task(sample_task)
        
        success = await orchestrator.execute_plan(plan.id)
        assert success
        
        # Verify plan is in active executions
        assert plan.id in orchestrator._active_executions
    
    async def test_execute_nonexistent_plan(self, orchestrator):
        """Test executing a plan that doesn't exist."""
        with pytest.raises(OrchestrationError, match="Execution plan not found"):
            await orchestrator.execute_plan(uuid4())


class TestErrorHandling:
    """Test error handling in various scenarios."""
    
    async def test_task_submission_error(self, orchestrator):
        """Test error handling during task submission."""
        # Mock task planner to raise an error
        with patch.object(orchestrator.task_planner, 'create_execution_plan', 
                         side_effect=Exception("Planning error")):
            task = Task(name="Test", description="Test task")
            
            with pytest.raises(TaskError, match="Failed to submit task"):
                await orchestrator.submit_task(task)
    
    async def test_agent_creation_error(self, orchestrator):
        """Test error handling during agent creation."""
        # Mock agent manager to raise an error
        with patch.object(orchestrator.agent_manager, 'spawn_agent',
                         side_effect=Exception("Spawn error")):
            
            with pytest.raises(AgentError, match="Failed to create agent"):
                await orchestrator.create_agent(
                    agent_type="test",
                    capabilities={AgentCapability.TASK_EXECUTION}
                )
    
    async def test_resource_creation_error(self, orchestrator):
        """Test error handling during resource creation."""
        # Mock resource allocator to raise an error
        with patch.object(orchestrator.resource_allocator, 'create_resource',
                         side_effect=Exception("Resource error")):
            
            with pytest.raises(ResourceError, match="Failed to create resource"):
                await orchestrator.create_resource(
                    resource_type=ResourceType.CPU,
                    capacity=4.0
                )
    
    async def test_checkpoint_creation_error(self, orchestrator):
        """Test error handling during checkpoint creation."""
        # Mock state manager to raise an error
        with patch.object(orchestrator.state_manager, 'create_checkpoint',
                         side_effect=Exception("Checkpoint error")):
            
            with pytest.raises(OrchestrationError, match="Failed to create checkpoint"):
                await orchestrator.create_checkpoint("test")


@pytest.mark.asyncio
async def test_full_workflow(orchestrator):
    """Test a complete workflow from task submission to completion."""
    # Create agents
    agents = []
    for i in range(3):
        agent = await orchestrator.create_agent(
            agent_type=f"worker_{i}",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        agents.append(agent)
    
    # Create resources
    cpu_resource = await orchestrator.create_resource(
        resource_type=ResourceType.CPU,
        capacity=8.0
    )
    
    memory_resource = await orchestrator.create_resource(
        resource_type=ResourceType.MEMORY,
        capacity=16.0
    )
    
    # Submit a task
    task = Task(
        name="Complex Task",
        description="A complex task requiring multiple agents",
        priority=TaskPriority.HIGH,
        metadata={
            'subtasks': [
                {'name': 'subtask1', 'description': 'First subtask'},
                {'name': 'subtask2', 'description': 'Second subtask'}
            ]
        }
    )
    
    plan = await orchestrator.submit_task(task)
    assert plan is not None
    
    # Execute the plan
    success = await orchestrator.execute_plan(plan.id)
    assert success
    
    # Create a checkpoint
    checkpoint_id = await orchestrator.create_checkpoint("workflow-checkpoint")
    assert checkpoint_id is not None
    
    # Get system status
    status = await orchestrator.get_system_status()
    assert status['running'] is True
    assert status['active_executions'] > 0
    
    # Get metrics
    metrics = await orchestrator.get_system_metrics()
    assert metrics['orchestrator']['tasks_submitted'] >= 1
    assert metrics['orchestrator']['agents_created'] >= 3
    
    # Clean up
    for agent in agents:
        await orchestrator.terminate_agent(agent.id)