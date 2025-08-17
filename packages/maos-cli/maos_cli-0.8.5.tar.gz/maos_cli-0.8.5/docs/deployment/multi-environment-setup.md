# MAOS Multi-Environment Setup Guide

## Overview

This guide covers setting up MAOS across multiple environments (development, staging, production) with proper configuration management, deployment pipelines, and environment-specific optimizations.

## Environment Strategy

### Environment Types

| Environment | Purpose | Configuration | Resources |
|-------------|---------|---------------|-----------|
| **Development** | Local development & testing | Minimal security, debug enabled | Low resource allocation |
| **Staging** | Pre-production testing | Production-like, test data | Medium resource allocation |
| **Production** | Live system | Full security, optimized performance | High resource allocation |
| **Demo** | Customer demonstrations | Sample data, stable features | Medium resource allocation |

### Configuration Management Philosophy

1. **Environment-Specific Variables**: Separate sensitive and environment-specific values
2. **Infrastructure as Code**: All environments defined in version control
3. **Consistent Base**: Common base configuration with environment overrides
4. **Automated Deployment**: CI/CD pipelines for consistent deployments
5. **Environment Parity**: Minimize differences between environments

## Project Structure

```
maos-environments/
├── environments/
│   ├── development/
│   │   ├── docker-compose.yml
│   │   ├── .env
│   │   ├── config/
│   │   └── k8s/
│   ├── staging/
│   │   ├── docker-compose.yml
│   │   ├── .env
│   │   ├── config/
│   │   └── k8s/
│   ├── production/
│   │   ├── docker-compose.yml
│   │   ├── .env
│   │   ├── config/
│   │   └── k8s/
│   └── demo/
│       ├── docker-compose.yml
│       ├── .env
│       ├── config/
│       └── k8s/
├── shared/
│   ├── base-config.yml
│   ├── scripts/
│   └── templates/
└── ci-cd/
    ├── Jenkinsfile
    ├── github-actions/
    └── gitlab-ci.yml
```

## Base Configuration

### Shared Configuration (`shared/base-config.yml`)

```yaml
# Base MAOS configuration - shared across all environments
system:
  # These will be overridden per environment
  environment: "{{ ENVIRONMENT }}"
  log_level: "{{ LOG_LEVEL }}"
  max_agents: "{{ MAX_AGENTS }}"
  
  # Common settings
  checkpoint_interval: 30
  agent_spawn_timeout: 30
  task_timeout: 3600

api:
  host: "0.0.0.0"
  port: 8000
  cors:
    enabled: true
    methods: ["GET", "POST", "PUT", "DELETE", "PATCH"]
    headers: ["Authorization", "Content-Type"]

agents:
  defaults:
    timeout: 1800
    retry_attempts: 3
    heartbeat_interval: 30
  
  types:
    researcher:
      capabilities: ["web_search", "data_analysis", "report_generation"]
      timeout: 3600
    coder:
      capabilities: ["code_generation", "testing", "debugging"]
      timeout: 2400
    analyst:
      capabilities: ["data_analysis", "visualization", "statistics"]
      timeout: 2400
    tester:
      capabilities: ["test_generation", "test_execution", "validation"]
      timeout: 1800
    coordinator:
      capabilities: ["task_coordination", "consensus_building"]
      timeout: 600

tasks:
  defaults:
    priority: "MEDIUM"
    timeout: 1800
    max_agents: 5
    require_consensus: false
    auto_retry: true
    max_retries: 2
  
  queue:
    max_size: 10000
    priority_levels: 4
    cleanup_interval: 300

checkpoints:
  interval: 30
  retention:
    count: 10
    age_days: 7
  compression:
    enabled: true
    algorithm: "gzip"
    level: 6
```

### Environment Templates

#### Template Engine Setup

```bash
# Install gomplate for template processing
curl -o /usr/local/bin/gomplate -sSL https://github.com/hairyhenderson/gomplate/releases/download/v3.11.3/gomplate_linux-amd64
chmod +x /usr/local/bin/gomplate
```

#### Template Processing Script (`shared/scripts/generate-config.sh`)

