"""Real-time event streaming capabilities."""

import asyncio
import logging
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
import uuid

from .core import Event, EventFilter

logger = logging.getLogger(__name__)


@dataclass
class EventStream:
    """Real-time event stream."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    event_filter: Optional[EventFilter] = None
    buffer_size: int = 1000
    buffer: deque = field(default_factory=deque)
    subscribers: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    event_count: int = 0
    last_event_time: Optional[datetime] = None
    
    def add_event(self, event: Event) -> bool:
        """Add an event to the stream buffer."""
        try:
            # Check filter
            if self.event_filter and not self.event_filter.matches(event):
                return False
            
            # Add to buffer
            self.buffer.append(event)
            self.event_count += 1
            self.last_event_time = datetime.utcnow()
            
            # Maintain buffer size
            while len(self.buffer) > self.buffer_size:
                self.buffer.popleft()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding event to stream {self.id}: {e}")
            return False
    
    def get_events(self, limit: int = 100, offset: int = 0) -> List[Event]:
        """Get events from the stream buffer."""
        try:
            events = list(self.buffer)
            
            # Apply offset and limit
            start = min(offset, len(events))
            end = min(start + limit, len(events))
            
            return events[start:end]
            
        except Exception as e:
            logger.error(f"Error getting events from stream {self.id}: {e}")
            return []
    
    def get_latest_events(self, count: int = 10) -> List[Event]:
        """Get the most recent events."""
        try:
            events = list(self.buffer)
            return events[-count:] if events else []
            
        except Exception as e:
            logger.error(f"Error getting latest events from stream {self.id}: {e}")
            return []


@dataclass 
class StreamSubscription:
    """Subscription to an event stream."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subscriber_id: str = ""
    stream_id: str = ""
    callback: Optional[callable] = None
    last_event_index: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


