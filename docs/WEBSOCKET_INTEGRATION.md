# WebSocket Real-Time Updates Integration

Complete guide for the real-time WebSocket processing updates system in Z-Stack Analyzer.

## Overview

The WebSocket system provides millisecond-latency updates for image processing operations, including:

- Real-time progress updates (0-100%)
- Step-by-step processing status
- ETA calculations
- GPU utilization monitoring
- Success/failure notifications
- Validation requirement alerts

## Architecture

```
┌─────────────────┐
│   Frontend      │
│  React Client   │
│                 │
│  - useWebSocket │◄──┐
│  - Toast        │   │
│  - Processing   │   │
│    Status       │   │
└─────────────────┘   │
         │            │
         │ WebSocket  │
         │ Connection │
         ▼            │
┌─────────────────┐   │
│   Backend       │   │
│  FastAPI        │   │
│                 │   │
│  - WebSocket    │───┘
│    Manager      │
│  - Event        │
│    Emitters     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  ZStackAnalyzer │
│  Progress       │
│  Callbacks      │
└─────────────────┘
```

## Backend Components

### 1. WebSocket Manager (`api/websocket/manager.py`)

Central connection management with:
- Session-based grouping
- Automatic heartbeat (30s interval)
- Reconnection handling
- Message broadcasting
- Connection health monitoring

```python
from api.websocket.manager import connection_manager

# Broadcast to all clients
await connection_manager.broadcast(event)

# Send to specific session
await connection_manager.send_to_session(session_id, event)

# Send to specific client
await connection_manager.send_to_client(client_id, event)
```

### 2. Event Definitions (`api/websocket/events.py`)

Type-safe event schemas using Pydantic:

**ProcessingStarted**
```python
{
    "event_type": "processing_started",
    "image_id": "abc123",
    "algorithm": "segmentation_3d",
    "estimated_time_seconds": 5.0,
    "parameters": {...}
}
```

**ProcessingProgress**
```python
{
    "event_type": "processing_progress",
    "image_id": "abc123",
    "progress": 45.5,
    "current_step": "Running 3D segmentation model",
    "eta_seconds": 2.3
}
```

**ProcessingComplete**
```python
{
    "event_type": "processing_complete",
    "image_id": "abc123",
    "result_id": "def456",
    "summary": {...},
    "processing_time_seconds": 4.8,
    "confidence_score": 0.85
}
```

**ProcessingFailed**
```python
{
    "event_type": "processing_failed",
    "image_id": "abc123",
    "error": "GPU memory insufficient",
    "error_code": "CUDA_OUT_OF_MEMORY",
    "retry_available": true
}
```

**ValidationRequired**
```python
{
    "event_type": "validation_required",
    "result_id": "def456",
    "confidence": 0.65,
    "reason": "Confidence score below threshold (0.7)",
    "suggested_actions": ["Review segmentation boundaries"]
}
```

**SystemStatus**
```python
{
    "event_type": "system_status",
    "gpu_utilization": 78.5,
    "gpu_memory_used_mb": 8192,
    "gpu_memory_total_mb": 16384,
    "queue_length": 3,
    "active_processing_count": 2
}
```

### 3. Progress Callback Integration

The `ZStackAnalyzer` accepts a progress callback:

```python
async def progress_callback(progress: float, step: str, eta: Optional[float]):
    event = ProcessingProgress(
        image_id=image_id,
        progress=progress,
        current_step=step,
        eta_seconds=eta
    )
    await connection_manager.broadcast(event)

analyzer = ZStackAnalyzer(progress_callback=progress_callback)
await analyzer.analyze(file_path, algorithm, parameters)
```

### 4. FastAPI Endpoint (`api/main.py`)

```python
@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: Optional[str] = Query(None)
):
    client_id = await connection_manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle client messages
    finally:
        await connection_manager.disconnect(client_id)
```

## Frontend Components

### 1. useWebSocket Hook (`hooks/useWebSocket.ts`)

React hook with auto-reconnection and exponential backoff:

```typescript
const { status, isConnected, send, reconnect } = useWebSocket(
  {
    url: "ws://localhost:8000/ws",
    sessionId: "user-session-123",
    reconnect: true,
    maxReconnectAttempts: 10,
  },
  {
    processing_progress: (event) => {
      console.log(`Progress: ${event.progress}%`);
    },
    processing_complete: (event) => {
      alert("Analysis complete!");
    },
  }
);
```

**Features:**
- Automatic reconnection with exponential backoff (1s → 2s → 4s → 8s → 16s → 30s max)
- Message queuing when disconnected
- Heartbeat timeout detection (45s)
- Type-safe event handlers
- Connection status tracking

### 2. ProcessingStatus Component

Real-time progress visualization:

```typescript
<ProcessingStatus
  imageId="abc123"
  progress={75.5}
  currentStep="Computing object metrics"
  etaSeconds={2.3}
  algorithm="segmentation_3d"
  gpuUtilization={78.5}
  onCancel={() => cancelAnalysis()}
/>
```

**Features:**
- Animated progress bar with shimmer effect
- Real-time ETA countdown
- GPU utilization indicator
- Cancel button
- Color-coded progress (orange → yellow → blue → green)
- Smooth animation transitions

