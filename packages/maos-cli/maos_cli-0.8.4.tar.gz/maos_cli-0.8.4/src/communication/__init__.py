"""
MAOS Inter-Agent Communication Layer

This module provides the communication infrastructure for Multi-Agent Operating System (MAOS),
enabling secure, reliable, and high-performance coordination between agents.

Components:
- Message Bus: Redis-based pub/sub messaging system
- Event Dispatcher: Event routing and subscription management  
- Consensus Manager: Voting mechanisms and conflict resolution
- Communication Protocols: Message standards and agent discovery
- Security Layer: Encryption and authentication
"""

from .message_bus import MessageBus, MessagePriority, DeliveryGuarantee
from .event_dispatcher import EventDispatcher, EventSubscription
from .consensus import ConsensusManager, VotingMechanism
from .protocols import MessageFormat, AgentRegistry, HealthMonitor
from .security import CommunicationSecurity, EncryptionManager

__version__ = "1.0.0"
__all__ = [
    "MessageBus",
    "MessagePriority", 
    "DeliveryGuarantee",
    "EventDispatcher",
    "EventSubscription",
    "ConsensusManager",
    "VotingMechanism",
    "MessageFormat",
    "AgentRegistry",
    "HealthMonitor",
    "CommunicationSecurity",
    "EncryptionManager"
]