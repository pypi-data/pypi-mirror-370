"""
Orchestrated Agent - Wrapper for Claude agents with message bus integration.

This enables true inter-agent communication and coordination.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from .agent_message_bus import AgentMessageBus, MessageType, AgentMessage
from .claude_sdk_executor import ClaudeSDKExecutor, AgentExecution
from ..utils.logging_config import MAOSLogger


class OrchestratedAgent:
    """
    Wrapper for Claude agents with message bus integration.
    
    Enables agents to:
    - Send and receive messages from other agents
    - Share discoveries in real-time
    - Request information from specific agents
    - Coordinate execution strategies
    """
    
    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        message_bus: AgentMessageBus,
        executor: ClaudeSDKExecutor = None
    ):
        """
        Initialize orchestrated agent.
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent (developer, analyst, etc.)
            message_bus: Message bus for communication
            executor: Claude SDK executor (optional)
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.message_bus = message_bus
        self.executor = executor or ClaudeSDKExecutor()
        self.logger = MAOSLogger(f"orchestrated_agent_{agent_id}")
        
        # Context buffer for messages
        self.context_buffer = []
        self.other_agents = []
        self.session_id = None
        
    async def execute_with_context(
        self,
        task: str,
        other_agents: List[str],
        system_prompt: Optional[str] = None,
        allowed_tools: Optional[List[str]] = None,
        max_turns: int = 5
    ) -> Dict[str, Any]:
        """
        Execute task with inter-agent communication context.
        
        Args:
            task: Task to execute
            other_agents: List of other agent IDs working on related tasks
            system_prompt: Custom system prompt
            allowed_tools: List of allowed tools
            max_turns: Maximum conversation turns
            
        Returns:
            Execution result with communication history
        """
        self.other_agents = other_agents
        
        # Enhanced task with coordination instructions
        enhanced_task = self._enhance_task_with_coordination(task, other_agents)
        
        # Register message handlers
        await self._setup_message_handlers()
        
        # Create agent execution
        execution = AgentExecution(
            agent_id=self.agent_id,
            task=enhanced_task,
            system_prompt=system_prompt or self._get_default_system_prompt(),
            allowed_tools=allowed_tools,
            max_turns=max_turns
        )
        
        # Execute with monitoring
        result = await self._execute_with_monitoring(execution)
        
        # Add communication history to result
        result["communication_history"] = self.context_buffer
        result["messages_sent"] = len([m for m in self.context_buffer if m.get("direction") == "sent"])
        result["messages_received"] = len([m for m in self.context_buffer if m.get("direction") == "received"])
        
        return result
    
    def _enhance_task_with_coordination(self, task: str, other_agents: List[str]) -> str:
        """
        Enhance task with coordination instructions.
        
        Args:
            task: Original task
            other_agents: List of other agent IDs
            
        Returns:
            Enhanced task with coordination context
        """
        coordination_context = f"""
{task}

COORDINATION CONTEXT:
- You are agent {self.agent_id} ({self.agent_type})
- Other agents working on related tasks: {', '.join(other_agents[:5]) if other_agents else 'None'}
- You can communicate with other agents through special commands:

COMMUNICATION COMMANDS:
1. To share an important discovery:
   DISCOVERY: [Your discovery here]
   
2. To request information from another agent:
   REQUEST_FROM {agent_id}: [Your request]
   
3. To broadcast to all agents:
   BROADCAST: [Your message]
   
4. To report a dependency or blocker:
   DEPENDENCY: [What you need from whom]

When you discover something that might help other agents, share it immediately.
When you need information that another agent might have, request it.
Check periodically for messages from other agents.
"""
        return coordination_context
    
    async def _setup_message_handlers(self):
        """Setup handlers for incoming messages."""
        # Register handler for discoveries
        self.message_bus.register_handler(
            MessageType.DISCOVERY,
            self._handle_discovery
        )
        
        # Register handler for requests
        self.message_bus.register_handler(
            MessageType.REQUEST,
            self._handle_request
        )
        
        # Register handler for broadcasts
        self.message_bus.register_handler(
            MessageType.BROADCAST,
            self._handle_broadcast
        )
    
    async def _handle_discovery(self, agent_id: str, message: AgentMessage):
        """
        Handle discovery message from another agent.
        
        Args:
            agent_id: Receiving agent ID (should be self.agent_id)
            message: Discovery message
        """
        if agent_id != self.agent_id:
            return
        
        self.context_buffer.append({
            "direction": "received",
            "type": "discovery",
            "from": message.from_agent,
            "content": message.content,
            "timestamp": message.timestamp
        })
        
        self.logger.logger.info(
            f"Received discovery from {message.from_agent}: {message.content[:100]}"
        )
    
    async def _handle_request(self, agent_id: str, message: AgentMessage):
        """
        Handle request from another agent.
        
        Args:
            agent_id: Receiving agent ID
            message: Request message
        """
        if agent_id != self.agent_id:
            return
        
        self.context_buffer.append({
            "direction": "received",
            "type": "request",
            "from": message.from_agent,
            "content": message.content,
            "timestamp": message.timestamp,
            "message_id": message.message_id
        })
        
        # Could auto-respond here if we have the information
        self.logger.logger.info(
            f"Received request from {message.from_agent}: {message.content[:100]}"
        )
    
    async def _handle_broadcast(self, agent_id: str, message: AgentMessage):
        """
        Handle broadcast message.
        
        Args:
            agent_id: Receiving agent ID
            message: Broadcast message
        """
        if agent_id != self.agent_id:
            return
        
        self.context_buffer.append({
            "direction": "received",
            "type": "broadcast",
            "from": message.from_agent,
            "content": message.content,
            "timestamp": message.timestamp
        })
        
        self.logger.logger.debug(
            f"Received broadcast from {message.from_agent}"
        )
    
    async def _execute_with_monitoring(self, execution: AgentExecution) -> Dict[str, Any]:
        """
        Execute agent task while monitoring for communication patterns.
        
        Args:
            execution: Agent execution configuration
            
        Returns:
            Execution result
        """
        # Start monitoring task
        monitor_task = asyncio.create_task(self._monitor_execution())
        
        try:
            # Execute the actual task
            result = await self.executor.execute_agent(execution)
            
            # Extract and process any communication commands from output
            if result.get("success") and result.get("result"):
                await self._process_communication_commands(result["result"])
            
            # Store session ID for resumption
            self.session_id = result.get("session_id")
            
            return result
            
        finally:
            # Stop monitoring
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_execution(self):
        """
        Monitor execution for incoming messages.
        
        Periodically checks for new messages and could inject them into context.
        """
        while True:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            # Get recent messages
            messages = await self.message_bus.get_messages_for_agent(
                self.agent_id,
                message_types=[MessageType.REQUEST, MessageType.DISCOVERY]
            )
            
            # Log if we have new messages
            if messages:
                self.logger.logger.debug(
                    f"Agent {self.agent_id} has {len(messages)} pending messages"
                )
    
    async def _process_communication_commands(self, output: str):
        """
        Process communication commands from agent output.
        
        Args:
            output: Agent output text
        """
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check for DISCOVERY command
            if line.startswith("DISCOVERY:"):
                discovery = line[10:].strip()
                if discovery:
                    await self.message_bus.notify_discovery(
                        self.agent_id,
                        discovery,
                        importance="high"
                    )
                    self.context_buffer.append({
                        "direction": "sent",
                        "type": "discovery",
                        "content": discovery,
                        "timestamp": datetime.now().isoformat()
                    })
                    self.logger.logger.info(f"Agent {self.agent_id} shared discovery: {discovery[:100]}")
            
            # Check for REQUEST_FROM command
            elif line.startswith("REQUEST_FROM"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    target_part = parts[0][12:].strip()
                    request = parts[1].strip()
                    if target_part and request:
                        await self.message_bus.send_message(
                            self.agent_id,
                            target_part,
                            request,
                            MessageType.REQUEST
                        )
                        self.context_buffer.append({
                            "direction": "sent",
                            "type": "request",
                            "to": target_part,
                            "content": request,
                            "timestamp": datetime.now().isoformat()
                        })
                        self.logger.logger.info(f"Agent {self.agent_id} requested from {target_part}: {request[:100]}")
            
            # Check for BROADCAST command
            elif line.startswith("BROADCAST:"):
                broadcast = line[10:].strip()
                if broadcast:
                    await self.message_bus.broadcast(
                        self.agent_id,
                        broadcast,
                        MessageType.BROADCAST
                    )
                    self.context_buffer.append({
                        "direction": "sent",
                        "type": "broadcast",
                        "content": broadcast,
                        "timestamp": datetime.now().isoformat()
                    })
                    self.logger.logger.info(f"Agent {self.agent_id} broadcast: {broadcast[:100]}")
            
            # Check for DEPENDENCY command
            elif line.startswith("DEPENDENCY:"):
                dependency = line[11:].strip()
                if dependency:
                    # Parse dependency to find target agent if specified
                    for other_agent in self.other_agents:
                        if other_agent in dependency:
                            await self.message_bus.notify_dependency(
                                self.agent_id,
                                other_agent,
                                dependency
                            )
                            self.context_buffer.append({
                                "direction": "sent",
                                "type": "dependency",
                                "to": other_agent,
                                "content": dependency,
                                "timestamp": datetime.now().isoformat()
                            })
                            self.logger.logger.info(f"Agent {self.agent_id} reported dependency on {other_agent}")
                            break
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt based on agent type."""
        prompts = {
            "developer": "You are an expert developer. Write clean, efficient code and share insights with other agents.",
            "analyst": "You are a code analyst. Analyze thoroughly and share important findings with the team.",
            "security": "You are a security expert. Identify vulnerabilities and coordinate with other agents on fixes.",
            "architect": "You are a software architect. Design solutions and coordinate with implementation agents.",
            "tester": "You are a testing specialist. Write tests and share coverage insights with developers.",
            "coordinator": "You are a coordination agent. Help other agents work together effectively."
        }
        
        for key, prompt in prompts.items():
            if key in self.agent_type.lower():
                return prompt
        
        return "You are an AI assistant. Complete your task and coordinate with other agents as needed."
    
    async def send_discovery(self, discovery: str, importance: str = "normal"):
        """
        Send a discovery to all other agents.
        
        Args:
            discovery: Discovery content
            importance: Discovery importance level
        """
        await self.message_bus.notify_discovery(
            self.agent_id,
            discovery,
            importance
        )
        
        self.context_buffer.append({
            "direction": "sent",
            "type": "discovery",
            "content": discovery,
            "importance": importance,
            "timestamp": datetime.now().isoformat()
        })
    
    async def request_from_agent(self, target_agent: str, request: str) -> Optional[str]:
        """
        Request information from another agent.
        
        Args:
            target_agent: Target agent ID
            request: Request content
            
        Returns:
            Response from target agent or None
        """
        response = await self.message_bus.request_from_agent(
            self.agent_id,
            target_agent,
            request,
            timeout=30.0
        )
        
        self.context_buffer.append({
            "direction": "sent",
            "type": "request",
            "to": target_agent,
            "content": request,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def get_communication_summary(self) -> str:
        """
        Get summary of agent's communication.
        
        Returns:
            Human-readable communication summary
        """
        sent = len([m for m in self.context_buffer if m.get("direction") == "sent"])
        received = len([m for m in self.context_buffer if m.get("direction") == "received"])
        
        discoveries = [m for m in self.context_buffer if m.get("type") == "discovery"]
        requests = [m for m in self.context_buffer if m.get("type") == "request"]
        
        summary = f"""
Communication Summary for {self.agent_id}:
- Messages sent: {sent}
- Messages received: {received}
- Discoveries shared: {len([d for d in discoveries if d.get("direction") == "sent"])}
- Discoveries received: {len([d for d in discoveries if d.get("direction") == "received"])}
- Requests made: {len([r for r in requests if r.get("direction") == "sent"])}
- Requests received: {len([r for r in requests if r.get("direction") == "received"])}
"""
        
        if discoveries:
            summary += "\nKey Discoveries:\n"
            for d in discoveries[:3]:
                summary += f"  - {d.get('from', self.agent_id)}: {d['content'][:100]}...\n"
        
        return summary