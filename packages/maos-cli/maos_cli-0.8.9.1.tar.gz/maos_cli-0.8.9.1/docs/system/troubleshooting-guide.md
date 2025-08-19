# MAOS Troubleshooting Guide

## Quick Diagnostic Commands

### System Health Check
```bash
# Basic health check
maos health

# Detailed system status
maos status --detailed

# Component-specific checks
maos health --component database
maos health --component redis
maos health --component agents
```

### Log Analysis
```bash
# View recent logs
maos logs --tail 100

# Filter by component
maos logs --component orchestrator
maos logs --component agents

# Follow logs in real-time
maos logs --follow
```

## Common Issues and Solutions

### 1. System Startup Issues

#### Issue: MAOS Fails to Start

**Symptoms:**
- Service exits immediately after startup
- "Configuration error" messages
- Database connection failures

**Diagnostic Steps:**
```bash
# Check configuration syntax
maos config validate

# Test database connectivity
psql "${MAOS_DATABASE_PRIMARY_URL}"

# Test Redis connectivity
redis-cli -u "${MAOS_REDIS_URL}" ping

# Check log files for specific errors
tail -n 50 /var/log/maos/maos.log
```

**Common Solutions:**

1. **Invalid Configuration**
   ```bash
   # Fix YAML syntax errors
   yamllint config/maos.yml
   
   # Use environment variable override
   export MAOS_SYSTEM_LOG_LEVEL="DEBUG"
   maos start
   ```

2. **Database Connection Issues**
   ```bash
   # Update connection string
   export MAOS_DATABASE_PRIMARY_URL="postgresql://user:pass@host:5432/db"
   
   # Check database exists
   createdb maos
   
   # Run database migrations
   maos db migrate
   ```

3. **Redis Connection Issues**
   ```bash
   # Start Redis if not running
   redis-server
   
   # Update Redis URL
   export MAOS_REDIS_URL="redis://localhost:6379/0"
   ```

#### Issue: Permission Denied Errors

**Symptoms:**
- Cannot create log files
- Cannot access configuration files
- Cannot write checkpoints

**Solutions:**
```bash
# Fix log directory permissions
sudo mkdir -p /var/log/maos
sudo chown $(whoami):$(whoami) /var/log/maos

# Fix checkpoint directory permissions
sudo mkdir -p /var/lib/maos/checkpoints
sudo chown $(whoami):$(whoami) /var/lib/maos/checkpoints

# Fix configuration file permissions
chmod 644 config/maos.yml
```

### 2. Agent Management Issues

#### Issue: Agents Not Spawning

**Symptoms:**
- Tasks remain in QUEUED status
- "No available agents" errors
- Agent spawn timeouts

**Diagnostic Steps:**
```bash
# Check agent status
maos agent list

# Check system resources
maos status --resources

# Check agent spawn logs
maos logs --component agent_manager --filter "spawn"
```

**Solutions:**

1. **Resource Limits Exceeded**
   ```bash
   # Check current resource usage
   maos status --resources
   
   # Increase limits in configuration
   export MAOS_SYSTEM_MAX_AGENTS=30
   export MAOS_AGENTS_DEFAULTS_MAX_MEMORY="1GB"
   
   # Restart MAOS
   maos restart
   ```

2. **Claude API Issues**
   ```bash
   # Check API key
   echo $CLAUDE_API_KEY | head -c 20
   
   # Test API connectivity
   curl -H "Authorization: Bearer $CLAUDE_API_KEY" \
        https://api.anthropic.com/v1/messages
   
   # Check rate limits
   maos logs --filter "rate_limit"
   ```

3. **Network Connectivity Issues**
   ```bash
   # Test internet connectivity
   ping api.anthropic.com
   
   # Check proxy settings
   echo $HTTP_PROXY $HTTPS_PROXY
   
   # Test with curl
   curl -I https://api.anthropic.com
   ```

#### Issue: Agents Failing or Crashing

