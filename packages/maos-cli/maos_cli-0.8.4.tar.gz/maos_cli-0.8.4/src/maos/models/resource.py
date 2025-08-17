"""
Resource data model and related enums for MAOS orchestration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4


class ResourceType(Enum):
    """Types of resources that can be managed."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    CUSTOM = "custom"


@dataclass
class ResourceAllocation:
    """Resource allocation record."""
    agent_id: UUID
    amount: float
    allocated_at: datetime = field(default_factory=datetime.utcnow)
    released_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_active(self) -> bool:
        """Check if allocation is currently active."""
        return self.released_at is None
    
    def release(self) -> None:
        """Release the resource allocation."""
        self.released_at = datetime.utcnow()


@dataclass
class Resource:
    """
    Resource model representing system resources in the orchestration system.
    
    Attributes:
        id: Unique resource identifier
        name: Human-readable resource name
        type: Type of resource
        total_capacity: Total available capacity
        available_capacity: Currently available capacity
        allocated_capacity: Currently allocated capacity
        reserved_capacity: Reserved capacity for critical tasks
        unit: Unit of measurement (e.g., 'cores', 'MB', 'GB/s')
        metadata: Additional resource metadata
        created_at: Resource creation timestamp
        updated_at: Last update timestamp
        allocations: List of active allocations
        tags: Resource classification tags
        location: Physical or logical location of resource
        health_status: Current health status
        performance_metrics: Performance metrics
        cost_per_unit: Cost per unit of resource
        minimum_allocation: Minimum allocation size
        maximum_allocation: Maximum allocation size per request
    """
    
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    type: ResourceType = ResourceType.CUSTOM
    total_capacity: float = 0.0
    available_capacity: float = 0.0
    allocated_capacity: float = 0.0
    reserved_capacity: float = 0.0
    unit: str = "units"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    allocations: List[ResourceAllocation] = field(default_factory=list)
    tags: set = field(default_factory=set)
    location: str = "local"
    health_status: str = "healthy"
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    cost_per_unit: float = 0.0
    minimum_allocation: float = 0.0
    maximum_allocation: float = 0.0
    
    def __post_init__(self):
        """Post-initialization setup."""
        if not self.name:
            self.name = f"Resource-{self.type.value}-{str(self.id)[:8]}"
        
        if self.maximum_allocation == 0.0:
            self.maximum_allocation = self.total_capacity
        
        # Initialize available capacity if not set
        if self.available_capacity == 0.0:
            self.available_capacity = self.total_capacity - self.reserved_capacity
    
    def can_allocate(self, amount: float) -> bool:
        """Check if resource can allocate the requested amount."""
        return (
            amount >= self.minimum_allocation and
            amount <= self.maximum_allocation and
            amount <= self.available_capacity and
            self.health_status == "healthy"
        )
    
    def allocate(self, agent_id: UUID, amount: float, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Allocate resource to an agent."""
        if not self.can_allocate(amount):
            return False
        
        allocation = ResourceAllocation(
            agent_id=agent_id,
            amount=amount,
            metadata=metadata or {}
        )
        
        self.allocations.append(allocation)
        self.allocated_capacity += amount
        self.available_capacity -= amount
        self.updated_at = datetime.utcnow()
        
        return True
    
    def release(self, agent_id: UUID, amount: Optional[float] = None) -> float:
        """Release resource allocation for an agent."""
        released_amount = 0.0
        
        for allocation in self.allocations:
            if allocation.agent_id == agent_id and allocation.is_active():
                if amount is None or allocation.amount == amount:
                    allocation.release()
                    released_amount += allocation.amount
                    self.allocated_capacity -= allocation.amount
                    self.available_capacity += allocation.amount
                    
                    if amount is not None:
                        break
        
        if released_amount > 0:
            self.updated_at = datetime.utcnow()
        
        return released_amount
    
    def release_all(self, agent_id: UUID) -> float:
        """Release all resource allocations for an agent."""
        return self.release(agent_id)
    
    def get_allocation_for_agent(self, agent_id: UUID) -> float:
        """Get total allocated amount for a specific agent."""
        return sum(
            allocation.amount 
            for allocation in self.allocations 
            if allocation.agent_id == agent_id and allocation.is_active()
        )
    
    def cleanup_released_allocations(self) -> int:
        """Remove released allocations and return count removed."""
        active_allocations = [
            allocation for allocation in self.allocations 
            if allocation.is_active()
        ]
        
        removed_count = len(self.allocations) - len(active_allocations)
        self.allocations = active_allocations
        
        if removed_count > 0:
            self.updated_at = datetime.utcnow()
        
        return removed_count
    
    def get_utilization_percentage(self) -> float:
        """Get resource utilization as a percentage."""
        if self.total_capacity == 0:
            return 0.0
        return (self.allocated_capacity / self.total_capacity) * 100
    
    def get_availability_percentage(self) -> float:
        """Get resource availability as a percentage."""
        if self.total_capacity == 0:
            return 0.0
        return (self.available_capacity / self.total_capacity) * 100
    
    def update_performance_metric(self, metric_name: str, value: float) -> None:
        """Update a performance metric."""
        self.performance_metrics[metric_name] = value
        self.updated_at = datetime.utcnow()
    
    def get_performance_metric(self, metric_name: str, default: float = 0.0) -> float:
        """Get a performance metric value."""
        return self.performance_metrics.get(metric_name, default)
    
    def set_health_status(self, status: str) -> None:
        """Update resource health status."""
        if self.health_status != status:
            self.health_status = status
            self.updated_at = datetime.utcnow()
    
    def is_healthy(self) -> bool:
        """Check if resource is healthy."""
        return self.health_status == "healthy"
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the resource."""
        self.tags.add(tag)
        self.updated_at = datetime.utcnow()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the resource."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()
    
    def has_tag(self, tag: str) -> bool:
        """Check if resource has a specific tag."""
        return tag in self.tags
    
    def calculate_cost(self, amount: float, duration_hours: float) -> float:
        """Calculate cost for using a specific amount of resource for duration."""
        return amount * duration_hours * self.cost_per_unit
    
    def get_active_agents(self) -> List[UUID]:
        """Get list of agents currently using this resource."""
        return list(set(
            allocation.agent_id 
            for allocation in self.allocations 
            if allocation.is_active()
        ))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary representation."""
        return {
            'id': str(self.id),
            'name': self.name,
            'type': self.type.value,
            'total_capacity': self.total_capacity,
            'available_capacity': self.available_capacity,
            'allocated_capacity': self.allocated_capacity,
            'reserved_capacity': self.reserved_capacity,
            'unit': self.unit,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'allocations': [
                {
                    'agent_id': str(alloc.agent_id),
                    'amount': alloc.amount,
                    'allocated_at': alloc.allocated_at.isoformat(),
                    'released_at': alloc.released_at.isoformat() if alloc.released_at else None,
                    'metadata': alloc.metadata
                } for alloc in self.allocations
            ],
            'tags': list(self.tags),
            'location': self.location,
            'health_status': self.health_status,
            'performance_metrics': self.performance_metrics,
            'cost_per_unit': self.cost_per_unit,
            'minimum_allocation': self.minimum_allocation,
            'maximum_allocation': self.maximum_allocation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Resource':
        """Create resource from dictionary representation."""
        # Convert string UUIDs back to UUID objects
        if 'id' in data:
            data['id'] = UUID(data['id'])
        
        # Convert type enum
        if 'type' in data:
            data['type'] = ResourceType(data['type'])
        
        # Convert datetime strings
        for field_name in ['created_at', 'updated_at']:
            if field_name in data:
                data[field_name] = datetime.fromisoformat(data[field_name])
        
        # Convert allocations
        if 'allocations' in data:
            allocations = []
            for alloc_data in data['allocations']:
                allocation = ResourceAllocation(
                    agent_id=UUID(alloc_data['agent_id']),
                    amount=alloc_data['amount'],
                    allocated_at=datetime.fromisoformat(alloc_data['allocated_at']),
                    released_at=datetime.fromisoformat(alloc_data['released_at']) if alloc_data['released_at'] else None,
                    metadata=alloc_data['metadata']
                )
                allocations.append(allocation)
            data['allocations'] = allocations
        
        # Convert tags to set
        if 'tags' in data:
            data['tags'] = set(data['tags'])
        
        return cls(**data)