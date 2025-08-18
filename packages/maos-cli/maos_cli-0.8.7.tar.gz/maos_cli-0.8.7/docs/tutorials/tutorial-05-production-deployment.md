# Tutorial 5: Production Deployment

**Duration:** 120-180 minutes  
**Difficulty:** Expert  
**Prerequisites:** System administration experience, completion of Tutorials 1-3

## Overview

In this comprehensive tutorial, you'll learn to deploy MAOS in production environments at enterprise scale. You'll master infrastructure planning, high availability configurations, security hardening, monitoring setup, and operational best practices for running MAOS in critical production workloads.

By the end of this tutorial, you'll be able to:
- Plan and size infrastructure for production MAOS deployments
- Configure high availability and fault tolerance
- Implement enterprise security and compliance requirements
- Set up comprehensive monitoring and observability
- Optimize performance for production workloads
- Implement disaster recovery and backup procedures

## Learning Objectives

1. **Infrastructure Planning**: Design scalable production architectures
2. **High Availability**: Configure fault-tolerant deployments
3. **Security Hardening**: Implement enterprise security controls
4. **Monitoring & Observability**: Set up comprehensive monitoring stacks
5. **Performance Optimization**: Tune systems for production loads
6. **Operational Excellence**: Establish production operational procedures

## Part 1: Infrastructure Planning and Sizing

### Exercise 1: Production Architecture Design

Design a production-ready MAOS architecture:

```bash
# Create architecture planning workspace
mkdir -p ~/maos-production/{infrastructure,security,monitoring,docs}
cd ~/maos-production

# Document requirements
cat > requirements.md << 'EOF'
# MAOS Production Requirements

## Business Requirements
- Support 1000+ concurrent tasks
- 99.9% uptime SLA (8.76 hours/year downtime)
- Global deployment across 3 regions
- Peak load: 500 tasks/minute
- Average agent count: 50-100 agents
- Data retention: 2 years

## Compliance Requirements
- SOC 2 Type II compliance
- GDPR compliance for EU users
- Data encryption in transit and at rest
- Audit logging and retention
- Role-based access control (RBAC)

## Performance Requirements
- Task completion time: <5 minutes (95th percentile)
- API response time: <500ms (95th percentile)
- Agent spawn time: <30 seconds
- Database query time: <100ms
- Message delivery latency: <50ms
EOF

# Calculate infrastructure sizing
python3 << 'EOF'
# Infrastructure sizing calculator
import math

# Load requirements
peak_tasks_per_minute = 500
avg_concurrent_tasks = 1000
agents_per_task = 3  # Average
task_duration_minutes = 3  # Average

# Calculate required agents
peak_agents_needed = (peak_tasks_per_minute * task_duration_minutes * agents_per_task) / 1
steady_state_agents = (avg_concurrent_tasks * agents_per_task)

print(f"Infrastructure Sizing Analysis")
print(f"=" * 40)
print(f"Peak agents needed: {peak_agents_needed:.0f}")
print(f"Steady state agents: {steady_state_agents:.0f}")
print(f"Recommended max agents: {peak_agents_needed * 1.5:.0f}")

# Calculate compute requirements
cpu_per_agent = 0.5  # CPU cores
memory_per_agent = 1  # GB
storage_per_agent = 2  # GB

total_cpu_cores = peak_agents_needed * cpu_per_agent * 1.5
total_memory_gb = peak_agents_needed * memory_per_agent * 1.5
total_storage_gb = peak_agents_needed * storage_per_agent

print(f"\nCompute Requirements:")
print(f"CPU cores: {total_cpu_cores:.0f}")
print(f"Memory: {total_memory_gb:.0f} GB")
print(f"Storage: {total_storage_gb:.0f} GB")

# Database sizing
tasks_per_day = peak_tasks_per_minute * 60 * 24 * 0.7  # 70% peak average
task_record_size_kb = 5  # Estimated
retention_days = 730  # 2 years

db_storage_gb = (tasks_per_day * task_record_size_kb * retention_days) / (1024 * 1024)
print(f"\nDatabase Requirements:")
print(f"Tasks per day: {tasks_per_day:.0f}")
print(f"Database storage: {db_storage_gb:.0f} GB")
print(f"Recommended DB storage: {db_storage_gb * 2:.0f} GB (with overhead)")

# Redis sizing
active_tasks = avg_concurrent_tasks
shared_state_per_task_mb = 0.5
agent_state_per_agent_mb = 0.2

redis_memory_mb = (active_tasks * shared_state_per_task_mb + 
                   steady_state_agents * agent_state_per_agent_mb)
redis_memory_gb = redis_memory_mb / 1024

print(f"\nRedis Requirements:")
print(f"Active memory: {redis_memory_gb:.1f} GB")
print(f"Recommended Redis memory: {redis_memory_gb * 2:.1f} GB")
EOF
```

**Expected Output:**
```
Infrastructure Sizing Analysis
========================================
Peak agents needed: 4500
Steady state agents: 3000
Recommended max agents: 6750

Compute Requirements:
CPU cores: 3375
Memory: 6750 GB
Storage: 9000 GB

Database Requirements:
Tasks per day: 504000
Database storage: 1798 GB
Recommended DB storage: 3596 GB

Redis Requirements:
Active memory: 1.1 GB
Recommended Redis memory: 2.2 GB
```

### Exercise 2: Multi-Region Architecture

Design a multi-region deployment:

```yaml
# infrastructure/global-architecture.yml
global_architecture:
  regions:
    primary:
      name: "us-east-1"
      purpose: "Primary production region"
      components:
        - maos_cluster: 
            nodes: 8
            instance_type: "c5.4xlarge"
        - database:
            type: "postgresql"
            instance: "r5.2xlarge"
            replicas: 2
        - redis:
            cluster_nodes: 6
            instance_type: "r5.large"
        - load_balancer:
            type: "application_load_balancer"
            instances: 2

    secondary:
      name: "us-west-2" 
      purpose: "Secondary region for disaster recovery"
      components:
        - maos_cluster:
            nodes: 4
            instance_type: "c5.2xlarge"
        - database:
            type: "postgresql_read_replica"
            instance: "r5.xlarge"
        - redis:
            cluster_nodes: 3
            instance_type: "r5.large"
        - load_balancer:
            type: "application_load_balancer"
            instances: 1

    edge:
      name: "eu-west-1"
      purpose: "Edge region for European users"
      components:
        - maos_cluster:
            nodes: 2
            instance_type: "c5.xlarge"
        - cache_layer:
            type: "redis"
            nodes: 2

  networking:
    vpc_peering: enabled
    transit_gateway: enabled
    private_subnets: true
    nat_gateway: true
    vpn_connectivity: enabled

  data_replication:
    database:
      primary_to_secondary: "async_replication"
      backup_frequency: "4_hours"
      point_in_time_recovery: true
    
    redis:
      cross_region_replication: enabled
      consistency_model: "eventual_consistency"

  traffic_routing:
    dns:
      provider: "route53"
      health_checks: enabled
      failover: "automatic"
    
    load_balancing:
      algorithm: "weighted_round_robin"
      health_check_interval: "30s"
      unhealthy_threshold: 3

  disaster_recovery:
    rpo: "1_hour"  # Recovery Point Objective
    rto: "30_minutes"  # Recovery Time Objective
    automated_failover: true
    backup_regions: ["us-west-2"]
```

### Exercise 3: Kubernetes Production Configuration

Create production Kubernetes configurations:

```yaml
# infrastructure/kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: maos-production
  labels:
    name: maos-production
    environment: production
    compliance: soc2
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: maos-resource-quota
  namespace: maos-production
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    limits.cpu: "200"
    limits.memory: 400Gi
    pods: "200"
    services: "50"
    persistentvolumeclaims: "20"
```

