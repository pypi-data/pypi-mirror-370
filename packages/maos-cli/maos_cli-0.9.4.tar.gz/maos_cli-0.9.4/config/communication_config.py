"""Configuration management for MAOS communication layer."""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum

from src.communication.security.encryption import CipherSuite
from src.communication.consensus.voting import VotingStrategy
from src.communication.utils.error_handling import RetryStrategy


class Environment(Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class RedisConfig:
    """Redis connection configuration."""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    max_connections: int = 20
    connection_timeout: int = 10
    socket_timeout: int = 5
    retry_on_timeout: bool = True
    health_check_interval: int = 30
    
    # Cluster configuration
    cluster_enabled: bool = False
    cluster_nodes: List[Dict[str, str]] = field(default_factory=list)
    
    @property
    def url(self) -> str:
        """Get Redis URL."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


@dataclass
class MessageBusConfig:
    """Message bus configuration."""
    max_queue_size: int = 10000
    cleanup_interval: int = 300  # 5 minutes
    batch_size: int = 100
    flush_interval: float = 1.0
    default_message_ttl: int = 3600  # 1 hour
    max_retry_count: int = 3
    
    # Serialization
    serialization_strategy: str = "json"  # json, msgpack, pickle
    enable_compression: bool = False
    
    # Performance tuning
    worker_count: int = 4
    prefetch_count: int = 10


@dataclass
class EventDispatcherConfig:
    """Event dispatcher configuration."""
    enable_persistence: bool = True
    enable_streaming: bool = True
    max_subscribers: int = 10000
    batch_size: int = 100
    flush_interval: float = 1.0
    
    # Event storage
    storage_backend: str = "sqlite"  # sqlite, postgresql
    storage_path: str = "events.db"
    max_events: int = 1000000
    retention_days: int = 30
    
    # Streaming
    max_streams: int = 1000
    default_stream_buffer_size: int = 1000


@dataclass
class ConsensusConfig:
    """Consensus management configuration."""
    default_voting_strategy: VotingStrategy = VotingStrategy.SIMPLE_MAJORITY
    max_concurrent_requests: int = 100
    default_timeout_minutes: int = 30
    required_quorum: float = 0.5
    
    # Voting mechanism
    cleanup_interval: int = 300
    monitor_interval: int = 30
    
    # Conflict resolution
    enable_automatic_resolution: bool = True
    resolution_strategies: List[str] = field(default_factory=lambda: [
        "priority_based", "timestamp_based", "consensus_building"
    ])


@dataclass
class SecurityConfig:
    """Security configuration."""
    require_encryption: bool = True
    require_authentication: bool = True
    require_authorization: bool = True
    
    # Encryption
    default_cipher: CipherSuite = CipherSuite.AES_256_GCM
    allowed_ciphers: Set[CipherSuite] = field(default_factory=lambda: {
        CipherSuite.AES_256_GCM, 
        CipherSuite.HYBRID,
        CipherSuite.FERNET
    })
    key_derivation_iterations: int = 100000
    
    # Rate limiting
    rate_limit_per_agent: int = 1000  # per minute
    rate_limit_window: int = 60  # seconds
    
    # Message security
    max_message_age: int = 300  # seconds
    enable_replay_protection: bool = True
    
    # Agent management
    trusted_agents: Set[str] = field(default_factory=set)
    blocked_agents: Set[str] = field(default_factory=set)


@dataclass
class HealthMonitorConfig:
    """Health monitoring configuration."""
    heartbeat_interval: int = 30  # seconds
    health_check_interval: int = 60  # seconds
    max_heartbeat_age: int = 90  # seconds
    
    # System monitoring
    enable_system_monitoring: bool = True
    cpu_threshold_warning: float = 75.0
    cpu_threshold_critical: float = 90.0
    memory_threshold_warning: float = 75.0
    memory_threshold_critical: float = 90.0
    disk_threshold_warning: float = 85.0
    disk_threshold_critical: float = 95.0
    
    # Cleanup
    cleanup_interval: int = 300
    max_health_history: int = 1000


@dataclass
class ErrorHandlingConfig:
    """Error handling configuration."""
    # Default retry policy
    max_retry_attempts: int = 3
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    base_retry_delay: float = 1.0
    max_retry_delay: float = 60.0
    backoff_multiplier: float = 2.0
    jitter_factor: float = 0.1
    
    # Circuit breaker
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: float = 60.0
    circuit_breaker_success_threshold: int = 3
    circuit_breaker_timeout: float = 30.0
    
    # Error tracking
    max_error_history: int = 1000
    error_callback_timeout: float = 5.0


@dataclass
class AgentRegistryConfig:
    """Agent registry configuration."""
    max_agents: int = 10000
    cleanup_interval: int = 60  # seconds
    heartbeat_timeout: int = 90  # seconds
    offline_cleanup_hours: int = 24
    
    # Registration
    require_authentication: bool = True
    default_capabilities: List[str] = field(default_factory=list)
    
    # Health monitoring
    enable_health_checks: bool = True
    health_check_interval: int = 60


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File logging
    enable_file_logging: bool = True
    log_file: str = "maos_communication.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    
    # Structured logging
    enable_structured_logging: bool = False
    structured_format: str = "json"
    
    # Component-specific levels
    component_levels: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricsConfig:
    """Metrics collection configuration."""
    enable_metrics: bool = True
    collection_interval: int = 60  # seconds
    
    # Prometheus integration
    enable_prometheus: bool = False
    prometheus_port: int = 8000
    prometheus_path: str = "/metrics"
    
    # Metric storage
    storage_backend: str = "memory"  # memory, redis, prometheus
    retention_hours: int = 24
    max_metrics_per_component: int = 1000


@dataclass
class CommunicationConfig:
    """Main configuration class for MAOS communication layer."""
    environment: Environment = Environment.DEVELOPMENT
    
    # Component configurations
    redis: RedisConfig = field(default_factory=RedisConfig)
    message_bus: MessageBusConfig = field(default_factory=MessageBusConfig)
    event_dispatcher: EventDispatcherConfig = field(default_factory=EventDispatcherConfig)
    consensus: ConsensusConfig = field(default_factory=ConsensusConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    health_monitor: HealthMonitorConfig = field(default_factory=HealthMonitorConfig)
    error_handling: ErrorHandlingConfig = field(default_factory=ErrorHandlingConfig)
    agent_registry: AgentRegistryConfig = field(default_factory=AgentRegistryConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    
    @classmethod
    def from_env(cls) -> "CommunicationConfig":
        """Create configuration from environment variables."""
        config = cls()
        
        # Environment
        config.environment = Environment(os.getenv("MAOS_ENV", "development"))
        
        # Redis configuration
        config.redis.host = os.getenv("REDIS_HOST", "localhost")
        config.redis.port = int(os.getenv("REDIS_PORT", "6379"))
        config.redis.password = os.getenv("REDIS_PASSWORD")
        config.redis.db = int(os.getenv("REDIS_DB", "0"))
        config.redis.max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", "20"))
        
        # Message bus configuration
        config.message_bus.max_queue_size = int(os.getenv("MESSAGE_BUS_MAX_QUEUE_SIZE", "10000"))
        config.message_bus.cleanup_interval = int(os.getenv("MESSAGE_BUS_CLEANUP_INTERVAL", "300"))
        config.message_bus.serialization_strategy = os.getenv("MESSAGE_BUS_SERIALIZATION", "json")
        
        # Security configuration
        config.security.require_encryption = os.getenv("SECURITY_REQUIRE_ENCRYPTION", "true").lower() == "true"
        config.security.require_authentication = os.getenv("SECURITY_REQUIRE_AUTH", "true").lower() == "true"
        config.security.rate_limit_per_agent = int(os.getenv("SECURITY_RATE_LIMIT", "1000"))
        
        # Logging configuration
        config.logging.level = os.getenv("LOG_LEVEL", "INFO")
        config.logging.enable_file_logging = os.getenv("LOG_FILE_ENABLED", "true").lower() == "true"
        config.logging.log_file = os.getenv("LOG_FILE", "maos_communication.log")
        
        return config
    
    @classmethod
    def development(cls) -> "CommunicationConfig":
        """Create development configuration."""
        config = cls()
        config.environment = Environment.DEVELOPMENT
        
        # Development-friendly settings
        config.logging.level = "DEBUG"
        config.security.require_encryption = False
        config.security.require_authentication = False
        config.event_dispatcher.enable_persistence = False
        config.metrics.enable_metrics = True
        
        return config
    
    @classmethod
    def testing(cls) -> "CommunicationConfig":
        """Create testing configuration."""
        config = cls()
        config.environment = Environment.TESTING
        
        # Testing-optimized settings
        config.redis.db = 15  # Use separate Redis DB for tests
        config.message_bus.cleanup_interval = 10
        config.event_dispatcher.enable_persistence = False
        config.event_dispatcher.enable_streaming = False
        config.security.require_encryption = False
        config.security.require_authentication = False
        config.logging.level = "WARNING"
        config.logging.enable_file_logging = False
        
        return config
    
    @classmethod
    def production(cls) -> "CommunicationConfig":
        """Create production configuration."""
        config = cls()
        config.environment = Environment.PRODUCTION
        
        # Production-hardened settings
        config.security.require_encryption = True
        config.security.require_authentication = True
        config.security.require_authorization = True
        config.event_dispatcher.enable_persistence = True
        config.health_monitor.enable_system_monitoring = True
        config.metrics.enable_metrics = True
        config.metrics.enable_prometheus = True
        config.logging.level = "INFO"
        config.logging.enable_structured_logging = True
        
        # Performance optimizations
        config.message_bus.worker_count = 8
        config.message_bus.batch_size = 500
        config.redis.max_connections = 50
        
        return config
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Redis validation
        if self.redis.port < 1 or self.redis.port > 65535:
            issues.append("Redis port must be between 1 and 65535")
        
        if self.redis.max_connections < 1:
            issues.append("Redis max_connections must be at least 1")
        
        # Security validation
        if self.environment == Environment.PRODUCTION:
            if not self.security.require_encryption:
                issues.append("Encryption is required in production")
            if not self.security.require_authentication:
                issues.append("Authentication is required in production")
        
        # Performance validation
        if self.message_bus.max_queue_size < 100:
            issues.append("Message bus queue size should be at least 100")
        
        if self.message_bus.worker_count < 1:
            issues.append("Message bus worker count must be at least 1")
        
        return issues
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return {
            "environment": self.environment.value,
            "redis": {
                "host": self.redis.host,
                "port": self.redis.port,
                "db": self.redis.db,
                "max_connections": self.redis.max_connections,
                "cluster_enabled": self.redis.cluster_enabled,
            },
            "message_bus": {
                "max_queue_size": self.message_bus.max_queue_size,
                "cleanup_interval": self.message_bus.cleanup_interval,
                "batch_size": self.message_bus.batch_size,
                "serialization_strategy": self.message_bus.serialization_strategy,
                "worker_count": self.message_bus.worker_count,
            },
            "security": {
                "require_encryption": self.security.require_encryption,
                "require_authentication": self.security.require_authentication,
                "default_cipher": self.security.default_cipher.value,
                "rate_limit_per_agent": self.security.rate_limit_per_agent,
            },
            "logging": {
                "level": self.logging.level,
                "enable_file_logging": self.logging.enable_file_logging,
                "log_file": self.logging.log_file,
            },
        }