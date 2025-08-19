# MAOS Complete User Guide

Welcome to the comprehensive user guide for MAOS (Multi-Agent Operating System) - the revolutionary platform that enables true parallel execution of AI agents with shared state management and inter-agent coordination.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Installation](#installation)
4. [Basic Usage](#basic-usage)
5. [Advanced Features](#advanced-features)
6. [Monitoring and Management](#monitoring-and-management)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Introduction

### What is MAOS?

MAOS represents a paradigm shift from traditional "multi-agent" systems that simulate parallel processing. Instead, MAOS provides:

- **True Parallel Execution**: Multiple agents work simultaneously on different parts of complex tasks
- **Shared State Management**: Real-time coordination and data sharing between agents
- **Automatic Checkpointing**: Fault tolerance with automatic state recovery
- **3-5x Performance Gains**: Measurable acceleration for parallelizable workloads
- **Transparent Operation**: Complete visibility into agent activities and coordination

### Key Benefits

- **Faster Task Completion**: Complex tasks complete in parallel rather than sequentially
- **Better Resource Utilization**: Optimal use of computational resources
- **Fault Tolerance**: Automatic recovery from failures
- **Scalability**: Seamlessly scale from single to hundreds of agents
- **Transparency**: Full visibility into what agents are doing and how they coordinate

## Getting Started

### System Requirements

**Minimum Requirements:**
- Python 3.8+
- 4 GB RAM
- 2 CPU cores
- 10 GB available disk space
- Internet connection for Claude API access

**Recommended for Production:**
- Python 3.11+
- 16 GB RAM
- 8 CPU cores
- 100 GB available disk space
- Redis 7.0+
- PostgreSQL 14+

### Quick Start

The fastest way to get started with MAOS:

```bash
# Install MAOS
pip install maos

# Initialize configuration
maos init

# Start the system
maos start

# Submit your first task
maos task submit "Research the top 3 cloud computing trends in 2025"

# Monitor progress
maos monitor --follow
```

## Installation

### Installation Methods

#### 1. pip Installation (Recommended)

```bash
# Install from PyPI
pip install maos

# Install with all optional dependencies
pip install "maos[all]"

# Verify installation
maos version
```

#### 2. Docker Installation

```bash
# Pull the official image
docker pull maos/maos:latest

# Run with Docker Compose
curl -o docker-compose.yml https://raw.githubusercontent.com/maos-team/maos/main/docker-compose.yml
docker-compose up -d

# Verify installation
docker-compose exec maos maos version
```

#### 3. Installation from Source

```bash
# Clone the repository
git clone https://github.com/maos-team/maos.git
cd maos

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests to verify
python -m pytest tests/
```

#### 4. Kubernetes Installation

```bash
# Add MAOS Helm repository
helm repo add maos https://charts.maos.dev
helm repo update

# Install MAOS
helm install maos maos/maos \
  --set redis.enabled=true \
  --set postgresql.enabled=true

# Verify installation
kubectl get pods -l app=maos
```

### Configuration

#### Initial Configuration

```bash
# Initialize configuration directory
maos init

# This creates:
# ~/.maos/config.yml - Main configuration
# ~/.maos/agents/ - Agent configurations
# ~/.maos/logs/ - Log directory
```

#### Essential Configuration

Edit `~/.maos/config.yml`:

```yaml
# System Configuration
system:
  max_agents: 10
  log_level: "INFO"
  
# Database Configuration
database:
  primary_url: "postgresql://username:password@localhost:5432/maos"
  
# Redis Configuration  
redis:
  url: "redis://localhost:6379/0"
  
# Claude API Configuration
claude:
  api_key: "${CLAUDE_API_KEY}"
  model: "claude-3-sonnet-20240229"
  
# Agent Defaults
agents:
  defaults:
    max_memory: "1GB"
    timeout: 3600
```

#### Environment Variables

```bash
# Essential environment variables
export CLAUDE_API_KEY="your-claude-api-key"
export MAOS_DATABASE_PRIMARY_URL="postgresql://username:password@host:5432/maos"
export MAOS_REDIS_URL="redis://localhost:6379/0"

# Optional configuration overrides
export MAOS_SYSTEM_MAX_AGENTS="20"
export MAOS_SYSTEM_LOG_LEVEL="DEBUG"
```

### Database Setup

#### PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres createuser --interactive maos
sudo -u postgres createdb maos -O maos

# Run migrations
maos db migrate
```

#### Redis Setup

```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test connection
redis-cli ping
```

### Verification

```bash
# Check system health
maos health

# Verify components
maos status --detailed

# Test with a simple task
maos task submit "What is 2+2?"
```

## Basic Usage

### Command Line Interface

The MAOS CLI is your primary interface for interacting with the system.

#### Core Commands

```bash
# System Management
maos start           # Start MAOS services
maos stop            # Stop MAOS services  
maos restart         # Restart MAOS services
maos status          # Show system status
maos health          # Run health checks

# Task Management
maos task submit "description"     # Submit a new task
maos task list                     # List all tasks
maos task show <task_id>          # Show task details
maos task cancel <task_id>        # Cancel a task
maos task results <task_id>       # Show task results

# Agent Management
maos agent list                   # List all agents
maos agent spawn <type>           # Spawn a new agent
maos agent kill <agent_id>        # Terminate an agent
maos agent status <agent_id>      # Show agent status

# Monitoring
maos monitor                      # Live system monitor
maos logs                         # View system logs
maos metrics                      # Show performance metrics
```

### Creating and Managing Tasks

#### Basic Task Submission

```bash
# Simple task
maos task submit "Summarize the key benefits of renewable energy"

# Task with specific type
maos task submit "Create a Python REST API for user management" --type coding

# Task with constraints
maos task submit "Analyze customer data trends" --max-agents 5 --priority HIGH

# Task with dependencies
maos task submit "Design database schema" --depends-on task_abc123
```

#### Task Types

MAOS optimizes agent selection based on task type:

```bash
# Research tasks - uses researcher agents
maos task submit "Research competitor analysis for SaaS platforms" --type research

# Coding tasks - uses coder agents  
maos task submit "Implement OAuth2 authentication" --type coding

# Analysis tasks - uses analyst agents
maos task submit "Analyze quarterly sales performance" --type analysis

# Mixed tasks - uses coordinator and specialized agents
maos task submit "Build and deploy a web application" --type mixed
```

#### Task Parameters

```bash
# Maximum agents to use
--max-agents 8

# Task priority (LOW, NORMAL, HIGH, CRITICAL)
--priority HIGH

# Task timeout in seconds
--timeout 7200

# Require consensus for decisions
--require-consensus

# Task context and constraints
--context "This is for a healthcare application"
--constraints "Must follow HIPAA compliance"
```

### Working with Agents

#### Agent Types

| Type | Capabilities | Use Cases |
|------|-------------|-----------|
| **researcher** | web_search, data_analysis, synthesis | Market research, competitive analysis |
| **coder** | programming, testing, debugging | Software development, automation |
| **analyst** | data_analysis, visualization, statistics | Data processing, insights |
| **tester** | test_generation, validation, qa | Quality assurance, testing |
| **coordinator** | orchestration, consensus, planning | Complex workflows, coordination |

#### Manual Agent Management

```bash
# Spawn specific agent types
maos agent spawn researcher
maos agent spawn coder --capabilities "python,fastapi,postgresql"
maos agent spawn analyst --capabilities "pandas,matplotlib,statistics"

# List agents with details
maos agent list --details
maos agent list --status IDLE
maos agent list --type researcher

# Agent performance
maos agent metrics agent_researcher_001
maos agent logs agent_researcher_001

# Agent lifecycle
maos agent pause agent_researcher_001
maos agent resume agent_researcher_001  
maos agent restart agent_researcher_001
maos agent terminate agent_researcher_001
```

### Checkpoints and Recovery

#### Automatic Checkpointing

MAOS automatically creates checkpoints during task execution:

```bash
# View available checkpoints
maos checkpoint list

# Checkpoint details
maos checkpoint show checkpoint_20250811_103000

# Manual checkpoint creation
maos checkpoint create --description "Before major changes"
```

#### Recovery Operations

```bash
# Recover from latest checkpoint
maos recover

# Recover from specific checkpoint
maos recover --checkpoint checkpoint_20250811_103000

# Recover specific components
maos recover --component task_manager
maos recover --component agent_pool

# Recovery with verification
maos recover --verify --checkpoint latest
```

### Monitoring System Status

#### Real-time Monitoring

```bash
# Live system monitor
maos monitor

# Monitor specific metrics
maos monitor --metric cpu,memory,tasks

# Monitor with custom intervals
maos monitor --interval 5s --duration 5m

# Export monitoring data
maos monitor --export csv --output system_metrics.csv
```

#### System Status

```bash
# Overall system status
maos status

# Detailed component status
maos status --detailed

# Resource usage
maos status --resources

# Performance metrics
maos status --performance
```

#### Logging

```bash
# View recent logs
maos logs

# Follow logs in real-time
maos logs --follow

# Filter by component
maos logs --component orchestrator
maos logs --component agents

# Filter by level
maos logs --level ERROR
maos logs --level WARNING

# Search logs
maos logs --grep "task_abc123"
maos logs --since "1h"
```

## Advanced Features

### Batch Processing

Process multiple related tasks efficiently:

```bash
# Create a batch
maos batch create --name "quarterly-analysis"

# Add tasks to batch
maos batch add-task "quarterly-analysis" "Analyze Q1 sales data"
maos batch add-task "quarterly-analysis" "Analyze Q1 marketing metrics"  
maos batch add-task "quarterly-analysis" "Analyze Q1 customer satisfaction"

# Submit entire batch
maos batch submit "quarterly-analysis"

# Monitor batch progress
maos batch status "quarterly-analysis"
maos batch results "quarterly-analysis"
```

### Workflow Templates

Create reusable workflow patterns:

```bash
# Create template from successful task
maos template create --name "api-development" --from-task task_abc123

# List available templates
maos template list

# Use template
maos task submit-from-template "api-development" \
  --params '{"language": "python", "framework": "fastapi"}'

# Share templates
maos template export "api-development" --output api_template.yml
maos template import api_template.yml
```

### Task Dependencies

Create complex workflows with task dependencies:

```bash
# Linear dependency chain
RESEARCH=$(maos task submit "Research user requirements")
DESIGN=$(maos task submit "Design system architecture" --depends-on $RESEARCH)
IMPLEMENT=$(maos task submit "Implement the system" --depends-on $DESIGN)
TEST=$(maos task submit "Create comprehensive tests" --depends-on $IMPLEMENT)

# Parallel dependencies
DB_DESIGN=$(maos task submit "Design database schema")
API_DESIGN=$(maos task submit "Design API structure")
IMPLEMENTATION=$(maos task submit "Implement system" --depends-on "$DB_DESIGN,$API_DESIGN")
```

### Custom Agent Configuration

Create specialized agents for your domain:

```yaml
# ~/.maos/agents/custom_researcher.yml
name: "domain_researcher"
type: "researcher"
capabilities:
  - "scientific_literature"
  - "patent_research"  
  - "academic_databases"
parameters:
  max_memory: "2GB"
  timeout: 7200
  specialized_tools:
    - "pubmed_search"
    - "arxiv_search"
    - "patent_db_access"
```

```bash
# Spawn custom agent
maos agent spawn domain_researcher

# Use in tasks
maos task submit "Research latest developments in quantum computing" \
  --agent-type domain_researcher
```

### API Integration

Use MAOS programmatically through its REST API:

```python
import requests

# Submit task via API
response = requests.post('http://localhost:8000/api/tasks', json={
    'description': 'Analyze customer satisfaction trends',
    'type': 'analysis',
    'max_agents': 4,
    'priority': 'HIGH'
})

task_id = response.json()['task_id']

# Check task status
status = requests.get(f'http://localhost:8000/api/tasks/{task_id}')
print(status.json())

# Get results
results = requests.get(f'http://localhost:8000/api/tasks/{task_id}/results')
```

### Consensus Mechanisms

For critical decisions requiring agent agreement:

```bash
# Enable consensus for important tasks
maos task submit "Recommend production deployment strategy" \
  --require-consensus \
  --consensus-threshold 0.75

# Configure consensus settings
maos config set consensus.voting_strategy "weighted"
maos config set consensus.timeout 300
```

## Monitoring and Management

### Performance Metrics

```bash
# System performance overview
maos metrics

# Detailed metrics by category
maos metrics --category system
maos metrics --category tasks  
maos metrics --category agents

# Historical metrics
maos metrics --timeframe 24h
maos metrics --timeframe 7d

# Export metrics
maos metrics --export prometheus --output metrics.prom
maos metrics --export json --output metrics.json
```

### Resource Management

```bash
# Resource utilization
maos resources

# Set resource limits
maos config set system.max_memory "8GB"
maos config set system.max_cpu_cores 16

# Monitor resource usage
maos monitor --metric memory,cpu --threshold 90
```

### Health Monitoring

```bash
# Comprehensive health check
maos health --all

# Component-specific health
maos health --component database
maos health --component redis
maos health --component agents

# Automated health monitoring
maos health --continuous --interval 60s
```

### Dashboard

Access the web-based dashboard at `http://localhost:3001`:

**Dashboard Features:**
- Real-time system status
- Task progress monitoring
- Agent pool management
- Performance analytics
- Log viewer
- Configuration management

## Best Practices

### Task Design

1. **Be Specific**: Provide clear, detailed task descriptions
   ```bash
   # Good
   maos task submit "Create a Python FastAPI REST API with JWT authentication, CRUD operations for user management, PostgreSQL database integration, and comprehensive unit tests"
   
   # Less optimal
   maos task submit "Make a web API"
   ```

2. **Use Appropriate Task Types**: Help MAOS optimize agent selection
3. **Set Reasonable Constraints**: Balance performance with resource usage
4. **Break Down Complex Tasks**: Use dependencies for multi-stage workflows

### Performance Optimization

1. **Right-size Agent Limits**:
   ```bash
   # For highly parallelizable tasks
   --max-agents 8
   
   # For sequential tasks
   --max-agents 2
   ```

2. **Use Task Priorities Wisely**:
   ```bash
   --priority CRITICAL  # Only for urgent business needs
   --priority HIGH      # Important but not urgent
   --priority NORMAL    # Default priority
   --priority LOW       # Background tasks
   ```

3. **Monitor Resource Usage**: Regular monitoring prevents resource exhaustion

### Security Best Practices

1. **Secure API Keys**: Never hardcode API keys
   ```bash
   export CLAUDE_API_KEY="sk-..."
   ```

2. **Network Security**: Use firewalls and secure connections
3. **Access Control**: Implement proper authentication and authorization
4. **Regular Updates**: Keep MAOS and dependencies updated

### Operational Best Practices

1. **Regular Backups**: Backup configuration and checkpoints
2. **Monitoring**: Set up comprehensive monitoring and alerting
3. **Capacity Planning**: Plan for growth and peak usage
4. **Documentation**: Document your workflows and configurations

## Troubleshooting

### Common Issues

#### Task Not Starting

**Symptoms**: Tasks stuck in QUEUED status

**Solutions**:
```bash
# Check agent availability
maos agent list --status IDLE

# Check system resources
maos status --resources

# Increase agent limit
maos config set system.max_agents 15
```

#### Poor Performance

**Symptoms**: Tasks taking longer than expected

**Solutions**:
```bash
# Analyze task performance
maos task analyze task_abc123

# Check parallelization
maos task show task_abc123 --execution-plan

# Optimize agent allocation
maos task update task_abc123 --max-agents 6
```

#### Memory Issues

**Symptoms**: Out of memory errors

**Solutions**:
```bash
# Check memory usage
maos status --memory

# Reduce agent memory limits
maos config set agents.defaults.max_memory "512MB"

# Enable memory cleanup
maos config set system.memory_cleanup true
```

#### Network Connectivity

**Symptoms**: API connection failures

**Solutions**:
```bash
# Test connectivity
ping api.anthropic.com

# Check proxy settings
echo $HTTP_PROXY $HTTPS_PROXY

# Test API access
curl -H "Authorization: Bearer $CLAUDE_API_KEY" \
     https://api.anthropic.com/v1/messages
```

### Getting Help

- **Documentation**: https://docs.maos.dev
- **Community Forum**: https://community.maos.dev  
- **GitHub Issues**: https://github.com/maos-team/maos/issues
- **Support**: support@maos.dev

### Support Information

When requesting support, include:
1. MAOS version (`maos version`)
2. System information (`maos status --system`)
3. Error messages and logs
4. Steps to reproduce the issue
5. Expected vs actual behavior

---

This comprehensive user guide covers everything you need to know to effectively use MAOS. Start with the basic usage examples and gradually explore the advanced features as your needs grow. Remember that MAOS is designed to make complex, multi-step tasks faster and more reliable through true parallel agent coordination.