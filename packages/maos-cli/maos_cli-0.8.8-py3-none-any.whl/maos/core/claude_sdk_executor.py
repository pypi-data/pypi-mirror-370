"""
Claude SDK Executor - Actually runs Claude agents autonomously using the SDK.
This replaces the subagent file creation approach with real process execution.
"""

import asyncio
import json
import subprocess
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentExecution:
    """Represents an autonomous Claude agent execution"""
    agent_id: str
    task: str
    session_id: Optional[str] = None
    system_prompt: Optional[str] = None
    allowed_tools: List[str] = None
    max_turns: int = 5
    output_format: str = "json"
    
    def __post_init__(self):
        if self.allowed_tools is None:
            self.allowed_tools = ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
        # Don't auto-generate session_id for new executions
        # Only set session_id when explicitly resuming an existing session


class ClaudeSDKExecutor:
    """
    Executes Claude agents autonomously using the SDK.
    Runs multiple agents in parallel without manual intervention.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.running_agents: Dict[str, asyncio.subprocess.Process] = {}
        self.agent_results: Dict[str, Any] = {}
    
    def _is_claude_code_authenticated(self) -> bool:
        """Check if Claude Code is running and authenticated."""
        import subprocess
        try:
            # Try to run a simple claude command to check if it's authenticated
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                timeout=2,
                text=True
            )
            # If claude command works, it's likely authenticated
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
        
    async def execute_agent(self, execution: AgentExecution) -> Dict[str, Any]:
        """
        Execute a single Claude agent autonomously.
        Uses --dangerously-skip-permissions for fully autonomous operation.
        """
        # Map agent types to Claude Code agents if available
        agent_mapping = {
            "security": "security-auditor",
            "security-auditor": "security-auditor", 
            "reviewer": "reviewer",
            "agent-162719-2": "agent-162719-2"
        }
        
        # Get agent name from agent_id (e.g., "security-abc123" -> "security")
        agent_type = execution.agent_id.split('-')[0] if '-' in execution.agent_id else execution.agent_id
        claude_agent = agent_mapping.get(agent_type)
        
        # Use Claude Code agent if available, otherwise use generic prompt
        if claude_agent:
            cmd = [
                "claude",
                f"@{claude_agent}",  # Use specific agent
                "-p",  # Print mode (non-interactive)
                "--output-format", execution.output_format
            ]
            print(f"🤖 Using Claude Code agent: @{claude_agent}")
        else:
            cmd = [
                "claude",
                "-p",  # Print mode (non-interactive)
                "--output-format", execution.output_format
            ]
            print(f"🤖 Using generic Claude with custom system prompt")
            
            # Add system prompt if provided (only for generic mode)
            if execution.system_prompt:
                cmd.extend(["--append-system-prompt", execution.system_prompt])
            
            # Add allowed tools (only for generic mode)
            if execution.allowed_tools:
                cmd.extend(["--allowedTools", ",".join(execution.allowed_tools)])
        
        # Resume session if provided (only for existing sessions)
        if execution.session_id:
            cmd.extend(["--resume", execution.session_id])
            print(f"🔄 Resuming session: {execution.session_id}")
        else:
            print(f"🆕 Starting new session for agent: {execution.agent_id}")
        
        # DON'T add the task as an argument - will provide via stdin
        # cmd.append(execution.task)  # REMOVED - claude -p needs stdin input
        
        # Use current environment (Claude Code uses OAuth, not API keys)
        env = dict(os.environ)
        print("🔗 Using authenticated Claude Code session (OAuth via Anthropic Console)")
        print("⏳ Note: Claude Code may take 30-60 seconds to start and process...")
        
        logger.info(f"Starting agent {execution.agent_id}: {' '.join(cmd)}")
        logger.info(f"Task (via stdin): {execution.task}")
        
        try:
            # Run Claude SDK command with stdin input
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            self.running_agents[execution.agent_id] = process
            
            # Send the task via stdin and wait for completion
            # Claude Code can take 30-60 seconds to start and process
            try:
                # Send task via stdin and close stdin
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=execution.task.encode()),
                    timeout=600  # 10 minutes timeout - Claude needs time to think and execute!
                )
            except asyncio.TimeoutError:
                logger.error(f"Claude Code timed out after 600s for {execution.agent_id}")
                process.terminate()
                await process.wait()
                return {
                    "agent_id": execution.agent_id,
                    "task": execution.task,
                    "session_id": execution.session_id,
                    "success": False,
                    "error": "Claude Code command timed out after 600 seconds (10 minutes)"
                }
            
            # Parse output
            if execution.output_format == "json":
                try:
                    # Parse the JSON output
                    result = json.loads(stdout.decode())
                    
                    # Extract key information
                    return {
                        "agent_id": execution.agent_id,
                        "task": execution.task,
                        "session_id": result.get("session_id", execution.session_id),
                        "result": result.get("result", ""),
                        "cost": result.get("total_cost_usd", 0),
                        "duration_ms": result.get("duration_ms", 0),
                        "num_turns": result.get("num_turns", 0),
                        "success": not result.get("is_error", False),
                        "error": stderr.decode() if stderr else None
                    }
                except json.JSONDecodeError:
                    # Fall back to text output
                    return {
                        "agent_id": execution.agent_id,
                        "task": execution.task,
                        "session_id": execution.session_id,
                        "result": stdout.decode(),
                        "success": process.returncode == 0,
                        "error": stderr.decode() if stderr else None
                    }
            else:
                return {
                    "agent_id": execution.agent_id,
                    "task": execution.task,
                    "session_id": execution.session_id,
                    "result": stdout.decode(),
                    "success": process.returncode == 0,
                    "error": stderr.decode() if stderr else None
                }
                
        except Exception as e:
            logger.error(f"Error executing agent {execution.agent_id}: {e}")
            return {
                "agent_id": execution.agent_id,
                "task": execution.task,
                "session_id": execution.session_id,
                "result": "",
                "success": False,
                "error": str(e)
            }
        finally:
            # Clean up
            if execution.agent_id in self.running_agents:
                del self.running_agents[execution.agent_id]
    
    async def execute_parallel(self, executions: List[AgentExecution]) -> List[Dict[str, Any]]:
        """
        Execute multiple Claude agents in parallel.
        This is TRUE parallel execution - each agent runs in its own process.
        """
        logger.info(f"Executing {len(executions)} agents in parallel")
        
        # Create tasks for all agents
        tasks = [
            self.execute_agent(execution)
            for execution in executions
        ]
        
        # Run all agents in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "agent_id": executions[i].agent_id,
                    "task": executions[i].task,
                    "success": False,
                    "error": str(result)
                })
            else:
                processed_results.append(result)
                self.agent_results[result["agent_id"]] = result
        
        return processed_results
    
    async def execute_batches(self, batches: List[List[AgentExecution]]) -> List[List[Dict[str, Any]]]:
        """
        Execute multiple batches of agents sequentially.
        Each batch runs in parallel, next batch waits for previous to complete.
        """
        all_results = []
        
        for i, batch in enumerate(batches, 1):
            logger.info(f"Executing batch {i}/{len(batches)} with {len(batch)} agents")
            batch_results = await self.execute_parallel(batch)
            all_results.append(batch_results)
            
            # Log batch completion
            successful = sum(1 for r in batch_results if r.get("success", False))
            logger.info(f"Batch {i} complete: {successful}/{len(batch)} successful")
        
        return all_results
    
    async def resume_agent(self, session_id: str, new_task: str, **kwargs) -> Dict[str, Any]:
        """
        Resume a previous agent session with a new task.
        Maintains conversation context from the previous execution.
        """
        execution = AgentExecution(
            agent_id=f"resumed-{session_id[:8]}",
            task=new_task,
            session_id=session_id,
            **kwargs
        )
        return await self.execute_agent(execution)
    
    def get_agent_result(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a specific agent execution"""
        return self.agent_results.get(agent_id)
    
    def get_all_results(self) -> Dict[str, Any]:
        """Get all agent results"""
        return self.agent_results.copy()
    
    async def kill_agent(self, agent_id: str) -> bool:
        """Kill a running agent process"""
        if agent_id in self.running_agents:
            process = self.running_agents[agent_id]
            process.terminate()
            await process.wait()
            del self.running_agents[agent_id]
            logger.info(f"Killed agent {agent_id}")
            return True
        return False
    
    async def kill_all_agents(self):
        """Kill all running agent processes"""
        for agent_id in list(self.running_agents.keys()):
            await self.kill_agent(agent_id)


import os  # Add this import at the top