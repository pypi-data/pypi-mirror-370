"""
Grafana dashboard integration for MAOS monitoring.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from ...maos.utils.logging_config import MAOSLogger


class GrafanaDashboardExporter:
    """
    Exports MAOS monitoring data as Grafana dashboard configurations.
    """
    
    def __init__(self):
        """Initialize Grafana dashboard exporter."""
        self.logger = MAOSLogger("grafana_exporter", str(uuid4()))
        
        # Dashboard templates
        self._dashboard_templates = {
            "system_overview": self._create_system_overview_dashboard,
            "health_monitoring": self._create_health_monitoring_dashboard,
            "performance_metrics": self._create_performance_dashboard,
            "alert_management": self._create_alert_dashboard,
            "agent_monitoring": self._create_agent_dashboard,
            "storage_monitoring": self._create_storage_dashboard
        }
    
    def generate_dashboard_config(self, dashboard_type: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate Grafana dashboard configuration.
        
        Args:
            dashboard_type: Type of dashboard to generate
            config: Additional configuration options
            
        Returns:
            Grafana dashboard JSON configuration
        """
        if dashboard_type not in self._dashboard_templates:
            raise ValueError(f"Unknown dashboard type: {dashboard_type}")
        
        config = config or {}
        template_func = self._dashboard_templates[dashboard_type]
        
        try:
            dashboard_config = template_func(config)
            self.logger.logger.info(f"Generated Grafana dashboard: {dashboard_type}")
            return dashboard_config
            
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "generate_dashboard_config",
                "dashboard_type": dashboard_type
            })
            raise
    
    def generate_all_dashboards(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, Any]]:
        """Generate all available dashboard configurations."""
        dashboards = {}
        
        for dashboard_type in self._dashboard_templates.keys():
            try:
                dashboards[dashboard_type] = self.generate_dashboard_config(dashboard_type, config)
            except Exception as e:
                self.logger.log_error(e, {
                    "operation": "generate_all_dashboards",
                    "dashboard_type": dashboard_type
                })
        
        return dashboards
    
    def _create_system_overview_dashboard(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create system overview dashboard."""
        return {
            "dashboard": {
                "id": None,
                "title": "MAOS - System Overview",
                "description": "High-level overview of MAOS system health and performance",
                "tags": ["maos", "overview", "system"],
                "timezone": "utc",
                "editable": True,
                "graphTooltip": 1,
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "refresh": "30s",
                "panels": [
                    {
                        "id": 1,
                        "title": "System Health Status",
                        "type": "stat",
                        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
                        "targets": [
                            {
                                "expr": "maos_system_health_status",
                                "legendFormat": "System Health",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "mappings": [
                                    {"options": {"0": {"text": "Unhealthy", "color": "red"}}}
                                    {"options": {"1": {"text": "Degraded", "color": "yellow"}}}
                                    {"options": {"2": {"text": "Healthy", "color": "green"}}}
                                ],
                                "thresholds": {
                                    "steps": [
                                        {"color": "red", "value": 0},
                                        {"color": "yellow", "value": 1},
                                        {"color": "green", "value": 2}
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "id": 2,
                        "title": "Active Alerts",
                        "type": "stat",
                        "gridPos": {"h": 4, "w": 3, "x": 6, "y": 0},
                        "targets": [
                            {
                                "expr": "sum(maos_alert_active_count)",
                                "legendFormat": "Active Alerts",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "thresholds"},
                                "thresholds": {
                                    "steps": [
                                        {"color": "green", "value": 0},
                                        {"color": "yellow", "value": 5},
                                        {"color": "red", "value": 10}
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "id": 3,
                        "title": "Component Health",
                        "type": "bargauge",
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                        "targets": [
                            {
                                "expr": "maos_component_health_status",
                                "legendFormat": "{{component}}",
                                "refId": "A"
                            }
                        ]
                    },
                    {
                        "id": 4,
                        "title": "System Throughput",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                        "targets": [
                            {
                                "expr": "rate(maos_tasks_total[5m])",
                                "legendFormat": "Tasks/sec",
                                "refId": "A"
                            }
                        ],
                        "yAxes": [
                            {"label": "Tasks per second", "min": 0}
                        ]
                    },
                    {
                        "id": 5,
                        "title": "Resource Usage",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                        "targets": [
                            {
                                "expr": "maos_cpu_usage_percentage",
                                "legendFormat": "CPU %",
                                "refId": "A"
                            },
                            {
                                "expr": "maos_memory_usage_bytes / 1024 / 1024",
                                "legendFormat": "Memory MB",
                                "refId": "B"
                            }
                        ],
                        "yAxes": [
                            {"label": "Percentage / MB", "min": 0}
                        ]
                    }
                ]
            }
        }
    
    def _create_health_monitoring_dashboard(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create health monitoring dashboard."""
        return {
            "dashboard": {
                "id": None,
                "title": "MAOS - Health Monitoring",
                "description": "Detailed health monitoring for all MAOS components",
                "tags": ["maos", "health", "monitoring"],
                "timezone": "utc",
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "15s",
                "panels": [
                    {
                        "id": 1,
                        "title": "Component Health Status",
                        "type": "table",
                        "gridPos": {"h": 12, "w": 24, "x": 0, "y": 0},
                        "targets": [
                            {
                                "expr": "maos_component_health_status",
                                "legendFormat": "{{component}}",
                                "refId": "A",
                                "format": "table"
                            }
                        ]
                    },
                    {
                        "id": 2,
                        "title": "Health Check Duration",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 12},
                        "targets": [
                            {
                                "expr": "maos_health_check_duration_seconds",
                                "legendFormat": "{{component}}",
                                "refId": "A"
                            }
                        ]
                    },
                    {
                        "id": 3,
                        "title": "System Availability",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 12},
                        "targets": [
                            {
                                "expr": "maos_availability_percentage",
                                "legendFormat": "{{component}}",
                                "refId": "A"
                            }
                        ],
                        "yAxes": [
                            {"label": "Availability %", "min": 0, "max": 100}
                        ]
                    }
                ]
            }
        }
    
    def _create_performance_dashboard(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create performance metrics dashboard."""
        return {
            "dashboard": {
                "id": None,
                "title": "MAOS - Performance Metrics",
                "description": "System performance and resource utilization metrics",
                "tags": ["maos", "performance", "metrics"],
                "timezone": "utc",
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "10s",
                "panels": [
                    {
                        "id": 1,
                        "title": "Task Processing Rate",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                        "targets": [
                            {
                                "expr": "rate(maos_tasks_total{status=\"success\"}[5m])",
                                "legendFormat": "Successful Tasks/sec",
                                "refId": "A"
                            },
                            {
                                "expr": "rate(maos_tasks_total{status=\"failed\"}[5m])",
                                "legendFormat": "Failed Tasks/sec", 
                                "refId": "B"
                            }
                        ]
                    },
                    {
                        "id": 2,
                        "title": "Task Duration Distribution",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.50, rate(maos_task_duration_seconds_bucket[5m]))",
                                "legendFormat": "50th percentile",
                                "refId": "A"
                            },
                            {
                                "expr": "histogram_quantile(0.95, rate(maos_task_duration_seconds_bucket[5m]))",
                                "legendFormat": "95th percentile",
                                "refId": "B"
                            },
                            {
                                "expr": "histogram_quantile(0.99, rate(maos_task_duration_seconds_bucket[5m]))",
                                "legendFormat": "99th percentile",
                                "refId": "C"
                            }
                        ]
                    },
                    {
                        "id": 3,
                        "title": "System Resource Usage",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
                        "targets": [
                            {
                                "expr": "maos_cpu_usage_percentage",
                                "legendFormat": "CPU Usage %",
                                "refId": "A"
                            },
                            {
                                "expr": "maos_memory_usage_bytes / 1024 / 1024 / 1024",
                                "legendFormat": "Memory Usage GB",
                                "refId": "B"
                            }
                        ]
                    }
                ]
            }
        }
    
    def _create_alert_dashboard(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create alert management dashboard."""
        return {
            "dashboard": {
                "id": None,
                "title": "MAOS - Alert Management",
                "description": "Alert status and management interface",
                "tags": ["maos", "alerts", "monitoring"],
                "timezone": "utc",
                "time": {"from": "now-4h", "to": "now"},
                "refresh": "30s",
                "panels": [
                    {
                        "id": 1,
                        "title": "Active Alerts by Severity",
                        "type": "piechart",
                        "gridPos": {"h": 8, "w": 8, "x": 0, "y": 0},
                        "targets": [
                            {
                                "expr": "maos_active_alerts_by_severity",
                                "legendFormat": "{{severity}}",
                                "refId": "A"
                            }
                        ]
                    },
                    {
                        "id": 2,
                        "title": "Alert Rate Trend",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 16, "x": 8, "y": 0},
                        "targets": [
                            {
                                "expr": "rate(maos_alerts_total[5m])",
                                "legendFormat": "{{severity}}",
                                "refId": "A"
                            }
                        ]
                    },
                    {
                        "id": 3,
                        "title": "Top Alerting Components",
                        "type": "table",
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                        "targets": [
                            {
                                "expr": "topk(10, sum by (component) (maos_alerts_total))",
                                "legendFormat": "{{component}}",
                                "refId": "A",
                                "format": "table"
                            }
                        ]
                    },
                    {
                        "id": 4,
                        "title": "Alert Resolution Time",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.50, rate(maos_alert_resolution_time_seconds_bucket[5m]))",
                                "legendFormat": "Median Resolution Time",
                                "refId": "A"
                            },
                            {
                                "expr": "histogram_quantile(0.95, rate(maos_alert_resolution_time_seconds_bucket[5m]))",
                                "legendFormat": "95th Percentile",
                                "refId": "B"
                            }
                        ]
                    }
                ]
            }
        }
    
    def _create_agent_dashboard(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create agent monitoring dashboard."""
        return {
            "dashboard": {
                "id": None,
                "title": "MAOS - Agent Monitoring",
                "description": "Agent status and performance monitoring",
                "tags": ["maos", "agents", "monitoring"],
                "timezone": "utc",
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "15s",
                "panels": [
                    {
                        "id": 1,
                        "title": "Agent Status Overview",
                        "type": "stat",
                        "gridPos": {"h": 4, "w": 24, "x": 0, "y": 0},
                        "targets": [
                            {
                                "expr": "maos_agents_total",
                                "legendFormat": "{{status}}",
                                "refId": "A"
                            }
                        ]
                    },
                    {
                        "id": 2,
                        "title": "Agent Utilization",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4},
                        "targets": [
                            {
                                "expr": "maos_agent_utilization_percentage",
                                "legendFormat": "{{agent_id}}",
                                "refId": "A"
                            }
                        ],
                        "yAxes": [
                            {"label": "Utilization %", "min": 0, "max": 100}
                        ]
                    },
                    {
                        "id": 3,
                        "title": "Agent Response Times",
                        "type": "graph", 
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4},
                        "targets": [
                            {
                                "expr": "maos_agent_response_time_seconds",
                                "legendFormat": "{{agent_id}}",
                                "refId": "A"
                            }
                        ]
                    },
                    {
                        "id": 4,
                        "title": "Task Assignments by Agent",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 12},
                        "targets": [
                            {
                                "expr": "rate(maos_agent_task_assignments_total[5m])",
                                "legendFormat": "{{agent_id}}",
                                "refId": "A"
                            }
                        ]
                    }
                ]
            }
        }
    
    def _create_storage_dashboard(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create storage monitoring dashboard."""
        return {
            "dashboard": {
                "id": None,
                "title": "MAOS - Storage Monitoring",
                "description": "Redis and storage system monitoring",
                "tags": ["maos", "storage", "redis"],
                "timezone": "utc",
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "15s",
                "panels": [
                    {
                        "id": 1,
                        "title": "Redis Memory Usage",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                        "targets": [
                            {
                                "expr": "maos_redis_memory_usage_bytes / 1024 / 1024",
                                "legendFormat": "Memory Usage MB",
                                "refId": "A"
                            }
                        ]
                    },
                    {
                        "id": 2,
                        "title": "Redis Operations",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                        "targets": [
                            {
                                "expr": "maos_redis_operations_per_second",
                                "legendFormat": "Operations/sec",
                                "refId": "A"
                            }
                        ]
                    },
                    {
                        "id": 3,
                        "title": "Redis Hit Rate",
                        "type": "stat",
                        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 8},
                        "targets": [
                            {
                                "expr": "maos_redis_hit_rate_percentage",
                                "legendFormat": "Hit Rate",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "unit": "percent",
                                "thresholds": {
                                    "steps": [
                                        {"color": "red", "value": 0},
                                        {"color": "yellow", "value": 70},
                                        {"color": "green", "value": 90}
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "id": 4,
                        "title": "Connected Clients",
                        "type": "stat",
                        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 8},
                        "targets": [
                            {
                                "expr": "maos_redis_connected_clients",
                                "legendFormat": "Clients",
                                "refId": "A"
                            }
                        ]
                    },
                    {
                        "id": 5,
                        "title": "Storage Operations",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                        "targets": [
                            {
                                "expr": "rate(maos_storage_operations_total[5m])",
                                "legendFormat": "{{operation}} - {{status}}",
                                "refId": "A"
                            }
                        ]
                    }
                ]
            }
        }
    
    def export_to_file(self, dashboard_config: Dict[str, Any], filename: str) -> None:
        """Export dashboard configuration to JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(dashboard_config, f, indent=2)
            
            self.logger.logger.info(f"Dashboard exported to {filename}")
            
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "export_to_file",
                "filename": filename
            })
            raise
    
    def get_datasource_config(self) -> Dict[str, Any]:
        """Get Prometheus datasource configuration for Grafana."""
        return {
            "name": "MAOS Prometheus",
            "type": "prometheus",
            "url": "http://localhost:9090",
            "access": "proxy",
            "isDefault": True,
            "basicAuth": False,
            "withCredentials": False,
            "jsonData": {
                "timeInterval": "5s",
                "queryTimeout": "60s",
                "httpMethod": "POST"
            }
        }