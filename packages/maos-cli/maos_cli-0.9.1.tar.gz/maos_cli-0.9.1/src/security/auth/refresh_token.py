"""Refresh token management with Redis persistence."""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import hashlib
import aioredis
import json

logger = logging.getLogger(__name__)


class RefreshTokenError(Exception):
    """Refresh token related errors."""
    pass


class RefreshTokenManager:
    """Manage refresh tokens with Redis persistence and rotation."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        redis_db: int = 2,  # Separate DB for refresh tokens
        token_prefix: str = "refresh_token:",
        user_tokens_prefix: str = "user_tokens:",
        max_tokens_per_user: int = 10,
        token_rotation: bool = True,
        cleanup_interval_hours: int = 24
    ):
        self.redis_url = redis_url
        self.redis_db = redis_db
        self.token_prefix = token_prefix
        self.user_tokens_prefix = user_tokens_prefix
        self.max_tokens_per_user = max_tokens_per_user
        self.token_rotation = token_rotation
        self.cleanup_interval_hours = cleanup_interval_hours
        
        # Redis connection
        self.redis: Optional[aioredis.Redis] = None
        
        # Metrics
        self.metrics = {
            "tokens_created": 0,
            "tokens_validated": 0,
            "tokens_revoked": 0,
            "tokens_rotated": 0,
            "cleanup_runs": 0
        }
        
        logger.info("Refresh token manager initialized")
    
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
            logger.info("Connected to Redis for refresh token storage")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise RefreshTokenError(f"Redis connection failed: {e}")
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    def _generate_token_hash(self, token: str) -> str:
        """Generate hash for token storage."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def _generate_family_id(self) -> str:
        """Generate family ID for token rotation."""
        return os.urandom(16).hex()
    
    async def store_refresh_token(
        self,
        token: str,
        user_id: str,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expires_in_days: int = 30,
        family_id: Optional[str] = None
    ) -> str:
        """Store refresh token with metadata."""
        try:
            if not self.redis:
                raise RefreshTokenError("Redis connection not initialized")
            
            # Generate token hash for storage
            token_hash = self._generate_token_hash(token)
            
            # Generate family ID for rotation if not provided
            if not family_id:
                family_id = self._generate_family_id()
            
            # Prepare token data
            token_data = {
                "user_id": user_id,
                "session_id": session_id,
                "agent_id": agent_id,
                "family_id": family_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_used": datetime.now(timezone.utc).isoformat(),
                "usage_count": 0,
                "metadata": metadata or {}
            }
            
            # Store token data
            token_key = f"{self.token_prefix}{token_hash}"
            expire_seconds = expires_in_days * 24 * 3600
            
            await self.redis.setex(
                token_key,
                expire_seconds,
                json.dumps(token_data)
            )
            
            # Add to user's token list
            user_tokens_key = f"{self.user_tokens_prefix}{user_id}"
            await self.redis.sadd(user_tokens_key, token_hash)
            await self.redis.expire(user_tokens_key, expire_seconds)
            
            # Enforce max tokens per user
            await self._enforce_token_limit(user_id)
            
            self.metrics["tokens_created"] += 1
            logger.debug(f"Stored refresh token for user: {user_id}")
            
            return family_id
            
        except Exception as e:
            logger.error(f"Failed to store refresh token: {e}")
            raise RefreshTokenError(f"Token storage failed: {e}")
    
    async def validate_refresh_token(
        self,
        token: str,
        expected_user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate refresh token and return metadata."""
        try:
            if not self.redis:
                raise RefreshTokenError("Redis connection not initialized")
            
            # Generate token hash
            token_hash = self._generate_token_hash(token)
            token_key = f"{self.token_prefix}{token_hash}"
            
            # Retrieve token data
            token_data_str = await self.redis.get(token_key)
            if not token_data_str:
                raise RefreshTokenError("Refresh token not found or expired")
            
            token_data = json.loads(token_data_str)
            
            # Validate user if specified
            if expected_user_id and token_data["user_id"] != expected_user_id:
                raise RefreshTokenError("Token user mismatch")
            
            # Update usage statistics
            token_data["usage_count"] += 1
            token_data["last_used"] = datetime.now(timezone.utc).isoformat()
            
            # Store updated data
            ttl = await self.redis.ttl(token_key)
            if ttl > 0:
                await self.redis.setex(token_key, ttl, json.dumps(token_data))
            
            self.metrics["tokens_validated"] += 1
            logger.debug(f"Validated refresh token for user: {token_data['user_id']}")
            
            return token_data
            
        except RefreshTokenError:
            raise
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            raise RefreshTokenError(f"Token validation failed: {e}")
    
    async def rotate_refresh_token(
        self,
        old_token: str,
        new_token: str,
        user_id: str
    ) -> str:
        """Rotate refresh token (invalidate old, store new)."""
        try:
            if not self.token_rotation:
                raise RefreshTokenError("Token rotation is disabled")
            
            # Validate old token
            old_token_data = await self.validate_refresh_token(old_token, user_id)
            family_id = old_token_data["family_id"]
            
            # Revoke old token
            await self.revoke_refresh_token(old_token, user_id)
            
            # Store new token with same family ID
            await self.store_refresh_token(
                token=new_token,
                user_id=user_id,
                session_id=old_token_data.get("session_id"),
                agent_id=old_token_data.get("agent_id"),
                metadata=old_token_data.get("metadata"),
                family_id=family_id
            )
            
            self.metrics["tokens_rotated"] += 1
            logger.debug(f"Rotated refresh token for user: {user_id}")
            
            return family_id
            
        except Exception as e:
            logger.error(f"Token rotation failed: {e}")
            # If rotation fails, revoke the token family for security
            await self._revoke_token_family(old_token_data.get("family_id", ""))
            raise RefreshTokenError(f"Token rotation failed: {e}")
    
    async def revoke_refresh_token(
        self,
        token: str,
        user_id: Optional[str] = None
    ) -> bool:
        """Revoke a specific refresh token."""
        try:
            if not self.redis:
                raise RefreshTokenError("Redis connection not initialized")
            
            # Generate token hash
            token_hash = self._generate_token_hash(token)
            token_key = f"{self.token_prefix}{token_hash}"
            
            # Get token data for user verification
            if user_id:
                token_data_str = await self.redis.get(token_key)
                if token_data_str:
                    token_data = json.loads(token_data_str)
                    if token_data["user_id"] != user_id:
                        raise RefreshTokenError("Token user mismatch")
                    
                    # Remove from user's token set
                    user_tokens_key = f"{self.user_tokens_prefix}{user_id}"
                    await self.redis.srem(user_tokens_key, token_hash)
            
            # Delete token
            deleted = await self.redis.delete(token_key)
            
            if deleted:
                self.metrics["tokens_revoked"] += 1
                logger.debug(f"Revoked refresh token for user: {user_id}")
            
            return deleted > 0
            
        except RefreshTokenError:
            raise
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False
    
    async def revoke_all_user_tokens(self, user_id: str) -> int:
        """Revoke all refresh tokens for a user."""
        try:
            if not self.redis:
                raise RefreshTokenError("Redis connection not initialized")
            
            user_tokens_key = f"{self.user_tokens_prefix}{user_id}"
            
            # Get all user token hashes
            token_hashes = await self.redis.smembers(user_tokens_key)
            
            revoked_count = 0
            for token_hash in token_hashes:
                token_key = f"{self.token_prefix}{token_hash}"
                if await self.redis.delete(token_key):
                    revoked_count += 1
            
            # Clear user's token set
            await self.redis.delete(user_tokens_key)
            
            self.metrics["tokens_revoked"] += revoked_count
            logger.info(f"Revoked {revoked_count} tokens for user: {user_id}")
            
            return revoked_count
            
        except Exception as e:
            logger.error(f"Failed to revoke user tokens: {e}")
            return 0
    
    async def _revoke_token_family(self, family_id: str) -> int:
        """Revoke all tokens in a family (for security after rotation failure)."""
        try:
            if not self.redis or not family_id:
                return 0
            
            revoked_count = 0
            
            # Scan for tokens with matching family ID
            async for key in self.redis.scan_iter(match=f"{self.token_prefix}*"):
                try:
                    token_data_str = await self.redis.get(key)
                    if token_data_str:
                        token_data = json.loads(token_data_str)
                        if token_data.get("family_id") == family_id:
                            await self.redis.delete(key)
                            revoked_count += 1
                except Exception:
                    continue
            
            logger.warning(f"Revoked {revoked_count} tokens in family: {family_id}")
            return revoked_count
            
        except Exception as e:
            logger.error(f"Failed to revoke token family: {e}")
            return 0
    
    async def _enforce_token_limit(self, user_id: str):
        """Enforce maximum tokens per user."""
        try:
            user_tokens_key = f"{self.user_tokens_prefix}{user_id}"
            token_hashes = await self.redis.smembers(user_tokens_key)
            
            if len(token_hashes) > self.max_tokens_per_user:
                # Remove oldest tokens
                tokens_with_timestamps = []
                
                for token_hash in token_hashes:
                    token_key = f"{self.token_prefix}{token_hash}"
                    token_data_str = await self.redis.get(token_key)
                    
                    if token_data_str:
                        token_data = json.loads(token_data_str)
                        created_at = datetime.fromisoformat(token_data["created_at"])
                        tokens_with_timestamps.append((token_hash, created_at))
                    else:
                        # Remove invalid token hash
                        await self.redis.srem(user_tokens_key, token_hash)
                
                # Sort by creation time (oldest first)
                tokens_with_timestamps.sort(key=lambda x: x[1])
                
                # Remove excess tokens
                excess_count = len(tokens_with_timestamps) - self.max_tokens_per_user
                for i in range(excess_count):
                    token_hash = tokens_with_timestamps[i][0]
                    token_key = f"{self.token_prefix}{token_hash}"
                    
                    await self.redis.delete(token_key)
                    await self.redis.srem(user_tokens_key, token_hash)
                
                logger.info(f"Removed {excess_count} excess tokens for user: {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to enforce token limit: {e}")
    
    async def get_user_tokens(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active tokens for a user."""
        try:
            if not self.redis:
                raise RefreshTokenError("Redis connection not initialized")
            
            user_tokens_key = f"{self.user_tokens_prefix}{user_id}"
            token_hashes = await self.redis.smembers(user_tokens_key)
            
            tokens = []
            for token_hash in token_hashes:
                token_key = f"{self.token_prefix}{token_hash}"
                token_data_str = await self.redis.get(token_key)
                
                if token_data_str:
                    token_data = json.loads(token_data_str)
                    token_data["token_hash"] = token_hash
                    tokens.append(token_data)
                else:
                    # Clean up invalid token hash
                    await self.redis.srem(user_tokens_key, token_hash)
            
            return tokens
            
        except Exception as e:
            logger.error(f"Failed to get user tokens: {e}")
            return []
    
    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens and statistics."""
        try:
            if not self.redis:
                return 0
            
            cleaned_count = 0
            
            # Clean up token references from user sets
            async for user_key in self.redis.scan_iter(match=f"{self.user_tokens_prefix}*"):
                token_hashes = await self.redis.smembers(user_key)
                
                for token_hash in token_hashes:
                    token_key = f"{self.token_prefix}{token_hash}"
                    exists = await self.redis.exists(token_key)
                    
                    if not exists:
                        # Remove from user set
                        await self.redis.srem(user_key, token_hash)
                        cleaned_count += 1
            
            self.metrics["cleanup_runs"] += 1
            logger.debug(f"Cleaned up {cleaned_count} expired token references")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Token cleanup failed: {e}")
            return 0
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get refresh token statistics."""
        try:
            if not self.redis:
                return {"error": "Redis not connected"}
            
            # Count total tokens
            total_tokens = 0
            total_users = 0
            
            async for key in self.redis.scan_iter(match=f"{self.token_prefix}*"):
                total_tokens += 1
            
            async for key in self.redis.scan_iter(match=f"{self.user_tokens_prefix}*"):
                total_users += 1
            
            return {
                "total_tokens": total_tokens,
                "total_users_with_tokens": total_users,
                "max_tokens_per_user": self.max_tokens_per_user,
                "token_rotation_enabled": self.token_rotation,
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
            stats = await self.get_statistics()
            
            return {
                "status": "healthy",
                "redis_connected": True,
                "statistics": stats
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()