```bash
#!/bin/bash
set -euo pipefail

ENVIRONMENT=${1:-development}
OUTPUT_DIR="environments/${ENVIRONMENT}/config"

echo "Generating configuration for environment: ${ENVIRONMENT}"

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Load environment variables
if [ -f "environments/${ENVIRONMENT}/.env" ]; then
    source "environments/${ENVIRONMENT}/.env"
fi

# Generate main configuration
gomplate \
    -f shared/base-config.yml \
    -o "${OUTPUT_DIR}/maos.yml"

echo "Configuration generated successfully in ${OUTPUT_DIR}/"
```

## Development Environment

### Configuration (`environments/development/.env`)

```bash
# Development Environment Configuration

# System Settings
ENVIRONMENT=development
LOG_LEVEL=DEBUG
MAX_AGENTS=5

# Security (Relaxed for development)
MAOS_SECURITY_AUTH_REQUIRE_AUTH=false
MAOS_SECURITY_ENCRYPTION_AT_REST_ENABLED=false
MAOS_SECURITY_ENCRYPTION_IN_TRANSIT_ENABLED=false

# Database (Local)
POSTGRES_DB=maos_dev
POSTGRES_USER=maos
POSTGRES_PASSWORD=devpassword
MAOS_DATABASE_PRIMARY_URL=postgresql://maos:devpassword@postgres:5432/maos_dev
MAOS_DATABASE_PRIMARY_POOL_SIZE=10

# Redis (Local)
MAOS_REDIS_URL=redis://redis:6379/0
MAOS_REDIS_POOL_MAX_CONNECTIONS=20

# Storage (Local filesystem)
MAOS_CHECKPOINTS_STORAGE_BACKEND=local
MAOS_CHECKPOINTS_LOCAL_PATH=/app/checkpoints

# Claude API
CLAUDE_API_KEY=${CLAUDE_API_KEY:-your-dev-api-key}

# Development Features
MAOS_API_DEBUG=true
MAOS_DEVELOPMENT_DEBUG=true
MAOS_DEVELOPMENT_AUTO_RELOAD=true
MAOS_DEVELOPMENT_MOCKS_CLAUDE_API=false
MAOS_DEVELOPMENT_FIXTURES_LOAD_ON_STARTUP=true

# Monitoring (Basic)
MAOS_MONITORING_METRICS_ENABLED=true
MAOS_MONITORING_ALERTS_ENABLED=false

# Performance (Development optimized)
MAOS_SYSTEM_CHECKPOINT_INTERVAL=60
MAOS_AGENTS_DEFAULTS_TIMEOUT=900
MAOS_AGENTS_DEFAULTS_MAX_MEMORY=256MB
```

### Docker Compose (`environments/development/docker-compose.yml`)

```yaml
version: '3.8'

services:
  maos-dev:
    image: maos/orchestrator:latest
    container_name: maos-dev
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config:ro
      - ./data/checkpoints:/app/checkpoints
      - ./data/logs:/app/logs
      - ../../src:/app/src  # Mount source for live reload
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    command: ["maos", "start", "--reload"]

  postgres:
    image: postgres:15-alpine
    container_name: maos-postgres-dev
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
      - ./scripts/dev-seed.sql:/docker-entrypoint-initdb.d/seed.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: maos-redis-dev
    ports:
      - "6379:6379"
    volumes:
      - redis_dev_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Optional development tools
  mailhog:
    image: mailhog/mailhog:latest
    container_name: maos-mailhog
    ports:
      - "1025:1025"  # SMTP
      - "8025:8025"  # Web UI

volumes:
  postgres_dev_data:
  redis_dev_data:
```

### Development Setup Script

```bash
#!/bin/bash
# environments/development/setup.sh

set -euo pipefail

echo "Setting up MAOS development environment..."

# Generate configuration
../../shared/scripts/generate-config.sh development

# Create directories
mkdir -p data/{checkpoints,logs}

# Start services
docker-compose up -d

# Wait for services
echo "Waiting for services to start..."
sleep 30

# Run database migrations
docker-compose exec maos-dev maos db migrate

# Load test fixtures
docker-compose exec maos-dev maos fixtures load

# Create development user
docker-compose exec maos-dev maos user create dev \
    --email dev@localhost \
    --password devpass123 \
    --role admin

echo "Development environment ready!"
echo "API: http://localhost:8000"
echo "Mail UI: http://localhost:8025"
echo "Database: localhost:5432 (maos/devpassword)"
```

