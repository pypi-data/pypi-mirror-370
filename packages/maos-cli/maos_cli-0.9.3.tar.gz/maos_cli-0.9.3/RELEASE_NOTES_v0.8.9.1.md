# MAOS v0.8.9.1 Release Notes

## 🔧 Hotfix Release

### Bug Fix
- **Fixed import error in orchestration commands** - Corrected import path from `..._main` to `.._main` in `orchestration.py`
  - This was preventing the CLI from starting properly
  - Error: `ModuleNotFoundError: No module named 'maos._main'`

### No Other Changes
- All v0.8.9 features remain the same
- Database schema unchanged
- Persistence system fully functional

### Package Files
- `dist/maos_cli-0.8.9.1-py3-none-any.whl` (291KB)
- `dist/maos_cli-0.8.9.1.tar.gz` (1.1MB)

### Installation
```bash
pip install --upgrade maos-cli==0.8.9.1
```

### Testing Confirmed
✅ All v0.8.9 features working:
- Progressive saving every 30 seconds
- Auto-checkpoints every 2 minutes
- Database migration support
- Full crash recovery
- All CLI commands functional

---
*This hotfix ensures the orchestration CLI commands work properly with the v0.8.9 persistence system.*