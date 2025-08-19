"""
Memory Pool Manager for Redis-based state management.

Manages 10GB+ memory pools with partitioning and resource quotas.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from uuid import UUID, uuid4
from aioredis import Redis

from .types import StateKey, MemoryPartition, MemoryPartitionType
from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError


class MemoryPoolManager:
    """
    Manages distributed memory pools with partitioning and quotas.
    
    Features:
    - 10GB+ memory pool support
    - Agent-specific partitions
    - Automatic cleanup
    - Resource quotas
    - Memory usage analytics
    """
    
    def __init__(
        self,
        redis: Redis,
        total_size_gb: int = 10,
        default_partition_size_mb: int = 100,
        cleanup_interval: int = 300,  # 5 minutes
        quota_enforcement: bool = True
    ):
        """Initialize memory pool manager."""
        self.redis = redis
        self.total_size_bytes = total_size_gb * 1024 * 1024 * 1024
        self.default_partition_size_bytes = default_partition_size_mb * 1024 * 1024
        self.cleanup_interval = cleanup_interval
        self.quota_enforcement = quota_enforcement
        
        self.logger = MAOSLogger("memory_pool_manager", str(uuid4()))
        
        # Partitions tracking
        self._partitions: Dict[UUID, MemoryPartition] = {}
        self._agent_partitions: Dict[UUID, Set[UUID]] = {}  # agent_id -> partition_ids
        self._key_allocations: Dict[str, Dict] = {}  # key -> allocation info
        
        # Memory usage tracking
        self._allocated_bytes = 0
        self._reserved_bytes = 0
        
        # Performance metrics
        self.metrics = {
            'total_allocations': 0,
            'total_deallocations': 0,
            'allocation_failures': 0,
            'cleanup_operations': 0,
            'fragmentation_ratio': 0.0,
            'utilization_percentage': 0.0
        }
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._monitoring_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Redis keys
        self.PARTITION_PREFIX = "memory_partition:"
        self.ALLOCATION_PREFIX = "memory_alloc:"
        self.QUOTA_PREFIX = "memory_quota:"
        self.STATS_KEY = "memory_pool:stats"
    
    async def initialize(self) -> None:
        """Initialize memory pool manager."""
        self.logger.logger.info("Initializing Memory Pool Manager")
        
        try:
            # Load existing partitions from Redis
            await self._load_partitions()
            
            # Create default shared partition if none exist
            if not self._partitions:
                await self._create_default_partitions()
            
            # Start background tasks
            await self._start_background_tasks()
            
            # Update initial metrics
            await self._update_metrics()
            
            self.logger.logger.info(
                f"Memory Pool Manager initialized",
                extra={
                    'total_size_gb': self.total_size_bytes // (1024**3),
                    'partitions_count': len(self._partitions),
                    'allocated_bytes': self._allocated_bytes
                }
            )
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'initialize'})
            raise MAOSError(f"Failed to initialize memory pool manager: {str(e)}")
    
    async def _load_partitions(self) -> None:
        """Load existing partitions from Redis."""
        try:
            # Scan for partition keys
            partition_keys = []
            async for key in self.redis.scan_iter(match=f"{self.PARTITION_PREFIX}*"):
                partition_keys.append(key)
            
            # Load partition data
            for key in partition_keys:
                try:
                    partition_data = await self.redis.hgetall(key)
                    if partition_data:
                        partition_id = UUID(key.split(':')[-1])
                        
                        partition = MemoryPartition(
                            id=partition_id,
                            type=MemoryPartitionType(partition_data.get('type', 'shared_pool')),
                            size_bytes=int(partition_data.get('size_bytes', 0)),
                            allocated_bytes=int(partition_data.get('allocated_bytes', 0)),
                            agent_id=UUID(partition_data['agent_id']) if partition_data.get('agent_id') else None,
                            namespace=partition_data.get('namespace', 'default'),
                            created_at=datetime.fromisoformat(partition_data.get('created_at', datetime.utcnow().isoformat())),
                            last_accessed=datetime.fromisoformat(partition_data.get('last_accessed', datetime.utcnow().isoformat())),
                            metadata=json.loads(partition_data.get('metadata', '{}'))
                        )
                        
                        self._partitions[partition_id] = partition
                        self._allocated_bytes += partition.allocated_bytes
                        
                        # Track agent partitions
                        if partition.agent_id:
                            if partition.agent_id not in self._agent_partitions:
                                self._agent_partitions[partition.agent_id] = set()
                            self._agent_partitions[partition.agent_id].add(partition_id)
                            
                except Exception as e:
                    self.logger.log_error(e, {
                        'operation': 'load_partition',
                        'key': key
                    })
            
            # Load key allocations
            allocation_keys = []
            async for key in self.redis.scan_iter(match=f"{self.ALLOCATION_PREFIX}*"):
                allocation_keys.append(key)
            
            for key in allocation_keys:
                try:
                    allocation_data = await self.redis.hgetall(key)
                    if allocation_data:
                        state_key = key.split(':', 2)[-1]
                        self._key_allocations[state_key] = {
                            'partition_id': UUID(allocation_data['partition_id']),
                            'size_bytes': int(allocation_data['size_bytes']),
                            'allocated_at': datetime.fromisoformat(allocation_data['allocated_at']),
                            'last_accessed': datetime.fromisoformat(allocation_data.get('last_accessed', allocation_data['allocated_at']))
                        }
                        
                except Exception as e:
                    self.logger.log_error(e, {
                        'operation': 'load_allocation',
                        'key': key
                    })
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'load_partitions'})
    
    async def _create_default_partitions(self) -> None:
        """Create default partitions."""
        # Create shared pool partition (80% of total memory)
        shared_size = int(self.total_size_bytes * 0.8)
        shared_partition = MemoryPartition(
            type=MemoryPartitionType.SHARED_POOL,
            size_bytes=shared_size,
            namespace="shared",
            metadata={'description': 'Default shared memory pool'}
        )
        
        await self._save_partition(shared_partition)
        self._partitions[shared_partition.id] = shared_partition
        
        # Create temporary partition (10% of total memory)
        temp_size = int(self.total_size_bytes * 0.1)
        temp_partition = MemoryPartition(
            type=MemoryPartitionType.TEMPORARY,
            size_bytes=temp_size,
            namespace="temporary",
            metadata={'description': 'Temporary memory partition', 'ttl': 3600}
        )
        
        await self._save_partition(temp_partition)
        self._partitions[temp_partition.id] = temp_partition
        
        # Reserve remaining 10% for agent-dedicated partitions
        self._reserved_bytes = int(self.total_size_bytes * 0.1)
    
    async def allocate_partition(
        self,
        agent_id: UUID,
        size_bytes: int,
        partition_type: str = "agent_dedicated"
    ) -> UUID:
        """
        Allocate a memory partition for an agent.
        
        Args:
            agent_id: Agent requesting the partition
            size_bytes: Size of partition in bytes
            partition_type: Type of partition
            
        Returns:
            Partition ID
        """
        try:
            # Check if we have enough space
            available_bytes = self.total_size_bytes - self._allocated_bytes - self._reserved_bytes
            if size_bytes > available_bytes:
                raise MAOSError(f"Insufficient memory: requested {size_bytes}, available {available_bytes}")
            
            # Create partition
            partition = MemoryPartition(
                type=MemoryPartitionType(partition_type),
                size_bytes=size_bytes,
                agent_id=agent_id,
                namespace=f"agent_{agent_id}",
                metadata={
                    'allocated_for_agent': str(agent_id),
                    'allocation_timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Save partition
            await self._save_partition(partition)
            self._partitions[partition.id] = partition
            
            # Update agent tracking
            if agent_id not in self._agent_partitions:
                self._agent_partitions[agent_id] = set()
            self._agent_partitions[agent_id].add(partition.id)
            
            # Update reserved bytes if this is from reserved pool
            if partition_type == "agent_dedicated":
                self._reserved_bytes = max(0, self._reserved_bytes - size_bytes)
            
            self.logger.logger.info(
                f"Allocated partition for agent {agent_id}",
                extra={
                    'partition_id': str(partition.id),
                    'size_bytes': size_bytes,
                    'partition_type': partition_type,
                    'agent_id': str(agent_id)
                }
            )
            
            return partition.id
            
        except Exception as e:
            self.metrics['allocation_failures'] += 1
            self.logger.log_error(e, {
                'operation': 'allocate_partition',
                'agent_id': str(agent_id),
                'size_bytes': size_bytes
            })
            raise MAOSError(f"Failed to allocate partition: {str(e)}")
    
    async def deallocate_partition(self, partition_id: UUID) -> bool:
        """
        Deallocate a memory partition.
        
        Args:
            partition_id: Partition to deallocate
            
        Returns:
            True if successful
        """
        try:
            if partition_id not in self._partitions:
                return False
            
            partition = self._partitions[partition_id]
            
            # Remove all key allocations in this partition
            keys_to_remove = []
            for key, allocation in self._key_allocations.items():
                if allocation['partition_id'] == partition_id:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                await self._deallocate_key_internal(key)
            
            # Remove partition tracking
            if partition.agent_id and partition.agent_id in self._agent_partitions:
                self._agent_partitions[partition.agent_id].discard(partition_id)
                if not self._agent_partitions[partition.agent_id]:
                    del self._agent_partitions[partition.agent_id]
            
            # Return space to reserved pool if it was agent-dedicated
            if partition.type == MemoryPartitionType.AGENT_DEDICATED:
                self._reserved_bytes += partition.size_bytes
            
            # Remove from Redis
            partition_key = f"{self.PARTITION_PREFIX}{partition_id}"
            await self.redis.delete(partition_key)
            
            # Remove from local tracking
            del self._partitions[partition_id]
            
            self.metrics['total_deallocations'] += 1
            
            self.logger.logger.info(
                f"Deallocated partition {partition_id}",
                extra={
                    'partition_id': str(partition_id),
                    'size_bytes': partition.size_bytes,
                    'keys_removed': len(keys_to_remove)
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'deallocate_partition',
                'partition_id': str(partition_id)
            })
            return False
    
    async def allocate_for_key(self, key: StateKey, size_bytes: int) -> bool:
        """
        Allocate memory for a specific state key.
        
        Args:
            key: State key
            size_bytes: Size to allocate
            
        Returns:
            True if successful
        """
        try:
            key_str = str(key)
            
            # Check if key already has allocation
            if key_str in self._key_allocations:
                await self._update_key_allocation(key_str, size_bytes)
                return True
            
            # Find suitable partition
            partition = await self._find_suitable_partition(key, size_bytes)
            if not partition:
                raise MAOSError(f"No suitable partition found for key {key}")
            
            # Allocate in partition
            if not partition.can_allocate(size_bytes):
                raise MAOSError(f"Partition {partition.id} cannot allocate {size_bytes} bytes")
            
            # Update partition
            partition.allocated_bytes += size_bytes
            partition.last_accessed = datetime.utcnow()
            
            # Track allocation
            self._key_allocations[key_str] = {
                'partition_id': partition.id,
                'size_bytes': size_bytes,
                'allocated_at': datetime.utcnow(),
                'last_accessed': datetime.utcnow()
            }
            
            # Save to Redis
            await self._save_key_allocation(key_str)
            await self._save_partition(partition)
            
            self._allocated_bytes += size_bytes
            self.metrics['total_allocations'] += 1
            
            self.logger.logger.debug(
                f"Allocated memory for key: {key}",
                extra={
                    'key': str(key),
                    'size_bytes': size_bytes,
                    'partition_id': str(partition.id)
                }
            )
            
            return True
            
        except Exception as e:
            self.metrics['allocation_failures'] += 1
            self.logger.log_error(e, {
                'operation': 'allocate_for_key',
                'key': str(key),
                'size_bytes': size_bytes
            })
            return False
    
    async def deallocate_for_key(self, key: StateKey) -> bool:
        """
        Deallocate memory for a specific state key.
        
        Args:
            key: State key
            
        Returns:
            True if successful
        """
        try:
            key_str = str(key)
            return await self._deallocate_key_internal(key_str)
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'deallocate_for_key',
                'key': str(key)
            })
            return False
    
    async def _deallocate_key_internal(self, key_str: str) -> bool:
        """Internal method to deallocate key allocation."""
        if key_str not in self._key_allocations:
            return True
        
        allocation = self._key_allocations[key_str]
        partition_id = allocation['partition_id']
        size_bytes = allocation['size_bytes']
        
        # Update partition
        if partition_id in self._partitions:
            partition = self._partitions[partition_id]
            partition.allocated_bytes = max(0, partition.allocated_bytes - size_bytes)
            await self._save_partition(partition)
        
        # Remove allocation tracking
        del self._key_allocations[key_str]
        
        # Remove from Redis
        allocation_key = f"{self.ALLOCATION_PREFIX}{key_str}"
        await self.redis.delete(allocation_key)
        
        self._allocated_bytes = max(0, self._allocated_bytes - size_bytes)
        self.metrics['total_deallocations'] += 1
        
        return True
    
    async def update_access_time(self, key: StateKey) -> None:
        """Update last access time for a key allocation."""
        try:
            key_str = str(key)
            if key_str in self._key_allocations:
                self._key_allocations[key_str]['last_accessed'] = datetime.utcnow()
                
                # Update partition access time
                partition_id = self._key_allocations[key_str]['partition_id']
                if partition_id in self._partitions:
                    self._partitions[partition_id].last_accessed = datetime.utcnow()
                
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'update_access_time',
                'key': str(key)
            })
    
    async def _find_suitable_partition(
        self,
        key: StateKey,
        size_bytes: int
    ) -> Optional[MemoryPartition]:
        """Find suitable partition for key allocation."""
        # Try agent-dedicated partitions first if key has agent context
        if hasattr(key, 'agent_id') and key.agent_id:
            agent_partitions = self._agent_partitions.get(key.agent_id, set())
            for partition_id in agent_partitions:
                if partition_id in self._partitions:
                    partition = self._partitions[partition_id]
                    if partition.can_allocate(size_bytes):
                        return partition
        
        # Try namespace-specific partitions
        namespace_partitions = [
            p for p in self._partitions.values()
            if p.namespace == key.namespace and p.can_allocate(size_bytes)
        ]
        
        if namespace_partitions:
            # Choose partition with most available space
            return max(namespace_partitions, key=lambda p: p.available_bytes)
        
        # Fall back to shared partitions
        shared_partitions = [
            p for p in self._partitions.values()
            if p.type in [MemoryPartitionType.SHARED_POOL, MemoryPartitionType.TEMPORARY]
            and p.can_allocate(size_bytes)
        ]
        
        if shared_partitions:
            return max(shared_partitions, key=lambda p: p.available_bytes)
        
        return None
    
    async def _update_key_allocation(self, key_str: str, new_size_bytes: int) -> None:
        """Update existing key allocation size."""
        allocation = self._key_allocations[key_str]
        old_size = allocation['size_bytes']
        size_diff = new_size_bytes - old_size
        
        partition_id = allocation['partition_id']
        partition = self._partitions[partition_id]
        
        # Check if partition can handle the increase
        if size_diff > 0 and not partition.can_allocate(size_diff):
            raise MAOSError(f"Cannot increase allocation by {size_diff} bytes")
        
        # Update allocation
        allocation['size_bytes'] = new_size_bytes
        allocation['last_accessed'] = datetime.utcnow()
        
        # Update partition
        partition.allocated_bytes += size_diff
        partition.last_accessed = datetime.utcnow()
        
        # Save changes
        await self._save_key_allocation(key_str)
        await self._save_partition(partition)
        
        self._allocated_bytes += size_diff
    
    async def _save_partition(self, partition: MemoryPartition) -> None:
        """Save partition to Redis."""
        partition_key = f"{self.PARTITION_PREFIX}{partition.id}"
        
        partition_data = {
            'type': partition.type.value,
            'size_bytes': str(partition.size_bytes),
            'allocated_bytes': str(partition.allocated_bytes),
            'namespace': partition.namespace,
            'created_at': partition.created_at.isoformat(),
            'last_accessed': partition.last_accessed.isoformat(),
            'metadata': json.dumps(partition.metadata, default=str)
        }
        
        if partition.agent_id:
            partition_data['agent_id'] = str(partition.agent_id)
        
        await self.redis.hset(partition_key, mapping=partition_data)
    
    async def _save_key_allocation(self, key_str: str) -> None:
        """Save key allocation to Redis."""
        allocation = self._key_allocations[key_str]
        allocation_key = f"{self.ALLOCATION_PREFIX}{key_str}"
        
        allocation_data = {
            'partition_id': str(allocation['partition_id']),
            'size_bytes': str(allocation['size_bytes']),
            'allocated_at': allocation['allocated_at'].isoformat(),
            'last_accessed': allocation['last_accessed'].isoformat()
        }
        
        await self.redis.hset(allocation_key, mapping=allocation_data)
    
    async def get_usage_stats(self) -> Dict[str, any]:
        """Get comprehensive memory usage statistics."""
        try:
            # Calculate partition statistics
            partition_stats = {}
            for partition_type in MemoryPartitionType:
                partitions = [p for p in self._partitions.values() if p.type == partition_type]
                if partitions:
                    total_size = sum(p.size_bytes for p in partitions)
                    allocated_size = sum(p.allocated_bytes for p in partitions)
                    partition_stats[partition_type.value] = {
                        'count': len(partitions),
                        'total_size_bytes': total_size,
                        'allocated_bytes': allocated_size,
                        'available_bytes': total_size - allocated_size,
                        'utilization_percentage': (allocated_size / total_size * 100) if total_size > 0 else 0
                    }
            
            # Calculate agent statistics
            agent_stats = {}
            for agent_id, partition_ids in self._agent_partitions.items():
                agent_partitions = [self._partitions[pid] for pid in partition_ids if pid in self._partitions]
                total_size = sum(p.size_bytes for p in agent_partitions)
                allocated_size = sum(p.allocated_bytes for p in agent_partitions)
                
                agent_stats[str(agent_id)] = {
                    'partitions': len(agent_partitions),
                    'total_size_bytes': total_size,
                    'allocated_bytes': allocated_size,
                    'utilization_percentage': (allocated_size / total_size * 100) if total_size > 0 else 0
                }
            
            # Calculate fragmentation
            fragmentation_ratio = self._calculate_fragmentation()
            
            stats = {
                'pool_overview': {
                    'total_pool_size_bytes': self.total_size_bytes,
                    'allocated_bytes': self._allocated_bytes,
                    'reserved_bytes': self._reserved_bytes,
                    'available_bytes': self.total_size_bytes - self._allocated_bytes - self._reserved_bytes,
                    'utilization_percentage': (self._allocated_bytes / self.total_size_bytes * 100),
                    'fragmentation_ratio': fragmentation_ratio
                },
                'partition_statistics': partition_stats,
                'agent_statistics': agent_stats,
                'allocation_metrics': self.metrics,
                'active_allocations': len(self._key_allocations),
                'active_partitions': len(self._partitions)
            }
            
            # Save stats to Redis for monitoring
            await self.redis.hset(self.STATS_KEY, mapping={
                'timestamp': datetime.utcnow().isoformat(),
                'stats': json.dumps(stats, default=str)
            })
            
            return stats
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'get_usage_stats'})
            return {}
    
    def _calculate_fragmentation(self) -> float:
        """Calculate memory fragmentation ratio."""
        if not self._partitions:
            return 0.0
        
        total_fragments = 0
        total_partitions = len(self._partitions)
        
        for partition in self._partitions.values():
            if partition.size_bytes > 0:
                utilization = partition.allocated_bytes / partition.size_bytes
                # Fragmentation increases as partition becomes more used but not fully used
                if 0 < utilization < 1.0:
                    total_fragments += (1.0 - utilization)
        
        return total_fragments / total_partitions if total_partitions > 0 else 0.0
    
    async def cleanup_expired_allocations(self) -> int:
        """Clean up expired allocations and unused partitions."""
        try:
            cleaned_count = 0
            current_time = datetime.utcnow()
            
            # Clean up old temporary allocations
            keys_to_remove = []
            for key_str, allocation in self._key_allocations.items():
                last_access = allocation['last_accessed']
                partition_id = allocation['partition_id']
                
                if partition_id in self._partitions:
                    partition = self._partitions[partition_id]
                    
                    # Remove allocations in temporary partitions that are old
                    if (partition.type == MemoryPartitionType.TEMPORARY and 
                        (current_time - last_access).total_seconds() > 3600):  # 1 hour
                        keys_to_remove.append(key_str)
                    
                    # Remove allocations that haven't been accessed in a long time
                    elif (current_time - last_access).total_seconds() > 86400:  # 1 day
                        keys_to_remove.append(key_str)
            
            # Clean up identified allocations
            for key_str in keys_to_remove:
                await self._deallocate_key_internal(key_str)
                cleaned_count += 1
            
            # Clean up empty agent partitions
            partitions_to_remove = []
            for partition in self._partitions.values():
                if (partition.type == MemoryPartitionType.AGENT_DEDICATED and 
                    partition.allocated_bytes == 0 and
                    (current_time - partition.last_accessed).total_seconds() > 3600):
                    partitions_to_remove.append(partition.id)
            
            for partition_id in partitions_to_remove:
                await self.deallocate_partition(partition_id)
                cleaned_count += 1
            
            if cleaned_count > 0:
                self.metrics['cleanup_operations'] += 1
                self.logger.logger.info(
                    f"Cleaned up {cleaned_count} expired allocations/partitions"
                )
            
            return cleaned_count
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'cleanup_expired_allocations'})
            return 0
    
    async def _update_metrics(self) -> None:
        """Update performance metrics."""
        try:
            # Update utilization percentage
            if self.total_size_bytes > 0:
                self.metrics['utilization_percentage'] = (self._allocated_bytes / self.total_size_bytes) * 100
            
            # Update fragmentation ratio
            self.metrics['fragmentation_ratio'] = self._calculate_fragmentation()
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'update_metrics'})
    
    async def _start_background_tasks(self) -> None:
        """Start background cleanup and monitoring tasks."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup task."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self.cleanup_expired_allocations()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'cleanup_loop'})
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring task."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Update every minute
                await self._update_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'monitoring_loop'})
    
    async def shutdown(self) -> None:
        """Shutdown memory pool manager."""
        self.logger.logger.info("Shutting down Memory Pool Manager")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel background tasks
        if self._cleanup_task:
            self._cleanup_task.cancel()
        if self._monitoring_task:
            self._monitoring_task.cancel()
        
        # Wait for tasks to complete
        tasks = [task for task in [self._cleanup_task, self._monitoring_task] if task]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Save final stats
        await self.get_usage_stats()
        
        # Clear local state
        self._partitions.clear()
        self._agent_partitions.clear()
        self._key_allocations.clear()
        
        self.logger.logger.info("Memory Pool Manager shutdown completed")