```yaml
# infrastructure/kubernetes/maos-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: maos-orchestrator
  namespace: maos-production
  labels:
    app: maos-orchestrator
    version: v2.1.0
    tier: orchestration
spec:
  replicas: 6
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 1
  selector:
    matchLabels:
      app: maos-orchestrator
  template:
    metadata:
      labels:
        app: maos-orchestrator
        version: v2.1.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: maos-service-account
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        fsGroup: 10001
      containers:
      - name: maos-orchestrator
        image: maos/maos:v2.1.0-production
        imagePullPolicy: Always
        ports:
        - name: http-api
          containerPort: 8000
          protocol: TCP
        - name: grpc-api
          containerPort: 9000
          protocol: TCP
        - name: metrics
          containerPort: 8080
          protocol: TCP
        env:
        - name: MAOS_ENVIRONMENT
          value: "production"
        - name: MAOS_LOG_LEVEL
          value: "INFO"
        - name: MAOS_DATABASE_PRIMARY_URL
          valueFrom:
            secretKeyRef:
              name: maos-database-credentials
              key: primary-url
        - name: MAOS_DATABASE_REPLICA_URL
          valueFrom:
            secretKeyRef:
              name: maos-database-credentials
              key: replica-url
        - name: MAOS_REDIS_URL
          valueFrom:
            secretKeyRef:
              name: maos-redis-credentials
              key: cluster-url
        - name: CLAUDE_API_KEY
          valueFrom:
            secretKeyRef:
              name: maos-api-keys
              key: claude-api-key
        - name: MAOS_ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: maos-encryption-keys
              key: primary-key
        resources:
          requests:
            cpu: "2"
            memory: "4Gi"
            ephemeral-storage: "10Gi"
          limits:
            cpu: "4"
            memory: "8Gi"
            ephemeral-storage: "20Gi"
        livenessProbe:
          httpGet:
            path: /health/live
            port: http-api
          initialDelaySeconds: 120
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health/ready
            port: http-api
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        volumeMounts:
        - name: maos-config
          mountPath: /app/config
          readOnly: true
        - name: maos-logs
          mountPath: /var/log/maos
        - name: checkpoint-storage
          mountPath: /var/lib/maos/checkpoints
        - name: tmp-volume
          mountPath: /tmp
      volumes:
      - name: maos-config
        configMap:
          name: maos-configuration
      - name: maos-logs
        emptyDir:
          sizeLimit: 1Gi
      - name: checkpoint-storage
        persistentVolumeClaim:
          claimName: maos-checkpoint-pvc
      - name: tmp-volume
        emptyDir:
          sizeLimit: 500Mi
      nodeSelector:
        workload-type: compute-intensive
        kubernetes.io/arch: amd64
      tolerations:
      - key: "high-performance"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - maos-orchestrator
              topologyKey: kubernetes.io/hostname
```

## Part 2: High Availability Configuration

### Exercise 4: Database High Availability

Configure PostgreSQL for high availability:

```yaml
# infrastructure/database/postgresql-ha.yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: maos-postgresql-cluster
  namespace: maos-production
spec:
  instances: 3
  
  postgresql:
    parameters:
      # Performance tuning
      shared_buffers: "2GB"
      effective_cache_size: "6GB"
      maintenance_work_mem: "512MB"
      work_mem: "64MB"
      
      # Connection settings
      max_connections: "300"
      max_prepared_transactions: "100"
      
      # WAL settings for replication
      wal_level: "replica"
      max_wal_size: "4GB"
      min_wal_size: "1GB"
      checkpoint_completion_target: "0.9"
      
      # Logging for audit
      log_statement: "mod"
      log_min_duration_statement: "1000"
      log_line_prefix: "%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h "
      
      # Security
      ssl: "on"
      ssl_cert_file: "/var/lib/postgresql/server.crt"
      ssl_key_file: "/var/lib/postgresql/server.key"
      
  primaryUpdateStrategy: unsupervised
  
  bootstrap:
    initdb:
      database: maos
      owner: maos
      secret:
        name: maos-postgresql-credentials
      options:
        - "--encoding=UTF8"
        - "--locale=en_US.UTF-8"
        - "--data-checksums"
      
  storage:
    size: 2Ti
    storageClass: high-performance-ssd
    
  monitoring:
    enabled: true
    
  backup:
    barmanObjectStore:
      destinationPath: "s3://maos-postgresql-backups"
      s3Credentials:
        accessKeyId:
          name: postgresql-backup-credentials
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: postgresql-backup-credentials
          key: SECRET_ACCESS_KEY
      wal:
        retention: "7d"
      data:
        retention: "30d"
      
  resources:
    requests:
      memory: "8Gi"
      cpu: "4"
    limits:
      memory: "16Gi"
      cpu: "8"
      
  affinity:
    enablePodAntiAffinity: true
    podAntiAffinityType: "preferred"
    
  nodeMaintenanceWindow:
    inProgress: false
    reusePVC: true
```

### Exercise 5: Redis High Availability

Configure Redis cluster for high availability:

```yaml
# infrastructure/redis/redis-cluster.yaml
apiVersion: redis.redis.opstreelabs.in/v1beta1
kind: RedisCluster
metadata:
  name: maos-redis-cluster
  namespace: maos-production
spec:
  clusterSize: 6
  
  redisLeader:
    replicas: 3
    image: redis:7.0-alpine
    
    redisConfig:
      maxmemory: 4gb
      maxmemory-policy: allkeys-lru
      maxmemory-samples: 10
      
      # Persistence
      save: "900 1 300 10 60 10000"
      rdbcompression: "yes"
      rdbchecksum: "yes"
      
      # Networking
      tcp-keepalive: "60"
      tcp-backlog: "2048"
      timeout: "0"
      
      # Performance
      hash-max-ziplist-entries: "512"
      hash-max-ziplist-value: "64"
      list-max-ziplist-size: "-2"
      set-max-intset-entries: "512"
      
      # Security
      requirepass: "${REDIS_PASSWORD}"
      
    resources:
      requests:
        cpu: "1"
        memory: "5Gi"
      limits:
        cpu: "2"
        memory: "6Gi"
    
    storage:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 100Gi
          storageClassName: high-iops-ssd
              
  redisFollower:
    replicas: 3
    image: redis:7.0-alpine
    
    redisConfig:
      maxmemory: 4gb
      maxmemory-policy: allkeys-lru
      replica-read-only: "yes"
      replica-serve-stale-data: "yes"
      
    resources:
      requests:
        cpu: "500m"
        memory: "5Gi"
      limits:
        cpu: "1"
        memory: "6Gi"
        
    storage:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 100Gi
          storageClassName: high-iops-ssd
  
  securityContext:
    runAsUser: 999
    fsGroup: 999
    
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - redis
        topologyKey: kubernetes.io/hostname
```

### Exercise 6: Load Balancer and Ingress

Configure ingress and load balancing:

```yaml
# infrastructure/networking/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: maos-ingress
  namespace: maos-production
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    
    # Rate limiting
    nginx.ingress.kubernetes.io/rate-limit-connections: "100"
    nginx.ingress.kubernetes.io/rate-limit-rpm: "1000"
    
    # Security headers
    nginx.ingress.kubernetes.io/server-snippet: |
      add_header X-Content-Type-Options nosniff;
      add_header X-Frame-Options DENY;
      add_header X-XSS-Protection "1; mode=block";
      add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
      
    # Load balancing
    nginx.ingress.kubernetes.io/upstream-hash-by: "$binary_remote_addr"
    nginx.ingress.kubernetes.io/load-balancing: "weighted"
    
    # Timeouts
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "5"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    
    # Body size
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    
spec:
  tls:
  - hosts:
    - api.maos.production.com
    - dashboard.maos.production.com
    secretName: maos-tls-certificate
  
  rules:
  - host: api.maos.production.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: maos-api-service
            port:
              number: 8000
  
  - host: dashboard.maos.production.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: maos-dashboard-service
            port:
              number: 3001

---
apiVersion: v1
kind: Service
metadata:
  name: maos-api-service
  namespace: maos-production
  labels:
    app: maos-orchestrator
    service-type: api
spec:
  selector:
    app: maos-orchestrator
  ports:
  - name: http-api
    port: 8000
    targetPort: 8000
    protocol: TCP
  - name: grpc-api
    port: 9000
    targetPort: 9000
    protocol: TCP
  type: ClusterIP
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 300

---
apiVersion: v1
kind: Service
metadata:
  name: maos-dashboard-service
  namespace: maos-production
spec:
  selector:
    app: maos-dashboard
  ports:
  - name: http
    port: 3001
    targetPort: 3001
  type: ClusterIP
```

## Part 3: Security Hardening

### Exercise 7: Security Configuration

Implement comprehensive security controls:

```yaml
# security/rbac.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: maos-service-account
  namespace: maos-production
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/MAOSServiceRole

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: maos-role
  namespace: maos-production
rules:
- apiGroups: [""]
  resources: ["pods", "services", "endpoints", "configmaps"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods/exec", "pods/log"]
  verbs: ["create", "get"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["autoscaling"]
  resources: ["horizontalpodautoscalers"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: maos-role-binding
  namespace: maos-production
subjects:
- kind: ServiceAccount
  name: maos-service-account
  namespace: maos-production
roleRef:
  kind: Role
  name: maos-role
  apiGroup: rbac.authorization.k8s.io

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: maos-network-policy
  namespace: maos-production
spec:
  podSelector:
    matchLabels:
      app: maos-orchestrator
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
    - protocol: TCP
      port: 3001
  - from:
    - podSelector:
        matchLabels:
          app: prometheus
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgresql
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS
    - protocol: TCP
      port: 53   # DNS
    - protocol: UDP
      port: 53   # DNS
```

### Exercise 8: Secret Management

Configure secure secret management:

```yaml
# security/external-secrets.yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: maos-production
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: maos-service-account

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: maos-database-credentials
  namespace: maos-production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: maos-database-credentials
    creationPolicy: Owner
  data:
  - secretKey: primary-url
    remoteRef:
      key: maos/production/database
      property: primary_url
  - secretKey: replica-url
    remoteRef:
      key: maos/production/database
      property: replica_url

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: maos-api-keys
  namespace: maos-production
spec:
  refreshInterval: 15m
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: maos-api-keys
    creationPolicy: Owner
  data:
  - secretKey: claude-api-key
    remoteRef:
      key: maos/production/api-keys
      property: claude_api_key
  - secretKey: openai-api-key
    remoteRef:
      key: maos/production/api-keys
      property: openai_api_key

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: maos-encryption-keys
  namespace: maos-production
spec:
  refreshInterval: 24h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: maos-encryption-keys
    creationPolicy: Owner
  data:
  - secretKey: primary-key
    remoteRef:
      key: maos/production/encryption
      property: primary_key
  - secretKey: backup-key
    remoteRef:
      key: maos/production/encryption
      property: backup_key
```

### Exercise 9: Security Scanning and Compliance

Set up security scanning and compliance monitoring:

```yaml
# security/falco-rules.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: falco-rules-maos
  namespace: maos-production
data:
  maos_security_rules.yaml: |
    - rule: Unauthorized Process in MAOS Container
      desc: Detect unauthorized process execution in MAOS containers
      condition: >
        spawned_process and container and
        container.image.repository contains "maos" and
        not proc.name in (python, maos, node, redis-cli, psql, bash, sh)
      output: >
        Unauthorized process in MAOS container
        (user=%user.name command=%proc.cmdline container=%container.name image=%container.image.repository)
      priority: WARNING
      tags: [maos, process, security]
    
    - rule: Sensitive Data Access in MAOS
      desc: Detect access to sensitive files in MAOS
      condition: >
        open_read and container and
        container.image.repository contains "maos" and
        fd.filename in (/app/secrets, /var/lib/maos/keys, /etc/ssl/private)
      output: >
        Sensitive file access in MAOS container
        (user=%user.name file=%fd.name container=%container.name)
      priority: CRITICAL
      tags: [maos, files, security]
    
    - rule: Network Connection from MAOS to Unexpected Destination
      desc: Detect unexpected network connections from MAOS
      condition: >
        outbound and container and
        container.image.repository contains "maos" and
        not fd.sip.name in (postgresql, redis, api.anthropic.com, api.openai.com)
      output: >
        Unexpected network connection from MAOS
        (user=%user.name connection=%fd.name container=%container.name)
      priority: WARNING
      tags: [maos, network, security]
    
    - rule: Privilege Escalation in MAOS
      desc: Detect privilege escalation attempts
      condition: >
        spawned_process and container and
        container.image.repository contains "maos" and
        (proc.name in (su, sudo, doas) or
         (proc.aname in (su, sudo, doas)))
      output: >
        Privilege escalation attempt in MAOS container
        (user=%user.name command=%proc.cmdline container=%container.name)
      priority: CRITICAL
      tags: [maos, privilege, security]

---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: falco
  namespace: maos-production
spec:
  selector:
    matchLabels:
      app: falco
  template:
    metadata:
      labels:
        app: falco
    spec:
      serviceAccountName: falco-service-account
      containers:
      - name: falco
        image: falcosecurity/falco:latest
        args:
          - /usr/bin/falco
          - --cri=/run/containerd/containerd.sock
          - --k8s-api=https://kubernetes.default.svc.cluster.local
          - --k8s-api-cert=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
          - --k8s-api-token=/var/run/secrets/kubernetes.io/serviceaccount/token
        securityContext:
          privileged: true
        volumeMounts:
        - mountPath: /host/var/run/docker.sock
          name: docker-socket
        - mountPath: /host/run/containerd/containerd.sock
          name: containerd-socket
        - mountPath: /host/dev
          name: dev-fs
        - mountPath: /host/proc
          name: proc-fs
          readOnly: true
        - mountPath: /host/boot
          name: boot-fs
          readOnly: true
        - mountPath: /host/lib/modules
          name: lib-modules
          readOnly: true
        - mountPath: /host/usr
          name: usr-fs
          readOnly: true
        - mountPath: /etc/falco/rules.d
          name: falco-rules
      volumes:
      - name: docker-socket
        hostPath:
          path: /var/run/docker.sock
      - name: containerd-socket
        hostPath:
          path: /run/containerd/containerd.sock
      - name: dev-fs
        hostPath:
          path: /dev
      - name: proc-fs
        hostPath:
          path: /proc
      - name: boot-fs
        hostPath:
          path: /boot
      - name: lib-modules
        hostPath:
          path: /lib/modules
      - name: usr-fs
        hostPath:
          path: /usr
      - name: falco-rules
        configMap:
          name: falco-rules-maos
```

## Part 4: Monitoring and Observability

### Exercise 10: Prometheus and Grafana Setup

Deploy comprehensive monitoring stack:

```yaml
# monitoring/prometheus.yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: maos-prometheus
  namespace: maos-production
spec:
  serviceAccountName: prometheus
  serviceMonitorSelector:
    matchLabels:
      app: maos
  ruleSelector:
    matchLabels:
      app: maos
      prometheus: maos
  resources:
    requests:
      memory: 4Gi
      cpu: "2"
    limits:
      memory: 8Gi
      cpu: "4"
  retention: 30d
  storage:
    volumeClaimTemplate:
      spec:
        storageClassName: high-performance-ssd
        resources:
          requests:
            storage: 1Ti
  alerting:
    alertmanagers:
    - namespace: maos-production
      name: alertmanager-maos
      port: web

---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: maos-orchestrator-metrics
  namespace: maos-production
  labels:
    app: maos
spec:
  selector:
    matchLabels:
      app: maos-orchestrator
  endpoints:
  - port: metrics
    interval: 15s
    path: /metrics

---
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: maos-alerts
  namespace: maos-production
  labels:
    app: maos
    prometheus: maos
spec:
  groups:
  - name: maos.rules
    interval: 15s
    rules:
    - alert: MAOSHighTaskFailureRate
      expr: rate(maos_tasks_failed_total[5m]) > 0.1
      for: 2m
      labels:
        severity: critical
        component: orchestrator
      annotations:
        summary: "High task failure rate in MAOS"
        description: "Task failure rate is {{ $value }} failures per second"
    
    - alert: MAOSAgentSpawnFailures
      expr: rate(maos_agent_spawn_failures_total[5m]) > 0.05
      for: 1m
      labels:
        severity: warning
        component: agents
      annotations:
        summary: "Agent spawn failures detected"
        description: "Agent spawn failure rate is {{ $value }} failures per second"
    
    - alert: MAOSHighLatency
      expr: histogram_quantile(0.95, rate(maos_http_request_duration_seconds_bucket[5m])) > 0.5
      for: 5m
      labels:
        severity: warning
        component: api
      annotations:
        summary: "High API latency in MAOS"
        description: "95th percentile latency is {{ $value }}s"
    
    - alert: MAOSLowAgentUtilization
      expr: maos_active_agents / maos_total_agents < 0.3
      for: 10m
      labels:
        severity: warning
        component: orchestrator
      annotations:
        summary: "Low agent utilization"
        description: "Agent utilization is {{ $value | humanizePercentage }}"
    
    - alert: MAOSDatabaseConnectionErrors
      expr: rate(maos_database_connection_errors_total[5m]) > 0.01
      for: 2m
      labels:
        severity: critical
        component: database
      annotations:
        summary: "Database connection errors"
        description: "Database error rate is {{ $value }} errors per second"
    
    - alert: MAOSRedisConnectionErrors
      expr: rate(maos_redis_connection_errors_total[5m]) > 0.01
      for: 2m
      labels:
        severity: critical
        component: redis
      annotations:
        summary: "Redis connection errors"
        description: "Redis error rate is {{ $value }} errors per second"

---
apiVersion: monitoring.coreos.com/v1
kind: Alertmanager
metadata:
  name: alertmanager-maos
  namespace: maos-production
spec:
  replicas: 3
  resources:
    requests:
      memory: 256Mi
      cpu: 100m
  storage:
    volumeClaimTemplate:
      spec:
        storageClassName: standard-ssd
        resources:
          requests:
            storage: 10Gi
  alertmanagerConfiguration:
    name: alertmanager-config
```

### Exercise 11: Grafana Dashboards

Create comprehensive Grafana dashboards:

