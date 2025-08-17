"""Permission system for MAOS RBAC."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class PermissionType(Enum):
    """Types of permissions in MAOS."""
    # Agent Management
    AGENT_CREATE = "agent:create"
    AGENT_READ = "agent:read"
    AGENT_UPDATE = "agent:update"
    AGENT_DELETE = "agent:delete"
    AGENT_EXECUTE = "agent:execute"
    AGENT_MONITOR = "agent:monitor"
    
    # Task Management
    TASK_CREATE = "task:create"
    TASK_READ = "task:read"
    TASK_UPDATE = "task:update"
    TASK_DELETE = "task:delete"
    TASK_ASSIGN = "task:assign"
    TASK_MONITOR = "task:monitor"
    
    # Resource Management
    RESOURCE_CREATE = "resource:create"
    RESOURCE_READ = "resource:read"
    RESOURCE_UPDATE = "resource:update"
    RESOURCE_DELETE = "resource:delete"
    RESOURCE_ALLOCATE = "resource:allocate"
    
    # Communication
    MESSAGE_SEND = "message:send"
    MESSAGE_RECEIVE = "message:receive"
    MESSAGE_BROADCAST = "message:broadcast"
    
    # System Administration
    SYSTEM_CONFIG = "system:config"
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_BACKUP = "system:backup"
    SYSTEM_RESTART = "system:restart"
    SYSTEM_SHUTDOWN = "system:shutdown"
    
    # Security Management
    SECURITY_READ = "security:read"
    SECURITY_CONFIG = "security:config"
    SECURITY_AUDIT = "security:audit"
    SECURITY_KEYS = "security:keys"
    
    # Orchestration
    ORCHESTRATE_READ = "orchestrate:read"
    ORCHESTRATE_WRITE = "orchestrate:write"
    ORCHESTRATE_EXECUTE = "orchestrate:execute"
    ORCHESTRATE_MONITOR = "orchestrate:monitor"
    
    # API Access
    API_READ = "api:read"
    API_WRITE = "api:write"
    API_ADMIN = "api:admin"


@dataclass
class Permission:
    """Individual permission with scope and conditions."""
    name: str
    permission_type: PermissionType
    resource: Optional[str] = None  # Specific resource (e.g., agent_id, task_id)
    scope: Set[str] = field(default_factory=set)  # Scope limitations
    conditions: Dict[str, Any] = field(default_factory=dict)  # Conditional access
    granted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    granted_by: Optional[str] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate permission after initialization."""
        if not self.name:
            self.name = self.permission_type.value
        
        # Convert scope to set if it's a list
        if isinstance(self.scope, list):
            self.scope = set(self.scope)
    
    def is_valid(self) -> bool:
        """Check if permission is currently valid."""
        try:
            # Check expiration
            if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking permission validity: {e}")
            return False
    
    def matches(
        self,
        permission_type: PermissionType,
        resource: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Check if this permission matches the requested access."""
        try:
            # Check if permission is valid
            if not self.is_valid():
                return False
            
            # Check permission type
            if self.permission_type != permission_type:
                return False
            
            # Check resource scope
            if self.resource and resource and self.resource != resource:
                # Check if resource matches scope patterns
                if not self._matches_scope(resource):
                    return False
            
            # Check conditions
            if self.conditions and not self._check_conditions(context or {}):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error matching permission: {e}")
            return False
    
    def _matches_scope(self, resource: str) -> bool:
        """Check if resource matches permission scope."""
        try:
            if not self.scope:
                return True  # No scope restrictions
            
            for scope_pattern in self.scope:
                # Simple wildcard matching
                if scope_pattern == "*":
                    return True
                
                # Prefix matching
                if scope_pattern.endswith("*"):
                    if resource.startswith(scope_pattern[:-1]):
                        return True
                
                # Exact matching
                if scope_pattern == resource:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking scope: {e}")
            return False
    
    def _check_conditions(self, context: Dict[str, Any]) -> bool:
        """Check if context satisfies permission conditions."""
        try:
            for condition_key, condition_value in self.conditions.items():
                context_value = context.get(condition_key)
                
                # Handle different condition types
                if isinstance(condition_value, dict):
                    # Complex condition (e.g., {"operator": "in", "values": [...]})
                    operator = condition_value.get("operator", "eq")
                    values = condition_value.get("values", condition_value.get("value"))
                    
                    if operator == "eq" and context_value != values:
                        return False
                    elif operator == "in" and context_value not in values:
                        return False
                    elif operator == "not_in" and context_value in values:
                        return False
                    elif operator == "gt" and context_value <= values:
                        return False
                    elif operator == "lt" and context_value >= values:
                        return False
                
                elif context_value != condition_value:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking conditions: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert permission to dictionary."""
        return {
            "name": self.name,
            "permission_type": self.permission_type.value,
            "resource": self.resource,
            "scope": list(self.scope),
            "conditions": self.conditions,
            "granted_at": self.granted_at.isoformat(),
            "granted_by": self.granted_by,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Permission":
        """Create permission from dictionary."""
        try:
            return cls(
                name=data["name"],
                permission_type=PermissionType(data["permission_type"]),
                resource=data.get("resource"),
                scope=set(data.get("scope", [])),
                conditions=data.get("conditions", {}),
                granted_at=datetime.fromisoformat(data["granted_at"]),
                granted_by=data.get("granted_by"),
                expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
                metadata=data.get("metadata", {})
            )
        except Exception as e:
            logger.error(f"Error creating permission from dict: {e}")
            raise ValueError(f"Invalid permission data: {e}")


class PermissionSet:
    """Collection of permissions with efficient lookup."""
    
    def __init__(self, permissions: Optional[List[Permission]] = None):
        self.permissions: List[Permission] = permissions or []
        self._index_by_type: Dict[PermissionType, List[Permission]] = {}
        self._build_index()
    
    def _build_index(self):
        """Build index for efficient permission lookups."""
        self._index_by_type.clear()
        
        for permission in self.permissions:
            if permission.permission_type not in self._index_by_type:
                self._index_by_type[permission.permission_type] = []
            self._index_by_type[permission.permission_type].append(permission)
    
    def add_permission(self, permission: Permission):
        """Add permission to set."""
        if permission not in self.permissions:
            self.permissions.append(permission)
            
            # Update index
            if permission.permission_type not in self._index_by_type:
                self._index_by_type[permission.permission_type] = []
            self._index_by_type[permission.permission_type].append(permission)
    
    def remove_permission(self, permission: Permission):
        """Remove permission from set."""
        if permission in self.permissions:
            self.permissions.remove(permission)
            
            # Update index
            if permission.permission_type in self._index_by_type:
                self._index_by_type[permission.permission_type].remove(permission)
    
    def has_permission(
        self,
        permission_type: PermissionType,
        resource: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Check if permission set contains a matching permission."""
        # Get permissions of the requested type
        matching_permissions = self._index_by_type.get(permission_type, [])
        
        # Check each permission
        for permission in matching_permissions:
            if permission.matches(permission_type, resource, context):
                return True
        
        return False
    
    def get_permissions(
        self,
        permission_type: Optional[PermissionType] = None,
        resource: Optional[str] = None,
        valid_only: bool = True
    ) -> List[Permission]:
        """Get filtered list of permissions."""
        permissions = self.permissions if permission_type is None else self._index_by_type.get(permission_type, [])
        
        result = []
        for permission in permissions:
            # Filter by validity
            if valid_only and not permission.is_valid():
                continue
            
            # Filter by resource
            if resource and permission.resource and permission.resource != resource:
                if not permission._matches_scope(resource):
                    continue
            
            result.append(permission)
        
        return result
    
    def cleanup_expired(self) -> int:
        """Remove expired permissions and return count of removed."""
        initial_count = len(self.permissions)
        self.permissions = [p for p in self.permissions if p.is_valid()]
        self._build_index()
        return initial_count - len(self.permissions)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert permission set to dictionary."""
        return {
            "permissions": [p.to_dict() for p in self.permissions],
            "count": len(self.permissions)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PermissionSet":
        """Create permission set from dictionary."""
        permissions = [Permission.from_dict(p) for p in data.get("permissions", [])]
        return cls(permissions)


# Predefined permission sets for common roles
ADMIN_PERMISSIONS = PermissionSet([
    Permission("admin_all", PermissionType.SYSTEM_CONFIG),
    Permission("admin_security", PermissionType.SECURITY_CONFIG),
    Permission("admin_agents", PermissionType.AGENT_CREATE),
    Permission("admin_tasks", PermissionType.TASK_CREATE),
    Permission("admin_resources", PermissionType.RESOURCE_CREATE),
    Permission("admin_orchestrate", PermissionType.ORCHESTRATE_EXECUTE),
    Permission("admin_api", PermissionType.API_ADMIN),
])

OPERATOR_PERMISSIONS = PermissionSet([
    Permission("operator_monitor", PermissionType.SYSTEM_MONITOR),
    Permission("operator_agents", PermissionType.AGENT_READ),
    Permission("operator_tasks", PermissionType.TASK_READ),
    Permission("operator_resources", PermissionType.RESOURCE_READ),
    Permission("operator_orchestrate", PermissionType.ORCHESTRATE_MONITOR),
    Permission("operator_api", PermissionType.API_READ),
])

AGENT_PERMISSIONS = PermissionSet([
    Permission("agent_message", PermissionType.MESSAGE_SEND),
    Permission("agent_receive", PermissionType.MESSAGE_RECEIVE),
    Permission("agent_task", PermissionType.TASK_READ),
    Permission("agent_resource", PermissionType.RESOURCE_READ),
])

READONLY_PERMISSIONS = PermissionSet([
    Permission("readonly_agents", PermissionType.AGENT_READ),
    Permission("readonly_tasks", PermissionType.TASK_READ),
    Permission("readonly_resources", PermissionType.RESOURCE_READ),
    Permission("readonly_api", PermissionType.API_READ),
])