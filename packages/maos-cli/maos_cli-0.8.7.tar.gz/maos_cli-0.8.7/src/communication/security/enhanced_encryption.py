"""Enhanced end-to-end encryption for inter-agent communication."""

import asyncio
import hashlib
import hmac
import logging
import os
import struct
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, x25519, ed25519
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305, AESGCM
from cryptography.hazmat.primitives import cmac
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class EncryptionProtocol(Enum):
    """Enhanced encryption protocols."""
    # Symmetric protocols
    CHACHA20_POLY1305 = "chacha20_poly1305"
    AES_256_GCM = "aes_256_gcm"
    XChaCha20_Poly1305 = "xchacha20_poly1305"
    
    # Key exchange protocols
    X25519_CHACHA20 = "x25519_chacha20"
    ECDH_AES = "ecdh_aes"
    
    # Forward secrecy protocols
    DOUBLE_RATCHET = "double_ratchet"
    SIGNAL = "signal"


class KeyType(Enum):
    """Cryptographic key types."""
    SYMMETRIC = "symmetric"
    ASYMMETRIC_PRIVATE = "asymmetric_private"
    ASYMMETRIC_PUBLIC = "asymmetric_public"
    EPHEMERAL = "ephemeral"
    ROOT = "root"
    CHAIN = "chain"


