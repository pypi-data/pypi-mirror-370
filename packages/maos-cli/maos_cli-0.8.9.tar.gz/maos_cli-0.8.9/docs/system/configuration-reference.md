# MAOS Configuration Reference

## Overview

MAOS supports multiple configuration methods to provide flexibility across different deployment scenarios. Configuration follows a hierarchical priority system where environment variables override configuration files, and command-line arguments override both.

**Configuration Priority (highest to lowest):**
1. Command-line arguments
2. Environment variables
3. Configuration files (`.env`, `maos.yml`)
4. Default values

## Configuration Files

### Main Configuration File (`maos.yml`)

```yaml
# MAOS Configuration File
# Version: 1.0

# System Settings
system:
  # Environment: development, staging, production
  environment: "production"
  
  # Logging configuration
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  log_format: "structured"  # structured, simple
  log_file: "/var/log/maos/maos.log"
  log_rotation:
    max_size: "100MB"
    max_files: 10
    
  # Performance settings
  max_agents: 20
  agent_spawn_timeout: 30  # seconds
  task_timeout: 3600  # seconds
  checkpoint_interval: 30  # seconds
  
  # Resource limits
  memory_limit_per_agent: "512MB"
  cpu_limit_per_agent: "1.0"  # CPU cores
  shared_memory_size: "10GB"

# API Configuration
api:
  # Server settings
  host: "0.0.0.0"
  port: 8000
  debug: false
  
  # CORS settings
  cors:
    enabled: true
    origins:
      - "https://app.maos.dev"
      - "http://localhost:3000"
    methods: ["GET", "POST", "PUT", "DELETE"]
    headers: ["Authorization", "Content-Type"]
  
  # Rate limiting
  rate_limit:
    enabled: true
    requests_per_minute: 600
    burst_size: 100
  
  # Authentication
  auth:
    jwt_secret: "your-jwt-secret-key"
    jwt_expiry: 3600  # seconds
    jwt_refresh_expiry: 604800  # 7 days
    require_auth: true

# Database Configuration
database:
  # Primary database (PostgreSQL)
  primary:
    url: "postgresql://maos:password@localhost:5432/maos"
    pool_size: 20
    max_overflow: 30
    pool_timeout: 30
    echo: false  # SQL query logging
  
  # Connection retry settings
  retry:
    max_attempts: 3
    backoff_factor: 2
    max_delay: 60

# Redis Configuration
redis:
  # Primary Redis instance
  url: "redis://localhost:6379/0"
  
  # Connection pool settings
  pool:
    max_connections: 50
    retry_on_timeout: true
    health_check_interval: 30
  
  # Cluster settings (for Redis Cluster)
  cluster:
    enabled: false
    nodes:
      - "redis-1:6379"
      - "redis-2:6379" 
      - "redis-3:6379"
    skip_full_coverage_check: false
  
  # Message bus settings
  message_bus:
    stream_max_length: 10000
    consumer_group: "maos-consumers"
    consumer_timeout: 5000  # milliseconds
    batch_size: 100
  
  # Shared state settings
  shared_state:
    key_prefix: "maos:state:"
    default_ttl: 86400  # 24 hours
    compression: true

# Agent Configuration
agents:
  # Default agent settings
  defaults:
    timeout: 1800  # 30 minutes
    max_memory: "512MB"
    max_cpu: "1.0"
    retry_attempts: 3
    heartbeat_interval: 30  # seconds
  
  # Agent types and their configurations
  types:
    researcher:
      max_instances: 5
      capabilities: ["web_search", "data_analysis", "report_generation"]
      timeout: 3600  # 1 hour
      memory: "1GB"
    
    coder:
      max_instances: 8
      capabilities: ["code_generation", "testing", "debugging"]
      timeout: 2400  # 40 minutes
      memory: "768MB"
    
    analyst:
      max_instances: 6
      capabilities: ["data_analysis", "visualization", "statistics"]
      timeout: 2400
      memory: "1GB"
    
    tester:
      max_instances: 4
      capabilities: ["test_generation", "test_execution", "validation"]
      timeout: 1800
      memory: "512MB"
    
    coordinator:
      max_instances: 2
      capabilities: ["task_coordination", "consensus_building", "workflow_management"]
      timeout: 600  # 10 minutes
      memory: "256MB"

# Task Configuration
tasks:
  # Default task settings
  defaults:
    priority: "MEDIUM"
    timeout: 1800  # 30 minutes
    max_agents: 5
    require_consensus: false
    auto_retry: true
    max_retries: 2
  
  # Queue settings
  queue:
    max_size: 10000
    priority_levels: 4
    cleanup_interval: 300  # 5 minutes
  
  # Result storage
  results:
    storage_backend: "s3"  # s3, local, database
    retention_days: 90
    compression: true
    encryption: true

# Checkpoint Configuration
checkpoints:
  # Storage backend
  storage:
    backend: "s3"  # s3, local, minio
    
    # S3 configuration
    s3:
      bucket: "maos-checkpoints"
      region: "us-east-1"
      access_key: "${AWS_ACCESS_KEY_ID}"
      secret_key: "${AWS_SECRET_ACCESS_KEY}"
      endpoint_url: null  # For S3-compatible services
    
    # Local storage configuration
    local:
      path: "/var/lib/maos/checkpoints"
      max_disk_usage: "10GB"
  
  # Checkpoint settings
  interval: 30  # seconds
  retention:
    count: 10  # Keep last 10 checkpoints
    age_days: 7  # Keep checkpoints for 7 days
  compression:
    enabled: true
    algorithm: "gzip"  # gzip, lzma
    level: 6
  encryption:
    enabled: true
    algorithm: "AES-256-GCM"
    key_source: "environment"  # environment, vault, kms

# Security Configuration
security:
  # Encryption settings
  encryption:
    # Data at rest
    at_rest:
      enabled: true
      algorithm: "AES-256-GCM"
      key_rotation_days: 90
    
    # Data in transit
    in_transit:
      enabled: true
      tls_version: "1.3"
      cipher_suites:
        - "TLS_AES_256_GCM_SHA384"
        - "TLS_CHACHA20_POLY1305_SHA256"
  
  # Authentication and authorization
  auth:
    # JWT settings
    jwt:
      algorithm: "HS256"
      secret: "${JWT_SECRET}"
      expiry: 3600
      refresh_expiry: 604800
    
    # Rate limiting
    rate_limiting:
      enabled: true
      window_size: 60  # seconds
      max_requests: 600
      burst_multiplier: 2
    
    # IP allowlist (optional)
    ip_allowlist:
      enabled: false
      addresses:
        - "192.168.1.0/24"
        - "10.0.0.0/8"
  
  # API security
  api:
    # Request validation
    validate_requests: true
    max_request_size: "10MB"
    
    # CORS
    cors:
      enabled: true
      origins: ["https://app.maos.dev"]
      credentials: true
    
    # Content Security Policy
    csp:
      enabled: true
      policy: "default-src 'self'; script-src 'self' 'unsafe-inline'"

# Monitoring Configuration
monitoring:
  # Metrics collection
  metrics:
    enabled: true
    backend: "prometheus"  # prometheus, datadog, statsd
    port: 9090
    path: "/metrics"
    
    # Custom metrics
    custom:
      task_duration_buckets: [0.1, 0.5, 1, 2, 5, 10, 30, 60, 300]
      agent_memory_buckets: [64, 128, 256, 512, 1024, 2048]
  
  # Health checks
  health:
    enabled: true
    endpoint: "/health"
    timeout: 10  # seconds
    
    # Component health checks
    components:
      database: true
      redis: true
      agents: true
      storage: true
  
  # Alerting
  alerts:
    enabled: true
    backend: "webhook"  # webhook, email, slack, pagerduty
    
    # Alert rules
    rules:
      high_task_failure_rate:
        threshold: 0.1  # 10% failure rate
        window: "5m"
      agent_spawn_failure:
        threshold: 3
        window: "1m"
      checkpoint_failure:
        threshold: 2
        window: "5m"
    
    # Notification settings
    notifications:
      webhook:
        url: "https://alerts.example.com/maos"
        timeout: 30
      email:
        smtp_host: "smtp.example.com"
        smtp_port: 587
        from: "alerts@maos.dev"
        to: ["admin@example.com"]

# Development Configuration
development:
  # Development-specific settings
  debug: true
  auto_reload: true
  
  # Mock services
  mocks:
    claude_api: false
    storage: false
    
  # Test data
  fixtures:
    load_on_startup: true
    path: "./tests/fixtures"
  
  # Profiling
  profiling:
    enabled: false
    output_dir: "./profiles"

# Production Overrides
production:
  # Override settings for production
  system:
    log_level: "WARNING"
    max_agents: 50
  
  api:
    debug: false
    
  security:
    auth:
      require_auth: true
    
  monitoring:
    metrics:
      enabled: true
    alerts:
      enabled: true
```

