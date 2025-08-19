# MAOS Persistence System - Complete Documentation

## Overview

MAOS v0.8.x introduces a comprehensive persistence system that prevents data loss during agent execution and enables resumption of orchestrations even after crashes or multi-day gaps.

## Key Features Implemented

### 1. Progressive Saving During Agent Execution
- **Problem Solved**: Previously, if MAOS crashed during the 10-minute agent execution window, all progress was lost
- **Solution**: Streaming output with saves every 30 seconds
- **Location**: `src/maos/core/claude_sdk_executor.py`

### 2. Auto-Save Loops in Orchestrator
- **Problem Solved**: Orchestration state was only saved at start and end
- **Solution**: Background task saves state every 30 seconds
- **Location**: `src/maos/core/orchestrator_v7.py`

### 3. PersistentMessageBus with Database Integration
- **Problem Solved**: Inter-agent communication was lost on restart
- **Solution**: Full database persistence of messages and agent states
- **Location**: `src/maos/core/persistent_message_bus.py`

### 4. Orchestration CLI Commands
- **Problem Solved**: No way to resume interrupted orchestrations
- **Solution**: New CLI commands for listing, resuming, and monitoring orchestrations
- **Location**: `src/maos/cli/commands/orchestration.py`

## Architecture

```
┌─────────────────────────────────────┐
│         Orchestrator V7              │
│  - Auto-save loop (30s)              │
│  - Checkpoint creation                │
│  - State persistence                 │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│     PersistentMessageBus            │
│  - Message persistence              │
│  - Agent state recovery             │
│  - Communication history            │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│     ClaudeSDKExecutor               │
│  - Streaming output                 │
│  - Progressive saves (30s)          │
│  - Partial result storage           │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│     SqlitePersistence               │
│  - Agents table                     │
│  - Sessions table                    │
│  - Messages table                   │
│  - Orchestrations table             │
│  - Checkpoints table                │
└─────────────────────────────────────┘
```

## Database Schema

### Orchestrations Table
```sql
CREATE TABLE orchestrations (
    id TEXT PRIMARY KEY,
    request TEXT NOT NULL,
    status TEXT DEFAULT 'running',
    agents TEXT,  -- JSON array of agent IDs
    batches TEXT,  -- JSON array of batch structure
    total_cost REAL DEFAULT 0.0,
    total_duration_ms INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    summary TEXT
)
```

### Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_agent TEXT NOT NULL,
    to_agent TEXT,  -- NULL for broadcasts
    message TEXT NOT NULL,
    message_type TEXT DEFAULT 'info',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged BOOLEAN DEFAULT 0
)
```

### Checkpoints Table
```sql
CREATE TABLE checkpoints (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    orchestrator_state TEXT,  -- JSON object
    agent_sessions TEXT,  -- JSON mapping
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Usage Guide

### Starting an Orchestration with Persistence

```bash
# Start orchestration (auto-save enabled by default)
maos orchestrate "Build a complete web application"

# Orchestration will automatically:
# - Save state every 30 seconds
# - Create checkpoints every 2 minutes
# - Persist all agent messages
# - Store partial results during execution
```

### Resuming After Interruption

```bash
# List all orchestrations
maos orchestration list

# Check status of specific orchestration
maos orchestration status abc123

# Resume interrupted orchestration
maos orchestration resume abc123

# Resume with new task
maos orchestration resume abc123 --task "Continue with testing"
```

### Creating Manual Checkpoints

```bash
# Create checkpoint for current orchestration
maos orchestration checkpoint abc123 --name "before-refactor"

# List all checkpoints
maos recover list

# Restore from checkpoint
maos recover restore checkpoint-20240118120000
```

## Save Frequency

| Event | What Gets Saved | Frequency | Automatic |
|-------|-----------------|-----------|-----------|
| Agent output | Partial results, discoveries | Every 30 seconds | ✅ |
| Orchestration state | Active agents, message count | Every 30 seconds | ✅ |
| Auto-checkpoint | Full state snapshot | Every 2 minutes | ✅ |
| Agent completion | Final results, costs | On completion | ✅ |
| Messages | All inter-agent communication | Immediately | ✅ |
| Manual checkpoint | Complete system state | On demand | ❌ |

## Recovery Scenarios

### Scenario 1: Clean Shutdown
```bash
# Start orchestration
maos orchestrate "Complex task"
# Press Ctrl+C
# State automatically saved

# Resume later
maos orchestration resume <id>
```

### Scenario 2: System Crash
```bash
# System crashes during execution
# ... reboot ...

# Check what can be resumed
maos orchestration list --status paused

# Resume specific orchestration
maos orchestration resume <id>
```

### Scenario 3: Multi-Day Gap
```bash
# Start orchestration on Monday
maos orchestrate "Large project"

# Resume on Friday
maos orchestration list
maos orchestration status <id> --messages
maos orchestration resume <id>
```

## API Reference

### PersistentMessageBus

```python
from maos.core.persistent_message_bus import PersistentMessageBus

# Initialize with database
message_bus = PersistentMessageBus(db, session_manager)

# Start (recovers from database)
await message_bus.start()

# Resume orchestration
result = await message_bus.resume_orchestration(orchestration_id)

# Get communication history
history = await message_bus.get_communication_history(
    since=datetime.now() - timedelta(hours=1),
    limit=100
)

# Create checkpoint
checkpoint_id = await message_bus.create_communication_checkpoint("my-checkpoint")
```

### ClaudeSDKExecutor with Progressive Saves

```python
from maos.core.claude_sdk_executor import ClaudeSDKExecutor

# Initialize with persistence
executor = ClaudeSDKExecutor(api_key, persistence=db)

# Execute agent (auto-saves every 30s)
result = await executor.execute_agent(execution)

# Partial results available even if crashes:
# - Saved to sessions table every 30 seconds
# - Checkpoints created every 2 minutes
# - Discoveries saved immediately
```

### Orchestrator with Auto-Save

```python
from maos.core.orchestrator_v7 import OrchestratorV7

# Initialize with persistence
orchestrator = OrchestratorV7(persistence=db)

# Start orchestration (auto-save enabled)
result = await orchestrator.orchestrate(
    request="Build application",
    auto_approve=True
)

# Resume previous orchestration
resume_result = await orchestrator.resume_orchestration(
    orchestration_id="abc123",
    new_request="Continue with testing"
)
```

## Configuration

### Auto-Save Intervals

```python
# In orchestrator_v7.py
save_interval = 30  # seconds between saves

# In claude_sdk_executor.py  
save_interval = 30  # seconds between progressive saves

# In persistent_message_bus.py
auto_save_interval = 30  # seconds between state saves
message_retention_days = 7  # days to keep messages
```

### Database Location

```python
# Default database
db_path = "./maos.db"

# Custom database
db = SqlitePersistence("/path/to/custom.db")
```

## Testing

### Basic Persistence Test
```bash
python test_persistence_simple.py
```

Tests:
- Database initialization
- Agent persistence
- Session persistence  
- Message persistence
- Orchestration persistence
- Checkpoint persistence
- Helper methods

### Full Integration Test
```bash
python test_persistence_complete.py
```

Tests:
- Progressive saving during execution
- Auto-save loops
- Message bus recovery
- Orchestration resumption
- Multi-day gap handling
- Crash recovery

## Troubleshooting

### Issue: Orchestration not resuming
```bash
# Check orchestration status
maos orchestration status <id> --agents --messages

# Check database directly
sqlite3 maos.db "SELECT * FROM orchestrations WHERE id LIKE 'abc%'"
```

### Issue: Messages not being saved
```bash
# Check message bus status
maos status --messages

# Verify database
sqlite3 maos.db "SELECT COUNT(*) FROM messages"
```

### Issue: Auto-save not working
```bash
# Check logs
tail -f maos.log | grep "auto-save"

# Verify checkpoints
maos recover list
```

## Performance Impact

- **Storage**: ~1MB per hour of orchestration
- **CPU**: <1% for auto-save loops
- **Memory**: ~10MB for message history
- **I/O**: Writes every 30 seconds (minimal)

## Best Practices

1. **Let auto-save handle persistence** - Don't manually save unless needed
2. **Create checkpoints before major changes** - Use `maos orchestration checkpoint`
3. **Monitor long-running orchestrations** - Use `maos orchestration status --watch`
4. **Clean up old data periodically** - Messages older than 7 days can be purged
5. **Use resumption for iterative development** - Resume with new tasks to continue work

## Future Enhancements

- [ ] Configurable save intervals via CLI
- [ ] Automatic cleanup of old orchestrations
- [ ] Export/import orchestration states
- [ ] Distributed persistence (Redis/PostgreSQL)
- [ ] Real-time orchestration monitoring dashboard
- [ ] Rollback to previous checkpoints
- [ ] Merge multiple orchestrations

## Conclusion

The persistence system in MAOS v0.8.x ensures that no work is lost, even during:
- Agent crashes
- System shutdowns
- Network interruptions
- Multi-day gaps
- Long-running operations

All persistence happens automatically in the background, requiring no user intervention while providing full control when needed.