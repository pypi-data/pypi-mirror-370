# MAOS CLI Reference

## Overview

The MAOS Command Line Interface (CLI) provides comprehensive control over the Multi-Agent Orchestration System. This reference covers all commands, options, and usage scenarios.

## Installation

### Install via Package Manager

```bash
# Install from PyPI
pip install maos-cli

# Install from source
git clone https://github.com/maos-team/maos
cd maos
pip install -e .

# Verify installation
maos --version
```

### Auto-completion Setup

```bash
# Bash
eval "$(_MAOS_COMPLETE=bash_source maos)" >> ~/.bashrc

# Zsh  
eval "$(_MAOS_COMPLETE=zsh_source maos)" >> ~/.zshrc

# Fish
_MAOS_COMPLETE=fish_source maos > ~/.config/fish/completions/maos.fish
```

## Global Options

All commands support these global options:

```bash
maos [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]

Global Options:
  --config PATH         Configuration file path (default: ~/.maos/config.yml)
  --api-url URL         MAOS API endpoint (default: http://localhost:8000)
  --api-key KEY         API authentication key
  --output FORMAT       Output format: json, yaml, table, csv (default: table)
  --verbose, -v         Verbose output (can be repeated: -v, -vv, -vvv)
  --quiet, -q           Suppress non-error output
  --help, -h            Show help message
  --version             Show version information
```

## Configuration Management

### `maos config`

Manage MAOS configuration settings.

#### `maos config show`

Display current configuration:

```bash
# Show all configuration
maos config show

# Show specific section
maos config show --section database

# Show in different formats
maos config show --output json
maos config show --output yaml
```

#### `maos config set`

Update configuration values:

```bash
# Set a configuration value
maos config set api.host "0.0.0.0"
maos config set system.max_agents 20

# Set nested values
maos config set database.primary.pool_size 30

# Set from file
maos config set --from-file config/production.yml
```

#### `maos config get`

Retrieve specific configuration values:

```bash
# Get a specific value
maos config get system.max_agents

# Get with default value
maos config get system.unknown_setting --default "default_value"
```

#### `maos config validate`

Validate configuration:

```bash
# Validate current configuration
maos config validate

# Validate specific file
maos config validate --file config/staging.yml

# Detailed validation output
maos config validate --detailed
```

## System Management

### `maos start`

Start the MAOS orchestration system:

```bash
# Start with default configuration
maos start

# Start with custom config
maos start --config /path/to/config.yml

# Start in development mode
maos start --dev --reload

# Start with specific log level
maos start --log-level DEBUG

# Start with custom agent limits
maos start --max-agents 15

Options:
  --config PATH         Configuration file path
  --dev                 Development mode (enables auto-reload)
  --reload              Auto-reload on code changes
  --log-level LEVEL     Log level (DEBUG, INFO, WARNING, ERROR)
  --max-agents N        Maximum number of agents
  --port PORT           API server port (default: 8000)
  --host HOST           API server host (default: 0.0.0.0)
  --workers N           Number of worker processes
  --daemon, -d          Run as daemon
```

### `maos stop`

Stop the MAOS system:

```bash
# Graceful shutdown
maos stop

# Force shutdown
maos stop --force

# Stop with timeout
maos stop --timeout 30

Options:
  --force, -f          Force shutdown without waiting for tasks
  --timeout SECONDS    Maximum wait time for graceful shutdown
```

### `maos restart`

Restart the MAOS system:

```bash
# Restart with current configuration
maos restart

# Restart with new configuration
maos restart --config /path/to/new-config.yml

# Restart in maintenance mode
maos restart --maintenance
```

### `maos status`

Display system status:

```bash
# Basic system status
maos status

# Detailed status with all components
maos status --detailed

# Show only specific components
maos status --components database,redis,agents

# Continuous monitoring
maos status --follow --interval 5

# Resource usage information
maos status --resources

Options:
  --detailed, -d       Show detailed component status
  --components LIST    Comma-separated list of components to check
  --follow, -f         Continuously update status
  --interval SECONDS   Update interval for --follow (default: 5)
  --resources, -r      Include resource usage information
```

### `maos health`

Comprehensive health check:

