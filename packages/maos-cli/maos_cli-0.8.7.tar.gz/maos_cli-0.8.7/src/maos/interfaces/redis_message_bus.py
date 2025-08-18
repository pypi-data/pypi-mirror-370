"""
Redis-backed message bus for MAOS orchestration system.

Provides distributed pub/sub messaging using Redis for inter-component communication.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Set, Any, Callable
from uuid import UUID, uuid4
from datetime import datetime
import os
import aioredis
from aioredis import Redis

from .message_bus import MessageBus, EventHandler
from ..models.message import Message, MessageType, MessagePriority
from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError


class RedisMessageBus(MessageBus):
    """
    Redis-backed distributed message bus.
    
    Extends the base MessageBus to use Redis pub/sub for distributed messaging,
    enabling communication across multiple MAOS instances and workers.
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        channel_prefix: str = "maos",
        max_queue_size: int = 10000,
        dead_letter_enabled: bool = True,
        message_ttl_seconds: int = 300,
        delivery_retry_attempts: int = 3,
        enable_persistence: bool = True
    ):
        """
        Initialize Redis message bus.
        
        Args:
            redis_url: Redis connection URL
            channel_prefix: Prefix for Redis channels
            max_queue_size: Maximum queue size
            dead_letter_enabled: Enable dead letter queue
            message_ttl_seconds: Message TTL in seconds
            delivery_retry_attempts: Number of delivery retries
            enable_persistence: Persist messages to Redis
        """
        # Initialize parent class
        super().__init__(
            max_queue_size=max_queue_size,
            dead_letter_enabled=dead_letter_enabled,
            message_ttl_seconds=message_ttl_seconds,
            delivery_retry_attempts=delivery_retry_attempts
        )
        
        # Redis configuration
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.channel_prefix = channel_prefix
        self.enable_persistence = enable_persistence
        
        # Redis connections
        self.redis_client: Optional[Redis] = None
        self.pubsub_client: Optional[Redis] = None
        self.subscriber: Optional[aioredis.client.PubSub] = None
        
        # Channel management
        self._subscribed_channels: Set[str] = set()
        self._channel_handlers: Dict[str, List[EventHandler]] = {}
        
        # Background tasks
        self._redis_listener_task: Optional[asyncio.Task] = None
        
        # Override logger name
        self.logger = MAOSLogger("redis_message_bus", str(uuid4()))
    
    async def start(self) -> None:
        """Start the Redis message bus and connections."""
        if self._running:
            return
        
        try:
            self.logger.logger.info(f"Starting Redis Message Bus with URL: {self.redis_url}")
            
            # Create Redis connections
            self.redis_client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False  # We'll handle encoding/decoding
            )
            
            self.pubsub_client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False
            )
            
            # Test connection
            await self.redis_client.ping()
            
            # Create pubsub subscriber
            self.subscriber = self.pubsub_client.pubsub()
            
            # Subscribe to global channel
            global_channel = f"{self.channel_prefix}:global"
            await self.subscriber.subscribe(global_channel)
            self._subscribed_channels.add(global_channel)
            
            # Start parent class
            await super().start()
            
            # Start Redis listener
            self._redis_listener_task = asyncio.create_task(self._redis_listener_loop())
            
            self.logger.logger.info("Redis Message Bus started successfully")
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'start'})
            raise MAOSError(f"Failed to start Redis message bus: {str(e)}")
    
    async def stop(self) -> None:
        """Stop the Redis message bus and close connections."""
        if not self._running:
            return
        
        self.logger.logger.info("Stopping Redis Message Bus")
        
        # Stop Redis listener
        if self._redis_listener_task:
            self._redis_listener_task.cancel()
            try:
                await self._redis_listener_task
            except asyncio.CancelledError:
                pass
        
        # Unsubscribe from all channels
        if self.subscriber:
            for channel in self._subscribed_channels:
                await self.subscriber.unsubscribe(channel)
            await self.subscriber.close()
        
        # Close Redis connections
        if self.redis_client:
            await self.redis_client.close()
        
        if self.pubsub_client:
            await self.pubsub_client.close()
        
        # Stop parent class
        await super().stop()
        
        self.logger.logger.info("Redis Message Bus stopped")
    
    async def publish(
        self,
        message: Message,
        topic: Optional[str] = None
    ) -> None:
        """
        Publish a message to Redis.
        
        Args:
            message: Message to publish
            topic: Optional topic (uses message type if not specified)
        """
        if not self._running:
            raise MAOSError("Message bus is not running")
        
        try:
            # Determine channel
            if topic:
                channel = f"{self.channel_prefix}:{topic}"
            else:
                channel = f"{self.channel_prefix}:{message.message_type.value}"
            
            # Serialize message
            message_data = {
                'id': str(message.id),
                'message_type': message.message_type.value,
                'priority': message.priority.value,
                'source': message.source,
                'target': message.target,
                'payload': message.payload,
                'correlation_id': str(message.correlation_id) if message.correlation_id else None,
                'timestamp': message.timestamp.isoformat(),
                'retry_count': message.retry_count,
                'metadata': message.metadata
            }
            
            serialized = json.dumps(message_data)
            
            # Publish to Redis
            await self.redis_client.publish(channel, serialized)
            
            # Also publish to global channel for broadcast
            if channel != f"{self.channel_prefix}:global":
                await self.redis_client.publish(f"{self.channel_prefix}:global", serialized)
            
            # Persist message if enabled
            if self.enable_persistence:
                await self._persist_message(message)
            
            # Update metrics
            self._metrics['messages_published'] += 1
            
            # Call parent publish for local handlers
            await super().publish(message, topic)
            
            self.logger.logger.debug(
                f"Published message to Redis",
                extra={
                    'message_id': str(message.id),
                    'channel': channel,
                    'type': message.message_type.value
                }
            )
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'publish',
                'message_id': str(message.id)
            })
            raise MAOSError(f"Failed to publish message: {str(e)}")
    
    async def subscribe(
        self,
        topic: str,
        handler: EventHandler
    ) -> None:
        """
        Subscribe to a Redis channel.
        
        Args:
            topic: Topic to subscribe to
            handler: Handler for messages on this topic
        """
        channel = f"{self.channel_prefix}:{topic}"
        
        # Subscribe to Redis channel if not already subscribed
        if channel not in self._subscribed_channels:
            await self.subscriber.subscribe(channel)
            self._subscribed_channels.add(channel)
            
            self.logger.logger.info(
                f"Subscribed to Redis channel",
                extra={'channel': channel}
            )
        
        # Register handler
        if channel not in self._channel_handlers:
            self._channel_handlers[channel] = []
        
        if handler not in self._channel_handlers[channel]:
            self._channel_handlers[channel].append(handler)
        
        # Also register with parent for local handling
        await super().subscribe(topic, handler)
    
    async def unsubscribe(
        self,
        topic: str,
        handler: EventHandler
    ) -> None:
        """
        Unsubscribe from a Redis channel.
        
        Args:
            topic: Topic to unsubscribe from
            handler: Handler to remove
        """
        channel = f"{self.channel_prefix}:{topic}"
        
        # Remove handler
        if channel in self._channel_handlers:
            if handler in self._channel_handlers[channel]:
                self._channel_handlers[channel].remove(handler)
            
            # Unsubscribe from Redis if no more handlers
            if not self._channel_handlers[channel]:
                del self._channel_handlers[channel]
                
                if channel in self._subscribed_channels:
                    await self.subscriber.unsubscribe(channel)
                    self._subscribed_channels.remove(channel)
                    
                    self.logger.logger.info(
                        f"Unsubscribed from Redis channel",
                        extra={'channel': channel}
                    )
        
        # Also unregister from parent
        await super().unsubscribe(topic, handler)
    
    async def _redis_listener_loop(self) -> None:
        """Background task to listen for Redis messages."""
        self.logger.logger.info("Starting Redis listener loop")
        
        while self._running:
            try:
                # Get message from Redis pubsub
                message = await self.subscriber.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0
                )
                
                if message is None:
                    continue
                
                # Parse message
                channel = message['channel'].decode('utf-8')
                data = message['data']
                
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                
                # Deserialize message
                try:
                    message_data = json.loads(data)
                    
                    # Reconstruct Message object
                    msg = Message(
                        id=UUID(message_data['id']),
                        message_type=MessageType(message_data['message_type']),
                        priority=MessagePriority(message_data['priority']),
                        source=message_data['source'],
                        target=message_data['target'],
                        payload=message_data['payload'],
                        correlation_id=UUID(message_data['correlation_id']) if message_data.get('correlation_id') else None,
                        timestamp=datetime.fromisoformat(message_data['timestamp']),
                        retry_count=message_data.get('retry_count', 0),
                        metadata=message_data.get('metadata', {})
                    )
                    
                    # Process message
                    await self._process_redis_message(msg, channel)
                    
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    self.logger.logger.warning(
                        f"Failed to parse Redis message",
                        extra={'channel': channel, 'error': str(e)}
                    )
                    continue
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'redis_listener_loop'})
                await asyncio.sleep(1)  # Brief pause before retry
        
        self.logger.logger.info("Redis listener loop stopped")
    
    async def _process_redis_message(
        self,
        message: Message,
        channel: str
    ) -> None:
        """
        Process a message received from Redis.
        
        Args:
            message: Received message
            channel: Redis channel it was received on
        """
        # Check if we've already processed this message (deduplication)
        if message.id in self._message_history:
            return
        
        # Add to history
        self._message_history[message.id] = message
        
        # Get handlers for this channel
        handlers = self._channel_handlers.get(channel, [])
        
        # Also check for type-based handlers
        type_handlers = self._handlers.get(message.message_type, [])
        
        # Combine handlers (deduplicated)
        all_handlers = list(set(handlers + type_handlers))
        
        # Process with each handler
        for handler in all_handlers:
            try:
                await handler.handle_message(message)
                self._metrics['messages_processed'] += 1
                
            except Exception as e:
                self.logger.log_error(e, {
                    'operation': 'process_redis_message',
                    'message_id': str(message.id),
                    'handler': handler.__class__.__name__
                })
                self._metrics['messages_failed'] += 1
    
    async def _persist_message(self, message: Message) -> None:
        """
        Persist message to Redis for recovery.
        
        Args:
            message: Message to persist
        """
        try:
            key = f"{self.channel_prefix}:messages:{message.id}"
            
            # Serialize message
            message_data = {
                'id': str(message.id),
                'message_type': message.message_type.value,
                'priority': message.priority.value,
                'source': message.source,
                'target': message.target,
                'payload': message.payload,
                'correlation_id': str(message.correlation_id) if message.correlation_id else None,
                'timestamp': message.timestamp.isoformat(),
                'retry_count': message.retry_count,
                'metadata': message.metadata
            }
            
            # Store with TTL
            await self.redis_client.setex(
                key,
                self.message_ttl_seconds,
                json.dumps(message_data)
            )
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'persist_message',
                'message_id': str(message.id)
            })
    
    async def get_queue_sizes(self) -> Dict[str, int]:
        """
        Get queue sizes from Redis.
        
        Returns:
            Dictionary of queue sizes
        """
        sizes = await super().get_queue_sizes()
        
        # Add Redis-specific metrics
        if self.redis_client:
            try:
                # Get number of subscribed channels
                sizes['redis_channels'] = len(self._subscribed_channels)
                
                # Get number of persisted messages
                pattern = f"{self.channel_prefix}:messages:*"
                keys = await self.redis_client.keys(pattern)
                sizes['persisted_messages'] = len(keys)
                
            except Exception as e:
                self.logger.log_error(e, {'operation': 'get_queue_sizes'})
        
        return sizes
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get Redis message bus metrics.
        
        Returns:
            Dictionary of metrics
        """
        metrics = super().get_metrics()
        
        # Add Redis-specific metrics
        metrics.update({
            'redis_url': self.redis_url,
            'subscribed_channels': len(self._subscribed_channels),
            'channel_handlers': sum(len(handlers) for handlers in self._channel_handlers.values()),
            'persistence_enabled': self.enable_persistence
        })
        
        return metrics