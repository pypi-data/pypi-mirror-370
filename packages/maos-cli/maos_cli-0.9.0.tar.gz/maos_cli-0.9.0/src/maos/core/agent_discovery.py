"""
Agent Discovery System - Dynamically discovers available Claude Code agents
"""

import asyncio
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AgentInfo:
    """Information about a discovered agent"""
    name: str
    source: str  # 'claude-code', 'local', 'builtin', 'mcp'
    description: str
    capabilities: List[str]
    file_path: Optional[str] = None
    is_specialized: bool = False
    last_discovered: str = ""
    
    def __post_init__(self):
        if not self.last_discovered:
            self.last_discovered = datetime.now().isoformat()


class AgentDiscovery:
    """
    Discovers available agents from multiple sources:
    1. .claude/agents/ directory (local custom agents)
    2. Claude Code built-in agents
    3. Known MAOS agent mappings
    4. MCP agents if configured
    """
    
    def __init__(self, cache_duration: int = 300):
        """
        Initialize agent discovery.
        
        Args:
            cache_duration: How long to cache discovered agents (seconds)
        """
        self.cache_duration = cache_duration
        self._cache: Dict[str, AgentInfo] = {}
        self._last_scan: Optional[datetime] = None
        self._known_claude_agents = {
            "security-auditor": {
                "description": "Security specialist for vulnerability assessment and security hardening",
                "capabilities": ["vulnerability-scan", "security-review", "threat-modeling", "security-fixes"]
            },
            "reviewer": {
                "description": "Code review specialist for quality, security, and best practices",
                "capabilities": ["code-review", "quality-check", "best-practices", "performance-review"]
            },
            "agent-162719-2": {
                "description": "General-purpose agent for various tasks",
                "capabilities": ["general", "read", "write", "edit", "bash", "grep", "glob"]
            }
        }
    
    async def scan_available_agents(self, force_refresh: bool = False) -> List[AgentInfo]:
        """
        Scan all sources for available agents.
        
        Args:
            force_refresh: Force a fresh scan even if cache is valid
            
        Returns:
            List of discovered agents
        """
        # Check cache validity
        if not force_refresh and self._is_cache_valid():
            logger.info(f"Using cached agents ({len(self._cache)} agents)")
            return list(self._cache.values())
        
        logger.info("Starting agent discovery scan...")
        agents = []
        
        # 1. Scan .claude/agents/ directory
        local_agents = await self._scan_local_agents()
        agents.extend(local_agents)
        logger.info(f"Found {len(local_agents)} local agents")
        
        # 2. Check Claude Code built-in agents
        claude_agents = await self._get_claude_code_agents()
        agents.extend(claude_agents)
        logger.info(f"Found {len(claude_agents)} Claude Code agents")
        
        # 3. Add known built-in agents
        builtin_agents = self._get_builtin_agents()
        agents.extend(builtin_agents)
        logger.info(f"Added {len(builtin_agents)} built-in agents")
        
        # 4. Check for MCP agents if available
        mcp_agents = await self._scan_mcp_agents()
        agents.extend(mcp_agents)
        if mcp_agents:
            logger.info(f"Found {len(mcp_agents)} MCP agents")
        
        # Update cache
        self._cache = {agent.name: agent for agent in agents}
        self._last_scan = datetime.now()
        
        logger.info(f"Agent discovery complete: {len(agents)} total agents found")
        return agents
    
    async def _scan_local_agents(self) -> List[AgentInfo]:
        """Scan .claude/agents/ directory for custom agents."""
        agents = []
        agents_dir = Path(".claude/agents")
        
        if not agents_dir.exists():
            logger.debug(".claude/agents directory not found")
            return agents
        
        # Scan for agent files (could be .md, .yaml, .json)
        for pattern in ["*.md", "*.yaml", "*.yml", "*.json"]:
            for agent_file in agents_dir.glob(pattern):
                try:
                    agent_info = self._parse_agent_file(agent_file)
                    if agent_info:
                        agents.append(agent_info)
                        logger.debug(f"Discovered local agent: {agent_info.name}")
                except Exception as e:
                    logger.warning(f"Failed to parse agent file {agent_file}: {e}")
        
        return agents
    
    def _parse_agent_file(self, file_path: Path) -> Optional[AgentInfo]:
        """Parse an agent definition file."""
        try:
            content = file_path.read_text()
            agent_name = file_path.stem
            
            # Extract description and capabilities from content
            description = "Custom local agent"
            capabilities = []
            
            if file_path.suffix == '.md':
                # Parse markdown format
                description = self._extract_md_description(content)
                capabilities = self._extract_md_capabilities(content)
            elif file_path.suffix in ['.yaml', '.yml']:
                import yaml
                data = yaml.safe_load(content)
                description = data.get('description', description)
                capabilities = data.get('capabilities', [])
                agent_name = data.get('name', agent_name)
            elif file_path.suffix == '.json':
                data = json.loads(content)
                description = data.get('description', description)
                capabilities = data.get('capabilities', [])
                agent_name = data.get('name', agent_name)
            
            return AgentInfo(
                name=agent_name,
                source='local',
                description=description,
                capabilities=capabilities or ['general'],
                file_path=str(file_path),
                is_specialized=True
            )
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return None
    
    def _extract_md_description(self, content: str) -> str:
        """Extract description from markdown content."""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('#'):
                # Use first heading as description
                return line.strip('#').strip()
        return "Custom agent"
    
    def _extract_md_capabilities(self, content: str) -> List[str]:
        """Extract capabilities from markdown content."""
        capabilities = []
        in_capabilities = False
        
        for line in content.split('\n'):
            if 'capabilities' in line.lower() or 'features' in line.lower():
                in_capabilities = True
            elif in_capabilities and line.strip().startswith('-'):
                cap = line.strip('- ').strip()
                if cap:
                    capabilities.append(cap.lower().replace(' ', '-'))
        
        return capabilities[:10]  # Limit to 10 capabilities
    
    async def _get_claude_code_agents(self) -> List[AgentInfo]:
        """Get Claude Code built-in agents."""
        agents = []
        
        # Try to get agent list from Claude CLI (if available in future versions)
        try:
            result = subprocess.run(
                ["claude", "--list-agents"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                # Parse the output if the command exists
                return self._parse_claude_agents_output(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass
        
        # Fall back to known agents
        for name, info in self._known_claude_agents.items():
            agents.append(AgentInfo(
                name=name,
                source='claude-code',
                description=info['description'],
                capabilities=info['capabilities'],
                is_specialized=True
            ))
        
        return agents
    
    def _parse_claude_agents_output(self, output: str) -> List[AgentInfo]:
        """Parse Claude CLI agent list output."""
        agents = []
        # This would parse the actual output format when available
        # For now, return empty list as the command doesn't exist yet
        return agents
    
    def _get_builtin_agents(self) -> List[AgentInfo]:
        """Get MAOS built-in agent types."""
        builtin = [
            AgentInfo(
                name="analyst",
                source='builtin',
                description="General analysis and code understanding",
                capabilities=["analyze", "explain", "document", "understand"],
                is_specialized=False
            ),
            AgentInfo(
                name="developer",
                source='builtin',
                description="Code development and implementation",
                capabilities=["implement", "code", "build", "create", "fix"],
                is_specialized=False
            ),
            AgentInfo(
                name="tester",
                source='builtin',
                description="Testing and validation",
                capabilities=["test", "validate", "verify", "qa"],
                is_specialized=False
            ),
            AgentInfo(
                name="researcher",
                source='builtin',
                description="Research and information gathering",
                capabilities=["research", "investigate", "explore", "find"],
                is_specialized=False
            ),
            AgentInfo(
                name="documenter",
                source='builtin',
                description="Documentation and technical writing",
                capabilities=["document", "write", "explain", "readme"],
                is_specialized=False
            )
        ]
        return builtin
    
    async def _scan_mcp_agents(self) -> List[AgentInfo]:
        """Scan for MCP (Model Context Protocol) agents if configured."""
        agents = []
        
        # Check if MCP is configured
        mcp_config_path = Path(".claude/mcp_servers.json")
        if not mcp_config_path.exists():
            return agents
        
        try:
            config = json.loads(mcp_config_path.read_text())
            for server_name, server_config in config.get("servers", {}).items():
                # Create agent info for each MCP server
                agents.append(AgentInfo(
                    name=f"mcp-{server_name}",
                    source='mcp',
                    description=f"MCP server: {server_name}",
                    capabilities=["mcp", "integration", server_name],
                    is_specialized=True
                ))
        except Exception as e:
            logger.warning(f"Failed to parse MCP config: {e}")
        
        return agents
    
    def _is_cache_valid(self) -> bool:
        """Check if the agent cache is still valid."""
        if not self._last_scan or not self._cache:
            return False
        
        age = (datetime.now() - self._last_scan).total_seconds()
        return age < self.cache_duration
    
    def get_agent_by_name(self, name: str) -> Optional[AgentInfo]:
        """Get a specific agent by name."""
        return self._cache.get(name)
    
    def get_agents_by_capability(self, capability: str) -> List[AgentInfo]:
        """Get all agents with a specific capability."""
        return [
            agent for agent in self._cache.values()
            if capability in agent.capabilities
        ]
    
    def get_specialized_agents(self) -> List[AgentInfo]:
        """Get all specialized agents (Claude Code or custom)."""
        return [
            agent for agent in self._cache.values()
            if agent.is_specialized
        ]
    
    async def refresh_cache(self) -> None:
        """Force refresh the agent cache."""
        await self.scan_available_agents(force_refresh=True)
    
    def to_json(self) -> str:
        """Export discovered agents as JSON."""
        agents_dict = {
            name: asdict(agent) 
            for name, agent in self._cache.items()
        }
        return json.dumps(agents_dict, indent=2)
    
    def print_summary(self) -> None:
        """Print a summary of discovered agents."""
        if not self._cache:
            print("No agents discovered yet. Run scan_available_agents() first.")
            return
        
        print(f"\n🤖 Discovered Agents Summary")
        print("=" * 50)
        
        by_source = {}
        for agent in self._cache.values():
            if agent.source not in by_source:
                by_source[agent.source] = []
            by_source[agent.source].append(agent)
        
        for source, agents in by_source.items():
            print(f"\n{source.upper()} ({len(agents)} agents):")
            for agent in agents:
                specialized = "⭐" if agent.is_specialized else "  "
                print(f"  {specialized} {agent.name}: {agent.description[:50]}...")
                if agent.capabilities:
                    print(f"      Capabilities: {', '.join(agent.capabilities[:5])}")
        
        print(f"\nTotal: {len(self._cache)} agents available")