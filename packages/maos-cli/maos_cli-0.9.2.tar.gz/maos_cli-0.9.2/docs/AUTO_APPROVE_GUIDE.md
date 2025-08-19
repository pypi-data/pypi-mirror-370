# MAOS --auto-approve Guide

## What is --auto-approve?

The `--auto-approve` flag allows MAOS to run completely autonomously without asking for user confirmation at each step.

## Usage

```bash
# With auto-approve (fully autonomous)
maos chat --auto-approve

# Without auto-approve (interactive mode)
maos chat
```

## What It Does

### WITHOUT --auto-approve (Default)
1. **Shows execution plan** - You see what agents will be created
2. **Asks for confirmation** - "Proceed with autonomous execution? [y/n]:"
3. **Waits for your response** - Type 'y' to continue or 'n' to cancel
4. **Shows progress** - You can monitor what's happening
5. **Asks before major operations** - Like running multiple agents

### WITH --auto-approve
1. **Shows execution plan** - You still see what will happen
2. **Immediately executes** - No confirmation needed
3. **Runs autonomously** - All agents execute automatically
4. **Continues on errors** - Attempts to complete all tasks
5. **No interruptions** - Runs until completion

## When to Use Each Mode

### Use DEFAULT (no flag) when:
- **Testing new requests** - You want to see the plan first
- **Learning MAOS** - Understanding how it decomposes tasks
- **Debugging** - Need to stop if something looks wrong
- **Sensitive operations** - Want to review before execution
- **First time users** - Getting familiar with the system

### Use --auto-approve when:
- **Production workflows** - You trust the system
- **Repeated tasks** - You know what will happen
- **CI/CD pipelines** - Automated environments
- **Long-running tasks** - You don't want to babysit
- **Batch processing** - Running multiple orchestrations

## Examples

### Interactive Mode (Default)
```bash
$ maos chat
MAOS>: analyze my code and fix bugs

📋 Execution Plan:
────────────────────
Batch 1 (Parallel):
  • analyst: Analyze codebase for bugs
  • developer: Fix identified bugs
  • tester: Validate fixes

Proceed with autonomous execution? [y/n]: y  # <-- YOU MUST CONFIRM
```

### Auto-Approve Mode
```bash
$ maos chat --auto-approve
MAOS>: analyze my code and fix bugs

📋 Execution Plan:
────────────────────
Batch 1 (Parallel):
  • analyst: Analyze codebase for bugs
  • developer: Fix identified bugs
  • tester: Validate fixes

[EXECUTING AUTOMATICALLY...]  # <-- NO CONFIRMATION NEEDED
```

## Safety Considerations

### --auto-approve will:
- ✅ Execute all planned agents
- ✅ Make decisions autonomously
- ✅ Continue even if some agents fail
- ✅ Save state automatically
- ✅ Use fallback strategies

### --auto-approve will NOT:
- ❌ Skip showing the plan
- ❌ Hide what it's doing
- ❌ Bypass safety checks
- ❌ Ignore errors completely
- ❌ Prevent you from monitoring

## Best Practices

1. **Start without --auto-approve** for new tasks
2. **Review the execution plan** before using auto-approve
3. **Monitor logs** even with auto-approve
4. **Use checkpoints** for long-running tasks
5. **Test in development** before production auto-approve

## Combining with Other Features

```bash
# Auto-approve with session recovery
maos orchestration resume <id> --auto-approve

# Auto-approve with specific requests
maos chat --auto-approve "build a REST API"

# Auto-approve in scripts
#!/bin/bash
echo "analyze security" | maos chat --auto-approve
```

## FAQ

**Q: Can I cancel an auto-approved task?**
A: Yes, use Ctrl+C to interrupt. The state is saved automatically.

**Q: Does auto-approve skip error handling?**
A: No, it handles errors the same way but doesn't ask for confirmation to continue.

**Q: Is auto-approve faster?**
A: Slightly - it saves the time waiting for confirmations, but agents run at the same speed.

**Q: Should I always use auto-approve?**
A: No, only when you're confident about what will happen.

**Q: Can I change my mind after starting?**
A: You can't add auto-approve mid-session, but you can always cancel with Ctrl+C.