"""
Type definitions for Redis-based shared state management system.
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic, Callable
from uuid import UUID, uuid4
from dataclasses import dataclass, field
import json

T = TypeVar('T')


class StateOperationType(Enum):
    """Types of state operations."""
    SET = "set"
    GET = "get"
    DELETE = "delete"
    UPDATE = "update"
    ATOMIC_UPDATE = "atomic_update"
    BATCH = "batch"
    TRANSACTION = "transaction"


class ConflictResolutionStrategy(Enum):
    """Strategies for conflict resolution."""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MERGE = "merge"
    REJECT = "reject"
    CUSTOM = "custom"


class MemoryPartitionType(Enum):
    """Types of memory partitions."""
    AGENT_DEDICATED = "agent_dedicated"
    SHARED_POOL = "shared_pool"
    TEMPORARY = "temporary"
    PERSISTENT = "persistent"


class StateChangeType(Enum):
    """Types of state changes."""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    CONFLICTED = "conflicted"
    RESOLVED = "resolved"


@dataclass
class StateKey:
    """Represents a key in the distributed state system."""
    namespace: str
    category: str
    identifier: str
    partition: Optional[str] = None
    
    def __str__(self) -> str:
        parts = [self.namespace, self.category, self.identifier]
        if self.partition:
            parts.append(self.partition)
        return ":".join(parts)
    
    def __hash__(self) -> int:
        return hash(str(self))
    
    @classmethod
    def from_string(cls, key_str: str) -> 'StateKey':
        """Create StateKey from string representation."""
        parts = key_str.split(':')
        if len(parts) < 3:
            raise ValueError(f"Invalid key format: {key_str}")
        
        return cls(
            namespace=parts[0],
            category=parts[1],
            identifier=parts[2],
            partition=parts[3] if len(parts) > 3 else None
        )


@dataclass
class StateValue:
    """Represents a value in the distributed state system."""
    data: Any
    version: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'data': self.data,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateValue':
        """Create StateValue from dictionary."""
        return cls(
            data=data['data'],
            version=data.get('version', 1),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.utcnow().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.utcnow().isoformat())),
            metadata=data.get('metadata', {})
        )


@dataclass
class VersionedState(Generic[T]):
    """Represents versioned state with conflict detection."""
    key: StateKey
    value: StateValue
    checksum: str
    lock_token: Optional[str] = None
    
    def calculate_checksum(self) -> str:
        """Calculate checksum for integrity verification."""
        import hashlib
        data_str = json.dumps(self.value.to_dict(), sort_keys=True, default=str)
        self.checksum = hashlib.sha256(data_str.encode()).hexdigest()
        return self.checksum
    
    def verify_integrity(self) -> bool:
        """Verify state integrity using checksum."""
        if not self.checksum:
            return True
        current_checksum = self.calculate_checksum()
        return current_checksum == self.checksum


@dataclass
class LockToken:
    """Represents an optimistic lock token."""
    token: str = field(default_factory=lambda: str(uuid4()))
    key: StateKey = None
    acquired_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = None
    agent_id: Optional[UUID] = None
    operation_type: StateOperationType = StateOperationType.UPDATE
    
    def is_expired(self) -> bool:
        """Check if lock token has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def extend_expiry(self, seconds: int) -> None:
        """Extend lock expiry time."""
        from datetime import timedelta
        if self.expires_at:
            self.expires_at += timedelta(seconds=seconds)
        else:
            self.expires_at = datetime.utcnow() + timedelta(seconds=seconds)


@dataclass
class ConflictResolution:
    """Represents a conflict resolution result."""
    strategy: ConflictResolutionStrategy
    winning_value: StateValue
    conflicted_values: List[StateValue]
    resolution_metadata: Dict[str, Any] = field(default_factory=dict)
    resolved_at: datetime = field(default_factory=datetime.utcnow)
    resolver_id: Optional[str] = None


