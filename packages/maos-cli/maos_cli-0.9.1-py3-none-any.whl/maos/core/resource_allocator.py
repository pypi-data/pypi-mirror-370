"""
Resource Allocator component for MAOS orchestration system.

This component is responsible for:
- Dynamic resource allocation based on task requirements
- Queue management and prioritization
- Capacity planning and scaling decisions
- Resource optimization and load balancing
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum

from ..models.resource import Resource, ResourceType, ResourceAllocation
from ..models.task import Task, TaskPriority
from ..models.agent import Agent
from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import (
    ResourceError, ResourceNotFoundError, ResourceAllocationError,
    ResourceExhaustionError, ValidationError
)


class AllocationStrategy(Enum):
    """Resource allocation strategies."""
    FIRST_FIT = "first_fit"
    BEST_FIT = "best_fit"
    WORST_FIT = "worst_fit"
    PRIORITY_BASED = "priority_based"
    LOAD_BALANCED = "load_balanced"


class ScalingPolicy(Enum):
    """Auto-scaling policies."""
    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    SCHEDULED = "scheduled"
    DISABLED = "disabled"


@dataclass
class AllocationRequest:
    """Represents a resource allocation request."""
    
    id: UUID = field(default_factory=uuid4)
    requester_id: UUID = UUID('00000000-0000-0000-0000-000000000000')
    resource_requirements: Dict[str, float] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.MEDIUM
    max_wait_time: int = 300  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    allocated_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization setup."""
        self.expired_at = self.created_at + timedelta(seconds=self.max_wait_time)
    
    def is_expired(self) -> bool:
        """Check if the allocation request has expired."""
        return datetime.utcnow() > self.expired_at
    
    def get_wait_time(self) -> float:
        """Get current wait time in seconds."""
        return (datetime.utcnow() - self.created_at).total_seconds()


@dataclass
class ResourcePool:
    """Represents a pool of resources of the same type."""
    
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    resource_type: ResourceType = ResourceType.CUSTOM
    resources: Dict[UUID, Resource] = field(default_factory=dict)
    total_capacity: float = 0.0
    available_capacity: float = 0.0
    allocated_capacity: float = 0.0
    reserved_capacity: float = 0.0
    allocation_strategy: AllocationStrategy = AllocationStrategy.BEST_FIT
    auto_scaling_enabled: bool = True
    min_capacity: float = 0.0
    max_capacity: float = float('inf')
    scale_up_threshold: float = 0.8  # 80%
    scale_down_threshold: float = 0.3  # 30%
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_capacity_stats(self) -> None:
        """Update capacity statistics based on current resources."""
        self.total_capacity = sum(resource.total_capacity for resource in self.resources.values())
        self.available_capacity = sum(resource.available_capacity for resource in self.resources.values())
        self.allocated_capacity = sum(resource.allocated_capacity for resource in self.resources.values())
        self.reserved_capacity = sum(resource.reserved_capacity for resource in self.resources.values())
    
    def get_utilization_percentage(self) -> float:
        """Get pool utilization percentage."""
        if self.total_capacity == 0:
            return 0.0
        return (self.allocated_capacity / self.total_capacity) * 100
    
    def needs_scaling_up(self) -> bool:
        """Check if pool needs to scale up."""
        if not self.auto_scaling_enabled:
            return False
        utilization = self.get_utilization_percentage() / 100
        return utilization > self.scale_up_threshold and self.total_capacity < self.max_capacity
    
    def needs_scaling_down(self) -> bool:
        """Check if pool needs to scale down."""
        if not self.auto_scaling_enabled:
            return False
        utilization = self.get_utilization_percentage() / 100
        return utilization < self.scale_down_threshold and self.total_capacity > self.min_capacity


