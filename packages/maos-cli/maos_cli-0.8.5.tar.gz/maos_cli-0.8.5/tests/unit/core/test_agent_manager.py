"""
Unit tests for MAOS Agent Manager component.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.maos.core.agent_manager import AgentManager
from src.maos.models.agent import Agent, AgentStatus, AgentCapability
from src.maos.models.task import Task, TaskStatus
from src.maos.utils.exceptions import AgentError
from tests.utils.test_helpers import TestDataFactory, StateVerifier


@pytest.mark.unit
class TestAgentManager:
    """Test suite for AgentManager class."""

    @pytest.fixture
    def agent_manager(self):
        """Create AgentManager instance."""
        return AgentManager()

    async def test_spawn_agent(self, agent_manager):
        """Test agent spawning."""
        agent = await agent_manager.spawn_agent(
            agent_type="test_agent",
            capabilities={AgentCapability.TASK_EXECUTION},
            configuration={"test_config": True}
        )
        
        assert agent is not None
        assert agent.type == "test_agent"
        assert AgentCapability.TASK_EXECUTION in agent.capabilities
        assert agent.configuration["test_config"] is True
        assert agent.status == AgentStatus.IDLE

    async def test_spawn_agent_duplicate(self, agent_manager):
        """Test spawning agent with duplicate capabilities."""
        capabilities = {
            AgentCapability.TASK_EXECUTION,
            AgentCapability.DATA_PROCESSING,
            AgentCapability.TASK_EXECUTION  # Duplicate
        }
        
        agent = await agent_manager.spawn_agent(
            agent_type="test_agent",
            capabilities=capabilities
        )
        
        # Should deduplicate capabilities
        assert len(agent.capabilities) == 2
        assert AgentCapability.TASK_EXECUTION in agent.capabilities
        assert AgentCapability.DATA_PROCESSING in agent.capabilities

    async def test_get_agent(self, agent_manager, sample_agent):
        """Test retrieving agent by ID."""
        # Add agent to manager's internal storage
        agent_manager._agents[sample_agent.id] = sample_agent
        
        result = await agent_manager.get_agent(sample_agent.id)
        
        assert result == sample_agent

    async def test_get_nonexistent_agent(self, agent_manager):
        """Test retrieving non-existent agent."""
        nonexistent_id = uuid4()
        
        result = await agent_manager.get_agent(nonexistent_id)
        
        assert result is None

    async def test_assign_task(self, agent_manager, sample_agent, sample_task):
        """Test task assignment to agent."""
        agent_manager._agents[sample_agent.id] = sample_agent
        
        assignment_id = await agent_manager.assign_task(sample_task)
        
        assert assignment_id == sample_agent.id
        assert sample_agent.current_task_id == sample_task.id
        assert sample_agent.status == AgentStatus.BUSY

    async def test_assign_task_no_available_agents(self, agent_manager, sample_task):
        """Test task assignment when no agents available."""
        # No agents in manager
        
        with pytest.raises(AgentError, match="No available agents"):
            await agent_manager.assign_task(sample_task)

    async def test_assign_task_agent_busy(self, agent_manager, sample_agent, sample_task):
        """Test task assignment when agent is busy."""
        # Set agent as busy
        sample_agent.status = AgentStatus.BUSY
        sample_agent.current_task_id = uuid4()
        agent_manager._agents[sample_agent.id] = sample_agent
        
        # Create another task
        another_task = TestDataFactory.create_task("Another Task")
        
        assignment_id = await agent_manager.assign_task(another_task)
        
        # Should queue the task
        assert assignment_id == sample_agent.id
        assert another_task.id in sample_agent.task_queue

    async def test_complete_task_success(self, agent_manager, sample_agent, sample_task):
        """Test successful task completion."""
        # Setup agent with assigned task
        sample_agent.current_task_id = sample_task.id
        sample_agent.status = AgentStatus.BUSY
        agent_manager._agents[sample_agent.id] = sample_agent
        
        await agent_manager.complete_task(
            task_id=sample_task.id,
            success=True,
            execution_time=2.5,
            result="Task completed successfully"
        )
        
        assert sample_agent.current_task_id is None
        assert sample_agent.status == AgentStatus.IDLE
        assert sample_agent.metrics.tasks_completed == 1
        assert sample_agent.metrics.total_execution_time == 2.5

    async def test_complete_task_failure(self, agent_manager, sample_agent, sample_task):
        """Test failed task completion."""
        # Setup agent with assigned task
        sample_agent.current_task_id = sample_task.id
        sample_agent.status = AgentStatus.BUSY
        agent_manager._agents[sample_agent.id] = sample_agent
        
        await agent_manager.complete_task(
            task_id=sample_task.id,
            success=False,
            execution_time=1.0,
            error="Task execution failed"
        )
        
        assert sample_agent.current_task_id is None
        assert sample_agent.status == AgentStatus.IDLE
        assert sample_agent.metrics.tasks_failed == 1
        assert sample_agent.metrics.total_execution_time == 1.0

    async def test_complete_task_with_queue(self, agent_manager, sample_agent):
        """Test task completion when agent has queued tasks."""
        current_task = TestDataFactory.create_task("Current Task")
        queued_task = TestDataFactory.create_task("Queued Task")
        
        # Setup agent with current task and queue
        sample_agent.current_task_id = current_task.id
        sample_agent.task_queue = [queued_task.id]
        sample_agent.status = AgentStatus.BUSY
        agent_manager._agents[sample_agent.id] = sample_agent
        
        await agent_manager.complete_task(
            task_id=current_task.id,
            success=True,
            execution_time=1.0,
            result="Success"
        )
        
        # Should start next task from queue
        assert sample_agent.current_task_id == queued_task.id
        assert len(sample_agent.task_queue) == 0
        assert sample_agent.status == AgentStatus.BUSY

    async def test_terminate_agent(self, agent_manager, sample_agent):
        """Test agent termination."""
        agent_manager._agents[sample_agent.id] = sample_agent
        
        result = await agent_manager.terminate_agent(
            sample_agent.id,
            reason="Test termination"
        )
        
        assert result is True
        assert sample_agent.status == AgentStatus.TERMINATED
        assert sample_agent.id not in agent_manager._agents

    async def test_terminate_nonexistent_agent(self, agent_manager):
        """Test terminating non-existent agent."""
        nonexistent_id = uuid4()
        
        result = await agent_manager.terminate_agent(nonexistent_id)
        
        assert result is False

    async def test_get_available_agents(self, agent_manager, multiple_agents):
        """Test getting available agents."""
        # Add agents to manager
        for agent in multiple_agents:
            agent.status = AgentStatus.IDLE
            agent_manager._agents[agent.id] = agent
        
        # Make one agent unavailable
        multiple_agents[0].status = AgentStatus.TERMINATED
        
        available = await agent_manager.get_available_agents()
        
        assert len(available) == 2  # Only 2 should be available
        assert multiple_agents[0] not in available

    async def test_get_agents_by_capability(self, agent_manager, multiple_agents):
        """Test filtering agents by capability."""
        # Set specific capabilities
        multiple_agents[0].capabilities = {AgentCapability.COMPUTATION}
        multiple_agents[1].capabilities = {AgentCapability.FILE_OPERATIONS}
        multiple_agents[2].capabilities = {
            AgentCapability.TASK_EXECUTION,
            AgentCapability.COMPUTATION
        }
        
        # Add to manager
        for agent in multiple_agents:
            agent.status = AgentStatus.IDLE
            agent_manager._agents[agent.id] = agent
        
        # Filter by computation capability
        result = await agent_manager.get_agents_by_capability(
            AgentCapability.COMPUTATION
        )
        
        assert len(result) == 2
        assert multiple_agents[0] in result
        assert multiple_agents[2] in result

    async def test_get_agent_load_distribution(self, agent_manager, multiple_agents):
        """Test getting agent load distribution."""
        # Setup agents with different loads
        multiple_agents[0].current_task_id = uuid4()
        multiple_agents[0].task_queue = [uuid4()]  # Load: 2/3 = 0.67
        
        multiple_agents[1].current_task_id = None
        multiple_agents[1].task_queue = []  # Load: 0/5 = 0.0
        
        multiple_agents[2].current_task_id = uuid4()
        multiple_agents[2].task_queue = []  # Load: 1/3 = 0.33
        
        # Add to manager
        for agent in multiple_agents:
            agent_manager._agents[agent.id] = agent
        
        load_distribution = await agent_manager.get_agent_load_distribution()
        
        assert len(load_distribution) == 3
        assert load_distribution[multiple_agents[0].id] == pytest.approx(0.67, abs=0.01)
        assert load_distribution[multiple_agents[1].id] == 0.0
        assert load_distribution[multiple_agents[2].id] == pytest.approx(0.33, abs=0.01)

    async def test_health_check_agents(self, agent_manager, multiple_agents):
        """Test agent health checking."""
        # Set different health states
        multiple_agents[0].status = AgentStatus.IDLE
        multiple_agents[0].metrics.last_heartbeat = datetime.utcnow()
        
        multiple_agents[1].status = AgentStatus.UNHEALTHY
        
        multiple_agents[2].status = AgentStatus.IDLE
        multiple_agents[2].metrics.last_heartbeat = datetime.utcnow() - timedelta(minutes=5)
        
        # Add to manager
        for agent in multiple_agents:
            agent_manager._agents[agent.id] = agent
        
        health_report = await agent_manager.health_check_agents()
        
        assert len(health_report["healthy_agents"]) == 1
        assert len(health_report["unhealthy_agents"]) >= 1
        assert health_report["total_agents"] == 3

    async def test_scale_agents(self, agent_manager):
        """Test agent scaling functionality."""
        # Start with no agents
        assert len(agent_manager._agents) == 0
        
        # Scale up
        await agent_manager.scale_agents(
            target_count=3,
            agent_type="auto_scaled",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        assert len(agent_manager._agents) == 3
        
        # Scale down
        await agent_manager.scale_agents(target_count=1)
        
        assert len(agent_manager._agents) == 1

    async def test_get_metrics(self, agent_manager, multiple_agents):
        """Test getting agent manager metrics."""
        # Setup agents with metrics
        multiple_agents[0].metrics.tasks_completed = 10
        multiple_agents[0].metrics.tasks_failed = 2
        multiple_agents[1].metrics.tasks_completed = 5
        multiple_agents[1].metrics.tasks_failed = 1
        
        # Add to manager
        for agent in multiple_agents:
            agent_manager._agents[agent.id] = agent
        
        metrics = await agent_manager.get_metrics()
        
        assert metrics["total_agents"] == 3
        assert metrics["total_tasks_completed"] == 15
        assert metrics["total_tasks_failed"] == 3
        assert metrics["average_success_rate"] > 0.7

    async def test_start_shutdown_lifecycle(self, agent_manager):
        """Test agent manager lifecycle."""
        await agent_manager.start()
        assert agent_manager._running is True
        
        await agent_manager.shutdown()
        assert agent_manager._running is False

    async def test_agent_failover(self, agent_manager, sample_agent):
        """Test agent failover mechanism."""
        # Add healthy agent
        sample_agent.status = AgentStatus.IDLE
        agent_manager._agents[sample_agent.id] = sample_agent
        
        # Simulate failure
        await agent_manager._handle_agent_failure(sample_agent.id, "Simulated failure")
        
        # Agent should be marked as failed
        assert sample_agent.status == AgentStatus.OFFLINE
        
        # Any assigned tasks should be reassigned (if implemented)
        # This would depend on the specific failover strategy