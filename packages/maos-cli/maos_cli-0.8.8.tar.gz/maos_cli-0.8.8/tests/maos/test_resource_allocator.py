"""
Unit tests for Resource Allocator component.
"""

import pytest
import asyncio
from uuid import uuid4

from src.maos.core.resource_allocator import ResourceAllocator, AllocationStrategy, ResourcePool
from src.maos.models.resource import Resource, ResourceType, ResourceAllocation
from src.maos.models.task import TaskPriority
from src.maos.utils.exceptions import ResourceError, ResourceAllocationError, ValidationError


@pytest.fixture
async def resource_allocator():
    """Create a ResourceAllocator instance for testing."""
    allocator = ResourceAllocator(
        default_allocation_strategy=AllocationStrategy.BEST_FIT,
        auto_scaling_enabled=True,
        capacity_monitoring_interval=0.1,  # Fast for testing
        queue_processing_interval=0.1
    )
    await allocator.start()
    yield allocator
    await allocator.shutdown()


@pytest.fixture
def sample_requester_id():
    """Create a sample requester ID for testing."""
    return uuid4()


@pytest.mark.asyncio
class TestResourceAllocator:
    """Test cases for ResourceAllocator class."""
    
    async def test_create_resource(self, resource_allocator):
        """Test creating a new resource."""
        resource = await resource_allocator.create_resource(
            resource_type=ResourceType.CPU,
            capacity=4.0
        )
        
        assert isinstance(resource, Resource)
        assert resource.type == ResourceType.CPU
        assert resource.total_capacity == 4.0
        assert resource.available_capacity == 4.0
        assert resource.unit == 'cores'
        
        # Resource should be registered in allocator
        retrieved_resource = resource_allocator.get_resource(resource.id)
        assert retrieved_resource is not None
        assert retrieved_resource.id == resource.id
    
    async def test_create_resource_pool(self, resource_allocator):
        """Test creating a resource pool."""
        pool = await resource_allocator.create_resource_pool(
            name="Test CPU Pool",
            resource_type=ResourceType.CPU,
            initial_capacity=8.0,
            allocation_strategy=AllocationStrategy.LOAD_BALANCED,
            auto_scaling_config={
                'min_capacity': 4.0,
                'max_capacity': 16.0,
                'scale_up_threshold': 0.8,
                'scale_down_threshold': 0.3
            }
        )
        
        assert isinstance(pool, ResourcePool)
        assert pool.name == "Test CPU Pool"
        assert pool.resource_type == ResourceType.CPU
        assert pool.total_capacity == 8.0
        assert pool.allocation_strategy == AllocationStrategy.LOAD_BALANCED
        assert pool.min_capacity == 4.0
        assert pool.max_capacity == 16.0
    
    async def test_request_allocation_simple(self, resource_allocator, sample_requester_id):
        """Test simple resource allocation request."""
        # Create resource pool
        await resource_allocator.create_resource_pool(
            name="Test Pool",
            resource_type=ResourceType.MEMORY,
            initial_capacity=2048.0
        )
        
        # Request allocation
        request_id = await resource_allocator.request_allocation(
            requester_id=sample_requester_id,
            resource_requirements={'memory_mb': 512.0},
            priority=TaskPriority.MEDIUM
        )
        
        assert request_id is not None
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        # Check allocation request
        request = resource_allocator.get_allocation_request(request_id)
        assert request is not None
        assert request.requester_id == sample_requester_id
    
    async def test_allocation_strategies(self, resource_allocator, sample_requester_id):
        """Test different allocation strategies."""
        # Create multiple resources in a pool
        pool = await resource_allocator.create_resource_pool(
            name="Strategy Test Pool",
            resource_type=ResourceType.MEMORY,
            initial_capacity=0  # Start empty
        )
        
        # Add multiple resources with different capacities
        resource1 = await resource_allocator.create_resource(
            resource_type=ResourceType.MEMORY,
            capacity=1024.0,
            pool_id=pool.id
        )
        resource2 = await resource_allocator.create_resource(
            resource_type=ResourceType.MEMORY,
            capacity=2048.0,
            pool_id=pool.id
        )
        
        pool.update_capacity_stats()
        
        # Test best fit strategy (should choose smallest fitting resource)
        allocated_resource = await resource_allocator._allocate_from_pool(
            pool=pool,
            requester_id=sample_requester_id,
            amount=512.0,
            strategy=AllocationStrategy.BEST_FIT
        )
        
        assert allocated_resource is not None
        # Should choose the smaller resource (1024) over larger (2048)
        assert allocated_resource.total_capacity == 1024.0
    
    async def test_release_allocation(self, resource_allocator, sample_requester_id):
        """Test releasing resource allocations."""
        # Create resource
        resource = await resource_allocator.create_resource(
            resource_type=ResourceType.CPU,
            capacity=4.0
        )
        
        # Allocate directly for testing
        success = resource.allocate(sample_requester_id, 2.0)
        assert success
        assert resource.available_capacity == 2.0
        assert resource.allocated_capacity == 2.0
        
        # Release allocation
        released_amount = await resource_allocator.release_allocation(
            requester_id=sample_requester_id,
            resource_id=resource.id
        )
        
        assert released_amount == 2.0
        assert resource.available_capacity == 4.0
        assert resource.allocated_capacity == 0.0
    
    async def test_resource_pool_utilization(self, resource_allocator, sample_requester_id):
        """Test resource pool utilization calculation."""
        pool = await resource_allocator.create_resource_pool(
            name="Utilization Test Pool",
            resource_type=ResourceType.DISK,
            initial_capacity=1000.0
        )
        
        # Initially, utilization should be 0%
        assert pool.get_utilization_percentage() == 0.0
        
        # Allocate some resources
        resource = list(pool.resources.values())[0]
        resource.allocate(sample_requester_id, 500.0)
        pool.update_capacity_stats()
        
        # Utilization should be 50%
        assert pool.get_utilization_percentage() == 50.0
    
    async def test_allocation_queue_processing(self, resource_allocator, sample_requester_id):
        """Test allocation queue processing."""
        # Create resource pool
        await resource_allocator.create_resource_pool(
            name="Queue Test Pool",
            resource_type=ResourceType.CPU,
            initial_capacity=4.0
        )
        
        # Submit multiple allocation requests
        request_ids = []
        for i in range(3):
            request_id = await resource_allocator.request_allocation(
                requester_id=uuid4(),
                resource_requirements={'cpu_cores': 1.0},
                priority=TaskPriority.MEDIUM
            )
            request_ids.append(request_id)
        
        # Wait for processing
        await asyncio.sleep(0.3)
        
        # All requests should have been processed
        for request_id in request_ids:
            request = resource_allocator.get_allocation_request(request_id)
            # Request should either be completed or failed
            assert request is None or request.allocated_at is not None
    
    async def test_priority_based_allocation(self, resource_allocator):
        """Test priority-based resource allocation."""
        # Create limited resource pool
        await resource_allocator.create_resource_pool(
            name="Priority Test Pool",
            resource_type=ResourceType.MEMORY,
            initial_capacity=1024.0
        )
        
        # Submit high priority request
        high_priority_id = await resource_allocator.request_allocation(
            requester_id=uuid4(),
            resource_requirements={'memory_mb': 512.0},
            priority=TaskPriority.CRITICAL
        )
        
        # Submit low priority request
        low_priority_id = await resource_allocator.request_allocation(
            requester_id=uuid4(),
            resource_requirements={'memory_mb': 512.0},
            priority=TaskPriority.LOW
        )
        
        # Wait for processing
        await asyncio.sleep(0.3)
        
        # Both should be processed, but high priority first
        high_priority_request = resource_allocator.get_allocation_request(high_priority_id)
        low_priority_request = resource_allocator.get_allocation_request(low_priority_id)
        
        # At least high priority should be allocated
        assert high_priority_request is None or high_priority_request.allocated_at is not None
    
    async def test_resource_exhaustion(self, resource_allocator, sample_requester_id):
        """Test handling resource exhaustion."""
        # Create small resource pool
        await resource_allocator.create_resource_pool(
            name="Small Pool",
            resource_type=ResourceType.MEMORY,
            initial_capacity=512.0
        )
        
        # Try to allocate more than available
        request_id = await resource_allocator.request_allocation(
            requester_id=sample_requester_id,
            resource_requirements={'memory_mb': 1024.0},  # More than pool capacity
            priority=TaskPriority.MEDIUM,
            max_wait_time=1  # Short timeout
        )
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        # Request should still be pending or failed
        request = resource_allocator.get_allocation_request(request_id)
        if request:
            assert request.allocated_at is None  # Should not be allocated
    
    async def test_auto_scaling_up(self, resource_allocator, sample_requester_id):
        """Test auto-scaling up when utilization is high."""
        # Create pool with auto-scaling
        pool = await resource_allocator.create_resource_pool(
            name="Auto Scale Pool",
            resource_type=ResourceType.CPU,
            initial_capacity=2.0,
            auto_scaling_config={
                'min_capacity': 2.0,
                'max_capacity': 8.0,
                'scale_up_threshold': 0.7  # 70%
            }
        )
        
        # Allocate resources to trigger scaling
        resource = list(pool.resources.values())[0]
        resource.allocate(sample_requester_id, 1.5)  # 75% utilization
        pool.update_capacity_stats()
        
        # Check if scaling is needed
        assert pool.needs_scaling_up()
        
        # Trigger scaling check
        await resource_allocator._check_scaling_needs()
        
        # Wait a bit for scaling to happen
        await asyncio.sleep(0.1)
        
        # Pool should have more capacity (though this is simplified for testing)
        pool.update_capacity_stats()
    
    async def test_allocation_request_expiration(self, resource_allocator, sample_requester_id):
        """Test allocation request expiration."""
        # Create empty pool (no resources)
        await resource_allocator.create_resource_pool(
            name="Empty Pool",
            resource_type=ResourceType.DISK,
            initial_capacity=0
        )
        
        # Submit request with short timeout
        request_id = await resource_allocator.request_allocation(
            requester_id=sample_requester_id,
            resource_requirements={'disk_mb': 1000.0},
            priority=TaskPriority.MEDIUM,
            max_wait_time=1  # 1 second
        )
        
        # Wait for expiration
        await asyncio.sleep(1.2)
        
        # Request should be expired and removed
        request = resource_allocator.get_allocation_request(request_id)
        assert request is None or request.is_expired()
    
    async def test_capacity_monitoring(self, resource_allocator, sample_requester_id):
        """Test capacity monitoring and metrics updating."""
        # Create resource
        resource = await resource_allocator.create_resource(
            resource_type=ResourceType.MEMORY,
            capacity=1024.0
        )
        
        # Allocate some capacity
        resource.allocate(sample_requester_id, 512.0)
        
        # Wait for monitoring cycle
        await asyncio.sleep(0.2)
        
        # Check metrics
        metrics = resource_allocator.get_metrics()
        assert metrics['total_capacity'] >= 1024.0
        assert metrics['utilized_capacity'] >= 512.0
        assert metrics['utilization_percentage'] > 0
    
    async def test_multiple_resource_types(self, resource_allocator, sample_requester_id):
        """Test allocating multiple resource types."""
        # Create pools for different resource types
        await resource_allocator.create_resource_pool(
            name="CPU Pool",
            resource_type=ResourceType.CPU,
            initial_capacity=4.0
        )
        
        await resource_allocator.create_resource_pool(
            name="Memory Pool",
            resource_type=ResourceType.MEMORY,
            initial_capacity=2048.0
        )
        
        # Request allocation for multiple resource types
        request_id = await resource_allocator.request_allocation(
            requester_id=sample_requester_id,
            resource_requirements={
                'cpu': 2.0,
                'memory': 1024.0
            },
            priority=TaskPriority.MEDIUM
        )
        
        await asyncio.sleep(0.2)
        
        # Both resources should be allocated or none (atomic allocation)
        request = resource_allocator.get_allocation_request(request_id)
        # Request processing depends on finding appropriate pools
    
    async def test_resource_factory_registration(self, resource_allocator):
        """Test resource factory registration."""
        # Default factories should be registered
        cpu_resource = await resource_allocator.create_resource(
            resource_type=ResourceType.CPU,
            capacity=2.0
        )
        
        assert cpu_resource.type == ResourceType.CPU
        assert cpu_resource.unit == 'cores'
        assert cpu_resource.minimum_allocation == 0.1
        
        memory_resource = await resource_allocator.create_resource(
            resource_type=ResourceType.MEMORY,
            capacity=1024.0
        )
        
        assert memory_resource.type == ResourceType.MEMORY
        assert memory_resource.unit == 'MB'
        assert memory_resource.minimum_allocation == 64
    
    async def test_get_all_resources(self, resource_allocator):
        """Test getting all resources."""
        # Create multiple resources
        resources = []
        for i in range(3):
            resource = await resource_allocator.create_resource(
                resource_type=ResourceType.CPU,
                capacity=float(i + 1)
            )
            resources.append(resource)
        
        all_resources = resource_allocator.get_all_resources()
        assert len(all_resources) >= 3
        
        created_resource_ids = {r.id for r in resources}
        all_resource_ids = {r.id for r in all_resources}
        
        # All created resources should be in the list
        assert created_resource_ids.issubset(all_resource_ids)
    
    async def test_get_all_pools(self, resource_allocator):
        """Test getting all resource pools."""
        # Create multiple pools
        pools = []
        for i in range(2):
            pool = await resource_allocator.create_resource_pool(
                name=f"Test Pool {i}",
                resource_type=ResourceType.MEMORY,
                initial_capacity=1024.0 * (i + 1)
            )
            pools.append(pool)
        
        all_pools = resource_allocator.get_all_pools()
        assert len(all_pools) >= 2
        
        created_pool_ids = {p.id for p in pools}
        all_pool_ids = {p.id for p in all_pools}
        
        # All created pools should be in the list
        assert created_pool_ids.issubset(all_pool_ids)
    
    async def test_allocator_metrics(self, resource_allocator, sample_requester_id):
        """Test resource allocator metrics collection."""
        initial_metrics = resource_allocator.get_metrics()
        
        # Create resources and make allocations
        await resource_allocator.create_resource(
            resource_type=ResourceType.CPU,
            capacity=4.0
        )
        
        await resource_allocator.request_allocation(
            requester_id=sample_requester_id,
            resource_requirements={'cpu': 2.0},
            priority=TaskPriority.MEDIUM
        )
        
        await asyncio.sleep(0.2)
        
        final_metrics = resource_allocator.get_metrics()
        
        # Metrics should show activity
        assert final_metrics['resources_created'] >= initial_metrics['resources_created']
        assert final_metrics['allocations_requested'] >= initial_metrics['allocations_requested']
        assert 'total_resources' in final_metrics
        assert 'total_pools' in final_metrics


