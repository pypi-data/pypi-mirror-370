"""Priority queue management for message bus."""

import asyncio
import heapq
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import logging

from .types import Message, MessagePriority, DeliveryGuarantee

logger = logging.getLogger(__name__)


@dataclass
class QueuedMessage:
    """Message wrapper for priority queue."""
    priority: int
    timestamp: float
    message: Message
    
    def __lt__(self, other):
        """Compare messages for priority queue ordering."""
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.timestamp < other.timestamp


class PriorityQueueManager:
    """Manages priority queues for different topics and delivery guarantees."""
    
    def __init__(self, max_queue_size: int = 10000):
        self.max_queue_size = max_queue_size
        
        # Priority queues by topic
        self.queues: Dict[str, List[QueuedMessage]] = defaultdict(list)
        
        # Delivery tracking
        self.pending_messages: Dict[str, Message] = {}  # message_id -> message
        self.delivery_receipts: Dict[str, Set[str]] = defaultdict(set)  # message_id -> recipients
        
        # Queue metrics
        self.queue_sizes: Dict[str, int] = defaultdict(int)
        self.dropped_messages: Dict[str, int] = defaultdict(int)
        
        # Locks for thread safety
        self.queue_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        
        logger.info("Priority queue manager initialized")
    
    async def enqueue(self, topic: str, message: Message) -> bool:
        """Enqueue a message with priority handling."""
        try:
            async with self.queue_locks[topic]:
                # Check queue size limits
                if self.queue_sizes[topic] >= self.max_queue_size:
                    # Drop lowest priority messages if needed
                    await self._drop_low_priority_messages(topic)
                    
                    if self.queue_sizes[topic] >= self.max_queue_size:
                        self.dropped_messages[topic] += 1
                        logger.warning(f"Queue {topic} full, dropping message {message.id}")
                        return False
                
                # Create queued message
                queued_msg = QueuedMessage(
                    priority=message.priority.value,
                    timestamp=time.time(),
                    message=message
                )
                
                # Add to priority queue
                heapq.heappush(self.queues[topic], queued_msg)
                self.queue_sizes[topic] += 1
                
                # Track for delivery guarantees
                if message.delivery_guarantee != DeliveryGuarantee.AT_MOST_ONCE:
                    self.pending_messages[message.id] = message
                
                logger.debug(f"Enqueued message {message.id} to topic {topic}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to enqueue message {message.id}: {e}")
            return False
    
    async def dequeue(self, topic: str) -> Optional[Message]:
        """Dequeue the highest priority message from a topic."""
        try:
            async with self.queue_locks[topic]:
                if not self.queues[topic]:
                    return None
                
                # Get highest priority message
                queued_msg = heapq.heappop(self.queues[topic])
                self.queue_sizes[topic] -= 1
                
                message = queued_msg.message
                
                # Check if message expired
                if message.is_expired():
                    logger.debug(f"Message {message.id} expired, skipping")
                    return await self.dequeue(topic)  # Try next message
                
                logger.debug(f"Dequeued message {message.id} from topic {topic}")
                return message
                
        except Exception as e:
            logger.error(f"Failed to dequeue from topic {topic}: {e}")
            return None
    
    async def peek(self, topic: str) -> Optional[Message]:
        """Peek at the highest priority message without removing it."""
        try:
            async with self.queue_locks[topic]:
                if not self.queues[topic]:
                    return None
                
                return self.queues[topic][0].message
                
        except Exception as e:
            logger.error(f"Failed to peek topic {topic}: {e}")
            return None
    
    async def acknowledge_delivery(self, message_id: str, recipient: str):
        """Acknowledge successful message delivery."""
        try:
            if message_id in self.pending_messages:
                self.delivery_receipts[message_id].add(recipient)
                
                message = self.pending_messages[message_id]
                
                # For point-to-point messages, one acknowledgment is enough
                if message.recipient:
                    if recipient == message.recipient:
                        del self.pending_messages[message_id]
                        del self.delivery_receipts[message_id]
                        logger.debug(f"Message {message_id} delivery acknowledged")
                
                # For broadcast messages, we may need multiple acknowledgments
                # (implementation depends on requirements)
                
        except Exception as e:
            logger.error(f"Failed to acknowledge delivery for {message_id}: {e}")
    
    async def handle_delivery_failure(self, message_id: str, recipient: str, error: str):
        """Handle failed message delivery."""
        try:
            if message_id not in self.pending_messages:
                return
            
            message = self.pending_messages[message_id]
            message.retry_count += 1
            
            logger.warning(f"Delivery failed for message {message_id} to {recipient}: {error}")
            
            # Check retry limits
            if message.retry_count >= message.max_retries:
                logger.error(f"Message {message_id} exceeded max retries, dropping")
                del self.pending_messages[message_id]
                if message_id in self.delivery_receipts:
                    del self.delivery_receipts[message_id]
            else:
                # Re-queue for retry
                await self.enqueue(message.topic, message)
                
        except Exception as e:
            logger.error(f"Failed to handle delivery failure for {message_id}: {e}")
    
    async def _drop_low_priority_messages(self, topic: str, count: int = 1):
        """Drop lowest priority messages to make room."""
        try:
            queue = self.queues[topic]
            if not queue:
                return
            
            # Sort by priority (reverse to get lowest priority first)
            queue.sort(key=lambda x: (-x.priority, -x.timestamp))
            
            # Drop the specified number of lowest priority messages
            for _ in range(min(count, len(queue))):
                dropped = queue.pop()
                self.queue_sizes[topic] -= 1
                self.dropped_messages[topic] += 1
                logger.debug(f"Dropped low priority message {dropped.message.id}")
            
            # Restore heap property
            heapq.heapify(queue)
            
        except Exception as e:
            logger.error(f"Failed to drop low priority messages: {e}")
    
    async def get_queue_stats(self, topic: str) -> Dict[str, int]:
        """Get queue statistics for a topic."""
        async with self.queue_locks[topic]:
            return {
                "queue_size": self.queue_sizes[topic],
                "dropped_messages": self.dropped_messages[topic],
                "pending_messages": len([m for m in self.pending_messages.values() if m.topic == topic])
            }
    
    async def get_all_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics for all queues."""
        stats = {}
        for topic in self.queues.keys():
            stats[topic] = await self.get_queue_stats(topic)
        return stats
    
    async def cleanup_expired_messages(self):
        """Clean up expired messages from all queues."""
        try:
            for topic in list(self.queues.keys()):
                async with self.queue_locks[topic]:
                    queue = self.queues[topic]
                    cleaned_queue = []
                    
                    for queued_msg in queue:
                        if not queued_msg.message.is_expired():
                            cleaned_queue.append(queued_msg)
                        else:
                            self.queue_sizes[topic] -= 1
                            logger.debug(f"Cleaned expired message {queued_msg.message.id}")
                    
                    # Update queue
                    self.queues[topic] = cleaned_queue
                    heapq.heapify(self.queues[topic])
            
            # Clean up pending messages
            expired_ids = [
                msg_id for msg_id, msg in self.pending_messages.items()
                if msg.is_expired()
            ]
            
            for msg_id in expired_ids:
                del self.pending_messages[msg_id]
                if msg_id in self.delivery_receipts:
                    del self.delivery_receipts[msg_id]
                logger.debug(f"Cleaned expired pending message {msg_id}")
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired messages: {e}")
    
    async def flush_topic(self, topic: str) -> int:
        """Flush all messages from a topic queue."""
        try:
            async with self.queue_locks[topic]:
                count = len(self.queues[topic])
                self.queues[topic].clear()
                self.queue_sizes[topic] = 0
                logger.info(f"Flushed {count} messages from topic {topic}")
                return count
                
        except Exception as e:
            logger.error(f"Failed to flush topic {topic}: {e}")
            return 0
    
    async def get_topics(self) -> List[str]:
        """Get list of all active topics."""
        return list(self.queues.keys())