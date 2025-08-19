"""Access policies and policy management for MAOS RBAC."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import aioredis

from .permissions import PermissionType
from .roles import Role

logger = logging.getLogger(__name__)


class PolicyEffect(Enum):
    """Policy decision effects."""
    ALLOW = "allow"
    DENY = "deny"


class PolicyConditionOperator(Enum):
    """Operators for policy conditions."""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX = "regex"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_EQUAL = "gte"
    LESS_EQUAL = "lte"


@dataclass
class PolicyCondition:
    """Individual condition in an access policy."""
    attribute: str  # Attribute to check (e.g., "time", "ip_address", "agent_id")
    operator: PolicyConditionOperator
    value: Union[str, int, float, List[Any]]
    description: Optional[str] = None
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate condition against context."""
        try:
            context_value = context.get(self.attribute)
            
            if context_value is None:
                return False
            
            if self.operator == PolicyConditionOperator.EQUALS:
                return context_value == self.value
            elif self.operator == PolicyConditionOperator.NOT_EQUALS:
                return context_value != self.value
            elif self.operator == PolicyConditionOperator.IN:
                return context_value in self.value
            elif self.operator == PolicyConditionOperator.NOT_IN:
                return context_value not in self.value
            elif self.operator == PolicyConditionOperator.CONTAINS:
                return str(self.value) in str(context_value)
            elif self.operator == PolicyConditionOperator.NOT_CONTAINS:
                return str(self.value) not in str(context_value)
            elif self.operator == PolicyConditionOperator.STARTS_WITH:
                return str(context_value).startswith(str(self.value))
            elif self.operator == PolicyConditionOperator.ENDS_WITH:
                return str(context_value).endswith(str(self.value))
            elif self.operator == PolicyConditionOperator.REGEX:
                return bool(re.match(str(self.value), str(context_value)))
            elif self.operator == PolicyConditionOperator.GREATER_THAN:
                return float(context_value) > float(self.value)
            elif self.operator == PolicyConditionOperator.LESS_THAN:
                return float(context_value) < float(self.value)
            elif self.operator == PolicyConditionOperator.GREATER_EQUAL:
                return float(context_value) >= float(self.value)
            elif self.operator == PolicyConditionOperator.LESS_EQUAL:
                return float(context_value) <= float(self.value)
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating policy condition: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert condition to dictionary."""
        return {
            "attribute": self.attribute,
            "operator": self.operator.value,
            "value": self.value,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PolicyCondition":
        """Create condition from dictionary."""
        return cls(
            attribute=data["attribute"],
            operator=PolicyConditionOperator(data["operator"]),
            value=data["value"],
            description=data.get("description")
        )


@dataclass
class AccessPolicy:
    """Access control policy with conditions and effects."""
    name: str
    description: str
    effect: PolicyEffect
    subjects: Set[str] = field(default_factory=set)  # Users, roles, or groups
    resources: Set[str] = field(default_factory=set)  # Resources or resource patterns
    actions: Set[PermissionType] = field(default_factory=set)  # Permitted actions
    conditions: List[PolicyCondition] = field(default_factory=list)  # Additional conditions
    priority: int = 0  # Higher priority policies are evaluated first
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate policy after initialization."""
        if isinstance(self.subjects, list):
            self.subjects = set(self.subjects)
        if isinstance(self.resources, list):
            self.resources = set(self.resources)
        if isinstance(self.actions, list):
            self.actions = set(PermissionType(action) if isinstance(action, str) else action for action in self.actions)
    
    def matches_subject(self, subject: str, user_roles: Optional[List[str]] = None) -> bool:
        """Check if policy applies to subject (user or role)."""
        if not self.subjects:
            return True  # Applies to all subjects
        
        # Direct subject match
        if subject in self.subjects:
            return True
        
        # Check if any user roles match
        if user_roles:
            for role in user_roles:
                if role in self.subjects:
                    return True
        
        # Check for wildcard patterns
        for policy_subject in self.subjects:
            if policy_subject == "*":
                return True
            if policy_subject.endswith("*") and subject.startswith(policy_subject[:-1]):
                return True
        
        return False
    
    def matches_resource(self, resource: str) -> bool:
        """Check if policy applies to resource."""
        if not self.resources:
            return True  # Applies to all resources
        
        # Direct resource match
        if resource in self.resources:
            return True
        
        # Check for wildcard patterns
        for policy_resource in self.resources:
            if policy_resource == "*":
                return True
            if policy_resource.endswith("*") and resource.startswith(policy_resource[:-1]):
                return True
            if policy_resource.startswith("*") and resource.endswith(policy_resource[1:]):
                return True
        
        return False
    
    def matches_action(self, action: PermissionType) -> bool:
        """Check if policy applies to action."""
        if not self.actions:
            return True  # Applies to all actions
        
        return action in self.actions
    
    def evaluate_conditions(self, context: Dict[str, Any]) -> bool:
        """Evaluate all policy conditions."""
        if not self.conditions:
            return True  # No conditions to check
        
        # All conditions must be satisfied
        for condition in self.conditions:
            if not condition.evaluate(context):
                return False
        
        return True
    
    def evaluate(
        self,
        subject: str,
        action: PermissionType,
        resource: str,
        context: Dict[str, Any],
        user_roles: Optional[List[str]] = None
    ) -> Optional[bool]:
        """Evaluate policy against access request."""
        try:
            if not self.is_active:
                return None  # Inactive policy
            
            # Check if policy applies
            if not self.matches_subject(subject, user_roles):
                return None
            
            if not self.matches_resource(resource):
                return None
            
            if not self.matches_action(action):
                return None
            
            # Evaluate conditions
            if not self.evaluate_conditions(context):
                return None
            
            # Return policy decision
            return self.effect == PolicyEffect.ALLOW
            
        except Exception as e:
            logger.error(f"Error evaluating policy {self.name}: {e}")
            return None  # Default to no decision on error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "effect": self.effect.value,
            "subjects": list(self.subjects),
            "resources": list(self.resources),
            "actions": [action.value for action in self.actions],
            "conditions": [condition.to_dict() for condition in self.conditions],
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccessPolicy":
        """Create policy from dictionary."""
        try:
            actions = []
            for action in data.get("actions", []):
                try:
                    actions.append(PermissionType(action))
                except ValueError:
                    logger.warning(f"Unknown permission type: {action}")
            
            conditions = [PolicyCondition.from_dict(c) for c in data.get("conditions", [])]
            
            return cls(
                name=data["name"],
                description=data["description"],
                effect=PolicyEffect(data["effect"]),
                subjects=set(data.get("subjects", [])),
                resources=set(data.get("resources", [])),
                actions=set(actions),
                conditions=conditions,
                priority=data.get("priority", 0),
                created_at=datetime.fromisoformat(data["created_at"]),
                created_by=data.get("created_by"),
                updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
                updated_by=data.get("updated_by"),
                is_active=data.get("is_active", True),
                metadata=data.get("metadata", {})
            )
        except Exception as e:
            logger.error(f"Error creating policy from dict: {e}")
            raise ValueError(f"Invalid policy data: {e}")


