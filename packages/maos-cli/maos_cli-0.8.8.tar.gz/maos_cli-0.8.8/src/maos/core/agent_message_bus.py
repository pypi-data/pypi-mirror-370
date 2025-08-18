"""
Agent Message Bus for inter-agent communication in MAOS.

Enables agents to communicate, coordinate, and share information.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError
from ..interfaces.sqlite_persistence import SqlitePersistence
from .session_manager import SessionManager


class MessageType(Enum):
    """Types of inter-agent messages."""
    INFO = "info"
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    COORDINATION = "coordination"
    ERROR = "error"
    DISCOVERY = "discovery"  # Agent found something important
    DEPENDENCY = "dependency"  # Agent needs something from another


@dataclass
class AgentMessage:
    """Represents a message between agents."""
    from_agent: str
    to_agent: Optional[str]  # None for broadcasts
    message_type: MessageType
    content: str
    metadata: Dict[str, Any] = None
    timestamp: str = None
    message_id: Optional[int] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "message_id": self.message_id
        }
    
    def to_claude_context(self) -> str:
        """Format message for injection into Claude context."""
        sender = f"Agent {self.from_agent}"
        if self.message_type == MessageType.DISCOVERY:
            return f"💡 {sender} discovered: {self.content}"
        elif self.message_type == MessageType.REQUEST:
            return f"📨 {sender} requests: {self.content}"
        elif self.message_type == MessageType.ERROR:
            return f"❌ {sender} reports error: {self.content}"
        elif self.message_type == MessageType.DEPENDENCY:
            return f"⚠️ {sender} needs: {self.content}"
        else:
            return f"ℹ️ {sender}: {self.content}"


class AgentMessageBus:
    """
    Message bus for inter-agent communication.
    
    Enables agents to:
    - Send direct messages to specific agents
    - Broadcast to all agents
    - Subscribe to message types
    - Coordinate on shared tasks
    """
    
    def __init__(
        self,
        db: SqlitePersistence,
        session_manager: SessionManager
    ):
        """
        Initialize message bus.
        
        Args:
            db: Database for message persistence
            session_manager: Manager for Claude sessions
        """
        self.db = db
        self.session_manager = session_manager
        self.logger = MAOSLogger("agent_message_bus")
        
        # Message handlers
        self._handlers: Dict[MessageType, List[Callable]] = {
            msg_type: [] for msg_type in MessageType
        }
        
        # Agent subscriptions
        self._subscriptions: Dict[str, List[MessageType]] = {}
        
        # Message queue for async processing
        self._message_queue = asyncio.Queue()
        self._processing_task = None
        
        # Track active agents
        self._active_agents: Dict[str, Dict] = {}
    
    async def start(self):
        """Start the message bus."""
        self._processing_task = asyncio.create_task(self._process_messages())
        self.logger.logger.info("Message bus started")
    
    async def stop(self):
        """Stop the message bus."""
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
        self.logger.logger.info("Message bus stopped")
    
    async def register_agent(
        self,
        agent_id: str,
        agent_info: Dict[str, Any],
        subscriptions: List[MessageType] = None,
        create_in_db: bool = True
    ):
        """
        Register an agent with the message bus.
        
        Args:
            agent_id: Agent identifier
            agent_info: Agent information (name, process_id, etc.)
            subscriptions: Message types to subscribe to
            create_in_db: Whether to create the agent in the database
        """
        # Create agent in database if needed
        if create_in_db:
            try:
                await self.db.create_agent(
                    agent_id,
                    agent_info.get('name', f'agent_{agent_id[:8]}'),
                    agent_info.get('type', 'generic'),
                    agent_info.get('capabilities', [])
                )
                # Update agent status to active
                await self.db.update_agent_session(
                    agent_id, 
                    agent_info.get('session_id', f'session_{agent_id[:8]}'),
                    agent_info.get('process_id')
                )
            except Exception as e:
                # Agent might already exist, that's OK
                self.logger.logger.debug(f"Agent {agent_id} may already exist: {e}")
        
        self._active_agents[agent_id] = agent_info
        
        if subscriptions:
            self._subscriptions[agent_id] = subscriptions
        else:
            # Default subscriptions
            self._subscriptions[agent_id] = [
                MessageType.BROADCAST,
                MessageType.REQUEST,
                MessageType.COORDINATION
            ]
        
        self.logger.logger.info(f"Registered agent {agent_id} with message bus")
        
        # Notify other agents (only if there are other agents)
        if len(self._active_agents) > 1:
            await self.broadcast(
                agent_id,
                f"Agent {agent_info.get('name', agent_id)} has joined",
                MessageType.INFO
            )
    
    async def unregister_agent(self, agent_id: str):
        """
        Unregister an agent from the message bus.
        
        Args:
            agent_id: Agent identifier
        """
        if agent_id in self._active_agents:
            agent_info = self._active_agents[agent_id]
            del self._active_agents[agent_id]
            
            if agent_id in self._subscriptions:
                del self._subscriptions[agent_id]
            
            self.logger.logger.info(f"Unregistered agent {agent_id}")
            
            # Notify other agents
            await self.broadcast(
                agent_id,
                f"Agent {agent_info.get('name', agent_id)} has left",
                MessageType.INFO
            )
    
    async def send_message(
        self,
        from_agent: str,
        to_agent: str,
        content: str,
        message_type: MessageType = MessageType.INFO,
        metadata: Dict[str, Any] = None
    ) -> int:
        """
        Send a direct message from one agent to another.
        
        Args:
            from_agent: Sender agent ID
            to_agent: Recipient agent ID
            content: Message content
            message_type: Type of message
            metadata: Additional metadata
            
        Returns:
            Message ID
        """
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            metadata=metadata or {}
        )
        
        # Save to database
        message_id = await self.db.save_message(
            from_agent, to_agent, content, message_type.value
        )
        message.message_id = message_id
        
        # Queue for processing
        await self._message_queue.put(message)
        
        self.logger.logger.debug(
            f"Message sent from {from_agent} to {to_agent}",
            extra={"message_id": message_id, "type": message_type.value}
        )
        
        return message_id
    
    async def broadcast(
        self,
        from_agent: str,
        content: str,
        message_type: MessageType = MessageType.BROADCAST,
        metadata: Dict[str, Any] = None
    ) -> int:
        """
        Broadcast a message to all other agents.
        
        Args:
            from_agent: Sender agent ID
            content: Message content
            message_type: Type of message
            metadata: Additional metadata
            
        Returns:
            Message ID
        """
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=None,  # Broadcast
            message_type=message_type,
            content=content,
            metadata=metadata or {}
        )
        
        # Save to database
        message_id = await self.db.save_message(
            from_agent, None, content, message_type.value
        )
        message.message_id = message_id
        
        # Queue for processing
        await self._message_queue.put(message)
        
        self.logger.logger.debug(
            f"Broadcast sent from {from_agent}",
            extra={"message_id": message_id, "type": message_type.value}
        )
        
        return message_id
    
    async def request_from_agent(
        self,
        from_agent: str,
        to_agent: str,
        request: str,
        timeout: float = 30.0
    ) -> Optional[str]:
        """
        Send a request to another agent and wait for response.
        
        Args:
            from_agent: Requesting agent
            to_agent: Target agent
            request: Request content
            timeout: Response timeout in seconds
            
        Returns:
            Response content or None if timeout
        """
        # Send request
        message_id = await self.send_message(
            from_agent, to_agent, request,
            MessageType.REQUEST,
            {"expects_response": True}
        )
        
        # Wait for response
        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            # Check for response in database
            messages = await self.db.get_messages_for_agent(
                from_agent,
                since_timestamp=datetime.now().isoformat()
            )
            
            for msg in messages:
                if (msg.get('from_agent') == to_agent and
                    msg.get('message_type') == MessageType.RESPONSE.value and
                    msg.get('metadata', {}).get('in_response_to') == message_id):
                    return msg.get('message')
            
            await asyncio.sleep(0.5)
        
        return None
    
    async def respond_to_request(
        self,
        from_agent: str,
        to_agent: str,
        response: str,
        request_message_id: int
    ) -> int:
        """
        Send a response to a request.
        
        Args:
            from_agent: Responding agent
            to_agent: Original requester
            response: Response content
            request_message_id: ID of the original request
            
        Returns:
            Response message ID
        """
        return await self.send_message(
            from_agent, to_agent, response,
            MessageType.RESPONSE,
            {"in_response_to": request_message_id}
        )
    
    async def notify_discovery(
        self,
        agent_id: str,
        discovery: str,
        importance: str = "normal"
    ):
        """
        Notify all agents of an important discovery.
        
        Args:
            agent_id: Discovering agent
            discovery: What was discovered
            importance: "low", "normal", "high", "critical"
        """
        await self.broadcast(
            agent_id, discovery,
            MessageType.DISCOVERY,
            {"importance": importance}
        )
    
    async def notify_dependency(
        self,
        agent_id: str,
        needed_from: str,
        dependency: str
    ):
        """
        Notify that an agent needs something from another.
        
        Args:
            agent_id: Agent with dependency
            needed_from: Agent that can provide
            dependency: What is needed
        """
        await self.send_message(
            agent_id, needed_from, dependency,
            MessageType.DEPENDENCY,
            {"blocking": True}
        )
    
    async def get_messages_for_agent(
        self,
        agent_id: str,
        since: Optional[datetime] = None,
        message_types: Optional[List[MessageType]] = None
    ) -> List[AgentMessage]:
        """
        Get messages for a specific agent.
        
        Args:
            agent_id: Agent to get messages for
            since: Get messages since this time
            message_types: Filter by message types
            
        Returns:
            List of messages
        """
        since_str = since.isoformat() if since else None
        db_messages = await self.db.get_messages_for_agent(agent_id, since_str)
        
        messages = []
        for db_msg in db_messages:
            msg_type = MessageType(db_msg['message_type'])
            
            # Filter by type if specified
            if message_types and msg_type not in message_types:
                continue
            
            messages.append(AgentMessage(
                from_agent=db_msg['from_agent'],
                to_agent=db_msg.get('to_agent'),
                message_type=msg_type,
                content=db_msg['message'],
                metadata=db_msg.get('metadata', {}),
                timestamp=db_msg['timestamp'],
                message_id=db_msg['id']
            ))
        
        return messages
    
    async def _process_messages(self):
        """Process messages from the queue."""
        while True:
            try:
                message = await self._message_queue.get()
                await self._deliver_message(message)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {"operation": "process_messages"})
    
    async def _deliver_message(self, message: AgentMessage):
        """
        Deliver a message to target agent(s).
        
        Args:
            message: Message to deliver
        """
        # Determine recipients
        if message.to_agent:
            # Direct message
            recipients = [message.to_agent]
        else:
            # Broadcast - send to all except sender
            recipients = [
                agent_id for agent_id in self._active_agents
                if agent_id != message.from_agent
            ]
        
        # Deliver to each recipient
        for recipient_id in recipients:
            # Check if agent is subscribed to this message type
            if recipient_id in self._subscriptions:
                if message.message_type not in self._subscriptions[recipient_id]:
                    continue
            
            # Get agent info
            agent_info = self._active_agents.get(recipient_id)
            if not agent_info:
                continue
            
            # Inject into Claude context if process is active
            if 'process_id' in agent_info:
                await self._inject_into_claude_context(
                    agent_info['process_id'],
                    message
                )
            
            # Call registered handlers
            for handler in self._handlers.get(message.message_type, []):
                try:
                    await handler(recipient_id, message)
                except Exception as e:
                    self.logger.log_error(e, {
                        "operation": "deliver_message",
                        "handler": str(handler),
                        "recipient": recipient_id
                    })
    
    async def _inject_into_claude_context(
        self,
        process_id: str,
        message: AgentMessage
    ):
        """
        Inject a message into a Claude session's context.
        
        Args:
            process_id: Claude process ID
            message: Message to inject
        """
        # Format message for Claude
        context_update = message.to_claude_context()
        
        # Send to Claude session
        success = await self.session_manager.send_to_session(
            process_id,
            f"\n[Inter-agent message]: {context_update}\n"
        )
        
        if success:
            self.logger.logger.debug(
                f"Injected message into Claude context",
                extra={"process_id": process_id, "message_id": message.message_id}
            )
    
    def register_handler(
        self,
        message_type: MessageType,
        handler: Callable
    ):
        """
        Register a handler for a message type.
        
        Args:
            message_type: Type of message to handle
            handler: Async function to call with (agent_id, message)
        """
        self._handlers[message_type].append(handler)
    
    async def get_agent_conversation(
        self,
        agent1: str,
        agent2: str
    ) -> List[AgentMessage]:
        """
        Get conversation history between two agents.
        
        Args:
            agent1: First agent
            agent2: Second agent
            
        Returns:
            List of messages between the agents
        """
        all_messages = []
        
        # Get messages from agent1 to agent2
        messages1 = await self.get_messages_for_agent(agent2)
        all_messages.extend([
            msg for msg in messages1
            if msg.from_agent == agent1
        ])
        
        # Get messages from agent2 to agent1
        messages2 = await self.get_messages_for_agent(agent1)
        all_messages.extend([
            msg for msg in messages2
            if msg.from_agent == agent2
        ])
        
        # Sort by timestamp
        all_messages.sort(key=lambda m: m.timestamp)
        
        return all_messages
    
    async def get_broadcast_history(
        self,
        limit: int = 50
    ) -> List[AgentMessage]:
        """
        Get broadcast message history.
        
        Args:
            limit: Maximum number of messages
            
        Returns:
            List of broadcast messages
        """
        # This would need a database query for broadcast messages
        # For now, return empty list
        return []
    
    def get_active_agents(self) -> List[Dict[str, Any]]:
        """
        Get list of active agents.
        
        Returns:
            List of active agent information
        """
        return [
            {
                "agent_id": agent_id,
                "name": info.get('name'),
                "process_id": info.get('process_id'),
                "subscriptions": self._subscriptions.get(agent_id, [])
            }
            for agent_id, info in self._active_agents.items()
        ]