"""Tests for event dispatcher functionality."""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from src.communication.event_dispatcher import (
    EventDispatcher, Event, EventType, EventFilter
)


@pytest.fixture
def sample_event():
    """Create a sample event for testing."""
    return Event(
        type=EventType.TASK_STARTED,
        source="test_agent",
        topic="tasks",
        data={"task_id": "test_task_123", "description": "Test task"},
        tags={"test", "automation"}
    )


@pytest.fixture
async def event_dispatcher():
    """Create test event dispatcher."""
    dispatcher = EventDispatcher(
        enable_persistence=False,  # Disable for testing
        enable_streaming=False,    # Disable for testing
        batch_size=5,
        flush_interval=0.1
    )
    await dispatcher.start()
    yield dispatcher
    await dispatcher.stop()


@pytest.mark.asyncio
class TestEventDispatcher:
    """Test suite for EventDispatcher."""
    
    async def test_event_creation(self, sample_event):
        """Test event creation and properties."""
        assert sample_event.id is not None
        assert sample_event.type == EventType.TASK_STARTED
        assert sample_event.source == "test_agent"
        assert sample_event.topic == "tasks"
        assert "task_id" in sample_event.data
        assert "test" in sample_event.tags
    
    async def test_event_to_message_conversion(self, sample_event):
        """Test converting event to message."""
        message = sample_event.to_message()
        
        assert message.sender == sample_event.source
        assert message.topic == sample_event.topic
        assert message.payload["event_type"] == sample_event.type.value
        assert message.payload["data"] == sample_event.data
    
    async def test_event_from_message_conversion(self, sample_event):
        """Test creating event from message."""
        message = sample_event.to_message()
        reconstructed_event = Event.from_message(message)
        
        assert reconstructed_event.type == sample_event.type
        assert reconstructed_event.source == sample_event.source
        assert reconstructed_event.data == sample_event.data
        assert reconstructed_event.tags == sample_event.tags
    
    async def test_event_subscription(self, event_dispatcher):
        """Test event subscription mechanism."""
        callback_called = False
        received_event = None
        
        async def test_callback(event: Event):
            nonlocal callback_called, received_event
            callback_called = True
            received_event = event
        
        # Subscribe to events
        subscription_id = await event_dispatcher.subscribe(
            "test_subscriber",
            test_callback,
            topics=["test_topic"]
        )
        
        assert subscription_id is not None
        
        # Dispatch an event
        test_event = Event(
            type=EventType.CUSTOM,
            source="test_source",
            topic="test_topic",
            data={"message": "test"}
        )
        
        await event_dispatcher.dispatch(test_event)
        
        # Give time for processing
        await asyncio.sleep(0.2)
        
        assert callback_called
        assert received_event.id == test_event.id
    
    async def test_event_filtering(self, event_dispatcher):
        """Test event filtering functionality."""
        callback_count = 0
        
        async def counting_callback(event: Event):
            nonlocal callback_count
            callback_count += 1
        
        # Create filter for specific event types
        event_filter = EventFilter(
            event_types=[EventType.TASK_STARTED, EventType.TASK_COMPLETED],
            sources=["test_agent"]
        )
        
        # Subscribe with filter
        subscription_id = await event_dispatcher.subscribe(
            "filtered_subscriber",
            counting_callback,
            event_filter=event_filter
        )
        
        # Dispatch matching events
        matching_event1 = Event(
            type=EventType.TASK_STARTED,
            source="test_agent",
            topic="tasks"
        )
        
        matching_event2 = Event(
            type=EventType.TASK_COMPLETED,
            source="test_agent",
            topic="tasks"
        )
        
        # Dispatch non-matching event
        non_matching_event = Event(
            type=EventType.TASK_FAILED,  # Different type
            source="test_agent",
            topic="tasks"
        )
        
        await event_dispatcher.dispatch(matching_event1)
        await event_dispatcher.dispatch(matching_event2)
        await event_dispatcher.dispatch(non_matching_event)
        
        # Give time for processing
        await asyncio.sleep(0.2)
        
        # Should only receive matching events
        assert callback_count == 2
    
    async def test_event_unsubscription(self, event_dispatcher):
        """Test event unsubscription."""
        callback_called = False
        
        async def test_callback(event: Event):
            nonlocal callback_called
            callback_called = True
        
        # Subscribe and then unsubscribe
        subscription_id = await event_dispatcher.subscribe(
            "test_subscriber",
            test_callback
        )
        
        result = await event_dispatcher.unsubscribe(subscription_id)
        assert result is True
        
        # Dispatch event after unsubscription
        test_event = Event(
            type=EventType.CUSTOM,
            source="test_source",
            topic="test_topic"
        )
        
        await event_dispatcher.dispatch(test_event)
        await asyncio.sleep(0.2)
        
        # Callback should not be called
        assert not callback_called
    
    async def test_batch_processing(self, event_dispatcher):
        """Test batch processing of events."""
        # Set small batch size for testing
        event_dispatcher.batch_size = 3
        
        callback_count = 0
        
        async def counting_callback(event: Event):
            nonlocal callback_count
            callback_count += 1
        
        await event_dispatcher.subscribe(
            "batch_subscriber",
            counting_callback
        )
        
        # Dispatch multiple events quickly
        for i in range(5):
            event = Event(
                type=EventType.CUSTOM,
                source="test_source",
                data={"index": i}
            )
            await event_dispatcher.dispatch(event)
        
        # Give time for batch processing
        await asyncio.sleep(0.3)
        
        assert callback_count == 5
    
    async def test_event_expiration(self):
        """Test event TTL and expiration."""
        # Create event with short TTL
        event = Event(
            type=EventType.CUSTOM,
            source="test_source",
            ttl=timedelta(milliseconds=100)
        )
        
        # Event should not be expired initially
        assert not event.is_expired()
        
        # Wait for expiration
        await asyncio.sleep(0.2)
        
        # Event should now be expired
        assert event.is_expired()
    
    async def test_metrics_collection(self, event_dispatcher, sample_event):
        """Test metrics collection."""
        initial_metrics = await event_dispatcher.get_metrics()
        
        # Dispatch an event
        await event_dispatcher.dispatch(sample_event)
        await asyncio.sleep(0.2)
        
        updated_metrics = await event_dispatcher.get_metrics()
        
        assert updated_metrics["events_dispatched"] > initial_metrics["events_dispatched"]
    
    async def test_health_check(self, event_dispatcher):
        """Test health check functionality."""
        health = await event_dispatcher.health_check()
        
        assert health["status"] == "healthy"
        assert "components" in health
        assert "subscription_manager" in health["components"]


