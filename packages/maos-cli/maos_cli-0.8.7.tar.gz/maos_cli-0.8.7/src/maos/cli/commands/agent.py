"""
MAOS CLI Agent Management Commands

Comprehensive agent management with lifecycle operations,
monitoring, and performance tracking.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from uuid import UUID

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt, Confirm

from ...models.agent import Agent, AgentCapability, AgentStatus
from ...utils.exceptions import AgentError, MAOSError
from ..formatters import OutputFormatter, TableFormatter
from ..monitoring import AgentMonitor
from .._main import _orchestrator, init_orchestrator

console = Console()
agent_app = typer.Typer(help="🤖 Agent lifecycle operations")


@agent_app.command(name="create")
def create_agent(
    agent_type: str = typer.Argument(..., help="Agent type identifier"),
    capabilities: List[str] = typer.Option(
        [], "--capability", "-c",
        help="Agent capabilities (can be specified multiple times)"
    ),
    max_concurrent_tasks: int = typer.Option(
        1, "--max-tasks", "-m",
        help="Maximum concurrent tasks"
    ),
    cpu_limit: Optional[float] = typer.Option(
        None, "--cpu-limit",
        help="CPU limit in cores"
    ),
    memory_limit: Optional[int] = typer.Option(
        None, "--memory-limit",
        help="Memory limit in MB"
    ),
    config_file: Optional[str] = typer.Option(
        None, "--config",
        help="Agent configuration file (JSON)"
    ),
    tags: Optional[List[str]] = typer.Option(
        None, "--tag",
        help="Agent tags (can be specified multiple times)"
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f",
        help="Output format (table, json, yaml)"
    )
):
    """🚀 Create a new agent
    
    Creates a new agent with specified capabilities and configuration.
    Supports various agent types and resource limits.
    """
    
    async def _create_agent():
        try:
            orchestrator = init_orchestrator()
            
            # Load additional configuration from file
            agent_config = {}
            if config_file:
                try:
                    with open(config_file) as f:
                        agent_config = json.load(f)
                except Exception as e:
                    console.print(f"[red]❌ Error loading config file: {e}[/red]")
                    raise typer.Exit(1)
            
            # Set resource limits
            if cpu_limit is not None:
                agent_config["cpu_limit"] = cpu_limit
            if memory_limit is not None:
                agent_config["memory_limit"] = memory_limit
            
            agent_config["max_concurrent_tasks"] = max_concurrent_tasks
            agent_config["tags"] = set(tags or [])
            
            # Convert capability strings to enums
            capability_set = set()
            for cap_str in capabilities:
                try:
                    capability_set.add(AgentCapability(cap_str))
                except ValueError:
                    # Try to find by name
                    for cap in AgentCapability:
                        if cap.value.lower() == cap_str.lower():
                            capability_set.add(cap)
                            break
                    else:
                        console.print(f"[yellow]⚠️  Unknown capability: {cap_str}[/yellow]")
            
            # Create agent
            with console.status("[bold blue]Creating agent..."):
                agent = await orchestrator.create_agent(
                    agent_type=agent_type,
                    capabilities=capability_set,
                    configuration=agent_config
                )
            
            console.print(f"[green]✅ Agent created successfully![/green]")
            
            # Display agent information
            agent_info = {
                "agent_id": str(agent.id),
                "type": agent.agent_type,
                "status": agent.status.value,
                "capabilities": [cap.value for cap in agent.capabilities],
                "max_concurrent_tasks": agent.max_concurrent_tasks,
                "created_at": agent.created_at.isoformat(),
                "tags": list(agent.tags) if hasattr(agent, 'tags') else []
            }
            
            if hasattr(agent, 'resource_limits') and agent.resource_limits:
                agent_info["resource_limits"] = agent.resource_limits
            
            # Format output
            formatter = OutputFormatter.create(output_format)
            console.print(formatter.format_dict(agent_info, "Agent Created"))
            
        except Exception as e:
            console.print(f"[red]❌ Failed to create agent: {e}[/red]")
            if isinstance(e, (AgentError, MAOSError)):
                console.print(f"[dim]Error code: {getattr(e, 'error_code', 'UNKNOWN')}[/dim]")
            raise typer.Exit(1)
    
    asyncio.run(_create_agent())


@agent_app.command(name="list")
def list_agents(
    status: Optional[List[str]] = typer.Option(
        None, "--status", "-s",
        help="Filter by status (available, busy, idle, error)"
    ),
    agent_type: Optional[str] = typer.Option(
        None, "--type", "-t",
        help="Filter by agent type"
    ),
    capabilities: Optional[List[str]] = typer.Option(
        None, "--capability", "-c",
        help="Filter by required capabilities"
    ),
    tags: Optional[List[str]] = typer.Option(
        None, "--tag",
        help="Filter by tags"
    ),
    limit: int = typer.Option(
        50, "--limit", "-l",
        help="Maximum number of agents to display"
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f",
        help="Output format (table, json, yaml)"
    ),
    watch: bool = typer.Option(
        False, "--watch", "-w",
        help="Watch for agent updates in real-time"
    ),
    detailed: bool = typer.Option(
        False, "--detailed", "-d",
        help="Show detailed information"
    )
):
    """📋 List agents with filtering options
    
    Displays agents with comprehensive filtering and formatting.
    """
    
    async def _list_agents():
        try:
            orchestrator = init_orchestrator()
            
            if watch:
                await _watch_agents(orchestrator, status, agent_type, capabilities, tags, limit, detailed)
            else:
                await _show_agents_once(orchestrator, status, agent_type, capabilities, tags, limit, output_format, detailed)
                
        except Exception as e:
            console.print(f"[red]❌ Failed to list agents: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_list_agents())


@agent_app.command(name="status")
def agent_status(
    agent_id: str = typer.Argument(..., help="Agent ID"),
    output_format: str = typer.Option(
        "table", "--format", "-f",
        help="Output format (table, json, yaml)"
    ),
    show_tasks: bool = typer.Option(
        False, "--tasks",
        help="Show current tasks"
    ),
    show_metrics: bool = typer.Option(
        False, "--metrics",
        help="Show performance metrics"
    ),
    monitor: bool = typer.Option(
        False, "--monitor", "-m",
        help="Monitor agent in real-time"
    )
):
    """🔍 Get detailed status of a specific agent
    
    Shows comprehensive agent information including current tasks,
    performance metrics, and resource usage.
    """
    
    async def _show_agent_status():
        try:
            orchestrator = init_orchestrator()
            
            # Validate agent ID
            try:
                agent_uuid = UUID(agent_id)
            except ValueError:
                console.print(f"[red]❌ Invalid agent ID format: {agent_id}[/red]")
                raise typer.Exit(1)
            
            if monitor:
                agent_monitor = AgentMonitor(orchestrator, [agent_uuid])
                await agent_monitor.start_live_monitoring(detailed=True)
            else:
                await _show_single_agent_status(orchestrator, agent_uuid, output_format, show_tasks, show_metrics)
                
        except Exception as e:
            console.print(f"[red]❌ Failed to get agent status: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_show_agent_status())


@agent_app.command(name="terminate")
def terminate_agent(
    agent_id: str = typer.Argument(..., help="Agent ID"),
    reason: str = typer.Option(
        "Terminated by user", "--reason", "-r",
        help="Termination reason"
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Force termination without confirmation"
    ),
    wait_for_tasks: bool = typer.Option(
        True, "--wait/--no-wait",
        help="Wait for current tasks to complete"
    )
):
    """🗑️ Terminate an agent
    
    Terminates the specified agent with optional graceful shutdown.
    """
    
    async def _terminate_agent():
        try:
            orchestrator = init_orchestrator()
            
            # Validate agent ID
            try:
                agent_uuid = UUID(agent_id)
            except ValueError:
                console.print(f"[red]❌ Invalid agent ID format: {agent_id}[/red]")
                raise typer.Exit(1)
            
            # Get agent for confirmation
            agent = await orchestrator.get_agent(agent_uuid)
            if not agent:
                console.print(f"[red]❌ Agent not found: {agent_id}[/red]")
                raise typer.Exit(1)
            
            # Confirmation
            if not force:
                agent_info = f"Agent: {agent.agent_type} (ID: {str(agent.id)[:8]}...)"
                if not Confirm.ask(f"Terminate {agent_info}?", default=False):
                    console.print("[yellow]Termination aborted[/yellow]")
                    return
            
            # Terminate agent
            with console.status("[bold red]Terminating agent..."):
                success = await orchestrator.terminate_agent(agent_uuid, reason)
            
            if success:
                console.print(f"[green]✅ Agent terminated successfully[/green]")
                console.print(f"[dim]Reason: {reason}[/dim]")
            else:
                console.print(f"[red]❌ Failed to terminate agent[/red]")
                raise typer.Exit(1)
                
        except Exception as e:
            console.print(f"[red]❌ Error terminating agent: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_terminate_agent())


@agent_app.command(name="restart")
def restart_agent(
    agent_id: str = typer.Argument(..., help="Agent ID"),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Force restart without confirmation"
    )
):
    """🔄 Restart an agent
    
    Restarts the specified agent, useful for recovery from error states.
    """
    
    async def _restart_agent():
        try:
            orchestrator = init_orchestrator()
            
            # Validate agent ID
            try:
                agent_uuid = UUID(agent_id)
            except ValueError:
                console.print(f"[red]❌ Invalid agent ID format: {agent_id}[/red]")
                raise typer.Exit(1)
            
            # Get agent for validation
            agent = await orchestrator.get_agent(agent_uuid)
            if not agent:
                console.print(f"[red]❌ Agent not found: {agent_id}[/red]")
                raise typer.Exit(1)
            
            # Confirmation
            if not force:
                agent_info = f"Agent: {agent.agent_type} (Status: {agent.status.value})"
                if not Confirm.ask(f"Restart {agent_info}?", default=True):
                    console.print("[yellow]Restart aborted[/yellow]")
                    return
            
            # Restart agent (terminate and recreate)
            with console.status("[bold blue]Restarting agent..."):
                # Get agent configuration for recreation
                agent_config = {
                    "max_concurrent_tasks": agent.max_concurrent_tasks,
                    "tags": agent.tags if hasattr(agent, 'tags') else set()
                }
                
                if hasattr(agent, 'resource_limits'):
                    agent_config.update(agent.resource_limits or {})
                
                # Terminate current agent
                await orchestrator.terminate_agent(agent_uuid, "Restarting")
                
                # Create new agent with same configuration
                new_agent = await orchestrator.create_agent(
                    agent_type=agent.agent_type,
                    capabilities=agent.capabilities,
                    configuration=agent_config
                )
            
            console.print(f"[green]✅ Agent restarted successfully[/green]")
            console.print(f"[dim]Old ID: {str(agent_uuid)[:8]}...[/dim]")
            console.print(f"[dim]New ID: {str(new_agent.id)[:8]}...[/dim]")
            
        except Exception as e:
            console.print(f"[red]❌ Error restarting agent: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_restart_agent())


@agent_app.command(name="metrics")
def agent_metrics(
    agent_id: Optional[str] = typer.Argument(None, help="Agent ID (optional - shows all if omitted)"),
    metric_type: str = typer.Option(
        "all", "--type", "-t",
        help="Metric type (all, performance, resource, task)"
    ),
    time_range: str = typer.Option(
        "1h", "--range", "-r",
        help="Time range (1h, 6h, 24h, 7d)"
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f",
        help="Output format (table, json, yaml)"
    )
):
    """📊 Show agent performance metrics
    
    Displays detailed performance and resource usage metrics
    for agents with time-based filtering.
    """
    
    async def _show_metrics():
        try:
            orchestrator = init_orchestrator()
            
            agent_uuid = None
            if agent_id:
                try:
                    agent_uuid = UUID(agent_id)
                except ValueError:
                    console.print(f"[red]❌ Invalid agent ID format: {agent_id}[/red]")
                    raise typer.Exit(1)
            
            # Get metrics from agent manager
            if agent_uuid:
                metrics = await orchestrator.agent_manager.get_agent_metrics(agent_uuid)
                if not metrics:
                    console.print(f"[red]❌ No metrics found for agent {agent_id}[/red]")
                    return
                
                # Display single agent metrics
                console.print(f"[bold blue]Metrics for Agent {str(agent_uuid)[:8]}...[/bold blue]")
                _display_agent_metrics(metrics, metric_type, output_format)
            else:
                # Display all agent metrics
                all_metrics = await orchestrator.agent_manager.get_all_agent_metrics()
                
                if not all_metrics:
                    console.print("[yellow]⚠️  No agent metrics available[/yellow]")
                    return
                
                console.print(f"[bold blue]All Agent Metrics[/bold blue]")
                for agent_id_str, metrics in all_metrics.items():
                    console.print(f"\n[dim]Agent {agent_id_str[:8]}...[/dim]")
                    _display_agent_metrics(metrics, metric_type, output_format)
                    
        except Exception as e:
            console.print(f"[red]❌ Error retrieving metrics: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_show_metrics())


# Helper functions

async def _show_agents_once(orchestrator, status_filter, agent_type, capabilities, tags, limit, output_format, detailed):
    """Show agents once with filtering."""
    agents_data = await _get_filtered_agents(
        orchestrator, status_filter, agent_type, capabilities, tags, limit
    )
    
    if not agents_data:
        console.print("[yellow]No agents found matching criteria[/yellow]")
        return
    
    formatter = OutputFormatter.create(output_format)
    if detailed:
        for agent_data in agents_data:
            console.print(formatter.format_dict(agent_data, f"Agent: {agent_data['type']}"))
            console.print("")
    else:
        console.print(formatter.format_list(agents_data, "Agents"))
    
    console.print(f"\n[dim]Showing {len(agents_data)} agents[/dim]")


async def _watch_agents(orchestrator, status_filter, agent_type, capabilities, tags, limit, detailed):
    """Watch agents with real-time updates."""
    with Live(console=console, refresh_per_second=2) as live:
        while True:
            try:
                agents_data = await _get_filtered_agents(
                    orchestrator, status_filter, agent_type, capabilities, tags, limit
                )
                
                if agents_data:
                    if detailed:
                        # Show detailed view
                        panels = []
                        for agent_data in agents_data[:5]:  # Limit to 5 for space
                            formatter = TableFormatter()
                            agent_table = formatter._create_dict_table(agent_data)
                            panels.append(Panel(agent_table, title=f"🤖 {agent_data['type']}", border_style="green"))
                        
                        if len(agents_data) > 5:
                            panels.append(Panel(f"[dim]...and {len(agents_data) - 5} more agents[/dim]", border_style="dim"))
                        
                        from rich.columns import Columns
                        live.update(Columns(panels, equal=True, expand=True))
                    else:
                        # Show table view
                        formatter = TableFormatter()
                        table = formatter._create_table(agents_data, "Live Agents")
                        live.update(Panel(table, title=f"🔄 Live Agents ({len(agents_data)})", border_style="blue"))
                else:
                    live.update(Panel("[yellow]No agents found[/yellow]", title="🔄 Live Agents", border_style="blue"))
                
                await asyncio.sleep(2)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                live.update(Panel(f"[red]Error: {e}[/red]", title="🔄 Live Agents", border_style="red"))
                await asyncio.sleep(5)


async def _show_single_agent_status(orchestrator, agent_id: UUID, output_format: str, show_tasks: bool, show_metrics: bool):
    """Show detailed status for a single agent."""
    agent = await orchestrator.get_agent(agent_id)
    if not agent:
        console.print(f"[red]❌ Agent not found: {agent_id}[/red]")
        raise typer.Exit(1)
    
    # Prepare agent data
    agent_data = {
        "id": str(agent.id),
        "type": agent.agent_type,
        "status": agent.status.value,
        "capabilities": [cap.value for cap in agent.capabilities],
        "max_concurrent_tasks": agent.max_concurrent_tasks,
        "current_tasks": len(getattr(agent, 'current_tasks', [])),
        "created_at": agent.created_at.isoformat(),
        "last_heartbeat": getattr(agent, 'last_heartbeat', None),
    }
    
    if hasattr(agent, 'resource_limits') and agent.resource_limits:
        agent_data["resource_limits"] = agent.resource_limits
    
    if hasattr(agent, 'tags') and agent.tags:
        agent_data["tags"] = list(agent.tags)
    
    # Format and display
    formatter = OutputFormatter.create(output_format)
    console.print(formatter.format_dict(agent_data, f"Agent Status: {agent.agent_type}"))
    
    # Show current tasks if requested
    if show_tasks and hasattr(agent, 'current_tasks') and agent.current_tasks:
        console.print("\n[bold]Current Tasks:[/bold]")
        tasks_table = Table(show_header=True, header_style="bold blue")
        tasks_table.add_column("Task ID", style="cyan")
        tasks_table.add_column("Name", style="green")
        tasks_table.add_column("Status", style="yellow")
        
        for task_id in agent.current_tasks:
            task = await orchestrator.get_task(task_id)
            if task:
                tasks_table.add_row(
                    str(task.id)[:8] + "...",
                    task.name,
                    task.status.value
                )
        
        console.print(tasks_table)
    
    # Show metrics if requested
    if show_metrics:
        try:
            metrics = await orchestrator.agent_manager.get_agent_metrics(agent_id)
            if metrics:
                console.print("\n[bold]Performance Metrics:[/bold]")
                _display_agent_metrics(metrics, "all", "table")
        except Exception as e:
            console.print(f"[dim]Could not retrieve metrics: {e}[/dim]")


async def _get_filtered_agents(orchestrator, status_filter, agent_type, capabilities, tags, limit):
    """Get agents with applied filters."""
    # Get all agents
    all_agents = await orchestrator.state_manager.get_objects('agents')
    
    filtered_agents = []
    for agent in all_agents:
        # Apply filters
        if status_filter and agent.status.value not in status_filter:
            continue
        
        if agent_type and agent.agent_type != agent_type:
            continue
        
        if capabilities:
            agent_cap_values = {cap.value for cap in agent.capabilities}
            if not any(cap in agent_cap_values for cap in capabilities):
                continue
        
        if tags and hasattr(agent, 'tags'):
            if not any(tag in agent.tags for tag in tags):
                continue
        
        filtered_agents.append({
            "id": str(agent.id)[:8] + "...",
            "type": agent.agent_type,
            "status": agent.status.value,
            "capabilities": [cap.value for cap in agent.capabilities],
            "current_tasks": len(getattr(agent, 'current_tasks', [])),
            "max_tasks": agent.max_concurrent_tasks,
            "created_at": agent.created_at.isoformat(),
        })
        
        if limit and len(filtered_agents) >= limit:
            break
    
    return filtered_agents


def _display_agent_metrics(metrics: Dict, metric_type: str, output_format: str):
    """Display agent metrics in specified format."""
    # Filter metrics by type
    if metric_type != "all":
        filtered_metrics = {
            k: v for k, v in metrics.items() 
            if metric_type in k.lower()
        }
    else:
        filtered_metrics = metrics
    
    if not filtered_metrics:
        console.print("[dim]No metrics available[/dim]")
        return
    
    if output_format == "table":
        metrics_table = Table(show_header=True, header_style="bold blue")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="green")
        
        for key, value in filtered_metrics.items():
            metrics_table.add_row(key, str(value))
        
        console.print(metrics_table)
    else:
        formatter = OutputFormatter.create(output_format)
        console.print(formatter.format_dict(filtered_metrics, "Agent Metrics"))