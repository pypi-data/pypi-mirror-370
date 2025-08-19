"""Security headers middleware."""

import logging
from typing import Any, Awaitable, Callable, Dict
from fastapi import Request, Response

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware:
    """Add comprehensive security headers to responses."""
    
    def __init__(
        self,
        force_https: bool = True,
        hsts_max_age: int = 31536000,  # 1 year
        content_type_options: bool = True,
        frame_options: str = "DENY",
        xss_protection: bool = True,
        referrer_policy: str = "strict-origin-when-cross-origin",
        csp_policy: str = "default-src 'self'",
        permissions_policy: str = "geolocation=(), microphone=(), camera=()"
    ):
        self.force_https = force_https
        self.hsts_max_age = hsts_max_age
        self.content_type_options = content_type_options
        self.frame_options = frame_options
        self.xss_protection = xss_protection
        self.referrer_policy = referrer_policy
        self.csp_policy = csp_policy
        self.permissions_policy = permissions_policy
    
    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        # HTTPS enforcement
        if self.force_https:
            response.headers["Strict-Transport-Security"] = f"max-age={self.hsts_max_age}; includeSubDomains"
        
        # Content type options
        if self.content_type_options:
            response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Frame options
        if self.frame_options:
            response.headers["X-Frame-Options"] = self.frame_options
        
        # XSS protection
        if self.xss_protection:
            response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer policy
        if self.referrer_policy:
            response.headers["Referrer-Policy"] = self.referrer_policy
        
        # Content Security Policy
        if self.csp_policy:
            response.headers["Content-Security-Policy"] = self.csp_policy
        
        # Permissions policy
        if self.permissions_policy:
            response.headers["Permissions-Policy"] = self.permissions_policy
        
        # Additional security headers
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        
        return response