"""
MAOS CLI Auto-completion Support

Provides shell completion for MAOS CLI commands, arguments, and IDs
with support for Bash, Zsh, and Fish shells.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


def setup_completion(shell: str = "bash") -> bool:
    """
    Setup shell completion for MAOS CLI.
    
    Args:
        shell: Target shell (bash, zsh, fish)
        
    Returns:
        bool: True if setup was successful
    """
    try:
        if shell == "bash":
            return _setup_bash_completion()
        elif shell == "zsh":
            return _setup_zsh_completion()
        elif shell == "fish":
            return _setup_fish_completion()
        else:
            console.print(f"[red]Unsupported shell: {shell}[/red]")
            return False
    except Exception as e:
        console.print(f"[red]Failed to setup completion: {e}[/red]")
        return False


def _setup_bash_completion() -> bool:
    """Setup Bash completion."""
    completion_script = _get_bash_completion_script()
    
    # Try to install in user's bash completion directory
    completion_dirs = [
        Path.home() / ".local/share/bash-completion/completions",
        Path.home() / ".bash_completion.d",
        Path("/usr/local/etc/bash_completion.d"),
        Path("/etc/bash_completion.d")
    ]
    
    for completion_dir in completion_dirs:
        if completion_dir.exists() or completion_dir.parent.exists():
            try:
                completion_dir.mkdir(parents=True, exist_ok=True)
                completion_file = completion_dir / "maos"
                completion_file.write_text(completion_script)
                
                console.print(f"[green]✓ Bash completion installed to {completion_file}[/green]")
                console.print("[dim]Restart your shell or run 'source ~/.bashrc' to activate[/dim]")
                return True
            except PermissionError:
                continue
    
    # Fallback: show instructions for manual installation
    console.print("[yellow]Could not install automatically. Manual setup required:[/yellow]")
    console.print("\n[cyan]Add the following to your ~/.bashrc:[/cyan]")
    console.print(Panel(Syntax(completion_script, "bash", theme="monokai"), title="Bash Completion"))
    return False


def _setup_zsh_completion() -> bool:
    """Setup Zsh completion."""
    completion_script = _get_zsh_completion_script()
    
    # Try to install in user's zsh completion directory
    zsh_completion_dir = Path.home() / ".zsh/completions"
    
    try:
        zsh_completion_dir.mkdir(parents=True, exist_ok=True)
        completion_file = zsh_completion_dir / "_maos"
        completion_file.write_text(completion_script)
        
        console.print(f"[green]✓ Zsh completion installed to {completion_file}[/green]")
        console.print("[dim]Add 'fpath=(~/.zsh/completions $fpath)' to your ~/.zshrc if not already present[/dim]")
        console.print("[dim]Then restart your shell or run 'compinit'[/dim]")
        return True
    except Exception:
        # Fallback: show instructions
        console.print("[yellow]Could not install automatically. Manual setup required:[/yellow]")
        console.print("\n[cyan]Save the following as ~/.zsh/completions/_maos:[/cyan]")
        console.print(Panel(Syntax(completion_script, "bash", theme="monokai"), title="Zsh Completion"))
        return False


def _setup_fish_completion() -> bool:
    """Setup Fish completion."""
    completion_script = _get_fish_completion_script()
    
    # Fish completion directory
    fish_completion_dir = Path.home() / ".config/fish/completions"
    
    try:
        fish_completion_dir.mkdir(parents=True, exist_ok=True)
        completion_file = fish_completion_dir / "maos.fish"
        completion_file.write_text(completion_script)
        
        console.print(f"[green]✓ Fish completion installed to {completion_file}[/green]")
        console.print("[dim]Completion is now active in new Fish shells[/dim]")
        return True
    except Exception:
        # Fallback: show instructions
        console.print("[yellow]Could not install automatically. Manual setup required:[/yellow]")
        console.print("\n[cyan]Save the following as ~/.config/fish/completions/maos.fish:[/cyan]")
        console.print(Panel(Syntax(completion_script, "fish", theme="monokai"), title="Fish Completion"))
        return False


def _get_bash_completion_script() -> str:
    """Generate Bash completion script."""
    return '''
# MAOS CLI Bash completion

_maos_completion() {
    local cur prev opts base_opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Main commands
    base_opts="start stop version shell task agent status recover config"
    
    # Task subcommands
    task_opts="submit list status cancel retry results export"
    
    # Agent subcommands
    agent_opts="create list status terminate restart metrics"
    
    # Status subcommands
    status_opts="overview health metrics monitor uptime summary"
    
    # Recover subcommands
    recover_opts="checkpoint list restore delete info export cleanup"
    
    # Config subcommands
    config_opts="show set init validate"
    
    # Global options
    global_opts="--config --verbose --quiet --format --help"
    
    case ${prev} in
        maos)
            COMPREPLY=($(compgen -W "${base_opts}" -- ${cur}))
            return 0
            ;;
        task)
            COMPREPLY=($(compgen -W "${task_opts}" -- ${cur}))
            return 0
            ;;
        agent)
            COMPREPLY=($(compgen -W "${agent_opts}" -- ${cur}))
            return 0
            ;;
        status)
            COMPREPLY=($(compgen -W "${status_opts}" -- ${cur}))
            return 0
            ;;
        recover)
            COMPREPLY=($(compgen -W "${recover_opts}" -- ${cur}))
            return 0
            ;;
        config)
            COMPREPLY=($(compgen -W "${config_opts}" -- ${cur}))
            return 0
            ;;
        --config)
            COMPREPLY=($(compgen -f -- ${cur}))
            return 0
            ;;
        --format)
            COMPREPLY=($(compgen -W "table json yaml tree" -- ${cur}))
            return 0
            ;;
        --priority)
            COMPREPLY=($(compgen -W "low medium high critical" -- ${cur}))
            return 0
            ;;
        --status)
            COMPREPLY=($(compgen -W "pending running completed failed cancelled" -- ${cur}))
            return 0
            ;;
        *)
            COMPREPLY=($(compgen -W "${global_opts}" -- ${cur}))
            return 0
            ;;
    esac
}

complete -F _maos_completion maos
'''.strip()


def _get_zsh_completion_script() -> str:
    """Generate Zsh completion script."""
    return '''
#compdef maos

# MAOS CLI Zsh completion

_maos() {
    local context state state_descr line
    typeset -A opt_args
    
    _arguments -C \
        "(-c --config)"{"-c","--config"}"[Configuration file]:file:_files" \
        "(-v --verbose)"{"-v","--verbose"}"[Enable verbose output]" \
        "(-q --quiet)"{"-q","--quiet"}"[Suppress non-essential output]" \
        "(-f --format)"{"-f","--format"}"[Output format]:format:(table json yaml tree)" \
        "(-h --help)"{"-h","--help"}"[Show help]" \
        "1: :_maos_commands" \
        "*:: :->args" && return 0
    
    case $state in
        args)
            case $words[1] in
                task)
                    _arguments \
                        "1: :(submit list status cancel retry results export)" \
                        "*:: :_maos_task_args"
                    ;;
                agent)
                    _arguments \
                        "1: :(create list status terminate restart metrics)" \
                        "*:: :_maos_agent_args"
                    ;;
                status)
                    _arguments \
                        "1: :(overview health metrics monitor uptime summary)"
                    ;;
                recover)
                    _arguments \
                        "1: :(checkpoint list restore delete info export cleanup)"
                    ;;
                config)
                    _arguments \
                        "1: :(show set init validate)"
                    ;;
            esac
            ;;
    esac
}

_maos_commands() {
    local commands
    commands=(
        "start:Start the MAOS orchestration system"
        "stop:Stop the MAOS orchestration system"
        "version:Show version information"
        "shell:Start interactive shell"
        "task:Task management operations"
        "agent:Agent lifecycle operations"
        "status:System monitoring and status"
        "recover:Recovery and checkpoint operations"
        "config:Configuration management"
    )
    _describe "commands" commands
}

_maos_task_args() {
    case $words[1] in
        submit)
            _arguments \
                "(-d --description)"{"-d","--description"}"[Task description]:description:" \
                "(-p --priority)"{"-p","--priority"}"[Task priority]:priority:(low medium high critical)" \
                "(-t --timeout)"{"-t","--timeout"}"[Task timeout in seconds]:timeout:" \
                "--wait[Wait for task completion]" \
                "--monitor[Monitor task progress]"
            ;;
        list)
            _arguments \
                "(-s --status)"{"-s","--status"}"[Filter by status]:status:(pending running completed failed cancelled)" \
                "(-l --limit)"{"-l","--limit"}"[Maximum tasks to show]:limit:" \
                "--watch[Watch for updates]"
            ;;
    esac
}

_maos_agent_args() {
    case $words[1] in
        create)
            _arguments \
                "(-c --capability)"{"-c","--capability"}"[Agent capabilities]:capability:" \
                "(-m --max-tasks)"{"-m","--max-tasks"}"[Maximum concurrent tasks]:max_tasks:" \
                "--cpu-limit[CPU limit in cores]:cpu_limit:" \
                "--memory-limit[Memory limit in MB]:memory_limit:"
            ;;
        list)
            _arguments \
                "(-s --status)"{"-s","--status"}"[Filter by status]:status:(available busy idle error)" \
                "(-t --type)"{"-t","--type"}"[Filter by agent type]:type:" \
                "--detailed[Show detailed information]"
            ;;
    esac
}

_maos "$@"
'''.strip()


def _get_fish_completion_script() -> str:
    """Generate Fish completion script."""
    return '''
# MAOS CLI Fish completion

# Main commands
complete -c maos -n "__fish_use_subcommand" -a "start" -d "Start the MAOS orchestration system"
complete -c maos -n "__fish_use_subcommand" -a "stop" -d "Stop the MAOS orchestration system"
complete -c maos -n "__fish_use_subcommand" -a "version" -d "Show version information"
complete -c maos -n "__fish_use_subcommand" -a "shell" -d "Start interactive shell"
complete -c maos -n "__fish_use_subcommand" -a "task" -d "Task management operations"
complete -c maos -n "__fish_use_subcommand" -a "agent" -d "Agent lifecycle operations"
complete -c maos -n "__fish_use_subcommand" -a "status" -d "System monitoring and status"
complete -c maos -n "__fish_use_subcommand" -a "recover" -d "Recovery and checkpoint operations"
complete -c maos -n "__fish_use_subcommand" -a "config" -d "Configuration management"

# Global options
complete -c maos -s c -l config -d "Configuration file" -r
complete -c maos -s v -l verbose -d "Enable verbose output"
complete -c maos -s q -l quiet -d "Suppress non-essential output"
complete -c maos -s f -l format -d "Output format" -xa "table json yaml tree"
complete -c maos -s h -l help -d "Show help"

# Task subcommands
complete -c maos -n "__fish_seen_subcommand_from task" -a "submit" -d "Submit a new task"
complete -c maos -n "__fish_seen_subcommand_from task" -a "list" -d "List tasks"
complete -c maos -n "__fish_seen_subcommand_from task" -a "status" -d "Get task status"
complete -c maos -n "__fish_seen_subcommand_from task" -a "cancel" -d "Cancel a task"
complete -c maos -n "__fish_seen_subcommand_from task" -a "retry" -d "Retry a failed task"
complete -c maos -n "__fish_seen_subcommand_from task" -a "results" -d "Get task results"
complete -c maos -n "__fish_seen_subcommand_from task" -a "export" -d "Export tasks to file"

# Task submit options
complete -c maos -n "__fish_seen_subcommand_from task; and __fish_seen_subcommand_from submit" -s d -l description -d "Task description" -r
complete -c maos -n "__fish_seen_subcommand_from task; and __fish_seen_subcommand_from submit" -s p -l priority -d "Task priority" -xa "low medium high critical"
complete -c maos -n "__fish_seen_subcommand_from task; and __fish_seen_subcommand_from submit" -s t -l timeout -d "Task timeout" -r
complete -c maos -n "__fish_seen_subcommand_from task; and __fish_seen_subcommand_from submit" -l wait -d "Wait for completion"
complete -c maos -n "__fish_seen_subcommand_from task; and __fish_seen_subcommand_from submit" -l monitor -d "Monitor progress"

# Task list options
complete -c maos -n "__fish_seen_subcommand_from task; and __fish_seen_subcommand_from list" -s s -l status -d "Filter by status" -xa "pending running completed failed cancelled"
complete -c maos -n "__fish_seen_subcommand_from task; and __fish_seen_subcommand_from list" -s l -l limit -d "Maximum tasks" -r
complete -c maos -n "__fish_seen_subcommand_from task; and __fish_seen_subcommand_from list" -l watch -d "Watch for updates"

# Agent subcommands
complete -c maos -n "__fish_seen_subcommand_from agent" -a "create" -d "Create a new agent"
complete -c maos -n "__fish_seen_subcommand_from agent" -a "list" -d "List agents"
complete -c maos -n "__fish_seen_subcommand_from agent" -a "status" -d "Get agent status"
complete -c maos -n "__fish_seen_subcommand_from agent" -a "terminate" -d "Terminate an agent"
complete -c maos -n "__fish_seen_subcommand_from agent" -a "restart" -d "Restart an agent"
complete -c maos -n "__fish_seen_subcommand_from agent" -a "metrics" -d "Show agent metrics"

# Agent create options
complete -c maos -n "__fish_seen_subcommand_from agent; and __fish_seen_subcommand_from create" -s c -l capability -d "Agent capabilities" -r
complete -c maos -n "__fish_seen_subcommand_from agent; and __fish_seen_subcommand_from create" -s m -l max-tasks -d "Max concurrent tasks" -r
complete -c maos -n "__fish_seen_subcommand_from agent; and __fish_seen_subcommand_from create" -l cpu-limit -d "CPU limit" -r
complete -c maos -n "__fish_seen_subcommand_from agent; and __fish_seen_subcommand_from create" -l memory-limit -d "Memory limit" -r

# Status subcommands
complete -c maos -n "__fish_seen_subcommand_from status" -a "overview" -d "System overview"
complete -c maos -n "__fish_seen_subcommand_from status" -a "health" -d "Health check"
complete -c maos -n "__fish_seen_subcommand_from status" -a "metrics" -d "System metrics"
complete -c maos -n "__fish_seen_subcommand_from status" -a "monitor" -d "Live monitoring"
complete -c maos -n "__fish_seen_subcommand_from status" -a "uptime" -d "System uptime"
complete -c maos -n "__fish_seen_subcommand_from status" -a "summary" -d "Status summary"

# Recover subcommands
complete -c maos -n "__fish_seen_subcommand_from recover" -a "checkpoint" -d "Create checkpoint"
complete -c maos -n "__fish_seen_subcommand_from recover" -a "list" -d "List checkpoints"
complete -c maos -n "__fish_seen_subcommand_from recover" -a "restore" -d "Restore from checkpoint"
complete -c maos -n "__fish_seen_subcommand_from recover" -a "delete" -d "Delete checkpoint"
complete -c maos -n "__fish_seen_subcommand_from recover" -a "info" -d "Checkpoint info"
complete -c maos -n "__fish_seen_subcommand_from recover" -a "export" -d "Export checkpoint"
complete -c maos -n "__fish_seen_subcommand_from recover" -a "cleanup" -d "Cleanup old checkpoints"

# Config subcommands
complete -c maos -n "__fish_seen_subcommand_from config" -a "show" -d "Show configuration"
complete -c maos -n "__fish_seen_subcommand_from config" -a "set" -d "Set configuration value"
complete -c maos -n "__fish_seen_subcommand_from config" -a "init" -d "Initialize configuration"
complete -c maos -n "__fish_seen_subcommand_from config" -a "validate" -d "Validate configuration"
'''.strip()


def show_completion_help():
    """Show help for setting up shell completion."""
    help_text = """