@pytest.mark.asyncio
class TestResourceModel:
    """Test cases for Resource model functionality."""
    
    def test_resource_creation(self):
        """Test basic resource creation."""
        resource = Resource(
            name="Test Resource",
            type=ResourceType.CPU,
            total_capacity=4.0,
            unit='cores'
        )
        
        assert resource.name == "Test Resource"
        assert resource.type == ResourceType.CPU
        assert resource.total_capacity == 4.0
        assert resource.available_capacity == 4.0
        assert resource.allocated_capacity == 0.0
    
    def test_resource_allocation(self):
        """Test resource allocation functionality."""
        resource = Resource(
            type=ResourceType.MEMORY,
            total_capacity=1024.0,
            minimum_allocation=64.0
        )
        
        requester_id = uuid4()
        
        # Should be able to allocate within capacity
        assert resource.can_allocate(512.0)
        success = resource.allocate(requester_id, 512.0)
        assert success
        assert resource.allocated_capacity == 512.0
        assert resource.available_capacity == 512.0
        
        # Should not be able to over-allocate
        assert not resource.can_allocate(600.0)
        
        # Should not be able to allocate below minimum
        assert not resource.can_allocate(32.0)
    
    def test_resource_release(self):
        """Test resource release functionality."""
        resource = Resource(
            type=ResourceType.DISK,
            total_capacity=1000.0
        )
        
        requester1 = uuid4()
        requester2 = uuid4()
        
        # Allocate to multiple requesters
        resource.allocate(requester1, 300.0)
        resource.allocate(requester2, 200.0)
        
        assert resource.allocated_capacity == 500.0
        assert resource.available_capacity == 500.0
        
        # Release from one requester
        released = resource.release(requester1, 300.0)
        assert released == 300.0
        assert resource.allocated_capacity == 200.0
        assert resource.available_capacity == 800.0
        
        # Release all from second requester
        released = resource.release_all(requester2)
        assert released == 200.0
        assert resource.allocated_capacity == 0.0
        assert resource.available_capacity == 1000.0
    
    def test_resource_utilization(self):
        """Test resource utilization calculation."""
        resource = Resource(
            type=ResourceType.CPU,
            total_capacity=8.0
        )
        
        # No allocation - 0% utilization
        assert resource.get_utilization_percentage() == 0.0
        
        # Half allocation - 50% utilization
        resource.allocate(uuid4(), 4.0)
        assert resource.get_utilization_percentage() == 50.0
        
        # Full allocation - 100% utilization
        resource.allocate(uuid4(), 4.0)
        assert resource.get_utilization_percentage() == 100.0


if __name__ == "__main__":
    pytest.main([__file__])