## Environment Variables

All configuration options can be overridden using environment variables. Use uppercase with `MAOS_` prefix and underscores for nested keys:

```bash
# System settings
export MAOS_SYSTEM_ENVIRONMENT="production"
export MAOS_SYSTEM_LOG_LEVEL="INFO"
export MAOS_SYSTEM_MAX_AGENTS="20"

# Database settings
export MAOS_DATABASE_PRIMARY_URL="postgresql://user:pass@host:5432/db"
export MAOS_DATABASE_PRIMARY_POOL_SIZE="20"

# Redis settings  
export MAOS_REDIS_URL="redis://localhost:6379/0"
export MAOS_REDIS_POOL_MAX_CONNECTIONS="50"

# API settings
export MAOS_API_HOST="0.0.0.0"
export MAOS_API_PORT="8000"
export MAOS_API_DEBUG="false"

# Security settings
export MAOS_SECURITY_AUTH_JWT_SECRET="your-secret-key"
export JWT_SECRET="your-secret-key"  # Alternative format

# Checkpoint settings
export MAOS_CHECKPOINTS_STORAGE_BACKEND="s3"
export MAOS_CHECKPOINTS_S3_BUCKET="maos-checkpoints"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"

# Monitoring settings
export MAOS_MONITORING_METRICS_ENABLED="true"
export MAOS_MONITORING_ALERTS_ENABLED="true"
```

