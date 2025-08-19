"""Event persistence and replay capabilities."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import json
import sqlite3
import aiofiles
import aiosqlite

from .core import Event, EventFilter

logger = logging.getLogger(__name__)


@dataclass
class EventQuery:
    """Query parameters for event retrieval."""
    from_timestamp: Optional[datetime] = None
    to_timestamp: Optional[datetime] = None
    event_types: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    correlation_ids: Optional[List[str]] = None
    limit: int = 1000
    offset: int = 0
    order_by: str = "timestamp"  # timestamp, type, source
    order_direction: str = "DESC"  # ASC, DESC


class EventStore:
    """Persistent event storage with SQLite backend."""
    
    def __init__(
        self,
        db_path: str = "events.db",
        max_events: int = 1000000,
        retention_days: int = 30
    ):
        self.db_path = db_path
        self.max_events = max_events
        self.retention_days = retention_days
        
        # Connection pool
        self.connection_pool: List[aiosqlite.Connection] = []
        self.pool_size = 10
        self.pool_lock = asyncio.Lock()
        
        # Batch operations
        self.batch_size = 1000
        self.batch_events: List[Event] = []
        self.batch_lock = asyncio.Lock()
        self.batch_flush_task: Optional[asyncio.Task] = None
        self.flush_interval = 5.0  # seconds
        
        # Cleanup
        self.cleanup_task: Optional[asyncio.Task] = None
        self.cleanup_interval = 3600  # 1 hour
        
        # Metrics
        self.metrics = {
            "events_stored": 0,
            "events_retrieved": 0,
            "storage_errors": 0,
            "db_size_bytes": 0,
            "batch_flushes": 0
        }
        
        # Status
        self.is_running = False
        
        logger.info(f"Event store initialized with DB: {db_path}")
    
    async def start(self):
        """Initialize the event store."""
        if self.is_running:
            return
        
        try:
            # Initialize database
            await self._init_database()
            
            # Create connection pool
            await self._create_connection_pool()
            
            self.is_running = True
            
            # Start background tasks
            self.batch_flush_task = asyncio.create_task(self._batch_flush_loop())
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info("Event store started")
            
        except Exception as e:
            logger.error(f"Failed to start event store: {e}")
            raise
    
    async def stop(self):
        """Stop the event store."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        try:
            # Cancel background tasks
            if self.batch_flush_task:
                self.batch_flush_task.cancel()
                try:
                    await self.batch_flush_task
                except asyncio.CancelledError:
                    pass
            
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Flush remaining events
            await self._flush_batch()
            
            # Close connection pool
            await self._close_connection_pool()
            
            logger.info("Event store stopped")
            
        except Exception as e:
            logger.error(f"Error stopping event store: {e}")
    
    async def _init_database(self):
        """Initialize the SQLite database schema."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        source TEXT NOT NULL,
                        topic TEXT NOT NULL,
                        data TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        correlation_id TEXT,
                        causation_id TEXT,
                        metadata TEXT,
                        tags TEXT,
                        severity TEXT DEFAULT 'info',
                        ttl_expires_at DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better query performance
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_timestamp 
                    ON events(timestamp)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_type 
                    ON events(type)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_source 
                    ON events(source)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_topic 
                    ON events(topic)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_correlation_id 
                    ON events(correlation_id)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_severity 
                    ON events(severity)
                """)
                
                await db.commit()
                
            logger.info("Database schema initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def _create_connection_pool(self):
        """Create a pool of database connections."""
        async with self.pool_lock:
            for _ in range(self.pool_size):
                conn = await aiosqlite.connect(self.db_path)
                conn.row_factory = aiosqlite.Row
                self.connection_pool.append(conn)
        
        logger.debug(f"Created connection pool with {self.pool_size} connections")
    
    async def _close_connection_pool(self):
        """Close all connections in the pool."""
        async with self.pool_lock:
            for conn in self.connection_pool:
                await conn.close()
            self.connection_pool.clear()
        
        logger.debug("Closed connection pool")
    
    async def _get_connection(self) -> aiosqlite.Connection:
        """Get a connection from the pool."""
        async with self.pool_lock:
            if self.connection_pool:
                return self.connection_pool.pop()
        
        # Create new connection if pool is empty
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        return conn
    
    async def _return_connection(self, conn: aiosqlite.Connection):
        """Return a connection to the pool."""
        async with self.pool_lock:
            if len(self.connection_pool) < self.pool_size:
                self.connection_pool.append(conn)
            else:
                await conn.close()
    
    async def store_event(self, event: Event):
        """Store an event (batched for performance)."""
        try:
            async with self.batch_lock:
                self.batch_events.append(event)
                
                # Flush immediately if batch is full
                if len(self.batch_events) >= self.batch_size:
                    await self._flush_batch()
            
        except Exception as e:
            self.metrics["storage_errors"] += 1
            logger.error(f"Failed to queue event for storage: {e}")
            raise
    
    async def _flush_batch(self):
        """Flush batched events to database."""
        if not self.batch_events:
            return
        
        try:
            # Get current batch
            current_batch = self.batch_events.copy()
            self.batch_events.clear()
            
            conn = await self._get_connection()
            
            try:
                # Prepare batch insert
                insert_data = []
                for event in current_batch:
                    # Skip expired events
                    if event.is_expired():
                        continue
                    
                    # Calculate TTL expiration
                    ttl_expires_at = None
                    if event.ttl:
                        ttl_expires_at = event.timestamp + event.ttl
                    
                    insert_data.append((
                        event.id,
                        event.type.value,
                        event.source,
                        event.topic,
                        json.dumps(event.data),
                        event.timestamp.isoformat(),
                        event.correlation_id,
                        event.causation_id,
                        json.dumps(event.metadata),
                        json.dumps(list(event.tags)),
                        event.severity,
                        ttl_expires_at.isoformat() if ttl_expires_at else None
                    ))
                
                if insert_data:
                    await conn.executemany("""
                        INSERT OR REPLACE INTO events 
                        (id, type, source, topic, data, timestamp, correlation_id, 
                         causation_id, metadata, tags, severity, ttl_expires_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, insert_data)
                    
                    await conn.commit()
                    
                    self.metrics["events_stored"] += len(insert_data)
                    self.metrics["batch_flushes"] += 1
                    
                    logger.debug(f"Stored batch of {len(insert_data)} events")
                    
            finally:
                await self._return_connection(conn)
                
        except Exception as e:
            self.metrics["storage_errors"] += 1
            logger.error(f"Failed to flush event batch: {e}")
    
    async def _batch_flush_loop(self):
        """Periodic batch flushing loop."""
        try:
            while self.is_running:
                await asyncio.sleep(self.flush_interval)
                
                async with self.batch_lock:
                    if self.batch_events:
                        await self._flush_batch()
                        
        except asyncio.CancelledError:
            logger.info("Batch flush loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Batch flush loop error: {e}")
    
    async def get_events(
        self,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None,
        event_filter: Optional[EventFilter] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Event]:
        """Retrieve events from storage."""
        try:
            conn = await self._get_connection()
            
            try:
                # Build query
                query = "SELECT * FROM events WHERE 1=1"
                params = []
                
                if from_timestamp:
                    query += " AND timestamp >= ?"
                    params.append(from_timestamp.isoformat())
                
                if to_timestamp:
                    query += " AND timestamp <= ?"
                    params.append(to_timestamp.isoformat())
                
                if event_filter:
                    if event_filter.event_types:
                        placeholders = ",".join(["?"] * len(event_filter.event_types))
                        query += f" AND type IN ({placeholders})"
                        params.extend([et.value for et in event_filter.event_types])
                    
                    if event_filter.sources:
                        placeholders = ",".join(["?"] * len(event_filter.sources))
                        query += f" AND source IN ({placeholders})"
                        params.extend(event_filter.sources)
                    
                    if event_filter.topics:
                        placeholders = ",".join(["?"] * len(event_filter.topics))
                        query += f" AND topic IN ({placeholders})"
                        params.extend(event_filter.topics)
                
                # Add ordering and pagination
                query += " ORDER BY timestamp DESC"
                query += f" LIMIT {limit} OFFSET {offset}"
                
                # Execute query
                cursor = await conn.execute(query, params)
                rows = await cursor.fetchall()
                
                # Convert to Event objects
                events = []
                for row in rows:
                    event = self._row_to_event(row)
                    
                    # Apply additional filtering
                    if event_filter and not event_filter.matches(event):
                        continue
                    
                    events.append(event)
                
                self.metrics["events_retrieved"] += len(events)
                return events
                
            finally:
                await self._return_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to retrieve events: {e}")
            return []
    
    async def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get a specific event by ID."""
        try:
            conn = await self._get_connection()
            
            try:
                cursor = await conn.execute(
                    "SELECT * FROM events WHERE id = ?",
                    (event_id,)
                )
                row = await cursor.fetchone()
                
                if row:
                    event = self._row_to_event(row)
                    self.metrics["events_retrieved"] += 1
                    return event
                
                return None
                
            finally:
                await self._return_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to retrieve event {event_id}: {e}")
            return None
    
    def _row_to_event(self, row) -> Event:
        """Convert database row to Event object."""
        from .core import EventType
        
        return Event(
            id=row["id"],
            type=EventType(row["type"]),
            source=row["source"],
            topic=row["topic"],
            data=json.loads(row["data"]),
            timestamp=datetime.fromisoformat(row["timestamp"]),
            correlation_id=row["correlation_id"],
            causation_id=row["causation_id"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            tags=set(json.loads(row["tags"])) if row["tags"] else set(),
            severity=row["severity"]
        )
    
    async def delete_event(self, event_id: str) -> bool:
        """Delete a specific event."""
        try:
            conn = await self._get_connection()
            
            try:
                cursor = await conn.execute(
                    "DELETE FROM events WHERE id = ?",
                    (event_id,)
                )
                await conn.commit()
                
                return cursor.rowcount > 0
                
            finally:
                await self._return_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to delete event {event_id}: {e}")
            return False
    
    async def _cleanup_loop(self):
        """Periodic cleanup of expired events."""
        try:
            while self.is_running:
                await asyncio.sleep(self.cleanup_interval)
                
                try:
                    await self._cleanup_expired_events()
                    await self._cleanup_old_events()
                    await self._update_metrics()
                    
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Cleanup loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Cleanup loop error: {e}")
    
    async def _cleanup_expired_events(self):
        """Remove TTL-expired events."""
        try:
            conn = await self._get_connection()
            
            try:
                cursor = await conn.execute("""
                    DELETE FROM events 
                    WHERE ttl_expires_at IS NOT NULL 
                    AND ttl_expires_at < CURRENT_TIMESTAMP
                """)
                await conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Cleaned up {cursor.rowcount} TTL-expired events")
                    
            finally:
                await self._return_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired events: {e}")
    
    async def _cleanup_old_events(self):
        """Remove events older than retention period."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            
            conn = await self._get_connection()
            
            try:
                cursor = await conn.execute(
                    "DELETE FROM events WHERE timestamp < ?",
                    (cutoff_date.isoformat(),)
                )
                await conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Cleaned up {cursor.rowcount} old events")
                    
            finally:
                await self._return_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to cleanup old events: {e}")
    
    async def _update_metrics(self):
        """Update storage metrics."""
        try:
            import os
            if os.path.exists(self.db_path):
                self.metrics["db_size_bytes"] = os.path.getsize(self.db_path)
                
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get event store metrics."""
        try:
            conn = await self._get_connection()
            
            try:
                # Get event counts
                cursor = await conn.execute("SELECT COUNT(*) as count FROM events")
                row = await cursor.fetchone()
                total_events = row["count"] if row else 0
                
                # Get events by type
                cursor = await conn.execute("""
                    SELECT type, COUNT(*) as count 
                    FROM events 
                    GROUP BY type 
                    ORDER BY count DESC
                """)
                events_by_type = {row["type"]: row["count"] for row in await cursor.fetchall()}
                
                return {
                    **self.metrics,
                    "total_events_in_db": total_events,
                    "events_by_type": events_by_type,
                    "batch_queue_size": len(self.batch_events)
                }
                
            finally:
                await self._return_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return self.metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            # Test database connectivity
            conn = await self._get_connection()
            
            try:
                cursor = await conn.execute("SELECT 1")
                await cursor.fetchone()
                
                db_status = "healthy"
                
            finally:
                await self._return_connection(conn)
            
            return {
                "status": "healthy" if self.is_running else "stopped",
                "database_status": db_status,
                "connection_pool_size": len(self.connection_pool),
                "batch_queue_size": len(self.batch_events),
                "metrics": await self.get_metrics()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class EventReplay:
    """Event replay functionality."""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        
        logger.info("Event replay initialized")
    
    async def replay_events(
        self,
        from_timestamp: datetime,
        to_timestamp: Optional[datetime] = None,
        event_filter: Optional[EventFilter] = None,
        callback: Optional[callable] = None,
        replay_speed: float = 1.0,  # 1.0 = real-time, 0.5 = half-speed, 2.0 = double-speed
        batch_size: int = 100
    ) -> int:
        """Replay events with optional speed control."""
        try:
            logger.info(f"Starting event replay from {from_timestamp}")
            
            total_replayed = 0
            offset = 0
            
            while True:
                # Get batch of events
                events = await self.event_store.get_events(
                    from_timestamp=from_timestamp,
                    to_timestamp=to_timestamp,
                    event_filter=event_filter,
                    limit=batch_size,
                    offset=offset
                )
                
                if not events:
                    break
                
                # Replay events with timing
                prev_timestamp = None
                
                for event in events:
                    # Calculate delay for realistic timing
                    if prev_timestamp and replay_speed > 0:
                        time_diff = (event.timestamp - prev_timestamp).total_seconds()
                        delay = time_diff / replay_speed
                        
                        if delay > 0:
                            await asyncio.sleep(min(delay, 10))  # Cap delay at 10 seconds
                    
                    # Execute callback
                    if callback:
                        try:
                            result = callback(event)
                            if asyncio.iscoroutine(result):
                                await result
                        except Exception as e:
                            logger.error(f"Replay callback error for event {event.id}: {e}")
                    
                    prev_timestamp = event.timestamp
                    total_replayed += 1
                
                offset += batch_size
                
                # Progress logging
                if total_replayed % 1000 == 0:
                    logger.info(f"Replayed {total_replayed} events")
            
            logger.info(f"Event replay completed. Total events replayed: {total_replayed}")
            return total_replayed
            
        except Exception as e:
            logger.error(f"Event replay failed: {e}")
            raise