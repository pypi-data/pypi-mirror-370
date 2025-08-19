"""Authentication middleware for MAOS security."""

import logging
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union
import json
from dataclasses import dataclass

from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..auth.jwt_manager import JWTManager, TokenType, TokenClaims
from ..rbac.rbac_manager import RBACManager
from ..rbac.permissions import PermissionType

logger = logging.getLogger(__name__)


@dataclass
class AuthContext:
    """Authentication context for requests."""
    authenticated: bool = False
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    token_claims: Optional[TokenClaims] = None
    roles: List[str] = None
    permissions: List[str] = None
    session_id: Optional[str] = None
    auth_method: Optional[str] = None
    
    def __post_init__(self):
        if self.roles is None:
            self.roles = []
        if self.permissions is None:
            self.permissions = []


class AuthenticationMiddleware:
    """Base authentication middleware."""
    
    def __init__(
        self,
        jwt_manager: JWTManager,
        rbac_manager: Optional[RBACManager] = None,
        excluded_paths: Optional[List[str]] = None,
        require_authentication: bool = True
    ):
        self.jwt_manager = jwt_manager
        self.rbac_manager = rbac_manager
        self.excluded_paths = excluded_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        self.require_authentication = require_authentication
        
        # Metrics
        self.metrics = {
            "requests_total": 0,
            "authenticated_requests": 0,
            "failed_authentications": 0,
            "unauthorized_requests": 0,
            "forbidden_requests": 0
        }
    
    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process authentication for incoming requests."""
        try:
            self.metrics["requests_total"] += 1
            
            # Check if path is excluded
            if self._is_path_excluded(request.url.path):
                return await call_next(request)
            
            # Extract authentication info
            auth_context = await self._authenticate_request(request)
            
            # Store auth context in request state
            request.state.auth_context = auth_context
            
            # Check if authentication is required
            if self.require_authentication and not auth_context.authenticated:
                self.metrics["unauthorized_requests"] += 1
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            if auth_context.authenticated:
                self.metrics["authenticated_requests"] += 1
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            self._add_security_headers(response, auth_context)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication middleware error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication system error"
            )
    
    def _is_path_excluded(self, path: str) -> bool:
        """Check if path is excluded from authentication."""
        for excluded_path in self.excluded_paths:
            if path.startswith(excluded_path):
                return True
        return False
    
    async def _authenticate_request(self, request: Request) -> AuthContext:
        """Authenticate incoming request."""
        auth_context = AuthContext()
        
        try:
            # Try different authentication methods
            
            # 1. JWT Bearer token
            jwt_context = await self._authenticate_jwt(request)
            if jwt_context.authenticated:
                return jwt_context
            
            # 2. API Key authentication
            api_key_context = await self._authenticate_api_key(request)
            if api_key_context.authenticated:
                return api_key_context
            
            # 3. Session authentication
            session_context = await self._authenticate_session(request)
            if session_context.authenticated:
                return session_context
            
            return auth_context
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            self.metrics["failed_authentications"] += 1
            return auth_context
    
    async def _authenticate_jwt(self, request: Request) -> AuthContext:
        """Authenticate using JWT token."""
        auth_context = AuthContext(auth_method="jwt")
        
        try:
            # Extract Bearer token
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return auth_context
            
            token = authorization.split(" ")[1]
            
            # Verify JWT token
            try:
                claims = self.jwt_manager.verify_token(token, TokenType.ACCESS)
                
                auth_context.authenticated = True
                auth_context.user_id = claims.sub
                auth_context.agent_id = claims.agent_id
                auth_context.token_claims = claims
                auth_context.session_id = claims.session_id
                auth_context.roles = claims.roles or []
                auth_context.permissions = claims.permissions or []
                
                # Get user permissions from RBAC if available
                if self.rbac_manager and auth_context.user_id:
                    user_permissions = await self.rbac_manager.get_user_permissions(auth_context.user_id)
                    auth_context.permissions.extend(user_permissions.get("permissions_by_type", {}).keys())
                
                return auth_context
                
            except Exception as e:
                logger.warning(f"JWT verification failed: {e}")
                return auth_context
                
        except Exception as e:
            logger.error(f"JWT authentication error: {e}")
            return auth_context
    
    async def _authenticate_api_key(self, request: Request) -> AuthContext:
        """Authenticate using API key."""
        auth_context = AuthContext(auth_method="api_key")
        
        try:
            # Extract API key from header or query parameter
            api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
            if not api_key:
                return auth_context
            
            # Validate API key (this would need API key manager)
            # For now, we'll just check if it exists
            if api_key.startswith("maos_key_"):
                auth_context.authenticated = True
                auth_context.user_id = "api_key_user"
                auth_context.roles = ["api_user"]
            
            return auth_context
            
        except Exception as e:
            logger.error(f"API key authentication error: {e}")
            return auth_context
    
    async def _authenticate_session(self, request: Request) -> AuthContext:
        """Authenticate using session."""
        auth_context = AuthContext(auth_method="session")
        
        try:
            # Extract session ID from cookie
            session_id = request.cookies.get("session_id")
            if not session_id:
                return auth_context
            
            # Validate session (this would need session manager)
            # For now, we'll just check basic format
            if len(session_id) >= 32:
                auth_context.authenticated = True
                auth_context.session_id = session_id
                auth_context.user_id = "session_user"
                auth_context.roles = ["session_user"]
            
            return auth_context
            
        except Exception as e:
            logger.error(f"Session authentication error: {e}")
            return auth_context
    
    def _add_security_headers(self, response: Response, auth_context: AuthContext):
        """Add security headers to response."""
        if auth_context.authenticated:
            response.headers["X-Authenticated"] = "true"
            response.headers["X-User-ID"] = auth_context.user_id or ""
            response.headers["X-Auth-Method"] = auth_context.auth_method or ""
        else:
            response.headers["X-Authenticated"] = "false"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get authentication metrics."""
        return self.metrics.copy()