## Environment-Specific Configuration

### Development (`.env.development`)

```bash
# Development environment
MAOS_SYSTEM_ENVIRONMENT=development
MAOS_SYSTEM_LOG_LEVEL=DEBUG
MAOS_SYSTEM_MAX_AGENTS=5

# Use local services
MAOS_DATABASE_PRIMARY_URL=postgresql://maos:password@localhost:5432/maos_dev
MAOS_REDIS_URL=redis://localhost:6379/0

# Disable security features
MAOS_SECURITY_AUTH_REQUIRE_AUTH=false
MAOS_SECURITY_ENCRYPTION_AT_REST_ENABLED=false

# Enable debug features
MAOS_API_DEBUG=true
MAOS_DEVELOPMENT_DEBUG=true
MAOS_DEVELOPMENT_AUTO_RELOAD=true

# Local checkpoint storage
MAOS_CHECKPOINTS_STORAGE_BACKEND=local
MAOS_CHECKPOINTS_LOCAL_PATH=./checkpoints
```

### Testing (`.env.testing`)

```bash
# Testing environment
MAOS_SYSTEM_ENVIRONMENT=testing
MAOS_SYSTEM_LOG_LEVEL=WARNING
MAOS_SYSTEM_MAX_AGENTS=2

# Use test databases
MAOS_DATABASE_PRIMARY_URL=postgresql://maos:password@localhost:5432/maos_test
MAOS_REDIS_URL=redis://localhost:6379/1

# Fast timeouts for tests
MAOS_SYSTEM_CHECKPOINT_INTERVAL=5
MAOS_AGENTS_DEFAULTS_TIMEOUT=60

# Disable external services
MAOS_DEVELOPMENT_MOCKS_CLAUDE_API=true
MAOS_DEVELOPMENT_MOCKS_STORAGE=true
```

