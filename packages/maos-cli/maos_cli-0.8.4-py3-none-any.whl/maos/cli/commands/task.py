"""
MAOS CLI Task Management Commands

Comprehensive task management commands with rich output formatting,
real-time monitoring, and advanced filtering capabilities.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from uuid import UUID

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.json import JSON

from ...models.task import Task, TaskStatus, TaskPriority
from ...utils.exceptions import TaskError, MAOSError
from ..formatters import OutputFormatter, TableFormatter, JSONFormatter
from ..monitoring import TaskMonitor
from .._main import _orchestrator, init_orchestrator

console = Console()
task_app = typer.Typer(help="📋 Task management operations")


@task_app.command(name="submit")
def submit_task(
    name: str = typer.Argument(..., help="Task name"),
    description: Optional[str] = typer.Option(
        None, "--description", "-d",
        help="Task description"
    ),
    priority: TaskPriority = typer.Option(
        TaskPriority.MEDIUM, "--priority", "-p",
        help="Task priority (low, medium, high, critical)"
    ),
    timeout: int = typer.Option(
        3600, "--timeout", "-t",
        help="Task timeout in seconds"
    ),
    max_retries: int = typer.Option(
        3, "--max-retries", "-r",
        help="Maximum number of retries"
    ),
    parameters_file: Optional[Path] = typer.Option(
        None, "--parameters", "--params",
        help="JSON file containing task parameters"
    ),
    resource_cpu: Optional[float] = typer.Option(
        None, "--cpu",
        help="Required CPU cores"
    ),
    resource_memory: Optional[int] = typer.Option(
        None, "--memory",
        help="Required memory in MB"
    ),
    resource_disk: Optional[int] = typer.Option(
        None, "--disk",
        help="Required disk space in MB"
    ),
    tags: Optional[List[str]] = typer.Option(
        None, "--tag",
        help="Task tags (can be specified multiple times)"
    ),
    decomposition_strategy: Optional[str] = typer.Option(
        None, "--strategy",
        help="Task decomposition strategy (hierarchical, parallel, pipeline)"
    ),
    wait: bool = typer.Option(
        False, "--wait", "-w",
        help="Wait for task completion"
    ),
    monitor: bool = typer.Option(
        False, "--monitor", "-m",
        help="Monitor task progress in real-time"
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f",
        help="Output format (table, json, yaml)"
    )
):
    """📋 Submit a new task for execution
    
    Creates and submits a new task to the orchestration system
    with comprehensive parameter support and monitoring options.
    """
    
    async def _submit_task():
        try:
            orchestrator = init_orchestrator()
            
            # Load parameters from file if provided
            parameters = {}
            if parameters_file:
                if not parameters_file.exists():
                    console.print(f"[red]❌ Parameters file not found: {parameters_file}[/red]")
                    raise typer.Exit(1)
                
                with open(parameters_file) as f:
                    parameters = json.load(f)
            
            # Build resource requirements
            resource_requirements = {}
            if resource_cpu is not None:
                resource_requirements['cpu_cores'] = resource_cpu
            if resource_memory is not None:
                resource_requirements['memory_mb'] = resource_memory
            if resource_disk is not None:
                resource_requirements['disk_mb'] = resource_disk
            
            # Create task
            task = Task(
                name=name,
                description=description or f"Task: {name}",
                priority=priority,
                parameters=parameters,
                timeout_seconds=timeout,
                max_retries=max_retries,
                resource_requirements=resource_requirements,
                tags=set(tags or []),
                metadata={
                    'submitted_via': 'cli',
                    'submitted_at': datetime.utcnow().isoformat()
                }
            )
            
            # Submit task
            with console.status("[bold blue]Submitting task..."):
                execution_plan = await orchestrator.submit_task(
                    task=task,
                    decomposition_strategy=decomposition_strategy
                )
            
            console.print(f"[green]✓ Task submitted successfully![/green]")
            
            # Display task information
            task_info = {
                "task_id": str(task.id),
                "name": task.name,
                "status": task.status.value,
                "priority": task.priority.value,
                "execution_plan_id": str(execution_plan.id),
                "submitted_at": task.created_at.isoformat(),
                "timeout": f"{timeout}s",
                "max_retries": max_retries
            }
            
            if tags:
                task_info["tags"] = list(tags)
            
            if resource_requirements:
                task_info["resources"] = resource_requirements
            
            # Format output
            formatter = OutputFormatter.create(output_format)
            console.print(formatter.format_dict(task_info, "Task Submitted"))
            
            # Wait or monitor if requested
            if wait or monitor:
                if monitor:
                    task_monitor = TaskMonitor(orchestrator, [task.id])
                    await task_monitor.start_live_monitoring()
                else:
                    await _wait_for_task_completion(orchestrator, task.id)
            else:
                console.print(f"\n[dim]Use 'maos task status {task.id}' to monitor progress[/dim]")
            
        except Exception as e:
            console.print(f"[red]❌ Failed to submit task: {e}[/red]")
            if isinstance(e, (TaskError, MAOSError)):
                console.print(f"[dim]Error code: {getattr(e, 'error_code', 'UNKNOWN')}[/dim]")
            raise typer.Exit(1)
    
    asyncio.run(_submit_task())


@task_app.command(name="list")
def list_tasks(
    status: Optional[List[TaskStatus]] = typer.Option(
        None, "--status", "-s",
        help="Filter by status (can be specified multiple times)"
    ),
    priority: Optional[List[TaskPriority]] = typer.Option(
        None, "--priority", "-p",
        help="Filter by priority (can be specified multiple times)"
    ),
    tags: Optional[List[str]] = typer.Option(
        None, "--tag", "-t",
        help="Filter by tags (can be specified multiple times)"
    ),
    limit: int = typer.Option(
        50, "--limit", "-l",
        help="Maximum number of tasks to display"
    ),
    since: Optional[str] = typer.Option(
        None, "--since",
        help="Show tasks created since (e.g., '1h', '1d', '2024-01-01')"
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f",
        help="Output format (table, json, yaml)"
    ),
    watch: bool = typer.Option(
        False, "--watch", "-w",
        help="Watch for task updates in real-time"
    )
):
    """📋 List tasks with filtering and formatting options
    
    Displays tasks with comprehensive filtering capabilities
    and multiple output formats.
    """
    
    async def _list_tasks():
        try:
            orchestrator = init_orchestrator()
            
            # Convert filters to sets
            status_filter = set(status) if status else None
            priority_filter = set(priority) if priority else None
            tag_filter = set(tags) if tags else None
            
            # Parse since filter
            since_datetime = None
            if since:
                since_datetime = _parse_time_string(since)
            
            if watch:
                await _watch_tasks(orchestrator, status_filter, priority_filter, tag_filter, since_datetime, limit, output_format)
            else:
                await _show_tasks_once(orchestrator, status_filter, priority_filter, tag_filter, since_datetime, limit, output_format)
            
        except Exception as e:
            console.print(f"[red]❌ Failed to list tasks: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_list_tasks())


@task_app.command(name="status")
def task_status(
    task_id: str = typer.Argument(..., help="Task ID"),
    output_format: str = typer.Option(
        "table", "--format", "-f",
        help="Output format (table, json, yaml)"
    ),
    show_subtasks: bool = typer.Option(
        False, "--subtasks",
        help="Show subtask details"
    ),
    show_logs: bool = typer.Option(
        False, "--logs",
        help="Show task execution logs"
    ),
    monitor: bool = typer.Option(
        False, "--monitor", "-m",
        help="Monitor task in real-time"
    )
):
    """🔍 Get detailed status of a specific task
    
    Displays comprehensive task information including
    status, progress, logs, and subtask details.
    """
    
    async def _show_task_status():
        try:
            orchestrator = init_orchestrator()
            
            # Validate task ID
            try:
                task_uuid = UUID(task_id)
            except ValueError:
                console.print(f"[red]❌ Invalid task ID format: {task_id}[/red]")
                raise typer.Exit(1)
            
            if monitor:
                task_monitor = TaskMonitor(orchestrator, [task_uuid])
                await task_monitor.start_live_monitoring(detailed=True)
            else:
                await _show_single_task_status(orchestrator, task_uuid, output_format, show_subtasks, show_logs)
            
        except Exception as e:
            console.print(f"[red]❌ Failed to get task status: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_show_task_status())


@task_app.command(name="cancel")
def cancel_task(
    task_id: str = typer.Argument(..., help="Task ID"),
    reason: str = typer.Option(
        "Cancelled by user", "--reason", "-r",
        help="Cancellation reason"
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Force cancellation without confirmation"
    )
):
    """❌ Cancel a running task
    
    Cancels the specified task with optional reason.
    Requires confirmation unless force is used.
    """
    
    async def _cancel_task():
        try:
            orchestrator = init_orchestrator()
            
            # Validate task ID
            try:
                task_uuid = UUID(task_id)
            except ValueError:
                console.print(f"[red]❌ Invalid task ID format: {task_id}[/red]")
                raise typer.Exit(1)
            
            # Get task for confirmation
            task = await orchestrator.get_task(task_uuid)
            if not task:
                console.print(f"[red]❌ Task not found: {task_id}[/red]")
                raise typer.Exit(1)
            
            # Check if task can be cancelled
            if task.is_terminal():
                console.print(f"[yellow]⚠️  Task is already in terminal state: {task.status.value}[/yellow]")
                return
            
            # Confirmation
            if not force:
                task_info = f"Task: {task.name} (Status: {task.status.value})"
                if not Confirm.ask(f"Cancel {task_info}?", default=False):
                    console.print("[yellow]Cancellation aborted[/yellow]")
                    return
            
            # Cancel task
            with console.status("[bold red]Cancelling task..."):
                success = await orchestrator.cancel_task(task_uuid, reason)
            
            if success:
                console.print(f"[green]✓ Task cancelled successfully[/green]")
                console.print(f"[dim]Reason: {reason}[/dim]")
            else:
                console.print(f"[red]❌ Failed to cancel task[/red]")
                raise typer.Exit(1)
            
        except Exception as e:
            console.print(f"[red]❌ Error cancelling task: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_cancel_task())


@task_app.command(name="retry")
def retry_task(
    task_id: str = typer.Argument(..., help="Task ID"),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Force retry without confirmation"
    )
):
    """🔄 Retry a failed task
    
    Retries the specified failed task if retry limit allows.
    """
    
    async def _retry_task():
        try:
            orchestrator = init_orchestrator()
            
            # Validate task ID
            try:
                task_uuid = UUID(task_id)
            except ValueError:
                console.print(f"[red]❌ Invalid task ID format: {task_id}[/red]")
                raise typer.Exit(1)
            
            # Get task for validation
            task = await orchestrator.get_task(task_uuid)
            if not task:
                console.print(f"[red]❌ Task not found: {task_id}[/red]")
                raise typer.Exit(1)
            
            # Check if task can be retried
            if not task.can_retry():
                if task.status != TaskStatus.FAILED:
                    console.print(f"[yellow]⚠️  Task is not in failed state: {task.status.value}[/yellow]")
                else:
                    console.print(f"[yellow]⚠️  Task has reached maximum retry limit: {task.retry_count}/{task.max_retries}[/yellow]")
                return
            
            # Confirmation
            if not force:
                retry_info = f"Task: {task.name} (Retry {task.retry_count + 1}/{task.max_retries})"
                if not Confirm.ask(f"Retry {retry_info}?", default=True):
                    console.print("[yellow]Retry aborted[/yellow]")
                    return
            
            # Retry task
            with console.status("[bold blue]Retrying task..."):
                success = await orchestrator.retry_task(task_uuid)
            
            if success:
                console.print(f"[green]✓ Task retry initiated[/green]")
                console.print(f"[dim]Retry count: {task.retry_count + 1}/{task.max_retries}[/dim]")
            else:
                console.print(f"[red]❌ Failed to retry task[/red]")
                raise typer.Exit(1)
            
        except Exception as e:
            console.print(f"[red]❌ Error retrying task: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_retry_task())


@task_app.command(name="results")
def get_task_results(
    task_id: str = typer.Argument(..., help="Task ID"),
    output_format: str = typer.Option(
        "json", "--format", "-f",
        help="Output format (json, yaml, text)"
    ),
    save_to: Optional[Path] = typer.Option(
        None, "--save", "-s",
        help="Save results to file"
    )
):
    """📋 Get results from a completed task
    
    Retrieves and displays the results of a completed task
    with multiple output formats and save options.
    """
    
    async def _get_results():
        try:
            orchestrator = init_orchestrator()
            
            # Validate task ID
            try:
                task_uuid = UUID(task_id)
            except ValueError:
                console.print(f"[red]❌ Invalid task ID format: {task_id}[/red]")
                raise typer.Exit(1)
            
            # Get task and check status
            task = await orchestrator.get_task(task_uuid)
            if not task:
                console.print(f"[red]❌ Task not found: {task_id}[/red]")
                raise typer.Exit(1)
            
            if task.status != TaskStatus.COMPLETED:
                console.print(f"[yellow]⚠️  Task is not completed (Status: {task.status.value})[/yellow]")
                if task.status == TaskStatus.FAILED and task.error:
                    console.print(f"[red]Error: {task.error}[/red]")
                return
            
            # Get results
            results = await orchestrator.get_task_results(task_uuid)
            if results is None:
                console.print(f"[yellow]⚠️  No results available for task {task_id}[/yellow]")
                return
            
            # Format and display results
            if output_format == "json":
                formatted_results = json.dumps(results, indent=2, default=str)
                console.print(JSON(formatted_results))
            elif output_format == "yaml":
                import yaml
                formatted_results = yaml.dump(results, default_flow_style=False)
                console.print(Syntax(formatted_results, "yaml"))
            else:
                # Text format
                console.print(Panel(str(results), title=f"Results for Task {task.name}", border_style="green"))
            
            # Save to file if requested
            if save_to:
                save_to.parent.mkdir(parents=True, exist_ok=True)
                
                if output_format == "json":
                    with open(save_to, 'w') as f:
                        json.dump(results, f, indent=2, default=str)
                elif output_format == "yaml":
                    import yaml
                    with open(save_to, 'w') as f:
                        yaml.dump(results, f, default_flow_style=False)
                else:
                    with open(save_to, 'w') as f:
                        f.write(str(results))
                
                console.print(f"[green]✓ Results saved to {save_to}[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Error getting task results: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_get_results())


@task_app.command(name="export")
def export_tasks(
    output_file: Path = typer.Argument(..., help="Output file path"),
    format_type: str = typer.Option(
        "json", "--format", "-f",
        help="Export format (json, csv, yaml)"
    ),
    status_filter: Optional[List[TaskStatus]] = typer.Option(
        None, "--status",
        help="Filter by status"
    ),
    since: Optional[str] = typer.Option(
        None, "--since",
        help="Export tasks since (e.g., '1h', '1d', '2024-01-01')"
    ),
    include_results: bool = typer.Option(
        False, "--include-results",
        help="Include task results in export"
    )
):
    """💾 Export tasks to file
    
    Exports task data to various formats for analysis or archival.
    """
    
    async def _export_tasks():
        try:
            orchestrator = init_orchestrator()
            
            # Get tasks with filters
            status_filter_set = set(status_filter) if status_filter else None
            since_datetime = _parse_time_string(since) if since else None
            
            tasks_data = await _get_filtered_tasks(
                orchestrator, status_filter_set, None, None, since_datetime, None
            )
            
            # Include results if requested
            if include_results:
                for task_data in tasks_data:
                    if task_data['status'] == 'completed':
                        task_uuid = UUID(task_data['id'])
                        results = await orchestrator.get_task_results(task_uuid)
                        task_data['results'] = results
            
            # Export to file
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format_type == "json":
                with open(output_file, 'w') as f:
                    json.dump(tasks_data, f, indent=2, default=str)
            elif format_type == "yaml":
                import yaml
                with open(output_file, 'w') as f:
                    yaml.dump(tasks_data, f, default_flow_style=False)
            elif format_type == "csv":
                import csv
                if tasks_data:
                    fieldnames = tasks_data[0].keys()
                    with open(output_file, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(tasks_data)
            else:
                console.print(f"[red]❌ Unsupported format: {format_type}[/red]")
                raise typer.Exit(1)
            
            console.print(f"[green]✓ Exported {len(tasks_data)} tasks to {output_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Export failed: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_export_tasks())


# Helper functions

async def _wait_for_task_completion(orchestrator, task_id: UUID):
    """Wait for task completion with progress indication."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task_progress = progress.add_task("Waiting for task completion...", total=None)
        
        while True:
            task = await orchestrator.get_task(task_id)
            if not task:
                progress.update(task_progress, description="[red]Task not found[/red]")
                break
            
            if task.is_terminal():
                status_color = "green" if task.status == TaskStatus.COMPLETED else "red"
                progress.update(task_progress, description=f"[{status_color}]Task {task.status.value}[/{status_color}]")
                break
            
            progress.update(task_progress, description=f"Task status: {task.status.value}")
            await asyncio.sleep(2)


