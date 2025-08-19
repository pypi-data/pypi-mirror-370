"""
MAOS Configuration Management
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class DecomposerConfig:
    """Configuration for task decomposition"""
    mode: str = "intelligent"  # "intelligent", "rule-based", "hybrid"
    show_orchestrator_prompt: bool = True
    show_reasoning: bool = True
    show_execution_plan: bool = True
    
    # Intelligent mode settings
    model: str = "claude-3-opus"
    temperature: float = 0.3
    max_analysis_time: int = 10  # seconds
    cache_decompositions: bool = True
    
    # Agent discovery settings
    scan_on_startup: bool = True
    scan_interval: int = 300  # seconds
    agent_sources: list = None
    
    def __post_init__(self):
        if self.agent_sources is None:
            self.agent_sources = [".claude/agents", "claude-code-builtin", "maos-templates"]


@dataclass
class OrchestrationConfig:
    """Configuration for orchestration"""
    auto_approve: bool = False
    max_parallel_agents: int = 10
    agent_timeout: int = 600  # 10 minutes
    auto_save_interval: int = 30  # seconds
    checkpoint_interval: int = 120  # seconds
    show_agent_output: bool = True
    verbose: bool = False


@dataclass
class MAOSConfig:
    """Main MAOS configuration"""
    decomposer: DecomposerConfig = None
    orchestration: OrchestrationConfig = None
    database_path: str = "./maos.db"
    log_level: str = "INFO"
    
    def __post_init__(self):
        if self.decomposer is None:
            self.decomposer = DecomposerConfig()
        if self.orchestration is None:
            self.orchestration = OrchestrationConfig()


class ConfigManager:
    """Manages MAOS configuration from multiple sources"""
    
    CONFIG_SOURCES = [
        ".maos/config.yaml",
        ".maos/config.json",
        "~/.maos/config.yaml",
        "~/.maos/config.json",
        "/etc/maos/config.yaml"
    ]
    
    def __init__(self):
        self.config = MAOSConfig()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from files and environment variables"""
        
        # 1. Load from config files
        for config_path in self.CONFIG_SOURCES:
            path = Path(config_path).expanduser()
            if path.exists():
                logger.info(f"Loading config from {path}")
                self._load_config_file(path)
                break
        
        # 2. Override with environment variables
        self._load_env_vars()
        
        # 3. Validate configuration
        self._validate_config()
    
    def _load_config_file(self, path: Path):
        """Load configuration from a file"""
        try:
            content = path.read_text()
            
            if path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(content)
            elif path.suffix == '.json':
                data = json.loads(content)
            else:
                logger.warning(f"Unknown config file format: {path}")
                return
            
            # Update decomposer config
            if 'decomposer' in data:
                for key, value in data['decomposer'].items():
                    if hasattr(self.config.decomposer, key):
                        setattr(self.config.decomposer, key, value)
            
            # Update orchestration config
            if 'orchestration' in data:
                for key, value in data['orchestration'].items():
                    if hasattr(self.config.orchestration, key):
                        setattr(self.config.orchestration, key, value)
            
            # Update main config
            for key in ['database_path', 'log_level']:
                if key in data:
                    setattr(self.config, key, data[key])
                    
        except Exception as e:
            logger.error(f"Failed to load config from {path}: {e}")
    
    def _load_env_vars(self):
        """Load configuration from environment variables"""
        
        # Decomposer settings
        if os.getenv('MAOS_DECOMPOSER_MODE'):
            self.config.decomposer.mode = os.getenv('MAOS_DECOMPOSER_MODE')
        
        if os.getenv('MAOS_SHOW_REASONING'):
            self.config.decomposer.show_reasoning = os.getenv('MAOS_SHOW_REASONING').lower() == 'true'
        
        if os.getenv('MAOS_TEMPERATURE'):
            self.config.decomposer.temperature = float(os.getenv('MAOS_TEMPERATURE'))
        
        # Orchestration settings
        if os.getenv('MAOS_AUTO_APPROVE'):
            self.config.orchestration.auto_approve = os.getenv('MAOS_AUTO_APPROVE').lower() == 'true'
        
        if os.getenv('MAOS_MAX_PARALLEL_AGENTS'):
            self.config.orchestration.max_parallel_agents = int(os.getenv('MAOS_MAX_PARALLEL_AGENTS'))
        
        # Database path
        if os.getenv('MAOS_DATABASE_PATH'):
            self.config.database_path = os.getenv('MAOS_DATABASE_PATH')
        
        # Log level
        if os.getenv('MAOS_LOG_LEVEL'):
            self.config.log_level = os.getenv('MAOS_LOG_LEVEL')
    
    def _validate_config(self):
        """Validate configuration values"""
        
        # Validate decomposer mode
        valid_modes = ["intelligent", "rule-based", "hybrid"]
        if self.config.decomposer.mode not in valid_modes:
            logger.warning(f"Invalid decomposer mode: {self.config.decomposer.mode}, using 'intelligent'")
            self.config.decomposer.mode = "intelligent"
        
        # Validate temperature
        if not 0 <= self.config.decomposer.temperature <= 1:
            logger.warning(f"Invalid temperature: {self.config.decomposer.temperature}, using 0.3")
            self.config.decomposer.temperature = 0.3
        
        # Validate timeouts
        if self.config.orchestration.agent_timeout < 60:
            logger.warning("Agent timeout too low, setting to 60 seconds")
            self.config.orchestration.agent_timeout = 60
    
    def get_decomposer_config(self) -> DecomposerConfig:
        """Get decomposer configuration"""
        return self.config.decomposer
    
    def get_orchestration_config(self) -> OrchestrationConfig:
        """Get orchestration configuration"""
        return self.config.orchestration
    
    def get_database_path(self) -> str:
        """Get database path"""
        return self.config.database_path
    
    def use_intelligent_decomposer(self) -> bool:
        """Check if intelligent decomposer should be used"""
        return self.config.decomposer.mode in ["intelligent", "hybrid"]
    
    def save_config(self, path: Optional[Path] = None):
        """Save current configuration to file"""
        if path is None:
            path = Path(".maos/config.yaml")
        
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dictionary
        config_dict = {
            'decomposer': asdict(self.config.decomposer),
            'orchestration': asdict(self.config.orchestration),
            'database_path': self.config.database_path,
            'log_level': self.config.log_level
        }
        
        # Save based on extension
        if path.suffix in ['.yaml', '.yml']:
            with open(path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False)
        else:
            with open(path, 'w') as f:
                json.dump(config_dict, f, indent=2)
        
        logger.info(f"Configuration saved to {path}")
    
    def create_default_config(self):
        """Create a default configuration file"""
        default_path = Path(".maos/config.yaml")
        
        if default_path.exists():
            logger.info("Config file already exists")
            return
        
        # Create directory
        default_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Default configuration
        default_config = """# MAOS Configuration File
# Generated automatically - customize as needed

decomposer:
  mode: "intelligent"              # Options: intelligent, rule-based, hybrid
  show_orchestrator_prompt: true   # Show the prompt sent to Claude
  show_reasoning: true             # Show Claude's reasoning
  show_execution_plan: true        # Show the execution plan
  
  # Claude settings for intelligent mode
  model: "claude-3-opus"
  temperature: 0.3                 # Lower = more consistent
  max_analysis_time: 10            # Timeout in seconds
  cache_decompositions: true       # Cache results for similar requests
  
  # Agent discovery
  scan_on_startup: true
  scan_interval: 300               # Rescan every 5 minutes
  agent_sources:
    - ".claude/agents"             # Local custom agents
    - "claude-code-builtin"        # Claude Code agents
    - "maos-templates"             # MAOS built-in templates

orchestration:
  auto_approve: false              # Skip confirmation prompts
  max_parallel_agents: 10          # Max agents running simultaneously
  agent_timeout: 600               # 10 minutes per agent
  auto_save_interval: 30           # Save progress every 30 seconds
  checkpoint_interval: 120         # Create checkpoint every 2 minutes
  show_agent_output: true          # Display agent output
  verbose: false                   # Extra logging

database_path: "./maos.db"        # SQLite database location
log_level: "INFO"                  # DEBUG, INFO, WARNING, ERROR
"""
        
        default_path.write_text(default_config)
        logger.info(f"Created default config at {default_path}")
        print(f"✅ Created default configuration at {default_path}")
        print("   Edit this file to customize MAOS behavior")


# Global config instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get the global configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reset_config():
    """Reset the global configuration (mainly for testing)"""
    global _config_manager
    _config_manager = None