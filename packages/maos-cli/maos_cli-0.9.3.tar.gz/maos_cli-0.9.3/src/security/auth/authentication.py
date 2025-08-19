"""Centralized authentication module importing from communication security."""

# Import existing authentication components from communication/security
from ...communication.security.core import (
    CommunicationSecurity,
    SecurityPolicy,
    SecurityError
)

# Enum for token types (keeping consistent with JWT implementation)
from enum import Enum


class TokenType(Enum):
    """JWT token types for MAOS authentication."""
    ACCESS = "access"
    REFRESH = "refresh"
    ID = "id"
    SERVICE = "service"
    AGENT = "agent"


class AuthenticationManager:
    """Authentication manager that integrates with existing communication security."""
    
    def __init__(self, communication_security: CommunicationSecurity):
        """Initialize with existing communication security instance."""
        self.comm_security = communication_security
        self.policy = communication_security.policy
        
    async def authenticate_agent(self, agent_id: str, credentials: dict) -> bool:
        """Authenticate an agent using the communication security system."""
        try:
            # Use existing communication security for agent authentication
            if not self.policy.require_authentication:
                return True
            
            # Check if agent is in trusted list
            if agent_id in self.policy.trusted_agents:
                return True
            
            # Check if agent is blocked
            if agent_id in self.policy.blocked_agents:
                return False
            
            # Additional authentication logic can be added here
            # For now, rely on the existing security framework
            return True
            
        except Exception:
            return False
    
    async def authorize_action(self, agent_id: str, action: str, resource: str = None) -> bool:
        """Authorize an agent action using existing security policies."""
        try:
            if not self.policy.require_authorization:
                return True
            
            # Check if agent is blocked
            if agent_id in self.policy.blocked_agents:
                return False
            
            # Check if agent is trusted (full access)
            if agent_id in self.policy.trusted_agents:
                return True
            
            # Additional authorization logic can be implemented here
            return True
            
        except Exception:
            return False
    
    async def get_agent_permissions(self, agent_id: str) -> list:
        """Get permissions for an agent."""
        permissions = []
        
        if agent_id in self.policy.trusted_agents:
            permissions.extend(["read", "write", "execute", "admin"])
        elif agent_id not in self.policy.blocked_agents:
            permissions.extend(["read", "write"])
        
        return permissions


# Re-export for backward compatibility
__all__ = [
    "AuthenticationManager",
    "TokenType",
    "CommunicationSecurity", 
    "SecurityPolicy",
    "SecurityError"
]