async def _show_tasks_once(orchestrator, status_filter, priority_filter, tag_filter, since_datetime, limit, output_format):
    """Show tasks once with filtering."""
    tasks_data = await _get_filtered_tasks(
        orchestrator, status_filter, priority_filter, tag_filter, since_datetime, limit
    )
    
    if not tasks_data:
        console.print("[yellow]No tasks found matching criteria[/yellow]")
        return
    
    formatter = OutputFormatter.create(output_format)
    console.print(formatter.format_list(tasks_data, "Tasks"))
    console.print(f"\n[dim]Showing {len(tasks_data)} tasks[/dim]")


async def _watch_tasks(orchestrator, status_filter, priority_filter, tag_filter, since_datetime, limit, output_format):
    """Watch tasks with real-time updates."""
    with Live(console=console, refresh_per_second=2) as live:
        while True:
            try:
                tasks_data = await _get_filtered_tasks(
                    orchestrator, status_filter, priority_filter, tag_filter, since_datetime, limit
                )
                
                if tasks_data:
                    formatter = TableFormatter()
                    table = formatter._create_table(tasks_data, "Tasks")
                    live.update(Panel(table, title=f"🔄 Live Tasks ({len(tasks_data)})", border_style="blue"))
                else:
                    live.update(Panel("[yellow]No tasks found[/yellow]", title="🔄 Live Tasks", border_style="blue"))
                
                await asyncio.sleep(2)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                live.update(Panel(f"[red]Error: {e}[/red]", title="🔄 Live Tasks", border_style="red"))
                await asyncio.sleep(5)


