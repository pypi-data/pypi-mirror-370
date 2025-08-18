"""
User-friendly execution explainer for MAOS.

Provides clear, non-technical explanations of what's happening during orchestration.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.tree import Tree
from rich.live import Live
from rich.layout import Layout
from rich.columns import Columns
import asyncio

class ExecutionExplainer:
    """
    Explains MAOS operations in plain English for non-technical users.
    """
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.current_phase = "idle"
        self.start_time = None
        
    def explain_request_processing(self, request: str):
        """Explain what happens when a user makes a request."""
        self.start_time = datetime.now()
        
        explanation = f"""
[bold cyan]🎯 Understanding Your Request[/bold cyan]

I received: "{request}"

Here's what I'm doing:

1️⃣  [yellow]Analyzing your request[/yellow]
   • Understanding what you want to achieve
   • Identifying the type of work needed
   • Determining complexity

2️⃣  [yellow]Planning the approach[/yellow]
   • Breaking down into smaller tasks
   • Deciding what can be done simultaneously
   • Estimating time and resources needed

3️⃣  [yellow]Preparing the team[/yellow]
   • Determining how many AI agents are needed
   • Assigning specific roles to each agent
   • Setting up coordination between agents
"""
        self.console.print(Panel(explanation, title="📋 Request Processing", border_style="cyan"))
    
    def explain_batches(self, batches: List[List[Any]]):
        """Explain what batches are and why we use them."""
        
        explanation = f"""
[bold green]📦 Understanding Batches[/bold green]

Think of batches like waves of workers:

• [cyan]Batch[/cyan] = A group of tasks that can happen at the same time
• Tasks in the same batch work in parallel (simultaneously)
• Next batch starts only after previous batch completes

[yellow]Why use batches?[/yellow]
✓ Faster completion - multiple tasks at once
✓ Efficient resource use - no agents sitting idle
✓ Logical organization - dependent tasks wait their turn

You have [bold]{len(batches)}[/bold] batch(es) to execute:
"""
        
        self.console.print(Panel(explanation, title="🔄 Batch Execution", border_style="green"))
        
        # Show batch details
        for i, batch in enumerate(batches, 1):
            batch_info = f"""
[bold]Batch {i}[/bold] - {len(batch)} task(s) running in parallel:
"""
            for task in batch:
                task_desc = getattr(task, 'description', str(task))[:60]
                batch_info += f"  • {task_desc}\n"
            
            self.console.print(batch_info)
    
    def explain_agent_allocation(self, new_agents: int, reused_agents: int, 
                               agent_details: List[Dict]):
        """Explain how agents are allocated."""
        
        explanation = f"""
[bold magenta]🤖 AI Agent Team Assembly[/bold magenta]

[yellow]What are agents?[/yellow]
Agents are individual AI assistants (Claude instances) that work on specific tasks.
Think of them as specialized workers, each with their own expertise.

[yellow]Your team composition:[/yellow]
• [green]New agents:[/green] {new_agents} fresh assistants starting from scratch
• [cyan]Reused agents:[/cyan] {reused_agents} continuing from previous work
• [bold]Total team size:[/bold] {new_agents + reused_agents} agents

[yellow]Why reuse agents?[/yellow]
✓ They remember previous context
✓ Faster startup (no re-learning)
✓ Cost-effective
✓ Maintains consistency
"""
        
        self.console.print(Panel(explanation, title="👥 Agent Team", border_style="magenta"))
        
        # Show agent details
        if agent_details:
            table = Table(title="Agent Assignments")
            table.add_column("Agent Name", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Task", style="yellow")
            table.add_column("Status", style="magenta")
            
            for agent in agent_details:
                table.add_row(
                    agent.get('name', 'Unknown'),
                    agent.get('type', 'general'),
                    agent.get('task', 'Pending')[:40] + "...",
                    "🆕 New" if agent.get('is_new') else "♻️ Reused"
                )
            
            self.console.print(table)
    
    def explain_execution_start(self):
        """Explain what happens when execution starts."""
        
        explanation = """
[bold yellow]🚀 Starting Execution[/bold yellow]

Here's what's happening now:

1. [cyan]Spawning AI agents[/cyan]
   Each agent is starting up as a separate Claude process
   
2. [cyan]Assigning tasks[/cyan]
   Each agent receives their specific instructions
   
3. [cyan]Establishing communication[/cyan]
   Agents can now share discoveries and coordinate
   
4. [cyan]Beginning work[/cyan]
   All agents in Batch 1 start working simultaneously

[dim]💡 Tip: Agents work independently but can communicate when needed[/dim]
"""
        
        self.console.print(Panel(explanation, title="▶️ Execution Started", border_style="yellow"))
    
    def explain_agent_progress(self, agent_name: str, progress: float, 
                             current_action: str = None):
        """Explain what an agent is doing."""
        
        progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
        
        status = f"""
[bold]{agent_name}[/bold]
Progress: [{progress_bar}] {progress:.0f}%
"""
        
        if current_action:
            status += f"Currently: {current_action}\n"
        
        self.console.print(status, style="dim")
    
    def explain_inter_agent_communication(self, from_agent: str, to_agent: str, 
                                         message_type: str, content: str):
        """Explain when agents communicate."""
        
        icons = {
            "discovery": "💡",
            "request": "❓",
            "response": "💬",
            "coordination": "🤝",
            "dependency": "⚠️"
        }
        
        icon = icons.get(message_type, "📨")
        
        explanation = f"""
{icon} [bold]Agent Communication[/bold]
[cyan]{from_agent}[/cyan] → [green]{to_agent}[/green]
Type: {message_type}
Message: "{content[:100]}..."

