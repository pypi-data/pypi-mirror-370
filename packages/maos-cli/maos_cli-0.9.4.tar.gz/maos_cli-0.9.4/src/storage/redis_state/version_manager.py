"""
Version Manager for Redis-based state management.

Provides version control and history tracking for shared state.
"""

import asyncio
import json
import time
import gzip
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4
from aioredis import Redis

from .types import StateKey, StateValue, VersionedState
from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError


class VersionManager:
    """
    Manages versioning and history for distributed state.
    
    Features:
    - Automatic version incrementing
    - Version history tracking
    - Timestamp-based versioning
    - Compression for large histories
    - Version rollback capabilities
    """
    
    def __init__(
        self,
        redis: Redis,
        max_versions_per_key: int = 100,
        history_retention_days: int = 30,
        enable_compression: bool = True,
        cleanup_interval: int = 3600  # 1 hour
    ):
        """Initialize version manager."""
        self.redis = redis
        self.max_versions_per_key = max_versions_per_key
        self.history_retention_days = history_retention_days
        self.enable_compression = enable_compression
        self.cleanup_interval = cleanup_interval
        
        self.logger = MAOSLogger("version_manager", str(uuid4()))
        
        # Version tracking
        self._version_cache: Dict[str, int] = {}
        
        # Performance metrics
        self.metrics = {
            'versions_created': 0,
            'versions_retrieved': 0,
            'versions_cleaned': 0,
            'compression_ratio': 0.0,
            'avg_version_size_bytes': 0.0
        }
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
    
    def _get_version_key(self, state_key: StateKey) -> str:
        """Generate Redis key for version tracking."""
        return f"version:{state_key}"
    
    def _get_history_key(self, state_key: StateKey) -> str:
        """Generate Redis key for version history."""
        return f"history:{state_key}"
    
    def _get_metadata_key(self, state_key: StateKey) -> str:
        """Generate Redis key for version metadata."""
        return f"version_meta:{state_key}"
    
    async def get_current_version(self, key: StateKey) -> int:
        """Get current version number for a key."""
        version_key = self._get_version_key(key)
        
        # Check cache first
        if version_key in self._version_cache:
            return self._version_cache[version_key]
        
        try:
            version = await self.redis.get(version_key)
            if version is None:
                return 0
            
            version_num = int(version)
            self._version_cache[version_key] = version_num
            return version_num
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'get_current_version',
                'key': str(key)
            })
            return 0
    
    async def increment_version(self, key: StateKey) -> int:
        """Increment version number for a key."""
        version_key = self._get_version_key(key)
        
        try:
            new_version = await self.redis.incr(version_key)
            self._version_cache[version_key] = new_version
            
            self.logger.logger.debug(
                f"Incremented version for key: {key}",
                extra={
                    'key': str(key),
                    'new_version': new_version
                }
            )
            
            return new_version
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'increment_version',
                'key': str(key)
            })
            raise MAOSError(f"Failed to increment version: {str(e)}")
    
    async def prepare_for_update(
        self,
        key: StateKey,
        value: StateValue
    ) -> StateValue:
        """
        Prepare a state value for update with version information.
        
        Args:
            key: State key
            value: State value to prepare
            
        Returns:
            StateValue with updated version information
        """
        try:
            # Get current version
            current_version = await self.get_current_version(key)
            
            # Create new version
            new_version = current_version + 1
            
            # Update value with version info
            value.version = new_version
            value.updated_at = datetime.utcnow()
            
            # Add version metadata
            if 'version_info' not in value.metadata:
                value.metadata['version_info'] = {}
            
            value.metadata['version_info'].update({
                'version': new_version,
                'previous_version': current_version,
                'timestamp': value.updated_at.isoformat(),
                'checksum': self._calculate_checksum(value.data)
            })
            
            return value
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'prepare_for_update',
                'key': str(key)
            })
            raise MAOSError(f"Failed to prepare value for update: {str(e)}")
    
    async def record_version(
        self,
        key: StateKey,
        value: StateValue
    ) -> bool:
        """
        Record a version in the history.
        
        Args:
            key: State key
            value: State value to record
            
        Returns:
            True if version was recorded successfully
        """
        try:
            # Update version counter
            await self.increment_version(key)
            
            # Prepare version record
            version_record = {
                'version': value.version,
                'data': value.data,
                'timestamp': value.updated_at.isoformat(),
                'metadata': value.metadata,
                'checksum': self._calculate_checksum(value.data)
            }
            
            # Serialize and optionally compress
            serialized_record = json.dumps(version_record, default=str)
            
            if self.enable_compression and len(serialized_record) > 1024:
                # Compress large records
                compressed_record = gzip.compress(serialized_record.encode())
                record_data = compressed_record
                is_compressed = True
            else:
                record_data = serialized_record.encode()
                is_compressed = False
            
            # Store in version history (sorted set with timestamp as score)
            history_key = self._get_history_key(key)
            timestamp_score = time.time()
            
            await self.redis.zadd(
                history_key,
                {record_data: timestamp_score}
            )
            
            # Store version metadata
            metadata_key = self._get_metadata_key(key)
            await self.redis.hset(
                metadata_key,
                mapping={
                    f"v{value.version}:compressed": str(is_compressed),
                    f"v{value.version}:size": str(len(record_data)),
                    f"v{value.version}:timestamp": str(timestamp_score)
                }
            )
            
            # Cleanup old versions if needed
            await self._cleanup_old_versions(key)
            
            # Update metrics
            self.metrics['versions_created'] += 1
            self._update_avg_size_metric(len(record_data))
            
            if is_compressed:
                compression_ratio = len(record_data) / len(serialized_record)
                self._update_compression_ratio_metric(compression_ratio)
            
            self.logger.logger.debug(
                f"Version recorded for key: {key}",
                extra={
                    'key': str(key),
                    'version': value.version,
                    'size_bytes': len(record_data),
                    'compressed': is_compressed
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'record_version',
                'key': str(key),
                'version': value.version
            })
            return False
    
    async def get_version_history(
        self,
        key: StateKey,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get version history for a key.
        
        Args:
            key: State key
            limit: Maximum number of versions to return
            offset: Number of versions to skip
            
        Returns:
            List of version records
        """
        try:
            history_key = self._get_history_key(key)
            metadata_key = self._get_metadata_key(key)
            
            # Get version records (most recent first)
            records = await self.redis.zrevrange(
                history_key,
                offset,
                offset + limit - 1,
                withscores=True
            )
            
            if not records:
                return []
            
            # Get metadata for all versions
            metadata = await self.redis.hgetall(metadata_key)
            
            version_history = []
            
            for record_data, timestamp_score in records:
                try:
                    # Determine if record is compressed
                    is_compressed = False
                    
                    # Try to find compression info in metadata
                    for meta_key, meta_value in metadata.items():
                        if meta_key.endswith(':compressed'):
                            version_from_key = meta_key.split(':')[0]
                            # We'd need better logic here to match records to versions
                            is_compressed = meta_value.lower() == 'true'
                            break
                    
                    # Deserialize record
                    if is_compressed:
                        decompressed_data = gzip.decompress(record_data)
                        record_dict = json.loads(decompressed_data.decode())
                    else:
                        record_dict = json.loads(record_data.decode())
                    
                    # Add timestamp from score
                    record_dict['stored_at'] = datetime.fromtimestamp(timestamp_score).isoformat()
                    
                    version_history.append(record_dict)
                    
                except Exception as record_error:
                    self.logger.log_error(record_error, {
                        'operation': 'deserialize_version_record',
                        'key': str(key)
                    })
                    continue
            
            self.metrics['versions_retrieved'] += len(version_history)
            
            self.logger.logger.debug(
                f"Retrieved version history for key: {key}",
                extra={
                    'key': str(key),
                    'versions_returned': len(version_history),
                    'limit': limit,
                    'offset': offset
                }
            )
            
            return version_history
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'get_version_history',
                'key': str(key)
            })
            return []
    
    async def get_version(
        self,
        key: StateKey,
        version: int
    ) -> Optional[StateValue]:
        """
        Get a specific version of a state value.
        
        Args:
            key: State key
            version: Version number
            
        Returns:
            StateValue for the specified version or None if not found
        """
        try:
            history = await self.get_version_history(key, limit=self.max_versions_per_key)
            
            # Find the requested version
            for record in history:
                if record.get('version') == version:
                    # Reconstruct StateValue
                    value = StateValue(
                        data=record['data'],
                        version=record['version'],
                        created_at=datetime.fromisoformat(record.get('timestamp', datetime.utcnow().isoformat())),
                        updated_at=datetime.fromisoformat(record.get('timestamp', datetime.utcnow().isoformat())),
                        metadata=record.get('metadata', {})
                    )
                    
                    self.logger.logger.debug(
                        f"Retrieved version {version} for key: {key}",
                        extra={
                            'key': str(key),
                            'version': version
                        }
                    )
                    
                    return value
            
            return None
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'get_version',
                'key': str(key),
                'version': version
            })
            return None
    
    async def rollback_to_version(
        self,
        key: StateKey,
        target_version: int
    ) -> Optional[StateValue]:
        """
        Rollback state to a specific version.
        
        Args:
            key: State key
            target_version: Version to rollback to
            
        Returns:
            StateValue of the target version or None if rollback failed
        """
        try:
            # Get the target version
            target_value = await self.get_version(key, target_version)
            
            if target_value is None:
                raise MAOSError(f"Target version {target_version} not found")
            
            # Create new value based on target version but with new version number
            current_version = await self.get_current_version(key)
            rollback_version = current_version + 1
            
            rollback_value = StateValue(
                data=target_value.data,
                version=rollback_version,
                created_at=target_value.created_at,
                updated_at=datetime.utcnow(),
                metadata=target_value.metadata.copy()
            )
            
            # Add rollback metadata
            rollback_value.metadata['rollback_info'] = {
                'rollback_from_version': current_version,
                'rollback_to_version': target_version,
                'rollback_timestamp': datetime.utcnow().isoformat()
            }
            
            # Record the rollback as a new version
            await self.record_version(key, rollback_value)
            
            self.logger.logger.info(
                f"Rolled back key {key} from version {current_version} to version {target_version}",
                extra={
                    'key': str(key),
                    'from_version': current_version,
                    'to_version': target_version,
                    'new_version': rollback_version
                }
            )
            
            return rollback_value
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'rollback_to_version',
                'key': str(key),
                'target_version': target_version
            })
            return None
    
    async def compare_versions(
        self,
        key: StateKey,
        version1: int,
        version2: int
    ) -> Optional[Dict[str, Any]]:
        """
        Compare two versions of a state value.
        
        Args:
            key: State key
            version1: First version to compare
            version2: Second version to compare
            
        Returns:
            Dictionary with comparison results
        """
        try:
            value1 = await self.get_version(key, version1)
            value2 = await self.get_version(key, version2)
            
            if value1 is None or value2 is None:
                return None
            
            comparison = {
                'key': str(key),
                'version1': {
                    'version': version1,
                    'timestamp': value1.updated_at.isoformat(),
                    'checksum': self._calculate_checksum(value1.data),
                    'data_size': len(json.dumps(value1.data, default=str))
                },
                'version2': {
                    'version': version2,
                    'timestamp': value2.updated_at.isoformat(),
                    'checksum': self._calculate_checksum(value2.data),
                    'data_size': len(json.dumps(value2.data, default=str))
                },
                'differences': {
                    'data_changed': value1.data != value2.data,
                    'metadata_changed': value1.metadata != value2.metadata,
                    'checksum_match': self._calculate_checksum(value1.data) == self._calculate_checksum(value2.data)
                }
            }
            
            return comparison
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'compare_versions',
                'key': str(key),
                'version1': version1,
                'version2': version2
            })
            return None
    
    async def _cleanup_old_versions(self, key: StateKey) -> None:
        """Clean up old versions for a key."""
        try:
            history_key = self._get_history_key(key)
            
            # Get current count
            total_versions = await self.redis.zcard(history_key)
            
            if total_versions > self.max_versions_per_key:
                # Remove oldest versions
                versions_to_remove = total_versions - self.max_versions_per_key
                await self.redis.zremrangebyrank(history_key, 0, versions_to_remove - 1)
                
                self.metrics['versions_cleaned'] += versions_to_remove
                
                self.logger.logger.debug(
                    f"Cleaned up {versions_to_remove} old versions for key: {key}",
                    extra={
                        'key': str(key),
                        'versions_removed': versions_to_remove,
                        'remaining_versions': self.max_versions_per_key
                    }
                )
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'cleanup_old_versions',
                'key': str(key)
            })
    
    async def cleanup_expired_versions(self) -> int:
        """Clean up versions older than retention period."""
        try:
            cutoff_time = time.time() - (self.history_retention_days * 24 * 3600)
            cleaned_count = 0
            
            # Get all history keys
            history_keys = []
            async for key in self.redis.scan_iter(match="history:*"):
                history_keys.append(key)
            
            for history_key in history_keys:
                # Remove versions older than cutoff
                removed = await self.redis.zremrangebyscore(
                    history_key,
                    0,
                    cutoff_time
                )
                cleaned_count += removed
            
            if cleaned_count > 0:
                self.metrics['versions_cleaned'] += cleaned_count
                
                self.logger.logger.info(
                    f"Cleaned up {cleaned_count} expired versions",
                    extra={
                        'cleaned_count': cleaned_count,
                        'retention_days': self.history_retention_days
                    }
                )
            
            return cleaned_count
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'cleanup_expired_versions'})
            return 0
    
    def _calculate_checksum(self, data: Any) -> str:
        """Calculate checksum for data integrity."""
        import hashlib
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _update_avg_size_metric(self, size_bytes: int) -> None:
        """Update average version size metric."""
        current_avg = self.metrics['avg_version_size_bytes']
        alpha = 0.1  # Smoothing factor
        self.metrics['avg_version_size_bytes'] = alpha * size_bytes + (1 - alpha) * current_avg
    
    def _update_compression_ratio_metric(self, ratio: float) -> None:
        """Update compression ratio metric."""
        current_ratio = self.metrics['compression_ratio']
        alpha = 0.1  # Smoothing factor
        self.metrics['compression_ratio'] = alpha * ratio + (1 - alpha) * current_ratio
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get version manager metrics."""
        return self.metrics.copy()
    
    def get_version_stats(self, key: StateKey) -> Optional[Dict[str, Any]]:
        """Get version statistics for a specific key."""
        try:
            current_version = self._version_cache.get(self._get_version_key(key), 0)
            
            return {
                'current_version': current_version,
                'total_versions': current_version,
                'max_versions_stored': self.max_versions_per_key,
                'retention_days': self.history_retention_days
            }
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'get_version_stats',
                'key': str(key)
            })
            return None
    
    async def start_background_tasks(self) -> None:
        """Start background cleanup tasks."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup task."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self.cleanup_expired_versions()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'cleanup_loop'})
    
    async def shutdown(self) -> None:
        """Shutdown version manager."""
        self.logger.logger.info("Shutting down version manager")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Clear cache
        self._version_cache.clear()
        
        self.logger.logger.info("Version manager shutdown completed")