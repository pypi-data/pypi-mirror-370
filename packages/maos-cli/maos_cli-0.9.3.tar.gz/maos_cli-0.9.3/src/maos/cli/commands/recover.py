"""
MAOS CLI Recovery Commands

Checkpoint management and system recovery operations with
comprehensive backup and restoration capabilities.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from uuid import UUID

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.tree import Tree

from ...models.checkpoint import Checkpoint, CheckpointType
from ...utils.exceptions import MAOSError
from ..formatters import OutputFormatter, format_duration, format_size, format_timestamp
from .._main import _orchestrator, init_orchestrator

console = Console()
recover_app = typer.Typer(help="🔄 Recovery and checkpoint operations")


@recover_app.command(name="checkpoint")
def create_checkpoint(
    name: Optional[str] = typer.Option(
        None, "--name", "-n",
        help="Checkpoint name (auto-generated if not provided)"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", "-d",
        help="Checkpoint description"
    ),
    include_data: bool = typer.Option(
        True, "--include-data/--no-data",
        help="Include runtime data in checkpoint"
    ),
    compress: bool = typer.Option(
        True, "--compress/--no-compress",
        help="Compress checkpoint data"
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f",
        help="Output format (table, json, yaml)"
    )
):
    """💾 Create a system checkpoint
    
    Creates a comprehensive checkpoint of the current system state
    including configuration, active tasks, and agent states.
    """
    
    async def _create_checkpoint():
        try:
            orchestrator = init_orchestrator()
            
            # Generate checkpoint name if not provided
            if not name:
                checkpoint_name = f"checkpoint-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
            else:
                checkpoint_name = name
            
            console.print(f"[bold blue]Creating checkpoint: {checkpoint_name}[/bold blue]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                
                checkpoint_task = progress.add_task(
                    "Creating checkpoint...", 
                    total=100
                )
                
                # Create checkpoint with progress updates
                progress.update(checkpoint_task, advance=20, description="Collecting system state...")
                
                checkpoint_id = await orchestrator.create_checkpoint(checkpoint_name)
                
                progress.update(checkpoint_task, advance=50, description="Saving checkpoint data...")
                
                # Get checkpoint details
                checkpoint = await orchestrator.state_manager.get_object('checkpoints', checkpoint_id)
                
                progress.update(checkpoint_task, advance=30, description="Finalizing checkpoint...")
                
                if not checkpoint:
                    console.print(f"[red]❌ Failed to retrieve checkpoint details[/red]")
                    raise typer.Exit(1)
                
                progress.update(checkpoint_task, advance=0, description="Checkpoint created successfully!")
            
            console.print(f"[green]✅ Checkpoint created successfully![/green]")
            
            # Display checkpoint information
            checkpoint_info = {
                "id": str(checkpoint.id),
                "name": checkpoint.name,
                "type": checkpoint.type.value,
                "created_at": checkpoint.created_at.isoformat(),
                "size_bytes": checkpoint.size_bytes,
                "size_formatted": format_size(checkpoint.size_bytes) if checkpoint.size_bytes else "Unknown",
                "description": description or "System checkpoint",
                "compressed": compress,
                "includes_data": include_data
            }
            
            formatter = OutputFormatter.create(output_format)
            console.print(formatter.format_dict(checkpoint_info, "Checkpoint Created"))
            
        except Exception as e:
            console.print(f"[red]❌ Failed to create checkpoint: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_create_checkpoint())


@recover_app.command(name="list")
def list_checkpoints(
    limit: int = typer.Option(
        20, "--limit", "-l",
        help="Maximum number of checkpoints to show"
    ),
    checkpoint_type: Optional[str] = typer.Option(
        None, "--type", "-t",
        help="Filter by checkpoint type"
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f",
        help="Output format (table, json, yaml, tree)"
    ),
    show_details: bool = typer.Option(
        False, "--details", "-d",
        help="Show detailed checkpoint information"
    )
):
    """📊 List available checkpoints
    
    Displays all available system checkpoints with filtering
    and sorting options.
    """
    
    async def _list_checkpoints():
        try:
            orchestrator = init_orchestrator()
            
            with console.status("[bold blue]Retrieving checkpoints..."):
                checkpoints = await orchestrator.list_checkpoints()
            
            if not checkpoints:
                console.print("[yellow]⚠️  No checkpoints found[/yellow]")
                return
            
            # Filter by type if specified
            if checkpoint_type:
                checkpoints = [
                    cp for cp in checkpoints 
                    if cp.get('type', '').lower() == checkpoint_type.lower()
                ]
                
                if not checkpoints:
                    console.print(f"[yellow]⚠️  No checkpoints found of type: {checkpoint_type}[/yellow]")
                    return
            
            # Limit results
            if limit < len(checkpoints):
                checkpoints = checkpoints[:limit]
                console.print(f"[dim]Showing {limit} of {len(checkpoints)} checkpoints[/dim]\n")
            
            # Format and display
            if output_format == "tree":
                await _show_checkpoints_tree(checkpoints, show_details)
            elif show_details:
                await _show_checkpoints_detailed(checkpoints, output_format)
            else:
                await _show_checkpoints_table(checkpoints, output_format)
                
        except Exception as e:
            console.print(f"[red]❌ Failed to list checkpoints: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_list_checkpoints())


@recover_app.command(name="restore")
def restore_checkpoint(
    checkpoint_id: str = typer.Argument(..., help="Checkpoint ID to restore"),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Force restore without confirmation"
    ),
    backup_current: bool = typer.Option(
        True, "--backup/--no-backup",
        help="Create backup of current state before restore"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run",
        help="Show what would be restored without actually doing it"
    )
):
    """🔄 Restore system from checkpoint
    
    Restores the system state from a previously created checkpoint
    with optional backup of current state.
    """
    
    async def _restore_checkpoint():
        try:
            orchestrator = init_orchestrator()
            
            # Validate checkpoint ID
            try:
                checkpoint_uuid = UUID(checkpoint_id)
            except ValueError:
                console.print(f"[red]❌ Invalid checkpoint ID format: {checkpoint_id}[/red]")
                raise typer.Exit(1)
            
            # Get checkpoint details
            checkpoint = await orchestrator.state_manager.get_object('checkpoints', checkpoint_uuid)
            if not checkpoint:
                console.print(f"[red]❌ Checkpoint not found: {checkpoint_id}[/red]")
                raise typer.Exit(1)
            
            # Display checkpoint information
            console.print(f"[bold blue]Checkpoint Information:[/bold blue]")
            console.print(f"  Name: {checkpoint.name}")
            console.print(f"  Created: {format_timestamp(checkpoint.created_at)}")
            console.print(f"  Type: {checkpoint.type.value}")
            console.print(f"  Size: {format_size(checkpoint.size_bytes) if checkpoint.size_bytes else 'Unknown'}")
            
            if dry_run:
                console.print(f"\n[yellow]🔍 DRY RUN: Would restore from checkpoint {checkpoint.name}[/yellow]")
                console.print("[dim]No actual changes will be made[/dim]")
                return
            
            # Confirmation
            if not force:
                if not Confirm.ask(
                    f"\nRestore system state from checkpoint '{checkpoint.name}'?", 
                    default=False
                ):
                    console.print("[yellow]Restore cancelled[/yellow]")
                    return
            
            # Backup current state if requested
            backup_id = None
            if backup_current:
                console.print("[bold blue]Creating backup of current state...[/bold blue]")
                try:
                    backup_name = f"pre-restore-backup-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
                    backup_id = await orchestrator.create_checkpoint(backup_name)
                    console.print(f"[green]✅ Backup created: {backup_name}[/green]")
                except Exception as e:
                    console.print(f"[red]⚠️  Backup failed: {e}[/red]")
                    if not Confirm.ask("Continue with restore anyway?", default=False):
                        console.print("[yellow]Restore cancelled[/yellow]")
                        return
            
            # Perform restore
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console
            ) as progress:
                
                restore_task = progress.add_task(
                    "Restoring from checkpoint...", 
                    total=None
                )
                
                success = await orchestrator.restore_checkpoint(checkpoint_uuid)
                
                progress.update(
                    restore_task, 
                    description="Restore completed!" if success else "Restore failed!"
                )
            
            if success:
                console.print(f"[green]✅ System successfully restored from checkpoint '{checkpoint.name}'[/green]")
                if backup_id:
                    console.print(f"[dim]Previous state backed up as: {str(backup_id)[:8]}...[/dim]")
            else:
                console.print(f"[red]❌ Failed to restore from checkpoint[/red]")
                if backup_id:
                    console.print(f"[yellow]Current state backup available: {str(backup_id)[:8]}...[/yellow]")
                raise typer.Exit(1)
                
        except Exception as e:
            console.print(f"[red]❌ Restore operation failed: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_restore_checkpoint())


@recover_app.command(name="delete")
def delete_checkpoint(
    checkpoint_id: str = typer.Argument(..., help="Checkpoint ID to delete"),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Force delete without confirmation"
    )
):
    """🗑️ Delete a checkpoint
    
    Permanently deletes a checkpoint and frees up storage space.
    """
    
    async def _delete_checkpoint():
        try:
            orchestrator = init_orchestrator()
            
            # Validate checkpoint ID
            try:
                checkpoint_uuid = UUID(checkpoint_id)
            except ValueError:
                console.print(f"[red]❌ Invalid checkpoint ID format: {checkpoint_id}[/red]")
                raise typer.Exit(1)
            
            # Get checkpoint details for confirmation
            checkpoint = await orchestrator.state_manager.get_object('checkpoints', checkpoint_uuid)
            if not checkpoint:
                console.print(f"[red]❌ Checkpoint not found: {checkpoint_id}[/red]")
                raise typer.Exit(1)
            
            # Confirmation
            if not force:
                checkpoint_info = f"'{checkpoint.name}' (Created: {format_timestamp(checkpoint.created_at, relative=False)})"
                if not Confirm.ask(
                    f"Permanently delete checkpoint {checkpoint_info}?", 
                    default=False
                ):
                    console.print("[yellow]Deletion cancelled[/yellow]")
                    return
            
            # Delete checkpoint
            with console.status("[bold red]Deleting checkpoint..."):
                success = await orchestrator.state_manager.remove_object('checkpoints', checkpoint_uuid)
            
            if success:
                console.print(f"[green]✅ Checkpoint '{checkpoint.name}' deleted successfully[/green]")
            else:
                console.print(f"[red]❌ Failed to delete checkpoint[/red]")
                raise typer.Exit(1)
                
        except Exception as e:
            console.print(f"[red]❌ Delete operation failed: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_delete_checkpoint())


@recover_app.command(name="info")
def checkpoint_info(
    checkpoint_id: str = typer.Argument(..., help="Checkpoint ID"),
    output_format: str = typer.Option(
        "table", "--format", "-f",
        help="Output format (table, json, yaml)"
    ),
    show_content: bool = typer.Option(
        False, "--content",
        help="Show checkpoint content summary"
    )
):
    """🔍 Show detailed checkpoint information
    
    Displays comprehensive information about a specific checkpoint
    including metadata, size, and optional content summary.
    """
    
    async def _show_checkpoint_info():
        try:
            orchestrator = init_orchestrator()
            
            # Validate checkpoint ID
            try:
                checkpoint_uuid = UUID(checkpoint_id)
            except ValueError:
                console.print(f"[red]❌ Invalid checkpoint ID format: {checkpoint_id}[/red]")
                raise typer.Exit(1)
            
            # Get checkpoint
            checkpoint = await orchestrator.state_manager.get_object('checkpoints', checkpoint_uuid)
            if not checkpoint:
                console.print(f"[red]❌ Checkpoint not found: {checkpoint_id}[/red]")
                raise typer.Exit(1)
            
            # Prepare checkpoint information
            checkpoint_info = {
                "id": str(checkpoint.id),
                "name": checkpoint.name,
                "type": checkpoint.type.value,
                "created_at": checkpoint.created_at.isoformat(),
                "created_at_formatted": format_timestamp(checkpoint.created_at),
                "size_bytes": checkpoint.size_bytes,
                "size_formatted": format_size(checkpoint.size_bytes) if checkpoint.size_bytes else "Unknown"
            }
            
            # Add content summary if requested
            if show_content and hasattr(checkpoint, 'state_data') and checkpoint.state_data:
                try:
                    content_summary = {
                        "tasks_count": len(checkpoint.state_data.get('tasks', [])),
                        "agents_count": len(checkpoint.state_data.get('agents', [])),
                        "resources_count": len(checkpoint.state_data.get('resources', [])),
                        "execution_plans_count": len(checkpoint.state_data.get('execution_plans', []))
                    }
                    checkpoint_info["content_summary"] = content_summary
                except Exception as e:
                    checkpoint_info["content_error"] = str(e)
            
            # Format and display
            formatter = OutputFormatter.create(output_format)
            console.print(formatter.format_dict(checkpoint_info, f"Checkpoint: {checkpoint.name}"))
            
        except Exception as e:
            console.print(f"[red]❌ Failed to get checkpoint info: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_show_checkpoint_info())


@recover_app.command(name="export")
def export_checkpoint(
    checkpoint_id: str = typer.Argument(..., help="Checkpoint ID to export"),
    output_file: Path = typer.Argument(..., help="Output file path"),
    format_type: str = typer.Option(
        "json", "--format", "-f",
        help="Export format (json, yaml)"
    ),
    compress: bool = typer.Option(
        True, "--compress/--no-compress",
        help="Compress exported data"
    )
):
    """💾 Export checkpoint to file
    
    Exports a checkpoint to a file for external backup or analysis.
    """
    
    async def _export_checkpoint():
        try:
            orchestrator = init_orchestrator()
            
            # Validate checkpoint ID
            try:
                checkpoint_uuid = UUID(checkpoint_id)
            except ValueError:
                console.print(f"[red]❌ Invalid checkpoint ID format: {checkpoint_id}[/red]")
                raise typer.Exit(1)
            
            # Get checkpoint
            checkpoint = await orchestrator.state_manager.get_object('checkpoints', checkpoint_uuid)
            if not checkpoint:
                console.print(f"[red]❌ Checkpoint not found: {checkpoint_id}[/red]")
                raise typer.Exit(1)
            
            # Prepare export data
            export_data = {
                "checkpoint_id": str(checkpoint.id),
                "name": checkpoint.name,
                "type": checkpoint.type.value,
                "created_at": checkpoint.created_at.isoformat(),
                "size_bytes": checkpoint.size_bytes,
                "exported_at": datetime.utcnow().isoformat(),
                "format": format_type,
                "compressed": compress
            }
            
            # Add state data if available
            if hasattr(checkpoint, 'state_data') and checkpoint.state_data:
                export_data["state_data"] = checkpoint.state_data
            
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Export with progress
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                export_task = progress.add_task(
                    "Exporting checkpoint...", 
                    total=None
                )
                
                # Write to file
                if format_type == "json":
                    with open(output_file, 'w') as f:
                        json.dump(export_data, f, indent=2, default=str)
                elif format_type == "yaml":
                    import yaml
                    with open(output_file, 'w') as f:
                        yaml.dump(export_data, f, default_flow_style=False)
                else:
                    console.print(f"[red]❌ Unsupported format: {format_type}[/red]")
                    raise typer.Exit(1)
                
                progress.update(export_task, description="Export completed!")
            
            file_size = output_file.stat().st_size
            console.print(f"[green]✅ Checkpoint exported successfully![/green]")
            console.print(f"[dim]File: {output_file}[/dim]")
            console.print(f"[dim]Size: {format_size(file_size)}[/dim]")
            
        except Exception as e:
            console.print(f"[red]❌ Export failed: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_export_checkpoint())


@recover_app.command(name="cleanup")
def cleanup_checkpoints(
    keep: int = typer.Option(
        10, "--keep", "-k",
        help="Number of recent checkpoints to keep"
    ),
    older_than_days: Optional[int] = typer.Option(
        None, "--older-than",
        help="Delete checkpoints older than N days"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run",
        help="Show what would be deleted without actually deleting"
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Force cleanup without confirmation"
    )
):
    """🧹 Clean up old checkpoints
    
    Removes old checkpoints to free up storage space while
    keeping recent checkpoints for recovery purposes.
    """
    
    async def _cleanup_checkpoints():
        try:
            orchestrator = init_orchestrator()
            
            # Get all checkpoints
            all_checkpoints = await orchestrator.list_checkpoints()
            
            if not all_checkpoints:
                console.print("[yellow]⚠️  No checkpoints found[/yellow]")
                return
            
            # Determine which checkpoints to delete
            checkpoints_to_delete = []
            
            if older_than_days:
                cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
                checkpoints_to_delete = [
                    cp for cp in all_checkpoints
                    if datetime.fromisoformat(cp['created_at']) < cutoff_date
                ]
            else:
                # Keep only the most recent 'keep' checkpoints
                if len(all_checkpoints) > keep:
                    checkpoints_to_delete = all_checkpoints[keep:]
            
            if not checkpoints_to_delete:
                console.print("[green]✅ No checkpoints need cleanup[/green]")
                return
            
            # Calculate space to be freed
            total_size = sum(
                cp.get('size_bytes', 0) for cp in checkpoints_to_delete
            )
            
            console.print(f"[bold blue]Cleanup Summary:[/bold blue]")
            console.print(f"  Total checkpoints: {len(all_checkpoints)}")
            console.print(f"  To delete: {len(checkpoints_to_delete)}")
            console.print(f"  Space to free: {format_size(total_size)}")
            console.print(f"  Remaining: {len(all_checkpoints) - len(checkpoints_to_delete)}")
            
            if dry_run:
                console.print(f"\n[yellow]🔍 DRY RUN: Would delete {len(checkpoints_to_delete)} checkpoints[/yellow]")
                
                # Show which checkpoints would be deleted
                if len(checkpoints_to_delete) <= 10:
                    console.print("\n[dim]Checkpoints that would be deleted:[/dim]")
                    for cp in checkpoints_to_delete:
                        console.print(f"  • {cp['name']} ({format_timestamp(datetime.fromisoformat(cp['created_at']))})")                
                return
            
            # Confirmation
            if not force:
                if not Confirm.ask(
                    f"\nDelete {len(checkpoints_to_delete)} checkpoints and free {format_size(total_size)}?",
                    default=False
                ):
                    console.print("[yellow]Cleanup cancelled[/yellow]")
                    return
            
            # Perform cleanup
            deleted_count = 0
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                
                cleanup_task = progress.add_task(
                    "Cleaning up checkpoints...", 
                    total=len(checkpoints_to_delete)
                )
                
                for cp in checkpoints_to_delete:
                    try:
                        checkpoint_uuid = UUID(cp['id'])
                        success = await orchestrator.state_manager.remove_object(
                            'checkpoints', checkpoint_uuid
                        )
                        
                        if success:
                            deleted_count += 1
                        
                        progress.update(
                            cleanup_task, 
                            advance=1,
                            description=f"Deleted {deleted_count}/{len(checkpoints_to_delete)} checkpoints"
                        )
                        
                    except Exception as e:
                        console.print(f"[red]Failed to delete checkpoint {cp['name']}: {e}[/red]")
            
            console.print(f"[green]✅ Cleanup completed![/green]")
            console.print(f"[dim]Deleted {deleted_count} checkpoints[/dim]")
            console.print(f"[dim]Freed approximately {format_size(total_size)}[/dim]")
            
        except Exception as e:
            console.print(f"[red]❌ Cleanup failed: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_cleanup_checkpoints())


# Helper functions

async def _show_checkpoints_tree(checkpoints: List[Dict], show_details: bool):
    """Show checkpoints in tree format."""
    tree = Tree("[bold blue]Checkpoints[/bold blue]")
    
    # Group by type
    by_type = {}
    for cp in checkpoints:
        cp_type = cp.get('type', 'unknown')
        if cp_type not in by_type:
            by_type[cp_type] = []
        by_type[cp_type].append(cp)
    
    for cp_type, type_checkpoints in by_type.items():
        type_node = tree.add(f"[cyan]{cp_type.title()}[/cyan] ({len(type_checkpoints)})")
        
        for cp in type_checkpoints:
            checkpoint_label = f"[green]{cp['name']}[/green]"
            if show_details:
                created_at = datetime.fromisoformat(cp['created_at'])
                size_str = format_size(cp.get('size_bytes', 0)) if cp.get('size_bytes') else "Unknown"
                checkpoint_label += f" - {format_timestamp(created_at)} ({size_str})"
            
            cp_node = type_node.add(checkpoint_label)
            
            if show_details:
                cp_node.add(f"[dim]ID: {cp['id'][:8]}...[/dim]")
    
    console.print(tree)


async def _show_checkpoints_detailed(checkpoints: List[Dict], output_format: str):
    """Show checkpoints in detailed format."""
    formatter = OutputFormatter.create(output_format)
    
    for i, cp in enumerate(checkpoints):
        if i > 0:
            console.print("")
        
        checkpoint_details = dict(cp)
        if 'created_at' in checkpoint_details:
            created_at = datetime.fromisoformat(checkpoint_details['created_at'])
            checkpoint_details['created_at_formatted'] = format_timestamp(created_at)
        
        if checkpoint_details.get('size_bytes'):
            checkpoint_details['size_formatted'] = format_size(checkpoint_details['size_bytes'])
        
        console.print(formatter.format_dict(checkpoint_details, f"Checkpoint: {cp['name']}"))


async def _show_checkpoints_table(checkpoints: List[Dict], output_format: str):
    """Show checkpoints in table format."""
    if output_format == "table":
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Name", style="green", width=25)
        table.add_column("ID", style="cyan", width=10)
        table.add_column("Type", style="yellow", width=15)
        table.add_column("Created", style="blue", width=20)
        table.add_column("Size", style="white", width=10)
        
        for cp in checkpoints:
            created_at = datetime.fromisoformat(cp['created_at'])
            size_str = format_size(cp.get('size_bytes', 0)) if cp.get('size_bytes') else "Unknown"
            
            table.add_row(
                cp['name'][:23] + "..." if len(cp['name']) > 23 else cp['name'],
                cp['id'][:8] + "...",
                cp.get('type', 'unknown').title(),
                format_timestamp(created_at, relative=False),
                size_str
            )
        
        console.print(table)
    else:
        formatter = OutputFormatter.create(output_format)
        console.print(formatter.format_list(checkpoints, "Checkpoints"))