"""
Daytona API Endpoints - v2
=========================

API endpoints for managing Daytona sandbox integration and status.
Provides sandbox management, configuration, and monitoring capabilities.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import Field
import structlog

from ...services.daytona_service import DaytonaService
from ...services.daytona_service import SandboxConfig


logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/daytona", tags=["daytona"])

class SandboxConfigRequest(BaseModel):
    """Request model for sandbox configuration"""
    cpu_limit: Optional[int] = Field(2, description="CPU limit for sandbox")
    memory_limit_mb: Optional[int] = Field(512, description="Memory limit in MB")
    execution_timeout: Optional[int] = Field(30, description="Execution timeout in seconds")
    temp_storage_mb: Optional[int] = Field(50, description="Temporary storage in MB")
    python_version: Optional[str] = Field("3.11", description="Python version")
    enable_networking: Optional[bool] = Field(False, description="Enable networking")
    enable_ast_validation: Optional[bool] = Field(True, description="Enable AST validation")
    allowed_imports: Optional[List[str]] = Field(None, description="List of allowed imports")

class CodeExecutionRequest(BaseModel):
    """Request model for code execution"""
    code: str = Field(..., description="Python code to execute")
    timeout: Optional[int] = Field(None, description="Execution timeout override")
    config: Optional[SandboxConfigRequest] = Field(None, description="Sandbox configuration override")

class SandboxStatusResponse(BaseModel):
    """Response model for sandbox status"""
    daytona_available: bool
    sandbox_active: bool
    config: Dict[str, Any]
    api_key_configured: bool
    service_status: str

class ExecutionResponse(BaseModel):
    """Response model for code execution"""
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    status: str
    resource_usage: Dict[str, Any]
    metadata: Dict[str, Any]

# Global Daytona service instance
_daytona_service: Optional[DaytonaService] = None

def get_daytona_service() -> DaytonaService:
    """Dependency to get or create Daytona service"""
    global _daytona_service
    if _daytona_service is None:
        _daytona_service = DaytonaService()
    return _daytona_service

@router.get("/status", response_model=SandboxStatusResponse)
async def get_status(service: DaytonaService = Depends(get_daytona_service)):
    """Get Daytona service status"""
    try:
        import os
        status_info = service.get_status()
        
        return SandboxStatusResponse(
            daytona_available=status_info["daytona_available"],
            sandbox_active=status_info["sandbox_active"],
            config=status_info["config"],
            api_key_configured=bool(os.getenv("DAYTONA_API_KEY")),
            service_status="operational" if status_info["daytona_available"] else "fallback_mode"
        )
    except Exception as e:
        logger.error(f"Failed to get Daytona status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sandbox/create")
async def create_sandbox(
    config: Optional[SandboxConfigRequest] = None,
    service: DaytonaService = Depends(get_daytona_service)
):
    """Create a new Daytona sandbox"""
    try:
        # Update service configuration if provided
        if config:
            sandbox_config = SandboxConfig(
                cpu_limit=config.cpu_limit,
                memory_limit_mb=config.memory_limit_mb,
                execution_timeout=config.execution_timeout,
                temp_storage_mb=config.temp_storage_mb,
                python_version=config.python_version,
                enable_networking=config.enable_networking,
                enable_ast_validation=config.enable_ast_validation,
                allowed_imports=config.allowed_imports
            )
            service.config = sandbox_config
        
        success = await service.create_sandbox()
        
        if success:
            return {"status": "success", "message": "Sandbox created successfully"}
        else:
            return {"status": "fallback", "message": "Using local fallback execution"}
            
    except Exception as e:
        logger.error(f"Failed to create sandbox: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute", response_model=ExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    service: DaytonaService = Depends(get_daytona_service)
):
    """Execute code in Daytona sandbox"""
    try:
        # Update configuration if provided
        if request.config:
            sandbox_config = SandboxConfig(
                cpu_limit=request.config.cpu_limit,
                memory_limit_mb=request.config.memory_limit_mb,
                execution_timeout=request.config.execution_timeout,
                temp_storage_mb=request.config.temp_storage_mb,
                python_version=request.config.python_version,
                enable_networking=request.config.enable_networking,
                enable_ast_validation=request.config.enable_ast_validation,
                allowed_imports=request.config.allowed_imports
            )
            service.config = sandbox_config
        
        # Execute code
        result = await service.execute_code(request.code, request.timeout)
        
        return ExecutionResponse(
            exit_code=result.exit_code,
            stdout=result.stdout,
            stderr=result.stderr,
            execution_time=result.execution_time,
            status=result.status.value,
            resource_usage=result.resource_usage,
            metadata=result.metadata
        )
        
    except Exception as e:
        logger.error(f"Code execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sandbox")
async def cleanup_sandbox(service: DaytonaService = Depends(get_daytona_service)):
    """Clean up current sandbox"""
    try:
        success = await service.cleanup_sandbox()
        
        if success:
            return {"status": "success", "message": "Sandbox cleaned up successfully"}
        else:
            return {"status": "warning", "message": "No active sandbox to cleanup"}
            
    except Exception as e:
        logger.error(f"Failed to cleanup sandbox: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_config(service: DaytonaService = Depends(get_daytona_service)):
    """Get current sandbox configuration"""
    try:
        from dataclasses import asdict
        return {"config": asdict(service.config)}
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config")
async def update_config(
    config: SandboxConfigRequest,
    service: DaytonaService = Depends(get_daytona_service)
):
    """Update sandbox configuration"""
    try:
        # Update service configuration
        service.config = SandboxConfig(
            cpu_limit=config.cpu_limit,
            memory_limit_mb=config.memory_limit_mb,
            execution_timeout=config.execution_timeout,
            temp_storage_mb=config.temp_storage_mb,
            python_version=config.python_version,
            enable_networking=config.enable_networking,
            enable_ast_validation=config.enable_ast_validation,
            allowed_imports=config.allowed_imports
        )
        
        return {"status": "success", "message": "Configuration updated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test")
async def test_execution(service: DaytonaService = Depends(get_daytona_service)):
    """Test Daytona sandbox with a simple execution"""
    try:
        test_code = '''
import time
import numpy as np

# Test basic functionality
data = {
    "message": "Hello from Daytona sandbox!",
    "timestamp": time.time(),
    "numpy_version": np.__version__,
    "computation": np.sum([1, 2, 3, 4, 5])
}

print(json.dumps(data))
'''
        
        result = await service.execute_code(test_code)
        
        return {
            "test_status": "success" if result.exit_code == 0 else "failed",
            "result": ExecutionResponse(
                exit_code=result.exit_code,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=result.execution_time,
                status=result.status.value,
                resource_usage=result.resource_usage,
                metadata=result.metadata
            )
        }
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))