```bash
# Quick health check
maos health

# All component health checks
maos health --all-components

# Specific component check
maos health --component database

# With performance metrics
maos health --with-metrics

# Export health report
maos health --export health-report.json

Options:
  --all-components     Check all system components
  --component NAME     Check specific component
  --with-metrics       Include performance metrics
  --export PATH        Export health report to file
```

## Task Management

### `maos task`

Core task management commands.

#### `maos task submit`

Submit new tasks:

```bash
# Basic task submission
maos task submit "Research renewable energy trends in 2025"

# Task with specific type
maos task submit "Create a REST API for user management" --type coding

# Task with priority and constraints
maos task submit "Analyze sales data Q4 2024" \
  --type analysis \
  --priority HIGH \
  --max-agents 5 \
  --timeout 3600

# Task with metadata
maos task submit "Market research report" \
  --metadata '{"project": "expansion", "budget": 10000}'

# Task with file attachments
maos task submit "Analyze this dataset" \
  --attach data.csv,schema.json \
  --type analysis

Options:
  --type TYPE          Task type (research, coding, analysis, testing, documentation)
  --priority PRIORITY  Task priority (LOW, MEDIUM, HIGH, CRITICAL)
  --max-agents N       Maximum agents for this task
  --timeout SECONDS    Task timeout in seconds
  --metadata JSON      Task metadata as JSON string
  --attach FILES       Comma-separated list of files to attach
  --require-consensus  Require agent consensus for decisions
  --tags TAGS          Comma-separated list of tags
  --depends-on TASK_ID Task dependency
```

#### `maos task list`

List and filter tasks:

```bash
# List all tasks
maos task list

# Filter by status
maos task list --status RUNNING
maos task list --status QUEUED,RUNNING

# Filter by type
maos task list --type research

# Filter by date range
maos task list --since 2025-01-01 --until 2025-01-31

# Show only recent tasks
maos task list --limit 10 --sort created_at

# Include detailed information
maos task list --detailed

# Export to file
maos task list --export tasks.json --format json

Options:
  --status STATUS      Filter by status (QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED)
  --type TYPE          Filter by task type
  --priority PRIORITY  Filter by priority
  --tags TAGS          Filter by tags
  --since DATE         Tasks created after date (YYYY-MM-DD)
  --until DATE         Tasks created before date (YYYY-MM-DD)
  --limit N            Maximum number of tasks to show
  --offset N           Number of tasks to skip
  --sort FIELD         Sort by field (created_at, priority, status)
  --detailed, -d       Show detailed task information
  --export PATH        Export results to file
```

#### `maos task show`

Display detailed task information:

```bash
# Basic task information
maos task show task_abc123

# Include agent assignments
maos task show task_abc123 --agents

# Include subtask breakdown
maos task show task_abc123 --subtasks

# Include execution timeline
maos task show task_abc123 --timeline

# Include all details
maos task show task_abc123 --all

# Show dependencies
maos task show task_abc123 --dependencies

Options:
  --agents, -a         Include agent assignment information
  --subtasks, -s       Include subtask breakdown
  --timeline, -t       Include execution timeline
  --dependencies, -d   Include task dependencies
  --all                Include all available information
  --format FORMAT      Output format (table, json, yaml)
```

#### `maos task progress`

Monitor task progress:

```bash
# Show current progress
maos task progress task_abc123

# Follow progress in real-time
maos task progress task_abc123 --follow

# Show progress with agent details
maos task progress task_abc123 --agents

# Progress with performance metrics
maos task progress task_abc123 --metrics

Options:
  --follow, -f         Follow progress in real-time
  --agents, -a         Include agent activity
  --metrics, -m        Include performance metrics
  --interval SECONDS   Update interval for --follow (default: 2)
```

#### `maos task cancel`

Cancel running or queued tasks:

```bash
# Cancel a single task
maos task cancel task_abc123

# Cancel multiple tasks
maos task cancel task_abc123,task_def456

# Cancel with reason
maos task cancel task_abc123 --reason "Requirements changed"

# Force cancel (immediate termination)
maos task cancel task_abc123 --force

Options:
  --reason TEXT        Cancellation reason
  --force, -f         Force immediate cancellation
  --no-confirm        Skip confirmation prompt
```

