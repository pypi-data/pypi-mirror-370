"""
Natural Language Interface v2 for MAOS

Integrates the complete orchestration system with SQLite persistence,
task decomposition, session management, and inter-agent communication.
"""

import asyncio
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm

from ..core.orchestrator_brain import OrchestratorBrain
from ..interfaces.sqlite_persistence import SqlitePersistence
from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError


class NaturalLanguageProcessorV2:
    """
    Enhanced natural language processor that uses the complete orchestration system.
    """
    
    def __init__(
        self,
        db_path: str = "./maos.db",
        auto_approve: bool = False
    ):
        """
        Initialize the natural language processor.
        
        Args:
            db_path: Path to SQLite database
            auto_approve: Auto-approve agent proposals
        """
        self.console = Console()
        self.logger = MAOSLogger("natural_language_v2")
        
        # Initialize persistence
        self.db = SqlitePersistence(db_path)
        
        # Initialize orchestrator brain
        self.brain = OrchestratorBrain(
            db=self.db,
            console=self.console,
            auto_approve=auto_approve
        )
        
        # Command history
        self.command_history: List[str] = []
        
        # Command patterns
        self.patterns = {
            'task': [
                r'(?:implement|build|create|develop|work on)\s+(.+)',
                r'(?:please\s+)?(?:can you\s+)?(.+)',
            ],
            'status': [
                r'(?:show|display|list)\s+(?:me\s+)?(?:the\s+)?status',
                r'what(?:\s+agents)?\s+(?:are|is)\s+running',
                r'status',
            ],
            'checkpoint': [
                r'(?:create|save|make)\s+(?:a\s+)?checkpoint(?:\s+(.+))?',
                r'save\s+(?:the\s+)?(?:current\s+)?state(?:\s+as\s+(.+))?',
            ],
            'restore': [
                r'restore\s+(?:from\s+)?(?:checkpoint\s+)?(.+)',
                r'load\s+(?:checkpoint\s+)?(.+)',
            ],
            'list_checkpoints': [
                r'(?:list|show)\s+checkpoints',
                r'what\s+checkpoints\s+(?:are\s+)?available',
            ],
            'pause': [
                r'pause\s+(?:execution)?',
                r'stop\s+temporarily',
            ],
            'resume': [
                r'resume\s+(?:execution)?',
                r'continue\s+(?:execution)?',
            ],
            'stop': [
                r'stop\s+(?:all\s+)?(?:agents|execution)',
                r'shutdown',
                r'exit',
                r'quit',
            ],
            'help': [
                r'help',
                r'what\s+can\s+(?:you|i)\s+do',
                r'(?:show|list)\s+commands',
            ],
        }
    
    async def start(self):
        """Start the natural language processor."""
        await self.brain.start()
        self.console.print("[bold green]MAOS Orchestrator initialized[/bold green]")
        self._show_welcome()
    
    async def stop(self):
        """Stop the natural language processor."""
        await self.brain.stop()
        self.console.print("[bold red]MAOS Orchestrator stopped[/bold red]")
    
    def _show_welcome(self):
        """Show welcome message."""
        welcome = """
[bold cyan]Welcome to MAOS - Multi-Agent Orchestration System[/bold cyan]

I can orchestrate multiple Claude agents to work on complex tasks in parallel.

[yellow]Examples:[/yellow]
• "Implement the requirements in prd.md"
• "Build a REST API with authentication"
• "Review and optimize the codebase"
• "Fix all the failing tests"
• "Create checkpoint my-work"
• "Show status"

Type [bold]help[/bold] for more commands or [bold]exit[/bold] to quit.
        """
        self.console.print(Panel(welcome, title="MAOS v0.3.0"))
    
    def _show_help(self):
        """Show help information."""
        help_text = """
[bold cyan]Available Commands:[/bold cyan]

[yellow]Task Execution:[/yellow]
• Any natural language request will be decomposed into subtasks
• Agents will be automatically created or reused
• Tasks run in parallel when possible

[yellow]Monitoring:[/yellow]
• [bold]status[/bold] - Show current execution status
• [bold]pause[/bold] - Pause execution
• [bold]resume[/bold] - Resume execution

[yellow]Checkpoints:[/yellow]
• [bold]save checkpoint <name>[/bold] - Save current state
• [bold]restore <name>[/bold] - Restore from checkpoint
• [bold]list checkpoints[/bold] - Show available checkpoints

[yellow]Control:[/yellow]
• [bold]stop[/bold] - Stop all agents
• [bold]exit[/bold] - Exit MAOS
• [bold]help[/bold] - Show this help

[green]Tips:[/green]
• Be specific in your requests for better task decomposition
• Use checkpoints to save progress on long-running tasks
• Agents communicate and coordinate automatically
        """
        self.console.print(Panel(help_text, title="Help"))
    
    async def process_command(self, command: str) -> bool:
        """
        Process a natural language command.
        
        Args:
            command: User command
            
        Returns:
            False if should exit, True otherwise
        """
        command = command.strip()
        if not command:
            return True
        
        # Add to history
        self.command_history.append(command)
        
        # Check for patterns
        try:
            # Exit commands
            if self._match_pattern(command, 'stop'):
                if Confirm.ask("Stop all agents and exit?"):
                    return False
                return True
            
            # Help
            elif self._match_pattern(command, 'help'):
                self._show_help()
            
            # Status
            elif self._match_pattern(command, 'status'):
                await self._show_status()
            
            # Checkpoint
            elif match := self._match_pattern(command, 'checkpoint'):
                name = match.group(1) if match.lastindex else None
                await self._create_checkpoint(name)
            
            # Restore
            elif match := self._match_pattern(command, 'restore'):
                name = match.group(1) if match.lastindex else None
                await self._restore_checkpoint(name)
            
            # List checkpoints
            elif self._match_pattern(command, 'list_checkpoints'):
                await self._list_checkpoints()
            
            # Pause
            elif self._match_pattern(command, 'pause'):
                await self.brain.pause_execution()
            
            # Resume
            elif self._match_pattern(command, 'resume'):
                await self.brain.resume_execution()
            
            # Default: treat as task request
            else:
                await self._execute_task(command)
        
        except Exception as e:
            self.logger.log_error(e, {"command": command})
            self.console.print(f"[red]Error: {e}[/red]")
        
        return True
    
    def _match_pattern(self, text: str, pattern_key: str):
        """Match text against patterns."""
        patterns = self.patterns.get(pattern_key, [])
        for pattern in patterns:
            if match := re.match(pattern, text, re.IGNORECASE):
                return match
        return None
    
    async def _execute_task(self, request: str):
        """Execute a task request."""
        self.console.print(f"\n[cyan]Processing request:[/cyan] {request}\n")
        
        # Create execution plan
        plan = await self.brain.process_request(request)
        
        if plan:
            # Execute the plan
            self.console.print("\n[bold green]Starting execution...[/bold green]\n")
            results = await self.brain.execute_plan(plan)
            
            # Show results
            self._show_results(results)
        else:
            self.console.print("[yellow]Execution cancelled[/yellow]")
    
    async def _show_status(self):
        """Show current status."""
        status = await self.brain.get_status()
        
        # Create status table
        table = Table(title="Orchestrator Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("State", status['state'])
        table.add_row("Current Plan", status['current_plan'] or "None")
        table.add_row("Total Agents", str(status['total_agents']))
        table.add_row("Active Sessions", str(status['sessions']))
        
        self.console.print(table)
        
        # Show active agents
        if status['active_agents']:
            agent_table = Table(title="Active Agents")
            agent_table.add_column("Agent", style="cyan")
            agent_table.add_column("Task", style="white")
            agent_table.add_column("Progress", style="yellow")
            
            for agent in status['active_agents']:
                agent_table.add_row(
                    agent['agent_name'],
                    agent['task'],
                    f"{agent['progress']:.0f}%"
                )
            
            self.console.print(agent_table)
    
    async def _create_checkpoint(self, name: Optional[str]):
        """Create a checkpoint."""
        if not name:
            name = Prompt.ask("Checkpoint name")
        
        description = Prompt.ask("Description (optional)", default="")
        
        checkpoint_id = await self.brain.save_checkpoint(name, description)
        self.console.print(f"[green]✓ Checkpoint '{name}' saved (ID: {checkpoint_id[:8]})[/green]")
    
    async def _restore_checkpoint(self, name: Optional[str]):
        """Restore from checkpoint."""
        if not name:
            # List available checkpoints
            await self._list_checkpoints()
            name = Prompt.ask("Checkpoint name to restore")
        
        success = await self.brain.restore_checkpoint(name)
        if success:
            self.console.print(f"[green]✓ Restored from checkpoint '{name}'[/green]")
        else:
            self.console.print(f"[red]Failed to restore checkpoint '{name}'[/red]")
    
    async def _list_checkpoints(self):
        """List available checkpoints."""
        checkpoints = await self.brain.list_checkpoints()
        
        if not checkpoints:
            self.console.print("[yellow]No checkpoints available[/yellow]")
            return
        
        table = Table(title="Available Checkpoints")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Created", style="yellow")
        
        for cp in checkpoints:
            table.add_row(
                cp['name'],
                cp.get('description', ''),
                cp.get('created_at', '')
            )
        
        self.console.print(table)
    
    def _show_results(self, results: Dict[str, Any]):
        """Show execution results."""
        self.console.print("\n[bold cyan]Execution Results:[/bold cyan]\n")
        
        # Show batch results
        for batch_name, batch_results in results.get('batch_results', {}).items():
            self.console.print(f"[yellow]{batch_name}:[/yellow]")
            for task_id, result in batch_results.items():
                status = result.get('status', 'unknown')
                icon = "✓" if status == "completed" else "✗"
                self.console.print(f"  {icon} Task {task_id[:8]}: {status}")
        
        # Show final results
        self.console.print("\n[bold]Agent Results:[/bold]")
        for agent_id, agent_result in results.get('final_results', {}).items():
            self.console.print(f"\n[cyan]{agent_result['agent_name']}:[/cyan]")
            self.console.print(f"  Task: {agent_result['task']}")
            self.console.print(f"  Status: {agent_result['status']}")
            self.console.print(f"  Progress: {agent_result['progress']:.0f}%")
            if agent_result.get('duration'):
                self.console.print(f"  Duration: {agent_result['duration']:.1f}s")
        
        # Show total cost
        if 'total_cost' in results:
            self.console.print(f"\n[yellow]Total cost: ${results['total_cost']:.4f}[/yellow]")


async def run_natural_language_interface():
    """Run the natural language interface."""
    processor = NaturalLanguageProcessorV2()
    
    try:
        await processor.start()
        
        # Main interaction loop
        while True:
            try:
                command = Prompt.ask("\n[bold cyan]MAOS>[/bold cyan]")
                if not await processor.process_command(command):
                    break
            except KeyboardInterrupt:
                if Confirm.ask("\nExit MAOS?"):
                    break
        
    finally:
        await processor.stop()


def main():
    """Main entry point."""
    asyncio.run(run_natural_language_interface())


if __name__ == "__main__":
    main()