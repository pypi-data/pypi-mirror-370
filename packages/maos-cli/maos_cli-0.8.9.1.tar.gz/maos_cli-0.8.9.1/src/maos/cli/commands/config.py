"""
MAOS CLI Configuration Commands

Configuration management commands for MAOS CLI settings,
system configuration, and environment setup.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from rich.text import Text

from ..config import CLIConfig, load_config, save_config, create_default_config, validate_config, get_config_paths
from ..formatters import OutputFormatter
from ..completion import setup_completion, show_completion_help, get_completion_status

console = Console()
config_app = typer.Typer(help="⚙️ Configuration management")


@config_app.command(name="show")
def show_config(
    config_file: Optional[str] = typer.Option(
        None, "--config", "-c",
        help="Specific config file to show"
    ),
    section: Optional[str] = typer.Option(
        None, "--section", "-s",
        help="Show specific configuration section"
    ),
    output_format: str = typer.Option(
        "yaml", "--format", "-f",
        help="Output format (yaml, json, table)"
    ),
    show_defaults: bool = typer.Option(
        False, "--defaults",
        help="Show default configuration values"
    ),
    show_paths: bool = typer.Option(
        False, "--paths",
        help="Show configuration file search paths"
    )
):
    """📝 Show current configuration
    
    Displays the current MAOS configuration with options to show
    specific sections, defaults, or file paths.
    """
    try:
        if show_paths:
            _show_config_paths()
            return
        
        if show_defaults:
            config = CLIConfig()
            title = "Default Configuration"
        else:
            config = load_config(config_file)
            title = f"Current Configuration{' from ' + config_file if config_file else ''}"
        
        config_dict = config.to_dict()
        
        # Show specific section if requested
        if section:
            if section in config_dict:
                config_dict = {section: config_dict[section]}
                title += f" - {section.title()}"
            else:
                console.print(f"[red]❌ Configuration section not found: {section}[/red]")
                available = ", ".join(config_dict.keys())
                console.print(f"[dim]Available sections: {available}[/dim]")
                raise typer.Exit(1)
        
        # Format and display
        if output_format == "yaml":
            yaml_content = yaml.dump(config_dict, default_flow_style=False, indent=2)
            console.print(Panel(
                Syntax(yaml_content, "yaml", theme="monokai", line_numbers=True),
                title=title,
                border_style="blue"
            ))
        elif output_format == "json":
            import json
            json_content = json.dumps(config_dict, indent=2, default=str)
            console.print(Panel(
                Syntax(json_content, "json", theme="monokai", line_numbers=True),
                title=title,
                border_style="green"
            ))
        else:
            formatter = OutputFormatter.create("table")
            _display_config_table(config_dict, title)
            
    except Exception as e:
        console.print(f"[red]❌ Failed to show configuration: {e}[/red]")
        raise typer.Exit(1)


@config_app.command(name="set")
def set_config(
    key: str = typer.Argument(..., help="Configuration key (e.g., logging.level)"),
    value: str = typer.Argument(..., help="Configuration value"),
    config_file: Optional[str] = typer.Option(
        None, "--config", "-c",
        help="Config file to modify"
    ),
    create_if_missing: bool = typer.Option(
        True, "--create/--no-create",
        help="Create config file if it doesn't exist"
    )
):
    """✏️ Set a configuration value
    
    Sets a configuration value using dot notation for nested keys.
    Creates configuration file if it doesn't exist.
    
    Examples:
      maos config set logging.level DEBUG
      maos config set system.max_agents 50
      maos config set storage.directory /custom/path
    """
    try:
        # Load existing config
        config = load_config(config_file)
        
        # Parse the key path
        key_parts = key.split('.')
        if len(key_parts) < 2:
            console.print(f"[red]❌ Invalid key format: {key}[/red]")
            console.print("[dim]Use dot notation like 'section.key' (e.g., 'logging.level')[/dim]")
            raise typer.Exit(1)
        
        section_name = key_parts[0]
        setting_name = '.'.join(key_parts[1:])
        
        # Validate section exists
        if not hasattr(config, section_name):
            console.print(f"[red]❌ Unknown configuration section: {section_name}[/red]")
            valid_sections = [attr for attr in dir(config) if not attr.startswith('_') and hasattr(getattr(config, attr), '__dict__')]
            console.print(f"[dim]Valid sections: {', '.join(valid_sections)}[/dim]")
            raise typer.Exit(1)
        
        section = getattr(config, section_name)
        
        # Validate setting exists
        if not hasattr(section, setting_name):
            console.print(f"[red]❌ Unknown setting: {section_name}.{setting_name}[/red]")
            valid_settings = [attr for attr in dir(section) if not attr.startswith('_')]
            console.print(f"[dim]Valid settings in {section_name}: {', '.join(valid_settings)}[/dim]")
            raise typer.Exit(1)
        
        # Get current value and type
        current_value = getattr(section, setting_name)
        current_type = type(current_value)
        
        # Convert value to appropriate type
        try:
            if current_type == bool:
                new_value = value.lower() in ('true', '1', 'yes', 'on', 'enabled')
            elif current_type == int:
                new_value = int(value)
            elif current_type == float:
                new_value = float(value)
            elif current_type == Path:
                new_value = Path(value)
            else:
                new_value = value
        except ValueError as e:
            console.print(f"[red]❌ Invalid value type: {e}[/red]")
            console.print(f"[dim]Expected type: {current_type.__name__}[/dim]")
            raise typer.Exit(1)
        
        # Set the new value
        setattr(section, setting_name, new_value)
        
        # Save configuration
        success = save_config(config, config_file)
        
        if success:
            console.print(f"[green]✅ Configuration updated successfully[/green]")
            console.print(f"[cyan]{key}[/cyan]: [white]{current_value}[/white] → [green]{new_value}[/green]")
        else:
            console.print(f"[red]❌ Failed to save configuration[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Failed to set configuration: {e}[/red]")
        raise typer.Exit(1)


@config_app.command(name="init")
def init_config(
    config_file: Optional[str] = typer.Option(
        None, "--config", "-c",
        help="Config file to create"
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Overwrite existing configuration"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive",
        help="Interactive configuration setup"
    ),
    template: Optional[str] = typer.Option(
        None, "--template",
        help="Configuration template (minimal, standard, full)"
    )
):
    """🎆 Initialize MAOS configuration
    
    Creates a new configuration file with default or custom settings.
    Supports interactive setup and multiple templates.
    """
    try:
        # Determine config file path
        if not config_file:
            config_paths = get_config_paths()
            config_file = str(config_paths[1])  # Use ~/.maos.yml
        
        config_path = Path(config_file)
        
        # Check if file exists
        if config_path.exists() and not force:
            console.print(f"[yellow]⚠️  Configuration file already exists: {config_file}[/yellow]")
            if not Confirm.ask("Overwrite existing configuration?", default=False):
                console.print("[yellow]Configuration initialization cancelled[/yellow]")
                return
        
        # Create configuration
        if interactive:
            config = _interactive_config_setup()
        else:
            config = _template_config_setup(template or "standard")
        
        # Create directory if needed
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save configuration
        success = save_config(config, str(config_path))
        
        if success:
            console.print(f"[green]✅ Configuration initialized successfully![/green]")
            console.print(f"[dim]Location: {config_path}[/dim]")
            
            if interactive:
                console.print("\n[cyan]Next steps:[/cyan]")
                console.print("1. Review the configuration: maos config show")
                console.print("2. Validate settings: maos config validate")
                console.print("3. Start MAOS: maos start")
        else:
            console.print(f"[red]❌ Failed to initialize configuration[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Configuration initialization failed: {e}[/red]")
        raise typer.Exit(1)


@config_app.command(name="validate")
def validate_config(
    config_file: Optional[str] = typer.Option(
        None, "--config", "-c",
        help="Config file to validate"
    ),
    fix_issues: bool = typer.Option(
        False, "--fix",
        help="Attempt to fix validation issues"
    ),
    show_examples: bool = typer.Option(
        False, "--examples",
        help="Show configuration examples"
    )
):
    """✅ Validate MAOS configuration
    
    Checks configuration for errors, missing values, and
    provides suggestions for improvements.
    """
    try:
        if show_examples:
            _show_config_examples()
            return
        
        # Load and validate configuration
        config = load_config(config_file)
        issues = validate_config(config)
        
        if not issues:
            console.print(f"[green]✅ Configuration is valid![/green]")
            
            # Show summary
            console.print("\n[bold cyan]Configuration Summary:[/bold cyan]")
            summary_table = Table(show_header=False, box=None)
            summary_table.add_column("Property", style="cyan", width=25)
            summary_table.add_column("Value", style="white")
            
            summary_table.add_row("Storage Directory", str(config.storage.directory))
            summary_table.add_row("Max Agents", str(config.system.max_agents))
            summary_table.add_row("Logging Level", config.logging.level)
            summary_table.add_row("Redis Enabled", str(config.redis.enabled))
            summary_table.add_row("Monitoring Enabled", str(config.monitoring.enabled))
            
            console.print(summary_table)
            
        else:
            console.print(f"[red]❌ Configuration has {len(issues)} issues:[/red]\n")
            
            for i, issue in enumerate(issues, 1):
                console.print(f"[red]{i}.[/red] {issue}")
            
            if fix_issues:
                console.print("\n[yellow]Attempting to fix issues...[/yellow]")
                
                fixed_config = _fix_configuration_issues(config, issues)
                
                if fixed_config:
                    save_success = save_config(fixed_config, config_file)
                    if save_success:
                        console.print(f"[green]✅ Configuration issues fixed and saved[/green]")
                    else:
                        console.print(f"[red]❌ Failed to save fixed configuration[/red]")
                else:
                    console.print(f"[red]❌ Could not automatically fix all issues[/red]")
            else:
                console.print("\n[dim]Use --fix to attempt automatic fixes[/dim]")
                
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Configuration validation failed: {e}[/red]")
        raise typer.Exit(1)


@config_app.command(name="completion")
def setup_shell_completion(
    shell: Optional[str] = typer.Option(
        None, "--shell", "-s",
        help="Target shell (bash, zsh, fish)"
    ),
    install: bool = typer.Option(
        False, "--install",
        help="Install completion scripts"
    ),
    show_status: bool = typer.Option(
        False, "--status",
        help="Show completion status for all shells"
    ),
    generate: bool = typer.Option(
        False, "--generate",
        help="Generate completion script to stdout"
    )
):
    """📝 Setup shell completion
    
    Installs or generates shell completion scripts for MAOS CLI
    with support for Bash, Zsh, and Fish shells.
    """
    try:
        if show_status:
            _show_completion_status()
            return
        
        if not shell:
            # Auto-detect shell
            shell = os.environ.get('SHELL', '').split('/')[-1]
            if shell not in ['bash', 'zsh', 'fish']:
                console.print(f"[yellow]⚠️  Could not detect shell. Please specify with --shell[/yellow]")
                show_completion_help()
                return
        
        if generate:
            # Generate and print completion script
            from ..completion import generate_completion_script
            script = generate_completion_script(shell)
            console.print(script)
            return
        
        if install:
            # Install completion
            success = setup_completion(shell)
            
            if success:
                console.print(f"[green]✅ Shell completion installed for {shell}[/green]")
            else:
                console.print(f"[red]❌ Failed to install completion for {shell}[/red]")
                show_completion_help()
        else:
            # Show help
            show_completion_help()
            
    except Exception as e:
        console.print(f"[red]❌ Completion setup failed: {e}[/red]")
        raise typer.Exit(1)


@config_app.command(name="reset")
def reset_config(
    section: Optional[str] = typer.Option(
        None, "--section", "-s",
        help="Reset specific section only"
    ),
    config_file: Optional[str] = typer.Option(
        None, "--config", "-c",
        help="Config file to reset"
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Skip confirmation"
    )
):
    """🔄 Reset configuration to defaults
    
    Resets the entire configuration or a specific section
    back to default values.
    """
    try:
        # Confirmation
        if not force:
            if section:
                message = f"Reset {section} section to defaults?"
            else:
                message = "Reset entire configuration to defaults?"
            
            if not Confirm.ask(message, default=False):
                console.print("[yellow]Reset cancelled[/yellow]")
                return
        
        # Load current config and create default
        current_config = load_config(config_file)
        default_config = CLIConfig()
        
        if section:
            # Reset specific section
            if hasattr(current_config, section) and hasattr(default_config, section):
                default_section = getattr(default_config, section)
                setattr(current_config, section, default_section)
                console.print(f"[green]✅ Section '{section}' reset to defaults[/green]")
            else:
                console.print(f"[red]❌ Unknown section: {section}[/red]")
                raise typer.Exit(1)
        else:
            # Reset entire config
            current_config = default_config
            console.print(f"[green]✅ Configuration reset to defaults[/green]")
        
        # Save reset configuration
        success = save_config(current_config, config_file)
        
        if not success:
            console.print(f"[red]❌ Failed to save reset configuration[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Configuration reset failed: {e}[/red]")
        raise typer.Exit(1)


# Helper functions

def _show_config_paths():
    """Show configuration file search paths."""
    paths = get_config_paths()
    
    console.print("[bold blue]Configuration File Search Paths:[/bold blue]\n")
    
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Priority", style="cyan", width=8)
    table.add_column("Path", style="white")
    table.add_column("Exists", style="green", width=8)
    table.add_column("Writable", style="yellow", width=10)
    
    for i, path in enumerate(paths, 1):
        exists = "✓" if path.exists() else "❌"
        exists_color = "green" if path.exists() else "red"
        
        try:
            # Test writeability
            if path.exists():
                writable = path.is_file() and os.access(path, os.W_OK)
            else:
                writable = os.access(path.parent, os.W_OK) if path.parent.exists() else False
            
            writable_icon = "✓" if writable else "❌"
            writable_color = "green" if writable else "red"
        except:
            writable_icon = "?"
            writable_color = "dim"
        
        table.add_row(
            str(i),
            str(path),
            f"[{exists_color}]{exists}[/{exists_color}]",
            f"[{writable_color}]{writable_icon}[/{writable_color}]"
        )
    
    console.print(table)
    console.print("\n[dim]MAOS searches for configuration files in order of priority.[/dim]")


def _display_config_table(config_dict: Dict[str, Any], title: str):
    """Display configuration as nested tables."""
    console.print(f"[bold blue]{title}[/bold blue]\n")
    
    for section_name, section_data in config_dict.items():
        if isinstance(section_data, dict):
            table = Table(show_header=True, header_style="bold cyan", title=section_name.title())
            table.add_column("Setting", style="cyan", width=25)
            table.add_column("Value", style="white")
            table.add_column("Type", style="dim", width=10)
            
            for key, value in section_data.items():
                # Format value based on type
                if isinstance(value, bool):
                    formatted_value = f"[green]{value}[/green]" if value else f"[red]{value}[/red]"
                elif isinstance(value, (int, float)):
                    formatted_value = f"[yellow]{value}[/yellow]"
                elif isinstance(value, Path):
                    formatted_value = f"[blue]{value}[/blue]"
                elif value is None:
                    formatted_value = f"[dim]None[/dim]"
                else:
                    formatted_value = str(value)
                
                table.add_row(
                    key.replace('_', ' ').title(),
                    formatted_value,
                    type(value).__name__
                )
            
            console.print(table)
            console.print()
        else:
            console.print(f"[cyan]{section_name}:[/cyan] [white]{section_data}[/white]")


def _interactive_config_setup() -> CLIConfig:
    """Interactive configuration setup."""
    console.print("[bold blue]MAOS Configuration Setup[/bold blue]\n")
    
    config = CLIConfig()
    
    # Logging configuration
    console.print("[cyan]Logging Configuration:[/cyan]")
    log_level = Prompt.ask(
        "Log level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO"
    )
    config.logging.level = log_level
    
    enable_file_logging = Confirm.ask("Enable file logging?", default=True)
    if enable_file_logging:
        log_file = Prompt.ask("Log file path", default="")
        if log_file:
            config.logging.file = log_file
    
    # Storage configuration
    console.print("\n[cyan]Storage Configuration:[/cyan]")
    storage_dir = Prompt.ask(
        "Storage directory",
        default=str(config.storage.directory)
    )
    config.storage.directory = Path(storage_dir)
    
    # System configuration
    console.print("\n[cyan]System Configuration:[/cyan]")
    max_agents = Prompt.ask(
        "Maximum agents",
        default=str(config.system.max_agents)
    )
    config.system.max_agents = int(max_agents)
    
    # Redis configuration
    console.print("\n[cyan]Redis Configuration:[/cyan]")
    enable_redis = Confirm.ask("Enable Redis?", default=False)
    config.redis.enabled = enable_redis
    
    if enable_redis:
        redis_url = Prompt.ask(
            "Redis URL",
            default=config.redis.url
        )
        config.redis.url = redis_url
    
    # Monitoring configuration
    console.print("\n[cyan]Monitoring Configuration:[/cyan]")
    enable_monitoring = Confirm.ask("Enable monitoring?", default=True)
    config.monitoring.enabled = enable_monitoring
    
    console.print("\n[green]✅ Configuration setup complete![/green]")
    
    return config


def _template_config_setup(template: str) -> CLIConfig:
    """Setup configuration from template."""
    config = CLIConfig()
    
    if template == "minimal":
        # Minimal configuration with basic settings
        config.logging.level = "WARNING"
        config.logging.file = None
        config.system.max_agents = 5
        config.monitoring.enabled = False
        config.redis.enabled = False
        
    elif template == "full":
        # Full configuration with all features enabled
        config.logging.level = "DEBUG"
        config.logging.file = "maos.log"
        config.system.max_agents = 100
        config.monitoring.enabled = True
        config.redis.enabled = True
        config.system.checkpoint_interval = 300
        
    # "standard" template uses defaults
    
    return config


def _show_completion_status():
    """Show shell completion installation status."""
    status = get_completion_status()
    
    console.print("[bold blue]Shell Completion Status:[/bold blue]\n")
    
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Shell", style="cyan", width=10)
    table.add_column("Status", style="white", width=12)
    table.add_column("Location", style="dim")
    
    for shell, installed in status.items():
        status_text = "[green]Installed[/green]" if installed else "[red]Not Installed[/red]"
        
        # Try to find completion file location
        location = "N/A"
        if shell == "bash" and installed:
            bash_paths = [
                Path.home() / ".local/share/bash-completion/completions/maos",
                Path.home() / ".bash_completion.d/maos"
            ]
            for path in bash_paths:
                if path.exists():
                    location = str(path)
                    break
        elif shell == "zsh" and installed:
            location = str(Path.home() / ".zsh/completions/_maos")
        elif shell == "fish" and installed:
            location = str(Path.home() / ".config/fish/completions/maos.fish")
        
        table.add_row(shell.title(), status_text, location)
    
    console.print(table)
    console.print("\n[dim]Use 'maos config completion --install --shell <shell>' to install[/dim]")


def _show_config_examples():
    """Show configuration examples."""
    examples = {
        "Basic Configuration": """
