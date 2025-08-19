"""
Claude Code CLI Manager for MAOS orchestration system.

This module manages actual Claude Code CLI processes, enabling real multi-agent
orchestration through subprocess management and IPC (Inter-Process Communication).
"""

import asyncio
import subprocess
import json
import os
import time
import signal
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError, AgentError


class ClaudeProcessState(Enum):
    """State of a Claude Code CLI process."""
    STARTING = "starting"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    TERMINATED = "terminated"


@dataclass
class ClaudeProcessInfo:
    """Information about a Claude Code CLI process."""
    process_id: str
    system_pid: int
    process: subprocess.Popen
    state: ClaudeProcessState
    working_dir: str
    created_at: datetime
    last_activity: datetime
    agent_name: Optional[str] = None
    current_task: Optional[str] = None
    resource_usage: Dict[str, float] = field(default_factory=dict)
    error_count: int = 0
    command_history: List[str] = field(default_factory=list)


class ClaudeCodeCLIManager:
    """
    Manages Claude Code CLI processes for real agent orchestration.
    
    This class handles:
    - Spawning and terminating Claude Code CLI processes
    - Inter-process communication with Claude instances
    - Process health monitoring and resource tracking
    - Command execution and response parsing
    """
    
    def __init__(
        self,
        max_processes: int = 10,
        claude_cli_path: str = "claude",
        base_working_dir: str = "/tmp/maos_claude",
        process_timeout: int = 300,
        enable_monitoring: bool = True
    ):
        """
        Initialize the Claude Code CLI Manager.
        
        Args:
            max_processes: Maximum number of concurrent Claude processes
            claude_cli_path: Path to Claude CLI executable
            base_working_dir: Base directory for Claude working directories
            process_timeout: Timeout for process operations in seconds
            enable_monitoring: Enable process monitoring
        """
        self.max_processes = max_processes
        self.claude_cli_path = claude_cli_path
        self.base_working_dir = Path(base_working_dir)
        self.process_timeout = process_timeout
        self.enable_monitoring = enable_monitoring
        
        # Process tracking
        self._processes: Dict[str, ClaudeProcessInfo] = {}
        self._process_lock = asyncio.Lock()
        
        # Monitoring
        self._monitor_task: Optional[asyncio.Task] = None
        self._monitor_interval = 5  # seconds
        
        # Logging
        self.logger = MAOSLogger("claude_cli_manager", str(uuid4()))
        
        # Ensure base directory exists
        self.base_working_dir.mkdir(parents=True, exist_ok=True)
        
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
                "Please install Claude Code CLI: npm install -g @anthropic-ai/claude-code"
            )
        except subprocess.TimeoutExpired:
            raise AgentError("Claude CLI verification timed out")
    
    async def start(self) -> None:
        """Start the CLI manager and monitoring."""
        if self.enable_monitoring:
            self._monitor_task = asyncio.create_task(self._monitor_processes())
        
        self.logger.logger.info("Claude Code CLI Manager started")
    
    async def stop(self) -> None:
        """Stop the CLI manager and terminate all processes."""
        # Cancel monitoring
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        # Terminate all processes
        async with self._process_lock:
            for process_id in list(self._processes.keys()):
                await self._terminate_process_internal(process_id)
        
        self.logger.logger.info("Claude Code CLI Manager stopped")
    
    async def spawn_claude_instance(
        self,
        agent_name: Optional[str] = None,
        working_dir: Optional[str] = None,
        env_vars: Optional[Dict[str, str]] = None,
        task: Optional[str] = None,
        max_turns: int = 10
    ) -> Tuple[str, Optional[str]]:
        """
        Spawn a new Claude Code CLI instance in SDK mode.
        
        Args:
            agent_name: Name for the agent/instance
            working_dir: Working directory for the instance
            env_vars: Additional environment variables
            task: Initial task for the Claude instance (SDK mode)
            max_turns: Maximum turns for SDK mode
            
        Returns:
            Tuple of (process_id, session_id) - session_id only if in SDK mode
        """
        async with self._process_lock:
            if len(self._processes) >= self.max_processes:
                raise AgentError(
                    f"Maximum number of Claude processes ({self.max_processes}) reached"
                )
            
            process_id = str(uuid4())
            session_id = None
            
            # Create working directory
            if not working_dir:
                working_dir = str(self.base_working_dir / f"claude_{process_id}")
            Path(working_dir).mkdir(parents=True, exist_ok=True)
            
            # Prepare environment
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)
            
            # Add MAOS-specific environment variables
            env.update({
                "MAOS_PROCESS_ID": process_id,
                "MAOS_AGENT_NAME": agent_name or f"agent_{process_id[:8]}"
            })
            
            try:
                # Build command based on mode
                if task:
                    # SDK mode with task
                    cmd = [
                        self.claude_cli_path,
                        "-p", task,
                        "--output-format", "json",
                        "--max-turns", str(max_turns),
                        "--verbose"
                    ]
                    session_id = f"session_{uuid4().hex}"
                else:
                    # Interactive mode (fallback)
                    cmd = [self.claude_cli_path]
                
                # Spawn Claude CLI process
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,  # Line buffered
                    cwd=working_dir,
                    env=env,
                    preexec_fn=os.setsid if os.name != 'nt' else None
                )
                
                # Create process info
                process_info = ClaudeProcessInfo(
                    process_id=process_id,
                    system_pid=process.pid,
                    process=process,
                    state=ClaudeProcessState.STARTING,
                    working_dir=working_dir,
                    created_at=datetime.utcnow(),
                    last_activity=datetime.utcnow(),
                    agent_name=agent_name
                )
                
                self._processes[process_id] = process_info
                
                # Wait for process to be ready
                await self._wait_for_ready(process_id)
                
                self.logger.logger.info(
                    f"Spawned Claude instance",
                    extra={
                        "process_id": process_id,
                        "pid": process.pid,
                        "agent_name": agent_name,
                        "working_dir": working_dir,
                        "mode": "SDK" if task else "interactive",
                        "session_id": session_id
                    }
                )
                
                return process_id, session_id
                
            except Exception as e:
                # Clean up on failure
                if process_id in self._processes:
                    await self._terminate_process_internal(process_id)
                
                self.logger.log_error(e, {
                    "operation": "spawn_claude_instance",
                    "agent_name": agent_name
                })
                raise AgentError(f"Failed to spawn Claude instance: {str(e)}")
    
    async def send_command(
        self,
        process_id: str,
        command: str,
        wait_for_response: bool = True,
        timeout: Optional[int] = None
    ) -> Optional[str]:
        """
        Send a command to a Claude instance.
        
        Args:
            process_id: Process ID of the Claude instance
            command: Command to send
            wait_for_response: Whether to wait for response
            timeout: Command timeout in seconds
            
        Returns:
            Response from Claude if wait_for_response is True
        """
        async with self._process_lock:
            if process_id not in self._processes:
                raise AgentError(f"Process {process_id} not found")
            
            process_info = self._processes[process_id]
            
            if process_info.state == ClaudeProcessState.TERMINATED:
                raise AgentError(f"Process {process_id} is terminated")
            
            if process_info.state == ClaudeProcessState.BUSY:
                raise AgentError(f"Process {process_id} is busy")
            
            # Update state
            process_info.state = ClaudeProcessState.BUSY
            process_info.last_activity = datetime.utcnow()
            process_info.command_history.append(command)
            
            # Keep last 100 commands in history
            if len(process_info.command_history) > 100:
                process_info.command_history = process_info.command_history[-100:]
        
        try:
            # Send command
            process_info.process.stdin.write(command + "\n")
            process_info.process.stdin.flush()
            
            if not wait_for_response:
                process_info.state = ClaudeProcessState.READY
                return None
            
            # Wait for response
            timeout = timeout or self.process_timeout
            response = await self._read_response(process_info.process, timeout)
            
            # Update state
            process_info.state = ClaudeProcessState.READY
            
            return response
            
        except Exception as e:
            process_info.state = ClaudeProcessState.ERROR
            process_info.error_count += 1
            
            self.logger.log_error(e, {
                "operation": "send_command",
                "process_id": process_id,
                "command": command[:100]  # Log first 100 chars
            })
            
            # Check if process needs recovery
            if process_info.error_count > 3:
                await self._recover_process(process_id)
            
            raise AgentError(f"Command execution failed: {str(e)}")
    
    async def execute_agent_task(
        self,
        process_id: str,
        agent_yaml: str,
        task_description: str
    ) -> Dict[str, Any]:
        """
        Execute a task using a specific agent definition.
        
        Args:
            process_id: Process ID of the Claude instance
            agent_yaml: YAML definition for the agent
            task_description: Task to execute
            
        Returns:
            Task execution results
        """
        # First, create the agent
        await self.send_command(process_id, "/agents")
        await asyncio.sleep(0.5)  # Brief pause for agent creation prompt
        
        # Send agent YAML
        await self.send_command(process_id, agent_yaml)
        await asyncio.sleep(1)  # Wait for agent creation
        
        # Execute task
        response = await self.send_command(
            process_id,
            f"/task {task_description}",
            wait_for_response=True,
            timeout=600  # 10 minutes for complex tasks
        )
        
        # Parse response
        return self._parse_task_response(response)
    
    async def terminate_process(self, process_id: str) -> None:
        """
        Terminate a Claude instance.
        
        Args:
            process_id: Process ID to terminate
        """
        async with self._process_lock:
            await self._terminate_process_internal(process_id)
    
    async def _terminate_process_internal(self, process_id: str) -> None:
        """Internal method to terminate a process (must be called with lock)."""
        if process_id not in self._processes:
            return
        
        process_info = self._processes[process_id]
        
        try:
            # Try graceful shutdown first
            if process_info.process.poll() is None:
                process_info.process.terminate()
                
                # Wait briefly for termination
                for _ in range(10):
                    if process_info.process.poll() is not None:
                        break
                    await asyncio.sleep(0.1)
                
                # Force kill if still running
                if process_info.process.poll() is None:
                    if os.name != 'nt':
                        os.killpg(os.getpgid(process_info.process.pid), signal.SIGKILL)
                    else:
                        process_info.process.kill()
            
            process_info.state = ClaudeProcessState.TERMINATED
            
            self.logger.logger.info(
                f"Terminated Claude instance",
                extra={"process_id": process_id, "pid": process_info.system_pid}
            )
            
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "terminate_process",
                "process_id": process_id
            })
        
        finally:
            # Remove from tracking
            del self._processes[process_id]
    
    async def _wait_for_ready(self, process_id: str, timeout: int = 30) -> None:
        """Wait for a Claude instance to be ready."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if process_id not in self._processes:
                raise AgentError(f"Process {process_id} terminated during startup")
            
            process_info = self._processes[process_id]
            
            # Check if process is still running
            if process_info.process.poll() is not None:
                raise AgentError(f"Process {process_id} terminated unexpectedly")
            
            # Try to read initial output
            try:
                output = await asyncio.wait_for(
                    asyncio.create_task(self._read_line_async(process_info.process)),
                    timeout=1
                )
                
                # Check for ready indicators
                if "Claude" in output or "Ready" in output or ">" in output:
                    process_info.state = ClaudeProcessState.READY
                    return
                    
            except asyncio.TimeoutError:
                pass
            
            await asyncio.sleep(0.5)
        
        raise AgentError(f"Process {process_id} failed to become ready within {timeout} seconds")
    
    async def _read_response(
        self,
        process: subprocess.Popen,
        timeout: int
    ) -> str:
        """Read response from Claude process."""
        response_lines = []
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                line = await asyncio.wait_for(
                    asyncio.create_task(self._read_line_async(process)),
                    timeout=1
                )
                
                if line:
                    response_lines.append(line)
                    
                    # Check for response completion markers
                    if self._is_response_complete(line, response_lines):
                        break
                        
            except asyncio.TimeoutError:
                # Check if we have enough response
                if response_lines and self._looks_complete(response_lines):
                    break
                continue
        
        return "\n".join(response_lines)
    
    async def _read_line_async(self, process: subprocess.Popen) -> str:
        """Asynchronously read a line from process stdout."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, process.stdout.readline)
    
    def _is_response_complete(self, line: str, lines: List[str]) -> bool:
        """Check if response is complete."""
        # Common completion indicators
        completion_markers = [
            "Human:",
            "Assistant:",
            "> ",
            "```",
            "Task completed",
            "Done",
            "[END]"
        ]
        
        for marker in completion_markers:
            if marker in line:
                return True
        
        # Check for multi-line code blocks
        code_blocks = sum(1 for l in lines if "```" in l)
        if code_blocks > 0 and code_blocks % 2 == 0:
            return True
        
        return False
    
    def _looks_complete(self, lines: List[str]) -> bool:
        """Heuristic to check if response looks complete."""
        if not lines:
            return False
        
        # Join lines and check
        full_response = "\n".join(lines)
        
        # Check for common patterns
        if len(full_response) > 100:  # Reasonable response length
            if any(marker in full_response for marker in [".", "!", "?", "```"]):
                return True
        
        return False
    
    def _parse_task_response(self, response: str) -> Dict[str, Any]:
        """Parse task execution response."""
        result = {
            "raw_response": response,
            "success": True,
            "error": None,
            "data": {}
        }
        
        # Try to extract structured data
        if "```json" in response:
            try:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
                result["data"] = json.loads(json_str)
            except (ValueError, json.JSONDecodeError):
                pass
        
        # Check for errors
        error_indicators = ["error:", "failed:", "exception:", "traceback:"]
        for indicator in error_indicators:
            if indicator.lower() in response.lower():
                result["success"] = False
                result["error"] = response
                break
        
        return result
    
    async def _recover_process(self, process_id: str) -> None:
        """Attempt to recover a failed process."""
        self.logger.logger.warning(
            f"Attempting to recover process",
            extra={"process_id": process_id}
        )
        
        if process_id in self._processes:
            process_info = self._processes[process_id]
            
            # Terminate the failed process
            await self._terminate_process_internal(process_id)
            
            # Respawn with same configuration
            try:
                new_process_id = await self.spawn_claude_instance(
                    agent_name=process_info.agent_name,
                    working_dir=process_info.working_dir
                )
                
                self.logger.logger.info(
                    f"Process recovered",
                    extra={
                        "old_process_id": process_id,
                        "new_process_id": new_process_id
                    }
                )
                
            except Exception as e:
                self.logger.log_error(e, {
                    "operation": "recover_process",
                    "process_id": process_id
                })
    
    async def _monitor_processes(self) -> None:
        """Monitor process health and resource usage."""
        while True:
            try:
                await asyncio.sleep(self._monitor_interval)
                
                async with self._process_lock:
                    for process_id, process_info in list(self._processes.items()):
                        # Check if process is still running
                        if process_info.process.poll() is not None:
                            self.logger.logger.warning(
                                f"Process terminated unexpectedly",
                                extra={"process_id": process_id}
                            )
                            process_info.state = ClaudeProcessState.TERMINATED
                            del self._processes[process_id]
                            continue
                        
                        # Update resource usage
                        try:
                            proc = psutil.Process(process_info.system_pid)
                            process_info.resource_usage = {
                                "cpu_percent": proc.cpu_percent(),
                                "memory_mb": proc.memory_info().rss / 1024 / 1024,
                                "num_threads": proc.num_threads(),
                                "num_fds": proc.num_fds() if hasattr(proc, "num_fds") else 0
                            }
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                        
                        # Check for inactive processes
                        inactive_time = (datetime.utcnow() - process_info.last_activity).total_seconds()
                        if inactive_time > 3600:  # 1 hour
                            self.logger.logger.info(
                                f"Terminating inactive process",
                                extra={
                                    "process_id": process_id,
                                    "inactive_seconds": inactive_time
                                }
                            )
                            await self._terminate_process_internal(process_id)
                            
            except Exception as e:
                self.logger.log_error(e, {"operation": "monitor_processes"})
    
    def get_process_info(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a Claude process."""
        if process_id not in self._processes:
            return None
        
        process_info = self._processes[process_id]
        
        return {
            "process_id": process_info.process_id,
            "system_pid": process_info.system_pid,
            "state": process_info.state.value,
            "working_dir": process_info.working_dir,
            "agent_name": process_info.agent_name,
            "current_task": process_info.current_task,
            "created_at": process_info.created_at.isoformat(),
            "last_activity": process_info.last_activity.isoformat(),
            "resource_usage": process_info.resource_usage,
            "error_count": process_info.error_count,
            "command_count": len(process_info.command_history)
        }
    
    def list_processes(self) -> List[Dict[str, Any]]:
        """List all Claude processes."""
        return [
            self.get_process_info(process_id)
            for process_id in self._processes.keys()
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get manager statistics."""
        total_processes = len(self._processes)
        states = {}
        total_cpu = 0
        total_memory = 0
        
        for process_info in self._processes.values():
            state = process_info.state.value
            states[state] = states.get(state, 0) + 1
            
            if process_info.resource_usage:
                total_cpu += process_info.resource_usage.get("cpu_percent", 0)
                total_memory += process_info.resource_usage.get("memory_mb", 0)
        
        return {
            "total_processes": total_processes,
            "max_processes": self.max_processes,
            "states": states,
            "total_cpu_percent": total_cpu,
            "total_memory_mb": total_memory,
            "available_slots": self.max_processes - total_processes
        }