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
{{
  "analysis": {{
    "user_intent": "Brief description of what the user wants",
    "identified_tasks": ["task1 description", "task2 description", ...],
    "complexity": "low|medium|high",
    "requires_parallel": true|false,
    "dependencies": {{"task2": ["task1"], ...}}
  }},
  "execution_plan": [
    {{
      "phase": 1,
      "parallel": true,
      "tasks": [
        {{
          "id": "task-001",
          "description": "Detailed task description",
          "agent_type": "analyst|developer|tester|researcher|documenter|security|reviewer",
          "assigned_agent": "specific-agent-name or generic",
          "estimated_duration": "X minutes",
          "dependencies": []
        }}
      ]
    }}
  ],
  "reasoning": "Explanation of why this decomposition was chosen",
  "orchestrator_prompt": "Instructions for the orchestrator agent"
}}"""
    
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
        """Call Claude to analyze the request with real-time visibility."""
        try:
            # Use Claude CLI for analysis
            # Note: Claude CLI has limited options
            cmd = [
                "claude",
                "-p"  # Print mode only - claude CLI is minimal
            ]
            
            # Add better prompt to ensure JSON output
            enhanced_prompt = f"""{prompt}

CRITICAL: You MUST respond with ONLY valid JSON in the exact format specified above. Do not include any explanation, markdown formatting, or additional text before or after the JSON. Start your response with {{ and end with }}.

