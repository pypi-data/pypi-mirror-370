"""
Redis-based Distributed State Manager for MAOS

Provides comprehensive distributed state management with Redis cluster integration,
optimistic locking, versioning, and high-performance operations.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Union, Callable
from uuid import UUID, uuid4
import aioredis
from aioredis import Redis
from aioredis.exceptions import RedisError, ConnectionError

from .types import (
    StateKey, StateValue, VersionedState, LockToken, StateChange,
    StateOperationType, StateChangeType, ConflictResolutionStrategy,
    BulkOperation, StateWatcher
)
from .cluster_manager import RedisClusterManager
from .lock_manager import OptimisticLockManager
from .version_manager import VersionManager
from .conflict_resolver import ConflictResolver
from .notification_system import StateNotificationSystem
from .memory_pool_manager import MemoryPoolManager
from .bulk_operations import BulkOperationsManager
from .backup_recovery import BackupRecoveryManager
from .monitoring import RedisStateMonitor
from .data_structures import RedisDataStructures
from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError


class RedisStateManager:
    """
    High-performance Redis-based distributed state manager.
    
    Features:
    - Redis cluster integration with automatic failover
    - Optimistic locking with compare-and-swap operations
    - Version control and conflict resolution
    - Memory pool management (10GB+)
    - Sub-100ms latency operations
    - Comprehensive monitoring and analytics
    """
    
    def __init__(
        self,
        redis_urls: List[str] = None,
        cluster_mode: bool = True,
        memory_pool_size_gb: int = 10,
        enable_monitoring: bool = True,
        enable_backup: bool = True,
        max_retries: int = 3,
        retry_delay: float = 0.1,
        lock_timeout: int = 30,
        notification_buffer_size: int = 10000,
        compression_enabled: bool = True,
        encryption_key: Optional[str] = None
    ):
        """Initialize Redis State Manager."""
        self.redis_urls = redis_urls or ['redis://localhost:6379']
        self.cluster_mode = cluster_mode
        self.memory_pool_size_gb = memory_pool_size_gb
        self.enable_monitoring = enable_monitoring
        self.enable_backup = enable_backup
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.lock_timeout = lock_timeout
        self.notification_buffer_size = notification_buffer_size
        self.compression_enabled = compression_enabled
        self.encryption_key = encryption_key
        
        # Initialize logger
        self.logger = MAOSLogger("redis_state_manager", str(uuid4()))
        
        # Redis connections
        self.redis: Optional[Redis] = None
        self.redis_cluster: Optional[RedisClusterManager] = None
        
        # Component managers
        self.lock_manager: Optional[OptimisticLockManager] = None
        self.version_manager: Optional[VersionManager] = None
        self.conflict_resolver: Optional[ConflictResolver] = None
        self.notification_system: Optional[StateNotificationSystem] = None
        self.memory_pool: Optional[MemoryPoolManager] = None
        self.bulk_ops: Optional[BulkOperationsManager] = None
        self.backup_recovery: Optional[BackupRecoveryManager] = None
        self.monitor: Optional[RedisStateMonitor] = None
        self.data_structures: Optional[RedisDataStructures] = None
        
        # Performance tracking
        self.operation_metrics = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'avg_latency_ms': 0.0,
            'max_latency_ms': 0.0,
            'operations_per_second': 0.0
        }
        
        # State watchers
        self._watchers: Dict[UUID, StateWatcher] = {}
        self._watcher_tasks: Dict[UUID, asyncio.Task] = {}
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        self._shutdown_event = asyncio.Event()
        
        # Connection pool settings
        self.connection_pool_settings = {
            'max_connections': 100,
            'retry_on_timeout': True,
            'health_check_interval': 30,
            'socket_keepalive': True,
            'socket_keepalive_options': {
                'TCP_KEEPIDLE': 1,
                'TCP_KEEPINTVL': 3,
                'TCP_KEEPCNT': 5,
            }
        }
    
    async def initialize(self) -> None:
        """Initialize all components and connections."""
        start_time = time.time()
        
        try:
            self.logger.logger.info("Initializing Redis State Manager")
            
            # Initialize Redis connections
            await self._initialize_redis()
            
            # Initialize component managers
            await self._initialize_components()
            
            # Start background tasks
            await self._start_background_tasks()
            
            # Verify system health
            await self._verify_system_health()
            
            init_time = (time.time() - start_time) * 1000
            self.logger.logger.info(
                f"Redis State Manager initialized successfully in {init_time:.2f}ms",
                extra={
                    'cluster_mode': self.cluster_mode,
                    'memory_pool_gb': self.memory_pool_size_gb,
                    'redis_nodes': len(self.redis_urls)
                }
            )
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'initialize'})
            raise MAOSError(f"Failed to initialize Redis State Manager: {str(e)}")
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connections."""
        if self.cluster_mode and len(self.redis_urls) > 1:
            # Initialize Redis cluster
            self.redis_cluster = RedisClusterManager(
                redis_urls=self.redis_urls,
                max_retries=self.max_retries,
                retry_delay=self.retry_delay,
                connection_pool_settings=self.connection_pool_settings
            )
            await self.redis_cluster.initialize()
            self.redis = self.redis_cluster.get_primary_connection()
        else:
            # Initialize single Redis connection
            self.redis = aioredis.from_url(
                self.redis_urls[0],
                max_connections=self.connection_pool_settings['max_connections'],
                retry_on_timeout=self.connection_pool_settings['retry_on_timeout'],
                health_check_interval=self.connection_pool_settings['health_check_interval']
            )
            
            # Test connection
            await self.redis.ping()
    
    async def _initialize_components(self) -> None:
        """Initialize all component managers."""
        # Lock manager
        self.lock_manager = OptimisticLockManager(
            redis=self.redis,
            default_timeout=self.lock_timeout,
            max_retries=self.max_retries
        )
        
        # Version manager
        self.version_manager = VersionManager(
            redis=self.redis,
            enable_compression=self.compression_enabled
        )
        
        # Conflict resolver
        self.conflict_resolver = ConflictResolver(
            redis=self.redis,
            default_strategy=ConflictResolutionStrategy.LAST_WRITE_WINS
        )
        
        # Notification system
        self.notification_system = StateNotificationSystem(
            redis=self.redis,
            buffer_size=self.notification_buffer_size
        )
        await self.notification_system.initialize()
        
        # Memory pool manager
        self.memory_pool = MemoryPoolManager(
            redis=self.redis,
            total_size_gb=self.memory_pool_size_gb
        )
        await self.memory_pool.initialize()
        
        # Bulk operations manager
        self.bulk_ops = BulkOperationsManager(
            redis=self.redis,
            max_batch_size=1000
        )
        
        # Backup and recovery
        if self.enable_backup:
            self.backup_recovery = BackupRecoveryManager(
                redis=self.redis,
                compression_enabled=self.compression_enabled,
                encryption_key=self.encryption_key
            )
        
        # Monitoring
        if self.enable_monitoring:
            self.monitor = RedisStateMonitor(
                redis=self.redis,
                collection_interval=1.0
            )
            await self.monitor.initialize()
        
        # Data structures
        self.data_structures = RedisDataStructures(redis=self.redis)
    
    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks."""
        # Memory pool cleanup task
        self._background_tasks.append(
            asyncio.create_task(self._memory_pool_cleanup_loop())
        )
        
        # Lock cleanup task
        self._background_tasks.append(
            asyncio.create_task(self._lock_cleanup_loop())
        )
        
        # Performance metrics collection task
        if self.enable_monitoring:
            self._background_tasks.append(
                asyncio.create_task(self._metrics_collection_loop())
            )
        
        # Health check task
        self._background_tasks.append(
            asyncio.create_task(self._health_check_loop())
        )
    
    async def _verify_system_health(self) -> None:
        """Verify system health and connectivity."""
        try:
            # Test Redis connectivity
            await self.redis.ping()
            
            # Test basic operations
            test_key = StateKey("test", "health", "check")
            test_value = StateValue("health_check_value")
            
            await self.set_state(test_key, test_value)
            retrieved_value = await self.get_state(test_key)
            await self.delete_state(test_key)
            
            if not retrieved_value or retrieved_value.data != test_value.data:
                raise MAOSError("Basic state operations failed")
            
            self.logger.logger.info("System health verification passed")
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'verify_system_health'})
            raise
    
    # Core State Operations
    
    async def set_state(
        self,
        key: StateKey,
        value: StateValue,
        lock_token: Optional[LockToken] = None,
        if_not_exists: bool = False
    ) -> bool:
        """
        Set state value with optimistic locking and versioning.
        
        Args:
            key: State key
            value: State value
            lock_token: Optional lock token for atomic operations
            if_not_exists: Only set if key doesn't exist
            
        Returns:
            True if operation was successful
        """
        start_time = time.time()
        operation_id = str(uuid4())
        
        try:
            # Update version information
            value = await self.version_manager.prepare_for_update(key, value)
            
            # Serialize value
            serialized_value = json.dumps(value.to_dict())
            
            # Prepare Redis operation
            redis_key = str(key)
            
            if lock_token:
                # Atomic compare-and-swap operation
                success = await self._compare_and_swap(
                    redis_key, serialized_value, lock_token
                )
            elif if_not_exists:
                # Set only if not exists
                success = await self.redis.setnx(redis_key, serialized_value)
            else:
                # Simple set operation
                await self.redis.set(redis_key, serialized_value)
                success = True
            
            if success:
                # Update memory pool allocation
                await self.memory_pool.allocate_for_key(key, len(serialized_value))
                
                # Notify watchers
                await self._notify_watchers(key, StateChangeType.UPDATED, None, value)
                
                # Update version history
                await self.version_manager.record_version(key, value)
                
                self.operation_metrics['successful_operations'] += 1
            else:
                self.operation_metrics['failed_operations'] += 1
            
            # Record latency
            latency_ms = (time.time() - start_time) * 1000
            await self._record_latency(latency_ms)
            
            self.logger.logger.debug(
                f"Set state operation completed",
                extra={
                    'operation_id': operation_id,
                    'key': str(key),
                    'success': success,
                    'latency_ms': latency_ms
                }
            )
            
            return success
            
        except Exception as e:
            self.operation_metrics['failed_operations'] += 1
            self.logger.log_error(e, {
                'operation': 'set_state',
                'operation_id': operation_id,
                'key': str(key)
            })
            raise MAOSError(f"Failed to set state: {str(e)}")
    
    async def get_state(
        self,
        key: StateKey,
        consistent_read: bool = True
    ) -> Optional[StateValue]:
        """
        Get state value with optional consistency guarantees.
        
        Args:
            key: State key
            consistent_read: Whether to ensure read consistency
            
        Returns:
            State value or None if not found
        """
        start_time = time.time()
        operation_id = str(uuid4())
        
        try:
            redis_key = str(key)
            
            if consistent_read and self.redis_cluster:
                # Read from primary for consistency
                serialized_value = await self.redis_cluster.get_primary_connection().get(redis_key)
            else:
                # Regular read (potentially from replica)
                serialized_value = await self.redis.get(redis_key)
            
            if serialized_value is None:
                return None
            
            # Deserialize value
            value_dict = json.loads(serialized_value)
            value = StateValue.from_dict(value_dict)
            
            # Update memory pool access time
            await self.memory_pool.update_access_time(key)
            
            # Record latency
            latency_ms = (time.time() - start_time) * 1000
            await self._record_latency(latency_ms)
            
            self.operation_metrics['successful_operations'] += 1
            
            self.logger.logger.debug(
                f"Get state operation completed",
                extra={
                    'operation_id': operation_id,
                    'key': str(key),
                    'found': True,
                    'latency_ms': latency_ms
                }
            )
            
            return value
            
        except Exception as e:
            self.operation_metrics['failed_operations'] += 1
            self.logger.log_error(e, {
                'operation': 'get_state',
                'operation_id': operation_id,
                'key': str(key)
            })
            raise MAOSError(f"Failed to get state: {str(e)}")
    
    async def delete_state(
        self,
        key: StateKey,
        lock_token: Optional[LockToken] = None
    ) -> bool:
        """
        Delete state value with optional locking.
        
        Args:
            key: State key
            lock_token: Optional lock token
            
        Returns:
            True if key was deleted
        """
        start_time = time.time()
        operation_id = str(uuid4())
        
        try:
            redis_key = str(key)
            
            # Get current value for notifications
            current_value = await self.get_state(key)
            
            if lock_token:
                # Atomic delete with lock verification
                success = await self._atomic_delete_with_lock(redis_key, lock_token)
            else:
                # Simple delete
                result = await self.redis.delete(redis_key)
                success = result > 0
            
            if success:
                # Free memory pool allocation
                await self.memory_pool.deallocate_for_key(key)
                
                # Notify watchers
                await self._notify_watchers(key, StateChangeType.DELETED, current_value, None)
                
                self.operation_metrics['successful_operations'] += 1
            else:
                self.operation_metrics['failed_operations'] += 1
            
            # Record latency
            latency_ms = (time.time() - start_time) * 1000
            await self._record_latency(latency_ms)
            
            self.logger.logger.debug(
                f"Delete state operation completed",
                extra={
                    'operation_id': operation_id,
                    'key': str(key),
                    'success': success,
                    'latency_ms': latency_ms
                }
            )
            
            return success
            
        except Exception as e:
            self.operation_metrics['failed_operations'] += 1
            self.logger.log_error(e, {
                'operation': 'delete_state',
                'operation_id': operation_id,
                'key': str(key)
            })
            raise MAOSError(f"Failed to delete state: {str(e)}")
    
    async def update_state(
        self,
        key: StateKey,
        updater_func: Callable[[Optional[StateValue]], StateValue],
        max_retries: Optional[int] = None
    ) -> StateValue:
        """
        Atomically update state using optimistic locking.
        
        Args:
            key: State key
            updater_func: Function to update the value
            max_retries: Maximum retry attempts
            
        Returns:
            Updated state value
        """
        max_retries = max_retries or self.max_retries
        
        for attempt in range(max_retries + 1):
            try:
                # Acquire lock
                lock_token = await self.lock_manager.acquire_lock(key)
                
                try:
                    # Get current value
                    current_value = await self.get_state(key)
                    
                    # Apply update function
                    new_value = updater_func(current_value)
                    
                    # Attempt to set with lock
                    success = await self.set_state(key, new_value, lock_token)
                    
                    if success:
                        return new_value
                    
                finally:
                    # Always release lock
                    await self.lock_manager.release_lock(lock_token)
                    
            except Exception as e:
                if attempt == max_retries:
                    self.logger.log_error(e, {
                        'operation': 'update_state',
                        'key': str(key),
                        'attempt': attempt
                    })
                    raise MAOSError(f"Failed to update state after {max_retries} attempts: {str(e)}")
                
                # Exponential backoff
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        raise MAOSError("Update operation failed after all retries")
    
    # Lock Management
    
    async def acquire_lock(
        self,
        key: StateKey,
        timeout: Optional[int] = None,
        agent_id: Optional[UUID] = None
    ) -> LockToken:
        """Acquire optimistic lock for a state key."""
        return await self.lock_manager.acquire_lock(
            key, timeout or self.lock_timeout, agent_id
        )
    
    async def release_lock(self, lock_token: LockToken) -> bool:
        """Release an acquired lock."""
        return await self.lock_manager.release_lock(lock_token)
    
    async def extend_lock(self, lock_token: LockToken, additional_time: int) -> bool:
        """Extend lock expiry time."""
        return await self.lock_manager.extend_lock(lock_token, additional_time)
    
    # Bulk Operations
    
    async def bulk_set(
        self,
        operations: Dict[StateKey, StateValue]
    ) -> BulkOperation:
        """Perform bulk set operations."""
        return await self.bulk_ops.bulk_set(operations)
    
    async def bulk_get(self, keys: List[StateKey]) -> Dict[StateKey, Optional[StateValue]]:
        """Perform bulk get operations."""
        return await self.bulk_ops.bulk_get(keys)
    
    async def bulk_delete(self, keys: List[StateKey]) -> BulkOperation:
        """Perform bulk delete operations."""
        return await self.bulk_ops.bulk_delete(keys)
    
    # State Watching and Notifications
    
    async def watch_state(
        self,
        key_pattern: str,
        callback: Callable[[StateChange], None],
        change_types: Optional[List[StateChangeType]] = None,
        agent_id: Optional[UUID] = None
    ) -> UUID:
        """
        Watch for state changes matching a pattern.
        
        Args:
            key_pattern: Pattern to match keys (supports wildcards)
            callback: Callback function for changes
            change_types: Specific change types to watch
            agent_id: Agent ID for tracking
            
        Returns:
            Watcher ID for management
        """
        watcher = StateWatcher(
            key_pattern=key_pattern,
            callback=callback,
            agent_id=agent_id,
            change_types=change_types or []
        )
        
        self._watchers[watcher.id] = watcher
        
        # Start watcher task
        self._watcher_tasks[watcher.id] = asyncio.create_task(
            self._watcher_loop(watcher)
        )
        
        self.logger.logger.info(
            f"State watcher created",
            extra={
                'watcher_id': str(watcher.id),
                'pattern': key_pattern,
                'agent_id': str(agent_id) if agent_id else None
            }
        )
        
        return watcher.id
    
    async def unwatch_state(self, watcher_id: UUID) -> bool:
        """Remove a state watcher."""
        if watcher_id not in self._watchers:
            return False
        
        # Cancel watcher task
        if watcher_id in self._watcher_tasks:
            self._watcher_tasks[watcher_id].cancel()
            del self._watcher_tasks[watcher_id]
        
        # Remove watcher
        del self._watchers[watcher_id]
        
        self.logger.logger.info(f"State watcher removed: {watcher_id}")
        return True
    
    # Memory Pool Operations
    
    async def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory pool usage statistics."""
        return await self.memory_pool.get_usage_stats()
    
    async def allocate_memory_partition(
        self,
        agent_id: UUID,
        size_mb: int,
        partition_type: str = "agent_dedicated"
    ) -> UUID:
        """Allocate dedicated memory partition for an agent."""
        return await self.memory_pool.allocate_partition(
            agent_id, size_mb * 1024 * 1024, partition_type
        )
    
    async def deallocate_memory_partition(self, partition_id: UUID) -> bool:
        """Deallocate a memory partition."""
        return await self.memory_pool.deallocate_partition(partition_id)
    
    # Data Structure Operations
    
    async def list_operations(self, key: StateKey) -> 'RedisListOperations':
        """Get list operations interface for a key."""
        return self.data_structures.get_list_operations(key)
    
    async def set_operations(self, key: StateKey) -> 'RedisSetOperations':
        """Get set operations interface for a key."""
        return self.data_structures.get_set_operations(key)
    
    async def sorted_set_operations(self, key: StateKey) -> 'RedisSortedSetOperations':
        """Get sorted set operations interface for a key."""
        return self.data_structures.get_sorted_set_operations(key)
    
    async def hash_operations(self, key: StateKey) -> 'RedisHashOperations':
        """Get hash operations interface for a key."""
        return self.data_structures.get_hash_operations(key)
    
    # Backup and Recovery
    
    async def create_backup(
        self,
        name: str,
        namespaces: Optional[List[str]] = None
    ) -> UUID:
        """Create a backup of state data."""
        if not self.backup_recovery:
            raise MAOSError("Backup functionality not enabled")
        
        return await self.backup_recovery.create_backup(name, namespaces)
    
    async def restore_backup(self, backup_id: UUID) -> bool:
        """Restore state from a backup."""
        if not self.backup_recovery:
            raise MAOSError("Backup functionality not enabled")
        
        return await self.backup_recovery.restore_backup(backup_id)
    
    # Monitoring and Metrics
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        metrics = self.operation_metrics.copy()
        
        if self.monitor:
            metrics.update(self.monitor.get_metrics())
        
        return metrics
    
    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get Redis cluster status."""
        if self.redis_cluster:
            return await self.redis_cluster.get_cluster_status()
        else:
            # Single instance status
            info = await self.redis.info()
            return {
                'mode': 'single',
                'connected': True,
                'memory_usage': info.get('used_memory', 0),
                'connected_clients': info.get('connected_clients', 0)
            }
    
    # Internal Helper Methods
    
    async def _compare_and_swap(
        self,
        redis_key: str,
        new_value: str,
        lock_token: LockToken
    ) -> bool:
        """Perform atomic compare-and-swap operation."""
        # Lua script for atomic compare-and-swap
        lua_script = """
        local lock_key = KEYS[1] .. ":lock"
        local current_lock = redis.call('GET', lock_key)
        
        if current_lock == ARGV[1] then
            redis.call('SET', KEYS[1], ARGV[2])
            redis.call('DEL', lock_key)
            return 1
        else
            return 0
        end
        """
        
        result = await self.redis.eval(
            lua_script,
            1,
            redis_key,
            lock_token.token,
            new_value
        )
        
        return result == 1
    
    async def _atomic_delete_with_lock(
        self,
        redis_key: str,
        lock_token: LockToken
    ) -> bool:
        """Perform atomic delete with lock verification."""
        lua_script = """
        local lock_key = KEYS[1] .. ":lock"
        local current_lock = redis.call('GET', lock_key)
        
        if current_lock == ARGV[1] then
            local deleted = redis.call('DEL', KEYS[1])
            redis.call('DEL', lock_key)
            return deleted
        else
            return 0
        end
        """
        
        result = await self.redis.eval(
            lua_script,
            1,
            redis_key,
            lock_token.token
        )
        
        return result > 0
    
    async def _notify_watchers(
        self,
        key: StateKey,
        change_type: StateChangeType,
        old_value: Optional[StateValue],
        new_value: Optional[StateValue]
    ) -> None:
        """Notify state watchers of changes."""
        change = StateChange(
            key=key,
            change_type=change_type,
            old_value=old_value,
            new_value=new_value
        )
        
        # Find matching watchers
        for watcher in self._watchers.values():
            if (watcher.active and 
                watcher.matches_key(key) and 
                watcher.matches_change_type(change_type)):
                
                try:
                    if asyncio.iscoroutinefunction(watcher.callback):
                        await watcher.callback(change)
                    else:
                        watcher.callback(change)
                    
                    watcher.trigger_count += 1
                    watcher.last_triggered = datetime.utcnow()
                    
                except Exception as e:
                    self.logger.log_error(e, {
                        'operation': 'notify_watcher',
                        'watcher_id': str(watcher.id),
                        'key': str(key)
                    })
    
    async def _watcher_loop(self, watcher: StateWatcher) -> None:
        """Background loop for state watcher."""
        try:
            while watcher.active and not self._shutdown_event.is_set():
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'watcher_loop',
                'watcher_id': str(watcher.id)
            })
    
    async def _record_latency(self, latency_ms: float) -> None:
        """Record operation latency for metrics."""
        self.operation_metrics['total_operations'] += 1
        
        # Update average latency (exponential moving average)
        current_avg = self.operation_metrics['avg_latency_ms']
        alpha = 0.1  # Smoothing factor
        self.operation_metrics['avg_latency_ms'] = (
            alpha * latency_ms + (1 - alpha) * current_avg
        )
        
        # Update max latency
        if latency_ms > self.operation_metrics['max_latency_ms']:
            self.operation_metrics['max_latency_ms'] = latency_ms
    
    # Background Task Loops
    
    async def _memory_pool_cleanup_loop(self) -> None:
        """Background task for memory pool cleanup."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Run every minute
                if self.memory_pool:
                    await self.memory_pool.cleanup_expired_allocations()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'memory_pool_cleanup'})
    
    async def _lock_cleanup_loop(self) -> None:
        """Background task for expired lock cleanup."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(30)  # Run every 30 seconds
                if self.lock_manager:
                    await self.lock_manager.cleanup_expired_locks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'lock_cleanup'})
    
    async def _metrics_collection_loop(self) -> None:
        """Background task for metrics collection."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(1)  # Collect every second
                if self.monitor:
                    await self.monitor.collect_metrics()
                    
                    # Update operations per second
                    current_time = time.time()
                    if hasattr(self, '_last_metrics_time'):
                        time_delta = current_time - self._last_metrics_time
                        if time_delta > 0:
                            ops_delta = (self.operation_metrics['total_operations'] - 
                                       getattr(self, '_last_total_ops', 0))
                            self.operation_metrics['operations_per_second'] = ops_delta / time_delta
                    
                    self._last_metrics_time = current_time
                    self._last_total_ops = self.operation_metrics['total_operations']
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'metrics_collection'})
    
    async def _health_check_loop(self) -> None:
        """Background task for health checks."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Check Redis connectivity
                await self.redis.ping()
                
                # Check cluster health if applicable
                if self.redis_cluster:
                    await self.redis_cluster.health_check()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'health_check'})
    
    async def shutdown(self) -> None:
        """Graceful shutdown of the state manager."""
        self.logger.logger.info("Shutting down Redis State Manager")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel all background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Cancel watcher tasks
        for task in self._watcher_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        if self._watcher_tasks:
            await asyncio.gather(*self._watcher_tasks.values(), return_exceptions=True)
        
        # Shutdown components
        if self.notification_system:
            await self.notification_system.shutdown()
        
        if self.monitor:
            await self.monitor.shutdown()
        
        if self.redis_cluster:
            await self.redis_cluster.shutdown()
        elif self.redis:
            await self.redis.close()
        
        self.logger.logger.info("Redis State Manager shutdown completed")