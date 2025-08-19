# Product Requirements Document
# Intelligent Task Decomposer with Claude-Powered Analysis

**Document Version:** 1.0  
**Date:** August 18, 2025  
**Author:** MAOS Development Team  
**Status:** Draft

---

## 1. Executive Summary

### 1.1 Purpose
Replace the current rule-based task decomposition system with an intelligent, Claude-powered analyzer that can understand complex user requests, automatically discover available agents, and create optimal execution plans.

### 1.2 Problem Statement
The current task decomposer uses hardcoded pattern matching, resulting in:
- Single agent execution for complex multi-part requests
- Inability to recognize compound tasks (connected with "AND", "THEN", etc.)
- No awareness of available Claude Code agents in `.claude/agents/`
- Poor parallelization of independent subtasks
- No intelligent understanding of user intent

### 1.3 Solution Overview
Implement a Claude-powered orchestrator agent that:
- Analyzes user requests using natural language understanding
- Discovers and utilizes available agents dynamically
- Creates intelligent multi-agent execution plans
- Provides transparency into the decomposition process

---

## 2. Goals and Objectives

### 2.1 Primary Goals
1. **Intelligent Analysis**: Use Claude to understand user intent and decompose complex requests
2. **Dynamic Agent Discovery**: Automatically detect and utilize available agents
3. **Optimal Parallelization**: Identify independent tasks for parallel execution
4. **Full Transparency**: Show users the orchestrator's reasoning and instructions

### 2.2 Success Metrics
- Increase multi-agent spawning rate from <10% to >60% for compound requests
- Reduce task decomposition errors by 80%
- Achieve 90% user satisfaction with task breakdown accuracy
- Enable discovery and use of 100% of available Claude Code agents

---

## 3. Functional Requirements

### 3.1 Claude-Powered Request Analysis

#### 3.1.1 Orchestrator Agent
Create a dedicated orchestrator agent that receives:

**Input Structure:**
```json
{
  "user_request": "The original user request",
  "available_agents": [
    {
      "name": "security-auditor",
      "description": "Security analysis and vulnerability assessment",
      "capabilities": ["code-review", "security-scan", "threat-modeling"]
    },
    {
      "name": "reviewer",
      "description": "Code review and quality assessment",
      "capabilities": ["code-review", "best-practices", "performance"]
    }
  ],
  "context": {
    "project_type": "web-app",
    "files_present": ["calculator.html", "styles.css"],
    "previous_tasks": []
  }
}
```

**Expected Output:**
```json
{
  "analysis": {
    "user_intent": "User wants to understand existing calculator functionality and enhance it with graphing capabilities",
    "complexity": "medium",
    "requires_parallel": true
  },
  "execution_plan": {
    "phases": [
      {
        "phase": 1,
        "parallel": true,
        "tasks": [
          {
            "id": "task-001",
            "description": "Analyze calculator.html structure and functionality",
            "agent_type": "analyst",
            "assigned_agent": "generic-analyst",
            "estimated_duration": "5 minutes",
            "dependencies": []
          },
          {
            "id": "task-002",
            "description": "Research graphing libraries and visualization options",
            "agent_type": "researcher",
            "assigned_agent": "generic-researcher",
            "estimated_duration": "3 minutes",
            "dependencies": []
          }
        ]
      },
      {
        "phase": 2,
        "parallel": false,
        "tasks": [
          {
            "id": "task-003",
            "description": "Design and implement graphing feature",
            "agent_type": "developer",
            "assigned_agent": "generic-developer",
            "estimated_duration": "10 minutes",
            "dependencies": ["task-001", "task-002"]
          }
        ]
      }
    ]
  },
  "reasoning": "The request contains two distinct parts: analysis of existing code and adding new functionality. These can be partially parallelized, with the analysis and research happening simultaneously, followed by implementation.",
  "orchestrator_prompt": "You are orchestrating a calculator enhancement project. First, coordinate parallel analysis of the existing calculator.html and research on graphing libraries. Once both complete, guide the implementation of the graphing feature based on the findings."
}
```

### 3.2 Dynamic Agent Discovery

#### 3.2.1 Agent Scanner
Implement a scanner that checks for available agents on startup and periodically:

```python
class AgentDiscovery:
    async def scan_available_agents(self) -> List[AgentInfo]:
        """
        Scan multiple sources for available agents:
        1. .claude/agents/ directory (local custom agents)
        2. Claude Code built-in agents (@security-auditor, @reviewer, etc.)
        3. MCP agents if configured
        4. Custom MAOS agent templates
        """
        agents = []
        
        # Scan .claude/agents/
        if Path(".claude/agents").exists():
            for agent_file in Path(".claude/agents").glob("*.md"):
                agent_info = self._parse_agent_file(agent_file)
                agents.append(agent_info)
        
        # Check Claude Code agents via --list-agents (if available)
        claude_agents = await self._get_claude_code_agents()
        agents.extend(claude_agents)
        
        # Add known built-in agents
        agents.extend(self._get_builtin_agents())
        
        return agents
```

### 3.3 Transparency Features

#### 3.3.1 Orchestrator Instruction Display
Show users exactly what instructions are being sent to the orchestrator:

```
╭─ Orchestrator Instructions ────────────────────────────────╮
│ ORIGINAL USER REQUEST:                                      │
│ "analyze the calculator.html and tell me what it is AND    │
│  add a new feature to be able to run functions and         │
│  visualize them on a screen in a graph"                    │
│                                                             │
│ ORCHESTRATOR PROMPT:                                        │
│ You are an intelligent task orchestrator. Analyze this     │
│ request and create an execution plan:                      │
│                                                             │
│ 1. Identify distinct subtasks                              │
│ 2. Determine which can run in parallel                     │
│ 3. Assign appropriate agent types                          │
│ 4. Consider dependencies between tasks                     │
│                                                             │
│ Available agents: security-auditor, reviewer,              │
│ general-purpose, developer, analyst                        │
│                                                             │
│ Project context: Web application with calculator.html      │
╰─────────────────────────────────────────────────────────────╯
```

#### 3.3.2 Decomposition Reasoning Display
Show the orchestrator's reasoning:

```
╭─ Orchestrator Analysis ─────────────────────────────────────╮
│ 📊 REASONING:                                               │
│ • Identified 2 main objectives:                            │
│   1. Understanding existing calculator (analysis)          │
│   2. Adding graphing functionality (development)           │
│                                                             │
│ • These can be partially parallelized:                     │
│   - Analysis and research can happen simultaneously        │
│   - Implementation must wait for analysis results          │
│                                                             │
│ • Recommended agents:                                       │
│   - Analyst for code understanding                         │
│   - Researcher for graphing options                        │
│   - Developer for implementation                           │
│                                                             │
│ 📋 EXECUTION PLAN:                                          │
│ Phase 1 (Parallel):                                        │
│   ├─ Task 1: Analyze calculator.html [@analyst]            │
│   └─ Task 2: Research graphing libraries [@researcher]     │
│                                                             │
│ Phase 2 (Sequential):                                      │
│   └─ Task 3: Implement graphing feature [@developer]       │
╰─────────────────────────────────────────────────────────────╯
```

### 3.4 Enhanced Task Decomposition Logic

#### 3.4.1 Intelligent Pattern Recognition
The orchestrator should recognize:

- **Compound requests**: "analyze X AND implement Y"
- **Sequential tasks**: "first do X, then do Y"
- **Conditional tasks**: "if X is found, then do Y"
- **Iterative tasks**: "for each file, analyze and document"
- **Complex dependencies**: "analyze A and B, then based on findings, implement C"

#### 3.4.2 Automatic Agent Selection
Based on task requirements, automatically select the best available agent:

```python
def select_best_agent(task: Task, available_agents: List[AgentInfo]) -> str:
    """
    Select the most appropriate agent for a task based on:
    1. Exact match with specialized agents
    2. Capability overlap score
    3. Agent availability and load
    4. Historical performance metrics
    """
    # Priority 1: Exact specialist match
    if task.type == "security" and "security-auditor" in available_agents:
        return "security-auditor"
    
    # Priority 2: Capability match
    best_match = find_best_capability_match(task.requirements, available_agents)
    if best_match.score > 0.8:
        return best_match.agent
    
    # Priority 3: Generic agent with custom prompt
    return create_custom_agent_prompt(task)
```

