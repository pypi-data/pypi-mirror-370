#!/usr/bin/env python3
"""
MAOS - Multi-Agent Orchestration System
Simple entry point for natural language interface

Just run: python maos.py
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.maos.cli.natural_language import NaturalLanguageShell
from src.maos.core.orchestrator import Orchestrator
from src.maos.utils.logging_config import setup_logging
from rich.console import Console
from rich.panel import Panel


def check_prerequisites():
    """Check if prerequisites are met."""
    console = Console()
    
    # Check for Claude CLI
    import subprocess
    try:
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception("Claude CLI not working")
    except:
        console.print(Panel(
            "[red]❌ Claude Code CLI not found![/red]\n\n"
            "Please install and authenticate Claude Code first:\n"
            "[cyan]npm install -g @anthropic-ai/claude-code[/cyan]\n"
            "[cyan]claude login[/cyan]",
            title="Prerequisites Missing",
            border_style="red"
        ))
        return False
    
    # Docker is optional
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            console.print("[dim]✓ Docker available for optional features[/dim]")
    except:
        pass  # Docker is optional
    
    return True


async def main():
    """Main entry point for MAOS natural language interface."""
    
    console = Console()
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    try:
        # Check if Redis is available (optional)
        redis_available = False
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=1)
            r.ping()
            redis_available = True
            console.print("[green]✓ Redis detected - distributed features enabled[/green]")
        except:
            console.print("[cyan]ℹ Running in local mode (Redis not required)[/cyan]")
        
        # Setup logging
        setup_logging(level="INFO")
        
        # Initialize orchestrator
        console.print("[cyan]Starting MAOS orchestration system...[/cyan]")
        
        orchestrator_config = {
            "storage_directory": "./maos_storage",
            "use_redis": redis_available,
            "redis_url": "redis://localhost:6379" if redis_available else None,
            "max_agents": 10,
            "claude_cli_path": "claude",
            "enable_monitoring": True
        }
        
        orchestrator = Orchestrator(component_config=orchestrator_config)
        await orchestrator.start()
        
        console.print("[green]✓ MAOS system ready![/green]\n")
        
        # Start natural language shell
        shell = NaturalLanguageShell(orchestrator)
        await shell.run()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)
    finally:
        try:
            await orchestrator.shutdown()
            console.print("[green]✓ Shutdown complete[/green]")
        except:
            pass


if __name__ == "__main__":
    # Make the script executable
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)