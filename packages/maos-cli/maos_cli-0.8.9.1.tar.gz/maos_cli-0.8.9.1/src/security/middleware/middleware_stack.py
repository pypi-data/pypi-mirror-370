"""Security middleware stack manager."""

import logging
from typing import List, Type, Any
from fastapi import FastAPI

from .auth_middleware import AuthenticationMiddleware, JWTAuthMiddleware
from .rate_limit_middleware import RateLimitMiddleware
from .security_headers import SecurityHeadersMiddleware
from .cors_middleware import CORSMiddleware

logger = logging.getLogger(__name__)


class SecurityMiddlewareStack:
    """Manage and configure security middleware stack."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.middlewares = []
    
    def add_cors(self, **kwargs) -> 'SecurityMiddlewareStack':
        """Add CORS middleware."""
        cors_middleware = CORSMiddleware(**kwargs)
        self.app.add_middleware(cors_middleware.get_fastapi_middleware().__class__)
        logger.info("Added CORS middleware")
        return self
    
    def add_security_headers(self, **kwargs) -> 'SecurityMiddlewareStack':
        """Add security headers middleware."""
        self.app.middleware("http")(SecurityHeadersMiddleware(**kwargs))
        logger.info("Added security headers middleware")
        return self
    
    def add_rate_limiting(self, **kwargs) -> 'SecurityMiddlewareStack':
        """Add rate limiting middleware."""
        rate_limit_middleware = RateLimitMiddleware(**kwargs)
        self.app.middleware("http")(rate_limit_middleware)
        logger.info("Added rate limiting middleware")
        return self
    
    def add_authentication(self, **kwargs) -> 'SecurityMiddlewareStack':
        """Add authentication middleware."""
        auth_middleware = AuthenticationMiddleware(**kwargs)
        self.app.middleware("http")(auth_middleware)
        logger.info("Added authentication middleware")
        return self
    
    def add_jwt_auth(self, **kwargs) -> 'SecurityMiddlewareStack':
        """Add JWT authentication middleware."""
        jwt_middleware = JWTAuthMiddleware(**kwargs)
        self.app.middleware("http")(jwt_middleware)
        logger.info("Added JWT authentication middleware")
        return self
    
    def configure_default_stack(
        self,
        jwt_manager=None,
        rbac_manager=None,
        **kwargs
    ) -> 'SecurityMiddlewareStack':
        """Configure default security middleware stack."""
        
        # Order matters - middlewares are executed in reverse order of addition
        
        # 1. CORS (outermost)
        self.add_cors(
            allow_origins=kwargs.get('cors_origins', ["http://localhost:3000"]),
            allow_credentials=True
        )
        
        # 2. Security headers
        self.add_security_headers()
        
        # 3. Rate limiting
        self.add_rate_limiting(
            redis_url=kwargs.get('redis_url', "redis://localhost:6379"),
            enable_ddos_protection=True
        )
        
        # 4. Authentication (innermost)
        if jwt_manager:
            self.add_jwt_auth(
                jwt_manager=jwt_manager,
                rbac_manager=rbac_manager
            )
        
        logger.info("Configured default security middleware stack")
        return self