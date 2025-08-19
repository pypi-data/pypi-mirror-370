# MAOS v0.9.2 Release Notes

## Release Date: 2025-01-18

## Overview
MAOS v0.9.2 fixes critical version display issues, extends Claude timeout, and resolves database foreign key errors.

## 🐛 Bug Fixes

### Version Display
- **Fixed version string**: Now correctly shows v0.9.2 everywhere
- **Fixed hardcoded v0.7.0**: Updated `natural_language_v7.py` to show correct version
- **Fixed __version__**: Now properly set in `__init__.py`

### Claude Timeout
- **Extended timeout**: Increased from 30 seconds to 600 seconds (10 minutes)
- **Rationale**: Claude needs time to think, especially for complex analysis
- **Better messages**: Shows "600s / 10 minutes" in timeout messages

### Database Issues
- **Fixed foreign key constraint**: Agent now saved BEFORE message bus registration
- **Prevents race conditions**: Ensures proper order of operations

## ✨ New Features

### Documentation
- **AUTO_APPROVE_GUIDE.md**: Complete guide for using --auto-approve flag
- **Explains behavior**: With and without auto-approve
- **Best practices**: When to use each mode

## 📊 Key Changes from v0.9.1

### Version Consistency
```python
# Before (v0.9.1)
__version__ = "0.9.0"  # Wrong!
"🚀 MAOS v0.7.0"       # Very wrong!

# After (v0.9.2)
__version__ = "0.9.2"  # Correct!
"🚀 MAOS v0.9.2"       # Correct!
```

### Claude Timeout
```python
# Before (v0.9.1)
timeout_seconds = 30  # Too short!

# After (v0.9.2)
timeout_seconds = 600  # 10 minutes - much better!
```

### Foreign Key Fix
```python
# Before (v0.9.1)
await self.message_bus.register_agent()  # First - causes error!
await self._save_agent()                 # Second

# After (v0.9.2)
await self._save_agent()                 # First - correct!
await self.message_bus.register_agent()  # Second
```

## 🔄 All Features from v0.9.1 Included

- ✅ Multi-agent fallback decomposition (3-4 agents instead of 1)
- ✅ Real-time Claude visibility
- ✅ Enhanced JSON extraction
- ✅ Fixed template string errors
- ✅ Progressive saving during execution
- ✅ Auto-save loops
- ✅ PersistentMessageBus
- ✅ Orchestration CLI commands

## 📦 Installation
```bash
pip install maos-cli==0.9.2
```

or with pipx:
```bash
pipx install maos-cli==0.9.2
```

## 🎯 What Users Will See

### Version Display
```
$ maos version
╭─────────────────────────── 🤖 Version Information ───────────────────────────╮
│ MAOS - Multi-Agent Orchestration System                                      │
│                                                                              │
│ Version: 0.9.2                                                               │
│ Author: MAOS Development Team                                                │
│ Python: 3.11.1                                                               │
│ Platform: darwin                                                             │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Chat Interface
```
🚀 MAOS v0.9.2 - Autonomous Multi-Agent Orchestrator
Using Claude SDK for real parallel execution
============================================================
```

## 🚀 Quick Test
```bash
# Install
pipx install maos-cli==0.9.2

# Verify version
maos version  # Should show 0.9.2

# Test with auto-approve
maos chat --auto-approve
```

## 📝 Notes
- Version now consistently shows 0.9.2
- Claude has 10 minutes to complete tasks
- Foreign key errors are fixed
- --auto-approve is fully documented

## 🙏 Acknowledgments
Thanks for catching the version display issues and timeout problems!