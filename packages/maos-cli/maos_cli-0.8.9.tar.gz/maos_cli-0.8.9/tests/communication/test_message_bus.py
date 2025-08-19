"""Tests for message bus functionality."""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.communication.message_bus import (
    MessageBus, MessagePriority, DeliveryGuarantee, Message, MessageType
)
from src.communication.message_bus.serialization import MessageSerializer


@pytest.fixture
async def message_bus():
    """Create a test message bus instance."""
    with patch('redis.asyncio.ConnectionPool'):
        with patch('redis.asyncio.Redis'):
            bus = MessageBus("redis://localhost:6379")
            
            # Mock Redis clients
            bus.pub_redis = AsyncMock()
            bus.sub_redis = AsyncMock()
            bus.pubsub = AsyncMock()
            
            # Mock ping responses
            bus.pub_redis.ping.return_value = True
            bus.sub_redis.ping.return_value = True
            
            await bus.connect()
            yield bus
            await bus.disconnect()


@pytest.fixture
def sample_message():
    """Create a sample message for testing."""
    return Message(
        type=MessageType.COMMAND,
        sender="test_agent",
        recipient="target_agent",
        topic="test_topic",
        payload={"action": "test", "data": "sample"},
        priority=MessagePriority.NORMAL
    )


@pytest.mark.asyncio
class TestMessageBus:
    """Test suite for MessageBus."""
    
    async def test_connection(self, message_bus):
        """Test Redis connection setup."""
        assert message_bus.is_connected
        assert message_bus.is_running
    
    async def test_publish_point_to_point(self, message_bus, sample_message):
        """Test point-to-point message publishing."""
        sample_message.recipient = "specific_agent"
        
        with patch.object(message_bus, '_send_point_to_point', new_callable=AsyncMock) as mock_send:
            result = await message_bus.publish(sample_message)
            
            assert result is True
            mock_send.assert_called_once()
            assert message_bus.metrics["messages_sent"] == 1
    
    async def test_publish_broadcast(self, message_bus, sample_message):
        """Test broadcast message publishing."""
        sample_message.recipient = None  # Broadcast
        
        with patch.object(message_bus, '_send_broadcast', new_callable=AsyncMock) as mock_send:
            result = await message_bus.publish(sample_message)
            
            assert result is True
            mock_send.assert_called_once()
            assert message_bus.metrics["messages_sent"] == 1
    
    async def test_subscribe(self, message_bus):
        """Test topic subscription."""
        callback = AsyncMock()
        
        subscription_id = await message_bus.subscribe(
            "test_agent", "test_topic", callback
        )
        
        assert subscription_id is not None
        assert "test_topic" in message_bus.subscriptions
        assert len(message_bus.subscriptions["test_topic"]) == 1
        assert message_bus.metrics["subscriptions_active"] == 1
    
    async def test_unsubscribe(self, message_bus):
        """Test unsubscribing from topic."""
        callback = AsyncMock()
        
        subscription_id = await message_bus.subscribe(
            "test_agent", "test_topic", callback
        )
        
        result = await message_bus.unsubscribe(subscription_id)
        
        assert result is True
        assert message_bus.metrics["subscriptions_active"] == 0
    
    async def test_message_serialization(self, sample_message):
        """Test message serialization/deserialization."""
        serializer = MessageSerializer("json")
        
        # Serialize
        serialized = serializer.serialize_message(sample_message)
        assert isinstance(serialized, bytes)
        
        # Deserialize
        deserialized = serializer.deserialize_message(serialized)
        assert deserialized.id == sample_message.id
        assert deserialized.sender == sample_message.sender
        assert deserialized.payload == sample_message.payload
    
    async def test_message_expiration(self):
        """Test message expiration checking."""
        # Expired message
        expired_message = Message(
            type=MessageType.COMMAND,
            sender="test_agent",
            expires_at=datetime.utcnow() - timedelta(seconds=10)
        )
        assert expired_message.is_expired()
        
        # Non-expired message
        fresh_message = Message(
            type=MessageType.COMMAND,
            sender="test_agent",
            expires_at=datetime.utcnow() + timedelta(seconds=10)
        )
        assert not fresh_message.is_expired()
    
    async def test_delivery_guarantees(self, message_bus, sample_message):
        """Test different delivery guarantee modes."""
        # At-most-once (fire and forget)
        sample_message.delivery_guarantee = DeliveryGuarantee.AT_MOST_ONCE
        result = await message_bus.publish(sample_message)
        assert result is True
        
        # At-least-once (with acknowledgment)
        sample_message.delivery_guarantee = DeliveryGuarantee.AT_LEAST_ONCE
        result = await message_bus.publish(sample_message)
        assert result is True
        
        # Exactly-once (with deduplication)
        sample_message.delivery_guarantee = DeliveryGuarantee.EXACTLY_ONCE
        result = await message_bus.publish(sample_message)
        assert result is True
    
    async def test_priority_handling(self, message_bus):
        """Test message priority handling."""
        high_priority_msg = Message(
            type=MessageType.COMMAND,
            sender="test_agent",
            recipient="target_agent",
            topic="test_topic",
            priority=MessagePriority.HIGH
        )
        
        low_priority_msg = Message(
            type=MessageType.COMMAND,
            sender="test_agent", 
            recipient="target_agent",
            topic="test_topic",
            priority=MessagePriority.LOW
        )
        
        # Publish both messages
        await message_bus.publish(high_priority_msg)
        await message_bus.publish(low_priority_msg)
        
        # High priority should have lower numeric value (higher priority)
        assert high_priority_msg.priority.value < low_priority_msg.priority.value
    
    async def test_health_check(self, message_bus):
        """Test health check functionality."""
        health = await message_bus.health_check()
        
        assert health["status"] == "healthy"
        assert health["is_connected"] is True
        assert "redis_latency" in health
        assert "metrics" in health
    
    async def test_metrics(self, message_bus, sample_message):
        """Test metrics collection."""
        initial_metrics = await message_bus.get_metrics()
        
        # Publish a message
        await message_bus.publish(sample_message)
        
        updated_metrics = await message_bus.get_metrics()
        
        assert updated_metrics["messages_sent"] > initial_metrics["messages_sent"]
    
    async def test_error_handling(self, message_bus):
        """Test error handling in message operations."""
        # Test with invalid message
        invalid_message = None
        
        with pytest.raises(Exception):
            await message_bus.publish(invalid_message)
        
        assert message_bus.metrics["messages_failed"] > 0


