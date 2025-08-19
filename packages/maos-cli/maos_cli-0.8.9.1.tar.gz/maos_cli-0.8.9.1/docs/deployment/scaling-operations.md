# MAOS Scaling and Operations Guide

## Overview

This guide covers scaling strategies, operational procedures, and performance optimization for MAOS deployments. Learn how to handle growing workloads, optimize resource utilization, and maintain system performance at scale.

## Scaling Strategies

### Horizontal Scaling

#### Application Layer Scaling

**Manual Scaling:**
```bash
# Docker Compose
docker-compose up --scale maos-orchestrator=5

# Kubernetes
kubectl scale deployment maos-orchestrator --replicas=10 -n maos-prod

# Helm
helm upgrade maos-prod maos/maos --set replicaCount=8 -n maos-prod
```

**Auto-scaling Configuration:**
```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: maos-orchestrator-hpa
  namespace: maos-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: maos-orchestrator
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
  - type: Pods
    pods:
      metric:
        name: active_agents_per_pod
      target:
        type: AverageValue
        averageValue: "15"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 120
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

#### Database Scaling

**PostgreSQL Read Replicas:**
```yaml
# PostgreSQL HA setup
postgresql:
  architecture: replication
  primary:
    persistence:
      size: 500Gi
      storageClass: fast-ssd
    resources:
      requests:
        cpu: 4
        memory: 16Gi
      limits:
        cpu: 8
        memory: 32Gi
  
  readReplicas:
    replicaCount: 3
    persistence:
      size: 500Gi
      storageClass: fast-ssd
    resources:
      requests:
        cpu: 2
        memory: 8Gi
      limits:
        cpu: 4
        memory: 16Gi
```

**Database Connection Pooling:**
```yaml
# PgBouncer configuration
pgbouncer:
  enabled: true
  poolMode: transaction
  maxClientConn: 1000
  defaultPoolSize: 25
  reservePoolSize: 5
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 1
      memory: 2Gi
```

#### Redis Scaling

**Redis Cluster Setup:**
```bash
# Redis cluster nodes
redis-cluster:
  cluster:
    enabled: true
    nodes: 6
    replicas: 1
  
  master:
    count: 3
    resources:
      requests:
        cpu: 1
        memory: 4Gi
      limits:
        cpu: 2
        memory: 8Gi
    
    persistence:
      enabled: true
      size: 100Gi
      storageClass: fast-ssd
  
  replica:
    count: 3
    resources:
      requests:
        cpu: 500m
        memory: 2Gi
      limits:
        cpu: 1
        memory: 4Gi
```

### Vertical Scaling

#### Resource Optimization

**Memory Optimization:**
```yaml
# Application resource limits
resources:
  requests:
    cpu: 2
    memory: 4Gi
  limits:
    cpu: 8
    memory: 16Gi

# JVM settings for memory-intensive workloads
env:
- name: MAOS_JVM_OPTS
  value: "-Xms2g -Xmx14g -XX:+UseG1GC -XX:MaxGCPauseMillis=200"

# Agent memory limits
agents:
  defaults:
    max_memory: "2GB"
    memory_cleanup_threshold: 0.8
```

**CPU Optimization:**
```yaml
# CPU-intensive configuration
system:
  max_agents: 50
  worker_threads: 16
  async_workers: 32

# CPU affinity (for bare metal)
deploy:
  resources:
    limits:
      cpu: "8"
  nodeSelector:
    kubernetes.io/arch: amd64
    node-type: cpu-optimized
```

### Agent Pool Scaling

#### Dynamic Agent Allocation

**Agent Pool Configuration:**
```python
# config/agent-pools.yml
agent_pools:
  default:
    min_size: 5
    max_size: 50
    scale_up_threshold: 0.8  # CPU utilization
    scale_down_threshold: 0.3
    scale_up_increment: 5
    scale_down_increment: 2
    cooldown_period: 300  # seconds
  
  high_priority:
    min_size: 10
    max_size: 100
    scale_up_threshold: 0.7
    scale_down_threshold: 0.2
    priority_multiplier: 2.0
    
  batch_processing:
    min_size: 0
    max_size: 200
    scale_up_threshold: 0.9
    scale_down_threshold: 0.1
    batch_optimization: true
```

**Auto-scaling Policies:**
```python
# Agent auto-scaling implementation
class AgentPoolScaler:
    def __init__(self, pool_config):
        self.config = pool_config
        self.last_scale_time = {}
    
    async def should_scale_up(self, pool_name: str) -> bool:
        metrics = await self.get_pool_metrics(pool_name)
        
        # Check utilization threshold
        if metrics.cpu_utilization > self.config[pool_name]['scale_up_threshold']:
            return True
        
        # Check queue depth
        if metrics.queue_depth > metrics.active_agents * 2:
            return True
        
        # Check task wait time
        if metrics.avg_task_wait_time > 30:  # seconds
            return True
        
        return False
    
    async def scale_up(self, pool_name: str):
        if not await self._can_scale(pool_name):
            return
        
        increment = self.config[pool_name]['scale_up_increment']
        current_size = await self.get_pool_size(pool_name)
        max_size = self.config[pool_name]['max_size']
        
        new_size = min(current_size + increment, max_size)
        
        await self.set_pool_size(pool_name, new_size)
        self.last_scale_time[pool_name] = time.time()
        
        logger.info(f"Scaled up pool {pool_name} from {current_size} to {new_size}")
```

## Performance Optimization

### System-Level Optimization

#### Operating System Tuning

```bash
# /etc/sysctl.conf optimizations
# Network settings
net.core.somaxconn = 65536
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65536
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 3

# Memory settings
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
vm.overcommit_memory = 1

# File descriptor limits
fs.file-max = 2097152

# Apply settings
sysctl -p
```

```bash
# /etc/security/limits.conf
* soft nofile 65536
* hard nofile 65536
* soft nproc 32768
* hard nproc 32768
```

#### Container Optimization

**Docker Configuration:**
```yaml
# docker-compose.yml optimizations
services:
  maos-orchestrator:
    image: maos/orchestrator:latest
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 16G
        reservations:
          cpus: '4'
          memory: 8G
    
    # Security and performance options
    security_opt:
      - no-new-privileges:true
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
      nproc:
        soft: 32768
        hard: 32768
    
    # Optimized logging
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"
```

**Kubernetes Optimization:**
```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: maos
    resources:
      requests:
        cpu: 2
        memory: 4Gi
      limits:
        cpu: 8
        memory: 16Gi
    
    # Performance-related environment
    env:
    - name: GOMAXPROCS
      valueFrom:
        resourceFieldRef:
          resource: limits.cpu
    
    # Security context for performance
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      runAsUser: 1000
      capabilities:
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE
```

### Database Performance Tuning

#### PostgreSQL Optimization

```sql
-- postgresql.conf optimizations for MAOS
-- Memory settings
shared_buffers = '4GB'                    -- 25% of total RAM
effective_cache_size = '12GB'             -- 75% of total RAM
work_mem = '256MB'                        -- For complex queries
maintenance_work_mem = '1GB'              -- For maintenance operations

-- Connection settings
max_connections = 200                     -- Based on connection pool size
max_prepared_transactions = 100          -- For two-phase commits

-- WAL settings
wal_buffers = '64MB'                     -- WAL buffer size
checkpoint_completion_target = 0.9        -- Spread out checkpoints
max_wal_size = '4GB'                     -- Maximum WAL size
min_wal_size = '1GB'                     -- Minimum WAL size

-- Performance settings
effective_io_concurrency = 200           -- For SSD storage
random_page_cost = 1.1                   -- For SSD storage
cpu_tuple_cost = 0.01                    -- CPU cost tuning
cpu_index_tuple_cost = 0.005             -- Index CPU cost
cpu_operator_cost = 0.0025               -- Operator CPU cost

-- Logging for monitoring
log_min_duration_statement = 1000        -- Log slow queries (1s+)
log_checkpoints = on                     -- Monitor checkpoint performance
log_lock_waits = on                      -- Monitor lock contention
```

**Index Optimization:**
```sql
-- Critical indexes for MAOS performance
CREATE INDEX CONCURRENTLY idx_tasks_status_created 
ON tasks (status, created_at) 
WHERE status IN ('QUEUED', 'RUNNING');

CREATE INDEX CONCURRENTLY idx_agents_status_heartbeat
ON agents (status, last_heartbeat)
WHERE status = 'ACTIVE';

CREATE INDEX CONCURRENTLY idx_messages_recipient_timestamp
ON messages (recipient, timestamp)
WHERE processed = false;

CREATE INDEX CONCURRENTLY idx_checkpoints_timestamp
ON checkpoints (created_at DESC);

-- Partial indexes for active data
CREATE INDEX CONCURRENTLY idx_active_tasks
ON tasks (id, priority, created_at)
WHERE status IN ('QUEUED', 'RUNNING');

-- Analyze tables for query optimization
ANALYZE tasks;
ANALYZE agents;
ANALYZE messages;
ANALYZE checkpoints;
```

#### Redis Optimization

```bash
# redis.conf optimizations
# Memory management
maxmemory 8gb
maxmemory-policy allkeys-lru
maxmemory-samples 10

# Persistence (for durability)
save 900 1
save 300 10
save 60 10000

# AOF persistence
appendonly yes
appendfsync everysec
no-appendfsync-on-rewrite no

# Network settings
tcp-keepalive 300
tcp-backlog 511
timeout 300

# Client connections
maxclients 10000

# Performance settings
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64

# Cluster settings (if using Redis Cluster)
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 15000
cluster-replica-validity-factor 10
```

### Application Performance Tuning

#### Connection Pool Optimization

```python
# Database connection pool tuning
DATABASE_CONFIG = {
    'pool_size': 20,              # Base pool size
    'max_overflow': 30,           # Additional connections
    'pool_timeout': 30,           # Connection timeout
    'pool_recycle': 3600,        # Recycle connections hourly
    'pool_pre_ping': True,       # Validate connections
    'echo': False,               # Disable SQL logging in production
    'connect_args': {
        'command_timeout': 60,
        'server_settings': {
            'application_name': 'maos-orchestrator',
            'tcp_keepalives_idle': '600',
            'tcp_keepalives_interval': '30',
            'tcp_keepalives_count': '3',
        }
    }
}

# Redis connection pool tuning
REDIS_CONFIG = {
    'connection_pool_kwargs': {
        'max_connections': 100,
        'retry_on_timeout': True,
        'health_check_interval': 30,
        'socket_connect_timeout': 5,
        'socket_timeout': 5,
        'socket_keepalive': True,
        'socket_keepalive_options': {
            'TCP_KEEPIDLE': 1,
            'TCP_KEEPINTVL': 3,
            'TCP_KEEPCNT': 5,
        }
    }
}
```

#### Async Processing Optimization

```python
# Optimized async configuration
ASYNC_CONFIG = {
    'task_queue_size': 10000,
    'worker_concurrency': 50,
    'batch_size': 100,
    'batch_timeout': 1.0,
    'circuit_breaker': {
        'failure_threshold': 5,
        'recovery_timeout': 60,
        'expected_exception': Exception,
    },
    'retry_policy': {
        'max_attempts': 3,
        'backoff_factor': 2,
        'max_delay': 60,
    }
}

# Optimized agent task processing
class OptimizedTaskProcessor:
    def __init__(self, config):
        self.config = config
        self.semaphore = asyncio.Semaphore(config['worker_concurrency'])
        self.task_queue = asyncio.Queue(config['task_queue_size'])
        self.batch_processor = BatchProcessor(config['batch_size'])
    
    async def process_tasks_in_batches(self):
        while True:
            batch = await self.batch_processor.collect_batch(
                self.task_queue, 
                timeout=self.config['batch_timeout']
            )
            
            if batch:
                await self.process_batch(batch)
    
    async def process_batch(self, tasks):
        async with asyncio.TaskGroup() as tg:
            for task in tasks:
                tg.create_task(self.process_single_task(task))
```

## Load Testing and Capacity Planning

### Load Testing Framework

```python
# load_test.py
import asyncio
import aiohttp
import time
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class LoadTestConfig:
    concurrent_users: int = 100
    requests_per_user: int = 10
    ramp_up_time: int = 60
    test_duration: int = 300
    target_url: str = "http://localhost:8000"

class LoadTester:
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results = []
    
    async def run_load_test(self):
        connector = aiohttp.TCPConnector(
            limit=self.config.concurrent_users * 2,
            limit_per_host=self.config.concurrent_users,
            keepalive_timeout=300
        )
        
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            
            # Ramp up users gradually
            for i in range(self.config.concurrent_users):
                task = asyncio.create_task(
                    self.user_session(session, i)
                )
                tasks.append(task)
                
                # Ramp up delay
                if i > 0:
                    await asyncio.sleep(
                        self.config.ramp_up_time / self.config.concurrent_users
                    )
            
            # Wait for all users to complete
            await asyncio.gather(*tasks)
    
    async def user_session(self, session: aiohttp.ClientSession, user_id: int):
        for request_id in range(self.config.requests_per_user):
            start_time = time.time()
            
            try:
                # Submit a test task
                task_response = await self.submit_task(session)
                task_id = task_response['task_id']
                
                # Wait for completion
                completion_time = await self.wait_for_completion(session, task_id)
                
                duration = time.time() - start_time
                
                self.results.append({
                    'user_id': user_id,
                    'request_id': request_id,
                    'duration': duration,
                    'success': True,
                    'task_completion_time': completion_time
                })
                
            except Exception as e:
                duration = time.time() - start_time
                self.results.append({
                    'user_id': user_id,
                    'request_id': request_id,
                    'duration': duration,
                    'success': False,
                    'error': str(e)
                })
    
    async def submit_task(self, session: aiohttp.ClientSession) -> Dict:
        payload = {
            "description": "Load test task - analyze sample data",
            "type": "analysis",
            "priority": "MEDIUM"
        }
        
        async with session.post(
            f"{self.config.target_url}/v1/tasks",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            return await response.json()
    
    async def wait_for_completion(self, session: aiohttp.ClientSession, task_id: str) -> float:
        start_time = time.time()
        
        while time.time() - start_time < 300:  # 5-minute timeout
            async with session.get(
                f"{self.config.target_url}/v1/tasks/{task_id}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                task_data = await response.json()
                
                if task_data['status'] in ['COMPLETED', 'FAILED']:
                    return time.time() - start_time
            
            await asyncio.sleep(1)
        
        raise TimeoutError(f"Task {task_id} did not complete within timeout")
    
    def generate_report(self) -> Dict:
        successful_requests = [r for r in self.results if r['success']]
        failed_requests = [r for r in self.results if not r['success']]
        
        if successful_requests:
            durations = [r['duration'] for r in successful_requests]
            completion_times = [r['task_completion_time'] for r in successful_requests]
        else:
            durations = []
            completion_times = []
        
        return {
            'total_requests': len(self.results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(self.results) * 100,
            'avg_response_time': sum(durations) / len(durations) if durations else 0,
            'avg_task_completion_time': sum(completion_times) / len(completion_times) if completion_times else 0,
            'p95_response_time': self._percentile(durations, 0.95) if durations else 0,
            'p99_response_time': self._percentile(durations, 0.99) if durations else 0,
        }
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]

# Run load test
async def main():
    config = LoadTestConfig(
        concurrent_users=50,
        requests_per_user=20,
        test_duration=600,
        target_url="https://api.maos.yourdomain.com"
    )
    
    tester = LoadTester(config)
    
    print("Starting load test...")
    await tester.run_load_test()
    
    report = tester.generate_report()
    print("\nLoad Test Report:")
    print(f"Total Requests: {report['total_requests']}")
    print(f"Success Rate: {report['success_rate']:.2f}%")
    print(f"Average Response Time: {report['avg_response_time']:.2f}s")
    print(f"Average Task Completion: {report['avg_task_completion_time']:.2f}s")
    print(f"P95 Response Time: {report['p95_response_time']:.2f}s")
    print(f"P99 Response Time: {report['p99_response_time']:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
```

### Capacity Planning Model

```python
# capacity_planning.py
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class SystemCapacity:
    cpu_cores: int
    memory_gb: int
    storage_gb: int
    network_gbps: int
    
    def scale(self, factor: float) -> 'SystemCapacity':
        return SystemCapacity(
            cpu_cores=int(self.cpu_cores * factor),
            memory_gb=int(self.memory_gb * factor),
            storage_gb=int(self.storage_gb * factor),
            network_gbps=int(self.network_gbps * factor)
        )

@dataclass
class WorkloadProfile:
    tasks_per_hour: int
    avg_task_duration: int  # seconds
    avg_agents_per_task: int
    memory_per_agent_mb: int
    cpu_per_agent_cores: float

class CapacityPlanner:
    def __init__(self):
        self.base_overhead = SystemCapacity(
            cpu_cores=2,    # Orchestrator overhead
            memory_gb=4,    # System overhead
            storage_gb=50,  # Base storage
            network_gbps=1  # Base network
        )
    
    def calculate_required_capacity(
        self, 
        workload: WorkloadProfile, 
        peak_multiplier: float = 2.0,
        buffer_percentage: float = 0.2
    ) -> SystemCapacity:
        """Calculate required system capacity for given workload"""
        
        # Calculate peak concurrent tasks
        peak_tasks_per_hour = workload.tasks_per_hour * peak_multiplier
        avg_concurrent_tasks = (
            peak_tasks_per_hour * workload.avg_task_duration / 3600
        )
        
        # Calculate required agents
        total_agents = avg_concurrent_tasks * workload.avg_agents_per_task
        
        # Calculate resource requirements
        cpu_cores = total_agents * workload.cpu_per_agent_cores
        memory_gb = total_agents * workload.memory_per_agent_mb / 1024
        
        # Storage: checkpoints + logs + metrics
        storage_per_task_mb = 10  # Estimated
        storage_gb = (
            workload.tasks_per_hour * 24 * 7 *  # Weekly retention
            storage_per_task_mb / 1024
        )
        
        # Network: API calls + agent communication
        network_gbps = max(1, math.ceil(workload.tasks_per_hour / 1000))
        
        required = SystemCapacity(
            cpu_cores=int(cpu_cores),
            memory_gb=int(memory_gb),
            storage_gb=int(storage_gb),
            network_gbps=network_gbps
        )
        
        # Add overhead and buffer
        total_required = SystemCapacity(
            cpu_cores=required.cpu_cores + self.base_overhead.cpu_cores,
            memory_gb=required.memory_gb + self.base_overhead.memory_gb,
            storage_gb=required.storage_gb + self.base_overhead.storage_gb,
            network_gbps=required.network_gbps + self.base_overhead.network_gbps
        )
        
        # Apply buffer
        buffer_factor = 1 + buffer_percentage
        return SystemCapacity(
            cpu_cores=int(total_required.cpu_cores * buffer_factor),
            memory_gb=int(total_required.memory_gb * buffer_factor),
            storage_gb=int(total_required.storage_gb * buffer_factor),
            network_gbps=int(total_required.network_gbps * buffer_factor)
        )
    
    def recommend_instance_types(self, required: SystemCapacity) -> Dict[str, List[str]]:
        """Recommend cloud instance types based on capacity requirements"""
        
        recommendations = {
            'aws': [],
            'gcp': [],
            'azure': []
        }
        
        # AWS instance recommendations
        if required.cpu_cores <= 4 and required.memory_gb <= 16:
            recommendations['aws'].append('c5.xlarge')
        elif required.cpu_cores <= 8 and required.memory_gb <= 32:
            recommendations['aws'].append('c5.2xlarge')
        elif required.cpu_cores <= 16 and required.memory_gb <= 64:
            recommendations['aws'].append('c5.4xlarge')
        else:
            recommendations['aws'].append('c5.9xlarge or larger')
        
        # Memory-optimized for high-memory workloads
        if required.memory_gb / required.cpu_cores > 4:
            if required.memory_gb <= 32:
                recommendations['aws'].append('r5.2xlarge')
            elif required.memory_gb <= 64:
                recommendations['aws'].append('r5.4xlarge')
            else:
                recommendations['aws'].append('r5.8xlarge or larger')
        
        return recommendations
    
    def estimate_costs(self, required: SystemCapacity) -> Dict[str, float]:
        """Estimate monthly costs for different cloud providers"""
        
        # Rough cost estimates (per month)
        aws_costs = {
            'compute': required.cpu_cores * 30,  # $30 per vCPU
            'memory': required.memory_gb * 5,    # $5 per GB
            'storage': required.storage_gb * 0.1, # $0.1 per GB
            'network': required.network_gbps * 50  # $50 per Gbps
        }
        
        gcp_costs = {
            'compute': required.cpu_cores * 28,
            'memory': required.memory_gb * 4.5,
            'storage': required.storage_gb * 0.09,
            'network': required.network_gbps * 45
        }
        
        azure_costs = {
            'compute': required.cpu_cores * 32,
            'memory': required.memory_gb * 5.5,
            'storage': required.storage_gb * 0.11,
            'network': required.network_gbps * 55
        }
        
        return {
            'aws': sum(aws_costs.values()),
            'gcp': sum(gcp_costs.values()),
            'azure': sum(azure_costs.values())
        }

# Example usage
def main():
    planner = CapacityPlanner()
    
    # Define workload profile
    workload = WorkloadProfile(
        tasks_per_hour=1000,      # High-volume workload
        avg_task_duration=300,    # 5-minute average
        avg_agents_per_task=3,    # Multi-agent tasks
        memory_per_agent_mb=512,  # 512MB per agent
        cpu_per_agent_cores=0.5   # 0.5 CPU cores per agent
    )
    
    # Calculate required capacity
    required_capacity = planner.calculate_required_capacity(workload)
    
    print("Capacity Planning Report")
    print("=" * 40)
    print(f"Workload: {workload.tasks_per_hour} tasks/hour")
    print(f"Required Capacity:")
    print(f"  CPU Cores: {required_capacity.cpu_cores}")
    print(f"  Memory: {required_capacity.memory_gb} GB")
    print(f"  Storage: {required_capacity.storage_gb} GB")
    print(f"  Network: {required_capacity.network_gbps} Gbps")
    
    # Instance recommendations
    recommendations = planner.recommend_instance_types(required_capacity)
    print(f"\nRecommended Instance Types:")
    for provider, instances in recommendations.items():
        print(f"  {provider.upper()}: {', '.join(instances)}")
    
    # Cost estimates
    costs = planner.estimate_costs(required_capacity)
    print(f"\nEstimated Monthly Costs:")
    for provider, cost in costs.items():
        print(f"  {provider.upper()}: ${cost:.2f}")

if __name__ == "__main__":
    main()
```

## Monitoring and Observability

### Key Performance Indicators (KPIs)

```yaml
# Grafana dashboard configuration
dashboard:
  title: "MAOS Scaling Dashboard"
  panels:
    - title: "Request Rate"
      targets:
        - expr: rate(maos_api_requests_total[5m])
        - legendFormat: "{{method}} {{endpoint}}"
    
    - title: "Task Processing Rate"
      targets:
        - expr: rate(maos_tasks_completed_total[5m])
        - legendFormat: "{{status}}"
    
    - title: "Agent Utilization"
      targets:
        - expr: (maos_agents_active / maos_agents_total) * 100
        - legendFormat: "Utilization %"
    
    - title: "Response Time Percentiles"
      targets:
        - expr: histogram_quantile(0.95, rate(maos_api_duration_seconds_bucket[5m]))
        - legendFormat: "P95"
        - expr: histogram_quantile(0.99, rate(maos_api_duration_seconds_bucket[5m]))
        - legendFormat: "P99"
    
    - title: "System Resources"
      targets:
        - expr: rate(container_cpu_usage_seconds_total[5m])
        - legendFormat: "CPU Usage"
        - expr: container_memory_usage_bytes / container_spec_memory_limit_bytes * 100
        - legendFormat: "Memory %"
    
    - title: "Database Performance"
      targets:
        - expr: rate(postgresql_stat_database_tup_returned_total[5m])
        - legendFormat: "DB Reads/sec"
        - expr: rate(postgresql_stat_database_tup_inserted_total[5m])
        - legendFormat: "DB Writes/sec"
```

### Alerting Rules

```yaml
# alerting-rules.yml
groups:
- name: maos-scaling
  rules:
  - alert: HighCPUUtilization
    expr: rate(container_cpu_usage_seconds_total[5m]) * 100 > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU utilization detected"
      description: "CPU utilization is above 80% for 5 minutes"

  - alert: HighMemoryUsage
    expr: container_memory_usage_bytes / container_spec_memory_limit_bytes * 100 > 85
    for: 3m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage detected"
      description: "Memory usage is above 85%"

  - alert: TaskQueueBacklog
    expr: maos_task_queue_depth > 100
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Task queue backlog building up"
      description: "More than 100 tasks queued for over 2 minutes"

  - alert: AgentSpawnFailure
    expr: rate(maos_agent_spawn_failures_total[5m]) > 0.1
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "High agent spawn failure rate"
      description: "Agent spawn failure rate above 10%"

  - alert: DatabaseConnectionPoolExhaustion
    expr: postgresql_stat_activity_count{state="active"} / postgresql_settings_max_connections * 100 > 90
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Database connection pool near exhaustion"
      description: "Active connections are above 90% of max_connections"
```

This comprehensive scaling and operations guide provides the foundation for running MAOS at scale with proper performance optimization, capacity planning, and monitoring. Regular review and adjustment of these configurations based on actual usage patterns will ensure optimal system performance.