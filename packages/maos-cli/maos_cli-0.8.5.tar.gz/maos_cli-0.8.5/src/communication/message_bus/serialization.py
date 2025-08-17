"""Message serialization and deserialization."""

import json
import pickle
import zlib
from typing import Any, Dict, Optional, Protocol
from datetime import datetime
import logging

from .types import Message

logger = logging.getLogger(__name__)


class SerializationProtocol(Protocol):
    """Protocol for message serialization strategies."""
    
    def serialize(self, data: Any) -> bytes:
        """Serialize data to bytes."""
        ...
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to data."""
        ...


class JSONSerializer:
    """JSON-based message serialization."""
    
    def serialize(self, data: Any) -> bytes:
        """Serialize data to JSON bytes."""
        try:
            # Handle datetime objects
            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            json_str = json.dumps(data, default=json_serializer, separators=(',', ':'))
            return json_str.encode('utf-8')
        except Exception as e:
            logger.error(f"JSON serialization failed: {e}")
            raise
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize JSON bytes to data."""
        try:
            json_str = data.decode('utf-8')
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"JSON deserialization failed: {e}")
            raise


class PickleSerializer:
    """Pickle-based message serialization."""
    
    def serialize(self, data: Any) -> bytes:
        """Serialize data to pickle bytes."""
        try:
            return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            logger.error(f"Pickle serialization failed: {e}")
            raise
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize pickle bytes to data."""
        try:
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"Pickle deserialization failed: {e}")
            raise


class CompressedSerializer:
    """Compressed serialization wrapper."""
    
    def __init__(self, base_serializer: SerializationProtocol, compression_level: int = 6):
        self.base_serializer = base_serializer
        self.compression_level = compression_level
    
    def serialize(self, data: Any) -> bytes:
        """Serialize and compress data."""
        try:
            serialized = self.base_serializer.serialize(data)
            return zlib.compress(serialized, self.compression_level)
        except Exception as e:
            logger.error(f"Compressed serialization failed: {e}")
            raise
    
    def deserialize(self, data: bytes) -> Any:
        """Decompress and deserialize data."""
        try:
            decompressed = zlib.decompress(data)
            return self.base_serializer.deserialize(decompressed)
        except Exception as e:
            logger.error(f"Compressed deserialization failed: {e}")
            raise


class MessageSerializer:
    """High-level message serializer with multiple strategies."""
    
    def __init__(self, strategy: str = "json", enable_compression: bool = False):
        self.strategy = strategy
        self.enable_compression = enable_compression
        
        # Initialize base serializer
        if strategy == "json":
            base_serializer = JSONSerializer()
        elif strategy == "pickle":
            base_serializer = PickleSerializer()
        else:
            raise ValueError(f"Unsupported serialization strategy: {strategy}")
        
        # Wrap with compression if enabled
        if enable_compression:
            self.serializer = CompressedSerializer(base_serializer)
        else:
            self.serializer = base_serializer
    
    def serialize_message(self, message: Message) -> bytes:
        """Serialize a Message object."""
        try:
            message_dict = message.to_dict()
            return self.serializer.serialize(message_dict)
        except Exception as e:
            logger.error(f"Message serialization failed: {e}")
            raise
    
    def deserialize_message(self, data: bytes) -> Message:
        """Deserialize bytes to a Message object."""
        try:
            message_dict = self.serializer.deserialize(data)
            return Message.from_dict(message_dict)
        except Exception as e:
            logger.error(f"Message deserialization failed: {e}")
            raise
    
    def serialize_payload(self, payload: Any) -> bytes:
        """Serialize arbitrary payload data."""
        return self.serializer.serialize(payload)
    
    def deserialize_payload(self, data: bytes) -> Any:
        """Deserialize payload data."""
        return self.serializer.deserialize(data)
    
    def get_serialized_size(self, data: Any) -> int:
        """Get size of serialized data in bytes."""
        try:
            serialized = self.serializer.serialize(data)
            return len(serialized)
        except Exception:
            return -1
    
    def validate_serialization(self, data: Any) -> bool:
        """Validate that data can be serialized and deserialized correctly."""
        try:
            serialized = self.serializer.serialize(data)
            deserialized = self.serializer.deserialize(serialized)
            return data == deserialized
        except Exception:
            return False


# Default serializer instances
json_serializer = MessageSerializer("json", enable_compression=False)
compressed_json_serializer = MessageSerializer("json", enable_compression=True)
pickle_serializer = MessageSerializer("pickle", enable_compression=False)
compressed_pickle_serializer = MessageSerializer("pickle", enable_compression=True)