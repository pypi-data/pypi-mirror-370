"""
Redis persistence backend for MAOS orchestration system.

This module provides Redis-based persistence implementation that integrates
with the comprehensive RedisStateManager for distributed state management.
"""

import asyncio
import json
import pickle
from typing import Any, Optional, Dict, List
from uuid import uuid4
import os

from .persistence import PersistenceInterface
from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError

# Import the comprehensive Redis state manager
from maos.storage.redis_state.redis_state_manager import RedisStateManager
from maos.storage.redis_state.types import StateKey, StateValue


class RedisPersistence(PersistenceInterface):
    """
    Redis-based persistence backend for MAOS.
    
    Provides high-performance, distributed state management using Redis.
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        enable_cluster: bool = False,
        enable_compression: bool = True,
        enable_monitoring: bool = True,
        memory_pool_size_gb: int = 10
    ):
        """
        Initialize Redis persistence backend.
        
        Args:
            redis_url: Redis connection URL (defaults to env var or localhost)
            enable_cluster: Enable Redis cluster mode for high availability
            enable_compression: Enable data compression
            enable_monitoring: Enable performance monitoring
            memory_pool_size_gb: Memory pool size in GB
        """
        # Get Redis URL from environment or use default
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        
        # Parse multiple Redis URLs if provided (for cluster mode)
        redis_urls = [self.redis_url]
        if ',' in self.redis_url:
            redis_urls = self.redis_url.split(',')
        
        # Initialize logger
        self.logger = MAOSLogger("redis_persistence", str(uuid4()))
        
        # Initialize Redis state manager with all advanced features
        self.state_manager = RedisStateManager(
            redis_urls=redis_urls,
            cluster_mode=enable_cluster,
            memory_pool_size_gb=memory_pool_size_gb,
            enable_monitoring=enable_monitoring,
            enable_backup=True,
            compression_enabled=enable_compression,
            notification_buffer_size=10000,
            lock_timeout=30,
            max_retries=3
        )
        
        # Track initialization status
        self._initialized = False
        
        # Namespace for MAOS data
        self.namespace = "maos"
        
        # Metrics
        self._metrics = {
            'total_saves': 0,
            'total_loads': 0,
            'total_deletes': 0,
            'failed_operations': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    async def initialize(self) -> None:
        """Initialize Redis connection and state manager."""
        if self._initialized:
            return
        
        try:
            # Initialize the Redis state manager
            await self.state_manager.initialize()
            
            self._initialized = True
            
            self.logger.logger.info(
                f"Redis persistence initialized",
                extra={
                    'redis_url': self.redis_url,
                    'cluster_mode': self.state_manager.cluster_mode,
                    'memory_pool_gb': self.state_manager.memory_pool_size_gb
                }
            )
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'initialize'})
            raise MAOSError(f"Failed to initialize Redis persistence: {str(e)}")
    
    async def save(self, key: str, data: Any) -> None:
        """
        Save data to Redis.
        
        Args:
            key: Storage key
            data: Data to store (will be serialized)
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Create namespaced key
            redis_key = StateKey(
                namespace=self.namespace,
                category="persistence",
                identifier=key
            )
            
            # Serialize data
            if isinstance(data, (dict, list)):
                serialized_data = json.dumps(data, default=str)
                data_type = "json"
            else:
                # Use pickle for complex objects
                serialized_data = pickle.dumps(data)
                data_type = "pickle"
            
            # Create state value
            state_value = StateValue(
                data=serialized_data,
                metadata={
                    'data_type': data_type,
                    'key': key
                }
            )
            
            # Save using state manager with versioning and locking
            await self.state_manager.set_state(
                key=redis_key,
                value=state_value,
                with_lock=True
            )
            
            self._metrics['total_saves'] += 1
            
            self.logger.logger.debug(
                f"Saved data to Redis",
                extra={'key': key, 'data_type': data_type}
            )
            
        except Exception as e:
            self._metrics['failed_operations'] += 1
            self.logger.log_error(e, {'operation': 'save', 'key': key})
            raise MAOSError(f"Failed to save to Redis: {str(e)}")
    
    async def load(self, key: str) -> Optional[Any]:
        """
        Load data from Redis.
        
        Args:
            key: Storage key
            
        Returns:
            Deserialized data or None if not found
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Create namespaced key
            redis_key = StateKey(
                namespace=self.namespace,
                category="persistence",
                identifier=key
            )
            
            # Get state from Redis
            state_value = await self.state_manager.get_state(redis_key)
            
            if state_value is None:
                self._metrics['cache_misses'] += 1
                return None
            
            self._metrics['cache_hits'] += 1
            
            # Deserialize based on data type
            data_type = state_value.metadata.get('data_type', 'json')
            
            if data_type == 'json':
                data = json.loads(state_value.data)
            else:
                # Use pickle for complex objects
                data = pickle.loads(state_value.data)
            
            self._metrics['total_loads'] += 1
            
            self.logger.logger.debug(
                f"Loaded data from Redis",
                extra={'key': key, 'data_type': data_type}
            )
            
            return data
            
        except Exception as e:
            self._metrics['failed_operations'] += 1
            self.logger.log_error(e, {'operation': 'load', 'key': key})
            return None
    
    async def delete(self, key: str) -> None:
        """
        Delete data from Redis.
        
        Args:
            key: Storage key
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Create namespaced key
            redis_key = StateKey(
                namespace=self.namespace,
                category="persistence",
                identifier=key
            )
            
            # Delete from Redis
            await self.state_manager.delete_state(redis_key)
            
            self._metrics['total_deletes'] += 1
            
            self.logger.logger.debug(
                f"Deleted data from Redis",
                extra={'key': key}
            )
            
        except Exception as e:
            self._metrics['failed_operations'] += 1
            self.logger.log_error(e, {'operation': 'delete', 'key': key})
            raise MAOSError(f"Failed to delete from Redis: {str(e)}")
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis.
        
        Args:
            key: Storage key
            
        Returns:
            True if key exists
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Create namespaced key
            redis_key = StateKey(
                namespace=self.namespace,
                category="persistence",
                identifier=key
            )
            
            # Check existence
            state_value = await self.state_manager.get_state(redis_key)
            return state_value is not None
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'exists', 'key': key})
            return False
    
    async def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """
        List all keys or keys with prefix.
        
        Args:
            prefix: Optional key prefix filter
            
        Returns:
            List of matching keys
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Get all keys from namespace
            pattern = f"{self.namespace}:persistence:*"
            if prefix:
                pattern = f"{self.namespace}:persistence:{prefix}*"
            
            # Use Redis state manager's search capability
            keys = await self.state_manager.search_keys(pattern)
            
            # Extract identifiers from full keys
            result_keys = []
            prefix_len = len(f"{self.namespace}:persistence:")
            for key in keys:
                if isinstance(key, str):
                    result_keys.append(key[prefix_len:])
            
            return result_keys
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'list_keys', 'prefix': prefix})
            return []
    
    async def clear(self) -> None:
        """Clear all data from Redis namespace."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Get all keys in namespace
            keys = await self.list_keys()
            
            # Delete all keys
            for key in keys:
                await self.delete(key)
            
            self.logger.logger.info(
                f"Cleared Redis namespace",
                extra={'namespace': self.namespace, 'keys_deleted': len(keys)}
            )
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'clear'})
            raise MAOSError(f"Failed to clear Redis: {str(e)}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get persistence statistics.
        
        Returns:
            Dictionary of statistics
        """
        stats = self._metrics.copy()
        
        # Add Redis state manager metrics
        if self._initialized and self.state_manager:
            redis_metrics = self.state_manager.get_metrics()
            stats.update({
                'redis_operations': redis_metrics.get('total_operations', 0),
                'redis_latency_ms': redis_metrics.get('avg_latency_ms', 0),
                'redis_memory_usage_mb': redis_metrics.get('memory_usage_mb', 0),
                'redis_connected': redis_metrics.get('connected', False)
            })
        
        return stats
    
    async def shutdown(self) -> None:
        """Shutdown Redis connection and cleanup."""
        if self._initialized and self.state_manager:
            try:
                await self.state_manager.shutdown()
                self._initialized = False
                
                self.logger.logger.info("Redis persistence shutdown complete")
                
            except Exception as e:
                self.logger.log_error(e, {'operation': 'shutdown'})
    
    def __str__(self) -> str:
        """String representation."""
        return f"RedisPersistence(url={self.redis_url}, initialized={self._initialized})"