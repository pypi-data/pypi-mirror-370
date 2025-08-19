"""Health monitoring and heartbeat system."""

import asyncio
import logging
import psutil
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ComponentType(Enum):
    """Types of components that can be monitored."""
    SYSTEM = "system"
    APPLICATION = "application"
    SERVICE = "service"
    NETWORK = "network"
    STORAGE = "storage"
    DATABASE = "database"
    MESSAGE_BUS = "message_bus"
    AGENT = "agent"


@dataclass
class HealthMetric:
    """Individual health metric."""
    name: str
    value: float
    unit: str = ""
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def get_status(self) -> HealthStatus:
        """Determine status based on thresholds."""
        if self.threshold_critical is not None and self.value >= self.threshold_critical:
            return HealthStatus.CRITICAL
        elif self.threshold_warning is not None and self.value >= self.threshold_warning:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY


@dataclass
class ComponentHealth:
    """Health information for a component."""
    component_id: str
    component_type: ComponentType
    status: HealthStatus = HealthStatus.UNKNOWN
    message: str = ""
    metrics: Dict[str, HealthMetric] = field(default_factory=dict)
    last_check: datetime = field(default_factory=datetime.utcnow)
    uptime: float = 0.0  # seconds
    error_count: int = 0
    warning_count: int = 0
    
    def add_metric(self, metric: HealthMetric):
        """Add or update a health metric."""
        self.metrics[metric.name] = metric
        self.last_check = datetime.utcnow()
        
        # Update overall status based on metric
        metric_status = metric.get_status()
        if metric_status == HealthStatus.CRITICAL:
            self.status = HealthStatus.CRITICAL
        elif metric_status == HealthStatus.DEGRADED and self.status != HealthStatus.CRITICAL:
            self.status = HealthStatus.DEGRADED
        elif self.status == HealthStatus.UNKNOWN:
            self.status = HealthStatus.HEALTHY
    
    def is_healthy(self) -> bool:
        """Check if component is healthy."""
        return self.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "component_id": self.component_id,
            "component_type": self.component_type.value,
            "status": self.status.value,
            "message": self.message,
            "metrics": {
                name: {
                    "value": metric.value,
                    "unit": metric.unit,
                    "status": metric.get_status().value,
                    "timestamp": metric.timestamp.isoformat()
                }
                for name, metric in self.metrics.items()
            },
            "last_check": self.last_check.isoformat(),
            "uptime": self.uptime,
            "error_count": self.error_count,
            "warning_count": self.warning_count
        }


@dataclass
class HeartbeatInfo:
    """Heartbeat information from an agent or service."""
    source_id: str
    status: HealthStatus
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metrics: Dict[str, float] = field(default_factory=dict)
    message: str = ""
    sequence_number: int = 0
    
    def is_recent(self, max_age_seconds: int = 90) -> bool:
        """Check if heartbeat is recent."""
        age = (datetime.utcnow() - self.timestamp).total_seconds()
        return age <= max_age_seconds


