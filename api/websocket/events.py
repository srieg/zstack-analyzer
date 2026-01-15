"""WebSocket event definitions for real-time processing updates."""

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class WebSocketEvent(BaseModel):
    """Base class for all WebSocket events."""

    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None


class ProcessingStarted(WebSocketEvent):
    """Event emitted when analysis processing starts."""

    event_type: Literal["processing_started"] = "processing_started"
    image_id: str
    algorithm: str
    estimated_time_seconds: Optional[float] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ProcessingProgress(WebSocketEvent):
    """Event emitted during analysis processing with progress updates."""

    event_type: Literal["processing_progress"] = "processing_progress"
    image_id: str
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage 0-100")
    current_step: str
    eta_seconds: Optional[float] = None
    substep_progress: Optional[float] = Field(None, ge=0.0, le=100.0)
    details: Optional[Dict[str, Any]] = None


class ProcessingComplete(WebSocketEvent):
    """Event emitted when analysis processing completes successfully."""

    event_type: Literal["processing_complete"] = "processing_complete"
    image_id: str
    result_id: str
    summary: Dict[str, Any]
    processing_time_seconds: float
    confidence_score: Optional[float] = None


class ProcessingFailed(WebSocketEvent):
    """Event emitted when analysis processing fails."""

    event_type: Literal["processing_failed"] = "processing_failed"
    image_id: str
    error: str
    error_code: Optional[str] = None
    retry_available: bool = True
    details: Optional[Dict[str, Any]] = None


class ValidationRequired(WebSocketEvent):
    """Event emitted when analysis results require human validation."""

    event_type: Literal["validation_required"] = "validation_required"
    result_id: str
    confidence: float
    preview_url: Optional[str] = None
    reason: str = "Low confidence score"
    suggested_actions: list[str] = Field(default_factory=list)


class SystemStatus(WebSocketEvent):
    """Event emitted with system resource and queue status updates."""

    event_type: Literal["system_status"] = "system_status"
    gpu_utilization: Optional[float] = Field(None, ge=0.0, le=100.0)
    gpu_memory_used_mb: Optional[float] = None
    gpu_memory_total_mb: Optional[float] = None
    cpu_utilization: Optional[float] = Field(None, ge=0.0, le=100.0)
    memory_used_mb: Optional[float] = None
    memory_total_mb: Optional[float] = None
    queue_length: int = 0
    active_processing_count: int = 0


class ConnectionAck(WebSocketEvent):
    """Event sent to acknowledge successful WebSocket connection."""

    event_type: Literal["connection_ack"] = "connection_ack"
    client_id: str
    message: str = "Connected to Z-Stack Analyzer"


class Heartbeat(WebSocketEvent):
    """Heartbeat event for connection health monitoring."""

    event_type: Literal["heartbeat"] = "heartbeat"
    server_time: datetime = Field(default_factory=datetime.utcnow)


# Event registry for type validation
EVENT_TYPES = {
    "processing_started": ProcessingStarted,
    "processing_progress": ProcessingProgress,
    "processing_complete": ProcessingComplete,
    "processing_failed": ProcessingFailed,
    "validation_required": ValidationRequired,
    "system_status": SystemStatus,
    "connection_ack": ConnectionAck,
    "heartbeat": Heartbeat,
}
