"""
Intelligent Task Decomposer - Uses Claude for natural language understanding
"""

import asyncio
import json
import subprocess
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import logging
from uuid import uuid4

from .agent_discovery import AgentDiscovery, AgentInfo
from .task_decomposer_v2 import TaskPlan, SubTask, TaskType
from ..interfaces.sqlite_persistence import SqlitePersistence

logger = logging.getLogger(__name__)


@dataclass
class DecompositionAnalysis:
    """Analysis result from the orchestrator"""
    user_intent: str
    identified_tasks: List[str]
    complexity: str  # 'low', 'medium', 'high'
    requires_parallel: bool
    dependencies: Dict[str, List[str]]  # task_id -> [dependency_ids]


@dataclass
class ExecutionPhase:
    """A phase in the execution plan"""
    phase_number: int
    parallel: bool
    tasks: List[Dict[str, Any]]
    estimated_duration: str


@dataclass
class DecompositionResult:
    """Complete decomposition result from Claude"""
    analysis: DecompositionAnalysis
    execution_plan: List[ExecutionPhase]
    reasoning: str
    orchestrator_prompt: str
    raw_response: Optional[str] = None


class IntelligentDecomposer:
    """
    Uses Claude to intelligently decompose user requests into multi-agent tasks.
    """
    
    def __init__(self, persistence: Optional[SqlitePersistence] = None):
        """
        Initialize the intelligent decomposer.
        
        Args:
            persistence: Database for storing decomposition results
        """
        self.persistence = persistence
        self.agent_discovery = AgentDiscovery()
        self.discovered_agents: List[AgentInfo] = []
        self._orchestrator_prompt_template = self._load_orchestrator_prompt()
        
    def _load_orchestrator_prompt(self) -> str:
        """Load the orchestrator prompt template."""
        return """You are an intelligent task orchestrator for MAOS (Multi-Agent Orchestration System).

USER REQUEST:
{user_request}

AVAILABLE AGENTS:
{agent_list}

PROJECT CONTEXT:
{context}

INSTRUCTIONS:
1. Analyze the user request to identify distinct subtasks
2. Look for compound requests (connected with AND, THEN, etc.)
3. Identify which tasks can run in parallel (no dependencies)
4. Identify task dependencies and create execution phases
5. Assign the most appropriate agent to each task based on their capabilities
6. Provide clear reasoning for your decomposition choices

IMPORTANT PATTERNS TO RECOGNIZE:
- "X AND Y" → Usually means two parallel tasks
- "First X, then Y" → Sequential tasks with dependency
- "For each X, do Y" → Iterative tasks
- "Analyze X and implement Y" → Analysis phase then implementation
- "Test X and Y and Z" → Multiple parallel testing tasks

OUTPUT FORMAT (valid JSON):
{
  "analysis": {
    "user_intent": "Brief description of what the user wants",
    "identified_tasks": ["task1 description", "task2 description", ...],
    "complexity": "low|medium|high",
    "requires_parallel": true|false,
    "dependencies": {"task2": ["task1"], ...}
  },
  "execution_plan": [
    {
      "phase": 1,
      "parallel": true,
      "tasks": [
        {
          "id": "task-001",
          "description": "Detailed task description",
          "agent_type": "analyst|developer|tester|researcher|documenter|security|reviewer",
          "assigned_agent": "specific-agent-name or generic",
          "estimated_duration": "X minutes",
          "dependencies": []
        }
      ]
    }
  ],
  "reasoning": "Explanation of why this decomposition was chosen",
  "orchestrator_prompt": "Instructions for the orchestrator agent"
}"""
    
    async def decompose(self, user_request: str, show_prompt: bool = True) -> Tuple[TaskPlan, DecompositionResult]:
        """
        Intelligently decompose a user request using Claude.
        
        Args:
            user_request: The user's natural language request
            show_prompt: Whether to show the orchestrator prompt to the user
            
        Returns:
            Tuple of (TaskPlan for compatibility, DecompositionResult with full details)
        """
        logger.info(f"Starting intelligent decomposition for: {user_request[:100]}...")
        
        # Step 1: Discover available agents
        if not self.discovered_agents:
            self.discovered_agents = await self.agent_discovery.scan_available_agents()
            logger.info(f"Discovered {len(self.discovered_agents)} agents")
        
        # Step 2: Build context
        context = await self._build_context()
        
        # Step 3: Create orchestrator prompt
        orchestrator_prompt = self._build_orchestrator_prompt(
            user_request, 
            self.discovered_agents,
            context
        )
        
        # Step 4: Show prompt to user if requested
        if show_prompt:
            self._display_orchestrator_prompt(user_request, orchestrator_prompt)
        
        # Step 5: Call Claude for analysis
        print("\n🧠 Analyzing request with Claude...")
        decomposition_result = await self._call_claude_orchestrator(orchestrator_prompt)
        
        # Step 6: Display reasoning
        self._display_reasoning(decomposition_result)
        
        # Step 7: Convert to TaskPlan for compatibility
        task_plan = self._convert_to_task_plan(decomposition_result, user_request)
        
        # Step 8: Save to database if available
        if self.persistence:
            await self._save_decomposition(user_request, decomposition_result)
        
        return task_plan, decomposition_result
    
    async def _build_context(self) -> Dict[str, Any]:
        """Build project context for the orchestrator."""
        context = {
            "project_type": "unknown",
            "files_present": [],
            "current_directory": str(Path.cwd()),
            "timestamp": datetime.now().isoformat()
        }
        
        # Check for common project files
        common_files = ["package.json", "requirements.txt", "Cargo.toml", "go.mod", 
                       "pom.xml", "build.gradle", "index.html", "calculator.html"]
        
        for file in common_files:
            if Path(file).exists():
                context["files_present"].append(file)
                
                # Infer project type
                if file == "package.json":
                    context["project_type"] = "node/javascript"
                elif file == "requirements.txt":
                    context["project_type"] = "python"
                elif file == "Cargo.toml":
                    context["project_type"] = "rust"
                elif file in ["index.html", "calculator.html"]:
                    context["project_type"] = "web"
        
        return context
    
    def _build_orchestrator_prompt(self, 
                                   user_request: str,
                                   agents: List[AgentInfo],
                                   context: Dict[str, Any]) -> str:
        """Build the complete prompt for Claude orchestrator."""
        
        # Format agent list
        agent_list = []
        for agent in agents:
            agent_str = f"- {agent.name} ({agent.source}): {agent.description}"
            if agent.capabilities:
                agent_str += f"\n  Capabilities: {', '.join(agent.capabilities[:5])}"
            agent_list.append(agent_str)
        
        # Format context
        context_str = json.dumps(context, indent=2)
        
        # Build prompt
        prompt = self._orchestrator_prompt_template.format(
            user_request=user_request,
            agent_list="\n".join(agent_list),
            context=context_str
        )
        
        return prompt
    
    async def _call_claude_orchestrator(self, prompt: str) -> DecompositionResult:
        """Call Claude to analyze the request."""
        try:
            # Use Claude CLI for analysis
            cmd = [
                "claude",
                "-p",  # Print mode
                "--output-format", "json",
                "--max-tokens", "2000",
                "--temperature", "0.3"  # Lower temperature for consistency
            ]
            
            # Run Claude with the prompt
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send prompt and get response
            stdout, stderr = await process.communicate(input=prompt.encode())
            
            if process.returncode != 0:
                logger.error(f"Claude analysis failed: {stderr.decode()}")
                # Fall back to simple decomposition
                return self._create_fallback_decomposition(prompt)
            
            # Parse Claude's response
            response_str = stdout.decode()
            return self._parse_claude_response(response_str, prompt)
            
        except Exception as e:
            logger.error(f"Error calling Claude: {e}")
            return self._create_fallback_decomposition(prompt)
    
    def _parse_claude_response(self, response_str: str, original_prompt: str) -> DecompositionResult:
        """Parse Claude's JSON response into DecompositionResult."""
        try:
            # Extract JSON from response
            response_data = json.loads(response_str)
            
            # Handle different response formats
            if "result" in response_data:
                # Claude CLI format
                result_text = response_data["result"]
                
                # Try to extract JSON from the result text
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result_json = json.loads(json_match.group())
                else:
                    # Try to parse the entire result as JSON
                    result_json = json.loads(result_text)
            else:
                result_json = response_data
            
            # Create DecompositionAnalysis
            analysis_data = result_json.get("analysis", {})
            analysis = DecompositionAnalysis(
                user_intent=analysis_data.get("user_intent", ""),
                identified_tasks=analysis_data.get("identified_tasks", []),
                complexity=analysis_data.get("complexity", "medium"),
                requires_parallel=analysis_data.get("requires_parallel", False),
                dependencies=analysis_data.get("dependencies", {})
            )
            
            # Create ExecutionPhases
            execution_phases = []
            for phase_data in result_json.get("execution_plan", []):
                phase = ExecutionPhase(
                    phase_number=phase_data.get("phase", 1),
                    parallel=phase_data.get("parallel", False),
                    tasks=phase_data.get("tasks", []),
                    estimated_duration=phase_data.get("estimated_duration", "5 minutes")
                )
                execution_phases.append(phase)
            
            # Create DecompositionResult
            return DecompositionResult(
                analysis=analysis,
                execution_plan=execution_phases,
                reasoning=result_json.get("reasoning", ""),
                orchestrator_prompt=result_json.get("orchestrator_prompt", original_prompt),
                raw_response=response_str
            )
            
        except Exception as e:
            logger.error(f"Error parsing Claude response: {e}")
            logger.debug(f"Raw response: {response_str[:500]}")
            return self._create_fallback_decomposition(original_prompt)
    
    def _create_fallback_decomposition(self, prompt: str) -> DecompositionResult:
        """Create a simple fallback decomposition when Claude is unavailable."""
        # Extract user request from prompt
        user_request = ""
        if "USER REQUEST:" in prompt:
            lines = prompt.split('\n')
            for i, line in enumerate(lines):
                if "USER REQUEST:" in line and i + 1 < len(lines):
                    user_request = lines[i + 1].strip()
                    break
        
        # Create simple single-task decomposition
        task_id = f"task-{uuid4().hex[:8]}"
        
        analysis = DecompositionAnalysis(
            user_intent="Process user request",
            identified_tasks=[user_request],
            complexity="medium",
            requires_parallel=False,
            dependencies={}
        )
        
        phase = ExecutionPhase(
            phase_number=1,
            parallel=False,
            tasks=[{
                "id": task_id,
                "description": user_request,
                "agent_type": "analyst",
                "assigned_agent": "generic",
                "estimated_duration": "5 minutes",
                "dependencies": []
            }],
            estimated_duration="5 minutes"
        )
        
        return DecompositionResult(
            analysis=analysis,
            execution_plan=[phase],
            reasoning="Fallback: Claude unavailable, creating single task",
            orchestrator_prompt=prompt
        )
    
    def _convert_to_task_plan(self, decomposition: DecompositionResult, user_request: str) -> TaskPlan:
        """Convert DecompositionResult to TaskPlan for compatibility."""
        subtasks = []
        
        for phase in decomposition.execution_plan:
            for task_data in phase.tasks:
                # Map agent_type to TaskType
                task_type_map = {
                    "analyst": TaskType.ANALYZE,
                    "developer": TaskType.IMPLEMENT,
                    "tester": TaskType.TEST,
                    "researcher": TaskType.ANALYZE,
                    "documenter": TaskType.EXPLAIN,
                    "security": TaskType.REVIEW,
                    "reviewer": TaskType.REVIEW
                }
                
                task_type = task_type_map.get(
                    task_data.get("agent_type", "analyst"),
                    TaskType.IMPLEMENT
                )
                
                subtask = SubTask(
                    id=task_data.get("id", str(uuid4())),
                    description=task_data.get("description", ""),
                    task_type=task_type,
                    dependencies=task_data.get("dependencies", []),
                    assigned_agent=task_data.get("assigned_agent"),
                    agent_type=task_data.get("agent_type", "analyst"),
                    required_capabilities=[]
                )
                subtasks.append(subtask)
        
        # Determine parallelization
        parallel_possible = any(phase.parallel for phase in decomposition.execution_plan)
        
        return TaskPlan(
            id=str(uuid4()),
            original_request=user_request,
            subtasks=subtasks,
            estimated_agents_needed=len(set(t.agent_type for t in subtasks)),
            parallel_execution_possible=parallel_possible,
            explanation=decomposition.reasoning
        )
    
    def _display_orchestrator_prompt(self, user_request: str, prompt: str):
        """Display the orchestrator prompt to the user."""
        print("\n" + "="*60)
        print("🤖 ORCHESTRATOR INSTRUCTIONS")
        print("="*60)
        print(f"\n📝 ORIGINAL USER REQUEST:")
        print(f'"{user_request}"')
        print(f"\n📋 ORCHESTRATOR ANALYSIS PROMPT:")
        print("-"*40)
        
        # Show abbreviated prompt (first part)
        lines = prompt.split('\n')[:20]
        for line in lines:
            print(f"  {line}")
        print("  ...")
        print("-"*40)
    
    def _display_reasoning(self, decomposition: DecompositionResult):
        """Display the orchestrator's reasoning."""
        print("\n" + "="*60)
        print("📊 ORCHESTRATOR ANALYSIS")
        print("="*60)
        
        print(f"\n🎯 User Intent: {decomposition.analysis.user_intent}")
        print(f"📈 Complexity: {decomposition.analysis.complexity}")
        print(f"⚡ Parallel Execution: {'Yes' if decomposition.analysis.requires_parallel else 'No'}")
        
        if decomposition.analysis.identified_tasks:
            print(f"\n📋 Identified {len(decomposition.analysis.identified_tasks)} Tasks:")
            for i, task in enumerate(decomposition.analysis.identified_tasks, 1):
                print(f"  {i}. {task}")
        
        print(f"\n💭 Reasoning:")
        # Wrap reasoning text
        words = decomposition.reasoning.split()
        line = ""
        for word in words:
            if len(line) + len(word) > 70:
                print(f"  {line}")
                line = word
            else:
                line = f"{line} {word}" if line else word
        if line:
            print(f"  {line}")
        
        print(f"\n📊 Execution Plan:")
        for phase in decomposition.execution_plan:
            phase_type = "Parallel" if phase.parallel else "Sequential"
            print(f"\n  Phase {phase.phase_number} ({phase_type}):")
            for task in phase.tasks:
                agent = task.get("assigned_agent", "generic")
                print(f"    • {task['description'][:50]}...")
                print(f"      Agent: {agent} | Duration: {task.get('estimated_duration', 'unknown')}")
    
    async def _save_decomposition(self, user_request: str, decomposition: DecompositionResult):
        """Save decomposition result to database."""
        if not self.persistence:
            return
        
        try:
            # Store as a checkpoint for recovery
            checkpoint_data = {
                "type": "intelligent_decomposition",
                "user_request": user_request,
                "analysis": asdict(decomposition.analysis),
                "execution_plan": [asdict(phase) for phase in decomposition.execution_plan],
                "reasoning": decomposition.reasoning,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.persistence.save_checkpoint(
                checkpoint_id=f"decomp-{uuid4().hex[:8]}",
                name=f"Decomposition: {user_request[:30]}",
                checkpoint_data=checkpoint_data
            )
        except Exception as e:
            logger.error(f"Failed to save decomposition: {e}")