---

## 4. Technical Requirements

### 4.1 Architecture Changes

#### 4.1.1 New Components
```
src/maos/core/
├── intelligent_decomposer.py      # New Claude-powered decomposer
├── agent_discovery.py              # Dynamic agent discovery
├── orchestrator_agent.py           # Dedicated orchestrator agent
└── decomposition_visualizer.py     # UI for showing reasoning
```

#### 4.1.2 Modified Components
- `task_decomposer_v2.py` → Delegates to `intelligent_decomposer.py`
- `claude_sdk_executor.py` → Uses discovered agents dynamically
- `orchestrator_v7.py` → Integrates new decomposer and visualizer

### 4.2 Integration Points

#### 4.2.1 Claude API Integration
```python
class IntelligentDecomposer:
    def __init__(self, claude_client):
        self.claude = claude_client
        self.system_prompt = """
        You are an expert task orchestrator for MAOS.
        Your role is to analyze user requests and create optimal
        multi-agent execution plans.
        
        Guidelines:
        1. Identify independent subtasks for parallelization
        2. Recognize dependencies between tasks
        3. Match tasks with available specialized agents
        4. Provide clear reasoning for your decisions
        """
    
    async def analyze_request(self, request: str, context: dict) -> DecompositionResult:
        response = await self.claude.complete(
            prompt=self._build_analysis_prompt(request, context),
            system=self.system_prompt,
            max_tokens=2000,
            temperature=0.3  # Lower temperature for consistent analysis
        )
        return self._parse_response(response)
```

### 4.3 Configuration

#### 4.3.1 Feature Flags
```yaml
# .maos/config.yaml
task_decomposition:
  mode: "intelligent"  # "intelligent" | "rule-based" | "hybrid"
  show_orchestrator_prompt: true
  show_reasoning: true
  show_execution_plan: true
  
  intelligent_mode:
    model: "claude-3-opus"  # Model for orchestration
    temperature: 0.3
    max_analysis_time: 10  # seconds
    cache_decompositions: true
    
  agent_discovery:
    scan_on_startup: true
    scan_interval: 300  # seconds
    sources:
      - ".claude/agents"
      - "claude-code-builtin"
      - "maos-templates"
```

---

## 5. User Experience

### 5.1 Command Line Interface

#### 5.1.1 New Commands
```bash
# Show available agents
maos agents list --discovered

# Test decomposition without execution
maos decompose "analyze code and add tests" --explain

# Show orchestrator prompt
maos orchestrate "build a web app" --show-prompt

# Use specific decomposition mode
maos orchestrate "complex task" --mode intelligent
```

#### 5.1.2 Interactive Mode
```
MAOS> analyze calculator.html and add graphing

🧠 Intelligent Task Analysis
═══════════════════════════════════════════════════════════

📝 Original Request:
"analyze calculator.html and add graphing"

🤖 Orchestrator Analysis:
[Claude is analyzing your request...]

📊 Discovered 5 available agents:
• @security-auditor (specialized)
• @reviewer (specialized)  
• analyst-001 (custom)
• developer-001 (custom)
• general-purpose (default)

🎯 Execution Plan Generated:

Phase 1 - Parallel Execution (2 agents):
┌─────────────────────────────────────────┐
│ Agent: analyst-001                      │
│ Task: Analyze calculator.html structure │
│ Duration: ~5 minutes                    │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ Agent: researcher-001                   │
│ Task: Research JS graphing libraries    │
│ Duration: ~3 minutes                    │
└─────────────────────────────────────────┘

Phase 2 - Sequential Execution (1 agent):
┌─────────────────────────────────────────┐
│ Agent: developer-001                    │
│ Task: Implement graphing feature        │
│ Dependencies: Phase 1 completion        │
│ Duration: ~10 minutes                   │
└─────────────────────────────────────────┘

View orchestrator reasoning? [y/N]: y

[Shows detailed reasoning...]

Proceed with execution? [Y/n]:
```

---

## 6. Implementation Plan

### 6.1 Phase 1: Foundation (Week 1)
- [ ] Implement agent discovery system
- [ ] Create orchestrator agent with Claude integration
- [ ] Build decomposition result parser

