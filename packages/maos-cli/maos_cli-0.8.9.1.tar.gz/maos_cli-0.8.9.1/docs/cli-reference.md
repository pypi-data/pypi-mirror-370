# MAOS CLI Reference Guide

Comprehensive command-line interface for the Multi-Agent Orchestration System (MAOS) with advanced features for task management, agent coordination, system monitoring, and recovery operations.

## Table of Contents

- [Installation and Setup](#installation-and-setup)
- [Quick Start](#quick-start)
- [Command Overview](#command-overview)
- [Core Commands](#core-commands)
- [Task Management](#task-management)
- [Agent Management](#agent-management)
- [System Monitoring](#system-monitoring)
- [Recovery Operations](#recovery-operations)
- [Configuration Management](#configuration-management)
- [Advanced Features](#advanced-features)
- [Interactive Shell](#interactive-shell)
- [Output Formats](#output-formats)
- [Shell Completion](#shell-completion)
- [Examples](#examples)

## Installation and Setup

### Prerequisites

- Python 3.11+
- Rich terminal support (for best experience)
- Optional: Redis (for distributed deployments)

### Installation

```bash
# Install MAOS with CLI
pip install maos

# Or install from source
git clone https://github.com/maos-team/maos.git
cd maos
pip install -e .
```

### Initial Setup

```bash
# Initialize configuration
maos config init

# Validate setup
maos config validate

# Setup shell completion (optional)
maos config completion --install --shell bash
```

## Quick Start

```bash
# Start MAOS system
maos start

# Check system status
maos status overview

# Submit a task
maos task submit "My First Task" --priority high

# List tasks
maos task list

# Create an agent
maos agent create worker --capability data_processing

# Monitor system
maos status monitor
```

## Command Overview

```
maos [OPTIONS] COMMAND [ARGS]...
```

### Global Options

- `--config, -c`: Configuration file path
- `--verbose, -v`: Enable verbose output
- `--quiet, -q`: Suppress non-essential output
- `--format, -f`: Output format (table, json, yaml, tree)
- `--help, -h`: Show help

### Main Commands

| Command | Description |
|---------|-------------|
| `start` | Start orchestration system |
| `stop` | Stop orchestration system |
| `version` | Show version information |
| `shell` | Start interactive shell |
| `task` | Task management operations |
| `agent` | Agent lifecycle operations |
| `status` | System monitoring and status |
| `recover` | Recovery and checkpoint operations |
| `config` | Configuration management |

## Core Commands

### System Control

#### Start System

```bash
maos start [OPTIONS]
```

**Options:**
- `--max-agents, -a`: Maximum number of agents (default: 10)
- `--storage-dir, -s`: Storage directory path
- `--daemon, -d`: Run as daemon process
- `--monitor/--no-monitor`: Enable real-time monitoring
- `--config, -c`: Configuration file

**Examples:**
```bash
# Basic start
maos start

# Start with custom settings
maos start --max-agents 50 --storage-dir ./data --daemon

# Start with monitoring
maos start --monitor
```

#### Stop System

```bash
maos stop [OPTIONS]
```

**Options:**
- `--force, -f`: Force shutdown without graceful cleanup
- `--timeout, -t`: Shutdown timeout in seconds (default: 30)

**Examples:**
```bash
# Graceful shutdown
maos stop

# Force shutdown
maos stop --force

# Custom timeout
maos stop --timeout 60
```

### Version and Help

```bash
# Show version
maos version

# Show help
maos --help
maos <command> --help
```

## Task Management

### Submit Tasks

```bash
maos task submit TASK_NAME [OPTIONS]
```

**Options:**
- `--description, -d`: Task description
- `--priority, -p`: Priority (low, medium, high, critical)
- `--timeout, -t`: Timeout in seconds
- `--max-retries, -r`: Maximum retries
- `--parameters`: JSON file with task parameters
- `--cpu`: Required CPU cores
- `--memory`: Required memory in MB
- `--disk`: Required disk space in MB
- `--tag`: Task tags (can specify multiple)
- `--strategy`: Decomposition strategy
- `--wait, -w`: Wait for completion
- `--monitor, -m`: Monitor progress in real-time

**Examples:**
```bash
# Simple task
maos task submit "Data Processing"

# High-priority task with resources
maos task submit "ML Training" \
  --priority critical \
  --cpu 4.0 \
  --memory 8192 \
  --timeout 3600

# Task with parameters file
maos task submit "Analysis Job" \
  --parameters ./task-params.json \
  --wait

# Tagged task with monitoring
maos task submit "Report Generation" \
  --tag reporting \
  --tag monthly \
  --monitor
```

### List and Filter Tasks

```bash
maos task list [OPTIONS]
```

**Options:**
- `--status, -s`: Filter by status (pending, running, completed, failed, cancelled)
- `--priority, -p`: Filter by priority
- `--tag, -t`: Filter by tags
- `--limit, -l`: Maximum tasks to show
- `--since`: Show tasks since (e.g., '1h', '1d')
- `--watch, -w`: Watch for updates
- `--format, -f`: Output format

**Examples:**
```bash
# List all tasks
maos task list

# List running tasks
maos task list --status running

# List high-priority tasks from last hour
maos task list --priority high --since 1h

# Watch task updates
maos task list --watch

# Export as JSON
maos task list --format json
```

### Task Status and Results

```bash
# Get task status
maos task status TASK_ID [OPTIONS]

# Get task results
maos task results TASK_ID [OPTIONS]
```

**Options:**
- `--subtasks`: Show subtask details
- `--logs`: Show execution logs
- `--monitor, -m`: Real-time monitoring
- `--save, -s`: Save results to file

**Examples:**
```bash
# Basic status
maos task status abc123def

# Detailed status with logs
maos task status abc123def --subtasks --logs

# Monitor task in real-time
maos task status abc123def --monitor

# Get and save results
maos task results abc123def --save results.json
```

### Task Operations

```bash
# Cancel task
maos task cancel TASK_ID [OPTIONS]

# Retry failed task
maos task retry TASK_ID [OPTIONS]

# Export tasks
maos task export OUTPUT_FILE [OPTIONS]
```

**Examples:**
```bash
# Cancel task
maos task cancel abc123def --reason "No longer needed"

# Retry with confirmation
maos task retry abc123def

# Export tasks to CSV
maos task export tasks.csv --format csv --status completed
```

## Agent Management

### Create Agents

```bash
maos agent create AGENT_TYPE [OPTIONS]
```

**Options:**
- `--capability, -c`: Agent capabilities (can specify multiple)
- `--max-tasks, -m`: Maximum concurrent tasks
- `--cpu-limit`: CPU limit in cores
- `--memory-limit`: Memory limit in MB
- `--config`: Agent configuration file
- `--tag`: Agent tags

**Examples:**
```bash
# Basic agent
maos agent create data_processor

# Specialized agent with capabilities
maos agent create ml_worker \
  --capability data_processing \
  --capability computation \
  --max-tasks 3 \
  --cpu-limit 4.0 \
  --memory-limit 8192

# Agent with configuration
maos agent create api_worker \
  --config ./agent-config.json \
  --tag production
```

### List and Monitor Agents

```bash
maos agent list [OPTIONS]
```

**Options:**
- `--status, -s`: Filter by status
- `--type, -t`: Filter by agent type
- `--capability, -c`: Filter by capabilities
- `--tag`: Filter by tags
- `--detailed, -d`: Show detailed information
- `--watch, -w`: Watch for updates

**Examples:**
```bash
# List all agents
maos agent list

# List available agents with details
maos agent list --status available --detailed

# Find agents with specific capability
maos agent list --capability data_processing

# Watch agent status
maos agent list --watch
```

### Agent Operations

```bash
# Get agent status
maos agent status AGENT_ID [OPTIONS]

# Show agent metrics
maos agent metrics [AGENT_ID] [OPTIONS]

# Terminate agent
maos agent terminate AGENT_ID [OPTIONS]

# Restart agent
maos agent restart AGENT_ID [OPTIONS]
```

**Examples:**
```bash
# Agent status with tasks
maos agent status abc123 --tasks --metrics

# Monitor agent in real-time
maos agent status abc123 --monitor

# Show performance metrics
maos agent metrics --type performance --range 1h

# Gracefully terminate agent
maos agent terminate abc123 --reason "Maintenance"

# Force restart
maos agent restart abc123 --force
```

## System Monitoring

### System Status

```bash
# System overview
maos status overview [OPTIONS]

# Health check
maos status health [OPTIONS]

# System metrics
maos status metrics [OPTIONS]

# System uptime
maos status uptime

# Status summary
maos status summary
```

**Options:**
- `--detailed, -d`: Show detailed information
- `--refresh, -r`: Auto-refresh display
- `--interval, -i`: Refresh interval
- `--component, -c`: Specific component
- `--export, -e`: Export to file

**Examples:**
```bash
# Basic overview
maos status overview

# Detailed health check
maos status health --verbose

# Component-specific metrics
maos status metrics --component orchestrator

# Export metrics
maos status metrics --export metrics.json
```

### Live Monitoring

```bash
maos status monitor [OPTIONS]
```

**Options:**
- `--rate, -r`: Refresh rate in seconds
- `--detailed, -d`: Detailed monitoring view
- `--component, -c`: Monitor specific components

**Examples:**
```bash
# Basic monitoring
maos status monitor

# Detailed monitoring with fast refresh
maos status monitor --detailed --rate 0.5

# Monitor specific components
maos status monitor --component task_planner --component agent_manager
```

## Recovery Operations

### Checkpoint Management

```bash
# Create checkpoint
maos recover checkpoint [NAME] [OPTIONS]

# List checkpoints
maos recover list [OPTIONS]

# Restore from checkpoint
maos recover restore CHECKPOINT_ID [OPTIONS]

# Delete checkpoint
maos recover delete CHECKPOINT_ID [OPTIONS]
```

**Options:**
- `--name, -n`: Checkpoint name
- `--description, -d`: Checkpoint description
- `--include-data/--no-data`: Include runtime data
- `--compress/--no-compress`: Compress checkpoint
- `--force, -f`: Skip confirmations
- `--backup/--no-backup`: Backup before restore
- `--dry-run`: Show what would be done

**Examples:**
```bash
# Create named checkpoint
maos recover checkpoint stable-state \
  --description "Stable system state"

# List recent checkpoints
maos recover list --limit 10 --details

# Safe restore with backup
maos recover restore abc123def --backup

# Force restore without backup
maos recover restore abc123def --force --no-backup

# Dry run restore
maos recover restore abc123def --dry-run
```

### Checkpoint Operations

```bash
# Show checkpoint info
maos recover info CHECKPOINT_ID [OPTIONS]

# Export checkpoint
maos recover export CHECKPOINT_ID OUTPUT_FILE [OPTIONS]

# Cleanup old checkpoints
maos recover cleanup [OPTIONS]
```

**Examples:**
```bash
# Detailed checkpoint info
maos recover info abc123def --content

# Export checkpoint
maos recover export abc123def backup.json --format json

# Cleanup keeping last 5
maos recover cleanup --keep 5

# Cleanup older than 30 days
maos recover cleanup --older-than 30 --dry-run
```

## Configuration Management

### Configuration Commands

```bash
# Show configuration
maos config show [OPTIONS]

# Set configuration value
maos config set KEY VALUE [OPTIONS]

# Initialize configuration
maos config init [OPTIONS]

# Validate configuration
maos config validate [OPTIONS]

# Reset configuration
maos config reset [OPTIONS]
```

**Examples:**
```bash
# Show all configuration
maos config show

# Show specific section
maos config show --section logging

# Show as YAML
maos config show --format yaml

# Set log level
maos config set logging.level DEBUG

# Set max agents
maos config set system.max_agents 50

# Interactive initialization
maos config init --interactive

# Use minimal template
maos config init --template minimal --no-interactive

# Validate and fix issues
maos config validate --fix

# Reset specific section
maos config reset --section logging
```

## Advanced Features

### Output Formats

MAOS CLI supports multiple output formats:

- `table` (default): Rich formatted tables
- `json`: JSON output for programmatic use
- `yaml`: YAML format for configuration
- `tree`: Hierarchical tree view
- `compact`: Compact format for limited space

### Filtering and Search

Most list commands support filtering:

```bash
# Multiple filters
maos task list --status running --priority high --tag production

# Time-based filtering
maos task list --since 2h --limit 20

# Pattern matching
maos agent list --type "*worker*"
```

### Real-time Updates

Many commands support live updates:

```bash
# Watch task list
maos task list --watch

# Monitor system status
maos status overview --refresh

# Live agent monitoring
maos agent list --watch --detailed
```

## Interactive Shell

### Starting the Shell

```bash
maos shell [OPTIONS]
```

### Shell Features

- Command completion
- Command history
- Context variables
- Rich formatting
- Built-in help system

### Shell Commands

```bash
# In shell
maos> help                    # Show help
maos> status                  # System status
maos> tasks                   # List tasks
maos> agents                  # List agents
maos> submit "Task Name"      # Submit task
maos> cancel task-id          # Cancel task
maos> monitor                 # Start monitoring
maos> set task_id abc123      # Set context variable
maos> get                     # Show context
maos> history                 # Command history
maos> exit                    # Exit shell
```

### Context Variables

```bash
# Set context for easier command execution
maos> set task_id abc123def
maos> cancel                  # Uses task_id from context
maos> get task_id            # Show specific variable
maos> clear context          # Clear all variables
```

## Shell Completion

### Setup Completion

```bash
# Auto-detect and install
maos config completion --install

# Specific shell
maos config completion --install --shell bash
maos config completion --install --shell zsh
maos config completion --install --shell fish

# Check status
maos config completion --status

# Generate script
maos config completion --generate --shell bash > completion.sh
```

### Manual Setup

#### Bash
```bash
# Add to ~/.bashrc
eval "$(maos config completion --generate --shell bash)"
```

#### Zsh
```bash
# Add to ~/.zshrc
fpath=(~/.zsh/completions $fpath)
autoload -U compinit && compinit

# Save completion script
maos config completion --generate --shell zsh > ~/.zsh/completions/_maos
```

#### Fish
```bash
# Save to Fish completions directory
maos config completion --generate --shell fish > ~/.config/fish/completions/maos.fish
```

## Examples

### Basic Workflow

```bash
# 1. Start system
maos start

# 2. Submit some tasks
maos task submit "Data Import" --priority high
maos task submit "Data Processing" --cpu 2.0 --memory 4096
maos task submit "Report Generation" --tag monthly

# 3. Create agents
maos agent create processor --capability data_processing --max-tasks 2
maos agent create reporter --capability file_operations

# 4. Monitor progress
maos status overview
maos task list --status running

# 5. Create checkpoint
maos recover checkpoint workflow-complete

# 6. Export results
maos task export completed-tasks.json --status completed
```

### Production Deployment

```bash
# 1. Initialize production config
maos config init --template full --no-interactive

# 2. Configure for production
maos config set logging.level WARNING
maos config set logging.file /var/log/maos.log
maos config set system.max_agents 100
maos config set redis.enabled true
maos config set monitoring.export_metrics true

# 3. Start in daemon mode
maos start --daemon --storage-dir /opt/maos/storage

# 4. Setup monitoring
maos status monitor --detailed > /dev/null 2>&1 &

# 5. Schedule regular checkpoints
maos recover checkpoint production-$(date +%Y%m%d-%H%M%S)
```

### Development Workflow

```bash
# 1. Quick development setup
maos config init --template minimal
maos config set logging.level DEBUG

# 2. Start with monitoring
maos start --max-agents 5 --monitor

# 3. Submit test tasks with monitoring
maos task submit "Test Task 1" --wait
maos task submit "Test Task 2" --monitor

# 4. Interactive debugging
maos shell
```

### Troubleshooting

```bash
# Check system health
maos status health --verbose

# View detailed metrics
maos status metrics --component all --export debug-metrics.json

# List failed tasks
maos task list --status failed --detailed

# Check agent status
maos agent list --status error --detailed

# Restore from last known good state
maos recover list --limit 5
maos recover restore <checkpoint-id> --backup

# Reset configuration if needed
maos config validate --fix
maos config reset --section system --force
```

## Error Handling and Troubleshooting

### Common Issues

1. **System won't start**: Check configuration and permissions
2. **Tasks stuck**: Monitor system resources and agent availability
3. **Agent errors**: Check agent logs and resource limits
4. **Configuration errors**: Use `maos config validate --fix`
5. **Performance issues**: Monitor with `maos status monitor --detailed`

### Debug Commands

```bash
# Verbose output
maos --verbose status overview

# Export debug information
maos status metrics --export debug-info.json
maos config show --format json > config-dump.json
maos task list --format json > tasks-dump.json

# Check logs
maos status health --verbose
```

### Getting Help

```bash
# General help
maos --help

# Command-specific help
maos task --help
maos task submit --help

# Interactive help
maos shell
maos> help submit

# Configuration help
maos config show --examples
```

## Best Practices

### Performance

1. **Use appropriate agent limits**: Don't create too many agents
2. **Monitor resource usage**: Use `maos status monitor`
3. **Regular checkpoints**: Create checkpoints before major changes
4. **Cleanup old data**: Use `maos recover cleanup` regularly

### Security

1. **Secure configuration files**: Protect `.maos.yml` files
2. **Use environment variables**: For sensitive configuration
3. **Regular updates**: Keep MAOS updated
4. **Monitor access**: Use logging and monitoring

### Operations

1. **Automation**: Use scripts for repetitive tasks
2. **Monitoring**: Set up continuous monitoring
3. **Backups**: Regular checkpoint creation
4. **Documentation**: Document your workflows

## Integration Examples

### CI/CD Integration

```bash
#!/bin/bash
# CI/CD pipeline integration

# Start MAOS
maos start --daemon

# Submit build task
TASK_ID=$(maos task submit "Build Pipeline" \
  --format json | jq -r '.task.id')

# Wait for completion
maos task status $TASK_ID --wait

# Check result
if maos task results $TASK_ID --format json | jq -r '.status' == 'completed'; then
    echo "Build successful"
    exit 0
else
    echo "Build failed"
    exit 1
fi
```

### Monitoring Script

```bash
#!/bin/bash
# System monitoring script

while true; do
    # Check system health
    if ! maos status health --quiet; then
        echo "ALERT: MAOS system unhealthy" >&2
        maos status health --verbose
    fi
    
    # Export metrics
    maos status metrics --export metrics-$(date +%s).json
    
    sleep 300  # Check every 5 minutes
done
```

This comprehensive CLI provides all the tools needed for effective MAOS system management, from development to production deployment.
