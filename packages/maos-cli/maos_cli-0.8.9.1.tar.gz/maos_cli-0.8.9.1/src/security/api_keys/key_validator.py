"""API key validation with caching and security features."""

import hashlib
import hmac
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
import aioredis

from .api_key_manager import APIKey, APIKeyScope, APIKeyManager

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of API key validation."""
    valid: bool
    key: Optional[APIKey] = None
    error: Optional[str] = None
    cached: bool = False
    validation_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "valid": self.valid,
            "key": self.key.to_dict() if self.key else None,
            "error": self.error,
            "cached": self.cached,
            "validation_time": self.validation_time.isoformat() if self.validation_time else None
        }


class APIKeyValidator:
    """High-performance API key validator with caching and security features."""
    
    def __init__(
        self,
        api_key_manager: APIKeyManager,
        redis_url: str = "redis://localhost:6379",
        redis_db: int = 7,  # Separate DB for validation cache
        cache_prefix: str = "key_validation:",
        rate_limit_prefix: str = "validation_rate:",
        cache_ttl: int = 300,  # 5 minutes cache
        enable_validation_cache: bool = True,
        max_validation_rate: int = 1000,  # Max validations per hour per key
        enable_security_logging: bool = True
    ):
        self.api_key_manager = api_key_manager
        self.redis_url = redis_url
        self.redis_db = redis_db
        self.cache_prefix = cache_prefix
        self.rate_limit_prefix = rate_limit_prefix
        self.cache_ttl = cache_ttl
        self.enable_validation_cache = enable_validation_cache
        self.max_validation_rate = max_validation_rate
        self.enable_security_logging = enable_security_logging
        
        # Redis connection for validation cache
        self.redis: Optional[aioredis.Redis] = None
        
        # In-memory validation cache (for ultra-fast validation)
        self._memory_cache: Dict[str, Tuple[ValidationResult, datetime]] = {}
        self._memory_cache_ttl = 60  # 1 minute memory cache
        
        # Security event tracking
        self._security_events: List[Dict[str, Any]] = []
        self._max_security_events = 1000
        
        # Performance metrics
        self.metrics = {
            "validations_total": 0,
            "validations_successful": 0,
            "validations_failed": 0,
            "cache_hits_memory": 0,
            "cache_hits_redis": 0,
            "cache_misses": 0,
            "rate_limit_violations": 0,
            "security_events": 0,
            "average_validation_time_ms": 0.0
        }
        
        logger.info("API key validator initialized")
    
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
            logger.info("Connected to Redis for validation caching")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Continue without Redis caching
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    def _get_cache_key(self, api_key_hash: str, required_scope: str, client_ip: str) -> str:
        """Generate cache key for validation result."""
        context_hash = hashlib.md5(f"{required_scope}:{client_ip}".encode()).hexdigest()[:8]
        return f"{self.cache_prefix}{api_key_hash[:16]}:{context_hash}"
    
    def _hash_api_key(self, api_key: str) -> str:
        """Create hash of API key for caching (without revealing the key)."""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def _is_memory_cache_valid(self, cache_key: str) -> bool:
        """Check if memory cache entry is valid."""
        if cache_key not in self._memory_cache:
            return False
        
        _, timestamp = self._memory_cache[cache_key]
        age = datetime.now(timezone.utc) - timestamp
        return age.total_seconds() < self._memory_cache_ttl
    
    def _cache_in_memory(self, cache_key: str, result: ValidationResult):
        """Cache validation result in memory."""
        # Limit memory cache size
        if len(self._memory_cache) > 1000:
            # Remove oldest entry
            oldest_key = min(self._memory_cache.keys(), key=lambda k: self._memory_cache[k][1])
            del self._memory_cache[oldest_key]
        
        self._memory_cache[cache_key] = (result, datetime.now(timezone.utc))
    
    async def _check_validation_rate_limit(self, key_id: str) -> bool:
        """Check validation rate limit for a key."""
        try:
            if not self.redis or not self.max_validation_rate:
                return True
            
            current_hour = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
            rate_key = f"{self.rate_limit_prefix}{key_id}:{current_hour.isoformat()}"
            
            # Get current validation count
            current_count = await self.redis.get(rate_key)
            current_count = int(current_count) if current_count else 0
            
            # Check if within limit
            if current_count >= self.max_validation_rate:
                return False
            
            # Increment counter
            await self.redis.incr(rate_key)
            await self.redis.expire(rate_key, 3600)  # 1 hour
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow on error
    
    def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event."""
        if not self.enable_security_logging:
            return
        
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "details": details
        }
        
        self._security_events.append(event)
        self.metrics["security_events"] += 1
        
        # Limit security events list
        if len(self._security_events) > self._max_security_events:
            self._security_events = self._security_events[-self._max_security_events//2:]
        
        logger.warning(f"Security event: {event_type} - {details}")
    
    async def validate_key(
        self,
        api_key: str,
        required_scope: Optional[APIKeyScope] = None,
        client_ip: Optional[str] = None,
        check_rate_limit: bool = True,
        use_cache: bool = True
    ) -> ValidationResult:
        """Validate API key with comprehensive security checks."""
        start_time = datetime.now(timezone.utc)
        
        try:
            self.metrics["validations_total"] += 1
            
            # Input validation
            if not api_key or len(api_key) < 10:
                self._log_security_event("invalid_key_format", {
                    "key_length": len(api_key) if api_key else 0,
                    "client_ip": client_ip
                })
                return ValidationResult(
                    valid=False,
                    error="Invalid API key format",
                    validation_time=start_time
                )
            
            # Generate cache key
            api_key_hash = self._hash_api_key(api_key)
            required_scope_str = required_scope.value if required_scope else "none"
            client_ip_str = client_ip or "unknown"
            cache_key = self._get_cache_key(api_key_hash, required_scope_str, client_ip_str)
            
            # Check memory cache first
            if use_cache and self.enable_validation_cache and self._is_memory_cache_valid(cache_key):
                cached_result, _ = self._memory_cache[cache_key]
                cached_result.cached = True
                self.metrics["cache_hits_memory"] += 1
                return cached_result
            
            # Check Redis cache
            if use_cache and self.enable_validation_cache and self.redis:
                try:
                    cached_data = await self.redis.get(cache_key)
                    if cached_data:
                        import json
                        cached_dict = json.loads(cached_data)
                        cached_result = ValidationResult(
                            valid=cached_dict["valid"],
                            key=APIKey.from_dict(cached_dict["key"]) if cached_dict.get("key") else None,
                            error=cached_dict.get("error"),
                            cached=True,
                            validation_time=datetime.fromisoformat(cached_dict["validation_time"])
                        )
                        
                        # Also cache in memory for faster subsequent access
                        self._cache_in_memory(cache_key, cached_result)
                        self.metrics["cache_hits_redis"] += 1
                        return cached_result
                        
                except Exception as e:
                    logger.error(f"Redis cache lookup failed: {e}")
            
            self.metrics["cache_misses"] += 1
            
            # Perform actual validation
            validated_key = await self.api_key_manager.validate_api_key(
                api_key=api_key,
                required_scope=required_scope,
                client_ip=client_ip,
                check_rate_limit=False  # We handle rate limiting here
            )
            
            if validated_key is None:
                self._log_security_event("validation_failed", {
                    "key_hash": api_key_hash[:16],
                    "required_scope": required_scope_str,
                    "client_ip": client_ip,
                    "reason": "Key not found or invalid"
                })
                
                result = ValidationResult(
                    valid=False,
                    error="Invalid API key",
                    validation_time=start_time
                )
                self.metrics["validations_failed"] += 1
            else:
                # Check validation rate limit
                if check_rate_limit:
                    if not await self._check_validation_rate_limit(validated_key.key_id):
                        self._log_security_event("validation_rate_limit", {
                            "key_id": validated_key.key_id,
                            "client_ip": client_ip
                        })
                        
                        result = ValidationResult(
                            valid=False,
                            error="Validation rate limit exceeded",
                            validation_time=start_time
                        )
                        self.metrics["rate_limit_violations"] += 1
                        self.metrics["validations_failed"] += 1
                    else:
                        result = ValidationResult(
                            valid=True,
                            key=validated_key,
                            validation_time=start_time
                        )
                        self.metrics["validations_successful"] += 1
                else:
                    result = ValidationResult(
                        valid=True,
                        key=validated_key,
                        validation_time=start_time
                    )
                    self.metrics["validations_successful"] += 1
            
            # Cache the result
            if use_cache and self.enable_validation_cache:
                # Cache in memory
                self._cache_in_memory(cache_key, result)
                
                # Cache in Redis
                if self.redis:
                    try:
                        import json
                        cache_data = json.dumps(result.to_dict())
                        await self.redis.setex(cache_key, self.cache_ttl, cache_data)
                    except Exception as e:
                        logger.error(f"Failed to cache in Redis: {e}")
            
            # Update performance metrics
            validation_time_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            # Update rolling average
            current_avg = self.metrics["average_validation_time_ms"]
            total_validations = self.metrics["validations_total"]
            new_avg = ((current_avg * (total_validations - 1)) + validation_time_ms) / total_validations
            self.metrics["average_validation_time_ms"] = round(new_avg, 2)
            
            return result
            
        except Exception as e:
            logger.error(f"Key validation error: {e}")
            self._log_security_event("validation_error", {
                "error": str(e),
                "client_ip": client_ip
            })
            
            self.metrics["validations_failed"] += 1
            
            return ValidationResult(
                valid=False,
                error=f"Validation error: {str(e)}",
                validation_time=start_time
            )
    
    async def bulk_validate_keys(
        self,
        key_requests: List[Dict[str, Any]],
        max_concurrent: int = 10
    ) -> List[ValidationResult]:
        """Validate multiple API keys concurrently."""
        try:
            # Create semaphore to limit concurrent validations
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def validate_single(request: Dict[str, Any]) -> ValidationResult:
                async with semaphore:
                    return await self.validate_key(
                        api_key=request["api_key"],
                        required_scope=request.get("required_scope"),
                        client_ip=request.get("client_ip"),
                        check_rate_limit=request.get("check_rate_limit", True),
                        use_cache=request.get("use_cache", True)
                    )
            
            # Execute all validations concurrently
            tasks = [validate_single(request) for request in key_requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Bulk validation error for request {i}: {result}")
                    final_results.append(ValidationResult(
                        valid=False,
                        error=f"Bulk validation error: {str(result)}"
                    ))
                else:
                    final_results.append(result)
            
            return final_results
            
        except Exception as e:
            logger.error(f"Bulk validation failed: {e}")
            return [ValidationResult(valid=False, error=str(e)) for _ in key_requests]
    
    def clear_cache(self, api_key: Optional[str] = None):
        """Clear validation cache."""
        try:
            if api_key:
                # Clear cache for specific key
                api_key_hash = self._hash_api_key(api_key)
                
                # Clear memory cache
                keys_to_remove = [k for k in self._memory_cache.keys() if api_key_hash[:16] in k]
                for key in keys_to_remove:
                    del self._memory_cache[key]
                
                logger.info(f"Cleared validation cache for API key")
            else:
                # Clear all cache
                self._memory_cache.clear()
                logger.info("Cleared all validation cache")
                
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    async def clear_redis_cache(self, pattern: Optional[str] = None):
        """Clear Redis validation cache."""
        try:
            if not self.redis:
                return
            
            search_pattern = pattern or f"{self.cache_prefix}*"
            keys_deleted = 0
            
            async for key in self.redis.scan_iter(match=search_pattern):
                await self.redis.delete(key)
                keys_deleted += 1
            
            logger.info(f"Cleared {keys_deleted} entries from Redis validation cache")
            
        except Exception as e:
            logger.error(f"Failed to clear Redis cache: {e}")
    
    def get_security_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent security events."""
        return self._security_events[-limit:] if limit else self._security_events
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance and security metrics."""
        return {
            "performance": {
                "validations_total": self.metrics["validations_total"],
                "validations_successful": self.metrics["validations_successful"],
                "validations_failed": self.metrics["validations_failed"],
                "success_rate": (
                    self.metrics["validations_successful"] / self.metrics["validations_total"]
                    if self.metrics["validations_total"] > 0 else 0
                ),
                "average_validation_time_ms": self.metrics["average_validation_time_ms"]
            },
            "caching": {
                "cache_hits_memory": self.metrics["cache_hits_memory"],
                "cache_hits_redis": self.metrics["cache_hits_redis"],
                "cache_misses": self.metrics["cache_misses"],
                "cache_hit_rate": (
                    (self.metrics["cache_hits_memory"] + self.metrics["cache_hits_redis"]) /
                    (self.metrics["cache_hits_memory"] + self.metrics["cache_hits_redis"] + self.metrics["cache_misses"])
                    if (self.metrics["cache_hits_memory"] + self.metrics["cache_hits_redis"] + self.metrics["cache_misses"]) > 0 else 0
                ),
                "memory_cache_size": len(self._memory_cache)
            },
            "security": {
                "rate_limit_violations": self.metrics["rate_limit_violations"],
                "security_events": self.metrics["security_events"],
                "recent_security_events": len(self._security_events)
            },
            "configuration": {
                "cache_enabled": self.enable_validation_cache,
                "cache_ttl_seconds": self.cache_ttl,
                "max_validation_rate_per_hour": self.max_validation_rate,
                "security_logging_enabled": self.enable_security_logging
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            status = "healthy"
            issues = []
            
            # Check Redis connection
            redis_connected = False
            if self.redis:
                try:
                    await self.redis.ping()
                    redis_connected = True
                except Exception:
                    issues.append("Redis connection failed")
                    if self.enable_validation_cache:
                        status = "degraded"
            
            # Check API key manager
            api_key_manager_healthy = hasattr(self.api_key_manager, 'redis') and self.api_key_manager.redis
            if not api_key_manager_healthy:
                issues.append("API key manager not connected")
                status = "unhealthy"
            
            # Get metrics
            metrics = self.get_performance_metrics()
            
            return {
                "status": status,
                "issues": issues,
                "redis_connected": redis_connected,
                "api_key_manager_healthy": api_key_manager_healthy,
                "metrics": metrics
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()