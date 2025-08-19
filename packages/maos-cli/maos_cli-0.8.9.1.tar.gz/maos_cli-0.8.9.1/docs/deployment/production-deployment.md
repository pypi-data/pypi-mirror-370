# MAOS Production Deployment Guide

## Overview

This guide covers deploying MAOS in production environments with high availability, security, and scalability. Choose from Docker Compose, Kubernetes, or bare metal deployment options.

## Pre-Deployment Checklist

### Infrastructure Requirements

**Minimum Production Requirements:**
- **CPU**: 8 cores (16 recommended)
- **RAM**: 16GB (32GB recommended)
- **Storage**: 100GB SSD (500GB+ recommended)
- **Network**: 1Gbps connection
- **OS**: Ubuntu 20.04+, RHEL 8+, or compatible

**Recommended Production Setup:**
- **Application Servers**: 3 nodes (HA setup)
- **Database**: PostgreSQL cluster with standby
- **Cache**: Redis cluster (3 masters + 3 replicas)
- **Storage**: S3-compatible object storage
- **Load Balancer**: HAProxy, NGINX, or cloud LB

### Dependencies

```bash
# Required services
- PostgreSQL 13+ (clustered for HA)
- Redis 6+ (clustered for HA)
- S3-compatible storage
- SSL certificates
- DNS configuration
- Monitoring stack (Prometheus + Grafana)
```

## Option 1: Docker Compose Production

### 1. Prepare Environment

```bash
# Create production directory
mkdir maos-production && cd maos-production

# Download production compose file
curl -O https://raw.githubusercontent.com/maos-team/maos/main/docker-compose.prod.yml

# Create directories
mkdir -p {config,secrets,data/{logs,checkpoints},ssl}
```

### 2. Configure Environment

Create `.env.production`:

```bash
# System Configuration
MAOS_SYSTEM_ENVIRONMENT=production
MAOS_SYSTEM_LOG_LEVEL=WARNING
MAOS_SYSTEM_MAX_AGENTS=50

# Security
MAOS_SECURITY_AUTH_REQUIRE_AUTH=true
MAOS_SECURITY_ENCRYPTION_AT_REST_ENABLED=true
MAOS_SECURITY_ENCRYPTION_IN_TRANSIT_ENABLED=true

# Secrets (use secure generation)
JWT_SECRET=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)
ENCRYPTION_KEY=$(openssl rand -hex 32)

# Database (External)
MAOS_DATABASE_PRIMARY_URL="postgresql://maos:${DB_PASSWORD}@postgres-primary:5432/maos"
MAOS_DATABASE_PRIMARY_POOL_SIZE=30
MAOS_DATABASE_PRIMARY_MAX_OVERFLOW=20

# Redis (External)  
MAOS_REDIS_URL="redis://:${REDIS_PASSWORD}@redis-cluster:6379/0"
MAOS_REDIS_POOL_MAX_CONNECTIONS=100

# Storage (S3)
MAOS_CHECKPOINTS_STORAGE_BACKEND=s3
MAOS_CHECKPOINTS_S3_BUCKET=maos-prod-checkpoints
MAOS_CHECKPOINTS_S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Claude API
CLAUDE_API_KEY=your-claude-api-key

# SSL Configuration
MAOS_API_TLS_ENABLED=true
MAOS_API_TLS_CERT_PATH=/app/ssl/cert.pem
MAOS_API_TLS_KEY_PATH=/app/ssl/key.pem

# Monitoring
MAOS_MONITORING_METRICS_ENABLED=true
MAOS_MONITORING_ALERTS_ENABLED=true
```

### 3. Production Docker Compose

`docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # Load Balancer
  nginx:
    image: nginx:alpine
    container_name: maos-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - maos-app-1
      - maos-app-2
      - maos-app-3
    restart: unless-stopped

  # MAOS Application Instances (HA)
  maos-app-1: &maos-app
    image: maos/orchestrator:1.0.0
    container_name: maos-app-1
    env_file: .env.production
    environment:
      - MAOS_INSTANCE_ID=app-1
      - MAOS_API_PORT=8000
    volumes:
      - ./config/maos.yml:/app/config/maos.yml:ro
      - ./ssl:/app/ssl:ro
      - ./data/logs:/app/logs
    depends_on:
      - postgres-primary
      - redis-cluster
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "https://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G

  maos-app-2:
    <<: *maos-app
    container_name: maos-app-2
    environment:
      - MAOS_INSTANCE_ID=app-2
      - MAOS_API_PORT=8000

  maos-app-3:
    <<: *maos-app
    container_name: maos-app-3
    environment:
      - MAOS_INSTANCE_ID=app-3
      - MAOS_API_PORT=8000

  # PostgreSQL HA Cluster
  postgres-primary:
    image: postgres:15
    container_name: postgres-primary
    environment:
      - POSTGRES_DB=maos
      - POSTGRES_USER=maos
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_REPLICATION_MODE=master
      - POSTGRES_REPLICATION_USER=replicator
      - POSTGRES_REPLICATION_PASSWORD=${DB_REPL_PASSWORD}
    volumes:
      - postgres_primary_data:/var/lib/postgresql/data
      - ./config/postgresql.conf:/etc/postgresql/postgresql.conf:ro
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  postgres-standby:
    image: postgres:15
    container_name: postgres-standby
    environment:
      - POSTGRES_REPLICATION_MODE=slave
      - POSTGRES_REPLICATION_USER=replicator
      - POSTGRES_REPLICATION_PASSWORD=${DB_REPL_PASSWORD}
      - POSTGRES_MASTER_SERVICE=postgres-primary
    volumes:
      - postgres_standby_data:/var/lib/postgresql/data
    depends_on:
      - postgres-primary
    restart: unless-stopped

  # Redis Cluster
  redis-cluster:
    image: redis:7-alpine
    container_name: redis-cluster
    command: >
      sh -c "
      redis-server --cluster-enabled yes 
      --cluster-config-file nodes.conf 
      --cluster-node-timeout 5000 
      --appendonly yes 
      --requirepass ${REDIS_PASSWORD}
      --masterauth ${REDIS_PASSWORD}
      "
    volumes:
      - redis_cluster_data:/data
    restart: unless-stopped

  # Monitoring Stack
  prometheus:
    image: prom/prometheus:v2.45.0
    container_name: maos-prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:10.1.0
    container_name: maos-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SECURITY_DISABLE_GRAVATAR=true
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana:/etc/grafana/provisioning:ro
    ports:
      - "3000:3000"
    restart: unless-stopped

  # Alert Manager
  alertmanager:
    image: prom/alertmanager:v0.25.0
    container_name: maos-alertmanager
    volumes:
      - ./config/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
      - alertmanager_data:/alertmanager
    ports:
      - "9093:9093"
    restart: unless-stopped

volumes:
  postgres_primary_data:
  postgres_standby_data:
  redis_cluster_data:
  prometheus_data:
  grafana_data:
  alertmanager_data:

networks:
  default:
    name: maos-production
    driver: bridge
```

### 4. NGINX Configuration

`config/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream maos_backend {
        least_conn;
        server maos-app-1:8000 max_fails=3 fail_timeout=30s;
        server maos-app-2:8000 max_fails=3 fail_timeout=30s;
        server maos-app-3:8000 max_fails=3 fail_timeout=30s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name api.maos.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS API Server
    server {
        listen 443 ssl http2;
        server_name api.maos.yourdomain.com;

        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";

        # API Proxy
        location /v1/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://maos_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 60s;
            proxy_read_timeout 300s;
            
            # Health check
            proxy_next_upstream error timeout http_502 http_503 http_504;
        }

        # Health check endpoint
        location /health {
            proxy_pass http://maos_backend/health;
            access_log off;
        }

        # WebSocket support
        location /ws {
            proxy_pass http://maos_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 5. Deploy

```bash
# Set up SSL certificates
sudo certbot certonly --standalone -d api.maos.yourdomain.com
cp /etc/letsencrypt/live/api.maos.yourdomain.com/fullchain.pem ssl/cert.pem
cp /etc/letsencrypt/live/api.maos.yourdomain.com/privkey.pem ssl/key.pem

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Initialize database
docker-compose exec maos-app-1 maos db migrate

# Create admin user
docker-compose exec maos-app-1 maos user create admin --email admin@yourdomain.com

# Verify deployment
curl https://api.maos.yourdomain.com/health
```

## Option 2: Kubernetes Deployment

### 1. Prerequisites

```bash
# Required tools
kubectl version --client
helm version

# Add MAOS Helm repository
helm repo add maos https://charts.maos.dev
helm repo update
```

### 2. Create Namespace and Secrets

```bash
# Create namespace
kubectl create namespace maos-prod

# Create secrets
kubectl create secret generic maos-secrets \
  --from-literal=jwt-secret=$(openssl rand -hex 32) \
  --from-literal=db-password=$(openssl rand -hex 16) \
  --from-literal=redis-password=$(openssl rand -hex 16) \
  --from-literal=claude-api-key=your-claude-api-key \
  --from-literal=aws-access-key-id=your-access-key \
  --from-literal=aws-secret-access-key=your-secret-key \
  --namespace maos-prod

# Create TLS secret
kubectl create secret tls maos-tls \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key \
  --namespace maos-prod