**Symptoms:**
- Tasks fail with agent errors
- Agents disappear from agent list
- Frequent agent restarts

**Diagnostic Steps:**
```bash
# Check failed agents
maos agent list --status FAILED

# View agent-specific logs
maos logs --agent agent_researcher_001

# Check system resource usage
top -p $(pgrep -f "maos-agent")
```

**Solutions:**

1. **Memory Issues**
   ```bash
   # Increase agent memory limit
   export MAOS_AGENTS_DEFAULTS_MAX_MEMORY="2GB"
   
   # Monitor memory usage
   maos agent metrics --metric memory
   
   # Restart affected agents
   maos agent restart agent_researcher_001
   ```

2. **Task Timeout Issues**
   ```bash
   # Increase task timeout
   export MAOS_AGENTS_DEFAULTS_TIMEOUT=3600
   
   # Check long-running tasks
   maos task list --status RUNNING --sort duration
   
   # Kill stuck tasks
   maos task cancel task_abc123
   ```

### 3. Task Execution Issues

#### Issue: Tasks Stuck in QUEUED Status

**Symptoms:**
- Tasks never start execution
- Queue depth continues growing
- No agent assignment

**Diagnostic Steps:**
```bash
# Check task queue
maos task list --status QUEUED

# Check agent availability
maos agent list --status IDLE

# Check task planner logs
maos logs --component task_planner
```

**Solutions:**

1. **Insufficient Available Agents**
   ```bash
   # Spawn additional agents
   maos agent spawn researcher --count 3
   
   # Increase max agents
   export MAOS_SYSTEM_MAX_AGENTS=25
   maos restart
   ```

2. **Task Planning Issues**
   ```bash
   # Check task dependencies
   maos task show task_abc123 --dependencies
   
   # Force task execution
   maos task execute task_abc123 --force
   
   # Reset task planner
   maos component restart task_planner
   ```

#### Issue: Tasks Failing with Errors

**Symptoms:**
- High task failure rate
- Consistent error patterns
- Timeout failures

**Diagnostic Steps:**
```bash
# Check failure patterns
maos task list --status FAILED --limit 20

# Analyze error messages
maos task show task_abc123 --error-details

# Check agent performance
maos agent metrics --metric success_rate
```

**Solutions:**

1. **Timeout Issues**
   ```bash
   # Increase task timeout
   maos task update task_abc123 --timeout 7200
   
   # Check task complexity
   maos task analyze task_abc123
   ```

2. **Agent Capability Mismatches**
   ```bash
   # Check task requirements vs agent capabilities
   maos task show task_abc123 --requirements
   maos agent list --capabilities
   
   # Spawn specialized agents
   maos agent spawn coder --capabilities "python,testing,debugging"
   ```

### 4. Performance Issues

#### Issue: Slow Task Execution

**Symptoms:**
- Tasks taking much longer than expected
- Poor parallelization
- High system resource usage

**Diagnostic Steps:**
```bash
# Check system performance
maos status --performance

# Analyze task execution times
maos task metrics --metric completion_time

# Check agent utilization
maos agent metrics --metric utilization
```

**Solutions:**

1. **Improve Parallelization**
   ```bash
   # Increase max agents per task
   export MAOS_TASKS_DEFAULTS_MAX_AGENTS=8
   
   # Enable better task decomposition
   export MAOS_TASK_PLANNER_PARALLELIZATION_AGGRESSIVE=true
   ```

2. **Resource Optimization**
   ```bash
   # Optimize Redis settings
   redis-cli config set maxmemory 2gb
   redis-cli config set maxmemory-policy allkeys-lru
   
   # Optimize database connections
   export MAOS_DATABASE_PRIMARY_POOL_SIZE=30
   ```

#### Issue: High Memory Usage

**Symptoms:**
- System running out of memory
- Frequent garbage collection
- Agent terminations due to memory

