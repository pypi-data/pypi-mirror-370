"""Agent registration and discovery service."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent status states."""
    REGISTERING = "registering"
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    ERROR = "error"


class AgentCapability(Enum):
    """Standard agent capabilities."""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    AI_INFERENCE = "ai_inference"
    DATA_PROCESSING = "data_processing"
    TASK_ORCHESTRATION = "task_orchestration"
    CONSENSUS = "consensus"
    MONITORING = "monitoring"
    SECURITY = "security"
    COMMUNICATION = "communication"


@dataclass
class AgentInfo:
    """Complete agent information."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: str = "generic"  # agent type/category
    version: str = "1.0.0"
    status: AgentStatus = AgentStatus.REGISTERING
    capabilities: Set[AgentCapability] = field(default_factory=set)
    
    # Contact information
    endpoints: Dict[str, str] = field(default_factory=dict)  # protocol -> endpoint
    topics: Set[str] = field(default_factory=set)  # subscribed topics
    
    # Resource information
    resources: Dict[str, Any] = field(default_factory=dict)  # cpu, memory, etc.
    load: Dict[str, float] = field(default_factory=dict)  # current load metrics
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    
    # Timestamps
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    
    # Configuration
    heartbeat_interval: int = 30  # seconds
    timeout_threshold: int = 90  # seconds
    
    def is_online(self) -> bool:
        """Check if agent is considered online."""
        if self.status == AgentStatus.OFFLINE:
            return False
        
        timeout = timedelta(seconds=self.timeout_threshold)
        return datetime.utcnow() - self.last_heartbeat < timeout
    
    def is_available(self) -> bool:
        """Check if agent is available for new tasks."""
        return self.is_online() and self.status in [
            AgentStatus.ACTIVE, 
            AgentStatus.IDLE
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "version": self.version,
            "status": self.status.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "endpoints": self.endpoints,
            "topics": list(self.topics),
            "resources": self.resources,
            "load": self.load,
            "metadata": self.metadata,
            "tags": list(self.tags),
            "registered_at": self.registered_at.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "heartbeat_interval": self.heartbeat_interval,
            "timeout_threshold": self.timeout_threshold,
            "is_online": self.is_online(),
            "is_available": self.is_available()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentInfo":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            version=data["version"],
            status=AgentStatus(data["status"]),
            capabilities={AgentCapability(cap) for cap in data.get("capabilities", [])},
            endpoints=data.get("endpoints", {}),
            topics=set(data.get("topics", [])),
            resources=data.get("resources", {}),
            load=data.get("load", {}),
            metadata=data.get("metadata", {}),
            tags=set(data.get("tags", [])),
            registered_at=datetime.fromisoformat(data["registered_at"]),
            last_seen=datetime.fromisoformat(data["last_seen"]),
            last_heartbeat=datetime.fromisoformat(data["last_heartbeat"]),
            heartbeat_interval=data.get("heartbeat_interval", 30),
            timeout_threshold=data.get("timeout_threshold", 90)
        )


@dataclass
class RegistrationRequest:
    """Agent registration request."""
    agent_info: AgentInfo
    auth_token: Optional[str] = None
    registration_data: Dict[str, Any] = field(default_factory=dict)
    requested_at: datetime = field(default_factory=datetime.utcnow)


class AgentRegistry:
    """Manages agent registration and discovery."""
    
    def __init__(
        self,
        max_agents: int = 10000,
        cleanup_interval: int = 60,
        heartbeat_timeout: int = 90
    ):
        self.max_agents = max_agents
        self.cleanup_interval = cleanup_interval
        self.heartbeat_timeout = heartbeat_timeout
        
        # Agent storage
        self.agents: Dict[str, AgentInfo] = {}
        self.agents_by_type: Dict[str, Set[str]] = {}
        self.agents_by_capability: Dict[AgentCapability, Set[str]] = {}
        self.agents_by_status: Dict[AgentStatus, Set[str]] = {}
        
        # Registration requests
        self.pending_registrations: Dict[str, RegistrationRequest] = {}
        
        # Event callbacks
        self.registration_callbacks: List[callable] = []
        self.status_change_callbacks: List[callable] = []
        self.offline_callbacks: List[callable] = []
        
        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        self.heartbeat_monitor_task: Optional[asyncio.Task] = None
        
        # Metrics
        self.metrics = {
            "total_registrations": 0,
            "active_agents": 0,
            "offline_agents": 0,
            "registration_failures": 0,
            "heartbeat_timeouts": 0
        }
        
        # Status
        self.is_running = False
        
        logger.info("Agent registry initialized")
    
    async def start(self):
        """Start the agent registry."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start background tasks
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.heartbeat_monitor_task = asyncio.create_task(self._heartbeat_monitor())
        
        logger.info("Agent registry started")
    
    async def stop(self):
        """Stop the agent registry."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel background tasks
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self.heartbeat_monitor_task:
            self.heartbeat_monitor_task.cancel()
            try:
                await self.heartbeat_monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Agent registry stopped")
    
    async def register_agent(
        self,
        agent_info: AgentInfo,
        auth_token: Optional[str] = None
    ) -> bool:
        """Register a new agent."""
        try:
            # Check limits
            if len(self.agents) >= self.max_agents:
                logger.warning("Maximum agent limit reached")
                return False
            
            # Validate agent info
            if not agent_info.id or not agent_info.name:
                logger.warning("Invalid agent info: missing id or name")
                return False
            
            # Check for duplicate ID
            if agent_info.id in self.agents:
                logger.warning(f"Agent {agent_info.id} already registered")
                return False
            
            # Update registration timestamp
            agent_info.registered_at = datetime.utcnow()
            agent_info.last_seen = datetime.utcnow()
            agent_info.last_heartbeat = datetime.utcnow()
            agent_info.status = AgentStatus.ACTIVE
            
            # Store agent
            self.agents[agent_info.id] = agent_info
            
            # Update indexes
            await self._update_indexes(agent_info.id, agent_info)
            
            # Update metrics
            self.metrics["total_registrations"] += 1
            self.metrics["active_agents"] += 1
            
            # Trigger callbacks
            await self._trigger_registration_callbacks(agent_info)
            
            logger.info(f"Registered agent {agent_info.id} ({agent_info.name})")
            return True
            
        except Exception as e:
            self.metrics["registration_failures"] += 1
            logger.error(f"Failed to register agent: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent."""
        try:
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            
            # Remove from indexes
            await self._remove_from_indexes(agent_id, agent)
            
            # Remove agent
            del self.agents[agent_id]
            
            # Update metrics
            self.metrics["active_agents"] = max(0, self.metrics["active_agents"] - 1)
            
            logger.info(f"Unregistered agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False
    
    async def update_agent_status(
        self,
        agent_id: str,
        status: AgentStatus,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update agent status."""
        try:
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            old_status = agent.status
            
            # Update status
            agent.status = status
            agent.last_seen = datetime.utcnow()
            
            if status != AgentStatus.OFFLINE:
                agent.last_heartbeat = datetime.utcnow()
            
            # Update metadata if provided
            if metadata:
                agent.metadata.update(metadata)
            
            # Update indexes
            await self._update_status_index(agent_id, old_status, status)
            
            # Trigger callbacks if status changed
            if old_status != status:
                await self._trigger_status_change_callbacks(agent, old_status, status)
            
            logger.debug(f"Updated status for agent {agent_id}: {old_status.value} -> {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update agent status: {e}")
            return False
    
    async def heartbeat(
        self,
        agent_id: str,
        metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Process agent heartbeat."""
        try:
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            agent.last_heartbeat = datetime.utcnow()
            agent.last_seen = datetime.utcnow()
            
            # Update load metrics if provided
            if metrics:
                agent.load.update(metrics)
            
            # If agent was offline, bring it back online
            if agent.status == AgentStatus.OFFLINE:
                await self.update_agent_status(agent_id, AgentStatus.ACTIVE)
            
            logger.debug(f"Received heartbeat from agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process heartbeat: {e}")
            return False
    
    async def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent information by ID."""
        return self.agents.get(agent_id)
    
    async def find_agents(
        self,
        agent_type: Optional[str] = None,
        capabilities: Optional[List[AgentCapability]] = None,
        status: Optional[AgentStatus] = None,
        tags: Optional[List[str]] = None,
        available_only: bool = False,
        limit: Optional[int] = None
    ) -> List[AgentInfo]:
        """Find agents matching criteria."""
        try:
            matching_agents = []
            
            # Start with all agents or filter by status
            if status:
                candidate_ids = self.agents_by_status.get(status, set())
                candidates = [self.agents[aid] for aid in candidate_ids if aid in self.agents]
            else:
                candidates = list(self.agents.values())
            
            for agent in candidates:
                # Filter by type
                if agent_type and agent.type != agent_type:
                    continue
                
                # Filter by capabilities
                if capabilities:
                    if not all(cap in agent.capabilities for cap in capabilities):
                        continue
                
                # Filter by tags
                if tags:
                    if not all(tag in agent.tags for tag in tags):
                        continue
                
                # Filter by availability
                if available_only and not agent.is_available():
                    continue
                
                matching_agents.append(agent)
            
            # Apply limit
            if limit:
                matching_agents = matching_agents[:limit]
            
            # Sort by last seen (most recent first)
            matching_agents.sort(key=lambda a: a.last_seen, reverse=True)
            
            return matching_agents
            
        except Exception as e:
            logger.error(f"Failed to find agents: {e}")
            return []
    
    async def get_agents_by_capability(self, capability: AgentCapability) -> List[AgentInfo]:
        """Get all agents with a specific capability."""
        agent_ids = self.agents_by_capability.get(capability, set())
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]
    
    async def get_available_agents(self) -> List[AgentInfo]:
        """Get all available agents."""
        return await self.find_agents(available_only=True)
    
    async def get_agent_count_by_status(self) -> Dict[str, int]:
        """Get count of agents by status."""
        counts = {}
        for status in AgentStatus:
            count = len(self.agents_by_status.get(status, set()))
            counts[status.value] = count
        return counts
    
    async def get_agent_count_by_type(self) -> Dict[str, int]:
        """Get count of agents by type."""
        counts = {}
        for agent_type, agent_ids in self.agents_by_type.items():
            counts[agent_type] = len(agent_ids)
        return counts
    
    async def get_agent_count_by_capability(self) -> Dict[str, int]:
        """Get count of agents by capability."""
        counts = {}
        for capability in AgentCapability:
            count = len(self.agents_by_capability.get(capability, set()))
            counts[capability.value] = count
        return counts
    
    async def _update_indexes(self, agent_id: str, agent: AgentInfo):
        """Update search indexes for an agent."""
        # Update type index
        if agent.type not in self.agents_by_type:
            self.agents_by_type[agent.type] = set()
        self.agents_by_type[agent.type].add(agent_id)
        
        # Update capability index
        for capability in agent.capabilities:
            if capability not in self.agents_by_capability:
                self.agents_by_capability[capability] = set()
            self.agents_by_capability[capability].add(agent_id)
        
        # Update status index
        if agent.status not in self.agents_by_status:
            self.agents_by_status[agent.status] = set()
        self.agents_by_status[agent.status].add(agent_id)
    
    async def _remove_from_indexes(self, agent_id: str, agent: AgentInfo):
        """Remove agent from search indexes."""
        # Remove from type index
        if agent.type in self.agents_by_type:
            self.agents_by_type[agent.type].discard(agent_id)
            if not self.agents_by_type[agent.type]:
                del self.agents_by_type[agent.type]
        
        # Remove from capability index
        for capability in agent.capabilities:
            if capability in self.agents_by_capability:
                self.agents_by_capability[capability].discard(agent_id)
                if not self.agents_by_capability[capability]:
                    del self.agents_by_capability[capability]
        
        # Remove from status index
        if agent.status in self.agents_by_status:
            self.agents_by_status[agent.status].discard(agent_id)
            if not self.agents_by_status[agent.status]:
                del self.agents_by_status[agent.status]
    
    async def _update_status_index(
        self,
        agent_id: str,
        old_status: AgentStatus,
        new_status: AgentStatus
    ):
        """Update status index when agent status changes."""
        # Remove from old status
        if old_status in self.agents_by_status:
            self.agents_by_status[old_status].discard(agent_id)
            if not self.agents_by_status[old_status]:
                del self.agents_by_status[old_status]
        
        # Add to new status
        if new_status not in self.agents_by_status:
            self.agents_by_status[new_status] = set()
        self.agents_by_status[new_status].add(agent_id)
    
    async def _cleanup_loop(self):
        """Periodic cleanup of inactive agents."""
        try:
            while self.is_running:
                await asyncio.sleep(self.cleanup_interval)
                
                try:
                    await self._cleanup_inactive_agents()
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Cleanup loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Cleanup loop error: {e}")
    
    async def _heartbeat_monitor(self):
        """Monitor agent heartbeats and mark offline agents."""
        try:
            while self.is_running:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                try:
                    current_time = datetime.utcnow()
                    offline_agents = []
                    
                    for agent_id, agent in self.agents.items():
                        if agent.status != AgentStatus.OFFLINE:
                            time_since_heartbeat = (current_time - agent.last_heartbeat).total_seconds()
                            
                            if time_since_heartbeat > agent.timeout_threshold:
                                offline_agents.append(agent_id)
                    
                    # Mark agents as offline
                    for agent_id in offline_agents:
                        await self.update_agent_status(agent_id, AgentStatus.OFFLINE)
                        await self._trigger_offline_callbacks(self.agents[agent_id])
                        
                        self.metrics["heartbeat_timeouts"] += 1
                        logger.warning(f"Agent {agent_id} marked as offline due to heartbeat timeout")
                        
                except Exception as e:
                    logger.error(f"Heartbeat monitor error: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Heartbeat monitor cancelled")
            raise
        except Exception as e:
            logger.error(f"Heartbeat monitor error: {e}")
    
    async def _cleanup_inactive_agents(self):
        """Clean up agents that have been offline for too long."""
        try:
            current_time = datetime.utcnow()
            cleanup_threshold = timedelta(hours=24)  # Remove after 24 hours offline
            
            agents_to_remove = []
            
            for agent_id, agent in self.agents.items():
                if agent.status == AgentStatus.OFFLINE:
                    time_offline = current_time - agent.last_seen
                    if time_offline > cleanup_threshold:
                        agents_to_remove.append(agent_id)
            
            # Remove inactive agents
            for agent_id in agents_to_remove:
                await self.unregister_agent(agent_id)
                logger.info(f"Cleaned up inactive agent {agent_id}")
                
            if agents_to_remove:
                logger.info(f"Cleaned up {len(agents_to_remove)} inactive agents")
                
        except Exception as e:
            logger.error(f"Failed to cleanup inactive agents: {e}")
    
    # Callback management
    def add_registration_callback(self, callback: callable):
        """Add callback for agent registration events."""
        self.registration_callbacks.append(callback)
    
    def add_status_change_callback(self, callback: callable):
        """Add callback for agent status change events."""
        self.status_change_callbacks.append(callback)
    
    def add_offline_callback(self, callback: callable):
        """Add callback for agent offline events."""
        self.offline_callbacks.append(callback)
    
    async def _trigger_registration_callbacks(self, agent: AgentInfo):
        """Trigger registration callbacks."""
        for callback in self.registration_callbacks:
            try:
                result = callback(agent)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Registration callback error: {e}")
    
    async def _trigger_status_change_callbacks(
        self,
        agent: AgentInfo,
        old_status: AgentStatus,
        new_status: AgentStatus
    ):
        """Trigger status change callbacks."""
        for callback in self.status_change_callbacks:
            try:
                result = callback(agent, old_status, new_status)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Status change callback error: {e}")
    
    async def _trigger_offline_callbacks(self, agent: AgentInfo):
        """Trigger offline callbacks."""
        for callback in self.offline_callbacks:
            try:
                result = callback(agent)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Offline callback error: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get registry metrics."""
        # Update current counts
        self.metrics["active_agents"] = len([
            agent for agent in self.agents.values()
            if agent.status != AgentStatus.OFFLINE
        ])
        self.metrics["offline_agents"] = len([
            agent for agent in self.agents.values()
            if agent.status == AgentStatus.OFFLINE
        ])
        
        return {
            **self.metrics,
            "total_agents": len(self.agents),
            "agents_by_status": await self.get_agent_count_by_status(),
            "agents_by_type": await self.get_agent_count_by_type(),
            "agents_by_capability": await self.get_agent_count_by_capability()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            online_agents = len([
                agent for agent in self.agents.values()
                if agent.is_online()
            ])
            
            return {
                "status": "healthy" if self.is_running else "stopped",
                "is_running": self.is_running,
                "total_agents": len(self.agents),
                "online_agents": online_agents,
                "metrics": await self.get_metrics()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    # Context manager support
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()