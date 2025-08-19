"""
Logging configuration and utilities for MAOS orchestration system.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields from the record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'funcName', 'lineno', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'exc_info', 'exc_text', 'stack_info',
                          'getMessage']:
                # Rename 'name' fields in extra to avoid conflicts
                if key == 'name' and hasattr(record, 'name'):
                    continue  # Skip as it's already handled as 'logger'
                log_data[key] = value
        
        return json.dumps(log_data, default=str)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    structured: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Setup logging configuration for MAOS.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, logs to console only)
        structured: Whether to use structured JSON logging
        max_file_size: Maximum log file size before rotation
        backup_count: Number of backup files to keep
    """
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Setup formatter
    if structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set levels for specific loggers
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            'level': level,
            'structured': structured,
            'log_file': log_file,
            'max_file_size': max_file_size,
            'backup_count': backup_count
        }
    )


def get_logger(name: str, extra_context: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """
    Get a logger with optional extra context.
    
    Args:
        name: Logger name
        extra_context: Extra context to include in all log messages
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if extra_context:
        # Create a custom adapter to add extra context
        class ContextAdapter(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                kwargs.setdefault('extra', {}).update(extra_context)
                return msg, kwargs
        
        logger = ContextAdapter(logger, {})
    
    return logger


class MAOSLogger:
    """Centralized logger for MAOS components with common patterns."""
    
    def __init__(self, component: str, component_id: Optional[str] = None):
        """Initialize MAOS logger for a specific component."""
        self.component = component
        self.component_id = component_id
        self.logger = get_logger(
            f"maos.{component}",
            extra_context={
                'component': component,
                'component_id': component_id
            }
        )
    
    def log_task_event(self, event: str, task_id: str, **kwargs) -> None:
        """Log task-related events."""
        self.logger.info(
            f"Task {event}",
            extra={
                'event_type': 'task',
                'event': event,
                'task_id': task_id,
                **kwargs
            }
        )
    
    def log_agent_event(self, event: str, agent_id: str, **kwargs) -> None:
        """Log agent-related events."""
        self.logger.info(
            f"Agent {event}",
            extra={
                'event_type': 'agent',
                'event': event,
                'agent_id': agent_id,
                **kwargs
            }
        )
    
    def log_resource_event(self, event: str, resource_id: str, **kwargs) -> None:
        """Log resource-related events."""
        self.logger.info(
            f"Resource {event}",
            extra={
                'event_type': 'resource',
                'event': event,
                'resource_id': resource_id,
                **kwargs
            }
        )
    
    def log_performance_metric(self, metric_name: str, value: float, **kwargs) -> None:
        """Log performance metrics."""
        self.logger.info(
            f"Performance metric: {metric_name}",
            extra={
                'event_type': 'metric',
                'metric_name': metric_name,
                'metric_value': value,
                **kwargs
            }
        )
    
    def log_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Log errors with context."""
        self.logger.error(
            f"Error occurred: {str(error)}",
            extra={
                'event_type': 'error',
                'error_type': type(error).__name__,
                'error_message': str(error),
                **context
            },
            exc_info=True
        )
    
    def log_state_change(self, from_state: str, to_state: str, **kwargs) -> None:
        """Log state transitions."""
        self.logger.info(
            f"State change: {from_state} -> {to_state}",
            extra={
                'event_type': 'state_change',
                'from_state': from_state,
                'to_state': to_state,
                **kwargs
            }
        )