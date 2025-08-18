#!/usr/bin/env python3
"""
MAOS Command Line Interface

Comprehensive CLI for Multi-Agent Orchestration System with rich console output,
real-time monitoring, and advanced features for system management.
"""

import asyncio
import json
import os
import signal
import sys
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from uuid import UUID

import typer
import yaml
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    Progress, SpinnerColumn, TextColumn, BarColumn, 
    TaskProgressColumn, TimeRemainingColumn
)
from rich.table import Table
from rich.tree import Tree
from rich.text import Text
from rich.layout import Layout
from rich.align import Align
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from rich import box

from ..core.orchestrator import Orchestrator
from ..models.task import Task, TaskStatus, TaskPriority
from ..models.agent import Agent, AgentCapability
from ..models.resource import Resource, ResourceType
from ..utils.exceptions import MAOSError, TaskError, AgentError, ResourceError
from ..utils.logging_config import setup_logging, MAOSLogger
from .config import CLIConfig, load_config, save_config
from .formatters import OutputFormatter, TableFormatter, JSONFormatter
from .monitoring import SystemMonitor, TaskMonitor
from .interactive import InteractiveShell
from .natural_language_v7 import NaturalLanguageProcessorV7
from .completion import setup_completion
from .commands.task import task_app
from .commands.agent import agent_app
from .commands.status import status_app
from .commands.recover import recover_app
from .commands.config import config_app

# Initialize Rich console
console = Console()
app = typer.Typer(
    name="maos",
    help="🤖 Multi-Agent Orchestration System - Command Line Interface",
    rich_markup_mode="rich",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    pretty_exceptions_show_locals=False
)

# Global orchestrator instance
_orchestrator: Optional[Orchestrator] = None
_config: Optional[CLIConfig] = None
_logger: Optional[MAOSLogger] = None

# Import command apps (they're already defined in their modules)

app.add_typer(task_app, name="task")
app.add_typer(agent_app, name="agent")
app.add_typer(status_app, name="status")
app.add_typer(recover_app, name="recover")
app.add_typer(config_app, name="config")


def init_orchestrator(config_path: Optional[str] = None) -> Orchestrator:
    """Initialize orchestrator with configuration."""
    global _orchestrator, _config, _logger
    
    if _orchestrator is not None:
        return _orchestrator
    
    # Load configuration
    _config = load_config(config_path)
    
    # Setup logging
    if _config.logging.enabled:
        setup_logging(
            level=_config.logging.level,
            log_file=_config.logging.file,
            structured=_config.logging.structured
        )
    
    _logger = MAOSLogger("cli")
    
    # Initialize orchestrator
    orchestrator_config = {
        "storage_directory": str(_config.storage.directory),
        "state_manager": {
            "auto_checkpoint_interval": _config.system.checkpoint_interval,
            "max_snapshots": _config.system.max_checkpoints
        },
        "message_bus": {} if not _config.redis.enabled else {
            "redis_url": _config.redis.url
        },
        "agent_manager": {
            "max_agents": _config.system.max_agents,
            "heartbeat_timeout": _config.system.agent_timeout
        },
        "resource_allocator": {}
    }
    
    _orchestrator = Orchestrator(component_config=orchestrator_config)
    
    return _orchestrator


def shutdown_orchestrator():
    """Gracefully shutdown orchestrator."""
    global _orchestrator
    
    if _orchestrator:
        asyncio.create_task(_orchestrator.shutdown())
        _orchestrator = None


def signal_handler(signum, frame):
    """Handle interrupt signals."""
    console.print("\n[yellow]Received shutdown signal. Cleaning up...[/yellow]")
    shutdown_orchestrator()
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


@app.callback()
def main(
    config_file: Optional[str] = typer.Option(
        None, "--config", "-c",
        help="Path to configuration file"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Enable verbose output"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q",
        help="Suppress non-essential output"
    ),
    format_output: str = typer.Option(
        "table", "--format", "-f",
        help="Output format (table, json, yaml)"
    )
):
    """🤖 Multi-Agent Orchestration System CLI
    
    MAOS provides a comprehensive command-line interface for managing
    distributed agent orchestration with real-time monitoring and
    advanced recovery capabilities.
    """
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")
    
    # Set global configuration using click context
    try:
        import click
        ctx = click.get_current_context()
        ctx.ensure_object(dict)
        ctx.obj.update({
            "config_file": config_file,
            "verbose": verbose,
            "quiet": quiet,
            "format": format_output
        })
    except RuntimeError:
        # No context available yet
        pass