### Production (`.env.production`)

```bash
# Production environment
MAOS_SYSTEM_ENVIRONMENT=production
MAOS_SYSTEM_LOG_LEVEL=INFO
MAOS_SYSTEM_MAX_AGENTS=50

# Production databases
MAOS_DATABASE_PRIMARY_URL=postgresql://maos:${DB_PASSWORD}@db.example.com:5432/maos
MAOS_REDIS_URL=redis://:${REDIS_PASSWORD}@redis.example.com:6379/0

# Security enabled
MAOS_SECURITY_AUTH_REQUIRE_AUTH=true
MAOS_SECURITY_ENCRYPTION_AT_REST_ENABLED=true
JWT_SECRET=${JWT_SECRET}

# Production storage
MAOS_CHECKPOINTS_STORAGE_BACKEND=s3
MAOS_CHECKPOINTS_S3_BUCKET=prod-maos-checkpoints
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

# Full monitoring
MAOS_MONITORING_METRICS_ENABLED=true
MAOS_MONITORING_ALERTS_ENABLED=true
```

## Docker Configuration

### Docker Compose Environment

```yaml
# docker-compose.override.yml
version: '3.8'

services:
  maos-orchestrator:
    environment:
      # Override configuration
      - MAOS_SYSTEM_LOG_LEVEL=${LOG_LEVEL:-INFO}
      - MAOS_SYSTEM_MAX_AGENTS=${MAX_AGENTS:-10}
      
      # Database connection
      - MAOS_DATABASE_PRIMARY_URL=postgresql://maos:${POSTGRES_PASSWORD}@postgres:5432/maos
      
      # Redis connection
      - MAOS_REDIS_URL=redis://redis:6379/0
      
      # JWT secret
      - JWT_SECRET=${JWT_SECRET}
      
      # Checkpoint storage
      - MAOS_CHECKPOINTS_STORAGE_BACKEND=local
      - MAOS_CHECKPOINTS_LOCAL_PATH=/app/checkpoints
    
    volumes:
      # Mount configuration
      - ./config/maos.yml:/app/config/maos.yml:ro
      - ./checkpoints:/app/checkpoints
```

### Kubernetes Configuration

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: maos-config
data:
  maos.yml: |
    system:
      environment: "production"
      log_level: "INFO"
      max_agents: 20
    
    api:
      host: "0.0.0.0"
      port: 8000
      
    # ... full configuration
    
---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: maos-secrets
type: Opaque
data:
  jwt-secret: <base64-encoded-secret>
  db-password: <base64-encoded-password>
  redis-password: <base64-encoded-password>
  
---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: maos-orchestrator
spec:
  template:
    spec:
      containers:
      - name: maos
        env:
        - name: MAOS_SYSTEM_ENVIRONMENT
          value: "production"
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: maos-secrets
              key: jwt-secret
        - name: MAOS_DATABASE_PRIMARY_URL
          value: "postgresql://maos:$(DB_PASSWORD)@postgres:5432/maos"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: maos-secrets
              key: db-password
        
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
          
      volumes:
      - name: config
        configMap:
          name: maos-config
```

## Configuration Validation

MAOS validates configuration on startup and provides detailed error messages:

```python
# Example configuration validation
from maos.config import ConfigValidator, ValidationError

try:
    validator = ConfigValidator()
    config = validator.load_and_validate('maos.yml')
    print("Configuration valid!")
except ValidationError as e:
    print(f"Configuration error: {e}")
    for error in e.errors:
        print(f"  - {error.path}: {error.message}")
