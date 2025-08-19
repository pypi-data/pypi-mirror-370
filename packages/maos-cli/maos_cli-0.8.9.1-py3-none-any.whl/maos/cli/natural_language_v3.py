"""
Natural Language Interface v3 for MAOS

Uses the correct Claude Code subagent architecture.
Creates subagent files and provides delegation prompts for Task tool execution.
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

from ..core.orchestrator_brain_v2 import OrchestratorBrainV2
from ..interfaces.sqlite_persistence import SqlitePersistence
from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError


class NaturalLanguageProcessorV3:
    """
    Natural language processor that creates subagents and delegation prompts.
    
    This version correctly uses Claude Code's subagent system.
    """
    
    def __init__(
        self,
        db_path: str = "./maos.db",
        auto_approve: bool = False,
        project_path: str = "."
    ):
        """
        Initialize the natural language processor v3.
        
        Args:
            db_path: Path to SQLite database
            auto_approve: Auto-approve agent proposals
            project_path: Path to project root
        """
        self.console = Console()
        self.logger = MAOSLogger("natural_language_v3")
        
        # Initialize persistence
        self.db = SqlitePersistence(db_path)
        
        # Initialize orchestrator brain v2
        self.brain = OrchestratorBrainV2(
            db=self.db,
            console=self.console,
            auto_approve=auto_approve,
            project_path=project_path
        )
        
        # Command history
        self.command_history: List[str] = []
        
        # Track created subagents
        self.created_subagents: List[str] = []
    
    async def start(self):
        """Start the processor."""
        await self.brain.start()
        self.logger.logger.info("Natural language processor v3 started")
        
        # Show welcome message
        welcome = """
[bold cyan]MAOS v0.6.0 - Claude Code Subagent Orchestrator[/bold cyan]

I help you orchestrate Claude Code subagents for complex tasks.

[yellow]How it works:[/yellow]
1. You describe what you want to accomplish
2. I create specialized subagents in .claude/agents/
3. I provide delegation prompts for Claude Code's Task tool
4. Claude Code executes the subagents in parallel

[green]Example requests:[/green]
• "Analyze this codebase and create documentation"
• "Review code for security issues and fix them"
• "Implement a new feature with tests"
• "Optimize performance across the application"

