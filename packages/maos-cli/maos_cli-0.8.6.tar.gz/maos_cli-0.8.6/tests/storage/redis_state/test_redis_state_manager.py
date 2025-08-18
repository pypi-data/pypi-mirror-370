"""
Test suite for Redis State Manager.
"""

import asyncio
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import uuid4

from src.storage.redis_state.redis_state_manager import RedisStateManager
from src.storage.redis_state.types import StateKey, StateValue, StateChangeType, LockToken
from src.maos.utils.exceptions import MAOSError


@pytest.fixture
async def mock_redis():
    """Mock Redis client."""
    redis_mock = AsyncMock()
    redis_mock.ping.return_value = True
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = 1
    redis_mock.exists.return_value = 0
    redis_mock.info.return_value = {
        'used_memory': 1000000,
        'connected_clients': 5,
        'total_commands_processed': 1000,
        'keyspace_hits': 800,
        'keyspace_misses': 200
    }
    return redis_mock


@pytest.fixture
async def state_manager(mock_redis):
    """Create Redis state manager with mocked dependencies."""
    with patch('src.storage.redis_state.redis_state_manager.aioredis.from_url') as mock_from_url:
        mock_from_url.return_value = mock_redis
        
        manager = RedisStateManager(
            redis_urls=['redis://localhost:6379'],
            cluster_mode=False,
            memory_pool_size_gb=1,
            enable_monitoring=False,
            enable_backup=False
        )
        
        # Mock all component managers
        manager.lock_manager = AsyncMock()
        manager.version_manager = AsyncMock()
        manager.conflict_resolver = AsyncMock()
        manager.notification_system = AsyncMock()
        manager.memory_pool = AsyncMock()
        manager.bulk_ops = AsyncMock()
        manager.data_structures = AsyncMock()
        
        # Initialize without actual Redis connections
        await manager._initialize_redis = AsyncMock()
        await manager._initialize_components = AsyncMock()
        await manager._start_background_tasks = AsyncMock()
        await manager._verify_system_health = AsyncMock()
        
        manager.redis = mock_redis
        
        return manager


@pytest.fixture
def sample_state_key():
    """Sample state key."""
    return StateKey(
        namespace="test",
        category="data",
        identifier="key1"
    )


@pytest.fixture
def sample_state_value():
    """Sample state value."""
    return StateValue(
        data={"message": "test value"},
        version=1,
        metadata={"test": True}
    )


