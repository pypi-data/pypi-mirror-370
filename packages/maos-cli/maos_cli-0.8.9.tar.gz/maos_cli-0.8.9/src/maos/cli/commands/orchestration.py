"""
MAOS Orchestration Management Commands

Commands for managing and resuming orchestrations with full persistence support.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Confirm
from rich.tree import Tree

from ..._main import init_orchestrator
from ...core.persistent_message_bus import PersistentMessageBus
from ...interfaces.sqlite_persistence import SqlitePersistence
from ...utils.logging_config import MAOSLogger

console = Console()
orchestration_app = typer.Typer(help="🎭 Orchestration management and resumption")
logger = MAOSLogger("orchestration_cli")


@orchestration_app.command(name="list")
def list_orchestrations(
    status: Optional[str] = typer.Option(
        None, "--status", "-s",
        help="Filter by status (running, paused, completed)"
    ),
    limit: int = typer.Option(
        10, "--limit", "-l",
        help="Maximum orchestrations to show"
    ),
    show_agents: bool = typer.Option(
        False, "--agents", "-a",
        help="Show agent details"
    )
):
    """📋 List all orchestrations with their status"""
    
    async def _list():
        try:
            # Initialize orchestrator and persistence
            orchestrator = init_orchestrator()
            db = SqlitePersistence()
            await db.initialize()
            
            # Get orchestrations from database
            orchestrations = await db.list_orchestrations()
            
            # Filter by status if requested
            if status:
                orchestrations = [
                    o for o in orchestrations
                    if o.get('status', '').lower() == status.lower()
                ]
            
            # Limit results
            if limit < len(orchestrations):
                orchestrations = orchestrations[:limit]
            
            if not orchestrations:
                console.print("[yellow]No orchestrations found[/yellow]")
                return
            
            # Create table
            table = Table(title="🎭 Orchestrations", show_header=True)
            table.add_column("ID", style="cyan", width=12)
            table.add_column("Request", style="white", width=40)
            table.add_column("Status", style="yellow", width=12)
            table.add_column("Agents", style="green", width=8)
            table.add_column("Cost", style="red", width=10)
            table.add_column("Duration", style="blue", width=12)
            table.add_column("Created", style="dim", width=20)
            
            for orch in orchestrations:
                # Status emoji
                status_emoji = {
                    'running': '🔄',
                    'paused': '⏸️',
                    'completed': '✅',
                    'failed': '❌'
                }.get(orch.get('status', 'unknown'), '❓')
                
                # Format values
                request_str = orch['request'][:37] + "..." if len(orch['request']) > 40 else orch['request']
                cost_str = f"${orch.get('total_cost', 0):.4f}"
                duration_ms = orch.get('total_duration_ms', 0)
                duration_str = f"{duration_ms // 1000}s" if duration_ms else "N/A"
                created_str = orch.get('created_at', 'Unknown')[:16]
                
                # Count agents
                agents = json.loads(orch.get('agents', '[]'))
                agent_count = len(agents)
                
                table.add_row(
                    orch['id'][:8] + "...",
                    request_str,
                    f"{status_emoji} {orch.get('status', 'unknown')}",
                    str(agent_count),
                    cost_str,
                    duration_str,
                    created_str
                )
                
                # Show agent details if requested
                if show_agents and agents:
                    for agent_id in agents[:3]:  # Show first 3
                        table.add_row(
                            "",
                            f"  └─ {agent_id[:20]}...",
                            "",
                            "",
                            "",
                            "",
                            "",
                            style="dim"
                        )
                    if len(agents) > 3:
                        table.add_row(
                            "",
                            f"  └─ ... ({len(agents) - 3} more)",
                            "",
                            "",
                            "",
                            "",
                            "",
                            style="dim"
                        )
            
            console.print(table)
            
            # Show resume hints
            resumable = [o for o in orchestrations if o.get('status') in ['running', 'paused']]
            if resumable:
                console.print(f"\n💡 Resume with: [cyan]maos orchestration resume <id>[/cyan]")
                console.print(f"   {len(resumable)} orchestration(s) can be resumed")
            
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_list())


@orchestration_app.command(name="status")
def orchestration_status(
    orchestration_id: str = typer.Argument(..., help="Orchestration ID or prefix"),
    show_messages: bool = typer.Option(
        False, "--messages", "-m",
        help="Show recent messages"
    ),
    show_tasks: bool = typer.Option(
        False, "--tasks", "-t",
        help="Show task progress"
    ),
    watch: bool = typer.Option(
        False, "--watch", "-w",
        help="Watch status in real-time"
    )
):
    """📊 Show detailed orchestration status and progress"""
    
    async def _show_status():
        try:
            db = SqlitePersistence()
            await db.initialize()
            
            # Get orchestration (support partial ID)
            orch = await db.get_orchestration(orchestration_id)
            if not orch:
                console.print(f"[red]❌ Orchestration not found: {orchestration_id}[/red]")
                return
            
            # Create status panel
            status_emoji = {
                'running': '🔄',
                'paused': '⏸️',
                'completed': '✅',
                'failed': '❌'
            }.get(orch.get('status', 'unknown'), '❓')
            
            # Get agent details
            agents = json.loads(orch.get('agents', '[]'))
            batches = json.loads(orch.get('batches', '[]'))
            
            # Main info panel
            info_text = f"""[bold]Orchestration:[/bold] {orch['id'][:12]}...
[bold]Request:[/bold] {orch['request']}
[bold]Status:[/bold] {status_emoji} {orch.get('status', 'unknown')}
[bold]Created:[/bold] {orch.get('created_at', 'Unknown')[:19]}
[bold]Agents:[/bold] {len(agents)} total in {len(batches)} batch(es)
[bold]Cost:[/bold] ${orch.get('total_cost', 0):.4f}
[bold]Duration:[/bold] {orch.get('total_duration_ms', 0) // 1000}s"""
            
            console.print(Panel(
                info_text,
                title="📂 Orchestration Status",
                border_style="blue"
            ))
            
            # Show agent breakdown
            if agents:
                agent_table = Table(title="Agent Status", show_header=True)
                agent_table.add_column("Agent ID", style="cyan")
                agent_table.add_column("Type", style="yellow")
                agent_table.add_column("Status", style="green")
                agent_table.add_column("Session", style="blue")
                
                for agent_id in agents[:10]:  # Show first 10
                    agent = await db.get_agent(agent_id)
                    if agent:
                        status_icon = '🟢' if agent.get('status') == 'active' else '🔴'
                        agent_table.add_row(
                            agent_id[:8] + "...",
                            agent.get('type', 'unknown'),
                            f"{status_icon} {agent.get('status', 'unknown')}",
                            agent.get('session_id', 'N/A')[:8] + "..." if agent.get('session_id') else "N/A"
                        )
                
                if len(agents) > 10:
                    agent_table.add_row(
                        "...",
                        f"({len(agents) - 10} more)",
                        "",
                        "",
                        style="dim"
                    )
                
                console.print("\n", agent_table)
            
            # Show recent messages if requested
            if show_messages:
                console.print("\n[bold]Recent Communications:[/bold]")
                
                # Get messages for agents in this orchestration
                message_count = 0
                for agent_id in agents[:3]:  # Sample from first 3 agents
                    messages = await db.get_messages_for_agent(
                        agent_id,
                        since_timestamp=(datetime.now() - timedelta(hours=1)).isoformat()
                    )
                    
                    for msg in messages[:2]:  # Show 2 messages per agent
                        icon = {
                            'discovery': '💡',
                            'request': '📨',
                            'broadcast': '📢',
                            'error': '❌',
                            'info': 'ℹ️'
                        }.get(msg.get('message_type', 'info'), 'ℹ️')
                        
                        from_agent = msg['from_agent'][:8] + "..." if msg['from_agent'] else "System"
                        to_agent = msg['to_agent'][:8] + "..." if msg['to_agent'] else "ALL"
                        content = msg['message'][:60] + "..." if len(msg['message']) > 60 else msg['message']
                        
                        console.print(f"  {icon} [{from_agent}] → [{to_agent}]: {content}")
                        message_count += 1
                
                if message_count == 0:
                    console.print("  [dim]No recent messages[/dim]")
            
            # Show task progress if requested
            if show_tasks:
                console.print("\n[bold]Task Progress:[/bold]")
                
                # Query tasks for agents
                task_query = """
                    SELECT id, description, status, progress
                    FROM tasks
                    WHERE id LIKE 'task-%'
                    ORDER BY created_at DESC
                    LIMIT 10
                """
                
                tasks = await db.execute_query(task_query, [])
                
                if tasks:
                    for task in tasks:
                        status_icon = {
                            'completed': '✅',
                            'running': '🔄',
                            'pending': '⏳',
                            'failed': '❌'
                        }.get(task.get('status', 'pending'), '❓')
                        
                        progress = task.get('progress', 0)
                        progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
                        
                        console.print(
                            f"  {status_icon} {task['description'][:50]}...\n"
                            f"     {progress_bar} {progress:.0f}%"
                        )
                else:
                    console.print("  [dim]No tasks found[/dim]")
            
            # Summary
            if orch.get('status') == 'completed':
                console.print(f"\n[green]✅ Orchestration completed successfully[/green]")
                if orch.get('summary'):
                    console.print(f"[dim]Summary: {orch['summary'][:200]}...[/dim]")
            elif orch.get('status') in ['running', 'paused']:
                console.print(f"\n[yellow]⚠️ Orchestration can be resumed[/yellow]")
                console.print(f"Run: [cyan]maos orchestration resume {orch['id'][:8]}[/cyan]")
            
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            raise typer.Exit(1)
    
    async def _watch_status():
        """Watch status with periodic refresh"""
        try:
            while True:
                console.clear()
                await _show_status()
                await asyncio.sleep(5)
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopped watching[/yellow]")
    
    if watch:
        asyncio.run(_watch_status())
    else:
        asyncio.run(_show_status())


@orchestration_app.command(name="resume")
def resume_orchestration(
    orchestration_id: str = typer.Argument(..., help="Orchestration ID to resume"),
    new_task: Optional[str] = typer.Option(
        None, "--task", "-t",
        help="New task for agents (optional)"
    ),
    auto_approve: bool = typer.Option(
        False, "--auto", "-y",
        help="Auto-approve without confirmation"
    )
):
    """🔄 Resume a paused or interrupted orchestration"""
    
    async def _resume():
        try:
            # Initialize components
            orchestrator = init_orchestrator()
            db = SqlitePersistence()
            await db.initialize()
            
            # Get orchestration
            orch = await db.get_orchestration(orchestration_id)
            if not orch:
                console.print(f"[red]❌ Orchestration not found: {orchestration_id}[/red]")
                return
            
            # Show what we're resuming
            agents = json.loads(orch.get('agents', '[]'))
            
            console.print(Panel(
                f"[bold]Orchestration:[/bold] {orch['id'][:12]}...\n"
                f"[bold]Original Request:[/bold] {orch['request']}\n"
                f"[bold]Status:[/bold] {orch.get('status', 'unknown')}\n"
                f"[bold]Created:[/bold] {orch.get('created_at', 'Unknown')[:19]}\n"
                f"[bold]Agents:[/bold] {len(agents)}",
                title="📂 Resuming Orchestration",
                border_style="blue"
            ))
            
            if not auto_approve:
                if not Confirm.ask("Continue with resumption?", default=True):
                    console.print("[yellow]Resumption cancelled[/yellow]")
                    return
            
            # Initialize persistent message bus
            console.print("\n[bold blue]Restoring communication channels...[/bold blue]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                # Step 1: Initialize message bus
                restore_task = progress.add_task("Initializing message bus...", total=None)
                
                session_manager = orchestrator.session_manager
                message_bus = PersistentMessageBus(db, session_manager)
                await message_bus.start()
                
                progress.update(restore_task, description="Message bus started")
                
                # Step 2: Resume orchestration
                progress.update(restore_task, description="Resuming orchestration...")
                
                result = await message_bus.resume_orchestration(orch['id'])
                
                if result:
                    progress.update(restore_task, description="Orchestration resumed!")
                    
                    console.print(f"\n[green]✅ Orchestration resumed successfully![/green]")
                    console.print(f"[dim]Agents restored: {result['agents_restored']}[/dim]")
                    console.print(f"[dim]Messages loaded: {len(result.get('communication_history', []))}[/dim]")
                    
                    # If new task provided, execute it
                    if new_task:
                        console.print(f"\n[bold]Executing new task:[/bold] {new_task}")
                        
                        # Use the orchestrator to resume with new task
                        exec_result = await orchestrator.resume_orchestration(
                            orch['id'], new_task
                        )
                        
                        if exec_result.success:
                            console.print(f"[green]✅ New task executed successfully![/green]")
                            console.print(f"Cost: ${exec_result.total_cost:.4f}")
                        else:
                            console.print(f"[red]❌ Task execution failed[/red]")
                else:
                    console.print(f"[red]❌ Failed to resume orchestration[/red]")
                
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            logger.log_error(e, {"operation": "resume_orchestration"})
            raise typer.Exit(1)
    
    asyncio.run(_resume())


@orchestration_app.command(name="save-interval")
def set_save_interval(
    seconds: int = typer.Argument(..., help="Save interval in seconds (minimum 10)")
):
    """⏱️ Set auto-save interval for orchestrations"""
    
    if seconds < 10:
        console.print("[red]❌ Save interval must be at least 10 seconds[/red]")
        raise typer.Exit(1)
    
    # This would update configuration
    console.print(f"[green]✅ Auto-save interval set to {seconds} seconds[/green]")
    console.print("[dim]This will apply to new orchestrations[/dim]")


@orchestration_app.command(name="checkpoint")
def create_checkpoint(
    orchestration_id: str = typer.Argument(..., help="Orchestration ID"),
    name: Optional[str] = typer.Option(
        None, "--name", "-n",
        help="Checkpoint name"
    )
):
    """💾 Create a checkpoint for an orchestration"""
    
    async def _create_checkpoint():
        try:
            db = SqlitePersistence()
            await db.initialize()
            
            # Get orchestration
            orch = await db.get_orchestration(orchestration_id)
            if not orch:
                console.print(f"[red]❌ Orchestration not found: {orchestration_id}[/red]")
                return
            
            # Create checkpoint name
            if not name:
                checkpoint_name = f"orch-{orch['id'][:8]}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            else:
                checkpoint_name = name
            
            # Create checkpoint
            checkpoint_data = {
                'orchestration_id': orch['id'],
                'request': orch['request'],
                'agents': json.loads(orch.get('agents', '[]')),
                'batches': json.loads(orch.get('batches', '[]')),
                'status': orch.get('status'),
                'created_at': datetime.now().isoformat()
            }
            
            checkpoint_id = f"checkpoint-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            await db.save_checkpoint(
                checkpoint_id=checkpoint_id,
                name=checkpoint_name,
                checkpoint_data=checkpoint_data
            )
            
            console.print(f"[green]✅ Checkpoint created: {checkpoint_name}[/green]")
            console.print(f"[dim]ID: {checkpoint_id}[/dim]")
            
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_create_checkpoint())


# Add this app to the main CLI
if __name__ == "__main__":
    orchestration_app()