#### `maos task retry`

Retry failed tasks:

```bash
# Retry a failed task
maos task retry task_abc123

# Retry with different configuration
maos task retry task_abc123 --max-agents 8 --timeout 7200

# Retry from specific checkpoint
maos task retry task_abc123 --from-checkpoint checkpoint_xyz

Options:
  --max-agents N       Override max agents setting
  --timeout SECONDS    Override timeout setting
  --priority PRIORITY  Override priority setting
  --from-checkpoint ID Retry from specific checkpoint
```

#### `maos task export`

Export task results:

```bash
# Export as markdown
maos task export task_abc123 --format markdown --output report.md

# Export as JSON
maos task export task_abc123 --format json --output results.json

# Export as PDF
maos task export task_abc123 --format pdf --output final_report.pdf

# Export with artifacts
maos task export task_abc123 --include-artifacts --output task_results.zip

Options:
  --format FORMAT      Export format (markdown, json, pdf, html)
  --output PATH        Output file path
  --include-artifacts  Include generated artifacts
  --template PATH      Custom export template
```

## Agent Management

### `maos agent`

Agent lifecycle and monitoring commands.

#### `maos agent list`

List system agents:

```bash
# List all agents
maos agent list

# Filter by status
maos agent list --status IDLE
maos agent list --status BUSY,FAILED

# Filter by type
maos agent list --type researcher

# Show detailed information
maos agent list --detailed

# Include performance metrics
maos agent list --metrics

Options:
  --status STATUS      Filter by agent status (IDLE, BUSY, FAILED, TERMINATED)
  --type TYPE          Filter by agent type
  --capabilities CAPS  Filter by capabilities
  --detailed, -d       Show detailed agent information
  --metrics, -m        Include performance metrics
  --sort FIELD         Sort by field (id, type, status, created_at)
```

#### `maos agent show`

Display detailed agent information:

```bash
# Basic agent information
maos agent show agent_researcher_001

# Include current task
maos agent show agent_researcher_001 --current-task

# Include performance history
maos agent show agent_researcher_001 --performance

# Include resource usage
maos agent show agent_researcher_001 --resources

# All available information
maos agent show agent_researcher_001 --all

Options:
  --current-task, -t   Show current task assignment
  --performance, -p    Include performance metrics
  --resources, -r      Include resource usage
  --all, -a           Show all available information
```

#### `maos agent spawn`

Create new agents:

```bash
# Spawn a basic agent
maos agent spawn researcher

# Spawn with specific capabilities
maos agent spawn researcher --capabilities "web_search,data_analysis,reporting"

# Spawn multiple agents
maos agent spawn researcher --count 3

# Spawn with custom configuration
maos agent spawn coder --memory 2GB --timeout 3600

# Spawn for specific task
maos agent spawn analyst --for-task task_abc123

Options:
  --capabilities CAPS  Comma-separated list of capabilities
  --count N           Number of agents to spawn
  --memory SIZE       Memory allocation (e.g., 512MB, 2GB)
  --timeout SECONDS   Agent timeout
  --for-task TASK_ID  Spawn specifically for a task
  --priority PRIORITY Agent priority level
```

#### `maos agent terminate`

Terminate agents:

```bash
# Terminate specific agent
maos agent terminate agent_researcher_001

# Terminate multiple agents
maos agent terminate agent_researcher_001,agent_coder_002

# Graceful termination (wait for current task)
maos agent terminate agent_researcher_001 --graceful

# Force termination
maos agent terminate agent_researcher_001 --force

Options:
  --graceful, -g      Wait for current task to complete
  --force, -f         Force immediate termination
  --reason TEXT       Termination reason
  --no-confirm        Skip confirmation prompt
```

#### `maos agent restart`

Restart agents:

```bash
# Restart specific agent
maos agent restart agent_researcher_001

# Restart with new configuration
maos agent restart agent_researcher_001 --memory 4GB

# Restart all agents of a type
maos agent restart --type researcher

Options:
  --memory SIZE       New memory allocation
  --timeout SECONDS   New timeout setting
  --type TYPE         Restart all agents of this type
```

#### `maos agent metrics`

View agent performance metrics:

```bash
# Show metrics for specific agent
maos agent metrics agent_researcher_001

# Show metrics for all agents
maos agent metrics --all

# Show specific metric types
maos agent metrics --metric cpu,memory,tasks

# Show metrics over time period
maos agent metrics --since 1h --until now

# Export metrics
maos agent metrics --export metrics.json

Options:
  --all, -a           Show metrics for all agents
  --metric METRICS    Specific metrics to show
  --since TIME        Start time (1h, 2d, 2025-01-01)
  --until TIME        End time
  --export PATH       Export metrics to file
  --format FORMAT     Export format (json, csv)
```

## Database Management

### `maos db`

Database operations and maintenance.

#### `maos db migrate`

Run database migrations:

```bash
# Run pending migrations
maos db migrate

# Run specific migration
maos db migrate --to 20250115_001_add_task_priorities

# Run migrations with verbose output
maos db migrate --verbose

# Dry run (show what would be executed)
maos db migrate --dry-run

Options:
  --to VERSION        Migrate to specific version
  --verbose, -v       Verbose migration output
  --dry-run          Show migrations without executing
  --force            Force migration even with warnings
```

#### `maos db rollback`

Rollback database migrations:

```bash
# Rollback last migration
maos db rollback

# Rollback to specific version
maos db rollback --to 20250115_001_add_task_priorities

# Rollback multiple versions
maos db rollback --steps 3

Options:
  --to VERSION        Rollback to specific version
  --steps N          Number of migrations to rollback
  --dry-run          Show rollback operations without executing
```

#### `maos db status`

Check database status:

```bash
# Show migration status
maos db status

# Show detailed database information
maos db status --detailed

# Check database connectivity
maos db status --check-connection

Options:
  --detailed, -d      Show detailed database information
  --check-connection  Test database connectivity
```

#### `maos db backup`

Create database backups:

```bash
# Create full backup
maos db backup

# Backup to specific location
maos db backup --output /backups/maos_backup_$(date +%Y%m%d).sql

# Compress backup
maos db backup --compress

# Backup with custom options
maos db backup --exclude-tables logs,temp_data --format custom

Options:
  --output PATH       Backup file path
  --compress, -c      Compress backup file
  --format FORMAT     Backup format (sql, custom, tar)
  --exclude-tables    Tables to exclude from backup
  --schema-only       Backup schema only (no data)
  --data-only         Backup data only (no schema)
```

#### `maos db restore`

Restore from database backup:

```bash
# Restore from backup file
maos db restore /backups/maos_backup.sql

# Restore with confirmation
maos db restore /backups/maos_backup.sql --confirm

# Restore to different database
maos db restore backup.sql --target-db maos_test

Options:
  --confirm           Require confirmation before restore
  --target-db DB      Target database name
  --clean            Drop existing objects before restore
  --no-owner         Skip ownership restoration
```

## Monitoring and Diagnostics

### `maos monitor`

Real-time system monitoring:

```bash
# Monitor system overview
maos monitor

# Monitor specific components
maos monitor --components tasks,agents,performance

# Monitor with custom refresh interval
maos monitor --interval 1

# Monitor specific metrics
maos monitor --metrics cpu,memory,queue_depth

# Monitor and log to file
maos monitor --log monitoring.log

Options:
  --components COMP   Components to monitor
  --interval SECONDS  Refresh interval (default: 5)
  --metrics METRICS   Specific metrics to display
  --log PATH          Log monitoring data to file
  --format FORMAT     Display format (table, json)
  --no-color         Disable colored output
```

### `maos metrics`

System metrics and analytics:

```bash
# Show current metrics
maos metrics

# Show metrics for specific time period
maos metrics --since 1h

# Show specific metric categories
maos metrics --category system,tasks,agents

# Export metrics
maos metrics --export metrics.json --format json

# Generate metrics report
maos metrics --report --output metrics_report.html

Options:
  --since TIME        Start time for metrics
  --until TIME        End time for metrics  
  --category CATS     Metric categories to show
  --export PATH       Export metrics to file
  --format FORMAT     Export format
  --report           Generate HTML report
  --output PATH       Report output file
```

### `maos logs`

Access and analyze system logs:

```bash
# View recent logs
maos logs

# Follow logs in real-time
maos logs --follow

# Filter by component
maos logs --component orchestrator
maos logs --component agents

# Filter by log level
maos logs --level ERROR,WARNING

# Search logs
maos logs --search "task failed"

# Show logs from specific time
maos logs --since "2025-01-15 10:00:00"

# Export logs
maos logs --export debug_logs.txt --since 1h

Options:
  --follow, -f        Follow logs in real-time
  --component COMP    Filter by component
  --level LEVEL       Filter by log level
  --search PATTERN    Search for pattern in logs
  --since TIME        Show logs since time
  --until TIME        Show logs until time
  --tail N           Show last N lines
  --export PATH       Export logs to file
```

### `maos benchmark`

Performance benchmarking:

```bash
# Run standard benchmark suite
maos benchmark

# Run specific benchmark tests
maos benchmark --tests task_processing,agent_spawning

# Run with custom parameters
maos benchmark --concurrent-users 100 --duration 300

# Save benchmark results
maos benchmark --output benchmark_results.json

# Compare with previous results
maos benchmark --compare-with previous_benchmark.json

Options:
  --tests TESTS       Specific tests to run
  --concurrent-users N Number of concurrent users to simulate
  --duration SECONDS  Benchmark duration
  --output PATH       Save results to file
  --compare-with PATH Compare with previous benchmark
  --detailed         Show detailed performance breakdown
```

## Maintenance and Utilities

### `maos checkpoint`

Checkpoint management:

```bash
# List available checkpoints
maos checkpoint list

# Create manual checkpoint
maos checkpoint create --name "before_migration"

# Restore from checkpoint
maos checkpoint restore checkpoint_20250115_103000

# Validate checkpoints
maos checkpoint validate --all

# Clean old checkpoints
maos checkpoint clean --older-than 7d

Options:
  --name NAME         Checkpoint name
  --all              Apply to all checkpoints
  --older-than TIME   Time threshold for cleanup
  --force            Force operation without confirmation
```

### `maos recover`

System recovery operations:

```bash
# Recover from latest checkpoint
maos recover

# Recover from specific checkpoint
maos recover --checkpoint checkpoint_20250115_103000

# Recover specific components
maos recover --components agents,tasks

# Dry run recovery
maos recover --dry-run

Options:
  --checkpoint ID     Specific checkpoint to recover from
  --components COMP   Components to recover
  --dry-run          Show recovery steps without executing
  --force            Force recovery without confirmation
```

### `maos cleanup`

System cleanup operations:

```bash
# Clean up completed tasks older than 30 days
maos cleanup tasks --older-than 30d

# Clean up failed agents
maos cleanup agents --status FAILED

# Clean up temporary files
maos cleanup files --type temp

# Clean up logs older than 7 days
maos cleanup logs --older-than 7d

# Comprehensive cleanup
maos cleanup all --older-than 30d

Options:
  --older-than TIME   Age threshold for cleanup
  --status STATUS     Filter by status
  --type TYPE         Type of cleanup
  --dry-run          Show cleanup actions without executing
  --force            Force cleanup without confirmation
```

## Batch Operations

### `maos batch`

Batch task processing:

#### `maos batch create`

Create task batches:

```bash
# Create a new batch
maos batch create --name "quarterly_reports"

# Create batch with metadata
maos batch create --name "data_analysis_q1" \
  --metadata '{"quarter": "Q1", "year": 2025}'

# Create batch with template
maos batch create --name "weekly_reports" --template report_template
```

#### `maos batch add-task`

Add tasks to batches:

```bash
# Add task to batch
maos batch add-task quarterly_reports "Generate Q1 sales report"

# Add multiple tasks
maos batch add-tasks quarterly_reports tasks.txt

# Add task with specific configuration
maos batch add-task quarterly_reports "Analyze customer data" \
  --type analysis --priority HIGH
```

#### `maos batch submit`

Submit batches for execution:

```bash
# Submit entire batch
maos batch submit quarterly_reports

# Submit with custom scheduling
maos batch submit quarterly_reports --schedule sequential

# Submit with dependencies
maos batch submit quarterly_reports --wait-for other_batch
```

#### `maos batch status`

Monitor batch progress:

