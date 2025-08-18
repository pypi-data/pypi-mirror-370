"""Standard message formats and protocol definitions."""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
import uuid

logger = logging.getLogger(__name__)


class ProtocolVersion(Enum):
    """Supported protocol versions."""
    V1_0 = "1.0"
    V1_1 = "1.1" 
    V2_0 = "2.0"


class MessageFormat:
    """Standard message format definitions and validation."""
    
    # Current protocol version
    CURRENT_VERSION = ProtocolVersion.V2_0
    
    # Message type definitions
    MESSAGE_TYPES = {
        "command": "Command to be executed by recipient",
        "query": "Request for information", 
        "response": "Response to a query or command",
        "event": "Notification of something that happened",
        "heartbeat": "Keep-alive signal",
        "registration": "Agent registration message",
        "discovery": "Service discovery message",
        "consensus": "Consensus-related message",
        "error": "Error notification"
    }
    
    # Required fields for all messages
    REQUIRED_FIELDS = [
        "id", "version", "type", "sender", "timestamp"
    ]
    
    # Field type definitions
    FIELD_TYPES = {
        "id": str,
        "version": str, 
        "type": str,
        "sender": str,
        "recipient": (str, type(None)),
        "topic": str,
        "payload": dict,
        "timestamp": str,
        "expires_at": (str, type(None)),
        "correlation_id": (str, type(None)),
        "reply_to": (str, type(None)),
        "headers": dict,
        "priority": int,
        "retry_count": int,
        "max_retries": int
    }
    
    @classmethod
    def create_message(
        cls,
        message_type: str,
        sender: str,
        payload: Optional[Dict[str, Any]] = None,
        recipient: Optional[str] = None,
        topic: str = "",
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        priority: int = 1,
        expires_in_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a standard message."""
        try:
            # Validate message type
            if message_type not in cls.MESSAGE_TYPES:
                raise ValueError(f"Invalid message type: {message_type}")
            
            # Create base message
            message = {
                "id": str(uuid.uuid4()),
                "version": cls.CURRENT_VERSION.value,
                "type": message_type,
                "sender": sender,
                "timestamp": datetime.utcnow().isoformat(),
                "payload": payload or {},
                "headers": headers or {},
                "priority": priority,
                "retry_count": 0,
                "max_retries": 3
            }
            
            # Add optional fields
            if recipient:
                message["recipient"] = recipient
            if topic:
                message["topic"] = topic
            if correlation_id:
                message["correlation_id"] = correlation_id
            if reply_to:
                message["reply_to"] = reply_to
            
            # Set expiration
            if expires_in_seconds:
                expires_at = datetime.utcnow().timestamp() + expires_in_seconds
                message["expires_at"] = datetime.fromtimestamp(expires_at).isoformat()
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to create message: {e}")
            raise
    
    @classmethod
    def validate_message(cls, message: Dict[str, Any]) -> bool:
        """Validate message format and structure."""
        try:
            # Check required fields
            for field in cls.REQUIRED_FIELDS:
                if field not in message:
                    logger.warning(f"Missing required field: {field}")
                    return False
            
            # Validate field types
            for field, value in message.items():
                if field in cls.FIELD_TYPES:
                    expected_type = cls.FIELD_TYPES[field]
                    
                    # Handle union types (e.g., str or None)
                    if isinstance(expected_type, tuple):
                        if not any(isinstance(value, t) for t in expected_type):
                            logger.warning(f"Invalid type for field {field}: expected {expected_type}, got {type(value)}")
                            return False
                    else:
                        if not isinstance(value, expected_type):
                            logger.warning(f"Invalid type for field {field}: expected {expected_type}, got {type(value)}")
                            return False
            
            # Validate message type
            if message["type"] not in cls.MESSAGE_TYPES:
                logger.warning(f"Invalid message type: {message['type']}")
                return False
            
            # Validate protocol version
            try:
                ProtocolVersion(message["version"])
            except ValueError:
                logger.warning(f"Unsupported protocol version: {message['version']}")
                return False
            
            # Validate timestamp format
            try:
                datetime.fromisoformat(message["timestamp"])
            except ValueError:
                logger.warning(f"Invalid timestamp format: {message['timestamp']}")
                return False
            
            # Validate expiration if present
            if "expires_at" in message and message["expires_at"]:
                try:
                    datetime.fromisoformat(message["expires_at"])
                except ValueError:
                    logger.warning(f"Invalid expires_at format: {message['expires_at']}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Message validation error: {e}")
            return False
    
    @classmethod
    def create_command(
        cls,
        sender: str,
        command: str,
        parameters: Optional[Dict[str, Any]] = None,
        recipient: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a command message."""
        payload = {
            "command": command,
            "parameters": parameters or {}
        }
        
        return cls.create_message(
            "command", sender, payload, recipient, **kwargs
        )
    
    @classmethod 
    def create_query(
        cls,
        sender: str,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        recipient: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a query message."""
        payload = {
            "query": query,
            "parameters": parameters or {}
        }
        
        return cls.create_message(
            "query", sender, payload, recipient, **kwargs
        )
    
    @classmethod
    def create_response(
        cls,
        sender: str,
        result: Any,
        success: bool = True,
        error: Optional[str] = None,
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a response message."""
        payload = {
            "result": result,
            "success": success
        }
        
        if error:
            payload["error"] = error
        
        return cls.create_message(
            "response", sender, payload,
            correlation_id=correlation_id,
            reply_to=reply_to,
            **kwargs
        )
    
    @classmethod
    def create_event(
        cls,
        sender: str,
        event_type: str,
        event_data: Dict[str, Any],
        topic: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """Create an event message."""
        payload = {
            "event_type": event_type,
            "event_data": event_data
        }
        
        return cls.create_message(
            "event", sender, payload, topic=topic, **kwargs
        )
    
    @classmethod
    def create_heartbeat(
        cls,
        sender: str,
        status: str = "healthy",
        metrics: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a heartbeat message."""
        payload = {
            "status": status,
            "metrics": metrics or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return cls.create_message(
            "heartbeat", sender, payload, topic="heartbeat", **kwargs
        )
    
    @classmethod
    def create_registration(
        cls,
        sender: str,
        agent_info: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Create an agent registration message."""
        payload = {
            "agent_info": agent_info,
            "registration_time": datetime.utcnow().isoformat()
        }
        
        return cls.create_message(
            "registration", sender, payload, topic="registration", **kwargs
        )
    
    @classmethod
    def create_discovery(
        cls,
        sender: str,
        discovery_type: str,  # "announce", "query", "response"
        service_info: Optional[Dict[str, Any]] = None,
        query_criteria: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a service discovery message."""
        payload = {
            "discovery_type": discovery_type
        }
        
        if service_info:
            payload["service_info"] = service_info
        if query_criteria:
            payload["query_criteria"] = query_criteria
        
        return cls.create_message(
            "discovery", sender, payload, topic="discovery", **kwargs
        )
    
    @classmethod
    def create_error(
        cls,
        sender: str,
        error_code: str,
        error_message: str,
        error_details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create an error message."""
        payload = {
            "error_code": error_code,
            "error_message": error_message,
            "error_details": error_details or {},
            "error_timestamp": datetime.utcnow().isoformat()
        }
        
        return cls.create_message(
            "error", sender, payload,
            correlation_id=correlation_id,
            **kwargs
        )
    
    @classmethod
    def is_expired(cls, message: Dict[str, Any]) -> bool:
        """Check if a message has expired."""
        if "expires_at" not in message or not message["expires_at"]:
            return False
        
        try:
            expires_at = datetime.fromisoformat(message["expires_at"])
            return datetime.utcnow() > expires_at
        except ValueError:
            return False
    
    @classmethod
    def get_message_age(cls, message: Dict[str, Any]) -> float:
        """Get message age in seconds."""
        try:
            timestamp = datetime.fromisoformat(message["timestamp"])
            return (datetime.utcnow() - timestamp).total_seconds()
        except (ValueError, KeyError):
            return 0.0
    
    @classmethod
    def serialize_message(cls, message: Dict[str, Any]) -> str:
        """Serialize message to JSON string."""
        try:
            return json.dumps(message, separators=(',', ':'))
        except Exception as e:
            logger.error(f"Failed to serialize message: {e}")
            raise
    
    @classmethod
    def deserialize_message(cls, data: str) -> Dict[str, Any]:
        """Deserialize JSON string to message."""
        try:
            message = json.loads(data)
            
            # Validate deserialized message
            if not cls.validate_message(message):
                raise ValueError("Invalid message format after deserialization")
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to deserialize message: {e}")
            raise
    
    @classmethod
    def upgrade_message(cls, message: Dict[str, Any], target_version: ProtocolVersion) -> Dict[str, Any]:
        """Upgrade message to a newer protocol version."""
        current_version = ProtocolVersion(message.get("version", "1.0"))
        
        if current_version == target_version:
            return message
        
        # Create upgraded message
        upgraded = message.copy()
        upgraded["version"] = target_version.value
        
        # Apply version-specific upgrades
        if current_version == ProtocolVersion.V1_0 and target_version != ProtocolVersion.V1_0:
            # V1.0 -> V1.1/V2.0: Add headers field
            if "headers" not in upgraded:
                upgraded["headers"] = {}
        
        if target_version == ProtocolVersion.V2_0:
            # V1.x -> V2.0: Add retry fields
            if "retry_count" not in upgraded:
                upgraded["retry_count"] = 0
            if "max_retries" not in upgraded:
                upgraded["max_retries"] = 3
        
        return upgraded
    
    @classmethod
    def get_supported_versions(cls) -> List[str]:
        """Get list of supported protocol versions."""
        return [version.value for version in ProtocolVersion]
    
    @classmethod
    def is_version_supported(cls, version: str) -> bool:
        """Check if protocol version is supported."""
        try:
            ProtocolVersion(version)
            return True
        except ValueError:
            return False