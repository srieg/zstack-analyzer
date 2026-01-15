"""WebSocket support for real-time processing updates."""

from .manager import ConnectionManager
from .events import (
    WebSocketEvent,
    ProcessingStarted,
    ProcessingProgress,
    ProcessingComplete,
    ProcessingFailed,
    ValidationRequired,
    SystemStatus,
)

__all__ = [
    "ConnectionManager",
    "WebSocketEvent",
    "ProcessingStarted",
    "ProcessingProgress",
    "ProcessingComplete",
    "ProcessingFailed",
    "ValidationRequired",
    "SystemStatus",
]