class ResourceAllocator:
    """
    Resource Allocator component for managing system resources.
    
    This component handles:
    - Dynamic resource allocation and deallocation
    - Resource pool management and scaling
    - Queue management for allocation requests
    - Capacity planning and optimization
    - Load balancing across resources
    """
    
    def __init__(
        self,
        default_allocation_strategy: AllocationStrategy = AllocationStrategy.BEST_FIT,
        auto_scaling_enabled: bool = True,
        capacity_monitoring_interval: int = 60,
        queue_processing_interval: int = 5,
        max_queue_size: int = 1000
    ):
        """Initialize the Resource Allocator."""
        self.default_allocation_strategy = default_allocation_strategy
        self.auto_scaling_enabled = auto_scaling_enabled
        self.capacity_monitoring_interval = capacity_monitoring_interval
        self.queue_processing_interval = queue_processing_interval
        self.max_queue_size = max_queue_size
        
        self.logger = MAOSLogger("resource_allocator", str(uuid4()))
        
        # Internal state
        self._resources: Dict[UUID, Resource] = {}
        self._resource_pools: Dict[UUID, ResourcePool] = {}
        self._allocation_queue: deque[AllocationRequest] = deque()
        self._pending_allocations: Dict[UUID, AllocationRequest] = {}
        
        # Background tasks
        self._capacity_monitor_task: Optional[asyncio.Task] = None
        self._queue_processor_task: Optional[asyncio.Task] = None
        self._scaling_task: Optional[asyncio.Task] = None
        
        # Metrics
        self._metrics = {
            'allocations_requested': 0,
            'allocations_completed': 0,
            'allocations_failed': 0,
            'resources_created': 0,
            'resources_destroyed': 0,
            'scaling_events': 0,
            'average_allocation_time_ms': 0.0,
            'queue_length': 0,
            'total_capacity': 0.0,
            'utilized_capacity': 0.0,
            'utilization_percentage': 0.0
        }
        
        # Allocation strategies
        self._allocation_strategies: Dict[AllocationStrategy, callable] = {
            AllocationStrategy.FIRST_FIT: self._allocate_first_fit,
            AllocationStrategy.BEST_FIT: self._allocate_best_fit,
            AllocationStrategy.WORST_FIT: self._allocate_worst_fit,
            AllocationStrategy.PRIORITY_BASED: self._allocate_priority_based,
            AllocationStrategy.LOAD_BALANCED: self._allocate_load_balanced
        }
        
        # Resource factory functions
        self._resource_factories: Dict[ResourceType, callable] = {}
        self._register_default_factories()
    
    async def start(self) -> None:
        """Start the resource allocator and background tasks."""
        self.logger.logger.info("Starting Resource Allocator")
        
        # Start capacity monitoring
        if self.capacity_monitoring_interval > 0:
            self._capacity_monitor_task = asyncio.create_task(self._capacity_monitor_loop())
        
        # Start queue processing
        if self.queue_processing_interval > 0:
            self._queue_processor_task = asyncio.create_task(self._queue_processor_loop())
        
        # Start auto-scaling
        if self.auto_scaling_enabled:
            self._scaling_task = asyncio.create_task(self._auto_scaling_loop())
    
    def _register_default_factories(self) -> None:
        """Register default resource factory functions."""
        
        def create_cpu_resource(capacity: float, **kwargs) -> Resource:
            return Resource(
                name=kwargs.get('name', 'CPU Resource'),
                type=ResourceType.CPU,
                total_capacity=capacity,
                available_capacity=capacity,
                unit='cores',
                minimum_allocation=0.1,
                maximum_allocation=capacity,
                **kwargs
            )
        
        def create_memory_resource(capacity: float, **kwargs) -> Resource:
            return Resource(
                name=kwargs.get('name', 'Memory Resource'),
                type=ResourceType.MEMORY,
                total_capacity=capacity,
                available_capacity=capacity,
                unit='MB',
                minimum_allocation=64,
                maximum_allocation=capacity,
                **kwargs
            )
        
        def create_disk_resource(capacity: float, **kwargs) -> Resource:
            return Resource(
                name=kwargs.get('name', 'Disk Resource'),
                type=ResourceType.DISK,
                total_capacity=capacity,
                available_capacity=capacity,
                unit='MB',
                minimum_allocation=100,
                maximum_allocation=capacity,
                **kwargs
            )
        
        self._resource_factories.update({
            ResourceType.CPU: create_cpu_resource,
            ResourceType.MEMORY: create_memory_resource,
            ResourceType.DISK: create_disk_resource
        })
    
    async def create_resource_pool(
        self,
        name: str,
        resource_type: ResourceType,
        initial_capacity: float,
        allocation_strategy: Optional[AllocationStrategy] = None,
        auto_scaling_config: Optional[Dict[str, Any]] = None
    ) -> ResourcePool:
        """
        Create a new resource pool.
        
        Args:
            name: Pool name
            resource_type: Type of resources in the pool
            initial_capacity: Initial capacity to allocate
            allocation_strategy: Allocation strategy to use
            auto_scaling_config: Auto-scaling configuration
            
        Returns:
            ResourcePool: The created resource pool
        """
        
        try:
            pool = ResourcePool(
                name=name,
                resource_type=resource_type,
                allocation_strategy=allocation_strategy or self.default_allocation_strategy,
                auto_scaling_enabled=self.auto_scaling_enabled
            )
            
            # Apply auto-scaling configuration
            if auto_scaling_config:
                pool.min_capacity = auto_scaling_config.get('min_capacity', 0.0)
                pool.max_capacity = auto_scaling_config.get('max_capacity', float('inf'))
                pool.scale_up_threshold = auto_scaling_config.get('scale_up_threshold', 0.8)
                pool.scale_down_threshold = auto_scaling_config.get('scale_down_threshold', 0.3)
            
            # Create initial resources
            if initial_capacity > 0:
                initial_resource = await self.create_resource(
                    resource_type=resource_type,
                    capacity=initial_capacity,
                    pool_id=pool.id
                )
                pool.resources[initial_resource.id] = initial_resource
            
            pool.update_capacity_stats()
            self._resource_pools[pool.id] = pool
            
            self.logger.logger.info(
                f"Resource pool created: {name}",
                extra={
                    'pool_id': str(pool.id),
                    'resource_type': resource_type.value,
                    'initial_capacity': initial_capacity
                }
            )
            
            return pool
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'create_resource_pool',
                'name': name,
                'resource_type': resource_type.value
            })
            raise ResourceError(
                f"Failed to create resource pool: {str(e)}",
                error_code="POOL_CREATION_FAILED"
            )
    
    async def create_resource(
        self,
        resource_type: ResourceType,
        capacity: float,
        pool_id: Optional[UUID] = None,
        **kwargs
    ) -> Resource:
        """
        Create a new resource.
        
        Args:
            resource_type: Type of resource to create
            capacity: Resource capacity
            pool_id: Pool to add resource to (optional)
            **kwargs: Additional resource configuration
            
        Returns:
            Resource: The created resource
        """
        
        if resource_type not in self._resource_factories:
            raise ValidationError(
                f"No factory registered for resource type: {resource_type}",
                field_name="resource_type",
                field_value=resource_type
            )
        
        try:
            factory = self._resource_factories[resource_type]
            resource = factory(capacity, **kwargs)
            
            self._resources[resource.id] = resource
            
            # Add to pool if specified
            if pool_id and pool_id in self._resource_pools:
                pool = self._resource_pools[pool_id]
                pool.resources[resource.id] = resource
                pool.update_capacity_stats()
            
            self._metrics['resources_created'] += 1
            
            self.logger.logger.info(
                f"Resource created: {resource.name}",
                extra={
                    'resource_id': str(resource.id),
                    'resource_type': resource_type.value,
                    'capacity': capacity,
                    'pool_id': str(pool_id) if pool_id else None
                }
            )
            
            return resource
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'create_resource',
                'resource_type': resource_type.value,
                'capacity': capacity
            })
            raise ResourceError(
                f"Failed to create resource: {str(e)}",
                error_code="RESOURCE_CREATION_FAILED"
            )
    
    async def request_allocation(
        self,
        requester_id: UUID,
        resource_requirements: Dict[str, float],
        priority: TaskPriority = TaskPriority.MEDIUM,
        max_wait_time: int = 300,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """
        Request resource allocation.
        
        Args:
            requester_id: ID of the entity requesting resources
            resource_requirements: Required resources (type -> amount)
            priority: Request priority
            max_wait_time: Maximum time to wait for allocation (seconds)
            metadata: Additional request metadata
            
        Returns:
            UUID: Allocation request ID
        """
        
        if len(self._allocation_queue) >= self.max_queue_size:
            raise ResourceAllocationError(
                "Allocation queue is full",
                error_code="QUEUE_FULL"
            )
        
        try:
            request = AllocationRequest(
                requester_id=requester_id,
                resource_requirements=resource_requirements,
                priority=priority,
                max_wait_time=max_wait_time,
                metadata=metadata or {}
            )
            
            self._allocation_queue.append(request)
            self._pending_allocations[request.id] = request
            
            self._metrics['allocations_requested'] += 1
            self._metrics['queue_length'] = len(self._allocation_queue)
            
            self.logger.logger.info(
                "Resource allocation requested",
                extra={
                    'request_id': str(request.id),
                    'requester_id': str(requester_id),
                    'requirements': resource_requirements,
                    'priority': priority.value,
                    'queue_length': len(self._allocation_queue)
                }
            )
            
            return request.id
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'request_allocation',
                'requester_id': str(requester_id)
            })
            raise
    
    async def _queue_processor_loop(self) -> None:
        """Background task for processing allocation requests."""
        
        while True:
            try:
                await asyncio.sleep(self.queue_processing_interval)
                await self._process_allocation_queue()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'queue_processor_loop'})
    
    async def _process_allocation_queue(self) -> None:
        """Process pending allocation requests."""
        
        if not self._allocation_queue:
            return
        
        processed_requests = []
        failed_requests = []
        
        # Process requests in priority order
        sorted_queue = sorted(
            self._allocation_queue,
            key=lambda req: (req.priority.value, req.created_at),
            reverse=True
        )
        
        for request in sorted_queue:
            try:
                # Check if request has expired
                if request.is_expired():
                    failed_requests.append((request, "Request expired"))
                    continue
                
                # Try to allocate resources
                success = await self._try_allocate_resources(request)
                
                if success:
                    processed_requests.append(request)
                    request.allocated_at = datetime.utcnow()
                    
                    self._metrics['allocations_completed'] += 1
                    
                    self.logger.logger.info(
                        "Resource allocation completed",
                        extra={
                            'request_id': str(request.id),
                            'wait_time': request.get_wait_time()
                        }
                    )
                
            except Exception as e:
                failed_requests.append((request, str(e)))
        
        # Remove processed and failed requests from queue
        for request in processed_requests:
            self._allocation_queue.remove(request)
            if request.id in self._pending_allocations:
                del self._pending_allocations[request.id]
        
        for request, error_msg in failed_requests:
            self._allocation_queue.remove(request)
            if request.id in self._pending_allocations:
                del self._pending_allocations[request.id]
            
            self._metrics['allocations_failed'] += 1
            
            self.logger.logger.warning(
                f"Resource allocation failed: {error_msg}",
                extra={
                    'request_id': str(request.id),
                    'error': error_msg
                }
            )
        
        self._metrics['queue_length'] = len(self._allocation_queue)
    
    async def _try_allocate_resources(self, request: AllocationRequest) -> bool:
        """Try to allocate resources for a request."""
        
        allocations = []
        
        try:
            for resource_type, amount in request.resource_requirements.items():
                # Find suitable resource pool
                pool = self._find_pool_for_resource_type(resource_type)
                if not pool:
                    return False
                
                # Try allocation using pool strategy
                resource = await self._allocate_from_pool(
                    pool,
                    request.requester_id,
                    amount,
                    pool.allocation_strategy
                )
                
                if resource:
                    allocations.append((resource, amount))
                else:
                    # Rollback any successful allocations
                    for allocated_resource, allocated_amount in allocations:
                        allocated_resource.release(request.requester_id, allocated_amount)
                    return False
            
            return True
            
        except Exception as e:
            # Rollback allocations on error
            for resource, amount in allocations:
                resource.release(request.requester_id, amount)
            raise
    
    def _find_pool_for_resource_type(self, resource_type_str: str) -> Optional[ResourcePool]:
        """Find a resource pool that can provide the specified resource type."""
        
        try:
            resource_type = ResourceType(resource_type_str.lower())
        except ValueError:
            return None
        
        # Find pool with matching resource type and available capacity
        for pool in self._resource_pools.values():
            if pool.resource_type == resource_type and pool.available_capacity > 0:
                return pool
        
        return None
    
    async def _allocate_from_pool(
        self,
        pool: ResourcePool,
        requester_id: UUID,
        amount: float,
        strategy: AllocationStrategy
    ) -> Optional[Resource]:
        """Allocate resources from a pool using the specified strategy."""
        
        strategy_func = self._allocation_strategies.get(strategy)
        if not strategy_func:
            strategy_func = self._allocation_strategies[AllocationStrategy.BEST_FIT]
        
        return await strategy_func(pool, requester_id, amount)
    
    async def _allocate_first_fit(
        self,
        pool: ResourcePool,
        requester_id: UUID,
        amount: float
    ) -> Optional[Resource]:
        """First-fit allocation strategy."""
        
        for resource in pool.resources.values():
            if resource.can_allocate(amount):
                if resource.allocate(requester_id, amount):
                    pool.update_capacity_stats()
                    return resource
        
        return None
    
    async def _allocate_best_fit(
        self,
        pool: ResourcePool,
        requester_id: UUID,
        amount: float
    ) -> Optional[Resource]:
        """Best-fit allocation strategy (smallest resource that fits)."""
        
        suitable_resources = [
            resource for resource in pool.resources.values()
            if resource.can_allocate(amount)
        ]
        
        if not suitable_resources:
            return None
        
        # Choose resource with smallest available capacity that fits
        best_resource = min(
            suitable_resources,
            key=lambda r: r.available_capacity
        )
        
        if best_resource.allocate(requester_id, amount):
            pool.update_capacity_stats()
            return best_resource
        
        return None
    
    async def _allocate_worst_fit(
        self,
        pool: ResourcePool,
        requester_id: UUID,
        amount: float
    ) -> Optional[Resource]:
        """Worst-fit allocation strategy (largest resource that fits)."""
        
        suitable_resources = [
            resource for resource in pool.resources.values()
            if resource.can_allocate(amount)
        ]
        
        if not suitable_resources:
            return None
        
        # Choose resource with largest available capacity
        worst_resource = max(
            suitable_resources,
            key=lambda r: r.available_capacity
        )
        
        if worst_resource.allocate(requester_id, amount):
            pool.update_capacity_stats()
            return worst_resource
        
        return None
    
    async def _allocate_priority_based(
        self,
        pool: ResourcePool,
        requester_id: UUID,
        amount: float
    ) -> Optional[Resource]:
        """Priority-based allocation (reserved resources for high priority)."""
        
        # For high priority requests, try reserved capacity first
        suitable_resources = [
            resource for resource in pool.resources.values()
            if resource.can_allocate(amount)
        ]
        
        if not suitable_resources:
            return None
        
        # Prefer resources with lowest utilization
        best_resource = min(
            suitable_resources,
            key=lambda r: r.get_utilization_percentage()
        )
        
        if best_resource.allocate(requester_id, amount):
            pool.update_capacity_stats()
            return best_resource
        
        return None
    
    async def _allocate_load_balanced(
        self,
        pool: ResourcePool,
        requester_id: UUID,
        amount: float
    ) -> Optional[Resource]:
        """Load-balanced allocation strategy."""
        
        suitable_resources = [
            resource for resource in pool.resources.values()
            if resource.can_allocate(amount)
        ]
        
        if not suitable_resources:
            return None
        
        # Choose resource with lowest load (utilization)
        balanced_resource = min(
            suitable_resources,
            key=lambda r: r.get_utilization_percentage()
        )
        
        if balanced_resource.allocate(requester_id, amount):
            pool.update_capacity_stats()
            return balanced_resource
        
        return None
    
    async def release_allocation(
        self,
        requester_id: UUID,
        resource_id: Optional[UUID] = None,
        amount: Optional[float] = None
    ) -> float:
        """
        Release resource allocation for a requester.
        
        Args:
            requester_id: ID of the entity releasing resources
            resource_id: Specific resource to release from (optional)
            amount: Specific amount to release (optional)
            
        Returns:
            float: Total amount released
        """
        
        total_released = 0.0
        
        try:
            if resource_id:
                # Release from specific resource
                resource = self._resources.get(resource_id)
                if resource:
                    released = resource.release(requester_id, amount)
                    total_released += released
                    
                    # Update pool stats
                    for pool in self._resource_pools.values():
                        if resource_id in pool.resources:
                            pool.update_capacity_stats()
                            break
            else:
                # Release from all resources
                for resource in self._resources.values():
                    released = resource.release(requester_id, amount)
                    total_released += released
                
                # Update all pool stats
                for pool in self._resource_pools.values():
                    pool.update_capacity_stats()
            
            if total_released > 0:
                self.logger.logger.info(
                    f"Resources released: {total_released}",
                    extra={
                        'requester_id': str(requester_id),
                        'resource_id': str(resource_id) if resource_id else 'all',
                        'amount_released': total_released
                    }
                )
            
            return total_released
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'release_allocation',
                'requester_id': str(requester_id)
            })
            raise ResourceError(
                f"Failed to release allocation: {str(e)}",
                error_code="RELEASE_FAILED"
            )
    
    async def _capacity_monitor_loop(self) -> None:
        """Background task for monitoring resource capacity."""
        
        while True:
            try:
                await asyncio.sleep(self.capacity_monitoring_interval)
                await self._monitor_capacity()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'capacity_monitor_loop'})
    
    async def _monitor_capacity(self) -> None:
        """Monitor resource capacity and update metrics."""
        
        total_capacity = 0.0
        utilized_capacity = 0.0
        
        for resource in self._resources.values():
            total_capacity += resource.total_capacity
            utilized_capacity += resource.allocated_capacity
            
            # Cleanup released allocations
            resource.cleanup_released_allocations()
        
        # Update metrics
        self._metrics['total_capacity'] = total_capacity
        self._metrics['utilized_capacity'] = utilized_capacity
        self._metrics['utilization_percentage'] = (
            (utilized_capacity / total_capacity * 100) if total_capacity > 0 else 0.0
        )
        
        # Update pool statistics
        for pool in self._resource_pools.values():
            pool.update_capacity_stats()
    
    async def _auto_scaling_loop(self) -> None:
        """Background task for auto-scaling resources."""
        
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self._check_scaling_needs()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'auto_scaling_loop'})
    
    async def _check_scaling_needs(self) -> None:
        """Check if resource pools need scaling."""
        
        for pool in self._resource_pools.values():
            try:
                if pool.needs_scaling_up():
                    await self._scale_up_pool(pool)
                elif pool.needs_scaling_down():
                    await self._scale_down_pool(pool)
                    
            except Exception as e:
                self.logger.log_error(e, {
                    'operation': 'check_scaling',
                    'pool_id': str(pool.id)
                })
    
    async def _scale_up_pool(self, pool: ResourcePool) -> None:
        """Scale up a resource pool."""
        
        # Calculate how much capacity to add
        current_utilization = pool.get_utilization_percentage() / 100
        target_utilization = 0.7  # Target 70% utilization
        
        if current_utilization > target_utilization:
            additional_capacity = pool.total_capacity * 0.5  # Add 50% more capacity
            
            # Create new resource
            new_resource = await self.create_resource(
                resource_type=pool.resource_type,
                capacity=additional_capacity,
                pool_id=pool.id
            )
            
            self._metrics['scaling_events'] += 1
            
            self.logger.logger.info(
                f"Scaled up pool: {pool.name}",
                extra={
                    'pool_id': str(pool.id),
                    'additional_capacity': additional_capacity,
                    'new_resource_id': str(new_resource.id)
                }
            )
    
    async def _scale_down_pool(self, pool: ResourcePool) -> None:
        """Scale down a resource pool."""
        
        # Find resources that are not being used
        unused_resources = [
            resource for resource in pool.resources.values()
            if resource.allocated_capacity == 0 and len(pool.resources) > 1
        ]
        
        if unused_resources:
            # Remove the smallest unused resource
            resource_to_remove = min(unused_resources, key=lambda r: r.total_capacity)
            
            await self._destroy_resource(resource_to_remove.id)
            
            self._metrics['scaling_events'] += 1
            
            self.logger.logger.info(
                f"Scaled down pool: {pool.name}",
                extra={
                    'pool_id': str(pool.id),
                    'removed_resource_id': str(resource_to_remove.id),
                    'capacity_removed': resource_to_remove.total_capacity
                }
            )
    
    async def _destroy_resource(self, resource_id: UUID) -> bool:
        """Destroy a resource and clean up references."""
        
        if resource_id not in self._resources:
            return False
        
        resource = self._resources[resource_id]
        
        try:
            # Ensure no active allocations
            if resource.allocated_capacity > 0:
                return False
            
            # Remove from pools
            for pool in self._resource_pools.values():
                if resource_id in pool.resources:
                    del pool.resources[resource_id]
                    pool.update_capacity_stats()
            
            # Remove from resource registry
            del self._resources[resource_id]
            
            self._metrics['resources_destroyed'] += 1
            
            self.logger.logger.info(
                f"Resource destroyed: {resource.name}",
                extra={
                    'resource_id': str(resource_id),
                    'capacity': resource.total_capacity
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'destroy_resource',
                'resource_id': str(resource_id)
            })
            return False
    
    def get_resource(self, resource_id: UUID) -> Optional[Resource]:
        """Get a resource by ID."""
        return self._resources.get(resource_id)
    
    def get_resource_pool(self, pool_id: UUID) -> Optional[ResourcePool]:
        """Get a resource pool by ID."""
        return self._resource_pools.get(pool_id)
    
    def get_all_resources(self) -> List[Resource]:
        """Get all resources."""
        return list(self._resources.values())
    
    def get_all_pools(self) -> List[ResourcePool]:
        """Get all resource pools."""
        return list(self._resource_pools.values())
    
    def get_allocation_request(self, request_id: UUID) -> Optional[AllocationRequest]:
        """Get an allocation request by ID."""
        return self._pending_allocations.get(request_id)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get resource allocator metrics."""
        metrics = self._metrics.copy()
        metrics.update({
            'total_resources': len(self._resources),
            'total_pools': len(self._resource_pools),
            'pending_requests': len(self._pending_allocations),
            'queue_length': len(self._allocation_queue)
        })
        return metrics
    
    async def shutdown(self) -> None:
        """Shutdown the resource allocator and cleanup resources."""
        
        self.logger.logger.info("Resource allocator shutting down")
        
        # Cancel background tasks
        tasks = [
            self._capacity_monitor_task,
            self._queue_processor_task,
            self._scaling_task
        ]
        
        for task in tasks:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Clear state
        self._resources.clear()
        self._resource_pools.clear()
        self._allocation_queue.clear()
        self._pending_allocations.clear()