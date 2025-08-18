"""
Redis Data Structures Manager for complex data operations.

Provides high-level interfaces for Redis data structures (lists, sets, sorted sets, hashes).
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from uuid import uuid4
from aioredis import Redis

from .types import StateKey
from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError


class RedisListOperations:
    """Operations for Redis lists."""
    
    def __init__(self, redis: Redis, key: StateKey, logger: MAOSLogger):
        self.redis = redis
        self.key = str(key)
        self.logger = logger
    
    async def push_left(self, value: Any) -> int:
        """Push value to the left (beginning) of the list."""
        serialized_value = json.dumps(value, default=str)
        return await self.redis.lpush(self.key, serialized_value)
    
    async def push_right(self, value: Any) -> int:
        """Push value to the right (end) of the list."""
        serialized_value = json.dumps(value, default=str)
        return await self.redis.rpush(self.key, serialized_value)
    
    async def pop_left(self) -> Optional[Any]:
        """Pop value from the left (beginning) of the list."""
        value = await self.redis.lpop(self.key)
        return json.loads(value) if value else None
    
    async def pop_right(self) -> Optional[Any]:
        """Pop value from the right (end) of the list."""
        value = await self.redis.rpop(self.key)
        return json.loads(value) if value else None
    
    async def get_range(self, start: int = 0, end: int = -1) -> List[Any]:
        """Get a range of values from the list."""
        values = await self.redis.lrange(self.key, start, end)
        return [json.loads(v) for v in values]
    
    async def set_index(self, index: int, value: Any) -> bool:
        """Set value at specific index."""
        try:
            serialized_value = json.dumps(value, default=str)
            await self.redis.lset(self.key, index, serialized_value)
            return True
        except Exception:
            return False
    
    async def get_index(self, index: int) -> Optional[Any]:
        """Get value at specific index."""
        value = await self.redis.lindex(self.key, index)
        return json.loads(value) if value else None
    
    async def length(self) -> int:
        """Get length of the list."""
        return await self.redis.llen(self.key)
    
    async def trim(self, start: int, end: int) -> bool:
        """Trim list to specified range."""
        try:
            await self.redis.ltrim(self.key, start, end)
            return True
        except Exception:
            return False
    
    async def remove(self, count: int, value: Any) -> int:
        """Remove occurrences of value from list."""
        serialized_value = json.dumps(value, default=str)
        return await self.redis.lrem(self.key, count, serialized_value)
    
    async def insert_before(self, pivot: Any, value: Any) -> int:
        """Insert value before pivot."""
        serialized_pivot = json.dumps(pivot, default=str)
        serialized_value = json.dumps(value, default=str)
        return await self.redis.linsert(self.key, "BEFORE", serialized_pivot, serialized_value)
    
    async def insert_after(self, pivot: Any, value: Any) -> int:
        """Insert value after pivot."""
        serialized_pivot = json.dumps(pivot, default=str)
        serialized_value = json.dumps(value, default=str)
        return await self.redis.linsert(self.key, "AFTER", serialized_pivot, serialized_value)


class RedisSetOperations:
    """Operations for Redis sets."""
    
    def __init__(self, redis: Redis, key: StateKey, logger: MAOSLogger):
        self.redis = redis
        self.key = str(key)
        self.logger = logger
    
    async def add(self, *values: Any) -> int:
        """Add values to the set."""
        serialized_values = [json.dumps(v, default=str) for v in values]
        return await self.redis.sadd(self.key, *serialized_values)
    
    async def remove(self, *values: Any) -> int:
        """Remove values from the set."""
        serialized_values = [json.dumps(v, default=str) for v in values]
        return await self.redis.srem(self.key, *serialized_values)
    
    async def members(self) -> Set[Any]:
        """Get all members of the set."""
        values = await self.redis.smembers(self.key)
        return {json.loads(v) for v in values}
    
    async def is_member(self, value: Any) -> bool:
        """Check if value is a member of the set."""
        serialized_value = json.dumps(value, default=str)
        return await self.redis.sismember(self.key, serialized_value)
    
    async def size(self) -> int:
        """Get size of the set."""
        return await self.redis.scard(self.key)
    
    async def pop(self, count: int = 1) -> List[Any]:
        """Remove and return random members from the set."""
        values = await self.redis.spop(self.key, count)
        if isinstance(values, bytes):
            return [json.loads(values)]
        return [json.loads(v) for v in values] if values else []
    
    async def random_members(self, count: int = 1) -> List[Any]:
        """Get random members without removing them."""
        values = await self.redis.srandmember(self.key, count)
        if isinstance(values, bytes):
            return [json.loads(values)]
        return [json.loads(v) for v in values] if values else []
    
    async def move(self, destination_key: str, value: Any) -> bool:
        """Move value from this set to destination set."""
        serialized_value = json.dumps(value, default=str)
        return await self.redis.smove(self.key, destination_key, serialized_value)
    
    async def union(self, *other_keys: str) -> Set[Any]:
        """Get union with other sets."""
        values = await self.redis.sunion(self.key, *other_keys)
        return {json.loads(v) for v in values}
    
    async def intersection(self, *other_keys: str) -> Set[Any]:
        """Get intersection with other sets."""
        values = await self.redis.sinter(self.key, *other_keys)
        return {json.loads(v) for v in values}
    
    async def difference(self, *other_keys: str) -> Set[Any]:
        """Get difference with other sets."""
        values = await self.redis.sdiff(self.key, *other_keys)
        return {json.loads(v) for v in values}


class RedisSortedSetOperations:
    """Operations for Redis sorted sets."""
    
    def __init__(self, redis: Redis, key: StateKey, logger: MAOSLogger):
        self.redis = redis
        self.key = str(key)
        self.logger = logger
    
    async def add(self, score_value_pairs: Dict[float, Any]) -> int:
        """Add members with scores to the sorted set."""
        mapping = {}
        for score, value in score_value_pairs.items():
            serialized_value = json.dumps(value, default=str)
            mapping[serialized_value] = score
        return await self.redis.zadd(self.key, mapping)
    
    async def remove(self, *values: Any) -> int:
        """Remove members from the sorted set."""
        serialized_values = [json.dumps(v, default=str) for v in values]
        return await self.redis.zrem(self.key, *serialized_values)
    
    async def score(self, value: Any) -> Optional[float]:
        """Get score of a member."""
        serialized_value = json.dumps(value, default=str)
        return await self.redis.zscore(self.key, serialized_value)
    
    async def rank(self, value: Any, reverse: bool = False) -> Optional[int]:
        """Get rank of a member."""
        serialized_value = json.dumps(value, default=str)
        if reverse:
            return await self.redis.zrevrank(self.key, serialized_value)
        return await self.redis.zrank(self.key, serialized_value)
    
    async def range_by_rank(
        self,
        start: int = 0,
        end: int = -1,
        reverse: bool = False,
        with_scores: bool = False
    ) -> Union[List[Any], List[Tuple[Any, float]]]:
        """Get members by rank range."""
        if reverse:
            result = await self.redis.zrevrange(self.key, start, end, withscores=with_scores)
        else:
            result = await self.redis.zrange(self.key, start, end, withscores=with_scores)
        
        if with_scores:
            return [(json.loads(v), s) for v, s in result]
        return [json.loads(v) for v in result]
    
    async def range_by_score(
        self,
        min_score: float,
        max_score: float,
        offset: int = 0,
        count: Optional[int] = None,
        with_scores: bool = False
    ) -> Union[List[Any], List[Tuple[Any, float]]]:
        """Get members by score range."""
        result = await self.redis.zrangebyscore(
            self.key,
            min_score,
            max_score,
            start=offset,
            num=count,
            withscores=with_scores
        )
        
        if with_scores:
            return [(json.loads(v), s) for v, s in result]
        return [json.loads(v) for v in result]
    
    async def count(self, min_score: float = float('-inf'), max_score: float = float('inf')) -> int:
        """Count members in score range."""
        return await self.redis.zcount(self.key, min_score, max_score)
    
    async def increment_score(self, value: Any, increment: float) -> float:
        """Increment score of a member."""
        serialized_value = json.dumps(value, default=str)
        return await self.redis.zincrby(self.key, increment, serialized_value)
    
    async def size(self) -> int:
        """Get size of the sorted set."""
        return await self.redis.zcard(self.key)
    
    async def remove_by_rank(self, start: int, end: int) -> int:
        """Remove members by rank range."""
        return await self.redis.zremrangebyrank(self.key, start, end)
    
    async def remove_by_score(self, min_score: float, max_score: float) -> int:
        """Remove members by score range."""
        return await self.redis.zremrangebyscore(self.key, min_score, max_score)


class RedisHashOperations:
    """Operations for Redis hashes."""
    
    def __init__(self, redis: Redis, key: StateKey, logger: MAOSLogger):
        self.redis = redis
        self.key = str(key)
        self.logger = logger
    
    async def set(self, field: str, value: Any) -> bool:
        """Set field value in hash."""
        serialized_value = json.dumps(value, default=str)
        return await self.redis.hset(self.key, field, serialized_value)
    
    async def set_multiple(self, field_value_pairs: Dict[str, Any]) -> bool:
        """Set multiple field values in hash."""
        mapping = {}
        for field, value in field_value_pairs.items():
            mapping[field] = json.dumps(value, default=str)
        return await self.redis.hset(self.key, mapping=mapping)
    
    async def get(self, field: str) -> Optional[Any]:
        """Get field value from hash."""
        value = await self.redis.hget(self.key, field)
        return json.loads(value) if value else None
    
    async def get_multiple(self, *fields: str) -> List[Optional[Any]]:
        """Get multiple field values from hash."""
        values = await self.redis.hmget(self.key, *fields)
        return [json.loads(v) if v else None for v in values]
    
    async def get_all(self) -> Dict[str, Any]:
        """Get all field-value pairs from hash."""
        data = await self.redis.hgetall(self.key)
        return {field: json.loads(value) for field, value in data.items()}
    
    async def delete(self, *fields: str) -> int:
        """Delete fields from hash."""
        return await self.redis.hdel(self.key, *fields)
    
    async def exists(self, field: str) -> bool:
        """Check if field exists in hash."""
        return await self.redis.hexists(self.key, field)
    
    async def keys(self) -> List[str]:
        """Get all field names in hash."""
        return await self.redis.hkeys(self.key)
    
    async def values(self) -> List[Any]:
        """Get all values in hash."""
        values = await self.redis.hvals(self.key)
        return [json.loads(v) for v in values]
    
    async def length(self) -> int:
        """Get number of fields in hash."""
        return await self.redis.hlen(self.key)
    
    async def increment(self, field: str, increment: Union[int, float] = 1) -> Union[int, float]:
        """Increment numeric field value."""
        if isinstance(increment, float):
            return await self.redis.hincrbyfloat(self.key, field, increment)
        return await self.redis.hincrby(self.key, field, increment)
    
    async def set_if_not_exists(self, field: str, value: Any) -> bool:
        """Set field value only if field doesn't exist."""
        serialized_value = json.dumps(value, default=str)
        return await self.redis.hsetnx(self.key, field, serialized_value)