class PolicyError(Exception):
    """Policy management errors."""
    pass


class PolicyManager:
    """Manage access policies with Redis persistence."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        redis_db: int = 4,  # Separate DB for policies
        policy_prefix: str = "policy:",
        cache_ttl: int = 1800,  # 30 minutes cache
        default_decision: bool = False  # Default deny
    ):
        self.redis_url = redis_url
        self.redis_db = redis_db
        self.policy_prefix = policy_prefix
        self.cache_ttl = cache_ttl
        self.default_decision = default_decision
        
        # Redis connection
        self.redis: Optional[aioredis.Redis] = None
        
        # In-memory cache for policies
        self._policy_cache: Dict[str, AccessPolicy] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        # Evaluation cache for performance
        self._evaluation_cache: Dict[str, Dict[str, Any]] = {}
        self._evaluation_cache_ttl = 300  # 5 minutes
        
        # Metrics
        self.metrics = {
            "policies_created": 0,
            "policies_updated": 0,
            "policies_deleted": 0,
            "evaluations": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        logger.info("Policy manager initialized")
    
    async def connect(self):
        """Connect to Redis and initialize default policies."""
        try:
            self.redis = aioredis.from_url(
                self.redis_url,
                db=self.redis_db,
                decode_responses=True
            )
            
            # Test connection
            await self.redis.ping()
            
            # Initialize default policies
            await self._initialize_default_policies()
            
            logger.info("Connected to Redis for policy management")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise PolicyError(f"Redis connection failed: {e}")
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    async def _initialize_default_policies(self):
        """Initialize default security policies."""
        try:
            default_policies = self._create_default_policies()
            
            for policy in default_policies:
                if not await self.policy_exists(policy.name):
                    await self.create_policy(policy)
                    logger.info(f"Initialized default policy: {policy.name}")
                    
        except Exception as e:
            logger.error(f"Failed to initialize default policies: {e}")
    
    def _create_default_policies(self) -> List[AccessPolicy]:
        """Create default security policies."""
        policies = []
        
        # Admin full access policy
        admin_policy = AccessPolicy(
            name="admin_full_access",
            description="Full system access for administrators",
            effect=PolicyEffect.ALLOW,
            subjects={"system_admin", "admin"},
            priority=1000,
            metadata={"system_policy": True}
        )
        policies.append(admin_policy)
        
        # Block policy for blocked agents
        block_policy = AccessPolicy(
            name="blocked_agents_deny",
            description="Deny all access for blocked agents",
            effect=PolicyEffect.DENY,
            priority=2000,  # Higher priority than allow policies
            conditions=[
                PolicyCondition(
                    attribute="agent_blocked",
                    operator=PolicyConditionOperator.EQUALS,
                    value=True,
                    description="Agent is in blocked list"
                )
            ],
            metadata={"system_policy": True}
        )
        policies.append(block_policy)
        
        # Time-based access policy
        business_hours_policy = AccessPolicy(
            name="business_hours_access",
            description="Allow access during business hours",
            effect=PolicyEffect.ALLOW,
            conditions=[
                PolicyCondition(
                    attribute="hour",
                    operator=PolicyConditionOperator.GREATER_EQUAL,
                    value=9,
                    description="After 9 AM"
                ),
                PolicyCondition(
                    attribute="hour",
                    operator=PolicyConditionOperator.LESS_THAN,
                    value=18,
                    description="Before 6 PM"
                )
            ],
            priority=100,
            metadata={"system_policy": True}
        )
        policies.append(business_hours_policy)
        
        # Rate limiting policy
        rate_limit_policy = AccessPolicy(
            name="rate_limit_protection",
            description="Deny access when rate limit exceeded",
            effect=PolicyEffect.DENY,
            conditions=[
                PolicyCondition(
                    attribute="rate_limit_exceeded",
                    operator=PolicyConditionOperator.EQUALS,
                    value=True,
                    description="Rate limit has been exceeded"
                )
            ],
            priority=1500,
            metadata={"system_policy": True}
        )
        policies.append(rate_limit_policy)
        
        return policies
    
    def _is_cache_valid(self, policy_name: str) -> bool:
        """Check if cached policy is still valid."""
        if policy_name not in self._cache_timestamps:
            return False
        
        cache_age = datetime.now(timezone.utc) - self._cache_timestamps[policy_name]
        return cache_age.total_seconds() < self.cache_ttl
    
    def _cache_policy(self, policy: AccessPolicy):
        """Cache policy in memory."""
        self._policy_cache[policy.name] = policy
        self._cache_timestamps[policy.name] = datetime.now(timezone.utc)
    
    def _invalidate_cache(self, policy_name: str):
        """Invalidate cached policy."""
        self._policy_cache.pop(policy_name, None)
        self._cache_timestamps.pop(policy_name, None)
    
    def _get_evaluation_cache_key(
        self,
        subject: str,
        action: PermissionType,
        resource: str,
        context_hash: str
    ) -> str:
        """Generate cache key for policy evaluation."""
        return f"eval:{subject}:{action.value}:{resource}:{context_hash}"
    
    def _hash_context(self, context: Dict[str, Any]) -> str:
        """Create hash of context for caching."""
        import hashlib
        context_str = json.dumps(context, sort_keys=True, default=str)
        return hashlib.md5(context_str.encode()).hexdigest()[:16]
    
    async def create_policy(self, policy: AccessPolicy) -> bool:
        """Create a new access policy."""
        try:
            if not self.redis:
                raise PolicyError("Redis connection not initialized")
            
            # Check if policy already exists
            if await self.policy_exists(policy.name):
                raise PolicyError(f"Policy already exists: {policy.name}")
            
            # Store policy in Redis
            policy_key = f"{self.policy_prefix}{policy.name}"
            policy_data = json.dumps(policy.to_dict())
            
            await self.redis.set(policy_key, policy_data)
            
            # Cache the policy
            self._cache_policy(policy)
            
            # Clear evaluation cache
            self._evaluation_cache.clear()
            
            self.metrics["policies_created"] += 1
            logger.info(f"Created policy: {policy.name}")
            
            return True
            
        except PolicyError:
            raise
        except Exception as e:
            logger.error(f"Failed to create policy: {e}")
            raise PolicyError(f"Policy creation failed: {e}")
    
    async def get_policy(self, policy_name: str) -> Optional[AccessPolicy]:
        """Get policy by name with caching."""
        try:
            # Check cache first
            if policy_name in self._policy_cache and self._is_cache_valid(policy_name):
                self.metrics["cache_hits"] += 1
                return self._policy_cache[policy_name]
            
            if not self.redis:
                raise PolicyError("Redis connection not initialized")
            
            # Get from Redis
            policy_key = f"{self.policy_prefix}{policy_name}"
            policy_data_str = await self.redis.get(policy_key)
            
            if not policy_data_str:
                self.metrics["cache_misses"] += 1
                return None
            
            policy_data = json.loads(policy_data_str)
            policy = AccessPolicy.from_dict(policy_data)
            
            # Cache the policy
            self._cache_policy(policy)
            self.metrics["cache_misses"] += 1
            
            return policy
            
        except PolicyError:
            raise
        except Exception as e:
            logger.error(f"Failed to get policy: {e}")
            return None
    
    async def update_policy(self, policy: AccessPolicy, updated_by: Optional[str] = None) -> bool:
        """Update an existing policy."""
        try:
            if not self.redis:
                raise PolicyError("Redis connection not initialized")
            
            # Check if policy exists
            if not await self.policy_exists(policy.name):
                raise PolicyError(f"Policy not found: {policy.name}")
            
            # Update metadata
            policy.updated_at = datetime.now(timezone.utc)
            policy.updated_by = updated_by
            
            # Store updated policy
            policy_key = f"{self.policy_prefix}{policy.name}"
            policy_data = json.dumps(policy.to_dict())
            
            await self.redis.set(policy_key, policy_data)
            
            # Update cache
            self._cache_policy(policy)
            
            # Clear evaluation cache
            self._evaluation_cache.clear()
            
            self.metrics["policies_updated"] += 1
            logger.info(f"Updated policy: {policy.name}")
            
            return True
            
        except PolicyError:
            raise
        except Exception as e:
            logger.error(f"Failed to update policy: {e}")
            raise PolicyError(f"Policy update failed: {e}")
    
    async def delete_policy(self, policy_name: str) -> bool:
        """Delete a policy."""
        try:
            if not self.redis:
                raise PolicyError("Redis connection not initialized")
            
            # Check if it's a system policy
            policy = await self.get_policy(policy_name)
            if policy and policy.metadata.get("system_policy"):
                raise PolicyError(f"Cannot delete system policy: {policy_name}")
            
            # Delete from Redis
            policy_key = f"{self.policy_prefix}{policy_name}"
            deleted = await self.redis.delete(policy_key)
            
            if deleted:
                # Invalidate cache
                self._invalidate_cache(policy_name)
                
                # Clear evaluation cache
                self._evaluation_cache.clear()
                
                self.metrics["policies_deleted"] += 1
                logger.info(f"Deleted policy: {policy_name}")
            
            return deleted > 0
            
        except PolicyError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete policy: {e}")
            return False
    
    async def policy_exists(self, policy_name: str) -> bool:
        """Check if policy exists."""
        try:
            if not self.redis:
                return False
            
            policy_key = f"{self.policy_prefix}{policy_name}"
            exists = await self.redis.exists(policy_key)
            return exists > 0
            
        except Exception as e:
            logger.error(f"Error checking policy existence: {e}")
            return False
    
    async def list_policies(self, active_only: bool = True) -> List[AccessPolicy]:
        """List all policies with optional filtering."""
        try:
            if not self.redis:
                raise PolicyError("Redis connection not initialized")
            
            policies = []
            
            # Get all policy keys
            async for key in self.redis.scan_iter(match=f"{self.policy_prefix}*"):
                try:
                    policy_data_str = await self.redis.get(key)
                    if policy_data_str:
                        policy_data = json.loads(policy_data_str)
                        policy = AccessPolicy.from_dict(policy_data)
                        
                        # Apply filters
                        if active_only and not policy.is_active:
                            continue
                        
                        policies.append(policy)
                        
                except Exception as e:
                    logger.error(f"Error processing policy key {key}: {e}")
                    continue
            
            # Sort by priority (descending) then name
            return sorted(policies, key=lambda p: (-p.priority, p.name))
            
        except PolicyError:
            raise
        except Exception as e:
            logger.error(f"Failed to list policies: {e}")
            return []
    
    async def evaluate_access(
        self,
        subject: str,
        action: PermissionType,
        resource: str,
        context: Dict[str, Any],
        user_roles: Optional[List[str]] = None
    ) -> bool:
        """Evaluate access request against all policies."""
        try:
            self.metrics["evaluations"] += 1
            
            # Check evaluation cache
            context_hash = self._hash_context(context)
            cache_key = self._get_evaluation_cache_key(subject, action, resource, context_hash)
            
            if cache_key in self._evaluation_cache:
                cache_entry = self._evaluation_cache[cache_key]
                cache_age = datetime.now(timezone.utc) - cache_entry["timestamp"]
                
                if cache_age.total_seconds() < self._evaluation_cache_ttl:
                    return cache_entry["decision"]
            
            # Get all active policies
            policies = await self.list_policies(active_only=True)
            
            # Evaluate policies in priority order
            allow_decisions = []
            deny_decisions = []
            
            for policy in policies:
                decision = policy.evaluate(subject, action, resource, context, user_roles)
                
                if decision is True:
                    allow_decisions.append(policy)
                elif decision is False:
                    deny_decisions.append(policy)
            
            # Policy decision logic: explicit deny overrides allow
            if deny_decisions:
                final_decision = False
            elif allow_decisions:
                final_decision = True
            else:
                final_decision = self.default_decision
            
            # Cache the decision
            self._evaluation_cache[cache_key] = {
                "decision": final_decision,
                "timestamp": datetime.now(timezone.utc),
                "allow_policies": [p.name for p in allow_decisions],
                "deny_policies": [p.name for p in deny_decisions]
            }
            
            # Limit cache size
            if len(self._evaluation_cache) > 1000:
                # Remove oldest entries
                oldest_key = min(
                    self._evaluation_cache.keys(),
                    key=lambda k: self._evaluation_cache[k]["timestamp"]
                )
                del self._evaluation_cache[oldest_key]
            
            logger.debug(f"Access evaluation: {subject} -> {action.value} on {resource} = {final_decision}")
            return final_decision
            
        except Exception as e:
            logger.error(f"Error evaluating access: {e}")
            return self.default_decision  # Fail safe
    
    async def get_policy_statistics(self) -> Dict[str, Any]:
        """Get policy management statistics."""
        try:
            if not self.redis:
                return {"error": "Redis not connected"}
            
            # Count policies by effect
            allow_policies = 0
            deny_policies = 0
            total_policies = 0
            active_policies = 0
            
            async for key in self.redis.scan_iter(match=f"{self.policy_prefix}*"):
                try:
                    policy_data_str = await self.redis.get(key)
                    if policy_data_str:
                        policy_data = json.loads(policy_data_str)
                        total_policies += 1
                        
                        if policy_data.get("is_active", True):
                            active_policies += 1
                            
                            effect = policy_data.get("effect", "allow")
                            if effect == "allow":
                                allow_policies += 1
                            else:
                                deny_policies += 1
                                
                except Exception:
                    continue
            
            return {
                "total_policies": total_policies,
                "active_policies": active_policies,
                "allow_policies": allow_policies,
                "deny_policies": deny_policies,
                "cache_statistics": {
                    "cached_policies": len(self._policy_cache),
                    "evaluation_cache_size": len(self._evaluation_cache)
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
            
            # Get statistics
            statistics = await self.get_policy_statistics()
            
            return {
                "status": "healthy",
                "redis_connected": True,
                "default_decision": self.default_decision,
                "statistics": statistics
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()