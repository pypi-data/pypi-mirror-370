"""
Comprehensive unit tests for the Agent Manager component.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import time

from maos.core.agent_manager import (
    AgentManager, AgentPool, LoadBalancingStrategy
)
from maos.models.agent import Agent, AgentStatus, AgentCapability, AgentMetrics
from maos.models.task import Task, TaskStatus, TaskPriority
from maos.models.message import Message, MessageType
from maos.utils.exceptions import (
    AgentError, AgentNotFoundError, AgentNotAvailableError,
    AgentCapabilityError, AgentHealthError
)


@pytest.fixture
async def agent_manager():
    """Create an agent manager instance for testing."""
    manager = AgentManager(
        max_agents=10,
        health_check_interval=5,
        heartbeat_timeout=10,
        enable_monitoring=False,
        enable_auto_recovery=False,
        enable_claude_integration=False
    )
    
    await manager.start()
    yield manager
    await manager.shutdown()


@pytest.fixture
def sample_agent():
    """Create a sample agent for testing."""
    return Agent(
        name="Test Agent",
        type="worker",
        capabilities={AgentCapability.TASK_EXECUTION},
        metadata={'test': True}
    )


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    return Task(
        name="Test Task",
        description="A test task",
        priority=TaskPriority.MEDIUM,
        metadata={'test': True}
    )


class TestAgentManagerInitialization:
    """Test agent manager initialization and configuration."""
    
    async def test_init_with_default_config(self):
        """Test initialization with default configuration."""
        manager = AgentManager()
        
        assert manager.max_agents == 50
        assert manager.health_check_interval == 30
        assert manager.heartbeat_timeout == 90
        assert manager.enable_monitoring is True
        assert manager.enable_auto_recovery is True
    
    async def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        manager = AgentManager(
            max_agents=20,
            health_check_interval=10,
            heartbeat_timeout=30,
            enable_monitoring=False,
            enable_auto_recovery=False
        )
        
        assert manager.max_agents == 20
        assert manager.health_check_interval == 10
        assert manager.heartbeat_timeout == 30
        assert manager.enable_monitoring is False
        assert manager.enable_auto_recovery is False
    
    async def test_start_and_shutdown(self, agent_manager):
        """Test starting and shutting down the agent manager."""
        assert agent_manager._running
        
        await agent_manager.shutdown()
        assert not agent_manager._running
    
    async def test_double_start(self, agent_manager):
        """Test that starting twice is safe."""
        await agent_manager.start()  # Should be a no-op
        assert agent_manager._running
    
    async def test_double_shutdown(self, agent_manager):
        """Test that shutting down twice is safe."""
        await agent_manager.shutdown()
        await agent_manager.shutdown()  # Should be a no-op
        assert not agent_manager._running


class TestAgentLifecycle:
    """Test agent lifecycle management."""
    
    async def test_spawn_agent(self, agent_manager):
        """Test spawning a new agent."""
        agent = await agent_manager.spawn_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        assert agent is not None
        assert agent.id is not None
        assert agent.type == "worker"
        assert agent.status == AgentStatus.IDLE
        assert agent.id in agent_manager._agents
    
    async def test_spawn_agent_with_configuration(self, agent_manager):
        """Test spawning an agent with custom configuration."""
        config = {
            'max_concurrent_tasks': 5,
            'memory_limit': 1024,
            'custom_param': 'test'
        }
        
        agent = await agent_manager.spawn_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION},
            configuration=config
        )
        
        assert agent.max_concurrent_tasks == 5
        assert agent.metadata.get('memory_limit') == 1024
        assert agent.metadata.get('custom_param') == 'test'
    
    async def test_spawn_agent_exceeds_limit(self, agent_manager):
        """Test that spawning agents beyond limit raises error."""
        # Spawn max agents
        for i in range(agent_manager.max_agents):
            await agent_manager.spawn_agent(
                agent_type=f"worker_{i}",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
        
        # Try to spawn one more
        with pytest.raises(AgentError, match="Maximum agent limit reached"):
            await agent_manager.spawn_agent(
                agent_type="extra",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
    
    async def test_get_agent(self, agent_manager):
        """Test retrieving an agent by ID."""
        agent = await agent_manager.spawn_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        retrieved = await agent_manager.get_agent(agent.id)
        assert retrieved is not None
        assert retrieved.id == agent.id
    
    async def test_get_nonexistent_agent(self, agent_manager):
        """Test getting an agent that doesn't exist."""
        with pytest.raises(AgentNotFoundError):
            await agent_manager.get_agent(uuid4())
    
    async def test_terminate_agent(self, agent_manager):
        """Test terminating an agent."""
        agent = await agent_manager.spawn_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        success = await agent_manager.terminate_agent(agent.id, "Test termination")
        assert success
        assert agent.id not in agent_manager._agents
        
        # Verify agent can't be retrieved
        with pytest.raises(AgentNotFoundError):
            await agent_manager.get_agent(agent.id)
    
    async def test_terminate_nonexistent_agent(self, agent_manager):
        """Test terminating an agent that doesn't exist."""
        success = await agent_manager.terminate_agent(uuid4(), "Test")
        assert not success
    
    async def test_restart_agent(self, agent_manager):
        """Test restarting an agent."""
        agent = await agent_manager.spawn_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        original_start_time = agent.started_at
        
        # Restart the agent
        success = await agent_manager.restart_agent(agent.id)
        assert success
        
        # Verify agent was restarted
        restarted_agent = await agent_manager.get_agent(agent.id)
        assert restarted_agent.started_at > original_start_time
        assert restarted_agent.status == AgentStatus.IDLE


