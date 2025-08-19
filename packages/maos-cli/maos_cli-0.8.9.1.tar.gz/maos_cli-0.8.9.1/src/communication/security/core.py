"""Core security management for MAOS communication."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass

from .encryption import EncryptionManager, CipherSuite
from ..message_bus.types import Message

logger = logging.getLogger(__name__)


@dataclass
class SecurityPolicy:
    """Security policy configuration."""
    require_encryption: bool = True
    require_authentication: bool = True
    require_authorization: bool = True
    allowed_ciphers: Set[CipherSuite] = None
    max_message_age: int = 300  # seconds
    rate_limit_per_agent: int = 1000  # messages per minute
    trusted_agents: Set[str] = None
    blocked_agents: Set[str] = None
    
    def __post_init__(self):
        if self.allowed_ciphers is None:
            self.allowed_ciphers = {CipherSuite.AES_256_GCM, CipherSuite.HYBRID}
        if self.trusted_agents is None:
            self.trusted_agents = set()
        if self.blocked_agents is None:
            self.blocked_agents = set()


class CommunicationSecurity:
    """Comprehensive security manager for MAOS communication."""
    
    def __init__(self, policy: Optional[SecurityPolicy] = None):
        self.policy = policy or SecurityPolicy()
        
        # Core security components
        self.encryption_manager = EncryptionManager()
        
        # Rate limiting
        self.rate_limits: Dict[str, List[datetime]] = {}
        
        # Message tracking for replay protection
        self.processed_messages: Set[str] = set()
        self.message_timestamps: Dict[str, datetime] = {}
        
        # Security events
        self.security_events: List[Dict[str, Any]] = []
        
        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # Metrics
        self.metrics = {
            "messages_encrypted": 0,
            "messages_decrypted": 0,
            "authentication_attempts": 0,
            "authentication_failures": 0,
            "authorization_checks": 0,
            "authorization_denials": 0,
            "rate_limit_violations": 0,
            "security_violations": 0,
            "replay_attempts": 0
        }
        
        # Status
        self.is_running = False
        
        logger.info("Communication security initialized")
    
    async def start(self):
        """Start security services."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Generate master key if not present
        if not self.encryption_manager.master_key:
            self.encryption_manager.generate_master_key()
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Communication security started")
    
    async def stop(self):
        """Stop security services."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Communication security stopped")
    
    async def secure_message(
        self,
        message: Message,
        recipient_key_id: Optional[str] = None,
        cipher: Optional[CipherSuite] = None
    ) -> Message:
        """Apply security to an outgoing message."""
        try:
            # Check if encryption is required
            if self.policy.require_encryption:
                if not recipient_key_id:
                    raise SecurityError("Recipient key required for encryption")
                
                # Choose cipher
                cipher = cipher or CipherSuite.AES_256_GCM
                if cipher not in self.policy.allowed_ciphers:
                    raise SecurityError(f"Cipher not allowed: {cipher}")
                
                # Encrypt message payload
                payload_json = message.payload if isinstance(message.payload, str) else str(message.payload)
                encrypted_data = self.encryption_manager.encrypt_message(
                    payload_json, recipient_key_id, cipher
                )
                
                # Update message with encrypted payload
                message.payload = {
                    "encrypted": True,
                    "data": encrypted_data
                }
                message.headers["encryption"] = "true"
                message.headers["cipher"] = cipher.value
                
                self.metrics["messages_encrypted"] += 1
            
            # Add security headers
            message.headers["security_timestamp"] = datetime.utcnow().isoformat()
            message.headers["security_nonce"] = self._generate_nonce()
            
            logger.debug(f"Secured message {message.id}")
            return message
            
        except Exception as e:
            self.metrics["security_violations"] += 1
            logger.error(f"Failed to secure message: {e}")
            raise SecurityError(f"Message security failed: {e}")
    
    async def verify_message(self, message: Message, sender_key_id: Optional[str] = None) -> Message:
        """Verify and process an incoming message."""
        try:
            # Check rate limits
            if not await self._check_rate_limit(message.sender):
                self.metrics["rate_limit_violations"] += 1
                raise SecurityError(f"Rate limit exceeded for agent: {message.sender}")
            
            # Check for blocked agents
            if message.sender in self.policy.blocked_agents:
                self.metrics["security_violations"] += 1
                raise SecurityError(f"Agent blocked: {message.sender}")
            
            # Check message age
            message_age = (datetime.utcnow() - message.timestamp).total_seconds()
            if message_age > self.policy.max_message_age:
                self.metrics["security_violations"] += 1
                raise SecurityError(f"Message too old: {message_age}s")
            
            # Check for replay attacks
            if await self._check_replay_protection(message):
                self.metrics["replay_attempts"] += 1
                raise SecurityError(f"Potential replay attack detected")
            
            # Decrypt if encrypted
            if message.headers.get("encryption") == "true":
                if not self.policy.require_encryption:
                    logger.warning("Received encrypted message but encryption not required")
                
                if not sender_key_id:
                    raise SecurityError("Sender key required for decryption")
                
                # Decrypt payload
                encrypted_data = message.payload.get("data")
                if not encrypted_data:
                    raise SecurityError("Missing encrypted data in message")
                
                decrypted_payload = self.encryption_manager.decrypt_message(encrypted_data)
                
                # Update message with decrypted payload
                try:
                    import json
                    message.payload = json.loads(decrypted_payload)
                except json.JSONDecodeError:
                    message.payload = decrypted_payload
                
                self.metrics["messages_decrypted"] += 1
            
            # Record message processing
            await self._record_message_processing(message)
            
            logger.debug(f"Verified message {message.id}")
            return message
            
        except Exception as e:
            await self._log_security_event("message_verification_failed", {
                "message_id": message.id,
                "sender": message.sender,
                "error": str(e)
            })
            logger.error(f"Message verification failed: {e}")
            raise
    
    async def _check_rate_limit(self, agent_id: str) -> bool:
        """Check if agent is within rate limits."""
        try:
            current_time = datetime.utcnow()
            minute_ago = current_time - timedelta(minutes=1)
            
            # Initialize or clean up rate limit tracking
            if agent_id not in self.rate_limits:
                self.rate_limits[agent_id] = []
            
            # Remove old timestamps
            self.rate_limits[agent_id] = [
                timestamp for timestamp in self.rate_limits[agent_id]
                if timestamp > minute_ago
            ]
            
            # Check if within limit
            if len(self.rate_limits[agent_id]) >= self.policy.rate_limit_per_agent:
                return False
            
            # Record current request
            self.rate_limits[agent_id].append(current_time)
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow on error
    
    async def _check_replay_protection(self, message: Message) -> bool:
        """Check for replay attacks."""
        try:
            # Create message fingerprint
            fingerprint = self._create_message_fingerprint(message)
            
            # Check if already processed
            if fingerprint in self.processed_messages:
                return True  # Replay detected
            
            # Record message
            self.processed_messages.add(fingerprint)
            self.message_timestamps[fingerprint] = message.timestamp
            
            return False  # Not a replay
            
        except Exception as e:
            logger.error(f"Replay protection check failed: {e}")
            return False  # Allow on error
    
    def _create_message_fingerprint(self, message: Message) -> str:
        """Create unique fingerprint for a message."""
        import hashlib
        
        # Use message ID, sender, timestamp, and content hash
        content = f"{message.id}:{message.sender}:{message.timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _generate_nonce(self) -> str:
        """Generate cryptographic nonce."""
        import os
        return os.urandom(16).hex()
    
    async def _record_message_processing(self, message: Message):
        """Record successful message processing."""
        fingerprint = self._create_message_fingerprint(message)
        self.processed_messages.add(fingerprint)
        self.message_timestamps[fingerprint] = datetime.utcnow()
    
    async def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "details": details
        }
        
        self.security_events.append(event)
        
        # Keep only recent events
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
        
        logger.warning(f"Security event: {event_type} - {details}")
    
    async def _cleanup_loop(self):
        """Periodic cleanup of old data."""
        try:
            while self.is_running:
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
                try:
                    await self._cleanup_old_data()
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Security cleanup loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Security cleanup loop error: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old security data."""
        try:
            current_time = datetime.utcnow()
            
            # Clean up old message timestamps (older than max_message_age * 2)
            cutoff_time = current_time - timedelta(seconds=self.policy.max_message_age * 2)
            
            old_fingerprints = [
                fp for fp, ts in self.message_timestamps.items()
                if ts < cutoff_time
            ]
            
            for fingerprint in old_fingerprints:
                self.processed_messages.discard(fingerprint)
                del self.message_timestamps[fingerprint]
            
            # Clean up old rate limit data (older than 5 minutes)
            rate_limit_cutoff = current_time - timedelta(minutes=5)
            
            for agent_id in list(self.rate_limits.keys()):
                self.rate_limits[agent_id] = [
                    timestamp for timestamp in self.rate_limits[agent_id]
                    if timestamp > rate_limit_cutoff
                ]
                
                # Remove empty entries
                if not self.rate_limits[agent_id]:
                    del self.rate_limits[agent_id]
            
            # Clean up old security events (older than 24 hours)
            event_cutoff = current_time - timedelta(hours=24)
            
            self.security_events = [
                event for event in self.security_events
                if datetime.fromisoformat(event["timestamp"]) > event_cutoff
            ]
            
            logger.debug("Security cleanup completed")
            
        except Exception as e:
            logger.error(f"Security cleanup failed: {e}")
    
    # Key management methods
    async def generate_agent_keys(self, agent_id: str) -> Dict[str, str]:
        """Generate encryption keys for an agent."""
        try:
            # Generate asymmetric key pair
            public_key, private_key = self.encryption_manager.generate_asymmetric_keypair(agent_id)
            
            # Generate symmetric key
            symmetric_key = self.encryption_manager.generate_symmetric_key(f"{agent_id}_symmetric")
            
            logger.info(f"Generated keys for agent: {agent_id}")
            
            return {
                "agent_id": agent_id,
                "public_key": public_key.decode(),
                "symmetric_key_id": f"{agent_id}_symmetric",
                "key_generated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate keys for agent {agent_id}: {e}")
            raise SecurityError(f"Key generation failed: {e}")
    
    async def import_agent_public_key(self, agent_id: str, public_key_pem: str) -> bool:
        """Import public key for an agent."""
        try:
            self.encryption_manager.import_public_key(agent_id, public_key_pem.encode())
            logger.info(f"Imported public key for agent: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import public key: {e}")
            return False
    
    async def update_security_policy(self, new_policy: SecurityPolicy):
        """Update security policy."""
        self.policy = new_policy
        
        await self._log_security_event("policy_updated", {
            "require_encryption": new_policy.require_encryption,
            "require_authentication": new_policy.require_authentication,
            "allowed_ciphers": [cipher.value for cipher in new_policy.allowed_ciphers]
        })
        
        logger.info("Security policy updated")
    
    async def add_trusted_agent(self, agent_id: str):
        """Add agent to trusted list."""
        self.policy.trusted_agents.add(agent_id)
        
        await self._log_security_event("agent_trusted", {"agent_id": agent_id})
        logger.info(f"Added trusted agent: {agent_id}")
    
    async def block_agent(self, agent_id: str, reason: str = ""):
        """Block an agent."""
        self.policy.blocked_agents.add(agent_id)
        
        await self._log_security_event("agent_blocked", {
            "agent_id": agent_id,
            "reason": reason
        })
        logger.warning(f"Blocked agent: {agent_id} - {reason}")
    
    async def unblock_agent(self, agent_id: str):
        """Unblock an agent."""
        self.policy.blocked_agents.discard(agent_id)
        
        await self._log_security_event("agent_unblocked", {"agent_id": agent_id})
        logger.info(f"Unblocked agent: {agent_id}")
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Get current security status."""
        return {
            "is_running": self.is_running,
            "policy": {
                "require_encryption": self.policy.require_encryption,
                "require_authentication": self.policy.require_authentication,
                "require_authorization": self.policy.require_authorization,
                "allowed_ciphers": [cipher.value for cipher in self.policy.allowed_ciphers],
                "max_message_age": self.policy.max_message_age,
                "rate_limit_per_agent": self.policy.rate_limit_per_agent
            },
            "agent_counts": {
                "trusted": len(self.policy.trusted_agents),
                "blocked": len(self.policy.blocked_agents)
            },
            "encryption_keys": self.encryption_manager.get_key_info(),
            "active_rate_limits": len(self.rate_limits),
            "processed_messages": len(self.processed_messages),
            "security_events": len(self.security_events)
        }
    
    async def get_security_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent security events."""
        return self.security_events[-limit:] if limit else self.security_events
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get security metrics."""
        return self.metrics.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform security health check."""
        try:
            status = "healthy"
            issues = []
            
            # Check if master key is present
            if not self.encryption_manager.master_key:
                status = "degraded"
                issues.append("No master key configured")
            
            # Check for excessive security violations
            if self.metrics["security_violations"] > 100:
                status = "degraded"
                issues.append("High number of security violations")
            
            # Check for too many blocked agents
            if len(self.policy.blocked_agents) > 10:
                status = "degraded"
                issues.append("Many agents blocked")
            
            return {
                "status": status,
                "is_running": self.is_running,
                "issues": issues,
                "metrics": await self.get_metrics(),
                "security_status": await self.get_security_status()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    # Context manager support
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


class SecurityError(Exception):
    """Security-related errors."""
    pass