@dataclass
class CryptoKey:
    """Cryptographic key with metadata."""
    key_id: str
    key_type: KeyType
    algorithm: str
    key_data: bytes
    public_key: Optional[bytes] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if key is expired."""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at


@dataclass
class SecureMessage:
    """Encrypted message with metadata."""
    message_id: str
    sender_id: str
    recipient_id: str
    protocol: EncryptionProtocol
    encrypted_data: bytes
    authentication_tag: bytes
    nonce: bytes
    ephemeral_key: Optional[bytes] = None
    key_id: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for transmission."""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "protocol": self.protocol.value,
            "encrypted_data": base64.b64encode(self.encrypted_data).decode(),
            "authentication_tag": base64.b64encode(self.authentication_tag).decode(),
            "nonce": base64.b64encode(self.nonce).decode(),
            "ephemeral_key": base64.b64encode(self.ephemeral_key).decode() if self.ephemeral_key else None,
            "key_id": self.key_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecureMessage":
        """Create from dictionary."""
        return cls(
            message_id=data["message_id"],
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            protocol=EncryptionProtocol(data["protocol"]),
            encrypted_data=base64.b64decode(data["encrypted_data"]),
            authentication_tag=base64.b64decode(data["authentication_tag"]),
            nonce=base64.b64decode(data["nonce"]),
            ephemeral_key=base64.b64decode(data["ephemeral_key"]) if data.get("ephemeral_key") else None,
            key_id=data.get("key_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


class SecureChannel:
    """Secure communication channel with forward secrecy."""
    
    def __init__(
        self,
        channel_id: str,
        local_agent_id: str,
        remote_agent_id: str,
        protocol: EncryptionProtocol = EncryptionProtocol.X25519_CHACHA20
    ):
        self.channel_id = channel_id
        self.local_agent_id = local_agent_id
        self.remote_agent_id = remote_agent_id
        self.protocol = protocol
        
        # Key management
        self.root_key: Optional[bytes] = None
        self.sending_chain_key: Optional[bytes] = None
        self.receiving_chain_key: Optional[bytes] = None
        self.ephemeral_keypairs: List[Tuple[bytes, bytes]] = []  # (private, public)
        
        # Message tracking for replay protection
        self.sent_message_numbers: Set[int] = set()
        self.received_message_numbers: Set[int] = set()
        self.current_send_number = 0
        self.current_receive_number = 0
        
        # Channel state
        self.established = False
        self.last_activity = datetime.now(timezone.utc)
        
        logger.debug(f"Created secure channel {channel_id}: {local_agent_id} <-> {remote_agent_id}")
    
    def generate_ephemeral_keypair(self) -> Tuple[bytes, bytes]:
        """Generate ephemeral X25519 keypair."""
        try:
            private_key = x25519.X25519PrivateKey.generate()
            public_key = private_key.public_key()
            
            private_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            
            self.ephemeral_keypairs.append((private_bytes, public_bytes))
            return private_bytes, public_bytes
            
        except Exception as e:
            logger.error(f"Failed to generate ephemeral keypair: {e}")
            raise
    
    def derive_shared_secret(self, our_private: bytes, their_public: bytes) -> bytes:
        """Derive shared secret using X25519."""
        try:
            private_key = x25519.X25519PrivateKey.from_private_bytes(our_private)
            public_key = x25519.X25519PublicKey.from_public_bytes(their_public)
            
            shared_secret = private_key.exchange(public_key)
            return shared_secret
            
        except Exception as e:
            logger.error(f"Failed to derive shared secret: {e}")
            raise
    
    def derive_keys(self, shared_secret: bytes, info: bytes) -> Tuple[bytes, bytes]:
        """Derive encryption and authentication keys from shared secret."""
        try:
            # Use HKDF to derive keys
            hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=64,  # 32 bytes for encryption + 32 bytes for authentication
                salt=None,
                info=info,
                backend=default_backend()
            )
            
            key_material = hkdf.derive(shared_secret)
            encryption_key = key_material[:32]
            authentication_key = key_material[32:64]
            
            return encryption_key, authentication_key
            
        except Exception as e:
            logger.error(f"Failed to derive keys: {e}")
            raise
    
    def advance_chain_key(self, chain_key: bytes) -> Tuple[bytes, bytes]:
        """Advance chain key and derive message key."""
        try:
            # Use HMAC to advance chain key
            new_chain_key = hmac.new(chain_key, b"chain", hashlib.sha256).digest()
            message_key = hmac.new(chain_key, b"message", hashlib.sha256).digest()
            
            return new_chain_key, message_key
            
        except Exception as e:
            logger.error(f"Failed to advance chain key: {e}")
            raise
    
    def establish_channel(self, remote_public_key: bytes) -> bool:
        """Establish secure channel with remote agent."""
        try:
            # Generate our ephemeral keypair
            our_private, our_public = self.generate_ephemeral_keypair()
            
            # Derive shared secret
            shared_secret = self.derive_shared_secret(our_private, remote_public_key)
            
            # Derive root key and initial chain keys
            info = f"{self.local_agent_id}:{self.remote_agent_id}:{self.channel_id}".encode()
            root_key, initial_key = self.derive_keys(shared_secret, info)
            
            self.root_key = root_key
            self.sending_chain_key = initial_key
            self.receiving_chain_key = initial_key
            
            self.established = True
            self.last_activity = datetime.now(timezone.utc)
            
            logger.info(f"Established secure channel {self.channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to establish channel: {e}")
            return False


class EnhancedEncryptionManager:
    """Enhanced encryption manager with forward secrecy and perfect forward secrecy."""
    
    def __init__(
        self,
        agent_id: str,
        default_protocol: EncryptionProtocol = EncryptionProtocol.X25519_CHACHA20
    ):
        self.agent_id = agent_id
        self.default_protocol = default_protocol
        
        # Key storage
        self.keys: Dict[str, CryptoKey] = {}
        self.agent_public_keys: Dict[str, bytes] = {}  # Public keys of other agents
        
        # Secure channels
        self.channels: Dict[str, SecureChannel] = {}
        
        # Identity keys (long-term)
        self.identity_private_key: Optional[bytes] = None
        self.identity_public_key: Optional[bytes] = None
        
        # Prekeys for asynchronous communication
        self.prekeys: Dict[str, Tuple[bytes, bytes]] = {}  # prekey_id -> (private, public)
        self.signed_prekey: Optional[Tuple[bytes, bytes]] = None
        self.signed_prekey_signature: Optional[bytes] = None
        
        # Message tracking
        self.message_cache: Dict[str, SecureMessage] = {}
        self.max_cache_size = 1000
        
        # Performance metrics
        self.metrics = {
            "messages_encrypted": 0,
            "messages_decrypted": 0,
            "key_exchanges": 0,
            "channels_established": 0,
            "encryption_errors": 0
        }
        
        self._generate_identity_keys()
        logger.info(f"Enhanced encryption manager initialized for agent: {agent_id}")
    
    def _generate_identity_keys(self):
        """Generate long-term identity keys."""
        try:
            # Generate Ed25519 signing keys for identity
            signing_key = ed25519.Ed25519PrivateKey.generate()
            verify_key = signing_key.public_key()
            
            self.identity_private_key = signing_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            self.identity_public_key = verify_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            
            # Generate signed prekey
            self._generate_signed_prekey()
            
            # Generate one-time prekeys
            self._generate_prekeys(10)
            
            logger.info("Generated identity keys and prekeys")
            
        except Exception as e:
            logger.error(f"Failed to generate identity keys: {e}")
            raise
    
    def _generate_signed_prekey(self):
        """Generate signed prekey."""
        try:
            # Generate X25519 keypair for prekey
            private_key = x25519.X25519PrivateKey.generate()
            public_key = private_key.public_key()
            
            private_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            
            # Sign the prekey with identity key
            identity_key = ed25519.Ed25519PrivateKey.from_private_bytes(self.identity_private_key)
            signature = identity_key.sign(public_bytes)
            
            self.signed_prekey = (private_bytes, public_bytes)
            self.signed_prekey_signature = signature
            
        except Exception as e:
            logger.error(f"Failed to generate signed prekey: {e}")
            raise
    
    def _generate_prekeys(self, count: int):
        """Generate one-time prekeys."""
        try:
            for i in range(count):
                prekey_id = f"prekey_{i:04d}_{os.urandom(4).hex()}"
                
                private_key = x25519.X25519PrivateKey.generate()
                public_key = private_key.public_key()
                
                private_bytes = private_key.private_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PrivateFormat.Raw,
                    encryption_algorithm=serialization.NoEncryption()
                )
                
                public_bytes = public_key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                )
                
                self.prekeys[prekey_id] = (private_bytes, public_bytes)
            
            logger.debug(f"Generated {count} one-time prekeys")
            
        except Exception as e:
            logger.error(f"Failed to generate prekeys: {e}")
    
    def get_public_key_bundle(self) -> Dict[str, Any]:
        """Get public key bundle for key exchange."""
        try:
            prekey_bundles = {}
            for prekey_id, (private, public) in list(self.prekeys.items())[:5]:  # Return up to 5 prekeys
                prekey_bundles[prekey_id] = base64.b64encode(public).decode()
            
            return {
                "agent_id": self.agent_id,
                "identity_key": base64.b64encode(self.identity_public_key).decode(),
                "signed_prekey": {
                    "public_key": base64.b64encode(self.signed_prekey[1]).decode(),
                    "signature": base64.b64encode(self.signed_prekey_signature).decode()
                },
                "prekeys": prekey_bundles,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get public key bundle: {e}")
            return {}
    
    def import_public_key_bundle(self, bundle: Dict[str, Any]) -> bool:
        """Import public key bundle from remote agent."""
        try:
            agent_id = bundle["agent_id"]
            identity_key = base64.b64decode(bundle["identity_key"])
            
            # Verify signed prekey
            signed_prekey_data = bundle["signed_prekey"]
            signed_prekey_public = base64.b64decode(signed_prekey_data["public_key"])
            signature = base64.b64decode(signed_prekey_data["signature"])
            
            # Verify signature
            verify_key = ed25519.Ed25519PublicKey.from_public_bytes(identity_key)
            verify_key.verify(signature, signed_prekey_public)
            
            # Store public keys
            self.agent_public_keys[agent_id] = {
                "identity_key": identity_key,
                "signed_prekey": signed_prekey_public,
                "prekeys": {
                    pid: base64.b64decode(pkey) 
                    for pid, pkey in bundle.get("prekeys", {}).items()
                }
            }
            
            logger.info(f"Imported public key bundle for agent: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import public key bundle: {e}")
            return False
    
    def establish_secure_channel(
        self,
        remote_agent_id: str,
        use_prekey: bool = True
    ) -> Optional[SecureChannel]:
        """Establish secure channel with remote agent."""
        try:
            channel_id = f"channel_{self.agent_id}_{remote_agent_id}_{os.urandom(8).hex()}"
            
            # Check if we have remote agent's public keys
            if remote_agent_id not in self.agent_public_keys:
                logger.error(f"No public key bundle for agent: {remote_agent_id}")
                return None
            
            # Create secure channel
            channel = SecureChannel(
                channel_id=channel_id,
                local_agent_id=self.agent_id,
                remote_agent_id=remote_agent_id,
                protocol=self.default_protocol
            )
            
            remote_keys = self.agent_public_keys[remote_agent_id]
            
            if use_prekey and remote_keys.get("prekeys"):
                # Use one-time prekey if available
                prekey_id = next(iter(remote_keys["prekeys"]))
                remote_public = remote_keys["prekeys"][prekey_id]
                
                # Remove used prekey
                del remote_keys["prekeys"][prekey_id]
            else:
                # Use signed prekey
                remote_public = remote_keys["signed_prekey"]
            
            # Establish channel
            if channel.establish_channel(remote_public):
                self.channels[channel_id] = channel
                self.metrics["channels_established"] += 1
                self.metrics["key_exchanges"] += 1
                return channel
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to establish secure channel: {e}")
            return None
    
    def encrypt_message(
        self,
        plaintext: str,
        recipient_id: str,
        channel_id: Optional[str] = None,
        additional_data: Optional[bytes] = None
    ) -> Optional[SecureMessage]:
        """Encrypt message for specific recipient."""
        try:
            # Find or create secure channel
            if channel_id and channel_id in self.channels:
                channel = self.channels[channel_id]
            else:
                # Try to find existing channel
                channel = None
                for ch in self.channels.values():
                    if ch.remote_agent_id == recipient_id and ch.established:
                        channel = ch
                        break
                
                # Create new channel if none exists
                if not channel:
                    channel = self.establish_secure_channel(recipient_id)
                    if not channel:
                        logger.error(f"Cannot establish channel with {recipient_id}")
                        return None
            
            # Generate message ID
            message_id = f"msg_{os.urandom(8).hex()}"
            
            # Advance sending chain key and get message key
            new_chain_key, message_key = channel.advance_chain_key(channel.sending_chain_key)
            channel.sending_chain_key = new_chain_key
            
            # Generate nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM
            
            # Encrypt with ChaCha20Poly1305 or AES-GCM
            if channel.protocol == EncryptionProtocol.CHACHA20_POLY1305:
                cipher = ChaCha20Poly1305(message_key)
                encrypted_data = cipher.encrypt(nonce, plaintext.encode(), additional_data)
                # ChaCha20Poly1305 includes auth tag in encrypted_data
                ciphertext = encrypted_data[:-16]
                auth_tag = encrypted_data[-16:]
            else:
                # Default to AES-GCM
                cipher = AESGCM(message_key)
                encrypted_data = cipher.encrypt(nonce, plaintext.encode(), additional_data)
                ciphertext = encrypted_data[:-16]
                auth_tag = encrypted_data[-16:]
            
            # Create secure message
            secure_msg = SecureMessage(
                message_id=message_id,
                sender_id=self.agent_id,
                recipient_id=recipient_id,
                protocol=channel.protocol,
                encrypted_data=ciphertext,
                authentication_tag=auth_tag,
                nonce=nonce,
                key_id=channel.channel_id
            )
            
            # Cache message
            self._cache_message(secure_msg)
            
            # Update metrics
            self.metrics["messages_encrypted"] += 1
            channel.current_send_number += 1
            channel.last_activity = datetime.now(timezone.utc)
            
            return secure_msg
            
        except Exception as e:
            logger.error(f"Failed to encrypt message: {e}")
            self.metrics["encryption_errors"] += 1
            return None
    
    def decrypt_message(self, secure_msg: SecureMessage) -> Optional[str]:
        """Decrypt secure message."""
        try:
            # Find secure channel
            channel = self.channels.get(secure_msg.key_id)
            if not channel:
                logger.error(f"Unknown channel: {secure_msg.key_id}")
                return None
            
            # Check message order and replay protection
            if secure_msg.message_id in channel.received_message_numbers:
                logger.warning(f"Replay attack detected: {secure_msg.message_id}")
                return None
            
            # Advance receiving chain key and get message key
            new_chain_key, message_key = channel.advance_chain_key(channel.receiving_chain_key)
            channel.receiving_chain_key = new_chain_key
            
            # Decrypt message
            if secure_msg.protocol == EncryptionProtocol.CHACHA20_POLY1305:
                cipher = ChaCha20Poly1305(message_key)
                encrypted_data = secure_msg.encrypted_data + secure_msg.authentication_tag
                plaintext_bytes = cipher.decrypt(secure_msg.nonce, encrypted_data, None)
            else:
                # Default to AES-GCM
                cipher = AESGCM(message_key)
                encrypted_data = secure_msg.encrypted_data + secure_msg.authentication_tag
                plaintext_bytes = cipher.decrypt(secure_msg.nonce, encrypted_data, None)
            
            # Record message as received
            channel.received_message_numbers.add(secure_msg.message_id)
            channel.current_receive_number += 1
            channel.last_activity = datetime.now(timezone.utc)
            
            # Update metrics
            self.metrics["messages_decrypted"] += 1
            
            return plaintext_bytes.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Failed to decrypt message: {e}")
            self.metrics["encryption_errors"] += 1
            return None
    
    def _cache_message(self, message: SecureMessage):
        """Cache message for replay protection."""
        try:
            self.message_cache[message.message_id] = message
            
            # Limit cache size
            if len(self.message_cache) > self.max_cache_size:
                # Remove oldest messages
                oldest_messages = sorted(
                    self.message_cache.items(),
                    key=lambda x: x[1].timestamp
                )[:self.max_cache_size // 2]
                
                for msg_id, _ in oldest_messages:
                    del self.message_cache[msg_id]
                    
        except Exception as e:
            logger.error(f"Failed to cache message: {e}")
    
    def rotate_keys(self, agent_id: Optional[str] = None):
        """Rotate ephemeral keys for forward secrecy."""
        try:
            if agent_id:
                # Rotate keys for specific agent
                channels_to_rotate = [ch for ch in self.channels.values() if ch.remote_agent_id == agent_id]
            else:
                # Rotate keys for all channels
                channels_to_rotate = list(self.channels.values())
            
            for channel in channels_to_rotate:
                # Generate new ephemeral keypair
                private, public = channel.generate_ephemeral_keypair()
                
                # Derive new root key (in practice, this would involve communication with remote)
                # For now, we'll just advance the chain keys
                if channel.sending_chain_key:
                    channel.sending_chain_key = hmac.new(
                        channel.sending_chain_key, 
                        b"rotate", 
                        hashlib.sha256
                    ).digest()
                
                if channel.receiving_chain_key:
                    channel.receiving_chain_key = hmac.new(
                        channel.receiving_chain_key, 
                        b"rotate", 
                        hashlib.sha256
                    ).digest()
                
                logger.debug(f"Rotated keys for channel: {channel.channel_id}")
            
            # Generate new one-time prekeys
            self._generate_prekeys(10)
            
        except Exception as e:
            logger.error(f"Failed to rotate keys: {e}")
    
    def cleanup_expired_keys(self) -> int:
        """Remove expired keys and inactive channels."""
        try:
            cleanup_count = 0
            current_time = datetime.now(timezone.utc)
            
            # Remove expired keys
            expired_keys = []
            for key_id, key in self.keys.items():
                if key.is_expired():
                    expired_keys.append(key_id)
            
            for key_id in expired_keys:
                del self.keys[key_id]
                cleanup_count += 1
            
            # Remove inactive channels (older than 24 hours)
            inactive_channels = []
            for channel_id, channel in self.channels.items():
                if current_time - channel.last_activity > timedelta(hours=24):
                    inactive_channels.append(channel_id)
            
            for channel_id in inactive_channels:
                del self.channels[channel_id]
                cleanup_count += 1
            
            # Clean old cached messages
            old_messages = []
            for msg_id, msg in self.message_cache.items():
                if current_time - msg.timestamp > timedelta(hours=1):
                    old_messages.append(msg_id)
            
            for msg_id in old_messages:
                del self.message_cache[msg_id]
                cleanup_count += 1
            
            logger.debug(f"Cleaned up {cleanup_count} expired items")
            return cleanup_count
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get encryption statistics."""
        return {
            "metrics": self.metrics,
            "active_channels": len(self.channels),
            "stored_keys": len(self.keys),
            "agent_public_keys": len(self.agent_public_keys),
            "cached_messages": len(self.message_cache),
            "available_prekeys": len(self.prekeys)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            status = "healthy"
            issues = []
            
            # Check identity keys
            if not self.identity_private_key or not self.identity_public_key:
                status = "unhealthy"
                issues.append("Identity keys not initialized")
            
            # Check if we have prekeys available
            if len(self.prekeys) < 5:
                status = "degraded"
                issues.append("Low number of prekeys available")
            
            return {
                "status": status,
                "issues": issues,
                "statistics": self.get_statistics()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}