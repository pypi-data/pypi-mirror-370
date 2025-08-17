"""
Claude Command Interface for MAOS orchestration system.

This module provides a high-level interface for communicating with Claude Code CLI
instances, handling complex command sequences, and parsing structured responses.
"""

import asyncio
import json
import re
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import UUID
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from ..core.claude_cli_manager import ClaudeCodeCLIManager
from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError


class ClaudeCommandType(Enum):
    """Types of Claude Code commands."""
    AGENT_CREATE = "agent_create"
    TASK_EXECUTE = "task_execute"
    SAVE_CONTEXT = "save_context"
    LOAD_CONTEXT = "load_context"
    DIRECT_MESSAGE = "direct_message"
    FILE_OPERATION = "file_operation"
    COORDINATION = "coordination"


@dataclass
class CommandResult:
    """Result of a Claude command execution."""
    command_type: ClaudeCommandType
    success: bool
    response: str
    structured_data: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ClaudeCommandInterface:
    """
    High-level interface for Claude Code CLI communication.
    
    This class provides:
    - Command composition and execution
    - Response parsing and structure extraction
    - Context management and persistence
    - Multi-turn conversation handling
    - Error recovery and retry logic
    """
    
    def __init__(
        self,
        cli_manager: ClaudeCodeCLIManager,
        default_timeout: int = 300,
        max_retries: int = 3,
        enable_response_parsing: bool = True
    ):
        """
        Initialize Claude Command Interface.
        
        Args:
            cli_manager: Claude CLI manager instance
            default_timeout: Default command timeout in seconds
            max_retries: Maximum number of retries for failed commands
            enable_response_parsing: Enable automatic response parsing
        """
        self.cli_manager = cli_manager
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.enable_response_parsing = enable_response_parsing
        
        # Command history and context
        self._command_history: Dict[str, List[Dict[str, Any]]] = {}  # process_id -> history
        self._conversation_context: Dict[str, Dict[str, Any]] = {}  # process_id -> context
        
        # Response patterns for parsing
        self._response_patterns = self._initialize_response_patterns()
        
        # Logging
        self.logger = MAOSLogger("claude_command_interface", "global")
    
    def _initialize_response_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize regex patterns for response parsing."""
        return {
            # JSON data extraction
            'json_block': re.compile(r'```json\s*\n(.*?)\n```', re.DOTALL | re.IGNORECASE),
            'json_inline': re.compile(r'\{[^{}]*\}'),
            
            # Code block extraction
            'code_block': re.compile(r'```(\w+)?\s*\n(.*?)\n```', re.DOTALL),
            'inline_code': re.compile(r'`([^`]+)`'),
            
            # File operations
            'file_created': re.compile(r'(?:created|wrote|generated):\s*(.+?)(?:\n|$)', re.IGNORECASE),
            'file_modified': re.compile(r'(?:modified|updated|edited):\s*(.+?)(?:\n|$)', re.IGNORECASE),
            'file_deleted': re.compile(r'(?:deleted|removed):\s*(.+?)(?:\n|$)', re.IGNORECASE),
            
            # Task status
            'task_completed': re.compile(r'(?:task|work|job)\s+(?:completed|finished|done)', re.IGNORECASE),
            'task_failed': re.compile(r'(?:task|work|job)\s+(?:failed|error|unsuccessful)', re.IGNORECASE),
            
            # Agent responses
            'agent_ready': re.compile(r'agent\s+(?:ready|initialized|available)', re.IGNORECASE),
            'agent_busy': re.compile(r'agent\s+(?:busy|working|executing)', re.IGNORECASE),
            
            # Error patterns
            'error_indicator': re.compile(r'(?:error|exception|failed|traceback):', re.IGNORECASE),
            'permission_denied': re.compile(r'permission\s+denied', re.IGNORECASE),
            'not_found': re.compile(r'(?:not\s+found|does\s+not\s+exist)', re.IGNORECASE),
        }
    
    async def execute_with_subagent(
        self,
        process_id: str,
        subagent_name: str,
        task_description: str
    ) -> CommandResult:
        """
        Execute a task using a specific Claude subagent.
        
        Args:
            process_id: Process ID of Claude instance
            subagent_name: Name of the subagent to use
            task_description: Description of the task to perform
            
        Returns:
            CommandResult with execution status
        """
        start_time = time.time()
        
        try:
            # Format command to use Claude's subagent system
            command = f"Use the {subagent_name} subagent to {task_description}"
            
            # Send command to Claude instance
            response = await self.cli_manager.send_command(
                process_id,
                command,
                wait_for_response=True,
                timeout=self.default_timeout
            )
            
            # Brief pause for command processing
            await asyncio.sleep(1)
            
            # Send agent YAML definition
            response = await self.cli_manager.send_command(
                process_id,
                agent_yaml,
                wait_for_response=True,
                timeout=self.default_timeout
            )
            
            execution_time = time.time() - start_time
            
            # Parse response
            result = CommandResult(
                command_type=ClaudeCommandType.AGENT_CREATE,
                success=self._is_agent_creation_successful(response),
                response=response,
                execution_time=execution_time,
                metadata={'agent_name': agent_name}
            )
            
            if self.enable_response_parsing:
                result.structured_data = self._parse_agent_creation_response(response)
            
            # Update command history
            self._add_to_history(process_id, {
                'command_type': 'agent_create',
                'agent_name': agent_name,
                'timestamp': datetime.utcnow().isoformat(),
                'success': result.success,
                'execution_time': execution_time
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return CommandResult(
                command_type=ClaudeCommandType.AGENT_CREATE,
                success=False,
                response="",
                execution_time=execution_time,
                error=str(e),
                metadata={'agent_name': agent_name}
            )
    
    async def execute_task(
        self,
        process_id: str,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> CommandResult:
        """
        Execute a task using Claude Code.
        
        Args:
            process_id: Process ID of Claude instance
            task_description: Description of the task to execute
            context: Optional context for the task
            
        Returns:
            CommandResult with execution results
        """
        start_time = time.time()
        
        try:
            # Prepare task command
            command = f"/task {task_description}"
            
            # Add context if provided
            if context:
                context_str = self._format_context_for_task(context)
                command += f"\n\nContext:\n{context_str}"
            
            # Execute task
            response = await self.cli_manager.send_command(
                process_id,
                command,
                wait_for_response=True,
                timeout=self.default_timeout
            )
            
            execution_time = time.time() - start_time
            
            # Parse response
            result = CommandResult(
                command_type=ClaudeCommandType.TASK_EXECUTE,
                success=self._is_task_execution_successful(response),
                response=response,
                execution_time=execution_time,
                metadata={'task_description': task_description}
            )
            
            if self.enable_response_parsing:
                result.structured_data = self._parse_task_execution_response(response)
            
            # Update command history
            self._add_to_history(process_id, {
                'command_type': 'task_execute',
                'task_description': task_description,
                'timestamp': datetime.utcnow().isoformat(),
                'success': result.success,
                'execution_time': execution_time
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return CommandResult(
                command_type=ClaudeCommandType.TASK_EXECUTE,
                success=False,
                response="",
                execution_time=execution_time,
                error=str(e),
                metadata={'task_description': task_description}
            )
    
    async def send_message(
        self,
        process_id: str,
        message: str,
        expect_structured_response: bool = False
    ) -> CommandResult:
        """
        Send a direct message to Claude.
        
        Args:
            process_id: Process ID of Claude instance
            message: Message to send
            expect_structured_response: Whether to expect structured data in response
            
        Returns:
            CommandResult with response
        """
        start_time = time.time()
        
        try:
            response = await self.cli_manager.send_command(
                process_id,
                message,
                wait_for_response=True,
                timeout=self.default_timeout
            )
            
            execution_time = time.time() - start_time
            
            result = CommandResult(
                command_type=ClaudeCommandType.DIRECT_MESSAGE,
                success=True,  # Direct messages are generally successful if they get a response
                response=response,
                execution_time=execution_time,
                metadata={'message_length': len(message)}
            )
            
            if self.enable_response_parsing and expect_structured_response:
                result.structured_data = self._parse_structured_response(response)
            
            # Update command history
            self._add_to_history(process_id, {
                'command_type': 'direct_message',
                'message_preview': message[:100],
                'timestamp': datetime.utcnow().isoformat(),
                'success': result.success,
                'execution_time': execution_time
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return CommandResult(
                command_type=ClaudeCommandType.DIRECT_MESSAGE,
                success=False,
                response="",
                execution_time=execution_time,
                error=str(e),
                metadata={'message_length': len(message)}
            )
    
    async def export_conversation(
        self,
        process_id: str,
        export_name: Optional[str] = None
    ) -> CommandResult:
        """
        Export the current conversation for preservation.
        Note: Claude Code doesn't have explicit save/load commands.
        This exports the conversation history for external storage.
        
        Args:
            process_id: Process ID of Claude instance
            export_name: Optional name for the export
            
        Returns:
            CommandResult with export status
        """
        start_time = time.time()
        
        try:
            # Use /export or similar available command
            # For now, we'll track the conversation state internally
            command = "/status"  # Get current status as a checkpoint
            
            response = await self.cli_manager.send_command(
                process_id,
                command,
                wait_for_response=True,
                timeout=30
            )
            
            execution_time = time.time() - start_time
            
            # Store conversation state internally
            conversation_state = {
                'export_name': export_name or f"checkpoint_{int(time.time())}",
                'timestamp': datetime.utcnow().isoformat(),
                'status_response': response,
                'command_history': self.get_command_history(process_id)
            }
            
            result = CommandResult(
                command_type=ClaudeCommandType.SAVE_CONTEXT,
                success=True,  # We successfully captured state
                response=response,
                execution_time=execution_time,
                metadata={'export_name': export_name},
                structured_data=conversation_state
            )
            
            # Update local context tracking
            self._update_context_tracking(process_id, export_name, 'exported')
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return CommandResult(
                command_type=ClaudeCommandType.SAVE_CONTEXT,
                success=False,
                response="",
                execution_time=execution_time,
                error=str(e),
                metadata={'export_name': export_name}
            )
    
    async def restore_conversation(
        self,
        process_id: str,
        conversation_state: Dict[str, Any]
    ) -> CommandResult:
        """
        Restore a conversation by replaying context.
        Since Claude Code doesn't have explicit load commands,
        we restore by providing the previous context.
        
        Args:
            process_id: Process ID of Claude instance
            conversation_state: Previously exported conversation state
            
        Returns:
            CommandResult with restoration status
        """
        start_time = time.time()
        
        try:
            # Restore by providing context about previous work
            context_message = f"""Previous work context:
