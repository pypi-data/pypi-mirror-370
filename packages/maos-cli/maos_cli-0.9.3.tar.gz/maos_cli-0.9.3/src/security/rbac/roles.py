"""Role management system for MAOS RBAC."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import aioredis

from .permissions import Permission, PermissionSet, PermissionType

logger = logging.getLogger(__name__)


class RoleType(Enum):
    """Types of roles in MAOS."""
    SYSTEM_ADMIN = "system_admin"
    SECURITY_ADMIN = "security_admin"
    OPERATOR = "operator"
    AGENT_MANAGER = "agent_manager"
    TASK_COORDINATOR = "task_coordinator"
    RESOURCE_MANAGER = "resource_manager"
    MONITOR = "monitor"
    AGENT = "agent"
    READONLY = "readonly"
    CUSTOM = "custom"


@dataclass
class Role:
    """Role definition with permissions and metadata."""
    name: str
    role_type: RoleType
    description: str
    permissions: PermissionSet = field(default_factory=PermissionSet)
    parent_roles: Set[str] = field(default_factory=set)  # Role inheritance
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate role after initialization."""
        if isinstance(self.parent_roles, list):
            self.parent_roles = set(self.parent_roles)
    
    def add_permission(self, permission: Permission):
        """Add permission to role."""
        self.permissions.add_permission(permission)
        self.updated_at = datetime.now(timezone.utc)
    
    def remove_permission(self, permission: Permission):
        """Remove permission from role."""
        self.permissions.remove_permission(permission)
        self.updated_at = datetime.now(timezone.utc)
    
    def has_permission(
        self,
        permission_type: PermissionType,
        resource: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Check if role has specific permission."""
        if not self.is_active:
            return False
        
        return self.permissions.has_permission(permission_type, resource, context)
    
    def get_all_permissions(self, include_inherited: bool = True) -> PermissionSet:
        """Get all permissions for this role."""
        if not include_inherited:
            return self.permissions
        
        # This will be enhanced when role inheritance is fully implemented
        return self.permissions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert role to dictionary."""
        return {
            "name": self.name,
            "role_type": self.role_type.value,
            "description": self.description,
            "permissions": self.permissions.to_dict(),
            "parent_roles": list(self.parent_roles),
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Role":
        """Create role from dictionary."""
        try:
            role = cls(
                name=data["name"],
                role_type=RoleType(data["role_type"]),
                description=data["description"],
                permissions=PermissionSet.from_dict(data.get("permissions", {})),
                parent_roles=set(data.get("parent_roles", [])),
                created_at=datetime.fromisoformat(data["created_at"]),
                created_by=data.get("created_by"),
                updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
                updated_by=data.get("updated_by"),
                is_active=data.get("is_active", True),
                metadata=data.get("metadata", {})
            )
            return role
        except Exception as e:
            logger.error(f"Error creating role from dict: {e}")
            raise ValueError(f"Invalid role data: {e}")


class RoleError(Exception):
    """Role management errors."""
    pass


class RoleManager:
    """Manage roles with Redis persistence and caching."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        redis_db: int = 3,  # Separate DB for roles
        role_prefix: str = "role:",
        user_roles_prefix: str = "user_roles:",
        cache_ttl: int = 3600  # 1 hour cache
    ):
        self.redis_url = redis_url
        self.redis_db = redis_db
        self.role_prefix = role_prefix
        self.user_roles_prefix = user_roles_prefix
        self.cache_ttl = cache_ttl
        
        # Redis connection
        self.redis: Optional[aioredis.Redis] = None
        
        # In-memory cache for frequently accessed roles
        self._role_cache: Dict[str, Role] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        # Predefined system roles
        self._system_roles = self._create_system_roles()
        
        # Metrics
        self.metrics = {
            "roles_created": 0,
            "roles_updated": 0,
            "roles_deleted": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        logger.info("Role manager initialized")
    
    async def connect(self):
        """Connect to Redis and initialize system roles."""
        try:
            self.redis = aioredis.from_url(
                self.redis_url,
                db=self.redis_db,
                decode_responses=True
            )
            
            # Test connection
            await self.redis.ping()
            
            # Initialize system roles
            await self._initialize_system_roles()
            
            logger.info("Connected to Redis for role management")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise RoleError(f"Redis connection failed: {e}")
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    def _create_system_roles(self) -> Dict[str, Role]:
        """Create predefined system roles."""
        from .permissions import (
            ADMIN_PERMISSIONS, OPERATOR_PERMISSIONS, 
            AGENT_PERMISSIONS, READONLY_PERMISSIONS
        )
        
        system_roles = {
            "system_admin": Role(
                name="system_admin",
                role_type=RoleType.SYSTEM_ADMIN,
                description="Full system administration access",
                permissions=ADMIN_PERMISSIONS,
                metadata={"system_role": True}
            ),
            "operator": Role(
                name="operator",
                role_type=RoleType.OPERATOR,
                description="System operation and monitoring",
                permissions=OPERATOR_PERMISSIONS,
                metadata={"system_role": True}
            ),
            "agent": Role(
                name="agent",
                role_type=RoleType.AGENT,
                description="Basic agent operations",
                permissions=AGENT_PERMISSIONS,
                metadata={"system_role": True}
            ),
            "readonly": Role(
                name="readonly",
                role_type=RoleType.READONLY,
                description="Read-only access",
                permissions=READONLY_PERMISSIONS,
                metadata={"system_role": True}
            )
        }
        
        # Add security admin role
        security_admin = Role(
            name="security_admin",
            role_type=RoleType.SECURITY_ADMIN,
            description="Security administration",
            metadata={"system_role": True}
        )
        security_admin.permissions.add_permission(Permission("security_config", PermissionType.SECURITY_CONFIG))
        security_admin.permissions.add_permission(Permission("security_audit", PermissionType.SECURITY_AUDIT))
        security_admin.permissions.add_permission(Permission("security_keys", PermissionType.SECURITY_KEYS))
        security_admin.permissions.add_permission(Permission("system_monitor", PermissionType.SYSTEM_MONITOR))
        
        system_roles["security_admin"] = security_admin
        
        return system_roles
    
    async def _initialize_system_roles(self):
        """Initialize system roles in Redis."""
        try:
            for role_name, role in self._system_roles.items():
                # Check if role exists
                if not await self.role_exists(role_name):
                    await self.create_role(role)
                    logger.info(f"Initialized system role: {role_name}")
        except Exception as e:
            logger.error(f"Failed to initialize system roles: {e}")
    
    def _is_cache_valid(self, role_name: str) -> bool:
        """Check if cached role is still valid."""
        if role_name not in self._cache_timestamps:
            return False
        
        cache_age = datetime.now(timezone.utc) - self._cache_timestamps[role_name]
        return cache_age.total_seconds() < self.cache_ttl
    
    def _cache_role(self, role: Role):
        """Cache role in memory."""
        self._role_cache[role.name] = role
        self._cache_timestamps[role.name] = datetime.now(timezone.utc)
    
    def _invalidate_cache(self, role_name: str):
        """Invalidate cached role."""
        self._role_cache.pop(role_name, None)
        self._cache_timestamps.pop(role_name, None)
    
    async def create_role(self, role: Role) -> bool:
        """Create a new role."""
        try:
            if not self.redis:
                raise RoleError("Redis connection not initialized")
            
            # Check if role already exists
            if await self.role_exists(role.name):
                raise RoleError(f"Role already exists: {role.name}")
            
            # Store role in Redis
            role_key = f"{self.role_prefix}{role.name}"
            role_data = json.dumps(role.to_dict())
            
            await self.redis.set(role_key, role_data)
            
            # Cache the role
            self._cache_role(role)
            
            self.metrics["roles_created"] += 1
            logger.info(f"Created role: {role.name}")
            
            return True
            
        except RoleError:
            raise
        except Exception as e:
            logger.error(f"Failed to create role: {e}")
            raise RoleError(f"Role creation failed: {e}")
    
    async def get_role(self, role_name: str) -> Optional[Role]:
        """Get role by name with caching."""
        try:
            # Check cache first
            if role_name in self._role_cache and self._is_cache_valid(role_name):
                self.metrics["cache_hits"] += 1
                return self._role_cache[role_name]
            
            if not self.redis:
                raise RoleError("Redis connection not initialized")
            
            # Get from Redis
            role_key = f"{self.role_prefix}{role_name}"
            role_data_str = await self.redis.get(role_key)
            
            if not role_data_str:
                self.metrics["cache_misses"] += 1
                return None
            
            role_data = json.loads(role_data_str)
            role = Role.from_dict(role_data)
            
            # Cache the role
            self._cache_role(role)
            self.metrics["cache_misses"] += 1
            
            return role
            
        except RoleError:
            raise
        except Exception as e:
            logger.error(f"Failed to get role: {e}")
            return None
    
    async def update_role(self, role: Role, updated_by: Optional[str] = None) -> bool:
        """Update an existing role."""
        try:
            if not self.redis:
                raise RoleError("Redis connection not initialized")
            
            # Check if role exists
            if not await self.role_exists(role.name):
                raise RoleError(f"Role not found: {role.name}")
            
            # Update metadata
            role.updated_at = datetime.now(timezone.utc)
            role.updated_by = updated_by
            
            # Store updated role
            role_key = f"{self.role_prefix}{role.name}"
            role_data = json.dumps(role.to_dict())
            
            await self.redis.set(role_key, role_data)
            
            # Update cache
            self._cache_role(role)
            
            self.metrics["roles_updated"] += 1
            logger.info(f"Updated role: {role.name}")
            
            return True
            
        except RoleError:
            raise
        except Exception as e:
            logger.error(f"Failed to update role: {e}")
            raise RoleError(f"Role update failed: {e}")
    
    async def delete_role(self, role_name: str) -> bool:
        """Delete a role."""
        try:
            if not self.redis:
                raise RoleError("Redis connection not initialized")
            
            # Check if it's a system role
            if role_name in self._system_roles:
                raise RoleError(f"Cannot delete system role: {role_name}")
            
            # Delete from Redis
            role_key = f"{self.role_prefix}{role_name}"
            deleted = await self.redis.delete(role_key)
            
            if deleted:
                # Invalidate cache
                self._invalidate_cache(role_name)
                
                self.metrics["roles_deleted"] += 1
                logger.info(f"Deleted role: {role_name}")
            
            return deleted > 0
            
        except RoleError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete role: {e}")
            return False
    
    async def role_exists(self, role_name: str) -> bool:
        """Check if role exists."""
        try:
            if not self.redis:
                return False
            
            role_key = f"{self.role_prefix}{role_name}"
            exists = await self.redis.exists(role_key)
            return exists > 0
            
        except Exception as e:
            logger.error(f"Error checking role existence: {e}")
            return False
    
    async def list_roles(
        self,
        role_type: Optional[RoleType] = None,
        active_only: bool = True
    ) -> List[Role]:
        """List all roles with optional filtering."""
        try:
            if not self.redis:
                raise RoleError("Redis connection not initialized")
            
            roles = []
            
            # Get all role keys
            async for key in self.redis.scan_iter(match=f"{self.role_prefix}*"):
                try:
                    role_data_str = await self.redis.get(key)
                    if role_data_str:
                        role_data = json.loads(role_data_str)
                        role = Role.from_dict(role_data)
                        
                        # Apply filters
                        if active_only and not role.is_active:
                            continue
                        
                        if role_type and role.role_type != role_type:
                            continue
                        
                        roles.append(role)
                        
                except Exception as e:
                    logger.error(f"Error processing role key {key}: {e}")
                    continue
            
            return sorted(roles, key=lambda r: r.name)
            
        except RoleError:
            raise
        except Exception as e:
            logger.error(f"Failed to list roles: {e}")
            return []
    
    async def assign_role_to_user(self, user_id: str, role_name: str) -> bool:
        """Assign role to user."""
        try:
            if not self.redis:
                raise RoleError("Redis connection not initialized")
            
            # Verify role exists
            if not await self.role_exists(role_name):
                raise RoleError(f"Role not found: {role_name}")
            
            # Add to user's roles set
            user_roles_key = f"{self.user_roles_prefix}{user_id}"
            await self.redis.sadd(user_roles_key, role_name)
            
            logger.info(f"Assigned role {role_name} to user {user_id}")
            return True
            
        except RoleError:
            raise
        except Exception as e:
            logger.error(f"Failed to assign role: {e}")
            return False
    
    async def remove_role_from_user(self, user_id: str, role_name: str) -> bool:
        """Remove role from user."""
        try:
            if not self.redis:
                raise RoleError("Redis connection not initialized")
            
            # Remove from user's roles set
            user_roles_key = f"{self.user_roles_prefix}{user_id}"
            removed = await self.redis.srem(user_roles_key, role_name)
            
            if removed:
                logger.info(f"Removed role {role_name} from user {user_id}")
            
            return removed > 0
            
        except Exception as e:
            logger.error(f"Failed to remove role: {e}")
            return False
    
    async def get_user_roles(self, user_id: str) -> List[Role]:
        """Get all roles assigned to user."""
        try:
            if not self.redis:
                raise RoleError("Redis connection not initialized")
            
            user_roles_key = f"{self.user_roles_prefix}{user_id}"
            role_names = await self.redis.smembers(user_roles_key)
            
            roles = []
            for role_name in role_names:
                role = await self.get_role(role_name)
                if role and role.is_active:
                    roles.append(role)
            
            return roles
            
        except RoleError:
            raise
        except Exception as e:
            logger.error(f"Failed to get user roles: {e}")
            return []
    
    async def user_has_role(self, user_id: str, role_name: str) -> bool:
        """Check if user has specific role."""
        try:
            if not self.redis:
                return False
            
            user_roles_key = f"{self.user_roles_prefix}{user_id}"
            has_role = await self.redis.sismember(user_roles_key, role_name)
            
            return bool(has_role)
            
        except Exception as e:
            logger.error(f"Error checking user role: {e}")
            return False
    
    async def get_role_statistics(self) -> Dict[str, Any]:
        """Get role management statistics."""
        try:
            if not self.redis:
                return {"error": "Redis not connected"}
            
            # Count roles by type
            role_counts = {}
            total_roles = 0
            active_roles = 0
            
            async for key in self.redis.scan_iter(match=f"{self.role_prefix}*"):
                try:
                    role_data_str = await self.redis.get(key)
                    if role_data_str:
                        role_data = json.loads(role_data_str)
                        role_type = role_data.get("role_type", "unknown")
                        role_counts[role_type] = role_counts.get(role_type, 0) + 1
                        total_roles += 1
                        
                        if role_data.get("is_active", True):
                            active_roles += 1
                            
                except Exception:
                    continue
            
            # Count users with roles
            users_with_roles = 0
            async for key in self.redis.scan_iter(match=f"{self.user_roles_prefix}*"):
                users_with_roles += 1
            
            return {
                "total_roles": total_roles,
                "active_roles": active_roles,
                "role_counts_by_type": role_counts,
                "users_with_roles": users_with_roles,
                "cache_statistics": {
                    "cached_roles": len(self._role_cache),
                    "cache_hits": self.metrics["cache_hits"],
                    "cache_misses": self.metrics["cache_misses"]
                },
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
            
            # Check system roles
            system_roles_ok = 0
            for role_name in self._system_roles.keys():
                if await self.role_exists(role_name):
                    system_roles_ok += 1
            
            statistics = await self.get_role_statistics()
            
            return {
                "status": "healthy",
                "redis_connected": True,
                "system_roles": f"{system_roles_ok}/{len(self._system_roles)}",
                "statistics": statistics
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()