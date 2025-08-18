"""
Alert Manager for MAOS monitoring system.
"""

import asyncio
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from uuid import uuid4

from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"


@dataclass
class Alert:
    """Represents an alert."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    severity: AlertSeverity = AlertSeverity.MEDIUM
    status: AlertStatus = AlertStatus.ACTIVE
    component: str = ""
    metric_name: str = ""
    metric_value: float = 0.0
    threshold: float = 0.0
    condition: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "severity": self.severity.value,
            "status": self.status.value,
            "component": self.component,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
            "condition": self.condition,
            "labels": self.labels,
            "annotations": self.annotations,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "acknowledged_by": self.acknowledged_by,
            "duration_seconds": (datetime.utcnow() - self.created_at).total_seconds()
        }
    
    def acknowledge(self, user: Optional[str] = None) -> None:
        """Acknowledge the alert."""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_at = datetime.utcnow()
        self.acknowledged_by = user
        self.updated_at = datetime.utcnow()
    
    def resolve(self) -> None:
        """Resolve the alert."""
        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def suppress(self) -> None:
        """Suppress the alert."""
        self.status = AlertStatus.SUPPRESSED
        self.updated_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """Check if alert is active."""
        return self.status == AlertStatus.ACTIVE


@dataclass
class AlertRule:
    """Defines an alert rule."""
    name: str
    description: str
    metric_name: str
    condition: str  # "gt", "lt", "eq", "ne", "gte", "lte"
    threshold: float
    severity: AlertSeverity
    component: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    evaluation_interval: float = 60.0  # seconds
    for_duration: float = 0.0  # seconds alert must be true before firing
    enabled: bool = True
    
    def evaluate(self, metric_value: float) -> bool:
        """Evaluate if the rule should trigger."""
        if not self.enabled:
            return False
        
        if self.condition == "gt":
            return metric_value > self.threshold
        elif self.condition == "lt":
            return metric_value < self.threshold
        elif self.condition == "eq":
            return metric_value == self.threshold
        elif self.condition == "ne":
            return metric_value != self.threshold
        elif self.condition == "gte":
            return metric_value >= self.threshold
        elif self.condition == "lte":
            return metric_value <= self.threshold
        else:
            return False
    
    def create_alert(self, metric_value: float) -> Alert:
        """Create an alert from this rule."""
        description = f"{self.description} (Value: {metric_value}, Threshold: {self.threshold})"
        
        return Alert(
            name=self.name,
            description=description,
            severity=self.severity,
            component=self.component,
            metric_name=self.metric_name,
            metric_value=metric_value,
            threshold=self.threshold,
            condition=self.condition,
            labels=self.labels.copy(),
            annotations=self.annotations.copy()
        )


class AlertManager:
    """
    Manages alerts, rules, and notifications for MAOS monitoring.
    """
    
    def __init__(
        self,
        evaluation_interval: float = 30.0,
        max_alerts: int = 10000,
        alert_retention_hours: int = 168  # 1 week
    ):
        """Initialize alert manager."""
        self.evaluation_interval = evaluation_interval
        self.max_alerts = max_alerts
        self.alert_retention_hours = alert_retention_hours
        
        self.logger = MAOSLogger("alert_manager", str(uuid4()))
        
        # Alert storage
        self._active_alerts: Dict[str, Alert] = {}
        self._resolved_alerts: Dict[str, Alert] = {}
        self._alert_history: List[Alert] = []
        
        # Alert rules
        self._alert_rules: Dict[str, AlertRule] = {}
        
        # Notification channels
        self._notification_channels: List[Any] = []
        
        # Background evaluation
        self._evaluation_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Metrics source (will be injected)
        self._metrics_collector = None
        self._health_manager = None
        
        # Alert suppression
        self._suppressed_rules: Set[str] = set()
        self._suppression_expiry: Dict[str, datetime] = {}
        
        # Escalation tracking
        self._escalation_tracking: Dict[str, Dict[str, Any]] = {}
        
        # Alert grouping
        self._alert_groups: Dict[str, List[str]] = {}
        
        # Rate limiting
        self._rate_limits: Dict[str, Dict[str, Any]] = {}
    
    def register_metrics_collector(self, metrics_collector: Any) -> None:
        """Register metrics collector for alert evaluation."""
        self._metrics_collector = metrics_collector
        self.logger.logger.info("Registered metrics collector for alert evaluation")
    
    def register_health_manager(self, health_manager: Any) -> None:
        """Register health manager for health-based alerts."""
        self._health_manager = health_manager
        self.logger.logger.info("Registered health manager for alert evaluation")
    
    def add_notification_channel(self, channel: Any) -> None:
        """Add notification channel."""
        self._notification_channels.append(channel)
        self.logger.logger.info(f"Added notification channel: {type(channel).__name__}")
    
    def remove_notification_channel(self, channel: Any) -> None:
        """Remove notification channel."""
        if channel in self._notification_channels:
            self._notification_channels.remove(channel)
            self.logger.logger.info(f"Removed notification channel: {type(channel).__name__}")
    
    def add_alert_rule(self, rule: AlertRule) -> None:
        """Add alert rule."""
        self._alert_rules[rule.name] = rule
        self.logger.logger.info(f"Added alert rule: {rule.name}")
    
    def remove_alert_rule(self, rule_name: str) -> None:
        """Remove alert rule."""
        if rule_name in self._alert_rules:
            del self._alert_rules[rule_name]
            self.logger.logger.info(f"Removed alert rule: {rule_name}")
    
    def enable_rule(self, rule_name: str) -> None:
        """Enable an alert rule."""
        if rule_name in self._alert_rules:
            self._alert_rules[rule_name].enabled = True
            self.logger.logger.info(f"Enabled alert rule: {rule_name}")
    
    def disable_rule(self, rule_name: str) -> None:
        """Disable an alert rule."""
        if rule_name in self._alert_rules:
            self._alert_rules[rule_name].enabled = False
            self.logger.logger.info(f"Disabled alert rule: {rule_name}")
    
    def suppress_rule(self, rule_name: str, duration_hours: float = 1.0) -> None:
        """Suppress an alert rule for a duration."""
        self._suppressed_rules.add(rule_name)
        self._suppression_expiry[rule_name] = datetime.utcnow() + timedelta(hours=duration_hours)
        
        self.logger.logger.info(f"Suppressed alert rule: {rule_name} for {duration_hours} hours")
    
    def unsuppress_rule(self, rule_name: str) -> None:
        """Remove suppression from an alert rule."""
        self._suppressed_rules.discard(rule_name)
        if rule_name in self._suppression_expiry:
            del self._suppression_expiry[rule_name]
        
        self.logger.logger.info(f"Removed suppression from alert rule: {rule_name}")
    
    async def start_evaluation(self) -> None:
        """Start alert rule evaluation."""
        self.logger.logger.info("Starting alert rule evaluation")
        
        self._shutdown_event.clear()
        self._evaluation_task = asyncio.create_task(self._evaluation_loop())
    
    async def stop_evaluation(self) -> None:
        """Stop alert rule evaluation."""
        self.logger.logger.info("Stopping alert rule evaluation")
        
        self._shutdown_event.set()
        
        if self._evaluation_task:
            self._evaluation_task.cancel()
            try:
                await self._evaluation_task
            except asyncio.CancelledError:
                pass
    
    async def _evaluation_loop(self) -> None:
        """Main evaluation loop."""
        while not self._shutdown_event.is_set():
            try:
                await self._evaluate_rules()
                await self._cleanup_expired_suppressions()
                await self._cleanup_old_alerts()
                
                await asyncio.sleep(self.evaluation_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {"operation": "alert_evaluation_loop"})
                await asyncio.sleep(self.evaluation_interval)
    
    async def _evaluate_rules(self) -> None:
        """Evaluate all alert rules."""
        if not self._metrics_collector and not self._health_manager:
            return
        
        for rule_name, rule in self._alert_rules.items():
            try:
                if not rule.enabled or rule_name in self._suppressed_rules:
                    continue
                
                # Get metric value
                metric_value = await self._get_metric_value(rule.metric_name)
                if metric_value is None:
                    continue
                
                # Evaluate rule
                should_alert = rule.evaluate(metric_value)
                existing_alert = self._find_existing_alert(rule_name, rule.component)
                
                if should_alert and not existing_alert:
                    # Create new alert
                    alert = rule.create_alert(metric_value)
                    await self._fire_alert(alert)
                    
                elif not should_alert and existing_alert and existing_alert.is_active():
                    # Resolve existing alert
                    await self._resolve_alert(existing_alert.id)
                
                elif existing_alert and existing_alert.is_active():
                    # Update existing alert value
                    existing_alert.metric_value = metric_value
                    existing_alert.updated_at = datetime.utcnow()
                
            except Exception as e:
                self.logger.log_error(e, {
                    "operation": "evaluate_rule",
                    "rule_name": rule_name
                })
    
    async def _get_metric_value(self, metric_name: str) -> Optional[float]:
        """Get current value for a metric."""
        try:
            # Try to get from metrics collector first
            if self._metrics_collector and hasattr(self._metrics_collector, 'get_metric_value'):
                value = await self._metrics_collector.get_metric_value(metric_name)
                if value is not None:
                    return float(value)
            
            # Try to get from health manager
            if self._health_manager:
                metrics = self._health_manager.get_health_metrics()
                
                # System metrics
                if metric_name in metrics.get("system_metrics", {}):
                    return float(metrics["system_metrics"][metric_name])
                
                # Component metrics
                if metric_name in metrics.get("component_metrics", {}):
                    return float(metrics["component_metrics"][metric_name])
            
            return None
            
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "get_metric_value",
                "metric_name": metric_name
            })
            return None
    
    def _find_existing_alert(self, rule_name: str, component: str) -> Optional[Alert]:
        """Find existing alert for a rule and component."""
        for alert in self._active_alerts.values():
            if alert.name == rule_name and alert.component == component:
                return alert
        return None
    
    async def _fire_alert(self, alert: Alert) -> None:
        """Fire a new alert."""
        self.logger.logger.warning(
            f"Alert fired: {alert.name}",
            extra={
                "alert_id": alert.id,
                "severity": alert.severity.value,
                "component": alert.component,
                "metric_value": alert.metric_value,
                "threshold": alert.threshold
            }
        )
        
        # Store alert
        self._active_alerts[alert.id] = alert
        self._alert_history.append(alert)
        
        # Limit alert history
        if len(self._alert_history) > self.max_alerts:
            self._alert_history.pop(0)
        
        # Send notifications
        await self._send_notifications(alert, "fired")
        
        # Set up escalation if needed
        await self._setup_escalation(alert)
    
    async def _resolve_alert(self, alert_id: str) -> None:
        """Resolve an alert."""
        if alert_id not in self._active_alerts:
            return
        
        alert = self._active_alerts[alert_id]
        alert.resolve()
        
        self.logger.logger.info(
            f"Alert resolved: {alert.name}",
            extra={
                "alert_id": alert.id,
                "duration_seconds": (alert.resolved_at - alert.created_at).total_seconds()
            }
        )
        
        # Move to resolved alerts
        self._resolved_alerts[alert_id] = alert
        del self._active_alerts[alert_id]
        
        # Send notifications
        await self._send_notifications(alert, "resolved")
        
        # Cancel escalation
        if alert_id in self._escalation_tracking:
            del self._escalation_tracking[alert_id]
    
    async def _send_notifications(self, alert: Alert, action: str) -> None:
        """Send notifications through all channels."""
        for channel in self._notification_channels:
            try:
                await channel.send_alert(alert, action)
            except Exception as e:
                self.logger.log_error(e, {
                    "operation": "send_notification",
                    "channel": type(channel).__name__,
                    "alert_id": alert.id
                })
    
    async def _setup_escalation(self, alert: Alert) -> None:
        """Setup alert escalation if needed."""
        if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            escalation_delay = 300 if alert.severity == AlertSeverity.HIGH else 120  # seconds
            
            self._escalation_tracking[alert.id] = {
                "escalate_at": datetime.utcnow() + timedelta(seconds=escalation_delay),
                "escalated": False
            }
    
    async def _cleanup_expired_suppressions(self) -> None:
        """Clean up expired rule suppressions."""
        now = datetime.utcnow()
        expired_rules = [
            rule_name for rule_name, expiry_time in self._suppression_expiry.items()
            if now > expiry_time
        ]
        
        for rule_name in expired_rules:
            self.unsuppress_rule(rule_name)
    
    async def _cleanup_old_alerts(self) -> None:
        """Clean up old resolved alerts."""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.alert_retention_hours)
        
        # Remove old resolved alerts
        expired_alerts = [
            alert_id for alert_id, alert in self._resolved_alerts.items()
            if alert.resolved_at and alert.resolved_at < cutoff_time
        ]
        
        for alert_id in expired_alerts:
            del self._resolved_alerts[alert_id]
    
    # Public API methods
    
    async def acknowledge_alert(self, alert_id: str, user: Optional[str] = None) -> bool:
        """Acknowledge an alert."""
        if alert_id in self._active_alerts:
            alert = self._active_alerts[alert_id]
            alert.acknowledge(user)
            
            self.logger.logger.info(f"Alert acknowledged: {alert.name}", extra={
                "alert_id": alert_id,
                "acknowledged_by": user
            })
            
            await self._send_notifications(alert, "acknowledged")
            return True
        
        return False
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active alerts."""
        alerts = list(self._active_alerts.values())
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        return sorted(alerts, key=lambda a: a.created_at, reverse=True)
    
    def get_resolved_alerts(self, hours: int = 24) -> List[Alert]:
        """Get recently resolved alerts."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            alert for alert in self._resolved_alerts.values()
            if alert.resolved_at and alert.resolved_at > cutoff_time
        ]
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            alert for alert in self._alert_history
            if alert.created_at > cutoff_time
        ]
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        
        # Count alerts by severity
        active_by_severity = {}
        for severity in AlertSeverity:
            active_by_severity[severity.value] = len([
                a for a in self._active_alerts.values() 
                if a.severity == severity
            ])
        
        # Count recent alerts
        recent_alerts = [a for a in self._alert_history if a.created_at > last_24h]
        recent_by_severity = {}
        for severity in AlertSeverity:
            recent_by_severity[severity.value] = len([
                a for a in recent_alerts if a.severity == severity
            ])
        
        return {
            "active_alerts_count": len(self._active_alerts),
            "resolved_alerts_count": len(self._resolved_alerts),
            "total_rules": len(self._alert_rules),
            "enabled_rules": len([r for r in self._alert_rules.values() if r.enabled]),
            "suppressed_rules": len(self._suppressed_rules),
            "notification_channels": len(self._notification_channels),
            "active_alerts_by_severity": active_by_severity,
            "recent_alerts_by_severity": recent_by_severity,
            "alerts_last_24h": len(recent_alerts)
        }