class StreamManager:
    """Manages real-time event streams."""
    
    def __init__(self, max_streams: int = 1000):
        self.max_streams = max_streams
        
        # Stream storage
        self.streams: Dict[str, EventStream] = {}
        self.stream_subscriptions: Dict[str, StreamSubscription] = {}
        self.subscriber_streams: Dict[str, Set[str]] = {}  # subscriber_id -> stream_ids
        
        # Stream processing
        self.stream_queue = asyncio.Queue()
        self.stream_workers: List[asyncio.Task] = []
        self.num_workers = 5
        
        # Metrics
        self.metrics = {
            "total_streams": 0,
            "active_streams": 0,
            "total_events_streamed": 0,
            "stream_subscriptions": 0
        }
        
        # Status
        self.is_running = False
        
        logger.info("Stream manager initialized")
    
    async def start(self):
        """Start the stream manager."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start stream workers
        self.stream_workers = [
            asyncio.create_task(self._stream_worker(i))
            for i in range(self.num_workers)
        ]
        
        logger.info(f"Stream manager started with {self.num_workers} workers")
    
    async def stop(self):
        """Stop the stream manager."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Stop stream workers
        for worker in self.stream_workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.stream_workers, return_exceptions=True)
        self.stream_workers.clear()
        
        logger.info("Stream manager stopped")
    
    async def create_stream(
        self,
        stream_id: str,
        event_filter: Optional[EventFilter] = None,
        buffer_size: int = 1000,
        name: str = ""
    ) -> bool:
        """Create a new event stream."""
        try:
            if len(self.streams) >= self.max_streams:
                raise ValueError("Maximum number of streams reached")
            
            if stream_id in self.streams:
                logger.warning(f"Stream {stream_id} already exists")
                return False
            
            # Create stream
            stream = EventStream(
                id=stream_id,
                name=name or stream_id,
                event_filter=event_filter,
                buffer_size=buffer_size
            )
            
            # Store stream
            self.streams[stream_id] = stream
            
            # Update metrics
            self.metrics["total_streams"] += 1
            self.metrics["active_streams"] += 1
            
            logger.info(f"Created event stream {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create stream {stream_id}: {e}")
            return False
    
    async def delete_stream(self, stream_id: str) -> bool:
        """Delete an event stream."""
        try:
            if stream_id not in self.streams:
                logger.warning(f"Stream {stream_id} not found")
                return False
            
            # Remove all subscriptions to this stream
            subscription_ids = [
                sub_id for sub_id, sub in self.stream_subscriptions.items()
                if sub.stream_id == stream_id
            ]
            
            for sub_id in subscription_ids:
                await self.unsubscribe_from_stream(sub_id)
            
            # Remove stream
            del self.streams[stream_id]
            
            # Update metrics
            self.metrics["active_streams"] -= 1
            
            logger.info(f"Deleted event stream {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete stream {stream_id}: {e}")
            return False
    
    async def deliver_event(self, event: Event) -> int:
        """Deliver an event to matching streams."""
        try:
            if not self.is_running:
                return 0
            
            # Queue event for processing
            await self.stream_queue.put(event)
            return 1
            
        except Exception as e:
            logger.error(f"Failed to queue event for streaming: {e}")
            return 0
    
    async def _stream_worker(self, worker_id: int):
        """Worker task for processing stream events."""
        logger.debug(f"Stream worker {worker_id} started")
        
        try:
            while self.is_running:
                try:
                    # Get event
                    event = await asyncio.wait_for(
                        self.stream_queue.get(),
                        timeout=1.0
                    )
                    
                    # Deliver to matching streams
                    delivered_count = 0
                    
                    for stream in self.streams.values():
                        if stream.is_active and stream.add_event(event):
                            delivered_count += 1
                            
                            # Notify subscribers
                            await self._notify_stream_subscribers(stream.id, event)
                    
                    if delivered_count > 0:
                        self.metrics["total_events_streamed"] += delivered_count
                    
                    # Mark task done
                    self.stream_queue.task_done()
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Stream worker {worker_id} error: {e}")
                    await asyncio.sleep(0.1)  # Brief pause on error
                    
        except asyncio.CancelledError:
            logger.debug(f"Stream worker {worker_id} cancelled")
            raise
        except Exception as e:
            logger.error(f"Stream worker {worker_id} fatal error: {e}")
    
    async def _notify_stream_subscribers(self, stream_id: str, event: Event):
        """Notify subscribers of new events in a stream."""
        try:
            # Find subscriptions for this stream
            stream_subs = [
                sub for sub in self.stream_subscriptions.values()
                if sub.stream_id == stream_id and sub.is_active and sub.callback
            ]
            
            # Notify subscribers
            for subscription in stream_subs:
                try:
                    result = subscription.callback(event)
                    
                    # Handle async callbacks
                    if asyncio.iscoroutine(result):
                        await result
                        
                except Exception as e:
                    logger.error(f"Error notifying stream subscriber {subscription.id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error notifying stream subscribers: {e}")
    
    async def subscribe_to_stream(
        self,
        subscriber_id: str,
        stream_id: str,
        callback: Optional[callable] = None
    ) -> Optional[str]:
        """Subscribe to a stream for real-time notifications."""
        try:
            if stream_id not in self.streams:
                logger.error(f"Stream {stream_id} not found")
                return None
            
            # Create subscription
            subscription = StreamSubscription(
                subscriber_id=subscriber_id,
                stream_id=stream_id,
                callback=callback
            )
            
            # Store subscription
            self.stream_subscriptions[subscription.id] = subscription
            
            # Update subscriber index
            if subscriber_id not in self.subscriber_streams:
                self.subscriber_streams[subscriber_id] = set()
            self.subscriber_streams[subscriber_id].add(stream_id)
            
            # Add to stream subscribers
            self.streams[stream_id].subscribers.add(subscription.id)
            
            # Update metrics
            self.metrics["stream_subscriptions"] += 1
            
            logger.info(f"Subscribed {subscriber_id} to stream {stream_id}")
            return subscription.id
            
        except Exception as e:
            logger.error(f"Failed to subscribe to stream: {e}")
            return None
    
    async def unsubscribe_from_stream(self, subscription_id: str) -> bool:
        """Unsubscribe from a stream."""
        try:
            if subscription_id not in self.stream_subscriptions:
                return False
            
            subscription = self.stream_subscriptions[subscription_id]
            stream_id = subscription.stream_id
            subscriber_id = subscription.subscriber_id
            
            # Remove from stream
            if stream_id in self.streams:
                self.streams[stream_id].subscribers.discard(subscription_id)
            
            # Remove from subscriber index
            if subscriber_id in self.subscriber_streams:
                self.subscriber_streams[subscriber_id].discard(stream_id)
                if not self.subscriber_streams[subscriber_id]:
                    del self.subscriber_streams[subscriber_id]
            
            # Remove subscription
            del self.stream_subscriptions[subscription_id]
            
            # Update metrics
            self.metrics["stream_subscriptions"] -= 1
            
            logger.info(f"Unsubscribed {subscription_id} from stream {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from stream: {e}")
            return False
    
    async def get_stream(self, stream_id: str) -> Optional[EventStream]:
        """Get a stream by ID."""
        return self.streams.get(stream_id)
    
    async def get_stream_events(
        self,
        stream_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Event]:
        """Get events from a stream."""
        if stream_id not in self.streams:
            return []
        
        return self.streams[stream_id].get_events(limit, offset)
    
    async def get_stream_latest_events(
        self,
        stream_id: str,
        count: int = 10
    ) -> List[Event]:
        """Get the latest events from a stream."""
        if stream_id not in self.streams:
            return []
        
        return self.streams[stream_id].get_latest_events(count)
    
    async def pause_stream(self, stream_id: str) -> bool:
        """Pause a stream."""
        try:
            if stream_id not in self.streams:
                return False
            
            self.streams[stream_id].is_active = False
            self.metrics["active_streams"] -= 1
            
            logger.info(f"Paused stream {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause stream: {e}")
            return False
    
    async def resume_stream(self, stream_id: str) -> bool:
        """Resume a paused stream."""
        try:
            if stream_id not in self.streams:
                return False
            
            stream = self.streams[stream_id]
            if not stream.is_active:
                stream.is_active = True
                self.metrics["active_streams"] += 1
                
                logger.info(f"Resumed stream {stream_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume stream: {e}")
            return False
    
    async def clear_stream_buffer(self, stream_id: str) -> bool:
        """Clear the buffer of a stream."""
        try:
            if stream_id not in self.streams:
                return False
            
            stream = self.streams[stream_id]
            cleared_count = len(stream.buffer)
            stream.buffer.clear()
            
            logger.info(f"Cleared {cleared_count} events from stream {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear stream buffer: {e}")
            return False
    
    async def update_stream_filter(
        self,
        stream_id: str,
        event_filter: Optional[EventFilter]
    ) -> bool:
        """Update the event filter for a stream."""
        try:
            if stream_id not in self.streams:
                return False
            
            self.streams[stream_id].event_filter = event_filter
            logger.info(f"Updated filter for stream {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update stream filter: {e}")
            return False
    
    async def get_stream_stats(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific stream."""
        if stream_id not in self.streams:
            return None
        
        stream = self.streams[stream_id]
        return {
            "id": stream.id,
            "name": stream.name,
            "is_active": stream.is_active,
            "buffer_size": stream.buffer_size,
            "current_buffer_count": len(stream.buffer),
            "total_events": stream.event_count,
            "subscriber_count": len(stream.subscribers),
            "last_event_time": stream.last_event_time.isoformat() if stream.last_event_time else None,
            "created_at": stream.created_at.isoformat()
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get stream manager metrics."""
        # Update active streams count
        active_count = sum(1 for stream in self.streams.values() if stream.is_active)
        self.metrics["active_streams"] = active_count
        
        return {
            **self.metrics,
            "queue_size": self.stream_queue.qsize(),
            "total_buffer_events": sum(len(stream.buffer) for stream in self.streams.values())
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            queue_size = self.stream_queue.qsize()
            active_workers = sum(1 for worker in self.stream_workers if not worker.done())
            
            status = "healthy"
            if queue_size > 1000:  # High queue size
                status = "degraded"
            if active_workers < self.num_workers // 2:  # Many workers failed
                status = "unhealthy"
            
            return {
                "status": status,
                "is_running": self.is_running,
                "queue_size": queue_size,
                "active_workers": active_workers,
                "total_workers": len(self.stream_workers),
                "metrics": await self.get_metrics()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}