### 6.2 Phase 2: Intelligence (Week 2)
- [ ] Develop intelligent analysis prompts
- [ ] Implement reasoning extraction
- [ ] Create execution plan optimizer

### 6.3 Phase 3: Transparency (Week 3)
- [ ] Build visualization components
- [ ] Add prompt display features
- [ ] Implement reasoning explanations

### 6.4 Phase 4: Integration (Week 4)
- [ ] Integrate with existing orchestrator
- [ ] Add configuration options
- [ ] Implement caching and optimization

---

## 7. Testing Strategy

### 7.1 Test Scenarios

#### 7.1.1 Compound Request Tests
```python
test_cases = [
    {
        "input": "analyze security vulnerabilities AND fix them",
        "expected_agents": ["security-auditor", "developer"],
        "expected_parallel": True
    },
    {
        "input": "read all files, then create documentation",
        "expected_agents": ["analyst", "documentation"],
        "expected_parallel": False
    },
    {
        "input": "test the API and the UI and the database",
        "expected_agents": ["tester", "tester", "tester"],
        "expected_parallel": True
    }
]
```

### 7.2 Performance Benchmarks
- Decomposition time: < 2 seconds for 95% of requests
- Agent discovery: < 500ms on startup
- Orchestrator reasoning: < 3 seconds

---

## 8. Success Criteria

### 8.1 Acceptance Criteria
- [ ] Successfully decomposes 90% of compound requests into multiple tasks
- [ ] Discovers and utilizes all available Claude Code agents
- [ ] Shows complete orchestrator reasoning to users
- [ ] Reduces single-agent execution for complex tasks by 75%
- [ ] Maintains backward compatibility with rule-based mode

### 8.2 Launch Criteria
- [ ] All test scenarios pass
- [ ] Performance benchmarks met
- [ ] Documentation complete
- [ ] User feedback incorporated from beta testing

---

## 9. Future Enhancements

### 9.1 Version 2.0 Features
- **Learning System**: Learn from successful decompositions
- **User Preferences**: Remember user's preferred decomposition styles
- **Agent Performance Tracking**: Select agents based on historical success
- **Custom Orchestrator Prompts**: Allow users to customize orchestrator behavior
- **Multi-Model Support**: Use different models for different complexity levels

### 9.2 Long-term Vision
- **Self-Improving System**: Orchestrator learns from execution results
- **Agent Marketplace**: Download and share custom agents
- **Visual Pipeline Builder**: GUI for creating execution plans
- **Distributed Orchestration**: Multiple orchestrators for massive tasks

---

## 10. Appendix

### 10.1 Example Orchestrator Prompt Template
```python
ORCHESTRATOR_PROMPT = """
You are an intelligent task orchestrator for MAOS (Multi-Agent Orchestration System).

USER REQUEST:
{user_request}

AVAILABLE AGENTS:
{agent_list}

PROJECT CONTEXT:
{context}

INSTRUCTIONS:
1. Analyze the user request to identify distinct subtasks
2. Determine which tasks can run in parallel (no dependencies)
3. Identify task dependencies and create execution phases
4. Assign the most appropriate agent to each task
5. Provide reasoning for your decomposition choices

OUTPUT FORMAT:
{
  "analysis": {
    "user_intent": "...",
    "identified_tasks": [...],
    "complexity": "low|medium|high"
  },
  "execution_plan": {
    "phases": [...]
  },
  "reasoning": "..."
}
"""
```

### 10.2 Sample Decomposition Results

#### Simple Request
**Input:** "test my code"
**Output:** Single agent (tester) execution

#### Compound Request
**Input:** "analyze security vulnerabilities and fix critical issues"
**Output:** 
- Phase 1: security-auditor (analysis)
- Phase 2: developer (fixes based on findings)

#### Complex Request
**Input:** "understand the entire codebase, create documentation, add tests, and improve performance"
**Output:**
- Phase 1 (Parallel): analyst (codebase), performance-analyzer (bottlenecks)
- Phase 2 (Parallel): documentation (based on analysis), tester (create tests)
- Phase 3: developer (performance improvements)

---

**Document Status:** Ready for Review  
**Next Steps:** Technical design review and approval  
**Target Release:** MAOS v0.9.0