- Export name: {conversation_state.get('export_name', 'unknown')}
- Timestamp: {conversation_state.get('timestamp', 'unknown')}
- Previous command count: {len(conversation_state.get('command_history', []))}

Please continue from where we left off."""
            
            response = await self.cli_manager.send_command(
                process_id,
                context_message,
                wait_for_response=True,
                timeout=30
            )
            
            execution_time = time.time() - start_time
            
            result = CommandResult(
                command_type=ClaudeCommandType.LOAD_CONTEXT,
                success=True,  # Context provided successfully
                response=response,
                execution_time=execution_time,
                metadata={'export_name': conversation_state.get('export_name')}
            )
            
            # Restore command history
            if 'command_history' in conversation_state:
                self._command_history[process_id] = conversation_state['command_history']
            
            # Update local context tracking
            self._update_context_tracking(process_id, conversation_state.get('export_name'), 'restored')
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return CommandResult(
                command_type=ClaudeCommandType.LOAD_CONTEXT,
                success=False,
                response="",
                execution_time=execution_time,
                error=str(e),
                metadata={'export_name': conversation_state.get('export_name')}
            )
    
    async def coordinate_agents(
        self,
        process_id: str,
        coordination_command: str,
        target_agents: List[str]
    ) -> CommandResult:
        """
        Send coordination commands between agents.
        
        Args:
            process_id: Process ID of Claude instance
            coordination_command: Command for coordination
            target_agents: List of target agent names
            
        Returns:
            CommandResult with coordination status
        """
        start_time = time.time()
        
        try:
            # Format coordination command
            agents_str = ", ".join(target_agents)
            command = f"@coordinate {agents_str}: {coordination_command}"
            
            response = await self.cli_manager.send_command(
                process_id,
                command,
                wait_for_response=True,
                timeout=self.default_timeout
            )
            
            execution_time = time.time() - start_time
            
            result = CommandResult(
                command_type=ClaudeCommandType.COORDINATION,
                success=self._is_coordination_successful(response),
                response=response,
                execution_time=execution_time,
                metadata={
                    'coordination_command': coordination_command,
                    'target_agents': target_agents
                }
            )
            
            if self.enable_response_parsing:
                result.structured_data = self._parse_coordination_response(response)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return CommandResult(
                command_type=ClaudeCommandType.COORDINATION,
                success=False,
                response="",
                execution_time=execution_time,
                error=str(e),
                metadata={
                    'coordination_command': coordination_command,
                    'target_agents': target_agents
                }
            )
    
    def get_command_history(self, process_id: str) -> List[Dict[str, Any]]:
        """Get command history for a process."""
        return self._command_history.get(process_id, [])
    
    def get_conversation_context(self, process_id: str) -> Dict[str, Any]:
        """Get conversation context for a process."""
        return self._conversation_context.get(process_id, {})
    
    def clear_history(self, process_id: str) -> None:
        """Clear command history for a process."""
        if process_id in self._command_history:
            del self._command_history[process_id]
        if process_id in self._conversation_context:
            del self._conversation_context[process_id]
    
    # Private helper methods
    
    def _add_to_history(self, process_id: str, command_info: Dict[str, Any]) -> None:
        """Add command to history."""
        if process_id not in self._command_history:
            self._command_history[process_id] = []
        
        self._command_history[process_id].append(command_info)
        
        # Keep last 100 commands
        if len(self._command_history[process_id]) > 100:
            self._command_history[process_id] = self._command_history[process_id][-100:]
    
    def _update_context_tracking(
        self,
        process_id: str,
        context_name: Optional[str],
        action: str
    ) -> None:
        """Update context tracking information."""
        if process_id not in self._conversation_context:
            self._conversation_context[process_id] = {}
        
        context = self._conversation_context[process_id]
        context['last_action'] = action
        context['last_action_time'] = datetime.utcnow().isoformat()
        
        if context_name:
            context['last_context_name'] = context_name
    
    def _format_context_for_task(self, context: Dict[str, Any]) -> str:
        """Format context dictionary for task execution."""
        context_lines = []
        
        for key, value in context.items():
            if isinstance(value, (dict, list)):
                context_lines.append(f"{key}: {json.dumps(value, indent=2)}")
            else:
                context_lines.append(f"{key}: {value}")
        
        return "\n".join(context_lines)
    
    # Response parsing methods
    
    def _is_agent_creation_successful(self, response: str) -> bool:
        """Check if agent creation was successful."""
        success_indicators = [
            'agent created', 'agent initialized', 'agent ready',
            'successfully created', 'agent definition saved'
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in success_indicators)
    
    def _is_task_execution_successful(self, response: str) -> bool:
        """Check if task execution was successful."""
        # Check for error indicators first
        if self._response_patterns['error_indicator'].search(response):
            return False
        
        # Check for success indicators
        if self._response_patterns['task_completed'].search(response):
            return True
        
        # If no clear indicators, assume success if response is substantial
        return len(response.strip()) > 50
    
    def _is_save_successful(self, response: str) -> bool:
        """Check if context save was successful."""
        success_indicators = ['saved', 'context saved', 'checkpoint created']
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in success_indicators)
    
    def _is_load_successful(self, response: str) -> bool:
        """Check if context load was successful."""
        success_indicators = ['loaded', 'context loaded', 'restored']
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in success_indicators)
    
    def _is_coordination_successful(self, response: str) -> bool:
        """Check if coordination command was successful."""
        success_indicators = ['coordinated', 'agents notified', 'message sent']
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in success_indicators)
    
    def _parse_agent_creation_response(self, response: str) -> Dict[str, Any]:
        """Parse agent creation response for structured data."""
        data = {
            'agent_status': 'unknown',
            'files_created': [],
            'errors': []
        }
        
        # Check agent status
        if self._response_patterns['agent_ready'].search(response):
            data['agent_status'] = 'ready'
        elif 'error' in response.lower():
            data['agent_status'] = 'error'
        
        # Extract created files
        file_matches = self._response_patterns['file_created'].findall(response)
        data['files_created'] = file_matches
        
        # Extract JSON data if present
        json_match = self._response_patterns['json_block'].search(response)
        if json_match:
            try:
                data['agent_config'] = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        return data
    
    def _parse_task_execution_response(self, response: str) -> Dict[str, Any]:
        """Parse task execution response for structured data."""
        data = {
            'status': 'unknown',
            'files_created': [],
            'files_modified': [],
            'code_blocks': [],
            'errors': []
        }
        
        # Determine status
        if self._response_patterns['task_completed'].search(response):
            data['status'] = 'completed'
        elif self._response_patterns['task_failed'].search(response):
            data['status'] = 'failed'
        elif self._response_patterns['error_indicator'].search(response):
            data['status'] = 'error'
        else:
            data['status'] = 'in_progress'
        
        # Extract file operations
        data['files_created'] = self._response_patterns['file_created'].findall(response)
        data['files_modified'] = self._response_patterns['file_modified'].findall(response)
        
        # Extract code blocks
        code_matches = self._response_patterns['code_block'].findall(response)
        data['code_blocks'] = [
            {'language': match[0] or 'text', 'code': match[1]}
            for match in code_matches
        ]
        
        # Extract errors
        if self._response_patterns['error_indicator'].search(response):
            data['errors'] = ['Error detected in response']
        
        return data
    
    def _parse_structured_response(self, response: str) -> Dict[str, Any]:
        """Parse response for any structured data."""
        data = {}
        
        # Extract JSON data
        json_match = self._response_patterns['json_block'].search(response)
        if json_match:
            try:
                data['json_data'] = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Extract code blocks
        code_matches = self._response_patterns['code_block'].findall(response)
        if code_matches:
            data['code_blocks'] = [
                {'language': match[0] or 'text', 'code': match[1]}
                for match in code_matches
            ]
        
        return data
    
    def _parse_save_response(self, response: str) -> Dict[str, Any]:
        """Parse context save response."""
        return {
            'save_successful': self._is_save_successful(response),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _parse_load_response(self, response: str) -> Dict[str, Any]:
        """Parse context load response."""
        return {
            'load_successful': self._is_load_successful(response),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _parse_coordination_response(self, response: str) -> Dict[str, Any]:
        """Parse coordination response."""
        return {
            'coordination_successful': self._is_coordination_successful(response),
            'timestamp': datetime.utcnow().isoformat()
        }