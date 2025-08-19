"""
MAOS CLI Status Commands

System monitoring and health check commands with real-time updates,
detailed component status, and performance metrics.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.text import Text
from rich.tree import Tree

from ..formatters import OutputFormatter, format_status, format_duration, format_size, create_summary_panel
from ..monitoring import SystemMonitor
from .._main import _orchestrator, init_orchestrator

console = Console()
status_app = typer.Typer(help="📊 System monitoring and status")


@status_app.command(name="overview")
def system_overview(
    output_format: str = typer.Option(
        "table", "--format", "-f",
        help="Output format (table, json, yaml, tree)"
    ),
    detailed: bool = typer.Option(
        False, "--detailed", "-d",
        help="Show detailed information"
    ),
    refresh: bool = typer.Option(
        False, "--refresh", "-r",
        help="Auto-refresh display"
    ),
    refresh_interval: float = typer.Option(
        2.0, "--interval", "-i",
        help="Refresh interval in seconds"
    )
):
    """📊 Show system overview and health status
    
    Displays comprehensive system status including component health,
    active operations, and key performance metrics.
    """
    
    async def _show_overview():
        try:
            orchestrator = init_orchestrator()
            
            if refresh:
                monitor = SystemMonitor(orchestrator, refresh_interval)
                await monitor.start_live_monitoring(detailed=detailed)
            else:
                await _show_status_once(orchestrator, output_format, detailed)
                
        except Exception as e:
            console.print(f"[red]❌ Failed to get system overview: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_show_overview())


@status_app.command(name="health")
def health_check(
    component: Optional[str] = typer.Option(
        None, "--component", "-c",
        help="Check specific component health"
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f",
        help="Output format (table, json, yaml)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Show detailed health information"
    )
):
    """🌡️ Perform system health check
    
    Checks the health of all system components or a specific component
    with optional verbose diagnostics.
    """
    
    async def _health_check():
        try:
            orchestrator = init_orchestrator()
            
            with console.status("[bold blue]Checking system health..."):
                health_status = await orchestrator.get_component_health()
                system_status = await orchestrator.get_system_status()
            
            if component:
                # Check specific component
                if component not in health_status:
                    console.print(f"[red]❌ Unknown component: {component}[/red]")
                    available = ", ".join(health_status.keys())
                    console.print(f"[dim]Available components: {available}[/dim]")
                    raise typer.Exit(1)
                
                component_status = health_status[component]
                await _show_component_health(orchestrator, component, component_status, verbose, output_format)
            else:
                # Check all components
                await _show_all_health(health_status, system_status, verbose, output_format)
                
        except Exception as e:
            console.print(f"[red]❌ Health check failed: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_health_check())


@status_app.command(name="metrics")
def system_metrics(
    component: Optional[str] = typer.Option(
        None, "--component", "-c",
        help="Show metrics for specific component"
    ),
    time_range: str = typer.Option(
        "1h", "--range", "-r",
        help="Time range for metrics (5m, 1h, 6h, 24h)"
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f",
        help="Output format (table, json, yaml)"
    ),
    export_file: Optional[str] = typer.Option(
        None, "--export", "-e",
        help="Export metrics to file"
    )
):
    """📊 Show detailed system metrics
    
    Displays performance metrics and statistics for system components
    with time-based filtering and export capabilities.
    """
    
    async def _show_metrics():
        try:
            orchestrator = init_orchestrator()
            
            with console.status("[bold blue]Collecting metrics..."):
                metrics = await orchestrator.get_system_metrics()
            
            if component:
                # Show specific component metrics
                if component not in metrics:
                    console.print(f"[red]❌ No metrics found for component: {component}[/red]")
                    available = ", ".join(k for k in metrics.keys() if k != "timestamp")
                    console.print(f"[dim]Available components: {available}[/dim]")
                    raise typer.Exit(1)
                
                component_metrics = metrics[component]
                await _show_component_metrics(component, component_metrics, output_format)
            else:
                # Show all metrics
                await _show_all_metrics(metrics, output_format)
            
            # Export if requested
            if export_file:
                await _export_metrics(metrics, export_file, component)
                
        except Exception as e:
            console.print(f"[red]❌ Failed to get metrics: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_show_metrics())


@status_app.command(name="monitor")
def live_monitor(
    refresh_rate: float = typer.Option(
        1.0, "--rate", "-r",
        help="Refresh rate in seconds"
    ),
    detailed: bool = typer.Option(
        False, "--detailed", "-d",
        help="Show detailed monitoring view"
    ),
    components: Optional[List[str]] = typer.Option(
        None, "--component", "-c",
        help="Monitor specific components only"
    )
):
    """🔄 Start live system monitoring
    
    Provides real-time monitoring dashboard with live updates
    of system status, metrics, and component health.
    """
    
    async def _start_monitoring():
        try:
            orchestrator = init_orchestrator()
            
            console.print("[bold blue]Starting live system monitor...[/bold blue]")
            console.print("[dim]Press Ctrl+C to exit[/dim]\n")
            
            monitor = SystemMonitor(orchestrator, refresh_rate)
            await monitor.start_live_monitoring(detailed=detailed)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoring stopped[/yellow]")
        except Exception as e:
            console.print(f"\n[red]❌ Monitoring failed: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_start_monitoring())


@status_app.command(name="uptime")
def system_uptime(
    output_format: str = typer.Option(
        "table", "--format", "-f",
        help="Output format (table, json, yaml)"
    )
):
    """⏱️ Show system uptime and availability
    
    Displays system uptime, startup time, and availability statistics.
    """
    
    async def _show_uptime():
        try:
            orchestrator = init_orchestrator()
            
            system_status = await orchestrator.get_system_status()
            
            uptime_data = {
                "running": system_status.get("running", False),
                "startup_time": system_status.get("startup_time"),
                "current_time": datetime.utcnow().isoformat(),
            }
            
            if uptime_data["startup_time"]:
                startup_time = datetime.fromisoformat(uptime_data["startup_time"])
                uptime_seconds = (datetime.utcnow() - startup_time).total_seconds()
                uptime_data["uptime_seconds"] = uptime_seconds
                uptime_data["uptime_formatted"] = format_duration(uptime_seconds)
                
                # Calculate availability (assuming 99.9% target)
                uptime_data["availability_percent"] = min(99.9, (uptime_seconds / (24 * 3600)) * 100)
            else:
                uptime_data["uptime_seconds"] = 0
                uptime_data["uptime_formatted"] = "N/A"
                uptime_data["availability_percent"] = 0
            
            # Format output
            formatter = OutputFormatter.create(output_format)
            console.print(formatter.format_dict(uptime_data, "System Uptime"))
            
        except Exception as e:
            console.print(f"[red]❌ Failed to get uptime: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_show_uptime())


@status_app.command(name="summary")
def status_summary(
    output_format: str = typer.Option(
        "table", "--format", "-f",
        help="Output format (table, json, yaml)"
    ),
    include_history: bool = typer.Option(
        False, "--history",
        help="Include historical data"
    )
):
    """📊 Show comprehensive status summary
    
    Provides a high-level summary of system status, key metrics,
    and overall health in a compact format.
    """
    
    async def _show_summary():
        try:
            orchestrator = init_orchestrator()
            
            with console.status("[bold blue]Generating status summary..."):
                system_status = await orchestrator.get_system_status()
                metrics = await orchestrator.get_system_metrics()
                health = await orchestrator.get_component_health()
            
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
            
            healthy_components = sum(1 for status in health.values() if status == "healthy")
            total_components = len(health)
            
            summary_data = {
                "system_running": system_status.get("running", False),
                "active_executions": system_status.get("active_executions", 0),
                "execution_plans": system_status.get("execution_plans", 0),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "success_rate_percent": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                "healthy_components": healthy_components,
                "total_components": total_components,
                "health_percentage": (healthy_components / total_components * 100) if total_components > 0 else 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if system_status.get("startup_time"):
                startup_time = datetime.fromisoformat(system_status["startup_time"])
                uptime_seconds = (datetime.utcnow() - startup_time).total_seconds()
                summary_data["uptime_seconds"] = uptime_seconds
                summary_data["uptime_formatted"] = format_duration(uptime_seconds)
            
            # Format output
            if output_format == "table":
                console.print(create_summary_panel(summary_data, "System Summary"))
            else:
                formatter = OutputFormatter.create(output_format)
                console.print(formatter.format_dict(summary_data, "System Summary"))
                
        except Exception as e:
            console.print(f"[red]❌ Failed to generate summary: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_show_summary())


# Helper functions

async def _show_status_once(orchestrator, output_format: str, detailed: bool):
    """Show system status once."""
    system_status = await orchestrator.get_system_status()
    component_health = await orchestrator.get_component_health()
    
    if detailed:
        metrics = await orchestrator.get_system_metrics()
        await _show_detailed_status(system_status, component_health, metrics, output_format)
    else:
        await _show_simple_status(system_status, component_health, output_format)


async def _show_detailed_status(system_status: Dict, health: Dict, metrics: Dict, output_format: str):
    """Show detailed system status."""
    # System information
    system_info = {
        "running": system_status.get("running", False),
        "startup_time": system_status.get("startup_time"),
        "active_executions": system_status.get("active_executions", 0),
        "execution_plans": system_status.get("execution_plans", 0),
        "uptime_seconds": system_status.get("uptime_seconds", 0)
    }
    
    if system_info["startup_time"]:
        startup_time = datetime.fromisoformat(system_info["startup_time"])
        uptime_seconds = (datetime.utcnow() - startup_time).total_seconds()
        system_info["uptime_formatted"] = format_duration(uptime_seconds)
    
    formatter = OutputFormatter.create(output_format)
    console.print(formatter.format_dict(system_info, "System Status"))
    
    # Component health
    console.print("\n")
    console.print(formatter.format_dict(health, "Component Health"))
    
    # Metrics summary
    console.print("\n")
    metrics_summary = {}
    for component, component_metrics in metrics.items():
        if component != "timestamp" and isinstance(component_metrics, dict):
            tasks_completed = component_metrics.get("tasks_completed", 0)
            tasks_failed = component_metrics.get("tasks_failed", 0)
            total_tasks = tasks_completed + tasks_failed
            
            metrics_summary[f"{component}_total_tasks"] = total_tasks
            if total_tasks > 0:
                metrics_summary[f"{component}_success_rate"] = f"{(tasks_completed/total_tasks*100):.1f}%"
    
    if metrics_summary:
        console.print(formatter.format_dict(metrics_summary, "Metrics Summary"))


async def _show_simple_status(system_status: Dict, health: Dict, output_format: str):
    """Show simple system status."""
    # Calculate health summary
    healthy_count = sum(1 for status in health.values() if status == "healthy")
    total_count = len(health)
    
    status_data = {
        "system_running": system_status.get("running", False),
        "active_executions": system_status.get("active_executions", 0),
        "component_health": f"{healthy_count}/{total_count} healthy",
        "health_percentage": f"{(healthy_count/total_count*100):.1f}%" if total_count > 0 else "0%"
    }
    
    if system_status.get("startup_time"):
        startup_time = datetime.fromisoformat(system_status["startup_time"])
        uptime_seconds = (datetime.utcnow() - startup_time).total_seconds()
        status_data["uptime"] = format_duration(uptime_seconds)
    
    formatter = OutputFormatter.create(output_format)
    console.print(formatter.format_dict(status_data, "System Status"))


async def _show_component_health(orchestrator, component: str, status: str, verbose: bool, output_format: str):
    """Show health for a specific component."""
    health_data = {
        "component": component,
        "status": status,
        "healthy": status == "healthy",
        "checked_at": datetime.utcnow().isoformat()
    }
    
    if verbose:
        # Add more detailed health information
        try:
            if component == "orchestrator":
                system_status = await orchestrator.get_system_status()
                health_data["running"] = system_status.get("running")
                health_data["active_executions"] = system_status.get("active_executions")
            
            # Add component-specific metrics if available
            metrics = await orchestrator.get_system_metrics()
            if component in metrics:
                component_metrics = metrics[component]
                if isinstance(component_metrics, dict):
                    health_data.update(component_metrics)
                    
        except Exception as e:
            health_data["verbose_error"] = str(e)
    
    formatter = OutputFormatter.create(output_format)
    console.print(formatter.format_dict(health_data, f"Health: {component}"))


async def _show_all_health(health: Dict, system_status: Dict, verbose: bool, output_format: str):
    """Show health for all components."""
    healthy_count = sum(1 for status in health.values() if status == "healthy")
    total_count = len(health)
    
    # Overall health summary
    console.print(f"[bold blue]Overall Health:[/bold blue] {healthy_count}/{total_count} components healthy\n")
    
    if output_format == "table":
        # Create health table
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Health", style="green")
        
        if verbose:
            table.add_column("Details", style="dim")
        
        for component, status in health.items():
            health_icon = "✓" if status == "healthy" else "❌"
            health_color = "green" if status == "healthy" else "red"
            
            row_data = [
                component.replace('_', ' ').title(),
                format_status(status),
                f"[{health_color}]{health_icon}[/{health_color}]"
            ]
            
            if verbose:
                # Add component details
                if component == "orchestrator":
                    details = f"Running: {system_status.get('running', False)}"
                else:
                    details = "OK"
                row_data.append(details)
            
            table.add_row(*row_data)
        
        console.print(table)
    else:
        # Use formatter
        formatter = OutputFormatter.create(output_format)
        health_with_summary = {
            "summary": {
                "healthy_components": healthy_count,
                "total_components": total_count,
                "health_percentage": f"{(healthy_count/total_count*100):.1f}%"
            },
            "components": health
        }
        console.print(formatter.format_dict(health_with_summary, "Component Health"))


async def _show_component_metrics(component: str, metrics: Dict, output_format: str):
    """Show metrics for a specific component."""
    formatter = OutputFormatter.create(output_format)
    console.print(formatter.format_dict(metrics, f"Metrics: {component}"))


async def _show_all_metrics(metrics: Dict, output_format: str):
    """Show metrics for all components."""
    # Filter out timestamp and process metrics
    processed_metrics = {}
    
    for component, component_metrics in metrics.items():
        if component == "timestamp":
            continue
        
        if isinstance(component_metrics, dict):
            # Calculate derived metrics
            tasks_completed = component_metrics.get("tasks_completed", 0)
            tasks_failed = component_metrics.get("tasks_failed", 0)
            total_tasks = tasks_completed + tasks_failed
            
            component_summary = dict(component_metrics)  # Copy
            
            if total_tasks > 0:
                component_summary["success_rate_percent"] = (tasks_completed / total_tasks) * 100
            
            processed_metrics[component] = component_summary
        else:
            processed_metrics[component] = component_metrics
    
    if output_format == "table":
        # Create metrics table
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Component", style="cyan")
        table.add_column("Total Tasks", style="green")
        table.add_column("Completed", style="blue")
        table.add_column("Failed", style="red")
        table.add_column("Success Rate", style="yellow")
        
        for component, component_metrics in processed_metrics.items():
            if isinstance(component_metrics, dict):
                tasks_completed = component_metrics.get("tasks_completed", 0)
                tasks_failed = component_metrics.get("tasks_failed", 0)
                total_tasks = tasks_completed + tasks_failed
                success_rate = component_metrics.get("success_rate_percent", 0)
                
                table.add_row(
                    component.title(),
                    str(total_tasks),
                    str(tasks_completed),
                    str(tasks_failed),
                    f"{success_rate:.1f}%" if success_rate else "N/A"
                )
        
        console.print(table)
    else:
        formatter = OutputFormatter.create(output_format)
        console.print(formatter.format_dict(processed_metrics, "System Metrics"))


async def _export_metrics(metrics: Dict, export_file: str, component: Optional[str] = None):
    """Export metrics to file."""
    try:
        export_data = {
            "exported_at": datetime.utcnow().isoformat(),
            "component": component,
            "metrics": metrics if not component else {component: metrics.get(component)}
        }
        
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        console.print(f"[green]✓ Metrics exported to {export_file}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Export failed: {e}[/red]")