## Staging Environment

### Configuration (`environments/staging/.env`)

```bash
# Staging Environment Configuration

# System Settings
ENVIRONMENT=staging
LOG_LEVEL=INFO
MAX_AGENTS=15

# Security (Production-like but with test certs)
MAOS_SECURITY_AUTH_REQUIRE_AUTH=true
MAOS_SECURITY_ENCRYPTION_AT_REST_ENABLED=true
MAOS_SECURITY_ENCRYPTION_IN_TRANSIT_ENABLED=true

# Database (External staging database)
POSTGRES_DB=maos_staging
POSTGRES_USER=maos
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
MAOS_DATABASE_PRIMARY_URL=postgresql://maos:${POSTGRES_PASSWORD}@staging-db.internal:5432/maos_staging
MAOS_DATABASE_PRIMARY_POOL_SIZE=20

# Redis (Staging cluster)
MAOS_REDIS_URL=redis://:${REDIS_PASSWORD}@staging-redis.internal:6379/0
MAOS_REDIS_POOL_MAX_CONNECTIONS=50

# Storage (Staging S3 bucket)
MAOS_CHECKPOINTS_STORAGE_BACKEND=s3
MAOS_CHECKPOINTS_S3_BUCKET=maos-staging-checkpoints
MAOS_CHECKPOINTS_S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

# Claude API
CLAUDE_API_KEY=${CLAUDE_API_KEY}

# Security secrets
JWT_SECRET=${JWT_SECRET}
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# Monitoring
MAOS_MONITORING_METRICS_ENABLED=true
MAOS_MONITORING_ALERTS_ENABLED=true

# Performance (Staging optimized)
MAOS_SYSTEM_CHECKPOINT_INTERVAL=30
MAOS_AGENTS_DEFAULTS_TIMEOUT=1800
MAOS_AGENTS_DEFAULTS_MAX_MEMORY=512MB

# Test data configuration
MAOS_STAGING_SYNTHETIC_DATA=true
MAOS_STAGING_DATA_REFRESH_INTERVAL=86400  # 24 hours
```

### Kubernetes Configuration (`environments/staging/k8s/`)

#### Namespace and Secrets

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: maos-staging
  labels:
    environment: staging
    app: maos

---
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: maos-staging-secrets
  namespace: maos-staging
type: Opaque
data:
  jwt-secret: # base64 encoded
  postgres-password: # base64 encoded
  redis-password: # base64 encoded
  claude-api-key: # base64 encoded
  encryption-key: # base64 encoded
  aws-access-key-id: # base64 encoded
  aws-secret-access-key: # base64 encoded
```

#### Application Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: maos-staging
  namespace: maos-staging
  labels:
    app: maos
    environment: staging
spec:
  replicas: 2
  selector:
    matchLabels:
      app: maos
      environment: staging
  template:
    metadata:
      labels:
        app: maos
        environment: staging
    spec:
      containers:
      - name: maos
        image: maos/orchestrator:staging-latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        env:
        - name: MAOS_SYSTEM_ENVIRONMENT
          value: "staging"
        - name: MAOS_SYSTEM_MAX_AGENTS
          value: "15"
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: maos-staging-secrets
              key: jwt-secret
        # ... other environment variables
        
        resources:
          requests:
            cpu: 1
            memory: 2Gi
          limits:
            cpu: 2
            memory: 4Gi
        
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: maos-staging-service
  namespace: maos-staging
spec:
  selector:
    app: maos
    environment: staging
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP

---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: maos-staging-ingress
  namespace: maos-staging
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-staging
    nginx.ingress.kubernetes.io/rate-limit: "300"
spec:
  tls:
  - hosts:
    - staging-api.maos.yourdomain.com
    secretName: maos-staging-tls
  rules:
  - host: staging-api.maos.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: maos-staging-service
            port:
              number: 80
```

### Staging Deployment Script

