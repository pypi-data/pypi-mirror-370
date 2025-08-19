"""
MAOS Monitoring System - Comprehensive monitoring and health check framework.

This package provides:
- Health check framework for all MAOS components
- Prometheus metrics collection and exposure
- Real-time monitoring dashboards
- Configurable alerting system
- Performance analytics and bottleneck detection
"""

from .health.health_manager import HealthManager
from .metrics.prometheus_collector import PrometheusCollector
from .alerts.alert_manager import AlertManager
from .dashboard.monitoring_dashboard import MonitoringDashboard

__version__ = "2.0.0"
__author__ = "MAOS Development Team"

__all__ = [
    "HealthManager",
    "PrometheusCollector", 
    "AlertManager",
    "MonitoringDashboard"
]