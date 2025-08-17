"""
Health Manager - Centralized health monitoring for all MAOS components.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from uuid import uuid4

from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError
from .health_checker import HealthChecker, ComponentHealth, HealthStatus


class HealthManager:
    """
    Centralized health management system for MAOS.
    
    Manages health checkers for all components and provides aggregate health status,
    dependency validation, and health reporting.
    """
    
    def __init__(self, check_interval: float = 30.0):
        """Initialize health manager."""
        self.check_interval = check_interval
        self.logger = MAOSLogger("health_manager", str(uuid4()))
        
        # Health checkers registry
        self._checkers: Dict[str, HealthChecker] = {}
        
        # Current health state
        self._current_health: Dict[str, ComponentHealth] = {}
        
        # Overall system status
        self._system_status: HealthStatus = HealthStatus.UNKNOWN
        self._system_message: str = "Health manager initializing"
        
        # Health history for analysis
        self._health_history: List[Dict[str, Any]] = []
        self._max_history = 1000
        
        # Background monitoring
        self._monitor_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Dependency graph
        self._dependency_graph: Dict[str, Set[str]] = {}
        
        # Alert callbacks
        self._alert_callbacks: List = []
    
    def register_checker(self, checker: HealthChecker) -> None:
        """Register a health checker."""
        self.logger.logger.info(f"Registering health checker: {checker.component_name}")
        
        self._checkers[checker.component_name] = checker
        
        # Build dependency graph
        self._dependency_graph[checker.component_name] = set(checker.dependencies)
        
        # Add status change callback
        checker.add_status_change_callback(self._on_component_status_change)
    
    def unregister_checker(self, component_name: str) -> None:
        """Unregister a health checker."""
        if component_name in self._checkers:
            checker = self._checkers[component_name]
            checker.remove_status_change_callback(self._on_component_status_change)
            del self._checkers[component_name]
            
            if component_name in self._dependency_graph:
                del self._dependency_graph[component_name]
            
            self.logger.logger.info(f"Unregistered health checker: {component_name}")
    
    async def start_monitoring(self) -> None:
        """Start health monitoring for all registered checkers."""
        self.logger.logger.info("Starting health monitoring system")
        
        # Start all health checkers
        for checker in self._checkers.values():
            await checker.start_monitoring()
        
        # Start aggregate monitoring
        self._shutdown_event.clear()
        self._monitor_task = asyncio.create_task(self._aggregate_monitoring_loop())
    
    async def stop_monitoring(self) -> None:
        """Stop health monitoring."""
        self.logger.logger.info("Stopping health monitoring system")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Stop aggregate monitoring
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        # Stop all health checkers
        for checker in self._checkers.values():
            await checker.stop_monitoring()
    
    async def _aggregate_monitoring_loop(self) -> None:
        """Aggregate monitoring loop."""
        while not self._shutdown_event.is_set():
            try:
                # Collect health from all checkers
                await self._collect_health_status()
                
                # Update system status
                await self._update_system_status()
                
                # Store health snapshot
                self._store_health_snapshot()
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {"operation": "aggregate_monitoring_loop"})
                await asyncio.sleep(self.check_interval)
    
    async def _collect_health_status(self) -> None:
        """Collect current health status from all checkers."""
        for component_name, checker in self._checkers.items():
            current_health = checker.get_current_health()
            if current_health:
                self._current_health[component_name] = current_health
    
    async def _update_system_status(self) -> None:
        """Update overall system health status."""
        if not self._current_health:
            self._system_status = HealthStatus.UNKNOWN
            self._system_message = "No health data available"
            return
        
        # Count components by status
        status_counts = {status: 0 for status in HealthStatus}
        for health in self._current_health.values():
            status_counts[health.status] += 1
        
        total_components = len(self._current_health)
        
        # Determine overall status
        if status_counts[HealthStatus.UNHEALTHY] > 0:
            self._system_status = HealthStatus.UNHEALTHY
            self._system_message = f"{status_counts[HealthStatus.UNHEALTHY]} of {total_components} components are unhealthy"
        elif status_counts[HealthStatus.DEGRADED] > 0:
            self._system_status = HealthStatus.DEGRADED
            self._system_message = f"{status_counts[HealthStatus.DEGRADED]} of {total_components} components are degraded"
        elif status_counts[HealthStatus.HEALTHY] == total_components:
            self._system_status = HealthStatus.HEALTHY
            self._system_message = f"All {total_components} components are healthy"
        else:
            self._system_status = HealthStatus.UNKNOWN
            self._system_message = "System health status unknown"
    
    def _store_health_snapshot(self) -> None:
        """Store current health snapshot in history."""
        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_status": self._system_status.value,
            "system_message": self._system_message,
            "components": {
                name: health.to_dict()
                for name, health in self._current_health.items()
            }
        }
        
        self._health_history.append(snapshot)
        
        # Limit history size
        if len(self._health_history) > self._max_history:
            self._health_history.pop(0)
    
    def _on_component_status_change(self, health: ComponentHealth) -> None:
        """Handle component status change."""
        old_health = self._current_health.get(health.component_name)
        
        if old_health and old_health.status != health.status:
            self.logger.logger.info(
                f"Component status changed: {health.component_name}",
                extra={
                    "component": health.component_name,
                    "old_status": old_health.status.value,
                    "new_status": health.status.value,
                    "message": health.message
                }
            )
            
            # Trigger alert callbacks
            for callback in self._alert_callbacks:
                try:
                    callback({
                        "type": "component_status_change",
                        "component": health.component_name,
                        "old_status": old_health.status.value,
                        "new_status": health.status.value,
                        "health": health.to_dict(),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    self.logger.log_error(e, {"operation": "alert_callback"})
    
    async def get_health_status(self, component: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current health status.
        
        Args:
            component: Specific component name, or None for all components
            
        Returns:
            Health status information
        """
        if component:
            if component not in self._current_health:
                raise MAOSError(f"Component not found: {component}")
            
            return {
                "component": component,
                "health": self._current_health[component].to_dict(),
                "dependencies": list(self._dependency_graph.get(component, []))
            }
        
        # Return full system health
        return {
            "system_status": self._system_status.value,
            "system_message": self._system_message,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                name: health.to_dict()
                for name, health in self._current_health.items()
            },
            "summary": {
                "total_components": len(self._current_health),
                "healthy": sum(1 for h in self._current_health.values() if h.is_healthy()),
                "degraded": sum(1 for h in self._current_health.values() if h.is_degraded()),
                "unhealthy": sum(1 for h in self._current_health.values() if h.is_unhealthy())
            }
        }
    
    async def get_dependency_status(self, component: str) -> Dict[str, Any]:
        """Get dependency health status for a component."""
        if component not in self._dependency_graph:
            raise MAOSError(f"Component not found: {component}")
        
        dependencies = self._dependency_graph[component]
        dependency_status = {}
        
        for dep in dependencies:
            if dep in self._current_health:
                dependency_status[dep] = self._current_health[dep].to_dict()
            else:
                dependency_status[dep] = {
                    "status": "unknown",
                    "message": "Dependency not monitored"
                }
        
        # Check if all dependencies are healthy
        all_healthy = all(
            self._current_health.get(dep, ComponentHealth("", HealthStatus.UNKNOWN, "")).is_healthy()
            for dep in dependencies
        )
        
        return {
            "component": component,
            "dependencies": dependency_status,
            "all_dependencies_healthy": all_healthy,
            "dependency_count": len(dependencies)
        }
    
    async def perform_health_check(self, component: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform immediate health check.
        
        Args:
            component: Specific component to check, or None for all
            
        Returns:
            Health check results
        """
        if component:
            if component not in self._checkers:
                raise MAOSError(f"Health checker not found: {component}")
            
            checker = self._checkers[component]
            health = await checker.perform_health_check()
            self._current_health[component] = health
            
            return {
                "component": component,
                "health": health.to_dict()
            }
        
        # Check all components
        results = {}
        for name, checker in self._checkers.items():
            health = await checker.perform_health_check()
            self._current_health[name] = health
            results[name] = health.to_dict()
        
        await self._update_system_status()
        
        return {
            "system_status": self._system_status.value,
            "system_message": self._system_message,
            "components": results
        }
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get aggregated health metrics."""
        if not self._current_health:
            return {"error": "No health data available"}
        
        # Aggregate metrics from all components
        all_metrics = {}
        for component, health in self._current_health.items():
            for metric_name, value in health.metrics.items():
                key = f"{component}_{metric_name}"
                all_metrics[key] = value
        
        # System-level metrics
        system_metrics = {
            "total_components": len(self._current_health),
            "healthy_components": sum(1 for h in self._current_health.values() if h.is_healthy()),
            "degraded_components": sum(1 for h in self._current_health.values() if h.is_degraded()),
            "unhealthy_components": sum(1 for h in self._current_health.values() if h.is_unhealthy()),
            "average_check_duration_ms": sum(h.check_duration_ms for h in self._current_health.values()) / len(self._current_health)
        }
        
        # Calculate overall health percentage
        total = len(self._current_health)
        healthy = system_metrics["healthy_components"]
        system_metrics["system_health_percentage"] = (healthy / total * 100) if total > 0 else 0
        
        return {
            "system_metrics": system_metrics,
            "component_metrics": all_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_health_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get health history for specified period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            snapshot for snapshot in self._health_history
            if datetime.fromisoformat(snapshot["timestamp"]) > cutoff_time
        ]
    
    def add_alert_callback(self, callback) -> None:
        """Add callback for health alerts."""
        self._alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback) -> None:
        """Remove alert callback."""
        if callback in self._alert_callbacks:
            self._alert_callbacks.remove(callback)
    
    def get_registered_components(self) -> List[str]:
        """Get list of registered component names."""
        return list(self._checkers.keys())
    
    async def export_health_report(self, hours: int = 24) -> str:
        """Export comprehensive health report."""
        history = self.get_health_history(hours)
        current_status = await self.get_health_status()
        metrics = self.get_health_metrics()
        
        report = {
            "export_info": {
                "generated_at": datetime.utcnow().isoformat(),
                "time_range_hours": hours,
                "data_points": len(history)
            },
            "current_status": current_status,
            "metrics": metrics,
            "history": history,
            "registered_components": self.get_registered_components()
        }
        
        return json.dumps(report, indent=2, default=str)