```json
# monitoring/grafana-dashboard-maos-overview.json
{
  "dashboard": {
    "id": null,
    "title": "MAOS Production Overview",
    "tags": ["maos", "production", "overview"],
    "timezone": "UTC",
    "panels": [
      {
        "id": 1,
        "title": "System Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "maos_system_info",
            "legendFormat": "Version: {{version}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "palette-classic"},
            "custom": {"displayMode": "list"},
            "mappings": [],
            "thresholds": {
              "steps": [
                {"color": "green", "value": null}
              ]
            }
          }
        },
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Active Tasks",
        "type": "stat",
        "targets": [
          {
            "expr": "maos_active_tasks",
            "legendFormat": "Active Tasks"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "thresholds"},
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 800},
                {"color": "red", "value": 1000}
              ]
            }
          }
        },
        "gridPos": {"h": 4, "w": 3, "x": 6, "y": 0}
      },
      {
        "id": 3,
        "title": "Task Completion Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(maos_tasks_completed_total[5m])",
            "legendFormat": "Tasks/sec"
          }
        ],
        "yAxes": [
          {
            "label": "Tasks per second",
            "min": 0
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4}
      },
      {
        "id": 4,
        "title": "Agent Utilization",
        "type": "graph",
        "targets": [
          {
            "expr": "maos_active_agents / maos_total_agents * 100",
            "legendFormat": "Utilization %"
          }
        ],
        "yAxes": [
          {
            "label": "Percentage",
            "min": 0,
            "max": 100
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4}
      },
      {
        "id": 5,
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(maos_http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          },
          {
            "expr": "histogram_quantile(0.95, rate(maos_http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.99, rate(maos_http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "99th percentile"
          }
        ],
        "yAxes": [
          {
            "label": "Seconds",
            "min": 0
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 12}
      },
      {
        "id": 6,
        "title": "Error Rates",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(maos_tasks_failed_total[5m])",
            "legendFormat": "Task failures/sec"
          },
          {
            "expr": "rate(maos_http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "HTTP 5xx errors/sec"
          },
          {
            "expr": "rate(maos_agent_spawn_failures_total[5m])",
            "legendFormat": "Agent spawn failures/sec"
          }
        ],
        "yAxes": [
          {
            "label": "Errors per second",
            "min": 0
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 12}
      },
      {
        "id": 7,
        "title": "Resource Utilization",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total{container=\"maos-orchestrator\"}[5m]) * 100",
            "legendFormat": "CPU %"
          },
          {
            "expr": "container_memory_usage_bytes{container=\"maos-orchestrator\"} / container_spec_memory_limit_bytes{container=\"maos-orchestrator\"} * 100",
            "legendFormat": "Memory %"
          }
        ],
        "yAxes": [
          {
            "label": "Percentage",
            "min": 0,
            "max": 100
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 20}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

### Exercise 12: Log Aggregation and Analysis

Set up centralized logging with ELK stack:

```yaml
# monitoring/elasticsearch.yaml
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: maos-elasticsearch
  namespace: maos-production
spec:
  version: 8.8.0
  nodeSets:
  - name: master
    count: 3
    config:
      node.roles: ["master"]
      cluster.initial_master_nodes: [
        "maos-elasticsearch-es-master-0",
        "maos-elasticsearch-es-master-1", 
        "maos-elasticsearch-es-master-2"
      ]
    podTemplate:
      spec:
        containers:
        - name: elasticsearch
          resources:
            requests:
              memory: 2Gi
              cpu: 1
            limits:
              memory: 4Gi
              cpu: 2
    volumeClaimTemplates:
    - metadata:
        name: elasticsearch-data
      spec:
        accessModes: [ReadWriteOnce]
        resources:
          requests:
            storage: 100Gi
        storageClassName: high-performance-ssd
  
  - name: data
    count: 6
    config:
      node.roles: ["data", "ingest"]
    podTemplate:
      spec:
        containers:
        - name: elasticsearch
          resources:
            requests:
              memory: 8Gi
              cpu: 2
            limits:
              memory: 16Gi
              cpu: 4
    volumeClaimTemplates:
    - metadata:
        name: elasticsearch-data
      spec:
        accessModes: [ReadWriteOnce]
        resources:
          requests:
            storage: 1Ti
        storageClassName: high-performance-ssd

---
apiVersion: kibana.k8s.elastic.co/v1
kind: Kibana
metadata:
  name: maos-kibana
  namespace: maos-production
spec:
  version: 8.8.0
  count: 2
  elasticsearchRef:
    name: maos-elasticsearch
  podTemplate:
    spec:
      containers:
      - name: kibana
        resources:
          requests:
            memory: 1Gi
            cpu: 500m
          limits:
            memory: 2Gi
            cpu: 1

---
apiVersion: beat.k8s.elastic.co/v1beta1
kind: Filebeat
metadata:
  name: maos-filebeat
  namespace: maos-production