```bash
#!/bin/bash
# environments/staging/deploy.sh

set -euo pipefail

NAMESPACE="maos-staging"
IMAGE_TAG="${1:-staging-latest}"

echo "Deploying MAOS to staging environment..."
echo "Image tag: ${IMAGE_TAG}"

# Generate configuration
../../shared/scripts/generate-config.sh staging

# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml

# Update image tag
kubectl set image deployment/maos-staging \
    maos=maos/orchestrator:${IMAGE_TAG} \
    -n ${NAMESPACE}

# Apply remaining manifests
kubectl apply -f k8s/

# Wait for rollout
kubectl rollout status deployment/maos-staging -n ${NAMESPACE} --timeout=300s

# Run database migrations
kubectl exec deployment/maos-staging -n ${NAMESPACE} -- maos db migrate

# Refresh test data
kubectl exec deployment/maos-staging -n ${NAMESPACE} -- maos staging refresh-data

echo "Staging deployment complete!"
echo "URL: https://staging-api.maos.yourdomain.com"
```

## Production Environment

### Configuration (`environments/production/.env`)

```bash
# Production Environment Configuration

# System Settings
ENVIRONMENT=production
LOG_LEVEL=WARNING
MAX_AGENTS=50

# Security (Full production security)
MAOS_SECURITY_AUTH_REQUIRE_AUTH=true
MAOS_SECURITY_ENCRYPTION_AT_REST_ENABLED=true
MAOS_SECURITY_ENCRYPTION_IN_TRANSIT_ENABLED=true

# High Availability Database
MAOS_DATABASE_PRIMARY_URL=postgresql://maos:${POSTGRES_PASSWORD}@prod-db-primary.internal:5432/maos
MAOS_DATABASE_REPLICA_URL=postgresql://maos:${POSTGRES_PASSWORD}@prod-db-replica.internal:5432/maos
MAOS_DATABASE_PRIMARY_POOL_SIZE=50
MAOS_DATABASE_REPLICA_POOL_SIZE=30

# Redis Cluster
MAOS_REDIS_CLUSTER_ENABLED=true
MAOS_REDIS_CLUSTER_NODES=prod-redis-1.internal:6379,prod-redis-2.internal:6379,prod-redis-3.internal:6379
MAOS_REDIS_PASSWORD=${REDIS_PASSWORD}
MAOS_REDIS_POOL_MAX_CONNECTIONS=100

# Production Storage
MAOS_CHECKPOINTS_STORAGE_BACKEND=s3
MAOS_CHECKPOINTS_S3_BUCKET=maos-prod-checkpoints
MAOS_CHECKPOINTS_S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

# Claude API
CLAUDE_API_KEY=${CLAUDE_API_KEY}

# Security
JWT_SECRET=${JWT_SECRET}
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# Monitoring (Full monitoring stack)
MAOS_MONITORING_METRICS_ENABLED=true
MAOS_MONITORING_ALERTS_ENABLED=true
MAOS_MONITORING_BACKEND=prometheus
DATADOG_API_KEY=${DATADOG_API_KEY}  # Optional

# Performance (Production optimized)
MAOS_SYSTEM_CHECKPOINT_INTERVAL=30
MAOS_AGENTS_DEFAULTS_TIMEOUT=3600
MAOS_AGENTS_DEFAULTS_MAX_MEMORY=2GB

# API Rate limiting
MAOS_API_RATE_LIMIT_ENABLED=true
MAOS_API_RATE_LIMIT_REQUESTS_PER_MINUTE=1000
```

### Helm Chart Values (`environments/production/helm-values.yaml`)

```yaml
# Production Helm values
global:
  environment: production
  imageTag: "1.0.0"

maos:
  replicaCount: 3
  
  image:
    pullPolicy: IfNotPresent
  
  resources:
    requests:
      cpu: 2
      memory: 4Gi
    limits:
      cpu: 4
      memory: 8Gi
  
  config:
    system:
      environment: production
      logLevel: WARNING
      maxAgents: 50

# External services (managed outside of Helm)
postgresql:
  enabled: false
  
redis:
  enabled: false

# Monitoring
monitoring:
  prometheus:
    enabled: true
  grafana:
    enabled: true
  alertmanager:
    enabled: true

# Auto-scaling
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70

# Security
podSecurityPolicy:
  enabled: true
  
networkPolicy:
  enabled: true
  
serviceAccount:
  create: true
  name: maos-prod

# Ingress
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: api.maos.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: maos-prod-tls
      hosts:
        - api.maos.yourdomain.com
```