[dim]Agents share information to work more effectively together[/dim]
"""
        
        self.console.print(Panel(explanation, border_style="blue"))
    
    def explain_checkpoint(self, checkpoint_name: str):
        """Explain what checkpoints are and when they're saved."""
        
        explanation = f"""
[bold green]💾 Checkpoint Saved: {checkpoint_name}[/bold green]

[yellow]What is a checkpoint?[/yellow]
A checkpoint is like a "save game" - it captures:
• Current progress of all agents
• Completed tasks
• Agent conversations and memory
• Current state of work

[yellow]Why save checkpoints?[/yellow]
✓ Resume work later if interrupted
✓ Review what was accomplished
✓ Rollback if something goes wrong
✓ Share progress with team members

[yellow]How to resume from this checkpoint:[/yellow]
```
maos restore "{checkpoint_name}"
```

[dim]Checkpoint saved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]
"""
        
        self.console.print(Panel(explanation, title="💾 Checkpoint", border_style="green"))
    
    def explain_session_persistence(self):
        """Explain how sessions are persisted."""
        
        explanation = """
[bold cyan]📚 Understanding Session Memory[/bold cyan]

[yellow]What gets saved?[/yellow]
• [green]Conversations:[/green] Everything each agent has said and learned
• [green]Decisions:[/green] Why certain approaches were chosen
• [green]Results:[/green] Output and discoveries from each task
• [green]Context:[/green] Understanding built up over time

[yellow]Where is it saved?[/yellow]
• Local SQLite database (maos.db in current directory)
• Each session has a unique ID for tracking
• Conversations are preserved even after agents stop

[yellow]When is it saved?[/yellow]
• ✓ Automatically after each agent response
• ✓ When you create a checkpoint
• ✓ Before agents shut down
• ✓ When tasks complete

[yellow]Memory building:[/yellow]
As agents work, they build up understanding:
1. Short-term: Current task context
2. Long-term: Patterns and insights across tasks
3. Shared: Knowledge exchanged between agents
"""
        
        self.console.print(Panel(explanation, title="🧠 Session Memory", border_style="cyan"))
    
    def explain_resume_session(self, session_id: str, last_activity: str):
        """Explain how to resume a previous session."""
        
        explanation = f"""
[bold green]↺ Resuming Previous Session[/bold green]

[yellow]Session ID:[/yellow] {session_id}
[yellow]Last activity:[/yellow] {last_activity}

[yellow]What happens when you resume?[/yellow]
1. Agents wake up with their full memory intact
2. They remember all previous conversations
3. Work continues from where it left off
4. No need to re-explain context

[yellow]Commands to manage sessions:[/yellow]
• `maos sessions`        - List all saved sessions
• `maos resume <id>`     - Continue specific session  
• `maos continue`        - Resume most recent session
• `maos checkpoint list` - Show saved checkpoints

[dim]💡 Tip: Sessions expire after 30 days of inactivity[/dim]
"""
        
        self.console.print(Panel(explanation, title="📂 Session Resume", border_style="green"))
    
    def explain_completion(self, duration: float, tasks_completed: int, 
                         agents_used: int, total_cost: float = None):
        """Explain what happened when execution completes."""
        
        duration_min = duration / 60
        
        explanation = f"""
[bold green]✅ Execution Complete![/bold green]

[yellow]Summary:[/yellow]
• ⏱️  Duration: {duration_min:.1f} minutes
• ✓  Tasks completed: {tasks_completed}
• 🤖 Agents used: {agents_used}
"""
        
        if total_cost:
            explanation += f"• 💰 Estimated cost: ${total_cost:.4f}\n"
        
        explanation += """

[yellow]What was saved?[/yellow]
• All agent conversations
• Task results and outputs
• Decision reasoning
• Inter-agent communications

[yellow]What can you do now?[/yellow]
• Review the results
• Save a checkpoint for future reference
• Continue with follow-up tasks
• Export conversations for documentation

[dim]All data has been saved to your local database[/dim]
"""
        
        self.console.print(Panel(explanation, title="🎉 Complete", border_style="green"))
    
    def explain_error(self, error_type: str, error_message: str, 
                     recovery_options: List[str] = None):
        """Explain errors in user-friendly terms."""
        
        friendly_errors = {
            "timeout": "The agent took too long to complete the task",
            "stuck": "The agent stopped responding",
            "connection": "Lost connection to the agent",
            "resource": "Not enough resources available",
            "permission": "Permission denied for requested action"
        }
        
        friendly_msg = friendly_errors.get(error_type, error_message)
        
        explanation = f"""
[bold red]⚠️ Issue Encountered[/bold red]

[yellow]What happened:[/yellow]
{friendly_msg}

[yellow]Technical details:[/yellow]
{error_message}
"""
        
        if recovery_options:
            explanation += "\n[yellow]What you can do:[/yellow]\n"
            for option in recovery_options:
                explanation += f"• {option}\n"
        else:
            explanation += """
[yellow]What you can do:[/yellow]
• Try running the task again
• Save a checkpoint and resume later
• Reduce the number of parallel agents
• Check the logs for more details
"""
        
        self.console.print(Panel(explanation, title="⚠️ Error", border_style="red"))
    
    def show_live_monitoring(self, agents: List[Dict]):
        """Show live monitoring dashboard."""
        
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Header
        header = "[bold cyan]🎯 MAOS Live Monitoring Dashboard[/bold cyan]"
        layout["header"].update(Panel(header))
        
        # Body - Agent status
        agent_status = Table(title="Agent Status")
        agent_status.add_column("Agent", style="cyan")
        agent_status.add_column("Task", style="yellow")
        agent_status.add_column("Progress", style="green")
        agent_status.add_column("Status", style="magenta")
        
        for agent in agents:
            progress_bar = "█" * int(agent.get('progress', 0) / 10)
            progress_bar += "░" * (10 - len(progress_bar))
            
            agent_status.add_row(
                agent['name'],
                agent['task'][:30] + "...",
                f"[{progress_bar}] {agent.get('progress', 0):.0f}%",
                agent.get('status', 'active')
            )
        
        layout["body"].update(agent_status)
        
        # Footer
        footer = f"[dim]Started: {self.start_time.strftime('%H:%M:%S')} | Press Ctrl+C to pause[/dim]"
        layout["footer"].update(Panel(footer))
        
        return layout
    
    async def explain_with_live_updates(self, get_status_func):
        """Show live updates during execution."""
        
        with Live(self.show_live_monitoring([]), refresh_per_second=1) as live:
            while True:
                status = await get_status_func()
                if status.get('state') != 'executing':
                    break
                    
                agents = status.get('agents', [])
                live.update(self.show_live_monitoring(agents))
                await asyncio.sleep(1)