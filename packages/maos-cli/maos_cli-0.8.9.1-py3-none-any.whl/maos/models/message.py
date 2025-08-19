"""
Message data model and related enums for MAOS orchestration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any
from uuid import UUID, uuid4


class MessageType(Enum):
    """Message types for inter-component communication."""
    TASK_ASSIGNMENT = "task_assignment"
    TASK_COMPLETION = "task_completion"
    TASK_FAILURE = "task_failure"
    HEARTBEAT = "heartbeat"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"
    RESOURCE_REQUEST = "resource_request"
    RESOURCE_ALLOCATION = "resource_allocation"
    SHUTDOWN_REQUEST = "shutdown_request"
    HEALTH_CHECK = "health_check"
    COORDINATION = "coordination"
    NOTIFICATION = "notification"


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class Message:
    """
    Message model for inter-component communication in the orchestration system.
    
    Attributes:
        id: Unique message identifier
        type: Message type
        priority: Message priority level
        sender_id: ID of component sending the message
        recipient_id: ID of component receiving the message
        subject: Message subject/title
        payload: Message data payload
        metadata: Additional message metadata
        created_at: Message creation timestamp
        sent_at: Message send timestamp
        received_at: Message receive timestamp
        processed_at: Message processing timestamp
        expires_at: Message expiration timestamp
        retry_count: Number of retry attempts
        max_retries: Maximum number of retries allowed
        correlation_id: ID for correlating request/response messages
        reply_to: ID of message this is a reply to
        requires_acknowledgment: Whether message requires ACK
        acknowledged_at: Acknowledgment timestamp
        tags: Message classification tags
        compression_enabled: Whether payload is compressed
        encryption_enabled: Whether payload is encrypted
    """
    
    id: UUID = field(default_factory=uuid4)
    type: MessageType = MessageType.NOTIFICATION
    priority: MessagePriority = MessagePriority.NORMAL
    sender_id: Optional[UUID] = None
    recipient_id: Optional[UUID] = None
    subject: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    correlation_id: Optional[UUID] = None
    reply_to: Optional[UUID] = None
    requires_acknowledgment: bool = False
    acknowledged_at: Optional[datetime] = None
    tags: set = field(default_factory=set)
    compression_enabled: bool = False
    encryption_enabled: bool = False
    
    def __post_init__(self):
        """Post-initialization setup."""
        if not self.subject:
            self.subject = f"{self.type.value.replace('_', ' ').title()}"
        
        # Set default expiration based on priority
        if not self.expires_at:
            from datetime import timedelta
            if self.priority == MessagePriority.CRITICAL:
                self.expires_at = self.created_at + timedelta(minutes=5)
            elif self.priority == MessagePriority.URGENT:
                self.expires_at = self.created_at + timedelta(minutes=15)
            elif self.priority == MessagePriority.HIGH:
                self.expires_at = self.created_at + timedelta(hours=1)
            else:
                self.expires_at = self.created_at + timedelta(hours=24)
    
    def is_expired(self) -> bool:
        """Check if message has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def can_retry(self) -> bool:
        """Check if message can be retried."""
        return self.retry_count < self.max_retries and not self.is_expired()
    
    def mark_sent(self) -> None:
        """Mark message as sent."""
        self.sent_at = datetime.utcnow()
    
    def mark_received(self) -> None:
        """Mark message as received."""
        self.received_at = datetime.utcnow()
    
    def mark_processed(self) -> None:
        """Mark message as processed."""
        self.processed_at = datetime.utcnow()
    
    def acknowledge(self) -> None:
        """Acknowledge message receipt/processing."""
        self.acknowledged_at = datetime.utcnow()
    
    def is_acknowledged(self) -> bool:
        """Check if message has been acknowledged."""
        return self.acknowledged_at is not None
    
    def increment_retry(self) -> bool:
        """Increment retry count and return if retry is allowed."""
        self.retry_count += 1
        return self.can_retry()
    
    def create_reply(self, reply_type: MessageType, reply_payload: Dict[str, Any]) -> 'Message':
        """Create a reply message."""
        return Message(
            type=reply_type,
            priority=self.priority,
            sender_id=self.recipient_id,
            recipient_id=self.sender_id,
            subject=f"Re: {self.subject}",
            payload=reply_payload,
            correlation_id=self.correlation_id or self.id,
            reply_to=self.id
        )
    
    def compress_payload(self) -> None:
        """Compress message payload to reduce size."""
        if not self.compression_enabled and self.payload:
            import gzip
            import json
            
            payload_str = json.dumps(self.payload, default=str)
            compressed_data = gzip.compress(payload_str.encode())
            
            # Store as base64 string
            import base64
            self.payload = {
                '__compressed__': True,
                'data': base64.b64encode(compressed_data).decode()
            }
            
            self.compression_enabled = True
    
    def decompress_payload(self) -> Dict[str, Any]:
        """Decompress and return payload."""
        if not self.compression_enabled:
            return self.payload
        
        if '__compressed__' in self.payload:
            import gzip
            import json
            import base64
            
            compressed_data = base64.b64decode(self.payload['data'])
            decompressed_str = gzip.decompress(compressed_data).decode()
            return json.loads(decompressed_str)
        
        return self.payload
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the message."""
        self.tags.add(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the message."""
        self.tags.discard(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if message has a specific tag."""
        return tag in self.tags
    
    def get_age_seconds(self) -> float:
        """Get message age in seconds."""
        return (datetime.utcnow() - self.created_at).total_seconds()
    
    def get_processing_time_seconds(self) -> Optional[float]:
        """Get message processing time in seconds."""
        if self.received_at and self.processed_at:
            return (self.processed_at - self.received_at).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary representation."""
        return {
            'id': str(self.id),
            'type': self.type.value,
            'priority': self.priority.value,
            'sender_id': str(self.sender_id) if self.sender_id else None,
            'recipient_id': str(self.recipient_id) if self.recipient_id else None,
            'subject': self.subject,
            'payload': self.payload,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'correlation_id': str(self.correlation_id) if self.correlation_id else None,
            'reply_to': str(self.reply_to) if self.reply_to else None,
            'requires_acknowledgment': self.requires_acknowledgment,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'tags': list(self.tags),
            'compression_enabled': self.compression_enabled,
            'encryption_enabled': self.encryption_enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary representation."""
        # Convert string UUIDs back to UUID objects
        uuid_fields = ['id', 'sender_id', 'recipient_id', 'correlation_id', 'reply_to']
        for field in uuid_fields:
            if field in data and data[field]:
                data[field] = UUID(data[field])
        
        # Convert enums
        if 'type' in data:
            data['type'] = MessageType(data['type'])
        if 'priority' in data:
            data['priority'] = MessagePriority(data['priority'])
        
        # Convert datetime strings
        datetime_fields = ['created_at', 'sent_at', 'received_at', 'processed_at', 'expires_at', 'acknowledged_at']
        for field in datetime_fields:
            if field in data and data[field]:
                data[field] = datetime.fromisoformat(data[field])
        
        # Convert tags to set
        if 'tags' in data:
            data['tags'] = set(data['tags'])
        
        return cls(**data)