# MAOS Quick Start Guide

## 5-Minute Setup

Get MAOS running locally in under 5 minutes with our streamlined setup process.

### Prerequisites

- Docker Desktop or Docker Engine
- 4GB+ available RAM
- Internet connection for initial setup

### Option 1: One-Command Setup (Recommended)

```bash
# Download and run the quick setup script
curl -fsSL https://get.maos.dev/quickstart | bash
```

This script will:
1. Download the latest MAOS release
2. Configure local environment with sensible defaults
3. Start all services with Docker Compose
4. Run health checks
5. Display access URLs and next steps

**Expected output:**
```
✅ MAOS Quick Start Complete!
🚀 Services are running at:
   • Web Dashboard: http://localhost:3001
   • API Endpoint: http://localhost:8000
   • Monitoring: http://localhost:3000 (admin/admin)

💡 Next Steps:
   1. Open the dashboard: http://localhost:3001
   2. Run your first task: maos task submit "Hello MAOS"
   3. Check the getting started guide: docs/user-guides/getting-started.md
```

### Option 2: Manual Setup

#### Step 1: Download MAOS

```bash
# Create project directory
mkdir maos-quickstart && cd maos-quickstart

# Download quick start configuration
curl -O https://raw.githubusercontent.com/maos-team/maos/main/docker-compose.quickstart.yml
curl -O https://raw.githubusercontent.com/maos-team/maos/main/.env.quickstart

# Rename files
mv docker-compose.quickstart.yml docker-compose.yml
mv .env.quickstart .env
```

#### Step 2: Configure Environment

```bash
# Generate JWT secret
export JWT_SECRET=$(openssl rand -hex 32)
echo "JWT_SECRET=${JWT_SECRET}" >> .env

# Set Claude API key (required for agent functionality)
read -p "Enter your Claude API key: " CLAUDE_API_KEY
echo "CLAUDE_API_KEY=${CLAUDE_API_KEY}" >> .env

# Review configuration (optional)
cat .env
```

#### Step 3: Start Services

```bash
# Start all services
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose exec maos-orchestrator wait-for-it postgres:5432 --timeout=60
docker-compose exec maos-orchestrator wait-for-it redis:6379 --timeout=60

# Run database migrations
docker-compose exec maos-orchestrator maos db migrate

# Verify all services are running
docker-compose ps
```

#### Step 4: Health Check

```bash
# Check system health
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "database": "healthy",
    "redis": "healthy",
    "agents": "healthy"
  }
}
```

## Quick Start Configuration

### Docker Compose Configuration

The quick start uses this optimized `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # MAOS Core Service
  maos-orchestrator:
    image: maos/orchestrator:latest
    container_name: maos-orchestrator
    environment:
      # Basic configuration
      - MAOS_SYSTEM_ENVIRONMENT=development
      - MAOS_SYSTEM_LOG_LEVEL=INFO
      - MAOS_SYSTEM_MAX_AGENTS=5
      
      # Database and Redis
      - MAOS_DATABASE_PRIMARY_URL=postgresql://maos:quickstart@postgres:5432/maos
      - MAOS_REDIS_URL=redis://redis:6379/0
      
      # Security (development mode)
      - MAOS_SECURITY_AUTH_REQUIRE_AUTH=false
      - JWT_SECRET=${JWT_SECRET}
      
      # Claude API
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      
      # Storage
      - MAOS_CHECKPOINTS_STORAGE_BACKEND=local
      - MAOS_CHECKPOINTS_LOCAL_PATH=/app/checkpoints
      
    ports:
      - "8000:8000"
    volumes:
      - ./data/checkpoints:/app/checkpoints
      - ./data/logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: maos-postgres
    environment:
      - POSTGRES_DB=maos
      - POSTGRES_USER=maos
      - POSTGRES_PASSWORD=quickstart
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U maos"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: maos-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Web Dashboard
  maos-dashboard:
    image: maos/dashboard:latest
    container_name: maos-dashboard
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - NODE_ENV=development
    ports:
      - "3001:3000"
    depends_on:
      - maos-orchestrator

  # Monitoring (Optional)
  prometheus:
    image: prom/prometheus:latest
    container_name: maos-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:latest
    container_name: maos-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana/dashboards:/var/lib/grafana/dashboards

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  default:
    name: maos-quickstart
```

### Environment Configuration

The `.env` file contains development-optimized settings:

```bash
# MAOS Quick Start Configuration

# System Settings
MAOS_SYSTEM_ENVIRONMENT=development
MAOS_SYSTEM_LOG_LEVEL=INFO
MAOS_SYSTEM_MAX_AGENTS=5

# Security (Development Mode)
MAOS_SECURITY_AUTH_REQUIRE_AUTH=false
JWT_SECRET=your-generated-secret-here

# Claude API (Required)
CLAUDE_API_KEY=your-claude-api-key-here

# Database
POSTGRES_DB=maos
POSTGRES_USER=maos
POSTGRES_PASSWORD=quickstart

# Features
MAOS_MONITORING_METRICS_ENABLED=true
MAOS_MONITORING_ALERTS_ENABLED=false

# Performance (Optimized for local development)
MAOS_SYSTEM_CHECKPOINT_INTERVAL=60
MAOS_AGENTS_DEFAULTS_TIMEOUT=1800
MAOS_DATABASE_PRIMARY_POOL_SIZE=10
MAOS_REDIS_POOL_MAX_CONNECTIONS=20
```

