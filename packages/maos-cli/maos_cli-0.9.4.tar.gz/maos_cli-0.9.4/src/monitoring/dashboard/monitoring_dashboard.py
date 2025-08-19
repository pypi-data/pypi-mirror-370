"""
Real-time monitoring dashboard for MAOS system.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from uuid import uuid4

from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError


class MonitoringDashboard:
    """
    Real-time monitoring dashboard that aggregates data from health manager,
    metrics collector, and alert manager to provide comprehensive system visibility.
    """
    
    def __init__(
        self,
        update_interval: float = 5.0,
        history_retention_hours: int = 24
    ):
        """Initialize monitoring dashboard."""
        self.update_interval = update_interval
        self.history_retention_hours = history_retention_hours
        
        self.logger = MAOSLogger("monitoring_dashboard", str(uuid4()))
        
        # Component references
        self._health_manager = None
        self._metrics_collector = None
        self._alert_manager = None
        self._redis_manager = None
        
        # Dashboard state
        self._dashboard_data: Dict[str, Any] = {}
        self._last_update: Optional[datetime] = None
        
        # Real-time subscribers (WebSocket connections, etc.)
        self._subscribers: Set[Any] = set()
        
        # Background update task
        self._update_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Performance metrics
        self._update_times: List[float] = []
        self._max_update_times = 1000
        
        # Dashboard configuration
        self._config = {
            "refresh_rate_seconds": update_interval,
            "show_detailed_metrics": True,
            "show_agent_details": True,
            "show_task_queue": True,
            "show_performance_charts": True,
            "alert_severity_filter": ["critical", "high", "medium", "low"]
        }
    
    def register_health_manager(self, health_manager: Any) -> None:
        """Register health manager."""
        self._health_manager = health_manager
        self.logger.logger.info("Registered health manager for dashboard")
    
    def register_metrics_collector(self, metrics_collector: Any) -> None:
        """Register metrics collector."""
        self._metrics_collector = metrics_collector
        self.logger.logger.info("Registered metrics collector for dashboard")
    
    def register_alert_manager(self, alert_manager: Any) -> None:
        """Register alert manager."""
        self._alert_manager = alert_manager
        self.logger.logger.info("Registered alert manager for dashboard")
    
    def register_redis_manager(self, redis_manager: Any) -> None:
        """Register Redis manager."""
        self._redis_manager = redis_manager
        self.logger.logger.info("Registered Redis manager for dashboard")
    
    async def start(self) -> None:
        """Start dashboard data collection."""
        self.logger.logger.info("Starting monitoring dashboard")
        
        # Initial data collection
        await self._collect_dashboard_data()
        
        # Start background updates
        self._shutdown_event.clear()
        self._update_task = asyncio.create_task(self._update_loop())
    
    async def stop(self) -> None:
        """Stop dashboard."""
        self.logger.logger.info("Stopping monitoring dashboard")
        
        self._shutdown_event.set()
        
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        
        # Clear subscribers
        self._subscribers.clear()
    
    async def _update_loop(self) -> None:
        """Background update loop."""
        while not self._shutdown_event.is_set():
            try:
                start_time = asyncio.get_event_loop().time()
                
                # Collect latest data
                await self._collect_dashboard_data()
                
                # Track update performance
                update_time = asyncio.get_event_loop().time() - start_time
                self._update_times.append(update_time)
                if len(self._update_times) > self._max_update_times:
                    self._update_times.pop(0)
                
                # Notify subscribers
                await self._notify_subscribers()
                
                await asyncio.sleep(self.update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {"operation": "dashboard_update_loop"})
                await asyncio.sleep(self.update_interval)
    
    async def _collect_dashboard_data(self) -> None:
        """Collect all dashboard data."""
        try:
            dashboard_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "system_overview": await self._get_system_overview(),
                "health_status": await self._get_health_status(),
                "performance_metrics": await self._get_performance_metrics(),
                "agent_status": await self._get_agent_status(),
                "task_queue_status": await self._get_task_queue_status(),
                "alert_summary": await self._get_alert_summary(),
                "resource_usage": await self._get_resource_usage(),
                "storage_status": await self._get_storage_status(),
                "communication_status": await self._get_communication_status(),
                "recent_activity": await self._get_recent_activity()
            }
            
            self._dashboard_data = dashboard_data
            self._last_update = datetime.utcnow()
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "collect_dashboard_data"})
    
    async def _get_system_overview(self) -> Dict[str, Any]:
        """Get system overview data."""
        overview = {
            "status": "unknown",
            "uptime_seconds": 0,
            "version": "2.0.0",
            "components_total": 0,
            "components_healthy": 0,
            "active_alerts": 0,
            "critical_alerts": 0
        }
        
        try:
            # System health
            if self._health_manager:
                health_data = await self._health_manager.get_health_status()
                overview.update({
                    "status": health_data.get("system_status", "unknown"),
                    "components_total": health_data.get("summary", {}).get("total_components", 0),
                    "components_healthy": health_data.get("summary", {}).get("healthy", 0)
                })
            
            # Alert summary
            if self._alert_manager:
                alert_stats = self._alert_manager.get_alert_statistics()
                overview.update({
                    "active_alerts": alert_stats.get("active_alerts_count", 0),
                    "critical_alerts": alert_stats.get("active_alerts_by_severity", {}).get("critical", 0)
                })
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "get_system_overview"})
        
        return overview
    
    async def _get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status."""
        if not self._health_manager:
            return {"error": "Health manager not available"}
        
        try:
            return await self._health_manager.get_health_status()
        except Exception as e:
            self.logger.log_error(e, {"operation": "get_health_status"})
            return {"error": str(e)}
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        metrics = {
            "system_throughput": 0.0,
            "average_response_time": 0.0,
            "error_rate_percentage": 0.0,
            "cpu_usage_percentage": 0.0,
            "memory_usage_percentage": 0.0,
            "disk_usage_percentage": 0.0
        }
        
        try:
            # Get metrics from health manager
            if self._health_manager:
                health_metrics = self._health_manager.get_health_metrics()
                system_metrics = health_metrics.get("system_metrics", {})
                
                metrics.update({
                    "system_health_percentage": system_metrics.get("system_health_percentage", 0),
                    "average_check_duration_ms": system_metrics.get("average_check_duration_ms", 0)
                })
            
            # Get system resources
            try:
                import psutil
                metrics.update({
                    "cpu_usage_percentage": psutil.cpu_percent(),
                    "memory_usage_percentage": psutil.virtual_memory().percent,
                    "disk_usage_percentage": psutil.disk_usage('/').percent
                })
            except ImportError:
                pass
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "get_performance_metrics"})
        
        return metrics
    
    async def _get_agent_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        agent_status = {
            "total_agents": 0,
            "active_agents": 0,
            "idle_agents": 0,
            "failed_agents": 0,
            "agent_details": []
        }
        
        try:
            # This would integrate with the agent manager
            # For now, we'll get data from health status
            if self._health_manager:
                health_data = await self._health_manager.get_health_status()
                components = health_data.get("components", {})
                
                if "agent_manager" in components:
                    agent_info = components["agent_manager"]
                    details = agent_info.get("details", {})
                    
                    agent_status.update({
                        "total_agents": details.get("total_agents", 0),
                        "active_agents": details.get("active_agents", 0),
                        "idle_agents": details.get("idle_agents", 0),
                        "failed_agents": details.get("failed_agents", 0)
                    })
                    
                    # Agent details if available
                    agents_info = details.get("agents", {})
                    agent_details = []
                    for agent_id, info in agents_info.items():
                        agent_details.append({
                            "id": agent_id,
                            "status": info.get("status", "unknown"),
                            "last_activity": info.get("last_activity")
                        })
                    
                    agent_status["agent_details"] = agent_details[:10]  # Limit to 10 for dashboard
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "get_agent_status"})
        
        return agent_status
    
    async def _get_task_queue_status(self) -> Dict[str, Any]:
        """Get task queue status."""
        task_status = {
            "pending_tasks": 0,
            "active_tasks": 0,
            "completed_tasks_today": 0,
            "failed_tasks_today": 0,
            "average_task_duration_seconds": 0.0,
            "task_throughput_per_hour": 0.0
        }
        
        try:
            # This would integrate with the orchestrator
            # For now, we'll get basic info from health status
            if self._health_manager:
                health_data = await self._health_manager.get_health_status()
                components = health_data.get("components", {})
                
                if "orchestrator" in components:
                    orchestrator_info = components["orchestrator"]
                    details = orchestrator_info.get("details", {})
                    
                    task_status.update({
                        "pending_tasks": details.get("pending_tasks", 0),
                        "active_tasks": details.get("active_tasks", 0)
                    })
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "get_task_queue_status"})
        
        return task_status
    
    async def _get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary."""
        alert_summary = {
            "active_alerts": [],
            "recent_alerts": [],
            "alert_statistics": {},
            "top_alerting_components": []
        }
        
        try:
            if self._alert_manager:
                # Get active alerts
                active_alerts = self._alert_manager.get_active_alerts()
                alert_summary["active_alerts"] = [
                    alert.to_dict() for alert in active_alerts[:10]  # Limit for dashboard
                ]
                
                # Get recent alerts
                recent_alerts = self._alert_manager.get_alert_history(hours=24)
                alert_summary["recent_alerts"] = [
                    alert.to_dict() for alert in recent_alerts[-10:]  # Last 10
                ]
                
                # Get statistics
                alert_summary["alert_statistics"] = self._alert_manager.get_alert_statistics()
                
                # Top alerting components
                component_counts = {}
                for alert in recent_alerts:
                    component = alert.component
                    component_counts[component] = component_counts.get(component, 0) + 1
                
                top_components = sorted(
                    component_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
                
                alert_summary["top_alerting_components"] = [
                    {"component": comp, "alert_count": count}
                    for comp, count in top_components
                ]
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "get_alert_summary"})
        
        return alert_summary
    
    async def _get_resource_usage(self) -> Dict[str, Any]:
        """Get system resource usage."""
        resource_usage = {
            "cpu": {"percentage": 0, "cores": 0},
            "memory": {"used_bytes": 0, "total_bytes": 0, "percentage": 0},
            "disk": {"used_bytes": 0, "total_bytes": 0, "percentage": 0},
            "network": {"bytes_sent": 0, "bytes_received": 0}
        }
        
        try:
            import psutil
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            resource_usage["cpu"] = {
                "percentage": cpu_percent,
                "cores": psutil.cpu_count()
            }
            
            # Memory
            memory = psutil.virtual_memory()
            resource_usage["memory"] = {
                "used_bytes": memory.used,
                "total_bytes": memory.total,
                "percentage": memory.percent
            }
            
            # Disk
            disk = psutil.disk_usage('/')
            resource_usage["disk"] = {
                "used_bytes": disk.used,
                "total_bytes": disk.total,
                "percentage": (disk.used / disk.total) * 100
            }
            
            # Network
            network = psutil.net_io_counters()
            if network:
                resource_usage["network"] = {
                    "bytes_sent": network.bytes_sent,
                    "bytes_received": network.bytes_recv
                }
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "get_resource_usage"})
        
        return resource_usage
    
    async def _get_storage_status(self) -> Dict[str, Any]:
        """Get storage system status."""
        storage_status = {
            "redis_status": "unknown",
            "redis_memory_usage": 0,
            "redis_connected_clients": 0,
            "redis_operations_per_second": 0,
            "redis_hit_rate_percentage": 0
        }
        
        try:
            if self._health_manager:
                health_data = await self._health_manager.get_health_status()
                components = health_data.get("components", {})
                
                if "storage" in components:
                    storage_info = components["storage"]
                    storage_status["redis_status"] = storage_info.get("status", "unknown")
                    
                    details = storage_info.get("details", {})
                    storage_status.update({
                        "redis_memory_usage": details.get("memory_usage_bytes", 0),
                        "redis_connected_clients": details.get("connected_clients", 0),
                        "redis_operations_per_second": details.get("operations_per_second", 0),
                        "redis_hit_rate_percentage": details.get("hit_rate_percentage", 0)
                    })
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "get_storage_status"})
        
        return storage_status
    
    async def _get_communication_status(self) -> Dict[str, Any]:
        """Get communication system status."""
        communication_status = {
            "message_bus_status": "unknown",
            "pending_messages": 0,
            "processed_messages": 0,
            "failed_messages": 0,
            "subscriber_count": 0,
            "error_rate_percentage": 0
        }
        
        try:
            if self._health_manager:
                health_data = await self._health_manager.get_health_status()
                components = health_data.get("components", {})
                
                if "communication" in components:
                    comm_info = components["communication"]
                    communication_status["message_bus_status"] = comm_info.get("status", "unknown")
                    
                    details = comm_info.get("details", {})
                    processed = details.get("processed_messages", 0)
                    failed = details.get("failed_messages", 0)
                    total = processed + failed
                    error_rate = (failed / total * 100) if total > 0 else 0
                    
                    communication_status.update({
                        "pending_messages": details.get("pending_messages", 0),
                        "processed_messages": processed,
                        "failed_messages": failed,
                        "subscriber_count": details.get("subscriber_count", 0),
                        "error_rate_percentage": error_rate
                    })
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "get_communication_status"})
        
        return communication_status
    
    async def _get_recent_activity(self) -> Dict[str, Any]:
        """Get recent system activity."""
        activity = {
            "recent_events": [],
            "activity_timeline": []
        }
        
        try:
            # This would integrate with system event logs
            # For now, we'll create a basic activity feed from available data
            events = []
            
            # Add health status changes
            if self._health_manager:
                # This would require the health manager to track status changes
                pass
            
            # Add recent alerts
            if self._alert_manager:
                recent_alerts = self._alert_manager.get_alert_history(hours=1)
                for alert in recent_alerts[-5:]:  # Last 5 alerts
                    events.append({
                        "timestamp": alert.created_at.isoformat(),
                        "type": "alert",
                        "severity": alert.severity.value,
                        "message": f"Alert fired: {alert.name} on {alert.component}",
                        "details": {
                            "component": alert.component,
                            "alert_name": alert.name
                        }
                    })
            
            # Sort events by timestamp
            events.sort(key=lambda x: x["timestamp"], reverse=True)
            activity["recent_events"] = events[:20]  # Limit to 20 events
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "get_recent_activity"})
        
        return activity
    
    async def _notify_subscribers(self) -> None:
        """Notify all subscribers of dashboard updates."""
        if not self._subscribers:
            return
        
        try:
            # This would send updates to WebSocket connections or other subscribers
            message = {
                "type": "dashboard_update",
                "data": self._dashboard_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # In a real implementation, you would send this to WebSocket connections
            self.logger.logger.debug(f"Notifying {len(self._subscribers)} dashboard subscribers")
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "notify_subscribers"})
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data."""
        return self._dashboard_data.copy()
    
    def get_dashboard_config(self) -> Dict[str, Any]:
        """Get dashboard configuration."""
        return self._config.copy()
    
    def update_dashboard_config(self, config: Dict[str, Any]) -> None:
        """Update dashboard configuration."""
        self._config.update(config)
        self.logger.logger.info("Dashboard configuration updated")
    
    def add_subscriber(self, subscriber: Any) -> None:
        """Add dashboard subscriber."""
        self._subscribers.add(subscriber)
    
    def remove_subscriber(self, subscriber: Any) -> None:
        """Remove dashboard subscriber."""
        self._subscribers.discard(subscriber)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get dashboard performance statistics."""
        if not self._update_times:
            return {"error": "No performance data available"}
        
        return {
            "average_update_time_seconds": sum(self._update_times) / len(self._update_times),
            "max_update_time_seconds": max(self._update_times),
            "min_update_time_seconds": min(self._update_times),
            "total_updates": len(self._update_times),
            "last_update": self._last_update.isoformat() if self._last_update else None,
            "subscriber_count": len(self._subscribers),
            "update_interval_seconds": self.update_interval
        }