@pytest.mark.asyncio
class TestPriorityQueueManager:
    """Test suite for PriorityQueueManager."""
    
    @pytest.fixture
    def queue_manager(self):
        """Create test queue manager."""
        from src.communication.message_bus.queue_manager import PriorityQueueManager
        return PriorityQueueManager(max_queue_size=100)
    
    async def test_enqueue_dequeue(self, queue_manager, sample_message):
        """Test basic enqueue/dequeue operations."""
        topic = "test_topic"
        
        # Enqueue message
        result = await queue_manager.enqueue(topic, sample_message)
        assert result is True
        
        # Check queue stats
        stats = await queue_manager.get_queue_stats(topic)
        assert stats["queue_size"] == 1
        
        # Dequeue message
        dequeued = await queue_manager.dequeue(topic)
        assert dequeued is not None
        assert dequeued.id == sample_message.id
        
        # Queue should be empty
        stats = await queue_manager.get_queue_stats(topic)
        assert stats["queue_size"] == 0
    
    async def test_priority_ordering(self, queue_manager):
        """Test priority-based message ordering."""
        topic = "test_topic"
        
        # Create messages with different priorities
        low_msg = Message(
            type=MessageType.COMMAND,
            sender="test",
            topic=topic,
            priority=MessagePriority.LOW
        )
        
        high_msg = Message(
            type=MessageType.COMMAND,
            sender="test",
            topic=topic,
            priority=MessagePriority.HIGH
        )
        
        critical_msg = Message(
            type=MessageType.COMMAND,
            sender="test",
            topic=topic,
            priority=MessagePriority.CRITICAL
        )
        
        # Enqueue in non-priority order
        await queue_manager.enqueue(topic, low_msg)
        await queue_manager.enqueue(topic, high_msg)
        await queue_manager.enqueue(topic, critical_msg)
        
        # Dequeue should return in priority order
        first = await queue_manager.dequeue(topic)
        assert first.priority == MessagePriority.CRITICAL
        
        second = await queue_manager.dequeue(topic)
        assert second.priority == MessagePriority.HIGH
        
        third = await queue_manager.dequeue(topic)
        assert third.priority == MessagePriority.LOW
    
    async def test_queue_size_limits(self, queue_manager):
        """Test queue size limitations."""
        topic = "test_topic"
        max_size = queue_manager.max_queue_size
        
        # Fill queue to capacity
        for i in range(max_size + 10):  # Try to add more than max
            msg = Message(
                type=MessageType.COMMAND,
                sender="test",
                topic=topic,
                priority=MessagePriority.NORMAL
            )
            await queue_manager.enqueue(topic, msg)
        
        stats = await queue_manager.get_queue_stats(topic)
        assert stats["queue_size"] <= max_size
        assert stats["dropped_messages"] > 0
    
    async def test_expired_message_cleanup(self, queue_manager):
        """Test cleanup of expired messages."""
        topic = "test_topic"
        
        # Create expired message
        expired_msg = Message(
            type=MessageType.COMMAND,
            sender="test",
            topic=topic,
            expires_at=datetime.utcnow() - timedelta(seconds=10)
        )
        
        await queue_manager.enqueue(topic, expired_msg)
        
        # Cleanup should remove expired messages
        await queue_manager.cleanup_expired_messages()
        
        # Try to dequeue - should get nothing
        dequeued = await queue_manager.dequeue(topic)
        assert dequeued is None


if __name__ == "__main__":
    pytest.main([__file__])