"""
MAOS CLI Interactive Shell

Advanced interactive shell with command completion, history,
and rich formatting for enhanced user experience.
"""

import asyncio
import cmd
import readline
import shlex
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.live import Live

from ..core.orchestrator import Orchestrator
from ..models.task import Task, TaskStatus, TaskPriority
from ..models.agent import Agent, AgentCapability
from .formatters import OutputFormatter
from .monitoring import SystemMonitor, TaskMonitor, AgentMonitor


class InteractiveShell:
    """Advanced interactive shell for MAOS CLI."""
    
    def __init__(self, orchestrator: Orchestrator, console: Console):
        self.orchestrator = orchestrator
        self.console = console
        self.running = False
        self.command_history = []
        self.current_context = {}
        
        # Command mappings
        self.commands = {
            'help': self.cmd_help,
            'status': self.cmd_status,
            'tasks': self.cmd_tasks,
            'agents': self.cmd_agents,
            'submit': self.cmd_submit_task,
            'cancel': self.cmd_cancel_task,
            'monitor': self.cmd_monitor,
            'checkpoint': self.cmd_checkpoint,
            'restore': self.cmd_restore,
            'metrics': self.cmd_metrics,
            'health': self.cmd_health,
            'logs': self.cmd_logs,
            'set': self.cmd_set,
            'get': self.cmd_get,
            'clear': self.cmd_clear,
            'history': self.cmd_history,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
        }
        
        # Command aliases
        self.aliases = {
            'h': 'help',
            'st': 'status',
            't': 'tasks',
            'a': 'agents',
            's': 'submit',
            'c': 'cancel',
            'm': 'monitor',
            'cp': 'checkpoint',
            'r': 'restore',
            'q': 'quit',
            'x': 'exit',
        }
    
    async def run(self):
        """Start the interactive shell."""
        self.running = True
        
        # Display welcome message
        self._show_welcome()
        
        while self.running:
            try:
                # Get command input
                prompt_text = self._get_prompt()
                command_line = await self._get_input(prompt_text)
                
                if not command_line.strip():
                    continue
                
                # Parse and execute command
                await self._execute_command(command_line)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'exit' or 'quit' to leave the shell[/yellow]")
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
        
        self._show_goodbye()
    
    def _show_welcome(self):
        """Display welcome message."""
        welcome_text = """
[bold blue]Welcome to MAOS Interactive Shell![/bold blue]

Type [cyan]'help'[/cyan] for available commands or [cyan]'help <command>'[/cyan] for specific help.
Use [cyan]'exit'[/cyan] or [cyan]'quit'[/cyan] to leave the shell.

[dim]Features:[/dim]
• Tab completion for commands and IDs
• Command history with arrow keys
• Real-time monitoring and status updates
• Rich formatting and interactive prompts
        """.strip()
        
        self.console.print(Panel(
            Text(welcome_text),
            title="🤖 MAOS Interactive Shell",
            border_style="blue"
        ))
        self.console.print()
    
    def _show_goodbye(self):
        """Display goodbye message."""
        self.console.print("\n[bold blue]Goodbye! Thanks for using MAOS.[/bold blue]")
    
    def _get_prompt(self) -> str:
        """Generate command prompt."""
        # Show current context if any
        context_info = ""
        if self.current_context:
            if 'task_id' in self.current_context:
                context_info = f"[task:{self.current_context['task_id'][:8]}...]"
            elif 'agent_id' in self.current_context:
                context_info = f"[agent:{self.current_context['agent_id'][:8]}...]"
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"[dim]{timestamp}[/dim] [bold blue]maos[/bold blue]{context_info}> "
    
    async def _get_input(self, prompt: str) -> str:
        """Get user input with prompt."""
        # Use rich prompt for better formatting
        try:
            return Prompt.ask(prompt, console=self.console)
        except KeyboardInterrupt:
            raise
        except EOFError:
            raise
    
    async def _execute_command(self, command_line: str):
        """Parse and execute a command."""
        try:
            # Parse command line
            parts = shlex.split(command_line)
            if not parts:
                return
            
            command = parts[0].lower()
            args = parts[1:]
            
            # Resolve aliases
            if command in self.aliases:
                command = self.aliases[command]
            
            # Add to history
            self.command_history.append({
                'command': command_line,
                'timestamp': datetime.utcnow(),
                'success': None
            })
            
            # Execute command
            if command in self.commands:
                try:
                    await self.commands[command](args)
                    self.command_history[-1]['success'] = True
                except Exception as e:
                    self.console.print(f"[red]Command failed: {e}[/red]")
                    self.command_history[-1]['success'] = False
            else:
                self.console.print(f"[red]Unknown command: {command}[/red]")
                self.console.print(f"[dim]Type 'help' for available commands[/dim]")
                self.command_history[-1]['success'] = False
                
        except Exception as e:
            self.console.print(f"[red]Command parsing error: {e}[/red]")
    
    # Command implementations
    
    async def cmd_help(self, args: List[str]):
        """Show help information."""
        if args:
            # Show help for specific command
            command = args[0].lower()
            if command in self.aliases:
                command = self.aliases[command]
            
            if command in self.commands:
                help_text = self._get_command_help(command)
                self.console.print(Panel(help_text, title=f"Help: {command}", border_style="cyan"))
            else:
                self.console.print(f"[red]Unknown command: {command}[/red]")
        else:
            # Show general help
            self._show_general_help()
    
    async def cmd_status(self, args: List[str]):
        """Show system status."""
        with self.console.status("[bold blue]Getting system status..."):
            status = await self.orchestrator.get_system_status()
            health = await self.orchestrator.get_component_health()
        
        # Format status
        formatter = OutputFormatter.create("table")
        self.console.print(formatter.format_dict(status, "System Status"))
        self.console.print("")
        self.console.print(formatter.format_dict(health, "Component Health"))
    
    async def cmd_tasks(self, args: List[str]):
        """List and manage tasks."""
        if args and args[0] == "--help":
            self.console.print("[cyan]Usage:[/cyan] tasks [status] [limit]")
            self.console.print("[dim]List tasks with optional status filter and limit[/dim]")
            return
        
        # Parse arguments
        status_filter = None
        limit = 20
        
        if args:
            if args[0].lower() in ['pending', 'running', 'completed', 'failed', 'cancelled']:
                status_filter = args[0].lower()
            else:
                try:
                    limit = int(args[0])
                except ValueError:
                    self.console.print(f"[red]Invalid limit: {args[0]}[/red]")
                    return
        
        # Get tasks
        with self.console.status("[bold blue]Retrieving tasks..."):
            all_tasks = await self.orchestrator.state_manager.get_objects('tasks')
        
        # Filter tasks
        filtered_tasks = []
        for task in all_tasks:
            if status_filter and task.status.value.lower() != status_filter:
                continue
            filtered_tasks.append({
                "id": str(task.id)[:8] + "...",
                "name": task.name,
                "status": task.status.value,
                "priority": task.priority.value,
                "created": task.created_at.strftime("%H:%M:%S")
            })
            
            if len(filtered_tasks) >= limit:
                break
        
        if not filtered_tasks:
            self.console.print("[yellow]No tasks found[/yellow]")
            return
        
        # Display tasks
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("ID", style="cyan", width=12)
        table.add_column("Name", style="green", width=30)
        table.add_column("Status", style="yellow", width=12)
        table.add_column("Priority", style="white", width=10)
        table.add_column("Created", style="dim", width=10)
        
        for task in filtered_tasks:
            table.add_row(
                task["id"],
                task["name"][:28] + "..." if len(task["name"]) > 28 else task["name"],
                task["status"],
                task["priority"],
                task["created"]
            )
        
        self.console.print(table)
        self.console.print(f"\n[dim]Showing {len(filtered_tasks)} tasks[/dim]")
    
    async def cmd_agents(self, args: List[str]):
        """List and manage agents."""
        with self.console.status("[bold blue]Retrieving agents..."):
            all_agents = await self.orchestrator.state_manager.get_objects('agents')
        
        if not all_agents:
            self.console.print("[yellow]No agents found[/yellow]")
            return
        
        # Display agents
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("ID", style="cyan", width=12)
        table.add_column("Type", style="green", width=20)
        table.add_column("Status", style="yellow", width=12)
        table.add_column("Capabilities", style="white", width=20)
        table.add_column("Tasks", style="dim", width=8)
        
        for agent in all_agents:
            current_tasks = len(getattr(agent, 'current_tasks', []))
            capabilities = ', '.join(cap.value for cap in agent.capabilities)[:18] + "..." if len(str(agent.capabilities)) > 18 else ', '.join(cap.value for cap in agent.capabilities)
            
            table.add_row(
                str(agent.id)[:8] + "...",
                agent.agent_type,
                agent.status.value,
                capabilities,
                f"{current_tasks}/{agent.max_concurrent_tasks}"
            )
        
        self.console.print(table)
        self.console.print(f"\n[dim]Showing {len(all_agents)} agents[/dim]")
    
    async def cmd_submit_task(self, args: List[str]):
        """Submit a new task."""
        if not args:
            task_name = Prompt.ask("Task name")
        else:
            task_name = " ".join(args)
        
        description = Prompt.ask("Description (optional)", default="", show_default=False)
        priority_str = Prompt.ask("Priority", choices=["low", "medium", "high", "critical"], default="medium")
        
        try:
            priority = TaskPriority(priority_str)
            
            # Create and submit task
            task = Task(
                name=task_name,
                description=description or f"Interactive task: {task_name}",
                priority=priority,
                metadata={'submitted_via': 'interactive_shell'}
            )
            
            with self.console.status("[bold blue]Submitting task..."):
                execution_plan = await self.orchestrator.submit_task(task)
            
            self.console.print(f"[green]✅ Task submitted successfully![/green]")
            self.console.print(f"[dim]Task ID: {str(task.id)[:8]}...[/dim]")
            self.console.print(f"[dim]Execution Plan ID: {str(execution_plan.id)[:8]}...[/dim]")
            
            # Set context
            self.current_context['task_id'] = str(task.id)
            
        except Exception as e:
            self.console.print(f"[red]❌ Failed to submit task: {e}[/red]")
    
    async def cmd_cancel_task(self, args: List[str]):
        """Cancel a task."""
        if not args:
            if 'task_id' in self.current_context:
                task_id = self.current_context['task_id']
            else:
                task_id = Prompt.ask("Task ID")
        else:
            task_id = args[0]
        
        try:
            task_uuid = UUID(task_id)
            
            # Get task for confirmation
            task = await self.orchestrator.get_task(task_uuid)
            if not task:
                self.console.print(f"[red]❌ Task not found: {task_id}[/red]")
                return
            
            if Confirm.ask(f"Cancel task '{task.name}'?", default=False):
                with self.console.status("[bold red]Cancelling task..."):
                    success = await self.orchestrator.cancel_task(task_uuid, "Cancelled via interactive shell")
                
                if success:
                    self.console.print(f"[green]✅ Task cancelled successfully[/green]")
                else:
                    self.console.print(f"[red]❌ Failed to cancel task[/red]")
            else:
                self.console.print("[yellow]Cancellation aborted[/yellow]")
                
        except ValueError:
            self.console.print(f"[red]❌ Invalid task ID format: {task_id}[/red]")
        except Exception as e:
            self.console.print(f"[red]❌ Error: {e}[/red]")
    
    async def cmd_monitor(self, args: List[str]):
        """Start monitoring."""
        monitor_type = args[0] if args else "system"
        
        if monitor_type == "system":
            self.console.print("[bold blue]Starting system monitor...[/bold blue]")
            self.console.print("[dim]Press Ctrl+C to stop[/dim]\n")
            
            monitor = SystemMonitor(self.orchestrator, 2.0)
            try:
                await monitor.start_live_monitoring(detailed=False)
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Monitoring stopped[/yellow]")
        else:
            self.console.print(f"[red]Unknown monitor type: {monitor_type}[/red]")
    
    async def cmd_checkpoint(self, args: List[str]):
        """Create a checkpoint."""
        checkpoint_name = args[0] if args else f"interactive-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        with self.console.status("[bold blue]Creating checkpoint..."):
            checkpoint_id = await self.orchestrator.create_checkpoint(checkpoint_name)
        
        self.console.print(f"[green]✅ Checkpoint created: {checkpoint_name}[/green]")
        self.console.print(f"[dim]ID: {str(checkpoint_id)[:8]}...[/dim]")
    
    async def cmd_restore(self, args: List[str]):
        """Restore from checkpoint."""
        if not args:
            self.console.print("[red]Usage: restore <checkpoint_id>[/red]")
            return
        
        checkpoint_id = args[0]
        
        try:
            checkpoint_uuid = UUID(checkpoint_id)
            
            if Confirm.ask(f"Restore from checkpoint {checkpoint_id}?", default=False):
                with self.console.status("[bold blue]Restoring from checkpoint..."):
                    success = await self.orchestrator.restore_checkpoint(checkpoint_uuid)
                
                if success:
                    self.console.print(f"[green]✅ Successfully restored from checkpoint[/green]")
                else:
                    self.console.print(f"[red]❌ Restore failed[/red]")
            else:
                self.console.print("[yellow]Restore cancelled[/yellow]")
                
        except ValueError:
            self.console.print(f"[red]❌ Invalid checkpoint ID format: {checkpoint_id}[/red]")
        except Exception as e:
            self.console.print(f"[red]❌ Error: {e}[/red]")
    
    async def cmd_metrics(self, args: List[str]):
        """Show system metrics."""
        with self.console.status("[bold blue]Collecting metrics..."):
            metrics = await self.orchestrator.get_system_metrics()
        
        formatter = OutputFormatter.create("table")
        self.console.print(formatter.format_dict(metrics, "System Metrics"))
    
    async def cmd_health(self, args: List[str]):
        """Show component health."""
        with self.console.status("[bold blue]Checking health..."):
            health = await self.orchestrator.get_component_health()
        
        formatter = OutputFormatter.create("table")
        self.console.print(formatter.format_dict(health, "Component Health"))
    
    async def cmd_logs(self, args: List[str]):
        """Show logs (placeholder)."""
        self.console.print("[yellow]Log viewing not yet implemented in interactive shell[/yellow]")
    
    async def cmd_set(self, args: List[str]):
        """Set context variables."""
        if len(args) < 2:
            self.console.print("[red]Usage: set <key> <value>[/red]")
            return
        
        key, value = args[0], args[1]
        self.current_context[key] = value
        self.console.print(f"[green]Set {key} = {value}[/green]")
    
    async def cmd_get(self, args: List[str]):
        """Get context variables."""
        if not args:
            # Show all context
            if self.current_context:
                formatter = OutputFormatter.create("table")
                self.console.print(formatter.format_dict(self.current_context, "Current Context"))
            else:
                self.console.print("[dim]No context variables set[/dim]")
        else:
            key = args[0]
            if key in self.current_context:
                self.console.print(f"[cyan]{key}[/cyan] = [white]{self.current_context[key]}[/white]")
            else:
                self.console.print(f"[red]Context variable not found: {key}[/red]")
    
    async def cmd_clear(self, args: List[str]):
        """Clear screen or context."""
        if args and args[0] == "context":
            self.current_context.clear()
            self.console.print("[green]Context cleared[/green]")
        else:
            self.console.clear()
    
    async def cmd_history(self, args: List[str]):
        """Show command history."""
        if not self.command_history:
            self.console.print("[dim]No command history[/dim]")
            return
        
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("#", style="dim", width=4)
        table.add_column("Time", style="cyan", width=10)
        table.add_column("Command", style="white")
        table.add_column("Status", style="green", width=8)
        
        for i, entry in enumerate(self.command_history[-20:], 1):  # Show last 20
            status_icon = "✓" if entry['success'] else "❌" if entry['success'] is False else "?"
            status_color = "green" if entry['success'] else "red" if entry['success'] is False else "dim"
            
            table.add_row(
                str(i),
                entry['timestamp'].strftime("%H:%M:%S"),
                entry['command'],
                f"[{status_color}]{status_icon}[/{status_color}]"
            )
        
        self.console.print(table)
    
    async def cmd_exit(self, args: List[str]):
        """Exit the shell."""
        self.running = False
    
    # Helper methods
    
    def _show_general_help(self):
        """Show general help information."""
        help_text = """
[bold blue]Available Commands:[/bold blue]

[cyan]System Commands:[/cyan]
  status        - Show system status and health
  metrics       - Display system metrics
  health        - Check component health
  monitor       - Start real-time monitoring
  
[cyan]Task Management:[/cyan]
  tasks         - List tasks with optional filters
  submit        - Submit a new task
  cancel        - Cancel a task
  
[cyan]Agent Management:[/cyan]
  agents        - List active agents
  
[cyan]Recovery Operations:[/cyan]
  checkpoint    - Create a system checkpoint
  restore       - Restore from checkpoint
  
[cyan]Shell Commands:[/cyan]
  set           - Set context variable
  get           - Get context variable
  clear         - Clear screen or context
  history       - Show command history
  help          - Show this help or help for specific command
  exit/quit     - Exit the shell

[cyan]Aliases:[/cyan]
  h=help, st=status, t=tasks, a=agents, s=submit, c=cancel, m=monitor, q=quit

[dim]Use 'help <command>' for detailed help on a specific command.[/dim]
        """.strip()
        
        self.console.print(Panel(
            Text(help_text),
            title="📚 MAOS Interactive Shell Help",
            border_style="cyan"
        ))
    
    def _get_command_help(self, command: str) -> Text:
        """Get detailed help for a specific command."""
        help_texts = {
            'status': "Show comprehensive system status including uptime, active operations, and component states.",
            'tasks': "List and filter tasks. Usage: tasks [status] [limit]\nExample: tasks running 10",
            'agents': "Display all active agents with their types, status, and current task load.",
            'submit': "Submit a new task interactively. Usage: submit [task_name]\nYou'll be prompted for additional details.",
            'cancel': "Cancel a running task. Usage: cancel [task_id]\nUse task ID from context or provide one.",
            'monitor': "Start real-time system monitoring. Usage: monitor [type]\nTypes: system (default)",
            'checkpoint': "Create a system checkpoint. Usage: checkpoint [name]\nName is auto-generated if not provided.",
            'restore': "Restore from a checkpoint. Usage: restore <checkpoint_id>\nRequires confirmation.",
            'metrics': "Display detailed system and component performance metrics.",
            'health': "Check the health status of all system components.",
            'set': "Set a context variable. Usage: set <key> <value>\nContext variables persist during the session.",
            'get': "Display context variables. Usage: get [key]\nShows all variables if no key specified.",
            'clear': "Clear screen or context. Usage: clear [context]\nUse 'clear context' to reset variables.",
            'history': "Show command history with timestamps and success status.",
        }
        
        return Text(help_texts.get(command, "No detailed help available for this command."))