## Environment Management Tools

### Environment Switcher Script

```bash
#!/bin/bash
# shared/scripts/switch-env.sh

set -euo pipefail

ENVIRONMENT=${1:-}
COMMAND=${2:-status}

if [ -z "$ENVIRONMENT" ]; then
    echo "Usage: $0 <environment> [command]"
    echo "Environments: development, staging, production, demo"
    echo "Commands: status, start, stop, deploy, logs, shell"
    exit 1
fi

WORK_DIR="environments/${ENVIRONMENT}"

if [ ! -d "$WORK_DIR" ]; then
    echo "Error: Environment '${ENVIRONMENT}' not found"
    exit 1
fi

cd "$WORK_DIR"

case "$COMMAND" in
    status)
        echo "Environment: ${ENVIRONMENT}"
        if [ -f "docker-compose.yml" ]; then
            docker-compose ps
        fi
        if [ -d "k8s" ]; then
            kubectl get pods -n "maos-${ENVIRONMENT}" 2>/dev/null || echo "Kubernetes namespace not found"
        fi
        ;;
    
    start)
        echo "Starting ${ENVIRONMENT} environment..."
        if [ -f "docker-compose.yml" ]; then
            docker-compose up -d
        fi
        ;;
    
    stop)
        echo "Stopping ${ENVIRONMENT} environment..."
        if [ -f "docker-compose.yml" ]; then
            docker-compose down
        fi
        ;;
    
    deploy)
        echo "Deploying ${ENVIRONMENT} environment..."
        if [ -f "deploy.sh" ]; then
            ./deploy.sh
        elif [ -f "helm-values.yaml" ]; then
            helm upgrade --install "maos-${ENVIRONMENT}" maos/maos \
                -n "maos-${ENVIRONMENT}" \
                -f helm-values.yaml
        fi
        ;;
    
    logs)
        if [ -f "docker-compose.yml" ]; then
            docker-compose logs -f
        fi
        ;;
    
    shell)
        if [ -f "docker-compose.yml" ]; then
            docker-compose exec maos-${ENVIRONMENT} /bin/bash
        fi
        ;;
    
    *)
        echo "Unknown command: ${COMMAND}"
        exit 1
        ;;
esac
```

### Configuration Validation

```bash
#!/bin/bash
# shared/scripts/validate-config.sh

set -euo pipefail

ENVIRONMENT=${1:-}

if [ -z "$ENVIRONMENT" ]; then
    echo "Usage: $0 <environment>"
    exit 1
fi

WORK_DIR="environments/${ENVIRONMENT}"
CONFIG_FILE="${WORK_DIR}/config/maos.yml"

echo "Validating configuration for ${ENVIRONMENT}..."

# Check if configuration exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file not found: $CONFIG_FILE"
    echo "Run: shared/scripts/generate-config.sh $ENVIRONMENT"
    exit 1
fi

# Validate YAML syntax
if ! python3 -c "import yaml; yaml.safe_load(open('$CONFIG_FILE'))" 2>/dev/null; then
    echo "Error: Invalid YAML syntax in $CONFIG_FILE"
    exit 1
fi

# Validate MAOS configuration
if command -v maos >/dev/null 2>&1; then
    if ! maos config validate --file "$CONFIG_FILE"; then
        echo "Error: Invalid MAOS configuration"
        exit 1
    fi
fi

# Environment-specific validations
case "$ENVIRONMENT" in
    production)
        # Check required production settings
        if grep -q "debug.*true" "$CONFIG_FILE"; then
            echo "Warning: Debug mode enabled in production"
        fi
        
        if grep -q "require_auth.*false" "$CONFIG_FILE"; then
            echo "Error: Authentication disabled in production"
            exit 1
        fi
        ;;
        
    development)
        # Development-specific checks
        if grep -q "max_agents.*[5-9][0-9]" "$CONFIG_FILE"; then
            echo "Warning: High agent count in development"
        fi
        ;;
esac

echo "Configuration validation passed for ${ENVIRONMENT}"
```

### Environment Comparison Tool