Example of what your response should look like:
{{
  "analysis": {{
    "user_intent": "...",
    "identified_tasks": ["...", "..."],
    "complexity": "medium",
    "requires_parallel": true,
    "dependencies": {{}}
  }},
  "execution_plan": [{{
    "phase": 1,
    "parallel": true,
    "tasks": [{{
      "id": "task-001",
      "description": "...",
      "agent_type": "analyst",
      "assigned_agent": "generic",
      "estimated_duration": "5 minutes",
      "dependencies": []
    }}]
  }}],
  "reasoning": "...",
  "orchestrator_prompt": "..."
}}"""
            
            print("\n🤖 Calling Claude for intelligent analysis...")
            print("📡 Starting Claude process...")
            
            # Run Claude with the prompt
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            print("📝 Sending prompt to Claude...")
            
            # Send prompt to stdin and close it
            process.stdin.write(enhanced_prompt.encode())
            await process.stdin.drain()
            process.stdin.close()
            
            # Stream output in real-time
            print("⏳ Waiting for Claude's response (streaming output)...")
            
            output_lines = []
            error_lines = []
            line_count = 0
            
            # Set timeout for the entire operation
            timeout_seconds = 30
            start_time = asyncio.get_event_loop().time()
            
            # Read stdout and stderr in parallel with timeout
            async def read_stream(stream, lines_list, stream_name):
                while True:
                    try:
                        # Check timeout
                        if asyncio.get_event_loop().time() - start_time > timeout_seconds:
                            print(f"\n⏱️ Timeout reached ({timeout_seconds}s)")
                            break
                        
                        # Read line with short timeout
                        line = await asyncio.wait_for(stream.readline(), timeout=0.5)
                        if not line:
                            break
                        
                        decoded_line = line.decode().rstrip()
                        lines_list.append(decoded_line)
                        
                        # Show progress
                        if stream_name == "stdout":
                            # Show dots for progress but not the actual JSON (it's messy)
                            if decoded_line.strip():
                                if decoded_line.startswith('{') or '"' in decoded_line:
                                    print(".", end="", flush=True)
                                else:
                                    # Non-JSON output, show it
                                    print(f"\n   Claude: {decoded_line[:100]}...")
                        elif stream_name == "stderr" and decoded_line:
                            print(f"\n   ⚠️ Claude stderr: {decoded_line}")
                            
                    except asyncio.TimeoutError:
                        # No data available, check if process is done
                        if process.returncode is not None:
                            break
                        continue
                    except Exception as e:
                        print(f"\n   Error reading {stream_name}: {e}")
                        break
            
            # Read both streams in parallel
            await asyncio.gather(
                read_stream(process.stdout, output_lines, "stdout"),
                read_stream(process.stderr, error_lines, "stderr")
            )
            
            # Wait for process to complete (with timeout)
            try:
                await asyncio.wait_for(process.wait(), timeout=2)
            except asyncio.TimeoutError:
                print("\n⚠️ Claude process didn't finish cleanly, terminating...")
                process.terminate()
                await asyncio.sleep(1)
                if process.returncode is None:
                    process.kill()
            
            print(f"\n✅ Claude finished (exit code: {process.returncode})")
            
            # Check if we got output
            if not output_lines:
                print("❌ No output from Claude")
                return self._create_fallback_decomposition(prompt)
            
            # Combine output
            response_str = '\n'.join(output_lines).strip()
            
            if process.returncode != 0:
                error_str = '\n'.join(error_lines)
                logger.error(f"Claude analysis failed with code {process.returncode}: {error_str}")
                print(f"❌ Claude CLI failed (exit {process.returncode}): {error_str[:200]}")
                # Fall back to simple decomposition
                return self._create_fallback_decomposition(prompt)
            
            # Parse Claude's response
            print(f"📊 Received {len(response_str)} chars from Claude")
            logger.info(f"Claude response received: {len(response_str)} chars")
            return self._parse_claude_response(response_str, prompt)
            
        except asyncio.TimeoutError:
            print("\n❌ Claude timed out after 30 seconds")
            logger.error("Claude timed out")
            return self._create_fallback_decomposition(prompt)
        except Exception as e:
            logger.error(f"Error calling Claude: {e}")
            print(f"\n❌ Error calling Claude: {e}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_decomposition(prompt)
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from mixed text using multiple strategies."""
        import re
        
        # Strategy 1: Find complete JSON object with balanced braces
        brace_count = 0
        start_idx = -1
        end_idx = -1
        
        for i, char in enumerate(text):
            if char == '{':
                if brace_count == 0:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx != -1:
                    end_idx = i
                    break
        
        if start_idx != -1 and end_idx != -1:
            json_str = text[start_idx:end_idx + 1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Strategy 2: Look for JSON blocks between lines
        lines = text.strip().split('\n')
        json_lines = []
        in_json = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('{'):
                in_json = True
                json_lines = [stripped]
            elif in_json:
                json_lines.append(stripped)
                if stripped.endswith('}'):
                    break
        
        if json_lines:
            json_str = '\n'.join(json_lines)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Remove markdown formatting and try again
        # Remove ```json and ``` blocks
        cleaned_text = re.sub(r'```json\s*', '', text)
        cleaned_text = re.sub(r'```\s*', '', cleaned_text)
        cleaned_text = cleaned_text.strip()
        
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            pass
        
        # If all strategies fail, raise an error
        raise json.JSONDecodeError(f"Could not extract valid JSON from text: {text[:200]}...", text, 0)
    
    def _parse_claude_response(self, response_str: str, original_prompt: str) -> DecompositionResult:
        """Parse Claude's JSON response into DecompositionResult."""
        try:
            # First, try to parse the response directly as JSON
            try:
                result_json = json.loads(response_str)
                # If it has the expected structure, use it
                if "analysis" in result_json and "execution_plan" in result_json:
                    # Direct JSON response
                    pass  # Use result_json as-is
                elif "result" in result_json:
                    # Claude CLI wrapped format
                    result_text = result_json["result"]
                    result_json = self._extract_json_from_text(result_text)
                else:
                    # Some other format, try to extract
                    result_json = self._extract_json_from_text(response_str)
            except json.JSONDecodeError:
                # Not valid JSON, try to extract JSON from text
                result_json = self._extract_json_from_text(response_str)
            
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
            logger.error(f"Full raw response: {response_str}")
            
            # Try to show what we're trying to parse
            try:
                response_data = json.loads(response_str)
                if "result" in response_data:
                    logger.error(f"Claude result field: {response_data['result']}")
            except:
                logger.error(f"Response is not valid JSON at all: {response_str[:200]}")
            
            print(f"❌ Intelligent decomposition failed, falling back: {str(e)}")
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
        
        if not user_request:
            user_request = "Process user request"
        
        # Create multi-agent fallback decomposition
        # Look for key words to determine what types of agents to create
        request_lower = user_request.lower()
        
        tasks = []
        task_descriptions = []
        
        # Always start with analysis
        if "analyz" in request_lower or "understand" in request_lower or "explain" in request_lower:
            task_descriptions.append(("analyst", f"Analyze and understand: {user_request}"))
        
        # Check for development work
        if any(word in request_lower for word in ["implement", "code", "build", "create", "develop", "feature", "function"]):
            task_descriptions.append(("developer", f"Implement solution for: {user_request}"))
        
        # Check for web development
        if any(word in request_lower for word in ["web", "html", "css", "javascript", "frontend", "ui", "website"]):
            task_descriptions.append(("developer", f"Develop web interface for: {user_request}"))
        
        # Check for testing
        if "test" in request_lower:
            task_descriptions.append(("tester", f"Test and validate: {user_request}"))
        
        # Check for documentation
        if any(word in request_lower for word in ["document", "readme", "explain", "guide"]):
            task_descriptions.append(("documenter", f"Document solution for: {user_request}"))
        
        # If we didn't find specific indicators, create a basic analyst + developer combo
        if not task_descriptions:
            task_descriptions = [
                ("analyst", f"Analyze requirements: {user_request}"),
                ("developer", f"Implement solution: {user_request}")
            ]
        
        # Create tasks
        for i, (agent_type, description) in enumerate(task_descriptions):
            task_id = f"task-{uuid4().hex[:8]}"
            tasks.append({
                "id": task_id,
                "description": description,
                "agent_type": agent_type,
                "assigned_agent": "generic",
                "estimated_duration": "5 minutes",
                "dependencies": [] if i == 0 else [task_descriptions[0][0]]  # First task has no deps, others depend on first
            })
        
        analysis = DecompositionAnalysis(
            user_intent=f"Process user request: {user_request}",
            identified_tasks=[desc for _, desc in task_descriptions],
            complexity="medium",
            requires_parallel=len(task_descriptions) > 1,
            dependencies={} if len(tasks) <= 1 else {tasks[1]["id"]: [tasks[0]["id"]]}
        )
        
        # Create execution phases
        if len(tasks) == 1:
            phases = [ExecutionPhase(
                phase_number=1,
                parallel=False,
                tasks=tasks,
                estimated_duration="5 minutes"
            )]
        else:
            # First task in phase 1, rest in phase 2 (parallel)
            phases = [
                ExecutionPhase(
                    phase_number=1,
                    parallel=False,
                    tasks=[tasks[0]],
                    estimated_duration="5 minutes"
                ),
                ExecutionPhase(
                    phase_number=2,
                    parallel=True,
                    tasks=tasks[1:],
                    estimated_duration="5 minutes"
                )
            ]
        
        return DecompositionResult(
            analysis=analysis,
            execution_plan=phases,
            reasoning=f"Fallback: Claude unavailable, created {len(tasks)} specialized agents based on request keywords",
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