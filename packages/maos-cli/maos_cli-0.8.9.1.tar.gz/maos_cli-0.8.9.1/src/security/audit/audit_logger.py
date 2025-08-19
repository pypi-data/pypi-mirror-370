"""Comprehensive audit logging system."""

import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import aioredis

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Audit event types."""
    # Authentication events
    AUTH_LOGIN_SUCCESS = "auth.login.success"
    AUTH_LOGIN_FAILURE = "auth.login.failure"
    AUTH_LOGOUT = "auth.logout"
    AUTH_TOKEN_REFRESH = "auth.token.refresh"
    AUTH_PASSWORD_CHANGE = "auth.password.change"
    
    # Authorization events
    AUTHZ_ACCESS_GRANTED = "authz.access.granted"
    AUTHZ_ACCESS_DENIED = "authz.access.denied"
    AUTHZ_PERMISSION_GRANTED = "authz.permission.granted"
    AUTHZ_PERMISSION_REVOKED = "authz.permission.revoked"
    AUTHZ_ROLE_ASSIGNED = "authz.role.assigned"
    AUTHZ_ROLE_REMOVED = "authz.role.removed"
    
    # API events
    API_REQUEST = "api.request"
    API_RESPONSE = "api.response"
    API_ERROR = "api.error"
    API_KEY_CREATED = "api.key.created"
    API_KEY_REVOKED = "api.key.revoked"
    
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"
    SYSTEM_CONFIG_CHANGE = "system.config.change"
    
    # Security events
    SECURITY_ATTACK_DETECTED = "security.attack.detected"
    SECURITY_VIOLATION = "security.violation"
    SECURITY_KEY_ROTATION = "security.key.rotation"
    SECURITY_POLICY_CHANGE = "security.policy.change"
    
    # Data events
    DATA_CREATE = "data.create"
    DATA_READ = "data.read"
    DATA_UPDATE = "data.update"
    DATA_DELETE = "data.delete"
    DATA_EXPORT = "data.export"
    
    # Agent events
    AGENT_CREATED = "agent.created"
    AGENT_STARTED = "agent.started"
    AGENT_STOPPED = "agent.stopped"
    AGENT_ERROR = "agent.error"
    
    # Task events
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"


class EventSeverity(Enum):
    """Event severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Comprehensive audit event."""
    event_id: str
    event_type: EventType
    timestamp: datetime
    severity: EventSeverity
    
    # Actor information
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Event details
    resource: Optional[str] = None
    action: Optional[str] = None
    outcome: Optional[str] = None
    reason: Optional[str] = None
    
    # Request/response details
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    request_params: Optional[Dict[str, Any]] = None
    response_status: Optional[int] = None
    response_time_ms: Optional[float] = None
    
    # Additional context
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['severity'] = self.severity.value
        data['timestamp'] = self.timestamp.isoformat()
        data['tags'] = list(self.tags)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEvent":
        """Create event from dictionary."""
        data = data.copy()
        data['event_type'] = EventType(data['event_type'])
        data['severity'] = EventSeverity(data['severity'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['tags'] = set(data.get('tags', []))
        return cls(**data)


class AuditLogger:
    """High-performance audit logger with multiple outputs."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        redis_db: int = 9,  # Separate DB for audit logs
        event_prefix: str = "audit:",
        batch_size: int = 100,
        flush_interval: int = 10,  # seconds
        retention_days: int = 365,
        enable_file_logging: bool = True,
        log_file_path: str = "/var/log/maos/audit.log",
        enable_syslog: bool = False,
        syslog_facility: str = "user"
    ):
        self.redis_url = redis_url
        self.redis_db = redis_db
        self.event_prefix = event_prefix
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.retention_days = retention_days
        self.enable_file_logging = enable_file_logging
        self.log_file_path = log_file_path
        self.enable_syslog = enable_syslog
        self.syslog_facility = syslog_facility
        
        # Redis connection
        self.redis: Optional[aioredis.Redis] = None
        
        # Event buffer for batch processing
        self.event_buffer: List[AuditEvent] = []
        self.buffer_lock = asyncio.Lock()
        
        # Background tasks
        self._flush_task: Optional[asyncio.Task] = None
        self._running = False
        
        # File logger
        self.file_logger = None
        if self.enable_file_logging:
            self._setup_file_logger()
        
        # Syslog
        self.syslog_handler = None
        if self.enable_syslog:
            self._setup_syslog()
        
        # Metrics
        self.metrics = {
            "events_logged": 0,
            "events_buffered": 0,
            "flush_operations": 0,
            "redis_errors": 0,
            "file_errors": 0
        }
        
        logger.info("Audit logger initialized")
    
    def _setup_file_logger(self):
        """Setup file-based audit logging."""
        try:
            import os
            os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
            
            self.file_logger = logging.getLogger("audit_file")
            self.file_logger.setLevel(logging.INFO)
            
            # Rotating file handler
            from logging.handlers import RotatingFileHandler
            handler = RotatingFileHandler(
                self.log_file_path,
                maxBytes=100*1024*1024,  # 100MB
                backupCount=10
            )
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.file_logger.addHandler(handler)
            
        except Exception as e:
            logger.error(f"Failed to setup file logging: {e}")
    
    def _setup_syslog(self):
        """Setup syslog audit logging."""
        try:
            from logging.handlers import SysLogHandler
            
            self.syslog_handler = SysLogHandler(
                address='/dev/log',
                facility=getattr(SysLogHandler, f'LOG_{self.syslog_facility.upper()}')
            )
            
            formatter = logging.Formatter(
                'MAOS-AUDIT: %(message)s'
            )
            self.syslog_handler.setFormatter(formatter)
            
        except Exception as e:
            logger.error(f"Failed to setup syslog: {e}")
    
    async def connect(self):
        """Connect to Redis and start background tasks."""
        try:
            self.redis = aioredis.from_url(
                self.redis_url,
                db=self.redis_db,
                decode_responses=True
            )
            
            # Test connection
            await self.redis.ping()
            
            # Start background flush task
            self._running = True
            self._flush_task = asyncio.create_task(self._flush_loop())
            
            logger.info("Audit logger connected to Redis")
            
        except Exception as e:
            logger.error(f"Failed to connect audit logger to Redis: {e}")
            # Continue without Redis (file logging only)
    
    async def disconnect(self):
        """Disconnect and flush remaining events."""
        self._running = False
        
        # Flush remaining events
        await self._flush_events()
        
        # Cancel flush task
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # Close Redis connection
        if self.redis:
            await self.redis.close()
            logger.info("Audit logger disconnected")
    
    async def log_event(self, event: AuditEvent):
        """Log audit event."""
        try:
            self.metrics["events_logged"] += 1
            
            # Immediate logging for critical events
            if event.severity == EventSeverity.CRITICAL:
                await self._write_event_immediately(event)
                return
            
            # Buffer non-critical events
            async with self.buffer_lock:
                self.event_buffer.append(event)
                self.metrics["events_buffered"] += 1
                
                # Flush if buffer is full
                if len(self.event_buffer) >= self.batch_size:
                    await self._flush_events_internal()
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    async def _write_event_immediately(self, event: AuditEvent):
        """Write event immediately for critical events."""
        try:
            await self._write_to_redis([event])
            self._write_to_file([event])
            self._write_to_syslog([event])
            
        except Exception as e:
            logger.error(f"Failed to write critical event: {e}")
    
    async def _flush_loop(self):
        """Background loop for flushing events."""
        try:
            while self._running:
                await asyncio.sleep(self.flush_interval)
                
                try:
                    async with self.buffer_lock:
                        if self.event_buffer:
                            await self._flush_events_internal()
                            
                except Exception as e:
                    logger.error(f"Flush loop error: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Audit flush loop cancelled")
            raise
    
    async def _flush_events(self):
        """Flush buffered events."""
        async with self.buffer_lock:
            await self._flush_events_internal()
    
    async def _flush_events_internal(self):
        """Internal flush implementation (assumes lock is held)."""
        if not self.event_buffer:
            return
        
        try:
            events_to_flush = self.event_buffer.copy()
            self.event_buffer.clear()
            
            # Write to all outputs
            await self._write_to_redis(events_to_flush)
            self._write_to_file(events_to_flush)
            self._write_to_syslog(events_to_flush)
            
            self.metrics["flush_operations"] += 1
            self.metrics["events_buffered"] -= len(events_to_flush)
            
        except Exception as e:
            logger.error(f"Failed to flush events: {e}")
            # Re-add events to buffer on failure
            self.event_buffer.extend(events_to_flush)
    
    async def _write_to_redis(self, events: List[AuditEvent]):
        """Write events to Redis."""
        try:
            if not self.redis:
                return
            
            pipe = self.redis.pipeline()
            
            for event in events:
                # Store as hash for structured data
                event_key = f"{self.event_prefix}{event.event_id}"
                event_data = event.to_dict()
                
                pipe.hset(event_key, mapping=event_data)
                
                # Set expiration based on retention policy
                if self.retention_days > 0:
                    pipe.expire(event_key, self.retention_days * 24 * 3600)
                
                # Add to sorted set for time-based queries
                pipe.zadd(
                    f"{self.event_prefix}timeline",
                    {event.event_id: event.timestamp.timestamp()}
                )
                
                # Add to type-specific index
                pipe.sadd(
                    f"{self.event_prefix}type:{event.event_type.value}",
                    event.event_id
                )
            
            await pipe.execute()
            
        except Exception as e:
            self.metrics["redis_errors"] += 1
            logger.error(f"Failed to write events to Redis: {e}")
    
    def _write_to_file(self, events: List[AuditEvent]):
        """Write events to file."""
        try:
            if not self.file_logger:
                return
            
            for event in events:
                log_message = json.dumps(event.to_dict())
                self.file_logger.info(log_message)
                
        except Exception as e:
            self.metrics["file_errors"] += 1
            logger.error(f"Failed to write events to file: {e}")
    
    def _write_to_syslog(self, events: List[AuditEvent]):
        """Write events to syslog."""
        try:
            if not self.syslog_handler:
                return
            
            syslog_logger = logging.getLogger("audit_syslog")
            syslog_logger.addHandler(self.syslog_handler)
            
            for event in events:
                log_message = json.dumps(event.to_dict())
                syslog_logger.info(log_message)
                
        except Exception as e:
            logger.error(f"Failed to write events to syslog: {e}")
    
    # Convenience methods for common events
    async def log_authentication(
        self,
        event_type: EventType,
        user_id: str,
        outcome: str,
        client_ip: str = None,
        reason: str = None,
        **kwargs
    ):
        """Log authentication event."""
        event = AuditEvent(
            event_id=f"auth_{datetime.now().timestamp()}_{hash(user_id) % 10000}",
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            severity=EventSeverity.MEDIUM if outcome == "success" else EventSeverity.HIGH,
            user_id=user_id,
            client_ip=client_ip,
            outcome=outcome,
            reason=reason,
            **kwargs
        )
        await self.log_event(event)
    
    async def log_api_request(
        self,
        user_id: str,
        method: str,
        path: str,
        status_code: int,
        response_time_ms: float,
        client_ip: str = None,
        **kwargs
    ):
        """Log API request."""
        severity = EventSeverity.LOW
        if status_code >= 500:
            severity = EventSeverity.HIGH
        elif status_code >= 400:
            severity = EventSeverity.MEDIUM
            
        event = AuditEvent(
            event_id=f"api_{datetime.now().timestamp()}_{hash(path) % 10000}",
            event_type=EventType.API_REQUEST,
            timestamp=datetime.now(timezone.utc),
            severity=severity,
            user_id=user_id,
            client_ip=client_ip,
            request_method=method,
            request_path=path,
            response_status=status_code,
            response_time_ms=response_time_ms,
            **kwargs
        )
        await self.log_event(event)
    
    async def log_security_event(
        self,
        event_type: EventType,
        severity: EventSeverity,
        description: str,
        client_ip: str = None,
        user_id: str = None,
        **kwargs
    ):
        """Log security event."""
        event = AuditEvent(
            event_id=f"sec_{datetime.now().timestamp()}_{hash(description) % 10000}",
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            severity=severity,
            user_id=user_id,
            client_ip=client_ip,
            reason=description,
            **kwargs
        )
        await self.log_event(event)
    
    async def get_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_types: Optional[List[EventType]] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Retrieve audit events with filtering."""
        try:
            if not self.redis:
                return []
            
            # Use timeline sorted set for time-based queries
            start_score = start_time.timestamp() if start_time else 0
            end_score = end_time.timestamp() if end_time else datetime.now(timezone.utc).timestamp()
            
            # Get event IDs in time range
            event_ids = await self.redis.zrangebyscore(
                f"{self.event_prefix}timeline",
                start_score,
                end_score,
                start=0,
                num=limit
            )
            
            events = []
            for event_id in event_ids:
                event_key = f"{self.event_prefix}{event_id}"
                event_data = await self.redis.hgetall(event_key)
                
                if event_data:
                    event = AuditEvent.from_dict(event_data)
                    
                    # Apply filters
                    if event_types and event.event_type not in event_types:
                        continue
                    
                    if user_id and event.user_id != user_id:
                        continue
                    
                    events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to retrieve events: {e}")
            return []
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get audit logging metrics."""
        return {
            "performance": self.metrics,
            "buffer_size": len(self.event_buffer),
            "redis_connected": self.redis is not None,
            "file_logging_enabled": self.enable_file_logging,
            "syslog_enabled": self.enable_syslog
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            status = "healthy"
            issues = []
            
            # Check Redis connection
            redis_connected = False
            if self.redis:
                try:
                    await self.redis.ping()
                    redis_connected = True
                except Exception:
                    issues.append("Redis connection failed")
                    status = "degraded"
            
            # Check buffer size
            if len(self.event_buffer) > self.batch_size * 2:
                issues.append("Event buffer growing large")
                status = "degraded"
            
            # Check flush task
            flush_running = self._flush_task is not None and not self._flush_task.done()
            if not flush_running:
                issues.append("Flush task not running")
                status = "degraded"
            
            return {
                "status": status,
                "issues": issues,
                "redis_connected": redis_connected,
                "flush_task_running": flush_running,
                "metrics": self.get_metrics()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()