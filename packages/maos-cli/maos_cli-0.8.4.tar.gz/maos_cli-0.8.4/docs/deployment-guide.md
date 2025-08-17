# MAOS Deployment Best Practices Guide

This comprehensive guide covers production deployment strategies, infrastructure requirements, and operational best practices for MAOS (Multi-Agent Operating System).

## Table of Contents

1. [Production Deployment Checklist](#production-deployment-checklist)
2. [Infrastructure Requirements](#infrastructure-requirements)
3. [Redis Cluster Setup](#redis-cluster-setup)
4. [Docker Deployment Strategies](#docker-deployment-strategies)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Scaling Considerations](#scaling-considerations)
7. [Performance Tuning](#performance-tuning)
8. [Security Hardening](#security-hardening)
9. [Monitoring and Observability](#monitoring-and-observability)
10. [Backup and Disaster Recovery](#backup-and-disaster-recovery)

## Production Deployment Checklist

### Pre-Deployment Checklist

**Infrastructure Requirements** ✓
- [ ] Minimum 16GB RAM, 8 CPU cores per node
- [ ] PostgreSQL 14+ with connection pooling
- [ ] Redis 7.0+ (cluster mode for HA)
- [ ] Load balancer configured
- [ ] SSL/TLS certificates installed
- [ ] Monitoring stack deployed

**Security Configuration** ✓
- [ ] API keys stored in secure secret management
- [ ] Network segmentation implemented
- [ ] Firewall rules configured
- [ ] RBAC policies defined
- [ ] Audit logging enabled
- [ ] Vulnerability scanning completed

**Performance Tuning** ✓
- [ ] Database indexes optimized
- [ ] Redis memory limits configured
- [ ] Connection pools sized appropriately
- [ ] Resource limits set for agents
- [ ] Caching strategies implemented

**Monitoring & Alerting** ✓
- [ ] Prometheus metrics exposed
- [ ] Grafana dashboards imported
- [ ] Critical alerts configured
- [ ] Log aggregation setup
- [ ] Health checks configured

**Backup & Recovery** ✓
- [ ] Automated backup schedules
- [ ] Recovery procedures tested
- [ ] Checkpoint storage configured
- [ ] Disaster recovery plan documented

### Post-Deployment Verification

```bash
# System health verification
maos health --all-components

# Performance baseline
maos benchmark --duration 300s --output baseline.json

# Load test
maos stress-test --concurrent-tasks 50 --duration 600s

# Security scan
maos security-scan --comprehensive

# Backup verification
maos backup verify --all
```

## Infrastructure Requirements

### Minimum Production Environment

**Single Node Deployment:**
```yaml
Hardware Requirements:
  CPU: 8 cores (16 threads)
  RAM: 16 GB
  Storage: 200 GB SSD
  Network: 1 Gbps

Software Requirements:
  OS: Ubuntu 20.04 LTS / RHEL 8 / CentOS 8
  Python: 3.11+
  PostgreSQL: 14+
  Redis: 7.0+
  Docker: 24+
```

**High Availability Deployment:**
```yaml
Load Balancer:
  CPU: 4 cores
  RAM: 8 GB
  Storage: 50 GB

MAOS Nodes (3+ nodes):
  CPU: 16 cores (32 threads)
  RAM: 32 GB  
  Storage: 500 GB SSD
  Network: 10 Gbps

Database Cluster:
  Primary: 16 cores, 64 GB RAM, 1TB SSD
  Replicas: 8 cores, 32 GB RAM, 500 GB SSD

Redis Cluster:
  Nodes: 6 nodes (3 masters, 3 replicas)
  CPU: 8 cores per node
  RAM: 16 GB per node
  Storage: 200 GB SSD per node
```

### Network Architecture

```mermaid
graph TB
    LB[Load Balancer] --> M1[MAOS Node 1]
    LB --> M2[MAOS Node 2]  
    LB --> M3[MAOS Node 3]
    
    M1 --> PG[(PostgreSQL Primary)]
    M2 --> PG
    M3 --> PG
    PG --> PGR1[(PostgreSQL Replica 1)]
    PG --> PGR2[(PostgreSQL Replica 2)]
    
    M1 --> RC[Redis Cluster]
    M2 --> RC
    M3 --> RC
    RC --> R1[(Redis Master 1)]
    RC --> R2[(Redis Master 2)]
    RC --> R3[(Redis Master 3)]
    RC --> R4[(Redis Replica 1)]
    RC --> R5[(Redis Replica 2)]
    RC --> R6[(Redis Replica 3)]
```

### Cloud Provider Specifications

#### AWS Deployment

```yaml
# EC2 Instance Types
MAOS Nodes: c6i.4xlarge (16 vCPU, 32 GB RAM)
Database: r6i.2xlarge (8 vCPU, 64 GB RAM)
Redis: r6i.xlarge (4 vCPU, 32 GB RAM)

# Storage
Database: gp3 with 10,000 IOPS
Redis: gp3 with 5,000 IOPS
Checkpoints: S3 with intelligent tiering

# Networking
VPC: Multi-AZ deployment
Subnets: Private for databases, public for load balancer
Security Groups: Restrictive rules
```

#### Azure Deployment

```yaml
# VM Types
MAOS Nodes: Standard_D16s_v5 (16 vCPU, 64 GB RAM)
Database: Standard_E8s_v5 (8 vCPU, 64 GB RAM) 
Redis: Standard_E4s_v5 (4 vCPU, 32 GB RAM)

# Storage
Database: Premium SSD with 5,000 IOPS
Redis: Premium SSD with 2,000 IOPS
Checkpoints: Blob Storage with hot/cool tiers

# Networking
VNet: Multi-region deployment
Subnets: Private for databases
NSGs: Restrictive security rules
```

#### GCP Deployment

```yaml
# Machine Types
MAOS Nodes: c2-standard-16 (16 vCPU, 64 GB RAM)
Database: n2-highmem-8 (8 vCPU, 64 GB RAM)
Redis: n2-standard-4 (4 vCPU, 16 GB RAM)

# Storage
Database: SSD persistent disk, 10,000 IOPS
Redis: SSD persistent disk, 5,000 IOPS
Checkpoints: Cloud Storage with lifecycle management

# Networking
VPC: Multi-zone deployment
Subnets: Private for databases
Firewall Rules: Least privilege access
```

## Redis Cluster Setup

### Redis Cluster Architecture

```bash
# 6-node Redis cluster (3 masters, 3 replicas)
redis-01:6379 (master)   -> redis-04:6379 (replica)
redis-02:6379 (master)   -> redis-05:6379 (replica)  
redis-03:6379 (master)   -> redis-06:6379 (replica)
```

### Redis Configuration

**Master Configuration (`redis-master.conf`):**
```conf
# Network
bind 0.0.0.0
port 6379
protected-mode yes
requirepass your-secure-password

# Cluster
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 15000
cluster-announce-ip 10.0.1.10

# Memory
maxmemory 8gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec

# Performance
tcp-keepalive 60
tcp-backlog 511
timeout 0

# Logging
logfile /var/log/redis/redis-server.log
loglevel notice
```

**Replica Configuration (`redis-replica.conf`):**
```conf
# Include master config
include /etc/redis/redis-master.conf

# Replica-specific settings
replica-read-only yes
replica-serve-stale-data yes
repl-diskless-sync yes
repl-diskless-sync-delay 5
```

### Cluster Setup Script

```bash
#!/bin/bash
# redis-cluster-setup.sh

# Create Redis cluster
redis-cli --cluster create \
  10.0.1.10:6379 \
  10.0.1.11:6379 \
  10.0.1.12:6379 \
  10.0.1.13:6379 \
  10.0.1.14:6379 \
  10.0.1.15:6379 \
  --cluster-replicas 1 \
  --cluster-yes

# Verify cluster status
redis-cli --cluster check 10.0.1.10:6379

# Test cluster connectivity
redis-cli -c -h 10.0.1.10 -p 6379 -a your-secure-password ping
```

### Redis Monitoring

```bash
# Monitor cluster health
redis-cli --cluster info 10.0.1.10:6379

# Check node roles
redis-cli --cluster nodes 10.0.1.10:6379

# Monitor memory usage
redis-cli -h 10.0.1.10 -p 6379 info memory

# Monitor replication lag
redis-cli -h 10.0.1.13 -p 6379 info replication
```

## Docker Deployment Strategies

### Single Node Docker Deployment

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  maos:
    image: maos/maos:latest
    restart: unless-stopped
    ports:
      - "8000:8000"
      - "3001:3001"
    environment:
      - MAOS_DATABASE_PRIMARY_URL=postgresql://maos:${POSTGRES_PASSWORD}@postgres:5432/maos
      - MAOS_REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
    volumes:
      - ./config:/app/config
      - maos_checkpoints:/var/lib/maos/checkpoints
      - maos_logs:/var/log/maos
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "maos", "health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15
    restart: unless-stopped
    environment:
      - POSTGRES_DB=maos
      - POSTGRES_USER=maos
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U maos"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "--no-auth-warning", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - maos

  prometheus:
    image: prom/prometheus:latest
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning

volumes:
  postgres_data:
  redis_data:
  maos_checkpoints:
  maos_logs:
  prometheus_data:
  grafana_data:

networks:
  default:
    name: maos_network
```

### Multi-Node Docker Swarm

**docker-compose.swarm.yml:**
```yaml
version: '3.8'

services:
  maos:
    image: maos/maos:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 30s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      placement:
        constraints:
          - node.labels.role==app
    ports:
      - "8000:8000"
    environment:
      - MAOS_DATABASE_PRIMARY_URL=postgresql://maos:${POSTGRES_PASSWORD}@postgres:5432/maos
      - MAOS_REDIS_URL=redis://redis-cluster:6379/0
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
    volumes:
      - maos_checkpoints:/var/lib/maos/checkpoints
    networks:
      - maos_overlay

  postgres:
    image: postgres:15
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.role==database
    environment:
      - POSTGRES_DB=maos
      - POSTGRES_USER=maos  
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - maos_overlay

  redis-cluster:
    image: redis:7-alpine
    deploy:
      replicas: 6
      placement:
        max_replicas_per_node: 2
    volumes:
      - redis_data:/data
    networks:
      - maos_overlay

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local  
  maos_checkpoints:
    driver: nfs
    driver_opts:
      share: nfs-server:/var/nfs/maos-checkpoints

networks:
  maos_overlay:
    driver: overlay
    attachable: true
```

### Docker Deployment Commands

```bash
# Deploy single node
docker-compose -f docker-compose.prod.yml up -d

# Deploy to Docker Swarm
docker stack deploy -c docker-compose.swarm.yml maos

# Scale services
docker service scale maos_maos=5

# Update service
docker service update --image maos/maos:v2.1.0 maos_maos

# Monitor services
docker service ls
docker service logs maos_maos
```

## Kubernetes Deployment

### Namespace and Configuration

**namespace.yaml:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: maos
  labels:
    name: maos
```

**configmap.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: maos-config
  namespace: maos
data:
  config.yml: |
    system:
      max_agents: 20
      log_level: "INFO"
    database:
      primary_url: "postgresql://maos:${POSTGRES_PASSWORD}@postgres:5432/maos"
    redis:
      url: "redis://redis-cluster:6379/0"
    agents:
      defaults:
        max_memory: "2GB"
        timeout: 3600
```

**secrets.yaml:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: maos-secrets
  namespace: maos
type: Opaque
data:
  claude-api-key: <base64-encoded-api-key>
  postgres-password: <base64-encoded-password>
  redis-password: <base64-encoded-password>
```

### MAOS Deployment

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: maos
  namespace: maos
spec:
  replicas: 3
  selector:
    matchLabels:
      app: maos
  template:
    metadata:
      labels:
        app: maos
    spec:
      containers:
      - name: maos
        image: maos/maos:latest
        ports:
        - containerPort: 8000
        - containerPort: 3001
        env:
        - name: CLAUDE_API_KEY
          valueFrom:
            secretKeyRef:
              name: maos-secrets
              key: claude-api-key
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: maos-secrets
              key: postgres-password
        - name: MAOS_DATABASE_PRIMARY_URL
          value: "postgresql://maos:$(POSTGRES_PASSWORD)@postgres:5432/maos"
        - name: MAOS_REDIS_URL
          value: "redis://redis-cluster:6379/0"
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: checkpoints
          mountPath: /var/lib/maos/checkpoints
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
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
      volumes:
      - name: config
        configMap:
          name: maos-config
      - name: checkpoints
        persistentVolumeClaim:
          claimName: maos-checkpoints-pvc
```

### Services and Ingress

**service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: maos-service
  namespace: maos
spec:
  selector:
    app: maos
  ports:
  - name: api
    port: 8000
    targetPort: 8000
  - name: dashboard
    port: 3001
    targetPort: 3001
  type: ClusterIP
```

**ingress.yaml:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: maos-ingress
  namespace: maos
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.maos.your-domain.com
    - dashboard.maos.your-domain.com
    secretName: maos-tls
  rules:
  - host: api.maos.your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: maos-service
            port:
              number: 8000
  - host: dashboard.maos.your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: maos-service
            port:
              number: 3001
```

### Database Deployment

**postgres-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: maos
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: maos
        - name: POSTGRES_USER
          value: maos
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: maos-secrets
              key: postgres-password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 100Gi
      storageClassName: fast-ssd
```

### Horizontal Pod Autoscaler

**hpa.yaml:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: maos-hpa
  namespace: maos
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: maos
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 25
        periodSeconds: 60
```

### Deployment Commands

```bash
# Apply all configurations
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml

# Monitor deployment
kubectl get pods -n maos
kubectl logs -f deployment/maos -n maos

# Check scaling
kubectl get hpa -n maos
kubectl top pods -n maos
```

## Scaling Considerations

### Vertical Scaling

**CPU Scaling:**
```yaml
# Increase CPU resources
resources:
  requests:
    cpu: "4"
  limits:
    cpu: "8"

# Monitor CPU usage
kubectl top pods -n maos --sort-by=cpu
```

**Memory Scaling:**
```yaml
# Increase memory resources  
resources:
  requests:
    memory: "8Gi"
  limits:
    memory: "16Gi"

# Monitor memory usage
kubectl top pods -n maos --sort-by=memory
```

### Horizontal Scaling

**Auto-scaling Configuration:**
```bash
# Configure cluster autoscaler
kubectl patch deployment cluster-autoscaler \
  -n kube-system \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"cluster-autoscaler","command":["./cluster-autoscaler","--v=4","--stderrthreshold=info","--cloud-provider=aws","--skip-nodes-with-local-storage=false","--expander=least-waste","--node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/maos-cluster","--balance-similar-node-groups","--skip-nodes-with-system-pods=false"]}]}}}}'
```

**Load Testing for Scaling:**
```bash
# Load test to verify scaling
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- /bin/sh

# Generate load
while true; do wget -q -O- http://maos-service.maos.svc.cluster.local:8000/api/health; done
```

### Database Scaling

**Read Replicas:**
```yaml
# PostgreSQL read replica
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-replica
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: PGUSER
          value: maos
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: maos-secrets
              key: postgres-password
        - name: POSTGRES_MASTER_SERVICE
          value: postgres
        command:
        - /bin/bash
        - -c
        - |
          pg_basebackup -h $POSTGRES_MASTER_SERVICE -D /var/lib/postgresql/data -U maos -v -P -W
          echo "standby_mode = 'on'" >> /var/lib/postgresql/data/recovery.conf
          echo "primary_conninfo = 'host=$POSTGRES_MASTER_SERVICE port=5432 user=maos'" >> /var/lib/postgresql/data/recovery.conf
          postgres
```

**Connection Pooling:**
```yaml
# PgBouncer deployment
apiVersion: apps/v1  
kind: Deployment
metadata:
  name: pgbouncer
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: pgbouncer
        image: pgbouncer/pgbouncer:latest
        env:
        - name: DATABASES_HOST
          value: postgres
        - name: DATABASES_PORT
          value: "5432"
        - name: DATABASES_DBNAME
          value: maos
        - name: POOL_MODE
          value: transaction
        - name: MAX_CLIENT_CONN
          value: "1000"
        - name: DEFAULT_POOL_SIZE
          value: "25"
```

## Performance Tuning

### Application-Level Tuning

**MAOS Configuration Optimization:**
```yaml
# config/production.yml
system:
  max_agents: 50
  agent_spawn_rate: 10
  task_queue_size: 1000
  checkpoint_interval: 300

database:
  pool_size: 50
  max_overflow: 100
  pool_timeout: 30
  pool_recycle: 3600

redis:
  pool_size: 50
  socket_keepalive: true
  socket_keepalive_options:
    TCP_KEEPIDLE: 30
    TCP_KEEPINTVL: 5
    TCP_KEEPCNT: 3

agents:
  defaults:
    max_memory: "4GB"
    timeout: 7200
    batch_size: 10
    
task_planner:
  parallelization_threshold: 5
  max_parallel_branches: 8
  dependency_timeout: 1800
```

### Database Tuning

**PostgreSQL Configuration (`postgresql.conf`):**
```conf
# Memory Configuration
shared_buffers = 8GB
effective_cache_size = 24GB
maintenance_work_mem = 2GB
work_mem = 256MB

# Connection Settings
max_connections = 200
max_prepared_transactions = 200

# WAL Configuration
wal_level = replica
max_wal_size = 4GB
min_wal_size = 1GB
checkpoint_completion_target = 0.9

# Query Optimization
random_page_cost = 1.1
effective_io_concurrency = 200
max_worker_processes = 16
max_parallel_workers_per_gather = 4
max_parallel_workers = 16

# Logging
log_min_duration_statement = 1000
log_checkpoints = on
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

**Index Optimization:**
```sql
-- Critical indexes for MAOS
CREATE INDEX CONCURRENTLY idx_tasks_status_created 
ON tasks(status, created_at) WHERE status IN ('QUEUED', 'RUNNING');

CREATE INDEX CONCURRENTLY idx_agents_status_type 
ON agents(status, agent_type) WHERE status = 'IDLE';

CREATE INDEX CONCURRENTLY idx_checkpoints_created 
ON checkpoints(created_at DESC);

CREATE INDEX CONCURRENTLY idx_shared_state_key_updated 
ON shared_state(key, updated_at) WHERE expires_at > NOW();

-- Analyze tables
ANALYZE tasks;
ANALYZE agents;
ANALYZE checkpoints;
ANALYZE shared_state;
```

### Redis Tuning

**Redis Configuration (`redis.conf`):**
```conf
# Memory Management
maxmemory 16gb
maxmemory-policy allkeys-lru
maxmemory-samples 10

# Persistence
save 900 1
save 300 10  
save 60 10000
rdbcompression yes
rdbchecksum yes

# Networking
tcp-keepalive 60
tcp-backlog 2048
timeout 0

# Performance
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64

# Clients
maxclients 65000
```

**Redis Monitoring:**
```bash
# Monitor Redis performance
redis-cli --latency -h redis-cluster
redis-cli --stat -h redis-cluster

# Check slow queries
redis-cli slowlog get 10

# Memory usage analysis
redis-cli --bigkeys
redis-cli memory usage shared_state:task_abc123
```

### Network Optimization

**TCP Tuning:**
```bash
# /etc/sysctl.d/99-maos.conf
net.core.somaxconn = 65536
net.core.netdev_max_backlog = 5000
net.core.rmem_default = 262144
net.core.rmem_max = 134217728
net.core.wmem_default = 262144
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.ipv4.tcp_congestion_control = bbr
net.ipv4.tcp_slow_start_after_idle = 0

# Apply settings
sysctl -p /etc/sysctl.d/99-maos.conf
```

**Load Balancer Configuration:**
```nginx
# nginx.conf for MAOS load balancing
upstream maos_backend {
    least_conn;
    server 10.0.1.10:8000 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:8000 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 80;
    listen 443 ssl http2;
    
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!SHA1:!WEAK;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://maos_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
}
```

## Security Hardening

### Network Security

**Firewall Configuration:**
```bash
# ufw rules for MAOS
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow from 10.0.0.0/8 to any port 8000
ufw allow from 10.0.0.0/8 to any port 5432
ufw allow from 10.0.0.0/8 to any port 6379
ufw allow 80
ufw allow 443
ufw enable
```

**iptables Rules:**
```bash
# Basic iptables configuration
iptables -P INPUT DROP
iptables -P FORWARD DROP  
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -I INPUT 1 -i lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow internal network access to services
iptables -A INPUT -s 10.0.0.0/8 -p tcp --dport 8000 -j ACCEPT
iptables -A INPUT -s 10.0.0.0/8 -p tcp --dport 5432 -j ACCEPT
iptables -A INPUT -s 10.0.0.0/8 -p tcp --dport 6379 -j ACCEPT

# Save rules
iptables-save > /etc/iptables/rules.v4
```

### SSL/TLS Configuration

**Certificate Management with cert-manager:**
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@your-domain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

**SSL Configuration:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: maos-tls
  namespace: maos
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-certificate>
  tls.key: <base64-encoded-private-key>
```

### Authentication and Authorization

**RBAC Configuration:**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: maos-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "endpoints"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["autoscaling"]
  resources: ["horizontalpodautoscalers"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: maos-binding
subjects:
- kind: ServiceAccount
  name: maos-service-account
  namespace: maos
roleRef:
  kind: ClusterRole
  name: maos-role
  apiGroup: rbac.authorization.k8s.io
```

**API Key Management:**
```yaml
# Secret for API keys
apiVersion: v1
kind: Secret
metadata:
  name: api-keys
  namespace: maos
type: Opaque
data:
  claude-api-key: <base64-encoded-key>
  openai-api-key: <base64-encoded-key>
  
# Use external secret management (e.g., AWS Secrets Manager)
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: maos
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-west-2
      auth:
        secretRef:
          accessKeyID:
            name: aws-creds
            key: access-key-id
          secretAccessKey:
            name: aws-creds
            key: secret-access-key
```

### Data Protection

**Encryption at Rest:**
```yaml
# StorageClass with encryption
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: encrypted-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  encrypted: "true"
  kmsKeyId: arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

**Backup Encryption:**
```bash
# Encrypted backup script
#!/bin/bash
BACKUP_DIR="/var/backups/maos"
ENCRYPTION_KEY="/etc/maos/backup.key"

# Create encrypted backup
tar czf - /var/lib/maos/checkpoints | \
gpg --symmetric --cipher-algo AES256 --compress-algo 1 \
    --passphrase-file $ENCRYPTION_KEY > $BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz.gpg

# Upload to S3 with encryption
aws s3 cp $BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz.gpg \
    s3://maos-backups/ --sse aws:kms --sse-kms-key-id alias/maos-backup-key
```

### Vulnerability Management

**Security Scanning:**
```bash
# Container vulnerability scanning
trivy image maos/maos:latest

# Kubernetes security scanning  
kube-bench run --targets master,node,etcd,policies

# Network security scanning
nmap -sS -O target-host

# Dependency scanning
safety check -r requirements.txt
```

**Security Monitoring:**
```yaml
# Falco rules for MAOS
apiVersion: v1
kind: ConfigMap
metadata:
  name: falco-rules
data:
  maos_rules.yaml: |
    - rule: Unauthorized Process in MAOS Container
      desc: Detect unauthorized process execution in MAOS containers
      condition: >
        spawned_process and
        container and
        container.image.repository="maos/maos" and
        not proc.name in (python, maos, redis-cli, psql)
      output: >
        Unauthorized process in MAOS container
        (user=%user.name command=%proc.cmdline container=%container.name)
      priority: WARNING
      
    - rule: Sensitive Data Access
      desc: Detect access to sensitive files
      condition: >
        open_read and
        container and
        container.image.repository="maos/maos" and
        fd.filename in (/app/config/secrets.yml, /var/lib/maos/keys/)
      output: >
        Sensitive file access detected
        (user=%user.name file=%fd.name container=%container.name)
      priority: WARNING
```

## Monitoring and Observability

### Prometheus Metrics Configuration

**prometheus.yml:**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "maos_alerts.yml"

scrape_configs:
  - job_name: 'maos'
    static_configs:
      - targets: ['maos-service:8000']
    scrape_interval: 10s
    metrics_path: /metrics
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
      
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
      
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Grafana Dashboards

**MAOS System Overview Dashboard:**
```json
{
  "dashboard": {
    "id": null,
    "title": "MAOS System Overview",
    "panels": [
      {
        "title": "Task Throughput",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(maos_tasks_completed_total[5m])",
            "legendFormat": "Tasks/sec"
          }
        ]
      },
      {
        "title": "Agent Utilization",
        "type": "stat",
        "targets": [
          {
            "expr": "(maos_agents_active / maos_agents_total) * 100",
            "legendFormat": "Utilization %"
          }
        ]
      },
      {
        "title": "System Resources",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total{container=\"maos\"}[5m]) * 100",
            "legendFormat": "CPU %"
          },
          {
            "expr": "container_memory_usage_bytes{container=\"maos\"} / container_spec_memory_limit_bytes{container=\"maos\"} * 100",
            "legendFormat": "Memory %"
          }
        ]
      }
    ]
  }
}
```

### Alert Rules

**maos_alerts.yml:**
```yaml
groups:
- name: maos_alerts
  rules:
  - alert: HighTaskFailureRate
    expr: rate(maos_tasks_failed_total[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High task failure rate detected"
      description: "Task failure rate is {{ $value }} failures per second"

  - alert: AgentSpawnFailures
    expr: rate(maos_agent_spawn_failures_total[5m]) > 0.05
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Agent spawn failures detected"
      description: "Agent spawn failure rate is {{ $value }} failures per second"

  - alert: HighMemoryUsage
    expr: container_memory_usage_bytes{container="maos"} / container_spec_memory_limit_bytes{container="maos"} > 0.9
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage in MAOS container"
      description: "Memory usage is {{ $value | humanizePercentage }}"

  - alert: DatabaseConnectionFailures
    expr: rate(maos_database_connection_errors_total[5m]) > 0.01
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Database connection failures"
      description: "Database connection error rate is {{ $value }} errors per second"
```

### Log Aggregation

**Fluentd Configuration:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/maos/*.log
      pos_file /var/log/fluentd-maos.log.pos
      tag maos.*
      format json
    </source>
    
    <filter maos.**>
      @type parser
      key_name message
      reserve_data true
      <parse>
        @type json
      </parse>
    </filter>
    
    <match maos.**>
      @type elasticsearch
      host elasticsearch
      port 9200
      index_name maos-logs
      type_name _doc
    </match>
```

### Distributed Tracing

**Jaeger Configuration:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
spec:
  template:
    spec:
      containers:
      - name: jaeger
        image: jaegertracing/all-in-one:latest
        env:
        - name: COLLECTOR_ZIPKIN_HTTP_PORT
          value: "9411"
        ports:
        - containerPort: 16686
        - containerPort: 14268
```

**MAOS Tracing Integration:**
```python
# Add to MAOS configuration
tracing:
  enabled: true
  jaeger:
    agent_host: jaeger
    agent_port: 6831
    service_name: maos
    sampler:
      type: const
      param: 1
```

## Backup and Disaster Recovery

### Backup Strategy

**Automated Backup Script:**
```bash
#!/bin/bash
# maos-backup.sh

set -euo pipefail

BACKUP_DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/var/backups/maos"
S3_BUCKET="maos-backups-prod"
RETENTION_DAYS=30

echo "Starting MAOS backup at $(date)"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump $MAOS_DATABASE_PRIMARY_URL | gzip > $BACKUP_DIR/postgres-$BACKUP_DATE.sql.gz

# Redis backup
redis-cli --rdb $BACKUP_DIR/redis-$BACKUP_DATE.rdb

# Checkpoint backup
tar czf $BACKUP_DIR/checkpoints-$BACKUP_DATE.tar.gz /var/lib/maos/checkpoints/

# Configuration backup
tar czf $BACKUP_DIR/config-$BACKUP_DATE.tar.gz /etc/maos/

# Upload to S3
aws s3 sync $BACKUP_DIR s3://$S3_BUCKET/daily/$(date +%Y/%m/%d)/

# Cleanup old local backups
find $BACKUP_DIR -name "*.gz" -type f -mtime +7 -delete
find $BACKUP_DIR -name "*.rdb" -type f -mtime +7 -delete

# Cleanup old S3 backups
aws s3 ls s3://$S3_BUCKET/daily/ --recursive | \
  awk -v date=$(date -d "$RETENTION_DAYS days ago" +%Y-%m-%d) '$1 < date {print $4}' | \
  xargs -I {} aws s3 rm s3://$S3_BUCKET/{}

echo "Backup completed at $(date)"
```

**Backup Verification:**
```bash
#!/bin/bash
# verify-backup.sh

BACKUP_DATE=$1
BACKUP_DIR="/var/backups/maos"

# Verify database backup
echo "Verifying database backup..."
if gunzip -t $BACKUP_DIR/postgres-$BACKUP_DATE.sql.gz; then
    echo "Database backup is valid"
else
    echo "Database backup is corrupted!"
    exit 1
fi

# Verify Redis backup  
echo "Verifying Redis backup..."
if redis-check-rdb $BACKUP_DIR/redis-$BACKUP_DATE.rdb; then
    echo "Redis backup is valid"
else
    echo "Redis backup is corrupted!"
    exit 1
fi

# Verify checkpoint backup
echo "Verifying checkpoint backup..."
if tar tzf $BACKUP_DIR/checkpoints-$BACKUP_DATE.tar.gz > /dev/null; then
    echo "Checkpoint backup is valid"
else
    echo "Checkpoint backup is corrupted!"
    exit 1
fi

echo "All backups verified successfully"
```

### Disaster Recovery Procedures

**Recovery Runbook:**
```bash
#!/bin/bash
# disaster-recovery.sh

RECOVERY_DATE=${1:-latest}
BACKUP_DIR="/var/backups/maos"
S3_BUCKET="maos-backups-prod"

echo "Starting disaster recovery for date: $RECOVERY_DATE"

# Stop MAOS services
echo "Stopping MAOS services..."
kubectl scale deployment maos --replicas=0 -n maos

# Download backups from S3
echo "Downloading backups..."
aws s3 sync s3://$S3_BUCKET/daily/ $BACKUP_DIR --exclude "*" --include "*$RECOVERY_DATE*"

# Restore database
echo "Restoring database..."
dropdb maos || true
createdb maos
gunzip -c $BACKUP_DIR/postgres-$RECOVERY_DATE.sql.gz | psql maos

# Restore Redis
echo "Restoring Redis..."
redis-cli flushall
redis-cli --rdb $BACKUP_DIR/redis-$RECOVERY_DATE.rdb
redis-cli debug reload

# Restore checkpoints
echo "Restoring checkpoints..."
rm -rf /var/lib/maos/checkpoints/*
tar xzf $BACKUP_DIR/checkpoints-$RECOVERY_DATE.tar.gz -C /

# Restore configuration  
echo "Restoring configuration..."
tar xzf $BACKUP_DIR/config-$RECOVERY_DATE.tar.gz -C /

# Start MAOS services
echo "Starting MAOS services..."
kubectl scale deployment maos --replicas=3 -n maos

# Wait for services to be ready
echo "Waiting for services to be ready..."
kubectl wait --for=condition=Ready pod -l app=maos -n maos --timeout=300s

# Verify recovery
echo "Verifying recovery..."
maos health --all-components

echo "Disaster recovery completed successfully"
```

**High Availability Setup:**
```yaml
# Multi-region deployment for disaster recovery
apiVersion: v1
kind: Service
metadata:
  name: maos-global
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    external-dns.alpha.kubernetes.io/hostname: maos.example.com
spec:
  type: LoadBalancer
  selector:
    app: maos
  ports:
  - port: 80
    targetPort: 8000

# Cross-region database replication
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-ha
spec:
  instances: 3
  primaryUpdateStrategy: unsupervised
  
  postgresql:
    parameters:
      wal_level: replica
      max_replication_slots: 10
      
  bootstrap:
    initdb:
      database: maos
      owner: maos
      
  backup:
    barmanObjectStore:
      destinationPath: s3://postgres-backups
      s3Credentials:
        accessKeyId:
          name: postgres-s3-creds
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: postgres-s3-creds
          key: SECRET_ACCESS_KEY
```

This comprehensive deployment guide provides everything needed to successfully deploy and operate MAOS in production environments. Follow the checklist and adapt the configurations to your specific infrastructure requirements.