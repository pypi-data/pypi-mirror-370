"""
Redis-based Shared State Management System for MAOS

This module provides a comprehensive distributed state management system
with Redis cluster integration, optimistic locking, memory pool management,
and high-performance operations for <100ms latency requirements.
"""

from .redis_state_manager import RedisStateManager
from .memory_pool_manager import MemoryPoolManager
from .cluster_manager import RedisClusterManager
from .version_manager import VersionManager
from .lock_manager import OptimisticLockManager
from .conflict_resolver import ConflictResolver
from .notification_system import StateNotificationSystem
from .bulk_operations import BulkOperationsManager
from .backup_recovery import BackupRecoveryManager
from .monitoring import RedisStateMonitor
from .data_structures import RedisDataStructures
from .types import (
    StateKey,
    StateValue,
    VersionedState,
    LockToken,
    ConflictResolution,
    MemoryPartition,
    StateChange,
    BulkOperation,
    BackupMetadata
)

__all__ = [
    'RedisStateManager',
    'MemoryPoolManager',
    'RedisClusterManager', 
    'VersionManager',
    'OptimisticLockManager',
    'ConflictResolver',
    'StateNotificationSystem',
    'BulkOperationsManager',
    'BackupRecoveryManager',
    'RedisStateMonitor',
    'RedisDataStructures',
    'StateKey',
    'StateValue',
    'VersionedState',
    'LockToken',
    'ConflictResolution',
    'MemoryPartition',
    'StateChange',
    'BulkOperation',
    'BackupMetadata'
]

__version__ = '1.0.0'