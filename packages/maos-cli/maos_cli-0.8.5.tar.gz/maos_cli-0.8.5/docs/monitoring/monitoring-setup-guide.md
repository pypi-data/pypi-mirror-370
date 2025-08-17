# MAOS Monitoring System Setup Guide

## Overview

The MAOS Monitoring System provides comprehensive observability for your Multi-Agent Orchestration System with health checks, metrics collection, alerting, and real-time dashboards.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Health        │    │   Metrics       │    │   Alerting      │
│   Manager       │    │   Collector     │    │   System        │
│                 │    │                 │    │                 │
│ • Component     │    │ • Prometheus    │    │ • Rules Engine  │
│   Health        │    │   Integration   │    │ • Notifications │
│ • Dependencies  │    │ • Custom        │    │ • Escalation    │
│ • Status API    │    │   Metrics       │    │ • Management    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────┐
         │              Monitoring Dashboard                │
         │                                                 │
         │ • Real-time Status    • Performance Graphs      │
         │ • Agent Activity      • Resource Usage          │
         │ • Alert Management    • System Overview         │
         └─────────────────────────────────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────┐
         │                Grafana Integration              │
         │                                                 │
         │ • Custom Dashboards   • Historical Analysis     │
         │ • Advanced Queries    • Alert Visualization     │
         └─────────────────────────────────────────────────┘
```

## Quick Start

### 1. Basic Setup

```python
from src.monitoring.monitoring_service import MonitoringService

# Initialize monitoring service
monitoring = MonitoringService(
    health_check_interval=30.0,
    metrics_collection_interval=15.0,
    alert_evaluation_interval=30.0,
    dashboard_update_interval=5.0
)

# Register your MAOS components
await monitoring.initialize(
    orchestrator=your_orchestrator,
    agent_manager=your_agent_manager,
    message_bus=your_message_bus,
    redis_manager=your_redis_manager,
    external_dependencies={
        "database": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432
        },
        "api_service": {
            "type": "http",
            "url": "https://api.example.com/health"
        }
    }
)

# Start monitoring
await monitoring.start()

# Create FastAPI app with monitoring endpoints
app = monitoring.create_fastapi_app()
```

### 2. Configuration

```python
config = {
    "notifications": {
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "alerts@yourcompany.com",
            "password": "your-app-password",
            "from_email": "alerts@yourcompany.com",
            "to_emails": ["ops@yourcompany.com", "dev@yourcompany.com"],
            "use_tls": True
        },
        "slack": {
            "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
            "channel": "#alerts",
            "username": "MAOS Monitor"
        },
        "webhook": {
            "url": "https://your-webhook-endpoint.com/alerts",
            "headers": {"Authorization": "Bearer your-token"},
            "timeout": 30
        },
        "pagerduty": {
            "integration_key": "your-pagerduty-integration-key",
            "severity_mapping": {
                "critical": "critical",
                "high": "error",
                "medium": "warning",
                "low": "info"
            }
        }
    }
}

monitoring = MonitoringService(config=config)
```

## Health Check System

### Component Health Checkers

The system includes health checkers for all major components:

- **Orchestrator**: Task queue status, active tasks, system state
- **Agent Manager**: Agent counts, status distribution, individual agent health
- **Communication**: Message bus connectivity, queue depths, error rates
- **Storage**: Redis connectivity, memory usage, performance metrics
- **Dependencies**: External service availability and response times

### Health Endpoints

```bash
# Overall system health
GET /health/

# Kubernetes probes
GET /health/live      # Liveness probe
GET /health/ready     # Readiness probe

# Component-specific health
GET /health/components/{component_name}

# Dependency health
GET /health/dependencies/{component_name}

# Trigger immediate health check
POST /health/check?component=orchestrator

# Health metrics
GET /health/metrics

# Health history
GET /health/history?hours=24

# Simple status for external monitoring
GET /health/status
```

### Custom Health Checkers

```python
from src.monitoring.health.health_checker import HealthChecker, HealthStatus, ComponentHealth

class CustomHealthChecker(HealthChecker):
    def __init__(self, your_component):
        super().__init__("custom_component", check_interval=30.0)
        self.component = your_component
    
    async def check_health(self) -> ComponentHealth:
        try:
            # Perform your health checks
            is_healthy = await self.component.health_check()
            metric_value = await self.component.get_metric()
            
            if is_healthy and metric_value < 100:
                status = HealthStatus.HEALTHY
                message = "Component is operating normally"
            elif is_healthy:
                status = HealthStatus.DEGRADED
                message = f"Component functional but metric high: {metric_value}"
            else:
                status = HealthStatus.UNHEALTHY
                message = "Component health check failed"
            
            return ComponentHealth(
                component_name=self.component_name,
                status=status,
                message=message,
                metrics={"custom_metric": metric_value}
            )
        except Exception as e:
            return ComponentHealth(
                component_name=self.component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check error: {str(e)}"
            )

