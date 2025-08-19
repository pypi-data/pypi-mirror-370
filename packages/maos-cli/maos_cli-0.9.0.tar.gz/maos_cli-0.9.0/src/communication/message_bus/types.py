"""Message bus type definitions."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union
import uuid


class MessagePriority(Enum):
    """Message priority levels."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class DeliveryGuarantee(Enum):
    """Message delivery guarantee levels."""
    AT_MOST_ONCE = "at_most_once"  # Fire and forget
    AT_LEAST_ONCE = "at_least_once"  # May duplicate
    EXACTLY_ONCE = "exactly_once"  # No duplicates


class MessageType(Enum):
    """Types of messages in the system."""
    COMMAND = "command"
    EVENT = "event"
    QUERY = "query"
    RESPONSE = "response"
    HEARTBEAT = "heartbeat"
    NOTIFICATION = "notification"


@dataclass
class Message:
    """Core message structure."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.COMMAND
    sender: str = ""
    recipient: Optional[str] = None  # None for broadcast
    topic: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    delivery_guarantee: DeliveryGuarantee = DeliveryGuarantee.AT_LEAST_ONCE
    timestamp: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3

    def is_expired(self) -> bool:
        """Check if message has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "sender": self.sender,
            "recipient": self.recipient,
            "topic": self.topic,
            "payload": self.payload,
            "priority": self.priority.value,
            "delivery_guarantee": self.delivery_guarantee.value,
            "timestamp": self.timestamp.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "correlation_id": self.correlation_id,
            "reply_to": self.reply_to,
            "headers": self.headers,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        message = cls(
            id=data["id"],
            type=MessageType(data["type"]),
            sender=data["sender"],
            recipient=data.get("recipient"),
            topic=data["topic"],
            payload=data.get("payload", {}),
            priority=MessagePriority(data.get("priority", MessagePriority.NORMAL.value)),
            delivery_guarantee=DeliveryGuarantee(data.get("delivery_guarantee", DeliveryGuarantee.AT_LEAST_ONCE.value)),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            correlation_id=data.get("correlation_id"),
            reply_to=data.get("reply_to"),
            headers=data.get("headers", {}),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3)
        )
        return message


@dataclass
class Subscription:
    """Message subscription information."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    topic: str = ""
    callback: Optional[callable] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class DeliveryReceipt:
    """Message delivery receipt."""
    message_id: str
    recipient: str
    status: str  # "delivered", "failed", "pending"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error: Optional[str] = None
    retry_count: int = 0