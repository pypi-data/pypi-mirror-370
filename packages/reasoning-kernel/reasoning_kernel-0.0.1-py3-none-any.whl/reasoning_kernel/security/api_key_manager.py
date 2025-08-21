"""
API Key Management System for MSA Reasoning Kernel

Provides comprehensive API key management:
- API key generation and validation
- Role-based access control
- Rate limit assignment
- Usage tracking and analytics
- Key rotation and expiration
"""

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timedelta
from enum import Enum
import hashlib
import json
import secrets
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi.security import HTTPBearer
from reasoning_kernel.core.logging_config import get_logger
from reasoning_kernel.middleware.rate_limiting import RateLimitRule
import redis.asyncio as redis
from redis.exceptions import RedisError


logger = get_logger(__name__)


class APIKeyStatus(Enum):
    """API key status states"""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


class UserRole(Enum):
    """User roles for access control"""

    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"
    SERVICE = "service"


@dataclass
class APIKeyPermissions:
    """Permissions associated with an API key"""

    # Endpoint access
    can_access_reasoning: bool = True
    can_access_msa: bool = True
    can_access_admin: bool = False
    can_access_health: bool = True

    # Operations
    can_read: bool = True
    can_write: bool = True
    can_delete: bool = False

    # Resources
    max_concurrent_requests: int = 10
    allowed_models: Set[str] = field(default_factory=lambda: {"default"})
    allowed_endpoints: Set[str] = field(default_factory=set)  # Empty means all allowed

    # Rate limiting
    custom_rate_limits: Optional[RateLimitRule] = None


@dataclass
class APIKeyMetadata:
    """API key metadata and configuration"""

    # Identification
    key_id: str
    key_hash: str  # Hashed version for storage
    name: str
    description: str = ""

    # User information
    user_id: Optional[str] = None
    user_role: UserRole = UserRole.USER

    # Status and timing
    status: APIKeyStatus = APIKeyStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

    # Security
    permissions: APIKeyPermissions = field(default_factory=APIKeyPermissions)
    ip_whitelist: Set[str] = field(default_factory=set)

    # Usage tracking
    total_requests: int = 0
    total_errors: int = 0
    last_error_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        result = {
            "key_id": self.key_id,
            "key_hash": self.key_hash,
            "name": self.name,
            "description": self.description,
            "user_id": self.user_id,
            "user_role": self.user_role.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "permissions": {
                "can_access_reasoning": self.permissions.can_access_reasoning,
                "can_access_msa": self.permissions.can_access_msa,
                "can_access_admin": self.permissions.can_access_admin,
                "can_access_health": self.permissions.can_access_health,
                "can_read": self.permissions.can_read,
                "can_write": self.permissions.can_write,
                "can_delete": self.permissions.can_delete,
                "max_concurrent_requests": self.permissions.max_concurrent_requests,
                "allowed_models": list(self.permissions.allowed_models),
                "allowed_endpoints": list(self.permissions.allowed_endpoints),
            },
            "ip_whitelist": list(self.ip_whitelist),
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "last_error_at": self.last_error_at.isoformat() if self.last_error_at else None,
        }
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APIKeyMetadata":
        """Create from dictionary"""
        permissions = APIKeyPermissions(
            can_access_reasoning=data["permissions"]["can_access_reasoning"],
            can_access_msa=data["permissions"]["can_access_msa"],
            can_access_admin=data["permissions"]["can_access_admin"],
            can_access_health=data["permissions"]["can_access_health"],
            can_read=data["permissions"]["can_read"],
            can_write=data["permissions"]["can_write"],
            can_delete=data["permissions"]["can_delete"],
            max_concurrent_requests=data["permissions"]["max_concurrent_requests"],
            allowed_models=set(data["permissions"]["allowed_models"]),
            allowed_endpoints=set(data["permissions"]["allowed_endpoints"]),
        )

        return cls(
            key_id=data["key_id"],
            key_hash=data["key_hash"],
            name=data["name"],
            description=data["description"],
            user_id=data["user_id"],
            user_role=UserRole(data["user_role"]),
            status=APIKeyStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data["expires_at"] else None,
            last_used_at=datetime.fromisoformat(data["last_used_at"]) if data["last_used_at"] else None,
            permissions=permissions,
            ip_whitelist=set(data["ip_whitelist"]),
            total_requests=data["total_requests"],
            total_errors=data["total_errors"],
            last_error_at=datetime.fromisoformat(data["last_error_at"]) if data["last_error_at"] else None,
        )


