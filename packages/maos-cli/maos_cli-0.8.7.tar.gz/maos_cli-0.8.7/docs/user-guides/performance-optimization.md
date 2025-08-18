# MAOS Performance Optimization Guide

## Overview

This guide provides comprehensive strategies for optimizing MAOS performance across different dimensions: task execution speed, resource utilization, throughput, and system responsiveness. Learn how to achieve maximum performance from your multi-agent orchestration system.

## Performance Fundamentals

### Understanding MAOS Performance Characteristics

**Key Performance Metrics:**

| Metric | Description | Target Range |
|--------|-------------|--------------|
| **Task Throughput** | Tasks completed per hour | 100-1000+ tasks/hour |
| **Agent Utilization** | % of time agents are actively working | 70-85% |
| **Response Latency** | API response time (P95) | <100ms |
| **Task Completion Time** | End-to-end task execution | 30s-30min (varies by complexity) |
| **Parallel Efficiency** | Speedup ratio vs sequential execution | 2x-5x |
| **Resource Efficiency** | CPU/Memory utilization | 60-80% |

**Performance Bottleneck Categories:**
1. **Task Planning**: Decomposition and scheduling overhead
2. **Agent Spawning**: Time to create and initialize agents
3. **Communication**: Inter-agent messaging latency
4. **State Management**: Shared memory access patterns
5. **Database Operations**: Query performance and connection pooling
6. **Storage I/O**: Checkpoint and artifact handling

## Task-Level Optimization

### 1. Intelligent Task Decomposition

**Optimal Parallelization Patterns:**

```python
# Example: Research task with optimal decomposition
def optimize_research_task(topic, aspects):
    """
    Break research into parallel streams while maintaining coherence
    """
    base_description = f"Research {topic} focusing on"
    
    # Parallel research streams
    subtasks = [
        f"{base_description} market size and growth trends",
        f"{base_description} competitive landscape and key players", 
        f"{base_description} technology trends and innovations",
        f"{base_description} regulatory environment and compliance",
        f"{base_description} customer needs and pain points"
    ]
    
    # Synthesis task depends on all research
    synthesis_task = f"Synthesize research findings on {topic} into comprehensive analysis"
    
    return {
        'parallel_tasks': subtasks,
        'synthesis_task': synthesis_task,
        'estimated_speedup': len(subtasks) * 0.8  # Account for coordination overhead
    }
```

**Task Complexity Analysis:**
```bash
# Analyze task for optimal agent allocation
maos task analyze "Create a comprehensive e-commerce platform with user management, product catalog, shopping cart, payment processing, and admin dashboard" --recommend-agents

# Output includes:
# - Complexity score: 8.5/10
# - Recommended agents: 6
# - Estimated duration: 45-60 minutes
# - Parallel efficiency: 3.2x
```

### 2. Agent Specialization Strategy

**Specialized Agent Configurations:**

```yaml
# config/optimized-agents.yml
agent_profiles:
  high_performance_researcher:
    type: researcher
    capabilities: ["web_search", "data_analysis", "report_generation"]
    resources:
      memory: "4GB"
      cpu_cores: 2.0
      timeout: 3600
    optimization:
      batch_size: 5
      cache_enabled: true
      parallel_search: true
      
  fast_coder:
    type: coder  
    capabilities: ["code_generation", "testing", "debugging"]
    resources:
      memory: "2GB"
      cpu_cores: 1.5
      timeout: 2400
    optimization:
      ide_integration: true
      auto_formatting: true
      lint_on_write: true
      
  data_analyst_pro:
    type: analyst
    capabilities: ["data_analysis", "visualization", "machine_learning"]
    resources:
      memory: "8GB"
      cpu_cores: 3.0
      timeout: 3600
    optimization:
      gpu_acceleration: true
      vectorized_operations: true
      distributed_computing: true
```

**Dynamic Agent Selection:**
```python
class OptimizedAgentSelector:
    def __init__(self):
        self.performance_history = {}
        self.agent_capabilities = {}
    
    def select_optimal_agents(self, task_requirements):
        """Select agents based on performance history and current load"""
        
        # Analyze task requirements
        required_capabilities = self.extract_capabilities(task_requirements)
        estimated_complexity = self.estimate_complexity(task_requirements)
        
        # Find best-performing agents for this task type
        candidate_agents = self.find_capable_agents(required_capabilities)
        
        # Score agents based on performance and availability
        agent_scores = {}
        for agent in candidate_agents:
            performance_score = self.get_performance_score(agent, task_requirements)
            load_score = self.get_load_score(agent)
            availability_score = self.get_availability_score(agent)
            
            agent_scores[agent] = (performance_score * 0.5 + 
                                 load_score * 0.3 + 
                                 availability_score * 0.2)
        
        # Select top agents up to max count
        max_agents = min(estimated_complexity + 2, 8)
        selected_agents = sorted(agent_scores.items(), 
                               key=lambda x: x[1], reverse=True)[:max_agents]
        
        return [agent[0] for agent in selected_agents]
```

### 3. Task Batching and Scheduling

**Intelligent Batch Processing:**

```python
class TaskBatchOptimizer:
    def __init__(self):
        self.batch_policies = {
            'research': {'max_batch_size': 8, 'similarity_threshold': 0.7},
            'coding': {'max_batch_size': 4, 'similarity_threshold': 0.8},
            'analysis': {'max_batch_size': 6, 'similarity_threshold': 0.6}
        }
    
    def optimize_batches(self, pending_tasks):
        """Group similar tasks for efficient batch processing"""
        
        task_batches = []
        processed_tasks = set()
        
        for task in pending_tasks:
            if task.id in processed_tasks:
                continue
                
            # Find similar tasks
            similar_tasks = self.find_similar_tasks(task, pending_tasks)
            policy = self.batch_policies.get(task.type, self.batch_policies['research'])
            
            # Create batch if enough similar tasks
            if len(similar_tasks) >= 2:
                batch_size = min(len(similar_tasks), policy['max_batch_size'])
                batch_tasks = similar_tasks[:batch_size]
                
                task_batches.append({
                    'type': task.type,
                    'tasks': batch_tasks,
                    'estimated_savings': self.calculate_batch_savings(batch_tasks)
                })
                
                processed_tasks.update([t.id for t in batch_tasks])
        
        return task_batches
    
    def find_similar_tasks(self, reference_task, task_pool):
        """Find tasks similar enough to batch together"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Extract task descriptions
        descriptions = [reference_task.description] + [t.description for t in task_pool 
                                                      if t.id != reference_task.id]
        
        # Calculate similarity
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(descriptions)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        # Filter by similarity threshold
        policy = self.batch_policies.get(reference_task.type, self.batch_policies['research'])
        similar_indices = [i for i, sim in enumerate(similarities) 
                          if sim >= policy['similarity_threshold']]
        
        return [reference_task] + [task_pool[i] for i in similar_indices]
```

**Optimized Task Scheduling:**
```bash
# Configure advanced scheduling
maos config set scheduling.algorithm "intelligent_priority"
maos config set scheduling.batch_optimization true
maos config set scheduling.load_balancing true
maos config set scheduling.agent_affinity true

# Resource-aware scheduling
maos config set scheduling.consider_agent_load true
maos config set scheduling.consider_system_resources true
maos config set scheduling.max_queue_time 300  # 5 minutes
```

## Agent-Level Optimization

### 1. Agent Pool Management

**Dynamic Pool Sizing:**

```python
class AdaptiveAgentPoolManager:
    def __init__(self):
        self.target_utilization = 0.75
        self.min_pool_size = 3
        self.max_pool_size = 50
        self.scale_up_threshold = 0.85
        self.scale_down_threshold = 0.30
        
    async def optimize_pool_size(self):
        """Dynamically adjust agent pool based on utilization"""
        
        current_metrics = await self.get_agent_metrics()
        
        for agent_type in ['researcher', 'coder', 'analyst']:
            metrics = current_metrics[agent_type]
            current_count = metrics['total_agents']
            utilization = metrics['utilization']
            queue_depth = metrics['queue_depth']
            
            # Determine if scaling is needed
            if (utilization > self.scale_up_threshold or 
                queue_depth > current_count * 2):
                # Scale up
                new_count = min(int(current_count * 1.5), self.max_pool_size)
                await self.scale_agent_pool(agent_type, new_count)
                
            elif (utilization < self.scale_down_threshold and 
                  queue_depth < current_count * 0.5):
                # Scale down
                new_count = max(int(current_count * 0.7), self.min_pool_size)
                await self.scale_agent_pool(agent_type, new_count)
    
    async def scale_agent_pool(self, agent_type, target_count):
        """Scale agent pool to target count"""
        current_count = await self.get_agent_count(agent_type)
        
        if target_count > current_count:
            # Spawn additional agents
            agents_to_spawn = target_count - current_count
            await self.spawn_agents(agent_type, agents_to_spawn)
        elif target_count < current_count:
            # Terminate excess agents (gracefully)
            agents_to_remove = current_count - target_count  
            await self.terminate_agents(agent_type, agents_to_remove)
```

**Agent Warm-up and Caching:**
```python
class AgentWarmupManager:
    def __init__(self):
        self.warmup_cache = {}
        
    async def warm_up_agents(self, predicted_workload):
        """Pre-spawn and warm up agents based on predicted workload"""
        
        for agent_type, predicted_count in predicted_workload.items():
            current_warm_agents = len(self.warmup_cache.get(agent_type, []))
            
            if predicted_count > current_warm_agents:
                agents_needed = predicted_count - current_warm_agents
                
                # Pre-spawn agents
                warm_agents = await self.spawn_warm_agents(agent_type, agents_needed)
                
                # Initialize with common resources
                await self.initialize_agents(warm_agents)
                
                if agent_type not in self.warmup_cache:
                    self.warmup_cache[agent_type] = []
                self.warmup_cache[agent_type].extend(warm_agents)
    
    async def get_warm_agent(self, agent_type):
        """Get a pre-warmed agent for immediate use"""
        if agent_type in self.warmup_cache and self.warmup_cache[agent_type]:
            agent = self.warmup_cache[agent_type].pop(0)
            
            # Replace the agent in warm cache
            asyncio.create_task(self.maintain_warm_pool(agent_type))
            
            return agent
        
        # Fallback to normal agent spawning
        return await self.spawn_agent(agent_type)
```

### 2. Agent Resource Optimization

**Memory Management:**
```yaml
# Memory optimization configuration
agents:
  memory_management:
    garbage_collection:
      enabled: true
      frequency: 300  # seconds
      threshold: 0.8  # 80% memory usage
    
    caching:
      enabled: true
      max_cache_size: "1GB"
      ttl: 3600  # 1 hour
      
    memory_profiling:
      enabled: true
      sample_rate: 0.1
      alert_threshold: "2GB"

# Resource limits by agent type  
agent_types:
  researcher:
    memory:
      request: "1GB"
      limit: "4GB"
    cpu:
      request: 1.0
      limit: 2.0
      
  coder:
    memory:
      request: "512MB" 
      limit: "2GB"
    cpu:
      request: 0.5
      limit: 1.5
      
  analyst:
    memory:
      request: "2GB"
      limit: "8GB"
    cpu:
      request: 1.5
      limit: 4.0
```

**CPU Optimization:**
```python
import asyncio
import concurrent.futures

class CPUOptimizedAgent:
    def __init__(self, cpu_cores=2):
        self.cpu_cores = cpu_cores
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=cpu_cores * 2
        )
        self.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=cpu_cores
        )
    
    async def process_task_optimized(self, task):
        """Process task with optimal CPU utilization"""
        
        if self.is_cpu_intensive(task):
            # Use process pool for CPU-bound work
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.process_pool, 
                self.cpu_intensive_work, 
                task
            )
        elif self.is_io_intensive(task):
            # Use async for I/O-bound work
            result = await self.async_io_work(task)
        else:
            # Use thread pool for mixed workload
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.thread_pool,
                self.mixed_work,
                task
            )
        
        return result
    
    def is_cpu_intensive(self, task):
        """Determine if task is CPU-intensive"""
        cpu_indicators = [
            'analysis', 'calculation', 'processing',
            'computation', 'algorithm', 'optimization'
        ]
        return any(indicator in task.description.lower() 
                  for indicator in cpu_indicators)
```

## System-Level Optimization

### 1. Database Performance Tuning

**PostgreSQL Optimization for MAOS:**
```sql
-- postgresql.conf optimizations
-- Connection settings
max_connections = 200
shared_buffers = '4GB'           -- 25% of RAM
effective_cache_size = '12GB'    -- 75% of RAM
work_mem = '256MB'               -- Per sort/hash operation
maintenance_work_mem = '1GB'     -- For maintenance ops

-- WAL settings for performance
wal_buffers = '64MB'
checkpoint_completion_target = 0.9
max_wal_size = '4GB'
min_wal_size = '1GB'

-- Query optimization
random_page_cost = 1.1           -- For SSD storage
effective_io_concurrency = 200   -- For SSD storage
cpu_tuple_cost = 0.01
cpu_index_tuple_cost = 0.005

-- Logging for optimization
log_min_duration_statement = 1000  -- Log slow queries
log_checkpoints = on
log_lock_waits = on
```

**Optimized Database Queries:**
```sql
-- Optimized indexes for MAOS workloads
CREATE INDEX CONCURRENTLY idx_tasks_status_priority_created 
ON tasks (status, priority DESC, created_at DESC) 
WHERE status IN ('QUEUED', 'RUNNING');

CREATE INDEX CONCURRENTLY idx_agents_type_status_heartbeat
ON agents (type, status, last_heartbeat DESC)
WHERE status IN ('IDLE', 'BUSY');

CREATE INDEX CONCURRENTLY idx_messages_recipient_unprocessed
ON messages (recipient, created_at DESC)
WHERE processed = false;

-- Partitioned tables for large datasets
CREATE TABLE tasks_2025 PARTITION OF tasks
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Optimized queries
EXPLAIN (ANALYZE, BUFFERS) 
SELECT t.id, t.description, t.status, t.created_at
FROM tasks t
WHERE t.status = 'QUEUED'
  AND t.priority = 'HIGH'
ORDER BY t.created_at ASC
LIMIT 20;
```

**Connection Pool Optimization:**
```python
# Advanced connection pooling
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine

def create_optimized_db_engine():
    return create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,              # Base pool size
        max_overflow=30,           # Additional connections  
        pool_timeout=30,           # Connection timeout
        pool_recycle=3600,         # Recycle connections hourly
        pool_pre_ping=True,        # Validate connections
        connect_args={
            'connect_timeout': 10,
            'command_timeout': 60,
            'application_name': 'maos-optimized',
            'server_settings': {
                'tcp_keepalives_idle': '600',
                'tcp_keepalives_interval': '30',
                'tcp_keepalives_count': '3'
            }
        }
    )
```

### 2. Redis Performance Optimization

**Redis Configuration for MAOS:**
```bash
# redis.conf optimizations
# Memory management
maxmemory 8gb
maxmemory-policy allkeys-lru
maxmemory-samples 10

# Network optimization
tcp-keepalive 300
tcp-backlog 511
timeout 300

# Performance settings
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
set-max-intset-entries 512

# Persistence optimization (for durability)
save 900 1
save 300 10  
save 60 10000
appendonly yes
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Client connections
maxclients 10000
```

**Optimized Redis Usage Patterns:**
```python
import redis
import json
from redis.connection import ConnectionPool

class OptimizedRedisManager:
    def __init__(self):
        # Connection pool for better performance
        self.pool = ConnectionPool(
            host='localhost',
            port=6379,
            db=0,
            max_connections=100,
            retry_on_timeout=True,
            health_check_interval=30
        )
        self.redis_client = redis.Redis(connection_pool=self.pool)
        
    async def batch_operations(self, operations):
        """Execute Redis operations in batches for better performance"""
        pipe = self.redis_client.pipeline()
        
        for operation in operations:
            getattr(pipe, operation['command'])(*operation['args'])
        
        return await pipe.execute()
    
    async def optimized_message_queue(self, queue_name, messages):
        """Optimized message queue operations"""
        pipe = self.redis_client.pipeline()
        
        # Batch multiple messages
        for message in messages:
            pipe.lpush(queue_name, json.dumps(message))
        
        # Set expiry for cleanup
        pipe.expire(queue_name, 86400)  # 24 hours
        
        return await pipe.execute()
    
    async def smart_caching(self, key, value, ttl=3600):
        """Smart caching with compression for large values"""
        import zlib
        
        serialized_value = json.dumps(value)
        
        # Compress if value is large
        if len(serialized_value) > 1024:  # 1KB threshold
            compressed_value = zlib.compress(serialized_value.encode())
            await self.redis_client.setex(
                f"compressed:{key}", 
                ttl, 
                compressed_value
            )
        else:
            await self.redis_client.setex(key, ttl, serialized_value)
```

### 3. I/O and Storage Optimization

**Checkpoint Optimization:**
```python
import asyncio
import aiofiles
import aioboto3
import lz4
import json

class OptimizedCheckpointManager:
    def __init__(self):
        self.compression_enabled = True
        self.async_uploads = True
        self.batch_size = 10
        
    async def create_optimized_checkpoint(self, state_data):
        """Create checkpoint with optimizations"""
        
        # Parallel serialization of different state components
        tasks = [
            self.serialize_agents(state_data['agents']),
            self.serialize_tasks(state_data['tasks']),
            self.serialize_shared_state(state_data['shared_state']),
            self.serialize_message_queues(state_data['message_queues'])
        ]
        
        serialized_components = await asyncio.gather(*tasks)
        
        # Combine into checkpoint
        checkpoint_data = {
            'timestamp': state_data['timestamp'],
            'version': state_data['version'],
            'agents': serialized_components[0],
            'tasks': serialized_components[1], 
            'shared_state': serialized_components[2],
            'message_queues': serialized_components[3]
        }
        
        # Compress checkpoint
        if self.compression_enabled:
            checkpoint_json = json.dumps(checkpoint_data)
            compressed_data = lz4.frame.compress(checkpoint_json.encode())
            
            # Calculate compression ratio
            original_size = len(checkpoint_json)
            compressed_size = len(compressed_data)
            compression_ratio = original_size / compressed_size
            
            print(f"Checkpoint compressed: {compression_ratio:.2f}x reduction")
            
            return compressed_data
        
        return json.dumps(checkpoint_data).encode()
    
    async def parallel_upload_to_s3(self, checkpoint_data, checkpoint_id):
        """Upload checkpoint to S3 with multipart for large files"""
        
        if len(checkpoint_data) > 100 * 1024 * 1024:  # 100MB threshold
            await self.multipart_upload(checkpoint_data, checkpoint_id)
        else:
            await self.simple_upload(checkpoint_data, checkpoint_id)
    
    async def multipart_upload(self, data, checkpoint_id):
        """Multipart upload for large checkpoints"""
        session = aioboto3.Session()
        
        async with session.client('s3') as s3:
            # Initiate multipart upload
            response = await s3.create_multipart_upload(
                Bucket='maos-checkpoints',
                Key=f'checkpoints/{checkpoint_id}.checkpoint'
            )
            
            upload_id = response['UploadId']
            part_size = 10 * 1024 * 1024  # 10MB parts
            parts = []
            
            # Upload parts in parallel
            upload_tasks = []
            for i in range(0, len(data), part_size):
                part_num = i // part_size + 1
                part_data = data[i:i + part_size]
                
                upload_tasks.append(
                    self.upload_part(s3, upload_id, part_num, part_data, checkpoint_id)
                )
            
            parts = await asyncio.gather(*upload_tasks)
            
            # Complete multipart upload
            await s3.complete_multipart_upload(
                Bucket='maos-checkpoints',
                Key=f'checkpoints/{checkpoint_id}.checkpoint',
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
```

## Network and Communication Optimization

### 1. Message Bus Optimization

**High-Performance Message Routing:**
```python
import asyncio
from collections import defaultdict, deque
import time

class OptimizedMessageBus:
    def __init__(self):
        self.message_queues = defaultdict(deque)
        self.subscribers = defaultdict(list)
        self.message_batches = defaultdict(list)
        self.batch_size = 100
        self.batch_timeout = 0.1  # 100ms
        self.stats = defaultdict(int)
        
    async def optimized_publish(self, topic, message):
        """Batch messages for efficient publishing"""
        self.message_batches[topic].append(message)
        self.stats[f'messages_queued_{topic}'] += 1
        
        # Process batch if size threshold reached
        if len(self.message_batches[topic]) >= self.batch_size:
            await self.flush_batch(topic)
    
    async def flush_batch(self, topic):
        """Flush message batch to subscribers"""
        if not self.message_batches[topic]:
            return
            
        batch = self.message_batches[topic].copy()
        self.message_batches[topic].clear()
        
        # Parallel delivery to all subscribers
        subscriber_tasks = []
        for subscriber in self.subscribers[topic]:
            subscriber_tasks.append(
                self.deliver_batch(subscriber, batch)
            )
        
        if subscriber_tasks:
            await asyncio.gather(*subscriber_tasks, return_exceptions=True)
        
        self.stats[f'batches_sent_{topic}'] += 1
        self.stats[f'messages_sent_{topic}'] += len(batch)
    
    async def deliver_batch(self, subscriber, messages):
        """Deliver message batch to subscriber"""
        try:
            await subscriber.handle_message_batch(messages)
        except Exception as e:
            self.stats['delivery_errors'] += 1
            print(f"Message delivery error: {e}")
    
    async def periodic_flush(self):
        """Periodically flush message batches"""
        while True:
            await asyncio.sleep(self.batch_timeout)
            
            for topic in list(self.message_batches.keys()):
                if self.message_batches[topic]:
                    await self.flush_batch(topic)
```

### 2. Agent Communication Optimization

**Optimized Inter-Agent Communication:**
```python
class OptimizedAgentCommunication:
    def __init__(self):
        self.communication_cache = {}
        self.message_compression = True
        self.priority_queues = {
            'CRITICAL': deque(),
            'HIGH': deque(), 
            'MEDIUM': deque(),
            'LOW': deque()
        }
        
    async def send_message_optimized(self, from_agent, to_agent, message, priority='MEDIUM'):
        """Optimized message sending with caching and compression"""
        
        # Check cache for recent similar communications
        cache_key = f"{from_agent}:{to_agent}:{hash(str(message))}"
        if cache_key in self.communication_cache:
            cached_result = self.communication_cache[cache_key]
            if time.time() - cached_result['timestamp'] < 300:  # 5 minutes
                return cached_result['response']
        
        # Compress message if enabled and large
        processed_message = message
        if self.message_compression and len(str(message)) > 500:
            processed_message = self.compress_message(message)
        
        # Add to priority queue
        self.priority_queues[priority].append({
            'from': from_agent,
            'to': to_agent,
            'message': processed_message,
            'timestamp': time.time()
        })
        
        # Process queue
        response = await self.process_message_queue()
        
        # Cache response
        self.communication_cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
        
        return response
    
    async def process_message_queue(self):
        """Process messages in priority order"""
        
        # Process in priority order
        for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            while self.priority_queues[priority]:
                message_data = self.priority_queues[priority].popleft()
                
                try:
                    response = await self.deliver_message(message_data)
                    return response
                except Exception as e:
                    # Handle delivery failure
                    if priority in ['CRITICAL', 'HIGH']:
                        # Retry critical/high priority messages
                        await asyncio.sleep(0.1)
                        self.priority_queues[priority].appendleft(message_data)
                    
                    print(f"Message delivery failed: {e}")
        
        return None
    
    def compress_message(self, message):
        """Compress large messages"""
        import gzip
        import json
        
        json_str = json.dumps(message)
        return gzip.compress(json_str.encode())
```

## Performance Monitoring and Analysis

### 1. Real-Time Performance Monitoring

**Performance Metrics Collection:**
```python
import time
import psutil
import asyncio
from collections import deque, defaultdict
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class PerformanceMetrics:
    timestamp: float
    cpu_usage: float
    memory_usage: float
    task_throughput: float
    agent_utilization: float
    response_latency_p95: float
    queue_depth: int

class PerformanceMonitor:
    def __init__(self, window_size=100):
        self.metrics_window = deque(maxlen=window_size)
        self.task_timings = deque(maxlen=1000)
        self.api_timings = deque(maxlen=1000) 
        self.agent_stats = defaultdict(list)
        
    async def collect_metrics(self):
        """Collect comprehensive performance metrics"""
        
        # System metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        memory_usage = memory_info.percent
        
        # MAOS-specific metrics
        task_throughput = await self.calculate_task_throughput()
        agent_utilization = await self.calculate_agent_utilization()
        response_latency = await self.calculate_response_latency()
        queue_depth = await self.get_queue_depth()
        
        metrics = PerformanceMetrics(
            timestamp=time.time(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            task_throughput=task_throughput,
            agent_utilization=agent_utilization,
            response_latency_p95=response_latency,
            queue_depth=queue_depth
        )
        
        self.metrics_window.append(metrics)
        
        # Check for performance issues
        await self.analyze_performance_trends()
        
        return metrics
    
    async def analyze_performance_trends(self):
        """Analyze performance trends and identify issues"""
        
        if len(self.metrics_window) < 10:
            return
        
        recent_metrics = list(self.metrics_window)[-10:]
        
        # CPU trend analysis
        cpu_trend = [m.cpu_usage for m in recent_metrics]
        if sum(cpu_trend) / len(cpu_trend) > 80:
            await self.handle_high_cpu_usage()
        
        # Memory trend analysis  
        memory_trend = [m.memory_usage for m in recent_metrics]
        if sum(memory_trend) / len(memory_trend) > 85:
            await self.handle_high_memory_usage()
        
        # Throughput trend analysis
        throughput_trend = [m.task_throughput for m in recent_metrics]
        if len(throughput_trend) > 5:
            recent_avg = sum(throughput_trend[-5:]) / 5
            historical_avg = sum(throughput_trend[:-5]) / (len(throughput_trend) - 5)
            
            if recent_avg < historical_avg * 0.7:  # 30% decrease
                await self.handle_throughput_degradation()
    
    async def handle_high_cpu_usage(self):
        """Handle high CPU usage situations"""
        print("High CPU usage detected - optimizing...")
        
        # Reduce concurrent agents
        await self.reduce_agent_concurrency()
        
        # Enable CPU throttling for non-critical tasks
        await self.enable_cpu_throttling()
    
    async def handle_high_memory_usage(self):
        """Handle high memory usage situations"""
        print("High memory usage detected - optimizing...")
        
        # Trigger garbage collection
        import gc
        gc.collect()
        
        # Reduce agent memory limits
        await self.reduce_agent_memory_limits()
        
        # Clear caches
        await self.clear_performance_caches()
    
    async def generate_performance_report(self):
        """Generate comprehensive performance report"""
        
        if not self.metrics_window:
            return "No metrics available"
        
        metrics_list = list(self.metrics_window)
        
        # Calculate statistics
        avg_cpu = sum(m.cpu_usage for m in metrics_list) / len(metrics_list)
        avg_memory = sum(m.memory_usage for m in metrics_list) / len(metrics_list)
        avg_throughput = sum(m.task_throughput for m in metrics_list) / len(metrics_list)
        avg_latency = sum(m.response_latency_p95 for m in metrics_list) / len(metrics_list)
        
        # Performance score calculation
        performance_score = self.calculate_performance_score(
            avg_cpu, avg_memory, avg_throughput, avg_latency
        )
        
        report = f"""
MAOS Performance Report
=====================

System Metrics:
  Average CPU Usage: {avg_cpu:.1f}%
  Average Memory Usage: {avg_memory:.1f}%
  
Task Processing:
  Average Throughput: {avg_throughput:.1f} tasks/minute
  Average P95 Latency: {avg_latency:.1f}ms
  
Performance Score: {performance_score:.1f}/100

Recommendations:
{await self.get_optimization_recommendations()}
        """
        
        return report
```

### 2. Performance Benchmarking

**Automated Benchmarking Suite:**
```python
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor

class MAOSBenchmarkSuite:
    def __init__(self):
        self.benchmark_results = {}
        
    async def run_comprehensive_benchmark(self):
        """Run complete benchmark suite"""
        
        print("Starting MAOS Performance Benchmark Suite...")
        
        # Run individual benchmarks
        benchmarks = [
            ('Task Submission Latency', self.benchmark_task_submission),
            ('Agent Spawning Performance', self.benchmark_agent_spawning),
            ('Parallel Processing Efficiency', self.benchmark_parallel_processing),
            ('Communication Latency', self.benchmark_communication),
            ('Database Performance', self.benchmark_database),
            ('Storage I/O Performance', self.benchmark_storage)
        ]
        
        for benchmark_name, benchmark_func in benchmarks:
            print(f"\nRunning {benchmark_name}...")
            result = await benchmark_func()
            self.benchmark_results[benchmark_name] = result
            print(f"Result: {result}")
        
        # Generate comparison report
        return self.generate_benchmark_report()
    
    async def benchmark_task_submission(self):
        """Benchmark task submission latency"""
        
        submission_times = []
        num_tasks = 100
        
        for i in range(num_tasks):
            start_time = time.time()
            
            # Submit test task
            task_id = await self.submit_benchmark_task(
                f"Benchmark task {i}: Simple calculation"
            )
            
            end_time = time.time()
            submission_times.append((end_time - start_time) * 1000)  # Convert to ms
        
        return {
            'average_latency_ms': statistics.mean(submission_times),
            'p95_latency_ms': self.percentile(submission_times, 0.95),
            'p99_latency_ms': self.percentile(submission_times, 0.99),
            'min_latency_ms': min(submission_times),
            'max_latency_ms': max(submission_times)
        }
    
    async def benchmark_parallel_processing(self):
        """Benchmark parallel processing efficiency"""
        
        # Test with different agent counts
        agent_counts = [1, 2, 4, 6, 8]
        efficiency_results = {}
        
        base_task = "Perform data analysis on sample dataset with statistical calculations"
        
        for agent_count in agent_counts:
            start_time = time.time()
            
            # Submit task with specific agent count
            task_id = await self.submit_benchmark_task(
                base_task,
                max_agents=agent_count
            )
            
            # Wait for completion
            await self.wait_for_task_completion(task_id, timeout=300)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            efficiency_results[agent_count] = {
                'execution_time': execution_time,
                'speedup': efficiency_results[1]['execution_time'] / execution_time if agent_count > 1 else 1.0
            }
        
        return efficiency_results
    
    async def benchmark_agent_spawning(self):
        """Benchmark agent spawning performance"""
        
        spawn_times = []
        agent_types = ['researcher', 'coder', 'analyst']
        
        for agent_type in agent_types:
            for i in range(10):  # 10 agents per type
                start_time = time.time()
                
                agent_id = await self.spawn_benchmark_agent(agent_type)
                
                end_time = time.time()
                spawn_times.append((end_time - start_time) * 1000)
                
                # Clean up
                await self.terminate_benchmark_agent(agent_id)
        
        return {
            'average_spawn_time_ms': statistics.mean(spawn_times),
            'p95_spawn_time_ms': self.percentile(spawn_times, 0.95),
            'total_agents_tested': len(spawn_times)
        }
    
    def generate_benchmark_report(self):
        """Generate comprehensive benchmark report"""
        
        report = """
MAOS Performance Benchmark Report
================================

"""
        
        for benchmark_name, results in self.benchmark_results.items():
            report += f"{benchmark_name}:\n"
            
            if isinstance(results, dict):
                for key, value in results.items():
                    if isinstance(value, float):
                        report += f"  {key}: {value:.2f}\n"
                    else:
                        report += f"  {key}: {value}\n"
            else:
                report += f"  Result: {results}\n"
            
            report += "\n"
        
        # Add performance recommendations
        report += self.generate_performance_recommendations()
        
        return report
    
    def generate_performance_recommendations(self):
        """Generate performance optimization recommendations"""
        
        recommendations = "\nPerformance Recommendations:\n"
        recommendations += "============================\n"
        
        # Analyze results and provide recommendations
        task_submission = self.benchmark_results.get('Task Submission Latency', {})
        if task_submission.get('average_latency_ms', 0) > 100:
            recommendations += "• High task submission latency detected. Consider optimizing database connections.\n"
        
        parallel_processing = self.benchmark_results.get('Parallel Processing Efficiency', {})
        if parallel_processing:
            max_speedup = max(result.get('speedup', 1.0) for result in parallel_processing.values())
            if max_speedup < 2.0:
                recommendations += "• Low parallel processing efficiency. Review task decomposition strategies.\n"
        
        agent_spawning = self.benchmark_results.get('Agent Spawning Performance', {})
        if agent_spawning.get('average_spawn_time_ms', 0) > 5000:
            recommendations += "• Slow agent spawning detected. Consider implementing agent warming strategies.\n"
        
        return recommendations
    
    def percentile(self, data, percentile):
        """Calculate percentile of data"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]
```

This comprehensive performance optimization guide provides the foundation for achieving maximum performance from your MAOS deployment. Regular monitoring, benchmarking, and optimization based on your specific workloads will ensure continued high performance as your usage scales.