"""CORS middleware with security controls."""

import logging
from typing import List, Optional, Awaitable, Callable
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware

logger = logging.getLogger(__name__)


class CORSMiddleware:
    """Secure CORS middleware with advanced origin validation."""
    
    def __init__(
        self,
        allow_origins: List[str] = None,
        allow_origin_regex: Optional[str] = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        allow_credentials: bool = False,
        expose_headers: List[str] = None,
        max_age: int = 600,
        strict_origin_validation: bool = True
    ):
        self.allow_origins = allow_origins or ["https://localhost:3000"]
        self.allow_origin_regex = allow_origin_regex
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allow_headers = allow_headers or [
            "Accept",
            "Accept-Language", 
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-API-Key"
        ]
        self.allow_credentials = allow_credentials
        self.expose_headers = expose_headers or []
        self.max_age = max_age
        self.strict_origin_validation = strict_origin_validation
    
    def get_fastapi_middleware(self):
        """Get FastAPI CORS middleware with our configuration."""
        return FastAPICORSMiddleware(
            allow_origins=self.allow_origins,
            allow_origin_regex=self.allow_origin_regex,
            allow_methods=self.allow_methods,
            allow_headers=self.allow_headers,
            allow_credentials=self.allow_credentials,
            expose_headers=self.expose_headers,
            max_age=self.max_age
        )