```bash
# Show batch status
maos batch status quarterly_reports

# Follow batch progress
maos batch status quarterly_reports --follow

# Show detailed task breakdown
maos batch status quarterly_reports --detailed
```

## Integration and Automation

### `maos webhook`

Webhook management:

```bash
# List configured webhooks
maos webhook list

# Create new webhook
maos webhook create --url "https://api.example.com/maos-webhook" \
  --events "task.completed,task.failed"

# Test webhook
maos webhook test webhook_abc123

# Delete webhook
maos webhook delete webhook_abc123

Options:
  --url URL           Webhook endpoint URL
  --events EVENTS     Comma-separated list of events
  --secret SECRET     Webhook secret for signature validation
  --headers HEADERS   Custom headers as JSON
```

### `maos template`

Task template management:

```bash
# List available templates
maos template list

# Create template from successful task
maos template create --name "api_development" --from-task task_abc123

# Create template from file
maos template create --name "data_analysis" --from-file template.yml

# Use template for new task
maos task submit-from-template "api_development" \
  --params '{"language": "python", "framework": "fastapi"}'

# Update template
maos template update api_development --description "Updated API template"

# Delete template
maos template delete api_development

Options:
  --name NAME         Template name
  --from-task ID      Create from successful task
  --from-file PATH    Create from file
  --params JSON       Template parameters
  --description TEXT  Template description
```

## Configuration Examples

### Basic Configuration

```bash
# Set up for local development
maos config set api.host "127.0.0.1"
maos config set api.port 8000
maos config set system.max_agents 5
maos config set security.auth.require_auth false

# Set up database connection
maos config set database.primary.url "postgresql://maos:password@localhost:5432/maos"

# Set up Redis connection
maos config set redis.url "redis://localhost:6379/0"
```

### Production Configuration

```bash
# Production API settings
maos config set api.host "0.0.0.0"
maos config set api.port 8000
maos config set system.max_agents 50

# Enable security
maos config set security.auth.require_auth true
maos config set security.encryption.at_rest.enabled true

# Production database
maos config set database.primary.url "postgresql://maos:${DB_PASSWORD}@db.prod.example.com:5432/maos"
maos config set database.primary.pool_size 50

# Production Redis cluster
maos config set redis.cluster.enabled true
maos config set redis.cluster.nodes "redis1:6379,redis2:6379,redis3:6379"

# Monitoring and logging
maos config set monitoring.metrics.enabled true
maos config set monitoring.alerts.enabled true
maos config set system.log_level "INFO"
```

## Troubleshooting Commands

```bash
# Quick system health check
maos health --all-components

# Check recent error logs
maos logs --level ERROR --tail 50

# Verify database connectivity
maos db status --check-connection

# Check agent status and resource usage
maos agent list --detailed --metrics

# Monitor system performance
maos monitor --interval 1

# Generate diagnostic report
maos diagnostics --output diagnostic_report.txt

# Validate current configuration
maos config validate --detailed

# Test system with benchmark
maos benchmark --tests basic --duration 60
```

## Environment Variables

The CLI respects these environment variables:

```bash
# API Configuration
export MAOS_API_URL="https://api.maos.example.com"
export MAOS_API_KEY="your-api-key"

# CLI Behavior  
export MAOS_CONFIG_FILE="~/.maos/production.yml"
export MAOS_OUTPUT_FORMAT="json"
export MAOS_VERBOSE="1"

# Authentication
export MAOS_AUTH_TOKEN="your-jwt-token"

# Development
export MAOS_DEBUG="1"
export MAOS_DEV_MODE="1"
```

## Exit Codes

The CLI uses standard exit codes:

- `0`: Success
- `1`: General error
- `2`: Invalid command or arguments
- `3`: Configuration error
- `4`: Connection error
- `5`: Authentication error
- `6`: Resource not found
- `7`: Operation timeout
- `8`: Insufficient permissions

## Getting Help

```bash
# General help
maos --help

# Command-specific help
maos task --help
maos agent spawn --help

# Show examples for a command
maos task submit --examples

# Show all available commands
maos help commands

# Show configuration options
maos config --help

# Version information
maos --version
```

This CLI reference provides comprehensive coverage of all MAOS commands and operations. Use `maos <command> --help` for detailed help on specific commands and their options.