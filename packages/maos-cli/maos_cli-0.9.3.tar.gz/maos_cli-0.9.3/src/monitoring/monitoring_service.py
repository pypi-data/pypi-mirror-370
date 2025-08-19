"""
Main monitoring service that coordinates all monitoring components.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from prometheus_client import make_asgi_app

from ..maos.utils.logging_config import MAOSLogger
from ..maos.utils.exceptions import MAOSError

from .health.health_manager import HealthManager
from .health.component_checkers import (
    OrchestratorHealthChecker,
    AgentHealthChecker,
    CommunicationHealthChecker,
    StorageHealthChecker,
    DependencyHealthChecker
)
from .health.health_api import create_health_router
from .metrics.prometheus_collector import PrometheusCollector
from .alerts.alert_manager import AlertManager
from .alerts.notification_channels import (
    EmailNotificationChannel,
    SlackNotificationChannel,
    WebhookNotificationChannel
)
from .dashboard.monitoring_dashboard import MonitoringDashboard


class MonitoringService:
    """
    Central monitoring service that coordinates health checks, metrics collection,
    alerting, and dashboard functionality.
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        health_check_interval: float = 30.0,
        metrics_collection_interval: float = 15.0,
        alert_evaluation_interval: float = 30.0,
        dashboard_update_interval: float = 5.0
    ):
        """Initialize monitoring service."""
        self.config = config or {}
        
        self.logger = MAOSLogger("monitoring_service", str(uuid4()))
        
        # Initialize core components
        self.health_manager = HealthManager(check_interval=health_check_interval)
        self.metrics_collector = PrometheusCollector(collection_interval=metrics_collection_interval)
        self.alert_manager = AlertManager(evaluation_interval=alert_evaluation_interval)
        self.dashboard = MonitoringDashboard(update_interval=dashboard_update_interval)
        
        # Component registry
        self._registered_components: Dict[str, Any] = {}
        
        # Service state
        self._running = False
        self._startup_time: Optional[datetime] = None
        
        # FastAPI app for REST endpoints
        self._app: Optional[FastAPI] = None
    
    async def initialize(
        self,
        orchestrator=None,
        agent_manager=None,
        message_bus=None,
        redis_manager=None,
        external_dependencies: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> None:
        """
        Initialize monitoring service with MAOS components.
        
        Args:
            orchestrator: MAOS orchestrator instance
            agent_manager: Agent manager instance
            message_bus: Message bus instance
            redis_manager: Redis state manager instance
            external_dependencies: External dependency configurations
        """
        self.logger.logger.info("Initializing MAOS monitoring service")
        
        try:
            # Register components
            if orchestrator:
                await self._register_orchestrator(orchestrator)
            
            if agent_manager:
                await self._register_agent_manager(agent_manager)
            
            if message_bus:
                await self._register_message_bus(message_bus)
            
            if redis_manager:
                await self._register_redis_manager(redis_manager)
            
            if external_dependencies:
                await self._register_external_dependencies(external_dependencies)
            
            # Setup component integrations
            await self._setup_integrations()
            
            # Configure alerts
            await self._setup_default_alerts()
            
            # Configure notification channels
            await self._setup_notification_channels()
            
            self.logger.logger.info("Monitoring service initialized successfully")
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "initialize"})
            raise MAOSError(f"Failed to initialize monitoring service: {str(e)}")
    
    async def start(self) -> None:
        """Start all monitoring components."""
        if self._running:
            self.logger.logger.warning("Monitoring service already running")
            return
        
        self.logger.logger.info("Starting MAOS monitoring service")
        
        try:
            # Start health monitoring
            await self.health_manager.start_monitoring()
            
            # Start metrics collection
            await self.metrics_collector.start_collection()
            
            # Start alert evaluation
            await self.alert_manager.start_evaluation()
            
            # Start dashboard
            await self.dashboard.start()
            
            self._running = True
            self._startup_time = datetime.utcnow()
            
            self.logger.logger.info("Monitoring service started successfully")
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "start"})
            raise MAOSError(f"Failed to start monitoring service: {str(e)}")
    
    async def stop(self) -> None:
        """Stop all monitoring components."""
        if not self._running:
            return
        
        self.logger.logger.info("Stopping MAOS monitoring service")
        
        try:
            # Stop components in reverse order
            await self.dashboard.stop()
            await self.alert_manager.stop_evaluation()
            await self.metrics_collector.stop_collection()
            await self.health_manager.stop_monitoring()
            
            self._running = False
            
            self.logger.logger.info("Monitoring service stopped successfully")
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "stop"})
    
    def create_fastapi_app(self) -> FastAPI:
        """Create FastAPI application with monitoring endpoints."""
        if self._app:
            return self._app
        
        app = FastAPI(
            title="MAOS Monitoring API",
            description="Comprehensive monitoring and health check API for MAOS",
            version="2.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add health check routes
        health_router = create_health_router(self.health_manager)
        app.include_router(health_router)
        
        # Add Prometheus metrics endpoint
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)
        
        # Add monitoring service info endpoints
        @app.get("/info")
        async def get_service_info():
            """Get monitoring service information."""
            return {
                "service": "maos-monitoring",
                "version": "2.0.0",
                "status": "running" if self._running else "stopped",
                "startup_time": self._startup_time.isoformat() if self._startup_time else None,
                "uptime_seconds": (datetime.utcnow() - self._startup_time).total_seconds() if self._startup_time else 0,
                "registered_components": list(self._registered_components.keys()),
                "endpoints": {
                    "health": "/health/",
                    "metrics": "/metrics",
                    "alerts": "/alerts/",
                    "dashboard": "/dashboard/"
                }
            }
        
        # Alert management endpoints
        @app.get("/alerts/")
        async def get_alerts(severity: Optional[str] = None):
            """Get active alerts."""
            try:
                from .alerts.alert_manager import AlertSeverity
                
                severity_filter = None
                if severity:
                    severity_filter = AlertSeverity(severity.lower())
                
                alerts = self.alert_manager.get_active_alerts(severity_filter)
                return {
                    "alerts": [alert.to_dict() for alert in alerts],
                    "total_count": len(alerts),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/alerts/{alert_id}/acknowledge")
        async def acknowledge_alert(alert_id: str, user: Optional[str] = None):
            """Acknowledge an alert."""
            try:
                success = await self.alert_manager.acknowledge_alert(alert_id, user)
                if success:
                    return {"message": "Alert acknowledged successfully"}
                else:
                    raise HTTPException(status_code=404, detail="Alert not found")
                    
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/alerts/statistics")
        async def get_alert_statistics():
            """Get alert statistics."""
            try:
                return self.alert_manager.get_alert_statistics()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Dashboard endpoints
        @app.get("/dashboard/")
        async def get_dashboard_data():
            """Get current dashboard data."""
            try:
                return self.dashboard.get_dashboard_data()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/dashboard/config")
        async def get_dashboard_config():
            """Get dashboard configuration."""
            try:
                return self.dashboard.get_dashboard_config()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.put("/dashboard/config")
        async def update_dashboard_config(config: Dict[str, Any]):
            """Update dashboard configuration."""
            try:
                self.dashboard.update_dashboard_config(config)
                return {"message": "Dashboard configuration updated"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        self._app = app
        return app
    
    async def _register_orchestrator(self, orchestrator) -> None:
        """Register orchestrator for monitoring."""
        self._registered_components["orchestrator"] = orchestrator
        
        # Create health checker
        health_checker = OrchestratorHealthChecker(orchestrator)
        self.health_manager.register_checker(health_checker)
        
        # Register with metrics collector
        self.metrics_collector.register_component("orchestrator", orchestrator)
        
        self.logger.logger.info("Registered orchestrator for monitoring")
    
    async def _register_agent_manager(self, agent_manager) -> None:
        """Register agent manager for monitoring."""
        self._registered_components["agent_manager"] = agent_manager
        
        # Create health checker
        health_checker = AgentHealthChecker(agent_manager)
        self.health_manager.register_checker(health_checker)
        
        # Register with metrics collector
        self.metrics_collector.register_component("agent_manager", agent_manager)
        
        self.logger.logger.info("Registered agent manager for monitoring")
    
    async def _register_message_bus(self, message_bus) -> None:
        """Register message bus for monitoring."""
        self._registered_components["message_bus"] = message_bus
        
        # Create health checker
        health_checker = CommunicationHealthChecker(message_bus)
        self.health_manager.register_checker(health_checker)
        
        # Register with metrics collector
        self.metrics_collector.register_component("message_bus", message_bus)
        
        self.logger.logger.info("Registered message bus for monitoring")
    
    async def _register_redis_manager(self, redis_manager) -> None:
        """Register Redis manager for monitoring."""
        self._registered_components["redis_manager"] = redis_manager
        
        # Create health checker
        health_checker = StorageHealthChecker(redis_manager)
        self.health_manager.register_checker(health_checker)
        
        # Register with metrics collector
        self.metrics_collector.register_component("redis_manager", redis_manager)
        
        self.logger.logger.info("Registered Redis manager for monitoring")
    
    async def _register_external_dependencies(self, dependencies: Dict[str, Dict[str, Any]]) -> None:
        """Register external dependencies for monitoring."""
        # Create dependency health checker
        health_checker = DependencyHealthChecker(dependencies)
        self.health_manager.register_checker(health_checker)
        
        self.logger.logger.info(f"Registered {len(dependencies)} external dependencies for monitoring")
    
    async def _setup_integrations(self) -> None:
        """Setup integrations between monitoring components."""
        # Register health manager with metrics collector
        self.metrics_collector.register_component("health_manager", self.health_manager)
        
        # Register metrics collector with alert manager
        self.alert_manager.register_metrics_collector(self.metrics_collector)
        self.alert_manager.register_health_manager(self.health_manager)
        
        # Register components with dashboard
        self.dashboard.register_health_manager(self.health_manager)
        self.dashboard.register_metrics_collector(self.metrics_collector)
        self.dashboard.register_alert_manager(self.alert_manager)
        
        if "redis_manager" in self._registered_components:
            self.dashboard.register_redis_manager(self._registered_components["redis_manager"])
    
    async def _setup_default_alerts(self) -> None:
        """Setup default alert rules."""
        from .alerts.alert_manager import AlertRule, AlertSeverity
        
        # System health alerts
        self.alert_manager.add_alert_rule(AlertRule(
            name="system_unhealthy",
            description="System health status is unhealthy",
            metric_name="system_health_percentage",
            condition="lt",
            threshold=50.0,
            severity=AlertSeverity.CRITICAL,
            component="system"
        ))
        
        # High CPU usage alert
        self.alert_manager.add_alert_rule(AlertRule(
            name="high_cpu_usage",
            description="CPU usage is high",
            metric_name="cpu_usage_percentage",
            condition="gt",
            threshold=80.0,
            severity=AlertSeverity.HIGH,
            component="system"
        ))
        
        # High memory usage alert
        self.alert_manager.add_alert_rule(AlertRule(
            name="high_memory_usage",
            description="Memory usage is high",
            metric_name="memory_usage_percentage", 
            condition="gt",
            threshold=85.0,
            severity=AlertSeverity.HIGH,
            component="system"
        ))
        
        # Redis memory usage alert
        self.alert_manager.add_alert_rule(AlertRule(
            name="redis_memory_high",
            description="Redis memory usage is high",
            metric_name="redis_memory_usage_percentage",
            condition="gt",
            threshold=90.0,
            severity=AlertSeverity.HIGH,
            component="storage"
        ))
        
        # Low cache hit rate alert
        self.alert_manager.add_alert_rule(AlertRule(
            name="low_cache_hit_rate",
            description="Redis cache hit rate is low",
            metric_name="redis_hit_rate_percentage",
            condition="lt",
            threshold=70.0,
            severity=AlertSeverity.MEDIUM,
            component="storage"
        ))
        
        self.logger.logger.info("Default alert rules configured")
    
    async def _setup_notification_channels(self) -> None:
        """Setup notification channels from configuration."""
        notifications_config = self.config.get("notifications", {})
        
        # Email notifications
        if "email" in notifications_config:
            email_config = notifications_config["email"]
            email_channel = EmailNotificationChannel(email_config)
            self.alert_manager.add_notification_channel(email_channel)
            self.logger.logger.info("Email notification channel configured")
        
        # Slack notifications  
        if "slack" in notifications_config:
            slack_config = notifications_config["slack"]
            slack_channel = SlackNotificationChannel(slack_config)
            self.alert_manager.add_notification_channel(slack_channel)
            self.logger.logger.info("Slack notification channel configured")
        
        # Webhook notifications
        if "webhook" in notifications_config:
            webhook_config = notifications_config["webhook"]
            webhook_channel = WebhookNotificationChannel(webhook_config)
            self.alert_manager.add_notification_channel(webhook_channel)
            self.logger.logger.info("Webhook notification channel configured")
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitoring service status."""
        return {
            "service_running": self._running,
            "startup_time": self._startup_time.isoformat() if self._startup_time else None,
            "uptime_seconds": (datetime.utcnow() - self._startup_time).total_seconds() if self._startup_time else 0,
            "registered_components": list(self._registered_components.keys()),
            "health_manager": {
                "registered_checkers": self.health_manager.get_registered_components(),
                "system_status": "running" if self._running else "stopped"
            },
            "metrics_collector": {
                "collection_interval": self.metrics_collector.collection_interval,
                "registered_components": len(self.metrics_collector._collectors)
            },
            "alert_manager": {
                "active_alerts": len(self.alert_manager._active_alerts),
                "alert_rules": len(self.alert_manager._alert_rules),
                "notification_channels": len(self.alert_manager._notification_channels)
            },
            "dashboard": {
                "update_interval": self.dashboard.update_interval,
                "subscribers": len(self.dashboard._subscribers)
            }
        }