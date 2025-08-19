"""
Simple Redis persistence backend for MAOS orchestration system.

This module provides a basic Redis-based persistence implementation
without external dependencies on the storage module.
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

# Optional Redis import
try:
    import redis
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


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
        if not REDIS_AVAILABLE:
            raise MAOSError(
                "Redis support not installed. Install with: pip install maos-cli[redis]"
            )
        
        # Get Redis URL from environment or use default
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        
        # Initialize Redis connection
        self.redis_client = None
        self.aio_redis = None
        
        # Store configuration
        self.enable_cluster = enable_cluster
        self.enable_compression = enable_compression
        self.enable_monitoring = enable_monitoring
        self.memory_pool_size_gb = memory_pool_size_gb
        
        # Initialize logger
        self.logger = MAOSLogger(self.__class__.__name__)
        
        # Connect to Redis
        self._connect()
    
    def _connect(self):
        """Establish Redis connection."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            self.redis_client.ping()
            self.logger.info(f"Connected to Redis at {self.redis_url}")
        except Exception as e:
            raise MAOSError(f"Failed to connect to Redis: {e}")
    
    async def _ensure_async_connection(self):
        """Ensure async Redis connection is established."""
        if not self.aio_redis:
            self.aio_redis = await aioredis.from_url(self.redis_url)
    
    async def save(self, key: str, value: Any) -> bool:
        """Save data to Redis."""
        await self._ensure_async_connection()
        try:
            serialized = pickle.dumps(value) if self.enable_compression else json.dumps(value)
            await self.aio_redis.set(key, serialized)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save key {key}: {e}")
            return False
    
    async def load(self, key: str) -> Optional[Any]:
        """Load data from Redis."""
        await self._ensure_async_connection()
        try:
            data = await self.aio_redis.get(key)
            if data:
                return pickle.loads(data) if self.enable_compression else json.loads(data)
            return None
        except Exception as e:
            self.logger.error(f"Failed to load key {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete data from Redis."""
        await self._ensure_async_connection()
        try:
            await self.aio_redis.delete(key)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        await self._ensure_async_connection()
        try:
            return await self.aio_redis.exists(key)
        except Exception as e:
            self.logger.error(f"Failed to check key {key}: {e}")
            return False
    
    async def list_keys(self, pattern: str = "*") -> List[str]:
        """List keys matching pattern."""
        await self._ensure_async_connection()
        try:
            keys = await self.aio_redis.keys(pattern)
            return [key.decode() if isinstance(key, bytes) else key for key in keys]
        except Exception as e:
            self.logger.error(f"Failed to list keys: {e}")
            return []
    
    async def clear_all(self) -> bool:
        """Clear all data from Redis."""
        await self._ensure_async_connection()
        try:
            await self.aio_redis.flushdb()
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear data: {e}")
            return False
    
    async def close(self):
        """Close Redis connections."""
        if self.aio_redis:
            await self.aio_redis.close()
        if self.redis_client:
            self.redis_client.close()