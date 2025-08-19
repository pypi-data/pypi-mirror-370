"""Enterprise API key management with rotation and scope control."""

import hashlib
import hmac
import logging
import os
import secrets
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import aioredis
import json
import base64

logger = logging.getLogger(__name__)


class APIKeyScope(Enum):
    """API key scopes for access control."""
    # Read permissions
    READ_AGENTS = "read:agents"
    READ_TASKS = "read:tasks"
    READ_RESOURCES = "read:resources"
    READ_SYSTEM = "read:system"
    READ_METRICS = "read:metrics"
    
    # Write permissions
    WRITE_AGENTS = "write:agents"
    WRITE_TASKS = "write:tasks"
    WRITE_RESOURCES = "write:resources"
    WRITE_SYSTEM = "write:system"
    
    # Execute permissions
    EXECUTE_AGENTS = "execute:agents"
    EXECUTE_TASKS = "execute:tasks"
    EXECUTE_SYSTEM = "execute:system"
    
    # Admin permissions
    ADMIN_USERS = "admin:users"
    ADMIN_KEYS = "admin:keys"
    ADMIN_SECURITY = "admin:security"
    ADMIN_SYSTEM = "admin:system"
    
    # Special scopes
    ALL = "all"
    READONLY = "readonly"


class APIKeyStatus(Enum):
    """API key status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


@dataclass
class APIKey:
    """API key with metadata and access control."""
    key_id: str
    key_hash: str  # Hashed version for storage
    name: str
    description: str
    scopes: Set[APIKeyScope]
    owner_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    rate_limit: Optional[int] = None  # Requests per hour
    ip_whitelist: Set[str] = field(default_factory=set)
    status: APIKeyStatus = APIKeyStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Process fields after initialization."""
        if isinstance(self.scopes, list):
            self.scopes = {APIKeyScope(scope) if isinstance(scope, str) else scope for scope in self.scopes}
        if isinstance(self.ip_whitelist, list):
            self.ip_whitelist = set(self.ip_whitelist)
    
    def is_valid(self) -> bool:
        """Check if API key is currently valid."""
        try:
            # Check status
            if self.status != APIKeyStatus.ACTIVE:
                return False
            
            # Check expiration
            if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking key validity: {e}")
            return False
    
    def has_scope(self, required_scope: APIKeyScope) -> bool:
        """Check if key has required scope."""
        if APIKeyScope.ALL in self.scopes:
            return True
        
        if required_scope in self.scopes:
            return True
        
        # Check for broader readonly access
        if required_scope in [APIKeyScope.READ_AGENTS, APIKeyScope.READ_TASKS, APIKeyScope.READ_RESOURCES, APIKeyScope.READ_SYSTEM, APIKeyScope.READ_METRICS]:
            if APIKeyScope.READONLY in self.scopes:
                return True
        
        return False
    
    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed."""
        if not self.ip_whitelist:
            return True  # No restrictions
        
        return ip_address in self.ip_whitelist
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert API key to dictionary (without sensitive data)."""
        return {
            "key_id": self.key_id,
            "name": self.name,
            "description": self.description,
            "scopes": [scope.value for scope in self.scopes],
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "usage_count": self.usage_count,
            "rate_limit": self.rate_limit,
            "ip_whitelist": list(self.ip_whitelist),
            "status": self.status.value,
            "metadata": self.metadata
        }
    
    def to_storage_dict(self) -> Dict[str, Any]:
        """Convert API key to dictionary for storage (includes hash)."""
        data = self.to_dict()
        data["key_hash"] = self.key_hash
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APIKey":
        """Create API key from dictionary."""
        try:
            scopes = {APIKeyScope(scope) for scope in data.get("scopes", [])}
            
            return cls(
                key_id=data["key_id"],
                key_hash=data["key_hash"],
                name=data["name"],
                description=data["description"],
                scopes=scopes,
                owner_id=data["owner_id"],
                created_at=datetime.fromisoformat(data["created_at"]),
                expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
                last_used=datetime.fromisoformat(data["last_used"]) if data.get("last_used") else None,
                usage_count=data.get("usage_count", 0),
                rate_limit=data.get("rate_limit"),
                ip_whitelist=set(data.get("ip_whitelist", [])),
                status=APIKeyStatus(data.get("status", "active")),
                metadata=data.get("metadata", {})
            )
        except Exception as e:
            logger.error(f"Error creating API key from dict: {e}")
            raise ValueError(f"Invalid API key data: {e}")