## First Steps After Setup

### 1. Access the Web Dashboard

Open http://localhost:3001 in your browser to see:
- Real-time system status
- Agent activity
- Task queue and progress
- System metrics

### 2. Submit Your First Task

#### Using the Web Dashboard
1. Navigate to "Tasks" > "New Task"
2. Enter description: "Write a simple Hello World program in Python"
3. Select type: "coding"
4. Click "Submit Task"
5. Watch the progress in real-time

#### Using the CLI
```bash
# Install MAOS CLI (if not using Docker)
pip install maos-cli

# Submit a task
maos task submit "Research the benefits of renewable energy" --type research

# Check task status
maos task list

# View task details
maos task show <task-id>
```

#### Using the API
```bash
# Submit task via API
curl -X POST http://localhost:8000/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Analyze customer feedback data",
    "type": "analysis",
    "priority": "MEDIUM"
  }'
```

### 3. Monitor Agent Activity

```bash
# View active agents
curl http://localhost:8000/v1/agents

# Check system metrics
curl http://localhost:8000/v1/system/metrics
```

### 4. Explore the Monitoring Dashboard

Visit http://localhost:3000 (admin/admin) to see:
- System performance metrics
- Task execution statistics
- Agent utilization graphs
- Resource usage trends

## Quick Configuration Changes

### Increase Agent Capacity

```bash
# Stop services
docker-compose down

# Update configuration
echo "MAOS_SYSTEM_MAX_AGENTS=10" >> .env

# Restart services
docker-compose up -d
```

### Enable Authentication

```bash
# Update environment
sed -i 's/MAOS_SECURITY_AUTH_REQUIRE_AUTH=false/MAOS_SECURITY_AUTH_REQUIRE_AUTH=true/' .env

# Restart services
docker-compose restart maos-orchestrator

# Create user account
docker-compose exec maos-orchestrator maos user create admin --password admin123
```

### Configure External Storage

```bash
# For S3 storage
echo "MAOS_CHECKPOINTS_STORAGE_BACKEND=s3" >> .env
echo "MAOS_CHECKPOINTS_S3_BUCKET=my-maos-checkpoints" >> .env
echo "AWS_ACCESS_KEY_ID=your-key" >> .env
echo "AWS_SECRET_ACCESS_KEY=your-secret" >> .env

docker-compose restart maos-orchestrator
```

## Next Steps

### 1. Explore Advanced Features

- **Multi-Agent Coordination**: Try complex tasks that benefit from parallel processing
- **Custom Agent Types**: Configure specialized agents for specific tasks
- **Workflow Management**: Create multi-step workflows with dependencies

### 2. Production Deployment

When ready for production:
- Review the [Production Deployment Guide](production-deployment.md)
- Set up proper authentication and encryption
- Configure external databases and storage
- Implement monitoring and alerting

### 3. Integration

- **API Integration**: Use the REST API to integrate with existing systems
- **Webhook Setup**: Configure webhooks for task completion notifications
- **SDK Usage**: Use Python or JavaScript SDKs for programmatic access

### 4. Learn More

- [User Guide](../user-guides/getting-started.md) - Comprehensive user documentation
- [API Documentation](../system/api-documentation.md) - Complete API reference
- [Best Practices](../user-guides/best-practices.md) - Optimization and usage guidelines

## Troubleshooting Quick Start

### Common Issues

#### Services Won't Start
```bash
# Check logs
docker-compose logs maos-orchestrator

# Common fixes
docker-compose down && docker system prune -f
docker-compose up -d --force-recreate
```

#### Database Connection Issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
# Wait 30 seconds
docker-compose up -d
```

#### API Not Responding
```bash
# Check service health
docker-compose exec maos-orchestrator curl http://localhost:8000/health

# Restart orchestrator
docker-compose restart maos-orchestrator
```

#### Out of Memory
```bash
# Reduce agent count
echo "MAOS_SYSTEM_MAX_AGENTS=3" >> .env
docker-compose restart maos-orchestrator
```

### Getting Help

If you encounter issues during quick start:

1. **Check the logs**: `docker-compose logs`
2. **Verify system requirements**: Ensure 4GB+ RAM available
3. **Review configuration**: Check `.env` file for typos
4. **Restart services**: `docker-compose restart`
5. **Contact support**: Create an issue at https://github.com/maos-team/maos/issues

## Clean Up

To completely remove the quick start environment:

```bash
# Stop all services
docker-compose down

# Remove volumes (deletes all data)
docker-compose down -v

# Remove images (optional)
docker rmi $(docker images "maos/*" -q)

# Clean up project directory
cd .. && rm -rf maos-quickstart
```

---

**Congratulations!** You now have MAOS running locally. The system is ready to handle your first multi-agent tasks with true parallel execution and automatic state management.

Ready to explore more? Check out the [Getting Started Tutorial](../user-guides/getting-started.md) for detailed usage examples and advanced features.