async def _show_single_task_status(orchestrator, task_id: UUID, output_format: str, show_subtasks: bool, show_logs: bool):
    """Show detailed status for a single task."""
    task = await orchestrator.get_task(task_id)
    if not task:
        console.print(f"[red]❌ Task not found: {task_id}[/red]")
        raise typer.Exit(1)
    
    # Prepare task data
    task_data = {
        "id": str(task.id),
        "name": task.name,
        "description": task.description,
        "status": task.status.value,
        "priority": task.priority.value,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "timeout_seconds": task.timeout_seconds,
        "retry_count": task.retry_count,
        "max_retries": task.max_retries,
        "resource_requirements": task.resource_requirements,
        "tags": list(task.tags),
        "metadata": task.metadata
    }
    
    if task.error:
        task_data["error"] = task.error
    
    if task.result and task.status == TaskStatus.COMPLETED:
        task_data["result"] = str(task.result)[:500] + "..." if len(str(task.result)) > 500 else task.result
    
    # Format and display
    formatter = OutputFormatter.create(output_format)
    console.print(formatter.format_dict(task_data, f"Task Status: {task.name}"))


async def _get_filtered_tasks(orchestrator, status_filter, priority_filter, tag_filter, since_datetime, limit):
    """Get tasks with applied filters."""
    # This would need to be implemented in the orchestrator
    # For now, get all tasks and filter client-side
    all_tasks = await orchestrator.state_manager.get_objects('tasks')
    
    filtered_tasks = []
    for task in all_tasks:
        # Apply filters
        if status_filter and task.status not in status_filter:
            continue
        
        if priority_filter and task.priority not in priority_filter:
            continue
        
        if tag_filter and not any(tag in task.tags for tag in tag_filter):
            continue
        
        if since_datetime and task.created_at < since_datetime:
            continue
        
        filtered_tasks.append({
            "id": str(task.id),
            "name": task.name,
            "status": task.status.value,
            "priority": task.priority.value,
            "created_at": task.created_at.isoformat(),
            "retry_count": task.retry_count,
            "tags": list(task.tags)
        })
        
        if limit and len(filtered_tasks) >= limit:
            break
    
    return filtered_tasks


def _parse_time_string(time_str: str) -> datetime:
    """Parse time string to datetime."""
    if time_str.endswith('h'):
        hours = int(time_str[:-1])
        return datetime.utcnow() - timedelta(hours=hours)
    elif time_str.endswith('d'):
        days = int(time_str[:-1])
        return datetime.utcnow() - timedelta(days=days)
    else:
        # Try parsing as ISO date
        return datetime.fromisoformat(time_str)