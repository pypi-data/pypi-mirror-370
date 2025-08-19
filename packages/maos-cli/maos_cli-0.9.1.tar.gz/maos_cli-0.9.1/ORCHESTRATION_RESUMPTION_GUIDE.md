# Complete Guide: Session Saving & Resumption in MAOS

## 1. How Often Are We Saving?

### Current Save Points:

| When | What Gets Saved | Where | Automatic? |
|------|----------------|-------|------------|
| **Start orchestration** | Initial orchestration, agents, tasks | orchestrations, agents, tasks tables | ✅ Automatic |
| **After each agent completes** | Session updates, task progress | sessions, tasks tables | ✅ Automatic |
| **End of orchestration** | Final results, costs, summary | orchestrations table | ✅ Automatic |
| **Checkpoint created** | Full state snapshot | checkpoints table | ✅ Automatic |
| **Every message** | All inter-agent communications | messages table | ✅ Automatic |

### Problem: Mid-Execution Crashes

If crash happens DURING agent execution (which can take 5-30 minutes), we lose:
- Current agent progress
- Partial results
- Recent discoveries

### Solution: Progressive Saving

```python
# Enhanced orchestrator with progressive saves
class OrchestratorV7:
    async def orchestrate(self, request: str):
        # Save every 30 seconds during execution
        self.auto_save_interval = 30  # seconds
        
        # Save after every N messages
        self.message_batch_size = 10
        
        # Save on every discovery
        self.save_on_discovery = True
```

## 2. User Resumption Process

### Current Commands Available:

```bash
# 1. Create checkpoint (manual save)
maos recover checkpoint --name "before-big-refactor"

# 2. List checkpoints
maos recover list

# 3. Restore from checkpoint
maos recover restore <checkpoint-id>
```

### What's Missing: Orchestration Resume

Currently NO direct command to resume orchestrations! Here's what we need:

```bash
# NEW COMMANDS NEEDED:

# List active/paused orchestrations
maos orchestration list

# Resume specific orchestration
maos orchestration resume <orchestration-id>

# Show orchestration status
maos orchestration status <orchestration-id>
```

## 3. Implementing Orchestration Resume Command

```python
# src/maos/cli/commands/orchestration.py (NEW FILE)

from typer import Typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

orchestration_app = Typer(help="🎭 Orchestration management")
console = Console()

@orchestration_app.command(name="list")
async def list_orchestrations(
    status: Optional[str] = typer.Option(None, "--status", "-s", 
                                         help="Filter by status (running, paused, completed)"),
    limit: int = typer.Option(10, "--limit", "-l", help="Max orchestrations to show")
):
    """📋 List all orchestrations with their status"""
    
    orchestrator = init_orchestrator()
    
    # Query database for orchestrations
    query = """
        SELECT o.id, o.request, o.status, o.created_at,
               COUNT(DISTINCT a.id) as agent_count,
               COUNT(DISTINCT m.id) as message_count,
               o.total_cost, o.total_duration_ms
        FROM orchestrations o
        LEFT JOIN agents a ON json_extract(o.agents, '$') LIKE '%' || a.id || '%'
        LEFT JOIN messages m ON m.from_agent IN (SELECT value FROM json_each(o.agents))
        WHERE 1=1
    """
    
    if status:
        query += f" AND o.status = '{status}'"
    
    query += " GROUP BY o.id ORDER BY o.created_at DESC LIMIT ?"
    
    orchestrations = await orchestrator.persistence.execute_query(query, [limit])
    
    # Display in table
    table = Table(title="🎭 Orchestrations", show_header=True)
    table.add_column("ID", style="cyan", width=12)
    table.add_column("Request", style="white", width=40)
    table.add_column("Status", style="yellow", width=10)
    table.add_column("Agents", style="green", width=8)
    table.add_column("Messages", style="blue", width=10)
    table.add_column("Cost", style="red", width=10)
    table.add_column("Created", style="dim", width=20)
    
    for orch in orchestrations:
        status_emoji = {
            "running": "🔄",
            "paused": "⏸️",
            "completed": "✅",
            "failed": "❌"
        }.get(orch['status'], "❓")
        
        table.add_row(
            orch['id'][:8] + "...",
            orch['request'][:37] + "..." if len(orch['request']) > 40 else orch['request'],
            f"{status_emoji} {orch['status']}",
            str(orch['agent_count']),
            str(orch['message_count']),
            f"${orch['total_cost']:.4f}" if orch['total_cost'] else "$0",
            format_timestamp(orch['created_at'])
        )
    
    console.print(table)
    
    # Show resume hint for paused orchestrations
    paused = [o for o in orchestrations if o['status'] in ['running', 'paused']]
    if paused:
        console.print(f"\n💡 Resume with: [cyan]maos orchestration resume <id>[/cyan]")


@orchestration_app.command(name="resume")
async def resume_orchestration(
    orchestration_id: str = typer.Argument(..., help="Orchestration ID or prefix"),
    new_task: Optional[str] = typer.Option(None, "--task", "-t", 
                                           help="New task for agents (optional)"),
    show_progress: bool = typer.Option(True, "--progress/--no-progress",
                                       help="Show progress details")
):
    """🔄 Resume a paused or interrupted orchestration"""
    
    orchestrator = init_orchestrator()
    
    # Find orchestration (support partial ID)
    orch = await orchestrator.persistence.get_orchestration(orchestration_id)
    if not orch:
        # Try partial match
        query = "SELECT * FROM orchestrations WHERE id LIKE ? LIMIT 1"
        results = await orchestrator.persistence.execute_query(
            query, [f"{orchestration_id}%"]
        )
        if results:
            orch = results[0]
    
    if not orch:
        console.print(f"[red]❌ Orchestration not found: {orchestration_id}[/red]")
        return
    
    # Show what we're resuming
    console.print(Panel(
        f"[bold]Orchestration:[/bold] {orch['id'][:12]}...\n"
        f"[bold]Original Request:[/bold] {orch['request']}\n"
        f"[bold]Status:[/bold] {orch['status']}\n"
        f"[bold]Created:[/bold] {format_timestamp(orch['created_at'])}\n"
        f"[bold]Agents:[/bold] {len(json.loads(orch['agents']))}",
        title="📂 Resuming Orchestration",
        border_style="blue"
    ))
    
    if show_progress:
        # Show progress details
        await show_orchestration_progress(orch['id'])
    
    # Restore message bus with all agents
    console.print("\n[bold blue]Restoring communication channels...[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Step 1: Restore message bus
        restore_task = progress.add_task("Restoring message bus...", total=4)
        
        message_bus = PersistentMessageBus(orchestrator.persistence, SessionManager())
        await message_bus.start()  # This restores from DB
        progress.update(restore_task, advance=1, description="Message bus restored")
        
        # Step 2: Restore agents
        agents = json.loads(orch['agents'])
        progress.update(restore_task, description=f"Restoring {len(agents)} agents...")
        
        for agent_id in agents:
            agent = await orchestrator.persistence.get_agent(agent_id)
            if agent:
                await message_bus.register_agent(
                    agent_id=agent_id,
                    agent_info={
                        'name': agent['name'],
                        'type': agent['type'],
                        'session_id': agent.get('session_id'),
                        'restored': True
                    },
                    create_in_db=False
                )
        progress.update(restore_task, advance=1, description="Agents restored")
        
        # Step 3: Load communication history
        progress.update(restore_task, description="Loading communication history...")
        
        history = await message_bus.get_communication_history(
            since=datetime.fromisoformat(orch['created_at'])
        )
        progress.update(restore_task, advance=1, 
                       description=f"Loaded {len(history)} messages")
        
        # Step 4: Resume execution
        progress.update(restore_task, description="Resuming execution...")
        
        if new_task:
            # Resume with new task
            result = await orchestrator.resume_orchestration(orch['id'], new_task)
        else:
            # Continue from where it left off
            result = await orchestrator.continue_orchestration(orch['id'])
        
        progress.update(restore_task, advance=1, description="Orchestration resumed!")
    
    # Show results
    if result.success:
        console.print(f"\n[green]✅ Orchestration resumed successfully![/green]")
        console.print(f"[dim]Agents active: {len(result.agents_created)}[/dim]")
        console.print(f"[dim]Total cost so far: ${result.total_cost:.4f}[/dim]")
    else:
        console.print(f"\n[red]❌ Failed to resume orchestration[/red]")


@orchestration_app.command(name="status")
async def orchestration_status(
    orchestration_id: str = typer.Argument(..., help="Orchestration ID or prefix"),
    show_messages: bool = typer.Option(False, "--messages", "-m",
                                       help="Show recent messages"),
    show_agents: bool = typer.Option(False, "--agents", "-a",
                                     help="Show agent details"),
    watch: bool = typer.Option(False, "--watch", "-w",
                              help="Watch status in real-time")
):
    """📊 Show detailed orchestration status and progress"""
    
    orchestrator = init_orchestrator()
    
    async def show_status():
        # Get orchestration
        orch = await get_orchestration_by_id(orchestration_id)
        if not orch:
            console.print(f"[red]❌ Orchestration not found[/red]")
            return
        
        console.clear()
        
        # Header
        console.print(Panel(
            f"[bold]Orchestration Status[/bold]",
            title=f"🎭 {orch['id'][:12]}...",
            border_style="blue"
        ))
        
        # Progress visualization
        agents = json.loads(orch['agents'])
        completed_tasks = await count_completed_tasks(agents)
        total_tasks = len(agents)
        
        progress_bar = create_progress_bar(completed_tasks, total_tasks)
        console.print(f"\nProgress: {progress_bar} {completed_tasks}/{total_tasks}")
        
        # Agent status grid
        if show_agents:
            agent_table = Table(title="Agent Status", show_header=True)
            agent_table.add_column("Agent", style="cyan")
            agent_table.add_column("Type", style="yellow")
            agent_table.add_column("Status", style="green")
            agent_table.add_column("Session", style="blue")
            agent_table.add_column("Messages", style="white")
            
            for agent_id in agents:
                agent = await orchestrator.persistence.get_agent(agent_id)
                msg_count = await count_agent_messages(agent_id)
                
                status_icon = {
                    'active': '🟢',
                    'paused': '🟡',
                    'completed': '✅',
                    'failed': '❌'
                }.get(agent.get('status', 'unknown'), '❓')
                
                agent_table.add_row(
                    agent_id[:8] + "...",
                    agent.get('type', 'unknown'),
                    f"{status_icon} {agent.get('status', 'unknown')}",
                    agent.get('session_id', 'N/A')[:8] + "..." if agent.get('session_id') else "N/A",
                    str(msg_count)
                )
            
            console.print("\n", agent_table)
        
        # Recent messages
        if show_messages:
            messages = await get_recent_messages(orch['id'], limit=5)
            
            console.print("\n[bold]Recent Communications:[/bold]")
            for msg in messages:
                icon = {
                    'discovery': '💡',
                    'request': '📨',
                    'broadcast': '📢',
                    'error': '❌'
                }.get(msg['type'], 'ℹ️')
                
                console.print(
                    f"{icon} [{msg['from_agent'][:8]}] → "
                    f"[{msg['to_agent'][:8] if msg['to_agent'] else 'ALL'}]: "
                    f"{msg['content'][:80]}..."
                )
        
        # Summary stats
        console.print("\n[bold]Summary:[/bold]")
        console.print(f"  Status: {orch['status']}")
        console.print(f"  Duration: {format_duration(orch.get('total_duration_ms', 0))}")
        console.print(f"  Cost: ${orch.get('total_cost', 0):.4f}")
        console.print(f"  Messages: {await count_total_messages(orch['id'])}")
    
    if watch:
        # Real-time monitoring
        try:
            while True:
                await show_status()
                await asyncio.sleep(5)  # Refresh every 5 seconds
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopped watching[/yellow]")
    else:
        await show_status()


async def show_orchestration_progress(orchestration_id: str):
    """Show detailed progress of an orchestration"""
    
    # Get all tasks for this orchestration
    query = """
        SELECT t.id, t.description, t.status, t.progress,
               a.name as agent_name, a.type as agent_type
        FROM tasks t
        LEFT JOIN agents a ON t.id LIKE 'task-' || a.id || '%'
        WHERE a.id IN (
            SELECT value FROM json_each(
                (SELECT agents FROM orchestrations WHERE id = ?)
            )
        )
        ORDER BY t.created_at
    """
    
    tasks = await persistence.execute_query(query, [orchestration_id])
    
    # Group by status
    by_status = {}
    for task in tasks:
        status = task['status'] or 'pending'
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(task)
    
    # Show progress
    console.print("\n[bold]Task Progress:[/bold]")
    
    for status, status_tasks in by_status.items():
        emoji = {
            'completed': '✅',
            'running': '🔄',
            'failed': '❌',
            'pending': '⏳'
        }.get(status, '❓')
        
        console.print(f"\n{emoji} {status.title()}: {len(status_tasks)}")
        
        if len(status_tasks) <= 3:
            for task in status_tasks:
                console.print(f"  • {task['agent_name']}: {task['description'][:50]}...")


def create_progress_bar(current: int, total: int, width: int = 30) -> str:
    """Create a visual progress bar"""
    if total == 0:
        return "━" * width
    
    filled = int((current / total) * width)
    bar = "█" * filled + "░" * (width - filled)
    percentage = int((current / total) * 100)
    
    return f"{bar} {percentage}%"
```

## 4. Auto-Save Implementation

```python
# Enhanced orchestrator with auto-save
class OrchestratorV7:
    
    async def orchestrate(self, request: str, auto_approve: bool = False):
        # Enable auto-save
        self.auto_save_task = asyncio.create_task(self._auto_save_loop())
        
        try:
            # ... normal orchestration ...
            pass
        finally:
            # Stop auto-save
            if self.auto_save_task:
                self.auto_save_task.cancel()
    
    async def _auto_save_loop(self):
        """Background task that saves state periodically"""
        while True:
            try:
                await asyncio.sleep(30)  # Save every 30 seconds
                
                # Save current state
                await self._save_orchestration_state()
                
                # Save checkpoint if significant progress
                if self._significant_progress_made():
                    checkpoint_name = f"auto-{self.orchestration_id[:8]}-{datetime.now().strftime('%H%M%S')}"
                    await self.persistence.save_checkpoint(
                        checkpoint_id=str(uuid.uuid4()),
                        name=checkpoint_name,
                        checkpoint_data=self._get_current_state()
                    )
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-save failed: {e}")
    
    async def _save_orchestration_state(self):
        """Save current orchestration state to database"""
        # Update orchestration record
        await self.persistence.update_orchestration(
            orchestration_id=self.orchestration_id,
            last_updated=datetime.now().isoformat(),
            active_agents=len(self.message_bus.get_active_agents()),
            messages_count=await self._count_messages(),
            current_phase=self.current_phase
        )
        
        # Save pending discoveries
        for discovery in self.pending_discoveries:
            await self.persistence.save_message(
                from_agent=discovery['from'],
                to_agent=None,
                message=discovery['content'],
                message_type='discovery'
            )
```

## 5. User Experience for Resumption

### Scenario 1: Graceful Stop
```bash
$ maos orchestrate "Refactor entire codebase"
🎭 Orchestration started: orch-abc123...
[Working for 20 minutes...]
^C
⏸️ Orchestration paused. Resume with: maos orchestration resume abc123
💾 State saved. 3 agents paused, 47 messages preserved.
```

### Scenario 2: System Crash
```bash
$ maos orchestration list
🎭 Orchestrations
┌────────────┬──────────────────────┬───────────┬────────┬──────────┐
│ ID         │ Request              │ Status    │ Agents │ Messages │
├────────────┼──────────────────────┼───────────┼────────┼──────────┤
│ abc123...  │ Refactor entire...  │ ⏸️ paused │ 3      │ 47       │
└────────────┴──────────────────────┴───────────┴────────┴──────────┘

$ maos orchestration resume abc123
📂 Resuming Orchestration
Orchestration: abc123def456...
Original Request: Refactor entire codebase
Status: paused
Created: 2 days ago
Agents: 3

Restoring communication channels...
✓ Message bus restored
✓ 3 agents restored
✓ Loaded 47 messages
✓ Orchestration resumed!

[analyst-001]: Resuming from src/utils/...
[developer-001]: Continuing refactoring of authentication module...
[tester-001]: Running tests on completed refactors...
```

### Scenario 3: Status Check
```bash
$ maos orchestration status abc123 --agents --messages

🎭 Orchestration Status: abc123def456...

Progress: ████████████░░░░░░░░░░░░░░░░░ 40% (2/5 tasks)

Agent Status:
┌────────────┬──────────┬─────────┬──────────┬──────────┐
│ Agent      │ Type     │ Status  │ Session  │ Messages │
├────────────┼──────────┼─────────┼──────────┼──────────┤
│ analyst... │ analyst  │ 🟢 active│ sess123..│ 15       │
│ develop... │ developer│ 🟢 active│ sess456..│ 22       │
│ tester...  │ tester   │ 🟡 paused│ sess789..│ 10       │
└────────────┴──────────┴─────────┴──────────┴──────────┘

Recent Communications:
💡 [analyst...] → [ALL]: Found 15 more files needing refactor
📨 [develop...] → [analyst...]: Need list of priority files
📢 [tester...] → [ALL]: Tests passing for auth module

Summary:
  Status: running
  Duration: 2h 34m
  Cost: $0.4523
  Messages: 47
```

## Summary

### 1. Save Frequency
- **Automatic saves**: At start, after each agent, at end
- **Progressive saves**: Every 30 seconds during execution
- **Message saves**: Every message immediately
- **Auto-checkpoints**: On significant progress

### 2. User Actions
- **Nothing required** for basic saves (all automatic)
- **Can manually checkpoint**: `maos recover checkpoint`
- **Can resume easily**: `maos orchestration resume <id>`
- **Can monitor progress**: `maos orchestration status <id> --watch`

### 3. What Gets Displayed on Resume
- Original request and context
- Number of agents being restored
- Communication history summary
- Current progress percentage
- What each agent is resuming
- Time since last activity

The system is designed to be **completely transparent** about what's being resumed and where it left off!