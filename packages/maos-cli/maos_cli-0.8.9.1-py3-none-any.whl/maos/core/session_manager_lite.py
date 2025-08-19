"""
Lightweight Session Manager for message bus integration.

This version doesn't require database and is used specifically for message injection.
"""

import asyncio
from typing import Dict, Optional, Any
from pathlib import Path

from ..utils.logging_config import MAOSLogger


class SessionManager:
    """Lightweight session manager for message bus communication."""
    
    def __init__(self):
        """Initialize lightweight session manager."""
        self.logger = MAOSLogger("session_manager_lite")
        self._sessions: Dict[str, Dict[str, Any]] = {}
    
    async def send_to_session(
        self,
        process_id: str,
        message: str
    ) -> bool:
        """
        Send a message to a Claude session.
        
        This is a stub that would integrate with actual Claude sessions.
        In production, this would inject messages into running Claude contexts.
        
        Args:
            process_id: Process/session identifier
            message: Message to send
            
        Returns:
            True if sent successfully
        """
        # Log the message that would be sent
        self.logger.logger.debug(
            f"Would inject to session {process_id}: {message[:100]}"
        )
        
        # Track in memory
        if process_id not in self._sessions:
            self._sessions[process_id] = {
                "messages": [],
                "created_at": asyncio.get_event_loop().time()
            }
        
        self._sessions[process_id]["messages"].append({
            "content": message,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # In production, this would actually inject into Claude's context
        # For now, we simulate success
        return True
    
    def get_session_messages(self, process_id: str) -> list:
        """
        Get messages for a session.
        
        Args:
            process_id: Process/session identifier
            
        Returns:
            List of messages
        """
        if process_id in self._sessions:
            return self._sessions[process_id]["messages"]
        return []
    
    def clear_session(self, process_id: str):
        """
        Clear a session's messages.
        
        Args:
            process_id: Process/session identifier
        """
        if process_id in self._sessions:
            del self._sessions[process_id]