class APIKeyManager:
    """Manages API keys with Redis backend"""

    def __init__(self, redis_url: str = "redis://localhost:6379/1"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.memory_store: Dict[str, APIKeyMetadata] = {}  # Fallback storage
        self.active_requests: Dict[str, int] = {}  # Track concurrent requests

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("API key manager initialized with Redis backend")
        except Exception as e:
            logger.warning(f"Redis initialization failed for API keys: {e}. Using memory fallback.")
            self.redis_client = None

    def _hash_key(self, api_key: str) -> str:
        """Create secure hash of API key"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    def _generate_key_id(self) -> str:
        """Generate unique key ID"""
        return str(uuid.uuid4())

    def _generate_api_key(self) -> str:
        """Generate secure API key"""
        # Format: rk_<random_32_chars>
        random_part = secrets.token_urlsafe(24)  # 32 chars base64url encoded
        return f"rk_{random_part}"

    async def create_api_key(
        self,
        name: str,
        user_id: Optional[str] = None,
        user_role: UserRole = UserRole.USER,
        description: str = "",
        permissions: Optional[APIKeyPermissions] = None,
        expires_in_days: Optional[int] = None,
        ip_whitelist: Optional[Set[str]] = None,
    ) -> Tuple[str, APIKeyMetadata]:
        """Create new API key"""

        # Generate key and metadata
        api_key = self._generate_api_key()
        key_id = self._generate_key_id()
        key_hash = self._hash_key(api_key)

        # Set expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Create metadata
        metadata = APIKeyMetadata(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            description=description,
            user_id=user_id,
            user_role=user_role,
            expires_at=expires_at,
            permissions=permissions or APIKeyPermissions(),
            ip_whitelist=ip_whitelist or set(),
        )

        # Store metadata
        await self._store_metadata(key_hash, metadata)

        logger.info(f"Created API key '{name}' for user {user_id}")

        return api_key, metadata

    async def validate_api_key(
        self, api_key: str, request: Optional[Request] = None
    ) -> Tuple[bool, Optional[APIKeyMetadata], Optional[str]]:
        """Validate API key and return metadata"""

        if not api_key or not api_key.startswith("rk_"):
            return False, None, "Invalid API key format"

        key_hash = self._hash_key(api_key)
        metadata = await self._get_metadata(key_hash)

        if not metadata:
            return False, None, "API key not found"

        # Check if key is active
        if metadata.status != APIKeyStatus.ACTIVE:
            return False, metadata, f"API key is {metadata.status.value}"

        # Check expiration
        if metadata.expires_at and datetime.utcnow() > metadata.expires_at:
            # Mark as expired
            metadata.status = APIKeyStatus.EXPIRED
            await self._store_metadata(key_hash, metadata)
            return False, metadata, "API key has expired"

        # Check IP whitelist
        if request and metadata.ip_whitelist:
            client_ip = self._get_client_ip(request)
            if client_ip not in metadata.ip_whitelist:
                logger.warning(f"IP {client_ip} not in whitelist for API key {metadata.name}")
                return False, metadata, "IP not in whitelist"

        # Check concurrent request limit
        if metadata.permissions.max_concurrent_requests > 0:
            current_requests = self.active_requests.get(key_hash, 0)
            if current_requests >= metadata.permissions.max_concurrent_requests:
                return False, metadata, "Concurrent request limit exceeded"

        # Update usage tracking
        metadata.last_used_at = datetime.utcnow()
        metadata.total_requests += 1
        await self._store_metadata(key_hash, metadata)

        # Track active request
        self.active_requests[key_hash] = self.active_requests.get(key_hash, 0) + 1

        return True, metadata, None

    async def check_permission(self, metadata: APIKeyMetadata, endpoint: str, method: str = "GET") -> Tuple[bool, str]:
        """Check if API key has permission for endpoint"""

        permissions = metadata.permissions

        # Check endpoint-specific access
        if permissions.allowed_endpoints and endpoint not in permissions.allowed_endpoints:
            return False, f"Access denied to endpoint: {endpoint}"

        # Check method permissions
        if method.upper() in ["POST", "PUT", "PATCH"] and not permissions.can_write:
            return False, "Write access denied"

        if method.upper() == "DELETE" and not permissions.can_delete:
            return False, "Delete access denied"

        if method.upper() == "GET" and not permissions.can_read:
            return False, "Read access denied"

        # Check specific endpoint categories
        if endpoint.startswith("/reasoning") and not permissions.can_access_reasoning:
            return False, "Access denied to reasoning endpoints"

        if endpoint.startswith("/msa") and not permissions.can_access_msa:
            return False, "Access denied to MSA endpoints"

        if endpoint.startswith("/admin") and not permissions.can_access_admin:
            return False, "Admin access denied"

        return True, "Access granted"

    async def revoke_api_key(self, api_key: str) -> bool:
        """Revoke an API key"""
        key_hash = self._hash_key(api_key)
        metadata = await self._get_metadata(key_hash)

        if metadata:
            metadata.status = APIKeyStatus.REVOKED
            metadata.updated_at = datetime.utcnow()
            await self._store_metadata(key_hash, metadata)
            logger.info(f"Revoked API key {metadata.name}")
            return True

        return False

    async def list_api_keys(self, user_id: Optional[str] = None) -> List[APIKeyMetadata]:
        """List API keys, optionally filtered by user"""
        # This is a simplified implementation
        # In production, you'd want pagination and better filtering
        keys = []

        if self.redis_client:
            try:
                # Get all API key hashes
                pattern = "api_key:*"
                async for key in self.redis_client.scan_iter(match=pattern):
                    data = await self.redis_client.get(key)
                    if data:
                        metadata = APIKeyMetadata.from_dict(json.loads(data))
                        if user_id is None or metadata.user_id == user_id:
                            keys.append(metadata)
            except RedisError:
                # Fall back to memory store
                keys = [m for m in self.memory_store.values() if user_id is None or m.user_id == user_id]
        else:
            keys = [m for m in self.memory_store.values() if user_id is None or m.user_id == user_id]

        return keys

    async def get_usage_stats(self, api_key: str) -> Dict[str, Any]:
        """Get usage statistics for an API key"""
        key_hash = self._hash_key(api_key)
        metadata = await self._get_metadata(key_hash)

        if not metadata:
            return {}

        return {
            "key_name": metadata.name,
            "total_requests": metadata.total_requests,
            "total_errors": metadata.total_errors,
            "error_rate": metadata.total_errors / max(metadata.total_requests, 1),
            "last_used_at": metadata.last_used_at.isoformat() if metadata.last_used_at else None,
            "created_at": metadata.created_at.isoformat(),
            "status": metadata.status.value,
            "current_concurrent_requests": self.active_requests.get(key_hash, 0),
        }

    def release_request(self, api_key: str):
        """Release a concurrent request slot"""
        key_hash = self._hash_key(api_key)
        if key_hash in self.active_requests:
            self.active_requests[key_hash] = max(0, self.active_requests[key_hash] - 1)
            if self.active_requests[key_hash] == 0:
                del self.active_requests[key_hash]

    async def _store_metadata(self, key_hash: str, metadata: APIKeyMetadata):
        """Store API key metadata"""
        redis_key = f"api_key:{key_hash}"
        data = json.dumps(metadata.to_dict())

        if self.redis_client:
            try:
                await self.redis_client.set(redis_key, data)
                return
            except RedisError:
                pass

        # Fall back to memory storage
        self.memory_store[key_hash] = metadata

    async def _get_metadata(self, key_hash: str) -> Optional[APIKeyMetadata]:
        """Retrieve API key metadata"""
        redis_key = f"api_key:{key_hash}"

        if self.redis_client:
            try:
                data = await self.redis_client.get(redis_key)
                if data:
                    return APIKeyMetadata.from_dict(json.loads(data))
            except RedisError:
                pass

        # Fall back to memory storage
        return self.memory_store.get(key_hash)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


# FastAPI dependencies and security
security = HTTPBearer(auto_error=False)
api_key_manager = APIKeyManager()


async def get_api_key_from_request(request: Request) -> Optional[str]:
    """Extract API key from request headers or query params"""

    # Try X-API-Key header
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return api_key

    # Try Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1]

    # Try query parameter
    return request.query_params.get("api_key")


async def validate_api_key_dependency(request: Request) -> APIKeyMetadata:
    """FastAPI dependency for API key validation"""

    api_key = await get_api_key_from_request(request)
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    is_valid, metadata, error = await api_key_manager.validate_api_key(api_key, request)
    if not is_valid:
        raise HTTPException(status_code=401, detail=error or "Invalid API key")

    # Store metadata in request state for later use
    assert metadata is not None
    request.state.api_key_metadata = metadata
    request.state.user_id = metadata.user_id  # type: ignore[attr-defined]

    return metadata


async def check_admin_permission(metadata: APIKeyMetadata = Depends(validate_api_key_dependency)):
    """Require admin permissions"""
    if not metadata.permissions.can_access_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return metadata


# Context manager for request tracking
class APIKeyRequestContext:
    """Context manager for tracking API key requests"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Release the request slot
        api_key_manager.release_request(self.api_key)

        # Log error if exception occurred
        if exc_type:
            key_hash = api_key_manager._hash_key(self.api_key)
            metadata = await api_key_manager._get_metadata(key_hash)
            if metadata:
                metadata.total_errors += 1
                metadata.last_error_at = datetime.utcnow()
                await api_key_manager._store_metadata(key_hash, metadata)
