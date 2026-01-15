"""WebSocket connection manager for real-time updates."""

import asyncio
import logging
from typing import Dict, Set, Optional, Any
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect
import json
import uuid

from .events import WebSocketEvent, ConnectionAck, Heartbeat

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections with session tracking and health monitoring."""

    def __init__(self, heartbeat_interval: int = 30):
        # Active connections: client_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

        # Session-based connections: session_id -> Set[client_id]
        self.sessions: Dict[str, Set[str]] = {}

        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

        # Heartbeat configuration
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}

        logger.info("ConnectionManager initialized")

    async def connect(
        self,
        websocket: WebSocket,
        session_id: Optional[str] = None
    ) -> str:
        """Accept a new WebSocket connection and register it."""
        await websocket.accept()

        # Generate unique client ID
        client_id = str(uuid.uuid4())

        # Store connection
        self.active_connections[client_id] = websocket

        # Associate with session if provided
        if session_id:
            if session_id not in self.sessions:
                self.sessions[session_id] = set()
            self.sessions[session_id].add(client_id)

        # Store metadata
        self.connection_metadata[client_id] = {
            "session_id": session_id,
            "connected_at": datetime.utcnow(),
            "last_heartbeat": datetime.utcnow(),
            "message_count": 0,
        }

        # Start heartbeat task
        self.heartbeat_tasks[client_id] = asyncio.create_task(
            self._heartbeat_loop(client_id)
        )

        # Send connection acknowledgment
        ack_event = ConnectionAck(
            client_id=client_id,
            session_id=session_id,
        )
        await self._send_to_client(client_id, ack_event)

        logger.info(
            f"Client {client_id} connected"
            + (f" (session: {session_id})" if session_id else "")
        )

        return client_id

    async def disconnect(self, client_id: str):
        """Disconnect a WebSocket client and clean up resources."""
        if client_id not in self.active_connections:
            return

        # Cancel heartbeat task
        if client_id in self.heartbeat_tasks:
            self.heartbeat_tasks[client_id].cancel()
            del self.heartbeat_tasks[client_id]

        # Remove from session
        metadata = self.connection_metadata.get(client_id)
        if metadata and metadata.get("session_id"):
            session_id = metadata["session_id"]
            if session_id in self.sessions:
                self.sessions[session_id].discard(client_id)
                if not self.sessions[session_id]:
                    del self.sessions[session_id]

        # Remove connection
        del self.active_connections[client_id]
        del self.connection_metadata[client_id]

        logger.info(f"Client {client_id} disconnected")

    async def broadcast(self, event: WebSocketEvent, exclude: Optional[Set[str]] = None):
        """Broadcast an event to all connected clients."""
        exclude = exclude or set()

        disconnected_clients = []
        for client_id in list(self.active_connections.keys()):
            if client_id not in exclude:
                success = await self._send_to_client(client_id, event)
                if not success:
                    disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)

    async def send_to_session(self, session_id: str, event: WebSocketEvent):
        """Send an event to all clients in a specific session."""
        if session_id not in self.sessions:
            logger.warning(f"No clients found for session {session_id}")
            return

        disconnected_clients = []
        for client_id in list(self.sessions[session_id]):
            success = await self._send_to_client(client_id, event)
            if not success:
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)

    async def send_to_client(self, client_id: str, event: WebSocketEvent):
        """Send an event to a specific client."""
        return await self._send_to_client(client_id, event)

    async def _send_to_client(self, client_id: str, event: WebSocketEvent) -> bool:
        """Internal method to send an event to a client."""
        if client_id not in self.active_connections:
            return False

        websocket = self.active_connections[client_id]

        try:
            # Serialize event to JSON
            event_data = event.model_dump(mode="json")
            await websocket.send_json(event_data)

            # Update metadata
            if client_id in self.connection_metadata:
                self.connection_metadata[client_id]["message_count"] += 1

            return True

        except WebSocketDisconnect:
            logger.info(f"Client {client_id} disconnected during send")
            return False
        except Exception as e:
            logger.error(f"Error sending to client {client_id}: {e}")
            return False

    async def _heartbeat_loop(self, client_id: str):
        """Send periodic heartbeat messages to maintain connection."""
        try:
            while client_id in self.active_connections:
                await asyncio.sleep(self.heartbeat_interval)

                if client_id not in self.active_connections:
                    break

                heartbeat = Heartbeat(session_id=None)
                success = await self._send_to_client(client_id, heartbeat)

                if success:
                    self.connection_metadata[client_id]["last_heartbeat"] = datetime.utcnow()
                else:
                    break

        except asyncio.CancelledError:
            logger.debug(f"Heartbeat loop cancelled for client {client_id}")
        except Exception as e:
            logger.error(f"Error in heartbeat loop for client {client_id}: {e}")

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about active connections."""
        total_connections = len(self.active_connections)
        total_sessions = len(self.sessions)

        sessions_info = {}
        for session_id, client_ids in self.sessions.items():
            sessions_info[session_id] = len(client_ids)

        return {
            "total_connections": total_connections,
            "total_sessions": total_sessions,
            "sessions": sessions_info,
            "connections": {
                client_id: {
                    "connected_at": metadata["connected_at"].isoformat(),
                    "last_heartbeat": metadata["last_heartbeat"].isoformat(),
                    "message_count": metadata["message_count"],
                    "session_id": metadata.get("session_id"),
                }
                for client_id, metadata in self.connection_metadata.items()
            },
        }

    async def cleanup_stale_connections(self, timeout_seconds: int = 120):
        """Clean up connections that haven't received heartbeat in timeout period."""
        now = datetime.utcnow()
        stale_clients = []

        for client_id, metadata in self.connection_metadata.items():
            last_heartbeat = metadata.get("last_heartbeat")
            if last_heartbeat and (now - last_heartbeat) > timedelta(seconds=timeout_seconds):
                stale_clients.append(client_id)

        for client_id in stale_clients:
            logger.warning(f"Cleaning up stale connection: {client_id}")
            await self.disconnect(client_id)

        return len(stale_clients)


# Global connection manager instance
connection_manager = ConnectionManager()