class TestRedisStateManager:
    """Test cases for Redis State Manager."""
    
    @pytest.mark.asyncio
    async def test_initialization(self, mock_redis):
        """Test state manager initialization."""
        with patch('src.storage.redis_state.redis_state_manager.aioredis.from_url') as mock_from_url:
            mock_from_url.return_value = mock_redis
            
            manager = RedisStateManager(
                redis_urls=['redis://localhost:6379'],
                cluster_mode=False
            )
            
            # Mock initialization methods
            manager._initialize_redis = AsyncMock()
            manager._initialize_components = AsyncMock()
            manager._start_background_tasks = AsyncMock()
            manager._verify_system_health = AsyncMock()
            
            await manager.initialize()
            
            assert manager.redis_urls == ['redis://localhost:6379']
            assert not manager.cluster_mode
    
    @pytest.mark.asyncio
    async def test_set_state_success(self, state_manager, sample_state_key, sample_state_value):
        """Test successful state set operation."""
        # Mock version manager
        state_manager.version_manager.prepare_for_update.return_value = sample_state_value
        state_manager.version_manager.record_version.return_value = True
        
        # Mock memory pool
        state_manager.memory_pool.allocate_for_key.return_value = True
        
        # Mock notifications
        state_manager._notify_watchers = AsyncMock()
        
        result = await state_manager.set_state(sample_state_key, sample_state_value)
        
        assert result is True
        state_manager.redis.set.assert_called_once()
        state_manager.memory_pool.allocate_for_key.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_state_success(self, state_manager, sample_state_key, sample_state_value):
        """Test successful state get operation."""
        # Mock Redis response
        redis_data = json.dumps(sample_state_value.to_dict())
        state_manager.redis.get.return_value = redis_data
        
        # Mock memory pool
        state_manager.memory_pool.update_access_time.return_value = None
        
        result = await state_manager.get_state(sample_state_key)
        
        assert result is not None
        assert result.data == sample_state_value.data
        state_manager.redis.get.assert_called_once_with(str(sample_state_key))
    
    @pytest.mark.asyncio
    async def test_get_state_not_found(self, state_manager, sample_state_key):
        """Test get state when key doesn't exist."""
        state_manager.redis.get.return_value = None
        
        result = await state_manager.get_state(sample_state_key)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_state_success(self, state_manager, sample_state_key, sample_state_value):
        """Test successful state delete operation."""
        # Mock get current value
        state_manager.get_state = AsyncMock(return_value=sample_state_value)
        
        # Mock Redis delete
        state_manager.redis.delete.return_value = 1
        
        # Mock memory pool
        state_manager.memory_pool.deallocate_for_key.return_value = True
        
        # Mock notifications
        state_manager._notify_watchers = AsyncMock()
        
        result = await state_manager.delete_state(sample_state_key)
        
        assert result is True
        state_manager.redis.delete.assert_called_once()
        state_manager.memory_pool.deallocate_for_key.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_state_with_optimistic_locking(self, state_manager, sample_state_key):
        """Test atomic state update with optimistic locking."""
        # Mock lock manager
        mock_lock_token = LockToken(key=sample_state_key)
        state_manager.lock_manager.acquire_lock.return_value = mock_lock_token
        state_manager.lock_manager.release_lock.return_value = True
        
        # Mock get and set operations
        original_value = StateValue(data={"count": 1})
        state_manager.get_state = AsyncMock(return_value=original_value)
        state_manager.set_state = AsyncMock(return_value=True)
        
        def updater_func(current_value):
            if current_value:
                new_data = current_value.data.copy()
                new_data["count"] += 1
                return StateValue(data=new_data)
            return StateValue(data={"count": 1})
        
        result = await state_manager.update_state(sample_state_key, updater_func)
        
        assert result is not None
        assert result.data["count"] == 2
        state_manager.lock_manager.acquire_lock.assert_called_once()
        state_manager.lock_manager.release_lock.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_bulk_operations(self, state_manager):
        """Test bulk operations."""
        # Mock bulk operations manager
        mock_bulk_result = MagicMock()
        mock_bulk_result.status = "completed"
        
        state_manager.bulk_ops.bulk_set.return_value = mock_bulk_result
        state_manager.bulk_ops.bulk_get.return_value = {}
        state_manager.bulk_ops.bulk_delete.return_value = mock_bulk_result
        
        # Test bulk set
        operations = {
            StateKey("test", "data", "key1"): StateValue(data={"value": 1}),
            StateKey("test", "data", "key2"): StateValue(data={"value": 2})
        }
        
        result = await state_manager.bulk_set(operations)
        assert result.status == "completed"
        
        # Test bulk get
        keys = list(operations.keys())
        result = await state_manager.bulk_get(keys)
        assert isinstance(result, dict)
        
        # Test bulk delete
        result = await state_manager.bulk_delete(keys)
        assert result.status == "completed"
    
    @pytest.mark.asyncio
    async def test_state_watching(self, state_manager, sample_state_key):
        """Test state watching functionality."""
        callback_called = False
        
        def test_callback(change):
            nonlocal callback_called
            callback_called = True
        
        # Test watch creation
        watcher_id = await state_manager.watch_state("test:*", test_callback)
        assert watcher_id is not None
        
        # Test unwatch
        result = await state_manager.unwatch_state(watcher_id)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_memory_pool_operations(self, state_manager):
        """Test memory pool operations."""
        agent_id = uuid4()
        
        # Mock memory pool methods
        state_manager.memory_pool.get_usage_stats.return_value = {
            'total_size_bytes': 1000000,
            'allocated_bytes': 500000,
            'utilization_percentage': 50.0
        }
        
        state_manager.memory_pool.allocate_partition.return_value = uuid4()
        state_manager.memory_pool.deallocate_partition.return_value = True
        
        # Test usage stats
        stats = await state_manager.get_memory_usage()
        assert 'total_size_bytes' in stats
        
        # Test partition allocation
        partition_id = await state_manager.allocate_memory_partition(agent_id, 100)
        assert partition_id is not None
        
        # Test partition deallocation
        result = await state_manager.deallocate_memory_partition(partition_id)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_error_handling(self, state_manager, sample_state_key, sample_state_value):
        """Test error handling in various operations."""
        # Test Redis connection error
        state_manager.redis.set.side_effect = Exception("Redis connection failed")
        
        with pytest.raises(MAOSError):
            await state_manager.set_state(sample_state_key, sample_state_value)
        
        # Reset side effect
        state_manager.redis.set.side_effect = None
        state_manager.redis.set.return_value = True
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, state_manager):
        """Test performance metrics collection."""
        # Perform some operations to generate metrics
        key = StateKey("test", "perf", "metric")
        value = StateValue(data={"test": "performance"})
        
        state_manager.redis.set.return_value = True
        state_manager.version_manager.prepare_for_update.return_value = value
        state_manager.version_manager.record_version.return_value = True
        state_manager.memory_pool.allocate_for_key.return_value = True
        state_manager._notify_watchers = AsyncMock()
        
        await state_manager.set_state(key, value)
        
        metrics = state_manager.get_performance_metrics()
        
        assert 'successful_operations' in metrics
        assert 'total_operations' in metrics
        assert metrics['successful_operations'] >= 1
    
    @pytest.mark.asyncio
    async def test_data_structure_operations(self, state_manager, sample_state_key):
        """Test Redis data structure operations."""
        # Mock data structures
        mock_list_ops = AsyncMock()
        mock_set_ops = AsyncMock()
        mock_sorted_set_ops = AsyncMock()
        mock_hash_ops = AsyncMock()
        
        state_manager.data_structures.get_list_operations.return_value = mock_list_ops
        state_manager.data_structures.get_set_operations.return_value = mock_set_ops
        state_manager.data_structures.get_sorted_set_operations.return_value = mock_sorted_set_ops
        state_manager.data_structures.get_hash_operations.return_value = mock_hash_ops
        
        # Test getting operations interfaces
        list_ops = await state_manager.list_operations(sample_state_key)
        set_ops = await state_manager.set_operations(sample_state_key)
        sorted_set_ops = await state_manager.sorted_set_operations(sample_state_key)
        hash_ops = await state_manager.hash_operations(sample_state_key)
        
        assert list_ops is mock_list_ops
        assert set_ops is mock_set_ops
        assert sorted_set_ops is mock_sorted_set_ops
        assert hash_ops is mock_hash_ops
    
    @pytest.mark.asyncio
    async def test_cluster_status(self, state_manager):
        """Test cluster status retrieval."""
        # Mock single instance status
        state_manager.redis_cluster = None
        
        status = await state_manager.get_cluster_status()
        
        assert status['mode'] == 'single'
        assert 'connected' in status
        assert 'memory_usage' in status
    
    @pytest.mark.asyncio 
    async def test_shutdown(self, state_manager):
        """Test graceful shutdown."""
        # Mock shutdown methods for components
        state_manager.notification_system.shutdown = AsyncMock()
        state_manager.monitor = None
        state_manager.redis_cluster = None
        state_manager.redis.close = AsyncMock()
        
        # Mock background tasks
        state_manager._background_tasks = []
        state_manager._watcher_tasks = {}
        state_manager._shutdown_event = AsyncMock()
        
        await state_manager.shutdown()
        
        state_manager.notification_system.shutdown.assert_called_once()
        state_manager.redis.close.assert_called_once()


