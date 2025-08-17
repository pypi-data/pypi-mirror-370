"""
Unit tests for Message Bus component.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.communication.message_bus.core import MessageBus, MessageBusError, ConnectionError
from src.communication.message_bus.types import Message, MessageType, MessagePriority, DeliveryGuarantee
from tests.utils.test_helpers import TestDataFactory


@pytest.mark.unit
@pytest.mark.redis_required
class TestMessageBus:
    """Test suite for MessageBus class."""

    @pytest.fixture
    async def message_bus(self):
        """Create MessageBus instance for testing."""
        bus = MessageBus(redis_url="redis://localhost:6379/1")
        return bus

    @pytest.fixture
    async def connected_bus(self, clean_redis):
        """Create connected MessageBus instance."""
        bus = MessageBus(redis_url="redis://localhost:6379/1")
        await bus.connect()
        yield bus
        await bus.disconnect()

    async def test_message_bus_initialization(self):
        """Test message bus initialization."""
        bus = MessageBus(redis_url="redis://localhost:6379/1")
        
        assert bus.redis_url == "redis://localhost:6379/1"
        assert bus.is_connected is False
        assert bus.is_running is False
        assert bus.metrics["messages_sent"] == 0

    async def test_connect_success(self, clean_redis):
        """Test successful connection to Redis."""
        bus = MessageBus(redis_url="redis://localhost:6379/1")
        
        await bus.connect()
        
        assert bus.is_connected is True
        assert bus.is_running is True
        assert bus.pub_redis is not None
        assert bus.sub_redis is not None
        
        await bus.disconnect()

    async def test_connect_failure(self):
        """Test connection failure handling."""
        bus = MessageBus(redis_url="redis://invalid:9999")
        
        with pytest.raises(ConnectionError):
            await bus.connect()
        
        assert bus.is_connected is False

    async def test_disconnect(self, connected_bus):
        """Test disconnection from Redis."""
        assert connected_bus.is_connected is True
        assert connected_bus.is_running is True
        
        await connected_bus.disconnect()
        
        assert connected_bus.is_connected is False
        assert connected_bus.is_running is False

    async def test_publish_point_to_point_message(self, connected_bus):
        """Test publishing point-to-point message."""
        message = TestDataFactory.create_message(
            MessageType.TASK_ASSIGNMENT,
            topic="test_topic",
            payload={"task_id": str(uuid4())},
            recipient="test_agent"
        )
        
        result = await connected_bus.publish(message)
        
        assert result is True
        assert connected_bus.metrics["messages_sent"] == 1

    async def test_publish_broadcast_message(self, connected_bus):
        """Test publishing broadcast message."""
        message = TestDataFactory.create_message(
            MessageType.STATUS_UPDATE,
            topic="system_events",
            payload={"status": "running"}
        )
        # No recipient = broadcast
        
        result = await connected_bus.publish(message)
        
        assert result is True
        assert connected_bus.metrics["messages_sent"] == 1

    async def test_publish_not_connected(self, message_bus):
        """Test publishing when not connected."""
        message = TestDataFactory.create_message()
        
        with pytest.raises(MessageBusError, match="not connected"):
            await message_bus.publish(message)

    async def test_subscribe_to_topic(self, connected_bus):
        """Test subscribing to a topic."""
        callback = AsyncMock()
        
        subscription_id = await connected_bus.subscribe(
            agent_id="test_agent",
            topic="test_topic",
            callback=callback
        )
        
        assert subscription_id is not None
        assert connected_bus.metrics["subscriptions_active"] == 1
        assert "test_topic" in connected_bus.subscriptions

    async def test_unsubscribe_from_topic(self, connected_bus):
        """Test unsubscribing from a topic."""
        callback = AsyncMock()
        
        subscription_id = await connected_bus.subscribe(
            agent_id="test_agent",
            topic="test_topic",
            callback=callback
        )
        
        result = await connected_bus.unsubscribe(subscription_id)
        
        assert result is True
        assert connected_bus.metrics["subscriptions_active"] == 0

    async def test_receive_message(self, connected_bus):
        """Test receiving a point-to-point message."""
        # First publish a message
        message = TestDataFactory.create_message(
            MessageType.TASK_ASSIGNMENT,
            topic="test_topic",
            payload={"test": "data"},
            recipient="test_agent"
        )
        
        await connected_bus.publish(message)
        
        # Then try to receive it
        received_message = await connected_bus.receive(
            agent_id="test_agent",
            topic="test_topic",
            timeout=1.0
        )
        
        assert received_message is not None
        assert received_message.type == MessageType.TASK_ASSIGNMENT
        assert received_message.payload["test"] == "data"
        assert connected_bus.metrics["messages_received"] == 1

    async def test_receive_timeout(self, connected_bus):
        """Test receiving with timeout when no messages."""
        received_message = await connected_bus.receive(
            agent_id="test_agent",
            topic="empty_topic",
            timeout=0.1
        )
        
        assert received_message is None

    async def test_message_priority_ordering(self, connected_bus):
        """Test that high priority messages are received first."""
        agent_id = "test_agent"
        topic = "priority_test"
        
        # Send low priority message first
        low_priority_msg = TestDataFactory.create_message(
            MessageType.STATUS_UPDATE,
            topic=topic,
            payload={"priority": "low"},
            recipient=agent_id,
            priority=MessagePriority.LOW
        )
        
        # Then high priority message
        high_priority_msg = TestDataFactory.create_message(
            MessageType.TASK_ASSIGNMENT,
            topic=topic,
            payload={"priority": "high"},
            recipient=agent_id,
            priority=MessagePriority.HIGH
        )
        
        await connected_bus.publish(low_priority_msg)
        await connected_bus.publish(high_priority_msg)
        
        # Should receive high priority first
        received_msg = await connected_bus.receive(agent_id, topic, timeout=1.0)
        assert received_msg.payload["priority"] == "high"
        
        # Then low priority
        received_msg = await connected_bus.receive(agent_id, topic, timeout=1.0)
        assert received_msg.payload["priority"] == "low"

    async def test_message_expiration(self, connected_bus):
        """Test that expired messages are not received."""
        message = TestDataFactory.create_message(
            MessageType.TASK_ASSIGNMENT,
            topic="expiry_test",
            recipient="test_agent",
            expires_at=datetime.utcnow() + timedelta(milliseconds=100)
        )
        
        await connected_bus.publish(message)
        
        # Wait for message to expire
        await asyncio.sleep(0.2)
        
        # Should not receive expired message
        received_msg = await connected_bus.receive(
            "test_agent", "expiry_test", timeout=0.1
        )
        assert received_msg is None

    async def test_delivery_guarantee_exactly_once(self, connected_bus):
        """Test exactly-once delivery guarantee."""
        message = TestDataFactory.create_message(
            MessageType.TASK_ASSIGNMENT,
            topic="exactly_once_test",
            recipient="test_agent",
            delivery_guarantee=DeliveryGuarantee.EXACTLY_ONCE
        )
        
        await connected_bus.publish(message)
        
        # First receive should succeed
        received_msg1 = await connected_bus.receive(
            "test_agent", "exactly_once_test", timeout=1.0
        )
        assert received_msg1 is not None
        
        # Second receive should return None (message already delivered)
        received_msg2 = await connected_bus.receive(
            "test_agent", "exactly_once_test", timeout=0.1
        )
        assert received_msg2 is None

    async def test_broadcast_message_delivery(self, connected_bus):
        """Test broadcast message delivery to multiple subscribers."""
        callback1 = AsyncMock()
        callback2 = AsyncMock()
        
        # Subscribe two agents
        await connected_bus.subscribe("agent1", "broadcast_test", callback1)
        await connected_bus.subscribe("agent2", "broadcast_test", callback2)
        
        # Publish broadcast message
        message = TestDataFactory.create_message(
            MessageType.STATUS_UPDATE,
            topic="broadcast_test",
            payload={"broadcast": "test"}
        )
        
        await connected_bus.publish(message)
        
        # Give some time for delivery
        await asyncio.sleep(0.1)
        
        # Both callbacks should have been called
        callback1.assert_called_once()
        callback2.assert_called_once()

    async def test_message_filtering(self, connected_bus):
        """Test message filtering in subscriptions."""
        callback = AsyncMock()
        
        # Subscribe with filter
        await connected_bus.subscribe(
            agent_id="test_agent",
            topic="filtered_topic",
            callback=callback,
            filters={"message_type": MessageType.TASK_ASSIGNMENT.value}
        )
        
        # Send matching message
        matching_msg = TestDataFactory.create_message(
            MessageType.TASK_ASSIGNMENT,
            topic="filtered_topic",
            payload={"match": True}
        )
        
        # Send non-matching message
        non_matching_msg = TestDataFactory.create_message(
            MessageType.STATUS_UPDATE,
            topic="filtered_topic",
            payload={"match": False}
        )
        
        await connected_bus.publish(matching_msg)
        await connected_bus.publish(non_matching_msg)
        
        await asyncio.sleep(0.1)
        
        # Only matching message should trigger callback
        callback.assert_called_once()

    async def test_health_check_healthy(self, connected_bus):
        """Test health check when bus is healthy."""
        health = await connected_bus.health_check()
        
        assert health["status"] == "healthy"
        assert "redis_latency" in health
        assert "metrics" in health

    async def test_health_check_unhealthy(self, message_bus):
        """Test health check when bus is not connected."""
        health = await message_bus.health_check()
        
        assert health["status"] == "unhealthy"
        assert health["reason"] == "not_connected"

    async def test_get_metrics(self, connected_bus):
        """Test getting message bus metrics."""
        # Send some messages to generate metrics
        message = TestDataFactory.create_message()
        await connected_bus.publish(message)
        
        metrics = await connected_bus.get_metrics()
        
        assert "messages_sent" in metrics
        assert "is_connected" in metrics
        assert "is_running" in metrics
        assert metrics["messages_sent"] == 1
        assert metrics["is_connected"] is True

    async def test_cleanup_expired_messages(self, connected_bus):
        """Test cleanup of expired messages."""
        # Create expired message
        expired_msg = TestDataFactory.create_message(
            expires_at=datetime.utcnow() - timedelta(hours=2)
        )
        
        await connected_bus.publish(expired_msg)
        
        # Trigger cleanup manually
        await connected_bus._cleanup_redis_keys()
        
        # Should not be able to receive expired message
        received = await connected_bus.receive(
            "test_agent", "test_topic", timeout=0.1
        )
        assert received is None

    async def test_context_manager(self, clean_redis):
        """Test using message bus as context manager."""
        async with MessageBus(redis_url="redis://localhost:6379/1") as bus:
            assert bus.is_connected is True
            
            # Use the bus
            message = TestDataFactory.create_message()
            await bus.publish(message)
        
        # Should be disconnected after context exit
        assert bus.is_connected is False

    async def test_concurrent_message_handling(self, connected_bus):
        """Test handling multiple concurrent messages."""
        num_messages = 100
        agent_id = "concurrent_agent"
        topic = "concurrent_topic"
        
        # Send multiple messages concurrently
        tasks = []
        for i in range(num_messages):
            message = TestDataFactory.create_message(
                topic=topic,
                recipient=agent_id,
                payload={"index": i}
            )
            tasks.append(connected_bus.publish(message))
        
        await asyncio.gather(*tasks)
        
        # Receive all messages
        received_count = 0
        while True:
            msg = await connected_bus.receive(agent_id, topic, timeout=0.1)
            if msg is None:
                break
            received_count += 1
        
        assert received_count == num_messages
        assert connected_bus.metrics["messages_sent"] == num_messages