# Register with health manager
monitoring.health_manager.register_checker(CustomHealthChecker(your_component))
```

## Metrics Collection

### Prometheus Integration

The system exposes comprehensive metrics in Prometheus format:

```bash
# Metrics endpoint
GET /metrics
```

### Available Metrics

#### System Health Metrics
- `maos_system_health_status` - Overall system health (0=unhealthy, 1=degraded, 2=healthy)
- `maos_component_health_status{component}` - Individual component health
- `maos_health_check_duration_seconds{component}` - Health check execution time

#### Task Metrics
- `maos_tasks_total{status,type}` - Total tasks processed
- `maos_task_duration_seconds{type,status}` - Task execution duration
- `maos_active_tasks{type}` - Currently active tasks
- `maos_task_queue_size{priority}` - Task queue depth

#### Agent Metrics
- `maos_agents_total{status,type}` - Total agents by status
- `maos_agent_utilization_percentage{agent_id}` - Agent utilization
- `maos_agent_response_time_seconds{agent_id}` - Agent response times
- `maos_agent_task_assignments_total{agent_id,task_type}` - Task assignments

#### Communication Metrics
- `maos_messages_total{type,status}` - Messages processed
- `maos_message_size_bytes{type}` - Message sizes
- `maos_message_processing_time_seconds{type}` - Processing time
- `maos_active_connections{type}` - Active connections

#### Storage Metrics
- `maos_redis_memory_usage_bytes` - Redis memory usage
- `maos_redis_operations_per_second` - Redis operations rate
- `maos_redis_hit_rate_percentage` - Cache hit rate
- `maos_storage_operations_total{operation,status}` - Storage operations

### Custom Metrics

```python
from src.monitoring.metrics.metrics_registry import MetricsRegistry, MetricDefinition

# Register custom metrics
registry = MetricsRegistry()

registry.register_metric(
    name="custom_business_metric",
    metric_type="gauge",
    description="Business-specific metric",
    labels=["department", "service"],
    collector=lambda: get_business_metric_value()
)

# Record metric values
monitoring.metrics_collector.record_custom_metric("custom_business_metric", 42.0, {"department": "sales"})
```

## Alerting System

### Built-in Alert Rules

Default alert rules are configured for:

- System health degradation
- High CPU usage (>80%)
- High memory usage (>85%)
- Redis memory usage (>90%)
- Low cache hit rate (<70%)
- Component failures
- High error rates

### Custom Alert Rules

```python
from src.monitoring.alerts.alert_manager import AlertRule, AlertSeverity

# Create custom alert rule
rule = AlertRule(
    name="high_task_failure_rate",
    description="Task failure rate is too high",
    metric_name="task_failure_rate_percentage",
    condition="gt",
    threshold=5.0,
    severity=AlertSeverity.HIGH,
    component="orchestrator",
    for_duration=300.0  # Alert after 5 minutes
)

monitoring.alert_manager.add_alert_rule(rule)
```

### Alert Management Endpoints

```bash
# Get active alerts
GET /alerts/

# Get alerts by severity
GET /alerts/?severity=critical

# Acknowledge alert
POST /alerts/{alert_id}/acknowledge

# Alert statistics
GET /alerts/statistics

# Alert history
GET /alerts/history?hours=24
```

### Notification Channels

Configure multiple notification channels:

```python
# Email notifications
email_config = {
    "smtp_server": "smtp.company.com",
    "username": "alerts@company.com",
    "password": "secure-password",
    "from_email": "alerts@company.com",
    "to_emails": ["ops@company.com"]
}

# Slack notifications
slack_config = {
    "webhook_url": "https://hooks.slack.com/services/...",
    "channel": "#alerts"
}

# PagerDuty for critical alerts
pagerduty_config = {
    "integration_key": "your-integration-key"
}
```

## Dashboard System

### Real-time Dashboard

Access the monitoring dashboard:

```bash
# Dashboard data
GET /dashboard/

# Dashboard configuration
GET /dashboard/config
PUT /dashboard/config

# Performance statistics
GET /dashboard/performance
```

### Dashboard Features

- **System Overview**: Health status, active alerts, component summary
- **Performance Metrics**: CPU, memory, disk usage, throughput
- **Agent Monitoring**: Agent status, utilization, task assignments
- **Task Queue Status**: Pending, active, completed tasks
- **Alert Summary**: Active alerts, recent activity, top alerting components
- **Resource Usage**: Real-time system resource consumption
- **Storage Status**: Redis metrics, cache performance
- **Communication Status**: Message bus health, processing rates

### WebSocket Integration

```javascript
// Real-time dashboard updates
const ws = new WebSocket('ws://localhost:8000/dashboard/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    updateDashboard(data);
};
```

## Grafana Integration

### Setup Grafana Dashboards

```python
from src.monitoring.dashboard.grafana_integration import GrafanaDashboardExporter

exporter = GrafanaDashboardExporter()

# Generate all dashboards
dashboards = exporter.generate_all_dashboards()

# Export specific dashboard
system_overview = exporter.generate_dashboard_config("system_overview")
exporter.export_to_file(system_overview, "maos-system-overview.json")

