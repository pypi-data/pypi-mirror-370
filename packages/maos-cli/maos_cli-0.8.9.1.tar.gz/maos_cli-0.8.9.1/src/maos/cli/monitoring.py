"""
MAOS CLI Real-time Monitoring

Advanced monitoring capabilities with live updates, metrics tracking,
and interactive dashboards for system and component monitoring.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from uuid import UUID
from collections import defaultdict, deque

from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, SpinnerColumn
from rich.tree import Tree
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule
from rich import box

from ..core.orchestrator import Orchestrator
from ..models.task import Task, TaskStatus
from ..models.agent import Agent, AgentStatus
from .formatters import format_duration, format_size, format_percentage, format_status, create_progress_bar


class BaseMonitor:
    """Base class for monitoring components."""
    
    def __init__(self, orchestrator: Orchestrator, refresh_rate: float = 1.0):
        self.orchestrator = orchestrator
        self.refresh_rate = refresh_rate
        self.console = Console()
        self.running = False
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.start_time = datetime.utcnow()
    
    async def start_live_monitoring(self, detailed: bool = False):
        """Start live monitoring with rich interface."""
        self.running = True
        self.start_time = datetime.utcnow()
        
        with Live(console=self.console, refresh_per_second=1/self.refresh_rate) as live:
            try:
                while self.running:
                    display = await self.create_display(detailed)
                    live.update(display)
                    await asyncio.sleep(self.refresh_rate)
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Monitoring stopped by user[/yellow]")
            except Exception as e:
                self.console.print(f"\n[red]Monitoring error: {e}[/red]")
            finally:
                self.running = False
    
    async def create_display(self, detailed: bool = False) -> Layout:
        """Create the monitoring display layout."""
        raise NotImplementedError()
    
    def stop(self):
        """Stop monitoring."""
        self.running = False
    
    def _record_metric(self, key: str, value: Any):
        """Record a metric value with timestamp."""
        self.metrics_history[key].append((datetime.utcnow(), value))
    
    def _get_metric_trend(self, key: str, duration_minutes: int = 5) -> str:
        """Get trend for a metric over specified duration."""
        if key not in self.metrics_history or len(self.metrics_history[key]) < 2:
            return "[dim]N/A[/dim]"
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=duration_minutes)
        recent_values = [
            value for timestamp, value in self.metrics_history[key]
            if timestamp >= cutoff_time and isinstance(value, (int, float))
        ]
        
        if len(recent_values) < 2:
            return "[dim]N/A[/dim]"
        
        first_value = recent_values[0]
        last_value = recent_values[-1]
        
        if first_value == 0:
            return "[green]↑[/green]" if last_value > 0 else "[dim]=>[/dim]"
        
        change_percent = ((last_value - first_value) / first_value) * 100
        
        if change_percent > 5:
            return f"[green]↑ {change_percent:+.1f}%[/green]"
        elif change_percent < -5:
            return f"[red]↓ {change_percent:+.1f}%[/red]"
        else:
            return f"[dim]=> {change_percent:+.1f}%[/dim]"


class SystemMonitor(BaseMonitor):
    """System-wide monitoring for overall orchestrator health."""
    
    async def create_display(self, detailed: bool = False) -> Layout:
        """Create system monitoring display."""
        layout = Layout(name="system_monitor")
        
        # Get system status and metrics
        system_status = await self.orchestrator.get_system_status()
        system_metrics = await self.orchestrator.get_system_metrics()
        component_health = await self.orchestrator.get_component_health()
        
        # Record metrics
        self._record_metric("active_executions", system_status.get("active_executions", 0))
        self._record_metric("total_tasks", system_metrics.get("orchestrator", {}).get("tasks_submitted", 0))
        
        if detailed:
            # Detailed layout with multiple panels
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="main", ratio=1),
                Layout(name="footer", size=5)
            )
            
            layout["main"].split_row(
                Layout(name="left"),
                Layout(name="right")
            )
            
            layout["left"].split_column(
                Layout(name="status"),
                Layout(name="metrics")
            )
            
            layout["right"].split_column(
                Layout(name="components"),
                Layout(name="activity")
            )
            
            # Populate panels
            layout["header"].update(self._create_header_panel())
            layout["status"].update(self._create_status_panel(system_status))
            layout["metrics"].update(self._create_metrics_panel(system_metrics))
            layout["components"].update(self._create_components_panel(component_health))
            layout["activity"].update(self._create_activity_panel())
            layout["footer"].update(self._create_footer_panel())
            
        else:
            # Simple layout
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="overview", ratio=1),
                Layout(name="status", size=8)
            )
            
            layout["header"].update(self._create_header_panel())
            layout["overview"].update(self._create_overview_panel(system_status, system_metrics))
            layout["status"].update(self._create_simple_status_panel(component_health))
        
        return layout
    
    def _create_header_panel(self) -> Panel:
        """Create header panel with system info."""
        uptime = datetime.utcnow() - self.start_time
        header_text = f"""