@app.command(name="start")
def start_system(
    config_file: Optional[str] = typer.Option(
        None, "--config", "-c",
        help="Path to configuration file"
    ),
    max_agents: int = typer.Option(
        10, "--max-agents", "-a",
        help="Maximum number of agents"
    ),
    storage_dir: Optional[str] = typer.Option(
        None, "--storage-dir", "-s",
        help="Storage directory path"
    ),
    daemon: bool = typer.Option(
        False, "--daemon", "-d",
        help="Run as daemon process"
    ),
    monitor: bool = typer.Option(
        True, "--monitor/--no-monitor",
        help="Enable real-time monitoring"
    )
):
    """🚀 Start the MAOS orchestration system
    
    Initializes and starts the orchestration system with configurable
    parameters. Supports daemon mode and real-time monitoring.
    """
    
    async def _start_system():
        try:
            with console.status("[bold blue]Starting MAOS orchestration system..."):
                orchestrator = init_orchestrator(config_file)
                
                # Apply command-line overrides
                if storage_dir:
                    orchestrator.component_config["storage_directory"] = storage_dir
                
                # Start orchestrator
                await orchestrator.start()
                
                console.print("[green]✓ MAOS orchestration system started successfully![/green]")
                
                # Display system information
                status = await orchestrator.get_system_status()
                
                panel_content = f"""
[bold]System Information:[/bold]
• Status: [green]{status['running']}[/green]
• Startup Time: {status['startup_time']}
• Active Executions: {status['active_executions']}
• Storage Directory: {storage_dir or 'default'}
• Max Agents: {max_agents}
                """.strip()
                
                console.print(Panel(panel_content, title="🤖 MAOS System Status", border_style="green"))
                
                if monitor and not daemon:
                    # Start monitoring interface
                    monitor_system = SystemMonitor(orchestrator)
                    await monitor_system.start_live_monitoring()
                elif daemon:
                    console.print("[dim]Running in daemon mode. Use 'maos status' to monitor.[/dim]")
                    # Keep running until interrupted
                    try:
                        while True:
                            await asyncio.sleep(1)
                    except KeyboardInterrupt:
                        console.print("\n[yellow]Shutting down...[/yellow]")
                        await orchestrator.shutdown()
                else:
                    console.print("[dim]System started. Use 'maos status' to monitor.[/dim]")
                    
        except Exception as e:
            console.print(f"[red]❌ Failed to start system: {e}[/red]")
            if _logger:
                _logger.log_error(e, {"operation": "start_system"})
            raise typer.Exit(1)
    
    asyncio.run(_start_system())


@app.command(name="stop")
def stop_system(
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Force shutdown without graceful cleanup"
    ),
    timeout: int = typer.Option(
        30, "--timeout", "-t",
        help="Shutdown timeout in seconds"
    )
):
    """🛑 Stop the MAOS orchestration system
    
    Gracefully shuts down the orchestration system with optional
    force mode for emergency stops.
    """
    
    async def _stop_system():
        try:
            if not _orchestrator:
                console.print("[yellow]⚠️  No running system found[/yellow]")
                return
            
            if force:
                console.print("[red]⚠️  Force shutdown requested[/red]")
            
            with console.status("[bold red]Shutting down MAOS system..."):
                if force:
                    # Force shutdown
                    shutdown_orchestrator()
                else:
                    # Graceful shutdown with timeout
                    try:
                        await asyncio.wait_for(
                            _orchestrator.shutdown(), 
                            timeout=timeout
                        )
                    except asyncio.TimeoutError:
                        console.print(f"[yellow]⚠️  Shutdown timeout after {timeout}s, forcing...[/yellow]")
                        shutdown_orchestrator()
                
                console.print("[green]✓ System shutdown complete[/green]")
                
        except Exception as e:
            console.print(f"[red]❌ Error during shutdown: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_stop_system())


@app.command(name="version")
def show_version():
    """📋 Show MAOS version information"""
    from .. import __version__, __author__
    
    version_info = f"""
[bold]MAOS - Multi-Agent Orchestration System[/bold]

Version: [green]{__version__}[/green]
Author: {__author__}
Python: {sys.version.split()[0]}
Platform: {sys.platform}
    """.strip()
    
    console.print(Panel(version_info, title="🤖 Version Information", border_style="blue"))


@app.command(name="shell")
def interactive_shell(
    config_file: Optional[str] = typer.Option(
        None, "--config", "-c",
        help="Path to configuration file"
    )
):
    """🔧 Start interactive MAOS shell
    
    Provides an interactive shell with command completion
    and rich formatting for advanced system interaction.
    """
    
    async def _start_shell():
        try:
            orchestrator = init_orchestrator(config_file)
            await orchestrator.start()
            
            shell = InteractiveShell(orchestrator, console)
            await shell.run()
            
        except Exception as e:
            console.print(f"[red]❌ Shell error: {e}[/red]")
            raise typer.Exit(1)
        finally:
            if _orchestrator:
                await _orchestrator.shutdown()
    
    asyncio.run(_start_shell())


@app.command(name="chat")
def natural_language_chat(
    config_file: Optional[str] = typer.Option(
        None, "--config", "-c",
        help="Path to configuration file"
    ),
    auto_approve: bool = typer.Option(
        False, "--auto-approve", "-y",
        help="Auto-approve agent proposals"
    )
):
    """💬 Start natural language chat interface
    
    Chat with MAOS using natural language - NOW WITH AUTONOMOUS EXECUTION!
    Control agent swarms with simple English commands.
    
    The new v7 interface includes:
    • REAL autonomous Claude execution using SDK
    • TRUE parallel execution with --dangerously-skip-permissions
    • No manual intervention required
    • Automatic task decomposition into parallel batches
    • Session persistence and resumption
    • Cost and performance tracking
    """
    
    # Use the v7 interface with autonomous SDK execution
    async def run_v7():
        # Get API key from environment (optional - will use Claude Code if available)
        import os
        import subprocess
        api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Check if Claude Code is available
        try:
            result = subprocess.run(["claude", "--version"], capture_output=True, timeout=2)
            if result.returncode == 0:
                console.print("[green]✅ Claude Code detected - using authenticated session[/green]")
                # Don't use API key if Claude Code is available
                api_key = None
            elif api_key:
                console.print("[yellow]📝 Using provided API key[/yellow]")
            else:
                console.print("[yellow]⚠️  No Claude Code session or API key found[/yellow]")
                console.print("[dim]Start Claude Code with 'claude' or set ANTHROPIC_API_KEY[/dim]")
        except:
            if api_key:
                console.print("[yellow]📝 Using provided API key[/yellow]")
        
        processor = NaturalLanguageProcessorV7(
            db_path=Path("./maos.db"),
            api_key=api_key
        )
        await processor.run(auto_approve=auto_approve)
    
    asyncio.run(run_v7())


if __name__ == "__main__":
    import sys
    # If no arguments provided, show help and exit cleanly
    if len(sys.argv) == 1:
        app(["--help"])
    else:
        app()