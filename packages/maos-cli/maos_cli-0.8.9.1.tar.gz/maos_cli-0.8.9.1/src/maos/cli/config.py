"""
MAOS CLI Configuration Management

Handles CLI configuration loading, validation, and management
with YAML support and environment variable overrides.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field

import yaml
from rich.console import Console

console = Console()


@dataclass
class LoggingConfig:
    """Logging configuration."""
    enabled: bool = True
    level: str = "INFO"
    file: Optional[str] = None
    structured: bool = True
    console_output: bool = True


@dataclass
class StorageConfig:
    """Storage configuration."""
    directory: Path = field(default_factory=lambda: Path.home() / ".maos" / "storage")
    backup_directory: Optional[Path] = None
    cleanup_interval: int = 3600  # seconds
    max_storage_size: Optional[int] = None  # bytes


@dataclass
class RedisConfig:
    """Redis configuration."""
    enabled: bool = False
    url: str = "redis://localhost:6379"
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False
    connection_pool_size: int = 10


@dataclass
class SystemConfig:
    """System-level configuration."""
    max_agents: int = 100
    agent_timeout: int = 300
    task_timeout: int = 3600
    checkpoint_interval: int = 300
    max_checkpoints: int = 50
    health_check_interval: int = 30
    auto_recovery: bool = True


@dataclass
class ResourcesConfig:
    """Resource management configuration."""
    default_cpu_limit: float = 2.0
    default_memory_limit: int = 4096  # MB
    default_disk_limit: int = 10240  # MB
    allocation_strategy: str = "fair"  # fair, priority, greedy
    resource_monitoring: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring and metrics configuration."""
    enabled: bool = True
    refresh_interval: float = 1.0
    history_size: int = 1000
    export_metrics: bool = False
    prometheus_port: Optional[int] = None


@dataclass
class OutputConfig:
    """Output formatting configuration."""
    default_format: str = "table"
    color_output: bool = True
    progress_bars: bool = True
    timestamps: bool = True
    verbose_errors: bool = True


@dataclass
class CLIConfig:
    """Main CLI configuration."""
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    system: SystemConfig = field(default_factory=SystemConfig)
    resources: ResourcesConfig = field(default_factory=ResourcesConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CLIConfig":
        """Create config from dictionary."""
        # Process nested configurations
        config = cls()
        
        if "logging" in data:
            config.logging = LoggingConfig(**data["logging"])
        
        if "storage" in data:
            storage_data = data["storage"].copy()
            if "directory" in storage_data:
                storage_data["directory"] = Path(storage_data["directory"])
            if "backup_directory" in storage_data and storage_data["backup_directory"]:
                storage_data["backup_directory"] = Path(storage_data["backup_directory"])
            config.storage = StorageConfig(**storage_data)
        
        if "redis" in data:
            config.redis = RedisConfig(**data["redis"])
        
        if "system" in data:
            config.system = SystemConfig(**data["system"])
        
        if "resources" in data:
            config.resources = ResourcesConfig(**data["resources"])
        
        if "monitoring" in data:
            config.monitoring = MonitoringConfig(**data["monitoring"])
        
        if "output" in data:
            config.output = OutputConfig(**data["output"])
        
        return config


def get_config_paths() -> List[Path]:
    """Get possible configuration file paths in order of priority."""
    paths = []
    
    # 1. Environment variable
    if env_path := os.environ.get("MAOS_CONFIG"):
        paths.append(Path(env_path))
    
    # 2. Current directory
    paths.extend([
        Path.cwd() / ".maos.yml",
        Path.cwd() / ".maos.yaml",
        Path.cwd() / "maos.yml",
        Path.cwd() / "maos.yaml"
    ])
    
    # 3. Home directory
    home = Path.home()
    paths.extend([
        home / ".maos.yml",
        home / ".maos.yaml",
        home / ".config" / "maos" / "config.yml",
        home / ".config" / "maos" / "config.yaml"
    ])
    
    # 4. System directories
    paths.extend([
        Path("/etc/maos/config.yml"),
        Path("/etc/maos/config.yaml")
    ])
    
    return paths


def load_config(config_path: Optional[str] = None) -> CLIConfig:
    """Load configuration from file with environment variable overrides."""
    config = CLIConfig()
    
    # Determine config file path
    if config_path:
        config_file = Path(config_path)
        if not config_file.exists():
            console.print(f"[red]Warning: Config file {config_path} not found[/red]")
            return config
    else:
        # Find first existing config file
        config_file = None
        for path in get_config_paths():
            if path.exists():
                config_file = path
                break
        
        if not config_file:
            # No config file found, use defaults
            return config
    
    try:
        # Load YAML configuration
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f) or {}
        
        config = CLIConfig.from_dict(config_data)
        
        # Apply environment variable overrides
        _apply_env_overrides(config)
        
    except Exception as e:
        console.print(f"[red]Error loading config from {config_file}: {e}[/red]")
        return CLIConfig()  # Return default config on error
    
    return config


