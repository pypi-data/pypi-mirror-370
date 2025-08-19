"""
Bulk Operations Manager for Redis-based state management.

Provides high-performance bulk operations for multiple state keys.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
from aioredis import Redis

from .types import StateKey, StateValue, BulkOperation, StateOperationType
from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError


class BulkOperationsManager:
    """
    Manages bulk operations for high-performance state management.
    
    Features:
    - Batch operations with pipelining
    - Transaction support
    - Parallel processing
    - Error handling and rollback
    - Performance optimization
    """
    
    def __init__(
        self,
        redis: Redis,
        max_batch_size: int = 1000,
        max_parallel_batches: int = 10,
        operation_timeout: float = 30.0,
        enable_transactions: bool = True
    ):
        """Initialize bulk operations manager."""
        self.redis = redis
        self.max_batch_size = max_batch_size
        self.max_parallel_batches = max_parallel_batches
        self.operation_timeout = operation_timeout
        self.enable_transactions = enable_transactions
        
        self.logger = MAOSLogger("bulk_operations_manager", str(uuid4()))
        
        # Operation tracking
        self._active_operations: Dict[UUID, BulkOperation] = {}
        
        # Performance metrics
        self.metrics = {
            'bulk_operations_completed': 0,
            'bulk_operations_failed': 0,
            'total_keys_processed': 0,
            'avg_batch_size': 0.0,
            'avg_operation_time_ms': 0.0,
            'throughput_keys_per_second': 0.0
        }
        
        # Operation semaphore for concurrency control
        self._operation_semaphore = asyncio.Semaphore(max_parallel_batches)
        
        # Performance tracking
        self._operation_times: List[float] = []
        self._batch_sizes: List[int] = []
    
    async def bulk_set(
        self,
        operations: Dict[StateKey, StateValue],
        use_transaction: bool = None
    ) -> BulkOperation:
        """
        Perform bulk set operations.
        
        Args:
            operations: Dictionary of key-value pairs to set
            use_transaction: Whether to use transaction (default: auto)
            
        Returns:
            BulkOperation with results
        """
        bulk_op = BulkOperation(operation_type=StateOperationType.BATCH)
        
        # Prepare operations
        for key, value in operations.items():
            bulk_op.add_operation('set', key, value.to_dict())
        
        try:
            return await self._execute_bulk_operation(bulk_op, self._bulk_set_internal, use_transaction)
            
        except Exception as e:
            bulk_op.mark_failed(str(e))
            self.logger.log_error(e, {
                'operation': 'bulk_set',
                'operation_id': str(bulk_op.id),
                'keys_count': len(operations)
            })
            return bulk_op
    
    async def bulk_get(self, keys: List[StateKey]) -> Dict[StateKey, Optional[StateValue]]:
        """
        Perform bulk get operations.
        
        Args:
            keys: List of keys to retrieve
            
        Returns:
            Dictionary of key-value pairs
        """
        start_time = time.time()
        
        try:
            # Split keys into batches
            batches = self._split_into_batches(keys, self.max_batch_size)
            results = {}
            
            # Process batches in parallel
            async with self._operation_semaphore:
                batch_tasks = []
                for batch in batches:
                    task = asyncio.create_task(self._get_batch(batch))
                    batch_tasks.append(task)
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Combine results
                for batch_result in batch_results:
                    if isinstance(batch_result, Exception):
                        self.logger.log_error(batch_result, {'operation': 'bulk_get_batch'})
                        continue
                    
                    if isinstance(batch_result, dict):
                        results.update(batch_result)
            
            # Update metrics
            operation_time = (time.time() - start_time) * 1000
            self._update_metrics(len(keys), operation_time, success=True)
            
            self.logger.logger.debug(
                f"Bulk get completed",
                extra={
                    'keys_requested': len(keys),
                    'keys_found': sum(1 for v in results.values() if v is not None),
                    'operation_time_ms': operation_time
                }
            )
            
            return results
            
        except Exception as e:
            operation_time = (time.time() - start_time) * 1000
            self._update_metrics(len(keys), operation_time, success=False)
            
            self.logger.log_error(e, {
                'operation': 'bulk_get',
                'keys_count': len(keys)
            })
            
            # Return empty results for all keys on error
            return {key: None for key in keys}
    
    async def bulk_delete(
        self,
        keys: List[StateKey],
        use_transaction: bool = None
    ) -> BulkOperation:
        """
        Perform bulk delete operations.
        
        Args:
            keys: List of keys to delete
            use_transaction: Whether to use transaction
            
        Returns:
            BulkOperation with results
        """
        bulk_op = BulkOperation(operation_type=StateOperationType.BATCH)
        
        # Prepare operations
        for key in keys:
            bulk_op.add_operation('delete', key)
        
        try:
            return await self._execute_bulk_operation(bulk_op, self._bulk_delete_internal, use_transaction)
            
        except Exception as e:
            bulk_op.mark_failed(str(e))
            self.logger.log_error(e, {
                'operation': 'bulk_delete',
                'operation_id': str(bulk_op.id),
                'keys_count': len(keys)
            })
            return bulk_op
    
    async def bulk_update(
        self,
        updates: Dict[StateKey, Dict[str, Any]],
        use_transaction: bool = None
    ) -> BulkOperation:
        """
        Perform bulk update operations (partial updates).
        
        Args:
            updates: Dictionary of key -> update fields
            use_transaction: Whether to use transaction
            
        Returns:
            BulkOperation with results
        """
        bulk_op = BulkOperation(operation_type=StateOperationType.ATOMIC_UPDATE)
        
        # Prepare operations
        for key, update_fields in updates.items():
            bulk_op.add_operation('update', key, update_fields)
        
        try:
            return await self._execute_bulk_operation(bulk_op, self._bulk_update_internal, use_transaction)
            
        except Exception as e:
            bulk_op.mark_failed(str(e))
            self.logger.log_error(e, {
                'operation': 'bulk_update',
                'operation_id': str(bulk_op.id),
                'keys_count': len(updates)
            })
            return bulk_op
    
    async def bulk_exists(self, keys: List[StateKey]) -> Dict[StateKey, bool]:
        """
        Check existence of multiple keys.
        
        Args:
            keys: List of keys to check
            
        Returns:
            Dictionary of key -> existence status
        """
        start_time = time.time()
        
        try:
            # Use pipeline for better performance
            pipeline = self.redis.pipeline()
            
            for key in keys:
                pipeline.exists(str(key))
            
            results = await pipeline.execute()
            
            # Map results back to keys
            existence_map = {}
            for i, key in enumerate(keys):
                existence_map[key] = bool(results[i])
            
            operation_time = (time.time() - start_time) * 1000
            self.logger.logger.debug(
                f"Bulk exists check completed",
                extra={
                    'keys_checked': len(keys),
                    'existing_keys': sum(existence_map.values()),
                    'operation_time_ms': operation_time
                }
            )
            
            return existence_map
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'bulk_exists',
                'keys_count': len(keys)
            })
            return {key: False for key in keys}
    
    async def bulk_expire(
        self,
        expirations: Dict[StateKey, int],
        use_transaction: bool = None
    ) -> BulkOperation:
        """
        Set expiration for multiple keys.
        
        Args:
            expirations: Dictionary of key -> expiration time in seconds
            use_transaction: Whether to use transaction
            
        Returns:
            BulkOperation with results
        """
        bulk_op = BulkOperation(operation_type=StateOperationType.BATCH)
        
        # Prepare operations
        for key, expiry in expirations.items():
            bulk_op.add_operation('expire', key, expiry)
        
        try:
            return await self._execute_bulk_operation(bulk_op, self._bulk_expire_internal, use_transaction)
            
        except Exception as e:
            bulk_op.mark_failed(str(e))
            self.logger.log_error(e, {
                'operation': 'bulk_expire',
                'operation_id': str(bulk_op.id),
                'keys_count': len(expirations)
            })
            return bulk_op
    
    async def _execute_bulk_operation(
        self,
        bulk_op: BulkOperation,
        operation_func: Any,
        use_transaction: Optional[bool] = None
    ) -> BulkOperation:
        """Execute a bulk operation with proper error handling and metrics."""
        start_time = time.time()
        bulk_op.status = "running"
        
        # Store operation for tracking
        self._active_operations[bulk_op.id] = bulk_op
        
        try:
            # Determine transaction usage
            if use_transaction is None:
                use_transaction = self.enable_transactions and len(bulk_op.operations) > 10
            
            # Execute with timeout
            await asyncio.wait_for(
                operation_func(bulk_op, use_transaction),
                timeout=self.operation_timeout
            )
            
            bulk_op.mark_completed()
            
            # Update metrics
            operation_time = (time.time() - start_time) * 1000
            self._update_metrics(len(bulk_op.operations), operation_time, success=True)
            self.metrics['bulk_operations_completed'] += 1
            
            self.logger.logger.info(
                f"Bulk operation completed",
                extra={
                    'operation_id': str(bulk_op.id),
                    'operation_type': bulk_op.operation_type.value,
                    'operations_count': len(bulk_op.operations),
                    'operation_time_ms': operation_time,
                    'use_transaction': use_transaction
                }
            )
            
        except asyncio.TimeoutError:
            bulk_op.mark_failed("Operation timed out")
            self.metrics['bulk_operations_failed'] += 1
            
            self.logger.logger.error(
                f"Bulk operation timed out",
                extra={
                    'operation_id': str(bulk_op.id),
                    'timeout_seconds': self.operation_timeout
                }
            )
            
        except Exception as e:
            bulk_op.mark_failed(str(e))
            self.metrics['bulk_operations_failed'] += 1
            
            operation_time = (time.time() - start_time) * 1000
            self._update_metrics(len(bulk_op.operations), operation_time, success=False)
            
            self.logger.log_error(e, {
                'operation': 'execute_bulk_operation',
                'operation_id': str(bulk_op.id)
            })
            
        finally:
            # Remove from active operations
            self._active_operations.pop(bulk_op.id, None)
        
        return bulk_op
    
    async def _bulk_set_internal(self, bulk_op: BulkOperation, use_transaction: bool) -> None:
        """Internal bulk set implementation."""
        if use_transaction:
            await self._bulk_set_transaction(bulk_op)
        else:
            await self._bulk_set_pipeline(bulk_op)
    
    async def _bulk_set_pipeline(self, bulk_op: BulkOperation) -> None:
        """Bulk set using Redis pipeline."""
        # Split into batches for memory efficiency
        operation_batches = self._split_operations_into_batches(bulk_op.operations, self.max_batch_size)
        
        for batch in operation_batches:
            pipeline = self.redis.pipeline()
            
            for operation in batch:
                if operation['type'] == 'set':
                    key = operation['key']
                    value = json.dumps(operation['value'], default=str)
                    pipeline.set(key, value)
            
            batch_results = await pipeline.execute()
            bulk_op.results.extend(batch_results)
    
    async def _bulk_set_transaction(self, bulk_op: BulkOperation) -> None:
        """Bulk set using Redis transaction."""
        # For very large operations, split into multiple transactions
        operation_batches = self._split_operations_into_batches(bulk_op.operations, self.max_batch_size)
        
        for batch in operation_batches:
            transaction = self.redis.multi_exec()
            
            for operation in batch:
                if operation['type'] == 'set':
                    key = operation['key']
                    value = json.dumps(operation['value'], default=str)
                    transaction.set(key, value)
            
            batch_results = await transaction.execute()
            if batch_results is not None:
                bulk_op.results.extend(batch_results)
            else:
                raise MAOSError("Transaction was discarded")
    
    async def _bulk_delete_internal(self, bulk_op: BulkOperation, use_transaction: bool) -> None:
        """Internal bulk delete implementation."""
        if use_transaction:
            await self._bulk_delete_transaction(bulk_op)
        else:
            await self._bulk_delete_pipeline(bulk_op)
    
    async def _bulk_delete_pipeline(self, bulk_op: BulkOperation) -> None:
        """Bulk delete using Redis pipeline."""
        operation_batches = self._split_operations_into_batches(bulk_op.operations, self.max_batch_size)
        
        for batch in operation_batches:
            # Extract keys for batch delete
            keys_to_delete = [op['key'] for op in batch if op['type'] == 'delete']
            
            if keys_to_delete:
                result = await self.redis.delete(*keys_to_delete)
                bulk_op.results.append(result)
    
    async def _bulk_delete_transaction(self, bulk_op: BulkOperation) -> None:
        """Bulk delete using Redis transaction."""
        operation_batches = self._split_operations_into_batches(bulk_op.operations, self.max_batch_size)
        
        for batch in operation_batches:
            keys_to_delete = [op['key'] for op in batch if op['type'] == 'delete']
            
            if keys_to_delete:
                transaction = self.redis.multi_exec()
                transaction.delete(*keys_to_delete)
                
                batch_results = await transaction.execute()
                if batch_results is not None:
                    bulk_op.results.extend(batch_results)
                else:
                    raise MAOSError("Transaction was discarded")
    
    async def _bulk_update_internal(self, bulk_op: BulkOperation, use_transaction: bool) -> None:
        """Internal bulk update implementation."""
        # Updates require individual handling as they need current values
        updated_count = 0
        
        for operation in bulk_op.operations:
            if operation['type'] == 'update':
                key = operation['key']
                update_fields = operation['value']
                
                try:
                    # Get current value
                    current_data = await self.redis.get(key)
                    if current_data:
                        current_value = json.loads(current_data)
                        
                        # Apply updates
                        if isinstance(current_value, dict):
                            current_value.update(update_fields)
                        
                        # Save updated value
                        updated_data = json.dumps(current_value, default=str)
                        await self.redis.set(key, updated_data)
                        updated_count += 1
                        
                except Exception as e:
                    bulk_op.errors.append(f"Update failed for key {key}: {str(e)}")
        
        bulk_op.results.append(updated_count)
    
    async def _bulk_expire_internal(self, bulk_op: BulkOperation, use_transaction: bool) -> None:
        """Internal bulk expire implementation."""
        if use_transaction:
            transaction = self.redis.multi_exec()
            
            for operation in bulk_op.operations:
                if operation['type'] == 'expire':
                    key = operation['key']
                    expiry = operation['value']
                    transaction.expire(key, expiry)
            
            results = await transaction.execute()
            if results is not None:
                bulk_op.results.extend(results)
            else:
                raise MAOSError("Transaction was discarded")
        else:
            pipeline = self.redis.pipeline()
            
            for operation in bulk_op.operations:
                if operation['type'] == 'expire':
                    key = operation['key']
                    expiry = operation['value']
                    pipeline.expire(key, expiry)
            
            results = await pipeline.execute()
            bulk_op.results.extend(results)
    
    async def _get_batch(self, keys: List[StateKey]) -> Dict[StateKey, Optional[StateValue]]:
        """Get a batch of keys using pipeline."""
        pipeline = self.redis.pipeline()
        
        for key in keys:
            pipeline.get(str(key))
        
        results = await pipeline.execute()
        
        # Map results back to keys
        key_value_map = {}
        for i, key in enumerate(keys):
            raw_value = results[i]
            if raw_value:
                try:
                    value_dict = json.loads(raw_value)
                    key_value_map[key] = StateValue.from_dict(value_dict)
                except json.JSONDecodeError:
                    key_value_map[key] = None
            else:
                key_value_map[key] = None
        
        return key_value_map
    
    def _split_into_batches(self, items: List, batch_size: int) -> List[List]:
        """Split items into batches of specified size."""
        batches = []
        for i in range(0, len(items), batch_size):
            batches.append(items[i:i + batch_size])
        return batches
    
    def _split_operations_into_batches(self, operations: List, batch_size: int) -> List[List]:
        """Split operations into batches of specified size."""
        return self._split_into_batches(operations, batch_size)
    
    def _update_metrics(self, keys_count: int, operation_time_ms: float, success: bool) -> None:
        """Update performance metrics."""
        self.metrics['total_keys_processed'] += keys_count
        
        # Update average batch size
        self._batch_sizes.append(keys_count)
        if len(self._batch_sizes) > 1000:  # Keep recent history
            self._batch_sizes = self._batch_sizes[-1000:]
        
        self.metrics['avg_batch_size'] = sum(self._batch_sizes) / len(self._batch_sizes)
        
        if success:
            # Update average operation time
            self._operation_times.append(operation_time_ms)
            if len(self._operation_times) > 1000:
                self._operation_times = self._operation_times[-1000:]
            
            self.metrics['avg_operation_time_ms'] = sum(self._operation_times) / len(self._operation_times)
            
            # Update throughput
            if operation_time_ms > 0:
                keys_per_second = (keys_count / operation_time_ms) * 1000
                
                # Exponential moving average for throughput
                current_throughput = self.metrics['throughput_keys_per_second']
                alpha = 0.1
                self.metrics['throughput_keys_per_second'] = (
                    alpha * keys_per_second + (1 - alpha) * current_throughput
                )
    
    def get_operation_status(self, operation_id: UUID) -> Optional[BulkOperation]:
        """Get status of a bulk operation."""
        return self._active_operations.get(operation_id)
    
    def get_active_operations(self) -> List[BulkOperation]:
        """Get all active bulk operations."""
        return list(self._active_operations.values())
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get bulk operations performance metrics."""
        return {
            **self.metrics,
            'active_operations': len(self._active_operations),
            'max_batch_size': self.max_batch_size,
            'max_parallel_batches': self.max_parallel_batches
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary with recommendations."""
        metrics = self.get_metrics()
        
        # Calculate efficiency metrics
        total_operations = metrics['bulk_operations_completed'] + metrics['bulk_operations_failed']
        success_rate = (metrics['bulk_operations_completed'] / total_operations * 100) if total_operations > 0 else 0
        
        recommendations = []
        
        # Performance recommendations
        if metrics['avg_operation_time_ms'] > 5000:  # 5 seconds
            recommendations.append("Consider reducing batch size or enabling transactions for better performance")
        
        if success_rate < 95:
            recommendations.append("High failure rate detected - check error handling and timeouts")
        
        if metrics['throughput_keys_per_second'] < 100:
            recommendations.append("Low throughput - consider increasing max_parallel_batches")
        
        return {
            'performance_metrics': metrics,
            'success_rate_percentage': success_rate,
            'efficiency_score': min(100, metrics['throughput_keys_per_second'] / 10),  # Simple efficiency score
            'recommendations': recommendations
        }