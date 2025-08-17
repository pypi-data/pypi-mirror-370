"""
Orchestrator V7 - Autonomous Multi-Agent Orchestration using Claude SDK.
This version actually runs Claude agents in parallel using the SDK.
"""

import asyncio
import uuid
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

from .claude_sdk_executor import ClaudeSDKExecutor, AgentExecution
from .task_decomposer_v2 import EnhancedTaskDecomposer
from .execution_explainer import ExecutionExplainer
from ..interfaces.sqlite_persistence import SqlitePersistence
from ..models.agent import Agent

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorResult:
    """Result from orchestrator execution"""
    success: bool
    agents_created: List[str]
    batch_results: List[List[Dict[str, Any]]]
    total_cost: float
    total_duration_ms: int
    summary: str
    orchestration_id: str  # Add this for tracking


@dataclass 
class OrchestrationSession:
    """Tracks a complete orchestration with all its agents"""
    orchestration_id: str
    request: str
    agents: List[Dict[str, Any]]  # Agent info with session IDs
    batches: List[List[str]]  # Agent IDs organized in batches
    created_at: str
    status: str  # "running", "completed", "paused"


class OrchestratorV7:
    """
    Autonomous orchestrator that actually runs Claude agents in parallel.
    Uses Claude SDK with --dangerously-skip-permissions for full automation.
    """
    
    def __init__(self, persistence: SqlitePersistence, api_key: Optional[str] = None):
        self.persistence = persistence
        self.executor = ClaudeSDKExecutor(api_key)
        self.decomposer = EnhancedTaskDecomposer(persistence)
        self.explainer = ExecutionExplainer()
        self.orchestration_sessions: Dict[str, OrchestrationSession] = {}
        
    async def orchestrate(self, request: str, auto_approve: bool = False) -> OrchestratorResult:
        """
        Orchestrate a complex task by decomposing it and running agents in parallel.
        
        Args:
            request: Natural language request
            auto_approve: If True, skip user confirmation
        """
        orchestration_id = str(uuid.uuid4())
        
        print("\n" + "="*60)
        print("🚀 AUTONOMOUS ORCHESTRATION MODE")
        print(f"Orchestration ID: {orchestration_id[:8]}")
        print("="*60)
        
        # Step 1: Decompose the task
        print("\n📋 Analyzing request...")
        task_plan = await self.decomposer.decompose(request)
        
        # Show task breakdown
        print(f"\nFound {len(task_plan.subtasks)} subtasks:")
        for i, task in enumerate(task_plan.subtasks, 1):
            print(f"  {i}. {task.description[:60]}...")
        
        # Step 2: Create batches for parallel execution
        batches = self._create_batches(task_plan.subtasks)
        print(f"\nOrganized into {len(batches)} batch(es) for execution")
        
        # Step 3: Show execution plan
        self._show_execution_plan(batches)
        
        # Step 4: Get user approval (unless auto-approve)
        if not auto_approve:
            response = input("\nProceed with autonomous execution? [y/n]: ")
            if response.lower() != 'y':
                print("Execution cancelled.")
                return OrchestratorResult(
                    success=False,
                    agents_created=[],
                    batch_results=[],
                    total_cost=0,
                    total_duration_ms=0,
                    summary="Execution cancelled by user",
                    orchestration_id=orchestration_id
                )
        
        # Step 5: Execute agents autonomously
        print("\n" + "="*60)
        print("🤖 STARTING AUTONOMOUS EXECUTION")
        print("="*60)
        
        # Convert to agent executions and track session info
        execution_batches = []
        all_agents = []
        agent_session_map = {}  # Maps agent_id to session info
        batch_structure = []  # Track batch organization
        
        for batch_idx, batch in enumerate(batches):
            batch_executions = []
            batch_agent_ids = []
            
            for task in batch:
                agent_id = f"{task.agent_type}-{uuid.uuid4().hex[:8]}"
                all_agents.append(agent_id)
                batch_agent_ids.append(agent_id)
                
                execution = AgentExecution(
                    agent_id=agent_id,
                    task=task.description,
                    system_prompt=self._get_system_prompt(task.agent_type),
                    allowed_tools=self._get_allowed_tools(task.agent_type),
                    max_turns=5
                )
                batch_executions.append(execution)
                
                # Track agent info for resumption
                agent_session_map[agent_id] = {
                    "task": task.description,
                    "agent_type": task.agent_type,
                    "batch_index": batch_idx,
                    "session_id": None  # Will be populated after execution
                }
                
                # Save to database
                await self._save_agent(agent_id, task)
            
            execution_batches.append(batch_executions)
            batch_structure.append(batch_agent_ids)
        
        # Execute all batches
        print(f"\nExecuting {len(all_agents)} agents across {len(execution_batches)} batch(es)...")
        print("Agents are running autonomously with --dangerously-skip-permissions\n")
        
        batch_results = await self.executor.execute_batches(execution_batches)
        
        # Update session IDs from results and save to database
        for batch_result in batch_results:
            for result in batch_result:
                agent_id = result["agent_id"]
                if agent_id in agent_session_map:
                    agent_session_map[agent_id]["session_id"] = result.get("session_id")
                    agent_session_map[agent_id]["success"] = result.get("success", False)
                    agent_session_map[agent_id]["cost"] = result.get("cost", 0)
                    
                    # Update agent with real session info
                    if result.get("session_id"):
                        await self.persistence.update_agent_session(
                            agent_id=agent_id,
                            session_id=result["session_id"],
                            process_id=result.get("process_id")
                        )
                        
                        # Update session with results
                        await self.persistence.update_session(
                            session_id=result["session_id"],
                            conversation_turn={
                                "role": "result",
                                "content": result.get("result", ""),
                                "timestamp": str(uuid.uuid4())
                            },
                            cost=result.get("cost", 0)
                        )
                    
                    # Update task status
                    task_id = f"task-{agent_id}"
                    if result.get("success"):
                        await self.persistence.complete_task(
                            task_id=task_id,
                            result={"success": True, "output": result.get("result", "")[:500]}
                        )
                    else:
                        await self.persistence.update_task_progress(
                            task_id=task_id,
                            progress=0,
                            status="failed"
                        )
        
        # Save orchestration to database with full relationships
        await self.persistence.save_orchestration(
            orchestration_id=orchestration_id,
            request=request,
            agents=all_agents,
            batches=batch_structure,
            status="running"
        )
        
        # Create inter-agent coordination messages
        for batch_idx, batch in enumerate(batch_structure):
            if len(batch) > 1:
                # Agents in same batch should coordinate
                for i, agent_id in enumerate(batch):
                    for j, other_agent in enumerate(batch):
                        if i != j:
                            await self.persistence.save_message(
                                from_agent=agent_id,
                                to_agent=other_agent,
                                message=f"Coordinating parallel execution in batch {batch_idx + 1}",
                                message_type="coordination"
                            )
        
        # Save orchestration session for resumption
        orchestration_session = OrchestrationSession(
            orchestration_id=orchestration_id,
            request=request,
            agents=list(agent_session_map.values()),
            batches=batch_structure,
            created_at=str(uuid.uuid4()),  # Should be timestamp
            status="completed"
        )
        self.orchestration_sessions[orchestration_id] = orchestration_session
        
        # Save session as checkpoint for backwards compatibility
        await self._save_orchestration_session(orchestration_session)
        
        # Step 6: Process results
        total_cost = 0
        total_duration = 0
        successful_agents = 0
        
        for batch_idx, batch_result in enumerate(batch_results, 1):
            print(f"\n📊 Batch {batch_idx} Results:")
            for result in batch_result:
                status = "✅" if result.get("success") else "❌"
                cost = result.get("cost", 0)
                duration = result.get("duration_ms", 0)
                
                total_cost += cost
                total_duration += duration
                if result.get("success"):
                    successful_agents += 1
                
                print(f"  {status} {result['agent_id']}")
                session_id = result.get('session_id', 'N/A')
                if session_id != 'N/A':
                    print(f"     Session: {session_id[:8]}...")
                else:
                    print(f"     Session: N/A")
                print(f"     Cost: ${cost:.4f} | Duration: {duration}ms | Turns: {result.get('num_turns', 0)}")
                
                if result.get("error"):
                    print(f"     Error: {result['error'][:500]}")
                else:
                    # Show the full result, not truncated
                    full_result = result.get("result", "No result")
                    print(f"\n     📝 Agent Response:\n")
                    print("     " + "-"*50)
                    # Display the full response with proper formatting
                    for line in full_result.split('\n')[:50]:  # Show first 50 lines
                        print(f"     {line}")
                    lines = full_result.split('\n')
                    if len(lines) > 50:
                        print(f"     ... ({len(lines) - 50} more lines)")
                    print("     " + "-"*50)
        
        # Step 7: Generate summary
        summary = f"""
Orchestration Complete!
━━━━━━━━━━━━━━━━━━━━━
• Orchestration ID: {orchestration_id[:8]}
• Agents: {successful_agents}/{len(all_agents)} successful
• Total Cost: ${total_cost:.4f}
• Total Duration: {total_duration}ms
• Batches Executed: {len(batch_results)}

To resume this entire orchestration:
  resume-all {orchestration_id[:8]}

To resume specific agents:
{self._generate_resume_commands(agent_session_map)}
"""
        print("\n" + "="*60)
        print(summary)
        print("="*60)
        
        # Update orchestration in database with completion info
        await self.persistence.update_orchestration(
            orchestration_id=orchestration_id,
            total_cost=total_cost,
            total_duration_ms=total_duration,
            successful_agents=successful_agents,
            total_agents=len(all_agents),
            status="completed",
            summary=summary
        )
        
        return OrchestratorResult(
            success=successful_agents > 0,
            agents_created=all_agents,
            batch_results=batch_results,
            total_cost=total_cost,
            total_duration_ms=total_duration,
            summary=summary,
            orchestration_id=orchestration_id
        )
    
    async def resume_orchestration(self, orchestration_id: str, new_request: str) -> OrchestratorResult:
        """
        Resume ALL agents from a previous orchestration with a new request.
        Maintains the same parallel structure and resumes each agent where it left off.
        """
        # Load orchestration session
        session = await self._load_orchestration_session(orchestration_id)
        if not session:
            # Try with short ID
            for oid, sess in self.orchestration_sessions.items():
                if oid.startswith(orchestration_id):
                    session = sess
                    break
        
        if not session:
            print(f"❌ Orchestration {orchestration_id} not found")
            return None
        
        print("\n" + "="*60)
        print(f"📂 RESUMING ORCHESTRATION {session.orchestration_id[:8]}")
        print(f"Original request: {session.request}")
        print(f"Resuming {len(session.agents)} agents in {len(session.batches)} batches")
        print("="*60)
        
        # Recreate execution batches with resume sessions
        execution_batches = []
        
        for batch_idx, batch_agent_ids in enumerate(session.batches):
            batch_executions = []
            print(f"\n📦 Batch {batch_idx + 1}:")
            
            for agent_info in session.agents:
                if agent_info.get("batch_index") == batch_idx:
                    agent_id = f"resumed-{agent_info['session_id'][:8]}"
                    print(f"  • Resuming {agent_info['agent_type']} (session: {agent_info['session_id'][:8]})")
                    
                    execution = AgentExecution(
                        agent_id=agent_id,
                        task=new_request,  # New task for all agents
                        session_id=agent_info["session_id"],  # Resume with this session
                        system_prompt=self._get_system_prompt(agent_info["agent_type"]),
                        allowed_tools=self._get_allowed_tools(agent_info["agent_type"]),
                        max_turns=5
                    )
                    batch_executions.append(execution)
            
            if batch_executions:
                execution_batches.append(batch_executions)
        
        # Execute all batches with resumed sessions
        print(f"\n🔄 Resuming execution with new request: '{new_request[:50]}...'")
        batch_results = await self.executor.execute_batches(execution_batches)
        
        # Process results (similar to orchestrate)
        total_cost = 0
        total_duration = 0
        successful_agents = 0
        
        for batch_idx, batch_result in enumerate(batch_results, 1):
            print(f"\n📊 Batch {batch_idx} Results:")
            for result in batch_result:
                status = "✅" if result.get("success") else "❌"
                cost = result.get("cost", 0)
                duration = result.get("duration_ms", 0)
                
                total_cost += cost
                total_duration += duration
                if result.get("success"):
                    successful_agents += 1
                
                print(f"  {status} {result['agent_id']}")
                print(f"     Cost: ${cost:.4f} | Duration: {duration}ms")
        
        summary = f"""
Resumed Orchestration Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Original ID: {session.orchestration_id[:8]}
• Agents Resumed: {len(session.agents)}
• Successful: {successful_agents}/{len(session.agents)}
• Total Cost: ${total_cost:.4f}
• Total Duration: {total_duration}ms
"""
        print("\n" + "="*60)
        print(summary)
        print("="*60)
        
        return OrchestratorResult(
            success=successful_agents > 0,
            agents_created=[a["agent_id"] for batch in batch_results for a in batch],
            batch_results=batch_results,
            total_cost=total_cost,
            total_duration_ms=total_duration,
            summary=summary,
            orchestration_id=session.orchestration_id
        )
    
    async def resume_single_agent(self, session_id: str, new_request: str) -> Dict[str, Any]:
        """Resume a single agent conversation with a new request"""
        print(f"\n📂 Resuming single agent session {session_id[:8]}...")
        result = await self.executor.resume_agent(session_id, new_request)
        
        if result.get("success"):
            print(f"✅ Session resumed successfully")
            print(f"   Cost: ${result.get('cost', 0):.4f}")
            print(f"   Result: {result.get('result', '')[:200]}...")
        else:
            print(f"❌ Failed to resume session: {result.get('error')}")
        
        return result
    
    async def list_orchestrations(self) -> List[OrchestrationSession]:
        """List all saved orchestrations"""
        # In production, this would load from database
        return list(self.orchestration_sessions.values())
    
    def _create_batches(self, tasks: List[Any]) -> List[List[Any]]:
        """Create batches of tasks that can run in parallel"""
        # Simple batching - tasks with no dependencies go in same batch
        # This can be enhanced with dependency analysis
        batch_size = 3  # Max agents per batch
        batches = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batches.append(batch)
        
        return batches
    
    def _show_execution_plan(self, batches: List[List[Any]]):
        """Display the execution plan"""
        print("\n📋 Execution Plan:")
        print("─" * 40)
        
        for batch_idx, batch in enumerate(batches, 1):
            print(f"\nBatch {batch_idx} (Parallel):")
            for task in batch:
                print(f"  • {task.agent_type}: {task.description[:50]}...")
    
    def _get_system_prompt(self, agent_type: str) -> str:
        """Get appropriate system prompt for agent type"""
        prompts = {
            "analyst": "You are a code analysis expert. Analyze thoroughly and provide insights.",
            "developer": "You are an expert developer. Write clean, efficient, well-tested code.",
            "tester": "You are a testing specialist. Write comprehensive tests with good coverage.",
            "reviewer": "You are a code reviewer. Check for bugs, security issues, and best practices.",
            "architect": "You are a software architect. Design scalable, maintainable solutions.",
            "security": "You are a security expert. Identify vulnerabilities and suggest fixes.",
        }
        
        # Try to match agent type
        for key, prompt in prompts.items():
            if key in agent_type.lower():
                return prompt
        
        return "You are an expert AI assistant. Complete the task thoroughly and efficiently."
    
    def _get_allowed_tools(self, agent_type: str) -> List[str]:
        """Get appropriate tools for agent type"""
        # Security agents shouldn't write/edit
        if "security" in agent_type.lower() or "audit" in agent_type.lower():
            return ["Read", "Grep", "Glob", "WebSearch"]
        
        # Analysts mainly read
        if "analyst" in agent_type.lower() or "review" in agent_type.lower():
            return ["Read", "Grep", "Glob", "WebSearch", "Bash"]
        
        # Developers need full access
        return ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "WebSearch"]
    
    def _generate_resume_commands(self, agent_session_map: Dict[str, Dict]) -> str:
        """Generate resume commands for individual agents"""
        commands = []
        for agent_id, info in agent_session_map.items():
            if info.get("session_id") and info.get("success"):
                commands.append(f"  resume {info['session_id'][:8]} # {agent_id}")
        return "\n".join(commands[:3]) + ("\n  ..." if len(commands) > 3 else "")
    
    async def _save_agent(self, agent_id: str, task: Any):
        """Save agent and related entities to database"""
        try:
            print(f"💾 Saving agent {agent_id} to database...")
            
            # 1. Create the agent
            await self.persistence.create_agent(
                agent_id=agent_id,
                name=agent_id,
                agent_type=task.agent_type,
                capabilities=[task.agent_type],
                metadata={"task": task.description}
            )
            
            # 2. Create a task for this agent's work
            task_id = f"task-{agent_id}"
            await self.persistence.create_task(
                task_id=task_id,
                description=task.description,
                assigned_agents=[agent_id]
            )
            
            # 3. Create initial session (will be updated with real session_id later)
            session_id = f"session-{agent_id}-pending"
            await self.persistence.create_session(
                session_id=session_id,
                agent_id=agent_id,
                task=task.description
            )
            
            print(f"✅ Agent {agent_id} with task and session saved successfully")
        except Exception as e:
            print(f"❌ Failed to save agent {agent_id}: {e}")
            import traceback
            traceback.print_exc()
    
    async def _save_orchestration_session(self, session: OrchestrationSession):
        """Save orchestration session to database"""
        try:
            print(f"💾 Saving orchestration session {session.orchestration_id[:8]} to database...")
            # Store as a special checkpoint
            checkpoint_data = {
                "type": "orchestration_session",
                "orchestration_id": session.orchestration_id,
                "request": session.request,
                "agents": session.agents,
                "batches": session.batches,
                "status": session.status
            }
            await self.persistence.save_checkpoint(
                session.orchestration_id,  # checkpoint_id
                f"orchestration_{session.orchestration_id[:8]}",  # name
                checkpoint_data  # checkpoint_data
            )
            print(f"✅ Orchestration session {session.orchestration_id[:8]} saved successfully")
        except Exception as e:
            print(f"❌ Failed to save orchestration session: {e}")
            import traceback
            traceback.print_exc()
    
    async def _load_orchestration_session(self, orchestration_id: str) -> Optional[OrchestrationSession]:
        """Load orchestration session from database"""
        # First try to load from orchestrations table
        orchestration = await self.persistence.get_orchestration(orchestration_id)
        if orchestration:
            # Need to reconstruct agent session map from checkpoint
            checkpoint_name = f"orchestration_{orchestration_id[:8]}"
            checkpoint = await self.persistence.load_checkpoint(checkpoint_name)
            
            if checkpoint:
                return OrchestrationSession(
                    orchestration_id=orchestration["id"],
                    request=orchestration["request"],
                    agents=checkpoint["agents"],  # Get detailed agent info from checkpoint
                    batches=orchestration["batches"],
                    created_at=orchestration.get("created_at", ""),
                    status=orchestration["status"]
                )
        
        # Fallback to checkpoint only (for backwards compatibility)
        checkpoint_name = f"orchestration_{orchestration_id[:8]}"
        checkpoint = await self.persistence.load_checkpoint(checkpoint_name)
        
        if checkpoint:
            return OrchestrationSession(
                orchestration_id=checkpoint["orchestration_id"],
                request=checkpoint["request"],
                agents=checkpoint["agents"],
                batches=checkpoint["batches"],
                created_at=checkpoint.get("created_at", ""),
                status=checkpoint["status"]
            )
        return None