class TestTaskAssignment:
    """Test task assignment and management."""
    
    async def test_assign_task_to_agent(self, agent_manager, sample_task):
        """Test assigning a task to an agent."""
        agent = await agent_manager.spawn_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        assigned_agent_id = await agent_manager.assign_task(sample_task)
        assert assigned_agent_id == agent.id
        
        # Verify agent status
        agent = await agent_manager.get_agent(agent.id)
        assert agent.status == AgentStatus.BUSY
        assert agent.current_task_id == sample_task.id
    
    async def test_assign_task_no_available_agents(self, agent_manager, sample_task):
        """Test assigning task when no agents are available."""
        with pytest.raises(AgentNotAvailableError):
            await agent_manager.assign_task(sample_task)
    
    async def test_assign_task_with_capabilities(self, agent_manager):
        """Test assigning task based on required capabilities."""
        # Create agents with different capabilities
        agent1 = await agent_manager.spawn_agent(
            agent_type="worker1",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        agent2 = await agent_manager.spawn_agent(
            agent_type="worker2",
            capabilities={AgentCapability.TASK_EXECUTION, AgentCapability.MONITORING}
        )
        
        # Create task requiring monitoring capability
        task = Task(
            name="Monitor Task",
            description="Task requiring monitoring",
            required_capabilities={AgentCapability.MONITORING}
        )
        
        assigned_agent_id = await agent_manager.assign_task(task)
        assert assigned_agent_id == agent2.id
    
    async def test_complete_task(self, agent_manager, sample_task):
        """Test completing a task."""
        agent = await agent_manager.spawn_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        await agent_manager.assign_task(sample_task)
        
        # Complete the task
        await agent_manager.complete_task(
            task_id=sample_task.id,
            success=True,
            execution_time=1.5,
            result={'data': 'test'}
        )
        
        # Verify agent is idle again
        agent = await agent_manager.get_agent(agent.id)
        assert agent.status == AgentStatus.IDLE
        assert agent.current_task_id is None
        assert agent.completed_tasks == 1
    
    async def test_fail_task(self, agent_manager, sample_task):
        """Test failing a task."""
        agent = await agent_manager.spawn_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        await agent_manager.assign_task(sample_task)
        
        # Fail the task
        await agent_manager.complete_task(
            task_id=sample_task.id,
            success=False,
            execution_time=0.5,
            error="Test failure"
        )
        
        # Verify agent status
        agent = await agent_manager.get_agent(agent.id)
        assert agent.status == AgentStatus.IDLE
        assert agent.failed_tasks == 1
    
    async def test_reassign_task(self, agent_manager, sample_task):
        """Test reassigning a task to another agent."""
        agent1 = await agent_manager.spawn_agent(
            agent_type="worker1",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        agent2 = await agent_manager.spawn_agent(
            agent_type="worker2",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        # Assign to first agent
        await agent_manager.assign_task(sample_task)
        
        # Reassign to second agent
        new_agent_id = await agent_manager.reassign_task(sample_task.id, agent2.id)
        assert new_agent_id == agent2.id
        
        # Verify agents' states
        agent1 = await agent_manager.get_agent(agent1.id)
        agent2 = await agent_manager.get_agent(agent2.id)
        
        assert agent1.status == AgentStatus.IDLE
        assert agent2.status == AgentStatus.BUSY
        assert agent2.current_task_id == sample_task.id


class TestAgentPools:
    """Test agent pool functionality."""
    
    async def test_create_agent_pool(self, agent_manager):
        """Test creating an agent pool."""
        pool_id = await agent_manager.create_agent_pool(
            name="test-pool",
            capabilities={AgentCapability.TASK_EXECUTION},
            min_agents=2,
            max_agents=5
        )
        
        assert pool_id is not None
        assert pool_id in agent_manager._agent_pools
        
        pool = agent_manager._agent_pools[pool_id]
        assert pool.name == "test-pool"
        assert pool.min_agents == 2
        assert pool.max_agents == 5
    
    async def test_add_agent_to_pool(self, agent_manager):
        """Test adding an agent to a pool."""
        pool_id = await agent_manager.create_agent_pool(
            name="test-pool",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        agent = await agent_manager.spawn_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        success = await agent_manager.add_agent_to_pool(agent.id, pool_id)
        assert success
        
        pool = agent_manager._agent_pools[pool_id]
        assert agent.id in pool.agents
    
    async def test_remove_agent_from_pool(self, agent_manager):
        """Test removing an agent from a pool."""
        pool_id = await agent_manager.create_agent_pool(
            name="test-pool",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        agent = await agent_manager.spawn_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        await agent_manager.add_agent_to_pool(agent.id, pool_id)
        
        success = await agent_manager.remove_agent_from_pool(agent.id, pool_id)
        assert success
        
        pool = agent_manager._agent_pools[pool_id]
        assert agent.id not in pool.agents
    
    async def test_get_pool_status(self, agent_manager):
        """Test getting pool status."""
        pool_id = await agent_manager.create_agent_pool(
            name="test-pool",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        # Add agents to pool
        for i in range(3):
            agent = await agent_manager.spawn_agent(
                agent_type=f"worker_{i}",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
            await agent_manager.add_agent_to_pool(agent.id, pool_id)
        
        status = await agent_manager.get_pool_status(pool_id)
        
        assert status['name'] == "test-pool"
        assert status['agent_count'] == 3
        assert status['available_agents'] == 3
        assert status['load_factor'] == 0.0


class TestHealthMonitoring:
    """Test health monitoring functionality."""
    
    async def test_agent_heartbeat(self, agent_manager):
        """Test agent heartbeat processing."""
        agent = await agent_manager.spawn_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        # Process heartbeat
        await agent_manager.process_heartbeat(
            agent_id=agent.id,
            cpu_usage=25.5,
            memory_usage=512.0,
            active_tasks=1
        )
        
        # Verify metrics updated
        agent = await agent_manager.get_agent(agent.id)
        assert agent.metrics.cpu_usage == 25.5
        assert agent.metrics.memory_usage == 512.0
        assert agent.last_heartbeat is not None
    
    async def test_detect_unhealthy_agent(self, agent_manager):
        """Test detecting unhealthy agents."""
        agent = await agent_manager.spawn_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        # Simulate high resource usage
        await agent_manager.process_heartbeat(
            agent_id=agent.id,
            cpu_usage=95.0,
            memory_usage=2048.0,
            active_tasks=10
        )
        
        # Check health
        health_status = await agent_manager.check_agent_health(agent.id)
        assert health_status['healthy'] is False
        assert 'high_cpu' in health_status.get('issues', [])
    
    async def test_detect_stale_agent(self, agent_manager):
        """Test detecting stale agents (no heartbeat)."""
        agent = await agent_manager.spawn_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        # Set last heartbeat to past
        agent.last_heartbeat = datetime.utcnow() - timedelta(minutes=5)
        
        # Run health check
        unhealthy = await agent_manager.get_unhealthy_agents()
        assert agent.id in [a.id for a in unhealthy]
    
    async def test_auto_recovery(self):
        """Test automatic recovery of unhealthy agents."""
        manager = AgentManager(
            health_check_interval=1,
            heartbeat_timeout=2,
            enable_auto_recovery=True
        )
        await manager.start()
        
        try:
            agent = await manager.spawn_agent(
                agent_type="worker",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
            
            # Mark agent as error
            agent.update_status(AgentStatus.ERROR)
            agent.error = "Test error"
            
            # Wait for recovery
            await asyncio.sleep(2)
            
            # Check if agent was recovered
            recovered_agent = await manager.get_agent(agent.id)
            assert recovered_agent.status != AgentStatus.ERROR
            
        finally:
            await manager.shutdown()


class TestLoadBalancing:
    """Test load balancing strategies."""
    
    async def test_round_robin_assignment(self, agent_manager):
        """Test round-robin task assignment."""
        agent_manager.default_load_balancing = LoadBalancingStrategy.ROUND_ROBIN
        
        # Create multiple agents
        agents = []
        for i in range(3):
            agent = await agent_manager.spawn_agent(
                agent_type=f"worker_{i}",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
            agents.append(agent)
        
        # Assign tasks
        assigned_agents = []
        for i in range(6):
            task = Task(name=f"Task_{i}", description="Test")
            agent_id = await agent_manager.assign_task(task)
            assigned_agents.append(agent_id)
            await agent_manager.complete_task(task.id, True, 0.1, {})
        
        # Verify round-robin distribution
        assert assigned_agents[0] == agents[0].id
        assert assigned_agents[1] == agents[1].id
        assert assigned_agents[2] == agents[2].id
        assert assigned_agents[3] == agents[0].id
    
    async def test_least_loaded_assignment(self, agent_manager):
        """Test least-loaded task assignment."""
        agent_manager.default_load_balancing = LoadBalancingStrategy.LEAST_LOADED
        
        # Create agents with different loads
        agent1 = await agent_manager.spawn_agent(
            agent_type="worker1",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        agent2 = await agent_manager.spawn_agent(
            agent_type="worker2",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        # Give agent1 more completed tasks (higher load)
        agent1.completed_tasks = 5
        agent1.metrics.avg_task_time = 2.0
        
        agent2.completed_tasks = 1
        agent2.metrics.avg_task_time = 1.0
        
        # Assign new task
        task = Task(name="New Task", description="Test")
        assigned_agent_id = await agent_manager.assign_task(task)
        
        # Should assign to less loaded agent
        assert assigned_agent_id == agent2.id
    
    async def test_capability_based_assignment(self, agent_manager):
        """Test capability-based task assignment."""
        agent_manager.default_load_balancing = LoadBalancingStrategy.CAPABILITY_BASED
        
        # Create agents with different capabilities
        agent1 = await agent_manager.spawn_agent(
            agent_type="basic",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        agent2 = await agent_manager.spawn_agent(
            agent_type="advanced",
            capabilities={
                AgentCapability.TASK_EXECUTION,
                AgentCapability.MONITORING,
                AgentCapability.OPTIMIZATION
            }
        )
        
        # Task requiring specific capability
        task = Task(
            name="Complex Task",
            description="Test",
            required_capabilities={AgentCapability.OPTIMIZATION}
        )
        
        assigned_agent_id = await agent_manager.assign_task(task)
        assert assigned_agent_id == agent2.id


class TestMetrics:
    """Test metrics collection and reporting."""
    
    async def test_get_metrics(self, agent_manager):
        """Test getting agent manager metrics."""
        # Create some agents and assign tasks
        for i in range(3):
            agent = await agent_manager.spawn_agent(
                agent_type=f"worker_{i}",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
            
            task = Task(name=f"Task_{i}", description="Test")
            await agent_manager.assign_task(task)
            await agent_manager.complete_task(task.id, True, 1.0, {})
        
        metrics = agent_manager.get_metrics()
        
        assert metrics['total_agents'] == 3
        assert metrics['available_agents'] == 3
        assert metrics['tasks_assigned'] == 3
        assert metrics['tasks_completed'] == 3
        assert metrics['tasks_failed'] == 0
    
    async def test_get_agent_metrics(self, agent_manager):
        """Test getting individual agent metrics."""
        agent = await agent_manager.spawn_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        # Assign and complete tasks
        for i in range(5):
            task = Task(name=f"Task_{i}", description="Test")
            await agent_manager.assign_task(task)
            await agent_manager.complete_task(task.id, True, 1.0 + i * 0.5, {})
        
        metrics = await agent_manager.get_agent_metrics(agent.id)
        
        assert metrics['completed_tasks'] == 5
        assert metrics['failed_tasks'] == 0
        assert metrics['avg_task_time'] > 0
        assert metrics['status'] == 'IDLE'
    
    async def test_get_performance_report(self, agent_manager):
        """Test getting performance report."""
        # Create agents and complete tasks
        agents = []
        for i in range(2):
            agent = await agent_manager.spawn_agent(
                agent_type=f"worker_{i}",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
            agents.append(agent)
            
            # Complete tasks with different success rates
            for j in range(4):
                task = Task(name=f"Task_{i}_{j}", description="Test")
                await agent_manager.assign_task(task)
                success = (i == 0) or (j % 2 == 0)  # First agent always succeeds
                await agent_manager.complete_task(task.id, success, 1.0, {})
        
        report = await agent_manager.get_performance_report()
        
        assert 'summary' in report
        assert 'agent_performance' in report
        assert len(report['agent_performance']) == 2
        assert report['summary']['total_tasks'] == 8


class TestErrorHandling:
    """Test error handling in various scenarios."""
    
    async def test_spawn_agent_error(self, agent_manager):
        """Test error handling when spawning agent fails."""
        # Mock internal method to raise error
        with patch.object(agent_manager, '_create_agent_instance',
                         side_effect=Exception("Creation failed")):
            
            with pytest.raises(AgentError, match="Failed to spawn agent"):
                await agent_manager.spawn_agent(
                    agent_type="worker",
                    capabilities={AgentCapability.TASK_EXECUTION}
                )
    
    async def test_assign_task_to_terminated_agent(self, agent_manager, sample_task):
        """Test assigning task to a terminated agent."""
        agent = await agent_manager.spawn_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        # Terminate the agent
        await agent_manager.terminate_agent(agent.id)
        
        # Try to assign task
        with pytest.raises(AgentNotAvailableError):
            await agent_manager.assign_task(sample_task)
    
    async def test_complete_nonexistent_task(self, agent_manager):
        """Test completing a task that doesn't exist."""
        with pytest.raises(AgentError, match="Task not found"):
            await agent_manager.complete_task(uuid4(), True, 1.0, {})
    
    async def test_health_check_error(self, agent_manager):
        """Test error handling in health check."""
        agent = await agent_manager.spawn_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        # Mock health check to raise error
        with patch.object(agent, 'update_heartbeat',
                         side_effect=Exception("Health check failed")):
            
            # Should handle error gracefully
            health_status = await agent_manager.check_agent_health(agent.id)
            assert health_status['healthy'] is False


@pytest.mark.asyncio
async def test_concurrent_operations(agent_manager):
    """Test concurrent operations on agent manager."""
    
    async def spawn_and_assign():
        agent = await agent_manager.spawn_agent(
            agent_type=f"worker_{uuid4().hex[:8]}",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        task = Task(name=f"Task_{uuid4().hex[:8]}", description="Test")
        await agent_manager.assign_task(task)
        await asyncio.sleep(0.1)
        await agent_manager.complete_task(task.id, True, 0.1, {})
        
        return agent.id
    
    # Run multiple operations concurrently
    tasks = [spawn_and_assign() for _ in range(5)]
    agent_ids = await asyncio.gather(*tasks)
    
    # Verify all agents were created
    assert len(agent_ids) == 5
    assert len(set(agent_ids)) == 5  # All unique
    
    # Verify metrics
    metrics = agent_manager.get_metrics()
    assert metrics['total_agents'] == 5
    assert metrics['tasks_completed'] == 5


@pytest.mark.asyncio
async def test_full_agent_lifecycle():
    """Test complete agent lifecycle from creation to termination."""
    manager = AgentManager(
        health_check_interval=1,
        enable_monitoring=True,
        enable_auto_recovery=True
    )
    
    await manager.start()
    
    try:
        # Create agent pool
        pool_id = await manager.create_agent_pool(
            name="test-pool",
            capabilities={AgentCapability.TASK_EXECUTION},
            min_agents=2,
            max_agents=5
        )
        
        # Spawn agents and add to pool
        agents = []
        for i in range(3):
            agent = await manager.spawn_agent(
                agent_type=f"worker_{i}",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
            await manager.add_agent_to_pool(agent.id, pool_id)
            agents.append(agent)
        
        # Assign and complete tasks
        completed_tasks = []
        for i in range(10):
            task = Task(
                name=f"Task_{i}",
                description=f"Test task {i}",
                priority=TaskPriority.MEDIUM
            )
            
            agent_id = await manager.assign_task(task)
            
            # Simulate task execution
            await asyncio.sleep(0.05)
            
            # Complete task
            await manager.complete_task(
                task_id=task.id,
                success=True,
                execution_time=0.05,
                result={'task_num': i}
            )
            
            completed_tasks.append(task.id)
        
        # Get performance report
        report = await manager.get_performance_report()
        assert report['summary']['total_tasks'] == 10
        assert report['summary']['success_rate'] == 1.0
        
        # Test agent restart
        agent_to_restart = agents[0]
        await manager.restart_agent(agent_to_restart.id)
        
        # Verify agent was restarted
        restarted = await manager.get_agent(agent_to_restart.id)
        assert restarted.status == AgentStatus.IDLE
        
        # Terminate all agents
        for agent in agents:
            await manager.terminate_agent(agent.id, "Test completion")
        
        # Verify all agents terminated
        assert len(manager._agents) == 0
        
    finally:
        await manager.shutdown()