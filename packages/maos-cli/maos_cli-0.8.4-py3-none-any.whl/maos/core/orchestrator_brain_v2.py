"""
Orchestrator Brain v2 - Using Claude Code Subagents Correctly.

This version creates subagent definition files and delegates work through
Claude Code's Task tool instead of trying to spawn CLI processes.
"""

import asyncio
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from uuid import uuid4
from dataclasses import dataclass, field
from enum import Enum
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table
from rich.panel import Panel

from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError, OrchestrationError
from ..interfaces.sqlite_persistence import SqlitePersistence
from .task_decomposer_v2 import EnhancedTaskDecomposer, TaskPlan, SubTask, AgentProposal
from .session_manager_v2 import SessionManagerV2
from .claude_subagent_manager import ClaudeSubagentManager, ClaudeSubagent
from .agent_message_bus import AgentMessageBus, MessageType
from .execution_explainer import ExecutionExplainer


class OrchestratorState(Enum):
    """States of the orchestrator."""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    MONITORING = "monitoring"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class SubagentExecution:
    """Tracks execution of a subagent on a task."""
    agent_id: str
    agent_name: str
    agent_file: str
    task: SubTask
    status: str = "pending"
    progress: float = 0.0
    result: Optional[Dict] = None
    errors: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class OrchestratorBrainV2:
    """
    Central brain for orchestrating Claude Code subagents.
    
    This version correctly uses Claude Code's subagent system by:
    1. Creating subagent definition files in .claude/agents/
    2. Delegating work through Claude Code's Task tool
    3. Tracking progress through the database
    """
    
    def __init__(
        self,
        db: SqlitePersistence,
        console: Optional[Console] = None,
        auto_approve: bool = False,
        verbose_mode: bool = True,
        project_path: str = "."
    ):
        """
        Initialize orchestrator brain v2.
        
        Args:
            db: Database for persistence
            console: Rich console for output
            auto_approve: Auto-approve agent proposals
            verbose_mode: Show detailed explanations
            project_path: Path to project root
        """
        self.db = db
        self.console = console or Console()
        self.auto_approve = auto_approve
        self.verbose_mode = verbose_mode
        self.project_path = project_path
        
        self.logger = MAOSLogger("orchestrator_brain_v2")
        
        # Core components
        self.task_decomposer = EnhancedTaskDecomposer(db)
        self.session_manager = SessionManagerV2(db, project_path)
        self.subagent_manager = ClaudeSubagentManager(project_path)
        self.message_bus = AgentMessageBus(db, None)  # No session manager needed
        self.explainer = ExecutionExplainer(self.console)
        
        # State tracking
        self.state = OrchestratorState.IDLE
        self.current_plan = None
        self.subagent_executions: Dict[str, SubagentExecution] = {}
        self.created_subagents: List[str] = []
        
        # For Task tool integration
        self._delegation_prompts: List[str] = []
    
    async def start(self):
        """Start the orchestrator brain."""
        await self.db.initialize()
        await self.message_bus.start()
        self.logger.logger.info("Orchestrator brain v2 started")
    
    async def stop(self):
        """Stop the orchestrator brain and clean up."""
        # Clean up created subagent files
        for agent_name in self.created_subagents:
            self.subagent_manager.delete_subagent(agent_name)
        
        await self.message_bus.stop()
        await self.session_manager.shutdown()
        await self.db.close()
        self.logger.logger.info("Orchestrator brain v2 stopped")
    
    async def process_request(
        self,
        user_request: str,
        max_agents: int = 10
    ) -> Dict[str, Any]:
        """
        Process a user request by creating subagents and delegation prompts.
        
        Args:
            user_request: Natural language request
            max_agents: Maximum agents to create
            
        Returns:
            Orchestration plan with delegation instructions
        """
        self.state = OrchestratorState.PLANNING
        
        try:
            # Explain what we're doing if verbose
            if self.verbose_mode:
                self.explainer.explain_request_processing(user_request)
            
            # Decompose task
            self.console.print("[blue]Analyzing request and creating task plan...[/blue]")
            task_plan = await self.task_decomposer.decompose(user_request)
            
            # Show task decomposition explanation
            if task_plan.explanation:
                self.console.print(f"[cyan]Task Understanding: {task_plan.explanation}[/cyan]")
            
            # Generate agent proposal
            self.console.print("[blue]Determining agent allocation...[/blue]")
            agent_proposal = await self.task_decomposer.suggest_agents(task_plan)
            
            # Check agent limit
            if agent_proposal.new_agents + agent_proposal.reused_agents > max_agents:
                self.console.print(f"[red]Error: Request would require {agent_proposal.new_agents + agent_proposal.reused_agents} agents, but limit is {max_agents}[/red]")
                return None
            
            # Get execution order (batches)
            execution_order = task_plan.get_execution_order()
            
            # Explain batches if verbose
            if self.verbose_mode:
                self.explainer.explain_batches(execution_order)
            
            # Create subagents for the tasks
            await self._create_subagents(task_plan, agent_proposal)
            
            # Generate delegation plan
            delegation_plan = await self._create_delegation_plan(task_plan, execution_order)
            
            # Show the plan
            if self.verbose_mode:
                self._display_delegation_plan(delegation_plan)
            
            # Get approval
            if not self.auto_approve:
                if not Confirm.ask("\nProceed with this plan?"):
                    return None
            
            self.state = OrchestratorState.IDLE
            
            return {
                "status": "ready",
                "task_plan": task_plan,
                "agent_proposal": agent_proposal,
                "delegation_plan": delegation_plan,
                "created_subagents": self.created_subagents,
                "instruction": "Execute the delegation prompts using Claude Code's Task tool"
            }
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "process_request"})
            self.state = OrchestratorState.ERROR
            self.console.print(f"[red]Error processing request: {e}[/red]")
            return None
    
    async def _create_subagents(self, task_plan: TaskPlan, agent_proposal: AgentProposal):
        """Create subagent definition files for the tasks."""
        self.console.print("[blue]Creating Claude Code subagents...[/blue]")
        
        for suggestion in agent_proposal.suggestions:
            if suggestion.is_new:
                # Create new subagent
                agent_name = suggestion.agent_name
                task = suggestion.assigned_task
                
                # Determine task type
                task_type = task.task_type.value if task.task_type else "general"
                
                # Create subagent with appropriate configuration
                subagent = ClaudeSubagent(
                    name=agent_name,
                    description=f"{suggestion.agent_type} agent. {suggestion.role_description}. Task: {task.description}",
                    system_prompt=f"""You are {agent_name}, a specialized {suggestion.agent_type} agent.

Role: {suggestion.role_description}

Your specific task: {task.description}

{task.specific_instructions if task.specific_instructions else ''}

Approach:
1. Understand the requirements fully
2. Plan your approach
3. Execute systematically
4. Verify your results
5. Report clearly

Work autonomously to complete your assigned task. If you need to coordinate with other agents,
use clear communication about your findings and needs.""",
                    tools=suggestion.capabilities if suggestion.capabilities else None
                )
                
                # Create the subagent file
                agent_file = self.subagent_manager.create_subagent(subagent)
                
                # Track the creation
                self.created_subagents.append(agent_name)
                
                # Store in database
                agent_id = str(uuid4())
                await self.db.create_agent(
                    agent_id,
                    agent_name,
                    suggestion.agent_type,
                    suggestion.capabilities
                )
                
                # Track execution
                self.subagent_executions[agent_id] = SubagentExecution(
                    agent_id=agent_id,
                    agent_name=agent_name,
                    agent_file=str(agent_file),
                    task=task,
                    status="created",
                    started_at=datetime.now()
                )
                
                self.console.print(f"  [green]✓[/green] Created subagent: {agent_name}")
                
            else:
                # Reuse existing agent (update its task)
                self.console.print(f"  [cyan]↻[/cyan] Reusing: {suggestion.agent_name}")
    
    async def _create_delegation_plan(self, task_plan: TaskPlan, execution_order: List[List[SubTask]]) -> Dict:
        """Create a plan for delegating work to subagents."""
        delegation_plan = {
            "batches": [],
            "total_tasks": len(task_plan.subtasks),
            "parallel_possible": task_plan.parallel_execution_possible
        }
        
        for batch_num, batch in enumerate(execution_order, 1):
            batch_info = {
                "batch_number": batch_num,
                "tasks": [],
                "delegation_prompt": "",
                "parallel": len(batch) > 1
            }
            
            # Build delegation prompt for this batch
            if len(batch) == 1:
                # Single task
                task = batch[0]
                agent_name = task.assigned_agent or f"agent-{batch_num}"
                prompt = f"Use the {agent_name} subagent to: {task.description}"
                
                batch_info["tasks"].append({
                    "description": task.description,
                    "agent": agent_name
                })
                batch_info["delegation_prompt"] = prompt
                
            else:
                # Multiple tasks in parallel
                prompts = []
                for task in batch:
                    agent_name = task.assigned_agent or f"agent-{batch_num}-{len(prompts)}"
                    prompts.append(f"- Use the {agent_name} subagent to: {task.description}")
                    
                    batch_info["tasks"].append({
                        "description": task.description,
                        "agent": agent_name
                    })
                
                batch_info["delegation_prompt"] = "Execute these tasks in parallel:\n" + "\n".join(prompts)
            
            delegation_plan["batches"].append(batch_info)
            self._delegation_prompts.append(batch_info["delegation_prompt"])
        
        return delegation_plan
    
    def _display_delegation_plan(self, delegation_plan: Dict):
        """Display the delegation plan to the user."""
        self.console.print("\n[bold cyan]Delegation Plan:[/bold cyan]")
        
        for batch in delegation_plan["batches"]:
            panel_content = f"""
[yellow]Batch {batch['batch_number']}[/yellow] {'(Parallel)' if batch['parallel'] else '(Sequential)'}

Tasks:"""
            for task in batch["tasks"]:
                panel_content += f"\n  • {task['agent']}: {task['description'][:50]}..."
            
            panel_content += f"\n\n[dim]Delegation prompt:[/dim]\n{batch['delegation_prompt']}"
            
            self.console.print(Panel(panel_content, border_style="blue"))
    
    def get_delegation_prompts(self) -> List[str]:
        """
        Get the delegation prompts to execute with Claude Code's Task tool.
        
        Returns:
            List of prompts to execute
        """
        return self._delegation_prompts
    
    async def execute_with_task_tool(self) -> Dict[str, Any]:
        """
        Generate instructions for executing the plan with Claude Code's Task tool.
        
        Returns:
            Execution instructions
        """
        if not self._delegation_prompts:
            return {"error": "No delegation prompts available. Run process_request first."}
        
        instructions = {
            "method": "Claude Code Task Tool",
            "steps": []
        }
        
        for i, prompt in enumerate(self._delegation_prompts, 1):
            instructions["steps"].append({
                "step": i,
                "action": "Execute with Task tool",
                "prompt": prompt,
                "note": "Claude Code will handle parallel execution internally"
            })
        
        # Display instructions
        self.console.print("\n[bold green]Execution Instructions:[/bold green]")
        self.console.print("""
The subagents have been created in .claude/agents/

To execute the plan, use Claude Code's Task tool with these prompts:
""")
        
        for i, prompt in enumerate(self._delegation_prompts, 1):
            self.console.print(f"\n[cyan]Step {i}:[/cyan]")
            self.console.print(Panel(prompt, border_style="green"))
        
        return instructions
    
    async def track_progress(self, agent_name: str, status: str, progress: float = 0.0):
        """
        Track progress of a subagent execution.
        
        Args:
            agent_name: Name of the subagent
            status: Current status
            progress: Progress percentage
        """
        for exec in self.subagent_executions.values():
            if exec.agent_name == agent_name:
                exec.status = status
                exec.progress = progress
                
                if status == "completed":
                    exec.completed_at = datetime.now()
                    
                # Update database
                await self.db.update_task_progress(
                    exec.task.id,
                    progress,
                    status
                )
                
                break
    
    async def save_results(self, results: Dict[str, Any]):
        """
        Save execution results to the database.
        
        Args:
            results: Results from subagent execution
        """
        for agent_name, result in results.items():
            for exec in self.subagent_executions.values():
                if exec.agent_name == agent_name:
                    exec.result = result
                    
                    # Save to database
                    await self.db.complete_task(
                        exec.task.id,
                        result
                    )
                    
                    break
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status."""
        active_agents = []
        for exec in self.subagent_executions.values():
            if exec.status in ["created", "running"]:
                active_agents.append({
                    "agent_id": exec.agent_id,
                    "agent_name": exec.agent_name,
                    "task": exec.task.description[:50],
                    "progress": exec.progress,
                    "status": exec.status
                })
        
        return {
            "state": self.state.value,
            "created_subagents": self.created_subagents,
            "active_agents": active_agents,
            "total_agents": len(self.subagent_executions),
            "delegation_prompts_ready": len(self._delegation_prompts)
        }
    
    async def cleanup(self):
        """Clean up created subagents."""
        for agent_name in self.created_subagents:
            if self.subagent_manager.delete_subagent(agent_name):
                self.console.print(f"[dim]Cleaned up subagent: {agent_name}[/dim]")
        
        self.created_subagents.clear()
        self._delegation_prompts.clear()
        self.subagent_executions.clear()