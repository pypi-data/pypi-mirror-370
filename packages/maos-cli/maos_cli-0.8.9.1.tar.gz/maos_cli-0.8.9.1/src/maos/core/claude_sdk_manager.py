"""
Claude SDK Manager for MAOS

Manages Claude Code CLI in SDK mode (non-interactive) for reliable orchestration.
Uses the proper CLI flags as documented in the official Claude Code SDK.
"""

import asyncio
import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from uuid import uuid4
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError, AgentError


@dataclass
class ClaudeSession:
    """Information about a Claude SDK session."""
    session_id: str
    process_id: str
    created_at: datetime
    last_activity: datetime
    working_dir: str
    subagents: List[str] = field(default_factory=list)
    total_cost: float = 0.0
    turn_count: int = 0
    active: bool = True


class ClaudeSDKManager:
    """
    Manages Claude Code CLI in SDK mode for orchestration.
    
    This class uses the Claude CLI in non-interactive mode with proper flags:
    - Uses `claude -p` for SDK mode
    - Uses `--output-format json` for structured responses
    - Uses `--resume` and `--continue` for session management
    - Leverages subagents in .claude/agents/ directory
    """
    
    def __init__(
        self,
        max_concurrent_sessions: int = 10,
        claude_cli_path: str = "claude",
        base_working_dir: str = None,
        default_max_turns: int = 10
    ):
        """
        Initialize the Claude SDK Manager.
        
        Args:
            max_concurrent_sessions: Maximum number of concurrent Claude sessions
            claude_cli_path: Path to Claude CLI executable
            base_working_dir: Base directory for operations
            default_max_turns: Default max turns for each session
        """
        self.max_concurrent_sessions = max_concurrent_sessions
        self.claude_cli_path = claude_cli_path
        self.base_working_dir = Path(base_working_dir or os.getcwd())
        self.default_max_turns = default_max_turns
        
        # Session tracking
        self._sessions: Dict[str, ClaudeSession] = {}
        self._session_lock = asyncio.Lock()
        
        # Logging
        self.logger = MAOSLogger("claude_sdk_manager")
        
        # Verify Claude CLI is available
        self._verify_claude_cli()
    
    def _verify_claude_cli(self) -> None:
        """Verify that Claude CLI is installed and accessible."""
        try:
            result = subprocess.run(
                [self.claude_cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise AgentError(f"Claude CLI not functional: {result.stderr}")
            
            self.logger.logger.info(f"Claude CLI verified: {result.stdout.strip()}")
            
        except FileNotFoundError:
            raise AgentError(
                f"Claude CLI not found at '{self.claude_cli_path}'. "
                "Please install: npm install -g @anthropic-ai/claude-code"
            )
        except subprocess.TimeoutExpired:
            raise AgentError("Claude CLI verification timed out")
    
    async def create_session(
        self,
        prompt: str,
        working_dir: Optional[str] = None,
        subagents: Optional[List[str]] = None,
        max_turns: Optional[int] = None,
        system_prompt: Optional[str] = None,
        allowed_tools: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Claude session using SDK mode.
        
        Args:
            prompt: Initial prompt to send
            working_dir: Working directory for the session
            subagents: List of subagent names available for this session
            max_turns: Maximum number of turns
            system_prompt: Optional system prompt to append
            allowed_tools: List of allowed tools
            
        Returns:
            Session information including session_id and initial response
        """
        async with self._session_lock:
            if len(self._sessions) >= self.max_concurrent_sessions:
                # Clean up inactive sessions
                await self._cleanup_inactive_sessions()
                
                if len(self._sessions) >= self.max_concurrent_sessions:
                    raise AgentError(f"Maximum concurrent sessions ({self.max_concurrent_sessions}) reached")
        
        # Create session ID
        process_id = str(uuid4())
        working_dir = working_dir or str(self.base_working_dir)
        
        # Build command
        cmd = [
            self.claude_cli_path,
            "-p", prompt,  # SDK mode with prompt
            "--output-format", "json",  # Structured output
            "--max-turns", str(max_turns or self.default_max_turns),
            "--cwd", working_dir
        ]
        
        # Add optional parameters
        if system_prompt:
            cmd.extend(["--append-system-prompt", system_prompt])
        
        if allowed_tools:
            cmd.extend(["--allowedTools", " ".join(allowed_tools)])
        
        # Add verbose for better debugging
        cmd.append("--verbose")
        
        try:
            # Execute Claude in SDK mode
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir
            )
            
            # Get output
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                raise AgentError(f"Claude CLI failed: {stderr.decode()}")
            
            # Parse JSON response
            response = json.loads(stdout.decode())
            
            # Extract session ID from response
            session_id = response.get("session_id", str(uuid4()))
            
            # Create session record
            session = ClaudeSession(
                session_id=session_id,
                process_id=process_id,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                working_dir=working_dir,
                subagents=subagents or [],
                total_cost=response.get("total_cost_usd", 0.0),
                turn_count=response.get("num_turns", 1),
                active=True
            )
            
            self._sessions[session_id] = session
            
            self.logger.logger.info(
                f"Created Claude session",
                extra={
                    "session_id": session_id,
                    "working_dir": working_dir,
                    "subagents": subagents
                }
            )
            
            return {
                "session_id": session_id,
                "response": response.get("result", ""),
                "cost": response.get("total_cost_usd", 0.0),
                "duration_ms": response.get("duration_ms", 0),
                "metadata": response
            }
            
        except json.JSONDecodeError as e:
            self.logger.log_error(e, {"operation": "create_session", "output": stdout.decode()[:500]})
            raise AgentError(f"Failed to parse Claude response: {str(e)}")
        except Exception as e:
            self.logger.log_error(e, {"operation": "create_session"})
            raise AgentError(f"Failed to create session: {str(e)}")
    
    async def continue_session(
        self,
        session_id: str,
        prompt: str,
        max_turns: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Continue an existing Claude session.
        
        Args:
            session_id: Session ID to continue
            prompt: New prompt to send
            max_turns: Maximum additional turns
            
        Returns:
            Response information
        """
        if session_id not in self._sessions:
            raise AgentError(f"Session {session_id} not found")
        
        session = self._sessions[session_id]
        
        if not session.active:
            raise AgentError(f"Session {session_id} is not active")
        
        # Build command to resume session
        cmd = [
            self.claude_cli_path,
            "--resume", session_id,
            prompt,
            "-p",  # SDK mode
            "--output-format", "json",
            "--max-turns", str(max_turns or self.default_max_turns),
            "--cwd", session.working_dir
        ]
        
        try:
            # Execute Claude with resume
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=session.working_dir
            )
            
            # Get output
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                raise AgentError(f"Claude CLI failed: {stderr.decode()}")
            
            # Parse JSON response
            response = json.loads(stdout.decode())
            
            # Update session info
            session.last_activity = datetime.utcnow()
            session.total_cost += response.get("total_cost_usd", 0.0)
            session.turn_count += response.get("num_turns", 1)
            
            return {
                "session_id": session_id,
                "response": response.get("result", ""),
                "cost": response.get("total_cost_usd", 0.0),
                "duration_ms": response.get("duration_ms", 0),
                "metadata": response
            }
            
        except json.JSONDecodeError as e:
            self.logger.log_error(e, {"operation": "continue_session", "session_id": session_id})
            raise AgentError(f"Failed to parse Claude response: {str(e)}")
        except Exception as e:
            self.logger.log_error(e, {"operation": "continue_session", "session_id": session_id})
            raise AgentError(f"Failed to continue session: {str(e)}")
    
    async def execute_with_subagent(
        self,
        prompt: str,
        subagent_name: str,
        working_dir: Optional[str] = None,
        max_turns: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a task using a specific subagent.
        
        Claude will automatically use the subagent if it exists in .claude/agents/
        and the task matches the subagent's description.
        
        Args:
            prompt: Task prompt
            subagent_name: Name of the subagent to use
            working_dir: Working directory
            max_turns: Maximum turns
            
        Returns:
            Execution results
        """
        working_dir = working_dir or str(self.base_working_dir)
        
        # Check if subagent exists
        subagent_path = Path(working_dir) / ".claude" / "agents" / f"{subagent_name}.md"
        if not subagent_path.exists():
            self.logger.logger.warning(f"Subagent {subagent_name} not found at {subagent_path}")
        
        # Create session with system prompt hinting at subagent
        # Claude will automatically delegate to the appropriate subagent
        return await self.create_session(
            prompt=prompt,
            working_dir=working_dir,
            subagents=[subagent_name],
            max_turns=max_turns,
            system_prompt=f"For this task, consider using the {subagent_name} subagent if appropriate."
        )
    
    async def run_parallel_sessions(
        self,
        tasks: List[Dict[str, Any]],
        max_concurrent: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Run multiple Claude sessions in parallel.
        
        Args:
            tasks: List of task dictionaries with 'prompt', 'subagent', etc.
            max_concurrent: Maximum concurrent executions
            
        Returns:
            List of results from all sessions
        """
        max_concurrent = max_concurrent or self.max_concurrent_sessions
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def run_task(task):
            async with semaphore:
                try:
                    if 'subagent' in task:
                        return await self.execute_with_subagent(
                            prompt=task['prompt'],
                            subagent_name=task['subagent'],
                            working_dir=task.get('working_dir'),
                            max_turns=task.get('max_turns')
                        )
                    else:
                        return await self.create_session(
                            prompt=task['prompt'],
                            working_dir=task.get('working_dir'),
                            max_turns=task.get('max_turns'),
                            system_prompt=task.get('system_prompt'),
                            allowed_tools=task.get('allowed_tools')
                        )
                except Exception as e:
                    self.logger.log_error(e, {"task": task})
                    return {
                        "error": str(e),
                        "task": task
                    }
        
        # Run all tasks concurrently
        results = await asyncio.gather(*[run_task(task) for task in tasks])
        
        return results
    
    async def get_session_info(self, session_id: str) -> Optional[ClaudeSession]:
        """Get information about a session."""
        return self._sessions.get(session_id)
    
    async def close_session(self, session_id: str) -> None:
        """Mark a session as inactive."""
        if session_id in self._sessions:
            self._sessions[session_id].active = False
            self.logger.logger.info(f"Closed session {session_id}")
    
    async def _cleanup_inactive_sessions(self) -> None:
        """Remove inactive sessions from memory."""
        inactive = [sid for sid, session in self._sessions.items() if not session.active]
        for sid in inactive:
            del self._sessions[sid]
        
        if inactive:
            self.logger.logger.info(f"Cleaned up {len(inactive)} inactive sessions")
    
    async def get_total_costs(self) -> float:
        """Get total costs across all sessions."""
        return sum(session.total_cost for session in self._sessions.values())
    
    async def shutdown(self) -> None:
        """Shutdown the SDK manager and clean up."""
        # Mark all sessions as inactive
        for session in self._sessions.values():
            session.active = False
        
        self.logger.logger.info("Claude SDK Manager shutdown complete")