"""Comprehensive RBAC manager integrating permissions, roles, and policies."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
import asyncio

from .permissions import Permission, PermissionSet, PermissionType
from .roles import Role, RoleManager, RoleError
from .policies import AccessPolicy, PolicyManager, PolicyError

logger = logging.getLogger(__name__)


class RBACError(Exception):
    """RBAC system errors."""
    pass


class AccessDecision:
    """Access control decision with reasoning."""
    
    def __init__(
        self,
        allowed: bool,
        reason: str,
        applicable_roles: List[str] = None,
        applicable_policies: List[str] = None,
        permissions_used: List[str] = None
    ):
        self.allowed = allowed
        self.reason = reason
        self.applicable_roles = applicable_roles or []
        self.applicable_policies = applicable_policies or []
        self.permissions_used = permissions_used or []
        self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert decision to dictionary."""
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "applicable_roles": self.applicable_roles,
            "applicable_policies": self.applicable_policies,
            "permissions_used": self.permissions_used,
            "timestamp": self.timestamp.isoformat()
        }


class RBACManager:
    """Comprehensive Role-Based Access Control manager."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        enable_caching: bool = True,
        cache_ttl: int = 1800,  # 30 minutes
        default_deny: bool = True,
        audit_decisions: bool = True
    ):
        self.redis_url = redis_url
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        self.default_deny = default_deny
        self.audit_decisions = audit_decisions
        
        # Component managers
        self.role_manager = RoleManager(redis_url=redis_url, redis_db=3)
        self.policy_manager = PolicyManager(
            redis_url=redis_url,
            redis_db=4,
            default_decision=not default_deny
        )
        
        # Access decision audit log
        self.decision_log: List[AccessDecision] = []
        self.max_log_size = 10000
        
        # Performance metrics
        self.metrics = {
            "access_checks": 0,
            "access_granted": 0,
            "access_denied": 0,
            "role_based_decisions": 0,
            "policy_based_decisions": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0
        }
        
        # Access decision cache
        self._decision_cache: Dict[str, Tuple[AccessDecision, datetime]] = {}
        
        logger.info("RBAC manager initialized")
    
    async def initialize(self):
        """Initialize RBAC system."""
        try:
            # Initialize component managers
            await self.role_manager.connect()
            await self.policy_manager.connect()
            
            logger.info("RBAC system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RBAC system: {e}")
            raise RBACError(f"RBAC initialization failed: {e}")
    
    async def shutdown(self):
        """Shutdown RBAC system."""
        try:
            await self.role_manager.disconnect()
            await self.policy_manager.disconnect()
            
            logger.info("RBAC system shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during RBAC shutdown: {e}")
    
    def _get_decision_cache_key(
        self,
        user_id: str,
        action: PermissionType,
        resource: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate cache key for access decisions."""
        import hashlib
        import json
        
        context_str = json.dumps(context, sort_keys=True, default=str)
        cache_data = f"{user_id}:{action.value}:{resource}:{context_str}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _is_decision_cached(self, cache_key: str) -> bool:
        """Check if access decision is cached and still valid."""
        if not self.enable_caching or cache_key not in self._decision_cache:
            return False
        
        _, timestamp = self._decision_cache[cache_key]
        cache_age = datetime.now(timezone.utc) - timestamp
        return cache_age.total_seconds() < self.cache_ttl
    
    def _cache_decision(self, cache_key: str, decision: AccessDecision):
        """Cache access decision."""
        if not self.enable_caching:
            return
        
        self._decision_cache[cache_key] = (decision, datetime.now(timezone.utc))
        
        # Limit cache size
        if len(self._decision_cache) > 1000:
            # Remove oldest entries
            oldest_key = min(
                self._decision_cache.keys(),
                key=lambda k: self._decision_cache[k][1]
            )
            del self._decision_cache[oldest_key]
    
    def _log_decision(self, decision: AccessDecision):
        """Log access decision for audit."""
        if not self.audit_decisions:
            return
        
        self.decision_log.append(decision)
        
        # Limit log size
        if len(self.decision_log) > self.max_log_size:
            self.decision_log = self.decision_log[-self.max_log_size//2:]
    
    async def check_access(
        self,
        user_id: str,
        action: PermissionType,
        resource: str = "*",
        context: Optional[Dict[str, Any]] = None
    ) -> AccessDecision:
        """Check if user has access to perform action on resource."""
        try:
            self.metrics["access_checks"] += 1
            context = context or {}
            
            # Add standard context information
            context.update({
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "hour": datetime.now().hour
            })
            
            # Check decision cache
            cache_key = self._get_decision_cache_key(user_id, action, resource, context)
            if self._is_decision_cached(cache_key):
                decision, _ = self._decision_cache[cache_key]
                self.metrics["cache_hits"] += 1
                return decision
            
            self.metrics["cache_misses"] += 1
            
            # Get user roles
            user_roles = await self.role_manager.get_user_roles(user_id)
            role_names = [role.name for role in user_roles]
            
            # Check role-based permissions
            role_decision = await self._check_role_based_access(
                user_roles, action, resource, context
            )
            
            # Check policy-based access
            policy_decision = await self.policy_manager.evaluate_access(
                subject=user_id,
                action=action,
                resource=resource,
                context=context,
                user_roles=role_names
            )
            
            # Combine decisions
            decision = self._combine_decisions(
                role_decision, policy_decision, user_id, action, resource, role_names
            )
            
            # Update metrics
            if decision.allowed:
                self.metrics["access_granted"] += 1
            else:
                self.metrics["access_denied"] += 1
            
            # Cache and log decision
            self._cache_decision(cache_key, decision)
            self._log_decision(decision)
            
            logger.debug(f"Access check: {user_id} -> {action.value} on {resource} = {decision.allowed}")
            return decision
            
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Error checking access: {e}")
            
            # Return safe default
            decision = AccessDecision(
                allowed=not self.default_deny,
                reason=f"Error during access check: {str(e)}"
            )
            return decision
    
    async def _check_role_based_access(
        self,
        user_roles: List[Role],
        action: PermissionType,
        resource: str,
        context: Dict[str, Any]
    ) -> Optional[bool]:
        """Check access based on user roles and permissions."""
        try:
            applicable_roles = []
            applicable_permissions = []
            
            for role in user_roles:
                if not role.is_active:
                    continue
                
                # Check if role has the required permission
                if role.has_permission(action, resource, context):
                    applicable_roles.append(role.name)
                    
                    # Get specific permissions that match
                    matching_permissions = role.permissions.get_permissions(
                        permission_type=action,
                        resource=resource
                    )
                    applicable_permissions.extend([p.name for p in matching_permissions])
            
            if applicable_roles:
                self.metrics["role_based_decisions"] += 1
                return True
            
            return None  # No role-based decision
            
        except Exception as e:
            logger.error(f"Error in role-based access check: {e}")
            return None
    
    def _combine_decisions(
        self,
        role_decision: Optional[bool],
        policy_decision: bool,
        user_id: str,
        action: PermissionType,
        resource: str,
        role_names: List[str]
    ) -> AccessDecision:
        """Combine role-based and policy-based decisions."""
        try:
            # Policy decisions take precedence (explicit deny/allow)
            if not policy_decision:
                self.metrics["policy_based_decisions"] += 1
                return AccessDecision(
                    allowed=False,
                    reason="Access denied by security policy",
                    applicable_roles=role_names,
                    applicable_policies=["security_policy"]
                )
            
            # If policies allow, check role-based permissions
            if role_decision is True:
                self.metrics["role_based_decisions"] += 1
                return AccessDecision(
                    allowed=True,
                    reason="Access granted based on user roles",
                    applicable_roles=role_names
                )
            
            # No explicit permissions or role access
            return AccessDecision(
                allowed=not self.default_deny,
                reason="No explicit permissions found, using default policy",
                applicable_roles=role_names
            )
            
        except Exception as e:
            logger.error(f"Error combining access decisions: {e}")
            return AccessDecision(
                allowed=not self.default_deny,
                reason=f"Error in decision combination: {str(e)}"
            )
    
    async def grant_permission(
        self,
        user_id: str,
        permission_type: PermissionType,
        resource: Optional[str] = None,
        expires_in_hours: Optional[int] = None,
        granted_by: Optional[str] = None
    ) -> bool:
        """Grant specific permission to user via temporary role."""
        try:
            # Create temporary role name
            temp_role_name = f"temp_{user_id}_{permission_type.value}_{datetime.now().timestamp()}"
            
            # Create permission
            permission = Permission(
                name=f"{permission_type.value}_permission",
                permission_type=permission_type,
                resource=resource,
                granted_by=granted_by,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=expires_in_hours) if expires_in_hours else None
            )
            
            # Create temporary role
            temp_role = Role(
                name=temp_role_name,
                role_type=RoleType.CUSTOM,
                description=f"Temporary role for {permission_type.value} permission",
                created_by=granted_by,
                metadata={"temporary": True, "expires_hours": expires_in_hours}
            )
            temp_role.add_permission(permission)
            
            # Create and assign role
            await self.role_manager.create_role(temp_role)
            await self.role_manager.assign_role_to_user(user_id, temp_role_name)
            
            # Clear decision cache for user
            self._clear_user_cache(user_id)
            
            logger.info(f"Granted permission {permission_type.value} to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to grant permission: {e}")
            return False
    
    async def revoke_permission(
        self,
        user_id: str,
        permission_type: PermissionType,
        resource: Optional[str] = None
    ) -> bool:
        """Revoke specific permission from user."""
        try:
            # Get user roles
            user_roles = await self.role_manager.get_user_roles(user_id)
            
            # Find and remove temporary roles with matching permission
            removed_count = 0
            for role in user_roles:
                if not role.metadata.get("temporary"):
                    continue
                
                # Check if role has the permission to revoke
                if role.has_permission(permission_type, resource):
                    await self.role_manager.remove_role_from_user(user_id, role.name)
                    await self.role_manager.delete_role(role.name)
                    removed_count += 1
            
            # Clear decision cache for user
            self._clear_user_cache(user_id)
            
            logger.info(f"Revoked permission {permission_type.value} from user {user_id}")
            return removed_count > 0
            
        except Exception as e:
            logger.error(f"Failed to revoke permission: {e}")
            return False
    
    def _clear_user_cache(self, user_id: str):
        """Clear cached decisions for a specific user."""
        try:
            keys_to_remove = []
            for cache_key in self._decision_cache.keys():
                # Cache key format includes user_id at the start
                if cache_key.startswith(user_id):
                    keys_to_remove.append(cache_key)
            
            for key in keys_to_remove:
                del self._decision_cache[key]
                
        except Exception as e:
            logger.error(f"Error clearing user cache: {e}")
    
    async def get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive view of user permissions."""
        try:
            # Get user roles
            user_roles = await self.role_manager.get_user_roles(user_id)
            
            # Aggregate all permissions
            all_permissions = PermissionSet()
            role_info = []
            
            for role in user_roles:
                if role.is_active:
                    role_info.append({
                        "name": role.name,
                        "type": role.role_type.value,
                        "description": role.description,
                        "permission_count": len(role.permissions.permissions)
                    })
                    
                    # Add role permissions to aggregate
                    for permission in role.permissions.permissions:
                        all_permissions.add_permission(permission)
            
            # Group permissions by type
            permissions_by_type = {}
            for permission in all_permissions.permissions:
                perm_type = permission.permission_type.value
                if perm_type not in permissions_by_type:
                    permissions_by_type[perm_type] = []
                permissions_by_type[perm_type].append({
                    "name": permission.name,
                    "resource": permission.resource,
                    "scope": list(permission.scope),
                    "expires_at": permission.expires_at.isoformat() if permission.expires_at else None
                })
            
            return {
                "user_id": user_id,
                "roles": role_info,
                "permissions_by_type": permissions_by_type,
                "total_permissions": len(all_permissions.permissions),
                "active_roles": len([r for r in user_roles if r.is_active])
            }
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return {"error": str(e)}
    
    async def cleanup_expired_permissions(self) -> int:
        """Clean up expired permissions and temporary roles."""
        try:
            cleanup_count = 0
            
            # Get all roles
            all_roles = await self.role_manager.list_roles(active_only=False)
            
            for role in all_roles:
                # Clean up expired permissions within roles
                expired_count = role.permissions.cleanup_expired()
                if expired_count > 0:
                    await self.role_manager.update_role(role)
                    cleanup_count += expired_count
                
                # Remove temporary roles that are expired
                if role.metadata.get("temporary"):
                    expires_hours = role.metadata.get("expires_hours")
                    if expires_hours:
                        role_age = datetime.now(timezone.utc) - role.created_at
                        if role_age.total_seconds() > expires_hours * 3600:
                            await self.role_manager.delete_role(role.name)
                            cleanup_count += 1
            
            # Clear decision cache to ensure fresh evaluations
            self._decision_cache.clear()
            
            logger.info(f"Cleaned up {cleanup_count} expired permissions and roles")
            return cleanup_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0
    
    async def get_access_statistics(self) -> Dict[str, Any]:
        """Get comprehensive access control statistics."""
        try:
            # Get component statistics
            role_stats = await self.role_manager.get_role_statistics()
            policy_stats = await self.policy_manager.get_policy_statistics()
            
            # Recent access decisions summary
            recent_decisions = self.decision_log[-100:] if self.decision_log else []
            recent_allowed = sum(1 for d in recent_decisions if d.allowed)
            recent_denied = len(recent_decisions) - recent_allowed
            
            return {
                "rbac_metrics": self.metrics,
                "role_statistics": role_stats,
                "policy_statistics": policy_stats,
                "recent_access_decisions": {
                    "total": len(recent_decisions),
                    "allowed": recent_allowed,
                    "denied": recent_denied
                },
                "cache_statistics": {
                    "decision_cache_size": len(self._decision_cache),
                    "decision_log_size": len(self.decision_log)
                },
                "configuration": {
                    "default_deny": self.default_deny,
                    "caching_enabled": self.enable_caching,
                    "audit_enabled": self.audit_decisions
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            # Check component health
            role_health = await self.role_manager.health_check()
            policy_health = await self.policy_manager.health_check()
            
            # Overall health status
            overall_status = "healthy"
            issues = []
            
            if role_health.get("status") != "healthy":
                overall_status = "degraded"
                issues.append("Role manager unhealthy")
            
            if policy_health.get("status") != "healthy":
                overall_status = "degraded"
                issues.append("Policy manager unhealthy")
            
            # Test access check functionality
            try:
                test_decision = await self.check_access(
                    "health_check_user",
                    PermissionType.AGENT_READ,
                    "health_check_resource"
                )
                if test_decision.reason.startswith("Error"):
                    overall_status = "degraded"
                    issues.append("Access check functionality impaired")
            except Exception:
                overall_status = "unhealthy"
                issues.append("Access check failed")
            
            return {
                "status": overall_status,
                "issues": issues,
                "component_health": {
                    "role_manager": role_health,
                    "policy_manager": policy_health
                },
                "statistics": await self.get_access_statistics()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    # Context manager support
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown()