"""
Session management commands for MAOS CLI.

Provides user-friendly commands for managing sessions, checkpoints, and memory.
"""

import asyncio
from typing import Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import json

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

from ..interfaces.sqlite_persistence import SqlitePersistence
from ..core.orchestrator_brain import OrchestratorBrain
from ..cli.natural_language_v2 import NaturalLanguageProcessorV2

app = typer.Typer(help="Session and memory management commands")
console = Console()


@app.command()
def sessions(
    db_path: str = typer.Option("./maos.db", help="Database path"),
    active_only: bool = typer.Option(False, help="Show only active sessions"),
    limit: int = typer.Option(20, help="Number of sessions to show")
):
    """List all saved sessions with their status and details."""
    
    async def list_sessions():
        db = SqlitePersistence(db_path)
        await db.initialize()
        
        # Get all sessions
        async with db.transaction() as conn:
            query = """
                SELECT 
                    s.id as session_id,
                    s.agent_id,
                    a.name as agent_name,
                    s.created_at,
                    s.conversation_history,
                    a.status as agent_status,
                    COUNT(DISTINCT t.id) as task_count,
                    MAX(m.timestamp) as last_activity
                FROM sessions s
                LEFT JOIN agents a ON s.agent_id = a.id
                LEFT JOIN tasks t ON json_extract(t.assigned_agents, '$') LIKE '%' || a.id || '%'
                LEFT JOIN messages m ON (m.from_agent = a.id OR m.to_agent = a.id)
                GROUP BY s.id
                ORDER BY s.created_at DESC
                LIMIT ?
            """
            
            async with conn.execute(query, (limit,)) as cursor:
                sessions_data = await cursor.fetchall()
        
        if not sessions_data:
            console.print("[yellow]No sessions found[/yellow]")
            await db.close()
            return
        
        # Create table
        table = Table(title=f"📚 MAOS Sessions (showing {len(sessions_data)} of latest)")
        table.add_column("Session ID", style="cyan", width=20)
        table.add_column("Agent", style="green")
        table.add_column("Created", style="yellow")
        table.add_column("Last Activity", style="magenta")
        table.add_column("Tasks", style="blue")
        table.add_column("Status", style="white")
        table.add_column("Memory Size", style="dim")
        
        for row in sessions_data:
            session_id = row[0][:16] + "..."
            agent_name = row[2] or "Unknown"
            created = datetime.fromisoformat(row[3]).strftime("%Y-%m-%d %H:%M")
            
            # Calculate last activity
            if row[7]:  # last_activity
                last_activity = datetime.fromisoformat(row[7])
                time_ago = datetime.now() - last_activity
                if time_ago.days > 0:
                    activity_str = f"{time_ago.days}d ago"
                elif time_ago.seconds > 3600:
                    activity_str = f"{time_ago.seconds // 3600}h ago"
                else:
                    activity_str = f"{time_ago.seconds // 60}m ago"
            else:
                activity_str = "Never"
            
            # Get conversation size
            conv_history = row[4]
            if conv_history:
                memory_size = f"{len(conv_history) // 1024}KB"
            else:
                memory_size = "0KB"
            
            # Determine status
            status = row[5] or "inactive"
            if status == "active":
                status_display = "🟢 Active"
            elif active_only:
                continue  # Skip inactive if active_only
            else:
                status_display = "⚫ Inactive"
            
            task_count = row[6] or 0
            
            table.add_row(
                session_id,
                agent_name,
                created,
                activity_str,
                str(task_count),
                status_display,
                memory_size
            )
        
        console.print(table)
        
        # Show help
        help_text = """
[dim]Commands:
• `maos resume <session_id>` - Resume a specific session
• `maos continue` - Continue the most recent session
• `maos checkpoint list` - Show saved checkpoints
• `maos memory <session_id>` - View session memory details[/dim]
"""
        console.print(help_text)
        
        await db.close()
    
    asyncio.run(list_sessions())


@app.command()
def resume(
    session_id: str = typer.Argument(..., help="Session ID to resume"),
    db_path: str = typer.Option("./maos.db", help="Database path")
):
    """Resume a specific session with full memory and context."""
    
    async def resume_session():
        console.print(f"[cyan]Resuming session {session_id}...[/cyan]")
        
        db = SqlitePersistence(db_path)
        await db.initialize()
        
        # Get session details
        session = await db.get_session(session_id)
        if not session:
            console.print(f"[red]Session {session_id} not found[/red]")
            await db.close()
            return
        
        # Get agent details
        agent = await db.get_agent(session['agent_id'])
        if not agent:
            console.print(f"[red]Agent for session not found[/red]")
            await db.close()
            return
        
        # Show session info
        info_panel = f"""
[bold cyan]📂 Resuming Session[/bold cyan]

[yellow]Session ID:[/yellow] {session_id}
[yellow]Agent:[/yellow] {agent['name']} ({agent['type']})
[yellow]Created:[/yellow] {session['created_at']}
[yellow]Memory:[/yellow] {len(session.get('conversation_history', [])) // 1024}KB of conversation history

[green]What happens now:[/green]
• Agent will wake up with full memory
• All previous context is restored
• Work continues from where it left off
• No need to re-explain anything

[dim]Press Ctrl+C to pause session[/dim]
"""
        console.print(Panel(info_panel, border_style="cyan"))
        
        # Initialize processor with resumed session
        processor = NaturalLanguageProcessorV2(db_path=db_path, auto_approve=True)
        await processor.start()
        
        # Resume the session
        continuation_task = Prompt.ask(
            "[yellow]What would you like the agent to do?[/yellow]",
            default="Continue your previous work"
        )
        
        # Process the continuation
        await processor.brain.session_manager.resume_session(
            agent['id'],
            session_id,
            continuation_task
        )
        
        console.print("[green]✓ Session resumed successfully[/green]")
        
        # Enter interactive mode
        await processor.chat_loop()
        
        await processor.stop()
        await db.close()
    
    asyncio.run(resume_session())


@app.command()
def continue_session(
    db_path: str = typer.Option("./maos.db", help="Database path")
):
    """Continue the most recent session."""
    
    async def continue_last():
        db = SqlitePersistence(db_path)
        await db.initialize()
        
        # Get most recent session
        async with db.transaction() as conn:
            query = """
                SELECT s.id, s.agent_id, a.name
                FROM sessions s
                JOIN agents a ON s.agent_id = a.id
                ORDER BY s.created_at DESC
                LIMIT 1
            """
            async with conn.execute(query) as cursor:
                row = await cursor.fetchone()
        
        if not row:
            console.print("[yellow]No sessions found to continue[/yellow]")
            await db.close()
            return
        
        session_id, agent_id, agent_name = row
        
        console.print(f"[cyan]Continuing most recent session:[/cyan]")
        console.print(f"  Session: {session_id[:16]}...")
        console.print(f"  Agent: {agent_name}")
        
        await db.close()
        
        # Resume that session
        resume(session_id, db_path)
    
    asyncio.run(continue_last())


@app.command()
def memory(
    session_id: str = typer.Argument(..., help="Session ID to inspect"),
    db_path: str = typer.Option("./maos.db", help="Database path"),
    show_full: bool = typer.Option(False, help="Show full conversation history")
):
    """View detailed memory and conversation history for a session."""
    
    async def show_memory():
        db = SqlitePersistence(db_path)
        await db.initialize()
        
        # Get session with full history
        session = await db.get_session(session_id)
        if not session:
            console.print(f"[red]Session {session_id} not found[/red]")
            await db.close()
            return
        
        # Get agent info
        agent = await db.get_agent(session['agent_id'])
        
        # Parse conversation history
        history = session.get('conversation_history', [])
        if isinstance(history, str):
            try:
                history = json.loads(history)
            except:
                history = []
        
        # Display memory overview
        memory_panel = f"""
[bold magenta]🧠 Session Memory Analysis[/bold magenta]

[yellow]Session:[/yellow] {session_id}
[yellow]Agent:[/yellow] {agent['name'] if agent else 'Unknown'}
[yellow]Created:[/yellow] {session['created_at']}

[cyan]Memory Statistics:[/cyan]
• Total exchanges: {len(history)}
• Memory size: {len(str(history)) // 1024}KB
• Unique topics: {len(set([m.get('topic', 'general') for m in history if isinstance(m, dict)]))}

[cyan]Memory Types:[/cyan]
• [green]Working Memory:[/green] Current task context and immediate goals
• [yellow]Episodic Memory:[/yellow] Specific events and interactions
• [blue]Semantic Memory:[/blue] Facts and knowledge learned
• [magenta]Procedural Memory:[/magenta] How to perform tasks
"""
        console.print(Panel(memory_panel, border_style="magenta"))
        
        # Show conversation samples or full history
        if show_full and history:
            console.print("\n[bold]Full Conversation History:[/bold]\n")
            for i, exchange in enumerate(history[-20:], 1):  # Last 20 exchanges
                if isinstance(exchange, dict):
                    role = exchange.get('role', 'unknown')
                    content = exchange.get('content', '')[:200]
                    timestamp = exchange.get('timestamp', '')
                    
                    if role == 'user':
                        console.print(f"[cyan]{i}. User:[/cyan] {content}")
                    else:
                        console.print(f"[green]{i}. Agent:[/green] {content}")
                    
                    if timestamp:
                        console.print(f"   [dim]{timestamp}[/dim]")
        elif history:
            # Show summary
            console.print("\n[bold]Recent Memory Samples:[/bold]\n")
            
            # Get last 5 exchanges
            recent = history[-5:] if len(history) >= 5 else history
            for exchange in recent:
                if isinstance(exchange, dict):
                    content = exchange.get('content', '')[:100] + "..."
                    role = exchange.get('role', 'unknown')
                    
                    if role == 'user':
                        console.print(f"[cyan]User:[/cyan] {content}")
                    else:
                        console.print(f"[green]Agent:[/green] {content}")
            
            console.print(f"\n[dim]Showing {len(recent)} of {len(history)} total exchanges[/dim]")
            console.print("[dim]Use --show-full to see complete history[/dim]")
        
        # Show related data
        console.print("\n[bold]Related Data:[/bold]")
        
        # Get tasks
        async with db.transaction() as conn:
            query = """
                SELECT COUNT(*) FROM tasks 
                WHERE json_extract(assigned_agents, '$') LIKE '%' || ? || '%'
            """
            async with conn.execute(query, (session['agent_id'],)) as cursor:
                task_count = (await cursor.fetchone())[0]
        
        # Get messages
        async with db.transaction() as conn:
            query = """
                SELECT COUNT(*) FROM messages 
                WHERE from_agent = ? OR to_agent = ?
            """
            async with conn.execute(query, (session['agent_id'], session['agent_id'])) as cursor:
                message_count = (await cursor.fetchone())[0]
        
        console.print(f"  • Tasks completed: {task_count}")
        console.print(f"  • Messages exchanged: {message_count}")
        
        await db.close()
    
    asyncio.run(show_memory())


@app.command()
def checkpoint(
    action: str = typer.Argument("list", help="Action: list, create, restore, delete"),
    name: Optional[str] = typer.Argument(None, help="Checkpoint name"),
    db_path: str = typer.Option("./maos.db", help="Database path")
):
    """Manage execution checkpoints."""
    
    async def manage_checkpoints():
        db = SqlitePersistence(db_path)
        await db.initialize()
        
        if action == "list":
            # List all checkpoints
            checkpoints = await db.list_checkpoints()
            
            if not checkpoints:
                console.print("[yellow]No checkpoints found[/yellow]")
            else:
                table = Table(title="💾 Saved Checkpoints")
                table.add_column("Name", style="cyan")
                table.add_column("Created", style="yellow")
                table.add_column("Description", style="green")
                table.add_column("Size", style="dim")
                
                for cp in checkpoints:
                    created = datetime.fromisoformat(cp['created_at']).strftime("%Y-%m-%d %H:%M")
                    desc = cp.get('description', 'No description')[:50]
                    size = f"{len(str(cp.get('state_data', {}))) // 1024}KB"
                    
                    table.add_row(
                        cp['name'],
                        created,
                        desc,
                        size
                    )
                
                console.print(table)
                console.print("\n[dim]Use `maos checkpoint restore <name>` to restore[/dim]")
        
        elif action == "create" and name:
            # Create new checkpoint
            desc = Prompt.ask("Description", default="Manual checkpoint")
            
            brain = OrchestratorBrain(db, console, auto_approve=True)
            await brain.start()
            
            checkpoint_id = await brain.save_checkpoint(name, desc)
            
            console.print(f"[green]✓ Checkpoint '{name}' created[/green]")
            console.print(f"[dim]ID: {checkpoint_id}[/dim]")
            
            await brain.stop()
        
        elif action == "restore" and name:
            # Restore checkpoint
            brain = OrchestratorBrain(db, console, auto_approve=True)
            await brain.start()
            
            success = await brain.restore_checkpoint(name)
            
            if success:
                console.print(f"[green]✓ Checkpoint '{name}' restored[/green]")
                
                # Continue execution
                if Confirm.ask("Continue execution from checkpoint?"):
                    processor = NaturalLanguageProcessorV2(db_path=db_path, auto_approve=True)
                    await processor.start()
                    await processor.chat_loop()
                    await processor.stop()
            
            await brain.stop()
        
        elif action == "delete" and name:
            # Delete checkpoint
            if Confirm.ask(f"Delete checkpoint '{name}'?"):
                # Note: Would need to add delete_checkpoint method to SqlitePersistence
                console.print(f"[yellow]Checkpoint deletion not yet implemented[/yellow]")
        
        else:
            console.print("[red]Invalid action or missing name[/red]")
            console.print("Usage: maos checkpoint [list|create|restore|delete] [name]")
        
        await db.close()
    
    asyncio.run(manage_checkpoints())


@app.command()
def cleanup(
    days: int = typer.Option(30, help="Delete sessions older than N days"),
    db_path: str = typer.Option("./maos.db", help="Database path"),
    dry_run: bool = typer.Option(True, help="Show what would be deleted without deleting")
):
    """Clean up old sessions and data."""
    
    async def cleanup_old_data():
        db = SqlitePersistence(db_path)
        await db.initialize()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Count what would be deleted
        async with db.transaction() as conn:
            # Old sessions
            query = "SELECT COUNT(*) FROM sessions WHERE created_at < ?"
            async with conn.execute(query, (cutoff_date,)) as cursor:
                session_count = (await cursor.fetchone())[0]
            
            # Old messages
            query = "SELECT COUNT(*) FROM messages WHERE timestamp < ?"
            async with conn.execute(query, (cutoff_date,)) as cursor:
                message_count = (await cursor.fetchone())[0]
            
            # Old checkpoints
            query = "SELECT COUNT(*) FROM checkpoints WHERE created_at < ?"
            async with conn.execute(query, (cutoff_date,)) as cursor:
                checkpoint_count = (await cursor.fetchone())[0]
        
        # Show what would be deleted
        cleanup_panel = f"""
[bold yellow]🧹 Cleanup Analysis[/bold yellow]

[cyan]Cutoff date:[/cyan] {cutoff_date[:10]} ({days} days ago)

[yellow]Data to be cleaned:[/yellow]
• Sessions: {session_count}
• Messages: {message_count}
• Checkpoints: {checkpoint_count}

[red]Warning:[/red] This action cannot be undone!
"""
        console.print(Panel(cleanup_panel, border_style="yellow"))
        
        if dry_run:
            console.print("[dim]This is a dry run. Use --no-dry-run to actually delete.[/dim]")
        else:
            if Confirm.ask("Proceed with cleanup?"):
                async with db.transaction() as conn:
                    # Delete old data
                    await conn.execute("DELETE FROM sessions WHERE created_at < ?", (cutoff_date,))
                    await conn.execute("DELETE FROM messages WHERE timestamp < ?", (cutoff_date,))
                    await conn.execute("DELETE FROM checkpoints WHERE created_at < ?", (cutoff_date,))
                
                console.print("[green]✓ Cleanup completed[/green]")
        
        await db.close()
    
    asyncio.run(cleanup_old_data())


if __name__ == "__main__":
    app()