[bold blue]MAOS CLI Shell Completion Setup[/bold blue]

[cyan]Automatic Setup:[/cyan]
  maos config completion --install [bash|zsh|fish]

[cyan]Manual Setup:[/cyan]

[yellow]Bash:[/yellow]
  1. Save completion script to ~/.local/share/bash-completion/completions/maos
  2. Restart shell or run: source ~/.bashrc

[yellow]Zsh:[/yellow]
  1. Create directory: mkdir -p ~/.zsh/completions
  2. Save completion script as ~/.zsh/completions/_maos
  3. Add to ~/.zshrc: fpath=(~/.zsh/completions $fpath)
  4. Run: compinit

[yellow]Fish:[/yellow]
  1. Save completion script as ~/.config/fish/completions/maos.fish
  2. Restart Fish shell

[cyan]Verification:[/cyan]
  Type 'maos ' and press Tab to test completion.
    """.strip()
    
    console.print(Panel(
        Text(help_text),
        title="📝 Shell Completion Help",
        border_style="cyan"
    ))


def get_completion_status() -> Dict[str, bool]:
    """Check which shells have completion configured."""
    status = {
        "bash": False,
        "zsh": False,
        "fish": False
    }
    
    # Check Bash
    bash_completion_paths = [
        Path.home() / ".local/share/bash-completion/completions/maos",
        Path.home() / ".bash_completion.d/maos",
        Path("/usr/local/etc/bash_completion.d/maos"),
        Path("/etc/bash_completion.d/maos")
    ]
    
    for path in bash_completion_paths:
        if path.exists():
            status["bash"] = True
            break
    
    # Check Zsh
    zsh_completion_file = Path.home() / ".zsh/completions/_maos"
    if zsh_completion_file.exists():
        status["zsh"] = True
    
    # Check Fish
    fish_completion_file = Path.home() / ".config/fish/completions/maos.fish"
    if fish_completion_file.exists():
        status["fish"] = True
    
    return status


def generate_completion_script(shell: str) -> str:
    """Generate completion script for specified shell."""
    if shell == "bash":
        return _get_bash_completion_script()
    elif shell == "zsh":
        return _get_zsh_completion_script()
    elif shell == "fish":
        return _get_fish_completion_script()
    else:
        raise ValueError(f"Unsupported shell: {shell}")


# Interactive completion helpers for the shell

def complete_command(text: str, commands: List[str]) -> List[str]:
    """Complete command names."""
    return [cmd for cmd in commands if cmd.startswith(text)]


def complete_file_path(text: str) -> List[str]:
    """Complete file paths."""
    try:
        path = Path(text)
        if path.is_dir():
            return [str(p) for p in path.iterdir() if p.name.startswith("")]
        else:
            parent = path.parent
            name_start = path.name
            return [
                str(parent / p.name) for p in parent.iterdir()
                if p.name.startswith(name_start)
            ]
    except:
        return []


def complete_task_id(text: str, task_ids: List[str]) -> List[str]:
    """Complete task IDs."""
    return [tid for tid in task_ids if tid.startswith(text)]


def complete_agent_id(text: str, agent_ids: List[str]) -> List[str]:
    """Complete agent IDs."""
    return [aid for aid in agent_ids if aid.startswith(text)]