# Get datasource configuration
datasource_config = exporter.get_datasource_config()
```

### Available Dashboard Types

1. **System Overview** - High-level health and performance
2. **Health Monitoring** - Detailed component health tracking
3. **Performance Metrics** - Task processing and system performance
4. **Alert Management** - Alert status and trends
5. **Agent Monitoring** - Agent-specific metrics and performance
6. **Storage Monitoring** - Redis and storage system metrics

### Import to Grafana

1. Install Grafana and configure Prometheus datasource
2. Import the generated dashboard JSON files
3. Configure alerts and notifications in Grafana
4. Set up dashboard permissions and sharing

## Deployment

### Docker Compose Setup

```yaml
version: '3.8'
services:
  maos-monitoring:
    build: .
    ports:
      - "8000:8000"     # Monitoring API
      - "9090:9090"     # Prometheus metrics
    environment:
      - MONITORING_CONFIG_PATH=/app/config/monitoring.yml
    volumes:
      - ./config:/app/config
    depends_on:
      - redis
      - prometheus
      - grafana

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./dashboards:/etc/grafana/provisioning/dashboards

volumes:
  prometheus_data:
  grafana_data:
```

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'maos-monitoring'
    static_configs:
      - targets: ['maos-monitoring:9090']
    scrape_interval: 5s
    metrics_path: /metrics

  - job_name: 'maos-health'
    static_configs:
      - targets: ['maos-monitoring:8000']
    scrape_interval: 30s
    metrics_path: /health/metrics

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

rule_files:
  - "maos_alerts.yml"
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: maos-monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: maos-monitoring
  template:
    metadata:
      labels:
        app: maos-monitoring
    spec:
      containers:
      - name: monitoring
        image: maos-monitoring:latest
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 9090
          name: metrics
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: maos-monitoring-service
spec:
  selector:
    app: maos-monitoring
  ports:
  - name: http
    port: 8000
    targetPort: 8000
  - name: metrics
    port: 9090
    targetPort: 9090
```

## Best Practices

### 1. Health Check Configuration

- Set appropriate timeouts for health checks
- Configure dependencies correctly to avoid cascade failures
- Use different check intervals for different components
- Implement graceful degradation for non-critical components

### 2. Metrics Collection

- Choose appropriate metric types (counter, gauge, histogram)
- Use meaningful labels but avoid high cardinality
- Monitor metric collection performance
- Implement metric retention policies

### 3. Alert Management

- Set realistic thresholds based on historical data
- Implement alert suppression during maintenance
- Use escalation policies for critical alerts
- Group related alerts to reduce noise
- Regularly review and tune alert rules

### 4. Dashboard Design

- Focus on actionable metrics
- Use appropriate visualization types
- Implement drill-down capabilities
- Consider different audiences (ops, dev, business)
- Keep dashboards simple and fast

### 5. Performance Optimization

- Monitor the monitoring system itself
- Use appropriate collection intervals
- Implement metric sampling for high-volume data
- Cache expensive calculations
- Scale monitoring components separately

## Troubleshooting

### Common Issues

#### 1. Health Checks Failing

```bash
# Check health status
curl -s http://localhost:8000/health/ | jq .

# Check specific component
curl -s http://localhost:8000/health/components/storage | jq .

# Trigger immediate health check
curl -X POST http://localhost:8000/health/check
```

#### 2. Metrics Not Appearing

```bash
# Check metrics endpoint
curl http://localhost:8000/metrics | grep maos_

# Check collector status
curl -s http://localhost:8000/info | jq .
```

#### 3. Alerts Not Firing

```bash
# Check alert rules
curl -s http://localhost:8000/alerts/statistics | jq .

# Check specific metric value
curl -s http://localhost:8000/health/metrics | jq .
```

#### 4. Dashboard Issues

```bash
# Check dashboard data
curl -s http://localhost:8000/dashboard/ | jq .

# Check dashboard performance
curl -s http://localhost:8000/dashboard/performance | jq .
```

### Debugging Commands

```bash
# Enable debug logging
export MAOS_LOG_LEVEL=DEBUG

# Check component registrations
curl -s http://localhost:8000/info | jq '.registered_components'

# Monitor real-time health changes
watch -n 5 'curl -s http://localhost:8000/health/ | jq ".system_status"'

# Check alert history
curl -s 'http://localhost:8000/alerts/history?hours=1' | jq '.alerts[] | {name, severity, timestamp}'
```

## Security Considerations

1. **API Security**
   - Enable authentication for monitoring endpoints
   - Use HTTPS in production
   - Implement rate limiting
   - Restrict access to sensitive metrics

2. **Notification Security**
   - Secure webhook endpoints
   - Use encrypted channels for sensitive alerts
   - Rotate notification channel credentials regularly
   - Validate notification payloads

3. **Data Protection**
   - Avoid logging sensitive data in health checks
   - Sanitize metric labels
   - Implement data retention policies
   - Secure dashboard access

This comprehensive monitoring system provides full observability for your MAOS deployment with health checks, metrics, alerting, and dashboards. Regular monitoring and maintenance of the monitoring system itself ensures reliable operation and early detection of issues.