"""
State management interface and implementation for MAOS orchestration system.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Type, TypeVar
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json
import copy

from ..models.task import Task
from ..models.agent import Agent
from ..models.checkpoint import Checkpoint, CheckpointType
from ..models.message import Message
from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError
from .persistence import PersistenceInterface, InMemoryPersistence

T = TypeVar('T')


@dataclass
class StateSnapshot:
    """Represents a snapshot of the system state at a specific point in time."""
    
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    state_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: Optional[str] = None
    
    def calculate_checksum(self) -> str:
        """Calculate checksum for state integrity."""
        import hashlib
        data_str = json.dumps(self.state_data, sort_keys=True, default=str)
        self.checksum = hashlib.sha256(data_str.encode()).hexdigest()
        return self.checksum
    
    def validate_checksum(self) -> bool:
        """Validate state integrity using checksum."""
        if not self.checksum:
            return True
        
        import hashlib
        data_str = json.dumps(self.state_data, sort_keys=True, default=str)
        calculated_checksum = hashlib.sha256(data_str.encode()).hexdigest()
        return calculated_checksum == self.checksum


class StateManager:
    """
    Centralized state management for the MAOS orchestration system.
    
    Provides:
    - Centralized state storage and retrieval
    - State snapshots and rollback functionality
    - Event-driven state updates
    - Persistence integration
    - State validation and consistency checks
    """
    
    def __init__(
        self,
        persistence_backend: Optional[PersistenceInterface] = None,
        auto_checkpoint_interval: int = 300,  # 5 minutes
        max_snapshots: int = 50,
        enable_state_validation: bool = True
    ):
        """Initialize the State Manager."""
        self.persistence_backend = persistence_backend or InMemoryPersistence()
        self.auto_checkpoint_interval = auto_checkpoint_interval
        self.max_snapshots = max_snapshots
        self.enable_state_validation = enable_state_validation
        
        self.logger = MAOSLogger("state_manager", str(uuid4()))
        
        # Internal state storage
        self._state: Dict[str, Dict[UUID, Any]] = {
            'tasks': {},
            'agents': {},
            'resources': {},
            'messages': {},
            'checkpoints': {},
            'execution_plans': {},
            'resource_pools': {},
            'agent_pools': {}
        }
        
        # State snapshots
        self._snapshots: Dict[UUID, StateSnapshot] = {}
        
        # State change tracking
        self._change_listeners: Dict[str, List[callable]] = {}
        self._state_locks: Dict[str, asyncio.Lock] = {}
        
        # Background tasks
        self._checkpoint_task: Optional[asyncio.Task] = None
        
        # Metrics
        self._metrics = {
            'state_updates': 0,
            'snapshots_created': 0,
            'checkpoints_created': 0,
            'rollbacks_performed': 0,
            'validation_failures': 0
        }
        
        # Initialize locks for each state category
        for category in self._state.keys():
            self._state_locks[category] = asyncio.Lock()
    
    async def start(self) -> None:
        """Start the state manager and background tasks."""
        self.logger.logger.info("Starting State Manager")
        
        # Load existing state from persistence
        await self._load_state_from_persistence()
        
        # Start auto-checkpoint task
        if self.auto_checkpoint_interval > 0:
            self._checkpoint_task = asyncio.create_task(self._auto_checkpoint_loop())
    
    async def _load_state_from_persistence(self) -> None:
        """Load state from persistence backend."""
        try:
            # Load each state category
            for category in self._state.keys():
                data = await self.persistence_backend.load(f"state_{category}")
                if data:
                    self._state[category] = data
                    self.logger.logger.debug(f"Loaded {len(data)} {category} from persistence")
            
            # Load snapshots
            snapshots_data = await self.persistence_backend.load("snapshots")
            if snapshots_data:
                for snapshot_id, snapshot_data in snapshots_data.items():
                    snapshot = StateSnapshot(**snapshot_data)
                    self._snapshots[UUID(snapshot_id)] = snapshot
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'load_state_from_persistence'})
    
    async def _save_state_to_persistence(self) -> None:
        """Save current state to persistence backend."""
        try:
            # Save each state category
            for category, data in self._state.items():
                # Convert to serializable format
                serializable_data = {}
                for obj_id, obj in data.items():
                    if hasattr(obj, 'to_dict'):
                        serializable_data[str(obj_id)] = obj.to_dict()
                    else:
                        serializable_data[str(obj_id)] = obj
                
                await self.persistence_backend.save(f"state_{category}", serializable_data)
            
            # Save snapshots
            snapshots_data = {}
            for snapshot_id, snapshot in self._snapshots.items():
                snapshots_data[str(snapshot_id)] = {
                    'id': str(snapshot.id),
                    'created_at': snapshot.created_at.isoformat(),
                    'state_data': snapshot.state_data,
                    'metadata': snapshot.metadata,
                    'checksum': snapshot.checksum
                }
            
            await self.persistence_backend.save("snapshots", snapshots_data)
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'save_state_to_persistence'})
    
    async def store_object(self, category: str, obj: Any) -> None:
        """
        Store an object in the state manager.
        
        Args:
            category: State category (e.g., 'tasks', 'agents', 'resources')
            obj: Object to store (must have an 'id' attribute)
        """
        
        if not hasattr(obj, 'id'):
            raise MAOSError("Object must have an 'id' attribute")
        
        async with self._state_locks.get(category, asyncio.Lock()):
            if category not in self._state:
                self._state[category] = {}
            
            old_obj = self._state[category].get(obj.id)
            self._state[category][obj.id] = obj
            
            # Trigger change listeners
            await self._notify_change_listeners(category, 'updated', obj, old_obj)
            
            self._metrics['state_updates'] += 1
            
            self.logger.logger.debug(
                f"Object stored in {category}",
                extra={
                    'object_id': str(obj.id),
                    'object_type': type(obj).__name__
                }
            )
    
    async def get_object(self, category: str, obj_id: UUID) -> Optional[Any]:
        """
        Retrieve an object from the state manager.
        
        Args:
            category: State category
            obj_id: Object ID
            
        Returns:
            The stored object or None if not found
        """
        
        async with self._state_locks.get(category, asyncio.Lock()):
            return self._state.get(category, {}).get(obj_id)
    
    async def get_objects(self, category: str, filter_func: Optional[callable] = None) -> List[Any]:
        """
        Get all objects in a category, optionally filtered.
        
        Args:
            category: State category
            filter_func: Optional filter function
            
        Returns:
            List of objects
        """
        
        async with self._state_locks.get(category, asyncio.Lock()):
            objects = list(self._state.get(category, {}).values())
            
            if filter_func:
                objects = [obj for obj in objects if filter_func(obj)]
            
            return objects
    
    async def remove_object(self, category: str, obj_id: UUID) -> bool:
        """
        Remove an object from the state manager.
        
        Args:
            category: State category
            obj_id: Object ID
            
        Returns:
            True if object was removed, False if not found
        """
        
        async with self._state_locks.get(category, asyncio.Lock()):
            if category in self._state and obj_id in self._state[category]:
                old_obj = self._state[category][obj_id]
                del self._state[category][obj_id]
                
                # Trigger change listeners
                await self._notify_change_listeners(category, 'removed', None, old_obj)
                
                self.logger.logger.debug(
                    f"Object removed from {category}",
                    extra={'object_id': str(obj_id)}
                )
                
                return True
            
            return False
    
    async def update_object(self, category: str, obj_id: UUID, updates: Dict[str, Any]) -> bool:
        """
        Update specific fields of an object.
        
        Args:
            category: State category
            obj_id: Object ID
            updates: Dictionary of field updates
            
        Returns:
            True if object was updated, False if not found
        """
        
        async with self._state_locks.get(category, asyncio.Lock()):
            if category in self._state and obj_id in self._state[category]:
                obj = self._state[category][obj_id]
                old_obj = copy.deepcopy(obj) if hasattr(obj, '__dict__') else obj
                
                # Apply updates
                for field, value in updates.items():
                    if hasattr(obj, field):
                        setattr(obj, field, value)
                
                # Trigger change listeners
                await self._notify_change_listeners(category, 'updated', obj, old_obj)
                
                self.logger.logger.debug(
                    f"Object updated in {category}",
                    extra={
                        'object_id': str(obj_id),
                        'updates': list(updates.keys())
                    }
                )
                
                return True
            
            return False
    
    async def create_snapshot(self, name: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> StateSnapshot:
        """
        Create a snapshot of the current state.
        
        Args:
            name: Optional snapshot name
            metadata: Optional metadata
            
        Returns:
            StateSnapshot: The created snapshot
        """
        
        try:
            # Create deep copy of current state
            state_copy = {}
            for category, objects in self._state.items():
                category_copy = {}
                for obj_id, obj in objects.items():
                    if hasattr(obj, 'to_dict'):
                        category_copy[str(obj_id)] = obj.to_dict()
                    else:
                        category_copy[str(obj_id)] = copy.deepcopy(obj)
                state_copy[category] = category_copy
            
            # Create snapshot
            snapshot = StateSnapshot(
                state_data=state_copy,
                metadata=metadata or {}
            )
            
            if name:
                snapshot.metadata['name'] = name
            
            # Calculate checksum
            snapshot.calculate_checksum()
            
            # Store snapshot
            self._snapshots[snapshot.id] = snapshot
            
            # Cleanup old snapshots if needed
            await self._cleanup_old_snapshots()
            
            self._metrics['snapshots_created'] += 1
            
            self.logger.logger.info(
                "State snapshot created",
                extra={
                    'snapshot_id': str(snapshot.id),
                    'name': name,
                    'state_size': len(state_copy)
                }
            )
            
            return snapshot
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'create_snapshot'})
            raise MAOSError(f"Failed to create snapshot: {str(e)}")
    
    async def restore_from_snapshot(self, snapshot_id: UUID) -> bool:
        """
        Restore state from a snapshot.
        
        Args:
            snapshot_id: ID of snapshot to restore from
            
        Returns:
            True if restoration was successful
        """
        
        if snapshot_id not in self._snapshots:
            raise MAOSError(f"Snapshot not found: {snapshot_id}")
        
        snapshot = self._snapshots[snapshot_id]
        
        try:
            # Validate snapshot integrity
            if not snapshot.validate_checksum():
                raise MAOSError("Snapshot integrity validation failed")
            
            # Clear current state
            for category in self._state.keys():
                async with self._state_locks[category]:
                    self._state[category].clear()
            
            # Restore state from snapshot
            for category, objects in snapshot.state_data.items():
                if category in self._state:
                    async with self._state_locks[category]:
                        for obj_id_str, obj_data in objects.items():
                            obj_id = UUID(obj_id_str)
                            
                            # Reconstruct object from data
                            # This is a simplified approach - in production, you'd need
                            # proper object reconstruction based on type
                            self._state[category][obj_id] = obj_data
            
            # Trigger restoration events
            for category in self._state.keys():
                await self._notify_change_listeners(category, 'restored', None, None)
            
            self._metrics['rollbacks_performed'] += 1
            
            self.logger.logger.info(
                "State restored from snapshot",
                extra={
                    'snapshot_id': str(snapshot_id),
                    'snapshot_created': snapshot.created_at.isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'restore_from_snapshot',
                'snapshot_id': str(snapshot_id)
            })
            raise MAOSError(f"Failed to restore from snapshot: {str(e)}")
    
    async def create_checkpoint(
        self,
        checkpoint_type: CheckpointType,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Checkpoint:
        """
        Create a system checkpoint.
        
        Args:
            checkpoint_type: Type of checkpoint
            name: Optional checkpoint name
            metadata: Optional metadata
            
        Returns:
            Checkpoint: The created checkpoint
        """
        
        try:
            # Create snapshot first
            snapshot = await self.create_snapshot(
                name=f"checkpoint_{name}" if name else None,
                metadata=metadata
            )
            
            # Create checkpoint
            checkpoint = Checkpoint(
                type=checkpoint_type,
                name=name or f"Checkpoint-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
                state_data=snapshot.state_data,
                metadata=metadata or {},
                checksum=snapshot.checksum
            )
            
            # Store checkpoint
            await self.store_object('checkpoints', checkpoint)
            
            self._metrics['checkpoints_created'] += 1
            
            self.logger.logger.info(
                "Checkpoint created",
                extra={
                    'checkpoint_id': str(checkpoint.id),
                    'type': checkpoint_type.value,
                    'name': name
                }
            )
            
            return checkpoint
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'create_checkpoint'})
            raise MAOSError(f"Failed to create checkpoint: {str(e)}")
    
    def add_change_listener(self, category: str, listener: callable) -> None:
        """
        Add a change listener for a specific state category.
        
        Args:
            category: State category to listen for
            listener: Callback function (category, action, new_obj, old_obj)
        """
        
        if category not in self._change_listeners:
            self._change_listeners[category] = []
        
        self._change_listeners[category].append(listener)
        
        self.logger.logger.debug(
            f"Change listener added for {category}",
            extra={'listener': str(listener)}
        )
    
    def remove_change_listener(self, category: str, listener: callable) -> None:
        """Remove a change listener."""
        
        if category in self._change_listeners:
            try:
                self._change_listeners[category].remove(listener)
            except ValueError:
                pass
    
    async def _notify_change_listeners(
        self,
        category: str,
        action: str,
        new_obj: Any,
        old_obj: Any
    ) -> None:
        """Notify change listeners of state changes."""
        
        if category in self._change_listeners:
            for listener in self._change_listeners[category]:
                try:
                    if asyncio.iscoroutinefunction(listener):
                        await listener(category, action, new_obj, old_obj)
                    else:
                        listener(category, action, new_obj, old_obj)
                except Exception as e:
                    self.logger.log_error(e, {
                        'operation': 'notify_change_listener',
                        'category': category,
                        'action': action
                    })
    
    async def _auto_checkpoint_loop(self) -> None:
        """Background task for automatic checkpointing."""
        
        while True:
            try:
                await asyncio.sleep(self.auto_checkpoint_interval)
                
                # Create automatic checkpoint
                await self.create_checkpoint(
                    CheckpointType.SYSTEM_STATE,
                    name="auto",
                    metadata={'auto_generated': True}
                )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'auto_checkpoint_loop'})
    
    async def _cleanup_old_snapshots(self) -> None:
        """Clean up old snapshots to maintain the maximum count."""
        
        if len(self._snapshots) <= self.max_snapshots:
            return
        
        # Sort snapshots by creation time
        sorted_snapshots = sorted(
            self._snapshots.items(),
            key=lambda x: x[1].created_at
        )
        
        # Remove oldest snapshots
        snapshots_to_remove = len(self._snapshots) - self.max_snapshots
        for i in range(snapshots_to_remove):
            snapshot_id, _ = sorted_snapshots[i]
            del self._snapshots[snapshot_id]
        
        self.logger.logger.debug(
            f"Cleaned up {snapshots_to_remove} old snapshots",
            extra={'remaining_snapshots': len(self._snapshots)}
        )
    
    async def validate_state(self) -> List[str]:
        """
        Validate the current state for consistency.
        
        Returns:
            List of validation issues found
        """
        
        if not self.enable_state_validation:
            return []
        
        issues = []
        
        try:
            # Validate task-agent relationships
            tasks = await self.get_objects('tasks')
            agents = await self.get_objects('agents')
            
            agent_ids = {agent.id for agent in agents}
            
            for task in tasks:
                if hasattr(task, 'agent_id') and task.agent_id:
                    if task.agent_id not in agent_ids:
                        issues.append(f"Task {task.id} references non-existent agent {task.agent_id}")
            
            # Validate task dependencies
            task_ids = {task.id for task in tasks}
            
            for task in tasks:
                if hasattr(task, 'dependencies'):
                    for dep in task.dependencies:
                        if dep.task_id not in task_ids:
                            issues.append(f"Task {task.id} depends on non-existent task {dep.task_id}")
            
            # Validate resource allocations
            resources = await self.get_objects('resources')
            
            for resource in resources:
                if hasattr(resource, 'allocations'):
                    total_allocated = sum(alloc.amount for alloc in resource.allocations if alloc.is_active())
                    if abs(total_allocated - resource.allocated_capacity) > 0.01:
                        issues.append(f"Resource {resource.id} allocation mismatch: {total_allocated} vs {resource.allocated_capacity}")
            
            if issues:
                self._metrics['validation_failures'] += 1
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'validate_state'})
            issues.append(f"State validation error: {str(e)}")
        
        return issues
    
    def get_snapshots(self) -> List[StateSnapshot]:
        """Get all snapshots sorted by creation time."""
        return sorted(self._snapshots.values(), key=lambda s: s.created_at, reverse=True)
    
    def get_snapshot(self, snapshot_id: UUID) -> Optional[StateSnapshot]:
        """Get a specific snapshot by ID."""
        return self._snapshots.get(snapshot_id)
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current state."""
        summary = {}
        
        for category, objects in self._state.items():
            summary[category] = {
                'count': len(objects),
                'ids': [str(obj_id) for obj_id in objects.keys()]
            }
        
        summary['snapshots'] = {
            'count': len(self._snapshots),
            'latest': max(s.created_at for s in self._snapshots.values()) if self._snapshots else None
        }
        
        return summary
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get state manager metrics."""
        metrics = self._metrics.copy()
        metrics.update({
            'total_objects': sum(len(objects) for objects in self._state.values()),
            'total_snapshots': len(self._snapshots),
            'state_categories': len(self._state),
            'change_listeners': sum(len(listeners) for listeners in self._change_listeners.values())
        })
        return metrics
    
    async def shutdown(self) -> None:
        """Shutdown the state manager and save state."""
        
        self.logger.logger.info("State manager shutting down")
        
        # Cancel background tasks
        if self._checkpoint_task:
            self._checkpoint_task.cancel()
            try:
                await self._checkpoint_task
            except asyncio.CancelledError:
                pass
        
        # Save current state
        await self._save_state_to_persistence()
        
        # Clear state
        self._state.clear()
        self._snapshots.clear()
        self._change_listeners.clear()