logging:
  enabled: true
  level: INFO
  structured: true

storage:
  directory: ~/.maos/storage

system:
  max_agents: 10
  agent_timeout: 300

monitoring:
  enabled: true
  refresh_interval: 1.0
        """.strip(),
        
        "Production Configuration": """
logging:
  enabled: true
  level: WARNING
  file: /var/log/maos.log
  structured: true

storage:
  directory: /opt/maos/storage
  backup_directory: /opt/maos/backups

redis:
  enabled: true
  url: redis://localhost:6379
  db: 0

system:
  max_agents: 100
  agent_timeout: 600
  checkpoint_interval: 300
  auto_recovery: true

resources:
  default_cpu_limit: 4.0
  default_memory_limit: 8192
  allocation_strategy: priority

monitoring:
  enabled: true
  export_metrics: true
  prometheus_port: 9090
        """.strip(),
        
        "Development Configuration": """
logging:
  enabled: true
  level: DEBUG
  console_output: true

storage:
  directory: ./dev_storage

system:
  max_agents: 5
  health_check_interval: 10

monitoring:
  enabled: true
  refresh_interval: 0.5
  history_size: 50

output:
  color_output: true
  progress_bars: true
  verbose_errors: true
        """.strip()
    }
    
    console.print("[bold blue]Configuration Examples:[/bold blue]\n")
    
    for title, example in examples.items():
        console.print(Panel(
            Syntax(example, "yaml", theme="monokai"),
            title=title,
            border_style="cyan",
            expand=False
        ))
        console.print()


def _fix_configuration_issues(config: CLIConfig, issues: List[str]) -> Optional[CLIConfig]:
    """Attempt to fix configuration issues automatically."""
    fixed = False
    
    for issue in issues:
        if "Cannot create storage directory" in issue:
            # Try to create storage directory
            try:
                config.storage.directory.mkdir(parents=True, exist_ok=True)
                console.print(f"[green]✓ Created storage directory: {config.storage.directory}[/green]")
                fixed = True
            except Exception as e:
                console.print(f"[red]Could not create storage directory: {e}[/red]")
        
        elif "max_agents must be greater than 0" in issue:
            config.system.max_agents = 10
            console.print(f"[green]✓ Set max_agents to 10[/green]")
            fixed = True
        
        elif "agent_timeout must be greater than 0" in issue:
            config.system.agent_timeout = 300
            console.print(f"[green]✓ Set agent_timeout to 300 seconds[/green]")
            fixed = True
        
        # Add more automatic fixes as needed
    
    return config if fixed else None