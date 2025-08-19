"""Core event dispatcher implementation."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ..message_bus.types import Message, MessageType
from .subscription import SubscriptionManager, EventSubscription
from .streaming import StreamManager
from .persistence import EventStore

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events in the system."""
    AGENT_CREATED = "agent_created"
    AGENT_DESTROYED = "agent_destroyed"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    RESOURCE_ALLOCATED = "resource_allocated"
    RESOURCE_RELEASED = "resource_released"
    CONSENSUS_INITIATED = "consensus_initiated"
    CONSENSUS_REACHED = "consensus_reached"
    ERROR_OCCURRED = "error_occurred"
    PERFORMANCE_ALERT = "performance_alert"
    CUSTOM = "custom"


@dataclass
class Event:
    """Core event structure."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType = EventType.CUSTOM
    source: str = ""  # Source agent/component
    topic: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None  # ID of event that caused this one
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    severity: str = "info"  # debug, info, warning, error, critical
    ttl: Optional[timedelta] = None
    
    def is_expired(self) -> bool:
        """Check if event has expired."""
        if self.ttl is None:
            return False
        return datetime.utcnow() > (self.timestamp + self.ttl)
    
    def to_message(self) -> Message:
        """Convert event to message for transport."""
        return Message(
            id=self.id,
            type=MessageType.EVENT,
            sender=self.source,
            topic=self.topic,
            payload={
                "event_type": self.type.value,
                "data": self.data,
                "correlation_id": self.correlation_id,
                "causation_id": self.causation_id,
                "metadata": self.metadata,
                "tags": list(self.tags),
                "severity": self.severity
            },
            timestamp=self.timestamp
        )
    
    @classmethod
    def from_message(cls, message: Message) -> "Event":
        """Create event from message."""
        payload = message.payload
        return cls(
            id=message.id,
            type=EventType(payload.get("event_type", EventType.CUSTOM.value)),
            source=message.sender,
            topic=message.topic,
            data=payload.get("data", {}),
            timestamp=message.timestamp,
            correlation_id=payload.get("correlation_id"),
            causation_id=payload.get("causation_id"),
            metadata=payload.get("metadata", {}),
            tags=set(payload.get("tags", [])),
            severity=payload.get("severity", "info")
        )


class EventFilter:
    """Event filtering utility."""
    
    def __init__(
        self,
        event_types: Optional[List[EventType]] = None,
        sources: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        tags: Optional[Set[str]] = None,
        severity_min: Optional[str] = None,
        custom_filter: Optional[Callable[[Event], bool]] = None
    ):
        self.event_types = event_types
        self.sources = sources
        self.topics = topics
        self.tags = tags
        self.severity_min = severity_min
        self.custom_filter = custom_filter
        
        # Severity levels for comparison
        self.severity_levels = {
            "debug": 0,
            "info": 1,
            "warning": 2,
            "error": 3,
            "critical": 4
        }
    
    def matches(self, event: Event) -> bool:
        """Check if event matches filter criteria."""
        try:
            # Check event type
            if self.event_types and event.type not in self.event_types:
                return False
            
            # Check source
            if self.sources and event.source not in self.sources:
                return False
            
            # Check topic
            if self.topics and event.topic not in self.topics:
                return False
            
            # Check tags (any tag match)
            if self.tags and not (self.tags & event.tags):
                return False
            
            # Check severity level
            if self.severity_min:
                event_level = self.severity_levels.get(event.severity, 0)
                min_level = self.severity_levels.get(self.severity_min, 0)
                if event_level < min_level:
                    return False
            
            # Custom filter
            if self.custom_filter and not self.custom_filter(event):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error in event filter: {e}")
            return False


class EventDispatcher:
    """High-performance event dispatcher with routing, streaming, and persistence."""
    
    def __init__(
        self,
        enable_persistence: bool = True,
        enable_streaming: bool = True,
        max_subscribers: int = 10000,
        batch_size: int = 100,
        flush_interval: float = 1.0
    ):
        self.enable_persistence = enable_persistence
        self.enable_streaming = enable_streaming
        self.max_subscribers = max_subscribers
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        # Core components
        self.subscription_manager = SubscriptionManager(max_subscribers)
        self.stream_manager = StreamManager() if enable_streaming else None
        self.event_store = EventStore() if enable_persistence else None
        
        # Event batching
        self.event_batch: List[Event] = []
        self.batch_lock = asyncio.Lock()
        self.flush_task: Optional[asyncio.Task] = None
        
        # Metrics
        self.metrics = {
            "events_dispatched": 0,
            "events_persisted": 0,
            "subscription_deliveries": 0,
            "stream_deliveries": 0,
            "errors": 0
        }
        
        # Status
        self.is_running = False
        
        logger.info("Event dispatcher initialized")
    
    async def start(self):
        """Start the event dispatcher."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start components
        await self.subscription_manager.start()
        if self.stream_manager:
            await self.stream_manager.start()
        if self.event_store:
            await self.event_store.start()
        
        # Start batch flushing
        self.flush_task = asyncio.create_task(self._batch_flush_loop())
        
        logger.info("Event dispatcher started")
    
    async def stop(self):
        """Stop the event dispatcher."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Stop batch flushing
        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass
        
        # Flush remaining events
        await self._flush_batch()
        
        # Stop components
        await self.subscription_manager.stop()
        if self.stream_manager:
            await self.stream_manager.stop()
        if self.event_store:
            await self.event_store.stop()
        
        logger.info("Event dispatcher stopped")
    
    async def dispatch(self, event: Event):
        """Dispatch an event to all interested parties."""
        try:
            if not self.is_running:
                logger.warning("Event dispatcher not running, dropping event")
                return
            
            # Set timestamp if not set
            if not event.timestamp:
                event.timestamp = datetime.utcnow()
            
            # Add to batch for processing
            async with self.batch_lock:
                self.event_batch.append(event)
                
                # Flush immediately if batch is full
                if len(self.event_batch) >= self.batch_size:
                    await self._flush_batch()
            
            self.metrics["events_dispatched"] += 1
            logger.debug(f"Event {event.id} queued for dispatch")
            
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Failed to dispatch event {event.id}: {e}")
            raise
    
    async def _flush_batch(self):
        """Flush batched events."""
        if not self.event_batch:
            return
        
        try:
            # Get current batch
            current_batch = self.event_batch.copy()
            self.event_batch.clear()
            
            # Process events in parallel
            tasks = []
            
            for event in current_batch:
                # Skip expired events
                if event.is_expired():
                    logger.debug(f"Skipping expired event {event.id}")
                    continue
                
                # Create processing tasks
                tasks.extend([
                    self._deliver_to_subscribers(event),
                    self._deliver_to_streams(event),
                    self._persist_event(event)
                ])
            
            # Execute all tasks
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.debug(f"Flushed batch of {len(current_batch)} events")
            
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Error flushing event batch: {e}")
    
    async def _deliver_to_subscribers(self, event: Event):
        """Deliver event to matching subscribers."""
        try:
            delivered = await self.subscription_manager.deliver_event(event)
            self.metrics["subscription_deliveries"] += delivered
            
        except Exception as e:
            logger.error(f"Error delivering to subscribers: {e}")
    
    async def _deliver_to_streams(self, event: Event):
        """Deliver event to active streams."""
        try:
            if self.stream_manager:
                delivered = await self.stream_manager.deliver_event(event)
                self.metrics["stream_deliveries"] += delivered
                
        except Exception as e:
            logger.error(f"Error delivering to streams: {e}")
    
    async def _persist_event(self, event: Event):
        """Persist event to storage."""
        try:
            if self.event_store:
                await self.event_store.store_event(event)
                self.metrics["events_persisted"] += 1
                
        except Exception as e:
            logger.error(f"Error persisting event: {e}")
    
    async def _batch_flush_loop(self):
        """Periodic batch flushing loop."""
        try:
            while self.is_running:
                await asyncio.sleep(self.flush_interval)
                
                async with self.batch_lock:
                    if self.event_batch:
                        await self._flush_batch()
                        
        except asyncio.CancelledError:
            logger.info("Batch flush loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Batch flush loop error: {e}")
    
    async def subscribe(
        self,
        subscriber_id: str,
        callback: Callable[[Event], Any],
        event_filter: Optional[EventFilter] = None,
        topics: Optional[List[str]] = None
    ) -> str:
        """Subscribe to events with optional filtering."""
        return await self.subscription_manager.subscribe(
            subscriber_id, callback, event_filter, topics
        )
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events."""
        return await self.subscription_manager.unsubscribe(subscription_id)
    
    async def create_stream(
        self,
        stream_id: str,
        event_filter: Optional[EventFilter] = None,
        buffer_size: int = 1000
    ) -> bool:
        """Create a new event stream."""
        if not self.stream_manager:
            return False
        
        return await self.stream_manager.create_stream(stream_id, event_filter, buffer_size)
    
    async def get_stream_events(
        self,
        stream_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Event]:
        """Get events from a stream."""
        if not self.stream_manager:
            return []
        
        return await self.stream_manager.get_stream_events(stream_id, limit, offset)
    
    async def replay_events(
        self,
        from_timestamp: datetime,
        to_timestamp: Optional[datetime] = None,
        event_filter: Optional[EventFilter] = None,
        callback: Optional[Callable[[Event], Any]] = None
    ) -> List[Event]:
        """Replay historical events."""
        if not self.event_store:
            return []
        
        events = await self.event_store.get_events(
            from_timestamp, to_timestamp, event_filter
        )
        
        # If callback provided, dispatch replayed events
        if callback:
            for event in events:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Error in replay callback: {e}")
        
        return events
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get dispatcher metrics."""
        base_metrics = self.metrics.copy()
        
        # Add component metrics
        base_metrics.update({
            "subscription_manager": await self.subscription_manager.get_metrics(),
            "stream_manager": await self.stream_manager.get_metrics() if self.stream_manager else {},
            "event_store": await self.event_store.get_metrics() if self.event_store else {}
        })
        
        return base_metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            health = {
                "status": "healthy" if self.is_running else "stopped",
                "components": {}
            }
            
            # Check components
            health["components"]["subscription_manager"] = await self.subscription_manager.health_check()
            
            if self.stream_manager:
                health["components"]["stream_manager"] = await self.stream_manager.health_check()
            
            if self.event_store:
                health["components"]["event_store"] = await self.event_store.health_check()
            
            # Overall health
            component_healths = [comp["status"] for comp in health["components"].values()]
            if any(status != "healthy" for status in component_healths):
                health["status"] = "degraded"
            
            return health
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    # Context manager support
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


# Helper functions for common event creation
def create_agent_event(event_type: EventType, agent_id: str, data: Dict[str, Any]) -> Event:
    """Create an agent-related event."""
    return Event(
        type=event_type,
        source=agent_id,
        topic="agents",
        data=data,
        tags={"agent", "lifecycle"}
    )


def create_task_event(event_type: EventType, task_id: str, agent_id: str, data: Dict[str, Any]) -> Event:
    """Create a task-related event."""
    return Event(
        type=event_type,
        source=agent_id,
        topic="tasks",
        data={**data, "task_id": task_id},
        tags={"task", "execution"}
    )


def create_resource_event(event_type: EventType, resource_id: str, agent_id: str, data: Dict[str, Any]) -> Event:
    """Create a resource-related event."""
    return Event(
        type=event_type,
        source=agent_id,
        topic="resources",
        data={**data, "resource_id": resource_id},
        tags={"resource", "allocation"}
    )