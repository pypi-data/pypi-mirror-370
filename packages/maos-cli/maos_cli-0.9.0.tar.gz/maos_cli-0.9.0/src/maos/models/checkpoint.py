"""
Checkpoint data model and related enums for MAOS orchestration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any
from uuid import UUID, uuid4


class CheckpointType(Enum):
    """Checkpoint types for different orchestration states."""
    TASK_STATE = "task_state"
    AGENT_STATE = "agent_state"
    SYSTEM_STATE = "system_state"
    WORKFLOW_STATE = "workflow_state"
    ERROR_STATE = "error_state"
    RECOVERY_POINT = "recovery_point"


@dataclass
class Checkpoint:
    """
    Checkpoint model for state persistence and recovery in the orchestration system.
    
    Attributes:
        id: Unique checkpoint identifier
        type: Type of checkpoint
        name: Human-readable checkpoint name
        description: Detailed checkpoint description
        state_data: Serialized state information
        metadata: Additional checkpoint metadata
        created_at: Checkpoint creation timestamp
        created_by: ID of component that created the checkpoint
        version: Checkpoint version for compatibility
        parent_checkpoint_id: ID of parent checkpoint (for incremental checkpoints)
        tags: Checkpoint classification tags
        retention_policy: How long to retain this checkpoint
        compression_enabled: Whether state data is compressed
        checksum: Data integrity checksum
        size_bytes: Size of checkpoint data in bytes
    """
    
    id: UUID = field(default_factory=uuid4)
    type: CheckpointType = CheckpointType.SYSTEM_STATE
    name: str = ""
    description: str = ""
    state_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[UUID] = None
    version: str = "1.0"
    parent_checkpoint_id: Optional[UUID] = None
    tags: set = field(default_factory=set)
    retention_policy: str = "7d"  # 7 days default
    compression_enabled: bool = False
    checksum: Optional[str] = None
    size_bytes: int = 0
    
    def __post_init__(self):
        """Post-initialization setup."""
        if not self.name:
            self.name = f"Checkpoint-{self.type.value}-{str(self.id)[:8]}"
        
        # Calculate size if state_data is present
        if self.state_data:
            import json
            self.size_bytes = len(json.dumps(self.state_data, default=str).encode('utf-8'))
    
    def is_expired(self) -> bool:
        """Check if checkpoint has expired based on retention policy."""
        if not self.retention_policy:
            return False
        
        now = datetime.utcnow()
        age_seconds = (now - self.created_at).total_seconds()
        
        # Parse retention policy (e.g., "7d", "24h", "60m")
        if self.retention_policy.endswith('d'):
            max_age_seconds = int(self.retention_policy[:-1]) * 24 * 3600
        elif self.retention_policy.endswith('h'):
            max_age_seconds = int(self.retention_policy[:-1]) * 3600
        elif self.retention_policy.endswith('m'):
            max_age_seconds = int(self.retention_policy[:-1]) * 60
        else:
            # Default to seconds
            max_age_seconds = int(self.retention_policy)
        
        return age_seconds > max_age_seconds
    
    def validate_checksum(self) -> bool:
        """Validate checkpoint data integrity using checksum."""
        if not self.checksum:
            return True  # No checksum to validate
        
        import hashlib
        import json
        
        data_str = json.dumps(self.state_data, sort_keys=True, default=str)
        calculated_checksum = hashlib.sha256(data_str.encode()).hexdigest()
        
        return calculated_checksum == self.checksum
    
    def calculate_checksum(self) -> str:
        """Calculate and update checksum for current state data."""
        import hashlib
        import json
        
        data_str = json.dumps(self.state_data, sort_keys=True, default=str)
        self.checksum = hashlib.sha256(data_str.encode()).hexdigest()
        return self.checksum
    
    def compress_state_data(self) -> None:
        """Compress state data to save storage space."""
        if not self.compression_enabled and self.state_data:
            import gzip
            import json
            
            data_str = json.dumps(self.state_data, default=str)
            compressed_data = gzip.compress(data_str.encode())
            
            # Store as base64 string
            import base64
            self.state_data = {
                '__compressed__': True,
                'data': base64.b64encode(compressed_data).decode()
            }
            
            self.compression_enabled = True
            self.size_bytes = len(compressed_data)
    
    def decompress_state_data(self) -> Dict[str, Any]:
        """Decompress and return state data."""
        if not self.compression_enabled:
            return self.state_data
        
        if '__compressed__' in self.state_data:
            import gzip
            import json
            import base64
            
            compressed_data = base64.b64decode(self.state_data['data'])
            decompressed_str = gzip.decompress(compressed_data).decode()
            return json.loads(decompressed_str)
        
        return self.state_data
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the checkpoint."""
        self.tags.add(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the checkpoint."""
        self.tags.discard(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if checkpoint has a specific tag."""
        return tag in self.tags
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert checkpoint to dictionary representation."""
        return {
            'id': str(self.id),
            'type': self.type.value,
            'name': self.name,
            'description': self.description,
            'state_data': self.state_data,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'created_by': str(self.created_by) if self.created_by else None,
            'version': self.version,
            'parent_checkpoint_id': str(self.parent_checkpoint_id) if self.parent_checkpoint_id else None,
            'tags': list(self.tags),
            'retention_policy': self.retention_policy,
            'compression_enabled': self.compression_enabled,
            'checksum': self.checksum,
            'size_bytes': self.size_bytes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Checkpoint':
        """Create checkpoint from dictionary representation."""
        # Convert string UUIDs back to UUID objects
        if 'id' in data:
            data['id'] = UUID(data['id'])
        if 'created_by' in data and data['created_by']:
            data['created_by'] = UUID(data['created_by'])
        if 'parent_checkpoint_id' in data and data['parent_checkpoint_id']:
            data['parent_checkpoint_id'] = UUID(data['parent_checkpoint_id'])
        
        # Convert type enum
        if 'type' in data:
            data['type'] = CheckpointType(data['type'])
        
        # Convert datetime string
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        # Convert tags to set
        if 'tags' in data:
            data['tags'] = set(data['tags'])
        
        return cls(**data)