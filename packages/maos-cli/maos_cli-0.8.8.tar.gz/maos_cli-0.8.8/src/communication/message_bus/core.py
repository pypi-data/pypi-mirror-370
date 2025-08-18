"""Core Redis-based message bus implementation."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set
import redis.asyncio as redis
from contextlib import asynccontextmanager

from .types import Message, MessageType, MessagePriority, DeliveryGuarantee, Subscription
from .serialization import MessageSerializer, json_serializer
from .queue_manager import PriorityQueueManager

logger = logging.getLogger(__name__)


class MessageBusError(Exception):
    """Base exception for message bus operations."""
    pass


class ConnectionError(MessageBusError):
    """Redis connection error."""
    pass


class SerializationError(MessageBusError):
    """Message serialization error."""
    pass


class MessageBus:
    """High-performance Redis-based message bus with priority queuing and delivery guarantees."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        serializer: Optional[MessageSerializer] = None,
        max_connections: int = 20,
        max_queue_size: int = 10000,
        cleanup_interval: int = 300  # 5 minutes
    ):
        self.redis_url = redis_url
        self.serializer = serializer or json_serializer
        self.max_connections = max_connections
        
        # Redis connection pools
        self.redis_pool: Optional[redis.ConnectionPool] = None
        self.pub_redis: Optional[redis.Redis] = None
        self.sub_redis: Optional[redis.Redis] = None
        
        # Queue management
        self.queue_manager = PriorityQueueManager(max_queue_size)
        
        # Subscriptions
        self.subscriptions: Dict[str, List[Subscription]] = {}
        self.pubsub: Optional[redis.client.PubSub] = None
        
        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        self.message_processor_task: Optional[asyncio.Task] = None
        self.cleanup_interval = cleanup_interval
        
        # Metrics
        self.metrics = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_failed": 0,
            "subscriptions_active": 0
        }
        
        # Status
        self.is_connected = False
        self.is_running = False
        
        logger.info("Message bus initialized")
    
    async def connect(self):
        """Initialize Redis connections and start background tasks."""
        try:
            # Create connection pool
            self.redis_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=self.max_connections,
                retry_on_timeout=True,
                retry_on_error=[ConnectionError]
            )
            
            # Create Redis clients
            self.pub_redis = redis.Redis(connection_pool=self.redis_pool)
            self.sub_redis = redis.Redis(connection_pool=self.redis_pool)
            
            # Test connections
            await self.pub_redis.ping()
            await self.sub_redis.ping()
            
            # Initialize pubsub
            self.pubsub = self.sub_redis.pubsub()
            
            self.is_connected = True
            logger.info("Connected to Redis message bus")
            
            # Start background tasks
            await self.start()
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise ConnectionError(f"Redis connection failed: {e}")
    
    async def disconnect(self):
        """Close Redis connections and stop background tasks."""
        try:
            self.is_running = False
            
            # Cancel background tasks
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            if self.message_processor_task:
                self.message_processor_task.cancel()
                try:
                    await self.message_processor_task
                except asyncio.CancelledError:
                    pass
            
            # Close pubsub
            if self.pubsub:
                await self.pubsub.close()
            
            # Close Redis connections
            if self.pub_redis:
                await self.pub_redis.close()
            if self.sub_redis:
                await self.sub_redis.close()
            
            # Close connection pool
            if self.redis_pool:
                await self.redis_pool.disconnect()
            
            self.is_connected = False
            logger.info("Disconnected from Redis message bus")
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    async def start(self):
        """Start background processing tasks."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Start message processor
        self.message_processor_task = asyncio.create_task(self._message_processor())
        
        logger.info("Message bus background tasks started")
    
    @asynccontextmanager
    async def get_redis_client(self):
        """Get a Redis client from the pool."""
        if not self.is_connected:
            raise ConnectionError("Message bus not connected")
        
        client = redis.Redis(connection_pool=self.redis_pool)
        try:
            yield client
        finally:
            await client.close()
    
    async def publish(self, message: Message) -> bool:
        """Publish a message to a topic."""
        try:
            if not self.is_connected:
                raise ConnectionError("Message bus not connected")
            
            # Set sender timestamp
            message.timestamp = datetime.utcnow()
            
            # Serialize message
            serialized_msg = self.serializer.serialize_message(message)
            
            # For point-to-point messages, use Redis lists with priority queuing
            if message.recipient:
                await self._send_point_to_point(message, serialized_msg)
            else:
                # For broadcast messages, use Redis pub/sub
                await self._send_broadcast(message, serialized_msg)
            
            self.metrics["messages_sent"] += 1
            logger.debug(f"Published message {message.id} to topic {message.topic}")
            return True
            
        except Exception as e:
            self.metrics["messages_failed"] += 1
            logger.error(f"Failed to publish message {message.id}: {e}")
            raise MessageBusError(f"Publish failed: {e}")
    
    async def _send_point_to_point(self, message: Message, serialized_msg: bytes):
        """Send point-to-point message with delivery guarantees."""
        queue_key = f"queue:{message.recipient}:{message.topic}"
        
        async with self.get_redis_client() as redis_client:
            # Add to priority queue
            await self.queue_manager.enqueue(message.topic, message)
            
            # Store in Redis with priority score
            priority_score = message.priority.value
            await redis_client.zadd(
                queue_key,
                {serialized_msg: priority_score},
                nx=True  # Only if not exists (for exactly-once delivery)
            )
            
            # Set TTL if message has expiration
            if message.expires_at:
                ttl = int((message.expires_at - datetime.utcnow()).total_seconds())
                if ttl > 0:
                    await redis_client.expire(queue_key, ttl)
    
    async def _send_broadcast(self, message: Message, serialized_msg: bytes):
        """Send broadcast message using pub/sub."""
        channel = f"broadcast:{message.topic}"
        
        async with self.get_redis_client() as redis_client:
            # Publish to Redis channel
            await redis_client.publish(channel, serialized_msg)
            
            # Store for subscribers that might be offline (if required)
            if message.delivery_guarantee == DeliveryGuarantee.AT_LEAST_ONCE:
                history_key = f"history:{message.topic}"
                await redis_client.lpush(history_key, serialized_msg)
                await redis_client.ltrim(history_key, 0, 1000)  # Keep last 1000 messages
                await redis_client.expire(history_key, 3600)  # 1 hour TTL
    
    async def subscribe(
        self,
        agent_id: str,
        topic: str,
        callback: Callable[[Message], Any],
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Subscribe to a topic with optional message filters."""
        try:
            subscription = Subscription(
                agent_id=agent_id,
                topic=topic,
                callback=callback,
                filters=filters or {}
            )
            
            # Add to subscriptions
            if topic not in self.subscriptions:
                self.subscriptions[topic] = []
            self.subscriptions[topic].append(subscription)
            
            # Subscribe to Redis channel for broadcasts
            broadcast_channel = f"broadcast:{topic}"
            await self.pubsub.subscribe(broadcast_channel)
            
            self.metrics["subscriptions_active"] += 1
            logger.info(f"Agent {agent_id} subscribed to topic {topic}")
            return subscription.id
            
        except Exception as e:
            logger.error(f"Failed to subscribe agent {agent_id} to topic {topic}: {e}")
            raise MessageBusError(f"Subscribe failed: {e}")
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from a topic."""
        try:
            # Find and remove subscription
            for topic, subs in self.subscriptions.items():
                for i, sub in enumerate(subs):
                    if sub.id == subscription_id:
                        subs.pop(i)
                        
                        # If no more subscribers, unsubscribe from Redis
                        if not subs:
                            broadcast_channel = f"broadcast:{topic}"
                            await self.pubsub.unsubscribe(broadcast_channel)
                        
                        self.metrics["subscriptions_active"] -= 1
                        logger.info(f"Unsubscribed subscription {subscription_id}")
                        return True
            
            logger.warning(f"Subscription {subscription_id} not found")
            return False
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe {subscription_id}: {e}")
            return False
    
    async def receive(self, agent_id: str, topic: str, timeout: Optional[float] = None) -> Optional[Message]:
        """Receive a message from a specific topic queue."""
        try:
            if not self.is_connected:
                raise ConnectionError("Message bus not connected")
            
            queue_key = f"queue:{agent_id}:{topic}"
            
            async with self.get_redis_client() as redis_client:
                # Get highest priority message (lowest score)
                result = await redis_client.bzpopmin(queue_key, timeout=timeout or 0)
                
                if not result:
                    return None
                
                _, serialized_msg, _ = result
                message = self.serializer.deserialize_message(serialized_msg)
                
                # Handle delivery guarantees
                if message.delivery_guarantee == DeliveryGuarantee.EXACTLY_ONCE:
                    # Remove from pending messages to prevent redelivery
                    await self.queue_manager.acknowledge_delivery(message.id, agent_id)
                
                self.metrics["messages_received"] += 1
                logger.debug(f"Received message {message.id} by agent {agent_id}")
                return message
                
        except Exception as e:
            logger.error(f"Failed to receive message for agent {agent_id}: {e}")
            return None
    
    async def _message_processor(self):
        """Process incoming broadcast messages."""
        try:
            while self.is_running:
                try:
                    # Get message from pubsub
                    message = await self.pubsub.get_message(timeout=1.0)
                    
                    if message and message["type"] == "message":
                        await self._process_broadcast_message(message)
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing broadcast message: {e}")
                    await asyncio.sleep(1)
                    
        except asyncio.CancelledError:
            logger.info("Message processor task cancelled")
            raise
        except Exception as e:
            logger.error(f"Message processor error: {e}")
    
    async def _process_broadcast_message(self, redis_message):
        """Process a broadcast message and deliver to subscribers."""
        try:
            # Extract topic from channel name
            channel = redis_message["channel"].decode()
            topic = channel.replace("broadcast:", "")
            
            # Deserialize message
            serialized_data = redis_message["data"]
            message = self.serializer.deserialize_message(serialized_data)
            
            # Deliver to subscribers
            if topic in self.subscriptions:
                for subscription in self.subscriptions[topic]:
                    if subscription.is_active and self._matches_filters(message, subscription.filters):
                        try:
                            await subscription.callback(message)
                            self.metrics["messages_received"] += 1
                        except Exception as e:
                            logger.error(f"Callback error for subscription {subscription.id}: {e}")
            
        except Exception as e:
            logger.error(f"Error processing broadcast message: {e}")
    
    def _matches_filters(self, message: Message, filters: Dict[str, Any]) -> bool:
        """Check if message matches subscription filters."""
        if not filters:
            return True
        
        for key, value in filters.items():
            if key == "message_type" and message.type.value != value:
                return False
            elif key == "sender" and message.sender != value:
                return False
            elif key == "priority" and message.priority.value > value:
                return False
            # Add more filter criteria as needed
        
        return True
    
    async def _cleanup_loop(self):
        """Periodic cleanup of expired messages and metrics."""
        try:
            while self.is_running:
                try:
                    # Cleanup expired messages
                    await self.queue_manager.cleanup_expired_messages()
                    
                    # Cleanup Redis keys
                    await self._cleanup_redis_keys()
                    
                    logger.debug("Cleanup completed")
                    
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")
                
                # Wait for next cleanup cycle
                await asyncio.sleep(self.cleanup_interval)
                
        except asyncio.CancelledError:
            logger.info("Cleanup task cancelled")
            raise
        except Exception as e:
            logger.error(f"Cleanup loop error: {e}")
    
    async def _cleanup_redis_keys(self):
        """Clean up expired Redis keys."""
        try:
            async with self.get_redis_client() as redis_client:
                # Get all queue keys
                queue_keys = await redis_client.keys("queue:*")
                
                for key in queue_keys:
                    # Remove expired messages from sorted sets
                    now = datetime.utcnow().timestamp()
                    await redis_client.zremrangebyscore(key, "-inf", now - 3600)  # Remove messages older than 1 hour
                    
        except Exception as e:
            logger.error(f"Redis cleanup error: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get message bus metrics."""
        queue_stats = await self.queue_manager.get_all_stats()
        
        return {
            **self.metrics,
            "is_connected": self.is_connected,
            "is_running": self.is_running,
            "active_subscriptions": sum(len(subs) for subs in self.subscriptions.values()),
            "queue_stats": queue_stats
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on message bus."""
        try:
            if not self.is_connected:
                return {"status": "unhealthy", "reason": "not_connected"}
            
            # Test Redis connectivity
            async with self.get_redis_client() as redis_client:
                latency = await redis_client.ping()
                
            return {
                "status": "healthy",
                "redis_latency": latency,
                "metrics": await self.get_metrics()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "reason": str(e)}
    
    # Context manager support
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()