"""API key rotation management with automated policies."""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import aioredis
import json

from .api_key_manager import APIKeyManager, APIKey, APIKeyScope, APIKeyStatus

logger = logging.getLogger(__name__)


class RotationTrigger(Enum):
    """Triggers for automatic key rotation."""
    TIME_BASED = "time_based"
    USAGE_BASED = "usage_based"
    SECURITY_EVENT = "security_event"
    MANUAL = "manual"
    COMPROMISE = "compromise"


class RotationStatus(Enum):
    """Status of key rotation operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class RotationPolicy:
    """Policy for automatic key rotation."""
    name: str
    description: str
    enabled: bool = True
    
    # Time-based rotation
    rotation_interval_days: Optional[int] = None
    max_key_age_days: Optional[int] = None
    
    # Usage-based rotation
    max_usage_count: Optional[int] = None
    
    # Grace period for old key after rotation
    grace_period_days: int = 7
    
    # Notification settings
    notify_before_rotation_days: int = 3
    notification_recipients: Set[str] = field(default_factory=set)
    
    # Scope restrictions
    applicable_scopes: Set[APIKeyScope] = field(default_factory=set)
    
    # Owner restrictions
    applicable_owners: Set[str] = field(default_factory=set)
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def applies_to_key(self, key: APIKey) -> bool:
        """Check if policy applies to a specific key."""
        try:
            # Check scope restrictions
            if self.applicable_scopes:
                if not any(scope in key.scopes for scope in self.applicable_scopes):
                    return False
            
            # Check owner restrictions
            if self.applicable_owners:
                if key.owner_id not in self.applicable_owners:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking policy applicability: {e}")
            return False
    
    def should_rotate(self, key: APIKey) -> tuple[bool, str]:
        """Check if key should be rotated based on policy."""
        try:
            if not self.enabled or not self.applies_to_key(key):
                return False, "Policy not applicable"
            
            current_time = datetime.now(timezone.utc)
            
            # Check time-based rotation
            if self.rotation_interval_days:
                last_rotation = key.metadata.get("last_rotation")
                if last_rotation:
                    last_rotation_time = datetime.fromisoformat(last_rotation)
                    if current_time - last_rotation_time >= timedelta(days=self.rotation_interval_days):
                        return True, f"Rotation interval exceeded ({self.rotation_interval_days} days)"
                else:
                    # No previous rotation, check key age
                    if current_time - key.created_at >= timedelta(days=self.rotation_interval_days):
                        return True, f"Key age exceeds rotation interval ({self.rotation_interval_days} days)"
            
            # Check maximum key age
            if self.max_key_age_days:
                key_age = current_time - key.created_at
                if key_age >= timedelta(days=self.max_key_age_days):
                    return True, f"Key age exceeds maximum ({self.max_key_age_days} days)"
            
            # Check usage-based rotation
            if self.max_usage_count:
                if key.usage_count >= self.max_usage_count:
                    return True, f"Usage count exceeds maximum ({self.max_usage_count})"
            
            return False, "No rotation criteria met"
            
        except Exception as e:
            logger.error(f"Error checking rotation criteria: {e}")
            return False, f"Error: {str(e)}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "rotation_interval_days": self.rotation_interval_days,
            "max_key_age_days": self.max_key_age_days,
            "max_usage_count": self.max_usage_count,
            "grace_period_days": self.grace_period_days,
            "notify_before_rotation_days": self.notify_before_rotation_days,
            "notification_recipients": list(self.notification_recipients),
            "applicable_scopes": [scope.value for scope in self.applicable_scopes],
            "applicable_owners": list(self.applicable_owners),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RotationPolicy":
        """Create policy from dictionary."""
        try:
            applicable_scopes = {APIKeyScope(scope) for scope in data.get("applicable_scopes", [])}
            
            return cls(
                name=data["name"],
                description=data["description"],
                enabled=data.get("enabled", True),
                rotation_interval_days=data.get("rotation_interval_days"),
                max_key_age_days=data.get("max_key_age_days"),
                max_usage_count=data.get("max_usage_count"),
                grace_period_days=data.get("grace_period_days", 7),
                notify_before_rotation_days=data.get("notify_before_rotation_days", 3),
                notification_recipients=set(data.get("notification_recipients", [])),
                applicable_scopes=applicable_scopes,
                applicable_owners=set(data.get("applicable_owners", [])),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
                metadata=data.get("metadata", {})
            )
        except Exception as e:
            logger.error(f"Error creating rotation policy from dict: {e}")
            raise ValueError(f"Invalid rotation policy data: {e}")


@dataclass
class RotationRecord:
    """Record of key rotation operation."""
    rotation_id: str
    old_key_id: str
    new_key_id: Optional[str]
    owner_id: str
    trigger: RotationTrigger
    status: RotationStatus
    initiated_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    policy_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary."""
        return {
            "rotation_id": self.rotation_id,
            "old_key_id": self.old_key_id,
            "new_key_id": self.new_key_id,
            "owner_id": self.owner_id,
            "trigger": self.trigger.value,
            "status": self.status.value,
            "initiated_at": self.initiated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "policy_name": self.policy_name,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RotationRecord":
        """Create record from dictionary."""
        return cls(
            rotation_id=data["rotation_id"],
            old_key_id=data["old_key_id"],
            new_key_id=data.get("new_key_id"),
            owner_id=data["owner_id"],
            trigger=RotationTrigger(data["trigger"]),
            status=RotationStatus(data["status"]),
            initiated_at=datetime.fromisoformat(data["initiated_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            error_message=data.get("error_message"),
            policy_name=data.get("policy_name"),
            metadata=data.get("metadata", {})
        )


class KeyRotationError(Exception):
    """Key rotation errors."""
    pass


class KeyRotationManager:
    """Manage API key rotation with policies and automation."""
    
    def __init__(
        self,
        api_key_manager: APIKeyManager,
        redis_url: str = "redis://localhost:6379",
        redis_db: int = 6,  # Separate DB for rotation data
        policy_prefix: str = "rotation_policy:",
        record_prefix: str = "rotation_record:",
        check_interval_minutes: int = 60  # Check for rotations every hour
    ):
        self.api_key_manager = api_key_manager
        self.redis_url = redis_url
        self.redis_db = redis_db
        self.policy_prefix = policy_prefix
        self.record_prefix = record_prefix
        self.check_interval_minutes = check_interval_minutes
        
        # Redis connection
        self.redis: Optional[aioredis.Redis] = None
        
        # Background task for automatic rotation
        self._rotation_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Rotation policies
        self._policies: Dict[str, RotationPolicy] = {}
        
        # Metrics
        self.metrics = {
            "rotations_completed": 0,
            "rotations_failed": 0,
            "automatic_rotations": 0,
            "manual_rotations": 0,
            "keys_pending_rotation": 0
        }
        
        logger.info("Key rotation manager initialized")
    
    async def connect(self):
        """Connect to Redis and initialize."""
        try:
            self.redis = aioredis.from_url(
                self.redis_url,
                db=self.redis_db,
                decode_responses=True
            )
            
            # Test connection
            await self.redis.ping()
            
            # Load existing policies
            await self._load_policies()
            
            # Initialize default policies
            await self._initialize_default_policies()
            
            logger.info("Connected to Redis for key rotation management")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise KeyRotationError(f"Redis connection failed: {e}")
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    async def start_automatic_rotation(self):
        """Start automatic key rotation background task."""
        try:
            if self._running:
                return
            
            self._running = True
            self._rotation_task = asyncio.create_task(self._rotation_loop())
            
            logger.info("Started automatic key rotation")
            
        except Exception as e:
            logger.error(f"Failed to start automatic rotation: {e}")
            raise KeyRotationError(f"Automatic rotation start failed: {e}")
    
    async def stop_automatic_rotation(self):
        """Stop automatic key rotation background task."""
        try:
            self._running = False
            
            if self._rotation_task:
                self._rotation_task.cancel()
                try:
                    await self._rotation_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Stopped automatic key rotation")
            
        except Exception as e:
            logger.error(f"Error stopping automatic rotation: {e}")
    
    async def _load_policies(self):
        """Load rotation policies from Redis."""
        try:
            if not self.redis:
                return
            
            self._policies.clear()
            
            async for key in self.redis.scan_iter(match=f"{self.policy_prefix}*"):
                try:
                    policy_data_str = await self.redis.get(key)
                    if policy_data_str:
                        policy_data = json.loads(policy_data_str)
                        policy = RotationPolicy.from_dict(policy_data)
                        self._policies[policy.name] = policy
                except Exception as e:
                    logger.error(f"Error loading policy {key}: {e}")
            
            logger.info(f"Loaded {len(self._policies)} rotation policies")
            
        except Exception as e:
            logger.error(f"Failed to load policies: {e}")
    
    async def _initialize_default_policies(self):
        """Initialize default rotation policies."""
        try:
            default_policies = [
                RotationPolicy(
                    name="high_privilege_keys",
                    description="Rotate high-privilege keys every 90 days",
                    rotation_interval_days=90,
                    max_key_age_days=365,
                    applicable_scopes={APIKeyScope.ADMIN_SYSTEM, APIKeyScope.ADMIN_SECURITY, APIKeyScope.ALL},
                    metadata={"system_policy": True}
                ),
                RotationPolicy(
                    name="standard_keys",
                    description="Rotate standard keys annually or after high usage",
                    rotation_interval_days=365,
                    max_usage_count=100000,
                    grace_period_days=14,
                    metadata={"system_policy": True}
                ),
                RotationPolicy(
                    name="readonly_keys",
                    description="Rotate readonly keys every 2 years",
                    rotation_interval_days=730,
                    applicable_scopes={APIKeyScope.READONLY},
                    grace_period_days=30,
                    metadata={"system_policy": True}
                )
            ]
            
            for policy in default_policies:
                if policy.name not in self._policies:
                    await self.create_rotation_policy(policy)
                    logger.info(f"Initialized default rotation policy: {policy.name}")
                    
        except Exception as e:
            logger.error(f"Failed to initialize default policies: {e}")
    
    async def create_rotation_policy(self, policy: RotationPolicy) -> bool:
        """Create a new rotation policy."""
        try:
            if not self.redis:
                raise KeyRotationError("Redis connection not initialized")
            
            # Store policy in Redis
            policy_key = f"{self.policy_prefix}{policy.name}"
            policy_data = json.dumps(policy.to_dict())
            
            await self.redis.set(policy_key, policy_data)
            
            # Update local cache
            self._policies[policy.name] = policy
            
            logger.info(f"Created rotation policy: {policy.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create rotation policy: {e}")
            return False
    
    async def _rotation_loop(self):
        """Background loop for automatic key rotation."""
        try:
            while self._running:
                try:
                    await self._check_and_rotate_keys()
                    await asyncio.sleep(self.check_interval_minutes * 60)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in rotation loop: {e}")
                    await asyncio.sleep(60)  # Wait 1 minute before retry
        
        except asyncio.CancelledError:
            logger.info("Rotation loop cancelled")
            raise
    
    async def _check_and_rotate_keys(self):
        """Check all keys for rotation requirements."""
        try:
            if not self.api_key_manager.redis:
                return
            
            pending_count = 0
            
            # Get all active API keys
            async for storage_key in self.api_key_manager.redis.scan_iter(
                match=f"{self.api_key_manager.key_prefix}*"
            ):
                try:
                    key_data_str = await self.api_key_manager.redis.get(storage_key)
                    if not key_data_str:
                        continue
                    
                    key_data = json.loads(key_data_str)
                    key = APIKey.from_dict(key_data)
                    
                    # Skip non-active keys
                    if key.status != APIKeyStatus.ACTIVE:
                        continue
                    
                    # Check each policy
                    for policy in self._policies.values():
                        should_rotate, reason = policy.should_rotate(key)
                        
                        if should_rotate:
                            logger.info(f"Scheduling automatic rotation for key {key.key_id}: {reason}")
                            
                            # Perform rotation
                            await self.rotate_key(
                                key.key_id,
                                RotationTrigger.TIME_BASED,
                                policy.name
                            )
                            pending_count += 1
                            break  # Only rotate once per check cycle
                
                except Exception as e:
                    logger.error(f"Error processing key {storage_key}: {e}")
                    continue
            
            self.metrics["keys_pending_rotation"] = pending_count
            
        except Exception as e:
            logger.error(f"Error checking keys for rotation: {e}")
    
    async def rotate_key(
        self,
        old_key_id: str,
        trigger: RotationTrigger = RotationTrigger.MANUAL,
        policy_name: Optional[str] = None,
        new_key_config: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Rotate an API key."""
        try:
            # Get old key
            old_key = await self.api_key_manager.get_api_key(old_key_id)
            if not old_key:
                raise KeyRotationError(f"Key not found: {old_key_id}")
            
            # Generate rotation ID
            rotation_id = f"rot_{secrets.token_hex(8)}"
            
            # Create rotation record
            rotation_record = RotationRecord(
                rotation_id=rotation_id,
                old_key_id=old_key_id,
                new_key_id=None,
                owner_id=old_key.owner_id,
                trigger=trigger,
                status=RotationStatus.IN_PROGRESS,
                initiated_at=datetime.now(timezone.utc),
                policy_name=policy_name
            )
            
            try:
                # Store initial rotation record
                await self._store_rotation_record(rotation_record)
                
                # Generate new key with same configuration
                new_config = new_key_config or {}
                
                new_key_name = new_config.get("name", f"{old_key.name}_rotated")
                new_key_desc = new_config.get("description", f"Rotated from {old_key.name}")
                new_scopes = new_config.get("scopes", list(old_key.scopes))
                new_rate_limit = new_config.get("rate_limit", old_key.rate_limit)
                new_ip_whitelist = new_config.get("ip_whitelist", list(old_key.ip_whitelist))
                
                # Create new key
                new_api_key, new_key_obj = await self.api_key_manager.generate_api_key(
                    name=new_key_name,
                    description=new_key_desc,
                    owner_id=old_key.owner_id,
                    scopes=new_scopes,
                    rate_limit=new_rate_limit,
                    ip_whitelist=new_ip_whitelist,
                    metadata={
                        "rotated_from": old_key_id,
                        "rotation_id": rotation_id,
                        "rotation_trigger": trigger.value
                    }
                )
                
                # Update rotation record
                rotation_record.new_key_id = new_key_obj.key_id
                rotation_record.status = RotationStatus.COMPLETED
                rotation_record.completed_at = datetime.now(timezone.utc)
                
                # Mark old key for graceful retirement
                grace_period_days = 7  # Default grace period
                if policy_name and policy_name in self._policies:
                    grace_period_days = self._policies[policy_name].grace_period_days
                
                # Schedule old key suspension
                old_key.metadata["rotation_id"] = rotation_id
                old_key.metadata["replacement_key_id"] = new_key_obj.key_id
                old_key.metadata["grace_period_end"] = (
                    datetime.now(timezone.utc) + timedelta(days=grace_period_days)
                ).isoformat()
                
                # Update old key
                await self.api_key_manager.update_api_key(
                    old_key_id,
                    metadata=old_key.metadata
                )
                
                # Update new key with rotation info
                new_key_obj.metadata["last_rotation"] = datetime.now(timezone.utc).isoformat()
                await self.api_key_manager.update_api_key(
                    new_key_obj.key_id,
                    metadata=new_key_obj.metadata
                )
                
                # Store completed rotation record
                await self._store_rotation_record(rotation_record)
                
                # Update metrics
                self.metrics["rotations_completed"] += 1
                if trigger == RotationTrigger.MANUAL:
                    self.metrics["manual_rotations"] += 1
                else:
                    self.metrics["automatic_rotations"] += 1
                
                logger.info(f"Successfully rotated key {old_key_id} to {new_key_obj.key_id}")
                return new_api_key
                
            except Exception as e:
                # Mark rotation as failed
                rotation_record.status = RotationStatus.FAILED
                rotation_record.error_message = str(e)
                await self._store_rotation_record(rotation_record)
                
                self.metrics["rotations_failed"] += 1
                raise
            
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            raise KeyRotationError(f"Rotation failed: {e}")
    
    async def _store_rotation_record(self, record: RotationRecord):
        """Store rotation record in Redis."""
        try:
            if not self.redis:
                return
            
            record_key = f"{self.record_prefix}{record.rotation_id}"
            record_data = json.dumps(record.to_dict())
            
            await self.redis.set(record_key, record_data)
            
            # Set expiration for old records (1 year)
            await self.redis.expire(record_key, 365 * 24 * 3600)
            
        except Exception as e:
            logger.error(f"Failed to store rotation record: {e}")
    
    async def get_rotation_history(
        self,
        owner_id: Optional[str] = None,
        limit: int = 100
    ) -> List[RotationRecord]:
        """Get rotation history."""
        try:
            if not self.redis:
                return []
            
            records = []
            
            async for key in self.redis.scan_iter(match=f"{self.record_prefix}*"):
                try:
                    record_data_str = await self.redis.get(key)
                    if record_data_str:
                        record_data = json.loads(record_data_str)
                        record = RotationRecord.from_dict(record_data)
                        
                        # Filter by owner if specified
                        if owner_id and record.owner_id != owner_id:
                            continue
                        
                        records.append(record)
                        
                        if len(records) >= limit:
                            break
                
                except Exception as e:
                    logger.error(f"Error processing rotation record {key}: {e}")
                    continue
            
            # Sort by initiated time (most recent first)
            return sorted(records, key=lambda r: r.initiated_at, reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to get rotation history: {e}")
            return []
    
    async def cleanup_expired_grace_periods(self) -> int:
        """Clean up keys that have passed their grace period."""
        try:
            cleanup_count = 0
            current_time = datetime.now(timezone.utc)
            
            # Find keys with expired grace periods
            async for storage_key in self.api_key_manager.redis.scan_iter(
                match=f"{self.api_key_manager.key_prefix}*"
            ):
                try:
                    key_data_str = await self.api_key_manager.redis.get(storage_key)
                    if not key_data_str:
                        continue
                    
                    key_data = json.loads(key_data_str)
                    key = APIKey.from_dict(key_data)
                    
                    # Check if key has grace period
                    grace_end_str = key.metadata.get("grace_period_end")
                    if not grace_end_str:
                        continue
                    
                    grace_end = datetime.fromisoformat(grace_end_str)
                    
                    # Check if grace period has ended
                    if current_time > grace_end:
                        # Revoke the old key
                        await self.api_key_manager.revoke_api_key(
                            key.key_id,
                            f"Grace period ended after rotation"
                        )
                        cleanup_count += 1
                        
                        logger.info(f"Revoked key {key.key_id} after grace period")
                
                except Exception as e:
                    logger.error(f"Error processing key {storage_key}: {e}")
                    continue
            
            return cleanup_count
            
        except Exception as e:
            logger.error(f"Grace period cleanup failed: {e}")
            return 0
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get rotation statistics."""
        try:
            # Count rotation records by status
            status_counts = {status.value: 0 for status in RotationStatus}
            
            if self.redis:
                async for key in self.redis.scan_iter(match=f"{self.record_prefix}*"):
                    try:
                        record_data_str = await self.redis.get(key)
                        if record_data_str:
                            record_data = json.loads(record_data_str)
                            status = record_data.get("status", "unknown")
                            status_counts[status] = status_counts.get(status, 0) + 1
                    except Exception:
                        continue
            
            return {
                "policies_count": len(self._policies),
                "rotation_records_by_status": status_counts,
                "metrics": self.metrics,
                "automatic_rotation_enabled": self._running
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
            
            # Check policies
            policies_loaded = len(self._policies) > 0
            
            # Get statistics
            stats = await self.get_statistics()
            
            return {
                "status": "healthy",
                "redis_connected": True,
                "policies_loaded": policies_loaded,
                "automatic_rotation_running": self._running,
                "statistics": stats
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop_automatic_rotation()
        await self.disconnect()


# Import secrets at top of file
import secrets