class TestStateKeyValue:
    """Test cases for StateKey and StateValue classes."""
    
    def test_state_key_string_representation(self):
        """Test StateKey string conversion."""
        key = StateKey(
            namespace="test_ns",
            category="test_cat", 
            identifier="test_id",
            partition="test_part"
        )
        
        assert str(key) == "test_ns:test_cat:test_id:test_part"
    
    def test_state_key_from_string(self):
        """Test StateKey creation from string."""
        key_str = "test_ns:test_cat:test_id"
        key = StateKey.from_string(key_str)
        
        assert key.namespace == "test_ns"
        assert key.category == "test_cat"
        assert key.identifier == "test_id"
        assert key.partition is None
    
    def test_state_value_serialization(self):
        """Test StateValue serialization."""
        value = StateValue(
            data={"test": "data"},
            version=1,
            metadata={"meta": "test"}
        )
        
        value_dict = value.to_dict()
        
        assert value_dict['data'] == {"test": "data"}
        assert value_dict['version'] == 1
        assert value_dict['metadata'] == {"meta": "test"}
        
        # Test deserialization
        restored_value = StateValue.from_dict(value_dict)
        assert restored_value.data == value.data
        assert restored_value.version == value.version
        assert restored_value.metadata == value.metadata


if __name__ == "__main__":
    pytest.main([__file__])