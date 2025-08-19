"""Event subscription management."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
import uuid

from .core import Event, EventFilter

logger = logging.getLogger(__name__)


@dataclass
class EventSubscription:
    """Event subscription information."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subscriber_id: str = ""
    callback: Optional[Callable[[Event], Any]] = None
    event_filter: Optional[EventFilter] = None
    topics: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    delivery_count: int = 0
    last_delivery: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    
    async def deliver_event(self, event: Event) -> bool:
        """Deliver an event to this subscription."""
        try:
            if not self.is_active or not self.callback:
                return False
            
            # Check topic filter
            if self.topics and event.topic not in self.topics:
                return False
            
            # Check event filter
            if self.event_filter and not self.event_filter.matches(event):
                return False
            
            # Deliver the event
            result = self.callback(event)
            
            # Handle async callbacks
            if asyncio.iscoroutine(result):
                await result
            
            # Update delivery stats
            self.delivery_count += 1
            self.last_delivery = datetime.utcnow()
            
            logger.debug(f"Delivered event {event.id} to subscription {self.id}")
            return True
            
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            logger.error(f"Error delivering event {event.id} to subscription {self.id}: {e}")
            return False


class SubscriptionManager:
    """Manages event subscriptions and delivery."""
    
    def __init__(self, max_subscribers: int = 10000):
        self.max_subscribers = max_subscribers
        
        # Subscriptions storage
        self.subscriptions: Dict[str, EventSubscription] = {}
        self.topic_subscriptions: Dict[str, Set[str]] = {}  # topic -> subscription_ids
        self.subscriber_subscriptions: Dict[str, Set[str]] = {}  # subscriber_id -> subscription_ids
        
        # Delivery tracking
        self.delivery_queue = asyncio.Queue()
        self.delivery_workers: List[asyncio.Task] = []
        self.num_workers = 10
        
        # Metrics
        self.metrics = {
            "total_subscriptions": 0,
            "active_subscriptions": 0,
            "total_deliveries": 0,
            "failed_deliveries": 0,
            "delivery_queue_size": 0
        }
        
        # Status
        self.is_running = False
        
        logger.info("Subscription manager initialized")
    
    async def start(self):
        """Start the subscription manager."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start delivery workers
        self.delivery_workers = [
            asyncio.create_task(self._delivery_worker(i))
            for i in range(self.num_workers)
        ]
        
        logger.info(f"Subscription manager started with {self.num_workers} workers")
    
    async def stop(self):
        """Stop the subscription manager."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Stop delivery workers
        for worker in self.delivery_workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.delivery_workers, return_exceptions=True)
        self.delivery_workers.clear()
        
        logger.info("Subscription manager stopped")
    
    async def subscribe(
        self,
        subscriber_id: str,
        callback: Callable[[Event], Any],
        event_filter: Optional[EventFilter] = None,
        topics: Optional[List[str]] = None
    ) -> str:
        """Create a new event subscription."""
        try:
            # Check limits
            if len(self.subscriptions) >= self.max_subscribers:
                raise ValueError("Maximum number of subscribers reached")
            
            # Create subscription
            subscription = EventSubscription(
                subscriber_id=subscriber_id,
                callback=callback,
                event_filter=event_filter,
                topics=set(topics) if topics else set()
            )
            
            # Store subscription
            self.subscriptions[subscription.id] = subscription
            
            # Update topic index
            for topic in subscription.topics:
                if topic not in self.topic_subscriptions:
                    self.topic_subscriptions[topic] = set()
                self.topic_subscriptions[topic].add(subscription.id)
            
            # Update subscriber index
            if subscriber_id not in self.subscriber_subscriptions:
                self.subscriber_subscriptions[subscriber_id] = set()
            self.subscriber_subscriptions[subscriber_id].add(subscription.id)
            
            # Update metrics
            self.metrics["total_subscriptions"] += 1
            self.metrics["active_subscriptions"] += 1
            
            logger.info(f"Created subscription {subscription.id} for subscriber {subscriber_id}")
            return subscription.id
            
        except Exception as e:
            logger.error(f"Failed to create subscription for {subscriber_id}: {e}")
            raise
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Remove a subscription."""
        try:
            if subscription_id not in self.subscriptions:
                logger.warning(f"Subscription {subscription_id} not found")
                return False
            
            subscription = self.subscriptions[subscription_id]
            
            # Remove from topic index
            for topic in subscription.topics:
                if topic in self.topic_subscriptions:
                    self.topic_subscriptions[topic].discard(subscription_id)
                    if not self.topic_subscriptions[topic]:
                        del self.topic_subscriptions[topic]
            
            # Remove from subscriber index
            subscriber_id = subscription.subscriber_id
            if subscriber_id in self.subscriber_subscriptions:
                self.subscriber_subscriptions[subscriber_id].discard(subscription_id)
                if not self.subscriber_subscriptions[subscriber_id]:
                    del self.subscriber_subscriptions[subscriber_id]
            
            # Remove subscription
            del self.subscriptions[subscription_id]
            
            # Update metrics
            self.metrics["active_subscriptions"] -= 1
            
            logger.info(f"Removed subscription {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove subscription {subscription_id}: {e}")
            return False
    
    async def unsubscribe_all(self, subscriber_id: str) -> int:
        """Remove all subscriptions for a subscriber."""
        try:
            if subscriber_id not in self.subscriber_subscriptions:
                return 0
            
            subscription_ids = self.subscriber_subscriptions[subscriber_id].copy()
            count = 0
            
            for subscription_id in subscription_ids:
                if await self.unsubscribe(subscription_id):
                    count += 1
            
            logger.info(f"Removed {count} subscriptions for subscriber {subscriber_id}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to remove subscriptions for {subscriber_id}: {e}")
            return 0
    
    async def deliver_event(self, event: Event) -> int:
        """Deliver an event to matching subscriptions."""
        try:
            if not self.is_running:
                return 0
            
            # Find matching subscriptions
            matching_subscriptions = await self._find_matching_subscriptions(event)
            
            if not matching_subscriptions:
                return 0
            
            # Queue delivery tasks
            delivered_count = 0
            for subscription_id in matching_subscriptions:
                try:
                    await self.delivery_queue.put((event, subscription_id))
                    delivered_count += 1
                except Exception as e:
                    logger.error(f"Failed to queue delivery: {e}")
            
            self.metrics["delivery_queue_size"] = self.delivery_queue.qsize()
            return delivered_count
            
        except Exception as e:
            logger.error(f"Failed to deliver event {event.id}: {e}")
            return 0
    
    async def _find_matching_subscriptions(self, event: Event) -> List[str]:
        """Find subscriptions that match an event."""
        matching = set()
        
        try:
            # Check topic-specific subscriptions
            if event.topic in self.topic_subscriptions:
                matching.update(self.topic_subscriptions[event.topic])
            
            # Check subscriptions with no topic filter (listen to all)
            for subscription_id, subscription in self.subscriptions.items():
                if not subscription.topics and subscription.is_active:
                    # Apply event filter if present
                    if not subscription.event_filter or subscription.event_filter.matches(event):
                        matching.add(subscription_id)
            
            return list(matching)
            
        except Exception as e:
            logger.error(f"Error finding matching subscriptions: {e}")
            return []
    
    async def _delivery_worker(self, worker_id: int):
        """Worker task for delivering events."""
        logger.debug(f"Delivery worker {worker_id} started")
        
        try:
            while self.is_running:
                try:
                    # Get delivery task
                    event, subscription_id = await asyncio.wait_for(
                        self.delivery_queue.get(),
                        timeout=1.0
                    )
                    
                    # Get subscription
                    if subscription_id not in self.subscriptions:
                        logger.warning(f"Subscription {subscription_id} not found for delivery")
                        continue
                    
                    subscription = self.subscriptions[subscription_id]
                    
                    # Deliver event
                    success = await subscription.deliver_event(event)
                    
                    if success:
                        self.metrics["total_deliveries"] += 1
                    else:
                        self.metrics["failed_deliveries"] += 1
                    
                    # Mark task done
                    self.delivery_queue.task_done()
                    self.metrics["delivery_queue_size"] = self.delivery_queue.qsize()
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Delivery worker {worker_id} error: {e}")
                    await asyncio.sleep(0.1)  # Brief pause on error
                    
        except asyncio.CancelledError:
            logger.debug(f"Delivery worker {worker_id} cancelled")
            raise
        except Exception as e:
            logger.error(f"Delivery worker {worker_id} fatal error: {e}")
    
    async def get_subscription(self, subscription_id: str) -> Optional[EventSubscription]:
        """Get subscription by ID."""
        return self.subscriptions.get(subscription_id)
    
    async def get_subscriptions_for_subscriber(self, subscriber_id: str) -> List[EventSubscription]:
        """Get all subscriptions for a subscriber."""
        if subscriber_id not in self.subscriber_subscriptions:
            return []
        
        subscription_ids = self.subscriber_subscriptions[subscriber_id]
        return [
            self.subscriptions[sub_id]
            for sub_id in subscription_ids
            if sub_id in self.subscriptions
        ]
    
    async def get_subscriptions_for_topic(self, topic: str) -> List[EventSubscription]:
        """Get all subscriptions for a topic."""
        if topic not in self.topic_subscriptions:
            return []
        
        subscription_ids = self.topic_subscriptions[topic]
        return [
            self.subscriptions[sub_id]
            for sub_id in subscription_ids
            if sub_id in self.subscriptions
        ]
    
    async def update_subscription_filter(
        self,
        subscription_id: str,
        event_filter: Optional[EventFilter]
    ) -> bool:
        """Update the event filter for a subscription."""
        try:
            if subscription_id not in self.subscriptions:
                return False
            
            self.subscriptions[subscription_id].event_filter = event_filter
            logger.info(f"Updated filter for subscription {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update subscription filter: {e}")
            return False
    
    async def pause_subscription(self, subscription_id: str) -> bool:
        """Pause a subscription."""
        try:
            if subscription_id not in self.subscriptions:
                return False
            
            self.subscriptions[subscription_id].is_active = False
            self.metrics["active_subscriptions"] -= 1
            
            logger.info(f"Paused subscription {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause subscription: {e}")
            return False
    
    async def resume_subscription(self, subscription_id: str) -> bool:
        """Resume a paused subscription."""
        try:
            if subscription_id not in self.subscriptions:
                return False
            
            subscription = self.subscriptions[subscription_id]
            if not subscription.is_active:
                subscription.is_active = True
                self.metrics["active_subscriptions"] += 1
                
                logger.info(f"Resumed subscription {subscription_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume subscription: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get subscription manager metrics."""
        self.metrics["delivery_queue_size"] = self.delivery_queue.qsize()
        
        # Add subscription stats
        active_count = sum(1 for sub in self.subscriptions.values() if sub.is_active)
        self.metrics["active_subscriptions"] = active_count
        
        return {
            **self.metrics,
            "topic_count": len(self.topic_subscriptions),
            "subscriber_count": len(self.subscriber_subscriptions)
        }
    
    async def get_subscription_stats(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific subscription."""
        if subscription_id not in self.subscriptions:
            return None
        
        subscription = self.subscriptions[subscription_id]
        return {
            "id": subscription.id,
            "subscriber_id": subscription.subscriber_id,
            "is_active": subscription.is_active,
            "delivery_count": subscription.delivery_count,
            "error_count": subscription.error_count,
            "last_delivery": subscription.last_delivery.isoformat() if subscription.last_delivery else None,
            "last_error": subscription.last_error,
            "created_at": subscription.created_at.isoformat(),
            "topics": list(subscription.topics)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            queue_size = self.delivery_queue.qsize()
            active_workers = sum(1 for worker in self.delivery_workers if not worker.done())
            
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
                "total_workers": len(self.delivery_workers),
                "metrics": await self.get_metrics()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}