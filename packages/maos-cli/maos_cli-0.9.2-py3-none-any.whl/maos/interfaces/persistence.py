"""
Persistence interfaces for MAOS orchestration system.
"""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
import aiofiles

from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError


class PersistenceInterface(ABC):
    """Abstract interface for persistence backends."""
    
    @abstractmethod
    async def save(self, key: str, data: Any) -> None:
        """Save data with the given key."""
        pass
    
    @abstractmethod
    async def load(self, key: str) -> Optional[Any]:
        """Load data for the given key."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete data for the given key."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if data exists for the given key."""
        pass
    
    @abstractmethod
    async def list_keys(self) -> list:
        """List all available keys."""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all stored data."""
        pass


class InMemoryPersistence(PersistenceInterface):
    """In-memory persistence backend for development and testing."""
    
    def __init__(self):
        self._storage: Dict[str, Any] = {}
        self.logger = MAOSLogger("in_memory_persistence")
    
    async def save(self, key: str, data: Any) -> None:
        """Save data in memory."""
        try:
            # Deep copy to avoid reference issues
            import copy
            self._storage[key] = copy.deepcopy(data)
            
            self.logger.logger.debug(
                f"Data saved to memory",
                extra={'key': key, 'size': len(str(data))}
            )
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'save',
                'key': key
            })
            raise MAOSError(f"Failed to save data to memory: {str(e)}")
    
    async def load(self, key: str) -> Optional[Any]:
        """Load data from memory."""
        try:
            data = self._storage.get(key)
            
            if data is not None:
                # Return deep copy to avoid reference issues
                import copy
                return copy.deepcopy(data)
            
            return None
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'load',
                'key': key
            })
            raise MAOSError(f"Failed to load data from memory: {str(e)}")
    
    async def delete(self, key: str) -> bool:
        """Delete data from memory."""
        try:
            if key in self._storage:
                del self._storage[key]
                self.logger.logger.debug(f"Data deleted from memory", extra={'key': key})
                return True
            return False
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'delete',
                'key': key
            })
            raise MAOSError(f"Failed to delete data from memory: {str(e)}")
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in memory."""
        return key in self._storage
    
    async def list_keys(self) -> list:
        """List all keys in memory."""
        return list(self._storage.keys())
    
    async def clear(self) -> None:
        """Clear all data from memory."""
        self._storage.clear()
        self.logger.logger.debug("Memory storage cleared")


class FilePersistence(PersistenceInterface):
    """File-based persistence backend."""
    
    def __init__(
        self,
        storage_directory: str = "./maos_storage",
        create_directory: bool = True,
        file_extension: str = ".json"
    ):
        self.storage_directory = Path(storage_directory)
        self.file_extension = file_extension
        self.logger = MAOSLogger("file_persistence")
        
        if create_directory:
            self.storage_directory.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, key: str) -> Path:
        """Get the file path for a given key."""
        # Sanitize key for filename
        safe_key = key.replace('/', '_').replace('\\', '_')
        return self.storage_directory / f"{safe_key}{self.file_extension}"
    
    async def save(self, key: str, data: Any) -> None:
        """Save data to file."""
        file_path = self._get_file_path(key)
        
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to JSON-serializable format
            json_data = json.dumps(data, indent=2, default=str)
            
            # Write to file asynchronously
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json_data)
            
            self.logger.logger.debug(
                f"Data saved to file",
                extra={
                    'key': key,
                    'file_path': str(file_path),
                    'size': len(json_data)
                }
            )
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'save',
                'key': key,
                'file_path': str(file_path)
            })
            raise MAOSError(f"Failed to save data to file: {str(e)}")
    
    async def load(self, key: str) -> Optional[Any]:
        """Load data from file."""
        file_path = self._get_file_path(key)
        
        if not file_path.exists():
            return None
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            data = json.loads(content)
            
            self.logger.logger.debug(
                f"Data loaded from file",
                extra={
                    'key': key,
                    'file_path': str(file_path),
                    'size': len(content)
                }
            )
            
            return data
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'load',
                'key': key,
                'file_path': str(file_path)
            })
            raise MAOSError(f"Failed to load data from file: {str(e)}")
    
    async def delete(self, key: str) -> bool:
        """Delete file for the given key."""
        file_path = self._get_file_path(key)
        
        try:
            if file_path.exists():
                file_path.unlink()
                self.logger.logger.debug(
                    f"File deleted",
                    extra={'key': key, 'file_path': str(file_path)}
                )
                return True
            return False
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'delete',
                'key': key,
                'file_path': str(file_path)
            })
            raise MAOSError(f"Failed to delete file: {str(e)}")
    
    async def exists(self, key: str) -> bool:
        """Check if file exists for the given key."""
        file_path = self._get_file_path(key)
        return file_path.exists()
    
    async def list_keys(self) -> list:
        """List all available keys (files)."""
        try:
            keys = []
            
            if self.storage_directory.exists():
                for file_path in self.storage_directory.iterdir():
                    if file_path.is_file() and file_path.suffix == self.file_extension:
                        # Remove extension and convert back to key
                        key = file_path.stem.replace('_', '/')
                        keys.append(key)
            
            return keys
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'list_keys'})
            raise MAOSError(f"Failed to list keys: {str(e)}")
    
    async def clear(self) -> None:
        """Clear all files in the storage directory."""
        try:
            if self.storage_directory.exists():
                for file_path in self.storage_directory.iterdir():
                    if file_path.is_file() and file_path.suffix == self.file_extension:
                        file_path.unlink()
                
                self.logger.logger.debug("All files cleared from storage directory")
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'clear'})
            raise MAOSError(f"Failed to clear storage: {str(e)}")