class HealthMonitor:
    """Comprehensive health monitoring system."""
    
    def __init__(
        self,
        heartbeat_interval: int = 30,
        health_check_interval: int = 60,
        max_heartbeat_age: int = 90
    ):
        self.heartbeat_interval = heartbeat_interval
        self.health_check_interval = health_check_interval
        self.max_heartbeat_age = max_heartbeat_age
        
        # Component health tracking
        self.components: Dict[str, ComponentHealth] = {}
        
        # Heartbeat tracking
        self.heartbeats: Dict[str, HeartbeatInfo] = {}
        self.missed_heartbeats: Dict[str, int] = {}
        
        # Health check functions
        self.health_checkers: Dict[str, Callable] = {}
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
        
        # Background tasks
        self.monitor_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # System metrics
        self.start_time = time.time()
        
        # Metrics
        self.metrics = {
            "total_components": 0,
            "healthy_components": 0,
            "degraded_components": 0,
            "unhealthy_components": 0,
            "critical_components": 0,
            "total_heartbeats": 0,
            "missed_heartbeats": 0,
            "alerts_sent": 0
        }
        
        # Status
        self.is_running = False
        
        logger.info("Health monitor initialized")
    
    async def start(self):
        """Start the health monitor."""
        if self.is_running:
            return
        
        self.is_running = True
        self.start_time = time.time()
        
        # Register built-in system health checker
        self.register_health_checker("system", self._check_system_health)
        
        # Start background tasks
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Health monitor started")
    
    async def stop(self):
        """Stop the health monitor."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel background tasks
        for task in [self.monitor_task, self.heartbeat_task, self.cleanup_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("Health monitor stopped")
    
    def register_component(
        self,
        component_id: str,
        component_type: ComponentType,
        initial_status: HealthStatus = HealthStatus.UNKNOWN
    ) -> bool:
        """Register a component for monitoring."""
        try:
            if component_id in self.components:
                logger.warning(f"Component {component_id} already registered")
                return False
            
            self.components[component_id] = ComponentHealth(
                component_id=component_id,
                component_type=component_type,
                status=initial_status
            )
            
            self.metrics["total_components"] += 1
            logger.info(f"Registered component {component_id} for monitoring")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register component: {e}")
            return False
    
    def unregister_component(self, component_id: str) -> bool:
        """Unregister a component."""
        try:
            if component_id not in self.components:
                return False
            
            del self.components[component_id]
            
            # Remove from heartbeats if present
            if component_id in self.heartbeats:
                del self.heartbeats[component_id]
            if component_id in self.missed_heartbeats:
                del self.missed_heartbeats[component_id]
            
            self.metrics["total_components"] = max(0, self.metrics["total_components"] - 1)
            logger.info(f"Unregistered component {component_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister component: {e}")
            return False
    
    def register_health_checker(self, component_id: str, checker_func: Callable) -> bool:
        """Register a health check function for a component."""
        try:
            self.health_checkers[component_id] = checker_func
            logger.info(f"Registered health checker for {component_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register health checker: {e}")
            return False
    
    async def record_heartbeat(
        self,
        source_id: str,
        status: HealthStatus = HealthStatus.HEALTHY,
        metrics: Optional[Dict[str, float]] = None,
        message: str = ""
    ) -> bool:
        """Record a heartbeat from a component."""
        try:
            # Get current sequence number
            sequence_number = 0
            if source_id in self.heartbeats:
                sequence_number = self.heartbeats[source_id].sequence_number + 1
            
            # Create heartbeat info
            heartbeat = HeartbeatInfo(
                source_id=source_id,
                status=status,
                metrics=metrics or {},
                message=message,
                sequence_number=sequence_number
            )
            
            # Store heartbeat
            self.heartbeats[source_id] = heartbeat
            
            # Reset missed heartbeat counter
            self.missed_heartbeats[source_id] = 0
            
            # Update component status if registered
            if source_id in self.components:
                component = self.components[source_id]
                component.status = status
                component.last_check = datetime.utcnow()
                component.uptime = time.time() - self.start_time
                
                if message:
                    component.message = message
                
                # Add metrics
                for metric_name, value in (metrics or {}).items():
                    metric = HealthMetric(name=metric_name, value=value)
                    component.add_metric(metric)
            
            self.metrics["total_heartbeats"] += 1
            logger.debug(f"Recorded heartbeat from {source_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record heartbeat: {e}")
            return False
    
    async def check_component_health(self, component_id: str) -> Optional[ComponentHealth]:
        """Perform health check on a specific component."""
        try:
            if component_id not in self.components:
                return None
            
            component = self.components[component_id]
            
            # Run registered health checker if available
            if component_id in self.health_checkers:
                try:
                    checker = self.health_checkers[component_id]
                    result = checker()
                    
                    if asyncio.iscoroutine(result):
                        result = await result
                    
                    # Update component health based on result
                    if isinstance(result, dict):
                        if "status" in result:
                            component.status = HealthStatus(result["status"])
                        if "message" in result:
                            component.message = result["message"]
                        if "metrics" in result:
                            for name, value in result["metrics"].items():
                                metric = HealthMetric(name=name, value=value)
                                component.add_metric(metric)
                    
                except Exception as e:
                    component.status = HealthStatus.UNHEALTHY
                    component.message = f"Health check failed: {e}"
                    component.error_count += 1
                    logger.error(f"Health check failed for {component_id}: {e}")
            
            # Check heartbeat status
            if component_id in self.heartbeats:
                heartbeat = self.heartbeats[component_id]
                if not heartbeat.is_recent(self.max_heartbeat_age):
                    component.status = HealthStatus.UNHEALTHY
                    component.message = "Heartbeat timeout"
                    self.missed_heartbeats[component_id] = self.missed_heartbeats.get(component_id, 0) + 1
            
            component.last_check = datetime.utcnow()
            component.uptime = time.time() - self.start_time
            
            return component
            
        except Exception as e:
            logger.error(f"Failed to check component health: {e}")
            return None
    
    async def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        try:
            # Update component counts
            healthy_count = 0
            degraded_count = 0
            unhealthy_count = 0
            critical_count = 0
            
            for component in self.components.values():
                if component.status == HealthStatus.HEALTHY:
                    healthy_count += 1
                elif component.status == HealthStatus.DEGRADED:
                    degraded_count += 1
                elif component.status == HealthStatus.UNHEALTHY:
                    unhealthy_count += 1
                elif component.status == HealthStatus.CRITICAL:
                    critical_count += 1
            
            # Determine overall status
            overall_status = HealthStatus.HEALTHY
            if critical_count > 0:
                overall_status = HealthStatus.CRITICAL
            elif unhealthy_count > 0:
                overall_status = HealthStatus.UNHEALTHY
            elif degraded_count > 0:
                overall_status = HealthStatus.DEGRADED
            
            # Update metrics
            self.metrics.update({
                "healthy_components": healthy_count,
                "degraded_components": degraded_count,
                "unhealthy_components": unhealthy_count,
                "critical_components": critical_count
            })
            
            return {
                "overall_status": overall_status.value,
                "component_counts": {
                    "total": len(self.components),
                    "healthy": healthy_count,
                    "degraded": degraded_count,
                    "unhealthy": unhealthy_count,
                    "critical": critical_count
                },
                "uptime": time.time() - self.start_time,
                "last_check": datetime.utcnow().isoformat(),
                "is_monitoring": self.is_running
            }
            
        except Exception as e:
            logger.error(f"Failed to get overall health: {e}")
            return {
                "overall_status": HealthStatus.UNKNOWN.value,
                "error": str(e)
            }
    
    async def get_component_health(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Get health information for a specific component."""
        component = await self.check_component_health(component_id)
        return component.to_dict() if component else None
    
    async def get_all_components_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health information for all components."""
        health_info = {}
        
        for component_id in self.components:
            component_health = await self.get_component_health(component_id)
            if component_health:
                health_info[component_id] = component_health
        
        return health_info
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Built-in system health checker."""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine status based on thresholds
            status = HealthStatus.HEALTHY
            messages = []
            
            if cpu_percent > 90:
                status = HealthStatus.CRITICAL
                messages.append(f"CPU usage critical: {cpu_percent}%")
            elif cpu_percent > 75:
                status = HealthStatus.DEGRADED
                messages.append(f"CPU usage high: {cpu_percent}%")
            
            if memory.percent > 90:
                status = HealthStatus.CRITICAL
                messages.append(f"Memory usage critical: {memory.percent}%")
            elif memory.percent > 75:
                status = HealthStatus.DEGRADED
                messages.append(f"Memory usage high: {memory.percent}%")
            
            if disk.percent > 95:
                status = HealthStatus.CRITICAL
                messages.append(f"Disk usage critical: {disk.percent}%")
            elif disk.percent > 85:
                status = HealthStatus.DEGRADED
                messages.append(f"Disk usage high: {disk.percent}%")
            
            return {
                "status": status.value,
                "message": "; ".join(messages) if messages else "System healthy",
                "metrics": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available": memory.available,
                    "disk_percent": disk.percent,
                    "disk_free": disk.free
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"System health check failed: {e}",
                "metrics": {}
            }
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        try:
            while self.is_running:
                try:
                    # Check health of all components
                    for component_id in list(self.components.keys()):
                        await self.check_component_health(component_id)
                    
                    # Check for alerts
                    await self._check_alerts()
                    
                except Exception as e:
                    logger.error(f"Monitor loop error: {e}")
                
                await asyncio.sleep(self.health_check_interval)
                
        except asyncio.CancelledError:
            logger.info("Monitor loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Monitor loop error: {e}")
    
    async def _heartbeat_loop(self):
        """Self-heartbeat loop."""
        try:
            while self.is_running:
                try:
                    # Send own heartbeat
                    await self.record_heartbeat(
                        "health_monitor",
                        HealthStatus.HEALTHY,
                        {"uptime": time.time() - self.start_time},
                        "Health monitor running"
                    )
                    
                except Exception as e:
                    logger.error(f"Heartbeat loop error: {e}")
                
                await asyncio.sleep(self.heartbeat_interval)
                
        except asyncio.CancelledError:
            logger.info("Heartbeat loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Heartbeat loop error: {e}")
    
    async def _cleanup_loop(self):
        """Cleanup old heartbeats and metrics."""
        try:
            while self.is_running:
                try:
                    current_time = datetime.utcnow()
                    cleanup_age = timedelta(hours=1)
                    
                    # Clean up old heartbeats
                    expired_heartbeats = [
                        source_id for source_id, heartbeat in self.heartbeats.items()
                        if (current_time - heartbeat.timestamp) > cleanup_age
                    ]
                    
                    for source_id in expired_heartbeats:
                        del self.heartbeats[source_id]
                        if source_id in self.missed_heartbeats:
                            del self.missed_heartbeats[source_id]
                    
                    if expired_heartbeats:
                        logger.info(f"Cleaned up {len(expired_heartbeats)} old heartbeats")
                    
                except Exception as e:
                    logger.error(f"Cleanup loop error: {e}")
                
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
        except asyncio.CancelledError:
            logger.info("Cleanup loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Cleanup loop error: {e}")
    
    async def _check_alerts(self):
        """Check for alert conditions and trigger callbacks."""
        try:
            alerts = []
            
            for component_id, component in self.components.items():
                # Alert on status changes
                if component.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                    alerts.append({
                        "type": "component_unhealthy",
                        "component_id": component_id,
                        "status": component.status.value,
                        "message": component.message,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                # Alert on missed heartbeats
                missed_count = self.missed_heartbeats.get(component_id, 0)
                if missed_count > 3:  # Alert after 3 missed heartbeats
                    alerts.append({
                        "type": "heartbeat_timeout",
                        "component_id": component_id,
                        "missed_count": missed_count,
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            # Trigger alert callbacks
            for alert in alerts:
                await self._trigger_alert_callbacks(alert)
                self.metrics["alerts_sent"] += 1
                
        except Exception as e:
            logger.error(f"Alert check error: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """Add callback for health alerts."""
        self.alert_callbacks.append(callback)
    
    async def _trigger_alert_callbacks(self, alert: Dict[str, Any]):
        """Trigger alert callbacks."""
        for callback in self.alert_callbacks:
            try:
                result = callback(alert)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get health monitor metrics."""
        return {
            **self.metrics,
            "active_heartbeats": len(self.heartbeats),
            "total_missed_heartbeats": sum(self.missed_heartbeats.values()),
            "registered_checkers": len(self.health_checkers),
            "uptime": time.time() - self.start_time
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the monitor itself."""
        try:
            overall_health = await self.get_overall_health()
            
            return {
                "status": "healthy" if self.is_running else "stopped",
                "is_running": self.is_running,
                "overall_health": overall_health,
                "metrics": await self.get_metrics()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    # Context manager support
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()