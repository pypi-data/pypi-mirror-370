# MAOS v0.9.3 Release Notes

## Release Date: 2025-01-18

## Overview
MAOS v0.9.3 fixes critical timeout issues for long-running agents and improves agent discovery to properly parse Claude agent files.

## 🐛 Bug Fixes

### Agent Execution Timeout
- **Extended timeout**: Increased from 10 minutes to 60 minutes per agent
- **Rationale**: Complex tasks (like implementing linear regression with visualization) need more than 10 minutes
- **Impact**: Agents can now run for up to 1 hour without timing out

### Agent Discovery
- **Fixed path resolution**: Now properly finds `.claude/agents/` from any working directory
- **Fixed YAML frontmatter parsing**: Correctly parses Claude agent files with frontmatter
- **Improved agent naming**: No more strange names like "MIGRATION_SUMMARY"
- **Better logging**: Shows which directory is being scanned for agents

## 📊 Key Changes from v0.9.2

### Timeout Extension
```python
# Before (v0.9.2)
timeout_time = asyncio.get_event_loop().time() + 600  # 10 minutes - too short!

# After (v0.9.3)
timeout_time = asyncio.get_event_loop().time() + 3600  # 60 minutes - proper time for complex tasks
```

### Agent Discovery Improvements
```python
# Before (v0.9.2)
agents_dir = Path(".claude/agents")  # Relative path, could be wrong

# After (v0.9.3)
# Searches current directory and up to 3 parent directories
# Finds the project root's .claude/agents/ reliably
```

### YAML Frontmatter Parsing
```yaml
# Now properly parses Claude agent files like:
---
name: reviewer
description: Code review specialist
tools: Read, Grep, Glob, Bash
---
```

## 🔄 All Features from v0.9.2 Included

- ✅ Version correctly displays (now 0.9.3)
- ✅ Multi-agent fallback (3-4 agents instead of 1)  
- ✅ Real-time Claude visibility
- ✅ 10-minute timeout for initial decomposition
- ✅ Progressive saving every 30 seconds
- ✅ Auto-save loops
- ✅ PersistentMessageBus
- ✅ Orchestration CLI commands
- ✅ Foreign key error fixes

## 📦 Installation
```bash
pip install maos-cli==0.9.3
```

## 🎯 What This Fixes

### The Problem You Reported
When running complex tasks like "analyze calculator.html and add linear regression with visualization":
- **Before**: Agents would timeout after 10 minutes mid-execution
- **After**: Agents have 60 minutes to complete their work

### Agent Discovery
- **Before**: Showed strange agent names from misread files
- **After**: Only shows actual agents from `.claude/agents/`

## 💡 Example Timeline

For your calculator enhancement request:
```
Phase 1: Analyze (3 min) ✅
Phase 2: Design (5 min) ✅  
Phase 3: Implement (10-12 min) ✅ (was timing out before!)
Phase 4: Integrate (8 min) ✅
Phase 5: Test (5 min) ✅
Total: ~31-33 minutes (well within 60-minute limit)
```

## 🚀 Quick Test
```bash
# Install
pip install maos-cli==0.9.3

# Verify version
maos version  # Should show 0.9.3

# Test with complex task
maos chat --auto-approve
> analyze calculator.html and add linear regression with visualization
# Should complete without timeout!
```

## 📝 Summary

v0.9.3 ensures that:
1. **Long-running agents don't timeout** (60 minutes vs 10)
2. **Agent discovery works correctly** (finds right `.claude/agents/`)
3. **Claude agent files parse properly** (YAML frontmatter support)
4. **Version displays correctly** (shows 0.9.3)

This release makes MAOS suitable for complex, long-running orchestrations!