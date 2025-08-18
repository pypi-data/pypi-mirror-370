"""Rate limiting middleware with DDoS protection."""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import aioredis

from fastapi import Request, Response, HTTPException, status

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitScope(Enum):
    """Rate limit scopes."""
    GLOBAL = "global"
    PER_IP = "per_ip"
    PER_USER = "per_user"
    PER_ENDPOINT = "per_endpoint"
    PER_API_KEY = "per_api_key"


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration."""
    name: str
    strategy: RateLimitStrategy
    scope: RateLimitScope
    limit: int  # Number of requests
    window_seconds: int  # Time window in seconds
    paths: List[str] = field(default_factory=list)  # Specific paths (empty = all paths)
    methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    user_roles: List[str] = field(default_factory=list)  # Apply to specific roles (empty = all users)
    priority: int = 0  # Higher priority rules are checked first
    enabled: bool = True
    
    # Advanced options
    burst_limit: Optional[int] = None  # Maximum burst above normal limit
    cooldown_seconds: int = 0  # Cooldown period after limit exceeded
    progressive_delay: bool = False  # Increase delay with repeated violations
    
    def matches_request(self, request: Request, user_roles: List[str] = None) -> bool:
        """Check if rule applies to request."""
        if not self.enabled:
            return False
        
        # Check paths
        if self.paths and not any(request.url.path.startswith(path) for path in self.paths):
            return False
        
        # Check methods
        if request.method not in self.methods:
            return False
        
        # Check user roles
        if self.user_roles and user_roles:
            if not any(role in self.user_roles for role in user_roles):
                return False
        
        return True


@dataclass
class RateLimitState:
    """Current rate limit state for a key."""
    requests_made: int = 0
    first_request_time: Optional[datetime] = None
    last_request_time: Optional[datetime] = None
    tokens: float = 0.0  # For token bucket
    last_refill_time: Optional[datetime] = None
    violations: int = 0
    last_violation_time: Optional[datetime] = None
    blocked_until: Optional[datetime] = None
    
    def is_blocked(self) -> bool:
        """Check if currently blocked."""
        if not self.blocked_until:
            return False
        return datetime.now(timezone.utc) < self.blocked_until


class RateLimitMiddleware:
    """Advanced rate limiting middleware with DDoS protection."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        redis_db: int = 8,  # Separate DB for rate limiting
        default_rules: Optional[List[RateLimitRule]] = None,
        enable_ddos_protection: bool = True,
        ddos_threshold_multiplier: float = 10.0,  # DDoS detection threshold
        ddos_block_duration: int = 3600,  # 1 hour DDoS block
        cleanup_interval: int = 300,  # 5 minutes cleanup interval
        enable_distributed: bool = True
    ):
        self.redis_url = redis_url
        self.redis_db = redis_db
        self.enable_ddos_protection = enable_ddos_protection
        self.ddos_threshold_multiplier = ddos_threshold_multiplier
        self.ddos_block_duration = ddos_block_duration
        self.cleanup_interval = cleanup_interval
        self.enable_distributed = enable_distributed
        
        # Redis connection for distributed rate limiting
        self.redis: Optional[aioredis.Redis] = None
        
        # Rate limit rules
        self.rules: List[RateLimitRule] = default_rules or self._create_default_rules()
        
        # Local state cache (for performance)
        self.local_state: Dict[str, RateLimitState] = {}
        self.local_state_lock = asyncio.Lock()
        
        # DDoS detection
        self.suspicious_ips: Set[str] = set()
        self.blocked_ips: Dict[str, datetime] = {}
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Metrics
        self.metrics = {
            "requests_processed": 0,
            "requests_limited": 0,
            "ddos_attacks_detected": 0,
            "ips_blocked": 0,
            "rules_triggered": {},
            "average_response_time_ms": 0.0
        }
        
        logger.info("Rate limit middleware initialized")
    
    async def connect(self):
        """Connect to Redis and start background tasks."""
        try:
            if self.enable_distributed:
                self.redis = aioredis.from_url(
                    self.redis_url,
                    db=self.redis_db,
                    decode_responses=True
                )
                
                # Test connection
                await self.redis.ping()
                logger.info("Connected to Redis for distributed rate limiting")
            
            # Start background cleanup task
            self._running = True
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Continue without distributed rate limiting
    
    async def disconnect(self):
        """Disconnect from Redis and stop background tasks."""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    def _create_default_rules(self) -> List[RateLimitRule]:
        """Create default rate limiting rules."""
        return [
            # Global rate limit
            RateLimitRule(
                name="global_limit",
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                scope=RateLimitScope.GLOBAL,
                limit=10000,
                window_seconds=60,
                priority=1
            ),
            
            # Per-IP rate limit
            RateLimitRule(
                name="per_ip_limit",
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                scope=RateLimitScope.PER_IP,
                limit=100,
                window_seconds=60,
                burst_limit=150,
                priority=10
            ),
            
            # API endpoints
            RateLimitRule(
                name="api_endpoints",
                strategy=RateLimitStrategy.TOKEN_BUCKET,
                scope=RateLimitScope.PER_IP,
                limit=30,
                window_seconds=60,
                paths=["/api/"],
                priority=20
            ),
            
            # Authentication endpoints
            RateLimitRule(
                name="auth_endpoints",
                strategy=RateLimitStrategy.FIXED_WINDOW,
                scope=RateLimitScope.PER_IP,
                limit=5,
                window_seconds=300,  # 5 minutes
                paths=["/auth/", "/login", "/register"],
                cooldown_seconds=60,
                priority=50
            ),
            
            # Admin endpoints
            RateLimitRule(
                name="admin_endpoints",
                strategy=RateLimitStrategy.FIXED_WINDOW,
                scope=RateLimitScope.PER_USER,
                limit=10,
                window_seconds=60,
                paths=["/admin/"],
                user_roles=["admin", "system_admin"],
                priority=30
            )
        ]
    
    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process rate limiting for incoming requests."""
        start_time = datetime.now(timezone.utc)
        
        try:
            self.metrics["requests_processed"] += 1
            
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Check if IP is blocked for DDoS
            if await self._check_ddos_block(client_ip):
                self.metrics["requests_limited"] += 1
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="IP temporarily blocked due to suspicious activity",
                    headers={"Retry-After": str(self.ddos_block_duration)}
                )
            
            # Get user context
            auth_context = getattr(request.state, "auth_context", None)
            user_id = auth_context.user_id if auth_context and auth_context.authenticated else None
            user_roles = auth_context.roles if auth_context and auth_context.authenticated else []
            
            # Check rate limits
            applicable_rules = self._get_applicable_rules(request, user_roles)
            
            for rule in applicable_rules:
                limit_key = self._generate_limit_key(rule, request, client_ip, user_id)
                
                if not await self._check_rate_limit(rule, limit_key, request):
                    self.metrics["requests_limited"] += 1
                    self.metrics["rules_triggered"][rule.name] = self.metrics["rules_triggered"].get(rule.name, 0) + 1
                    
                    # Check for potential DDoS
                    if self.enable_ddos_protection:
                        await self._detect_ddos_attack(client_ip, rule)
                    
                    # Calculate retry after
                    retry_after = self._calculate_retry_after(rule)
                    
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded: {rule.name}",
                        headers={
                            "Retry-After": str(retry_after),
                            "X-RateLimit-Limit": str(rule.limit),
                            "X-RateLimit-Remaining": "0",
                            "X-RateLimit-Reset": str(int((datetime.now(timezone.utc) + timedelta(seconds=retry_after)).timestamp()))
                        }
                    )
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            await self._add_rate_limit_headers(response, applicable_rules, request, client_ip, user_id)
            
            # Update performance metrics
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            current_avg = self.metrics["average_response_time_ms"]
            total_requests = self.metrics["requests_processed"]
            new_avg = ((current_avg * (total_requests - 1)) + processing_time) / total_requests
            self.metrics["average_response_time_ms"] = round(new_avg, 2)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Continue without rate limiting on error
            return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        return request.client.host if request.client else "unknown"
    
    def _get_applicable_rules(self, request: Request, user_roles: List[str]) -> List[RateLimitRule]:
        """Get rules that apply to the current request."""
        applicable_rules = []
        
        for rule in self.rules:
            if rule.matches_request(request, user_roles):
                applicable_rules.append(rule)
        
        # Sort by priority (higher priority first)
        return sorted(applicable_rules, key=lambda r: r.priority, reverse=True)
    
    def _generate_limit_key(
        self,
        rule: RateLimitRule,
        request: Request,
        client_ip: str,
        user_id: Optional[str]
    ) -> str:
        """Generate rate limit key based on scope."""
        base_key = f"rate_limit:{rule.name}"
        
        if rule.scope == RateLimitScope.GLOBAL:
            return f"{base_key}:global"
        elif rule.scope == RateLimitScope.PER_IP:
            return f"{base_key}:ip:{client_ip}"
        elif rule.scope == RateLimitScope.PER_USER:
            user_key = user_id or f"anonymous:{client_ip}"
            return f"{base_key}:user:{user_key}"
        elif rule.scope == RateLimitScope.PER_ENDPOINT:
            endpoint = f"{request.method}:{request.url.path}"
            return f"{base_key}:endpoint:{hashlib.md5(endpoint.encode()).hexdigest()[:8]}"
        elif rule.scope == RateLimitScope.PER_API_KEY:
            api_key = request.headers.get("X-API-Key", f"nokey:{client_ip}")
            return f"{base_key}:apikey:{hashlib.md5(api_key.encode()).hexdigest()[:8]}"
        
        return f"{base_key}:unknown"
    
    async def _check_rate_limit(self, rule: RateLimitRule, limit_key: str, request: Request) -> bool:
        """Check if request is within rate limit."""
        try:
            current_time = datetime.now(timezone.utc)
            
            if rule.strategy == RateLimitStrategy.FIXED_WINDOW:
                return await self._check_fixed_window(rule, limit_key, current_time)
            elif rule.strategy == RateLimitStrategy.SLIDING_WINDOW:
                return await self._check_sliding_window(rule, limit_key, current_time)
            elif rule.strategy == RateLimitStrategy.TOKEN_BUCKET:
                return await self._check_token_bucket(rule, limit_key, current_time)
            elif rule.strategy == RateLimitStrategy.LEAKY_BUCKET:
                return await self._check_leaky_bucket(rule, limit_key, current_time)
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True  # Allow on error
    
    async def _check_fixed_window(self, rule: RateLimitRule, limit_key: str, current_time: datetime) -> bool:
        """Check fixed window rate limit."""
        try:
            # Calculate window start
            window_start = current_time.replace(second=0, microsecond=0)
            window_key = f"{limit_key}:{window_start.timestamp()}"
            
            if self.redis:
                # Distributed check
                current_count = await self.redis.get(window_key)
                current_count = int(current_count) if current_count else 0
                
                if current_count >= rule.limit:
                    return False
                
                # Increment and set expiration
                await self.redis.incr(window_key)
                await self.redis.expire(window_key, rule.window_seconds)
                
            else:
                # Local check
                async with self.local_state_lock:
                    state = self.local_state.get(limit_key, RateLimitState())
                    
                    # Reset if new window
                    if not state.first_request_time or (current_time - state.first_request_time).total_seconds() >= rule.window_seconds:
                        state.requests_made = 0
                        state.first_request_time = current_time
                    
                    if state.requests_made >= rule.limit:
                        return False
                    
                    state.requests_made += 1
                    state.last_request_time = current_time
                    self.local_state[limit_key] = state
            
            return True
            
        except Exception as e:
            logger.error(f"Fixed window check error: {e}")
            return True
    
    async def _check_sliding_window(self, rule: RateLimitRule, limit_key: str, current_time: datetime) -> bool:
        """Check sliding window rate limit."""
        try:
            window_start = current_time - timedelta(seconds=rule.window_seconds)
            
            if self.redis:
                # Use Redis sorted set for sliding window
                pipe = self.redis.pipeline()
                
                # Remove old entries
                pipe.zremrangebyscore(limit_key, 0, window_start.timestamp())
                
                # Count current entries
                pipe.zcard(limit_key)
                
                # Add current request
                pipe.zadd(limit_key, {str(current_time.timestamp()): current_time.timestamp()})
                
                # Set expiration
                pipe.expire(limit_key, rule.window_seconds)
                
                results = await pipe.execute()
                current_count = results[1] if len(results) > 1 else 0
                
                return current_count < rule.limit
                
            else:
                # Local sliding window (simplified)
                async with self.local_state_lock:
                    state = self.local_state.get(limit_key, RateLimitState())
                    
                    # Simple approximation: reset counter if window passed
                    if not state.first_request_time or (current_time - state.first_request_time).total_seconds() >= rule.window_seconds:
                        state.requests_made = 0
                        state.first_request_time = current_time
                    
                    if state.requests_made >= rule.limit:
                        return False
                    
                    state.requests_made += 1
                    state.last_request_time = current_time
                    self.local_state[limit_key] = state
                    
                    return True
            
        except Exception as e:
            logger.error(f"Sliding window check error: {e}")
            return True
    
    async def _check_token_bucket(self, rule: RateLimitRule, limit_key: str, current_time: datetime) -> bool:
        """Check token bucket rate limit."""
        try:
            if self.redis:
                # Get current state from Redis
                state_data = await self.redis.get(f"{limit_key}:bucket")
                if state_data:
                    state = json.loads(state_data)
                    tokens = float(state.get("tokens", rule.limit))
                    last_refill = datetime.fromisoformat(state.get("last_refill", current_time.isoformat()))
                else:
                    tokens = float(rule.limit)
                    last_refill = current_time
                
                # Calculate tokens to add
                time_passed = (current_time - last_refill).total_seconds()
                tokens_to_add = time_passed * (rule.limit / rule.window_seconds)
                tokens = min(rule.limit, tokens + tokens_to_add)
                
                # Check if we have tokens
                if tokens < 1.0:
                    return False
                
                # Consume token
                tokens -= 1.0
                
                # Save state
                state_data = {
                    "tokens": tokens,
                    "last_refill": current_time.isoformat()
                }
                await self.redis.set(f"{limit_key}:bucket", json.dumps(state_data), ex=rule.window_seconds * 2)
                
            else:
                # Local token bucket
                async with self.local_state_lock:
                    state = self.local_state.get(limit_key, RateLimitState())
                    
                    if not state.last_refill_time:
                        state.tokens = float(rule.limit)
                        state.last_refill_time = current_time
                    
                    # Refill tokens
                    time_passed = (current_time - state.last_refill_time).total_seconds()
                    tokens_to_add = time_passed * (rule.limit / rule.window_seconds)
                    state.tokens = min(rule.limit, state.tokens + tokens_to_add)
                    state.last_refill_time = current_time
                    
                    # Check and consume token
                    if state.tokens < 1.0:
                        self.local_state[limit_key] = state
                        return False
                    
                    state.tokens -= 1.0
                    self.local_state[limit_key] = state
            
            return True
            
        except Exception as e:
            logger.error(f"Token bucket check error: {e}")
            return True
    
    async def _check_leaky_bucket(self, rule: RateLimitRule, limit_key: str, current_time: datetime) -> bool:
        """Check leaky bucket rate limit."""
        # Simplified leaky bucket implementation
        return await self._check_token_bucket(rule, limit_key, current_time)
    
    async def _detect_ddos_attack(self, client_ip: str, rule: RateLimitRule):
        """Detect potential DDoS attack."""
        try:
            if not self.enable_ddos_protection:
                return
            
            # Simple DDoS detection: multiple rapid violations
            violation_key = f"violations:{client_ip}"
            
            if self.redis:
                # Increment violation count
                violations = await self.redis.incr(violation_key)
                await self.redis.expire(violation_key, 300)  # 5 minutes window
                
                # Check if threshold exceeded
                threshold = rule.limit * self.ddos_threshold_multiplier
                if violations > threshold:
                    # Block IP
                    block_until = datetime.now(timezone.utc) + timedelta(seconds=self.ddos_block_duration)
                    await self.redis.set(f"blocked:{client_ip}", block_until.isoformat(), ex=self.ddos_block_duration)
                    
                    self.metrics["ddos_attacks_detected"] += 1
                    self.metrics["ips_blocked"] += 1
                    
                    logger.warning(f"DDoS attack detected from IP {client_ip}, blocked for {self.ddos_block_duration}s")
            else:
                # Local tracking
                self.suspicious_ips.add(client_ip)
                if len(self.suspicious_ips) > 100:  # Limit memory usage
                    self.suspicious_ips = set(list(self.suspicious_ips)[-50:])
            
        except Exception as e:
            logger.error(f"DDoS detection error: {e}")
    
    async def _check_ddos_block(self, client_ip: str) -> bool:
        """Check if IP is blocked for DDoS."""
        try:
            if self.redis:
                block_data = await self.redis.get(f"blocked:{client_ip}")
                if block_data:
                    block_until = datetime.fromisoformat(block_data)
                    return datetime.now(timezone.utc) < block_until
            else:
                # Check local blocks
                block_until = self.blocked_ips.get(client_ip)
                if block_until and datetime.now(timezone.utc) < block_until:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"DDoS block check error: {e}")
            return False
    
    def _calculate_retry_after(self, rule: RateLimitRule) -> int:
        """Calculate retry-after header value."""
        base_retry = rule.window_seconds
        
        # Add cooldown if configured
        if rule.cooldown_seconds > 0:
            base_retry += rule.cooldown_seconds
        
        return base_retry
    
    async def _add_rate_limit_headers(
        self,
        response: Response,
        rules: List[RateLimitRule],
        request: Request,
        client_ip: str,
        user_id: Optional[str]
    ):
        """Add rate limit headers to response."""
        try:
            if not rules:
                return
            
            # Use the most restrictive rule for headers
            primary_rule = rules[0]  # Rules are sorted by priority
            limit_key = self._generate_limit_key(primary_rule, request, client_ip, user_id)
            
            # Get current state
            remaining = primary_rule.limit
            reset_time = int((datetime.now(timezone.utc) + timedelta(seconds=primary_rule.window_seconds)).timestamp())
            
            if self.redis:
                if primary_rule.strategy == RateLimitStrategy.SLIDING_WINDOW:
                    current_count = await self.redis.zcard(limit_key)
                    remaining = max(0, primary_rule.limit - current_count)
                elif primary_rule.strategy == RateLimitStrategy.FIXED_WINDOW:
                    window_start = datetime.now(timezone.utc).replace(second=0, microsecond=0)
                    window_key = f"{limit_key}:{window_start.timestamp()}"
                    current_count = await self.redis.get(window_key)
                    current_count = int(current_count) if current_count else 0
                    remaining = max(0, primary_rule.limit - current_count)
                elif primary_rule.strategy == RateLimitStrategy.TOKEN_BUCKET:
                    state_data = await self.redis.get(f"{limit_key}:bucket")
                    if state_data:
                        state = json.loads(state_data)
                        remaining = int(state.get("tokens", primary_rule.limit))
            
            # Add headers
            response.headers["X-RateLimit-Limit"] = str(primary_rule.limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_time)
            response.headers["X-RateLimit-Policy"] = primary_rule.name
            
        except Exception as e:
            logger.error(f"Error adding rate limit headers: {e}")
    
    async def _cleanup_loop(self):
        """Background cleanup task."""
        try:
            while self._running:
                await asyncio.sleep(self.cleanup_interval)
                
                try:
                    await self._cleanup_expired_data()
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Rate limit cleanup loop cancelled")
            raise
    
    async def _cleanup_expired_data(self):
        """Clean up expired rate limit data."""
        try:
            current_time = datetime.now(timezone.utc)
            cleanup_count = 0
            
            # Clean up local state
            async with self.local_state_lock:
                expired_keys = []
                for key, state in self.local_state.items():
                    if state.last_request_time and (current_time - state.last_request_time).total_seconds() > 3600:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.local_state[key]
                    cleanup_count += 1
            
            # Clean up blocked IPs
            expired_blocks = []
            for ip, block_until in self.blocked_ips.items():
                if current_time >= block_until:
                    expired_blocks.append(ip)
            
            for ip in expired_blocks:
                del self.blocked_ips[ip]
                cleanup_count += 1
            
            if cleanup_count > 0:
                logger.debug(f"Cleaned up {cleanup_count} expired rate limit entries")
                
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def add_rule(self, rule: RateLimitRule):
        """Add new rate limiting rule."""
        self.rules.append(rule)
        # Re-sort by priority
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove rate limiting rule."""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                del self.rules[i]
                return True
        return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get rate limiting metrics."""
        return {
            "performance": self.metrics,
            "rules_count": len(self.rules),
            "local_state_entries": len(self.local_state),
            "suspicious_ips": len(self.suspicious_ips),
            "blocked_ips": len(self.blocked_ips),
            "distributed_enabled": self.enable_distributed and self.redis is not None
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            status = "healthy"
            issues = []
            
            # Check Redis connection
            redis_connected = False
            if self.enable_distributed and self.redis:
                try:
                    await self.redis.ping()
                    redis_connected = True
                except Exception:
                    issues.append("Redis connection failed")
                    status = "degraded"
            
            # Check if cleanup task is running
            cleanup_running = self._cleanup_task is not None and not self._cleanup_task.done()
            if not cleanup_running:
                issues.append("Cleanup task not running")
                status = "degraded"
            
            return {
                "status": status,
                "issues": issues,
                "redis_connected": redis_connected,
                "cleanup_running": cleanup_running,
                "metrics": self.get_metrics()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()