### 3. Toast Notification System

Event-driven notifications:

```typescript
const toast = useToast();

toast.success("Analysis Complete", "Processing finished in 4.8s", {
  duration: 5000,
  action: {
    label: "View Results",
    onClick: () => navigate(`/results/${resultId}`)
  }
});

toast.error("Analysis Failed", error.message, {
  duration: 0, // No auto-dismiss
  action: {
    label: "Retry",
    onClick: () => retryAnalysis()
  }
});
```

**Features:**
- Auto-dismiss with progress bar
- Multiple toast stacking (max 5)
- Action buttons
- Type-based styling (success, error, warning, info)
- Slide-in animation
- Accessible (ARIA labels)

### 4. WebSocketProvider

Context provider with automatic event handling:

```typescript
<WebSocketProvider wsUrl="ws://localhost:8000/ws" sessionId={userId}>
  <App />
</WebSocketProvider>
```

Automatically handles:
- Connection management
- Processing state tracking
- Toast notifications
- System status updates

**Hooks:**
```typescript
// Get processing state for specific image
const state = useProcessingState(imageId);

// Check if any processing is active
const hasActive = useHasActiveProcessing();

// Get all active processing states
const allStates = useAllProcessingStates();

// Access WebSocket context
const { status, isConnected, clientId, systemStatus } = useWebSocketContext();
```

## Usage Examples

### Basic Integration

```typescript
import { WebSocketProvider } from "./components/WebSocketProvider";
import { AnalysisDashboard } from "./components/AnalysisDashboard";

function App() {
  return (
    <WebSocketProvider wsUrl="ws://localhost:8000/ws">
      <AnalysisDashboard />
    </WebSocketProvider>
  );
}
```

### Custom Event Handling

```typescript
const { status, send } = useWebSocket(
  { url: "ws://localhost:8000/ws" },
  {
    processing_started: (event) => {
      console.log(`Started: ${event.algorithm}`);
    },
    processing_progress: (event) => {
      updateProgressBar(event.progress);
    },
    processing_complete: (event) => {
      showResults(event.result_id);
    },
    processing_failed: (event) => {
      handleError(event.error);
    },
  }
);
```

### Session-Based Updates

Multiple tabs/windows can share updates using the same session ID:

```typescript
const sessionId = localStorage.getItem("session_id") || generateSessionId();

<WebSocketProvider wsUrl="ws://localhost:8000/ws" sessionId={sessionId}>
  {children}
</WebSocketProvider>
```

## Testing

### Manual Testing

1. Start backend: `uvicorn api.main:app --reload`
2. Start frontend: `npm run dev`
3. Open DevTools → Network → WS
4. Upload image and start analysis
5. Observe WebSocket messages

### Event Simulation

Create a demo route for testing:

```python
@router.post("/demo/simulate-analysis/{image_id}")
async def simulate_analysis(image_id: str):
    async def emit_progress(p, step, eta):
        await connection_manager.broadcast(
            ProcessingProgress(
                image_id=image_id,
                progress=p,
                current_step=step,
                eta_seconds=eta
            )
        )

    await emit_progress(0, "Starting", 5)
    await asyncio.sleep(1)
    await emit_progress(25, "Loading data", 4)
    await asyncio.sleep(1)
    await emit_progress(50, "Processing", 2)
    await asyncio.sleep(1)
    await emit_progress(75, "Finalizing", 1)
    await asyncio.sleep(1)
    await emit_progress(100, "Complete", 0)
```

## Performance Considerations

**Message Frequency:**
- Progress updates: Max 10/second (100ms intervals)
- Heartbeat: Every 30 seconds
- System status: Every 5 seconds

**Connection Limits:**
- No hard limit on concurrent connections
- Each connection uses ~50KB memory
- Recommend max 1000 concurrent clients per instance

**Network Efficiency:**
- JSON payloads: 200-500 bytes per message
- Gzip compression supported
- Batching not implemented (each event sent immediately)

## Troubleshooting

**Connection keeps dropping:**
- Check firewall settings
- Verify WebSocket proxy configuration (nginx, etc.)
- Increase heartbeat timeout

**Events not received:**
- Check session_id matches
- Verify event handlers are registered
- Check browser console for errors

**High memory usage:**
- Limit max connections
- Clean up stale connections
- Reduce heartbeat frequency

**Slow reconnection:**
- Reduce maxReconnectAttempts
- Adjust reconnectInterval
- Implement connection pooling

## Production Deployment

**HTTPS/WSS:**
```typescript
const wsUrl = window.location.protocol === "https:"
  ? "wss://api.example.com/ws"
  : "ws://localhost:8000/ws";
```

**Load Balancing:**
Use sticky sessions or Redis pub/sub for multi-instance deployments.

**Monitoring:**
- Track connection count: `GET /ws/stats`
- Monitor reconnection rate
- Alert on high error rate

## Future Enhancements

- [ ] Message compression (MessagePack)
- [ ] Binary data support (images, videos)
- [ ] Event replay on reconnection
- [ ] Multi-room broadcasting
- [ ] Rate limiting per client
- [ ] Connection authentication tokens
- [ ] Encryption (end-to-end)
