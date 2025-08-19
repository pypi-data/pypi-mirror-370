"""
Session Manager v2 for Claude Code subagents.

This version creates Claude Code subagent files instead of trying to spawn processes.
The actual execution is delegated to Claude Code through the Task tool.
"""

import asyncio
import json
import os
from typing import Dict, Optional, Tuple, List, Any
from datetime import datetime
from uuid import uuid4
from pathlib import Path

from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError
from ..interfaces.sqlite_persistence import SqlitePersistence
from .claude_subagent_manager import ClaudeSubagentManager, ClaudeSubagent


class SessionManagerV2:
    """
    Manages Claude Code subagent sessions.
    
    Instead of spawning processes, this creates subagent definition files
    and tracks their usage through the database.
    """
    
    def __init__(
        self,
        db: SqlitePersistence,
        project_path: str = "."
    ):
        """
        Initialize session manager v2.
        
        Args:
            db: Database for session persistence
            project_path: Path to project root
        """
        self.db = db
        self.project_path = Path(project_path)
        self.subagent_manager = ClaudeSubagentManager(self.project_path)
        
        self.logger = MAOSLogger("session_manager_v2")
        
        # Track active agents
        self._active_agents: Dict[str, Dict] = {}
    
    async def create_session(
        self,
        agent_id: str,
        agent_name: str,
        task: str,
        max_turns: int = 10,
        working_dir: Optional[str] = None,
        allowed_tools: Optional[List[str]] = None
    ) -> Tuple[str, str, Dict]:
        """
        Create a new Claude subagent session.
        
        This creates a subagent definition file and returns session info.
        
        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            task: Task to execute
            max_turns: Maximum turns (not used for subagents)
            working_dir: Working directory (not used for subagents)
            allowed_tools: List of allowed tools for the agent
            
        Returns:
            Tuple of (process_id, session_id, agent_info)
        """
        # Generate IDs
        process_id = str(uuid4())  # Simulated process ID
        session_id = f"session_{uuid4().hex}"
        
        try:
            # Determine task type from description
            task_lower = task.lower()
            if 'analyze' in task_lower or 'understand' in task_lower:
                task_type = 'analyze'
            elif 'implement' in task_lower or 'create' in task_lower or 'build' in task_lower:
                task_type = 'implement'
            elif 'test' in task_lower:
                task_type = 'test'
            elif 'review' in task_lower:
                task_type = 'review'
            elif 'document' in task_lower:
                task_type = 'document'
            elif 'debug' in task_lower or 'fix' in task_lower:
                task_type = 'debug'
            else:
                task_type = 'general'
            
            # Create the subagent
            subagent = ClaudeSubagent(
                name=agent_name,
                description=f"Agent for: {task}. Use proactively to complete this task.",
                system_prompt=f"""You are {agent_name}, a specialized agent.

Your task: {task}

Approach:
1. Understand the requirements
2. Plan your approach
3. Execute systematically
4. Verify your work
5. Report results clearly

Work autonomously and proactively to complete your assigned task.""",
                tools=allowed_tools
            )
            
            # Create the subagent file
            agent_file = self.subagent_manager.create_subagent(subagent)
            
            self.logger.logger.info(f"Created subagent {agent_name} at {agent_file}")
            
            # Store in database
            await self.db.create_agent(agent_id, agent_name, task_type, allowed_tools)
            await self.db.update_agent_session(agent_id, session_id, process_id)
            await self.db.create_session(session_id, agent_id, task)
            
            # Track active agent
            agent_info = {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "session_id": session_id,
                "process_id": process_id,
                "task": task,
                "task_type": task_type,
                "agent_file": str(agent_file),
                "status": "created",
                "created_at": datetime.now().isoformat()
            }
            
            self._active_agents[process_id] = agent_info
            
            self.logger.logger.info(
                f"Created session for {agent_name}",
                extra={
                    "agent_id": agent_id,
                    "process_id": process_id,
                    "session_id": session_id,
                    "agent_file": str(agent_file)
                }
            )
            
            return process_id, session_id, agent_info
            
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "create_session",
                "agent_id": agent_id,
                "task": task[:100]
            })
            raise MAOSError(f"Failed to create Claude subagent session: {str(e)}")
    
    async def read_session_output(
        self,
        process_id: str,
        timeout: float = 5.0
    ) -> Optional[Dict]:
        """
        Simulate reading session output.
        
        Since subagents don't have real processes, this returns simulated status.
        
        Args:
            process_id: Process identifier
            timeout: Timeout in seconds
            
        Returns:
            Simulated output or None
        """
        if process_id not in self._active_agents:
            return None
        
        agent_info = self._active_agents[process_id]
        
        # Simulate different states
        if agent_info["status"] == "created":
            # First read - agent is starting
            agent_info["status"] = "running"
            return {
                "type": "status",
                "message": f"Agent {agent_info['agent_name']} created and ready",
                "progress": 10
            }
        
        elif agent_info["status"] == "running":
            # Simulate work in progress
            # In reality, Claude Code would be executing the subagent
            agent_info["status"] = "delegated"
            return {
                "type": "delegated",
                "message": f"Task delegated to {agent_info['agent_name']} subagent",
                "progress": 50,
                "content": f"Use the {agent_info['agent_name']} subagent to: {agent_info['task']}"
            }
        
        elif agent_info["status"] == "delegated":
            # Simulate completion
            agent_info["status"] = "completed"
            return {
                "type": "completion",
                "message": f"Task completed by {agent_info['agent_name']}",
                "progress": 100,
                "result": {
                    "status": "success",
                    "output": f"Successfully completed: {agent_info['task']}"
                }
            }
        
        return None
    
    async def resume_session(
        self,
        agent_id: str,
        session_id: str,
        continuation_task: str = "Continue your previous task",
        max_turns: int = 10
    ) -> Tuple[str, Dict]:
        """
        Resume an existing session by updating the subagent.
        
        Args:
            agent_id: Agent identifier
            session_id: Session to resume
            continuation_task: Task to continue with
            max_turns: Maximum additional turns
            
        Returns:
            Tuple of (process_id, agent_info)
        """
        process_id = str(uuid4())
        
        # Get agent info
        agent = await self.db.get_agent(agent_id)
        if not agent:
            raise MAOSError(f"Agent {agent_id} not found")
        
        # Update or recreate the subagent with continuation task
        subagent = ClaudeSubagent(
            name=agent['name'],
            description=f"Continuing previous work. New task: {continuation_task}",
            system_prompt=f"""You are {agent['name']}, continuing from a previous session.

Previous context is available in your memory.

New task: {continuation_task}

Continue where you left off and complete the new task.""",
            tools=agent.get('allowed_tools')
        )
        
        # Update the subagent file
        agent_file = self.subagent_manager.create_subagent(subagent)
        
        # Update database
        await self.db.update_agent_session(agent_id, session_id, process_id)
        
        # Track active agent
        agent_info = {
            "agent_id": agent_id,
            "agent_name": agent['name'],
            "session_id": session_id,
            "process_id": process_id,
            "task": continuation_task,
            "agent_file": str(agent_file),
            "status": "resumed",
            "resumed_at": datetime.now().isoformat()
        }
        
        self._active_agents[process_id] = agent_info
        
        self.logger.logger.info(
            f"Resumed session for {agent['name']}",
            extra={
                "agent_id": agent_id,
                "process_id": process_id,
                "session_id": session_id
            }
        )
        
        return process_id, agent_info
    
    async def delegate_to_subagents(self, agent_names: List[str], task: str) -> str:
        """
        Generate a prompt to delegate work to subagents.
        
        Args:
            agent_names: List of subagent names
            task: Task to delegate
            
        Returns:
            Delegation prompt for Claude Code
        """
        if not agent_names:
            return task
        
        if len(agent_names) == 1:
            return f"Use the {agent_names[0]} subagent to: {task}"
        else:
            # Multiple agents - coordinate them
            agents_str = ", ".join(agent_names[:-1]) + f" and {agent_names[-1]}"
            return f"Coordinate the {agents_str} subagents to work together on: {task}"
    
    async def shutdown(self):
        """Clean up and shutdown."""
        # Clean up created subagent files
        for agent_info in self._active_agents.values():
            agent_name = agent_info.get("agent_name")
            if agent_name:
                self.subagent_manager.delete_subagent(agent_name)
        
        self._active_agents.clear()
        self.logger.logger.info("Session manager shutdown complete")
    
    def get_active_agents(self) -> List[Dict]:
        """Get list of active agents."""
        return list(self._active_agents.values())
    
    def get_agent_status(self, process_id: str) -> Optional[str]:
        """Get status of a specific agent."""
        if process_id in self._active_agents:
            return self._active_agents[process_id].get("status")
        return None