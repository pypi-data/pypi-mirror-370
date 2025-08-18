"""
Context Manager for MAOS Claude Code integration.

This component handles:
- Context preservation across agent sessions
- Automatic checkpointing at key intervals
- Context restoration and recovery
- Cross-agent context sharing
- Long-running session management
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ..interfaces.claude_commands import ClaudeCommandInterface, CommandResult
from ..core.claude_cli_manager import ClaudeCodeCLIManager
from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError


class ContextType(Enum):
    """Types of context preservation."""
    AGENT_SESSION = "agent_session"
    TASK_CONTEXT = "task_context"
    WORKFLOW_STATE = "workflow_state"
    COORDINATION_CONTEXT = "coordination_context"
    MEMORY_SNAPSHOT = "memory_snapshot"


class ContextStrategy(Enum):
    """Strategies for context management."""
    MANUAL = "manual"           # Manual save/load commands
    AUTOMATIC = "automatic"     # Auto-save at intervals
    MILESTONE = "milestone"     # Save at task milestones
    HYBRID = "hybrid"          # Combination of strategies


@dataclass
class ContextCheckpoint:
    """Represents a context checkpoint."""
    id: UUID = field(default_factory=uuid4)
    agent_id: UUID = field(default_factory=uuid4)
    process_id: str = ""
    context_type: ContextType = ContextType.AGENT_SESSION
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    context_data: Dict[str, Any] = field(default_factory=dict)
    saved_successfully: bool = False
    restoration_tested: bool = False


class ContextManager:
    """
    Manages context preservation and checkpointing for Claude agents.
    
    This component ensures that agent contexts can be preserved across
    sessions, allowing for long-running work that spans multiple days.
    """
    
    def __init__(
        self,
        claude_command_interface: ClaudeCommandInterface,
        claude_cli_manager: ClaudeCodeCLIManager,
        checkpoint_dir: str = "./maos_checkpoints",
        auto_save_interval: int = 300,  # 5 minutes
        max_checkpoints_per_agent: int = 10,
        context_strategy: ContextStrategy = ContextStrategy.HYBRID
    ):
        """Initialize the Context Manager."""
        self.claude_command_interface = claude_command_interface
        self.claude_cli_manager = claude_cli_manager
        self.checkpoint_dir = Path(checkpoint_dir)
        self.auto_save_interval = auto_save_interval
        self.max_checkpoints_per_agent = max_checkpoints_per_agent
        self.context_strategy = context_strategy
        
        # Create checkpoint directory
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Internal state
        self._checkpoints: Dict[UUID, ContextCheckpoint] = {}
        self._agent_contexts: Dict[UUID, Dict[str, Any]] = {}
        self._auto_save_tasks: Dict[str, asyncio.Task] = {}  # process_id -> task
        self._last_checkpoint: Dict[str, datetime] = {}  # process_id -> timestamp
        
        # Shared context between agents
        self._shared_context: Dict[str, Any] = {}
        self._context_sharing_rules: Dict[str, Set[str]] = {}  # context_key -> allowed_agents
        
        # Logging
        self.logger = MAOSLogger("context_manager", str(uuid4()))
        
        # Performance metrics
        self._metrics = {
            'checkpoints_created': 0,
            'checkpoints_restored': 0,
            'auto_saves_performed': 0,
            'context_sharing_events': 0,
            'restoration_failures': 0,
            'total_context_size_mb': 0.0
        }
    
    async def start(self) -> None:
        """Start the context manager."""
        self.logger.logger.info("Starting Context Manager")
        
        # Load existing checkpoints
        await self._load_existing_checkpoints()
        
        self.logger.logger.info(
            f"Context Manager started with {len(self._checkpoints)} existing checkpoints"
        )
    
    async def stop(self) -> None:
        """Stop the context manager and cleanup."""
        self.logger.logger.info("Stopping Context Manager")
        
        # Cancel all auto-save tasks
        for task in self._auto_save_tasks.values():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._auto_save_tasks.clear()
        
        self.logger.logger.info("Context Manager stopped")
    
    async def create_checkpoint(
        self,
        agent_id: UUID,
        process_id: str,
        context_type: ContextType = ContextType.AGENT_SESSION,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContextCheckpoint:
        """
        Create a context checkpoint for an agent.
        
        Args:
            agent_id: UUID of the agent
            process_id: Process ID of the Claude instance
            context_type: Type of context being saved
            name: Optional name for the checkpoint
            description: Optional description
            metadata: Additional metadata
            
        Returns:
            Created checkpoint
        """
        try:
            # Generate checkpoint name if not provided
            if not name:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                name = f"{context_type.value}_{timestamp}"
            
            # Create checkpoint object
            checkpoint = ContextCheckpoint(
                agent_id=agent_id,
                process_id=process_id,
                context_type=context_type,
                name=name,
                description=description,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            
            # Export conversation state (Claude Code doesn't have explicit save command)
            save_result = await self.claude_command_interface.export_conversation(
                process_id=process_id,
                export_name=name
            )
            
            if save_result.success:
                checkpoint.saved_successfully = True
                checkpoint.context_data = save_result.structured_data or {}
                checkpoint.size_bytes = len(save_result.response.encode('utf-8'))
                
                # Store checkpoint
                self._checkpoints[checkpoint.id] = checkpoint
                
                # Update agent context tracking
                if agent_id not in self._agent_contexts:
                    self._agent_contexts[agent_id] = {}
                
                self._agent_contexts[agent_id][str(checkpoint.id)] = {
                    'checkpoint_id': checkpoint.id,
                    'name': name,
                    'created_at': checkpoint.created_at,
                    'context_type': context_type.value
                }
                
                # Save checkpoint to disk
                await self._save_checkpoint_to_disk(checkpoint)
                
                # Cleanup old checkpoints if needed
                await self._cleanup_old_checkpoints(agent_id)
                
                self._metrics['checkpoints_created'] += 1
                self._metrics['total_context_size_mb'] += checkpoint.size_bytes / 1024 / 1024
                
                self.logger.logger.info(
                    f"Context checkpoint created: {name}",
                    extra={
                        'checkpoint_id': str(checkpoint.id),
                        'agent_id': str(agent_id),
                        'process_id': process_id,
                        'context_type': context_type.value,
                        'size_bytes': checkpoint.size_bytes
                    }
                )
                
            else:
                checkpoint.saved_successfully = False
                self.logger.logger.error(
                    f"Failed to save context checkpoint: {save_result.error or 'Unknown error'}",
                    extra={
                        'agent_id': str(agent_id),
                        'process_id': process_id,
                        'checkpoint_name': name
                    }
                )
            
            return checkpoint
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'create_checkpoint',
                'agent_id': str(agent_id),
                'process_id': process_id,
                'context_type': context_type.value
            })
            
            # Create a failed checkpoint for tracking
            checkpoint = ContextCheckpoint(
                agent_id=agent_id,
                process_id=process_id,
                context_type=context_type,
                name=name or f"failed_{int(time.time())}",
                saved_successfully=False,
                metadata={'error': str(e)}
            )
            return checkpoint
    
    async def restore_checkpoint(
        self,
        checkpoint_id: UUID,
        target_process_id: Optional[str] = None
    ) -> bool:
        """
        Restore a context checkpoint to a Claude agent.
        
        Args:
            checkpoint_id: ID of the checkpoint to restore
            target_process_id: Target process ID (if different from original)
            
        Returns:
            True if restoration was successful
        """
        if checkpoint_id not in self._checkpoints:
            self.logger.logger.error(f"Checkpoint not found: {checkpoint_id}")
            return False
        
        checkpoint = self._checkpoints[checkpoint_id]
        process_id = target_process_id or checkpoint.process_id
        
        try:
            # Restore conversation context (Claude Code doesn't have explicit load command)
            # We restore by providing the previous conversation state
            load_result = await self.claude_command_interface.restore_conversation(
                process_id=process_id,
                conversation_state=checkpoint.context_data
            )
            
            if load_result.success:
                checkpoint.restoration_tested = True
                
                self._metrics['checkpoints_restored'] += 1
                
                self.logger.logger.info(
                    f"Context checkpoint restored: {checkpoint.name}",
                    extra={
                        'checkpoint_id': str(checkpoint_id),
                        'agent_id': str(checkpoint.agent_id),
                        'process_id': process_id,
                        'original_process_id': checkpoint.process_id
                    }
                )
                
                return True
            else:
                self._metrics['restoration_failures'] += 1
                
                self.logger.logger.error(
                    f"Failed to restore checkpoint: {load_result.error or 'Unknown error'}",
                    extra={
                        'checkpoint_id': str(checkpoint_id),
                        'checkpoint_name': checkpoint.name,
                        'process_id': process_id
                    }
                )
                
                return False
                
        except Exception as e:
            self._metrics['restoration_failures'] += 1
            
            self.logger.log_error(e, {
                'operation': 'restore_checkpoint',
                'checkpoint_id': str(checkpoint_id),
                'process_id': process_id
            })
            
            return False
    
    async def enable_auto_save(
        self,
        agent_id: UUID,
        process_id: str,
        interval_seconds: Optional[int] = None
    ) -> None:
        """
        Enable automatic context saving for an agent.
        
        Args:
            agent_id: UUID of the agent
            process_id: Process ID of the Claude instance
            interval_seconds: Save interval (uses default if None)
        """
        if process_id in self._auto_save_tasks:
            # Cancel existing auto-save task
            self._auto_save_tasks[process_id].cancel()
        
        interval = interval_seconds or self.auto_save_interval
        
        async def auto_save_loop():
            while True:
                try:
                    await asyncio.sleep(interval)
                    
                    # Create automatic checkpoint
                    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                    await self.create_checkpoint(
                        agent_id=agent_id,
                        process_id=process_id,
                        context_type=ContextType.AGENT_SESSION,
                        name=f"auto_save_{timestamp}",
                        description="Automatic context save",
                        metadata={'auto_save': True, 'interval_seconds': interval}
                    )
                    
                    self._metrics['auto_saves_performed'] += 1
                    self._last_checkpoint[process_id] = datetime.utcnow()
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.log_error(e, {
                        'operation': 'auto_save_loop',
                        'agent_id': str(agent_id),
                        'process_id': process_id
                    })
        
        # Start auto-save task
        task = asyncio.create_task(auto_save_loop())
        self._auto_save_tasks[process_id] = task
        
        self.logger.logger.info(
            f"Auto-save enabled for agent",
            extra={
                'agent_id': str(agent_id),
                'process_id': process_id,
                'interval_seconds': interval
            }
        )
    
    async def disable_auto_save(self, process_id: str) -> None:
        """Disable automatic context saving for a process."""
        if process_id in self._auto_save_tasks:
            self._auto_save_tasks[process_id].cancel()
            del self._auto_save_tasks[process_id]
            
            self.logger.logger.info(
                f"Auto-save disabled for process: {process_id}"
            )
    
    async def share_context(
        self,
        source_agent_id: UUID,
        target_agent_ids: List[UUID],
        context_key: str,
        context_data: Dict[str, Any],
        access_rules: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Share context between agents.
        
        Args:
            source_agent_id: Agent sharing the context
            target_agent_ids: Agents receiving the context
            context_key: Key for the shared context
            context_data: Context data to share
            access_rules: Optional access control rules
            
        Returns:
            True if sharing was successful
        """
        try:
            # Store shared context
            shared_key = f"{source_agent_id}:{context_key}"
            self._shared_context[shared_key] = {
                'source_agent_id': str(source_agent_id),
                'context_data': context_data,
                'created_at': datetime.utcnow().isoformat(),
                'access_rules': access_rules or {},
                'access_count': 0
            }
            
            # Set up sharing rules
            allowed_agents = {str(agent_id) for agent_id in target_agent_ids}
            allowed_agents.add(str(source_agent_id))  # Source can always access
            self._context_sharing_rules[shared_key] = allowed_agents
            
            self._metrics['context_sharing_events'] += 1
            
            self.logger.logger.info(
                f"Context shared: {context_key}",
                extra={
                    'source_agent_id': str(source_agent_id),
                    'target_agent_count': len(target_agent_ids),
                    'context_key': context_key,
                    'shared_key': shared_key
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'share_context',
                'source_agent_id': str(source_agent_id),
                'context_key': context_key
            })
            return False
    
    async def get_shared_context(
        self,
        requesting_agent_id: UUID,
        context_key: str,
        source_agent_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve shared context for an agent.
        
        Args:
            requesting_agent_id: Agent requesting the context
            context_key: Key for the shared context
            source_agent_id: Optional source agent filter
            
        Returns:
            Shared context data if accessible
        """
        try:
            # Find matching shared context
            search_keys = []
            if source_agent_id:
                search_keys.append(f"{source_agent_id}:{context_key}")
            else:
                # Search all shared contexts with this key
                search_keys = [
                    key for key in self._shared_context.keys()
                    if key.endswith(f":{context_key}")
                ]
            
            for shared_key in search_keys:
                if shared_key not in self._shared_context:
                    continue
                
                # Check access permissions
                if shared_key in self._context_sharing_rules:
                    allowed_agents = self._context_sharing_rules[shared_key]
                    if str(requesting_agent_id) not in allowed_agents:
                        continue
                
                # Return context data
                context_entry = self._shared_context[shared_key]
                context_entry['access_count'] += 1
                
                self.logger.logger.info(
                    f"Shared context accessed: {context_key}",
                    extra={
                        'requesting_agent_id': str(requesting_agent_id),
                        'shared_key': shared_key,
                        'access_count': context_entry['access_count']
                    }
                )
                
                return context_entry['context_data']
            
            return None
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'get_shared_context',
                'requesting_agent_id': str(requesting_agent_id),
                'context_key': context_key
            })
            return None
    
    def get_agent_checkpoints(self, agent_id: UUID) -> List[ContextCheckpoint]:
        """Get all checkpoints for an agent."""
        return [
            checkpoint for checkpoint in self._checkpoints.values()
            if checkpoint.agent_id == agent_id
        ]
    
    def get_checkpoint(self, checkpoint_id: UUID) -> Optional[ContextCheckpoint]:
        """Get a specific checkpoint by ID."""
        return self._checkpoints.get(checkpoint_id)
    
    def list_all_checkpoints(self) -> List[ContextCheckpoint]:
        """List all checkpoints."""
        return list(self._checkpoints.values())
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get context manager metrics."""
        metrics = self._metrics.copy()
        metrics.update({
            'total_checkpoints': len(self._checkpoints),
            'agents_with_checkpoints': len(self._agent_contexts),
            'active_auto_save_tasks': len(self._auto_save_tasks),
            'shared_contexts': len(self._shared_context)
        })
        return metrics
    
    async def _load_existing_checkpoints(self) -> None:
        """Load existing checkpoints from disk."""
        try:
            checkpoints_loaded = 0
            
            for checkpoint_file in self.checkpoint_dir.glob("*.json"):
                try:
                    with open(checkpoint_file, 'r') as f:
                        checkpoint_data = json.load(f)
                    
                    # Reconstruct checkpoint object
                    checkpoint = ContextCheckpoint(
                        id=UUID(checkpoint_data['id']),
                        agent_id=UUID(checkpoint_data['agent_id']),
                        process_id=checkpoint_data['process_id'],
                        context_type=ContextType(checkpoint_data['context_type']),
                        name=checkpoint_data['name'],
                        description=checkpoint_data.get('description'),
                        created_at=datetime.fromisoformat(checkpoint_data['created_at']),
                        size_bytes=checkpoint_data.get('size_bytes', 0),
                        metadata=checkpoint_data.get('metadata', {}),
                        context_data=checkpoint_data.get('context_data', {}),
                        saved_successfully=checkpoint_data.get('saved_successfully', False),
                        restoration_tested=checkpoint_data.get('restoration_tested', False)
                    )
                    
                    self._checkpoints[checkpoint.id] = checkpoint
                    checkpoints_loaded += 1
                    
                except Exception as e:
                    self.logger.logger.warning(
                        f"Failed to load checkpoint file: {checkpoint_file}",
                        extra={'error': str(e)}
                    )
            
            self.logger.logger.info(
                f"Loaded {checkpoints_loaded} existing checkpoints from disk"
            )
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'load_existing_checkpoints'})
    
    async def _save_checkpoint_to_disk(self, checkpoint: ContextCheckpoint) -> None:
        """Save a checkpoint to disk."""
        try:
            checkpoint_file = self.checkpoint_dir / f"{checkpoint.id}.json"
            
            checkpoint_data = {
                'id': str(checkpoint.id),
                'agent_id': str(checkpoint.agent_id),
                'process_id': checkpoint.process_id,
                'context_type': checkpoint.context_type.value,
                'name': checkpoint.name,
                'description': checkpoint.description,
                'created_at': checkpoint.created_at.isoformat(),
                'size_bytes': checkpoint.size_bytes,
                'metadata': checkpoint.metadata,
                'context_data': checkpoint.context_data,
                'saved_successfully': checkpoint.saved_successfully,
                'restoration_tested': checkpoint.restoration_tested
            }
            
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'save_checkpoint_to_disk',
                'checkpoint_id': str(checkpoint.id)
            })
    
    async def _cleanup_old_checkpoints(self, agent_id: UUID) -> None:
        """Clean up old checkpoints for an agent."""
        agent_checkpoints = self.get_agent_checkpoints(agent_id)
        
        if len(agent_checkpoints) <= self.max_checkpoints_per_agent:
            return
        
        # Sort by creation time and remove oldest
        sorted_checkpoints = sorted(agent_checkpoints, key=lambda c: c.created_at)
        checkpoints_to_remove = sorted_checkpoints[:-self.max_checkpoints_per_agent]
        
        for checkpoint in checkpoints_to_remove:
            # Remove from memory
            if checkpoint.id in self._checkpoints:
                del self._checkpoints[checkpoint.id]
            
            # Remove from disk
            checkpoint_file = self.checkpoint_dir / f"{checkpoint.id}.json"
            try:
                checkpoint_file.unlink(missing_ok=True)
            except Exception as e:
                self.logger.logger.warning(
                    f"Failed to delete checkpoint file: {checkpoint_file}",
                    extra={'error': str(e)}
                )
        
        self.logger.logger.info(
            f"Cleaned up {len(checkpoints_to_remove)} old checkpoints for agent {agent_id}"
        )