**Diagnostic Steps:**
```bash
# Check memory usage breakdown
maos status --memory

# Monitor memory over time
maos monitor --metric memory --duration 5m

# Check for memory leaks
maos diagnostics --memory-profile
```

**Solutions:**

1. **Reduce Agent Memory Limits**
   ```bash
   # Lower per-agent memory limit
   export MAOS_AGENTS_DEFAULTS_MAX_MEMORY="256MB"
   
   # Reduce number of concurrent agents
   export MAOS_SYSTEM_MAX_AGENTS=10
   ```

2. **Enable Memory Optimization**
   ```bash
   # Enable checkpoint compression
   export MAOS_CHECKPOINTS_COMPRESSION_ENABLED=true
   export MAOS_CHECKPOINTS_COMPRESSION_LEVEL=9
   
   # Enable shared memory cleanup
   export MAOS_REDIS_SHARED_STATE_DEFAULT_TTL=3600
   ```

### 5. Data and State Issues

#### Issue: Checkpoint Failures

**Symptoms:**
- Checkpoints not being created
- Checkpoint corruption
- Recovery failures

**Diagnostic Steps:**
```bash
# Check checkpoint status
maos checkpoint list

# Test checkpoint creation
maos checkpoint create --manual

# Validate existing checkpoints
maos checkpoint validate --all
```

**Solutions:**

1. **Storage Issues**
   ```bash
   # Check storage space
   df -h /var/lib/maos/checkpoints
   
   # Test S3 connectivity (if using S3)
   aws s3 ls s3://maos-checkpoints/
   
   # Fix permissions
   chmod 755 /var/lib/maos/checkpoints
   ```

2. **Corruption Issues**
   ```bash
   # Clean corrupted checkpoints
   maos checkpoint clean --corrupted
   
   # Restore from last good checkpoint
   maos recover --checkpoint checkpoint_20250811_103000
   ```

#### Issue: Shared State Inconsistencies

**Symptoms:**
- Agents seeing stale data
- Conflicting updates
- Data synchronization issues

**Diagnostic Steps:**
```bash
# Check Redis connectivity
redis-cli -u "${MAOS_REDIS_URL}" info

# Monitor shared state operations
maos logs --component shared_state --follow

# Check for conflicts
maos state conflicts --show
```

**Solutions:**

1. **Redis Configuration Issues**
   ```bash
   # Increase Redis memory
   redis-cli config set maxmemory 4gb
   
   # Enable AOF persistence
   redis-cli config set appendonly yes
   
   # Check Redis cluster health (if clustered)
   redis-cli cluster nodes
   ```

2. **Synchronization Issues**
   ```bash
   # Force state synchronization
   maos state sync --force
   
   # Clear conflicting state
   maos state clear --pattern "task:abc123:*"
   
   # Restart state manager
   maos component restart state_manager
   ```

### 6. Network and Connectivity Issues

#### Issue: Intermittent Network Failures

**Symptoms:**
- Sporadic connection timeouts
- Failed API calls
- Agent communication errors

**Diagnostic Steps:**
```bash
# Check network connectivity
ping api.anthropic.com
traceroute api.anthropic.com

# Test DNS resolution
nslookup api.anthropic.com

# Check firewall rules
iptables -L | grep -i drop
```

**Solutions:**

1. **DNS Issues**
   ```bash
   # Use alternative DNS servers
   echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
   
   # Clear DNS cache
   sudo systemctl restart systemd-resolved
   ```

2. **Proxy Configuration**
   ```bash
   # Configure proxy settings
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   export NO_PROXY=localhost,127.0.0.1
   ```

#### Issue: SSL/TLS Certificate Errors

**Symptoms:**
- Certificate verification failures
- SSL handshake errors
- HTTPS connection issues

**Solutions:**
```bash
# Update CA certificates
sudo update-ca-certificates

# Bypass SSL verification (temporary)
export PYTHONHTTPSVERIFY=0

# Use custom certificate bundle
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

## Monitoring and Alerting

### Set Up Monitoring Dashboard

```bash
# Start monitoring stack
docker-compose up -d prometheus grafana

