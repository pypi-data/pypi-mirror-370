# MAOS Troubleshooting Guide

This comprehensive guide helps you diagnose and resolve common issues when working with the Multi-Agent Operating System (MAOS).

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation Issues](#installation-issues)
3. [Task Execution Problems](#task-execution-problems)
4. [Agent Issues](#agent-issues)
5. [Performance Problems](#performance-problems)
6. [Network and Connectivity](#network-and-connectivity)
7. [Redis and State Management](#redis-and-state-management)
8. [Checkpoint and Recovery Issues](#checkpoint-and-recovery-issues)
9. [Dashboard and UI Problems](#dashboard-and-ui-problems)
10. [Error Messages Reference](#error-messages-reference)
11. [Advanced Debugging](#advanced-debugging)
12. [Getting Help](#getting-help)

## Quick Diagnostics

### System Health Check

Start with a comprehensive system check:

```bash
# Quick health overview
maos health --all-components

# Detailed system status
maos status --verbose

# Check configuration
maos config validate

# Verify dependencies
maos doctor
```

### Common Quick Fixes

**MAOS not responding:**
```bash
# Restart MAOS services
sudo systemctl restart maos
# or
maos restart --all-services

# Check if processes are running
ps aux | grep maos
```

**Dashboard not accessible:**
```bash
# Restart dashboard
maos dashboard restart --port 3001

# Check if port is in use
netstat -tlnp | grep :3001
```

## Installation Issues

### Python Installation Problems

**Error: `maos` command not found**

```bash
# Check if MAOS is installed
pip list | grep maos

# If not installed, install with:
pip install maos

# Check Python PATH
echo $PATH | grep -o '[^:]*python[^:]*'

# Add to PATH if needed
export PATH=$PATH:~/.local/bin
```

**Permission errors during installation:**

```bash
# Install with user permissions
pip install --user maos

# Or use virtual environment
python -m venv maos-env
source maos-env/bin/activate
pip install maos
```

### Dependencies Issues

**Redis connection failed:**

```bash
# Check Redis status
redis-cli ping

# Install Redis if missing
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install redis-server

# macOS:
brew install redis

# CentOS/RHEL:
sudo yum install redis
```

**PostgreSQL connection issues:**

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Install PostgreSQL if missing
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Create database
sudo -u postgres createdb maos
```

## Task Execution Problems

### Tasks Not Starting

**Symptoms**: Tasks remain in QUEUED status

**Diagnosis:**
```bash
# Check agent availability
maos agent list --status IDLE

# Check system resources
maos status --resources

# Verify task queue
maos task list --status QUEUED
```

**Solutions:**
```bash
# Start more agents if none available
maos agent spawn --type researcher --count 2

# Clear stuck tasks
maos task cleanup --stuck-tasks

# Restart task manager
maos service restart task-manager
```

### Tasks Failing Immediately

**Check task errors:**
```bash
# View detailed error information
maos task show $TASK_ID --error-details

# Check logs
maos logs --task $TASK_ID --level ERROR
```

**Common causes:**
- Invalid task description
- Resource constraints
- Agent configuration issues

**Solutions:**
```bash
# Retry with different parameters
maos task retry $TASK_ID --max-agents 2

# Submit with lower resource requirements
maos task submit "task description" --memory-limit 2GB --timeout 3600
```

### Tasks Taking Too Long

**Monitor resource usage:**
```bash
# Check CPU and memory usage
maos monitor --metric cpu,memory --duration 5m

# Identify bottlenecks
maos task analyze $TASK_ID --performance
```

**Optimization steps:**
```bash
# Increase agent count
maos task scale $TASK_ID --agents 5

# Set priority
maos task priority $TASK_ID HIGH

# Enable checkpointing
maos task checkpoint $TASK_ID --enable --interval 300
```

## Agent Issues

### Agents Not Spawning

**Check agent limits:**
```bash
# View current limits
maos config show agent_limits

# Check system capacity
maos capacity --show-limits
```

**Increase limits if needed:**
```bash
maos config set agent_limits.max_total 50
maos config set agent_limits.max_per_type 20
```

### Agent Performance Issues

**Monitor individual agents:**
```bash
# List agents with performance metrics
maos agent list --metrics

# Monitor specific agent
maos agent monitor $AGENT_ID --detailed
```

**Agent optimization:**
```bash
# Restart underperforming agents
maos agent restart $AGENT_ID

# Update agent configuration
maos agent configure $AGENT_ID --memory 4GB --cpu-limit 2
```

### Agent Communication Failures

**Diagnose communication issues:**
```bash
# Test agent connectivity
maos agent ping --all

# Check network configuration
maos network diagnostics

# Monitor inter-agent communication
maos monitor --agent-communication --duration 2m
```

## Performance Problems

### Slow Task Execution

**Performance analysis:**
```bash
# Analyze current performance
maos performance analyze --timeframe 1h

# Identify bottlenecks
maos bottleneck detect --auto

# Get optimization recommendations
maos optimize suggest --apply-best-practices
```

### Memory Issues

**Monitor memory usage:**
```bash
# System memory overview
maos memory --show-usage

# Per-agent memory usage
maos agent list --memory-usage

# Check for memory leaks
maos diagnostics --memory-leaks
```

**Memory optimization:**
```bash
# Clean up cached data
maos cache clear --all

# Adjust memory limits
maos config set memory.max_per_agent "2GB"
maos config set memory.swap_threshold 0.8

# Enable memory monitoring
maos config set monitoring.memory_alerts true
```

### CPU Performance Issues

**CPU monitoring:**
```bash
# Monitor CPU usage
maos monitor --metric cpu --detailed

# Check CPU-intensive agents
maos agent list --sort-by cpu_usage

# Profile task execution
maos task profile $TASK_ID --cpu
```

**CPU optimization:**
```bash
# Adjust CPU limits
maos config set cpu.max_cores_per_agent 2

# Enable CPU affinity
maos config set cpu.affinity_enabled true

# Load balancing
maos balance --cpu-based
```

## Network and Connectivity

### Connection Timeouts

**Network diagnostics:**
```bash
# Test external connectivity
maos network test --external

# Check internal communication
maos network test --internal

# Monitor connection latency
maos monitor --metric network_latency --duration 5m
```

**Network optimization:**
```bash
# Adjust timeout settings
maos config set network.timeout 60
maos config set network.retry_attempts 5

# Enable connection pooling
maos config set network.connection_pooling true
```

### Firewall Issues

**Check required ports:**
```bash
# List required ports
maos network ports --required

# Test port connectivity
maos network test-ports --list 6379,5432,3001,8000
```

**Firewall configuration:**
```bash
# Ubuntu/Debian (UFW):
sudo ufw allow 6379  # Redis
sudo ufw allow 5432  # PostgreSQL
sudo ufw allow 3001  # Dashboard

# CentOS/RHEL (firewalld):
sudo firewall-cmd --permanent --add-port=6379/tcp
sudo firewall-cmd --permanent --add-port=5432/tcp
sudo firewall-cmd --permanent --add-port=3001/tcp
sudo firewall-cmd --reload
```

## Redis and State Management

### Redis Connection Issues

**Diagnose Redis problems:**
```bash
# Test Redis connection
redis-cli ping

# Check Redis configuration
redis-cli config get "*"

# Monitor Redis performance
redis-cli --latency-history
```

**Redis optimization:**
```bash
# Increase memory limit
redis-cli config set maxmemory 2gb

# Set eviction policy
redis-cli config set maxmemory-policy allkeys-lru

# Enable persistence
redis-cli config set save "900 1 300 10 60 10000"
```

### State Synchronization Issues

**Check state consistency:**
```bash
# Verify state integrity
maos state verify --all-agents

# Check for state conflicts
maos state conflicts --detect

# Force state synchronization
maos state sync --force
```

### Shared Memory Issues

**Monitor shared memory:**
```bash
# Check shared memory usage
maos memory shared --usage

# Clean up stale shared memory
maos memory cleanup --shared

# Optimize shared memory settings
maos config set shared_memory.size "1GB"
```

## Checkpoint and Recovery Issues

### Checkpoint Failures

**Diagnose checkpoint issues:**
```bash
# List available checkpoints
maos checkpoint list --task $TASK_ID

# Verify checkpoint integrity
maos checkpoint verify $CHECKPOINT_ID

# Check checkpoint storage
df -h /var/lib/maos/checkpoints/
```

**Checkpoint optimization:**
```bash
# Adjust checkpoint frequency
maos config set checkpointing.interval 600

# Enable compression
maos config set checkpointing.compression true

# Clean old checkpoints
maos checkpoint cleanup --older-than 7d
```

### Recovery Problems

**Recovery diagnostics:**
```bash
# Check recovery status
maos recovery status --task $TASK_ID

# List available recovery points
maos recovery list --task $TASK_ID

# Validate recovery data
maos recovery validate $RECOVERY_POINT_ID
```

**Manual recovery:**
```bash
# Recover from specific checkpoint
maos task recover $TASK_ID --from-checkpoint $CHECKPOINT_ID

# Recover with state reconstruction
maos task recover $TASK_ID --reconstruct-state

# Force recovery (use with caution)
maos task recover $TASK_ID --force --ignore-consistency
```

## Dashboard and UI Problems

### Dashboard Not Loading

**Basic troubleshooting:**
```bash
# Check dashboard status
maos dashboard status

# View dashboard logs
maos logs --service dashboard --tail 50

# Restart dashboard
maos dashboard restart --force
```

**Browser-specific issues:**
- Clear browser cache and cookies
- Disable browser extensions
- Try incognito/private mode
- Check browser console for JavaScript errors

### Dashboard Performance Issues

**Optimize dashboard performance:**
```bash
# Reduce update frequency
maos dashboard config --update-interval 5000

# Limit displayed data
maos dashboard config --max-tasks-shown 100

# Enable data compression
maos dashboard config --compression true
```

### Authentication Issues

**Reset dashboard authentication:**
```bash
# Reset authentication tokens
maos auth reset --dashboard

# Create new access credentials
maos auth create-token --scope dashboard --expires 30d

# Check authentication configuration
maos config show auth.dashboard
```

## Error Messages Reference

### Common Error Codes

**MAOS-001: Agent Spawn Failure**
```
Error: Failed to spawn agent of type 'researcher'
Cause: Resource limits exceeded or agent configuration invalid
Solution: Check resource availability or increase limits
```

**MAOS-002: Task Submission Failed**
```
Error: Task submission rejected
Cause: Invalid task parameters or queue full
Solution: Validate task parameters or wait for queue space
```

**MAOS-003: State Synchronization Error**
```
Error: Failed to synchronize shared state
Cause: Network issues or Redis unavailable
Solution: Check network connectivity and Redis status
```

**MAOS-004: Checkpoint Creation Failed**
```
Error: Unable to create checkpoint
Cause: Insufficient disk space or permission issues
Solution: Free disk space or check file permissions
```

### Database Errors

**PostgreSQL Connection Errors:**
```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Test connection
psql -h localhost -U maos -d maos -c "SELECT 1;"

# Reset connection pool
maos db pool-reset
```

**Redis Errors:**
```bash
# Check Redis memory usage
redis-cli info memory

# Clear Redis if needed (CAUTION: Will lose data)
redis-cli flushall

# Restart Redis
sudo systemctl restart redis
```

## Advanced Debugging

### Debug Mode

**Enable comprehensive debugging:**
```bash
# Start MAOS in debug mode
maos start --debug-level TRACE

# Enable specific debug categories
maos debug enable --categories "agent,task,network"

# Debug specific task
maos task debug $TASK_ID --verbose
```

### Profiling and Tracing

**Performance profiling:**
```bash
# Profile system performance
maos profile --duration 300 --output profile.json

# Trace task execution
maos trace --task $TASK_ID --output trace.log

# Analyze execution patterns
maos analyze --profile profile.json --report performance_report.html
```

### Log Analysis

**Comprehensive log analysis:**
```bash
# Collect all logs
maos logs collect --output maos_logs.tar.gz

# Search logs for errors
maos logs search --pattern "ERROR|FATAL" --last 24h

# Real-time log monitoring
maos logs follow --level DEBUG --filter agent
```

### System Monitoring

**Set up monitoring:**
```bash
# Enable Prometheus metrics
maos config set monitoring.prometheus.enabled true

# Export metrics
maos metrics export --format prometheus --output metrics.prom

# Setup alerts
maos alerts configure --cpu-threshold 80 --memory-threshold 90
```

## Performance Tuning

### System Optimization

**Optimize for throughput:**
```bash
# Increase worker threads
maos config set system.worker_threads 16

# Optimize I/O settings
maos config set system.io_threads 8
maos config set system.async_io true

# Enable batch processing
maos config set processing.batch_size 10
```

**Optimize for latency:**
```bash
# Reduce polling intervals
maos config set polling.task_queue_interval 100
maos config set polling.agent_status_interval 500

# Enable real-time processing
maos config set processing.real_time_mode true
```

### Database Tuning

**PostgreSQL optimization:**
```sql
-- Increase connection limits
ALTER SYSTEM SET max_connections = 200;

-- Optimize memory settings
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';

-- Reload configuration
SELECT pg_reload_conf();
```

**Redis optimization:**
```bash
# Optimize Redis configuration
redis-cli config set maxmemory-policy allkeys-lru
redis-cli config set timeout 0
redis-cli config set tcp-keepalive 60
```

## Getting Help

### Built-in Help System

```bash
# General help
maos help

# Command-specific help
maos task help submit
maos agent help spawn

# Configuration help
maos config help
```

### Diagnostic Information Collection

**Prepare support request:**
```bash
# Generate comprehensive diagnostic report
maos diagnostics report --output support_report.tar.gz

# Include system information
maos system info --detailed > system_info.txt

# Export configuration (sanitized)
maos config export --sanitized > config.yaml
```

### Community Resources

- **Documentation**: https://docs.maos.dev
- **Community Forum**: https://community.maos.dev
- **GitHub Issues**: https://github.com/maos-dev/maos/issues
- **Discord Server**: https://discord.gg/maos
- **Stack Overflow**: Tag questions with `maos`

### Professional Support

For enterprise customers:
- **Technical Support**: support@maos.dev
- **Emergency Hotline**: Available 24/7 for enterprise customers
- **Dedicated Support Portal**: https://enterprise.maos.dev/support

### Reporting Bugs

**Bug report template:**
```markdown
## Bug Report

**MAOS Version**: (output of `maos version`)
**OS/Environment**: 
**Python Version**: 

**Description**: 
Brief description of the issue

**Steps to Reproduce**:
1. 
2. 
3. 

**Expected Behavior**: 
What should have happened

**Actual Behavior**: 
What actually happened

**Logs**: 
(Attach relevant log snippets)

**Configuration**: 
(Include relevant config sections)
```

## Emergency Procedures

### System Recovery

**Complete system failure:**
```bash
# Stop all services
maos stop --all --force

# Reset to default configuration
maos reset --configuration --keep-data

# Restart with minimal configuration
maos start --minimal --safe-mode

# Gradually restore services
maos service start task-manager
maos service start agent-manager
maos service start dashboard
```

### Data Recovery

**Recover from backup:**
```bash
# List available backups
maos backup list --detailed

# Restore from backup
maos restore --backup $BACKUP_ID --confirm

# Verify data integrity after restore
maos verify --all-data
```

### Disaster Recovery

**Emergency contact procedures:**
1. **Immediate**: Stop all non-critical tasks
2. **Assessment**: Document the issue and impact
3. **Communication**: Notify relevant stakeholders
4. **Recovery**: Follow documented recovery procedures
5. **Post-incident**: Conduct review and improve procedures

---

This troubleshooting guide covers the most common issues encountered when working with MAOS. For issues not covered here, please consult the community resources or contact support with detailed diagnostic information.

**Last Updated**: November 2024  
**Version**: 2.0.0