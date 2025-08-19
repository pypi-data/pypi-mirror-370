"""
Claude Agent Process wrapper for MAOS orchestration system.

This module provides a high-level wrapper around Claude Code CLI processes,
integrating them seamlessly with the MAOS agent model and task execution system.
"""

import asyncio
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field

from .agent import Agent, AgentStatus, AgentCapability, AgentType
from .task import Task, TaskStatus
from ..core.claude_cli_manager import ClaudeCodeCLIManager, ClaudeProcessState
from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import AgentError, TaskError


@dataclass
class AgentDefinition:
    """Agent definition that can be converted to YAML for Claude Code."""
    name: str
    color: str
    type: str
    version: str = "1.0.0"
    created: str = field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d"))
    author: str = "MAOS"
    
    # Metadata
    description: str = ""
    specialization: str = ""
    complexity: str = "simple"
    autonomous: bool = True
    
    # Triggers
    keywords: List[str] = field(default_factory=list)
    file_patterns: List[str] = field(default_factory=list)
    task_patterns: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    
    # Capabilities
    allowed_tools: List[str] = field(default_factory=lambda: ["Read", "Grep", "Glob"])
    restricted_tools: List[str] = field(default_factory=lambda: ["Write", "Edit", "Bash"])
    max_file_operations: int = 50
    max_execution_time: int = 300
    memory_access: str = "both"
    
    # Constraints
    allowed_paths: List[str] = field(default_factory=lambda: ["src/**", "app/**"])
    forbidden_paths: List[str] = field(default_factory=lambda: ["node_modules/**", ".git/**"])
    max_file_size: int = 1048576  # 1MB
    allowed_file_types: List[str] = field(default_factory=lambda: [".py", ".js", ".ts"])
    
    # Behavior
    error_handling: str = "lenient"
    confirmation_required: List[str] = field(default_factory=list)
    auto_rollback: bool = False
    logging_level: str = "info"
    
    # Communication
    style: str = "professional"
    update_frequency: str = "summary"
    include_code_snippets: bool = True
    emoji_usage: str = "minimal"
    
    # Integration
    can_spawn: List[str] = field(default_factory=list)
    can_delegate_to: List[str] = field(default_factory=list)
    requires_approval_from: List[str] = field(default_factory=list)
    shares_context_with: List[str] = field(default_factory=list)
    
    # Optimization
    parallel_operations: bool = True
    batch_size: int = 10
    cache_results: bool = True
    memory_limit: str = "256MB"
    
    # Hooks
    pre_execution: str = ""
    post_execution: str = ""
    on_error: str = ""
    
    # Examples and prompt
    examples: List[Dict[str, str]] = field(default_factory=list)
    system_prompt: str = ""
    
    def to_yaml(self) -> str:
        """Convert agent definition to YAML format for Claude Code."""
        data = {
            "name": self.name,
            "color": self.color,
            "type": self.type,
            "version": self.version,
            "created": self.created,
            "author": self.author,
            "metadata": {
                "description": self.description,
                "specialization": self.specialization,
                "complexity": self.complexity,
                "autonomous": self.autonomous
            },
            "triggers": {
                "keywords": self.keywords,
                "file_patterns": self.file_patterns,
                "task_patterns": self.task_patterns,
                "domains": self.domains
            },
            "capabilities": {
                "allowed_tools": self.allowed_tools,
                "restricted_tools": self.restricted_tools,
                "max_file_operations": self.max_file_operations,
                "max_execution_time": self.max_execution_time,
                "memory_access": self.memory_access
            },
            "constraints": {
                "allowed_paths": self.allowed_paths,
                "forbidden_paths": self.forbidden_paths,
                "max_file_size": self.max_file_size,
                "allowed_file_types": self.allowed_file_types
            },
            "behavior": {
                "error_handling": self.error_handling,
                "confirmation_required": self.confirmation_required,
                "auto_rollback": self.auto_rollback,
                "logging_level": self.logging_level
            },
            "communication": {
                "style": self.style,
                "update_frequency": self.update_frequency,
                "include_code_snippets": self.include_code_snippets,
                "emoji_usage": self.emoji_usage
            },
            "integration": {
                "can_spawn": self.can_spawn,
                "can_delegate_to": self.can_delegate_to,
                "requires_approval_from": self.requires_approval_from,
                "shares_context_with": self.shares_context_with
            },
            "optimization": {
                "parallel_operations": self.parallel_operations,
                "batch_size": self.batch_size,
                "cache_results": self.cache_results,
                "memory_limit": self.memory_limit
            }
        }
        
        # Add hooks if provided
        if any([self.pre_execution, self.post_execution, self.on_error]):
            data["hooks"] = {}
            if self.pre_execution:
                data["hooks"]["pre_execution"] = self.pre_execution
            if self.post_execution:
                data["hooks"]["post_execution"] = self.post_execution
            if self.on_error:
                data["hooks"]["on_error"] = self.on_error
        
        # Add examples if provided
        if self.examples:
            data["examples"] = self.examples
        
        # Convert to YAML with the system prompt at the end
        yaml_content = "---\n" + yaml.dump(data, default_flow_style=False, sort_keys=False)
        yaml_content += "---\n\n"
        
        if self.system_prompt:
            yaml_content += f"# {self.name}\n\n{self.system_prompt}"
        
        return yaml_content


