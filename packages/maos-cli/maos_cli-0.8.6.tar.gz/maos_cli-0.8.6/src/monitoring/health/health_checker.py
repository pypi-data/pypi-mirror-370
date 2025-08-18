"""
Core health checking infrastructure for MAOS components.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from uuid import uuid4

from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Represents the health status of a component."""
    component_name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    last_check: datetime = field(default_factory=datetime.utcnow)
    check_duration_ms: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "component_name": self.component_name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "last_check": self.last_check.isoformat(),
            "check_duration_ms": self.check_duration_ms,
            "dependencies": self.dependencies,
            "metrics": self.metrics,
            "is_healthy": self.status == HealthStatus.HEALTHY
        }
    
    def is_healthy(self) -> bool:
        """Check if component is healthy."""
        return self.status == HealthStatus.HEALTHY
    
    def is_degraded(self) -> bool:
        """Check if component is degraded."""
        return self.status == HealthStatus.DEGRADED
    
    def is_unhealthy(self) -> bool:
        """Check if component is unhealthy."""
        return self.status == HealthStatus.UNHEALTHY


class HealthChecker(ABC):
    """
    Abstract base class for component health checkers.
    """
    
    def __init__(
        self,
        component_name: str,
        check_interval: float = 30.0,
        timeout: float = 10.0,
        dependencies: Optional[List[str]] = None
    ):
        """Initialize health checker."""
        self.component_name = component_name
        self.check_interval = check_interval
        self.timeout = timeout
        self.dependencies = dependencies or []
        
        self.logger = MAOSLogger(f"health_checker_{component_name}", str(uuid4()))
        
        # Health state
        self._current_health: Optional[ComponentHealth] = None
        self._health_history: List[ComponentHealth] = []
        self._max_history = 100
        
        # Background monitoring
        self._monitor_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Callbacks
        self._status_change_callbacks: List[Callable[[ComponentHealth], None]] = []
    
    @abstractmethod
    async def check_health(self) -> ComponentHealth:
        """
        Perform health check for this component.
        
        Returns:
            ComponentHealth: Current health status
        """
        pass
    
    async def start_monitoring(self) -> None:
        """Start continuous health monitoring."""
        if self._monitor_task and not self._monitor_task.done():
            self.logger.logger.warning("Health monitoring already running")
            return
        
        self.logger.logger.info(f"Starting health monitoring for {self.component_name}")
        self._shutdown_event.clear()
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self) -> None:
        """Stop health monitoring."""
        self.logger.logger.info(f"Stopping health monitoring for {self.component_name}")
        
        self._shutdown_event.set()
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
    
    async def _monitoring_loop(self) -> None:
        """Continuous monitoring loop."""
        while not self._shutdown_event.is_set():
            try:
                # Perform health check
                health = await self.perform_health_check()
                
                # Check for status changes
                if self._current_health and self._current_health.status != health.status:
                    self.logger.logger.info(
                        f"Health status changed: {self._current_health.status.value} -> {health.status.value}",
                        extra={
                            "component": self.component_name,
                            "old_status": self._current_health.status.value,
                            "new_status": health.status.value,
                            "message": health.message
                        }
                    )
                    
                    # Notify callbacks
                    for callback in self._status_change_callbacks:
                        try:
                            callback(health)
                        except Exception as e:
                            self.logger.log_error(e, {"operation": "status_change_callback"})
                
                # Update current health
                self._current_health = health
                
                # Store in history
                self._health_history.append(health)
                if len(self._health_history) > self._max_history:
                    self._health_history.pop(0)
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {"operation": "health_monitoring_loop"})
                
                # Set unhealthy status on monitoring failure
                error_health = ComponentHealth(
                    component_name=self.component_name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health monitoring failed: {str(e)}",
                    details={"error": str(e), "error_type": type(e).__name__}
                )
                self._current_health = error_health
                
                await asyncio.sleep(self.check_interval)
    
    async def perform_health_check(self) -> ComponentHealth:
        """
        Perform health check with timeout and error handling.
        
        Returns:
            ComponentHealth: Health status result
        """
        start_time = time.time()
        
        try:
            # Perform health check with timeout
            health = await asyncio.wait_for(
                self.check_health(),
                timeout=self.timeout
            )
            
            # Calculate check duration
            duration_ms = (time.time() - start_time) * 1000
            health.check_duration_ms = duration_ms
            
            return health
            
        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            return ComponentHealth(
                component_name=self.component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {self.timeout}s",
                details={"timeout": self.timeout},
                check_duration_ms=duration_ms
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.log_error(e, {
                "operation": "health_check",
                "component": self.component_name
            })
            
            return ComponentHealth(
                component_name=self.component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                details={
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                check_duration_ms=duration_ms
            )
    
    def get_current_health(self) -> Optional[ComponentHealth]:
        """Get current health status."""
        return self._current_health
    
    def get_health_history(self, hours: int = 1) -> List[ComponentHealth]:
        """Get health history for specified hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            health for health in self._health_history
            if health.last_check > cutoff_time
        ]
    
    def add_status_change_callback(self, callback: Callable[[ComponentHealth], None]) -> None:
        """Add callback for status changes."""
        self._status_change_callbacks.append(callback)
    
    def remove_status_change_callback(self, callback: Callable[[ComponentHealth], None]) -> None:
        """Remove status change callback."""
        if callback in self._status_change_callbacks:
            self._status_change_callbacks.remove(callback)
    
    def get_uptime_percentage(self, hours: int = 24) -> float:
        """Calculate uptime percentage for specified period."""
        history = self.get_health_history(hours)
        
        if not history:
            return 0.0
        
        healthy_count = sum(1 for h in history if h.is_healthy())
        return (healthy_count / len(history)) * 100.0
    
    def get_average_response_time(self, hours: int = 1) -> float:
        """Get average response time for health checks."""
        history = self.get_health_history(hours)
        
        if not history:
            return 0.0
        
        total_duration = sum(h.check_duration_ms for h in history)
        return total_duration / len(history)