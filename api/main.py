from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
import logging
from typing import Optional

from api.database.connection import get_database
from api.routes import images, analysis, validation, demo
from api.models.base import Base
from api.database.connection import engine
from api.websocket.manager import connection_manager
from api.websocket.events import SystemStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Z-Stack Analyzer API")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    logger.info("Shutting down Z-Stack Analyzer API")

app = FastAPI(
    title="Z-Stack Analyzer API",
    description="GPU-accelerated confocal microscopy Z-stack analysis platform",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(images.router, prefix="/api/v1/images", tags=["images"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(validation.router, prefix="/api/v1/validation", tags=["validation"])
app.include_router(demo.router, prefix="/api/v1/demo", tags=["demo"])

@app.get("/")
async def root():
    return {
        "message": "Z-Stack Analyzer API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "zstack-analyzer-api"}

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: Optional[str] = Query(None, description="Session ID for grouping connections")
):
    """WebSocket endpoint for real-time processing updates."""
    client_id = None
    try:
        # Connect the client
        client_id = await connection_manager.connect(websocket, session_id)
        logger.info(f"WebSocket client {client_id} connected (session: {session_id})")

        # Keep the connection alive and handle incoming messages
        while True:
            try:
                # Receive messages from client (for ping/pong, commands, etc.)
                data = await websocket.receive_json()

                # Handle client messages (optional - for future commands)
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

            except WebSocketDisconnect:
                logger.info(f"WebSocket client {client_id} disconnected")
                break
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected during handshake")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if client_id:
            await connection_manager.disconnect(client_id)

@app.get("/ws/stats")
async def websocket_stats():
    """Get WebSocket connection statistics."""
    return connection_manager.get_connection_stats()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )