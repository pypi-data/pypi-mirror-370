# MAOS Quick Start Guide
## Multi-Agent Orchestration System

Welcome to MAOS! This guide will get you up and running with the Multi-Agent Orchestration System in under 5 minutes.

---

## 🚀 Installation

### Option 1: Install from Source (Recommended for Testing)

```bash
# Clone the repository
cd /Users/vincentsider/2-Projects/1-KEY PROJECTS/mazurai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install MAOS in development mode
pip install -e .
```

### Option 2: Docker Installation

```bash
# Build the Docker image
docker build -t maos:latest .

# Run with Docker Compose (includes Redis)
docker-compose up -d
```

---

## 🔧 Prerequisites

### 1. Start Redis (Required for State Management)

```bash
# Using Docker
docker run -d --name maos-redis -p 6379:6379 redis:7-alpine

# Or using local Redis
redis-server
```

### 2. Verify Claude Code is Available

```bash
# MAOS uses Claude Code's Task API for true parallel execution
which claude
```

### 3. Set Environment Variables

```bash
# Create .env file
cat > .env << EOF
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Security (for production)
JWT_SECRET_KEY=$(openssl rand -hex 32)
API_KEY_SECRET=$(openssl rand -hex 32)

# Agent Configuration
MAX_AGENTS=20
DEFAULT_AGENT_TIMEOUT=300

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
EOF

# Load environment
source .env
```

---

## 🎯 Basic Usage

### 1. Start the MAOS System

```bash
# Start the orchestration system
maos start

# Or with custom configuration
maos start --config config/production.yaml

# Check system status
maos status
```

### 2. Create Your First Task

```bash
# Simple task execution
maos task create "Analyze the codebase and generate documentation"

# Task with multiple agents
maos task create "Build a REST API" --agents 3 --strategy parallel

# Complex workflow with dependencies
maos task create "Deploy application" \
  --subtasks "Run tests,Build Docker image,Push to registry,Deploy to k8s" \
  --strategy pipeline
```

### 3. Monitor Task Progress

```bash
# Watch task execution in real-time
maos task status --follow

# Get detailed task information
maos task show <task-id>

# View agent activity
maos agent list --active
```

### 4. Working with Agents

```bash
# List all agents
maos agent list

# Spawn specific agent types
maos agent spawn --type researcher --name "Research-Bot"
maos agent spawn --type coder --count 3

# Monitor agent health
maos agent health

# View agent metrics
maos agent metrics <agent-id>
```

---

## 🧪 Testing the System

### Run the Test Suite

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/unit/           # Unit tests
pytest tests/integration/    # Integration tests
pytest tests/performance/    # Performance benchmarks

# Run with coverage
pytest --cov=src tests/
```

### Performance Benchmark

```bash
# Run the benchmark suite
python scripts/benchmark.py

# Compare sequential vs parallel execution
python scripts/benchmark.py --compare

# Test with different agent counts
python scripts/benchmark.py --agents 5,10,20
```

---

## 💡 Example Workflows

### Example 1: Code Analysis Task

```bash
# Create a code analysis workflow
maos task create "Analyze project structure" \
  --config examples/code-analysis.yaml

# Monitor progress
maos task status --follow
```

### Example 2: Multi-Agent Build Pipeline

```python
# examples/pipeline.py
from maos import Orchestrator, Task

# Initialize orchestrator
orchestrator = Orchestrator()

# Create pipeline
task = Task(
    name="Build and Deploy",
    subtasks=[
        Task("Lint code", agent_type="tester"),
        Task("Run tests", agent_type="tester"),
        Task("Build application", agent_type="coder"),
        Task("Deploy", agent_type="coder")
    ],
    strategy="pipeline"
)

# Execute
result = orchestrator.execute(task)
print(f"Pipeline completed in {result.duration} seconds")
```

### Example 3: Consensus-Based Decision

```bash
# Create a consensus task
maos task create "Choose deployment strategy" \
  --agents 5 \
  --consensus majority \
  --timeout 60