class RedisDataStructures:
    """
    High-level interface for Redis data structures.
    
    Provides typed operations for lists, sets, sorted sets, and hashes.
    """
    
    def __init__(self, redis: Redis):
        """Initialize data structures manager."""
        self.redis = redis
        self.logger = MAOSLogger("redis_data_structures", str(uuid4()))
        
        # Performance metrics
        self.metrics = {
            'list_operations': 0,
            'set_operations': 0,
            'sorted_set_operations': 0,
            'hash_operations': 0,
            'avg_operation_time_ms': 0.0
        }
        
        # Operation tracking
        self._operation_count = 0
        self._total_operation_time = 0.0
    
    def get_list_operations(self, key: StateKey) -> RedisListOperations:
        """Get list operations interface for a key."""
        self.metrics['list_operations'] += 1
        return RedisListOperations(self.redis, key, self.logger)
    
    def get_set_operations(self, key: StateKey) -> RedisSetOperations:
        """Get set operations interface for a key."""
        self.metrics['set_operations'] += 1
        return RedisSetOperations(self.redis, key, self.logger)
    
    def get_sorted_set_operations(self, key: StateKey) -> RedisSortedSetOperations:
        """Get sorted set operations interface for a key."""
        self.metrics['sorted_set_operations'] += 1
        return RedisSortedSetOperations(self.redis, key, self.logger)
    
    def get_hash_operations(self, key: StateKey) -> RedisHashOperations:
        """Get hash operations interface for a key."""
        self.metrics['hash_operations'] += 1
        return RedisHashOperations(self.redis, key, self.logger)
    
    async def get_key_type(self, key: StateKey) -> Optional[str]:
        """Get the type of a Redis key."""
        try:
            key_type = await self.redis.type(str(key))
            return key_type if key_type != "none" else None
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'get_key_type',
                'key': str(key)
            })
            return None
    
    async def exists(self, key: StateKey) -> bool:
        """Check if key exists."""
        try:
            return await self.redis.exists(str(key)) > 0
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'exists',
                'key': str(key)
            })
            return False
    
    async def delete(self, *keys: StateKey) -> int:
        """Delete keys."""
        try:
            str_keys = [str(key) for key in keys]
            return await self.redis.delete(*str_keys)
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'delete',
                'keys': [str(key) for key in keys]
            })
            return 0
    
    async def expire(self, key: StateKey, seconds: int) -> bool:
        """Set expiration time for key."""
        try:
            return await self.redis.expire(str(key), seconds)
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'expire',
                'key': str(key),
                'seconds': seconds
            })
            return False
    
    async def ttl(self, key: StateKey) -> int:
        """Get time-to-live for key."""
        try:
            return await self.redis.ttl(str(key))
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'ttl',
                'key': str(key)
            })
            return -2  # Key doesn't exist
    
    async def rename(self, old_key: StateKey, new_key: StateKey) -> bool:
        """Rename a key."""
        try:
            await self.redis.rename(str(old_key), str(new_key))
            return True
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'rename',
                'old_key': str(old_key),
                'new_key': str(new_key)
            })
            return False
    
    async def copy(self, source_key: StateKey, dest_key: StateKey, replace: bool = False) -> bool:
        """Copy a key to another key."""
        try:
            # Redis COPY command (Redis 6.2+)
            # For older versions, we'd need to implement copy based on key type
            if replace:
                result = await self.redis.copy(str(source_key), str(dest_key), replace=True)
            else:
                result = await self.redis.copy(str(source_key), str(dest_key))
            return result
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'copy',
                'source_key': str(source_key),
                'dest_key': str(dest_key)
            })
            return False
    
    async def scan_keys(
        self,
        pattern: str = "*",
        count: int = 1000
    ) -> List[StateKey]:
        """Scan for keys matching pattern."""
        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern, count=count):
                try:
                    # Parse key back to StateKey format
                    key_str = key.decode() if isinstance(key, bytes) else key
                    if ":" in key_str:
                        state_key = StateKey.from_string(key_str)
                        keys.append(state_key)
                except Exception:
                    # Skip keys that don't match our format
                    continue
            
            return keys
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'scan_keys',
                'pattern': pattern
            })
            return []
    
    async def get_memory_usage(self, key: StateKey) -> Optional[int]:
        """Get memory usage of a key in bytes."""
        try:
            return await self.redis.memory_usage(str(key))
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'get_memory_usage',
                'key': str(key)
            })
            return None
    
    async def pipeline_operations(self, operations: List[Dict[str, Any]]) -> List[Any]:
        """Execute multiple operations in a pipeline for better performance."""
        try:
            start_time = time.time()
            
            pipeline = self.redis.pipeline()
            
            for operation in operations:
                op_type = operation.get('type')
                key = operation.get('key')
                
                if op_type == 'set':
                    pipeline.set(key, json.dumps(operation.get('value'), default=str))
                elif op_type == 'get':
                    pipeline.get(key)
                elif op_type == 'delete':
                    pipeline.delete(key)
                elif op_type == 'exists':
                    pipeline.exists(key)
                elif op_type == 'expire':
                    pipeline.expire(key, operation.get('seconds', 3600))
                # Add more operation types as needed
            
            results = await pipeline.execute()
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                op_type = operations[i].get('type')
                if op_type == 'get' and result:
                    processed_results.append(json.loads(result))
                else:
                    processed_results.append(result)
            
            # Update metrics
            operation_time = (time.time() - start_time) * 1000
            self._update_metrics(len(operations), operation_time)
            
            self.logger.logger.debug(
                f"Executed pipeline with {len(operations)} operations",
                extra={
                    'operations_count': len(operations),
                    'execution_time_ms': operation_time
                }
            )
            
            return processed_results
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'pipeline_operations',
                'operations_count': len(operations)
            })
            return []
    
    async def transaction_operations(
        self,
        operations: List[Dict[str, Any]],
        watch_keys: Optional[List[StateKey]] = None
    ) -> bool:
        """Execute operations in a transaction (MULTI/EXEC)."""
        try:
            start_time = time.time()
            
            # Start transaction
            if watch_keys:
                str_watch_keys = [str(key) for key in watch_keys]
                await self.redis.watch(*str_watch_keys)
            
            transaction = self.redis.multi_exec()
            
            # Add operations to transaction
            for operation in operations:
                op_type = operation.get('type')
                key = operation.get('key')
                
                if op_type == 'set':
                    transaction.set(key, json.dumps(operation.get('value'), default=str))
                elif op_type == 'delete':
                    transaction.delete(key)
                elif op_type == 'expire':
                    transaction.expire(key, operation.get('seconds', 3600))
                elif op_type == 'hset':
                    transaction.hset(key, operation.get('field'), 
                                   json.dumps(operation.get('value'), default=str))
                # Add more operation types as needed
            
            # Execute transaction
            results = await transaction.execute()
            
            success = results is not None  # None means transaction was discarded
            
            # Update metrics
            operation_time = (time.time() - start_time) * 1000
            self._update_metrics(len(operations), operation_time)
            
            self.logger.logger.debug(
                f"Executed transaction with {len(operations)} operations",
                extra={
                    'operations_count': len(operations),
                    'execution_time_ms': operation_time,
                    'success': success
                }
            )
            
            return success
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'transaction_operations',
                'operations_count': len(operations)
            })
            return False
    
    def _update_metrics(self, operation_count: int, operation_time_ms: float) -> None:
        """Update performance metrics."""
        self._operation_count += operation_count
        self._total_operation_time += operation_time_ms
        
        if self._operation_count > 0:
            self.metrics['avg_operation_time_ms'] = self._total_operation_time / self._operation_count
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get data structures performance metrics."""
        return {
            **self.metrics,
            'total_operations': self._operation_count,
            'total_operation_time_ms': self._total_operation_time
        }
    
    async def analyze_key_patterns(self, sample_size: int = 1000) -> Dict[str, Any]:
        """Analyze key patterns and data structure usage."""
        try:
            analysis = {
                'total_keys': 0,
                'type_distribution': {},
                'namespace_distribution': {},
                'category_distribution': {},
                'memory_usage_by_type': {},
                'sample_size': sample_size
            }
            
            # Sample keys
            keys_analyzed = 0
            async for key in self.redis.scan_iter(count=sample_size):
                if keys_analyzed >= sample_size:
                    break
                
                key_str = key.decode() if isinstance(key, bytes) else key
                
                # Get key type
                key_type = await self.redis.type(key)
                if key_type:
                    analysis['type_distribution'][key_type] = \
                        analysis['type_distribution'].get(key_type, 0) + 1
                    
                    # Get memory usage
                    try:
                        memory_usage = await self.redis.memory_usage(key)
                        if memory_usage:
                            if key_type not in analysis['memory_usage_by_type']:
                                analysis['memory_usage_by_type'][key_type] = []
                            analysis['memory_usage_by_type'][key_type].append(memory_usage)
                    except Exception:
                        pass
                
                # Analyze key structure (if it matches our StateKey format)
                if ":" in key_str:
                    try:
                        parts = key_str.split(':')
                        if len(parts) >= 3:
                            namespace = parts[0]
                            category = parts[1]
                            
                            analysis['namespace_distribution'][namespace] = \
                                analysis['namespace_distribution'].get(namespace, 0) + 1
                            analysis['category_distribution'][category] = \
                                analysis['category_distribution'].get(category, 0) + 1
                    except Exception:
                        pass
                
                keys_analyzed += 1
            
            analysis['total_keys'] = keys_analyzed
            
            # Calculate average memory usage by type
            for key_type, memory_usages in analysis['memory_usage_by_type'].items():
                if memory_usages:
                    analysis['memory_usage_by_type'][key_type] = {
                        'avg_bytes': sum(memory_usages) / len(memory_usages),
                        'total_bytes': sum(memory_usages),
                        'count': len(memory_usages)
                    }
            
            return analysis
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'analyze_key_patterns'})
            return {}