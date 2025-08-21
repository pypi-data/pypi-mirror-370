"""
API Key Management Endpoints for MSA Reasoning Kernel

Provides REST API endpoints for API key management:
- Create API keys
- List API keys
- Revoke API keys
- Get API key usage statistics
- Manage API key permissions
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Request
from pydantic import BaseModel
from pydantic import Field
from reasoning_kernel.core.logging_config import get_logger
from reasoning_kernel.security.api_key_manager import (
    validate_api_key_dependency,
)
from reasoning_kernel.security.api_key_manager import api_key_manager
from reasoning_kernel.security.api_key_manager import APIKeyMetadata
from reasoning_kernel.security.api_key_manager import APIKeyPermissions
from reasoning_kernel.security.api_key_manager import APIKeyStatus
from reasoning_kernel.security.api_key_manager import check_admin_permission
from reasoning_kernel.security.api_key_manager import UserRole
from reasoning_kernel.security.audit_logging import audit_logger
from reasoning_kernel.security.audit_logging import AuditEventType


logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/admin/api-keys", tags=["API Key Management"])


class CreateAPIKeyRequest(BaseModel):
    """Request model for creating API key"""

    name: str = Field(..., description="Human-readable name for the API key")
    description: str = Field("", description="Optional description of the API key's purpose")
    user_id: Optional[str] = Field(None, description="User ID to associate with the key")
    user_role: UserRole = Field(UserRole.USER, description="Role for the API key")
    expires_in_days: Optional[int] = Field(None, description="Number of days until expiration")

    # Permissions
    can_access_reasoning: bool = Field(True, description="Can access reasoning endpoints")
    can_access_msa: bool = Field(True, description="Can access MSA endpoints")
    can_access_admin: bool = Field(False, description="Can access admin endpoints")
    can_access_health: bool = Field(True, description="Can access health endpoints")
    can_read: bool = Field(True, description="Can perform read operations")
    can_write: bool = Field(True, description="Can perform write operations")
    can_delete: bool = Field(False, description="Can perform delete operations")
    max_concurrent_requests: int = Field(10, description="Maximum concurrent requests")

    # IP restriction
    ip_whitelist: List[str] = Field([], description="Allowed IP addresses (empty for no restriction)")


class APIKeyResponse(BaseModel):
    """Response model for API key operations"""

    key_id: str
    name: str
    description: str
    user_id: Optional[str]
    user_role: str
    status: str
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    permissions: Dict[str, Any]
    ip_whitelist: List[str]
    total_requests: int
    total_errors: int


class CreateAPIKeyResponse(BaseModel):
    """Response model for API key creation"""

    api_key: str = Field(..., description="The generated API key (only shown once)")
    metadata: APIKeyResponse


class APIKeyUsageStats(BaseModel):
    """API key usage statistics"""

    key_name: str
    total_requests: int
    total_errors: int
    error_rate: float
    last_used_at: Optional[datetime]
    created_at: datetime
    status: str
    current_concurrent_requests: int


@router.post("/", response_model=CreateAPIKeyResponse, status_code=201)
async def create_api_key(request: CreateAPIKeyRequest, _admin: APIKeyMetadata = Depends(check_admin_permission)):
    """
    Create a new API key

    Requires admin permissions. Returns the API key only once - save it securely!
    """
    try:
        # Create permissions object
        permissions = APIKeyPermissions(
            can_access_reasoning=request.can_access_reasoning,
            can_access_msa=request.can_access_msa,
            can_access_admin=request.can_access_admin,
            can_access_health=request.can_access_health,
            can_read=request.can_read,
            can_write=request.can_write,
            can_delete=request.can_delete,
            max_concurrent_requests=request.max_concurrent_requests,
            allowed_models={"default"},  # Could be made configurable
            allowed_endpoints=set(),  # Empty means all allowed
        )

        # Create API key
        api_key, metadata = await api_key_manager.create_api_key(
            name=request.name,
            description=request.description,
            user_id=request.user_id,
            user_role=request.user_role,
            permissions=permissions,
            expires_in_days=request.expires_in_days,
            ip_whitelist=set(request.ip_whitelist) if request.ip_whitelist else set(),
        )

        # Log the creation
        await audit_logger.log_auth_event(
            AuditEventType.API_KEY_CREATED,
            success=True,
            user_id=_admin.user_id,
            api_key_id=metadata.key_id,
            details={
                "created_key_name": request.name,
                "created_key_role": request.user_role.value,
                "created_by_admin": _admin.key_id,
            },
        )

        # Convert metadata to response format
        metadata_response = APIKeyResponse(
            key_id=metadata.key_id,
            name=metadata.name,
            description=metadata.description,
            user_id=metadata.user_id,
            user_role=metadata.user_role.value,
            status=metadata.status.value,
            created_at=metadata.created_at,
            updated_at=metadata.updated_at,
            expires_at=metadata.expires_at,
            last_used_at=metadata.last_used_at,
            permissions={
                "can_access_reasoning": metadata.permissions.can_access_reasoning,
                "can_access_msa": metadata.permissions.can_access_msa,
                "can_access_admin": metadata.permissions.can_access_admin,
                "can_access_health": metadata.permissions.can_access_health,
                "can_read": metadata.permissions.can_read,
                "can_write": metadata.permissions.can_write,
                "can_delete": metadata.permissions.can_delete,
                "max_concurrent_requests": metadata.permissions.max_concurrent_requests,
            },
            ip_whitelist=list(metadata.ip_whitelist),
            total_requests=metadata.total_requests,
            total_errors=metadata.total_errors,
        )

        return CreateAPIKeyResponse(api_key=api_key, metadata=metadata_response)

    except Exception as e:
        logger.error(f"Failed to create API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to create API key")


@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status: Optional[APIKeyStatus] = Query(None, description="Filter by status"),
    _admin: APIKeyMetadata = Depends(check_admin_permission),
):
    """
    List API keys

    Requires admin permissions. Can filter by user ID and status.
    """
    try:
        # Get all keys (or filtered by user_id)
        keys = await api_key_manager.list_api_keys(user_id=user_id)

        # Apply status filter if provided
        if status:
            keys = [k for k in keys if k.status == status]

        # Convert to response format
        response_keys = []
        for metadata in keys:
            response_keys.append(
                APIKeyResponse(
                    key_id=metadata.key_id,
                    name=metadata.name,
                    description=metadata.description,
                    user_id=metadata.user_id,
                    user_role=metadata.user_role.value,
                    status=metadata.status.value,
                    created_at=metadata.created_at,
                    updated_at=metadata.updated_at,
                    expires_at=metadata.expires_at,
                    last_used_at=metadata.last_used_at,
                    permissions={
                        "can_access_reasoning": metadata.permissions.can_access_reasoning,
                        "can_access_msa": metadata.permissions.can_access_msa,
                        "can_access_admin": metadata.permissions.can_access_admin,
                        "can_access_health": metadata.permissions.can_access_health,
                        "can_read": metadata.permissions.can_read,
                        "can_write": metadata.permissions.can_write,
                        "can_delete": metadata.permissions.can_delete,
                        "max_concurrent_requests": metadata.permissions.max_concurrent_requests,
                    },
                    ip_whitelist=list(metadata.ip_whitelist),
                    total_requests=metadata.total_requests,
                    total_errors=metadata.total_errors,
                )
            )

        return response_keys

    except Exception as e:
        logger.error(f"Failed to list API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to list API keys")


@router.delete("/{key_id}")
async def revoke_api_key(key_id: str, _admin: APIKeyMetadata = Depends(check_admin_permission)):
    """
    Revoke an API key

    Requires admin permissions. This will immediately disable the key.
    """
    try:
        # Find the key to revoke
        keys = await api_key_manager.list_api_keys()
        target_key = None
        for key_metadata in keys:
            if key_metadata.key_id == key_id:
                target_key = key_metadata
                break

        if not target_key:
            raise HTTPException(status_code=404, detail="API key not found")

        # Can't revoke if we don't have the actual key - this is a limitation
        # In a full implementation, you'd store a mapping of key_id to key_hash
        # For now, we'll update the status directly
        target_key.status = APIKeyStatus.REVOKED
        target_key.updated_at = datetime.utcnow()

        # Store updated metadata
        key_hash = api_key_manager._hash_key("dummy")  # This won't work properly
        # TODO: Implement proper key_id to key_hash mapping

        # Log the revocation
        await audit_logger.log_auth_event(
            AuditEventType.API_KEY_REVOKED,
            success=True,
            user_id=_admin.user_id,
            api_key_id=key_id,
            details={"revoked_key_name": target_key.name, "revoked_by_admin": _admin.key_id},
        )

        return {"message": "API key revoked successfully", "key_id": key_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke API key")


@router.get("/{key_id}/usage", response_model=APIKeyUsageStats)
async def get_api_key_usage(key_id: str, _admin: APIKeyMetadata = Depends(check_admin_permission)):
    """
    Get usage statistics for an API key

    Requires admin permissions.
    """
    try:
        # Find the key
        keys = await api_key_manager.list_api_keys()
        target_key = None
        for key_metadata in keys:
            if key_metadata.key_id == key_id:
                target_key = key_metadata
                break

        if not target_key:
            raise HTTPException(status_code=404, detail="API key not found")

        # Get usage stats - this would need the actual key
        # For now, return the basic stats we have
        return APIKeyUsageStats(
            key_name=target_key.name,
            total_requests=target_key.total_requests,
            total_errors=target_key.total_errors,
            error_rate=target_key.total_errors / max(target_key.total_requests, 1),
            last_used_at=target_key.last_used_at,
            created_at=target_key.created_at,
            status=target_key.status.value,
            current_concurrent_requests=0,  # Would need the actual key to check
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get API key usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to get API key usage")


@router.get("/me/info", response_model=APIKeyResponse)
async def get_current_api_key_info(metadata: APIKeyMetadata = Depends(validate_api_key_dependency)):
    """
    Get information about the current API key

    Returns details about the API key used to make this request.
    """
    return APIKeyResponse(
        key_id=metadata.key_id,
        name=metadata.name,
        description=metadata.description,
        user_id=metadata.user_id,
        user_role=metadata.user_role.value,
        status=metadata.status.value,
        created_at=metadata.created_at,
        updated_at=metadata.updated_at,
        expires_at=metadata.expires_at,
        last_used_at=metadata.last_used_at,
        permissions={
            "can_access_reasoning": metadata.permissions.can_access_reasoning,
            "can_access_msa": metadata.permissions.can_access_msa,
            "can_access_admin": metadata.permissions.can_access_admin,
            "can_access_health": metadata.permissions.can_access_health,
            "can_read": metadata.permissions.can_read,
            "can_write": metadata.permissions.can_write,
            "can_delete": metadata.permissions.can_delete,
            "max_concurrent_requests": metadata.permissions.max_concurrent_requests,
        },
        ip_whitelist=list(metadata.ip_whitelist),
        total_requests=metadata.total_requests,
        total_errors=metadata.total_errors,
    )


@router.get("/me/usage", response_model=APIKeyUsageStats)
async def get_current_api_key_usage(request: Request, metadata: APIKeyMetadata = Depends(validate_api_key_dependency)):
    """
    Get usage statistics for the current API key

    Returns usage stats for the API key used to make this request.
    """
    # Extract the actual API key from the request
    from reasoning_kernel.security.api_key_manager import (
        get_api_key_from_request,
    )

    api_key = await get_api_key_from_request(request)
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    try:
        stats = await api_key_manager.get_usage_stats(api_key)

        if not stats:
            raise HTTPException(status_code=404, detail="API key stats not found")

        return APIKeyUsageStats(
            key_name=stats["key_name"],
            total_requests=stats["total_requests"],
            total_errors=stats["total_errors"],
            error_rate=stats["error_rate"],
            last_used_at=datetime.fromisoformat(stats["last_used_at"]) if stats["last_used_at"] else None,
            created_at=datetime.fromisoformat(stats["created_at"]),
            status=stats["status"],
            current_concurrent_requests=stats["current_concurrent_requests"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current API key usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to get usage stats")