```

### 3. Helm Values Configuration

`values-prod.yaml`:

```yaml
# MAOS Production Helm Values
global:
  environment: production
  imageTag: "1.0.0"
  imagePullPolicy: IfNotPresent

# Application Configuration
maos:
  replicaCount: 3
  
  image:
    repository: maos/orchestrator
    tag: "1.0.0"
  
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
      logLevel: INFO
      maxAgents: 50
    
    security:
      auth:
        requireAuth: true
      encryption:
        atRestEnabled: true
        inTransitEnabled: true
    
    monitoring:
      metrics:
        enabled: true
      alerts:
        enabled: true

# Service Configuration
service:
  type: ClusterIP
  port: 8000
  targetPort: 8000

# Ingress Configuration
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "600"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  
  hosts:
    - host: api.maos.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  
  tls:
    - secretName: maos-tls
      hosts:
        - api.maos.yourdomain.com

# Database Configuration
postgresql:
  enabled: true
  auth:
    postgresPassword: ""
    existingSecret: maos-secrets
    secretKeys:
      adminPasswordKey: db-password
  
  architecture: replication
  primary:
    resources:
      requests:
        cpu: 1
        memory: 2Gi
      limits:
        cpu: 2
        memory: 4Gi
    
    persistence:
      enabled: true
      size: 100Gi
      storageClass: fast-ssd
  
  readReplicas:
    replicaCount: 1
    resources:
      requests:
        cpu: 500m
        memory: 1Gi
      limits:
        cpu: 1
        memory: 2Gi

# Redis Configuration
redis:
  enabled: true
  auth:
    enabled: true
    existingSecret: maos-secrets
    existingSecretPasswordKey: redis-password
  
  architecture: replication
  master:
    resources:
      requests:
        cpu: 500m
        memory: 1Gi
      limits:
        cpu: 1
        memory: 2Gi
    
    persistence:
      enabled: true
      size: 50Gi
      storageClass: fast-ssd
  
  replica:
    replicaCount: 2
    resources:
      requests:
        cpu: 250m
        memory: 512Mi
      limits:
        cpu: 500m
        memory: 1Gi

# Monitoring Stack
monitoring:
  prometheus:
    enabled: true
    persistence:
      size: 50Gi
      storageClass: standard
  
  grafana:
    enabled: true
    adminPassword: ""
    existingSecret: maos-secrets
    existingSecretPasswordKey: grafana-password
    
    persistence:
      enabled: true
      size: 10Gi
      storageClass: standard
  
  alertmanager:
    enabled: true
    config:
      global:
        smtp_smarthost: 'localhost:587'
        smtp_from: 'alerts@maos.yourdomain.com'

# Auto Scaling
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

# Pod Disruption Budget
podDisruptionBudget:
  enabled: true
  minAvailable: 2

# Network Policies
networkPolicy:
  enabled: true
  ingress:
    enabled: true
  egress:
    enabled: true

# Storage Configuration
storage:
  checkpoints:
    backend: s3
    s3:
      bucket: maos-prod-checkpoints
      region: us-east-1
      existingSecret: maos-secrets
```

### 4. Deploy with Helm

```bash
# Install MAOS
helm install maos-prod maos/maos \
  --namespace maos-prod \
  --values values-prod.yaml \
  --wait --timeout 10m

# Verify deployment
kubectl get pods -n maos-prod
kubectl get services -n maos-prod
kubectl get ingress -n maos-prod

# Check logs
kubectl logs -f deployment/maos-prod -n maos-prod

# Run database migrations
kubectl exec -it deployment/maos-prod -n maos-prod -- maos db migrate

# Create admin user
kubectl exec -it deployment/maos-prod -n maos-prod -- maos user create admin --email admin@yourdomain.com
```

### 5. Monitoring and Alerting

```bash
# Access Grafana
kubectl port-forward svc/maos-prod-grafana 3000:3000 -n maos-prod

# Access Prometheus
kubectl port-forward svc/maos-prod-prometheus 9090:9090 -n maos-prod