def save_config(config: CLIConfig, config_path: Optional[str] = None) -> bool:
    """Save configuration to file."""
    if not config_path:
        # Use first writable location
        for path in get_config_paths()[:4]:  # Skip system paths
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                config_path = str(path)
                break
            except PermissionError:
                continue
        
        if not config_path:
            console.print("[red]Error: No writable config location found[/red]")
            return False
    
    try:
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert config to dict and handle Path objects
        config_dict = config.to_dict()
        _prepare_config_for_yaml(config_dict)
        
        with open(config_file, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        
        console.print(f"[green]Configuration saved to {config_path}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Error saving config: {e}[/red]")
        return False


def _apply_env_overrides(config: CLIConfig) -> None:
    """Apply environment variable overrides to configuration."""
    # Mapping of environment variables to config paths
    env_mappings = {
        "MAOS_LOG_LEVEL": ("logging", "level"),
        "MAOS_LOG_FILE": ("logging", "file"),
        "MAOS_STORAGE_DIR": ("storage", "directory"),
        "MAOS_REDIS_URL": ("redis", "url"),
        "MAOS_REDIS_ENABLED": ("redis", "enabled"),
        "MAOS_MAX_AGENTS": ("system", "max_agents"),
        "MAOS_CHECKPOINT_INTERVAL": ("system", "checkpoint_interval"),
        "MAOS_DEFAULT_CPU_LIMIT": ("resources", "default_cpu_limit"),
        "MAOS_DEFAULT_MEMORY_LIMIT": ("resources", "default_memory_limit"),
        "MAOS_MONITORING_ENABLED": ("monitoring", "enabled"),
        "MAOS_OUTPUT_FORMAT": ("output", "default_format"),
    }
    
    for env_var, (section, key) in env_mappings.items():
        if value := os.environ.get(env_var):
            section_obj = getattr(config, section)
            
            # Type conversion based on current value type
            current_value = getattr(section_obj, key)
            if isinstance(current_value, bool):
                value = value.lower() in ('true', '1', 'yes', 'on')
            elif isinstance(current_value, int):
                value = int(value)
            elif isinstance(current_value, float):
                value = float(value)
            elif isinstance(current_value, Path):
                value = Path(value)
            
            setattr(section_obj, key, value)


def _prepare_config_for_yaml(config_dict: Dict[str, Any]) -> None:
    """Prepare configuration dictionary for YAML serialization."""
    def convert_paths(obj):
        if isinstance(obj, dict):
            return {k: convert_paths(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_paths(item) for item in obj]
        elif isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, set):
            return list(obj)
        else:
            return obj
    
    # Convert in-place
    for key, value in config_dict.items():
        config_dict[key] = convert_paths(value)


def create_default_config() -> str:
    """Create a default configuration file content."""
    default_config = CLIConfig()
    config_dict = default_config.to_dict()
    _prepare_config_for_yaml(config_dict)
    
    return yaml.dump(config_dict, default_flow_style=False, indent=2)


def validate_config(config: CLIConfig) -> List[str]:
    """Validate configuration and return list of issues."""
    issues = []
    
    # Validate storage directory
    try:
        config.storage.directory.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        issues.append(f"Cannot create storage directory: {config.storage.directory}")
    
    # Validate Redis configuration
    if config.redis.enabled:
        if not config.redis.url:
            issues.append("Redis is enabled but no URL provided")
    
    # Validate system limits
    if config.system.max_agents <= 0:
        issues.append("max_agents must be greater than 0")
    
    if config.system.agent_timeout <= 0:
        issues.append("agent_timeout must be greater than 0")
    
    # Validate resource limits
    if config.resources.default_cpu_limit <= 0:
        issues.append("default_cpu_limit must be greater than 0")
    
    if config.resources.default_memory_limit <= 0:
        issues.append("default_memory_limit must be greater than 0")
    
    # Validate monitoring
    if config.monitoring.refresh_interval <= 0:
        issues.append("monitoring refresh_interval must be greater than 0")
    
    return issues