@pytest.mark.asyncio
class TestEventFilter:
    """Test suite for EventFilter."""
    
    def test_filter_by_event_type(self):
        """Test filtering by event type."""
        filter = EventFilter(event_types=[EventType.TASK_STARTED])
        
        matching_event = Event(type=EventType.TASK_STARTED, source="test")
        non_matching_event = Event(type=EventType.TASK_COMPLETED, source="test")
        
        assert filter.matches(matching_event)
        assert not filter.matches(non_matching_event)
    
    def test_filter_by_source(self):
        """Test filtering by event source."""
        filter = EventFilter(sources=["agent1", "agent2"])
        
        matching_event = Event(type=EventType.CUSTOM, source="agent1")
        non_matching_event = Event(type=EventType.CUSTOM, source="agent3")
        
        assert filter.matches(matching_event)
        assert not filter.matches(non_matching_event)
    
    def test_filter_by_tags(self):
        """Test filtering by tags."""
        filter = EventFilter(tags={"important", "urgent"})
        
        # Event with matching tag
        matching_event = Event(
            type=EventType.CUSTOM,
            source="test",
            tags={"important", "routine"}
        )
        
        # Event without matching tags
        non_matching_event = Event(
            type=EventType.CUSTOM,
            source="test",
            tags={"routine", "normal"}
        )
        
        assert filter.matches(matching_event)
        assert not filter.matches(non_matching_event)
    
    def test_filter_by_severity(self):
        """Test filtering by severity level."""
        filter = EventFilter(severity_min="warning")
        
        # High severity event
        high_severity_event = Event(
            type=EventType.CUSTOM,
            source="test",
            severity="error"
        )
        
        # Low severity event
        low_severity_event = Event(
            type=EventType.CUSTOM,
            source="test",
            severity="info"
        )
        
        assert filter.matches(high_severity_event)
        assert not filter.matches(low_severity_event)
    
    def test_custom_filter(self):
        """Test custom filter function."""
        def custom_filter_func(event: Event) -> bool:
            return "special" in event.data.get("category", "")
        
        filter = EventFilter(custom_filter=custom_filter_func)
        
        matching_event = Event(
            type=EventType.CUSTOM,
            source="test",
            data={"category": "special_event"}
        )
        
        non_matching_event = Event(
            type=EventType.CUSTOM,
            source="test",
            data={"category": "normal_event"}
        )
        
        assert filter.matches(matching_event)
        assert not filter.matches(non_matching_event)


@pytest.mark.asyncio
class TestEventHelpers:
    """Test suite for event helper functions."""
    
    def test_create_agent_event(self):
        """Test agent event creation helper."""
        from src.communication.event_dispatcher.core import create_agent_event
        
        event = create_agent_event(
            EventType.AGENT_CREATED,
            "agent_123",
            {"name": "TestAgent", "capabilities": ["compute"]}
        )
        
        assert event.type == EventType.AGENT_CREATED
        assert event.source == "agent_123"
        assert event.topic == "agents"
        assert "agent" in event.tags
        assert "lifecycle" in event.tags
    
    def test_create_task_event(self):
        """Test task event creation helper."""
        from src.communication.event_dispatcher.core import create_task_event
        
        event = create_task_event(
            EventType.TASK_STARTED,
            "task_456",
            "agent_123",
            {"description": "Test task"}
        )
        
        assert event.type == EventType.TASK_STARTED
        assert event.source == "agent_123"
        assert event.topic == "tasks"
        assert event.data["task_id"] == "task_456"
        assert "task" in event.tags


if __name__ == "__main__":
    pytest.main([__file__])