```

---

## 🔍 Verification & Health Checks

### System Health Check

```bash
# Full system health check
maos health

# Component-specific checks
maos health redis
maos health agents
maos health tasks
```

### Verify Parallel Execution

```bash
# Run parallel execution test
python -c "
from maos.core import Orchestrator
import time

# Create test task
orch = Orchestrator()
start = time.time()

# Run 5 tasks in parallel (should take ~2 minutes, not 10)
tasks = [orch.create_task(f'Sleep 2 minutes - Task {i}') for i in range(5)]
orch.execute_parallel(tasks)

duration = time.time() - start
print(f'Parallel execution took {duration:.1f} seconds')
print(f'Speedup: {(5*120)/duration:.1f}x')
"
```

---

## 🛠️ Configuration

### Basic Configuration (config/default.yaml)

```yaml
orchestrator:
  max_agents: 20
  default_strategy: adaptive
  checkpoint_interval: 30

redis:
  host: localhost
  port: 6379
  db: 0
  pool_size: 50

agents:
  timeout: 300
  health_check_interval: 10
  auto_restart: true

monitoring:
  enabled: true
  metrics_port: 9090
  log_level: INFO
```

### Production Configuration

```bash
# Use production config
maos start --config config/production.yaml --env production
```

---

## 📊 Monitoring & Metrics

### Prometheus Metrics

```bash
# Metrics available at http://localhost:9090/metrics
curl http://localhost:9090/metrics

# Key metrics:
# - maos_tasks_total
# - maos_agents_active
# - maos_task_duration_seconds
# - maos_agent_utilization
```

### Grafana Dashboard

```bash
# Import dashboard
maos dashboard import dashboards/maos-overview.json

# Access at http://localhost:3000
```

---

## 🔄 Checkpoints & Recovery

### Manual Checkpoint

```bash
# Create checkpoint
maos checkpoint create --name "before-deployment"

# List checkpoints
maos checkpoint list

# Recover from checkpoint
maos recover --checkpoint "before-deployment"
```

### Automatic Recovery

```bash
# System automatically creates checkpoints every 30 seconds
# On crash, recover with:
maos recover --latest
```

---

## 🐛 Troubleshooting

### Common Issues

1. **Redis Connection Error**
```bash
# Check Redis is running
redis-cli ping

# Restart Redis
docker restart maos-redis
```

2. **Agent Spawn Failures**
```bash
# Check Claude Code availability
which claude

# Check agent logs
maos logs --agent <agent-id>
```

3. **Task Stuck**
```bash
# Force task cancellation
maos task cancel <task-id>

# Clean up stuck agents
maos agent cleanup
```

### Debug Mode

```bash
# Run with debug logging
maos start --debug

# Verbose output
maos task create "Test task" -vvv
```

---

## 📚 Next Steps

1. Read the [Architecture Documentation](architecture.md)
2. Review [API Documentation](api-reference.md)
3. Explore [Advanced Features](advanced-features.md)
4. Join our [Community Discord](https://discord.gg/maos)

---

## 🆘 Getting Help

- **Documentation**: `/docs/` directory
- **Examples**: `/examples/` directory
- **Issues**: Check `maos logs` for detailed error messages
- **Support**: Create an issue on GitHub

---

## 🎉 Quick Win - Your First Parallel Task

Try this to see the power of MAOS:

```bash
# This would take 15 minutes sequentially, but only 3 minutes with MAOS!
maos task create "Process 5 large files" \
  --subtasks "Process file1.txt,Process file2.txt,Process file3.txt,Process file4.txt,Process file5.txt" \
  --strategy parallel \
  --agents 5

# Watch the magic happen
maos task status --follow
```

Congratulations! You're now running true parallel multi-agent orchestration with MAOS! 🚀