spec:
  version: 8.8.0
  elasticsearchRef:
    name: maos-elasticsearch
  config:
    filebeat.inputs:
    - type: container
      paths:
      - /var/log/containers/*maos*.log
      processors:
      - add_kubernetes_metadata:
          host: ${NODE_NAME}
          matchers:
          - logs_path:
              logs_path: "/var/log/containers/"
    
    processors:
    - add_cloud_metadata: {}
    - add_host_metadata: {}
    
    output.elasticsearch:
      hosts: ["maos-elasticsearch-es-http:9200"]
      index: "maos-logs-%{+yyyy.MM.dd}"
      
  daemonSet:
    podTemplate:
      spec:
        serviceAccountName: filebeat
        terminationGracePeriodSeconds: 30
        containers:
        - name: filebeat
          securityContext:
            runAsUser: 0
          volumeMounts:
          - name: varlogcontainers
            mountPath: /var/log/containers
            readOnly: true
          - name: varlogpods
            mountPath: /var/log/pods
            readOnly: true
          env:
          - name: NODE_NAME
            valueFrom:
              fieldRef:
                fieldPath: spec.nodeName
        volumes:
        - name: varlogcontainers
          hostPath:
            path: /var/log/containers
        - name: varlogpods
          hostPath:
            path: /var/log/pods
```

## Part 5: Performance Optimization

### Exercise 13: Auto-scaling Configuration

Configure horizontal and vertical pod autoscaling:

```yaml
# performance/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: maos-orchestrator-hpa
  namespace: maos-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: maos-orchestrator
  minReplicas: 6
  maxReplicas: 50
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
  - type: Object
    object:
      metric:
        name: maos_active_tasks
      target:
        type: AverageValue
        averageValue: "20"
      describedObject:
        apiVersion: v1
        kind: Service
        name: maos-api-service
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 120
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 5
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 25
        periodSeconds: 60

---
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: maos-orchestrator-vpa
  namespace: maos-production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: maos-orchestrator
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: maos-orchestrator
      minAllowed:
        cpu: 1
        memory: 2Gi
      maxAllowed:
        cpu: 8
        memory: 16Gi
      controlledResources: ["cpu", "memory"]
      controlledValues: RequestsAndLimits
```

### Exercise 14: Cluster Auto-scaling

Configure cluster auto-scaling for dynamic node management:

```yaml
# performance/cluster-autoscaler.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
  labels:
    app: cluster-autoscaler
spec:
  selector:
    matchLabels:
      app: cluster-autoscaler
  template:
    metadata:
      labels:
        app: cluster-autoscaler
    spec:
      serviceAccountName: cluster-autoscaler
      containers:
      - image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.21.0
        name: cluster-autoscaler
        resources:
          limits:
            cpu: 100m
            memory: 300Mi
          requests:
            cpu: 100m
            memory: 300Mi
        command:
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws
        - --skip-nodes-with-local-storage=false
        - --expander=least-waste
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/maos-production
        - --balance-similar-node-groups
        - --skip-nodes-with-system-pods=false
        - --scale-down-delay-after-add=10m
        - --scale-down-unneeded-time=10m
        - --scale-down-delay-after-delete=10m
        - --scale-down-delay-after-failure=3m
        - --scale-down-utilization-threshold=0.5
        env:
        - name: AWS_REGION
          value: us-east-1
        volumeMounts:
        - name: ssl-certs
          mountPath: /etc/ssl/certs/ca-certificates.crt
          readOnly: true
      volumes:
      - name: ssl-certs
        hostPath:
          path: /etc/ssl/certs/ca-certificates.crt

---
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    k8s-addon: cluster-autoscaler.addons.k8s.io
    k8s-app: cluster-autoscaler
  name: cluster-autoscaler
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-autoscaler
  labels:
    k8s-addon: cluster-autoscaler.addons.k8s.io
    k8s-app: cluster-autoscaler
rules:
- apiGroups: [""]
  resources: ["events", "endpoints"]
  verbs: ["create", "patch"]
- apiGroups: [""]
  resources: ["pods/eviction"]
  verbs: ["create"]
- apiGroups: [""]
  resources: ["pods/status"]
  verbs: ["update"]
- apiGroups: [""]
  resources: ["endpoints"]
  resourceNames: ["cluster-autoscaler"]
  verbs: ["get", "update"]
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["watch", "list", "get", "update"]
- apiGroups: [""]
  resources: ["pods", "services", "replicationcontrollers", "persistentvolumeclaims", "persistentvolumes"]
  verbs: ["watch", "list", "get"]
- apiGroups: ["extensions"]
  resources: ["replicasets", "daemonsets"]
  verbs: ["watch", "list", "get"]
- apiGroups: ["policy"]
  resources: ["poddisruptionbudgets"]
  verbs: ["watch", "list"]
- apiGroups: ["apps"]
  resources: ["statefulsets", "replicasets", "daemonsets"]
  verbs: ["watch", "list", "get"]
- apiGroups: ["storage.k8s.io"]
  resources: ["storageclasses", "csinodes", "csidrivers", "csistoragecapacities"]
  verbs: ["watch", "list", "get"]
- apiGroups: ["batch", "extensions"]
  resources: ["jobs"]
  verbs: ["get", "list", "watch", "patch"]
- apiGroups: ["coordination.k8s.io"]
  resources: ["leases"]
  verbs: ["create"]
- apiGroups: ["coordination.k8s.io"]
  resourceNames: ["cluster-autoscaler"]
  resources: ["leases"]
  verbs: ["get", "update"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cluster-autoscaler
  labels:
    k8s-addon: cluster-autoscaler.addons.k8s.io
    k8s-app: cluster-autoscaler
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-autoscaler
subjects:
  - kind: ServiceAccount
    name: cluster-autoscaler
    namespace: kube-system
```

## Part 6: Disaster Recovery and Backup

### Exercise 15: Backup Strategy Implementation

Implement comprehensive backup and recovery procedures:

```bash
#!/bin/bash
# backup/maos-backup-script.sh

set -euo pipefail

# Configuration
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_BUCKET="s3://maos-production-backups"
RETENTION_DAYS=90
NAMESPACE="maos-production"
LOG_FILE="/var/log/maos-backup.log"

# Logging function
log() {
    echo "[$(date -Iseconds)] $*" | tee -a "$LOG_FILE"
}

log "Starting MAOS production backup at $(date)"

# Create backup directory
BACKUP_DIR="/tmp/maos-backup-$BACKUP_DATE"
mkdir -p "$BACKUP_DIR"

# 1. Backup Kubernetes resources
log "Backing up Kubernetes resources..."
kubectl get all,configmaps,secrets,pvc,ingress -n "$NAMESPACE" -o yaml > "$BACKUP_DIR/k8s-resources.yaml"

# 2. Backup PostgreSQL database
log "Backing up PostgreSQL database..."
POSTGRES_POD=$(kubectl get pod -n "$NAMESPACE" -l postgres-operator.crunchydata.com/cluster=maos-postgresql-cluster,postgres-operator.crunchydata.com/role=master -o jsonpath='{.items[0].metadata.name}')

kubectl exec -n "$NAMESPACE" "$POSTGRES_POD" -- pg_dumpall -U maos | gzip > "$BACKUP_DIR/postgresql-dump.sql.gz"

# 3. Backup Redis data
log "Backing up Redis data..."
for i in $(seq 0 5); do
    REDIS_POD=$(kubectl get pod -n "$NAMESPACE" -l app=redis-cluster,role=master --field-selector=status.phase=Running -o jsonpath="{.items[$i].metadata.name}")
    if [ -n "$REDIS_POD" ]; then
        kubectl exec -n "$NAMESPACE" "$REDIS_POD" -- redis-cli --rdb /tmp/dump-node-$i.rdb
        kubectl cp "$NAMESPACE/$REDIS_POD:/tmp/dump-node-$i.rdb" "$BACKUP_DIR/redis-dump-node-$i.rdb"
    fi
done

# 4. Backup application configuration
log "Backing up application configuration..."
kubectl get configmap -n "$NAMESPACE" maos-configuration -o yaml > "$BACKUP_DIR/app-config.yaml"

# 5. Backup persistent volume data (if using file storage)
log "Backing up persistent volumes..."
kubectl get pvc -n "$NAMESPACE" -o json | jq -r '.items[] | select(.spec.storageClassName=="file-storage") | .metadata.name' | while read pvc_name; do
    POD_NAME="backup-pod-$(date +%s)"
    kubectl run "$POD_NAME" -n "$NAMESPACE" --image=busybox --restart=Never --rm -it --overrides="
    {
        \"spec\": {
            \"containers\": [{
                \"name\": \"backup\",
                \"image\": \"busybox\",
                \"command\": [\"tar\", \"czf\", \"/backup/$pvc_name.tar.gz\", \"-C\", \"/data\", \".\"],
                \"volumeMounts\": [{
                    \"name\": \"data\",
                    \"mountPath\": \"/data\"
                }, {
                    \"name\": \"backup\",
                    \"mountPath\": \"/backup\"
                }]
            }],
            \"volumes\": [{
                \"name\": \"data\",
                \"persistentVolumeClaim\": {\"claimName\": \"$pvc_name\"}
            }, {
                \"name\": \"backup\",
                \"hostPath\": {\"path\": \"$BACKUP_DIR\"}
            }]
        }
    }" -- sleep 3600 &
    sleep 60
    kubectl delete pod "$POD_NAME" -n "$NAMESPACE" --ignore-not-found=true
done

# 6. Create backup manifest
log "Creating backup manifest..."
cat > "$BACKUP_DIR/backup-manifest.json" << EOF
{
  "backup_date": "$BACKUP_DATE",
  "namespace": "$NAMESPACE",
  "components": [
    "kubernetes-resources",
    "postgresql-database", 
    "redis-data",
    "application-config",
    "persistent-volumes"
  ],
  "backup_version": "1.0",
  "retention_days": $RETENTION_DAYS,
  "size_bytes": $(du -sb "$BACKUP_DIR" | cut -f1),
  "files": [
    $(ls -la "$BACKUP_DIR" | awk 'NR>1 {printf "\"%s\",", $9}' | sed 's/,$//')
  ]
}
EOF

# 7. Compress backup
log "Compressing backup..."
tar czf "$BACKUP_DIR.tar.gz" -C "$(dirname "$BACKUP_DIR")" "$(basename "$BACKUP_DIR")"

# 8. Upload to S3
log "Uploading backup to S3..."
aws s3 cp "$BACKUP_DIR.tar.gz" "$BACKUP_BUCKET/daily/$(date +%Y/%m/%d)/maos-backup-$BACKUP_DATE.tar.gz"

# 9. Verify upload
log "Verifying backup upload..."
if aws s3 ls "$BACKUP_BUCKET/daily/$(date +%Y/%m/%d)/maos-backup-$BACKUP_DATE.tar.gz" > /dev/null; then
    log "Backup uploaded successfully"
else
    log "ERROR: Backup upload failed"
    exit 1
fi

# 10. Cleanup old backups
log "Cleaning up old backups..."
aws s3 ls "$BACKUP_BUCKET/daily/" --recursive | awk '{print $1" "$2" "$4}' | while read date time file; do
    backup_date=$(echo "$file" | grep -o '[0-9]\{8\}_[0-9]\{6\}' | head -1)
    if [ -n "$backup_date" ]; then
        backup_epoch=$(date -d "${backup_date:0:8} ${backup_date:9:2}:${backup_date:11:2}:${backup_date:13:2}" +%s)
        cutoff_epoch=$(date -d "$RETENTION_DAYS days ago" +%s)
        if [ "$backup_epoch" -lt "$cutoff_epoch" ]; then
            log "Deleting old backup: $file"
            aws s3 rm "$BACKUP_BUCKET/$file"
        fi
    fi
done

# 11. Cleanup local files
log "Cleaning up local files..."
rm -rf "$BACKUP_DIR" "$BACKUP_DIR.tar.gz"

# 12. Send notification
log "Sending backup completion notification..."
aws sns publish --topic-arn "arn:aws:sns:us-east-1:123456789012:maos-backup-notifications" \
    --message "MAOS production backup completed successfully at $(date). Backup ID: $BACKUP_DATE"

log "MAOS backup completed successfully at $(date)"
```

### Exercise 16: Disaster Recovery Procedures

Create comprehensive disaster recovery runbook:

```bash
#!/bin/bash
# disaster-recovery/maos-disaster-recovery.sh

set -euo pipefail

# Configuration
RECOVERY_BACKUP_ID="${1:-latest}"
BACKUP_BUCKET="s3://maos-production-backups"
NAMESPACE="maos-production"
LOG_FILE="/var/log/maos-disaster-recovery.log"

log() {
    echo "[$(date -Iseconds)] $*" | tee -a "$LOG_FILE"
}

log "Starting MAOS disaster recovery process"
log "Recovery backup ID: $RECOVERY_BACKUP_ID"

# 1. Stop all MAOS services
log "Stopping MAOS services..."
kubectl scale deployment -n "$NAMESPACE" --replicas=0 --all
kubectl wait --for=delete pod -n "$NAMESPACE" -l app=maos-orchestrator --timeout=300s

# 2. Download backup
log "Downloading backup from S3..."
if [ "$RECOVERY_BACKUP_ID" = "latest" ]; then
    BACKUP_FILE=$(aws s3 ls "$BACKUP_BUCKET/daily/" --recursive | sort | tail -n 1 | awk '{print $4}')
else
    BACKUP_FILE=$(aws s3 ls "$BACKUP_BUCKET/" --recursive | grep "$RECOVERY_BACKUP_ID" | awk '{print $4}' | head -n 1)
fi

if [ -z "$BACKUP_FILE" ]; then
    log "ERROR: No backup found for ID: $RECOVERY_BACKUP_ID"
    exit 1
fi

RECOVERY_DIR="/tmp/maos-recovery-$(date +%s)"
mkdir -p "$RECOVERY_DIR"

aws s3 cp "$BACKUP_BUCKET/$BACKUP_FILE" "$RECOVERY_DIR/backup.tar.gz"
cd "$RECOVERY_DIR"
tar xzf backup.tar.gz

# 3. Verify backup integrity
log "Verifying backup integrity..."
if [ ! -f "*/backup-manifest.json" ]; then
    log "ERROR: Backup manifest not found"
    exit 1
fi

BACKUP_MANIFEST=$(find . -name "backup-manifest.json")
BACKUP_DIR=$(dirname "$BACKUP_MANIFEST")

# 4. Restore database
log "Restoring PostgreSQL database..."
POSTGRES_RESTORE_POD="postgres-restore-$(date +%s)"

# Create temporary pod for database restore
kubectl run "$POSTGRES_RESTORE_POD" -n "$NAMESPACE" \
    --image=postgres:15 \
    --restart=Never \
    --rm -i --tty \
    --overrides='{
        "spec": {
            "containers": [{
                "name": "postgres",
                "image": "postgres:15",
                "env": [
                    {"name": "PGPASSWORD", "value": "'$POSTGRES_PASSWORD'"}
                ],
                "command": ["sleep", "3600"]
            }]
        }
    }' &

sleep 30

# Copy database dump to pod
kubectl cp "$BACKUP_DIR/postgresql-dump.sql.gz" "$NAMESPACE/$POSTGRES_RESTORE_POD:/tmp/db-dump.sql.gz"

# Restore database
kubectl exec -n "$NAMESPACE" "$POSTGRES_RESTORE_POD" -- bash -c "
    gunzip /tmp/db-dump.sql.gz
    psql -h maos-postgresql-cluster -U maos -f /tmp/db-dump.sql
"

kubectl delete pod "$POSTGRES_RESTORE_POD" -n "$NAMESPACE"

# 5. Restore Redis data
log "Restoring Redis data..."
for i in $(seq 0 5); do
    if [ -f "$BACKUP_DIR/redis-dump-node-$i.rdb" ]; then
        REDIS_POD=$(kubectl get pod -n "$NAMESPACE" -l app=redis-cluster,role=master --field-selector=status.phase=Running -o jsonpath="{.items[$i].metadata.name}")
        if [ -n "$REDIS_POD" ]; then
            kubectl cp "$BACKUP_DIR/redis-dump-node-$i.rdb" "$NAMESPACE/$REDIS_POD:/data/dump.rdb"
            kubectl exec -n "$NAMESPACE" "$REDIS_POD" -- redis-cli DEBUG RELOAD
        fi
    fi
done

# 6. Restore Kubernetes resources
log "Restoring Kubernetes resources..."
if [ -f "$BACKUP_DIR/k8s-resources.yaml" ]; then
    kubectl apply -n "$NAMESPACE" -f "$BACKUP_DIR/k8s-resources.yaml"
fi

# 7. Restore application configuration
log "Restoring application configuration..."
if [ -f "$BACKUP_DIR/app-config.yaml" ]; then
    kubectl apply -f "$BACKUP_DIR/app-config.yaml"
fi

