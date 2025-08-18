"""
Backup and Recovery Manager for Redis-based state management.

Provides state backup and recovery capabilities with compression and encryption.
"""

import asyncio
import gzip
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
import tempfile
import shutil
from cryptography.fernet import Fernet
from aioredis import Redis

from .types import StateKey, StateValue, BackupMetadata
from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError


class BackupRecoveryManager:
    """
    Manages state backup and recovery operations.
    
    Features:
    - Full and incremental backups
    - Compression and encryption
    - Point-in-time recovery
    - Backup verification
    - Storage management
    """
    
    def __init__(
        self,
        redis: Redis,
        backup_directory: str = "/tmp/maos_backups",
        compression_enabled: bool = True,
        encryption_key: Optional[str] = None,
        max_backup_age_days: int = 30,
        backup_retention_count: int = 100
    ):
        """Initialize backup recovery manager."""
        self.redis = redis
        self.backup_directory = backup_directory
        self.compression_enabled = compression_enabled
        self.encryption_key = encryption_key
        self.max_backup_age_days = max_backup_age_days
        self.backup_retention_count = backup_retention_count
        
        self.logger = MAOSLogger("backup_recovery_manager", str(uuid4()))
        
        # Encryption setup
        self._fernet = None
        if encryption_key:
            try:
                self._fernet = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
            except Exception as e:
                self.logger.log_error(e, {'operation': 'setup_encryption'})
                raise MAOSError(f"Invalid encryption key: {str(e)}")
        
        # Backup tracking
        self._backup_metadata: Dict[UUID, BackupMetadata] = {}
        
        # Performance metrics
        self.metrics = {
            'backups_created': 0,
            'backups_restored': 0,
            'backup_failures': 0,
            'restore_failures': 0,
            'avg_backup_time_ms': 0.0,
            'avg_restore_time_ms': 0.0,
            'total_backup_size_bytes': 0
        }
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Ensure backup directory exists
        self._ensure_backup_directory()
    
    def _ensure_backup_directory(self) -> None:
        """Ensure backup directory exists."""
        try:
            os.makedirs(self.backup_directory, exist_ok=True)
            
            # Test write permissions
            test_file = os.path.join(self.backup_directory, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            
        except Exception as e:
            raise MAOSError(f"Cannot access backup directory {self.backup_directory}: {str(e)}")
    
    async def create_backup(
        self,
        name: str,
        namespaces: Optional[List[str]] = None,
        incremental: bool = False,
        last_backup_id: Optional[UUID] = None
    ) -> UUID:
        """
        Create a backup of state data.
        
        Args:
            name: Backup name
            namespaces: Specific namespaces to backup (None for all)
            incremental: Whether to create incremental backup
            last_backup_id: Reference backup for incremental
            
        Returns:
            Backup ID
        """
        start_time = time.time()
        backup_id = uuid4()
        
        try:
            self.logger.logger.info(
                f"Starting backup creation: {name}",
                extra={
                    'backup_id': str(backup_id),
                    'namespaces': namespaces,
                    'incremental': incremental
                }
            )
            
            # Create backup metadata
            metadata = BackupMetadata(
                id=backup_id,
                name=name,
                namespaces=namespaces or [],
                compression_type="gzip" if self.compression_enabled else "none",
                encryption_enabled=self._fernet is not None
            )
            
            # Collect state data
            if incremental and last_backup_id:
                backup_data = await self._collect_incremental_data(namespaces, last_backup_id)
            else:
                backup_data = await self._collect_full_data(namespaces)
            
            # Update metadata with collection results
            metadata.key_count = len(backup_data)
            
            # Create backup file
            backup_file = await self._create_backup_file(backup_id, backup_data, metadata)
            
            # Calculate backup size and checksum
            backup_size = os.path.getsize(backup_file)
            metadata.size_bytes = backup_size
            metadata.storage_location = backup_file
            metadata.checksum = await self._calculate_file_checksum(backup_file)
            
            # Store metadata
            self._backup_metadata[backup_id] = metadata
            await self._save_backup_metadata(metadata)
            
            # Update metrics
            backup_time = (time.time() - start_time) * 1000
            self._update_backup_metrics(backup_time, backup_size, success=True)
            self.metrics['backups_created'] += 1
            
            self.logger.logger.info(
                f"Backup created successfully: {name}",
                extra={
                    'backup_id': str(backup_id),
                    'size_bytes': backup_size,
                    'key_count': metadata.key_count,
                    'backup_time_ms': backup_time
                }
            )
            
            return backup_id
            
        except Exception as e:
            backup_time = (time.time() - start_time) * 1000
            self._update_backup_metrics(backup_time, 0, success=False)
            self.metrics['backup_failures'] += 1
            
            self.logger.log_error(e, {
                'operation': 'create_backup',
                'backup_id': str(backup_id),
                'name': name
            })
            raise MAOSError(f"Failed to create backup: {str(e)}")
    
    async def restore_backup(
        self,
        backup_id: UUID,
        target_namespaces: Optional[List[str]] = None,
        overwrite: bool = False,
        dry_run: bool = False
    ) -> bool:
        """
        Restore state from a backup.
        
        Args:
            backup_id: Backup to restore
            target_namespaces: Specific namespaces to restore
            overwrite: Whether to overwrite existing keys
            dry_run: Perform validation without actual restore
            
        Returns:
            True if successful
        """
        start_time = time.time()
        
        try:
            # Get backup metadata
            if backup_id not in self._backup_metadata:
                await self._load_backup_metadata(backup_id)
            
            if backup_id not in self._backup_metadata:
                raise MAOSError(f"Backup {backup_id} not found")
            
            metadata = self._backup_metadata[backup_id]
            
            self.logger.logger.info(
                f"Starting backup restore: {metadata.name}",
                extra={
                    'backup_id': str(backup_id),
                    'target_namespaces': target_namespaces,
                    'overwrite': overwrite,
                    'dry_run': dry_run
                }
            )
            
            # Verify backup integrity
            if not await self._verify_backup_integrity(metadata):
                raise MAOSError("Backup integrity verification failed")
            
            # Load backup data
            backup_data = await self._load_backup_file(metadata)
            
            # Filter by target namespaces if specified
            if target_namespaces:
                filtered_data = {}
                for key_str, value_data in backup_data.items():
                    try:
                        key = StateKey.from_string(key_str)
                        if key.namespace in target_namespaces:
                            filtered_data[key_str] = value_data
                    except Exception:
                        continue
                backup_data = filtered_data
            
            if dry_run:
                self.logger.logger.info(
                    f"Dry run completed - would restore {len(backup_data)} keys"
                )
                return True
            
            # Perform restore
            restored_count = await self._restore_data(backup_data, overwrite)
            
            # Update metrics
            restore_time = (time.time() - start_time) * 1000
            self._update_restore_metrics(restore_time, success=True)
            self.metrics['backups_restored'] += 1
            
            self.logger.logger.info(
                f"Backup restored successfully: {metadata.name}",
                extra={
                    'backup_id': str(backup_id),
                    'restored_keys': restored_count,
                    'restore_time_ms': restore_time
                }
            )
            
            return True
            
        except Exception as e:
            restore_time = (time.time() - start_time) * 1000
            self._update_restore_metrics(restore_time, success=False)
            self.metrics['restore_failures'] += 1
            
            self.logger.log_error(e, {
                'operation': 'restore_backup',
                'backup_id': str(backup_id)
            })
            return False
    
    async def list_backups(
        self,
        namespace_filter: Optional[str] = None,
        limit: int = 100
    ) -> List[BackupMetadata]:
        """
        List available backups.
        
        Args:
            namespace_filter: Filter by namespace
            limit: Maximum number of backups to return
            
        Returns:
            List of backup metadata
        """
        try:
            # Load all backup metadata if not already loaded
            await self._load_all_backup_metadata()
            
            backups = list(self._backup_metadata.values())
            
            # Apply namespace filter
            if namespace_filter:
                backups = [
                    backup for backup in backups
                    if namespace_filter in backup.namespaces
                ]
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda b: b.created_at, reverse=True)
            
            return backups[:limit]
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'list_backups'})
            return []
    
    async def delete_backup(self, backup_id: UUID) -> bool:
        """
        Delete a backup.
        
        Args:
            backup_id: Backup to delete
            
        Returns:
            True if successful
        """
        try:
            if backup_id not in self._backup_metadata:
                await self._load_backup_metadata(backup_id)
            
            if backup_id not in self._backup_metadata:
                return False
            
            metadata = self._backup_metadata[backup_id]
            
            # Delete backup file
            if os.path.exists(metadata.storage_location):
                os.remove(metadata.storage_location)
            
            # Delete metadata file
            metadata_file = self._get_metadata_file_path(backup_id)
            if os.path.exists(metadata_file):
                os.remove(metadata_file)
            
            # Remove from memory
            del self._backup_metadata[backup_id]
            
            self.logger.logger.info(f"Deleted backup: {metadata.name}")
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'delete_backup',
                'backup_id': str(backup_id)
            })
            return False
    
    async def _collect_full_data(self, namespaces: Optional[List[str]]) -> Dict[str, Any]:
        """Collect all state data for backup."""
        backup_data = {}
        
        try:
            # Scan all keys
            async for key in self.redis.scan_iter(match="*", count=1000):
                key_str = key.decode() if isinstance(key, bytes) else key
                
                # Filter by namespace if specified
                if namespaces:
                    try:
                        state_key = StateKey.from_string(key_str)
                        if state_key.namespace not in namespaces:
                            continue
                    except Exception:
                        continue
                
                # Get value
                value = await self.redis.get(key)
                if value:
                    backup_data[key_str] = value.decode() if isinstance(value, bytes) else value
            
            return backup_data
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'collect_full_data'})
            raise
    
    async def _collect_incremental_data(
        self,
        namespaces: Optional[List[str]],
        last_backup_id: UUID
    ) -> Dict[str, Any]:
        """Collect incremental state data since last backup."""
        # For incremental backup, we would need to track modifications
        # This is a simplified implementation
        # In production, you'd track modifications with timestamps or version numbers
        
        # For now, fall back to full backup
        self.logger.logger.warning("Incremental backup not fully implemented, performing full backup")
        return await self._collect_full_data(namespaces)
    
    async def _create_backup_file(
        self,
        backup_id: UUID,
        backup_data: Dict[str, Any],
        metadata: BackupMetadata
    ) -> str:
        """Create backup file with compression and encryption."""
        backup_file = os.path.join(self.backup_directory, f"{backup_id}.backup")
        
        try:
            # Serialize data
            serialized_data = json.dumps(backup_data, default=str)
            data_bytes = serialized_data.encode('utf-8')
            
            # Compress if enabled
            if self.compression_enabled:
                data_bytes = gzip.compress(data_bytes)
            
            # Encrypt if enabled
            if self._fernet:
                data_bytes = self._fernet.encrypt(data_bytes)
            
            # Write to file
            with open(backup_file, 'wb') as f:
                f.write(data_bytes)
            
            return backup_file
            
        except Exception as e:
            if os.path.exists(backup_file):
                os.remove(backup_file)
            raise MAOSError(f"Failed to create backup file: {str(e)}")
    
    async def _load_backup_file(self, metadata: BackupMetadata) -> Dict[str, Any]:
        """Load and decompress backup file."""
        try:
            # Read file
            with open(metadata.storage_location, 'rb') as f:
                data_bytes = f.read()
            
            # Decrypt if enabled
            if metadata.encryption_enabled and self._fernet:
                data_bytes = self._fernet.decrypt(data_bytes)
            
            # Decompress if enabled
            if metadata.compression_type == "gzip":
                data_bytes = gzip.decompress(data_bytes)
            
            # Deserialize
            serialized_data = data_bytes.decode('utf-8')
            backup_data = json.loads(serialized_data)
            
            return backup_data
            
        except Exception as e:
            raise MAOSError(f"Failed to load backup file: {str(e)}")
    
    async def _restore_data(self, backup_data: Dict[str, Any], overwrite: bool) -> int:
        """Restore data to Redis."""
        restored_count = 0
        
        try:
            # Use pipeline for better performance
            pipeline = self.redis.pipeline()
            batch_size = 1000
            current_batch = 0
            
            for key_str, value_data in backup_data.items():
                # Check if key exists and overwrite policy
                if not overwrite:
                    exists = await self.redis.exists(key_str)
                    if exists:
                        continue
                
                # Add to pipeline
                pipeline.set(key_str, value_data)
                current_batch += 1
                
                # Execute batch when full
                if current_batch >= batch_size:
                    await pipeline.execute()
                    pipeline = self.redis.pipeline()
                    restored_count += current_batch
                    current_batch = 0
            
            # Execute remaining batch
            if current_batch > 0:
                await pipeline.execute()
                restored_count += current_batch
            
            return restored_count
            
        except Exception as e:
            raise MAOSError(f"Failed to restore data: {str(e)}")
    
    async def _verify_backup_integrity(self, metadata: BackupMetadata) -> bool:
        """Verify backup file integrity."""
        try:
            if not os.path.exists(metadata.storage_location):
                return False
            
            # Check file size
            actual_size = os.path.getsize(metadata.storage_location)
            if actual_size != metadata.size_bytes:
                return False
            
            # Verify checksum if available
            if metadata.checksum:
                actual_checksum = await self._calculate_file_checksum(metadata.storage_location)
                if actual_checksum != metadata.checksum:
                    return False
            
            # Try to load the backup to verify format
            try:
                await self._load_backup_file(metadata)
            except Exception:
                return False
            
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'verify_backup_integrity',
                'backup_id': str(metadata.id)
            })
            return False
    
    async def _calculate_file_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of file."""
        import hashlib
        
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def _get_metadata_file_path(self, backup_id: UUID) -> str:
        """Get path for backup metadata file."""
        return os.path.join(self.backup_directory, f"{backup_id}.metadata.json")
    
    async def _save_backup_metadata(self, metadata: BackupMetadata) -> None:
        """Save backup metadata to file."""
        metadata_file = self._get_metadata_file_path(metadata.id)
        
        try:
            with open(metadata_file, 'w') as f:
                json.dump(metadata.to_dict(), f, indent=2, default=str)
                
        except Exception as e:
            raise MAOSError(f"Failed to save backup metadata: {str(e)}")
    
    async def _load_backup_metadata(self, backup_id: UUID) -> None:
        """Load backup metadata from file."""
        metadata_file = self._get_metadata_file_path(backup_id)
        
        if not os.path.exists(metadata_file):
            return
        
        try:
            with open(metadata_file, 'r') as f:
                metadata_dict = json.load(f)
            
            metadata = BackupMetadata(
                id=UUID(metadata_dict['id']),
                name=metadata_dict['name'],
                created_at=datetime.fromisoformat(metadata_dict['created_at']),
                size_bytes=metadata_dict['size_bytes'],
                key_count=metadata_dict['key_count'],
                namespaces=metadata_dict['namespaces'],
                checksum=metadata_dict['checksum'],
                compression_type=metadata_dict['compression_type'],
                encryption_enabled=metadata_dict['encryption_enabled'],
                storage_location=metadata_dict['storage_location'],
                metadata=metadata_dict.get('metadata', {})
            )
            
            self._backup_metadata[backup_id] = metadata
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'load_backup_metadata',
                'backup_id': str(backup_id)
            })
    
    async def _load_all_backup_metadata(self) -> None:
        """Load all backup metadata files."""
        try:
            for filename in os.listdir(self.backup_directory):
                if filename.endswith('.metadata.json'):
                    backup_id_str = filename.replace('.metadata.json', '')
                    try:
                        backup_id = UUID(backup_id_str)
                        if backup_id not in self._backup_metadata:
                            await self._load_backup_metadata(backup_id)
                    except ValueError:
                        continue
                        
        except Exception as e:
            self.logger.log_error(e, {'operation': 'load_all_backup_metadata'})
    
    def _update_backup_metrics(self, backup_time_ms: float, size_bytes: int, success: bool) -> None:
        """Update backup metrics."""
        if success:
            # Update average backup time
            current_avg = self.metrics['avg_backup_time_ms']
            alpha = 0.1
            self.metrics['avg_backup_time_ms'] = alpha * backup_time_ms + (1 - alpha) * current_avg
            
            # Update total backup size
            self.metrics['total_backup_size_bytes'] += size_bytes
    
    def _update_restore_metrics(self, restore_time_ms: float, success: bool) -> None:
        """Update restore metrics."""
        if success:
            # Update average restore time
            current_avg = self.metrics['avg_restore_time_ms']
            alpha = 0.1
            self.metrics['avg_restore_time_ms'] = alpha * restore_time_ms + (1 - alpha) * current_avg
    
    async def cleanup_old_backups(self) -> int:
        """Clean up old backups based on retention policy."""
        try:
            await self._load_all_backup_metadata()
            
            cleanup_count = 0
            current_time = datetime.utcnow()
            
            # Sort backups by creation time
            sorted_backups = sorted(
                self._backup_metadata.values(),
                key=lambda b: b.created_at,
                reverse=True
            )
            
            # Remove backups beyond retention count
            backups_to_remove = sorted_backups[self.backup_retention_count:]
            
            # Remove old backups
            for backup in backups_to_remove:
                age_days = (current_time - backup.created_at).days
                if age_days > self.max_backup_age_days:
                    await self.delete_backup(backup.id)
                    cleanup_count += 1
            
            if cleanup_count > 0:
                self.logger.logger.info(f"Cleaned up {cleanup_count} old backups")
            
            return cleanup_count
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'cleanup_old_backups'})
            return 0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get backup and recovery metrics."""
        return {
            **self.metrics,
            'active_backups': len(self._backup_metadata),
            'backup_directory': self.backup_directory,
            'compression_enabled': self.compression_enabled,
            'encryption_enabled': self._fernet is not None
        }
    
    def get_backup_summary(self) -> Dict[str, Any]:
        """Get backup system summary."""
        total_size = sum(backup.size_bytes for backup in self._backup_metadata.values())
        
        return {
            'total_backups': len(self._backup_metadata),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'oldest_backup': min((b.created_at for b in self._backup_metadata.values()), default=None),
            'newest_backup': max((b.created_at for b in self._backup_metadata.values()), default=None),
            'metrics': self.get_metrics()
        }
    
    async def start_background_tasks(self) -> None:
        """Start background cleanup tasks."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup task."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self.cleanup_old_backups()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'cleanup_loop'})
    
    async def shutdown(self) -> None:
        """Shutdown backup recovery manager."""
        self.logger.logger.info("Shutting down Backup Recovery Manager")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Clear state
        self._backup_metadata.clear()
        
        self.logger.logger.info("Backup Recovery Manager shutdown completed")