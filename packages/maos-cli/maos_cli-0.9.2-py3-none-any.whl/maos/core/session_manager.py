"""
Session Manager for Claude Code CLI sessions.

Manages Claude session lifecycle including creation, resumption, and tracking.
"""

import asyncio
import json
import os
import subprocess
from typing import Dict, Optional, Tuple, List, Any
from datetime import datetime
from uuid import uuid4
from pathlib import Path

from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError
from ..interfaces.sqlite_persistence import SqlitePersistence


class SessionManager:
    """Manages Claude Code CLI sessions with full lifecycle support."""
    
    def __init__(
        self,
        db: SqlitePersistence,
        claude_cli_path: str = "claude",
        base_working_dir: str = "/tmp/maos_sessions"
    ):
        """
        Initialize session manager.
        
        Args:
            db: Database for session persistence
            claude_cli_path: Path to Claude CLI executable
            base_working_dir: Base directory for session working directories
        """
        self.db = db
        self.claude_cli_path = claude_cli_path
        self.base_working_dir = Path(base_working_dir)
        self.base_working_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = MAOSLogger("session_manager")
        
        # Track active processes
        self._active_processes: Dict[str, subprocess.Popen] = {}
        self._process_lock = asyncio.Lock()
    
    async def create_session(
        self,
        agent_id: str,
        agent_name: str,
        task: str,
        max_turns: int = 10,
        working_dir: Optional[str] = None,
        allowed_tools: Optional[List[str]] = None
    ) -> Tuple[str, str, subprocess.Popen]:
        """
        Create a new Claude session for an agent.
        
        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            task: Task to execute
            max_turns: Maximum turns for the session
            working_dir: Working directory for the session
            allowed_tools: List of allowed tools for the agent
            
        Returns:
            Tuple of (process_id, session_id, process)
        """
        process_id = str(uuid4())
        
        # Set up working directory
        if not working_dir:
            working_dir = str(self.base_working_dir / f"session_{process_id}")
        Path(working_dir).mkdir(parents=True, exist_ok=True)
        
        # Build Claude command
        cmd = [
            self.claude_cli_path,
            "-p", task,
            "--output-format", "json",
            "--max-turns", str(max_turns),
            "--verbose"  # To get detailed output including session_id
        ]
        
        # Add allowed tools if specified
        if allowed_tools:
            for tool in allowed_tools:
                cmd.extend(["--allowedTools", tool])
        
        try:
            # Spawn Claude process
            self.logger.logger.info(f"Spawning Claude session for {agent_name}")
            self.logger.logger.debug(f"Command: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=working_dir,
                env={**os.environ, "MAOS_AGENT": agent_name}
            )
            
            # Wait for first response to get session_id
            session_id = await self._extract_session_id(process)
            
            if not session_id:
                # Generate a fallback session_id
                session_id = f"session_{uuid4().hex}"
                self.logger.logger.warning(f"Could not extract session_id, using fallback: {session_id}")
            
            # Store in database
            await self.db.create_agent(agent_id, agent_name, "claude", allowed_tools)
            await self.db.update_agent_session(agent_id, session_id, process_id)
            await self.db.create_session(session_id, agent_id, task)
            
            # Track active process
            async with self._process_lock:
                self._active_processes[process_id] = process
            
            self.logger.logger.info(
                f"Created session for {agent_name}",
                extra={
                    "agent_id": agent_id,
                    "process_id": process_id,
                    "session_id": session_id,
                    "working_dir": working_dir
                }
            )
            
            return process_id, session_id, process
            
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "create_session",
                "agent_id": agent_id,
                "task": task[:100]
            })
            raise MAOSError(f"Failed to create Claude session: {str(e)}")
    
    async def resume_session(
        self,
        agent_id: str,
        session_id: str,
        continuation_task: str = "Continue your previous task",
        max_turns: int = 10
    ) -> Tuple[str, subprocess.Popen]:
        """
        Resume an existing Claude session.
        
        Args:
            agent_id: Agent identifier
            session_id: Session to resume
            continuation_task: Task to continue with
            max_turns: Maximum additional turns
            
        Returns:
            Tuple of (process_id, process)
        """
        process_id = str(uuid4())
        
        # Get agent info
        agent = await self.db.get_agent(agent_id)
        if not agent:
            raise MAOSError(f"Agent {agent_id} not found")
        
        # Build resume command
        cmd = [
            self.claude_cli_path,
            "--resume", session_id,
            "-p", continuation_task,
            "--output-format", "json",
            "--max-turns", str(max_turns),
            "--verbose"
        ]
        
        try:
            # Get working directory from previous session
            working_dir = str(self.base_working_dir / f"session_{process_id}")
            Path(working_dir).mkdir(parents=True, exist_ok=True)
            
            # Spawn resumed process
            self.logger.logger.info(f"Resuming session {session_id} for {agent['name']}")
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=working_dir,
                env={**os.environ, "MAOS_AGENT": agent['name']}
            )
            
            # Update database
            await self.db.update_agent_session(agent_id, session_id, process_id)
            
            # Track active process
            async with self._process_lock:
                self._active_processes[process_id] = process
            
            self.logger.logger.info(
                f"Resumed session for {agent['name']}",
                extra={
                    "agent_id": agent_id,
                    "process_id": process_id,
                    "session_id": session_id
                }
            )
            
            return process_id, process
            
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "resume_session",
                "agent_id": agent_id,
                "session_id": session_id
            })
            raise MAOSError(f"Failed to resume session: {str(e)}")
    
    async def continue_session(
        self,
        agent_id: str,
        continuation_task: str = "Continue",
        max_turns: int = 10
    ) -> Tuple[str, str, subprocess.Popen]:
        """
        Continue the most recent session for an agent.
        
        Args:
            agent_id: Agent identifier
            continuation_task: Task to continue with
            max_turns: Maximum additional turns
            
        Returns:
            Tuple of (process_id, session_id, process)
        """
        # Get agent's current session
        agent = await self.db.get_agent(agent_id)
        if not agent or not agent.get('session_id'):
            raise MAOSError(f"No active session for agent {agent_id}")
        
        session_id = agent['session_id']
        
        # Resume the session
        process_id, process = await self.resume_session(
            agent_id, session_id, continuation_task, max_turns
        )
        
        return process_id, session_id, process
    
    async def _extract_session_id(self, process: subprocess.Popen) -> Optional[str]:
        """
        Extract session_id from Claude's initial output.
        
        Args:
            process: The Claude process
            
        Returns:
            Session ID if found, None otherwise
        """
        try:
            # Read first lines of output looking for session_id
            for _ in range(10):  # Check first 10 lines
                line = await asyncio.wait_for(
                    asyncio.create_task(self._read_line_async(process.stdout)),
                    timeout=2.0
                )
                
                if not line:
                    break
                
                # Try to parse as JSON
                try:
                    data = json.loads(line)
                    if 'session_id' in data:
                        return data['session_id']
                    if 'sessionId' in data:
                        return data['sessionId']
                except json.JSONDecodeError:
                    # Check for session_id in plain text
                    if 'session' in line.lower():
                        import re
                        match = re.search(r'session[_-]?id[:\s]+([a-f0-9-]+)', line, re.IGNORECASE)
                        if match:
                            return match.group(1)
            
            return None
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            self.logger.logger.debug(f"Error extracting session_id: {e}")
            return None
    
    async def _read_line_async(self, stream) -> Optional[str]:
        """Read a line from a stream asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, stream.readline)
    
    async def read_session_output(
        self,
        process_id: str,
        timeout: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Read output from a Claude session.
        
        Args:
            process_id: Process identifier
            timeout: Read timeout in seconds
            
        Returns:
            Parsed JSON output or None
        """
        process = self._active_processes.get(process_id)
        if not process:
            return None
        
        try:
            line = await asyncio.wait_for(
                self._read_line_async(process.stdout),
                timeout=timeout or 30.0
            )
            
            if line:
                # Try to parse as JSON
                try:
                    data = json.loads(line)
                    
                    # Store conversation turn if session_id present
                    if 'session_id' in data:
                        await self.db.update_session(
                            data['session_id'],
                            data,
                            data.get('total_cost_usd', 0.0)
                        )
                    
                    return data
                except json.JSONDecodeError:
                    return {"type": "text", "content": line.strip()}
            
            return None
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "read_session_output",
                "process_id": process_id
            })
            return None
    
    async def send_to_session(
        self,
        process_id: str,
        message: str
    ) -> bool:
        """
        Send a message to a Claude session.
        
        Args:
            process_id: Process identifier
            message: Message to send
            
        Returns:
            True if sent successfully
        """
        process = self._active_processes.get(process_id)
        if not process or process.poll() is not None:
            return False
        
        try:
            process.stdin.write(message + "\n")
            process.stdin.flush()
            return True
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "send_to_session",
                "process_id": process_id
            })
            return False
    
    async def terminate_session(self, process_id: str) -> bool:
        """
        Terminate a Claude session.
        
        Args:
            process_id: Process identifier
            
        Returns:
            True if terminated successfully
        """
        async with self._process_lock:
            process = self._active_processes.get(process_id)
            if not process:
                return False
            
            try:
                # Send termination signal
                process.terminate()
                
                # Wait for process to end
                try:
                    await asyncio.wait_for(
                        asyncio.create_task(self._wait_for_process(process)),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    # Force kill if needed
                    process.kill()
                
                # Remove from active processes
                del self._active_processes[process_id]
                
                self.logger.logger.info(f"Terminated session {process_id}")
                return True
                
            except Exception as e:
                self.logger.log_error(e, {
                    "operation": "terminate_session",
                    "process_id": process_id
                })
                return False
    
    async def _wait_for_process(self, process: subprocess.Popen):
        """Wait for a process to complete."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, process.wait)
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session information or None
        """
        return await self.db.get_session(session_id)
    
    async def list_active_sessions(self) -> List[Dict[str, Any]]:
        """
        List all active sessions.
        
        Returns:
            List of active session information
        """
        agents = await self.db.get_active_agents()
        sessions = []
        
        for agent in agents:
            if agent.get('session_id'):
                session = await self.db.get_session(agent['session_id'])
                if session:
                    sessions.append({
                        "agent_id": agent['id'],
                        "agent_name": agent['name'],
                        "session_id": agent['session_id'],
                        "process_id": agent.get('process_id'),
                        "task": session.get('task'),
                        "turn_count": session.get('turn_count', 0),
                        "total_cost": session.get('total_cost', 0.0),
                        "created_at": session.get('created_at')
                    })
        
        return sessions
    
    async def cleanup_inactive_sessions(self) -> int:
        """
        Clean up inactive sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        cleaned = 0
        
        async with self._process_lock:
            # Check all tracked processes
            for process_id, process in list(self._active_processes.items()):
                if process.poll() is not None:
                    # Process has terminated
                    del self._active_processes[process_id]
                    cleaned += 1
                    self.logger.logger.info(f"Cleaned up inactive session {process_id}")
        
        return cleaned
    
    async def shutdown(self):
        """Shutdown all active sessions."""
        self.logger.logger.info("Shutting down session manager")
        
        # Terminate all active processes
        for process_id in list(self._active_processes.keys()):
            await self.terminate_session(process_id)
        
        self.logger.logger.info("Session manager shutdown complete")