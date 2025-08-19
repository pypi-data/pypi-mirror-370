"""
Orchestrator Brain - The central intelligence for MAOS orchestration.

Coordinates all agents, manages task distribution, and maintains global state.
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
from .session_manager import SessionManager
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
class ExecutionPlan:
    """Complete execution plan for a user request."""
    id: str
    task_plan: TaskPlan
    agent_proposal: AgentProposal
    execution_order: List[List[SubTask]]
    estimated_duration: float  # minutes
    estimated_cost: float  # USD
    
    def get_summary(self) -> str:
        """Get human-readable summary."""
        lines = []
        lines.append(f"Execution Plan {self.id[:8]}")
        lines.append(f"Original request: {self.task_plan.original_request}")
        lines.append(f"Subtasks: {len(self.task_plan.subtasks)}")
        lines.append(f"Agents needed: {self.agent_proposal.new_agents + self.agent_proposal.reused_agents}")
        lines.append(f"  • New: {self.agent_proposal.new_agents}")
        lines.append(f"  • Reused: {self.agent_proposal.reused_agents}")
        lines.append(f"Estimated duration: {self.estimated_duration:.1f} minutes")
        lines.append(f"Estimated cost: ${self.estimated_cost:.4f}")
        return "\n".join(lines)


@dataclass
class AgentExecution:
    """Tracks execution of an agent on a task."""
    agent_id: str
    agent_name: str
    process_id: str
    session_id: str
    task: SubTask
    status: str = "pending"
    progress: float = 0.0
    result: Optional[Dict] = None
    errors: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class OrchestratorBrain:
    """
    Central brain for orchestrating agent swarms.
    
    Responsibilities:
    - Task decomposition and planning
    - Agent allocation and spawning
    - Parallel execution management
    - Inter-agent coordination
    - Progress monitoring
    - State persistence and recovery
    """
    
    def __init__(
        self,
        db: SqlitePersistence,
        console: Optional[Console] = None,
        auto_approve: bool = False,
        verbose_mode: bool = True
    ):
        """
        Initialize orchestrator brain.
        
        Args:
            db: Database for persistence
            console: Rich console for output
            auto_approve: Auto-approve agent proposals
            verbose_mode: Show detailed explanations
        """
        self.db = db
        self.console = console or Console()
        self.auto_approve = auto_approve
        self.verbose_mode = verbose_mode
        
        self.logger = MAOSLogger("orchestrator_brain")
        
        # Core components
        self.task_decomposer = EnhancedTaskDecomposer(db)
        self.session_manager = SessionManager(db)
        self.message_bus = AgentMessageBus(db, self.session_manager)
        self.explainer = ExecutionExplainer(self.console)
        
        # State tracking
        self.state = OrchestratorState.IDLE
        self.current_plan: Optional[ExecutionPlan] = None
        self.agent_executions: Dict[str, AgentExecution] = {}
        self.active_sessions: Dict[str, str] = {}  # agent_id -> session_id
        
        # Monitoring
        self._monitor_task: Optional[asyncio.Task] = None
        self._monitor_interval = 2.0  # seconds
    
    async def start(self):
        """Start the orchestrator brain."""
        await self.db.initialize()
        await self.message_bus.start()
        self._monitor_task = asyncio.create_task(self._monitor_execution())
        self.logger.logger.info("Orchestrator brain started")
    
    async def stop(self):
        """Stop the orchestrator brain."""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        await self.message_bus.stop()
        await self.session_manager.shutdown()
        await self.db.close()
        self.logger.logger.info("Orchestrator brain stopped")
    
    async def process_request(
        self,
        user_request: str,
        max_agents: int = 10
    ) -> Optional[ExecutionPlan]:
        """
        Process a user request and create an execution plan.
        
        Args:
            user_request: Natural language request
            max_agents: Maximum agents to spawn
            
        Returns:
            Execution plan if approved, None otherwise
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
            
            # Get execution order
            execution_order = task_plan.get_execution_order()
            
            # Explain batches if verbose
            if self.verbose_mode:
                self.explainer.explain_batches(execution_order)
            
            # Estimate duration and cost
            estimated_duration = len(execution_order) * 2.0  # 2 minutes per batch
            estimated_cost = agent_proposal.new_agents * 0.05  # $0.05 per new agent
            
            # Create execution plan
            plan = ExecutionPlan(
                id=str(uuid4()),
                task_plan=task_plan,
                agent_proposal=agent_proposal,
                execution_order=execution_order,
                estimated_duration=estimated_duration,
                estimated_cost=estimated_cost
            )
            
            # Explain agent allocation if verbose
            if self.verbose_mode:
                agent_details = [
                    {
                        'name': s.agent_name,
                        'type': s.agent_type,
                        'task': s.assigned_task.description if s.assigned_task else '',
                        'is_new': s.is_new
                    }
                    for s in agent_proposal.suggestions
                ]
                self.explainer.explain_agent_allocation(
                    agent_proposal.new_agents,
                    agent_proposal.reused_agents,
                    agent_details
                )
            
            # Display and get approval
            if await self._get_approval(plan):
                self.current_plan = plan
                self.state = OrchestratorState.IDLE
                return plan
            else:
                self.state = OrchestratorState.IDLE
                return None
                
        except Exception as e:
            self.logger.log_error(e, {"operation": "process_request"})
            self.state = OrchestratorState.ERROR
            self.console.print(f"[red]Error processing request: {e}[/red]")
            return None
    
    async def _get_approval(self, plan: ExecutionPlan) -> bool:
        """
        Get user approval for execution plan.
        
        Args:
            plan: Execution plan to approve
            
        Returns:
            True if approved
        """
        # Display plan
        self.console.print("\n[bold cyan]Execution Plan:[/bold cyan]")
        self.console.print(Panel(plan.agent_proposal.get_summary(), title="Agent Allocation"))
        
        # Show execution batches
        table = Table(title="Execution Order")
        table.add_column("Batch", style="cyan")
        table.add_column("Tasks", style="white")
        table.add_column("Agents", style="green")
        
        for i, batch in enumerate(plan.execution_order, 1):
            tasks = "\n".join([task.description[:50] for task in batch])
            agents = "\n".join([task.assigned_agent or "TBD" for task in batch])
            table.add_row(f"Batch {i}", tasks, agents)
        
        self.console.print(table)
        
        # Show estimates
        self.console.print(f"\n[yellow]Estimated duration: {plan.estimated_duration:.1f} minutes[/yellow]")
        self.console.print(f"[yellow]Estimated cost: ${plan.estimated_cost:.4f}[/yellow]")
        
        # Get approval
        if self.auto_approve:
            self.console.print("[green]Auto-approving plan[/green]")
            return True
        else:
            return Confirm.ask("\nProceed with this plan?")
    
    async def execute_plan(
        self,
        plan: Optional[ExecutionPlan] = None
    ) -> Dict[str, Any]:
        """
        Execute the plan by spawning agents and managing tasks.
        
        Args:
            plan: Execution plan (uses current if not provided)
            
        Returns:
            Execution results
        """
        if not plan:
            plan = self.current_plan
        
        if not plan:
            raise OrchestrationError("No execution plan available")
        
        self.state = OrchestratorState.EXECUTING
        self.console.print("\n[bold green]Starting execution...[/bold green]")
        
        # Explain execution start if verbose
        if self.verbose_mode:
            self.explainer.explain_execution_start()
            self.explainer.explain_session_persistence()
        
        execution_start_time = datetime.now()
        
        try:
            # Create/spawn agents
            await self._spawn_agents(plan)
            
            # Execute batches in order
            results = {}
            for batch_num, batch in enumerate(plan.execution_order, 1):
                self.console.print(f"\n[cyan]Executing batch {batch_num}/{len(plan.execution_order)}[/cyan]")
                batch_results = await self._execute_batch(batch)
                results[f"batch_{batch_num}"] = batch_results
            
            # Collect final results
            final_results = await self._collect_results()
            
            self.state = OrchestratorState.IDLE
            self.console.print("[bold green]Execution complete![/bold green]")
            
            # Calculate execution metrics
            execution_duration = (datetime.now() - execution_start_time).total_seconds()
            tasks_completed = len([t for t in plan.task_plan.subtasks])
            agents_used = plan.agent_proposal.new_agents + plan.agent_proposal.reused_agents
            total_cost = await self._calculate_total_cost()
            
            # Explain completion if verbose
            if self.verbose_mode:
                self.explainer.explain_completion(
                    execution_duration,
                    tasks_completed,
                    agents_used,
                    total_cost
                )
            
            return {
                "plan_id": plan.id,
                "batch_results": results,
                "final_results": final_results,
                "total_cost": total_cost,
                "duration": execution_duration
            }
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "execute_plan"})
            self.state = OrchestratorState.ERROR
            self.console.print(f"[red]Execution error: {e}[/red]")
            raise
    
    async def _spawn_agents(self, plan: ExecutionPlan):
        """Spawn agents according to the plan."""
        self.console.print("[blue]Spawning agents...[/blue]")
        
        for suggestion in plan.agent_proposal.suggestions:
            if suggestion.is_new:
                # Create new agent
                agent_id = str(uuid4())
                
                # Create agent with its task
                task_prompt = suggestion.assigned_task.to_claude_prompt()
                
                # Spawn Claude session
                process_id, session_id, process = await self.session_manager.create_session(
                    agent_id=agent_id,
                    agent_name=suggestion.agent_name,
                    task=task_prompt,
                    max_turns=10
                )
                
                # Register with message bus (agent already created in DB by session_manager)
                await self.message_bus.register_agent(
                    agent_id,
                    {
                        "name": suggestion.agent_name,
                        "process_id": process_id,
                        "session_id": session_id,
                        "type": suggestion.agent_type
                    },
                    create_in_db=False  # Already created by session_manager
                )
                
                # Track execution
                self.agent_executions[agent_id] = AgentExecution(
                    agent_id=agent_id,
                    agent_name=suggestion.agent_name,
                    process_id=process_id,
                    session_id=session_id,
                    task=suggestion.assigned_task,
                    status="active",
                    started_at=datetime.now()
                )
                
                self.active_sessions[agent_id] = session_id
                
                self.console.print(f"  [green]✓[/green] Spawned {suggestion.agent_name}")
                
            else:
                # Resume existing agent
                agent_id = suggestion.agent_id
                
                # Resume session with new task
                task_prompt = suggestion.assigned_task.to_claude_prompt()
                process_id, process = await self.session_manager.resume_session(
                    agent_id=agent_id,
                    session_id=suggestion.session_id,
                    continuation_task=task_prompt
                )
                
                # Update execution tracking
                self.agent_executions[agent_id] = AgentExecution(
                    agent_id=agent_id,
                    agent_name=suggestion.agent_name,
                    process_id=process_id,
                    session_id=suggestion.session_id,
                    task=suggestion.assigned_task,
                    status="active",
                    started_at=datetime.now()
                )
                
                self.console.print(f"  [cyan]↻[/cyan] Resumed {suggestion.agent_name}")
    
    async def _execute_batch(self, batch: List[SubTask]) -> Dict[str, Any]:
        """Execute a batch of tasks in parallel."""
        tasks = []
        task_names = []
        
        # Show what's being executed
        self.console.print(f"[cyan]Executing {len(batch)} tasks in parallel:[/cyan]")
        for subtask in batch:
            self.console.print(f"  • {subtask.description[:60]}")
            if subtask.assigned_agent:
                self.console.print(f"    Agent: {subtask.assigned_agent}")
        
        for subtask in batch:
            # Find agent assigned to this task
            agent_execution = None
            for exec in self.agent_executions.values():
                if exec.task.id == subtask.id:
                    agent_execution = exec
                    break
            
            if agent_execution:
                # Start monitoring this agent's output
                tasks.append(self._monitor_agent_execution(agent_execution))
                task_names.append(agent_execution.agent_name)
            else:
                self.console.print(f"[yellow]Warning: No agent found for task {subtask.id}[/yellow]")
        
        # Show monitoring status
        self.console.print(f"[blue]Monitoring {len(tasks)} agents...[/blue]")
        
        # Execute all in parallel with progress tracking
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        batch_results = {}
        for subtask, result in zip(batch, results):
            if isinstance(result, Exception):
                self.console.print(f"[red]✗ Task failed: {subtask.description[:40]}[/red]")
                self.console.print(f"  Error: {str(result)}")
                batch_results[subtask.id] = {
                    "status": "error",
                    "error": str(result)
                }
            else:
                status = result.get("status", "unknown")
                if status == "completed":
                    self.console.print(f"[green]✓ Task completed: {subtask.description[:40]}[/green]")
                elif status == "timeout":
                    self.console.print(f"[yellow]⚠ Task timed out: {subtask.description[:40]}[/yellow]")
                else:
                    self.console.print(f"[blue]? Task status {status}: {subtask.description[:40]}[/blue]")
                batch_results[subtask.id] = result
        
        return batch_results
    
    async def _monitor_agent_execution(
        self,
        execution: AgentExecution,
        timeout: float = 180.0  # Increased timeout
    ) -> Dict[str, Any]:
        """Monitor an agent's execution of a task."""
        start_time = asyncio.get_event_loop().time()
        last_output_time = start_time
        no_output_warnings = 0
        
        self.console.print(f"[dim]Started monitoring {execution.agent_name}...[/dim]")
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            elapsed = asyncio.get_event_loop().time() - start_time
            
            # Read output from Claude session
            try:
                output = await self.session_manager.read_session_output(
                    execution.process_id,
                    timeout=5.0
                )
                
                if output:
                    last_output_time = asyncio.get_event_loop().time()
                    no_output_warnings = 0
                    
                    # Check if task is complete
                    if output.get("type") == "completion":
                        execution.status = "completed"
                        execution.completed_at = datetime.now()
                        execution.result = output
                        execution.progress = 100.0
                        
                        # Update database
                        await self.db.complete_task(
                            execution.task.id,
                            output
                        )
                        
                        return {
                            "status": "completed",
                            "result": output,
                            "duration": (execution.completed_at - execution.started_at).total_seconds()
                        }
                    
                    # Update progress
                    elif output.get("progress"):
                        execution.progress = output["progress"]
                        await self.db.update_task_progress(
                            execution.task.id,
                            execution.progress
                        )
                        self.console.print(f"[dim]{execution.agent_name}: {execution.progress:.0f}% complete[/dim]")
                    
                    # Show any output content
                    elif output.get("content"):
                        # Truncate long output for visibility
                        content = output["content"][:100] + "..." if len(output["content"]) > 100 else output["content"]
                        self.console.print(f"[dim]{execution.agent_name}: {content}[/dim]")
                
                # Check for no output timeout
                if asyncio.get_event_loop().time() - last_output_time > 30:
                    no_output_warnings += 1
                    if no_output_warnings == 1:
                        self.console.print(f"[yellow]⚠ {execution.agent_name} has not produced output for 30s[/yellow]")
                    elif no_output_warnings >= 3:
                        self.console.print(f"[red]✗ {execution.agent_name} appears to be stuck, terminating[/red]")
                        execution.status = "stuck"
                        execution.errors.append("No output for extended period")
                        return {
                            "status": "stuck",
                            "progress": execution.progress,
                            "error": "Agent produced no output for extended period"
                        }
                        
            except Exception as e:
                self.console.print(f"[red]Error monitoring {execution.agent_name}: {e}[/red]")
                execution.errors.append(str(e))
            
            await asyncio.sleep(1)
        
        # Timeout reached
        execution.status = "timeout"
        self.console.print(f"[yellow]⚠ {execution.agent_name} timed out after {timeout}s[/yellow]")
        return {
            "status": "timeout",
            "progress": execution.progress,
            "duration": timeout
        }
    
    async def _monitor_execution(self):
        """Background task to monitor execution progress."""
        while True:
            try:
                await asyncio.sleep(self._monitor_interval)
                
                if self.state == OrchestratorState.EXECUTING:
                    # Check agent health
                    for execution in self.agent_executions.values():
                        if execution.status == "active":
                            # Check if process is still alive
                            # Could implement health checks here
                            pass
                    
                    # Handle inter-agent messages
                    for agent_id in self.active_sessions:
                        messages = await self.message_bus.get_messages_for_agent(
                            agent_id,
                            message_types=[MessageType.DISCOVERY, MessageType.DEPENDENCY]
                        )
                        
                        for message in messages:
                            await self._handle_agent_message(agent_id, message)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {"operation": "monitor_execution"})
    
    async def _handle_agent_message(self, agent_id: str, message):
        """Handle important inter-agent messages."""
        if message.message_type == MessageType.DISCOVERY:
            # An agent discovered something important
            self.console.print(f"[yellow]💡 {message.from_agent} discovered: {message.content}[/yellow]")
            
            # Explain if verbose
            if self.verbose_mode:
                self.explainer.explain_inter_agent_communication(
                    message.from_agent,
                    message.to_agent or "all agents",
                    "discovery",
                    message.content
                )
            
        elif message.message_type == MessageType.DEPENDENCY:
            # An agent needs something from another
            self.console.print(f"[cyan]⚠️ {message.from_agent} needs from {message.to_agent}: {message.content}[/cyan]")
            
            # Explain if verbose
            if self.verbose_mode:
                self.explainer.explain_inter_agent_communication(
                    message.from_agent,
                    message.to_agent,
                    "dependency",
                    message.content
                )
    
    async def _collect_results(self) -> Dict[str, Any]:
        """Collect final results from all agents."""
        results = {}
        
        for agent_id, execution in self.agent_executions.items():
            results[agent_id] = {
                "agent_name": execution.agent_name,
                "task": execution.task.description,
                "status": execution.status,
                "progress": execution.progress,
                "result": execution.result,
                "errors": execution.errors,
                "duration": (
                    (execution.completed_at - execution.started_at).total_seconds()
                    if execution.completed_at else None
                )
            }
        
        return results
    
    async def _calculate_total_cost(self) -> float:
        """Calculate total cost of execution."""
        total_cost = 0.0
        
        for session_id in self.active_sessions.values():
            session = await self.db.get_session(session_id)
            if session:
                total_cost += session.get('total_cost', 0.0)
        
        return total_cost
    
    async def pause_execution(self):
        """Pause current execution."""
        if self.state == OrchestratorState.EXECUTING:
            self.state = OrchestratorState.PAUSED
            self.console.print("[yellow]Execution paused[/yellow]")
    
    async def resume_execution(self):
        """Resume paused execution."""
        if self.state == OrchestratorState.PAUSED:
            self.state = OrchestratorState.EXECUTING
            self.console.print("[green]Execution resumed[/green]")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status."""
        active_agents = []
        for agent_id, execution in self.agent_executions.items():
            if execution.status == "active":
                active_agents.append({
                    "agent_id": agent_id,
                    "agent_name": execution.agent_name,
                    "task": execution.task.description[:50],
                    "progress": execution.progress
                })
        
        return {
            "state": self.state.value,
            "current_plan": self.current_plan.id if self.current_plan else None,
            "active_agents": active_agents,
            "total_agents": len(self.agent_executions),
            "sessions": len(self.active_sessions)
        }
    
    async def save_checkpoint(self, name: str, description: str = "") -> str:
        """
        Save current state as a checkpoint.
        
        Args:
            name: Checkpoint name
            description: Checkpoint description
            
        Returns:
            Checkpoint ID
        """
        checkpoint_id = str(uuid4())
        
        checkpoint_data = {
            "description": description,
            "orchestrator_state": {
                "state": self.state.value,
                "current_plan": self.current_plan.id if self.current_plan else None
            },
            "agent_sessions": dict(self.active_sessions),
            "task_states": {
                exec.task.id: {
                    "status": exec.status,
                    "progress": exec.progress,
                    "agent": exec.agent_id
                }
                for exec in self.agent_executions.values()
            },
            "message_history": []  # Could save recent messages
        }
        
        await self.db.save_checkpoint(checkpoint_id, name, checkpoint_data)
        
        self.console.print(f"[green]✓ Checkpoint saved: {name}[/green]")
        
        # Explain checkpoint if verbose
        if self.verbose_mode:
            self.explainer.explain_checkpoint(name)
        
        return checkpoint_id
    
    async def restore_checkpoint(self, name: str) -> bool:
        """
        Restore from a checkpoint.
        
        Args:
            name: Checkpoint name
            
        Returns:
            True if restored successfully
        """
        checkpoint = await self.db.load_checkpoint(name)
        if not checkpoint:
            self.console.print(f"[red]Checkpoint '{name}' not found[/red]")
            return False
        
        try:
            self.console.print(f"[blue]Restoring checkpoint '{name}'...[/blue]")
            
            # Explain resume if verbose
            if self.verbose_mode:
                last_activity = checkpoint.get('description', 'Unknown')
                self.explainer.explain_resume_session(name, last_activity)
            
            # Restore orchestrator state
            orchestrator_state = checkpoint['orchestrator_state']
            self.state = OrchestratorState(orchestrator_state['state'])
            
            # Restore agent sessions
            for agent_id, session_id in checkpoint['agent_sessions'].items():
                # Resume session
                process_id, process = await self.session_manager.resume_session(
                    agent_id, session_id,
                    "Continue from checkpoint"
                )
                
                self.active_sessions[agent_id] = session_id
                self.console.print(f"  [cyan]↻[/cyan] Restored session for agent {agent_id[:8]}")
            
            self.console.print(f"[green]✓ Checkpoint restored successfully[/green]")
            return True
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "restore_checkpoint", "name": name})
            self.console.print(f"[red]Failed to restore checkpoint: {e}[/red]")
            return False
    
    async def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List available checkpoints."""
        return await self.db.list_checkpoints()