Type 'help' for commands or describe your task.
"""
        self.console.print(Panel(welcome, border_style="cyan"))
    
    async def stop(self):
        """Stop the processor and clean up."""
        await self.brain.cleanup()
        await self.brain.stop()
        self.logger.logger.info("Natural language processor v3 stopped")
    
    async def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process a natural language command.
        
        Args:
            command: User command
            
        Returns:
            Processing result
        """
        self.command_history.append(command)
        command_lower = command.lower().strip()
        
        # Check for special commands
        if command_lower in ['help', '?', 'h']:
            return await self._show_help()
        
        elif command_lower in ['status', 'st']:
            return await self._show_status()
        
        elif command_lower.startswith('cleanup'):
            return await self._cleanup_subagents()
        
        elif command_lower in ['exit', 'quit', 'q']:
            return await self._exit()
        
        elif command_lower.startswith('list'):
            return await self._list_subagents()
        
        elif command_lower.startswith('execute'):
            return await self._show_execution_instructions()
        
        else:
            # Process as a task request
            return await self._process_task_request(command)
    
    async def _process_task_request(self, request: str) -> Dict[str, Any]:
        """Process a task request by creating subagents."""
        self.console.print(f"\n[cyan]Processing: {request}[/cyan]")
        
        # Process with orchestrator
        result = await self.brain.process_request(request)
        
        if not result:
            return {"status": "cancelled"}
        
        if result.get("status") == "ready":
            # Show created subagents
            self.console.print("\n[bold green]✅ Subagents Created Successfully![/bold green]")
            
            created = result.get("created_subagents", [])
            if created:
                self.created_subagents.extend(created)
                
                table = Table(title="Created Subagents")
                table.add_column("Name", style="cyan")
                table.add_column("Location", style="green")
                
                for agent_name in created:
                    table.add_row(
                        agent_name,
                        f".claude/agents/{agent_name}.md"
                    )
                
                self.console.print(table)
            
            # Show delegation instructions
            self.console.print("\n[bold yellow]📋 Delegation Instructions:[/bold yellow]")
            
            delegation_plan = result.get("delegation_plan", {})
            for batch in delegation_plan.get("batches", []):
                self.console.print(f"\n[cyan]Batch {batch['batch_number']}:[/cyan]")
                
                # Show the delegation prompt
                prompt_panel = f"""
[yellow]Copy and execute this with Claude Code's Task tool:[/yellow]

{batch['delegation_prompt']}

[dim]This will delegate work to the created subagents.[/dim]
"""
                self.console.print(Panel(prompt_panel, border_style="green"))
            
            # Save delegation prompts for later execution
            self.brain._delegation_prompts = [
                batch['delegation_prompt'] 
                for batch in delegation_plan.get("batches", [])
            ]
            
            return {
                "status": "success",
                "created_subagents": created,
                "delegation_plan": delegation_plan,
                "message": "Subagents created. Use the delegation prompts with Claude Code's Task tool."
            }
        
        return result
    
    async def _show_help(self) -> Dict[str, Any]:
        """Show help information."""
        help_text = """
[bold cyan]MAOS Commands:[/bold cyan]

[yellow]Task Processing:[/yellow]
• Any natural language request - Creates subagents and delegation plan
• execute - Show execution instructions for current plan

[yellow]Management:[/yellow]
• status - Show current status and created subagents
• list - List all created subagents
• cleanup - Remove all created subagents

[yellow]Control:[/yellow]
• help - Show this help
• exit/quit - Exit MAOS

[yellow]How to use:[/yellow]
1. Describe your task (e.g., "analyze this codebase")
2. MAOS creates specialized subagents in .claude/agents/
3. Copy the delegation prompts
4. Execute them with Claude Code's Task tool
5. Claude Code runs the subagents in parallel

[dim]Tip: Subagents are specialized for different tasks (analyzer, developer, tester, etc.)[/dim]
"""
        self.console.print(Panel(help_text, title="Help", border_style="blue"))
        return {"status": "help_shown"}
    
    async def _show_status(self) -> Dict[str, Any]:
        """Show current status."""
        status = await self.brain.get_status()
        
        table = Table(title="MAOS Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("State", status['state'])
        table.add_row("Created Subagents", str(len(status['created_subagents'])))
        table.add_row("Active Agents", str(len(status['active_agents'])))
        table.add_row("Delegation Prompts Ready", str(status['delegation_prompts_ready']))
        
        self.console.print(table)
        
        if status['created_subagents']:
            self.console.print("\n[cyan]Created Subagents:[/cyan]")
            for agent in status['created_subagents']:
                self.console.print(f"  • {agent}")
        
        return {"status": "displayed", "data": status}
    
    async def _list_subagents(self) -> Dict[str, Any]:
        """List all created subagents."""
        agents_dir = Path(self.brain.project_path) / ".claude" / "agents"
        
        if not agents_dir.exists():
            self.console.print("[yellow]No subagents directory found[/yellow]")
            return {"status": "no_agents"}
        
        agent_files = list(agents_dir.glob("*.md"))
        
        if not agent_files:
            self.console.print("[yellow]No subagents found[/yellow]")
            return {"status": "no_agents"}
        
        table = Table(title="Claude Code Subagents")
        table.add_column("Name", style="cyan")
        table.add_column("File", style="green")
        table.add_column("Size", style="yellow")
        
        for file in agent_files:
            table.add_row(
                file.stem,
                file.name,
                f"{file.stat().st_size} bytes"
            )
        
        self.console.print(table)
        
        return {"status": "listed", "count": len(agent_files)}
    
    async def _cleanup_subagents(self) -> Dict[str, Any]:
        """Clean up created subagents."""
        if not self.created_subagents:
            self.console.print("[yellow]No subagents to clean up[/yellow]")
            return {"status": "nothing_to_cleanup"}
        
        if not self.brain.auto_approve:
            if not Confirm.ask(f"Remove {len(self.created_subagents)} created subagents?"):
                return {"status": "cancelled"}
        
        await self.brain.cleanup()
        
        cleaned = len(self.created_subagents)
        self.created_subagents.clear()
        
        self.console.print(f"[green]✓ Cleaned up {cleaned} subagents[/green]")
        
        return {"status": "cleaned", "count": cleaned}
    
    async def _show_execution_instructions(self) -> Dict[str, Any]:
        """Show how to execute the current plan."""
        prompts = self.brain.get_delegation_prompts()
        
        if not prompts:
            self.console.print("[yellow]No execution plan available. Process a request first.[/yellow]")
            return {"status": "no_plan"}
        
        instructions = await self.brain.execute_with_task_tool()
        
        return {"status": "instructions_shown", "data": instructions}
    
    async def _exit(self) -> Dict[str, Any]:
        """Exit the processor."""
        if self.created_subagents:
            if Confirm.ask(f"Clean up {len(self.created_subagents)} created subagents before exit?"):
                await self.brain.cleanup()
        
        await self.stop()
        return {"status": "exit"}
    
    async def chat_loop(self):
        """Run interactive chat loop."""
        await self.start()
        
        try:
            while True:
                try:
                    command = Prompt.ask("\n[cyan]MAOS>[/cyan]")
                    
                    result = await self.process_command(command)
                    
                    if result.get("status") == "exit":
                        break
                        
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]Use 'exit' to quit[/yellow]")
                except Exception as e:
                    self.logger.log_error(e, {"operation": "chat_loop"})
                    self.console.print(f"[red]Error: {e}[/red]")
        
        finally:
            await self.stop()


async def main():
    """Main entry point for testing."""
    processor = NaturalLanguageProcessorV3(
        db_path="./maos_v3.db",
        auto_approve=True
    )
    
    await processor.chat_loop()


if __name__ == "__main__":
    asyncio.run(main())