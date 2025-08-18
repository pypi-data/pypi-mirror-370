"""Security configuration and integration with Redis state management."""

import os
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import timedelta
import yaml

from .auth import JWTManager, RefreshTokenManager
from .rbac import RBACManager
from .api_keys import APIKeyManager, KeyRotationManager
from .audit import AuditLogger
from .validation import InputValidator
from .rate_limiting import DDoSDetector
from .middleware import SecurityMiddlewareStack

logger = logging.getLogger(__name__)


@dataclass
class SecurityConfig:
    """Comprehensive security configuration."""
    
    # Redis configuration
    redis_url: str = "redis://localhost:6379"
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    
    # JWT configuration
    jwt_secret_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 30
    jwt_issuer: str = "maos"
    jwt_audience: List[str] = field(default_factory=lambda: ["maos-agents"])
    
    # RBAC configuration
    rbac_default_deny: bool = True
    rbac_enable_caching: bool = True
    rbac_cache_ttl_minutes: int = 30
    
    # API Keys configuration
    api_key_default_expiry_days: int = 365
    api_key_rotation_enabled: bool = True
    api_key_min_length: int = 32
    
    # Rate limiting configuration
    rate_limit_redis_db: int = 8
    rate_limit_enable_ddos_protection: bool = True
    rate_limit_global_limit: int = 10000
    rate_limit_per_ip_limit: int = 100
    
    # Audit logging configuration
    audit_redis_db: int = 9
    audit_enable_file_logging: bool = True
    audit_log_file_path: str = "/var/log/maos/audit.log"
    audit_retention_days: int = 365
    audit_batch_size: int = 100
    
    # Security middleware configuration
    security_headers_force_https: bool = True
    security_headers_hsts_max_age: int = 31536000
    cors_allowed_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000"])
    cors_allow_credentials: bool = True
    
    # Input validation configuration
    input_validation_max_length: int = 10000
    input_validation_enable_html_sanitization: bool = True
    
    # DDoS detection configuration
    ddos_analysis_window_minutes: int = 5
    ddos_anomaly_threshold: float = 3.0
    ddos_min_requests_for_analysis: int = 50
    
    # Encryption configuration
    encryption_master_key: Optional[str] = None
    encryption_key_rotation_days: int = 90
    
    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """Create configuration from environment variables."""
        return cls(
            # Redis
            redis_url=os.getenv("MAOS_REDIS_URL", "redis://localhost:6379"),
            redis_password=os.getenv("MAOS_REDIS_PASSWORD"),
            redis_ssl=os.getenv("MAOS_REDIS_SSL", "false").lower() == "true",
            
            # JWT
            jwt_secret_key=os.getenv("MAOS_JWT_SECRET_KEY"),
            jwt_algorithm=os.getenv("MAOS_JWT_ALGORITHM", "HS256"),
            jwt_access_token_expire_minutes=int(os.getenv("MAOS_JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
            jwt_refresh_token_expire_days=int(os.getenv("MAOS_JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30")),
            jwt_issuer=os.getenv("MAOS_JWT_ISSUER", "maos"),
            jwt_audience=os.getenv("MAOS_JWT_AUDIENCE", "maos-agents").split(","),
            
            # RBAC
            rbac_default_deny=os.getenv("MAOS_RBAC_DEFAULT_DENY", "true").lower() == "true",
            rbac_enable_caching=os.getenv("MAOS_RBAC_ENABLE_CACHING", "true").lower() == "true",
            rbac_cache_ttl_minutes=int(os.getenv("MAOS_RBAC_CACHE_TTL_MINUTES", "30")),
            
            # API Keys
            api_key_default_expiry_days=int(os.getenv("MAOS_API_KEY_DEFAULT_EXPIRY_DAYS", "365")),
            api_key_rotation_enabled=os.getenv("MAOS_API_KEY_ROTATION_ENABLED", "true").lower() == "true",
            
            # Rate limiting
            rate_limit_enable_ddos_protection=os.getenv("MAOS_RATE_LIMIT_ENABLE_DDOS", "true").lower() == "true",
            rate_limit_global_limit=int(os.getenv("MAOS_RATE_LIMIT_GLOBAL", "10000")),
            rate_limit_per_ip_limit=int(os.getenv("MAOS_RATE_LIMIT_PER_IP", "100")),
            
            # Audit
            audit_enable_file_logging=os.getenv("MAOS_AUDIT_FILE_LOGGING", "true").lower() == "true",
            audit_log_file_path=os.getenv("MAOS_AUDIT_LOG_FILE", "/var/log/maos/audit.log"),
            audit_retention_days=int(os.getenv("MAOS_AUDIT_RETENTION_DAYS", "365")),
            
            # Security headers
            security_headers_force_https=os.getenv("MAOS_FORCE_HTTPS", "true").lower() == "true",
            cors_allowed_origins=os.getenv("MAOS_CORS_ORIGINS", "http://localhost:3000").split(","),
            
            # Encryption
            encryption_master_key=os.getenv("MAOS_ENCRYPTION_MASTER_KEY"),
            encryption_key_rotation_days=int(os.getenv("MAOS_KEY_ROTATION_DAYS", "90"))
        )
    
    @classmethod
    def from_yaml(cls, config_path: str) -> "SecurityConfig":
        """Create configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
            
            security_data = data.get('security', {})
            return cls(**security_data)
            
        except Exception as e:
            logger.error(f"Failed to load security config from YAML: {e}")
            return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Check required fields
        if not self.jwt_secret_key:
            issues.append("JWT secret key is required (set MAOS_JWT_SECRET_KEY)")
        
        if len(self.jwt_secret_key or "") < 32:
            issues.append("JWT secret key should be at least 32 characters")
        
        # Check Redis URL format
        if not self.redis_url.startswith(("redis://", "rediss://")):
            issues.append("Invalid Redis URL format")
        
        # Check file paths
        if self.audit_enable_file_logging:
            audit_dir = os.path.dirname(self.audit_log_file_path)
            if not os.path.exists(audit_dir):
                try:
                    os.makedirs(audit_dir, exist_ok=True)
                except Exception as e:
                    issues.append(f"Cannot create audit log directory: {e}")
        
        # Check numeric ranges
        if self.jwt_access_token_expire_minutes <= 0:
            issues.append("JWT access token expiry must be positive")
        
        if self.rate_limit_global_limit <= 0:
            issues.append("Global rate limit must be positive")
        
        return issues


class SecurityManager:
    """Centralized security manager that coordinates all security components."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        
        # Security components
        self.jwt_manager: Optional[JWTManager] = None
        self.refresh_token_manager: Optional[RefreshTokenManager] = None
        self.rbac_manager: Optional[RBACManager] = None
        self.api_key_manager: Optional[APIKeyManager] = None
        self.key_rotation_manager: Optional[KeyRotationManager] = None
        self.audit_logger: Optional[AuditLogger] = None
        self.input_validator: Optional[InputValidator] = None
        self.ddos_detector: Optional[DDoSDetector] = None
        
        # Middleware stack
        self.middleware_stack: Optional[SecurityMiddlewareStack] = None
        
        # Initialization status
        self.initialized = False
        
        logger.info("Security manager created")
    
    async def initialize(self):
        """Initialize all security components."""
        try:
            logger.info("Initializing security manager...")
            
            # Validate configuration
            config_issues = self.config.validate()
            if config_issues:
                logger.warning(f"Security configuration issues: {config_issues}")
            
            # Initialize JWT manager
            self.jwt_manager = JWTManager(
                secret_key=self.config.jwt_secret_key,
                issuer=self.config.jwt_issuer,
                audience=self.config.jwt_audience,
                access_token_expire_minutes=self.config.jwt_access_token_expire_minutes
            )
            
            # Initialize refresh token manager
            self.refresh_token_manager = RefreshTokenManager(
                redis_url=self.config.redis_url,
                redis_db=2
            )
            await self.refresh_token_manager.connect()
            
            # Initialize RBAC manager
            self.rbac_manager = RBACManager(
                redis_url=self.config.redis_url,
                enable_caching=self.config.rbac_enable_caching,
                cache_ttl=self.config.rbac_cache_ttl_minutes * 60,
                default_deny=self.config.rbac_default_deny
            )
            await self.rbac_manager.initialize()
            
            # Initialize API key manager
            self.api_key_manager = APIKeyManager(
                redis_url=self.config.redis_url,
                redis_db=5,
                default_expiry_days=self.config.api_key_default_expiry_days
            )
            await self.api_key_manager.connect()
            
            # Initialize key rotation manager
            if self.config.api_key_rotation_enabled:
                self.key_rotation_manager = KeyRotationManager(
                    api_key_manager=self.api_key_manager,
                    redis_url=self.config.redis_url,
                    redis_db=6
                )
                await self.key_rotation_manager.connect()
                await self.key_rotation_manager.start_automatic_rotation()
            
            # Initialize audit logger
            self.audit_logger = AuditLogger(
                redis_url=self.config.redis_url,
                redis_db=self.config.audit_redis_db,
                batch_size=self.config.audit_batch_size,
                retention_days=self.config.audit_retention_days,
                enable_file_logging=self.config.audit_enable_file_logging,
                log_file_path=self.config.audit_log_file_path
            )
            await self.audit_logger.connect()
            
            # Initialize input validator
            self.input_validator = InputValidator()
            
            # Initialize DDoS detector
            self.ddos_detector = DDoSDetector(
                redis_url=self.config.redis_url,
                redis_db=10,
                analysis_window_minutes=self.config.ddos_analysis_window_minutes,
                anomaly_threshold=self.config.ddos_anomaly_threshold,
                min_requests_for_analysis=self.config.ddos_min_requests_for_analysis
            )
            await self.ddos_detector.connect()
            
            self.initialized = True
            logger.info("Security manager initialized successfully")
            
            # Log initialization event
            from .audit import AuditEvent, EventType, EventSeverity
            await self.audit_logger.log_event(AuditEvent(
                event_id=f"security_init_{int(datetime.now().timestamp())}",
                event_type=EventType.SYSTEM_STARTUP,
                timestamp=datetime.now(timezone.utc),
                severity=EventSeverity.MEDIUM,
                reason="Security manager initialized",
                metadata={"components_initialized": self._get_initialized_components()}
            ))
            
        except Exception as e:
            logger.error(f"Security manager initialization failed: {e}")
            await self.shutdown()
            raise
    
    def configure_middleware(self, app) -> SecurityMiddlewareStack:
        """Configure security middleware stack for FastAPI app."""
        try:
            if not self.initialized:
                raise RuntimeError("Security manager not initialized")
            
            self.middleware_stack = SecurityMiddlewareStack(app)
            
            # Configure middleware stack
            self.middleware_stack.configure_default_stack(
                jwt_manager=self.jwt_manager,
                rbac_manager=self.rbac_manager,
                redis_url=self.config.redis_url,
                cors_origins=self.config.cors_allowed_origins
            )
            
            logger.info("Security middleware configured")
            return self.middleware_stack
            
        except Exception as e:
            logger.error(f"Middleware configuration failed: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown all security components."""
        try:
            logger.info("Shutting down security manager...")
            
            # Shutdown components in reverse order
            if self.ddos_detector:
                await self.ddos_detector.disconnect()
            
            if self.key_rotation_manager:
                await self.key_rotation_manager.disconnect()
            
            if self.api_key_manager:
                await self.api_key_manager.disconnect()
            
            if self.rbac_manager:
                await self.rbac_manager.shutdown()
            
            if self.refresh_token_manager:
                await self.refresh_token_manager.disconnect()
            
            # Log shutdown event before closing audit logger
            if self.audit_logger:
                from .audit import AuditEvent, EventType, EventSeverity
                await self.audit_logger.log_event(AuditEvent(
                    event_id=f"security_shutdown_{int(datetime.now().timestamp())}",
                    event_type=EventType.SYSTEM_SHUTDOWN,
                    timestamp=datetime.now(timezone.utc),
                    severity=EventSeverity.MEDIUM,
                    reason="Security manager shutdown"
                ))
                await self.audit_logger.disconnect()
            
            self.initialized = False
            logger.info("Security manager shutdown complete")
            
        except Exception as e:
            logger.error(f"Security manager shutdown error: {e}")
    
    def _get_initialized_components(self) -> List[str]:
        """Get list of successfully initialized components."""
        components = []
        
        if self.jwt_manager:
            components.append("jwt_manager")
        if self.refresh_token_manager:
            components.append("refresh_token_manager")
        if self.rbac_manager:
            components.append("rbac_manager")
        if self.api_key_manager:
            components.append("api_key_manager")
        if self.key_rotation_manager:
            components.append("key_rotation_manager")
        if self.audit_logger:
            components.append("audit_logger")
        if self.input_validator:
            components.append("input_validator")
        if self.ddos_detector:
            components.append("ddos_detector")
        
        return components
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive security health check."""
        try:
            if not self.initialized:
                return {"status": "unhealthy", "error": "Not initialized"}
            
            component_health = {}
            overall_status = "healthy"
            issues = []
            
            # Check each component
            components = [
                ("jwt_manager", self.jwt_manager),
                ("refresh_token_manager", self.refresh_token_manager),
                ("rbac_manager", self.rbac_manager),
                ("api_key_manager", self.api_key_manager),
                ("key_rotation_manager", self.key_rotation_manager),
                ("audit_logger", self.audit_logger),
                ("input_validator", self.input_validator),
                ("ddos_detector", self.ddos_detector)
            ]
            
            for name, component in components:
                if component and hasattr(component, 'health_check'):
                    try:
                        health = await component.health_check()
                        component_health[name] = health
                        
                        if health.get("status") != "healthy":
                            overall_status = "degraded"
                            issues.append(f"{name}: {health.get('status')}")
                            
                    except Exception as e:
                        component_health[name] = {"status": "unhealthy", "error": str(e)}
                        overall_status = "degraded"
                        issues.append(f"{name}: error")
                elif component:
                    component_health[name] = {"status": "healthy"}
                else:
                    component_health[name] = {"status": "not_initialized"}
            
            return {
                "status": overall_status,
                "issues": issues,
                "initialized": self.initialized,
                "components": component_health,
                "config_validation": self.config.validate()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    # Context manager support
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown()


# Convenience function for creating configured security manager
async def create_security_manager(
    config_path: Optional[str] = None,
    use_env: bool = True
) -> SecurityManager:
    """Create and initialize security manager with configuration."""
    try:
        # Load configuration
        if config_path:
            config = SecurityConfig.from_yaml(config_path)
        elif use_env:
            config = SecurityConfig.from_env()
        else:
            config = SecurityConfig()
        
        # Create and initialize manager
        manager = SecurityManager(config)
        await manager.initialize()
        
        return manager
        
    except Exception as e:
        logger.error(f"Failed to create security manager: {e}")
        raise