@dataclass
class MemoryPartition:
    """Represents a memory partition in the pool."""
    id: UUID = field(default_factory=uuid4)
    type: MemoryPartitionType = MemoryPartitionType.SHARED_POOL
    size_bytes: int = 0
    allocated_bytes: int = 0
    agent_id: Optional[UUID] = None
    namespace: str = "default"
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def available_bytes(self) -> int:
        """Get available bytes in partition."""
        return self.size_bytes - self.allocated_bytes
    
    @property
    def utilization_percentage(self) -> float:
        """Get utilization percentage."""
        if self.size_bytes == 0:
            return 0.0
        return (self.allocated_bytes / self.size_bytes) * 100
    
    def can_allocate(self, bytes_needed: int) -> bool:
        """Check if partition can allocate requested bytes."""
        return self.available_bytes >= bytes_needed


@dataclass
class StateChange:
    """Represents a change in state."""
    id: UUID = field(default_factory=uuid4)
    key: StateKey = None
    change_type: StateChangeType = StateChangeType.UPDATED
    old_value: Optional[StateValue] = None
    new_value: Optional[StateValue] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    agent_id: Optional[UUID] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': str(self.id),
            'key': str(self.key) if self.key else None,
            'change_type': self.change_type.value,
            'old_value': self.old_value.to_dict() if self.old_value else None,
            'new_value': self.new_value.to_dict() if self.new_value else None,
            'timestamp': self.timestamp.isoformat(),
            'agent_id': str(self.agent_id) if self.agent_id else None,
            'metadata': self.metadata
        }


@dataclass
class BulkOperation:
    """Represents a bulk operation on multiple state keys."""
    id: UUID = field(default_factory=uuid4)
    operation_type: StateOperationType = StateOperationType.BATCH
    operations: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed
    results: List[Any] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_operation(self, operation_type: str, key: StateKey, value: Any = None) -> None:
        """Add an operation to the bulk operation."""
        self.operations.append({
            'type': operation_type,
            'key': str(key),
            'value': value
        })
    
    def mark_completed(self) -> None:
        """Mark bulk operation as completed."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
    
    def mark_failed(self, error: str) -> None:
        """Mark bulk operation as failed."""
        self.status = "failed"
        self.completed_at = datetime.utcnow()
        self.errors.append(error)


@dataclass
class BackupMetadata:
    """Represents metadata for state backup."""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    size_bytes: int = 0
    key_count: int = 0
    namespaces: List[str] = field(default_factory=list)
    checksum: str = ""
    compression_type: str = "gzip"
    encryption_enabled: bool = False
    storage_location: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': str(self.id),
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'size_bytes': self.size_bytes,
            'key_count': self.key_count,
            'namespaces': self.namespaces,
            'checksum': self.checksum,
            'compression_type': self.compression_type,
            'encryption_enabled': self.encryption_enabled,
            'storage_location': self.storage_location,
            'metadata': self.metadata
        }


@dataclass 
class StateWatcher:
    """Represents a state watcher for notifications."""
    id: UUID = field(default_factory=uuid4)
    key_pattern: str = ""
    callback: Optional[Callable] = None
    agent_id: Optional[UUID] = None
    change_types: List[StateChangeType] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def matches_key(self, key: StateKey) -> bool:
        """Check if watcher matches the given key."""
        import re
        pattern = self.key_pattern.replace('*', '.*')
        return bool(re.match(pattern, str(key)))
    
    def matches_change_type(self, change_type: StateChangeType) -> bool:
        """Check if watcher matches the change type."""
        if not self.change_types:
            return True
        return change_type in self.change_types


# Type aliases for commonly used types
StateDict = Dict[StateKey, StateValue]
OperationCallback = Callable[[StateKey, StateValue], None]
ConflictResolver = Callable[[List[StateValue]], StateValue]
StateValidator = Callable[[StateKey, StateValue], bool]