[bold blue]MAOS System Monitor[/bold blue] | Uptime: {format_duration(uptime.total_seconds())} | 🔄 Live Updates
        """.strip()
        
        return Panel(
            Align.center(Text(header_text)),
            style="bold",
            box=box.DOUBLE
        )
    
    def _create_status_panel(self, status: Dict[str, Any]) -> Panel:
        """Create system status panel."""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="white")
        table.add_column("Trend", style="dim", width=10)
        
        running_status = "[green]✓ Running[/green]" if status.get("running") else "[red]❌ Stopped[/red]"
        table.add_row("Status", running_status, "")
        
        active_executions = status.get("active_executions", 0)
        table.add_row(
            "Active Executions", 
            str(active_executions),
            self._get_metric_trend("active_executions")
        )
        
        table.add_row("Execution Plans", str(status.get("execution_plans", 0)), "")
        
        if "startup_time" in status and status["startup_time"]:
            startup_time = datetime.fromisoformat(status["startup_time"])
            uptime = datetime.utcnow() - startup_time
            table.add_row("Uptime", format_duration(uptime.total_seconds()), "")
        
        return Panel(table, title="🔋 System Status", border_style="green")
    
    def _create_metrics_panel(self, metrics: Dict[str, Any]) -> Panel:
        """Create metrics panel."""
        table = Table(show_header=True, header_style="bold blue", box=box.SIMPLE)
        table.add_column("Component", style="cyan")
        table.add_column("Tasks", style="green")
        table.add_column("Success Rate", style="yellow")
        table.add_column("Trend", style="dim")
        
        for component, component_metrics in metrics.items():
            if component == "timestamp" or not isinstance(component_metrics, dict):
                continue
            
            tasks_completed = component_metrics.get("tasks_completed", 0)
            tasks_failed = component_metrics.get("tasks_failed", 0)
            total_tasks = tasks_completed + tasks_failed
            
            if total_tasks > 0:
                success_rate = (tasks_completed / total_tasks) * 100
                success_rate_str = f"{success_rate:.1f}%"
            else:
                success_rate_str = "N/A"
            
            # Record metric for trending
            self._record_metric(f"{component}_tasks", total_tasks)
            
            table.add_row(
                component.title(),
                str(total_tasks),
                success_rate_str,
                self._get_metric_trend(f"{component}_tasks")
            )
        
        return Panel(table, title="📊 Component Metrics", border_style="blue")
    
    def _create_components_panel(self, health: Dict[str, str]) -> Panel:
        """Create components health panel."""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Component", style="cyan", width=20)
        table.add_column("Status", style="white")
        
        for component, status in health.items():
            formatted_status = format_status(status)
            table.add_row(component.replace('_', ' ').title(), formatted_status)
        
        return Panel(table, title="🟢 Component Health", border_style="cyan")
    
    def _create_activity_panel(self) -> Panel:
        """Create recent activity panel."""
        # This would show recent log entries or events
        # For now, show a simple activity indicator
        
        activity_text = """
[dim]• System monitoring active[/dim]
[dim]• Components healthy[/dim]
[dim]• Processing requests...[/dim]
        """.strip()
        
        return Panel(
            Text(activity_text),
            title="📜 Recent Activity",
            border_style="dim"
        )
    
    def _create_footer_panel(self) -> Panel:
        """Create footer with controls and info."""
        footer_text = """
[dim]Press Ctrl+C to exit | Refresh rate: {:.1f}s | Last update: {}[/dim]
        """.format(
            self.refresh_rate,
            datetime.utcnow().strftime("%H:%M:%S")
        )
        
        return Panel(
            Align.center(Text(footer_text)),
            style="dim"
        )
    
    def _create_overview_panel(self, status: Dict[str, Any], metrics: Dict[str, Any]) -> Panel:
        """Create simple overview panel."""
        # Calculate summary statistics
        total_tasks = sum(
            m.get("tasks_submitted", 0) if isinstance(m, dict) else 0
            for m in metrics.values()
        )
        
        completed_tasks = sum(
            m.get("tasks_completed", 0) if isinstance(m, dict) else 0
            for m in metrics.values()
        )
        
        failed_tasks = sum(
            m.get("tasks_failed", 0) if isinstance(m, dict) else 0
            for m in metrics.values()
        )
        
        success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        overview_text = f"""
