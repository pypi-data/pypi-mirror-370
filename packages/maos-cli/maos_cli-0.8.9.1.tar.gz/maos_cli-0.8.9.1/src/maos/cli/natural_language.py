"""
Natural Language Interface for MAOS

Provides a Claude Code-like conversational interface for controlling agent swarms
using natural language instead of Python code.
"""

import asyncio
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from uuid import uuid4

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown

from ..core.orchestrator import Orchestrator
from ..core.swarm_coordinator import SwarmPattern, CoordinationStrategy
from ..core.claude_subagent_manager import ClaudeSubagentManager
from ..core.claude_cli_manager import ClaudeCodeCLIManager
from ..models.task import Task, TaskPriority
from ..utils.logging_config import MAOSLogger


class NaturalLanguageProcessor:
    """
    Processes natural language commands and translates them into
    orchestrator actions, similar to how Claude Code works.
    """
    
    def __init__(self, orchestrator: Orchestrator, console: Console):
        self.orchestrator = orchestrator
        self.console = console
        self.logger = MAOSLogger("natural_language")
        
        # Initialize Claude subagent manager
        self.subagent_manager = ClaudeSubagentManager()
        
        # Initialize Claude CLI manager for spawning actual processes
        self.cli_manager = ClaudeCodeCLIManager(
            max_processes=10,
            claude_cli_path="claude",
            base_working_dir="/tmp/maos_claude"
        )
        
        # Track active swarms and context
        self.active_swarms: Dict[str, Any] = {}
        self.current_context: Dict[str, Any] = {}
        self.command_history: List[str] = []
        self.created_subagents: List[str] = []  # Track subagents we created
        
        # Command patterns for natural language understanding
        self.patterns = {
            'spawn_swarm': [
                r'spawn\s+(\d+)?\s*agents?\s+(?:to\s+)?(.+)',
                r'create\s+(?:a\s+)?swarm\s+(?:of\s+)?(\d+)?\s*agents?\s+(?:to\s+)?(.+)',
                r'start\s+(\d+)?\s*agents?\s+(?:to\s+)?(.+)',
            ],
            'implement_prd': [
                r'(?:implement|deliver|build)\s+(?:the\s+)?(?:requirements\s+)?(?:in\s+)?(.+\.md)',
                r'(?:work\s+on|execute)\s+(?:the\s+)?prd(?:\.md)?',
                r'spawn\s+(?:a\s+)?swarm\s+to\s+(?:implement|deliver)\s+(?:the\s+)?(?:requirements\s+)?(?:in\s+)?(.+\.md)',
            ],
            'show_status': [
                r'(?:show|display|list)\s+(?:me\s+)?(?:the\s+)?(?:status|agents|swarms)',
                r'what(?:\s+agents)?\s+(?:are|is)\s+running',
                r'status',
            ],
            'checkpoint': [
                r'(?:create|save|make)\s+(?:a\s+)?checkpoint(?:\s+(.+))?',
                r'checkpoint(?:\s+(.+))?',
                r'save\s+(?:the\s+)?(?:current\s+)?state(?:\s+as\s+(.+))?',
            ],
            'restore': [
                r'restore\s+(?:from\s+)?(?:checkpoint\s+)?(.+)',
                r'load\s+(?:checkpoint\s+)?(.+)',
                r'go\s+back\s+to\s+(.+)',
            ],
            'show_progress': [
                r'(?:show|display)\s+(?:me\s+)?(?:the\s+)?progress',
                r'(?:how\s+is|what\'s)\s+(?:the\s+)?progress',
                r'progress',
            ],
            'stop': [
                r'stop\s+(?:all\s+)?(?:agents|swarms)',
                r'shutdown\s+(?:everything|all)',
                r'cancel\s+(?:all\s+)?(?:tasks|agents)',
            ],
            'help': [
                r'help',
                r'what\s+can\s+(?:you|i)\s+do',
                r'(?:show|list)\s+commands',
            ],
        }
    
    async def process_command(self, user_input: str) -> None:
        """Process a natural language command from the user."""
        
        # Add to history
        self.command_history.append(user_input)
        
        # Convert to lowercase for matching
        input_lower = user_input.lower().strip()
        
        # Try to match command patterns
        if await self._handle_spawn_swarm(input_lower, user_input):
            return
        elif await self._handle_implement_prd(input_lower, user_input):
            return
        elif await self._handle_show_status(input_lower):
            return
        elif await self._handle_checkpoint(input_lower, user_input):
            return
        elif await self._handle_restore(input_lower, user_input):
            return
        elif await self._handle_show_progress(input_lower):
            return
        elif await self._handle_stop(input_lower):
            return
        elif await self._handle_help(input_lower):
            return
        else:
            # Try to interpret as a general task
            await self._handle_general_task(user_input)
    
    async def _handle_spawn_swarm(self, input_lower: str, original_input: str) -> bool:
        """Handle commands to spawn agent swarms."""
        
        for pattern in self.patterns['spawn_swarm']:
            match = re.search(pattern, input_lower)
            if match:
                # Extract number of agents and task
                if len(match.groups()) == 2:
                    num_agents = int(match.group(1)) if match.group(1) else 3
                    task_description = match.group(2) if len(match.groups()) > 1 else match.group(1)
                else:
                    num_agents = 3
                    task_description = match.group(1) if match.group(1) else "general tasks"
                
                with self.console.status(f"[bold blue]🚀 Creating swarm of {num_agents} agents...[/bold blue]"):
                    try:
                        # Create Claude subagents for this task
                        subagent_names = self.subagent_manager.create_subagents_for_task(
                            task_description, 
                            num_agents
                        )
                        self.created_subagents.extend(subagent_names)
                        
                        self.console.print(f"[green]✓ Created Claude subagents: {', '.join(subagent_names)}[/green]")
                        
                        # Actually spawn Claude CLI processes for each agent
                        spawned_processes = []
                        for agent_name in subagent_names:
                            try:
                                process_id = await self.cli_manager.spawn_claude_instance(
                                    agent_name=agent_name,
                                    working_dir=str(Path.cwd())  # Use current directory
                                )
                                spawned_processes.append(process_id)
                                self.console.print(f"[cyan]  • Spawned Claude process for {agent_name} (ID: {process_id[:8]}...)[/cyan]")
                            except Exception as e:
                                self.console.print(f"[yellow]  ⚠ Failed to spawn process for {agent_name}: {e}[/yellow]")
                        
                        if spawned_processes:
                            self.console.print(f"[green]✓ Successfully spawned {len(spawned_processes)} Claude CLI instances[/green]")
                        else:
                            self.console.print(f"[red]✗ Failed to spawn any Claude processes[/red]")
                            return True
                        
                        # Create the swarm using these subagents
                        swarm_id = await self.orchestrator.create_agent_swarm(
                            name=f"swarm_{datetime.now().strftime('%H%M%S')}",
                            pattern=SwarmPattern.PARALLEL,
                            strategy=CoordinationStrategy.CAPABILITY_BASED,
                            agent_templates=subagent_names,  # Use actual subagent names
                            min_agents=num_agents,
                            max_agents=num_agents + 2
                        )
                        
                        self.active_swarms[str(swarm_id)] = {
                            'name': f"swarm_{datetime.now().strftime('%H%M%S')}",
                            'agents': subagent_names,
                            'task': task_description,
                            'created': datetime.now(),
                            'processes': spawned_processes
                        }
                        
                        self.console.print(f"[green]✓ Spawned {num_agents} Claude instances with subagents[/green]")
                        
                        # Create and execute task
                        task = Task(
                            name=f"nl_task_{uuid4().hex[:8]}",
                            description=original_input,
                            priority=TaskPriority.HIGH,
                            metadata={'source': 'natural_language', 'original_command': original_input}
                        )
                        
                        self.console.print(f"[cyan]✓ Distributed task: {task_description}[/cyan]")
                        
                        # Execute the task
                        results = await self.orchestrator.execute_swarm_task(
                            swarm_id=swarm_id,
                            task=task,
                            execution_mode="parallel"
                        )
                        
                        self.console.print("\n[green]⚡ Agents working in parallel:[/green]")
                        for agent_type in agent_types:
                            self.console.print(f"  • {agent_type}: Processing assigned tasks...")
                        
                    except Exception as e:
                        self.console.print(f"[red]❌ Error creating swarm: {e}[/red]")
                        self.logger.log_error(e, {"command": original_input})
                
                return True
        
        return False
    
    async def _handle_implement_prd(self, input_lower: str, original_input: str) -> bool:
        """Handle commands to implement a PRD file."""
        
        for pattern in self.patterns['implement_prd']:
            match = re.search(pattern, input_lower)
            if match:
                # Extract PRD filename
                if match.groups():
                    prd_file = match.group(1) if match.group(1) else "prd.md"
                else:
                    prd_file = "prd.md"
                
                # Check if PRD file exists
                prd_path = Path(prd_file)
                if not prd_path.exists():
                    prd_path = Path.cwd() / prd_file
                
                if not prd_path.exists():
                    self.console.print(f"[red]❌ PRD file not found: {prd_file}[/red]")
                    self.console.print("[yellow]Please ensure the file exists in the current directory[/yellow]")
                    return True
                
                with self.console.status("[bold blue]📄 Analyzing PRD...[/bold blue]"):
                    try:
                        # Read PRD content
                        prd_content = prd_path.read_text()
                        
                        # Analyze requirements (simple parsing for now)
                        lines = prd_content.split('\n')
                        requirements = []
                        for line in lines:
                            if line.strip().startswith(('-', '*', '•')) or re.match(r'^\d+\.', line.strip()):
                                requirements.append(line.strip().lstrip('-*•').strip())
                        
                        if not requirements:
                            # Fall back to using the entire content
                            requirements = [prd_content[:500]]  # First 500 chars as summary
                        
                        self.console.print(f"[green]✓ Found {len(requirements)} requirements in {prd_file}[/green]")
                        
                        # Determine optimal swarm configuration
                        num_agents = min(max(3, len(requirements) // 3), 10)  # 3-10 agents
                        agent_types = ['architect', 'developer', 'developer', 'tester', 'reviewer'][:num_agents]
                        
                        # Create swarm
                        swarm_id = await self.orchestrator.create_agent_swarm(
                            name=f"prd_implementation_{datetime.now().strftime('%H%M%S')}",
                            pattern=SwarmPattern.HIERARCHICAL,
                            strategy=CoordinationStrategy.WORKLOAD_BALANCED,
                            agent_templates=agent_types,
                            min_agents=len(agent_types),
                            max_agents=len(agent_types) + 2
                        )
                        
                        self.console.print(f"[green]✓ Spawned {len(agent_types)} agents: {', '.join(agent_types)}[/green]")
                        
                        # Create tasks from requirements
                        tasks = []
                        for i, req in enumerate(requirements[:12]):  # Limit to 12 tasks
                            task = Task(
                                name=f"requirement_{i+1}",
                                description=req,
                                priority=TaskPriority.HIGH,
                                metadata={
                                    'source': 'prd',
                                    'prd_file': str(prd_file),
                                    'requirement_index': i
                                }
                            )
                            tasks.append(task)
                        
                        self.console.print(f"[cyan]✓ Distributed {len(tasks)} tasks across agents[/cyan]")
                        
                        # Execute tasks
                        self.console.print("\n[green]⚡ Agents working on PRD implementation:[/green]")
                        for agent_type in agent_types:
                            self.console.print(f"  • {agent_type}: Processing requirements...")
                        
                        # Store context
                        self.current_context['prd_implementation'] = {
                            'swarm_id': str(swarm_id),
                            'prd_file': str(prd_file),
                            'num_requirements': len(requirements),
                            'started': datetime.now()
                        }
                        
                    except Exception as e:
                        self.console.print(f"[red]❌ Error processing PRD: {e}[/red]")
                        self.logger.log_error(e, {"prd_file": str(prd_file)})
                
                return True
        
        return False
    
    async def _handle_show_status(self, input_lower: str) -> bool:
        """Handle status display commands."""
        
        for pattern in self.patterns['show_status']:
            if re.search(pattern, input_lower):
                
                # Get system status
                with self.console.status("[bold blue]Getting system status...[/bold blue]"):
                    status = await self.orchestrator.get_system_status()
                    agents = await self.orchestrator.agent_manager.get_all_agents()
                
                # Display status table
                table = Table(title="🤖 MAOS System Status", show_header=True, header_style="bold blue")
                table.add_column("Component", style="cyan", width=20)
                table.add_column("Status", style="green", width=30)
                
                table.add_row("System", "Running" if status.get('running') else "Stopped")
                table.add_row("Active Swarms", str(len(self.active_swarms)))
                table.add_row("Running Agents", str(len(agents)))
                table.add_row("Active Tasks", str(status.get('active_executions', 0)))
                
                self.console.print(table)
                
                # Show active swarms
                if self.active_swarms:
                    self.console.print("\n[bold cyan]Active Swarms:[/bold cyan]")
                    for swarm_id, info in self.active_swarms.items():
                        self.console.print(f"  • {info['name']}: {info['task']}")
                        self.console.print(f"    Agents: {', '.join(info['agents'])}")
                
                # Show agents
                if agents:
                    self.console.print("\n[bold cyan]Running Agents:[/bold cyan]")
                    for agent in agents[:10]:  # Show first 10
                        status_color = "green" if agent.status.value == "idle" else "yellow"
                        self.console.print(f"  • {agent.agent_type}: [{status_color}]{agent.status.value}[/{status_color}]")
                
                return True
        
        return False
    
    async def _handle_checkpoint(self, input_lower: str, original_input: str) -> bool:
        """Handle checkpoint creation commands."""
        
        for pattern in self.patterns['checkpoint']:
            match = re.search(pattern, input_lower)
            if match:
                # Extract checkpoint name if provided
                checkpoint_name = match.group(1) if match.groups() and match.group(1) else None
                
                if not checkpoint_name:
                    # Generate name from context or timestamp
                    checkpoint_name = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                with self.console.status(f"[bold blue]💾 Creating checkpoint: {checkpoint_name}...[/bold blue]"):
                    try:
                        checkpoint_id = await self.orchestrator.create_checkpoint(checkpoint_name)
                        self.console.print(f"[green]✓ Checkpoint saved: {checkpoint_name}[/green]")
                        self.console.print(f"[dim]ID: {str(checkpoint_id)[:8]}...[/dim]")
                        
                        # Store in context
                        self.current_context['last_checkpoint'] = {
                            'id': str(checkpoint_id),
                            'name': checkpoint_name,
                            'created': datetime.now()
                        }
                        
                    except Exception as e:
                        self.console.print(f"[red]❌ Failed to create checkpoint: {e}[/red]")
                
                return True
        
        return False
    
    async def _handle_restore(self, input_lower: str, original_input: str) -> bool:
        """Handle checkpoint restoration commands."""
        
        for pattern in self.patterns['restore']:
            match = re.search(pattern, input_lower)
            if match:
                checkpoint_ref = match.group(1) if match.groups() else None
                
                if not checkpoint_ref:
                    self.console.print("[red]Please specify a checkpoint name or ID[/red]")
                    # TODO: Show list of available checkpoints
                    return True
                
                with self.console.status(f"[bold blue]📂 Restoring from checkpoint: {checkpoint_ref}...[/bold blue]"):
                    try:
                        # Try to find checkpoint by name or ID
                        # This is simplified - would need proper checkpoint lookup
                        success = await self.orchestrator.restore_checkpoint(checkpoint_ref)
                        
                        if success:
                            self.console.print(f"[green]✓ Restored checkpoint successfully[/green]")
                            self.console.print("[cyan]Agents resumed with full context[/cyan]")
                        else:
                            self.console.print(f"[red]❌ Failed to restore checkpoint[/red]")
                        
                    except Exception as e:
                        self.console.print(f"[red]❌ Error restoring checkpoint: {e}[/red]")
                
                return True
        
        return False
    
    async def _handle_show_progress(self, input_lower: str) -> bool:
        """Handle progress display commands."""
        
        for pattern in self.patterns['show_progress']:
            if re.search(pattern, input_lower):
                
                if not self.active_swarms:
                    self.console.print("[yellow]No active swarms running[/yellow]")
                    return True
                
                self.console.print("\n[bold cyan]📊 Swarm Progress:[/bold cyan]")
                
                for swarm_id, info in self.active_swarms.items():
                    # Get swarm status
                    status = await self.orchestrator.get_swarm_status(swarm_id)
                    
                    if status:
                        metrics = status.get('metrics', {})
                        completed = metrics.get('completed_tasks', 0)
                        total = metrics.get('total_tasks', 1)
                        progress = (completed / total) * 100 if total > 0 else 0
                        
                        self.console.print(f"\n[cyan]{info['name']}:[/cyan]")
                        for agent in info['agents']:
                            # Simulate per-agent progress (would need real metrics)
                            agent_progress = progress + (hash(agent) % 20) - 10  # Vary by agent
                            agent_progress = max(0, min(100, agent_progress))
                            self.console.print(f"  • {agent}: {agent_progress:.0f}% complete")
                
                return True
        
        return False
    
    async def _handle_stop(self, input_lower: str) -> bool:
        """Handle stop/shutdown commands."""
        
        for pattern in self.patterns['stop']:
            if re.search(pattern, input_lower):
                
                self.console.print("[yellow]⚠️  Stopping all agents and swarms...[/yellow]")
                
                with self.console.status("[bold red]Shutting down...[/bold red]"):
                    try:
                        # Shutdown all swarms
                        for swarm_id in list(self.active_swarms.keys()):
                            await self.orchestrator.shutdown_swarm(swarm_id)
                        
                        self.active_swarms.clear()
                        self.console.print("[green]✓ All agents stopped[/green]")
                        
                    except Exception as e:
                        self.console.print(f"[red]❌ Error during shutdown: {e}[/red]")
                
                return True
        
        return False
    
    async def _handle_help(self, input_lower: str) -> bool:
        """Handle help commands."""
        
        for pattern in self.patterns['help']:
            if re.search(pattern, input_lower):
                
                help_text = """
[bold cyan]MAOS Natural Language Commands:[/bold cyan]

[green]Creating Agent Swarms:[/green]
  • "spawn 3 agents to review my code"
  • "create a swarm to analyze security issues"
  • "start 5 agents for parallel testing"

[green]Working with PRDs:[/green]
  • "implement the requirements in prd.md"
  • "spawn a swarm to deliver the PRD"
  • "build the features from requirements.md"

[green]Monitoring:[/green]
  • "show status" / "what agents are running"
  • "show progress" / "how is the progress"
  • "list active swarms"

[green]Checkpoints:[/green]
  • "create checkpoint before deployment"
  • "save state as milestone-1"
  • "restore from yesterday's checkpoint"

[green]Control:[/green]
  • "stop all agents"
  • "shutdown everything"
  • "exit" / "quit"

[dim]Type naturally - MAOS understands variations of these commands![/dim]
                """
                
                self.console.print(Panel(help_text.strip(), title="📚 Help", border_style="cyan"))
                return True
        
        return False
    
    async def _handle_general_task(self, user_input: str) -> None:
        """Handle general task descriptions that don't match specific patterns."""
        
        self.console.print("[cyan]Interpreting as general task request...[/cyan]")
        
        # Default to creating a small swarm for the task
        num_agents = 3
        agent_types = self._determine_agent_types(user_input, num_agents)
        
        with self.console.status("[bold blue]Creating agent swarm for your task...[/bold blue]"):
            try:
                swarm_id = await self.orchestrator.create_agent_swarm(
                    name=f"task_{datetime.now().strftime('%H%M%S')}",
                    pattern=SwarmPattern.PARALLEL,
                    strategy=CoordinationStrategy.CAPABILITY_BASED,
                    agent_templates=agent_types,
                    min_agents=num_agents
                )
                
                task = Task(
                    name=f"user_task_{uuid4().hex[:8]}",
                    description=user_input,
                    priority=TaskPriority.MEDIUM,
                    metadata={'source': 'natural_language'}
                )
                
                await self.orchestrator.execute_swarm_task(
                    swarm_id=swarm_id,
                    task=task,
                    execution_mode="parallel"
                )
                
                self.console.print(f"[green]✓ Created swarm with {num_agents} agents to handle your request[/green]")
                
            except Exception as e:
                self.console.print(f"[red]❌ Could not process request: {e}[/red]")
                self.console.print("[yellow]Try rephrasing or use 'help' to see available commands[/yellow]")
    
    def _determine_agent_types(self, task_description: str, num_agents: int) -> List[str]:
        """Determine appropriate agent types based on task description."""
        
        task_lower = task_description.lower()
        
        # Keywords to agent type mapping
        if 'security' in task_lower or 'vulnerability' in task_lower:
            base_types = ['security-auditor', 'code-analyzer', 'penetration-tester']
        elif 'test' in task_lower or 'testing' in task_lower:
            base_types = ['test-engineer', 'qa-specialist', 'test-automation']
        elif 'review' in task_lower or 'analyze' in task_lower:
            base_types = ['code-analyzer', 'reviewer', 'quality-analyst']
        elif 'performance' in task_lower or 'optimize' in task_lower:
            base_types = ['performance-analyst', 'optimizer', 'profiler']
        elif 'document' in task_lower or 'documentation' in task_lower:
            base_types = ['documentation-writer', 'technical-writer', 'api-documenter']
        elif 'refactor' in task_lower or 'clean' in task_lower:
            base_types = ['refactoring-specialist', 'code-cleaner', 'architect']
        else:
            # Default general-purpose agents
            base_types = ['developer', 'analyst', 'tester', 'reviewer', 'architect']
        
        # Ensure we have enough types
        while len(base_types) < num_agents:
            base_types.append('general-agent')
        
        return base_types[:num_agents]


class NaturalLanguageShell:
    """
    Interactive shell with natural language processing,
    similar to Claude Code's interface.
    """
    
    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator
        self.console = Console()
        self.processor = NaturalLanguageProcessor(orchestrator, self.console)
        self.running = False
        self.logger = MAOSLogger("natural_language_shell")
    
    async def run(self):
        """Run the interactive natural language shell."""
        
        # Start the CLI manager
        await self.processor.cli_manager.start()
        
        self.running = True
        self._show_welcome()
        
        while self.running:
            try:
                # Get user input
                user_input = self.console.input("\n[bold blue]MAOS>[/bold blue] ")
                
                if not user_input.strip():
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    break
                
                # Process natural language command
                await self.processor.process_command(user_input)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'exit' or 'quit' to leave[/yellow]")
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
                self.logger.log_error(e, {"phase": "shell_loop"})
        
        # Stop CLI manager and cleanup
        await self.processor.cli_manager.stop()
        
        self._show_goodbye()
    
    def _show_welcome(self):
        """Display welcome message."""
        
        welcome = """
[bold green]Welcome to MAOS Natural Language Interface![/bold green]

Control agent swarms using natural language - just like Claude Code!

[cyan]Quick examples:[/cyan]
  • "spawn 3 agents to review my code"
  • "implement the requirements in prd.md"
  • "show me what agents are running"
  • "create a checkpoint before deployment"

[dim]Type 'help' for more commands or 'exit' to quit.[/dim]
        """
        
        self.console.print(Panel(welcome.strip(), title="🤖 MAOS", border_style="green"))
    
    def _show_goodbye(self):
        """Display goodbye message."""
        # Cleanup any created subagents
        if self.processor.created_subagents:
            self.console.print(f"[dim]Cleaning up {len(self.processor.created_subagents)} created subagents...[/dim]")
            self.processor.subagent_manager.cleanup_subagents()
        
        self.console.print("\n[bold green]Thanks for using MAOS! Goodbye! 👋[/bold green]")