```bash
#!/bin/bash
# shared/scripts/compare-envs.sh

set -euo pipefail

ENV1=${1:-}
ENV2=${2:-}

if [ -z "$ENV1" ] || [ -z "$ENV2" ]; then
    echo "Usage: $0 <env1> <env2>"
    exit 1
fi

CONFIG1="environments/${ENV1}/config/maos.yml"
CONFIG2="environments/${ENV2}/config/maos.yml"

echo "Comparing configurations: ${ENV1} vs ${ENV2}"
echo "==========================================="

# Check if both configs exist
for config in "$CONFIG1" "$CONFIG2"; do
    if [ ! -f "$config" ]; then
        echo "Error: Configuration not found: $config"
        exit 1
    fi
done

# Show differences
diff -u "$CONFIG1" "$CONFIG2" | grep -E '^[+-]' | grep -v -E '^[+-]{3}' || {
    echo "No differences found"
    exit 0
}
```

## CI/CD Pipeline Integration

### GitHub Actions

```yaml
# .github/workflows/multi-environment.yml
name: Multi-Environment Deployment

on:
  push:
    branches:
      - main
      - develop
      - staging
  pull_request:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Development Environment
        run: |
          cd environments/development
          ./setup.sh
          
      - name: Run Tests
        run: |
          cd environments/development
          docker-compose exec -T maos-dev maos test
          
  deploy-staging:
    if: github.ref == 'refs/heads/staging'
    needs: test
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v1
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_STAGING }}
          
      - name: Deploy to Staging
        run: |
          cd environments/staging
          ./deploy.sh ${{ github.sha }}
          
  deploy-production:
    if: github.ref == 'refs/heads/main'
    needs: test
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v1
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_PROD }}
          
      - name: Deploy to Production
        run: |
          cd environments/production
          helm upgrade --install maos-prod maos/maos \
            -f helm-values.yaml \
            --set image.tag=${{ github.sha }} \
            --wait
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - test
  - deploy-staging
  - deploy-production

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: ""

validate-configs:
  stage: validate
  script:
    - |
      for env in development staging production; do
        shared/scripts/generate-config.sh $env
        shared/scripts/validate-config.sh $env
      done

test-development:
  stage: test
  script:
    - cd environments/development
    - ./setup.sh
    - docker-compose exec -T maos-dev maos test

deploy-staging:
  stage: deploy-staging
  environment:
    name: staging
    url: https://staging-api.maos.yourdomain.com
  only:
    - staging
  script:
    - cd environments/staging
    - kubectl config use-context $KUBE_CONTEXT_STAGING
    - ./deploy.sh $CI_COMMIT_SHA

deploy-production:
  stage: deploy-production
  environment:
    name: production
    url: https://api.maos.yourdomain.com
  only:
    - main
  when: manual
  script:
    - cd environments/production
    - kubectl config use-context $KUBE_CONTEXT_PROD
    - helm upgrade --install maos-prod maos/maos \
        -f helm-values.yaml \
        --set image.tag=$CI_COMMIT_SHA \
        --wait
```

## Best Practices

### 1. Configuration Management

- **Use templates**: Single source of truth with environment-specific overrides
- **Secret management**: Never commit secrets, use proper secret management
- **Validation**: Always validate configurations before deployment
- **Documentation**: Document environment-specific differences

### 2. Environment Parity

- **Minimize differences**: Keep environments as similar as possible
- **Infrastructure as Code**: Define all infrastructure in version control
- **Automated deployment**: Use consistent deployment processes
- **Testing**: Test deployment process in staging before production

### 3. Security

- **Environment isolation**: Separate networks and access controls
- **Secret rotation**: Regular rotation of secrets and certificates
- **Least privilege**: Minimal required permissions for each environment
- **Audit logging**: Track all changes and access

### 4. Monitoring

- **Environment-specific monitoring**: Different alert thresholds per environment
- **Cross-environment comparison**: Monitor differences between environments
- **Deployment monitoring**: Track deployment success and health
- **Performance baselines**: Establish performance baselines per environment

This multi-environment setup ensures consistent, secure, and maintainable deployments across all stages of the development lifecycle while maintaining the flexibility needed for each environment's specific requirements.