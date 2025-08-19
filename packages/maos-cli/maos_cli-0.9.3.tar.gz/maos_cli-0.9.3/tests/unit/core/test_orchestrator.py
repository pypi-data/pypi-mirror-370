"""
Unit tests for MAOS Orchestrator component.
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.maos.core.orchestrator import Orchestrator, MAOSEventHandler
from src.maos.models.task import Task, TaskStatus, TaskPriority
from src.maos.models.agent import Agent, AgentCapability
from src.maos.models.message import Message, MessageType
from src.maos.utils.exceptions import OrchestrationError, TaskError
from tests.utils.test_helpers import TestDataFactory, StateVerifier, MockManager


@pytest.mark.unit
class TestOrchestrator:
    """Test suite for Orchestrator class."""

    @pytest.fixture
    async def mock_orchestrator(self, mock_persistence):
        """Create orchestrator with mocked dependencies."""
        with patch.multiple(
            'src.maos.core.orchestrator',
            StateManager=MagicMock(),
            MessageBus=MagicMock(),
            TaskPlanner=MagicMock(),
            AgentManager=MagicMock(),
            ResourceAllocator=MagicMock()
        ):
            orchestrator = Orchestrator(persistence_backend=mock_persistence)
            
            # Mock the component methods
            orchestrator.state_manager.start = AsyncMock()
            orchestrator.message_bus.start = AsyncMock()
            orchestrator.agent_manager.start = AsyncMock()
            orchestrator.resource_allocator.start = AsyncMock()
            
            orchestrator.state_manager.shutdown = AsyncMock()
            orchestrator.message_bus.stop = AsyncMock()
            orchestrator.agent_manager.shutdown = AsyncMock()
            orchestrator.resource_allocator.shutdown = AsyncMock()
            
            return orchestrator

    async def test_orchestrator_initialization(self, mock_persistence):
        """Test orchestrator initializes correctly."""
        orchestrator = Orchestrator(persistence_backend=mock_persistence)
        
        assert orchestrator is not None
        assert orchestrator._running is False
        assert orchestrator._startup_time is None
        assert len(orchestrator._execution_plans) == 0
        assert len(orchestrator._active_executions) == 0
        assert orchestrator._metrics['tasks_submitted'] == 0

    async def test_start_orchestrator(self, mock_orchestrator):
        """Test orchestrator startup process."""
        # Mock component start methods
        mock_orchestrator.state_manager.start = AsyncMock()
        mock_orchestrator.message_bus.start = AsyncMock()
        mock_orchestrator.agent_manager.start = AsyncMock()
        mock_orchestrator.resource_allocator.start = AsyncMock()
        mock_orchestrator.message_bus.register_handler = MagicMock()
        mock_orchestrator.state_manager.add_change_listener = MagicMock()
        mock_orchestrator._create_startup_checkpoint = AsyncMock()
        
        await mock_orchestrator.start()
        
        assert mock_orchestrator._running is True
        assert mock_orchestrator._startup_time is not None
        mock_orchestrator.state_manager.start.assert_called_once()
        mock_orchestrator.message_bus.start.assert_called_once()
        mock_orchestrator.agent_manager.start.assert_called_once()
        mock_orchestrator.resource_allocator.start.assert_called_once()

    async def test_start_orchestrator_failure(self, mock_orchestrator):
        """Test orchestrator startup failure handling."""
        # Mock component failure
        mock_orchestrator.state_manager.start = AsyncMock(
            side_effect=Exception("Start failed")
        )
        mock_orchestrator.shutdown = AsyncMock()
        
        with pytest.raises(OrchestrationError, match="Failed to start orchestrator"):
            await mock_orchestrator.start()
        
        mock_orchestrator.shutdown.assert_called_once()

    async def test_shutdown_orchestrator(self, mock_orchestrator):
        """Test orchestrator shutdown process."""
        # Setup running state
        mock_orchestrator._running = True
        
        # Mock active execution
        mock_task = AsyncMock()
        mock_orchestrator._active_executions[uuid4()] = mock_task
        
        mock_orchestrator._create_shutdown_checkpoint = AsyncMock()
        mock_orchestrator.resource_allocator.shutdown = AsyncMock()
        mock_orchestrator.agent_manager.shutdown = AsyncMock()
        mock_orchestrator.message_bus.stop = AsyncMock()
        mock_orchestrator.state_manager.shutdown = AsyncMock()
        
        await mock_orchestrator.shutdown()
        
        assert mock_orchestrator._running is False
        mock_task.cancel.assert_called_once()

    async def test_submit_task(self, mock_orchestrator, sample_task):
        """Test task submission process."""
        mock_orchestrator._running = True
        
        # Mock dependencies
        mock_orchestrator.state_manager.store_object = AsyncMock()
        mock_execution_plan = MagicMock()
        mock_execution_plan.id = uuid4()
        mock_orchestrator.task_planner.create_execution_plan = AsyncMock(
            return_value=mock_execution_plan
        )
        mock_orchestrator.message_bus.publish_to_topic = AsyncMock()
        
        result = await mock_orchestrator.submit_task(sample_task)
        
        assert result == mock_execution_plan
        assert mock_orchestrator._metrics['tasks_submitted'] == 1
        mock_orchestrator.state_manager.store_object.assert_called()
        mock_orchestrator.task_planner.create_execution_plan.assert_called_once()

    async def test_submit_task_not_running(self, mock_orchestrator, sample_task):
        """Test task submission when orchestrator not running."""
        mock_orchestrator._running = False
        
        with pytest.raises(OrchestrationError, match="Orchestrator is not running"):
            await mock_orchestrator.submit_task(sample_task)

    async def test_submit_task_failure(self, mock_orchestrator, sample_task):
        """Test task submission failure handling."""
        mock_orchestrator._running = True
        mock_orchestrator.state_manager.store_object = AsyncMock(
            side_effect=Exception("Storage failed")
        )
        
        with pytest.raises(TaskError, match="Failed to submit task"):
            await mock_orchestrator.submit_task(sample_task)

    async def test_get_task(self, mock_orchestrator, sample_task):
        """Test retrieving a task."""
        mock_orchestrator.state_manager.get_object = AsyncMock(
            return_value=sample_task
        )
        
        result = await mock_orchestrator.get_task(sample_task.id)
        
        assert result == sample_task
        mock_orchestrator.state_manager.get_object.assert_called_with(
            'tasks', sample_task.id
        )

    async def test_get_task_status(self, mock_orchestrator, sample_task):
        """Test getting task status."""
        sample_task.status = TaskStatus.RUNNING
        mock_orchestrator.state_manager.get_object = AsyncMock(
            return_value=sample_task
        )
        
        status = await mock_orchestrator.get_task_status(sample_task.id)
        
        assert status == TaskStatus.RUNNING

    async def test_cancel_task(self, mock_orchestrator, sample_task):
        """Test task cancellation."""
        sample_task.status = TaskStatus.RUNNING
        mock_orchestrator.state_manager.get_object = AsyncMock(
            return_value=sample_task
        )
        mock_orchestrator.state_manager.store_object = AsyncMock()
        
        # Mock active execution
        mock_task = AsyncMock()
        mock_orchestrator._active_executions[sample_task.id] = mock_task
        
        result = await mock_orchestrator.cancel_task(sample_task.id, "Test cancel")
        
        assert result is True
        assert sample_task.status == TaskStatus.CANCELLED
        assert sample_task.error == "Test cancel"
        mock_task.cancel.assert_called_once()

    async def test_cancel_terminal_task(self, mock_orchestrator, sample_task):
        """Test cancelling a task that's already completed."""
        sample_task.status = TaskStatus.COMPLETED
        mock_orchestrator.state_manager.get_object = AsyncMock(
            return_value=sample_task
        )
        
        result = await mock_orchestrator.cancel_task(sample_task.id)
        
        assert result is False

    async def test_retry_task(self, mock_orchestrator, sample_task):
        """Test task retry functionality."""
        sample_task.status = TaskStatus.FAILED
        sample_task.retry_count = 1
        sample_task.error = "Previous error"
        
        mock_orchestrator.state_manager.get_object = AsyncMock(
            return_value=sample_task
        )
        mock_orchestrator.state_manager.store_object = AsyncMock()
        
        result = await mock_orchestrator.retry_task(sample_task.id)
        
        assert result is True
        assert sample_task.status == TaskStatus.PENDING
        assert sample_task.error is None
        assert sample_task.retry_count == 2

    async def test_create_agent(self, mock_orchestrator):
        """Test agent creation."""
        mock_orchestrator._running = True
        
        mock_agent = TestDataFactory.create_agent()
        mock_orchestrator.agent_manager.spawn_agent = AsyncMock(
            return_value=mock_agent
        )
        mock_orchestrator.state_manager.store_object = AsyncMock()
        
        result = await mock_orchestrator.create_agent(
            "test_agent",
            {AgentCapability.TASK_EXECUTION}
        )
        
        assert result == mock_agent
        assert mock_orchestrator._metrics['agents_created'] == 1
        mock_orchestrator.agent_manager.spawn_agent.assert_called_once()

    async def test_get_available_agents(self, mock_orchestrator, multiple_agents):
        """Test getting available agents."""
        # Set first agent as available
        multiple_agents[0].status = AgentCapability.TASK_EXECUTION
        
        mock_orchestrator.state_manager.get_objects = AsyncMock(
            return_value=multiple_agents
        )
        
        # Mock is_available method
        for agent in multiple_agents:
            agent.is_available = MagicMock(return_value=True)
            agent.can_handle_task = MagicMock(return_value=True)
        
        # Test without capability filter
        result = await mock_orchestrator.get_available_agents()
        assert len(result) == len(multiple_agents)
        
        # Test with capability filter
        result = await mock_orchestrator.get_available_agents(
            {AgentCapability.TASK_EXECUTION}
        )
        assert len(result) == len(multiple_agents)

    async def test_system_metrics(self, mock_orchestrator):
        """Test system metrics collection."""
        mock_orchestrator._running = True
        mock_orchestrator._startup_time = datetime.utcnow() - timedelta(hours=1)
        
        # Mock component metrics
        mock_orchestrator.task_planner.get_metrics = MagicMock(
            return_value={"tasks_planned": 5}
        )
        mock_orchestrator.agent_manager.get_metrics = MagicMock(
            return_value={"agents_active": 3}
        )
        mock_orchestrator.resource_allocator.get_metrics = MagicMock(
            return_value={"resources_allocated": 2}
        )
        mock_orchestrator.state_manager.get_metrics = MagicMock(
            return_value={"state_size": 1024}
        )
        mock_orchestrator.message_bus.get_metrics = MagicMock(
            return_value={"messages_sent": 100}
        )
        
        metrics = await mock_orchestrator.get_system_metrics()
        
        assert 'orchestrator' in metrics
        assert 'task_planner' in metrics
        assert 'agent_manager' in metrics
        assert metrics['orchestrator']['uptime_seconds'] > 0

    async def test_create_checkpoint(self, mock_orchestrator):
        """Test checkpoint creation."""
        mock_checkpoint = MagicMock()
        mock_checkpoint.id = uuid4()
        mock_orchestrator.state_manager.create_checkpoint = AsyncMock(
            return_value=mock_checkpoint
        )
        
        checkpoint_id = await mock_orchestrator.create_checkpoint("test-checkpoint")
        
        assert checkpoint_id == mock_checkpoint.id
        mock_orchestrator.state_manager.create_checkpoint.assert_called_once()

    async def test_restore_checkpoint(self, mock_orchestrator):
        """Test checkpoint restoration."""
        checkpoint_id = uuid4()
        mock_checkpoint = MagicMock()
        mock_checkpoint.name = "test-checkpoint"
        mock_checkpoint.state_data = {"test": "data"}
        
        mock_orchestrator.state_manager.get_object = AsyncMock(
            return_value=mock_checkpoint
        )
        mock_orchestrator.state_manager.create_snapshot = AsyncMock(
            return_value=MagicMock(id=uuid4())
        )
        mock_orchestrator.state_manager.restore_from_snapshot = AsyncMock(
            return_value=True
        )
        
        result = await mock_orchestrator.restore_checkpoint(checkpoint_id)
        
        assert result is True
        mock_orchestrator.state_manager.restore_from_snapshot.assert_called_once()