class ClaudeAgentProcess:
    """
    High-level wrapper around Claude Code CLI processes for MAOS integration.
    
    This class provides:
    - Agent definition management and YAML generation
    - Task execution through Claude Code CLI
    - State synchronization with MAOS Agent model
    - Error handling and recovery
    """
    
    def __init__(
        self,
        cli_manager: ClaudeCodeCLIManager,
        agent: Agent,
        agent_definition: AgentDefinition,
        working_dir: Optional[str] = None
    ):
        """
        Initialize Claude Agent Process wrapper.
        
        Args:
            cli_manager: Claude CLI manager instance
            agent: MAOS Agent model
            agent_definition: Agent definition for Claude Code
            working_dir: Working directory for the agent
        """
        self.cli_manager = cli_manager
        self.agent = agent
        self.agent_definition = agent_definition
        self.working_dir = working_dir
        
        # Process management
        self.process_id: Optional[str] = None
        self.is_initialized = False
        self.current_task: Optional[Task] = None
        
        # State tracking
        self._last_sync = datetime.utcnow()
        self._execution_history: List[Dict[str, Any]] = []
        
        # Logging
        self.logger = MAOSLogger(f"claude_agent_{agent.id}", str(agent.id))
    
    async def initialize(self) -> None:
        """Initialize the Claude agent process."""
        try:
            # Spawn Claude instance
            self.process_id = await self.cli_manager.spawn_claude_instance(
                agent_name=self.agent_definition.name,
                working_dir=self.working_dir
            )
            
            # Create agent in Claude Code
            agent_yaml = self.agent_definition.to_yaml()
            
            # Send agent creation commands
            await self.cli_manager.send_command(self.process_id, "/agents")
            await asyncio.sleep(1)  # Wait for agent creation prompt
            
            await self.cli_manager.send_command(
                self.process_id,
                agent_yaml,
                wait_for_response=True,
                timeout=30
            )
            
            # Update agent status
            self.agent.status = AgentStatus.IDLE
            self.agent.metadata["claude_process_id"] = self.process_id
            self.agent.metadata["agent_definition"] = self.agent_definition.name
            
            self.is_initialized = True
            
            self.logger.logger.info(
                f"Initialized Claude agent",
                extra={
                    "agent_id": str(self.agent.id),
                    "process_id": self.process_id,
                    "agent_name": self.agent_definition.name
                }
            )
            
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "initialize",
                "agent_id": str(self.agent.id)
            })
            self.agent.status = AgentStatus.ERROR
            self.agent.last_error = str(e)
            raise AgentError(f"Failed to initialize Claude agent: {str(e)}")
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a task using the Claude agent.
        
        Args:
            task: Task to execute
            
        Returns:
            Task execution results
        """
        if not self.is_initialized:
            raise AgentError("Agent not initialized")
        
        if not self.process_id:
            raise AgentError("No Claude process available")
        
        if self.current_task:
            raise AgentError("Agent is already executing a task")
        
        self.current_task = task
        self.agent.status = AgentStatus.BUSY
        
        try:
            # Prepare task command
            task_description = self._format_task_for_claude(task)
            
            # Execute task
            response = await self.cli_manager.send_command(
                self.process_id,
                f"/task {task_description}",
                wait_for_response=True,
                timeout=task.timeout_seconds or 300
            )
            
            # Parse results
            results = self._parse_task_results(response)
            
            # Update execution history
            execution_record = {
                "task_id": str(task.id),
                "task_name": task.name,
                "executed_at": datetime.utcnow().isoformat(),
                "success": results.get("success", False),
                "response_length": len(response),
                "execution_time": results.get("execution_time", 0)
            }
            
            self._execution_history.append(execution_record)
            
            # Keep last 50 executions
            if len(self._execution_history) > 50:
                self._execution_history = self._execution_history[-50:]
            
            # Update agent status
            self.agent.status = AgentStatus.IDLE
            self.agent.last_activity = datetime.utcnow()
            self.agent.tasks_completed += 1
            
            if results.get("success", False):
                self.agent.successful_tasks += 1
            else:
                self.agent.failed_tasks += 1
                self.agent.last_error = results.get("error", "Task execution failed")
            
            self.current_task = None
            
            self.logger.logger.info(
                f"Task execution completed",
                extra={
                    "agent_id": str(self.agent.id),
                    "task_id": str(task.id),
                    "success": results.get("success", False)
                }
            )
            
            return results
            
        except Exception as e:
            # Update agent on error
            self.agent.status = AgentStatus.ERROR
            self.agent.last_error = str(e)
            self.agent.failed_tasks += 1
            self.current_task = None
            
            self.logger.log_error(e, {
                "operation": "execute_task",
                "agent_id": str(self.agent.id),
                "task_id": str(task.id)
            })
            
            raise TaskError(f"Task execution failed: {str(e)}")
    
    async def send_message(self, message: str) -> str:
        """
        Send a direct message to the Claude agent.
        
        Args:
            message: Message to send
            
        Returns:
            Agent response
        """
        if not self.is_initialized or not self.process_id:
            raise AgentError("Agent not initialized")
        
        response = await self.cli_manager.send_command(
            self.process_id,
            message,
            wait_for_response=True
        )
        
        return response
    
    async def save_context(self) -> Dict[str, Any]:
        """
        Save agent context using Claude's /save command.
        
        Returns:
            Context save information
        """
        if not self.is_initialized or not self.process_id:
            raise AgentError("Agent not initialized")
        
        response = await self.cli_manager.send_command(
            self.process_id,
            "/save",
            wait_for_response=True
        )
        
        return {
            "saved_at": datetime.utcnow().isoformat(),
            "response": response,
            "agent_id": str(self.agent.id)
        }
    
    async def load_context(self, context_path: str) -> bool:
        """
        Load agent context from a saved state.
        
        Args:
            context_path: Path to saved context
            
        Returns:
            True if successfully loaded
        """
        if not self.is_initialized or not self.process_id:
            raise AgentError("Agent not initialized")
        
        try:
            response = await self.cli_manager.send_command(
                self.process_id,
                f"/load {context_path}",
                wait_for_response=True
            )
            
            # Check if load was successful
            success = "loaded" in response.lower() or "restored" in response.lower()
            
            if success:
                self.logger.logger.info(
                    f"Context loaded successfully",
                    extra={
                        "agent_id": str(self.agent.id),
                        "context_path": context_path
                    }
                )
            
            return success
            
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "load_context",
                "agent_id": str(self.agent.id),
                "context_path": context_path
            })
            return False
    
    async def terminate(self) -> None:
        """Terminate the Claude agent process."""
        if self.process_id:
            try:
                # Save context before terminating
                await self.save_context()
            except Exception:
                pass  # Don't fail termination on save error
            
            await self.cli_manager.terminate_process(self.process_id)
            self.process_id = None
        
        self.agent.status = AgentStatus.TERMINATED
        self.is_initialized = False
        
        self.logger.logger.info(
            f"Terminated Claude agent",
            extra={"agent_id": str(self.agent.id)}
        )
    
    def _format_task_for_claude(self, task: Task) -> str:
        """Format a MAOS task for Claude Code execution."""
        # Base task description
        description = task.description
        
        # Add parameters if available
        if task.parameters:
            param_str = "\n".join([
                f"- {k}: {v}" for k, v in task.parameters.items()
            ])
            description += f"\n\nParameters:\n{param_str}"
        
        # Add constraints from agent definition
        if self.agent_definition.allowed_paths:
            paths_str = ", ".join(self.agent_definition.allowed_paths)
            description += f"\n\nWork within these paths: {paths_str}"
        
        # Add priority information
        if task.priority:
            description += f"\n\nPriority: {task.priority.value}"
        
        # Add timeout information
        if task.timeout_seconds:
            description += f"\n\nTimeout: {task.timeout_seconds} seconds"
        
        return description
    
    def _parse_task_results(self, response: str) -> Dict[str, Any]:
        """Parse Claude Code response into structured results."""
        results = {
            "success": True,
            "raw_response": response,
            "error": None,
            "data": {},
            "files_created": [],
            "files_modified": [],
            "commands_executed": []
        }
        
        # Check for error indicators
        error_keywords = [
            "error:", "failed:", "exception:", "traceback:",
            "permission denied", "not found", "invalid"
        ]
        
        response_lower = response.lower()
        for keyword in error_keywords:
            if keyword in response_lower:
                results["success"] = False
                results["error"] = response
                break
        
        # Extract JSON data if present
        if "```json" in response:
            try:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
                results["data"] = json.loads(json_str)
            except (ValueError, json.JSONDecodeError):
                pass
        
        # Extract file operations
        if "created:" in response_lower or "wrote:" in response_lower:
            # Simple heuristic to extract file names
            lines = response.split("\n")
            for line in lines:
                if "created:" in line.lower() or "wrote:" in line.lower():
                    # Extract filename from line
                    parts = line.split()
                    for part in parts:
                        if "/" in part or "\\" in part:
                            results["files_created"].append(part)
        
        # Extract command executions
        if "executed:" in response_lower or "ran:" in response_lower:
            lines = response.split("\n")
            for line in lines:
                if "executed:" in line.lower() or "ran:" in line.lower():
                    results["commands_executed"].append(line.strip())
        
        # Check for successful completion indicators
        success_indicators = [
            "completed", "done", "finished", "success",
            "✓", "✅", "task completed"
        ]
        
        for indicator in success_indicators:
            if indicator in response_lower:
                results["success"] = True
                break
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        process_info = None
        if self.process_id:
            process_info = self.cli_manager.get_process_info(self.process_id)
        
        return {
            "agent_id": str(self.agent.id),
            "agent_name": self.agent_definition.name,
            "status": self.agent.status.value,
            "is_initialized": self.is_initialized,
            "process_id": self.process_id,
            "process_info": process_info,
            "current_task": str(self.current_task.id) if self.current_task else None,
            "tasks_completed": self.agent.tasks_completed,
            "successful_tasks": self.agent.successful_tasks,
            "failed_tasks": self.agent.failed_tasks,
            "last_activity": self.agent.last_activity.isoformat() if self.agent.last_activity else None,
            "last_error": self.agent.last_error,
            "execution_history_count": len(self._execution_history)
        }
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get task execution history."""
        return self._execution_history.copy()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics."""
        total_tasks = self.agent.tasks_completed
        
        if total_tasks == 0:
            return {
                "total_tasks": 0,
                "success_rate": 0,
                "average_execution_time": 0,
                "error_rate": 0
            }
        
        success_rate = (self.agent.successful_tasks / total_tasks) * 100
        error_rate = (self.agent.failed_tasks / total_tasks) * 100
        
        # Calculate average execution time from recent history
        recent_executions = self._execution_history[-10:]  # Last 10 executions
        avg_time = 0
        if recent_executions:
            total_time = sum(
                exec_record.get("execution_time", 0)
                for exec_record in recent_executions
            )
            avg_time = total_time / len(recent_executions)
        
        return {
            "total_tasks": total_tasks,
            "successful_tasks": self.agent.successful_tasks,
            "failed_tasks": self.agent.failed_tasks,
            "success_rate": round(success_rate, 2),
            "error_rate": round(error_rate, 2),
            "average_execution_time": round(avg_time, 2),
            "uptime_hours": self._get_uptime_hours()
        }
    
    def _get_uptime_hours(self) -> float:
        """Calculate agent uptime in hours."""
        if self.agent.created_at:
            uptime = datetime.utcnow() - self.agent.created_at
            return round(uptime.total_seconds() / 3600, 2)
        return 0