```

Common validation errors:
- Invalid data types (string instead of integer)
- Missing required fields
- Values outside allowed ranges
- Invalid connection strings
- Conflicting settings

## Best Practices

### 1. Security Configuration

```yaml
# Never store secrets in configuration files
security:
  auth:
    jwt_secret: "${JWT_SECRET}"  # Use environment variables
    
# Use strong encryption
encryption:
  at_rest:
    algorithm: "AES-256-GCM"
    key_rotation_days: 30  # Frequent rotation
    
# Enable all security features in production
security:
  auth:
    require_auth: true
  encryption:
    at_rest:
      enabled: true
    in_transit:
      enabled: true
```

### 2. Performance Configuration

```yaml
# Right-size agent limits
system:
  max_agents: 20  # Based on available resources
  
# Configure appropriate timeouts
agents:
  defaults:
    timeout: 1800  # 30 minutes for most tasks
    
# Optimize database connections
database:
  primary:
    pool_size: 20  # 2-3x number of agents
    max_overflow: 10
```

### 3. Monitoring Configuration

```yaml
# Enable comprehensive monitoring
monitoring:
  metrics:
    enabled: true
    backend: "prometheus"
    
  alerts:
    enabled: true
    rules:
      # Monitor key metrics
      high_task_failure_rate:
        threshold: 0.05  # 5% failure rate
      
# Configure health checks
health:
  components:
    database: true
    redis: true
    agents: true
```

### 4. Development vs Production

| Setting | Development | Production |
|---------|-------------|------------|
| `log_level` | DEBUG | INFO |
| `debug` | true | false |
| `require_auth` | false | true |
| `max_agents` | 5 | 20+ |
| `checkpoint_interval` | 60s | 30s |
| `encryption` | disabled | enabled |
| `monitoring` | basic | comprehensive |

## Configuration Management Tools

### 1. Configuration Templates

Use templating tools like Helm or Kustomize:

```yaml
# values.yaml (Helm)
system:
  environment: {{ .Values.environment }}
  maxAgents: {{ .Values.maxAgents | default 20 }}
  
database:
  url: postgresql://{{ .Values.database.user }}:{{ .Values.database.password }}@{{ .Values.database.host }}/{{ .Values.database.name }}
```

### 2. Configuration Validation Scripts

```bash
#!/bin/bash
# validate-config.sh

# Validate configuration syntax
python -m maos.config.validator config/maos.yml

# Test database connection
python -c "
from maos.config import load_config
from maos.database import test_connection
config = load_config()
if test_connection(config.database.primary.url):
    print('Database connection: OK')
else:
    print('Database connection: FAILED')
    exit(1)
"

# Test Redis connection
redis-cli -u $MAOS_REDIS_URL ping

echo "Configuration validation complete!"
```

### 3. Environment-Specific Overrides

```yaml
# base.yml
system: &system_defaults
  log_level: "INFO"
  max_agents: 20

# development.yml  
system:
  <<: *system_defaults
  log_level: "DEBUG"
  max_agents: 5
  
# production.yml
system:
  <<: *system_defaults
  log_level: "WARNING"
  max_agents: 50
```

## Troubleshooting Configuration

### Common Issues

1. **Configuration Not Loading**
   ```bash
   # Check file permissions
   ls -la maos.yml
   
   # Validate YAML syntax
   python -c "import yaml; yaml.safe_load(open('maos.yml'))"
   ```

2. **Environment Variables Not Working**
   ```bash
   # Check variable names (case sensitive)
   env | grep MAOS_
   
   # Test specific override
   MAOS_SYSTEM_LOG_LEVEL=DEBUG python -m maos.config.print
   ```

3. **Database Connection Issues**
   ```bash
   # Test connection string
   psql "postgresql://maos:password@localhost:5432/maos"
   
   # Check network connectivity
   telnet database-host 5432
   ```

4. **Redis Connection Issues**
   ```bash
   # Test Redis connection
   redis-cli -u redis://localhost:6379/0 ping
   
   # Check Redis configuration
   redis-cli config get '*'
   ```

For additional support, see the [troubleshooting guide](troubleshooting-guide.md) or contact support.