[bold cyan]System Status:[/bold cyan] {'[green]Running[/green]' if status.get('running') else '[red]Stopped[/red]'}

[bold cyan]Task Statistics:[/bold cyan]
  • Total Tasks: [white]{total_tasks:,}[/white]
  • Completed: [green]{completed_tasks:,}[/green]
  • Failed: [red]{failed_tasks:,}[/red]
  • Success Rate: {format_percentage(completed_tasks, total_tasks)}

[bold cyan]Active Operations:[/bold cyan]
  • Executions: [yellow]{status.get('active_executions', 0)}[/yellow]
  • Plans: [blue]{status.get('execution_plans', 0)}[/blue]
        """.strip()
        
        return Panel(
            Text(overview_text),
            title="📊 System Overview",
            border_style="blue"
        )
    
    def _create_simple_status_panel(self, health: Dict[str, str]) -> Panel:
        """Create simple status panel."""
        healthy_count = sum(1 for status in health.values() if status == "healthy")
        total_count = len(health)
        
        status_text = f"""
[bold cyan]Component Health:[/bold cyan] {healthy_count}/{total_count} healthy

        """
        
        for component, status in health.items():
            status_icon = "✓" if status == "healthy" else "❌"
            status_color = "green" if status == "healthy" else "red"
            component_name = component.replace('_', ' ').title()
            status_text += f"[{status_color}]{status_icon}[/{status_color}] {component_name}\n"
        
        return Panel(
            Text(status_text.strip()),
            title="🟢 Component Status",
            border_style="cyan"
        )


class TaskMonitor(BaseMonitor):
    """Task-specific monitoring for tracking task execution."""
    
    def __init__(self, orchestrator: Orchestrator, task_ids: List[UUID], refresh_rate: float = 1.0):
        super().__init__(orchestrator, refresh_rate)
        self.task_ids = task_ids
        self.task_history: Dict[UUID, List[Dict]] = {task_id: [] for task_id in task_ids}
    
    async def create_display(self, detailed: bool = False) -> Layout:
        """Create task monitoring display."""
        layout = Layout(name="task_monitor")
        
        # Get task information
        tasks_info = []
        for task_id in self.task_ids:
            task = await self.orchestrator.get_task(task_id)
            if task:
                tasks_info.append(task)
        
        if not tasks_info:
            return Panel("[red]No tasks found[/red]", title="Task Monitor")
        
        if len(tasks_info) == 1:
            # Single task detailed view
            layout.update(self._create_single_task_panel(tasks_info[0], detailed))
        else:
            # Multiple tasks view
            if detailed:
                layout.split_column(
                    Layout(name="header", size=3),
                    Layout(name="tasks", ratio=1)
                )
                
                layout["header"].update(self._create_tasks_header(len(tasks_info)))
                layout["tasks"].update(self._create_multiple_tasks_panel(tasks_info))
            else:
                layout.update(self._create_tasks_table(tasks_info))
        
        return layout
    
    def _create_single_task_panel(self, task: Task, detailed: bool) -> Panel:
        """Create detailed panel for single task monitoring."""
        # Record task status for history
        task_info = {
            "status": task.status.value,
            "retry_count": task.retry_count,
            "timestamp": datetime.utcnow()
        }
        self.task_history[task.id].append(task_info)
        
        # Keep only last 20 entries
        self.task_history[task.id] = self.task_history[task.id][-20:]
        
        if detailed:
            content = self._create_detailed_task_content(task)
        else:
            content = self._create_simple_task_content(task)
        
        return Panel(
            content,
            title=f"📋 Task: {task.name}",
            border_style="blue"
        )
    
    def _create_detailed_task_content(self, task: Task) -> Layout:
        """Create detailed content for single task."""
        layout = Layout()
        layout.split_row(
            Layout(name="info"),
            Layout(name="progress")
        )
        
        # Task information
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Property", style="cyan", width=15)
        info_table.add_column("Value", style="white")
        
        info_table.add_row("ID", str(task.id)[:8] + "...")
        info_table.add_row("Status", format_status(task.status.value))
        info_table.add_row("Priority", task.priority.value)
        info_table.add_row("Retries", f"{task.retry_count}/{task.max_retries}")
        info_table.add_row("Created", task.created_at.strftime("%H:%M:%S"))
        
        if task.error:
            info_table.add_row("Error", task.error[:50] + "..." if len(task.error) > 50 else task.error)
        
        layout["info"].update(Panel(info_table, title="Task Info", border_style="cyan"))
        
        # Progress and history
        progress_content = self._create_task_progress(task)
        layout["progress"].update(Panel(progress_content, title="Progress", border_style="green"))
        
        return layout
    
    def _create_simple_task_content(self, task: Task) -> Text:
        """Create simple content for single task."""
        content_lines = [
            f"[bold cyan]Status:[/bold cyan] {format_status(task.status.value)}",
            f"[bold cyan]Priority:[/bold cyan] {task.priority.value}",
            f"[bold cyan]Retries:[/bold cyan] {task.retry_count}/{task.max_retries}",
            f"[bold cyan]Created:[/bold cyan] {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        if task.error:
            content_lines.append(f"[bold red]Error:[/bold red] {task.error}")
        
        if task.result and task.status == TaskStatus.COMPLETED:
            result_preview = str(task.result)[:100] + "..." if len(str(task.result)) > 100 else str(task.result)
            content_lines.append(f"[bold green]Result:[/bold green] {result_preview}")
        
        return Text("\n\n".join(content_lines))
    
    def _create_task_progress(self, task: Task) -> Text:
        """Create progress visualization for task."""
        history = self.task_history[task.id]
        
        if not history:
            return Text("[dim]No history available[/dim]")
        
        progress_lines = []
        
        # Status timeline
        progress_lines.append("[bold]Status Timeline:[/bold]")
        for entry in history[-10:]:  # Last 10 entries
            timestamp = entry["timestamp"].strftime("%H:%M:%S")
            status = format_status(entry["status"])
            progress_lines.append(f"  {timestamp} - {status}")
        
        # Current progress based on status
        if task.status == TaskStatus.RUNNING:
            progress_lines.append("\n[bold]Current:[/bold] 🟠 Executing...")
        elif task.status == TaskStatus.COMPLETED:
            progress_lines.append("\n[bold]Current:[/bold] ✅ Completed successfully")
        elif task.status == TaskStatus.FAILED:
            progress_lines.append("\n[bold]Current:[/bold] ❌ Failed")
        elif task.status == TaskStatus.PENDING:
            progress_lines.append("\n[bold]Current:[/bold] ⏳ Waiting to start")
        
        return Text("\n".join(progress_lines))
    
    def _create_tasks_header(self, task_count: int) -> Panel:
        """Create header for multiple tasks view."""
        header_text = f"[bold blue]Task Monitor[/bold blue] - Tracking {task_count} tasks"
        return Panel(
            Align.center(Text(header_text)),
            style="bold"
        )
    
    def _create_multiple_tasks_panel(self, tasks: List[Task]) -> Columns:
        """Create panel for multiple tasks."""
        panels = []
        
        for task in tasks:
            task_panel = Panel(
                self._create_simple_task_content(task),
                title=f"{task.name[:20]}...",
                border_style="blue",
                width=40
            )
            panels.append(task_panel)
        
        return Columns(panels, equal=True, expand=True)
    
    def _create_tasks_table(self, tasks: List[Task]) -> Panel:
        """Create table view for multiple tasks."""
        table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
        table.add_column("Task", style="green", width=30)
        table.add_column("Status", style="yellow", width=12)
        table.add_column("Priority", style="cyan", width=10)
        table.add_column("Retries", style="white", width=8)
        table.add_column("Age", style="dim", width=12)
        
        for task in tasks:
            age = datetime.utcnow() - task.created_at
            table.add_row(
                task.name[:28] + "..." if len(task.name) > 28 else task.name,
                format_status(task.status.value),
                task.priority.value,
                f"{task.retry_count}/{task.max_retries}",
                format_duration(age.total_seconds())
            )
        
        return Panel(table, title="📋 Task Status", border_style="blue")


class AgentMonitor(BaseMonitor):
    """Agent-specific monitoring for tracking agent performance."""
    
    def __init__(self, orchestrator: Orchestrator, agent_ids: List[UUID], refresh_rate: float = 1.0):
        super().__init__(orchestrator, refresh_rate)
        self.agent_ids = agent_ids
    
    async def create_display(self, detailed: bool = False) -> Layout:
        """Create agent monitoring display."""
        layout = Layout(name="agent_monitor")
        
        # Get agent information
        agents_info = []
        for agent_id in self.agent_ids:
            agent = await self.orchestrator.get_agent(agent_id)
            if agent:
                agents_info.append(agent)
        
        if not agents_info:
            return Panel("[red]No agents found[/red]", title="Agent Monitor")
        
        if len(agents_info) == 1:
            # Single agent detailed view
            layout.update(await self._create_single_agent_panel(agents_info[0], detailed))
        else:
            # Multiple agents view
            layout.update(await self._create_multiple_agents_panel(agents_info, detailed))
        
        return layout
    
    async def _create_single_agent_panel(self, agent: Agent, detailed: bool) -> Panel:
        """Create detailed panel for single agent monitoring."""
        if detailed:
            content = await self._create_detailed_agent_content(agent)
        else:
            content = self._create_simple_agent_content(agent)
        
        return Panel(
            content,
            title=f"🤖 Agent: {agent.agent_type}",
            border_style="green"
        )
    
    async def _create_detailed_agent_content(self, agent: Agent) -> Layout:
        """Create detailed content for single agent."""
        layout = Layout()
        layout.split_row(
            Layout(name="info"),
            Layout(name="metrics")
        )
        
        # Agent information
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Property", style="cyan", width=15)
        info_table.add_column("Value", style="white")
        
        info_table.add_row("ID", str(agent.id)[:8] + "...")
        info_table.add_row("Type", agent.agent_type)
        info_table.add_row("Status", format_status(agent.status.value))
        info_table.add_row("Capabilities", f"{len(agent.capabilities)} items")
        info_table.add_row("Max Tasks", str(agent.max_concurrent_tasks))
        info_table.add_row("Current Tasks", str(len(getattr(agent, 'current_tasks', []))))
        
        layout["info"].update(Panel(info_table, title="Agent Info", border_style="cyan"))
        
        # Metrics
        try:
            metrics = await self.orchestrator.agent_manager.get_agent_metrics(agent.id)
            metrics_content = self._create_agent_metrics_content(metrics)
        except Exception:
            metrics_content = Text("[dim]Metrics unavailable[/dim]")
        
        layout["metrics"].update(Panel(metrics_content, title="Metrics", border_style="yellow"))
        
        return layout
    
    def _create_simple_agent_content(self, agent: Agent) -> Text:
        """Create simple content for single agent."""
        content_lines = [
            f"[bold cyan]Type:[/bold cyan] {agent.agent_type}",
            f"[bold cyan]Status:[/bold cyan] {format_status(agent.status.value)}",
            f"[bold cyan]Capabilities:[/bold cyan] {', '.join(cap.value for cap in agent.capabilities)}",
            f"[bold cyan]Max Tasks:[/bold cyan] {agent.max_concurrent_tasks}",
            f"[bold cyan]Current Tasks:[/bold cyan] {len(getattr(agent, 'current_tasks', []))}",
            f"[bold cyan]Created:[/bold cyan] {agent.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        return Text("\n\n".join(content_lines))
    
    def _create_agent_metrics_content(self, metrics: Dict[str, Any]) -> Text:
        """Create metrics content for agent."""
        if not metrics:
            return Text("[dim]No metrics available[/dim]")
        
        metrics_lines = []
        for key, value in metrics.items():
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, (int, float)):
                metrics_lines.append(f"[cyan]{formatted_key}:[/cyan] [white]{value}[/white]")
            else:
                metrics_lines.append(f"[cyan]{formatted_key}:[/cyan] [white]{str(value)}[/white]")
        
        return Text("\n".join(metrics_lines))
    
    async def _create_multiple_agents_panel(self, agents: List[Agent], detailed: bool) -> Panel:
        """Create panel for multiple agents."""
        if detailed:
            # Create columns of agent panels
            panels = []
            for agent in agents:
                agent_panel = Panel(
                    self._create_simple_agent_content(agent),
                    title=f"{agent.agent_type[:15]}...",
                    border_style="green",
                    width=40
                )
                panels.append(agent_panel)
            
            return Panel(
                Columns(panels, equal=True, expand=True),
                title="🤖 Agent Status",
                border_style="blue"
            )
        else:
            # Create table view
            table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
            table.add_column("Agent", style="green", width=25)
            table.add_column("Status", style="yellow", width=12)
            table.add_column("Type", style="cyan", width=20)
            table.add_column("Tasks", style="white", width=10)
            table.add_column("Capabilities", style="dim", width=15)
            
            for agent in agents:
                table.add_row(
                    str(agent.id)[:8] + "...",
                    format_status(agent.status.value),
                    agent.agent_type,
                    f"{len(getattr(agent, 'current_tasks', []))}/{agent.max_concurrent_tasks}",
                    f"{len(agent.capabilities)} caps"
                )
            
            return Panel(table, title="🤖 Agent Status", border_style="green")