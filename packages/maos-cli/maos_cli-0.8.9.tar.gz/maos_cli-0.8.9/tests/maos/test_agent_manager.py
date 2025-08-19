"""
Unit tests for Agent Manager component.
"""

import pytest
import asyncio
from uuid import uuid4
from datetime import datetime

from src.maos.core.agent_manager import AgentManager, AgentPool, LoadBalancingStrategy
from src.maos.models.agent import Agent, AgentStatus, AgentCapability
from src.maos.models.task import Task, TaskStatus, TaskPriority
from src.maos.utils.exceptions import AgentError, AgentNotFoundError, AgentNotAvailableError


@pytest.fixture
async def agent_manager():
    """Create an AgentManager instance for testing."""
    manager = AgentManager(
        max_agents=10,
        health_check_interval=1,
        heartbeat_timeout=5,
        auto_recovery_enabled=True
    )
    await manager.start()
    yield manager
    await manager.shutdown()


@pytest.fixture
def sample_capabilities():
    """Create sample agent capabilities for testing."""
    return {
        AgentCapability.TASK_EXECUTION,
        AgentCapability.DATA_PROCESSING,
        AgentCapability.FILE_OPERATIONS
    }


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    return Task(
        name="Test Task",
        description="A test task for agent assignment",
        priority=TaskPriority.MEDIUM,
        resource_requirements={'cpu_cores': 1, 'memory_mb': 512}
    )


