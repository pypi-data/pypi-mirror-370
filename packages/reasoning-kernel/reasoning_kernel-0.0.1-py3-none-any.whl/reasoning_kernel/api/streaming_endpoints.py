"""
WebSocket Streaming Endpoints for Real-time Reasoning Updates
==============================================================

Provides real-time streaming of reasoning stages through WebSocket connections.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect
import structlog

from ...reasoning_kernel import ReasoningConfig


logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v2/ws", tags=["websocket-streaming"])

class ReasoningStreamManager:
    """Manages WebSocket connections for streaming reasoning updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.reasoning_sessions: Dict[str, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info("WebSocket connected", session_id=session_id)
        
    def disconnect(self, session_id: str):
        """Disconnect a WebSocket client"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info("WebSocket disconnected", session_id=session_id)
            
    async def send_stage_update(self, session_id: str, stage_data: Dict[str, Any]):
        """Send stage update to connected client"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_json({
                    "type": "stage_update",
                    "timestamp": datetime.now().isoformat(),
                    **stage_data
                })
            except Exception as e:
                logger.error("Failed to send stage update", 
                           session_id=session_id, 
                           error=str(e))
                
    async def send_thinking_update(self, session_id: str, thinking_data: Dict[str, Any]):
        """Send thinking mode update to connected client"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_json({
                    "type": "thinking_update",
                    "timestamp": datetime.now().isoformat(),
                    **thinking_data
                })
            except Exception as e:
                logger.error("Failed to send thinking update",
                           session_id=session_id,
                           error=str(e))
                
    async def send_sandbox_update(self, session_id: str, sandbox_data: Dict[str, Any]):
        """Send Daytona sandbox execution update"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_json({
                    "type": "sandbox_update",
                    "timestamp": datetime.now().isoformat(),
                    **sandbox_data
                })
            except Exception as e:
                logger.error("Failed to send sandbox update",
                           session_id=session_id,
                           error=str(e))

# Global stream manager instance
stream_manager = ReasoningStreamManager()

@router.websocket("/reasoning/stream/{session_id}")
async def reasoning_stream(
    websocket: WebSocket,
    session_id: str
):
    """
    WebSocket endpoint for streaming reasoning updates in real-time.
    
    Provides live updates for:
    - Stage progress (parse, retrieve, graph, synthesize, infer)
    - Thinking mode sentences
    - Confidence scores
    - Daytona sandbox execution status
    - Error messages and diagnostics
    """
    await stream_manager.connect(websocket, session_id)
    
    try:
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()
                
                if data.get("type") == "ping":
                    # Respond to ping to keep connection alive
                    await websocket.send_json({"type": "pong"})
                    
                elif data.get("type") == "start_reasoning":
                    # Start reasoning process with streaming updates
                    vignette = data.get("vignette", "")
                    config = data.get("config", {})
                    
                    # Start reasoning in background task
                    asyncio.create_task(
                        stream_reasoning_process(
                            session_id,
                            vignette,
                            config,
                            stream_manager
                        )
                    )
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error("WebSocket error", session_id=session_id, error=str(e))
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                
    finally:
        stream_manager.disconnect(session_id)


async def stream_reasoning_process(
    session_id: str,
    vignette: str,
    config: Dict[str, Any],
    manager: ReasoningStreamManager
):
    """
    Execute reasoning process with real-time streaming updates
    """
    try:
        # Get reasoning kernel instance
        from ...main import reasoning_kernel
        if not reasoning_kernel:
            await manager.send_stage_update(session_id, {
                "stage": "error",
                "message": "Reasoning kernel not initialized"
            })
            return
            
        # Configure for streaming
        reasoning_config = ReasoningConfig(**config)
        reasoning_config.enable_streaming = True
        reasoning_config.stream_callback = lambda update: asyncio.create_task(
            handle_stream_update(session_id, update, manager)
        )
        
        # Start reasoning with streaming
        await manager.send_stage_update(session_id, {
            "stage": "initializing",
            "status": "starting",
            "message": "Initializing five-stage reasoning pipeline..."
        })
        
        # Execute reasoning stages with callbacks
        result = await reasoning_kernel.reason_with_streaming(
            vignette=vignette,
            session_id=session_id,
            config=reasoning_config,
            on_stage_start=lambda stage: asyncio.create_task(
                manager.send_stage_update(session_id, {
                    "stage": stage,
                    "status": "running",
                    "message": f"Processing {stage} stage..."
                })
            ),
            on_stage_complete=lambda stage, data: asyncio.create_task(
                manager.send_stage_update(session_id, {
                    "stage": stage,
                    "status": "completed",
                    "confidence": data.get("confidence", 0),
                    "execution_time": data.get("execution_time", 0),
                    "results": data.get("results", {})
                })
            ),
            on_thinking_sentence=lambda sentence: asyncio.create_task(
                manager.send_thinking_update(session_id, {
                    "sentence": sentence,
                    "stage": "thinking"
                })
            ),
            on_sandbox_event=lambda event: asyncio.create_task(
                manager.send_sandbox_update(session_id, event)
            )
        )
        
        # Send final result
        await manager.send_stage_update(session_id, {
            "stage": "complete",
            "status": "finished",
            "overall_confidence": result.overall_confidence,
            "total_time": result.total_execution_time,
            "success": result.success
        })
        
    except Exception as e:
        logger.error("Streaming reasoning failed", 
                    session_id=session_id,
                    error=str(e))
        await manager.send_stage_update(session_id, {
            "stage": "error",
            "status": "failed",
            "message": str(e)
        })


async def handle_stream_update(
    session_id: str, 
    update: Dict[str, Any],
    manager: ReasoningStreamManager
):
    """Handle streaming update from reasoning kernel"""
    update_type = update.get("type", "general")
    
    if update_type == "stage":
        await manager.send_stage_update(session_id, update)
    elif update_type == "thinking":
        await manager.send_thinking_update(session_id, update)
    elif update_type == "sandbox":
        await manager.send_sandbox_update(session_id, update)
    else:
        # Send as general update
        await manager.send_stage_update(session_id, update)