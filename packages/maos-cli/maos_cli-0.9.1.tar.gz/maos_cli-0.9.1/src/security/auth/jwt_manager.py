"""JWT token management with enterprise security features."""

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

logger = logging.getLogger(__name__)


class TokenType(Enum):
    """JWT token types."""
    ACCESS = "access"
    REFRESH = "refresh"
    ID = "id"
    SERVICE = "service"


class JWTAlgorithm(Enum):
    """Supported JWT algorithms."""
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"
    ES256 = "ES256"
    ES384 = "ES384"
    ES512 = "ES512"


@dataclass
class TokenPair:
    """JWT access and refresh token pair."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600  # seconds
    scope: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TokenClaims:
    """Standard JWT claims."""
    sub: str  # Subject (user ID)
    iat: int  # Issued at
    exp: int  # Expiration
    iss: str  # Issuer
    aud: Union[str, List[str]]  # Audience
    jti: str  # JWT ID
    token_type: str  # Token type (access, refresh, etc.)
    scope: Optional[str] = None  # Permissions/scope
    agent_id: Optional[str] = None  # MAOS agent ID
    session_id: Optional[str] = None  # Session identifier
    roles: Optional[List[str]] = None  # User roles
    permissions: Optional[List[str]] = None  # Specific permissions
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata


class JWTError(Exception):
    """JWT-related errors."""
    pass


class TokenExpiredError(JWTError):
    """Token has expired."""
    pass


class TokenInvalidError(JWTError):
    """Token is invalid."""
    pass


class JWTManager:
    """Enterprise-grade JWT token management."""
    
    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: JWTAlgorithm = JWTAlgorithm.HS256,
        issuer: str = "maos",
        audience: Union[str, List[str]] = "maos-agents",
        access_token_expire_minutes: int = 60,
        refresh_token_expire_days: int = 30,
        private_key_path: Optional[str] = None,
        public_key_path: Optional[str] = None
    ):
        self.algorithm = algorithm
        self.issuer = issuer
        self.audience = audience if isinstance(audience, list) else [audience]
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        
        # Key management
        self.secret_key = secret_key or os.urandom(32).hex()
        self.private_key = None
        self.public_key = None
        
        # Load RSA keys if specified
        if private_key_path and public_key_path:
            self._load_rsa_keys(private_key_path, public_key_path)
        elif algorithm.value.startswith('RS') or algorithm.value.startswith('ES'):
            self._generate_rsa_keys()
        
        # Token blacklist for logout/revocation
        self.blacklisted_tokens: set = set()
        
        # Token usage tracking
        self.token_usage = {}
        
        logger.info(f"JWT manager initialized with algorithm: {algorithm.value}")
    
    def _load_rsa_keys(self, private_key_path: str, public_key_path: str):
        """Load RSA keys from files."""
        try:
            with open(private_key_path, 'rb') as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None
                )
            
            with open(public_key_path, 'rb') as f:
                self.public_key = serialization.load_pem_public_key(f.read())
                
            logger.info("RSA keys loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load RSA keys: {e}")
            raise JWTError(f"Key loading failed: {e}")
    
    def _generate_rsa_keys(self):
        """Generate RSA key pair for RS algorithms."""
        try:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self.public_key = self.private_key.public_key()
            
            logger.info("RSA keys generated successfully")
            
        except Exception as e:
            logger.error(f"Failed to generate RSA keys: {e}")
            raise JWTError(f"Key generation failed: {e}")
    
    def _get_signing_key(self) -> Union[str, Any]:
        """Get signing key for token creation."""
        if self.algorithm.value.startswith('HS'):
            return self.secret_key
        elif self.algorithm.value.startswith('RS'):
            if not self.private_key:
                raise JWTError("Private key required for RSA algorithms")
            return self.private_key
        else:
            raise JWTError(f"Unsupported algorithm: {self.algorithm.value}")
    
    def _get_verification_key(self) -> Union[str, Any]:
        """Get verification key for token validation."""
        if self.algorithm.value.startswith('HS'):
            return self.secret_key
        elif self.algorithm.value.startswith('RS'):
            if not self.public_key:
                raise JWTError("Public key required for RSA algorithms")
            return self.public_key
        else:
            raise JWTError(f"Unsupported algorithm: {self.algorithm.value}")
    
    def create_access_token(
        self,
        subject: str,
        scopes: Optional[List[str]] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        roles: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        try:
            now = datetime.now(timezone.utc)
            expire = now + (expires_delta or timedelta(minutes=self.access_token_expire_minutes))
            
            # Generate unique token ID
            jti = os.urandom(16).hex()
            
            # Build claims
            claims = {
                "sub": subject,
                "iat": int(now.timestamp()),
                "exp": int(expire.timestamp()),
                "iss": self.issuer,
                "aud": self.audience,
                "jti": jti,
                "token_type": TokenType.ACCESS.value,
                "scope": " ".join(scopes) if scopes else None,
                "agent_id": agent_id,
                "session_id": session_id,
                "roles": roles,
                "permissions": permissions,
                "metadata": metadata
            }
            
            # Remove None values
            claims = {k: v for k, v in claims.items() if v is not None}
            
            # Create token
            token = jwt.encode(
                claims,
                self._get_signing_key(),
                algorithm=self.algorithm.value
            )
            
            # Track token usage
            self.token_usage[jti] = {
                "created_at": now,
                "subject": subject,
                "agent_id": agent_id,
                "usage_count": 0
            }
            
            logger.debug(f"Access token created for subject: {subject}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise JWTError(f"Token creation failed: {e}")
    
    def create_refresh_token(
        self,
        subject: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT refresh token."""
        try:
            now = datetime.now(timezone.utc)
            expire = now + (expires_delta or timedelta(days=self.refresh_token_expire_days))
            
            # Generate unique token ID
            jti = os.urandom(16).hex()
            
            # Build claims
            claims = {
                "sub": subject,
                "iat": int(now.timestamp()),
                "exp": int(expire.timestamp()),
                "iss": self.issuer,
                "aud": self.audience,
                "jti": jti,
                "token_type": TokenType.REFRESH.value,
                "session_id": session_id,
                "metadata": metadata
            }
            
            # Remove None values
            claims = {k: v for k, v in claims.items() if v is not None}
            
            # Create token
            token = jwt.encode(
                claims,
                self._get_signing_key(),
                algorithm=self.algorithm.value
            )
            
            # Track token usage
            self.token_usage[jti] = {
                "created_at": now,
                "subject": subject,
                "token_type": "refresh",
                "usage_count": 0
            }
            
            logger.debug(f"Refresh token created for subject: {subject}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to create refresh token: {e}")
            raise JWTError(f"Refresh token creation failed: {e}")
    
    def create_token_pair(
        self,
        subject: str,
        scopes: Optional[List[str]] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        roles: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TokenPair:
        """Create access and refresh token pair."""
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = os.urandom(16).hex()
            
            # Create tokens
            access_token = self.create_access_token(
                subject=subject,
                scopes=scopes,
                agent_id=agent_id,
                session_id=session_id,
                roles=roles,
                permissions=permissions,
                metadata=metadata
            )
            
            refresh_token = self.create_refresh_token(
                subject=subject,
                session_id=session_id,
                metadata=metadata
            )
            
            return TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=self.access_token_expire_minutes * 60,
                scope=" ".join(scopes) if scopes else None
            )
            
        except Exception as e:
            logger.error(f"Failed to create token pair: {e}")
            raise JWTError(f"Token pair creation failed: {e}")
    
    def verify_token(
        self,
        token: str,
        expected_type: Optional[TokenType] = None,
        verify_signature: bool = True,
        verify_expiration: bool = True,
        verify_audience: bool = True,
        verify_issuer: bool = True
    ) -> TokenClaims:
        """Verify and decode JWT token."""
        try:
            # Check if token is blacklisted
            if token in self.blacklisted_tokens:
                raise TokenInvalidError("Token has been revoked")
            
            # Decode token
            options = {
                "verify_signature": verify_signature,
                "verify_exp": verify_expiration,
                "verify_aud": verify_audience,
                "verify_iss": verify_issuer,
                "require_exp": True,
                "require_iat": True,
                "require_jti": True
            }
            
            claims = jwt.decode(
                token,
                self._get_verification_key(),
                algorithms=[self.algorithm.value],
                issuer=self.issuer if verify_issuer else None,
                audience=self.audience if verify_audience else None,
                options=options
            )
            
            # Verify token type if specified
            if expected_type and claims.get("token_type") != expected_type.value:
                raise TokenInvalidError(f"Expected {expected_type.value} token")
            
            # Update token usage
            jti = claims.get("jti")
            if jti in self.token_usage:
                self.token_usage[jti]["usage_count"] += 1
                self.token_usage[jti]["last_used"] = datetime.now(timezone.utc)
            
            # Convert to TokenClaims object
            return TokenClaims(
                sub=claims["sub"],
                iat=claims["iat"],
                exp=claims["exp"],
                iss=claims["iss"],
                aud=claims["aud"],
                jti=claims["jti"],
                token_type=claims.get("token_type", TokenType.ACCESS.value),
                scope=claims.get("scope"),
                agent_id=claims.get("agent_id"),
                session_id=claims.get("session_id"),
                roles=claims.get("roles"),
                permissions=claims.get("permissions"),
                metadata=claims.get("metadata")
            )
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise TokenExpiredError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            raise TokenInvalidError(f"Invalid token: {e}")
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise JWTError(f"Token verification failed: {e}")
    
    def refresh_access_token(
        self,
        refresh_token: str,
        scopes: Optional[List[str]] = None,
        agent_id: Optional[str] = None,
        roles: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None
    ) -> str:
        """Create new access token using refresh token."""
        try:
            # Verify refresh token
            claims = self.verify_token(refresh_token, TokenType.REFRESH)
            
            # Create new access token
            return self.create_access_token(
                subject=claims.sub,
                scopes=scopes,
                agent_id=agent_id or claims.agent_id,
                session_id=claims.session_id,
                roles=roles or claims.roles,
                permissions=permissions or claims.permissions,
                metadata=claims.metadata
            )
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise JWTError(f"Token refresh failed: {e}")
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a token by adding to blacklist."""
        try:
            # Verify token to get claims
            claims = self.verify_token(token, verify_expiration=False)
            
            # Add to blacklist
            self.blacklisted_tokens.add(token)
            
            # Remove from usage tracking
            jti = claims.jti
            if jti in self.token_usage:
                self.token_usage[jti]["revoked_at"] = datetime.now(timezone.utc)
            
            logger.info(f"Token revoked for subject: {claims.sub}")
            return True
            
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False
    
    def revoke_all_user_tokens(self, subject: str) -> int:
        """Revoke all tokens for a specific user."""
        try:
            revoked_count = 0
            
            # Find all tokens for the subject
            for jti, usage_info in self.token_usage.items():
                if usage_info.get("subject") == subject and "revoked_at" not in usage_info:
                    # Mark as revoked
                    usage_info["revoked_at"] = datetime.now(timezone.utc)
                    revoked_count += 1
            
            logger.info(f"Revoked {revoked_count} tokens for subject: {subject}")
            return revoked_count
            
        except Exception as e:
            logger.error(f"Failed to revoke user tokens: {e}")
            return 0
    
    def is_token_revoked(self, token: str) -> bool:
        """Check if token is revoked."""
        try:
            if token in self.blacklisted_tokens:
                return True
            
            # Check usage tracking
            claims = self.verify_token(token, verify_expiration=False)
            jti = claims.jti
            
            if jti in self.token_usage:
                return "revoked_at" in self.token_usage[jti]
            
            return False
            
        except Exception:
            return True  # Consider invalid tokens as revoked
    
    def cleanup_expired_tokens(self) -> int:
        """Clean up expired token tracking data."""
        try:
            now = datetime.now(timezone.utc)
            cleaned_count = 0
            
            # Find expired tokens
            expired_jtis = []
            for jti, usage_info in self.token_usage.items():
                created_at = usage_info.get("created_at")
                if created_at:
                    # Consider tokens expired if they're older than max refresh token age
                    max_age = timedelta(days=self.refresh_token_expire_days + 1)
                    if now - created_at > max_age:
                        expired_jtis.append(jti)
            
            # Remove expired tokens
            for jti in expired_jtis:
                del self.token_usage[jti]
                cleaned_count += 1
            
            logger.debug(f"Cleaned up {cleaned_count} expired token records")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Token cleanup failed: {e}")
            return 0
    
    def get_token_info(self, token: str) -> Dict[str, Any]:
        """Get information about a token without full verification."""
        try:
            # Decode without verification to get claims
            claims = jwt.decode(token, options={"verify_signature": False})
            
            # Get usage information
            jti = claims.get("jti")
            usage_info = self.token_usage.get(jti, {})
            
            return {
                "subject": claims.get("sub"),
                "token_type": claims.get("token_type"),
                "issued_at": datetime.fromtimestamp(claims.get("iat", 0), timezone.utc).isoformat(),
                "expires_at": datetime.fromtimestamp(claims.get("exp", 0), timezone.utc).isoformat(),
                "agent_id": claims.get("agent_id"),
                "session_id": claims.get("session_id"),
                "roles": claims.get("roles"),
                "permissions": claims.get("permissions"),
                "is_revoked": self.is_token_revoked(token),
                "usage_count": usage_info.get("usage_count", 0),
                "last_used": usage_info.get("last_used", {}).isoformat() if usage_info.get("last_used") else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get token info: {e}")
            return {"error": str(e)}
    
    def get_active_tokens_count(self) -> Dict[str, int]:
        """Get count of active tokens by type."""
        try:
            now = datetime.now(timezone.utc)
            counts = {"access": 0, "refresh": 0, "total": 0}
            
            for jti, usage_info in self.token_usage.items():
                if "revoked_at" not in usage_info:
                    token_type = usage_info.get("token_type", "access")
                    counts[token_type] = counts.get(token_type, 0) + 1
                    counts["total"] += 1
            
            return counts
            
        except Exception as e:
            logger.error(f"Failed to get token counts: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Perform JWT manager health check."""
        try:
            # Test token creation and verification
            test_subject = "health_check_test"
            test_token = self.create_access_token(test_subject)
            self.verify_token(test_token)
            self.revoke_token(test_token)
            
            return {
                "status": "healthy",
                "algorithm": self.algorithm.value,
                "issuer": self.issuer,
                "active_tokens": self.get_active_tokens_count(),
                "blacklisted_count": len(self.blacklisted_tokens)
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}