@pytest.mark.asyncio
class TestAgentManager:
    """Test cases for AgentManager class."""
    
    async def test_spawn_agent(self, agent_manager, sample_capabilities):
        """Test spawning a new agent."""
        agent = await agent_manager.spawn_agent(
            agent_type="test_agent",
            capabilities=sample_capabilities,
            configuration={'test_config': 'value'}
        )
        
        assert isinstance(agent, Agent)
        assert agent.type == "test_agent"
        assert agent.capabilities == sample_capabilities
        assert agent.status == AgentStatus.IDLE
        assert agent.configuration['test_config'] == 'value'
        
        # Agent should be registered in manager
        retrieved_agent = agent_manager.get_agent(agent.id)
        assert retrieved_agent is not None
        assert retrieved_agent.id == agent.id
    
    async def test_spawn_multiple_agents(self, agent_manager, sample_capabilities):
        """Test spawning multiple agents."""
        agents = []
        for i in range(3):
            agent = await agent_manager.spawn_agent(
                agent_type=f"test_agent_{i}",
                capabilities=sample_capabilities
            )
            agents.append(agent)
        
        assert len(agents) == 3
        
        # All agents should be available
        available_agents = agent_manager.get_available_agents()
        available_ids = {agent.id for agent in available_agents}
        
        for agent in agents:
            assert agent.id in available_ids
    
    async def test_max_agents_limit(self, agent_manager, sample_capabilities):
        """Test that max agents limit is enforced."""
        # Spawn agents up to the limit
        for i in range(agent_manager.max_agents):
            await agent_manager.spawn_agent(
                agent_type=f"agent_{i}",
                capabilities=sample_capabilities
            )
        
        # Attempting to spawn one more should fail
        with pytest.raises(AgentError) as exc_info:
            await agent_manager.spawn_agent(
                agent_type="extra_agent",
                capabilities=sample_capabilities
            )
        
        assert "Maximum agent limit reached" in str(exc_info.value)
    
    async def test_terminate_agent(self, agent_manager, sample_capabilities):
        """Test terminating an agent."""
        agent = await agent_manager.spawn_agent(
            agent_type="test_agent",
            capabilities=sample_capabilities
        )
        
        # Terminate the agent
        success = await agent_manager.terminate_agent(agent.id, "Test termination")
        assert success
        
        # Agent should no longer be available
        retrieved_agent = agent_manager.get_agent(agent.id)
        assert retrieved_agent is None
    
    async def test_terminate_nonexistent_agent(self, agent_manager):
        """Test terminating a non-existent agent."""
        fake_agent_id = uuid4()
        
        with pytest.raises(AgentNotFoundError):
            await agent_manager.terminate_agent(fake_agent_id)
    
    async def test_assign_task_to_available_agent(self, agent_manager, sample_capabilities, sample_task):
        """Test assigning a task to an available agent."""
        agent = await agent_manager.spawn_agent(
            agent_type="test_agent",
            capabilities=sample_capabilities
        )
        
        # Assign task
        assigned_agent_id = await agent_manager.assign_task(
            task=sample_task,
            required_capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        assert assigned_agent_id == agent.id
        assert agent.status == AgentStatus.BUSY
        assert agent.current_task_id == sample_task.id
    
    async def test_assign_task_with_capability_requirements(self, agent_manager, sample_task):
        """Test task assignment with specific capability requirements."""
        # Create agent with limited capabilities
        agent = await agent_manager.spawn_agent(
            agent_type="limited_agent",
            capabilities={AgentCapability.FILE_OPERATIONS}
        )
        
        # Try to assign task requiring different capability
        with pytest.raises(AgentNotAvailableError):
            await agent_manager.assign_task(
                task=sample_task,
                required_capabilities={AgentCapability.DATA_PROCESSING}
            )
    
    async def test_assign_task_preferred_agent(self, agent_manager, sample_capabilities, sample_task):
        """Test task assignment with preferred agent."""
        agent1 = await agent_manager.spawn_agent(
            agent_type="agent1",
            capabilities=sample_capabilities
        )
        agent2 = await agent_manager.spawn_agent(
            agent_type="agent2",
            capabilities=sample_capabilities
        )
        
        # Assign task to preferred agent
        assigned_agent_id = await agent_manager.assign_task(
            task=sample_task,
            preferred_agent_id=agent2.id,
            required_capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        assert assigned_agent_id == agent2.id
    
    async def test_complete_task(self, agent_manager, sample_capabilities, sample_task):
        """Test completing a task and updating agent state."""
        agent = await agent_manager.spawn_agent(
            agent_type="test_agent",
            capabilities=sample_capabilities
        )
        
        # Assign task
        await agent_manager.assign_task(
            task=sample_task,
            required_capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        assert agent.status == AgentStatus.BUSY
        
        # Complete task
        await agent_manager.complete_task(
            task_id=sample_task.id,
            success=True,
            execution_time=2.5,
            result="Task completed successfully"
        )
        
        assert agent.status == AgentStatus.IDLE
        assert agent.current_task_id is None
        assert agent.metrics.tasks_completed == 1
        assert agent.metrics.success_rate == 1.0
    
    async def test_agent_health_monitoring(self, agent_manager, sample_capabilities):
        """Test agent health monitoring."""
        agent = await agent_manager.spawn_agent(
            agent_type="test_agent",
            capabilities=sample_capabilities
        )
        
        # Update heartbeat with system metrics
        agent.update_heartbeat(cpu_usage=50.0, memory_usage=512.0)
        
        assert agent.is_healthy()
        assert agent.metrics.cpu_usage_percent == 50.0
        assert agent.metrics.memory_usage_mb == 512.0
        assert agent.metrics.health_score > 0.5
    
    async def test_agent_overload_detection(self, agent_manager, sample_capabilities):
        """Test agent overload detection."""
        agent = await agent_manager.spawn_agent(
            agent_type="test_agent",
            capabilities=sample_capabilities,
            configuration={'max_concurrent_tasks': 2}
        )
        
        # Update agent to simulate overload
        agent.update_heartbeat(cpu_usage=98.0, memory_usage=1000.0)
        
        # Agent should be marked as overloaded
        assert agent.status == AgentStatus.OVERLOADED
        assert not agent.is_available()
    
    async def test_create_agent_pool(self, agent_manager, sample_capabilities):
        """Test creating an agent pool."""
        pool = await agent_manager.create_agent_pool(
            name="Test Pool",
            capabilities=sample_capabilities,
            min_agents=2,
            max_agents=5,
            auto_scaling_enabled=True
        )
        
        assert isinstance(pool, AgentPool)
        assert pool.name == "Test Pool"
        assert pool.capabilities == sample_capabilities
        assert len(pool.agents) >= 2  # Should create minimum agents
        assert pool.min_agents == 2
        assert pool.max_agents == 5
    
    async def test_agent_pool_load_calculation(self, agent_manager, sample_capabilities, sample_task):
        """Test agent pool load calculation."""
        pool = await agent_manager.create_agent_pool(
            name="Load Test Pool",
            capabilities=sample_capabilities,
            min_agents=2,
            max_agents=4
        )
        
        # Initially, load should be low
        initial_load = pool.get_current_load()
        assert initial_load == 0.0
        
        # Assign tasks to agents
        available_agents = pool.get_available_agents()
        if available_agents:
            await agent_manager.assign_task(
                task=sample_task,
                preferred_agent_id=available_agents[0].id,
                required_capabilities=sample_capabilities
            )
            
            # Load should increase
            current_load = pool.get_current_load()
            assert current_load > initial_load
    
    async def test_agent_task_queue(self, agent_manager, sample_capabilities):
        """Test agent task queuing."""
        agent = await agent_manager.spawn_agent(
            agent_type="queue_test_agent",
            capabilities=sample_capabilities,
            configuration={'max_concurrent_tasks': 3}
        )
        
        # Assign multiple tasks
        tasks = []
        for i in range(3):
            task = Task(
                name=f"Task {i}",
                description=f"Test task {i}",
                priority=TaskPriority.MEDIUM
            )
            tasks.append(task)
            
            await agent_manager.assign_task(
                task=task,
                preferred_agent_id=agent.id,
                required_capabilities={AgentCapability.TASK_EXECUTION}
            )
        
        # First task should be current, others in queue
        assert agent.current_task_id == tasks[0].id
        assert len(agent.task_queue) == 2
        assert tasks[1].id in agent.task_queue
        assert tasks[2].id in agent.task_queue
    
    async def test_agent_metrics_tracking(self, agent_manager, sample_capabilities, sample_task):
        """Test agent performance metrics tracking."""
        agent = await agent_manager.spawn_agent(
            agent_type="metrics_test_agent",
            capabilities=sample_capabilities
        )
        
        # Assign and complete successful task
        await agent_manager.assign_task(
            task=sample_task,
            preferred_agent_id=agent.id,
            required_capabilities=sample_capabilities
        )
        
        await agent_manager.complete_task(
            task_id=sample_task.id,
            success=True,
            execution_time=1.5
        )
        
        # Check metrics
        assert agent.metrics.tasks_completed == 1
        assert agent.metrics.tasks_failed == 0
        assert agent.metrics.success_rate == 1.0
        assert agent.metrics.total_execution_time == 1.5
        assert agent.metrics.average_execution_time == 1.5
        
        # Complete failed task
        failed_task = Task(name="Failed Task", description="A failing task")
        await agent_manager.assign_task(
            task=failed_task,
            preferred_agent_id=agent.id,
            required_capabilities=sample_capabilities
        )
        
        await agent_manager.complete_task(
            task_id=failed_task.id,
            success=False,
            execution_time=0.5,
            error="Task failed"
        )
        
        # Check updated metrics
        assert agent.metrics.tasks_completed == 1
        assert agent.metrics.tasks_failed == 1
        assert agent.metrics.success_rate == 0.5
    
    async def test_get_all_agents(self, agent_manager, sample_capabilities):
        """Test getting all agents."""
        # Create multiple agents
        agents = []
        for i in range(3):
            agent = await agent_manager.spawn_agent(
                agent_type=f"agent_{i}",
                capabilities=sample_capabilities
            )
            agents.append(agent)
        
        all_agents = agent_manager.get_all_agents()
        assert len(all_agents) == 3
        
        all_agent_ids = {agent.id for agent in all_agents}
        for agent in agents:
            assert agent.id in all_agent_ids
    
    async def test_get_available_agents(self, agent_manager, sample_capabilities, sample_task):
        """Test getting available agents."""
        # Create agents
        agent1 = await agent_manager.spawn_agent(
            agent_type="agent1",
            capabilities=sample_capabilities
        )
        agent2 = await agent_manager.spawn_agent(
            agent_type="agent2",
            capabilities=sample_capabilities
        )
        
        # Initially both should be available
        available_agents = agent_manager.get_available_agents()
        assert len(available_agents) == 2
        
        # Assign task to one agent
        await agent_manager.assign_task(
            task=sample_task,
            preferred_agent_id=agent1.id,
            required_capabilities=sample_capabilities
        )
        
        # Only one should be available now
        available_agents = agent_manager.get_available_agents()
        available_ids = {agent.id for agent in available_agents}
        assert agent1.id not in available_ids or agent1.max_concurrent_tasks > 1
        assert agent2.id in available_ids
    
    async def test_agent_manager_metrics(self, agent_manager, sample_capabilities):
        """Test agent manager metrics collection."""
        initial_metrics = agent_manager.get_metrics()
        initial_agents_spawned = initial_metrics['agents_spawned']
        
        # Spawn some agents
        for i in range(2):
            await agent_manager.spawn_agent(
                agent_type=f"metrics_agent_{i}",
                capabilities=sample_capabilities
            )
        
        final_metrics = agent_manager.get_metrics()
        
        assert final_metrics['agents_spawned'] == initial_agents_spawned + 2
        assert final_metrics['total_agents'] == 2
        assert final_metrics['available_agents'] == 2
    
    async def test_agent_capability_matching(self, agent_manager):
        """Test agent capability matching for task assignment."""
        # Create agents with different capabilities
        cpu_agent = await agent_manager.spawn_agent(
            agent_type="cpu_agent",
            capabilities={AgentCapability.COMPUTATION}
        )
        
        data_agent = await agent_manager.spawn_agent(
            agent_type="data_agent",
            capabilities={AgentCapability.DATA_PROCESSING, AgentCapability.FILE_OPERATIONS}
        )
        
        # Create task requiring data processing
        data_task = Task(
            name="Data Task",
            description="Task requiring data processing",
            priority=TaskPriority.MEDIUM
        )
        
        # Should assign to data agent
        assigned_agent_id = await agent_manager.assign_task(
            task=data_task,
            required_capabilities={AgentCapability.DATA_PROCESSING}
        )
        
        assert assigned_agent_id == data_agent.id
    
    async def test_terminate_agent_with_active_tasks(self, agent_manager, sample_capabilities, sample_task):
        """Test terminating agent with active tasks."""
        agent = await agent_manager.spawn_agent(
            agent_type="busy_agent",
            capabilities=sample_capabilities
        )
        
        # Assign task
        await agent_manager.assign_task(
            task=sample_task,
            preferred_agent_id=agent.id,
            required_capabilities=sample_capabilities
        )
        
        # Try to terminate without force - should fail
        with pytest.raises(AgentError) as exc_info:
            await agent_manager.terminate_agent(agent.id, "Test termination", force=False)
        
        assert "has active tasks" in str(exc_info.value)
        
        # Force termination should succeed
        success = await agent_manager.terminate_agent(agent.id, "Force termination", force=True)
        assert success


if __name__ == "__main__":
    pytest.main([__file__])