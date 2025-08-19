"""
Message bus interface for MAOS orchestration system.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any, Set
from uuid import UUID, uuid4
from datetime import datetime
from collections import defaultdict, deque

from ..models.message import Message, MessageType, MessagePriority
from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError


class EventHandler(ABC):
    """Abstract base class for event handlers."""
    
    @abstractmethod
    async def handle_message(self, message: Message) -> None:
        """Handle a received message."""
        pass
    
    def get_supported_message_types(self) -> Set[MessageType]:
        """Get set of message types this handler supports."""
        return set()


class MessageBus:
    """
    Message bus for inter-component communication in MAOS.
    
    Provides:
    - Publish/subscribe messaging
    - Message routing and filtering
    - Priority-based message handling
    - Message persistence and reliability
    - Dead letter handling
    """
    
    def __init__(
        self,
        max_queue_size: int = 10000,
        dead_letter_enabled: bool = True,
        message_ttl_seconds: int = 300,
        delivery_retry_attempts: int = 3
    ):
        """Initialize the message bus."""
        self.max_queue_size = max_queue_size
        self.dead_letter_enabled = dead_letter_enabled
        self.message_ttl_seconds = message_ttl_seconds
        self.delivery_retry_attempts = delivery_retry_attempts
        
        self.logger = MAOSLogger("message_bus", str(uuid4()))
        
        # Message routing
        self._handlers: Dict[MessageType, List[EventHandler]] = defaultdict(list)
        self._subscribers: Dict[str, List[EventHandler]] = defaultdict(list)  # topic -> handlers
        
        # Message queues (priority-based)
        self._message_queues: Dict[MessagePriority, deque] = {
            priority: deque() for priority in MessagePriority
        }
        
        # Message tracking
        self._pending_messages: Dict[UUID, Message] = {}
        self._message_history: Dict[UUID, Message] = {}
        self._dead_letter_queue: deque = deque()
        
        # Background tasks
        self._message_processor_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Metrics
        self._metrics = {
            'messages_published': 0,
            'messages_processed': 0,
            'messages_failed': 0,
            'messages_retried': 0,
            'dead_letter_messages': 0,
            'active_handlers': 0,
            'queue_size': 0
        }
        
        self._running = False
    
    async def start(self) -> None:
        """Start the message bus and background processing."""
        if self._running:
            return
        
        self.logger.logger.info("Starting Message Bus")
        
        self._running = True
        
        # Start message processing
        self._message_processor_task = asyncio.create_task(self._message_processor_loop())
        
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop(self) -> None:
        """Stop the message bus and cleanup."""
        if not self._running:
            return
        
        self.logger.logger.info("Stopping Message Bus")
        
        self._running = False
        
        # Cancel background tasks
        if self._message_processor_task:
            self._message_processor_task.cancel()
            try:
                await self._message_processor_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Clear state
        for queue in self._message_queues.values():
            queue.clear()
        
        self._handlers.clear()
        self._subscribers.clear()
        self._pending_messages.clear()
    
    def register_handler(
        self,
        handler: EventHandler,
        message_types: Optional[Set[MessageType]] = None,
        topics: Optional[Set[str]] = None
    ) -> None:
        """
        Register an event handler.
        
        Args:
            handler: The event handler instance
            message_types: Set of message types to handle (optional)
            topics: Set of topics to subscribe to (optional)
        """
        
        # Register for specific message types
        if message_types:
            for message_type in message_types:
                if handler not in self._handlers[message_type]:
                    self._handlers[message_type].append(handler)
        else:
            # Register for handler's supported types
            supported_types = handler.get_supported_message_types()
            for message_type in supported_types:
                if handler not in self._handlers[message_type]:
                    self._handlers[message_type].append(handler)
        
        # Register for topics
        if topics:
            for topic in topics:
                if handler not in self._subscribers[topic]:
                    self._subscribers[topic].append(handler)
        
        self._metrics['active_handlers'] = sum(
            len(handlers) for handlers in self._handlers.values()
        )
        
        self.logger.logger.debug(
            f"Handler registered: {type(handler).__name__}",
            extra={
                'message_types': [mt.value for mt in (message_types or set())],
                'topics': list(topics or [])
            }
        )
    
    def unregister_handler(self, handler: EventHandler) -> None:
        """Unregister an event handler."""
        
        # Remove from message type handlers
        for handlers in self._handlers.values():
            if handler in handlers:
                handlers.remove(handler)
        
        # Remove from topic subscribers
        for subscribers in self._subscribers.values():
            if handler in subscribers:
                subscribers.remove(handler)
        
        self._metrics['active_handlers'] = sum(
            len(handlers) for handlers in self._handlers.values()
        )
        
        self.logger.logger.debug(f"Handler unregistered: {type(handler).__name__}")
    
    async def publish(
        self,
        message_type: MessageType,
        payload: Dict[str, Any],
        sender_id: Optional[UUID] = None,
        recipient_id: Optional[UUID] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        topic: Optional[str] = None,
        correlation_id: Optional[UUID] = None,
        requires_acknowledgment: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """
        Publish a message to the bus.
        
        Args:
            message_type: Type of message
            payload: Message payload
            sender_id: ID of sender (optional)
            recipient_id: ID of specific recipient (optional)
            priority: Message priority
            topic: Topic for pub/sub routing (optional)
            correlation_id: Correlation ID for request/response (optional)
            requires_acknowledgment: Whether message requires ACK
            metadata: Additional message metadata
            
        Returns:
            UUID: Message ID
        """
        
        if not self._running:
            raise MAOSError("Message bus is not running")
        
        # Check queue capacity
        current_queue_size = sum(len(queue) for queue in self._message_queues.values())
        if current_queue_size >= self.max_queue_size:
            raise MAOSError("Message queue is full")
        
        try:
            # Create message
            message = Message(
                type=message_type,
                priority=priority,
                sender_id=sender_id,
                recipient_id=recipient_id,
                payload=payload,
                correlation_id=correlation_id,
                requires_acknowledgment=requires_acknowledgment,
                metadata=metadata or {}
            )
            
            # Add topic to metadata if specified
            if topic:
                message.metadata['topic'] = topic
            
            # Add to appropriate priority queue
            self._message_queues[priority].append(message)
            self._pending_messages[message.id] = message
            
            # Mark as sent
            message.mark_sent()
            
            self._metrics['messages_published'] += 1
            self._metrics['queue_size'] = current_queue_size + 1
            
            self.logger.logger.debug(
                f"Message published: {message_type.value}",
                extra={
                    'message_id': str(message.id),
                    'priority': priority.value,
                    'topic': topic,
                    'queue_size': self._metrics['queue_size']
                }
            )
            
            return message.id
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'publish',
                'message_type': message_type.value
            })
            raise MAOSError(f"Failed to publish message: {str(e)}")
    
    async def send_direct(
        self,
        recipient_id: UUID,
        message_type: MessageType,
        payload: Dict[str, Any],
        sender_id: Optional[UUID] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        correlation_id: Optional[UUID] = None,
        requires_acknowledgment: bool = False
    ) -> UUID:
        """
        Send a direct message to a specific recipient.
        
        Args:
            recipient_id: ID of message recipient
            message_type: Type of message
            payload: Message payload
            sender_id: ID of sender (optional)
            priority: Message priority
            correlation_id: Correlation ID for request/response (optional)
            requires_acknowledgment: Whether message requires ACK
            
        Returns:
            UUID: Message ID
        """
        
        return await self.publish(
            message_type=message_type,
            payload=payload,
            sender_id=sender_id,
            recipient_id=recipient_id,
            priority=priority,
            correlation_id=correlation_id,
            requires_acknowledgment=requires_acknowledgment
        )
    
    async def publish_to_topic(
        self,
        topic: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        sender_id: Optional[UUID] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        correlation_id: Optional[UUID] = None
    ) -> UUID:
        """
        Publish a message to a specific topic.
        
        Args:
            topic: Topic to publish to
            message_type: Type of message
            payload: Message payload
            sender_id: ID of sender (optional)
            priority: Message priority
            correlation_id: Correlation ID for request/response (optional)
            
        Returns:
            UUID: Message ID
        """
        
        return await self.publish(
            message_type=message_type,
            payload=payload,
            sender_id=sender_id,
            priority=priority,
            topic=topic,
            correlation_id=correlation_id
        )
    
    async def acknowledge(self, message_id: UUID) -> bool:
        """
        Acknowledge receipt of a message.
        
        Args:
            message_id: ID of message to acknowledge
            
        Returns:
            bool: True if message was found and acknowledged
        """
        
        if message_id in self._pending_messages:
            message = self._pending_messages[message_id]
            message.acknowledge()
            
            # Move to history
            self._message_history[message_id] = message
            del self._pending_messages[message_id]
            
            self.logger.logger.debug(
                f"Message acknowledged",
                extra={'message_id': str(message_id)}
            )
            
            return True
        
        return False
    
    async def _message_processor_loop(self) -> None:
        """Background task for processing messages."""
        
        while self._running:
            try:
                # Process messages by priority (highest first)
                message_processed = False
                
                for priority in sorted(MessagePriority, key=lambda p: p.value, reverse=True):
                    queue = self._message_queues[priority]
                    
                    if queue:
                        message = queue.popleft()
                        await self._process_message(message)
                        message_processed = True
                        break
                
                if not message_processed:
                    # No messages to process, wait a bit
                    await asyncio.sleep(0.1)
                
                # Update queue size metric
                self._metrics['queue_size'] = sum(
                    len(queue) for queue in self._message_queues.values()
                )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'message_processor_loop'})
                await asyncio.sleep(1)  # Prevent tight loop on errors
    
    async def _process_message(self, message: Message) -> None:
        """Process a single message."""
        
        try:
            # Check if message has expired
            if message.is_expired():
                await self._handle_expired_message(message)
                return
            
            # Mark as received
            message.mark_received()
            
            # Find handlers for this message
            handlers = []
            
            # Handlers by message type
            if message.type in self._handlers:
                handlers.extend(self._handlers[message.type])
            
            # Handlers by topic
            topic = message.metadata.get('topic')
            if topic and topic in self._subscribers:
                handlers.extend(self._subscribers[topic])
            
            # Direct message handling
            if message.recipient_id and not handlers:
                # No specific handlers, but this might be handled by the recipient directly
                # In a real implementation, you might have a registry of component handlers
                pass
            
            if not handlers:
                self.logger.logger.warning(
                    f"No handlers found for message",
                    extra={
                        'message_id': str(message.id),
                        'message_type': message.type.value,
                        'topic': topic
                    }
                )
                await self._handle_undeliverable_message(message, "No handlers found")
                return
            
            # Deliver to all handlers
            delivery_errors = []
            successful_deliveries = 0
            
            for handler in handlers:
                try:
                    await handler.handle_message(message)
                    successful_deliveries += 1
                    
                except Exception as e:
                    delivery_errors.append(f"{type(handler).__name__}: {str(e)}")
                    self.logger.log_error(e, {
                        'operation': 'deliver_message',
                        'message_id': str(message.id),
                        'handler': type(handler).__name__
                    })
            
            # Mark as processed
            message.mark_processed()
            
            # Handle delivery results
            if successful_deliveries == 0:
                # All deliveries failed
                await self._handle_failed_message(message, delivery_errors)
            elif delivery_errors:
                # Partial failure
                self.logger.logger.warning(
                    f"Partial message delivery failure",
                    extra={
                        'message_id': str(message.id),
                        'successful_deliveries': successful_deliveries,
                        'failed_deliveries': len(delivery_errors),
                        'errors': delivery_errors
                    }
                )
                # Still count as processed since some handlers succeeded
                self._metrics['messages_processed'] += 1
            else:
                # All deliveries successful
                self._metrics['messages_processed'] += 1
            
            # Handle acknowledgment requirement
            if message.requires_acknowledgment and not message.is_acknowledged():
                # Set up timeout for acknowledgment
                asyncio.create_task(self._wait_for_acknowledgment(message))
            else:
                # Move to history immediately
                self._message_history[message.id] = message
                if message.id in self._pending_messages:
                    del self._pending_messages[message.id]
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'process_message',
                'message_id': str(message.id)
            })
            await self._handle_failed_message(message, [str(e)])
    
    async def _handle_expired_message(self, message: Message) -> None:
        """Handle an expired message."""
        
        self.logger.logger.warning(
            f"Message expired",
            extra={
                'message_id': str(message.id),
                'message_type': message.type.value,
                'age_seconds': message.get_age_seconds()
            }
        )
        
        if self.dead_letter_enabled:
            self._dead_letter_queue.append(message)
            self._metrics['dead_letter_messages'] += 1
        
        # Remove from pending
        if message.id in self._pending_messages:
            del self._pending_messages[message.id]
        
        self._metrics['messages_failed'] += 1
    
    async def _handle_failed_message(self, message: Message, errors: List[str]) -> None:
        """Handle a message that failed to be delivered."""
        
        if message.can_retry():
            # Retry the message
            message.increment_retry()
            
            # Re-queue with slight delay (exponential backoff)
            delay = min(2 ** message.retry_count, 60)  # Max 60 second delay
            await asyncio.sleep(delay)
            
            self._message_queues[message.priority].append(message)
            self._metrics['messages_retried'] += 1
            
            self.logger.logger.info(
                f"Message requeued for retry",
                extra={
                    'message_id': str(message.id),
                    'retry_count': message.retry_count,
                    'delay_seconds': delay
                }
            )
        else:
            # Move to dead letter queue
            await self._handle_undeliverable_message(message, f"Max retries exceeded: {errors}")
    
    async def _handle_undeliverable_message(self, message: Message, reason: str) -> None:
        """Handle a message that cannot be delivered."""
        
        self.logger.logger.error(
            f"Message undeliverable: {reason}",
            extra={
                'message_id': str(message.id),
                'message_type': message.type.value,
                'reason': reason
            }
        )
        
        if self.dead_letter_enabled:
            message.metadata['dead_letter_reason'] = reason
            message.metadata['dead_letter_time'] = datetime.utcnow().isoformat()
            self._dead_letter_queue.append(message)
            self._metrics['dead_letter_messages'] += 1
        
        # Remove from pending
        if message.id in self._pending_messages:
            del self._pending_messages[message.id]
        
        self._metrics['messages_failed'] += 1
    
    async def _wait_for_acknowledgment(self, message: Message) -> None:
        """Wait for message acknowledgment with timeout."""
        
        timeout = 30  # 30 seconds timeout for acknowledgment
        
        try:
            # Wait for acknowledgment
            start_time = asyncio.get_event_loop().time()
            
            while not message.is_acknowledged():
                if asyncio.get_event_loop().time() - start_time > timeout:
                    # Acknowledgment timeout
                    self.logger.logger.warning(
                        f"Message acknowledgment timeout",
                        extra={'message_id': str(message.id)}
                    )
                    break
                
                await asyncio.sleep(0.5)
            
            # Move to history
            self._message_history[message.id] = message
            if message.id in self._pending_messages:
                del self._pending_messages[message.id]
                
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'wait_for_acknowledgment',
                'message_id': str(message.id)
            })
    
    async def _cleanup_loop(self) -> None:
        """Background task for cleanup operations."""
        
        while self._running:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                # Cleanup old messages from history
                current_time = datetime.utcnow()
                max_history_age = 3600  # 1 hour
                
                expired_message_ids = []
                for message_id, message in self._message_history.items():
                    age = (current_time - message.created_at).total_seconds()
                    if age > max_history_age:
                        expired_message_ids.append(message_id)
                
                for message_id in expired_message_ids:
                    del self._message_history[message_id]
                
                if expired_message_ids:
                    self.logger.logger.debug(
                        f"Cleaned up {len(expired_message_ids)} old messages from history"
                    )
                
                # Cleanup old dead letter messages
                max_dead_letter_age = 86400  # 24 hours
                while (self._dead_letter_queue and 
                       (current_time - self._dead_letter_queue[0].created_at).total_seconds() > max_dead_letter_age):
                    expired_message = self._dead_letter_queue.popleft()
                    self.logger.logger.debug(
                        f"Removed expired dead letter message",
                        extra={'message_id': str(expired_message.id)}
                    )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'cleanup_loop'})
    
    def get_pending_messages(self) -> List[Message]:
        """Get all pending messages."""
        return list(self._pending_messages.values())
    
    def get_dead_letter_messages(self) -> List[Message]:
        """Get all dead letter messages."""
        return list(self._dead_letter_queue)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get message queue statistics."""
        return {
            'queue_sizes': {
                priority.name: len(queue) 
                for priority, queue in self._message_queues.items()
            },
            'total_queued': sum(len(queue) for queue in self._message_queues.values()),
            'pending_messages': len(self._pending_messages),
            'message_history': len(self._message_history),
            'dead_letter_messages': len(self._dead_letter_queue),
            'active_handlers': sum(len(handlers) for handlers in self._handlers.values())
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get message bus metrics."""
        metrics = self._metrics.copy()
        metrics.update(self.get_queue_stats())
        return metrics