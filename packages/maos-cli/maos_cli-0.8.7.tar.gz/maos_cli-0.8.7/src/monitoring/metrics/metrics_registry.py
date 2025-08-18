"""
Centralized metrics registry for MAOS monitoring.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from ...maos.utils.logging_config import MAOSLogger


@dataclass
class MetricDefinition:
    """Definition of a custom metric."""
    name: str
    metric_type: str  # counter, gauge, histogram, summary
    description: str
    labels: List[str]
    buckets: Optional[List[float]] = None  # For histograms


class MetricsRegistry:
    """
    Registry for custom MAOS metrics and their collection functions.
    """
    
    def __init__(self):
        """Initialize metrics registry."""
        self.logger = MAOSLogger("metrics_registry", str(uuid4()))
        
        # Metric definitions
        self._metric_definitions: Dict[str, MetricDefinition] = {}
        
        # Metric collectors (functions that collect metric values)
        self._metric_collectors: Dict[str, Callable[[], Any]] = {}
        
        # Custom metric values cache
        self._metric_cache: Dict[str, Any] = {}
        
        # Metric metadata
        self._metric_metadata: Dict[str, Dict[str, Any]] = {}
    
    def register_metric(
        self,
        name: str,
        metric_type: str,
        description: str,
        labels: Optional[List[str]] = None,
        buckets: Optional[List[float]] = None,
        collector: Optional[Callable[[], Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a custom metric.
        
        Args:
            name: Metric name
            metric_type: Type (counter, gauge, histogram, summary)
            description: Metric description
            labels: Label names
            buckets: Histogram buckets (if applicable)
            collector: Function to collect metric value
            metadata: Additional metadata
        """
        self.logger.logger.info(f"Registering metric: {name}")
        
        # Create metric definition
        metric_def = MetricDefinition(
            name=name,
            metric_type=metric_type,
            description=description,
            labels=labels or [],
            buckets=buckets
        )
        
        self._metric_definitions[name] = metric_def
        
        # Register collector if provided
        if collector:
            self._metric_collectors[name] = collector
        
        # Store metadata
        if metadata:
            self._metric_metadata[name] = metadata
    
    def register_collector(self, metric_name: str, collector: Callable[[], Any]) -> None:
        """Register a collector function for a metric."""
        if metric_name not in self._metric_definitions:
            raise ValueError(f"Metric not registered: {metric_name}")
        
        self._metric_collectors[metric_name] = collector
        self.logger.logger.info(f"Registered collector for metric: {metric_name}")
    
    def unregister_metric(self, name: str) -> None:
        """Unregister a metric."""
        if name in self._metric_definitions:
            del self._metric_definitions[name]
        
        if name in self._metric_collectors:
            del self._metric_collectors[name]
        
        if name in self._metric_cache:
            del self._metric_cache[name]
        
        if name in self._metric_metadata:
            del self._metric_metadata[name]
        
        self.logger.logger.info(f"Unregistered metric: {name}")
    
    def get_metric_definition(self, name: str) -> Optional[MetricDefinition]:
        """Get metric definition."""
        return self._metric_definitions.get(name)
    
    def get_all_metrics(self) -> Dict[str, MetricDefinition]:
        """Get all registered metric definitions."""
        return self._metric_definitions.copy()
    
    def collect_metric(self, name: str) -> Any:
        """Collect value for a specific metric."""
        if name not in self._metric_collectors:
            return None
        
        try:
            collector = self._metric_collectors[name]
            value = collector()
            
            # Cache the value
            self._metric_cache[name] = {
                "value": value,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return value
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "collect_metric", "metric": name})
            return None
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect values for all registered metrics."""
        results = {}
        
        for metric_name in self._metric_collectors.keys():
            value = self.collect_metric(metric_name)
            if value is not None:
                results[metric_name] = value
        
        return results
    
    def get_cached_value(self, name: str) -> Optional[Any]:
        """Get cached metric value."""
        cached = self._metric_cache.get(name)
        return cached["value"] if cached else None
    
    def get_metric_metadata(self, name: str) -> Dict[str, Any]:
        """Get metric metadata."""
        return self._metric_metadata.get(name, {})
    
    def update_metric_metadata(self, name: str, metadata: Dict[str, Any]) -> None:
        """Update metric metadata."""
        if name not in self._metric_definitions:
            raise ValueError(f"Metric not registered: {name}")
        
        if name not in self._metric_metadata:
            self._metric_metadata[name] = {}
        
        self._metric_metadata[name].update(metadata)
    
    def get_metrics_by_type(self, metric_type: str) -> Dict[str, MetricDefinition]:
        """Get all metrics of a specific type."""
        return {
            name: definition
            for name, definition in self._metric_definitions.items()
            if definition.metric_type == metric_type
        }
    
    def get_metrics_with_label(self, label_name: str) -> Dict[str, MetricDefinition]:
        """Get all metrics that have a specific label."""
        return {
            name: definition
            for name, definition in self._metric_definitions.items()
            if label_name in definition.labels
        }