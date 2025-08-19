# How MAOS Really Works - Technical Deep Dive

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Task Decomposition](#task-decomposition)
4. [Agent Execution](#agent-execution)
5. [Orchestration](#orchestration)
6. [Database Integration](#database-integration)
7. [Claude Integration](#claude-integration)
8. [Parallel Execution - The Truth](#parallel-execution---the-truth)
9. [What Actually Works vs What Doesn't](#what-actually-works-vs-what-doesnt)

## Overview

MAOS (Multi-Agent Orchestration System) is designed to orchestrate multiple Claude subagents to handle complex tasks. However, based on the codebase analysis, there are significant gaps between the intended design and actual implementation.

### Key Components
- **Task Decomposer** (`task_decomposer_v2.py`): Breaks down user requests into subtasks
- **Orchestrator** (`orchestrator_v7.py`): Manages the execution flow
- **Claude SDK Executor** (`claude_sdk_executor.py`): Interfaces with Claude CLI
- **SQLite Persistence** (`sqlite_persistence.py`): Stores execution data

## Architecture

```
User Input ’ Natural Language Interface ’ Task Decomposer
                                              “
                                    Orchestrator (v7)
                                              “
                                    Claude SDK Executor
                                              “
                                    Claude CLI (subprocess)
                                              “
                                    Database Persistence
```

## Task Decomposition

### How It Works (task_decomposer_v2.py)

The task decomposer uses **pattern matching** to identify how to break down tasks:

```python
# Lines 214-219: Pattern detection
if any(pattern in request_lower for pattern in [
    "use", "spawn", "create", "launch", "start"
]) and "agent" in request_lower:
    # Creates multiple agents
```

### Evidence from Code

**WORKING Patterns (as of v0.8.8):**
1. **"spawn X agent and Y agent"** ’ Creates 2 agents
2. **"analyze X and do Y analysis"** ’ Creates 2 agents if Y is security/performance

**NOT WORKING Patterns:**
- Generic requests without keywords ’ Single agent only
- Complex requests without explicit agent mentions ’ Single agent

### Actual Implementation (Lines 259-312)

```python
# Pattern 1: Explicit spawn requests
if "spawn" in request_lower or "create" in request_lower:
    agent_types = []
    if "analyst" in request_lower:
        agent_types.append("analyst")
    if "security" in request_lower:
        agent_types.append("security")
    # Creates SubTask for each agent type found
```

**Limitation**: Only recognizes hardcoded agent types (analyst, security, developer, tester, reviewer)

## Agent Execution

### How It's Supposed to Work

The `ClaudeSDKExecutor` (claude_sdk_executor.py) executes agents via subprocess:

```python
# Lines 103-109: Actual execution
process = await asyncio.create_subprocess_exec(
    *cmd,
    stdin=asyncio.subprocess.PIPE,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
    env=env
)
```

### The Reality (Evidence from Testing)

1. **v0.8.7 Fix**: Changed from passing task as argument to stdin
   ```python
   # Line 118: Send task via stdin
   stdout, stderr = await process.communicate(input=execution.task.encode())
   ```

2. **v0.8.8 Enhancement**: Attempts to use Claude Code agents
   ```python
   # Lines 68-74: Agent mapping
   agent_mapping = {
       "security": "security-auditor",
       "reviewer": "reviewer",
   }
   # Uses: claude @security-auditor -p --output-format json
   ```

**Problem**: Claude Code agents (`@security-auditor`) may not exist or work as expected

## Orchestration

### The Orchestrator V7 (orchestrator_v7.py)

The orchestrator manages execution flow:

```python
# Lines 122-150: Main orchestration loop
async def orchestrate(self, request: str, auto_approve: bool = False):
    # 1. Decompose task
    plan = await self.decomposer.decompose(request)
    
    # 2. Create batches based on dependencies
    batches = plan.get_execution_order()
    
    # 3. Execute batches sequentially
    for batch in batches:
        # Each batch runs agents in parallel
        results = await self.executor.execute_parallel(batch_executions)
```

### Batch Execution Evidence (Lines 155-232)

```python
# Batches execute SEQUENTIALLY, not in parallel
for batch_idx, batch in enumerate(batches, 1):
    batch_executions = []
    for task in batch:
        # Creates execution for each agent
        execution = AgentExecution(...)
        batch_executions.append(execution)
    
    # This claims parallel but...
    results = await self.executor.execute_parallel(batch_executions)
```

## Database Integration

### Schema (sqlite_persistence.py)

Six main tables work together:

```sql
-- Lines 25-86: Database schema
1. orchestrations
   - id (PRIMARY KEY)
   - request (user input)
   - status (running/completed/failed)
   - total_agents, successful_agents
   - total_cost, total_duration

2. agents  
   - id, name, type
   - capabilities (JSON)
   - created_at

3. sessions
   - id, agent_id (FOREIGN KEY)
   - started_at, ended_at
   - total_messages, total_cost

4. tasks
   - id, agent_id (FOREIGN KEY)
   - description, status
   - result (JSON)

5. messages
   - id, session_id (FOREIGN KEY)
   - role, content
   - timestamp

6. checkpoints
   - id, session_id (FOREIGN KEY)
   - state (JSON)
   - created_at
```

### How They Work Together

```
orchestrations (1) ’ (N) agents
       “
    sessions (1) ’ (N) messages
       “
     tasks (1) ’ (1) result
       “
   checkpoints (for resume)
```

### Evidence of Database Usage (Lines 419-459)

```python
# Orchestrator saves agents
async def _save_agent(self, agent_id: str, task: Any):
    await self.persistence.save_agent(
        agent_id=agent_id,
        name=agent_id,
        agent_type=task.agent_type,
        capabilities=task.required_capabilities
    )
```

**Reality Check**: Database saves records BUT messages table often empty (evidence from test outputs)

## Claude Integration

### How MAOS Calls Claude

MAOS uses the Claude CLI, NOT the API:

```python
# Lines 69-93: Command construction
cmd = ["claude", "-p", "--output-format", "json"]

# v0.8.8 tries to use Claude Code agents:
if claude_agent:
    cmd = ["claude", f"@{claude_agent}", "-p", "--output-format", "json"]
```

### The Integration Issues

1. **Timeout Issues**: Claude takes 30-60+ seconds to respond
2. **Authentication**: Uses OAuth via Anthropic Console (not API keys)
3. **Agent Mapping**: Tries to use `.claude/agents/` but these may not exist

Evidence from error logs:
```
Error: Input must be provided either through stdin or as a prompt argument when using --print
```

## Parallel Execution - The Truth

### What the Code Claims

```python
# claude_sdk_executor.py, Line 183
async def execute_parallel(self, executions: List[AgentExecution]):
    """Execute multiple Claude agents in parallel."""
    tasks = [self.execute_agent(execution) for execution in executions]
    results = await asyncio.gather(*tasks)  # Should run in parallel
```

### The Reality

**Parallel execution PARTIALLY works:**

1. **Within a batch**: Agents DO run in parallel via `asyncio.gather()`
2. **Between batches**: Sequential execution
3. **Practical limitation**: Claude CLI startup time (30-60s) makes parallelism less effective

### Evidence from Testing

Test output shows:
```
Found 2 subtasks:
1. analyst: Analyze and explain...
2. security: Perform security analysis...

=Ê Batch 1 Results:
  L analyst-bb7cf885
     Session: N/A
     Cost: $0.0000 | Duration: 0ms | Turns: 0
     Error: [timeout or execution failure]
```

**Agents are created but execution often fails or times out**

## What Actually Works vs What Doesn't

###  What Works

1. **Task Decomposition** (v0.8.8+)
   - Pattern matching for "spawn X and Y agent"
   - Creates multiple SubTask objects
   - Evidence: Test shows "Found 2 subtasks"

2. **Database Structure**
   - Tables created correctly
   - Orchestrations and agents saved
   - Evidence: "New agents: 2" in test outputs

3. **Basic Claude Integration** (v0.8.7+)
   - Fixed stdin input issue
   - Can execute single agents
   - Evidence: Simple tasks complete successfully

### L What Doesn't Work Reliably

1. **Multi-Agent Execution**
   - Agents often timeout or fail
   - Claude Code agents (@security-auditor) may not exist
   - Evidence: Execution timeouts in tests

2. **True Orchestration**
   - No inter-agent communication
   - No result sharing between agents
   - Agents run independently, not as coordinated team

3. **Agent Persistence**
   - MAOS doesn't create `.claude/agents/` files
   - Can't reuse agent sessions effectively
   - Evidence: No new files in `.claude/agents/`

###   What Partially Works

1. **Parallel Execution**
   - Code structure supports it
   - `asyncio.gather()` used correctly
   - BUT: Claude startup time negates benefits

2. **Resume Functionality**
   - Code exists for resuming sessions
   - Database stores session IDs
   - BUT: Rarely works in practice

## Honest Assessment

### Current State (v0.8.8)

1. **Task decomposition**:  Working (creates multiple tasks)
2. **Database integration**:  Working (saves records)
3. **Claude integration**:   Partially working (timeouts common)
4. **Multi-agent execution**: L Not working reliably
5. **True orchestration**: L Not implemented (no agent coordination)
6. **Parallel execution**:   Technically yes, practically limited

### The Gap

**Intended**: Orchestrate swarms of intelligent agents working together
**Reality**: Spawns multiple independent Claude instances that often timeout

### Root Causes

1. **Claude CLI limitations**: 30-60s startup time per agent
2. **No agent communication**: Agents can't share results
3. **Pattern matching**: Limited to hardcoded patterns
4. **Timeout issues**: 600s timeout still insufficient for complex tasks

## Conclusion

MAOS v0.8.8 has the **architecture** for multi-agent orchestration but faces **practical limitations**:

-  Can decompose tasks into multiple subtasks
-  Can spawn multiple Claude processes
-   Processes run in parallel but don't communicate
- L Execution often fails due to timeouts
- L Not true orchestration, just parallel execution

The system is more accurately described as a **"Claude parallel executor"** rather than a true **"multi-agent orchestrator"**.

---

*This analysis is based on code review and test evidence from versions 0.8.6-0.8.8*