class JWTAuthMiddleware:
    """JWT-specific authentication middleware with advanced features."""
    
    def __init__(
        self,
        jwt_manager: JWTManager,
        rbac_manager: Optional[RBACManager] = None,
        token_refresh_threshold: int = 300,  # Refresh if expires in 5 minutes
        require_fresh_token: bool = False,  # Require recently issued tokens
        fresh_token_max_age: int = 3600,  # 1 hour
        blacklist_check: bool = True
    ):
        self.jwt_manager = jwt_manager
        self.rbac_manager = rbac_manager
        self.token_refresh_threshold = token_refresh_threshold
        self.require_fresh_token = require_fresh_token
        self.fresh_token_max_age = fresh_token_max_age
        self.blacklist_check = blacklist_check
        
        # Security bearer scheme
        self.security_scheme = HTTPBearer(auto_error=False)
        
        # Metrics
        self.metrics = {
            "tokens_validated": 0,
            "tokens_refreshed": 0,
            "expired_tokens": 0,
            "invalid_tokens": 0,
            "blacklisted_tokens": 0,
            "fresh_token_violations": 0
        }
    
    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process JWT authentication."""
        try:
            # Extract credentials
            credentials = await self.security_scheme(request)
            auth_context = AuthContext()
            
            if credentials:
                auth_context = await self._validate_jwt_token(credentials.credentials, request)
            
            # Store auth context
            request.state.auth_context = auth_context
            
            # Process request
            response = await call_next(request)
            
            # Add token refresh header if needed
            await self._add_refresh_headers(response, auth_context)
            
            return response
            
        except Exception as e:
            logger.error(f"JWT middleware error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="JWT authentication error"
            )
    
    async def _validate_jwt_token(self, token: str, request: Request) -> AuthContext:
        """Validate JWT token with comprehensive checks."""
        auth_context = AuthContext(auth_method="jwt")
        
        try:
            self.metrics["tokens_validated"] += 1
            
            # Check if token is blacklisted
            if self.blacklist_check and self.jwt_manager.is_token_revoked(token):
                self.metrics["blacklisted_tokens"] += 1
                logger.warning(f"Blacklisted token used from IP: {request.client.host}")
                return auth_context
            
            # Verify token
            claims = self.jwt_manager.verify_token(token, TokenType.ACCESS)
            
            # Check if token is fresh enough
            if self.require_fresh_token:
                token_age = datetime.now(timezone.utc).timestamp() - claims.iat
                if token_age > self.fresh_token_max_age:
                    self.metrics["fresh_token_violations"] += 1
                    logger.warning(f"Stale token used: age={token_age}s")
                    return auth_context
            
            # Token is valid
            auth_context.authenticated = True
            auth_context.user_id = claims.sub
            auth_context.agent_id = claims.agent_id
            auth_context.token_claims = claims
            auth_context.session_id = claims.session_id
            auth_context.roles = claims.roles or []
            auth_context.permissions = claims.permissions or []
            
            # Enhanced authorization with RBAC
            if self.rbac_manager and auth_context.user_id:
                try:
                    # Check user permissions
                    user_roles = await self.rbac_manager.role_manager.get_user_roles(auth_context.user_id)
                    auth_context.roles.extend([role.name for role in user_roles])
                    
                    # Get comprehensive permissions
                    user_permissions = await self.rbac_manager.get_user_permissions(auth_context.user_id)
                    for perm_type, perms in user_permissions.get("permissions_by_type", {}).items():
                        auth_context.permissions.extend([f"{perm_type}:{p['name']}" for p in perms])
                    
                except Exception as e:
                    logger.error(f"RBAC lookup error: {e}")
            
            return auth_context
            
        except Exception as e:
            if "expired" in str(e).lower():
                self.metrics["expired_tokens"] += 1
            else:
                self.metrics["invalid_tokens"] += 1
            
            logger.debug(f"Token validation failed: {e}")
            return auth_context
    
    async def _add_refresh_headers(self, response: Response, auth_context: AuthContext):
        """Add token refresh headers if needed."""
        try:
            if not auth_context.authenticated or not auth_context.token_claims:
                return
            
            # Check if token is close to expiration
            current_time = datetime.now(timezone.utc).timestamp()
            time_to_expiry = auth_context.token_claims.exp - current_time
            
            if time_to_expiry <= self.token_refresh_threshold:
                response.headers["X-Token-Refresh-Required"] = "true"
                response.headers["X-Token-Expires-In"] = str(int(time_to_expiry))
                self.metrics["tokens_refreshed"] += 1
            
        except Exception as e:
            logger.error(f"Error adding refresh headers: {e}")
    
    async def require_permission(
        self,
        request: Request,
        required_permission: PermissionType,
        resource: str = "*"
    ) -> bool:
        """Check if authenticated user has required permission."""
        try:
            auth_context = getattr(request.state, "auth_context", AuthContext())
            
            if not auth_context.authenticated:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check permissions using RBAC
            if self.rbac_manager and auth_context.user_id:
                decision = await self.rbac_manager.check_access(
                    user_id=auth_context.user_id,
                    action=required_permission,
                    resource=resource,
                    context={"ip_address": request.client.host}
                )
                
                if not decision.allowed:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions: {decision.reason}"
                    )
                
                return True
            
            # Fallback: check token permissions
            permission_str = required_permission.value
            if permission_str in auth_context.permissions:
                return True
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Permission check error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Permission check failed"
            )
    
    async def require_role(self, request: Request, required_role: str) -> bool:
        """Check if authenticated user has required role."""
        try:
            auth_context = getattr(request.state, "auth_context", AuthContext())
            
            if not auth_context.authenticated:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if required_role in auth_context.roles:
                return True
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role missing: {required_role}"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Role check error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Role check failed"
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get JWT middleware metrics."""
        return self.metrics.copy()


# FastAPI dependency for extracting auth context
def get_auth_context(request: Request) -> AuthContext:
    """FastAPI dependency to get authentication context."""
    return getattr(request.state, "auth_context", AuthContext())


# FastAPI dependency for requiring authentication
def require_auth(request: Request) -> AuthContext:
    """FastAPI dependency to require authentication."""
    auth_context = get_auth_context(request)
    if not auth_context.authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return auth_context