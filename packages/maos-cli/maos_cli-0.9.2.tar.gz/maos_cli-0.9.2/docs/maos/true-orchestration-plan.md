# True Orchestration Implementation Plan for MAOS

## Executive Summary

**YES, TRUE ORCHESTRATION IS POSSIBLE** - but it requires significant architectural changes to enable real-time inter-agent communication and coordination.

The good news: **The infrastructure already exists** in the codebase (`agent_message_bus.py`) but is **not connected** to the current orchestrator (v7).

## Current State vs True Orchestration

### Current State (v0.8.8)
```
User Request → Decomposer → Parallel Execution → Independent Results
                                ↓
                         [Agent 1] [Agent 2] [Agent 3]
                          (isolated) (isolated) (isolated)
```

### True Orchestration (Proposed)
```
User Request → Decomposer → Coordinated Execution → Unified Result
                                ↓
                    ┌─────[Coordinator Agent]─────┐
                    ↓              ↓              ↓
                [Agent 1] ←→ [Agent 2] ←→ [Agent 3]
                    ↑              ↑              ↑
                    └──────[Message Bus]──────────┘
```

## Why It's Possible

### 1. **Message Bus Already Exists**
File: `src/maos/core/agent_message_bus.py`

The system already has:
- ✅ Inter-agent messaging (`send_message`, `broadcast`)
- ✅ Request/response patterns (`request_from_agent`)
- ✅ Discovery notifications (`notify_discovery`)
- ✅ Dependency management (`notify_dependency`)
- ✅ Claude context injection (`_inject_into_claude_context`)

### 2. **Claude Supports Context Injection**
- Can inject messages into running Claude sessions
- Can modify agent prompts with shared context
- Can use system messages for coordination

### 3. **Database Infrastructure Ready**
- Messages table exists for persistence
- Agent tracking in place
- Session management implemented

## Implementation Plan

### Phase 1: Connect Message Bus to Orchestrator (1-2 days)

#### 1.1 Modify Orchestrator V7
```python
# orchestrator_v7.py modifications

class OrchestratorV7:
    def __init__(self, persistence: SqlitePersistence):
        self.persistence = persistence
        self.decomposer = EnhancedTaskDecomposer(persistence)
        self.executor = ClaudeSDKExecutor()
        
        # NEW: Add message bus
        from .agent_message_bus import AgentMessageBus
        from .session_manager import SessionManager
        self.session_manager = SessionManager()
        self.message_bus = AgentMessageBus(persistence, self.session_manager)
        
    async def orchestrate(self, request: str, auto_approve: bool = False):
        # Start message bus
        await self.message_bus.start()
        
        # ... existing decomposition ...
        
        # Register agents with message bus
        for task in plan.subtasks:
            await self.message_bus.register_agent(
                agent_id=task.id,
                agent_info={
                    'name': task.agent_type,
                    'type': task.agent_type,
                    'capabilities': task.required_capabilities
                }
            )
```

#### 1.2 Create Agent Wrapper
```python
# new file: src/maos/core/orchestrated_agent.py

class OrchestratedAgent:
    """Wrapper for Claude agents with message bus integration"""
    
    def __init__(self, agent_id: str, message_bus: AgentMessageBus):
        self.agent_id = agent_id
        self.message_bus = message_bus
        self.context_buffer = []
        
    async def execute_with_context(self, task: str, other_agents: List[str]):
        # Inject coordination instructions
        enhanced_task = f"""
        {task}
        
        COORDINATION INSTRUCTIONS:
        - You are agent {self.agent_id}
        - Other agents working on this: {other_agents}
        - If you discover something important, announce it
        - If you need information from another agent, request it
        - Check for messages from other agents periodically
        """
        
        # Execute with message monitoring
        result = await self._execute_with_monitoring(enhanced_task)
        return result
```

### Phase 2: Implement Coordination Patterns (2-3 days)

#### 2.1 Coordinator Agent Pattern
```python
class CoordinatorAgent:
    """Special agent that orchestrates others"""
    
    async def coordinate(self, agents: List[str], goal: str):
        # 1. Break down goal into phases
        # 2. Assign agents to phases
        # 3. Monitor progress via message bus
        # 4. Adjust plan based on discoveries
        # 5. Synthesize results
```

#### 2.2 Discovery Sharing Pattern
```python
async def share_discovery(agent_id: str, discovery: str):
    # Broadcast discovery to all agents
    await message_bus.notify_discovery(
        agent_id=agent_id,
        discovery=discovery,
        importance="high"
    )
    
    # Update all running agents' context
    for agent in active_agents:
        await inject_context(agent, f"DISCOVERY: {discovery}")
```

#### 2.3 Dependency Resolution Pattern
```python
async def request_dependency(requester: str, provider: str, need: str):
    # Agent A needs something from Agent B
    response = await message_bus.request_from_agent(
        from_agent=requester,
        to_agent=provider,
        request=f"I need: {need}",
        timeout=30.0
    )
    return response
```

### Phase 3: Enhanced Execution Models (3-5 days)

#### 3.1 Sequential with Context Passing
```python
async def execute_sequential_with_context(agents: List[Agent]):
    context = {}
    for agent in agents:
        # Pass accumulated context to next agent
        agent.set_context(context)
        result = await agent.execute()
        context.update(result.discoveries)
```

