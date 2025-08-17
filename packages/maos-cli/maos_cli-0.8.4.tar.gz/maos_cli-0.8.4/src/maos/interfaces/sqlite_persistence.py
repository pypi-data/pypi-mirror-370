"""
SQLite persistence backend for MAOS orchestration system.

Provides a robust, single-file database for storing all orchestration data including
agents, sessions, tasks, messages, and checkpoints.
"""

import asyncio
import json
import aiosqlite
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from contextlib import asynccontextmanager

from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError
from .persistence import PersistenceInterface


class SqlitePersistence(PersistenceInterface):
    """SQLite-based persistence for MAOS with full relational support."""
    
    def __init__(self, db_path: str = "./maos.db"):
        """
        Initialize SQLite persistence.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.logger = MAOSLogger("sqlite_persistence")
        self._db = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize database and create tables."""
        if self._initialized:
            return
            
        try:
            # Create database connection
            self._db = await aiosqlite.connect(str(self.db_path))
            
            # Set row factory to return dictionaries
            self._db.row_factory = aiosqlite.Row
            
            # Enable foreign keys
            await self._db.execute("PRAGMA foreign_keys = ON")
            
            # Create tables
            await self._create_tables()
            
            await self._db.commit()
            self._initialized = True
            
            self.logger.logger.info(f"SQLite database initialized at {self.db_path}")
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "initialize"})
            raise MAOSError(f"Failed to initialize SQLite database: {str(e)}")
    
    async def _create_tables(self):
        """Create all required database tables."""
        
        # Agents table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                session_id TEXT,
                process_id TEXT,
                status TEXT DEFAULT 'inactive',
                capabilities TEXT,  -- JSON array
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP,
                metadata TEXT  -- JSON object
            )
        """)
        
        # Sessions table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                task TEXT,
                conversation_history TEXT,  -- JSON array
                turn_count INTEGER DEFAULT 0,
                total_cost REAL DEFAULT 0.0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
            )
        """)
        
        # Tasks table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                parent_task_id TEXT,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                assigned_agents TEXT,  -- JSON array of agent IDs
                subtasks TEXT,  -- JSON array
                progress REAL DEFAULT 0.0,
                result TEXT,  -- JSON object
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """)
        
        # Inter-agent messages table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_agent TEXT NOT NULL,
                to_agent TEXT,  -- NULL for broadcasts
                message TEXT NOT NULL,
                message_type TEXT DEFAULT 'info',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                acknowledged BOOLEAN DEFAULT 0,
                FOREIGN KEY (from_agent) REFERENCES agents(id) ON DELETE CASCADE,
                FOREIGN KEY (to_agent) REFERENCES agents(id) ON DELETE CASCADE
            )
        """)
        
        # Checkpoints table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                orchestrator_state TEXT,  -- JSON object
                agent_sessions TEXT,  -- JSON object mapping agent_id -> session_id
                task_states TEXT,  -- JSON object
                message_history TEXT,  -- JSON array
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Orchestrations table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS orchestrations (
                id TEXT PRIMARY KEY,
                request TEXT NOT NULL,
                status TEXT DEFAULT 'running',
                agents TEXT,  -- JSON array of agent IDs
                batches TEXT,  -- JSON array of batch structure
                total_cost REAL DEFAULT 0.0,
                total_duration_ms INTEGER DEFAULT 0,
                successful_agents INTEGER DEFAULT 0,
                total_agents INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                summary TEXT,
                metadata TEXT  -- JSON object
            )
        """)
        
        # Create indexes for performance
        await self._db.execute("CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status)")
        await self._db.execute("CREATE INDEX IF NOT EXISTS idx_sessions_agent ON sessions(agent_id)")
        await self._db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
        await self._db.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)")
        await self._db.execute("CREATE INDEX IF NOT EXISTS idx_checkpoints_name ON checkpoints(name)")
        await self._db.execute("CREATE INDEX IF NOT EXISTS idx_orchestrations_status ON orchestrations(status)")
    
    @asynccontextmanager
    async def transaction(self):
        """Context manager for database transactions."""
        if not self._initialized:
            await self.initialize()
        
        try:
            yield self._db
            await self._db.commit()
        except Exception as e:
            await self._db.rollback()
            raise e
    
    # Agent management
    
    async def create_agent(self, agent_id: str, name: str, agent_type: str, 
                          capabilities: List[str] = None, metadata: Dict = None) -> None:
        """Create a new agent record."""
        async with self.transaction() as db:
            await db.execute("""
                INSERT INTO agents (id, name, type, capabilities, metadata, last_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                agent_id, name, agent_type,
                json.dumps(capabilities or []),
                json.dumps(metadata or {}),
                datetime.now().isoformat()
            ))
    
    async def update_agent_session(self, agent_id: str, session_id: str, process_id: str = None) -> None:
        """Update agent's session information."""
        async with self.transaction() as db:
            await db.execute("""
                UPDATE agents 
                SET session_id = ?, process_id = ?, status = 'active', last_active = ?
                WHERE id = ?
            """, (session_id, process_id, datetime.now().isoformat(), agent_id))
    
    async def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent information."""
        if not self._initialized:
            await self.initialize()
            
        async with self._db.execute(
            "SELECT * FROM agents WHERE id = ?", (agent_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
        return None
    
    async def get_active_agents(self) -> List[Dict]:
        """Get all active agents."""
        if not self._initialized:
            await self.initialize()
        
        try:
            async with self._db.execute(
                "SELECT * FROM agents WHERE status = 'active'"
            ) as cursor:
                rows = await cursor.fetchall()
                if not rows:
                    return []
                # Use dict(row) if row_factory is set, otherwise manual conversion
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.log_error(e, {"operation": "get_active_agents"})
            return []  # Return empty list on error instead of hanging
    
    # Session management
    
    async def create_session(self, session_id: str, agent_id: str, task: str) -> None:
        """Create a new session record."""
        async with self.transaction() as db:
            await db.execute("""
                INSERT INTO sessions (session_id, agent_id, task, updated_at)
                VALUES (?, ?, ?, ?)
            """, (session_id, agent_id, task, datetime.now().isoformat()))
    
    async def update_session(self, session_id: str, conversation_turn: Dict, cost: float = 0.0) -> None:
        """Update session with new conversation turn."""
        if not self._initialized:
            await self.initialize()
            
        # Get existing conversation history
        async with self._db.execute(
            "SELECT conversation_history, turn_count, total_cost FROM sessions WHERE session_id = ?",
            (session_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return
            
            history = json.loads(row[0]) if row[0] else []
            turn_count = row[1] or 0
            total_cost = row[2] or 0.0
        
        # Append new turn
        history.append(conversation_turn)
        
        # Update session
        async with self.transaction() as db:
            await db.execute("""
                UPDATE sessions 
                SET conversation_history = ?, turn_count = ?, total_cost = ?, updated_at = ?
                WHERE session_id = ?
            """, (
                json.dumps(history),
                turn_count + 1,
                total_cost + cost,
                datetime.now().isoformat(),
                session_id
            ))
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session information."""
        if not self._initialized:
            await self.initialize()
            
        async with self._db.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                result = dict(row)
                # Parse JSON fields
                if result.get('conversation_history'):
                    result['conversation_history'] = json.loads(result['conversation_history'])
                return result
        return None
    
    # Task management
    
    async def create_task(self, task_id: str, description: str, 
                         parent_task_id: str = None, assigned_agents: List[str] = None) -> None:
        """Create a new task record."""
        async with self.transaction() as db:
            await db.execute("""
                INSERT INTO tasks (id, parent_task_id, description, assigned_agents)
                VALUES (?, ?, ?, ?)
            """, (
                task_id, parent_task_id, description,
                json.dumps(assigned_agents or [])
            ))
    
    async def update_task_progress(self, task_id: str, progress: float, status: str = None) -> None:
        """Update task progress."""
        async with self.transaction() as db:
            if status:
                await db.execute("""
                    UPDATE tasks SET progress = ?, status = ? WHERE id = ?
                """, (progress, status, task_id))
            else:
                await db.execute("""
                    UPDATE tasks SET progress = ? WHERE id = ?
                """, (progress, task_id))
    
    async def complete_task(self, task_id: str, result: Dict) -> None:
        """Mark task as completed with result."""
        async with self.transaction() as db:
            await db.execute("""
                UPDATE tasks 
                SET status = 'completed', progress = 100.0, result = ?, completed_at = ?
                WHERE id = ?
            """, (json.dumps(result), datetime.now().isoformat(), task_id))
    
    # Message management
    
    async def save_message(self, from_agent: str, to_agent: Optional[str], 
                          message: str, message_type: str = "info") -> int:
        """Save an inter-agent message."""
        async with self.transaction() as db:
            cursor = await db.execute("""
                INSERT INTO messages (from_agent, to_agent, message, message_type)
                VALUES (?, ?, ?, ?)
            """, (from_agent, to_agent, message, message_type))
            return cursor.lastrowid
    
    async def get_messages_for_agent(self, agent_id: str, since_timestamp: str = None) -> List[Dict]:
        """Get messages for a specific agent."""
        if not self._initialized:
            await self.initialize()
            
        query = """
            SELECT * FROM messages 
            WHERE (to_agent = ? OR to_agent IS NULL)
        """
        params = [agent_id]
        
        if since_timestamp:
            query += " AND timestamp > ?"
            params.append(since_timestamp)
        
        query += " ORDER BY timestamp ASC"
        
        async with self._db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]
    
    async def acknowledge_message(self, message_id: int) -> None:
        """Mark a message as acknowledged."""
        async with self.transaction() as db:
            await db.execute("""
                UPDATE messages SET acknowledged = 1 WHERE id = ?
            """, (message_id,))
    
    # Orchestration management
    
    async def save_orchestration(self, orchestration_id: str, request: str, 
                                 agents: List[str], batches: List[List[str]], 
                                 status: str = 'running', metadata: Dict = None) -> None:
        """Save orchestration information."""
        async with self.transaction() as db:
            await db.execute("""
                INSERT INTO orchestrations 
                (id, request, status, agents, batches, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                orchestration_id, request, status,
                json.dumps(agents), json.dumps(batches),
                datetime.now().isoformat(),
                json.dumps(metadata or {})
            ))
    
    async def update_orchestration(self, orchestration_id: str, 
                                  total_cost: float = None, total_duration_ms: int = None,
                                  successful_agents: int = None, total_agents: int = None,
                                  status: str = None, summary: str = None) -> None:
        """Update orchestration completion information."""
        updates = []
        params = []
        
        if total_cost is not None:
            updates.append("total_cost = ?")
            params.append(total_cost)
        if total_duration_ms is not None:
            updates.append("total_duration_ms = ?")
            params.append(total_duration_ms)
        if successful_agents is not None:
            updates.append("successful_agents = ?")
            params.append(successful_agents)
        if total_agents is not None:
            updates.append("total_agents = ?")
            params.append(total_agents)
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        if summary is not None:
            updates.append("summary = ?")
            params.append(summary)
        
        if status == 'completed':
            updates.append("completed_at = ?")
            params.append(datetime.now().isoformat())
        
        if updates:
            params.append(orchestration_id)
            async with self.transaction() as db:
                await db.execute(f"""
                    UPDATE orchestrations 
                    SET {', '.join(updates)}
                    WHERE id = ?
                """, params)
    
    async def get_orchestration(self, orchestration_id: str) -> Optional[Dict]:
        """Get orchestration information."""
        if not self._initialized:
            await self.initialize()
            
        async with self._db.execute(
            "SELECT * FROM orchestrations WHERE id = ? OR id LIKE ?", 
            (orchestration_id, f"{orchestration_id}%")
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                result = dict(row)
                # Parse JSON fields
                for field in ['agents', 'batches', 'metadata']:
                    if result.get(field):
                        result[field] = json.loads(result[field])
                return result
        return None
    
    async def get_statistics(self) -> Dict[str, int]:
        """Get database statistics"""
        if not self._initialized:
            await self.initialize()
        
        stats = {}
        tables = ['agents', 'sessions', 'tasks', 'messages', 'orchestrations', 'checkpoints']
        
        for table in tables:
            async with self._db.execute(f"SELECT COUNT(*) FROM {table}") as cursor:
                row = await cursor.fetchone()
                stats[table] = row[0] if row else 0
        
        return stats
    
    async def list_orchestrations(self) -> List[Dict]:
        """List all orchestrations."""
        if not self._initialized:
            await self.initialize()
            
        async with self._db.execute(
            "SELECT * FROM orchestrations ORDER BY created_at DESC"
        ) as cursor:
            rows = await cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                # Parse JSON fields
                for field in ['agents', 'batches', 'metadata']:
                    if result.get(field):
                        result[field] = json.loads(result[field])
                results.append(result)
            return results
    
    # Checkpoint management
    
    async def save_checkpoint(self, checkpoint_id: str, name: str, checkpoint_data: Dict) -> None:
        """Save a complete checkpoint."""
        async with self.transaction() as db:
            await db.execute("""
                INSERT OR REPLACE INTO checkpoints 
                (id, name, description, orchestrator_state, agent_sessions, task_states, message_history)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                checkpoint_id,
                name,
                checkpoint_data.get('description', ''),
                json.dumps(checkpoint_data.get('orchestrator_state', {})),
                json.dumps(checkpoint_data.get('agent_sessions', {})),
                json.dumps(checkpoint_data.get('task_states', {})),
                json.dumps(checkpoint_data.get('message_history', []))
            ))
    
    async def load_checkpoint(self, name: str) -> Optional[Dict]:
        """Load a checkpoint by name."""
        if not self._initialized:
            await self.initialize()
            
        async with self._db.execute(
            "SELECT * FROM checkpoints WHERE name = ?", (name,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                result = dict(row)
                # Parse JSON fields
                for field in ['orchestrator_state', 'agent_sessions', 'task_states', 'message_history']:
                    if result.get(field):
                        result[field] = json.loads(result[field])
                return result
        return None
    
    async def list_checkpoints(self) -> List[Dict]:
        """List all available checkpoints."""
        if not self._initialized:
            await self.initialize()
            
        async with self._db.execute(
            "SELECT id, name, description, created_at FROM checkpoints ORDER BY created_at DESC"
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]
    
    # Generic persistence interface implementation
    
    async def save(self, key: str, data: Any) -> None:
        """Generic save method for compatibility."""
        # Store as JSON in a generic key-value table
        async with self.transaction() as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS key_value_store (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                INSERT OR REPLACE INTO key_value_store (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, json.dumps(data, default=str), datetime.now().isoformat()))
    
    async def load(self, key: str) -> Optional[Any]:
        """Generic load method for compatibility."""
        if not self._initialized:
            await self.initialize()
            
        async with self._db.execute(
            "SELECT value FROM key_value_store WHERE key = ?", (key,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return json.loads(row[0])
        return None
    
    async def delete(self, key: str) -> bool:
        """Generic delete method for compatibility."""
        async with self.transaction() as db:
            cursor = await db.execute(
                "DELETE FROM key_value_store WHERE key = ?", (key,)
            )
            return cursor.rowcount > 0
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        if not self._initialized:
            await self.initialize()
            
        async with self._db.execute(
            "SELECT 1 FROM key_value_store WHERE key = ? LIMIT 1", (key,)
        ) as cursor:
            return await cursor.fetchone() is not None
    
    async def list_keys(self) -> List[str]:
        """List all keys."""
        if not self._initialized:
            await self.initialize()
            
        async with self._db.execute("SELECT key FROM key_value_store") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def clear(self) -> None:
        """Clear all data (use with caution!)."""
        async with self.transaction() as db:
            tables = ['agents', 'sessions', 'tasks', 'messages', 'checkpoints', 'key_value_store', 'orchestrations']
            for table in tables:
                await db.execute(f"DELETE FROM {table}")
    
    async def close(self) -> None:
        """Close database connection."""
        if self._db:
            await self._db.close()
            self._db = None
            self._initialized = False