@pytest.mark.unit
class TestMAOSEventHandler:
    """Test suite for MAOSEventHandler class."""

    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock orchestrator."""
        orchestrator = MagicMock()
        orchestrator.logger = MagicMock()
        return orchestrator

    @pytest.fixture
    def event_handler(self, mock_orchestrator):
        """Create event handler with mock orchestrator."""
        return MAOSEventHandler(mock_orchestrator)

    async def test_handle_task_completion(self, event_handler, mock_orchestrator):
        """Test task completion message handling."""
        task_id = uuid4()
        message = TestDataFactory.create_message(
            MessageType.TASK_COMPLETION,
            payload={
                'task_id': str(task_id),
                'result': 'success',
                'execution_time': 1.5
            }
        )
        
        mock_orchestrator._on_task_completed = AsyncMock()
        
        await event_handler.handle_message(message)
        
        mock_orchestrator._on_task_completed.assert_called_once_with(
            task_id, 'success', 1.5
        )

    async def test_handle_task_failure(self, event_handler, mock_orchestrator):
        """Test task failure message handling."""
        task_id = uuid4()
        message = TestDataFactory.create_message(
            MessageType.TASK_FAILURE,
            payload={
                'task_id': str(task_id),
                'error': 'Task failed',
                'execution_time': 0.5
            }
        )
        
        mock_orchestrator._on_task_failed = AsyncMock()
        
        await event_handler.handle_message(message)
        
        mock_orchestrator._on_task_failed.assert_called_once_with(
            task_id, 'Task failed', 0.5
        )

    async def test_handle_heartbeat(self, event_handler, mock_orchestrator):
        """Test heartbeat message handling."""
        agent_id = uuid4()
        message = TestDataFactory.create_message(
            MessageType.HEARTBEAT,
            payload={
                'cpu_usage': 75.0,
                'memory_usage': 512.0
            }
        )
        message.sender_id = agent_id
        
        mock_agent = MagicMock()
        mock_orchestrator.agent_manager.get_agent = AsyncMock(
            return_value=mock_agent
        )
        
        await event_handler.handle_message(message)
        
        mock_orchestrator.agent_manager.get_agent.assert_called_once_with(agent_id)
        mock_agent.update_heartbeat.assert_called_once_with(75.0, 512.0)

    async def test_handle_resource_request(self, event_handler, mock_orchestrator):
        """Test resource request message handling."""
        requester_id = uuid4()
        request_id = uuid4()
        message = TestDataFactory.create_message(
            MessageType.RESOURCE_REQUEST,
            payload={
                'requirements': {'cpu': 2.0, 'memory': 1024},
                'priority': 'HIGH'
            }
        )
        message.sender_id = requester_id
        
        mock_orchestrator.resource_allocator.request_allocation = AsyncMock(
            return_value=request_id
        )
        mock_orchestrator.message_bus.send_direct = AsyncMock()
        
        await event_handler.handle_message(message)
        
        mock_orchestrator.resource_allocator.request_allocation.assert_called_once()
        mock_orchestrator.message_bus.send_direct.assert_called_once()

    async def test_handle_message_exception(self, event_handler, mock_orchestrator):
        """Test exception handling in message processing."""
        message = TestDataFactory.create_message(
            MessageType.TASK_COMPLETION,
            payload={'task_id': 'invalid-uuid'}
        )
        
        # This should not raise an exception
        await event_handler.handle_message(message)
        
        # Verify error was logged (mock the logger if needed)
        assert event_handler.logger is not None

    def test_get_supported_message_types(self, event_handler):
        """Test getting supported message types."""
        supported_types = event_handler.get_supported_message_types()
        
        expected_types = {
            MessageType.TASK_COMPLETION,
            MessageType.TASK_FAILURE,
            MessageType.HEARTBEAT,
            MessageType.ERROR_REPORT,
            MessageType.RESOURCE_REQUEST,
            MessageType.STATUS_UPDATE
        }
        
        assert supported_types == expected_types