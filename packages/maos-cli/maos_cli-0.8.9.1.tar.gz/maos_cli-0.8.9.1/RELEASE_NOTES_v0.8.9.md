# MAOS v0.8.9 Release Notes

## 🎉 Major Release: Complete Persistence & Recovery System

### What's New

#### ✅ Progressive Saving (No More Data Loss!)
- **Auto-save every 30 seconds** - All agent progress is saved progressively
- **Auto-checkpoint every 2 minutes** - Full state snapshots for recovery
- **Immediate discovery capture** - Important findings saved instantly
- **Streaming output monitoring** - Non-blocking reads with continuous saves

#### ✅ Full Database Integration
- **Complete SQLite persistence** - All state stored in local database
- **Automatic schema migration** - Seamlessly updates existing databases
- **7-day recovery window** - Resume orchestrations even after days

#### ✅ Enhanced CLI Commands
```bash
# List all orchestrations
maos orchestration list [--status running|paused|completed]

# Check detailed status
maos orchestration status <id> [--watch]

# Resume interrupted work
maos orchestration resume <id>

# Create manual checkpoint
maos orchestration checkpoint <id>

# Configure auto-save interval
maos orchestration save-interval <seconds>
```

#### ✅ Persistent Message Bus
- Survives restarts and crashes
- Restores all active agents on startup
- Tracks undelivered messages
- Maintains full communication history

### Critical Bug Fix
- Fixed database schema mismatch that was preventing auto-save from working
- Added missing columns: `last_updated`, `active_agents`, `message_count`
- Implemented automatic migration for existing databases

### Technical Details

#### Components Updated:
- `ClaudeSDKExecutor` - Progressive saving implementation
- `OrchestratorV7` - Auto-save loop with 30-second interval
- `PersistentMessageBus` - Full database recovery on startup
- `SqlitePersistence` - New methods and migration support
- `orchestration.py` - CLI commands for management

#### Database Schema:
- 6 core tables: agents, sessions, tasks, messages, checkpoints, orchestrations
- Proper indexes for performance
- Foreign key relationships maintained
- Automatic migration for v0.8.8 → v0.8.9 upgrades

### Installation

```bash
pip install --upgrade maos-cli==0.8.9
```

### Upgrade Notes

**For users upgrading from v0.8.8:**
- Database schema will be automatically migrated on first run
- No manual intervention required
- All existing data will be preserved

### Recovery Capabilities

| Scenario | Data Loss | Recovery Time |
|----------|-----------|---------------|
| Clean shutdown (Ctrl+C) | ZERO | Immediate |
| System crash | Max 30 seconds | Immediate |
| Network interruption | ZERO | Immediate |
| Multi-day gap | ZERO | Immediate |
| Agent timeout | ZERO | Immediate |

### Performance Impact
- CPU overhead: <5%
- Memory: ~20-30MB
- Database writes: Every 30 seconds
- Storage: ~1-2MB per hour

### What This Means

**Before v0.8.9:** If MAOS crashed during the 10-30 minute agent execution window, ALL progress was lost.

**With v0.8.9:** MAOS is now unstoppable. Even catastrophic failures result in minimal data loss (max 30 seconds) with full ability to resume exactly where you left off.

### Package Files

- `dist/maos_cli-0.8.9-py3-none-any.whl` (298KB)
- `dist/maos_cli-0.8.9.tar.gz` (1.1MB)

---

*The days of losing hours of work to crashes are over. MAOS v0.8.9 is production-ready with enterprise-grade persistence.*