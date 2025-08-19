"""
Natural Language Processor V7 - Autonomous Claude SDK Execution
"""

import asyncio
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

from ..core.orchestrator_v7 import OrchestratorV7
from ..interfaces.sqlite_persistence import SqlitePersistence

console = Console()


class NaturalLanguageProcessorV7:
    """
    Natural language interface for autonomous Claude orchestration.
    Actually runs Claude agents in parallel using the SDK.
    """
    
    def __init__(self, db_path: Path = Path("maos.db"), api_key: Optional[str] = None):
        self.db_path = db_path
        self.api_key = api_key
        self.persistence = None
        self.orchestrator = None
        self.session_history = []
        self.auto_approve = False  # FIX: Initialize auto_approve!
        
    async def initialize(self):
        """Initialize the processor"""
        self.persistence = SqlitePersistence(self.db_path)
        await self.persistence.initialize()
        self.orchestrator = OrchestratorV7(self.persistence, self.api_key)
        
    async def process(self, input_text: str) -> bool:
        """Process natural language input"""
        # Handle commands
        if input_text.lower() in ['exit', 'quit', 'bye']:
            return False
        
        if input_text.lower() == 'help':
            self._show_help()
            return True
        
        if input_text.lower() == 'status':
            await self._show_status()
            return True
        
        if input_text.lower().startswith('resume-all '):
            orchestration_id = input_text.split(' ', 1)[1]
            new_task = Prompt.ask("Continue all agents with")
            await self.orchestrator.resume_orchestration(orchestration_id, new_task)
            return True
        
        if input_text.lower().startswith('resume '):
            session_id = input_text.split(' ', 1)[1]
            new_task = Prompt.ask("Continue with")
            await self.orchestrator.resume_single_agent(session_id, new_task)
            return True
        
        if input_text.lower() == 'list':
            await self._list_orchestrations()
            return True
        
        # Process as task request
        await self._process_task_request(input_text)
        return True
    
    async def _process_task_request(self, request: str):
        """Process a task orchestration request"""
        console.print("\n[bold cyan]🤖 MAOS AUTONOMOUS ORCHESTRATOR v0.7.0[/bold cyan]")
        console.print("[yellow]Using Claude SDK for real parallel execution[/yellow]\n")
        
        try:
            # Check for auto-approve flag in request text or from CLI
            auto_approve_request = "--auto" in request or "--auto-approve" in request
            if auto_approve_request:
                request = request.replace("--auto", "").replace("--auto-approve", "").strip()
            
            # Use CLI auto-approve or request auto-approve
            final_auto_approve = self.auto_approve or auto_approve_request
            
            # Run orchestration
            result = await self.orchestrator.orchestrate(request, final_auto_approve)
            
            # Store in history
            self.session_history.append({
                "request": request,
                "result": result
            })
            
            # Show results
            if result.success:
                console.print("\n[bold green]✅ Orchestration Complete![/bold green]")
                
                # Show agent results table
                table = Table(title="Agent Execution Results")
                table.add_column("Agent ID", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Cost", style="yellow")
                table.add_column("Duration", style="blue")
                
                for batch in result.batch_results:
                    for agent_result in batch:
                        status = "✅" if agent_result.get("success") else "❌"
                        cost = f"${agent_result.get('cost', 0):.4f}"
                        duration = f"{agent_result.get('duration_ms', 0)}ms"
                        table.add_row(
                            agent_result['agent_id'],
                            status,
                            cost,
                            duration
                        )
                
                console.print(table)
                
                # Show session IDs for resuming
                console.print("\n[bold]Session IDs for resuming:[/bold]")
                for batch in result.batch_results:
                    for agent_result in batch:
                        if agent_result.get("session_id"):
                            console.print(f"  • {agent_result['agent_id']}: [cyan]{agent_result['session_id']}[/cyan]")
            else:
                console.print("\n[bold red]❌ Orchestration failed or was cancelled[/bold red]")
                
        except Exception as e:
            console.print(f"\n[bold red]Error: {e}[/bold red]")
            import traceback
            traceback.print_exc()
    
    def _show_help(self):
        """Show help information"""
        help_text = """
[bold cyan]MAOS Autonomous Orchestrator - Help[/bold cyan]

[bold]Natural Language Commands:[/bold]
  • Just describe what you want to do
  • Add --auto to skip confirmation
  
[bold]Examples:[/bold]
  • "Analyze this codebase and write tests"
  • "Review all Python files for security issues --auto"
  • "Build a REST API with authentication"
  
[bold]System Commands:[/bold]
  • [cyan]help[/cyan] - Show this help
  • [cyan]status[/cyan] - Show orchestrator status
  • [cyan]list[/cyan] - List all saved orchestrations
  • [cyan]resume-all <orchestration_id>[/cyan] - Resume entire orchestration (all agents)
  • [cyan]resume <session_id>[/cyan] - Resume single agent session
  • [cyan]exit[/cyan] - Exit MAOS

[bold]Features:[/bold]
  ✅ Runs Claude agents autonomously (no manual intervention)
  ✅ True parallel execution using multiple SDK processes
  ✅ Session persistence and resumption
  ✅ Automatic task decomposition
  ✅ Cost and performance tracking
"""
        console.print(Panel(help_text, title="Help", border_style="blue"))
    
    async def _show_status(self):
        """Show current status"""
        console.print("\n[bold]Orchestrator Status:[/bold]")
        
        # Get running agents
        running = self.orchestrator.executor.running_agents
        if running:
            console.print(f"  • Running agents: {len(running)}")
            for agent_id in running:
                console.print(f"    - {agent_id}")
        else:
            console.print("  • No agents currently running")
        
        # Show history
        if self.session_history:
            console.print(f"\n  • Sessions in history: {len(self.session_history)}")
            for i, session in enumerate(self.session_history[-3:], 1):
                console.print(f"    {i}. {session['request'][:50]}...")
        
        # Database stats
        try:
            stats = await self.persistence.get_statistics()
            console.print(f"\n  • Database: {self.db_path}")
            console.print(f"    - Agents: {stats.get('agents', 0)}")
            console.print(f"    - Tasks: {stats.get('tasks', 0)}")
            console.print(f"    - Sessions: {stats.get('sessions', 0)}")
        except Exception as e:
            console.print(f"\n  • Database: {self.db_path} (error: {e})")
    
    async def _list_orchestrations(self):
        """List all saved orchestrations"""
        console.print("\n[bold]Saved Orchestrations:[/bold]")
        
        orchestrations = await self.orchestrator.list_orchestrations()
        if orchestrations:
            table = Table()
            table.add_column("ID", style="cyan")
            table.add_column("Request", style="white")
            table.add_column("Agents", style="green")
            table.add_column("Status", style="yellow")
            
            for orch in orchestrations:
                table.add_row(
                    orch.orchestration_id[:8],
                    orch.request[:50] + "..." if len(orch.request) > 50 else orch.request,
                    str(len(orch.agents)),
                    orch.status
                )
            
            console.print(table)
            console.print("\n[dim]Use 'resume-all <ID>' to resume an entire orchestration[/dim]")
        else:
            console.print("  No saved orchestrations found")
    
    async def run(self, auto_approve: bool = False):
        """Run the interactive orchestrator"""
        self.auto_approve = auto_approve
        await self.initialize()
        
        console.print("\n" + "="*60)
        console.print("[bold cyan]🚀 MAOS v0.7.0 - Autonomous Multi-Agent Orchestrator[/bold cyan]")
        console.print("[yellow]Using Claude SDK for real parallel execution[/yellow]")
        console.print("="*60)
        console.print("\nType 'help' for commands or describe what you want to do.")
        console.print("[dim]Add --auto to skip confirmation prompts[/dim]\n")
        
        while True:
            try:
                user_input = Prompt.ask("[bold green]MAOS>[/bold green]")
                if not await self.process(user_input):
                    break
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
        
        # Cleanup
        if self.orchestrator.executor.running_agents:
            console.print("\n[yellow]Stopping running agents...[/yellow]")
            await self.orchestrator.executor.kill_all_agents()
        
        await self.persistence.close()
        console.print("\n[cyan]Goodbye! 👋[/cyan]")


async def main():
    """Main entry point"""
    processor = NaturalLanguageProcessorV7()
    await processor.run()


if __name__ == "__main__":
    asyncio.run(main())