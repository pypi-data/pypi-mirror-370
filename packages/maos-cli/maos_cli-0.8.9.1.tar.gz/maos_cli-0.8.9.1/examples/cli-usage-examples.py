#!/usr/bin/env python3
"""
MAOS CLI Usage Examples

Comprehensive examples demonstrating all MAOS CLI capabilities
including task management, agent operations, monitoring, and recovery.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_command(command: str, description: str = ""):
    """Run a CLI command and display results."""
    print(f"\n{'='*60}")
    if description:
        print(f"Description: {description}")
    print(f"Command: {command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode != 0:
            print(f"Command failed with exit code: {result.returncode}")
        
    except subprocess.TimeoutExpired:
        print("Command timed out")
    except Exception as e:
        print(f"Error running command: {e}")


def demonstrate_basic_commands():
    """Demonstrate basic CLI commands."""
    print("\n🔥 MAOS CLI - Basic Commands Demo")
    
    # Version and help
    run_command("maos version", "Show MAOS version information")
    run_command("maos --help", "Show main help")
    
    # Configuration commands
    run_command("maos config show --defaults", "Show default configuration")
    run_command("maos config init --no-interactive --template standard", "Initialize configuration")
    run_command("maos config validate", "Validate configuration")
    run_command("maos config show --format json", "Show configuration as JSON")


def demonstrate_system_operations():
    """Demonstrate system start/stop and status commands."""
    print("\n🚀 MAOS CLI - System Operations Demo")
    
    # Start system
    run_command("maos start --no-monitor --daemon", "Start MAOS system in daemon mode")
    time.sleep(2)  # Allow system to start
    
    # Status commands
    run_command("maos status overview", "Show system overview")
    run_command("maos status health", "Check system health")
    run_command("maos status metrics --format table", "Show system metrics")
    run_command("maos status uptime", "Show system uptime")
    run_command("maos status summary", "Show status summary")


def demonstrate_task_management():
    """Demonstrate task management operations."""
    print("\n📋 MAOS CLI - Task Management Demo")
    
    # Submit tasks
    run_command(
        "maos task submit 'Data Processing Task' --description 'Process customer data' --priority high --timeout 600",
        "Submit a high-priority task"
    )
    
    run_command(
        "maos task submit 'Background Analysis' --priority low --max-retries 5",
        "Submit a low-priority task with retries"
    )
    
    run_command(
        "maos task submit 'ML Training Job' --priority critical --cpu 4.0 --memory 8192",
        "Submit resource-intensive task"
    )
    
    # List and manage tasks
    run_command("maos task list --limit 10", "List recent tasks")
    run_command("maos task list --status running", "List running tasks")
    run_command("maos task list --format json", "List tasks as JSON")
    
    # Export tasks
    run_command(
        "maos task export tasks_export.json --format json --include-results",
        "Export tasks to JSON file"
    )


def demonstrate_agent_management():
    """Demonstrate agent management operations."""
    print("\n🤖 MAOS CLI - Agent Management Demo")
    
    # Create agents
    run_command(
        "maos agent create data_processor --capability data_processing --capability computation --max-tasks 3 --cpu-limit 2.0",
        "Create a data processing agent"
    )
    
    run_command(
        "maos agent create api_worker --capability api_integration --capability communication --max-tasks 5",
        "Create an API integration agent"
    )
    
    # List and monitor agents
    run_command("maos agent list", "List all agents")
    run_command("maos agent list --status available", "List available agents")
    run_command("maos agent list --detailed --format table", "Show detailed agent information")
    
    # Show agent metrics
    run_command("maos agent metrics --type performance", "Show agent performance metrics")


def demonstrate_monitoring():
    """Demonstrate monitoring capabilities."""
    print("\n📊 MAOS CLI - Monitoring Demo")
    
    # Note: These commands would normally run interactively
    # For demo purposes, we'll show the command syntax
    
    print("\n⚠️  Interactive monitoring commands (run manually):")
    print("  maos status monitor --detailed     # Start live system monitoring")
    print("  maos task status <task-id> --monitor  # Monitor specific task")
    print("  maos agent status <agent-id> --monitor  # Monitor specific agent")
    
    # Export metrics
    run_command(
        "maos status metrics --export metrics_export.json",
        "Export system metrics"
    )


def demonstrate_recovery_operations():
    """Demonstrate checkpoint and recovery operations."""
    print("\n💾 MAOS CLI - Recovery Operations Demo")
    
    # Create checkpoints
    run_command(
        "maos recover checkpoint demo-checkpoint --description 'Demo system state'",
        "Create a named checkpoint"
    )
    
    run_command(
        "maos recover checkpoint --name automated-backup",
        "Create an automated backup checkpoint"
    )
    
    # List and manage checkpoints
    run_command("maos recover list --limit 5", "List recent checkpoints")
    run_command("maos recover list --format json", "List checkpoints as JSON")
    run_command("maos recover list --details", "Show detailed checkpoint info")
    
    # Export checkpoint
    run_command(
        "maos recover export <checkpoint-id> checkpoint_backup.json --format json",
        "Export checkpoint to file (replace <checkpoint-id>)"
    )


def demonstrate_interactive_features():
    """Demonstrate interactive features."""
    print("\n🔧 MAOS CLI - Interactive Features Demo")
    
    print("\n⚠️  Interactive features (run manually):")
    print("  maos shell                    # Start interactive shell")
    print("  maos config completion --install --shell bash  # Setup completion")
    print("  maos task submit --wait       # Submit task and wait for completion")
    print("  maos task list --watch        # Watch task list with live updates")


def demonstrate_advanced_features():
    """Demonstrate advanced CLI features."""
    print("\n⚡ MAOS CLI - Advanced Features Demo")
    
    # Configuration management
    run_command(
        "maos config set logging.level DEBUG",
        "Set log level to DEBUG"
    )
    
    run_command(
        "maos config set system.max_agents 50",
        "Set maximum agents to 50"
    )
    
    run_command(
        "maos config show --section system",
        "Show system configuration section"
    )
    
    # Multiple output formats
    run_command("maos status summary --format yaml", "Show status as YAML")
    run_command("maos agent list --format tree", "Show agents as tree")
    
    # Filtering and search
    run_command("maos task list --priority high --status running", "Filter high-priority running tasks")
    run_command("maos agent list --capability data_processing", "Find agents with specific capability")


def demonstrate_error_handling():
    """Demonstrate error handling and help systems."""
    print("\n🚨 MAOS CLI - Error Handling Demo")
    
    # Intentional errors to show error handling
    run_command("maos task status invalid-task-id", "Try to get status of invalid task")
    run_command("maos agent terminate nonexistent-agent", "Try to terminate non-existent agent")
    run_command("maos config set invalid.setting value", "Try to set invalid configuration")
    
    # Help system
    run_command("maos task --help", "Show task command help")
    run_command("maos agent create --help", "Show agent creation help")
    run_command("maos status monitor --help", "Show monitoring help")


def cleanup_demo():
    """Clean up demo resources."""
    print("\n🧹 MAOS CLI - Cleanup")
    
    # Stop system
    run_command("maos stop --force", "Stop MAOS system")
    
    # Cleanup files
    files_to_cleanup = [
        "tasks_export.json",
        "metrics_export.json",
        "checkpoint_backup.json"
    ]
    
    for file_path in files_to_cleanup:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            print(f"Cleaned up: {file_path}")


def main():
    """Run complete MAOS CLI demonstration."""
    print("🎯 MAOS CLI Comprehensive Demonstration")
    print("This script demonstrates all major MAOS CLI capabilities.")
    print("Some interactive features need to be run manually.")
    
    try:
        # Run demonstrations
        demonstrate_basic_commands()
        demonstrate_system_operations()
        demonstrate_task_management()
        demonstrate_agent_management()
        demonstrate_monitoring()
        demonstrate_recovery_operations()
        demonstrate_interactive_features()
        demonstrate_advanced_features()
        demonstrate_error_handling()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    
    finally:
        cleanup_demo()
    
    print("\n✅ MAOS CLI demonstration complete!")
    print("\n📚 For more information:")
    print("  • Run 'maos --help' for command overview")
    print("  • Run 'maos <command> --help' for specific help")
    print("  • Use 'maos shell' for interactive mode")
    print("  • Check examples/maos-config-example.yml for configuration")


if __name__ == "__main__":
    main()