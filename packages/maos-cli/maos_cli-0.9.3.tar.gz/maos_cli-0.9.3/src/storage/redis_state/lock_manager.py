"""
Optimistic Lock Manager for Redis-based state management.

Provides distributed locking with compare-and-swap operations.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Set
from uuid import UUID, uuid4
from aioredis import Redis

from .types import StateKey, LockToken, StateOperationType
from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError


class OptimisticLockManager:
    """
    Manages optimistic locks for distributed state operations.
    
    Features:
    - Compare-and-swap operations
    - Automatic lock expiry
    - Lock extension
    - Deadlock prevention
    - Performance optimization
    """
    
    def __init__(
        self,
        redis: Redis,
        default_timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 0.1,
        cleanup_interval: int = 60
    ):
        """Initialize optimistic lock manager."""
        self.redis = redis
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.cleanup_interval = cleanup_interval
        
        self.logger = MAOSLogger("optimistic_lock_manager", str(uuid4()))
        
        # Lock tracking
        self._active_locks: Dict[str, LockToken] = {}
        self._lock_holders: Dict[UUID, Set[str]] = {}  # agent_id -> set of lock keys
        
        # Performance metrics
        self.metrics = {
            'locks_acquired': 0,
            'locks_released': 0,
            'locks_expired': 0,
            'lock_conflicts': 0,
            'avg_lock_duration': 0.0
        }
        
        # Lua scripts for atomic operations
        self._lua_scripts = {}
        self._initialize_lua_scripts()
    
    def _initialize_lua_scripts(self) -> None:
        """Initialize Lua scripts for atomic operations."""
        # Acquire lock script
        self._lua_scripts['acquire_lock'] = """
        local lock_key = KEYS[1]
        local token = ARGV[1]
        local expiry = ARGV[2]
        
        if redis.call('EXISTS', lock_key) == 0 then
            redis.call('SETEX', lock_key, expiry, token)
            return 1
        else
            return 0
        end
        """
        
        # Release lock script
        self._lua_scripts['release_lock'] = """
        local lock_key = KEYS[1]
        local token = ARGV[1]
        local current_token = redis.call('GET', lock_key)
        
        if current_token == token then
            redis.call('DEL', lock_key)
            return 1
        else
            return 0
        end
        """
        
        # Extend lock script
        self._lua_scripts['extend_lock'] = """
        local lock_key = KEYS[1]
        local token = ARGV[1]
        local additional_time = ARGV[2]
        local current_token = redis.call('GET', lock_key)
        
        if current_token == token then
            local current_ttl = redis.call('TTL', lock_key)
            if current_ttl > 0 then
                redis.call('EXPIRE', lock_key, current_ttl + tonumber(additional_time))
                return current_ttl + tonumber(additional_time)
            else
                return 0
            end
        else
            return -1
        end
        """
        
        # Compare and swap script
        self._lua_scripts['compare_and_swap'] = """
        local data_key = KEYS[1]
        local lock_key = KEYS[2]
        local expected_lock_token = ARGV[1]
        local new_value = ARGV[2]
        local current_lock_token = redis.call('GET', lock_key)
        
        if current_lock_token == expected_lock_token then
            redis.call('SET', data_key, new_value)
            redis.call('DEL', lock_key)
            return 1
        else
            return 0
        end
        """
    
    def _get_lock_key(self, state_key: StateKey) -> str:
        """Generate Redis key for lock."""
        return f"lock:{state_key}"
    
    async def acquire_lock(
        self,
        key: StateKey,
        timeout: Optional[int] = None,
        agent_id: Optional[UUID] = None,
        operation_type: StateOperationType = StateOperationType.UPDATE
    ) -> LockToken:
        """
        Acquire an optimistic lock for a state key.
        
        Args:
            key: State key to lock
            timeout: Lock timeout in seconds
            agent_id: Agent acquiring the lock
            operation_type: Type of operation
            
        Returns:
            LockToken for the acquired lock
            
        Raises:
            MAOSError: If lock cannot be acquired
        """
        timeout = timeout or self.default_timeout
        lock_key = self._get_lock_key(key)
        
        # Create lock token
        lock_token = LockToken(
            key=key,
            expires_at=datetime.utcnow() + timedelta(seconds=timeout),
            agent_id=agent_id,
            operation_type=operation_type
        )
        
        start_time = time.time()
        
        try:
            # Attempt to acquire lock with retries
            for attempt in range(self.max_retries + 1):
                result = await self.redis.eval(
                    self._lua_scripts['acquire_lock'],
                    1,
                    lock_key,
                    lock_token.token,
                    timeout
                )
                
                if result == 1:
                    # Lock acquired successfully
                    self._active_locks[lock_key] = lock_token
                    
                    # Track by agent
                    if agent_id:
                        if agent_id not in self._lock_holders:
                            self._lock_holders[agent_id] = set()
                        self._lock_holders[agent_id].add(lock_key)
                    
                    self.metrics['locks_acquired'] += 1
                    
                    self.logger.logger.debug(
                        f"Lock acquired for key: {key}",
                        extra={
                            'lock_token': lock_token.token,
                            'timeout': timeout,
                            'agent_id': str(agent_id) if agent_id else None,
                            'attempt': attempt + 1
                        }
                    )
                    
                    return lock_token
                
                # Lock not acquired, check if we should retry
                if attempt < self.max_retries:
                    self.metrics['lock_conflicts'] += 1
                    
                    # Check if lock is held by same agent (deadlock prevention)
                    if agent_id and await self._check_deadlock_risk(agent_id, lock_key):
                        raise MAOSError(f"Potential deadlock detected for agent {agent_id}")
                    
                    # Exponential backoff
                    delay = self.retry_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    self.metrics['lock_conflicts'] += 1
            
            # All attempts failed
            elapsed_time = time.time() - start_time
            raise MAOSError(
                f"Failed to acquire lock for key {key} after {self.max_retries} attempts "
                f"({elapsed_time:.2f}s elapsed)"
            )
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'acquire_lock',
                'key': str(key),
                'agent_id': str(agent_id) if agent_id else None
            })
            if isinstance(e, MAOSError):
                raise
            raise MAOSError(f"Lock acquisition failed: {str(e)}")
    
    async def release_lock(self, lock_token: LockToken) -> bool:
        """
        Release an acquired lock.
        
        Args:
            lock_token: Lock token to release
            
        Returns:
            True if lock was released successfully
        """
        lock_key = self._get_lock_key(lock_token.key)
        
        try:
            result = await self.redis.eval(
                self._lua_scripts['release_lock'],
                1,
                lock_key,
                lock_token.token
            )
            
            success = result == 1
            
            if success:
                # Remove from tracking
                if lock_key in self._active_locks:
                    del self._active_locks[lock_key]
                
                if lock_token.agent_id and lock_token.agent_id in self._lock_holders:
                    self._lock_holders[lock_token.agent_id].discard(lock_key)
                    if not self._lock_holders[lock_token.agent_id]:
                        del self._lock_holders[lock_token.agent_id]
                
                # Update metrics
                self.metrics['locks_released'] += 1
                
                if lock_token.acquired_at:
                    duration = (datetime.utcnow() - lock_token.acquired_at).total_seconds()
                    self._update_avg_lock_duration(duration)
                
                self.logger.logger.debug(
                    f"Lock released for key: {lock_token.key}",
                    extra={
                        'lock_token': lock_token.token,
                        'agent_id': str(lock_token.agent_id) if lock_token.agent_id else None
                    }
                )
            else:
                self.logger.logger.warning(
                    f"Failed to release lock - token mismatch or expired: {lock_token.key}",
                    extra={'lock_token': lock_token.token}
                )
            
            return success
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'release_lock',
                'key': str(lock_token.key),
                'lock_token': lock_token.token
            })
            return False
    
    async def extend_lock(self, lock_token: LockToken, additional_time: int) -> bool:
        """
        Extend the expiry time of an acquired lock.
        
        Args:
            lock_token: Lock token to extend
            additional_time: Additional time in seconds
            
        Returns:
            True if lock was extended successfully
        """
        lock_key = self._get_lock_key(lock_token.key)
        
        try:
            result = await self.redis.eval(
                self._lua_scripts['extend_lock'],
                1,
                lock_key,
                lock_token.token,
                additional_time
            )
            
            if result > 0:
                # Update local tracking
                lock_token.extend_expiry(additional_time)
                
                self.logger.logger.debug(
                    f"Lock extended for key: {lock_token.key}",
                    extra={
                        'lock_token': lock_token.token,
                        'additional_time': additional_time,
                        'new_ttl': result
                    }
                )
                return True
            elif result == 0:
                self.logger.logger.warning(f"Lock extension failed - lock expired: {lock_token.key}")
                return False
            else:  # result == -1
                self.logger.logger.warning(f"Lock extension failed - token mismatch: {lock_token.key}")
                return False
                
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'extend_lock',
                'key': str(lock_token.key),
                'lock_token': lock_token.token
            })
            return False
    
    async def is_locked(self, key: StateKey) -> bool:
        """Check if a key is currently locked."""
        lock_key = self._get_lock_key(key)
        
        try:
            result = await self.redis.exists(lock_key)
            return result == 1
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'is_locked',
                'key': str(key)
            })
            return False
    
    async def get_lock_info(self, key: StateKey) -> Optional[Dict[str, any]]:
        """Get information about a lock."""
        lock_key = self._get_lock_key(key)
        
        try:
            # Get lock token and TTL
            lock_token = await self.redis.get(lock_key)
            ttl = await self.redis.ttl(lock_key)
            
            if lock_token is None:
                return None
            
            # Get local lock info if available
            local_lock = self._active_locks.get(lock_key)
            
            return {
                'token': lock_token,
                'ttl_seconds': ttl,
                'agent_id': str(local_lock.agent_id) if local_lock and local_lock.agent_id else None,
                'operation_type': local_lock.operation_type.value if local_lock else None,
                'acquired_at': local_lock.acquired_at.isoformat() if local_lock else None
            }
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'get_lock_info',
                'key': str(key)
            })
            return None
    
    async def compare_and_swap(
        self,
        data_key: str,
        lock_token: LockToken,
        new_value: str
    ) -> bool:
        """
        Perform atomic compare-and-swap operation.
        
        Args:
            data_key: Redis key for the data
            lock_token: Lock token for verification
            new_value: New value to set
            
        Returns:
            True if operation was successful
        """
        lock_key = self._get_lock_key(lock_token.key)
        
        try:
            result = await self.redis.eval(
                self._lua_scripts['compare_and_swap'],
                2,
                data_key,
                lock_key,
                lock_token.token,
                new_value
            )
            
            success = result == 1
            
            if success:
                # Automatically release the lock on successful CAS
                await self.release_lock(lock_token)
            
            return success
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'compare_and_swap',
                'data_key': data_key,
                'lock_token': lock_token.token
            })
            return False
    
    async def cleanup_expired_locks(self) -> int:
        """Clean up expired locks and update metrics."""
        cleaned_count = 0
        expired_locks = []
        
        try:
            # Check all tracked locks
            for lock_key, lock_token in list(self._active_locks.items()):
                if lock_token.is_expired():
                    expired_locks.append((lock_key, lock_token))
            
            # Clean up expired locks
            for lock_key, lock_token in expired_locks:
                # Verify lock is actually expired in Redis
                ttl = await self.redis.ttl(lock_key)
                
                if ttl <= 0:  # Expired or doesn't exist
                    # Remove from local tracking
                    if lock_key in self._active_locks:
                        del self._active_locks[lock_key]
                    
                    if lock_token.agent_id and lock_token.agent_id in self._lock_holders:
                        self._lock_holders[lock_token.agent_id].discard(lock_key)
                        if not self._lock_holders[lock_token.agent_id]:
                            del self._lock_holders[lock_token.agent_id]
                    
                    cleaned_count += 1
            
            if cleaned_count > 0:
                self.metrics['locks_expired'] += cleaned_count
                
                self.logger.logger.info(
                    f"Cleaned up {cleaned_count} expired locks",
                    extra={'expired_locks': [lt.token for _, lt in expired_locks]}
                )
            
            return cleaned_count
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'cleanup_expired_locks'})
            return 0
    
    async def get_agent_locks(self, agent_id: UUID) -> List[LockToken]:
        """Get all locks held by a specific agent."""
        if agent_id not in self._lock_holders:
            return []
        
        agent_locks = []
        for lock_key in self._lock_holders[agent_id]:
            if lock_key in self._active_locks:
                agent_locks.append(self._active_locks[lock_key])
        
        return agent_locks
    
    async def release_all_agent_locks(self, agent_id: UUID) -> int:
        """Release all locks held by a specific agent."""
        agent_locks = await self.get_agent_locks(agent_id)
        released_count = 0
        
        for lock_token in agent_locks:
            if await self.release_lock(lock_token):
                released_count += 1
        
        self.logger.logger.info(
            f"Released {released_count} locks for agent {agent_id}",
            extra={'agent_id': str(agent_id)}
        )
        
        return released_count
    
    async def _check_deadlock_risk(self, agent_id: UUID, lock_key: str) -> bool:
        """Check for potential deadlock scenarios."""
        # Simple deadlock detection: check if agent already holds other locks
        # In a more sophisticated implementation, you'd build a wait-for graph
        
        if agent_id not in self._lock_holders:
            return False
        
        held_locks_count = len(self._lock_holders[agent_id])
        
        # Risk of deadlock if agent already holds multiple locks
        return held_locks_count >= 3
    
    def _update_avg_lock_duration(self, duration: float) -> None:
        """Update average lock duration metric."""
        current_avg = self.metrics['avg_lock_duration']
        alpha = 0.1  # Smoothing factor
        self.metrics['avg_lock_duration'] = alpha * duration + (1 - alpha) * current_avg
    
    def get_metrics(self) -> Dict[str, any]:
        """Get lock manager metrics."""
        return {
            **self.metrics,
            'active_locks': len(self._active_locks),
            'agents_with_locks': len(self._lock_holders),
            'total_tracked_locks': sum(len(locks) for locks in self._lock_holders.values())
        }
    
    def get_lock_status(self) -> Dict[str, any]:
        """Get detailed lock status information."""
        agent_lock_counts = {
            str(agent_id): len(locks) 
            for agent_id, locks in self._lock_holders.items()
        }
        
        return {
            'total_active_locks': len(self._active_locks),
            'agent_lock_distribution': agent_lock_counts,
            'metrics': self.get_metrics()
        }