#### 3.2 Parallel with Synchronization Points
```python
async def execute_parallel_with_sync(batches: List[List[Agent]]):
    for batch in batches:
        # Parallel execution
        results = await asyncio.gather(*[agent.execute() for agent in batch])
        
        # Synchronization point - share all discoveries
        for result in results:
            await broadcast_discoveries(result.discoveries)
        
        # Wait for all agents to acknowledge
        await synchronize_agents(batch)
```

#### 3.3 Dynamic Task Reassignment
```python
async def dynamic_orchestration(agents: List[Agent], tasks: List[Task]):
    task_queue = asyncio.Queue()
    for task in tasks:
        await task_queue.put(task)
    
    while not task_queue.empty():
        # Find available agent
        agent = await get_available_agent()
        task = await task_queue.get()
        
        # Agent can create new subtasks
        asyncio.create_task(
            execute_with_subtask_creation(agent, task, task_queue)
        )
```

### Phase 4: Claude-Specific Optimizations (2-3 days)

#### 4.1 Shared Memory Context
```python
class SharedContext:
    """Shared memory between Claude agents"""
    
    def __init__(self):
        self.discoveries = []
        self.facts = {}
        self.decisions = []
        
    def to_prompt(self) -> str:
        return f"""
        SHARED KNOWLEDGE:
        Discoveries: {self.discoveries}
        Established Facts: {self.facts}
        Decisions Made: {self.decisions}
        """
```

#### 4.2 Context Injection via System Messages
```python
async def inject_system_context(session_id: str, context: str):
    """Inject context as system message to running Claude"""
    message = f"""
    <system>
    COORDINATION UPDATE:
    {context}
    
    Please acknowledge and incorporate this information.
    </system>
    """
    await send_to_claude_session(session_id, message)
```

#### 4.3 Result Synthesis Agent
```python
class SynthesisAgent:
    """Specialized agent to combine results"""
    
    async def synthesize(self, agent_results: Dict[str, Any]):
        prompt = f"""
        Synthesize these results from multiple agents:
        {json.dumps(agent_results, indent=2)}
        
        Create a unified response that:
        1. Combines all insights
        2. Resolves any conflicts
        3. Highlights key discoveries
        4. Provides actionable conclusions
        """
        return await execute_claude(prompt)
```

## Implementation Challenges & Solutions

### Challenge 1: Claude Session Persistence
**Problem**: Claude CLI creates new sessions, can't modify running ones
**Solution**: Use `--resume` flag with session IDs + context injection

### Challenge 2: Real-time Communication
**Problem**: Agents can't poll for messages while thinking
**Solution**: Inject critical messages as interrupts between turns

### Challenge 3: Context Window Limits
**Problem**: Shared context grows too large
**Solution**: Implement context summarization and pruning

### Challenge 4: Synchronization Overhead
**Problem**: Waiting for all agents slows execution
**Solution**: Async message passing with eventual consistency

## Proof of Concept Implementation

### Step 1: Minimal Working Example
```python
# test_orchestration.py

async def test_true_orchestration():
    # Initialize components
    db = SqlitePersistence('./test_orch.db')
    await db.initialize()
    
    message_bus = AgentMessageBus(db, SessionManager())
    await message_bus.start()
    
    # Create two agents
    analyst = OrchestratedAgent("analyst-001", message_bus)
    security = OrchestratedAgent("security-001", message_bus)
    
    # Task with coordination
    analyst_task = """
    Analyze the codebase and share any security concerns you find.
    When you find something, announce: "DISCOVERY: [what you found]"
    """
    
    security_task = """
    Perform security analysis. 
    Listen for discoveries from the analyst.
    If they find something relevant, investigate further.
    """
    
    # Execute with message passing
    results = await asyncio.gather(
        analyst.execute_with_context(analyst_task, ["security-001"]),
        security.execute_with_context(security_task, ["analyst-001"])
    )
    
    # Check message history
    messages = await message_bus.get_broadcast_history()
    print(f"Inter-agent messages: {len(messages)}")
    
    return results
```

## Success Metrics

### Level 1: Basic Communication ✅
- Agents can send messages
- Messages are persisted
- Agents receive broadcasts

### Level 2: Coordination 🎯
- Agents respond to discoveries
- Dependencies are resolved
- Tasks are dynamically adjusted

### Level 3: True Orchestration 🚀
- Coordinator agent manages others
- Real-time strategy adjustment
- Unified result synthesis
- Learned patterns reused

## Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1 | 1-2 days | Message bus integrated |
| Phase 2 | 2-3 days | Coordination patterns working |
| Phase 3 | 3-5 days | Enhanced execution models |
| Phase 4 | 2-3 days | Claude optimizations |
| **Total** | **8-13 days** | **True orchestration** |

## Conclusion

**True orchestration IS POSSIBLE** and most of the infrastructure already exists. The implementation requires:

1. **Connecting existing components** (message bus to orchestrator)
2. **Adding coordination patterns** (discovery sharing, dependencies)
3. **Enhancing execution models** (context passing, synchronization)
4. **Claude-specific optimizations** (context injection, synthesis)

The key insight: **We don't need to rebuild, just connect and enhance**.

### Next Steps
1. ✅ Connect message bus to orchestrator v7
2. ✅ Test basic message passing between agents
3. ✅ Implement discovery sharing pattern
4. ✅ Add coordinator agent
5. ✅ Deploy and test with real tasks

---

*This plan is based on existing code analysis and architectural review of MAOS v0.8.8*