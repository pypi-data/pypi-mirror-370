"""
Conflict Resolution Manager for Redis-based state management.

Handles conflicts when multiple agents attempt to modify the same state.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from uuid import UUID, uuid4
from aioredis import Redis

from .types import (
    StateKey, StateValue, ConflictResolution, ConflictResolutionStrategy,
    StateChangeType
)
from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError


class ConflictResolver:
    """
    Manages conflict detection and resolution for distributed state.
    
    Features:
    - Multiple resolution strategies
    - Custom conflict resolution functions
    - Automatic conflict detection
    - Resolution history tracking
    - Performance optimization
    """
    
    def __init__(
        self,
        redis: Redis,
        default_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.LAST_WRITE_WINS,
        max_resolution_history: int = 1000,
        resolution_timeout: float = 5.0
    ):
        """Initialize conflict resolver."""
        self.redis = redis
        self.default_strategy = default_strategy
        self.max_resolution_history = max_resolution_history
        self.resolution_timeout = resolution_timeout
        
        self.logger = MAOSLogger("conflict_resolver", str(uuid4()))
        
        # Custom resolvers for specific keys or patterns
        self._custom_resolvers: Dict[str, Callable] = {}
        self._key_strategies: Dict[str, ConflictResolutionStrategy] = {}
        
        # Resolution history
        self._resolution_history: List[ConflictResolution] = []
        
        # Performance metrics
        self.metrics = {
            'conflicts_detected': 0,
            'conflicts_resolved': 0,
            'resolution_failures': 0,
            'avg_resolution_time_ms': 0.0,
            'strategy_usage': {
                strategy.value: 0 for strategy in ConflictResolutionStrategy
            }
        }
        
        # Built-in resolution strategies
        self._resolution_strategies = {
            ConflictResolutionStrategy.LAST_WRITE_WINS: self._resolve_last_write_wins,
            ConflictResolutionStrategy.FIRST_WRITE_WINS: self._resolve_first_write_wins,
            ConflictResolutionStrategy.MERGE: self._resolve_merge,
            ConflictResolutionStrategy.REJECT: self._resolve_reject
        }
    
    def _get_conflict_key(self, state_key: StateKey) -> str:
        """Generate Redis key for conflict tracking."""
        return f"conflict:{state_key}"
    
    def _get_resolution_history_key(self, state_key: StateKey) -> str:
        """Generate Redis key for resolution history."""
        return f"resolution_history:{state_key}"
    
    async def detect_conflict(
        self,
        key: StateKey,
        proposed_value: StateValue,
        current_value: Optional[StateValue] = None
    ) -> bool:
        """
        Detect if there's a conflict for a state update.
        
        Args:
            key: State key
            proposed_value: Value being proposed for update
            current_value: Current value in the system
            
        Returns:
            True if conflict is detected
        """
        try:
            # Get current value if not provided
            if current_value is None:
                # This would typically come from the main state manager
                # For now, we'll simulate getting it from Redis
                current_data = await self.redis.get(str(key))
                if current_data:
                    current_value = StateValue.from_dict(json.loads(current_data))
            
            if current_value is None:
                # No current value, no conflict
                return False
            
            # Check for version conflicts
            if hasattr(proposed_value, 'version') and hasattr(current_value, 'version'):
                # Conflict if proposed version is not exactly current version + 1
                if proposed_value.version <= current_value.version:
                    self.logger.logger.warning(
                        f"Version conflict detected for key: {key}",
                        extra={
                            'key': str(key),
                            'proposed_version': proposed_value.version,
                            'current_version': current_value.version
                        }
                    )
                    return True
            
            # Check for timestamp conflicts (concurrent writes)
            if hasattr(proposed_value, 'updated_at') and hasattr(current_value, 'updated_at'):
                time_diff = abs((proposed_value.updated_at - current_value.updated_at).total_seconds())
                
                # Conflict if updates are very close in time (potential race condition)
                if time_diff < 1.0:  # Within 1 second
                    self.logger.logger.warning(
                        f"Timestamp conflict detected for key: {key}",
                        extra={
                            'key': str(key),
                            'time_diff_seconds': time_diff,
                            'proposed_timestamp': proposed_value.updated_at.isoformat(),
                            'current_timestamp': current_value.updated_at.isoformat()
                        }
                    )
                    return True
            
            return False
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'detect_conflict',
                'key': str(key)
            })
            return False
    
    async def resolve_conflict(
        self,
        key: StateKey,
        conflicted_values: List[StateValue],
        strategy: Optional[ConflictResolutionStrategy] = None,
        custom_resolver: Optional[Callable] = None
    ) -> ConflictResolution:
        """
        Resolve a conflict between multiple state values.
        
        Args:
            key: State key
            conflicted_values: List of conflicting values
            strategy: Resolution strategy to use
            custom_resolver: Custom resolution function
            
        Returns:
            ConflictResolution with the winning value
        """
        start_time = time.time()
        
        try:
            self.metrics['conflicts_detected'] += 1
            
            # Determine resolution strategy
            if custom_resolver:
                strategy = ConflictResolutionStrategy.CUSTOM
            elif strategy is None:
                strategy = self._key_strategies.get(str(key), self.default_strategy)
            
            # Resolve the conflict
            if strategy == ConflictResolutionStrategy.CUSTOM and custom_resolver:
                winning_value = await self._resolve_custom(conflicted_values, custom_resolver)
            else:
                resolver_func = self._resolution_strategies.get(strategy)
                if not resolver_func:
                    raise MAOSError(f"Unknown resolution strategy: {strategy}")
                
                winning_value = await resolver_func(conflicted_values)
            
            # Create resolution record
            resolution = ConflictResolution(
                strategy=strategy,
                winning_value=winning_value,
                conflicted_values=conflicted_values,
                resolution_metadata={
                    'resolver_id': str(uuid4()),
                    'key': str(key),
                    'num_conflicted_values': len(conflicted_values),
                    'resolution_time_ms': (time.time() - start_time) * 1000
                }
            )
            
            # Record resolution
            await self._record_resolution(key, resolution)
            
            # Update metrics
            self.metrics['conflicts_resolved'] += 1
            self.metrics['strategy_usage'][strategy.value] += 1
            
            resolution_time_ms = (time.time() - start_time) * 1000
            self._update_avg_resolution_time(resolution_time_ms)
            
            self.logger.logger.info(
                f"Conflict resolved for key: {key}",
                extra={
                    'key': str(key),
                    'strategy': strategy.value,
                    'conflicted_values': len(conflicted_values),
                    'resolution_time_ms': resolution_time_ms,
                    'winning_version': winning_value.version if hasattr(winning_value, 'version') else None
                }
            )
            
            return resolution
            
        except Exception as e:
            self.metrics['resolution_failures'] += 1
            self.logger.log_error(e, {
                'operation': 'resolve_conflict',
                'key': str(key),
                'strategy': strategy.value if strategy else 'unknown'
            })
            raise MAOSError(f"Failed to resolve conflict: {str(e)}")
    
    async def _resolve_last_write_wins(self, conflicted_values: List[StateValue]) -> StateValue:
        """Resolve conflict using last-write-wins strategy."""
        if not conflicted_values:
            raise MAOSError("No values to resolve")
        
        # Find value with latest timestamp
        latest_value = max(conflicted_values, key=lambda v: v.updated_at)
        
        self.logger.logger.debug(
            "Resolved conflict using last-write-wins",
            extra={
                'winning_timestamp': latest_value.updated_at.isoformat(),
                'num_values': len(conflicted_values)
            }
        )
        
        return latest_value
    
    async def _resolve_first_write_wins(self, conflicted_values: List[StateValue]) -> StateValue:
        """Resolve conflict using first-write-wins strategy."""
        if not conflicted_values:
            raise MAOSError("No values to resolve")
        
        # Find value with earliest timestamp
        earliest_value = min(conflicted_values, key=lambda v: v.updated_at)
        
        self.logger.logger.debug(
            "Resolved conflict using first-write-wins",
            extra={
                'winning_timestamp': earliest_value.updated_at.isoformat(),
                'num_values': len(conflicted_values)
            }
        )
        
        return earliest_value
    
    async def _resolve_merge(self, conflicted_values: List[StateValue]) -> StateValue:
        """Resolve conflict by merging values."""
        if not conflicted_values:
            raise MAOSError("No values to resolve")
        
        if len(conflicted_values) == 1:
            return conflicted_values[0]
        
        # Sort by timestamp
        sorted_values = sorted(conflicted_values, key=lambda v: v.updated_at)
        
        # Start with the earliest value as base
        merged_value = StateValue(
            data=sorted_values[0].data,
            version=max(v.version for v in conflicted_values if hasattr(v, 'version')),
            created_at=min(v.created_at for v in conflicted_values),
            updated_at=max(v.updated_at for v in conflicted_values),
            metadata={}
        )
        
        # Merge data based on type
        try:
            if isinstance(merged_value.data, dict):
                # Merge dictionaries
                for value in sorted_values[1:]:
                    if isinstance(value.data, dict):
                        merged_value.data.update(value.data)
            
            elif isinstance(merged_value.data, list):
                # Merge lists (remove duplicates)
                merged_list = list(merged_value.data)
                for value in sorted_values[1:]:
                    if isinstance(value.data, list):
                        for item in value.data:
                            if item not in merged_list:
                                merged_list.append(item)
                merged_value.data = merged_list
            
            else:
                # For non-mergeable types, use last write wins
                merged_value.data = sorted_values[-1].data
            
            # Merge metadata
            for value in sorted_values:
                if hasattr(value, 'metadata') and value.metadata:
                    merged_value.metadata.update(value.metadata)
            
            # Add merge metadata
            merged_value.metadata['merge_info'] = {
                'merged_from_versions': [v.version for v in conflicted_values if hasattr(v, 'version')],
                'merge_timestamp': datetime.utcnow().isoformat(),
                'merge_strategy': 'automatic'
            }
            
            self.logger.logger.debug(
                "Resolved conflict using merge strategy",
                extra={
                    'merged_from_count': len(conflicted_values),
                    'merge_type': type(merged_value.data).__name__
                }
            )
            
            return merged_value
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'merge_resolution'})
            # Fallback to last write wins if merge fails
            return await self._resolve_last_write_wins(conflicted_values)
    
    async def _resolve_reject(self, conflicted_values: List[StateValue]) -> StateValue:
        """Resolve conflict by rejecting the update (keeping first value)."""
        if not conflicted_values:
            raise MAOSError("No values to resolve")
        
        # Keep the first value (usually the current value)
        rejected_value = conflicted_values[0]
        
        # Add rejection metadata
        if not hasattr(rejected_value, 'metadata'):
            rejected_value.metadata = {}
        
        rejected_value.metadata['conflict_info'] = {
            'resolution_strategy': 'reject',
            'rejected_updates': len(conflicted_values) - 1,
            'rejection_timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.logger.debug(
            "Resolved conflict using reject strategy",
            extra={
                'rejected_updates': len(conflicted_values) - 1,
                'kept_version': rejected_value.version if hasattr(rejected_value, 'version') else None
            }
        )
        
        return rejected_value
    
    async def _resolve_custom(
        self,
        conflicted_values: List[StateValue],
        resolver_func: Callable
    ) -> StateValue:
        """Resolve conflict using custom resolver function."""
        try:
            # Call custom resolver with timeout
            if asyncio.iscoroutinefunction(resolver_func):
                winning_value = await asyncio.wait_for(
                    resolver_func(conflicted_values),
                    timeout=self.resolution_timeout
                )
            else:
                winning_value = resolver_func(conflicted_values)
            
            if not isinstance(winning_value, StateValue):
                raise MAOSError("Custom resolver must return a StateValue")
            
            # Add custom resolution metadata
            if not hasattr(winning_value, 'metadata'):
                winning_value.metadata = {}
            
            winning_value.metadata['custom_resolution'] = {
                'resolver_function': resolver_func.__name__ if hasattr(resolver_func, '__name__') else 'unknown',
                'resolution_timestamp': datetime.utcnow().isoformat()
            }
            
            self.logger.logger.debug(
                "Resolved conflict using custom resolver",
                extra={
                    'resolver_function': resolver_func.__name__ if hasattr(resolver_func, '__name__') else 'unknown',
                    'num_values': len(conflicted_values)
                }
            )
            
            return winning_value
            
        except asyncio.TimeoutError:
            self.logger.logger.error(f"Custom resolver timed out after {self.resolution_timeout}s")
            # Fallback to default strategy
            return await self._resolve_last_write_wins(conflicted_values)
        
        except Exception as e:
            self.logger.log_error(e, {'operation': 'custom_resolution'})
            # Fallback to default strategy
            return await self._resolve_last_write_wins(conflicted_values)
    
    async def _record_resolution(
        self,
        key: StateKey,
        resolution: ConflictResolution
    ) -> None:
        """Record conflict resolution in history."""
        try:
            # Add to in-memory history
            self._resolution_history.append(resolution)
            
            # Maintain history size limit
            if len(self._resolution_history) > self.max_resolution_history:
                self._resolution_history = self._resolution_history[-self.max_resolution_history:]
            
            # Store in Redis for persistence
            history_key = self._get_resolution_history_key(key)
            resolution_record = {
                'strategy': resolution.strategy.value,
                'resolved_at': resolution.resolved_at.isoformat(),
                'winning_version': resolution.winning_value.version if hasattr(resolution.winning_value, 'version') else None,
                'conflicted_count': len(resolution.conflicted_values),
                'metadata': resolution.resolution_metadata
            }
            
            await self.redis.lpush(
                history_key,
                json.dumps(resolution_record, default=str)
            )
            
            # Keep only recent history in Redis
            await self.redis.ltrim(history_key, 0, self.max_resolution_history - 1)
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'record_resolution',
                'key': str(key)
            })
    
    def set_key_strategy(
        self,
        key_pattern: str,
        strategy: ConflictResolutionStrategy
    ) -> None:
        """Set resolution strategy for specific keys or patterns."""
        self._key_strategies[key_pattern] = strategy
        
        self.logger.logger.info(
            f"Set resolution strategy for pattern: {key_pattern}",
            extra={
                'pattern': key_pattern,
                'strategy': strategy.value
            }
        )
    
    def set_custom_resolver(
        self,
        key_pattern: str,
        resolver_func: Callable
    ) -> None:
        """Set custom resolver function for specific keys or patterns."""
        self._custom_resolvers[key_pattern] = resolver_func
        
        self.logger.logger.info(
            f"Set custom resolver for pattern: {key_pattern}",
            extra={
                'pattern': key_pattern,
                'resolver': resolver_func.__name__ if hasattr(resolver_func, '__name__') else 'unknown'
            }
        )
    
    def get_resolution_history(
        self,
        key: Optional[StateKey] = None,
        limit: int = 100
    ) -> List[ConflictResolution]:
        """Get conflict resolution history."""
        if key is None:
            # Return global history
            return self._resolution_history[-limit:]
        else:
            # Filter by key
            key_str = str(key)
            filtered_history = [
                resolution for resolution in self._resolution_history
                if resolution.resolution_metadata.get('key') == key_str
            ]
            return filtered_history[-limit:]
    
    async def get_resolution_stats(self, key: StateKey) -> Dict[str, Any]:
        """Get resolution statistics for a specific key."""
        try:
            history_key = self._get_resolution_history_key(key)
            
            # Get resolution history from Redis
            history_data = await self.redis.lrange(history_key, 0, -1)
            
            if not history_data:
                return {
                    'total_resolutions': 0,
                    'strategy_breakdown': {},
                    'average_conflicts_per_resolution': 0
                }
            
            strategy_counts = {}
            total_conflicts = 0
            
            for record_data in history_data:
                try:
                    record = json.loads(record_data)
                    strategy = record.get('strategy', 'unknown')
                    strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
                    total_conflicts += record.get('conflicted_count', 0)
                except json.JSONDecodeError:
                    continue
            
            return {
                'total_resolutions': len(history_data),
                'strategy_breakdown': strategy_counts,
                'average_conflicts_per_resolution': total_conflicts / len(history_data) if history_data else 0
            }
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'get_resolution_stats',
                'key': str(key)
            })
            return {}
    
    def _update_avg_resolution_time(self, resolution_time_ms: float) -> None:
        """Update average resolution time metric."""
        current_avg = self.metrics['avg_resolution_time_ms']
        alpha = 0.1  # Smoothing factor
        self.metrics['avg_resolution_time_ms'] = alpha * resolution_time_ms + (1 - alpha) * current_avg
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get conflict resolver metrics."""
        return {
            **self.metrics,
            'active_custom_resolvers': len(self._custom_resolvers),
            'active_key_strategies': len(self._key_strategies),
            'resolution_history_size': len(self._resolution_history)
        }
    
    def get_strategy_effectiveness(self) -> Dict[str, float]:
        """Get effectiveness metrics for each resolution strategy."""
        total_resolutions = sum(self.metrics['strategy_usage'].values())
        
        if total_resolutions == 0:
            return {}
        
        effectiveness = {}
        for strategy, usage_count in self.metrics['strategy_usage'].items():
            effectiveness[strategy] = (usage_count / total_resolutions) * 100
        
        return effectiveness