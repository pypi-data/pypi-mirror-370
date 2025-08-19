"""Advanced DDoS detection and mitigation."""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, Counter
import aioredis
import numpy as np

logger = logging.getLogger(__name__)


class AttackType(Enum):
    """Types of DDoS attacks."""
    VOLUMETRIC = "volumetric"
    PROTOCOL = "protocol"
    APPLICATION = "application"
    SLOWLORIS = "slowloris"
    AMPLIFICATION = "amplification"


class AttackSeverity(Enum):
    """Attack severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AttackPattern:
    """Detected attack pattern."""
    attack_id: str
    attack_type: AttackType
    severity: AttackSeverity
    source_ips: Set[str]
    start_time: datetime
    end_time: Optional[datetime] = None
    request_rate: float = 0.0
    unique_endpoints: int = 0
    user_agents: Set[str] = field(default_factory=set)
    geographic_diversity: float = 0.0
    confidence_score: float = 0.0
    mitigations_applied: List[str] = field(default_factory=list)
    
    def is_active(self) -> bool:
        """Check if attack is still active."""
        return self.end_time is None


@dataclass
class RequestMetrics:
    """Request metrics for analysis."""
    timestamp: datetime
    ip: str
    endpoint: str
    user_agent: str
    response_time: float
    status_code: int
    payload_size: int


class DDoSDetector:
    """Advanced DDoS detection using statistical analysis and ML techniques."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        redis_db: int = 10,
        analysis_window_minutes: int = 5,
        baseline_samples: int = 100,
        anomaly_threshold: float = 3.0,  # Standard deviations
        min_requests_for_analysis: int = 50
    ):
        self.redis_url = redis_url
        self.redis_db = redis_db
        self.analysis_window_minutes = analysis_window_minutes
        self.baseline_samples = baseline_samples
        self.anomaly_threshold = anomaly_threshold
        self.min_requests_for_analysis = min_requests_for_analysis
        
        # Redis connection
        self.redis: Optional[aioredis.Redis] = None
        
        # Request metrics buffer
        self.request_buffer: deque = deque(maxlen=1000)
        self.baseline_metrics: Dict[str, List[float]] = {
            "request_rate": deque(maxlen=self.baseline_samples),
            "unique_ips": deque(maxlen=self.baseline_samples),
            "avg_response_time": deque(maxlen=self.baseline_samples),
            "error_rate": deque(maxlen=self.baseline_samples)
        }
        
        # Active attacks
        self.active_attacks: Dict[str, AttackPattern] = {}
        
        # IP tracking
        self.ip_statistics: Dict[str, Dict[str, Any]] = {}
        
        # Background tasks
        self._analysis_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Detection rules
        self.detection_rules = {
            "volumetric": {
                "request_rate_multiplier": 10.0,
                "unique_ip_threshold": 100,
                "min_requests_per_ip": 10
            },
            "application": {
                "error_rate_threshold": 0.5,
                "slow_request_threshold": 5.0,  # seconds
                "suspicious_endpoint_patterns": [
                    "/admin/", "/wp-admin/", "/.env", "/api/debug"
                ]
            },
            "slowloris": {
                "connection_timeout_threshold": 30.0,
                "concurrent_connections_per_ip": 50
            }
        }
        
        # Metrics
        self.metrics = {
            "requests_analyzed": 0,
            "attacks_detected": 0,
            "false_positives": 0,
            "ips_blocked": 0,
            "mitigations_applied": 0
        }
        
        logger.info("DDoS detector initialized")
    
    async def connect(self):
        """Connect to Redis and start analysis."""
        try:
            self.redis = aioredis.from_url(
                self.redis_url,
                db=self.redis_db,
                decode_responses=True
            )
            
            # Test connection
            await self.redis.ping()
            
            # Start analysis task
            self._running = True
            self._analysis_task = asyncio.create_task(self._analysis_loop())
            
            logger.info("DDoS detector connected and analysis started")
            
        except Exception as e:
            logger.error(f"Failed to connect DDoS detector: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect and stop analysis."""
        self._running = False
        
        if self._analysis_task:
            self._analysis_task.cancel()
            try:
                await self._analysis_task
            except asyncio.CancelledError:
                pass
        
        if self.redis:
            await self.redis.close()
            logger.info("DDoS detector disconnected")
    
    async def record_request(self, request_metrics: RequestMetrics):
        """Record request for analysis."""
        try:
            self.request_buffer.append(request_metrics)
            self.metrics["requests_analyzed"] += 1
            
            # Update IP statistics
            await self._update_ip_statistics(request_metrics)
            
        except Exception as e:
            logger.error(f"Failed to record request: {e}")
    
    async def _update_ip_statistics(self, metrics: RequestMetrics):
        """Update statistics for IP address."""
        try:
            ip = metrics.ip
            current_time = datetime.now(timezone.utc)
            
            if ip not in self.ip_statistics:
                self.ip_statistics[ip] = {
                    "request_count": 0,
                    "first_seen": current_time,
                    "last_seen": current_time,
                    "endpoints": set(),
                    "user_agents": set(),
                    "status_codes": Counter(),
                    "response_times": [],
                    "request_rate": 0.0
                }
            
            stats = self.ip_statistics[ip]
            stats["request_count"] += 1
            stats["last_seen"] = current_time
            stats["endpoints"].add(metrics.endpoint)
            stats["user_agents"].add(metrics.user_agent)
            stats["status_codes"][metrics.status_code] += 1
            stats["response_times"].append(metrics.response_time)
            
            # Keep only recent response times
            if len(stats["response_times"]) > 100:
                stats["response_times"] = stats["response_times"][-100:]
            
            # Calculate request rate (requests per minute)
            time_window = (current_time - stats["first_seen"]).total_seconds() / 60
            if time_window > 0:
                stats["request_rate"] = stats["request_count"] / time_window
            
        except Exception as e:
            logger.error(f"Failed to update IP statistics: {e}")
    
    async def _analysis_loop(self):
        """Background analysis loop."""
        try:
            while self._running:
                await asyncio.sleep(60)  # Analyze every minute
                
                try:
                    await self._analyze_traffic_patterns()
                    await self._check_active_attacks()
                    await self._cleanup_old_data()
                    
                except Exception as e:
                    logger.error(f"Analysis loop error: {e}")
                    
        except asyncio.CancelledError:
            logger.info("DDoS analysis loop cancelled")
            raise
    
    async def _analyze_traffic_patterns(self):
        """Analyze current traffic patterns for anomalies."""
        try:
            if len(self.request_buffer) < self.min_requests_for_analysis:
                return
            
            current_time = datetime.now(timezone.utc)
            window_start = current_time - timedelta(minutes=self.analysis_window_minutes)
            
            # Filter recent requests
            recent_requests = [
                req for req in self.request_buffer
                if req.timestamp >= window_start
            ]
            
            if not recent_requests:
                return
            
            # Calculate current metrics
            current_metrics = await self._calculate_current_metrics(recent_requests)
            
            # Update baseline
            self._update_baseline(current_metrics)
            
            # Detect anomalies
            anomalies = await self._detect_anomalies(current_metrics)
            
            # Check for attack patterns
            if anomalies:
                await self._analyze_attack_patterns(recent_requests, anomalies)
            
        except Exception as e:
            logger.error(f"Traffic analysis error: {e}")
    
    async def _calculate_current_metrics(self, requests: List[RequestMetrics]) -> Dict[str, float]:
        """Calculate current traffic metrics."""
        try:
            if not requests:
                return {}
            
            # Basic metrics
            request_count = len(requests)
            unique_ips = len(set(req.ip for req in requests))
            unique_endpoints = len(set(req.endpoint for req in requests))
            
            # Request rate (per minute)
            time_span = (requests[-1].timestamp - requests[0].timestamp).total_seconds() / 60
            request_rate = request_count / max(time_span, 1.0)
            
            # Response time metrics
            response_times = [req.response_time for req in requests]
            avg_response_time = np.mean(response_times)
            
            # Error rate
            error_count = sum(1 for req in requests if req.status_code >= 400)
            error_rate = error_count / request_count
            
            # Payload size metrics
            payload_sizes = [req.payload_size for req in requests]
            avg_payload_size = np.mean(payload_sizes)
            
            return {
                "request_rate": request_rate,
                "unique_ips": unique_ips,
                "unique_endpoints": unique_endpoints,
                "avg_response_time": avg_response_time,
                "error_rate": error_rate,
                "avg_payload_size": avg_payload_size
            }
            
        except Exception as e:
            logger.error(f"Metrics calculation error: {e}")
            return {}
    
    def _update_baseline(self, current_metrics: Dict[str, float]):
        """Update baseline metrics for anomaly detection."""
        try:
            for metric_name, value in current_metrics.items():
                if metric_name in self.baseline_metrics:
                    self.baseline_metrics[metric_name].append(value)
                    
        except Exception as e:
            logger.error(f"Baseline update error: {e}")
    
    async def _detect_anomalies(self, current_metrics: Dict[str, float]) -> List[str]:
        """Detect statistical anomalies in current metrics."""
        try:
            anomalies = []
            
            for metric_name, current_value in current_metrics.items():
                if metric_name not in self.baseline_metrics:
                    continue
                
                baseline_values = list(self.baseline_metrics[metric_name])
                if len(baseline_values) < 10:  # Need enough samples
                    continue
                
                # Calculate z-score
                baseline_mean = np.mean(baseline_values)
                baseline_std = np.std(baseline_values)
                
                if baseline_std == 0:
                    continue
                
                z_score = abs((current_value - baseline_mean) / baseline_std)
                
                if z_score > self.anomaly_threshold:
                    anomalies.append(f"{metric_name}_anomaly")
                    logger.warning(f"Anomaly detected in {metric_name}: current={current_value:.2f}, baseline_mean={baseline_mean:.2f}, z_score={z_score:.2f}")
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            return []
    
    async def _analyze_attack_patterns(
        self,
        requests: List[RequestMetrics],
        anomalies: List[str]
    ):
        """Analyze requests for specific attack patterns."""
        try:
            # Volumetric attack detection
            if "request_rate_anomaly" in anomalies:
                await self._detect_volumetric_attack(requests)
            
            # Application layer attack detection
            if "error_rate_anomaly" in anomalies or "avg_response_time_anomaly" in anomalies:
                await self._detect_application_attack(requests)
            
            # Slowloris attack detection
            if "avg_response_time_anomaly" in anomalies:
                await self._detect_slowloris_attack(requests)
            
        except Exception as e:
            logger.error(f"Attack pattern analysis error: {e}")
    
    async def _detect_volumetric_attack(self, requests: List[RequestMetrics]) -> Optional[AttackPattern]:
        """Detect volumetric DDoS attack."""
        try:
            # Group requests by IP
            ip_requests = {}
            for req in requests:
                if req.ip not in ip_requests:
                    ip_requests[req.ip] = []
                ip_requests[req.ip].append(req)
            
            # Check for high volume from multiple IPs
            high_volume_ips = []
            for ip, ip_reqs in ip_requests.items():
                if len(ip_reqs) >= self.detection_rules["volumetric"]["min_requests_per_ip"]:
                    high_volume_ips.append(ip)
            
            if len(high_volume_ips) >= self.detection_rules["volumetric"]["unique_ip_threshold"]:
                # Volumetric attack detected
                attack_id = f"volumetric_{datetime.now().timestamp()}"
                
                attack = AttackPattern(
                    attack_id=attack_id,
                    attack_type=AttackType.VOLUMETRIC,
                    severity=AttackSeverity.HIGH,
                    source_ips=set(high_volume_ips),
                    start_time=requests[0].timestamp,
                    request_rate=len(requests) / self.analysis_window_minutes,
                    unique_endpoints=len(set(req.endpoint for req in requests)),
                    user_agents=set(req.user_agent for req in requests),
                    confidence_score=0.8
                )
                
                self.active_attacks[attack_id] = attack
                self.metrics["attacks_detected"] += 1
                
                logger.warning(f"Volumetric DDoS attack detected: {attack_id}")
                return attack
            
            return None
            
        except Exception as e:
            logger.error(f"Volumetric attack detection error: {e}")
            return None
    
    async def _detect_application_attack(self, requests: List[RequestMetrics]) -> Optional[AttackPattern]:
        """Detect application layer attack."""
        try:
            suspicious_requests = 0
            suspicious_endpoints = set()
            attacking_ips = set()
            
            for req in requests:
                is_suspicious = False
                
                # Check for suspicious endpoints
                for pattern in self.detection_rules["application"]["suspicious_endpoint_patterns"]:
                    if pattern in req.endpoint:
                        suspicious_requests += 1
                        suspicious_endpoints.add(req.endpoint)
                        attacking_ips.add(req.ip)
                        is_suspicious = True
                        break
                
                # Check for slow responses (potential application DoS)
                if req.response_time > self.detection_rules["application"]["slow_request_threshold"]:
                    suspicious_requests += 1
                    attacking_ips.add(req.ip)
                    is_suspicious = True
                
                # Check for high error rates from specific IPs
                if req.status_code >= 400:
                    ip_error_rate = self._calculate_ip_error_rate(req.ip, requests)
                    if ip_error_rate > self.detection_rules["application"]["error_rate_threshold"]:
                        suspicious_requests += 1
                        attacking_ips.add(req.ip)
                        is_suspicious = True
            
            # Determine if this constitutes an attack
            suspicious_ratio = suspicious_requests / len(requests)
            if suspicious_ratio > 0.3 and len(attacking_ips) > 5:
                attack_id = f"application_{datetime.now().timestamp()}"
                
                attack = AttackPattern(
                    attack_id=attack_id,
                    attack_type=AttackType.APPLICATION,
                    severity=AttackSeverity.MEDIUM,
                    source_ips=attacking_ips,
                    start_time=requests[0].timestamp,
                    request_rate=len(requests) / self.analysis_window_minutes,
                    unique_endpoints=len(suspicious_endpoints),
                    confidence_score=suspicious_ratio
                )
                
                self.active_attacks[attack_id] = attack
                self.metrics["attacks_detected"] += 1
                
                logger.warning(f"Application layer attack detected: {attack_id}")
                return attack
            
            return None
            
        except Exception as e:
            logger.error(f"Application attack detection error: {e}")
            return None
    
    async def _detect_slowloris_attack(self, requests: List[RequestMetrics]) -> Optional[AttackPattern]:
        """Detect Slowloris-style attack."""
        try:
            # Look for many slow connections from few IPs
            ip_slow_requests = {}
            
            for req in requests:
                if req.response_time > self.detection_rules["slowloris"]["connection_timeout_threshold"]:
                    if req.ip not in ip_slow_requests:
                        ip_slow_requests[req.ip] = 0
                    ip_slow_requests[req.ip] += 1
            
            attacking_ips = []
            for ip, slow_count in ip_slow_requests.items():
                if slow_count >= self.detection_rules["slowloris"]["concurrent_connections_per_ip"]:
                    attacking_ips.append(ip)
            
            if attacking_ips:
                attack_id = f"slowloris_{datetime.now().timestamp()}"
                
                attack = AttackPattern(
                    attack_id=attack_id,
                    attack_type=AttackType.SLOWLORIS,
                    severity=AttackSeverity.MEDIUM,
                    source_ips=set(attacking_ips),
                    start_time=requests[0].timestamp,
                    request_rate=len(requests) / self.analysis_window_minutes,
                    confidence_score=0.7
                )
                
                self.active_attacks[attack_id] = attack
                self.metrics["attacks_detected"] += 1
                
                logger.warning(f"Slowloris attack detected: {attack_id}")
                return attack
            
            return None
            
        except Exception as e:
            logger.error(f"Slowloris attack detection error: {e}")
            return None
    
    def _calculate_ip_error_rate(self, ip: str, requests: List[RequestMetrics]) -> float:
        """Calculate error rate for specific IP."""
        try:
            ip_requests = [req for req in requests if req.ip == ip]
            if not ip_requests:
                return 0.0
            
            error_count = sum(1 for req in ip_requests if req.status_code >= 400)
            return error_count / len(ip_requests)
            
        except Exception as e:
            logger.error(f"IP error rate calculation error: {e}")
            return 0.0
    
    async def _check_active_attacks(self):
        """Check if active attacks are still ongoing."""
        try:
            current_time = datetime.now(timezone.utc)
            expired_attacks = []
            
            for attack_id, attack in self.active_attacks.items():
                # Check if attack has been inactive for too long
                if (current_time - attack.start_time).total_seconds() > 600:  # 10 minutes
                    # Check if attack is still active
                    if not await self._is_attack_still_active(attack):
                        attack.end_time = current_time
                        expired_attacks.append(attack_id)
                        logger.info(f"Attack ended: {attack_id}")
            
            # Remove expired attacks
            for attack_id in expired_attacks:
                del self.active_attacks[attack_id]
                
        except Exception as e:
            logger.error(f"Active attack check error: {e}")
    
    async def _is_attack_still_active(self, attack: AttackPattern) -> bool:
        """Check if attack pattern is still active."""
        try:
            # Simple check: are we still seeing high traffic from the attacking IPs?
            current_time = datetime.now(timezone.utc)
            recent_window = current_time - timedelta(minutes=2)
            
            recent_requests = [
                req for req in self.request_buffer
                if req.timestamp >= recent_window and req.ip in attack.source_ips
            ]
            
            # Attack is considered active if we're still seeing significant traffic
            return len(recent_requests) > 10
            
        except Exception as e:
            logger.error(f"Attack activity check error: {e}")
            return False
    
    async def _cleanup_old_data(self):
        """Clean up old data to prevent memory bloat."""
        try:
            current_time = datetime.now(timezone.utc)
            cutoff_time = current_time - timedelta(hours=1)
            
            # Clean up old IP statistics
            expired_ips = []
            for ip, stats in self.ip_statistics.items():
                if stats["last_seen"] < cutoff_time:
                    expired_ips.append(ip)
            
            for ip in expired_ips:
                del self.ip_statistics[ip]
            
            # Clean up finished attacks older than 24 hours
            old_attacks = []
            for attack_id, attack in self.active_attacks.items():
                if (attack.end_time and 
                    (current_time - attack.end_time).total_seconds() > 86400):
                    old_attacks.append(attack_id)
            
            for attack_id in old_attacks:
                del self.active_attacks[attack_id]
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def get_active_attacks(self) -> List[AttackPattern]:
        """Get list of currently active attacks."""
        return [attack for attack in self.active_attacks.values() if attack.is_active()]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get detection metrics."""
        return {
            "performance": self.metrics,
            "active_attacks": len(self.active_attacks),
            "monitored_ips": len(self.ip_statistics),
            "buffer_size": len(self.request_buffer),
            "baseline_samples": {
                name: len(samples) for name, samples in self.baseline_metrics.items()
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            status = "healthy"
            issues = []
            
            # Check if analysis task is running
            if not self._running or (self._analysis_task and self._analysis_task.done()):
                status = "degraded"
                issues.append("Analysis task not running")
            
            # Check Redis connection
            redis_connected = False
            if self.redis:
                try:
                    await self.redis.ping()
                    redis_connected = True
                except Exception:
                    issues.append("Redis connection failed")
                    status = "degraded"
            
            return {
                "status": status,
                "issues": issues,
                "redis_connected": redis_connected,
                "analysis_running": self._running,
                "metrics": self.get_metrics()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()