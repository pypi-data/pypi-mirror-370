"""
State Change Notification System for Redis-based state management.

Provides event-driven notifications for state changes.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any, Set
from uuid import UUID, uuid4
from collections import deque
import aioredis
from aioredis import Redis

from .types import StateKey, StateValue, StateChange, StateChangeType, StateWatcher
from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError


class StateNotificationSystem:
    """
    Event-driven notification system for state changes.
    
    Features:
    - Real-time state change notifications
    - Pattern-based subscriptions
    - Buffered delivery
    - Delivery guarantees
    - Performance optimization
    """
    
    def __init__(
        self,
        redis: Redis,
        buffer_size: int = 10000,
        max_delivery_attempts: int = 3,
        delivery_timeout: float = 5.0,
        batch_size: int = 100
    ):
        """Initialize notification system."""
        self.redis = redis
        self.buffer_size = buffer_size
        self.max_delivery_attempts = max_delivery_attempts
        self.delivery_timeout = delivery_timeout
        self.batch_size = batch_size
        
        self.logger = MAOSLogger("state_notification_system", str(uuid4()))
        
        # Subscribers and watchers
        self._subscribers: Dict[UUID, StateWatcher] = {}
        self._pattern_subscribers: Dict[str, Set[UUID]] = {}
        
        # Notification buffer
        self._notification_buffer: deque = deque(maxlen=buffer_size)
        self._failed_deliveries: Dict[UUID, List[StateChange]] = {}
        
        # Redis pub/sub
        self._pubsub: Optional[aioredis.client.PubSub] = None
        self._pubsub_task: Optional[asyncio.Task] = None
        
        # Background tasks
        self._delivery_task: Optional[asyncio.Task] = None
        self._retry_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Performance metrics
        self.metrics = {
            'notifications_sent': 0,
            'notifications_delivered': 0,
            'notifications_failed': 0,
            'subscribers_count': 0,
            'avg_delivery_time_ms': 0.0,
            'buffer_utilization': 0.0
        }
        
        # Redis channels
        self.STATE_CHANGE_CHANNEL = "state_changes"
        self.NOTIFICATION_CHANNEL_PREFIX = "notifications:"
        
        # Delivery tracking
        self._delivery_times: List[float] = []
    
    async def initialize(self) -> None:
        """Initialize notification system."""
        self.logger.logger.info("Initializing State Notification System")
        
        try:
            # Initialize Redis pub/sub
            self._pubsub = self.redis.pubsub()
            await self._pubsub.subscribe(self.STATE_CHANGE_CHANNEL)
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.logger.logger.info("State Notification System initialized")
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'initialize'})
            raise MAOSError(f"Failed to initialize notification system: {str(e)}")
    
    async def subscribe(
        self,
        watcher: StateWatcher
    ) -> UUID:
        """
        Subscribe to state change notifications.
        
        Args:
            watcher: State watcher configuration
            
        Returns:
            Subscription ID
        """
        try:
            subscription_id = watcher.id
            
            # Store subscriber
            self._subscribers[subscription_id] = watcher
            
            # Add to pattern index
            pattern = watcher.key_pattern
            if pattern not in self._pattern_subscribers:
                self._pattern_subscribers[pattern] = set()
            self._pattern_subscribers[pattern].add(subscription_id)
            
            # Update metrics
            self.metrics['subscribers_count'] = len(self._subscribers)
            
            self.logger.logger.info(
                f"Added state subscription",
                extra={
                    'subscription_id': str(subscription_id),
                    'pattern': pattern,
                    'agent_id': str(watcher.agent_id) if watcher.agent_id else None,
                    'change_types': [ct.value for ct in watcher.change_types]
                }
            )
            
            return subscription_id
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'subscribe',
                'pattern': watcher.key_pattern
            })
            raise MAOSError(f"Failed to create subscription: {str(e)}")
    
    async def unsubscribe(self, subscription_id: UUID) -> bool:
        """
        Unsubscribe from state change notifications.
        
        Args:
            subscription_id: Subscription to remove
            
        Returns:
            True if successful
        """
        try:
            if subscription_id not in self._subscribers:
                return False
            
            watcher = self._subscribers[subscription_id]
            
            # Remove from pattern index
            pattern = watcher.key_pattern
            if pattern in self._pattern_subscribers:
                self._pattern_subscribers[pattern].discard(subscription_id)
                if not self._pattern_subscribers[pattern]:
                    del self._pattern_subscribers[pattern]
            
            # Remove subscriber
            del self._subscribers[subscription_id]
            
            # Clean up failed deliveries
            if subscription_id in self._failed_deliveries:
                del self._failed_deliveries[subscription_id]
            
            # Update metrics
            self.metrics['subscribers_count'] = len(self._subscribers)
            
            self.logger.logger.info(
                f"Removed state subscription",
                extra={'subscription_id': str(subscription_id)}
            )
            
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'unsubscribe',
                'subscription_id': str(subscription_id)
            })
            return False
    
    async def notify_change(self, change: StateChange) -> None:
        """
        Notify subscribers of a state change.
        
        Args:
            change: State change to notify
        """
        try:
            start_time = time.time()
            
            # Add to buffer
            self._notification_buffer.append(change)
            
            # Publish to Redis channel for distributed notifications
            await self.redis.publish(
                self.STATE_CHANGE_CHANNEL,
                json.dumps(change.to_dict(), default=str)
            )
            
            # Find matching subscribers
            matching_subscribers = await self._find_matching_subscribers(change)
            
            # Deliver notifications
            delivered_count = 0
            for subscriber_id in matching_subscribers:
                if subscriber_id in self._subscribers:
                    watcher = self._subscribers[subscriber_id]
                    
                    try:
                        await self._deliver_notification(watcher, change)
                        delivered_count += 1
                        
                    except Exception as delivery_error:
                        # Add to failed deliveries for retry
                        if subscriber_id not in self._failed_deliveries:
                            self._failed_deliveries[subscriber_id] = []
                        self._failed_deliveries[subscriber_id].append(change)
                        
                        self.logger.log_error(delivery_error, {
                            'operation': 'deliver_notification',
                            'subscriber_id': str(subscriber_id),
                            'change_id': str(change.id)
                        })
            
            # Update metrics
            self.metrics['notifications_sent'] += 1
            self.metrics['notifications_delivered'] += delivered_count
            
            delivery_time = (time.time() - start_time) * 1000
            self._update_avg_delivery_time(delivery_time)
            
            self.logger.logger.debug(
                f"Notified state change",
                extra={
                    'change_id': str(change.id),
                    'key': str(change.key),
                    'change_type': change.change_type.value,
                    'matching_subscribers': len(matching_subscribers),
                    'delivered_count': delivered_count,
                    'delivery_time_ms': delivery_time
                }
            )
            
        except Exception as e:
            self.metrics['notifications_failed'] += 1
            self.logger.log_error(e, {
                'operation': 'notify_change',
                'change_id': str(change.id) if change else None
            })
    
    async def _find_matching_subscribers(self, change: StateChange) -> Set[UUID]:
        """Find subscribers that match the state change."""
        matching_subscribers = set()
        
        try:
            key_str = str(change.key)
            
            # Check each pattern
            for pattern, subscriber_ids in self._pattern_subscribers.items():
                if self._matches_pattern(key_str, pattern):
                    for subscriber_id in subscriber_ids:
                        if subscriber_id in self._subscribers:
                            watcher = self._subscribers[subscriber_id]
                            
                            # Check change type filter
                            if (not watcher.change_types or 
                                change.change_type in watcher.change_types):
                                matching_subscribers.add(subscriber_id)
            
            return matching_subscribers
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'find_matching_subscribers',
                'change_id': str(change.id)
            })
            return set()
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern (supports wildcards)."""
        import re
        
        # Convert wildcard pattern to regex
        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        regex_pattern = f'^{regex_pattern}$'
        
        try:
            return bool(re.match(regex_pattern, key))
        except re.error:
            # If regex is invalid, fall back to exact match
            return key == pattern
    
    async def _deliver_notification(self, watcher: StateWatcher, change: StateChange) -> None:
        """Deliver notification to a specific watcher."""
        try:
            if not watcher.callback:
                return
            
            # Call callback with timeout
            if asyncio.iscoroutinefunction(watcher.callback):
                await asyncio.wait_for(
                    watcher.callback(change),
                    timeout=self.delivery_timeout
                )
            else:
                # Run sync callback in thread pool
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, watcher.callback, change)
            
            # Update watcher stats
            watcher.trigger_count += 1
            watcher.last_triggered = datetime.utcnow()
            
        except asyncio.TimeoutError:
            raise MAOSError(f"Notification delivery timed out for watcher {watcher.id}")
        except Exception as e:
            raise MAOSError(f"Notification delivery failed: {str(e)}")
    
    async def _retry_failed_deliveries(self) -> None:
        """Retry failed notification deliveries."""
        try:
            retry_count = 0
            
            for subscriber_id, failed_changes in list(self._failed_deliveries.items()):
                if subscriber_id not in self._subscribers:
                    # Subscriber no longer exists, remove failed deliveries
                    del self._failed_deliveries[subscriber_id]
                    continue
                
                watcher = self._subscribers[subscriber_id]
                successful_deliveries = []
                
                # Try to deliver each failed change
                for change in failed_changes[:self.batch_size]:  # Limit batch size
                    try:
                        await self._deliver_notification(watcher, change)
                        successful_deliveries.append(change)
                        retry_count += 1
                        
                    except Exception as e:
                        self.logger.log_error(e, {
                            'operation': 'retry_delivery',
                            'subscriber_id': str(subscriber_id),
                            'change_id': str(change.id)
                        })
                
                # Remove successful deliveries from failed list
                for change in successful_deliveries:
                    failed_changes.remove(change)
                
                # Remove subscriber from failed deliveries if all succeeded
                if not failed_changes:
                    del self._failed_deliveries[subscriber_id]
            
            if retry_count > 0:
                self.logger.logger.debug(f"Retried {retry_count} failed deliveries")
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'retry_failed_deliveries'})
    
    async def _cleanup_expired_notifications(self) -> None:
        """Clean up expired notifications and inactive watchers."""
        try:
            current_time = datetime.utcnow()
            cleanup_count = 0
            
            # Clean up inactive watchers
            inactive_watchers = []
            for watcher_id, watcher in self._subscribers.items():
                # Remove watchers that haven't been triggered in a long time
                if (watcher.last_triggered and 
                    (current_time - watcher.last_triggered).total_seconds() > 86400):  # 1 day
                    inactive_watchers.append(watcher_id)
            
            for watcher_id in inactive_watchers:
                await self.unsubscribe(watcher_id)
                cleanup_count += 1
            
            # Clean up old failed deliveries
            expired_failures = []
            for subscriber_id, failed_changes in self._failed_deliveries.items():
                # Remove old failed deliveries (older than 1 hour)
                expired_changes = [
                    change for change in failed_changes
                    if (current_time - change.timestamp).total_seconds() > 3600
                ]
                
                for expired_change in expired_changes:
                    failed_changes.remove(expired_change)
                    cleanup_count += 1
                
                if not failed_changes:
                    expired_failures.append(subscriber_id)
            
            for subscriber_id in expired_failures:
                del self._failed_deliveries[subscriber_id]
            
            if cleanup_count > 0:
                self.logger.logger.debug(f"Cleaned up {cleanup_count} expired notifications/watchers")
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'cleanup_expired_notifications'})
    
    async def _handle_redis_messages(self) -> None:
        """Handle incoming Redis pub/sub messages."""
        try:
            async for message in self._pubsub.listen():
                if message['type'] == 'message':
                    try:
                        # Parse state change from message
                        change_data = json.loads(message['data'])
                        
                        # Reconstruct StateChange object
                        change = StateChange(
                            id=UUID(change_data['id']),
                            key=StateKey.from_string(change_data['key']) if change_data['key'] else None,
                            change_type=StateChangeType(change_data['change_type']),
                            timestamp=datetime.fromisoformat(change_data['timestamp']),
                            agent_id=UUID(change_data['agent_id']) if change_data['agent_id'] else None,
                            metadata=change_data.get('metadata', {})
                        )
                        
                        # Handle old_value and new_value if present
                        if change_data.get('old_value'):
                            change.old_value = StateValue.from_dict(change_data['old_value'])
                        if change_data.get('new_value'):
                            change.new_value = StateValue.from_dict(change_data['new_value'])
                        
                        # Process the distributed notification
                        # (This could trigger additional local processing)
                        self.logger.logger.debug(
                            f"Received distributed state change notification",
                            extra={
                                'change_id': str(change.id),
                                'key': str(change.key),
                                'change_type': change.change_type.value
                            }
                        )
                        
                    except Exception as parse_error:
                        self.logger.log_error(parse_error, {
                            'operation': 'parse_redis_message',
                            'message_data': message.get('data', 'unknown')
                        })
                        
        except Exception as e:
            self.logger.log_error(e, {'operation': 'handle_redis_messages'})
    
    def _update_avg_delivery_time(self, delivery_time_ms: float) -> None:
        """Update average delivery time metric."""
        self._delivery_times.append(delivery_time_ms)
        
        # Keep only recent measurements (last 1000)
        if len(self._delivery_times) > 1000:
            self._delivery_times = self._delivery_times[-1000:]
        
        # Update metric
        if self._delivery_times:
            self.metrics['avg_delivery_time_ms'] = sum(self._delivery_times) / len(self._delivery_times)
    
    async def _start_background_tasks(self) -> None:
        """Start background tasks."""
        # Redis pub/sub message handler
        self._pubsub_task = asyncio.create_task(self._handle_redis_messages())
        
        # Delivery retry task
        self._retry_task = asyncio.create_task(self._retry_loop())
        
        # Cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _retry_loop(self) -> None:
        """Background task for retrying failed deliveries."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(30)  # Retry every 30 seconds
                await self._retry_failed_deliveries()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'retry_loop'})
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup task."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(300)  # Clean up every 5 minutes
                await self._cleanup_expired_notifications()
                
                # Update buffer utilization metric
                self.metrics['buffer_utilization'] = len(self._notification_buffer) / self.buffer_size * 100
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'cleanup_loop'})
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get notification system metrics."""
        return {
            **self.metrics,
            'active_subscribers': len(self._subscribers),
            'pattern_subscriptions': len(self._pattern_subscribers),
            'failed_deliveries_pending': sum(len(changes) for changes in self._failed_deliveries.values()),
            'notification_buffer_size': len(self._notification_buffer)
        }
    
    def get_subscription_stats(self) -> Dict[str, Any]:
        """Get detailed subscription statistics."""
        stats = {
            'total_subscriptions': len(self._subscribers),
            'subscriptions_by_pattern': {
                pattern: len(subscriber_ids) 
                for pattern, subscriber_ids in self._pattern_subscribers.items()
            },
            'subscriptions_by_agent': {},
            'most_active_subscriptions': []
        }
        
        # Group by agent
        for watcher in self._subscribers.values():
            if watcher.agent_id:
                agent_str = str(watcher.agent_id)
                stats['subscriptions_by_agent'][agent_str] = \
                    stats['subscriptions_by_agent'].get(agent_str, 0) + 1
        
        # Find most active subscriptions
        sorted_watchers = sorted(
            self._subscribers.values(),
            key=lambda w: w.trigger_count,
            reverse=True
        )
        
        stats['most_active_subscriptions'] = [
            {
                'watcher_id': str(w.id),
                'pattern': w.key_pattern,
                'trigger_count': w.trigger_count,
                'agent_id': str(w.agent_id) if w.agent_id else None
            }
            for w in sorted_watchers[:10]  # Top 10
        ]
        
        return stats
    
    async def get_notification_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent notification history from buffer."""
        try:
            # Get recent notifications from buffer
            recent_notifications = list(self._notification_buffer)[-limit:]
            
            history = []
            for change in recent_notifications:
                if isinstance(change, StateChange):
                    history.append(change.to_dict())
            
            return history
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'get_notification_history'})
            return []
    
    async def shutdown(self) -> None:
        """Shutdown notification system."""
        self.logger.logger.info("Shutting down State Notification System")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel background tasks
        tasks = [
            self._pubsub_task,
            self._retry_task,
            self._cleanup_task
        ]
        
        for task in tasks:
            if task:
                task.cancel()
        
        # Wait for tasks to complete
        if tasks:
            await asyncio.gather(*[t for t in tasks if t], return_exceptions=True)
        
        # Close pub/sub connection
        if self._pubsub:
            await self._pubsub.close()
        
        # Clear state
        self._subscribers.clear()
        self._pattern_subscribers.clear()
        self._notification_buffer.clear()
        self._failed_deliveries.clear()
        
        self.logger.logger.info("State Notification System shutdown completed")