# View alerts
kubectl port-forward svc/maos-prod-alertmanager 9093:9093 -n maos-prod
```

## Production Configuration

### Security Hardening

1. **Authentication & Authorization**
   ```yaml
   security:
     auth:
       requireAuth: true
       jwtExpiry: 3600
       refreshExpiry: 604800
     
     rateLimiting:
       enabled: true
       maxRequests: 1000
       windowSize: 3600
   ```

2. **Encryption**
   ```yaml
   encryption:
     atRest:
       enabled: true
       algorithm: AES-256-GCM
     inTransit:
       enabled: true
       tlsVersion: "1.3"
   ```

3. **Network Security**
   ```yaml
   networkPolicy:
     enabled: true
     ingress:
       - from:
         - namespaceSelector:
             matchLabels:
               name: ingress-nginx
         ports:
         - protocol: TCP
           port: 8000
   ```

### Performance Optimization

1. **Resource Allocation**
   ```yaml
   resources:
     requests:
       cpu: 2
       memory: 4Gi
     limits:
       cpu: 4
       memory: 8Gi
   ```

2. **Auto Scaling**
   ```yaml
   autoscaling:
     enabled: true
     minReplicas: 3
     maxReplicas: 20
     metrics:
       - type: Resource
         resource:
           name: cpu
           target:
             type: Utilization
             averageUtilization: 70
   ```

3. **Database Optimization**
   ```sql
   -- PostgreSQL performance tuning
   ALTER SYSTEM SET shared_buffers = '2GB';
   ALTER SYSTEM SET effective_cache_size = '6GB';
   ALTER SYSTEM SET work_mem = '64MB';
   ALTER SYSTEM SET maintenance_work_mem = '512MB';
   SELECT pg_reload_conf();
   ```

### Monitoring Configuration

```yaml
# Prometheus scrape config
scrape_configs:
  - job_name: 'maos'
    static_configs:
      - targets: ['maos-app-1:8000', 'maos-app-2:8000', 'maos-app-3:8000']
    metrics_path: /metrics
    scrape_interval: 15s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-primary:9187']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-cluster:9121']
    scrape_interval: 30s
```

### Backup Strategy

1. **Database Backups**
   ```bash
   # Daily automated backups
   kubectl create cronjob postgres-backup \
     --image=postgres:15 \
     --schedule="0 2 * * *" \
     --restart=OnFailure \
     -- pg_dump -h postgres-primary -U maos -d maos | gzip > /backups/$(date +%Y%m%d).sql.gz
   ```

2. **Checkpoint Backups**
   ```bash
   # S3 backup with versioning enabled
   aws s3api put-bucket-versioning \
     --bucket maos-prod-checkpoints \
     --versioning-configuration Status=Enabled
   
   # Lifecycle policy for old versions
   aws s3api put-bucket-lifecycle-configuration \
     --bucket maos-prod-checkpoints \
     --lifecycle-configuration file://lifecycle.json
   ```

### Disaster Recovery

1. **Multi-Region Setup**
   ```yaml
   # values-dr.yaml
   global:
     region: us-west-2
   
   postgresql:
     primary:
       configuration: |
         wal_level = replica
         max_wal_senders = 3
         wal_keep_segments = 64
   ```

2. **Recovery Procedures**
   ```bash
   # Automated failover testing
   kubectl create job disaster-recovery-test \
     --image=maos/dr-test:latest \
     --schedule="0 4 * * 0"  # Weekly
   ```

## Maintenance Procedures

### Rolling Updates

```bash
# Update MAOS to new version
helm upgrade maos-prod maos/maos \
  --namespace maos-prod \
  --values values-prod.yaml \
  --set image.tag=1.1.0 \
  --wait

# Monitor rollout
kubectl rollout status deployment/maos-prod -n maos-prod

# Rollback if needed
helm rollback maos-prod 1 -n maos-prod
```

### Scaling Operations

```bash
# Manual scaling
kubectl scale deployment maos-prod --replicas=5 -n maos-prod

# Update HPA limits
kubectl patch hpa maos-prod -n maos-prod -p '{"spec":{"maxReplicas":15}}'
```

### Health Checks

```bash
# Comprehensive health check script
#!/bin/bash
kubectl exec deployment/maos-prod -n maos-prod -- maos health --all-components
kubectl get pods -n maos-prod -o wide
kubectl top nodes
kubectl top pods -n maos-prod
```

## Troubleshooting Production Issues

### Common Production Issues

1. **High Memory Usage**
   ```bash
   # Check memory metrics
   kubectl top pods -n maos-prod --sort-by=memory
   
   # Adjust memory limits
   kubectl patch deployment maos-prod -n maos-prod -p '{"spec":{"template":{"spec":{"containers":[{"name":"maos","resources":{"limits":{"memory":"12Gi"}}}]}}}}'
   ```

2. **Database Connection Pool Exhaustion**
   ```bash
   # Increase pool size
   kubectl set env deployment/maos-prod -n maos-prod MAOS_DATABASE_PRIMARY_POOL_SIZE=50
   ```

3. **SSL Certificate Issues**
   ```bash
   # Renew certificates
   kubectl delete secret maos-tls -n maos-prod
   kubectl create secret tls maos-tls --cert=new-cert.pem --key=new-key.pem -n maos-prod
   ```

This production deployment guide ensures MAOS runs reliably at scale with proper security, monitoring, and maintenance procedures. Follow the post-deployment checklist to verify everything is working correctly.