# Import MAOS dashboards
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @config/grafana-dashboard.json
```

### Configure Alerts

```yaml
# alertmanager.yml
route:
  group_by: ['alertname']
  receiver: 'maos-alerts'

receivers:
- name: 'maos-alerts'
  webhook_configs:
  - url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    send_resolved: true
```

### Key Metrics to Monitor

| Metric | Alert Threshold | Description |
|--------|----------------|-------------|
| Task failure rate | >10% | High task failure rate |
| Agent spawn failures | >3/minute | Agent creation issues |
| Checkpoint failures | >2/hour | State persistence issues |
| Memory usage | >90% | System resource exhaustion |
| Response latency | >5s P95 | API performance degradation |

## Debug Mode

### Enable Debug Mode

```bash
# Enable debug logging
export MAOS_SYSTEM_LOG_LEVEL="DEBUG"
export MAOS_API_DEBUG="true"

# Enable performance profiling
export MAOS_DEVELOPMENT_PROFILING_ENABLED="true"

# Restart with debug mode
maos restart
```

### Debug Tools

```bash
# Interactive debug session
maos debug --interactive

# Performance profiling
maos profile --duration 60s --output profile.prof

# Memory analysis
maos memory-analysis --agent agent_001

# Database query analysis
maos db analyze-queries --slow-queries
```

## Recovery Procedures

### Complete System Recovery

```bash
# 1. Stop MAOS services
maos stop

# 2. Backup current state
cp -r /var/lib/maos/checkpoints /backup/checkpoints-$(date +%Y%m%d)

# 3. Recover from last checkpoint
maos recover --checkpoint latest --force

# 4. Start services
maos start

# 5. Verify system health
maos health --all-components
```

### Partial Recovery

```bash
# Recover specific components
maos component recover agent_manager
maos component recover task_planner

# Recover specific agents
maos agent recover agent_researcher_001 --from-checkpoint

# Recover failed tasks
maos task recover --status FAILED --retry
```

## Performance Tuning

### Database Optimization

```sql
-- PostgreSQL optimization queries
ANALYZE;
REINDEX DATABASE maos;

-- Check for missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats 
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;
```

### Redis Optimization

```bash
# Redis performance tuning
redis-cli config set save "900 1 300 10 60 10000"
redis-cli config set maxmemory-policy allkeys-lru
redis-cli config set tcp-keepalive 60
```

### System-Level Optimization

```bash
# Increase file descriptor limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize kernel parameters
echo "net.core.somaxconn = 65536" >> /etc/sysctl.conf
echo "vm.overcommit_memory = 1" >> /etc/sysctl.conf
sysctl -p
```

## Getting Help

### Log Collection for Support

```bash
# Collect comprehensive logs
maos support collect-logs --output maos-logs.tar.gz

# Include system information
maos support system-info --output system-info.txt

# Generate support bundle
maos support bundle --output maos-support.tar.gz
```

### Support Channels

- **Documentation**: https://docs.maos.dev
- **GitHub Issues**: https://github.com/maos-team/maos/issues
- **Community Forum**: https://community.maos.dev
- **Email Support**: support@maos.dev
- **Emergency Support**: emergency@maos.dev (Enterprise only)

### Information to Include in Support Requests

1. **System Information**
   - MAOS version (`maos version`)
   - Operating system and version
   - Hardware specifications
   - Deployment method (Docker, K8s, bare metal)

2. **Configuration**
   - Sanitized configuration file
   - Environment variables (remove secrets)
   - Recent configuration changes

3. **Error Details**
   - Complete error messages
   - Relevant log entries
   - Steps to reproduce
   - Expected vs actual behavior

4. **Performance Data**
   - System metrics during issue
   - Task execution times
   - Resource utilization graphs

By following this troubleshooting guide, you should be able to resolve most common MAOS issues. For persistent problems, don't hesitate to reach out to our support team with the collected information.