class APIKeyError(Exception):
    """API key management errors."""
    pass


class APIKeyManager:
    """Comprehensive API key management system."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        redis_db: int = 5,  # Separate DB for API keys
        key_prefix: str = "api_key:",
        owner_keys_prefix: str = "owner_keys:",
        secret_key: Optional[str] = None,
        default_expiry_days: int = 365,
        min_key_length: int = 32,
        rate_limit_window: int = 3600  # 1 hour in seconds
    ):
        self.redis_url = redis_url
        self.redis_db = redis_db
        self.key_prefix = key_prefix
        self.owner_keys_prefix = owner_keys_prefix
        self.secret_key = secret_key or os.urandom(32).hex()
        self.default_expiry_days = default_expiry_days
        self.min_key_length = min_key_length
        self.rate_limit_window = rate_limit_window
        
        # Redis connection
        self.redis: Optional[aioredis.Redis] = None
        
        # Rate limiting tracking
        self._rate_limit_counters: Dict[str, Dict[str, int]] = {}
        
        # Metrics
        self.metrics = {
            "keys_generated": 0,
            "keys_validated": 0,
            "keys_revoked": 0,
            "validation_failures": 0,
            "rate_limit_violations": 0
        }
        
        logger.info("API key manager initialized")
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis = aioredis.from_url(
                self.redis_url,
                db=self.redis_db,
                decode_responses=True
            )
            
            # Test connection
            await self.redis.ping()
            logger.info("Connected to Redis for API key management")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise APIKeyError(f"Redis connection failed: {e}")
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    def _generate_key(self) -> str:
        """Generate cryptographically secure API key."""
        # Generate random bytes
        random_bytes = secrets.token_bytes(24)  # 24 bytes = 192 bits
        
        # Encode to base64 URL-safe format
        key = base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')
        
        # Add MAOS prefix for identification
        return f"maos_key_{key}"
    
    def _hash_key(self, key: str) -> str:
        """Create secure hash of API key for storage."""
        return hashlib.sha256(f"{self.secret_key}:{key}".encode()).hexdigest()
    
    def _verify_key_hash(self, key: str, key_hash: str) -> bool:
        """Verify API key against stored hash."""
        return hmac.compare_digest(self._hash_key(key), key_hash)
    
    async def generate_api_key(
        self,
        name: str,
        description: str,
        owner_id: str,
        scopes: List[APIKeyScope],
        expires_in_days: Optional[int] = None,
        rate_limit: Optional[int] = None,
        ip_whitelist: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, APIKey]:
        """Generate new API key."""
        try:
            if not self.redis:
                raise APIKeyError("Redis connection not initialized")
            
            # Generate key and ID
            api_key = self._generate_key()
            key_id = f"key_{secrets.token_hex(8)}"
            
            # Calculate expiration
            expires_at = None
            if expires_in_days or self.default_expiry_days:
                days = expires_in_days or self.default_expiry_days
                expires_at = datetime.now(timezone.utc) + timedelta(days=days)
            
            # Create API key object
            key_obj = APIKey(
                key_id=key_id,
                key_hash=self._hash_key(api_key),
                name=name,
                description=description,
                scopes=set(scopes),
                owner_id=owner_id,
                expires_at=expires_at,
                rate_limit=rate_limit,
                ip_whitelist=set(ip_whitelist or []),
                metadata=metadata or {}
            )
            
            # Store in Redis
            key_storage_key = f"{self.key_prefix}{key_id}"
            key_data = json.dumps(key_obj.to_storage_dict())
            
            await self.redis.set(key_storage_key, key_data)
            
            # Add to owner's key set
            owner_keys_key = f"{self.owner_keys_prefix}{owner_id}"
            await self.redis.sadd(owner_keys_key, key_id)
            
            # Set expiration on Redis keys if applicable
            if expires_at:
                expire_seconds = int((expires_at - datetime.now(timezone.utc)).total_seconds())
                await self.redis.expire(key_storage_key, expire_seconds)
            
            self.metrics["keys_generated"] += 1
            logger.info(f"Generated API key {key_id} for owner {owner_id}")
            
            return api_key, key_obj
            
        except Exception as e:
            logger.error(f"Failed to generate API key: {e}")
            raise APIKeyError(f"Key generation failed: {e}")
    
    async def validate_api_key(
        self,
        api_key: str,
        required_scope: Optional[APIKeyScope] = None,
        client_ip: Optional[str] = None,
        check_rate_limit: bool = True
    ) -> Optional[APIKey]:
        """Validate API key and return key object if valid."""
        try:
            if not self.redis:
                raise APIKeyError("Redis connection not initialized")
            
            self.metrics["keys_validated"] += 1
            
            # Extract key ID from the key (for optimization, we could store a mapping)
            # For now, we'll need to check against all keys (can be optimized with indexing)
            key_hash = self._hash_key(api_key)
            
            # Find matching key
            async for storage_key in self.redis.scan_iter(match=f"{self.key_prefix}*"):
                try:
                    key_data_str = await self.redis.get(storage_key)
                    if not key_data_str:
                        continue
                    
                    key_data = json.loads(key_data_str)
                    
                    # Check if hash matches
                    if not hmac.compare_digest(key_data.get("key_hash", ""), key_hash):
                        continue
                    
                    # Found matching key
                    key_obj = APIKey.from_dict(key_data)
                    
                    # Check if key is valid
                    if not key_obj.is_valid():
                        self.metrics["validation_failures"] += 1
                        return None
                    
                    # Check IP whitelist
                    if client_ip and not key_obj.is_ip_allowed(client_ip):
                        self.metrics["validation_failures"] += 1
                        return None
                    
                    # Check required scope
                    if required_scope and not key_obj.has_scope(required_scope):
                        self.metrics["validation_failures"] += 1
                        return None
                    
                    # Check rate limit
                    if check_rate_limit and key_obj.rate_limit:
                        if not await self._check_rate_limit(key_obj):
                            self.metrics["rate_limit_violations"] += 1
                            return None
                    
                    # Update usage statistics
                    await self._update_usage_stats(key_obj)
                    
                    return key_obj
                    
                except Exception as e:
                    logger.error(f"Error processing key {storage_key}: {e}")
                    continue
            
            # Key not found or invalid
            self.metrics["validation_failures"] += 1
            return None
            
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            self.metrics["validation_failures"] += 1
            return None
    
    async def _check_rate_limit(self, key_obj: APIKey) -> bool:
        """Check if API key is within rate limits."""
        try:
            if not key_obj.rate_limit:
                return True
            
            current_hour = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
            rate_key = f"rate_limit:{key_obj.key_id}:{current_hour.isoformat()}"
            
            # Get current usage count
            current_count = await self.redis.get(rate_key)
            current_count = int(current_count) if current_count else 0
            
            # Check if within limit
            if current_count >= key_obj.rate_limit:
                return False
            
            # Increment counter
            await self.redis.incr(rate_key)
            await self.redis.expire(rate_key, self.rate_limit_window)
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow on error
    
    async def _update_usage_stats(self, key_obj: APIKey):
        """Update API key usage statistics."""
        try:
            key_obj.last_used = datetime.now(timezone.utc)
            key_obj.usage_count += 1
            
            # Update in Redis
            key_storage_key = f"{self.key_prefix}{key_obj.key_id}"
            key_data = json.dumps(key_obj.to_storage_dict())
            
            # Preserve existing TTL
            ttl = await self.redis.ttl(key_storage_key)
            await self.redis.set(key_storage_key, key_data)
            
            if ttl > 0:
                await self.redis.expire(key_storage_key, ttl)
                
        except Exception as e:
            logger.error(f"Failed to update usage stats: {e}")
    
    async def get_api_key(self, key_id: str) -> Optional[APIKey]:
        """Get API key by ID."""
        try:
            if not self.redis:
                raise APIKeyError("Redis connection not initialized")
            
            key_storage_key = f"{self.key_prefix}{key_id}"
            key_data_str = await self.redis.get(key_storage_key)
            
            if not key_data_str:
                return None
            
            key_data = json.loads(key_data_str)
            return APIKey.from_dict(key_data)
            
        except Exception as e:
            logger.error(f"Failed to get API key: {e}")
            return None
    
    async def list_owner_keys(
        self,
        owner_id: str,
        include_expired: bool = False,
        include_revoked: bool = False
    ) -> List[APIKey]:
        """List all API keys for an owner."""
        try:
            if not self.redis:
                raise APIKeyError("Redis connection not initialized")
            
            owner_keys_key = f"{self.owner_keys_prefix}{owner_id}"
            key_ids = await self.redis.smembers(owner_keys_key)
            
            keys = []
            for key_id in key_ids:
                key_obj = await self.get_api_key(key_id)
                if key_obj:
                    # Apply filters
                    if not include_expired and key_obj.status == APIKeyStatus.EXPIRED:
                        continue
                    if not include_revoked and key_obj.status == APIKeyStatus.REVOKED:
                        continue
                    
                    keys.append(key_obj)
            
            return sorted(keys, key=lambda k: k.created_at, reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list owner keys: {e}")
            return []
    
    async def revoke_api_key(self, key_id: str, reason: str = "") -> bool:
        """Revoke an API key."""
        try:
            if not self.redis:
                raise APIKeyError("Redis connection not initialized")
            
            key_obj = await self.get_api_key(key_id)
            if not key_obj:
                return False
            
            # Update status
            key_obj.status = APIKeyStatus.REVOKED
            key_obj.metadata["revoked_at"] = datetime.now(timezone.utc).isoformat()
            key_obj.metadata["revocation_reason"] = reason
            
            # Update in Redis
            key_storage_key = f"{self.key_prefix}{key_id}"
            key_data = json.dumps(key_obj.to_storage_dict())
            
            # Preserve existing TTL
            ttl = await self.redis.ttl(key_storage_key)
            await self.redis.set(key_storage_key, key_data)
            
            if ttl > 0:
                await self.redis.expire(key_storage_key, ttl)
            
            self.metrics["keys_revoked"] += 1
            logger.info(f"Revoked API key {key_id}: {reason}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke API key: {e}")
            return False
    
    async def update_api_key(
        self,
        key_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        scopes: Optional[List[APIKeyScope]] = None,
        rate_limit: Optional[int] = None,
        ip_whitelist: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update API key properties."""
        try:
            if not self.redis:
                raise APIKeyError("Redis connection not initialized")
            
            key_obj = await self.get_api_key(key_id)
            if not key_obj:
                return False
            
            # Update fields
            if name is not None:
                key_obj.name = name
            if description is not None:
                key_obj.description = description
            if scopes is not None:
                key_obj.scopes = set(scopes)
            if rate_limit is not None:
                key_obj.rate_limit = rate_limit
            if ip_whitelist is not None:
                key_obj.ip_whitelist = set(ip_whitelist)
            if metadata is not None:
                key_obj.metadata.update(metadata)
            
            # Update in Redis
            key_storage_key = f"{self.key_prefix}{key_id}"
            key_data = json.dumps(key_obj.to_storage_dict())
            
            # Preserve existing TTL
            ttl = await self.redis.ttl(key_storage_key)
            await self.redis.set(key_storage_key, key_data)
            
            if ttl > 0:
                await self.redis.expire(key_storage_key, ttl)
            
            logger.info(f"Updated API key {key_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update API key: {e}")
            return False
    
    async def cleanup_expired_keys(self) -> int:
        """Clean up expired and revoked API keys."""
        try:
            if not self.redis:
                raise APIKeyError("Redis connection not initialized")
            
            cleanup_count = 0
            current_time = datetime.now(timezone.utc)
            
            # Process all keys
            async for storage_key in self.redis.scan_iter(match=f"{self.key_prefix}*"):
                try:
                    key_data_str = await self.redis.get(storage_key)
                    if not key_data_str:
                        continue
                    
                    key_data = json.loads(key_data_str)
                    key_obj = APIKey.from_dict(key_data)
                    
                    # Check if key should be cleaned up
                    should_cleanup = False
                    
                    if key_obj.expires_at and current_time > key_obj.expires_at:
                        # Mark as expired
                        key_obj.status = APIKeyStatus.EXPIRED
                        should_cleanup = True
                    
                    # Remove very old revoked keys (older than 30 days)
                    if key_obj.status == APIKeyStatus.REVOKED:
                        revoked_at_str = key_obj.metadata.get("revoked_at")
                        if revoked_at_str:
                            revoked_at = datetime.fromisoformat(revoked_at_str)
                            if current_time - revoked_at > timedelta(days=30):
                                await self.redis.delete(storage_key)
                                # Remove from owner's set
                                owner_keys_key = f"{self.owner_keys_prefix}{key_obj.owner_id}"
                                await self.redis.srem(owner_keys_key, key_obj.key_id)
                                cleanup_count += 1
                                continue
                    
                    # Update expired keys
                    if should_cleanup and key_obj.status != APIKeyStatus.EXPIRED:
                        key_obj.status = APIKeyStatus.EXPIRED
                        updated_data = json.dumps(key_obj.to_storage_dict())
                        await self.redis.set(storage_key, updated_data)
                        cleanup_count += 1
                
                except Exception as e:
                    logger.error(f"Error processing key {storage_key}: {e}")
                    continue
            
            logger.info(f"Cleaned up {cleanup_count} expired/old API keys")
            return cleanup_count
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get API key management statistics."""
        try:
            if not self.redis:
                return {"error": "Redis not connected"}
            
            # Count keys by status
            status_counts = {"active": 0, "expired": 0, "revoked": 0, "suspended": 0}
            total_keys = 0
            total_owners = 0
            
            async for storage_key in self.redis.scan_iter(match=f"{self.key_prefix}*"):
                try:
                    key_data_str = await self.redis.get(storage_key)
                    if key_data_str:
                        key_data = json.loads(key_data_str)
                        status = key_data.get("status", "active")
                        status_counts[status] = status_counts.get(status, 0) + 1
                        total_keys += 1
                except Exception:
                    continue
            
            # Count unique owners
            async for owner_key in self.redis.scan_iter(match=f"{self.owner_keys_prefix}*"):
                total_owners += 1
            
            return {
                "total_keys": total_keys,
                "total_owners": total_owners,
                "status_counts": status_counts,
                "metrics": self.metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            if not self.redis:
                return {"status": "unhealthy", "error": "Redis not connected"}
            
            # Test Redis connection
            await self.redis.ping()
            
            # Test key generation and validation
            test_key, test_obj = await self.generate_api_key(
                name="health_check",
                description="Health check test key",
                owner_id="health_check",
                scopes=[APIKeyScope.READ_SYSTEM]
            )
            
            # Test validation
            validated_obj = await self.validate_api_key(test_key, APIKeyScope.READ_SYSTEM)
            
            # Clean up test key
            await self.revoke_api_key(test_obj.key_id, "Health check cleanup")
            
            # Get statistics
            stats = await self.get_statistics()
            
            return {
                "status": "healthy",
                "redis_connected": True,
                "key_operations_working": validated_obj is not None,
                "statistics": stats
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()