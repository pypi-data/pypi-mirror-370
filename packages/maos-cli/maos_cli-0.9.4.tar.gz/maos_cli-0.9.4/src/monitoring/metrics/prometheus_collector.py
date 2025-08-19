"""
Prometheus metrics collector for MAOS monitoring system.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from uuid import uuid4

from prometheus_client import (
    Counter, Gauge, Histogram, Summary, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)

from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError


class MAOSMetrics:
    """MAOS-specific Prometheus metrics definitions."""
    
    def __init__(self, registry: CollectorRegistry):
        """Initialize MAOS metrics."""
        self.registry = registry
        
        # System Health Metrics
        self.system_health = Gauge(
            'maos_system_health_status',
            'Overall system health status (0=unhealthy, 1=degraded, 2=healthy)',
            registry=registry
        )
        
        self.component_health = Gauge(
            'maos_component_health_status',
            'Component health status',
            ['component'],
            registry=registry
        )
        
        self.health_check_duration = Histogram(
            'maos_health_check_duration_seconds',
            'Duration of health checks',
            ['component'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
            registry=registry
        )
        
        # Task Metrics
        self.tasks_total = Counter(
            'maos_tasks_total',
            'Total number of tasks processed',
            ['status', 'type'],
            registry=registry
        )
        
        self.task_duration = Histogram(
            'maos_task_duration_seconds',
            'Duration of task execution',
            ['type', 'status'],
            buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0],
            registry=registry
        )
        
        self.active_tasks = Gauge(
            'maos_active_tasks',
            'Number of currently active tasks',
            ['type'],
            registry=registry
        )
        
        self.task_queue_size = Gauge(
            'maos_task_queue_size',
            'Number of tasks in queue',
            ['priority'],
            registry=registry
        )
        
        # Agent Metrics
        self.agents_total = Gauge(
            'maos_agents_total',
            'Total number of agents',
            ['status', 'type'],
            registry=registry
        )
        
        self.agent_task_assignments = Counter(
            'maos_agent_task_assignments_total',
            'Total task assignments to agents',
            ['agent_id', 'task_type'],
            registry=registry
        )
        
        self.agent_utilization = Gauge(
            'maos_agent_utilization_percentage',
            'Agent utilization percentage',
            ['agent_id'],
            registry=registry
        )
        
        self.agent_response_time = Histogram(
            'maos_agent_response_time_seconds',
            'Agent response time',
            ['agent_id'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
            registry=registry
        )
        
        # Communication Metrics
        self.messages_total = Counter(
            'maos_messages_total',
            'Total messages processed',
            ['type', 'status'],
            registry=registry
        )
        
        self.message_size_bytes = Histogram(
            'maos_message_size_bytes',
            'Message size in bytes',
            ['type'],
            buckets=[64, 256, 1024, 4096, 16384, 65536, 262144],
            registry=registry
        )
        
        self.message_processing_time = Histogram(
            'maos_message_processing_time_seconds',
            'Message processing time',
            ['type'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
            registry=registry
        )
        
        self.active_connections = Gauge(
            'maos_active_connections',
            'Number of active connections',
            ['type'],
            registry=registry
        )
        
        # Storage Metrics
        self.storage_operations_total = Counter(
            'maos_storage_operations_total',
            'Total storage operations',
            ['operation', 'status'],
            registry=registry
        )
        
        self.storage_operation_duration = Histogram(
            'maos_storage_operation_duration_seconds',
            'Storage operation duration',
            ['operation'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
            registry=registry
        )
        
        self.redis_memory_usage_bytes = Gauge(
            'maos_redis_memory_usage_bytes',
            'Redis memory usage in bytes',
            registry=registry
        )
        
        self.redis_connected_clients = Gauge(
            'maos_redis_connected_clients',
            'Number of Redis connected clients',
            registry=registry
        )
        
        self.redis_operations_per_second = Gauge(
            'maos_redis_operations_per_second',
            'Redis operations per second',
            registry=registry
        )
        
        self.redis_hit_rate = Gauge(
            'maos_redis_hit_rate_percentage',
            'Redis cache hit rate percentage',
            registry=registry
        )
        
        # Resource Metrics
        self.cpu_usage_percentage = Gauge(
            'maos_cpu_usage_percentage',
            'CPU usage percentage',
            ['component'],
            registry=registry
        )
        
        self.memory_usage_bytes = Gauge(
            'maos_memory_usage_bytes',
            'Memory usage in bytes',
            ['component'],
            registry=registry
        )
        
        self.disk_usage_bytes = Gauge(
            'maos_disk_usage_bytes',
            'Disk usage in bytes',
            ['component'],
            registry=registry
        )
        
        self.network_bytes_total = Counter(
            'maos_network_bytes_total',
            'Total network bytes',
            ['direction'],
            registry=registry
        )
        
        # Business Metrics
        self.task_completion_rate = Gauge(
            'maos_task_completion_rate_percentage',
            'Task completion rate percentage',
            ['time_window'],
            registry=registry
        )
        
        self.system_throughput = Gauge(
            'maos_system_throughput_tasks_per_second',
            'System throughput in tasks per second',
            registry=registry
        )
        
        self.error_rate = Gauge(
            'maos_error_rate_percentage',
            'System error rate percentage',
            ['component'],
            registry=registry
        )
        
        self.availability_percentage = Gauge(
            'maos_availability_percentage',
            'System availability percentage',
            ['component'],
            registry=registry
        )
        
        # Performance Metrics
        self.latency_percentiles = Summary(
            'maos_latency_seconds',
            'Request latency percentiles',
            ['operation'],
            registry=registry
        )
        
        # System Info
        self.system_info = Info(
            'maos_system_info',
            'MAOS system information',
            registry=registry
        )


class PrometheusCollector:
    """
    Prometheus metrics collector for MAOS system.
    
    Collects and exposes metrics from all MAOS components in Prometheus format.
    """
    
    def __init__(
        self,
        collection_interval: float = 15.0,
        port: int = 8000,
        registry: Optional[CollectorRegistry] = None
    ):
        """Initialize Prometheus collector."""
        self.collection_interval = collection_interval
        self.port = port
        self.registry = registry or CollectorRegistry()
        
        self.logger = MAOSLogger("prometheus_collector", str(uuid4()))
        
        # Initialize MAOS metrics
        self.metrics = MAOSMetrics(self.registry)
        
        # Metric collectors from various components
        self._collectors: Dict[str, Any] = {}
        
        # Background collection
        self._collection_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Metric cache for performance
        self._metric_cache: Dict[str, Any] = {}
        self._cache_ttl = 10.0  # seconds
        self._last_cache_update = 0.0
        
        # Health manager integration
        self._health_manager = None
        
        # Component integrations
        self._orchestrator = None
        self._agent_manager = None
        self._message_bus = None
        self._redis_manager = None
    
    def register_component(self, component_type: str, component_instance: Any) -> None:
        """Register a component for metrics collection."""
        self.logger.logger.info(f"Registering component for metrics: {component_type}")
        
        if component_type == "health_manager":
            self._health_manager = component_instance
        elif component_type == "orchestrator":
            self._orchestrator = component_instance
        elif component_type == "agent_manager":
            self._agent_manager = component_instance
        elif component_type == "message_bus":
            self._message_bus = component_instance
        elif component_type == "redis_manager":
            self._redis_manager = component_instance
        else:
            self._collectors[component_type] = component_instance
    
    async def start_collection(self) -> None:
        """Start metrics collection."""
        self.logger.logger.info("Starting Prometheus metrics collection")
        
        # Initialize system info
        self._update_system_info()
        
        # Start collection loop
        self._shutdown_event.clear()
        self._collection_task = asyncio.create_task(self._collection_loop())
    
    async def stop_collection(self) -> None:
        """Stop metrics collection."""
        self.logger.logger.info("Stopping Prometheus metrics collection")
        
        self._shutdown_event.set()
        
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
    
    async def _collection_loop(self) -> None:
        """Main collection loop."""
        while not self._shutdown_event.is_set():
            try:
                start_time = time.time()
                
                # Collect metrics from all components
                await self._collect_all_metrics()
                
                collection_duration = time.time() - start_time
                self.logger.logger.debug(f"Metrics collection completed in {collection_duration:.3f}s")
                
                # Wait for next collection
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {"operation": "metrics_collection_loop"})
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_all_metrics(self) -> None:
        """Collect metrics from all registered components."""
        # Health metrics
        if self._health_manager:
            await self._collect_health_metrics()
        
        # Task metrics
        if self._orchestrator:
            await self._collect_task_metrics()
        
        # Agent metrics
        if self._agent_manager:
            await self._collect_agent_metrics()
        
        # Communication metrics
        if self._message_bus:
            await self._collect_communication_metrics()
        
        # Storage metrics
        if self._redis_manager:
            await self._collect_storage_metrics()
        
        # System resource metrics
        await self._collect_system_metrics()
        
        # Business metrics
        await self._collect_business_metrics()
    
    async def _collect_health_metrics(self) -> None:
        """Collect health metrics."""
        try:
            health_data = await self._health_manager.get_health_status()
            
            # System health status
            status_map = {"healthy": 2, "degraded": 1, "unhealthy": 0, "unknown": 0}
            system_status = status_map.get(health_data.get("system_status"), 0)
            self.metrics.system_health.set(system_status)
            
            # Component health
            for component, health_info in health_data.get("components", {}).items():
                component_status = status_map.get(health_info.get("status"), 0)
                self.metrics.component_health.labels(component=component).set(component_status)
                
                # Health check duration
                duration = health_info.get("check_duration_ms", 0) / 1000.0
                self.metrics.health_check_duration.labels(component=component).observe(duration)
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "collect_health_metrics"})
    
    async def _collect_task_metrics(self) -> None:
        """Collect task metrics from orchestrator."""
        try:
            # Get task statistics
            pending_tasks = len(getattr(self._orchestrator, '_task_queue', []))
            active_tasks = len(getattr(self._orchestrator, '_active_tasks', {}))
            
            # Update gauges
            self.metrics.active_tasks.labels(type="all").set(active_tasks)
            self.metrics.task_queue_size.labels(priority="all").set(pending_tasks)
            
            # Task completion metrics would come from task events
            # This would be integrated with the orchestrator's event system
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "collect_task_metrics"})
    
    async def _collect_agent_metrics(self) -> None:
        """Collect agent metrics."""
        try:
            if not hasattr(self._agent_manager, '_agents'):
                return
            
            # Agent statistics
            agents = getattr(self._agent_manager, '_agents', {})
            status_counts = {"active": 0, "idle": 0, "failed": 0}
            
            for agent_id, agent in agents.items():
                status = getattr(agent, 'status', 'unknown')
                if status in status_counts:
                    status_counts[status] += 1
                
                # Agent utilization (would need to be calculated based on task assignments)
                utilization = getattr(agent, 'utilization', 0.0)
                self.metrics.agent_utilization.labels(agent_id=agent_id).set(utilization)
            
            # Update agent totals
            for status, count in status_counts.items():
                self.metrics.agents_total.labels(status=status, type="all").set(count)
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "collect_agent_metrics"})
    
    async def _collect_communication_metrics(self) -> None:
        """Collect communication metrics."""
        try:
            # Message statistics
            pending_messages = len(getattr(self._message_bus, '_pending_messages', []))
            processed_count = getattr(self._message_bus, '_processed_count', 0)
            failed_count = getattr(self._message_bus, '_failed_count', 0)
            
            # Active connections
            connections = len(getattr(self._message_bus, '_connections', {}))
            self.metrics.active_connections.labels(type="message_bus").set(connections)
            
            # These counters would be incremented by the message bus during operation
            # Here we're just reading the current state
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "collect_communication_metrics"})
    
    async def _collect_storage_metrics(self) -> None:
        """Collect Redis storage metrics."""
        try:
            redis_client = self._redis_manager.redis
            info = await redis_client.info()
            
            # Memory usage
            memory_usage = info.get('used_memory', 0)
            self.metrics.redis_memory_usage_bytes.set(memory_usage)
            
            # Connected clients
            clients = info.get('connected_clients', 0)
            self.metrics.redis_connected_clients.set(clients)
            
            # Operations per second
            ops = info.get('instantaneous_ops_per_sec', 0)
            self.metrics.redis_operations_per_second.set(ops)
            
            # Hit rate
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            if hits + misses > 0:
                hit_rate = (hits / (hits + misses)) * 100
                self.metrics.redis_hit_rate.set(hit_rate)
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "collect_storage_metrics"})
    
    async def _collect_system_metrics(self) -> None:
        """Collect system resource metrics."""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics.cpu_usage_percentage.labels(component="system").set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics.memory_usage_bytes.labels(component="system").set(memory.used)
            
            # Network I/O
            network = psutil.net_io_counters()
            if network:
                self.metrics.network_bytes_total.labels(direction="received").inc(network.bytes_recv)
                self.metrics.network_bytes_total.labels(direction="sent").inc(network.bytes_sent)
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "collect_system_metrics"})
    
    async def _collect_business_metrics(self) -> None:
        """Collect business-level metrics."""
        try:
            # These would be calculated based on historical data
            # For now, we'll use placeholder values
            
            # Task completion rate (would be calculated from task history)
            completion_rate = 95.0  # Placeholder
            self.metrics.task_completion_rate.labels(time_window="1h").set(completion_rate)
            
            # System throughput (tasks per second)
            throughput = 10.5  # Placeholder
            self.metrics.system_throughput.set(throughput)
            
            # Availability (based on health status)
            if self._health_manager:
                health_data = await self._health_manager.get_health_status()
                if health_data.get("system_status") == "healthy":
                    availability = 100.0
                elif health_data.get("system_status") == "degraded":
                    availability = 80.0
                else:
                    availability = 0.0
                
                self.metrics.availability_percentage.labels(component="system").set(availability)
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "collect_business_metrics"})
    
    def _update_system_info(self) -> None:
        """Update system information metrics."""
        import platform
        import sys
        
        system_info = {
            "version": "2.0.0",  # MAOS version
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "hostname": platform.node(),
            "architecture": platform.machine()
        }
        
        self.metrics.system_info.info(system_info)
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        return generate_latest(self.registry).decode('utf-8')
    
    def get_content_type(self) -> str:
        """Get Prometheus content type."""
        return CONTENT_TYPE_LATEST
    
    # Instrumentation methods for components to call
    
    def record_task_start(self, task_id: str, task_type: str) -> None:
        """Record task start."""
        self.metrics.tasks_total.labels(status="started", type=task_type).inc()
    
    def record_task_completion(self, task_id: str, task_type: str, duration: float, success: bool) -> None:
        """Record task completion."""
        status = "success" if success else "failed"
        self.metrics.tasks_total.labels(status=status, type=task_type).inc()
        self.metrics.task_duration.labels(type=task_type, status=status).observe(duration)
    
    def record_message_processed(self, message_type: str, size_bytes: int, processing_time: float, success: bool) -> None:
        """Record message processing."""
        status = "success" if success else "failed"
        self.metrics.messages_total.labels(type=message_type, status=status).inc()
        self.metrics.message_size_bytes.labels(type=message_type).observe(size_bytes)
        self.metrics.message_processing_time.labels(type=message_type).observe(processing_time)
    
    def record_storage_operation(self, operation: str, duration: float, success: bool) -> None:
        """Record storage operation."""
        status = "success" if success else "failed"
        self.metrics.storage_operations_total.labels(operation=operation, status=status).inc()
        self.metrics.storage_operation_duration.labels(operation=operation).observe(duration)
    
    def record_agent_response_time(self, agent_id: str, response_time: float) -> None:
        """Record agent response time."""
        self.metrics.agent_response_time.labels(agent_id=agent_id).observe(response_time)
    
    def record_latency(self, operation: str, latency: float) -> None:
        """Record operation latency."""
        self.metrics.latency_percentiles.labels(operation=operation).observe(latency)