class DatabasePersistence(PersistenceInterface):
    """Database persistence backend (implementation placeholder)."""
    
    def __init__(
        self,
        connection_string: str,
        table_name: str = "maos_state"
    ):
        self.connection_string = connection_string
        self.table_name = table_name
        self.logger = MAOSLogger("database_persistence")
        
        # Connection pool would be initialized here
        self._connection_pool = None
    
    async def save(self, key: str, data: Any) -> None:
        """Save data to database."""
        # Implementation would use actual database connection
        raise NotImplementedError("Database persistence not yet implemented")
    
    async def load(self, key: str) -> Optional[Any]:
        """Load data from database."""
        # Implementation would use actual database connection
        raise NotImplementedError("Database persistence not yet implemented")
    
    async def delete(self, key: str) -> bool:
        """Delete data from database."""
        # Implementation would use actual database connection
        raise NotImplementedError("Database persistence not yet implemented")
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in database."""
        # Implementation would use actual database connection
        raise NotImplementedError("Database persistence not yet implemented")
    
    async def list_keys(self) -> list:
        """List all keys in database."""
        # Implementation would use actual database connection
        raise NotImplementedError("Database persistence not yet implemented")
    
    async def clear(self) -> None:
        """Clear all data from database."""
        # Implementation would use actual database connection
        raise NotImplementedError("Database persistence not yet implemented")


class CompositePersistence(PersistenceInterface):
    """
    Composite persistence backend that can use multiple backends.
    
    Useful for implementing cache layers, backup strategies, etc.
    """
    
    def __init__(
        self,
        primary_backend: PersistenceInterface,
        secondary_backends: Optional[list] = None
    ):
        self.primary_backend = primary_backend
        self.secondary_backends = secondary_backends or []
        self.logger = MAOSLogger("composite_persistence")
    
    async def save(self, key: str, data: Any) -> None:
        """Save data to all backends."""
        # Save to primary backend
        await self.primary_backend.save(key, data)
        
        # Save to secondary backends (best effort)
        for backend in self.secondary_backends:
            try:
                await backend.save(key, data)
            except Exception as e:
                self.logger.log_error(e, {
                    'operation': 'save_secondary',
                    'key': key,
                    'backend': type(backend).__name__
                })
    
    async def load(self, key: str) -> Optional[Any]:
        """Load data from primary backend, fallback to secondary if needed."""
        try:
            # Try primary backend first
            data = await self.primary_backend.load(key)
            if data is not None:
                return data
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'load_primary',
                'key': key
            })
        
        # Try secondary backends
        for backend in self.secondary_backends:
            try:
                data = await backend.load(key)
                if data is not None:
                    # Restore to primary backend for next time
                    try:
                        await self.primary_backend.save(key, data)
                    except:
                        pass  # Best effort
                    return data
            except Exception as e:
                self.logger.log_error(e, {
                    'operation': 'load_secondary',
                    'key': key,
                    'backend': type(backend).__name__
                })
        
        return None
    
    async def delete(self, key: str) -> bool:
        """Delete data from all backends."""
        success = False
        
        try:
            success = await self.primary_backend.delete(key)
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'delete_primary',
                'key': key
            })
        
        # Delete from secondary backends (best effort)
        for backend in self.secondary_backends:
            try:
                await backend.delete(key)
            except Exception as e:
                self.logger.log_error(e, {
                    'operation': 'delete_secondary',
                    'key': key,
                    'backend': type(backend).__name__
                })
        
        return success
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in any backend."""
        try:
            if await self.primary_backend.exists(key):
                return True
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'exists_primary',
                'key': key
            })
        
        # Check secondary backends
        for backend in self.secondary_backends:
            try:
                if await backend.exists(key):
                    return True
            except Exception as e:
                self.logger.log_error(e, {
                    'operation': 'exists_secondary',
                    'key': key,
                    'backend': type(backend).__name__
                })
        
        return False
    
    async def list_keys(self) -> list:
        """List keys from primary backend."""
        try:
            return await self.primary_backend.list_keys()
        except Exception as e:
            self.logger.log_error(e, {'operation': 'list_keys_primary'})
            
            # Try secondary backends
            for backend in self.secondary_backends:
                try:
                    return await backend.list_keys()
                except:
                    continue
            
            return []
    
    async def clear(self) -> None:
        """Clear all backends."""
        try:
            await self.primary_backend.clear()
        except Exception as e:
            self.logger.log_error(e, {'operation': 'clear_primary'})
        
        for backend in self.secondary_backends:
            try:
                await backend.clear()
            except Exception as e:
                self.logger.log_error(e, {
                    'operation': 'clear_secondary',
                    'backend': type(backend).__name__
                })