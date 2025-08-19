"""
Redis State Monitoring System for performance and health tracking.

Provides comprehensive monitoring and analytics for Redis-based state management.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
from collections import deque
from aioredis import Redis

from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError


class RedisStateMonitor:
    """
    Comprehensive monitoring system for Redis state management.
    
    Features:
    - Performance metrics collection
    - Health monitoring
    - Bottleneck detection
    - Alert generation
    - Historical analytics
    """
    
    def __init__(
        self,
        redis: Redis,
        collection_interval: float = 1.0,
        retention_hours: int = 24,
        alert_thresholds: Optional[Dict[str, Any]] = None
    ):
        """Initialize monitoring system."""
        self.redis = redis
        self.collection_interval = collection_interval
        self.retention_hours = retention_hours
        self.alert_thresholds = alert_thresholds or self._default_alert_thresholds()
        
        self.logger = MAOSLogger("redis_state_monitor", str(uuid4()))
        
        # Metrics storage
        self.max_data_points = int((retention_hours * 3600) / collection_interval)
        self._metrics_history: Dict[str, deque] = {
            'timestamp': deque(maxlen=self.max_data_points),
            'memory_usage_bytes': deque(maxlen=self.max_data_points),
            'connected_clients': deque(maxlen=self.max_data_points),
            'operations_per_second': deque(maxlen=self.max_data_points),
            'hit_rate_percentage': deque(maxlen=self.max_data_points),
            'latency_ms': deque(maxlen=self.max_data_points),
            'cpu_usage_percentage': deque(maxlen=self.max_data_points),
            'network_io_bytes': deque(maxlen=self.max_data_points),
            'keyspace_size': deque(maxlen=self.max_data_points),
            'evictions_count': deque(maxlen=self.max_data_points)
        }
        
        # Real-time metrics
        self._current_metrics: Dict[str, Any] = {}
        
        # Alert tracking
        self._active_alerts: List[Dict[str, Any]] = []
        self._alert_history: deque = deque(maxlen=1000)
        
        # Performance baselines
        self._performance_baselines: Dict[str, float] = {}
        
        # Background tasks
        self._collection_task: Optional[asyncio.Task] = None
        self._analysis_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Latency tracking
        self._latency_samples: deque = deque(maxlen=1000)
        self._operation_counters: Dict[str, int] = {}
        
        # Redis info keys we monitor
        self.REDIS_INFO_KEYS = {
            'used_memory': 'memory_usage_bytes',
            'connected_clients': 'connected_clients',
            'instantaneous_ops_per_sec': 'operations_per_second',
            'keyspace_hits': 'keyspace_hits',
            'keyspace_misses': 'keyspace_misses',
            'evicted_keys': 'evictions_count',
            'used_cpu_sys': 'cpu_usage_percentage',
            'total_net_input_bytes': 'network_input_bytes',
            'total_net_output_bytes': 'network_output_bytes'
        }
    
    def _default_alert_thresholds(self) -> Dict[str, Any]:
        """Default alert thresholds."""
        return {
            'memory_usage_percentage': 80.0,
            'cpu_usage_percentage': 80.0,
            'hit_rate_percentage': 80.0,  # Alert if below this
            'latency_ms': 100.0,
            'operations_per_second': 10000.0,  # Alert if above this
            'connected_clients': 1000,
            'evictions_count_rate': 100.0  # per minute
        }
    
    async def initialize(self) -> None:
        """Initialize monitoring system."""
        self.logger.logger.info("Initializing Redis State Monitor")
        
        try:
            # Establish baselines
            await self._establish_performance_baselines()
            
            # Start background tasks
            await self._start_monitoring_tasks()
            
            self.logger.logger.info("Redis State Monitor initialized")
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'initialize'})
            raise MAOSError(f"Failed to initialize monitor: {str(e)}")
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect current Redis metrics."""
        try:
            start_time = time.time()
            
            # Get Redis info
            info = await self.redis.info()
            
            # Calculate derived metrics
            metrics = await self._process_redis_info(info)
            
            # Add timestamp
            metrics['timestamp'] = datetime.utcnow().isoformat()
            metrics['collection_time_ms'] = (time.time() - start_time) * 1000
            
            # Store in history
            await self._store_metrics(metrics)
            
            # Update current metrics
            self._current_metrics = metrics
            
            # Check for alerts
            await self._check_alerts(metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'collect_metrics'})
            return {}
    
    async def _process_redis_info(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Process Redis info into standardized metrics."""
        metrics = {}
        
        # Basic Redis metrics
        for redis_key, metric_name in self.REDIS_INFO_KEYS.items():
            if redis_key in info:
                metrics[metric_name] = info[redis_key]
        
        # Calculate derived metrics
        if 'keyspace_hits' in info and 'keyspace_misses' in info:
            total_requests = info['keyspace_hits'] + info['keyspace_misses']
            if total_requests > 0:
                metrics['hit_rate_percentage'] = (info['keyspace_hits'] / total_requests) * 100
            else:
                metrics['hit_rate_percentage'] = 0.0
        
        # Memory utilization
        if 'used_memory' in info and 'maxmemory' in info and info['maxmemory'] > 0:
            metrics['memory_usage_percentage'] = (info['used_memory'] / info['maxmemory']) * 100
        
        # Network I/O total
        if 'total_net_input_bytes' in info and 'total_net_output_bytes' in info:
            metrics['network_io_bytes'] = info['total_net_input_bytes'] + info['total_net_output_bytes']
        
        # Keyspace size
        keyspace_size = 0
        for key, value in info.items():
            if key.startswith('db') and isinstance(value, dict):
                if 'keys' in value:
                    keyspace_size += value['keys']
        metrics['keyspace_size'] = keyspace_size
        
        # Add latency metrics if available
        if self._latency_samples:
            metrics['avg_latency_ms'] = sum(self._latency_samples) / len(self._latency_samples)
            metrics['max_latency_ms'] = max(self._latency_samples)
            metrics['min_latency_ms'] = min(self._latency_samples)
        
        return metrics
    
    async def _store_metrics(self, metrics: Dict[str, Any]) -> None:
        """Store metrics in history."""
        timestamp = time.time()
        self._metrics_history['timestamp'].append(timestamp)
        
        for key, value in metrics.items():
            if key in self._metrics_history and isinstance(value, (int, float)):
                self._metrics_history[key].append(value)
    
    def record_operation_latency(self, operation: str, latency_ms: float) -> None:
        """Record latency for a specific operation."""
        self._latency_samples.append(latency_ms)
        
        # Update operation counters
        self._operation_counters[operation] = self._operation_counters.get(operation, 0) + 1
    
    async def _check_alerts(self, metrics: Dict[str, Any]) -> None:
        """Check metrics against alert thresholds."""
        new_alerts = []
        
        try:
            # Memory usage alert
            if 'memory_usage_percentage' in metrics:
                threshold = self.alert_thresholds['memory_usage_percentage']
                if metrics['memory_usage_percentage'] > threshold:
                    new_alerts.append({
                        'type': 'HIGH_MEMORY_USAGE',
                        'severity': 'WARNING',
                        'message': f"Memory usage is {metrics['memory_usage_percentage']:.1f}% (threshold: {threshold}%)",
                        'value': metrics['memory_usage_percentage'],
                        'threshold': threshold,
                        'timestamp': datetime.utcnow()
                    })
            
            # CPU usage alert
            if 'cpu_usage_percentage' in metrics:
                threshold = self.alert_thresholds['cpu_usage_percentage']
                if metrics['cpu_usage_percentage'] > threshold:
                    new_alerts.append({
                        'type': 'HIGH_CPU_USAGE',
                        'severity': 'WARNING',
                        'message': f"CPU usage is {metrics['cpu_usage_percentage']:.1f}% (threshold: {threshold}%)",
                        'value': metrics['cpu_usage_percentage'],
                        'threshold': threshold,
                        'timestamp': datetime.utcnow()
                    })
            
            # Hit rate alert (low hit rate is bad)
            if 'hit_rate_percentage' in metrics:
                threshold = self.alert_thresholds['hit_rate_percentage']
                if metrics['hit_rate_percentage'] < threshold:
                    new_alerts.append({
                        'type': 'LOW_HIT_RATE',
                        'severity': 'WARNING',
                        'message': f"Cache hit rate is {metrics['hit_rate_percentage']:.1f}% (threshold: {threshold}%)",
                        'value': metrics['hit_rate_percentage'],
                        'threshold': threshold,
                        'timestamp': datetime.utcnow()
                    })
            
            # Latency alert
            if 'avg_latency_ms' in metrics:
                threshold = self.alert_thresholds['latency_ms']
                if metrics['avg_latency_ms'] > threshold:
                    new_alerts.append({
                        'type': 'HIGH_LATENCY',
                        'severity': 'CRITICAL',
                        'message': f"Average latency is {metrics['avg_latency_ms']:.1f}ms (threshold: {threshold}ms)",
                        'value': metrics['avg_latency_ms'],
                        'threshold': threshold,
                        'timestamp': datetime.utcnow()
                    })
            
            # Operations per second alert
            if 'operations_per_second' in metrics:
                threshold = self.alert_thresholds['operations_per_second']
                if metrics['operations_per_second'] > threshold:
                    new_alerts.append({
                        'type': 'HIGH_OPERATIONS_RATE',
                        'severity': 'WARNING',
                        'message': f"Operations rate is {metrics['operations_per_second']} ops/sec (threshold: {threshold})",
                        'value': metrics['operations_per_second'],
                        'threshold': threshold,
                        'timestamp': datetime.utcnow()
                    })
            
            # Process new alerts
            for alert in new_alerts:
                # Check if this alert is already active
                is_duplicate = any(
                    active_alert['type'] == alert['type'] 
                    for active_alert in self._active_alerts
                )
                
                if not is_duplicate:
                    self._active_alerts.append(alert)
                    self._alert_history.append(alert)
                    
                    self.logger.logger.warning(
                        f"Alert triggered: {alert['message']}",
                        extra={
                            'alert_type': alert['type'],
                            'severity': alert['severity'],
                            'value': alert['value'],
                            'threshold': alert['threshold']
                        }
                    )
            
            # Clean up resolved alerts (simplified - in production you'd want more sophisticated logic)
            self._active_alerts = [
                alert for alert in self._active_alerts 
                if (datetime.utcnow() - alert['timestamp']).total_seconds() < 300  # 5 minutes
            ]
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'check_alerts'})
    
    async def get_performance_report(self, hours: int = 1) -> Dict[str, Any]:
        """Generate performance report for specified time period."""
        try:
            # Calculate time range
            end_time = time.time()
            start_time = end_time - (hours * 3600)
            
            # Filter metrics by time range
            metrics_in_range = self._get_metrics_in_range(start_time, end_time)
            
            if not metrics_in_range:
                return {'error': 'No metrics available for the specified time range'}
            
            # Calculate statistics
            report = {
                'time_range': {
                    'start': datetime.fromtimestamp(start_time).isoformat(),
                    'end': datetime.fromtimestamp(end_time).isoformat(),
                    'duration_hours': hours
                },
                'data_points': len(metrics_in_range['timestamp']),
                'metrics': {}
            }
            
            # Calculate statistics for each metric
            for metric_name, values in metrics_in_range.items():
                if metric_name != 'timestamp' and values:
                    report['metrics'][metric_name] = {
                        'avg': sum(values) / len(values),
                        'min': min(values),
                        'max': max(values),
                        'latest': values[-1] if values else None
                    }
            
            # Add trend analysis
            report['trends'] = await self._analyze_trends(metrics_in_range)
            
            # Add bottleneck analysis
            report['bottlenecks'] = await self._detect_bottlenecks(metrics_in_range)
            
            # Add alerts summary
            report['alerts'] = {
                'active_count': len(self._active_alerts),
                'total_in_period': len([
                    alert for alert in self._alert_history
                    if (datetime.utcnow() - alert['timestamp']).total_seconds() <= hours * 3600
                ])
            }
            
            return report
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'get_performance_report'})
            return {'error': f'Failed to generate report: {str(e)}'}
    
    def _get_metrics_in_range(self, start_time: float, end_time: float) -> Dict[str, List]:
        """Get metrics within specified time range."""
        filtered_metrics = {}
        
        # Find indices within time range
        timestamps = list(self._metrics_history['timestamp'])
        start_idx = None
        end_idx = None
        
        for i, ts in enumerate(timestamps):
            if start_idx is None and ts >= start_time:
                start_idx = i
            if ts <= end_time:
                end_idx = i
        
        if start_idx is None or end_idx is None:
            return {}
        
        # Extract metrics in range
        for metric_name, values in self._metrics_history.items():
            values_list = list(values)
            filtered_metrics[metric_name] = values_list[start_idx:end_idx + 1]
        
        return filtered_metrics
    
    async def _analyze_trends(self, metrics: Dict[str, List]) -> Dict[str, str]:
        """Analyze trends in metrics."""
        trends = {}
        
        try:
            for metric_name, values in metrics.items():
                if metric_name == 'timestamp' or len(values) < 2:
                    continue
                
                # Simple trend analysis (linear regression would be better)
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                first_avg = sum(first_half) / len(first_half) if first_half else 0
                second_avg = sum(second_half) / len(second_half) if second_half else 0
                
                if second_avg > first_avg * 1.1:
                    trends[metric_name] = 'INCREASING'
                elif second_avg < first_avg * 0.9:
                    trends[metric_name] = 'DECREASING'
                else:
                    trends[metric_name] = 'STABLE'
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'analyze_trends'})
        
        return trends
    
    async def _detect_bottlenecks(self, metrics: Dict[str, List]) -> List[Dict[str, Any]]:
        """Detect performance bottlenecks."""
        bottlenecks = []
        
        try:
            # High memory usage bottleneck
            if 'memory_usage_percentage' in metrics:
                values = metrics['memory_usage_percentage']
                if values and max(values) > 90:
                    bottlenecks.append({
                        'type': 'MEMORY_BOTTLENECK',
                        'description': 'High memory usage detected',
                        'max_value': max(values),
                        'recommendation': 'Consider increasing memory or optimizing data structures'
                    })
            
            # High latency bottleneck
            if 'avg_latency_ms' in metrics:
                values = metrics['avg_latency_ms']
                if values and max(values) > 200:
                    bottlenecks.append({
                        'type': 'LATENCY_BOTTLENECK',
                        'description': 'High latency detected',
                        'max_value': max(values),
                        'recommendation': 'Check network connectivity and Redis configuration'
                    })
            
            # Low hit rate bottleneck
            if 'hit_rate_percentage' in metrics:
                values = metrics['hit_rate_percentage']
                if values and min(values) < 70:
                    bottlenecks.append({
                        'type': 'CACHE_EFFICIENCY_BOTTLENECK',
                        'description': 'Low cache hit rate detected',
                        'min_value': min(values),
                        'recommendation': 'Review caching strategy and key patterns'
                    })
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'detect_bottlenecks'})
        
        return bottlenecks
    
    async def _establish_performance_baselines(self) -> None:
        """Establish performance baselines."""
        try:
            # Collect initial metrics
            metrics = await self.collect_metrics()
            
            # Set baselines (in production, you'd want historical data)
            self._performance_baselines = {
                'memory_usage_bytes': metrics.get('memory_usage_bytes', 0),
                'operations_per_second': metrics.get('operations_per_second', 0),
                'hit_rate_percentage': metrics.get('hit_rate_percentage', 100),
                'avg_latency_ms': metrics.get('avg_latency_ms', 0)
            }
            
            self.logger.logger.info("Performance baselines established")
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'establish_baselines'})
    
    async def _start_monitoring_tasks(self) -> None:
        """Start background monitoring tasks."""
        self._collection_task = asyncio.create_task(self._metrics_collection_loop())
        self._analysis_task = asyncio.create_task(self._analysis_loop())
    
    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop."""
        while not self._shutdown_event.is_set():
            try:
                await self.collect_metrics()
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'metrics_collection_loop'})
                await asyncio.sleep(self.collection_interval)
    
    async def _analysis_loop(self) -> None:
        """Background analysis loop."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Run analysis every minute
                
                # Perform periodic analysis
                await self._periodic_analysis()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'analysis_loop'})
    
    async def _periodic_analysis(self) -> None:
        """Perform periodic analysis and optimization recommendations."""
        try:
            # Generate performance report for last hour
            report = await self.get_performance_report(hours=1)
            
            # Log performance summary
            if 'metrics' in report:
                self.logger.logger.info(
                    "Performance summary",
                    extra={
                        'memory_usage': report['metrics'].get('memory_usage_bytes', {}).get('avg', 0),
                        'operations_per_second': report['metrics'].get('operations_per_second', {}).get('avg', 0),
                        'hit_rate': report['metrics'].get('hit_rate_percentage', {}).get('avg', 0),
                        'avg_latency_ms': report['metrics'].get('avg_latency_ms', {}).get('avg', 0),
                        'active_alerts': len(self._active_alerts)
                    }
                )
        
        except Exception as e:
            self.logger.log_error(e, {'operation': 'periodic_analysis'})
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        return self._current_metrics.copy()
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get currently active alerts."""
        return self._active_alerts.copy()
    
    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history for specified period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            alert for alert in self._alert_history
            if alert['timestamp'] > cutoff_time
        ]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get monitoring system metrics."""
        return {
            'collection_interval': self.collection_interval,
            'data_points_stored': len(self._metrics_history['timestamp']),
            'retention_hours': self.retention_hours,
            'active_alerts': len(self._active_alerts),
            'total_alerts_in_history': len(self._alert_history),
            'monitoring_uptime_seconds': time.time() - (self._metrics_history['timestamp'][0] if self._metrics_history['timestamp'] else time.time())
        }
    
    async def export_metrics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        format_type: str = 'json'
    ) -> str:
        """Export metrics data."""
        try:
            # Default time range (last 24 hours)
            if not start_time:
                start_time = datetime.utcnow() - timedelta(hours=24)
            if not end_time:
                end_time = datetime.utcnow()
            
            # Get metrics in range
            start_ts = start_time.timestamp()
            end_ts = end_time.timestamp()
            metrics_data = self._get_metrics_in_range(start_ts, end_ts)
            
            if format_type == 'json':
                return json.dumps({
                    'export_info': {
                        'start_time': start_time.isoformat(),
                        'end_time': end_time.isoformat(),
                        'data_points': len(metrics_data.get('timestamp', [])),
                        'exported_at': datetime.utcnow().isoformat()
                    },
                    'metrics': metrics_data
                }, indent=2, default=str)
            else:
                raise MAOSError(f"Unsupported export format: {format_type}")
            
        except Exception as e:
            self.logger.log_error(e, {'operation': 'export_metrics'})
            return json.dumps({'error': f'Export failed: {str(e)}'})
    
    async def shutdown(self) -> None:
        """Shutdown monitoring system."""
        self.logger.logger.info("Shutting down Redis State Monitor")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel background tasks
        tasks = [self._collection_task, self._analysis_task]
        for task in tasks:
            if task:
                task.cancel()
        
        # Wait for tasks to complete
        if tasks:
            await asyncio.gather(*[t for t in tasks if t], return_exceptions=True)
        
        # Clear data
        for deque_obj in self._metrics_history.values():
            deque_obj.clear()
        
        self._current_metrics.clear()
        self._active_alerts.clear()
        self._alert_history.clear()
        
        self.logger.logger.info("Redis State Monitor shutdown completed")