# 8. Restore persistent volume data
log "Restoring persistent volume data..."
for pvc_backup in "$BACKUP_DIR"/*.tar.gz; do
    if [[ "$pvc_backup" =~ pvc-.*\.tar\.gz ]]; then
        pvc_name=$(basename "$pvc_backup" .tar.gz)
        
        RESTORE_POD="restore-pod-$(date +%s)"
        kubectl run "$RESTORE_POD" -n "$NAMESPACE" --image=busybox --restart=Never --rm -it --overrides="
        {
            \"spec\": {
                \"containers\": [{
                    \"name\": \"restore\",
                    \"image\": \"busybox\",
                    \"command\": [\"sh\", \"-c\", \"cd /data && tar xzf /backup/$(basename "$pvc_backup")\"],
                    \"volumeMounts\": [{
                        \"name\": \"data\",
                        \"mountPath\": \"/data\"
                    }, {
                        \"name\": \"backup\",
                        \"mountPath\": \"/backup\"
                    }]
                }],
                \"volumes\": [{
                    \"name\": \"data\",
                    \"persistentVolumeClaim\": {\"claimName\": \"$pvc_name\"}
                }, {
                    \"name\": \"backup\",
                    \"hostPath\": {\"path\": \"$(dirname "$pvc_backup")\"}
                }]
            }
        }" -- sleep 3600 &
        
        sleep 60
        kubectl delete pod "$RESTORE_POD" -n "$NAMESPACE" --ignore-not-found=true
    fi
done

# 9. Start MAOS services
log "Starting MAOS services..."
kubectl scale deployment -n "$NAMESPACE" maos-orchestrator --replicas=6

# Wait for services to be ready
kubectl wait --for=condition=Available deployment -n "$NAMESPACE" maos-orchestrator --timeout=600s

# 10. Verify system health
log "Verifying system health..."
sleep 60

HEALTH_CHECK=$(kubectl exec -n "$NAMESPACE" deployment/maos-orchestrator -- curl -s http://localhost:8000/health || echo "FAILED")

if [[ "$HEALTH_CHECK" =~ "healthy" ]]; then
    log "System health check passed"
else
    log "ERROR: System health check failed"
    exit 1
fi

# 11. Run smoke tests
log "Running smoke tests..."
SMOKE_TEST_POD="smoke-test-$(date +%s)"

kubectl run "$SMOKE_TEST_POD" -n "$NAMESPACE" \
    --image=curlimages/curl \
    --restart=Never \
    --rm -it \
    --command -- /bin/sh -c "
    # Test API endpoint
    curl -f http://maos-api-service:8000/health
    
    # Test task submission
    curl -f -X POST http://maos-api-service:8000/api/tasks \
        -H 'Content-Type: application/json' \
        -d '{\"description\": \"Test task for disaster recovery verification\", \"type\": \"general\"}'
"

if [ $? -eq 0 ]; then
    log "Smoke tests passed"
else
    log "WARNING: Some smoke tests failed"
fi

# 12. Cleanup
log "Cleaning up recovery files..."
rm -rf "$RECOVERY_DIR"

# 13. Send notification
log "Sending disaster recovery completion notification..."
aws sns publish --topic-arn "arn:aws:sns:us-east-1:123456789012:maos-disaster-recovery-notifications" \
    --message "MAOS disaster recovery completed successfully at $(date). Backup ID: $RECOVERY_BACKUP_ID"

log "MAOS disaster recovery completed successfully at $(date)"

# 14. Update DNS and traffic routing if needed
log "Updating DNS and traffic routing..."
# This would contain specific logic for your DNS provider
# Example for Route 53:
# aws route53 change-resource-record-sets --hosted-zone-id Z123456789 --change-batch file://dns-change.json

log "Disaster recovery process completed"
```

### Exercise 17: Production Deployment Validation

Create comprehensive production validation tests:

```python
# validation/production-validation.py
import asyncio
import aiohttp
import time
import json
import logging
from typing import Dict, List, Any
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionValidator:
    """Comprehensive production deployment validation"""
    
    def __init__(self, base_url: str, auth_token: str = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session = None
        self.validation_results = {
            'overall_status': 'PENDING',
            'test_results': {},
            'performance_metrics': {},
            'errors': []
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),
            headers={'Authorization': f'Bearer {self.auth_token}'} if self.auth_token else {}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_full_validation(self) -> Dict[str, Any]:
        """Run complete production validation suite"""
        logger.info("Starting production validation suite...")
        
        validation_tests = [
            ('health_check', self.test_health_endpoints),
            ('api_functionality', self.test_api_functionality),
            ('task_execution', self.test_task_execution),
            ('agent_management', self.test_agent_management),
            ('database_connectivity', self.test_database_connectivity),
            ('redis_connectivity', self.test_redis_connectivity),
            ('performance_load', self.test_performance_load),
            ('security_headers', self.test_security_headers),
            ('monitoring_endpoints', self.test_monitoring_endpoints),
            ('disaster_recovery', self.test_disaster_recovery_readiness)
        ]
        
        for test_name, test_func in validation_tests:
            logger.info(f"Running {test_name} test...")
            try:
                result = await test_func()
                self.validation_results['test_results'][test_name] = result
                logger.info(f"{test_name}: {'PASSED' if result['passed'] else 'FAILED'}")
            except Exception as e:
                logger.error(f"{test_name} test failed with exception: {e}")
                self.validation_results['test_results'][test_name] = {
                    'passed': False,
                    'error': str(e),
                    'duration': 0
                }
                self.validation_results['errors'].append(f"{test_name}: {e}")
        
        # Calculate overall status
        all_passed = all(result['passed'] for result in self.validation_results['test_results'].values())
        self.validation_results['overall_status'] = 'PASSED' if all_passed else 'FAILED'
        
        return self.validation_results
    
    async def test_health_endpoints(self) -> Dict[str, Any]:
        """Test health and readiness endpoints"""
        start_time = time.time()
        
        health_endpoints = [
            '/health',
            '/health/live', 
            '/health/ready',
            '/health/components'
        ]
        
        results = {}
        all_healthy = True
        
        for endpoint in health_endpoints:
            try:
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    if response.status == 200:
                        data = await response.json()
                        results[endpoint] = {'status': 'healthy', 'response': data}
                    else:
                        results[endpoint] = {'status': 'unhealthy', 'status_code': response.status}
                        all_healthy = False
            except Exception as e:
                results[endpoint] = {'status': 'error', 'error': str(e)}
                all_healthy = False
        
        return {
            'passed': all_healthy,
            'duration': time.time() - start_time,
            'details': results
        }
    
    async def test_api_functionality(self) -> Dict[str, Any]:
        """Test core API functionality"""
        start_time = time.time()
        
        api_tests = [
            ('GET', '/api/status', None, 200),
            ('GET', '/api/agents/types', None, 200),
            ('GET', '/api/tasks', None, 200),
            ('POST', '/api/tasks', {
                'description': 'Validation test task',
                'type': 'general',
                'priority': 'LOW'
            }, 201)
        ]
        
        results = {}
        all_passed = True
        
        for method, endpoint, payload, expected_status in api_tests:
            try:
                async with self.session.request(
                    method, 
                    f"{self.base_url}{endpoint}",
                    json=payload if payload else None
                ) as response:
                    
                    if response.status == expected_status:
                        data = await response.json()
                        results[f"{method} {endpoint}"] = {
                            'status': 'passed',
                            'response_time': response.headers.get('X-Response-Time'),
                            'response': data
                        }
                    else:
                        results[f"{method} {endpoint}"] = {
                            'status': 'failed',
                            'expected_status': expected_status,
                            'actual_status': response.status
                        }
                        all_passed = False
                        
            except Exception as e:
                results[f"{method} {endpoint}"] = {'status': 'error', 'error': str(e)}
                all_passed = False
        
        return {
            'passed': all_passed,
            'duration': time.time() - start_time,
            'details': results
        }
    
    async def test_task_execution(self) -> Dict[str, Any]:
        """Test end-to-end task execution"""
        start_time = time.time()
        
        try:
            # Submit test task
            task_payload = {
                'description': 'Production validation test: What is 2+2?',
                'type': 'general',
                'priority': 'HIGH'
            }
            
            async with self.session.post(
                f"{self.base_url}/api/tasks",
                json=task_payload
            ) as response:
                
                if response.status != 201:
                    return {
                        'passed': False,
                        'duration': time.time() - start_time,
                        'error': f'Task submission failed: {response.status}'
                    }
                
                task_data = await response.json()
                task_id = task_data['task_id']
            
            # Monitor task completion
            max_wait_time = 180  # 3 minutes
            wait_start = time.time()
            
            while time.time() - wait_start < max_wait_time:
                async with self.session.get(f"{self.base_url}/api/tasks/{task_id}") as response:
                    if response.status == 200:
                        task_status = await response.json()
                        
                        if task_status['status'] == 'COMPLETED':
                            return {
                                'passed': True,
                                'duration': time.time() - start_time,
                                'task_id': task_id,
                                'completion_time': task_status.get('completed_at'),
                                'agent_count': task_status.get('agents_used', 0)
                            }
                        elif task_status['status'] == 'FAILED':
                            return {
                                'passed': False,
                                'duration': time.time() - start_time,
                                'error': f"Task failed: {task_status.get('error')}"
                            }
                
                await asyncio.sleep(5)
            
            return {
                'passed': False,
                'duration': time.time() - start_time,
                'error': 'Task did not complete within timeout period'
            }
            
        except Exception as e:
            return {
                'passed': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    async def test_performance_load(self) -> Dict[str, Any]:
        """Test system performance under load"""
        start_time = time.time()
        
        # Submit multiple concurrent tasks
        concurrent_tasks = 10
        task_payload = {
            'description': 'Load test task',
            'type': 'general',
            'priority': 'NORMAL'
        }
        
        try:
            # Submit tasks concurrently
            submit_tasks = []
            for i in range(concurrent_tasks):
                submit_tasks.append(
                    self.session.post(f"{self.base_url}/api/tasks", json=task_payload)
                )
            
            submit_start = time.time()
            responses = await asyncio.gather(*submit_tasks, return_exceptions=True)
            submit_duration = time.time() - submit_start
            
            successful_submissions = 0
            task_ids = []
            
            for response in responses:
                if isinstance(response, Exception):
                    continue
                if response.status == 201:
                    successful_submissions += 1
                    task_data = await response.json()
                    task_ids.append(task_data['task_id'])
            
            # Wait for tasks to complete
            completion_times = []
            for task_id in task_ids:
                task_start = time.time()
                
                while time.time() - task_start < 120:  # 2 minute timeout per task
                    async with self.session.get(f"{self.base_url}/api/tasks/{task_id}") as response:
                        if response.status == 200:
                            task_status = await response.json()
                            if task_status['status'] in ['COMPLETED', 'FAILED']:
                                completion_times.append(time.time() - task_start)
                                break
                    await asyncio.sleep(2)
            
            # Calculate performance metrics
            avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
            max_completion_time = max(completion_times) if completion_times else 0
            
            return {
                'passed': successful_submissions >= concurrent_tasks * 0.8,  # 80% success rate
                'duration': time.time() - start_time,
                'details': {
                    'concurrent_tasks': concurrent_tasks,
                    'successful_submissions': successful_submissions,
                    'submit_duration': submit_duration,
                    'avg_completion_time': avg_completion_time,
                    'max_completion_time': max_completion_time,
                    'completed_tasks': len(completion_times)
                }
            }
            
        except Exception as e:
            return {
                'passed': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    async def test_monitoring_endpoints(self) -> Dict[str, Any]:
        """Test monitoring and metrics endpoints"""
        start_time = time.time()
        
        monitoring_endpoints = [
            '/metrics',
            '/api/metrics/system',
            '/api/metrics/tasks',
            '/api/metrics/agents'
        ]
        
        results = {}
        all_accessible = True
        
        for endpoint in monitoring_endpoints:
            try:
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    if response.status == 200:
                        if endpoint == '/metrics':
                            # Prometheus format
                            content = await response.text()
                            results[endpoint] = {
                                'status': 'accessible',
                                'format': 'prometheus',
                                'metrics_count': content.count('\n')
                            }
                        else:
                            # JSON format
                            data = await response.json()
                            results[endpoint] = {
                                'status': 'accessible',
                                'format': 'json',
                                'data_keys': list(data.keys())
                            }
                    else:
                        results[endpoint] = {
                            'status': 'inaccessible',
                            'status_code': response.status
                        }
                        all_accessible = False
                        
            except Exception as e:
                results[endpoint] = {'status': 'error', 'error': str(e)}
                all_accessible = False
        
        return {
            'passed': all_accessible,
            'duration': time.time() - start_time,
            'details': results
        }
    
    async def test_security_headers(self) -> Dict[str, Any]:
        """Test security headers and configurations"""
        start_time = time.time()
        
        required_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age'
        }
        
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                headers = response.headers
                
                security_results = {}
                all_present = True
                
                for header, expected_value in required_headers.items():
                    header_value = headers.get(header, '')
                    if expected_value in header_value:
                        security_results[header] = {'status': 'present', 'value': header_value}
                    else:
                        security_results[header] = {'status': 'missing', 'expected': expected_value}
                        all_present = False
                
                return {
                    'passed': all_present,
                    'duration': time.time() - start_time,
                    'details': security_results
                }
                
        except Exception as e:
            return {
                'passed': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    async def test_disaster_recovery_readiness(self) -> Dict[str, Any]:
        """Test disaster recovery readiness"""
        start_time = time.time()
        
        # This would test various aspects of disaster recovery readiness
        # For demo purposes, we'll check backup endpoints and configurations
        
        dr_checks = {}
        all_ready = True
        
        # Check backup status endpoint
        try:
            async with self.session.get(f"{self.base_url}/api/backup/status") as response:
                if response.status == 200:
                    backup_status = await response.json()
                    dr_checks['backup_status'] = {
                        'status': 'available',
                        'last_backup': backup_status.get('last_backup'),
                        'backup_health': backup_status.get('health', 'unknown')
                    }
                else:
                    dr_checks['backup_status'] = {'status': 'unavailable'}
                    all_ready = False
        except Exception as e:
            dr_checks['backup_status'] = {'status': 'error', 'error': str(e)}
            all_ready = False
        
        return {
            'passed': all_ready,
            'duration': time.time() - start_time,
            'details': dr_checks
        }
    
    # Additional test methods would be implemented here...
    async def test_agent_management(self) -> Dict[str, Any]:
        """Test agent management functionality"""
        start_time = time.time()
        
        try:
            # Test agent listing
            async with self.session.get(f"{self.base_url}/api/agents") as response:
                if response.status != 200:
                    return {
                        'passed': False,
                        'duration': time.time() - start_time,
                        'error': f'Failed to list agents: {response.status}'
                    }
                
                agents_data = await response.json()
                
                return {
                    'passed': True,
                    'duration': time.time() - start_time,
                    'details': {
                        'total_agents': len(agents_data.get('agents', [])),
                        'active_agents': len([a for a in agents_data.get('agents', []) if a.get('status') == 'ACTIVE'])
                    }
                }
                
        except Exception as e:
            return {
                'passed': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    async def test_database_connectivity(self) -> Dict[str, Any]:
        """Test database connectivity"""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.base_url}/health/database") as response:
                if response.status == 200:
                    db_health = await response.json()
                    return {
                        'passed': db_health.get('status') == 'healthy',
                        'duration': time.time() - start_time,
                        'details': db_health
                    }
                else:
                    return {
                        'passed': False,
                        'duration': time.time() - start_time,
                        'error': f'Database health check failed: {response.status}'
                    }
                    
        except Exception as e:
            return {
                'passed': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    async def test_redis_connectivity(self) -> Dict[str, Any]:
        """Test Redis connectivity"""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.base_url}/health/redis") as response:
                if response.status == 200:
                    redis_health = await response.json()
                    return {
                        'passed': redis_health.get('status') == 'healthy',
                        'duration': time.time() - start_time,
                        'details': redis_health
                    }
                else:
                    return {
                        'passed': False,
                        'duration': time.time() - start_time,
                        'error': f'Redis health check failed: {response.status}'
                    }
                    
        except Exception as e:
            return {
                'passed': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }

async def main():
    """Main validation function"""
    if len(sys.argv) < 2:
        print("Usage: python production-validation.py <base_url> [auth_token]")
        sys.exit(1)
    
    base_url = sys.argv[1]
    auth_token = sys.argv[2] if len(sys.argv) > 2 else None
    
    async with ProductionValidator(base_url, auth_token) as validator:
        results = await validator.run_full_validation()
        
        # Print results
        print("\n" + "="*60)
        print("MAOS PRODUCTION VALIDATION RESULTS")
        print("="*60)
        print(f"Overall Status: {results['overall_status']}")
        print(f"Tests Run: {len(results['test_results'])}")
        print(f"Tests Passed: {sum(1 for r in results['test_results'].values() if r['passed'])}")
        print(f"Tests Failed: {sum(1 for r in results['test_results'].values() if not r['passed'])}")
        
        if results['errors']:
            print(f"\nErrors Encountered: {len(results['errors'])}")
            for error in results['errors']:
                print(f"  - {error}")
        
        print("\nDetailed Test Results:")
        print("-" * 60)
        for test_name, result in results['test_results'].items():
            status = "PASSED" if result['passed'] else "FAILED"
            duration = f"{result['duration']:.2f}s"
            print(f"{test_name:.<30} {status:>8} ({duration})")
            
            if not result['passed'] and 'error' in result:
                print(f"    Error: {result['error']}")
        
        # Save detailed results
        with open('production-validation-results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: production-validation-results.json")
        
        # Exit with appropriate code
        sys.exit(0 if results['overall_status'] == 'PASSED' else 1)

if __name__ == "__main__":
    asyncio.run(main())
```

## Tutorial Summary

### What You've Mastered

✅ **Infrastructure Planning**: Enterprise-scale architecture design  
✅ **High Availability**: Multi-region, fault-tolerant deployments  
✅ **Security Hardening**: Comprehensive security controls and compliance  
✅ **Monitoring Stack**: Full observability with Prometheus, Grafana, and ELK  
✅ **Performance Optimization**: Auto-scaling and performance tuning  
✅ **Disaster Recovery**: Backup strategies and recovery procedures  
✅ **Production Validation**: Comprehensive testing and validation frameworks  
✅ **Operational Excellence**: Production-ready operational procedures  

### Key Achievements

1. **Designed Enterprise Architecture** supporting 1000+ concurrent tasks
2. **Implemented Multi-Region Deployment** with 99.9% uptime SLA
3. **Configured Comprehensive Security** with SOC 2 compliance readiness  
4. **Set up Full Observability Stack** with metrics, logging, and alerting
5. **Optimized for Production Performance** with auto-scaling and tuning
6. **Established Disaster Recovery** with automated backup and recovery
7. **Created Production Validation Suite** for deployment verification

### Production Capabilities

Your deployment now supports:
- **Scale**: 1000+ concurrent tasks, 50-100 agents
- **Performance**: <500ms API response time (95th percentile)
- **Availability**: 99.9% uptime with automated failover
- **Security**: SOC 2 compliance ready with comprehensive controls
- **Observability**: Full metrics, logging, and alerting coverage
- **Recovery**: RTO: 30 minutes, RPO: 1 hour

### Operational Excellence

You've established:
- **Automated Deployment Pipelines**
- **Comprehensive Monitoring and Alerting**
- **Disaster Recovery Procedures** 
- **Security Scanning and Compliance**
- **Performance Optimization Processes**
- **Production Validation Frameworks**

## Next Steps

### Immediate Actions

1. **Deploy to staging environment** using the configurations
2. **Run production validation suite** to verify deployment
3. **Set up monitoring dashboards** and configure alerts
4. **Test disaster recovery procedures** in non-production
5. **Conduct security audit** and compliance review

### Ongoing Operations

1. **Monitor system performance** and optimize as needed
2. **Regular backup testing** and disaster recovery drills
3. **Security updates** and vulnerability management
4. **Capacity planning** and scaling decisions
5. **Performance tuning** based on production workloads

### Advanced Topics

- **Multi-Cloud Deployment**: Extend to multiple cloud providers
- **Advanced Security**: Zero-trust architecture implementation
- **Global Load Balancing**: Intelligent traffic routing
- **Compliance Automation**: Automated compliance reporting
- **Cost Optimization**: Advanced cost management strategies

### Community Leadership

- **Share production patterns** with the MAOS community
- **Contribute infrastructure templates** to the repository
- **Mentor others** in production deployment best practices
- **Lead enterprise adoption** initiatives

## Troubleshooting Production Issues

### Common Production Problems

**High API latency:**
```bash
# Check resource utilization
kubectl top pods -n maos-production

# Analyze slow queries
kubectl exec -n maos-production deployment/maos-orchestrator -- curl http://localhost:8080/metrics | grep http_request_duration

# Check database performance
kubectl exec -n maos-production postgresql-cluster-0 -- psql -U maos -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

**Agent scaling issues:**
```bash
# Check HPA status
kubectl get hpa -n maos-production

# Review cluster autoscaler
kubectl logs -n kube-system deployment/cluster-autoscaler

# Check node resources
kubectl describe nodes | grep -A 5 "Allocated resources"
```

**Database connectivity:**
```bash
# Test database connection
kubectl exec -n maos-production deployment/maos-orchestrator -- pg_isready -h postgresql-cluster

# Check connection pool status
kubectl logs -n maos-production deployment/maos-orchestrator | grep -i "database\|connection"
```

### Production Support Contacts

- **Production Support**: production-support@maos.dev
- **Security Issues**: security@maos.dev  
- **Performance Optimization**: performance@maos.dev
- **Emergency Escalation**: emergency@maos.dev (Enterprise customers)

---

🎉 **Outstanding Achievement!** You've completed the most comprehensive MAOS tutorial and are now equipped to deploy and operate MAOS at enterprise scale in production environments.

**Tutorial Stats:**
- **Exercises Completed**: 17 production-grade exercises
- **Technologies Mastered**: Kubernetes, PostgreSQL, Redis, Prometheus, Grafana, ELK
- **Capabilities Deployed**: Enterprise architecture, HA, security, monitoring, DR
- **Skills Acquired**: Production deployment, operational excellence, enterprise architecture

**You are now a MAOS Production Expert!** Ready to lead enterprise deployments and mentor others in production best practices.

**Complete Tutorial Series Stats:**
- **Total Duration**: 8-12 hours across 5 tutorials  
- **Exercises Completed**: 85+ hands-on exercises
- **Skills Mastered**: Basic usage → Multi-agent workflows → Consensus → Custom agents → Production deployment
- **Certification Ready**: MAOS Practitioner and Expert certifications