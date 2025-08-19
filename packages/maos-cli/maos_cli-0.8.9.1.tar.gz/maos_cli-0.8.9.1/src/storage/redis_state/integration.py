"""
Integration module for Redis-based state management with existing MAOS system.

Provides seamless integration with the existing StateManager interface.
"""

import asyncio
from typing import Dict, List, Optional, Any, UUID
from datetime import datetime

from .redis_state_manager import RedisStateManager
from .types import StateKey, StateValue, StateChangeType
from ..interfaces.state_manager import StateManager as MAOSStateManager, StateSnapshot
from ..interfaces.persistence import PersistenceInterface
from ..models.task import Task
from ..models.agent import Agent
from ..models.checkpoint import Checkpoint, CheckpointType
from ..models.message import Message
from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError


class RedisStateManagerIntegration(MAOSStateManager):
    """
    Integration wrapper that makes Redis State Manager compatible with MAOS StateManager interface.
    
    This allows seamless replacement of the existing state manager with the Redis-based solution
    while maintaining full API compatibility.
    """
    
    def __init__(
        self,
        redis_urls: List[str] = None,
        cluster_mode: bool = True,
        memory_pool_size_gb: int = 10,
        enable_monitoring: bool = True,
        enable_backup: bool = True,
        persistence_backend: Optional[PersistenceInterface] = None,
        auto_checkpoint_interval: int = 300,
        max_snapshots: int = 50,
        enable_state_validation: bool = True
    ):
        """Initialize Redis State Manager Integration."""
        # Initialize parent StateManager
        super().__init__(
            persistence_backend=persistence_backend,
            auto_checkpoint_interval=auto_checkpoint_interval,
            max_snapshots=max_snapshots,
            enable_state_validation=enable_state_validation
        )
        
        # Initialize Redis State Manager
        self.redis_manager = RedisStateManager(
            redis_urls=redis_urls,
            cluster_mode=cluster_mode,
            memory_pool_size_gb=memory_pool_size_gb,
            enable_monitoring=enable_monitoring,
            enable_backup=enable_backup
        )
        
        self.logger = MAOSLogger("redis_state_integration", str(UUID.uuid4()))
        
        # Mapping between MAOS objects and Redis state
        self._object_type_mapping = {
            Task: "tasks",
            Agent: "agents", 
            Message: "messages",
            Checkpoint: "checkpoints"
        }
    
    async def start(self) -> None:
        """Start the integrated state manager."""
        try:
            # Initialize Redis manager
            await self.redis_manager.initialize()
            
            # Start parent state manager
            await super().start()
            
            # Set up state synchronization
            await self._setup_state_synchronization()
            
            self.logger.logger.info("Redis State Manager Integration started successfully")
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'start'})
            raise MAOSError(f"Failed to start integrated state manager: {str(e)}")
    
    async def _setup_state_synchronization(self) -> None:
        """Set up bidirectional state synchronization."""
        # Watch for changes in Redis and update local state
        await self.redis_manager.watch_state(
            "*:*:*",
            self._handle_redis_state_change,
            change_types=[StateChangeType.UPDATED, StateChangeType.CREATED, StateChangeType.DELETED]
        )
        
        # Set up local state change listeners
        for category in self._state.keys():
            self.add_change_listener(category, self._handle_local_state_change)
    
    async def _handle_redis_state_change(self, change) -> None:
        """Handle state changes from Redis."""
        try:
            if not change.key:
                return
            
            # Convert Redis key to MAOS category and object ID
            category = change.key.category
            obj_id = UUID(change.key.identifier)
            
            if change.change_type == StateChangeType.DELETED:
                # Remove from local state
                if category in self._state and obj_id in self._state[category]:
                    del self._state[category][obj_id]
                    
            elif change.new_value:
                # Update local state
                obj = self._deserialize_object_from_redis(category, change.new_value)
                if obj:
                    if category not in self._state:
                        self._state[category] = {}
                    self._state[category][obj_id] = obj
            
            self.logger.logger.debug(
                f"Synchronized Redis state change to local state",
                extra={
                    'category': category,
                    'object_id': str(obj_id),
                    'change_type': change.change_type.value
                }
            )
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'handle_redis_state_change',
                'change_id': str(change.id) if change else None
            })
    
    async def _handle_local_state_change(self, category: str, action: str, new_obj: Any, old_obj: Any) -> None:
        """Handle local state changes and sync to Redis."""
        try:
            if new_obj and hasattr(new_obj, 'id'):
                # Convert to Redis format and store
                redis_key = StateKey(
                    namespace="maos",
                    category=category,
                    identifier=str(new_obj.id)
                )
                
                redis_value = self._serialize_object_for_redis(new_obj)
                
                if action == 'updated':
                    await self.redis_manager.set_state(redis_key, redis_value)
                elif action == 'removed' and old_obj:
                    await self.redis_manager.delete_state(redis_key)
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'handle_local_state_change',
                'category': category,
                'action': action
            })
    
    def _serialize_object_for_redis(self, obj: Any) -> StateValue:
        """Serialize MAOS object for Redis storage."""
        try:
            if hasattr(obj, 'to_dict'):
                data = obj.to_dict()
            else:
                # Basic serialization for simple objects
                data = {
                    'type': type(obj).__name__,
                    'data': obj.__dict__ if hasattr(obj, '__dict__') else str(obj)
                }
            
            return StateValue(
                data=data,
                version=getattr(obj, 'version', 1),
                created_at=getattr(obj, 'created_at', datetime.utcnow()),
                updated_at=getattr(obj, 'updated_at', datetime.utcnow()),
                metadata={
                    'object_type': type(obj).__name__,
                    'maos_integration': True
                }
            )
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'serialize_object_for_redis',
                'object_type': type(obj).__name__
            })
            raise
    
    def _deserialize_object_from_redis(self, category: str, redis_value: StateValue) -> Any:
        """Deserialize Redis value back to MAOS object."""
        try:
            object_type = redis_value.metadata.get('object_type')
            data = redis_value.data
            
            # Reconstruct object based on type
            if object_type == 'Task' and category == 'tasks':
                return Task.from_dict(data) if hasattr(Task, 'from_dict') else Task(**data)
            elif object_type == 'Agent' and category == 'agents':
                return Agent.from_dict(data) if hasattr(Agent, 'from_dict') else Agent(**data)
            elif object_type == 'Message' and category == 'messages':
                return Message.from_dict(data) if hasattr(Message, 'from_dict') else Message(**data)
            elif object_type == 'Checkpoint' and category == 'checkpoints':
                return Checkpoint.from_dict(data) if hasattr(Checkpoint, 'from_dict') else Checkpoint(**data)
            else:
                # Generic reconstruction
                return type(object_type, (), data)() if isinstance(data, dict) else data
                
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'deserialize_object_from_redis',
                'category': category,
                'object_type': redis_value.metadata.get('object_type')
            })
            return None
    
    # Override StateManager methods to use Redis backend
    
    async def store_object(self, category: str, obj: Any) -> None:
        """Store an object using Redis backend."""
        try:
            # Store in Redis first
            redis_key = StateKey(
                namespace="maos",
                category=category,
                identifier=str(obj.id)
            )
            
            redis_value = self._serialize_object_for_redis(obj)
            await self.redis_manager.set_state(redis_key, redis_value)
            
            # Also store in local state for compatibility
            await super().store_object(category, obj)
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'store_object',
                'category': category,
                'object_id': str(obj.id) if hasattr(obj, 'id') else 'unknown'
            })
            raise
    
    async def get_object(self, category: str, obj_id: UUID) -> Optional[Any]:
        """Get an object from Redis backend."""
        try:
            # Try Redis first
            redis_key = StateKey(
                namespace="maos",
                category=category,
                identifier=str(obj_id)
            )
            
            redis_value = await self.redis_manager.get_state(redis_key)
            if redis_value:
                return self._deserialize_object_from_redis(category, redis_value)
            
            # Fallback to local state
            return await super().get_object(category, obj_id)
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'get_object',
                'category': category,
                'object_id': str(obj_id)
            })
            # Fallback to local state on error
            return await super().get_object(category, obj_id)
    
    async def get_objects(self, category: str, filter_func: Optional[callable] = None) -> List[Any]:
        """Get all objects in a category from Redis backend."""
        try:
            # Get keys pattern for category
            pattern = f"maos:{category}:*"
            keys = await self.redis_manager.data_structures.scan_keys(pattern)
            
            if not keys:
                # Fallback to local state
                return await super().get_objects(category, filter_func)
            
            # Bulk get from Redis
            redis_values = await self.redis_manager.bulk_get(keys)
            
            objects = []
            for key, value in redis_values.items():
                if value:
                    obj = self._deserialize_object_from_redis(category, value)
                    if obj and (not filter_func or filter_func(obj)):
                        objects.append(obj)
            
            return objects
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'get_objects',
                'category': category
            })
            # Fallback to local state
            return await super().get_objects(category, filter_func)
    
    async def remove_object(self, category: str, obj_id: UUID) -> bool:
        """Remove an object from Redis backend."""
        try:
            # Remove from Redis
            redis_key = StateKey(
                namespace="maos",
                category=category,
                identifier=str(obj_id)
            )
            
            redis_success = await self.redis_manager.delete_state(redis_key)
            
            # Also remove from local state
            local_success = await super().remove_object(category, obj_id)
            
            return redis_success or local_success
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'remove_object',
                'category': category,
                'object_id': str(obj_id)
            })
            # Try local state removal
            return await super().remove_object(category, obj_id)
    
    async def update_object(self, category: str, obj_id: UUID, updates: Dict[str, Any]) -> bool:
        """Update specific fields of an object in Redis backend."""
        try:
            # Get current object
            current_obj = await self.get_object(category, obj_id)
            if not current_obj:
                return False
            
            # Apply updates
            for field, value in updates.items():
                if hasattr(current_obj, field):
                    setattr(current_obj, field, value)
            
            # Store updated object
            await self.store_object(category, current_obj)
            
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'update_object',
                'category': category,
                'object_id': str(obj_id)
            })
            return False
    
    async def create_snapshot(self, name: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> StateSnapshot:
        """Create a snapshot using Redis backup functionality."""
        try:
            # Create Redis backup
            backup_id = await self.redis_manager.create_backup(
                name=name or f"snapshot_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                namespaces=["maos"]
            )
            
            # Create compatible StateSnapshot
            snapshot = StateSnapshot(
                state_data={},  # Data is stored in Redis backup
                metadata={
                    'redis_backup_id': str(backup_id),
                    **(metadata or {})
                }
            )
            
            snapshot.calculate_checksum()
            
            # Store snapshot reference
            self._snapshots[snapshot.id] = snapshot
            
            self.logger.logger.info(
                f"Created Redis-backed snapshot: {name}",
                extra={
                    'snapshot_id': str(snapshot.id),
                    'backup_id': str(backup_id)
                }
            )
            
            return snapshot
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'create_snapshot',
                'name': name
            })
            # Fallback to local snapshot
            return await super().create_snapshot(name, metadata)
    
    async def restore_from_snapshot(self, snapshot_id: UUID) -> bool:
        """Restore state from a Redis-backed snapshot."""
        try:
            if snapshot_id not in self._snapshots:
                return await super().restore_from_snapshot(snapshot_id)
            
            snapshot = self._snapshots[snapshot_id]
            backup_id = snapshot.metadata.get('redis_backup_id')
            
            if backup_id:
                # Restore from Redis backup
                success = await self.redis_manager.restore_backup(
                    UUID(backup_id),
                    target_namespaces=["maos"]
                )
                
                if success:
                    # Reload local state from Redis
                    await self._reload_local_state_from_redis()
                    return True
            
            # Fallback to local snapshot restore
            return await super().restore_from_snapshot(snapshot_id)
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'restore_from_snapshot',
                'snapshot_id': str(snapshot_id)
            })
            return False
    
    async def _reload_local_state_from_redis(self) -> None:
        """Reload local state from Redis after restore."""
        try:
            # Clear local state
            for category in self._state:
                self._state[category].clear()
            
            # Reload each category from Redis
            for category in ['tasks', 'agents', 'messages', 'checkpoints']:
                objects = await self.get_objects(category)
                if objects:
                    self._state[category] = {obj.id: obj for obj in objects if hasattr(obj, 'id')}
            
            self.logger.logger.info("Local state reloaded from Redis")
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'reload_local_state_from_redis'})
    
    # Enhanced functionality from Redis backend
    
    async def get_memory_usage_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory usage statistics."""
        return await self.redis_manager.get_memory_usage()
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get enhanced performance metrics."""
        redis_metrics = self.redis_manager.get_performance_metrics()
        local_metrics = self.get_metrics()
        
        return {
            'redis_metrics': redis_metrics,
            'local_metrics': local_metrics,
            'integration_metrics': {
                'active_watchers': len(self.redis_manager._watchers),
                'active_partitions': len(self.redis_manager.memory_pool._partitions) if self.redis_manager.memory_pool else 0
            }
        }
    
    async def create_backup(self, name: str, categories: Optional[List[str]] = None) -> UUID:
        """Create a backup of specific state categories."""
        namespaces = ["maos"] if not categories else [f"maos_{cat}" for cat in categories]
        return await self.redis_manager.create_backup(name, namespaces)
    
    async def restore_backup(self, backup_id: UUID) -> bool:
        """Restore state from backup."""
        success = await self.redis_manager.restore_backup(backup_id)
        if success:
            await self._reload_local_state_from_redis()
        return success
    
    async def optimize_memory_usage(self) -> Dict[str, Any]:
        """Optimize memory usage across the system."""
        results = {}
        
        try:
            # Cleanup expired allocations
            if self.redis_manager.memory_pool:
                cleaned_allocations = await self.redis_manager.memory_pool.cleanup_expired_allocations()
                results['cleaned_allocations'] = cleaned_allocations
            
            # Cleanup expired locks
            if self.redis_manager.lock_manager:
                cleaned_locks = await self.redis_manager.lock_manager.cleanup_expired_locks()
                results['cleaned_locks'] = cleaned_locks
            
            # Create checkpoint for current state
            checkpoint = await self.create_checkpoint(
                CheckpointType.SYSTEM_STATE,
                "optimization_checkpoint"
            )
            results['checkpoint_created'] = str(checkpoint.id)
            
            return results
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'optimize_memory_usage'})
            return {'error': str(e)}
    
    async def get_cluster_health(self) -> Dict[str, Any]:
        """Get comprehensive cluster health information."""
        try:
            redis_status = await self.redis_manager.get_cluster_status()
            local_summary = self.get_state_summary()
            
            return {
                'redis_cluster': redis_status,
                'local_state': local_summary,
                'integration_status': 'healthy',
                'last_sync': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'get_cluster_health'})
            return {
                'integration_status': 'error',
                'error': str(e),
                'last_sync': datetime.utcnow().isoformat()
            }
    
    async def shutdown(self) -> None:
        """Shutdown the integrated state manager."""
        try:
            self.logger.logger.info("Shutting down Redis State Manager Integration")
            
            # Shutdown Redis manager first
            await self.redis_manager.shutdown()
            
            # Shutdown parent state manager
            await super().shutdown()
            
            self.logger.logger.info("Redis State Manager Integration shutdown completed")
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'shutdown'})


# Factory function for easy integration
async def create_integrated_state_manager(**kwargs) -> RedisStateManagerIntegration:
    """
    Factory function to create and initialize an integrated state manager.
    
    Args:
        **kwargs: Configuration parameters for RedisStateManagerIntegration
        
    Returns:
        Initialized RedisStateManagerIntegration instance
    """
    manager = RedisStateManagerIntegration(**kwargs)
    await manager.start()
    return manager