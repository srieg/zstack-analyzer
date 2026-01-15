# Quick Start: WebSocket Integration

Get real-time processing updates running in 5 minutes.

## Step 1: Backend Setup

The backend is already configured! WebSocket endpoint is available at:
```
ws://localhost:8000/ws
```

Start the backend:
```bash
cd /Users/samriegel/zstack-analyzer
uvicorn api.main:app --reload
```

## Step 2: Frontend Integration

### Update Your App Root

```typescript
// frontend/src/main.tsx or App.tsx
import { WebSocketProvider } from "./components/WebSocketProvider";
import { AnalysisDashboard } from "./components/AnalysisDashboard";

function App() {
  return (
    <WebSocketProvider
      wsUrl={import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws"}
      sessionId={getUserSessionId()} // Optional: group connections by user
    >
      <YourAppContent />
      {/* Optionally add the sidebar for compact view */}
      <ProcessingStatusSidebar />
    </WebSocketProvider>
  );
}
```

### Environment Variables

```bash
# frontend/.env
VITE_WS_URL=ws://localhost:8000/ws
VITE_API_URL=http://localhost:8000
```

## Step 3: Use in Your Components

### Show Processing Status

```typescript
import { useProcessingState } from "../components/WebSocketProvider";
import { ProcessingStatus } from "../components/ProcessingStatus";

function ImageAnalysisView({ imageId }: { imageId: string }) {
  const processingState = useProcessingState(imageId);

  if (!processingState) {
    return <div>Ready to analyze</div>;
  }

  return (
    <ProcessingStatus
      imageId={processingState.imageId}
      progress={processingState.progress}
      currentStep={processingState.currentStep}
      etaSeconds={processingState.etaSeconds}
      algorithm={processingState.algorithm}
      onCancel={() => cancelAnalysis(imageId)}
    />
  );
}
```

### Check Active Processing

```typescript
import { useHasActiveProcessing } from "../components/WebSocketProvider";

function UploadButton() {
  const hasActiveProcessing = useHasActiveProcessing();

  return (
    <button disabled={hasActiveProcessing}>
      {hasActiveProcessing ? "Processing..." : "Upload Image"}
    </button>
  );
}
```

### Manual Toast Notifications

```typescript
import { useToast } from "../components/Toast";

function MyComponent() {
  const toast = useToast();

  const handleUpload = async () => {
    try {
      await uploadImage();
      toast.success("Upload Complete", "Starting analysis...");
    } catch (error) {
      toast.error("Upload Failed", error.message);
    }
  };

  return <button onClick={handleUpload}>Upload</button>;
}
```

## Step 4: Start Analysis with WebSocket Updates

When starting an analysis, pass the session_id to get updates:

```typescript
async function startAnalysis(imageId: string, algorithm: string) {
  const sessionId = getUserSessionId(); // Or generate one

  const response = await fetch(`/api/v1/analysis/${imageId}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      algorithm,
      parameters: {},
      session_id: sessionId, // Important: match WebSocket session
    }),
  });

  // WebSocket will automatically receive updates!
  // No polling needed.
}
```

## Step 5: Test It

1. Start backend: `uvicorn api.main:app --reload`
2. Start frontend: `npm run dev`
3. Open browser DevTools → Network → WS
4. Upload an image and start analysis
5. Watch real-time updates!

## Complete Example

```typescript
import React, { useState } from "react";
import { WebSocketProvider, useProcessingState } from "./components/WebSocketProvider";
import { ProcessingStatus } from "./components/ProcessingStatus";
import { useToast } from "./components/Toast";

function AnalysisPage() {
  const [imageId, setImageId] = useState<string | null>(null);
  const processingState = useProcessingState(imageId || "");
  const toast = useToast();

  const handleStartAnalysis = async () => {
    const id = "test-image-123";
    setImageId(id);

    try {
      const response = await fetch(`/api/v1/analysis/${id}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          algorithm: "segmentation_3d",
          parameters: { threshold: 0.5 },
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to start analysis");
      }

      toast.info("Analysis Started", "Processing your image...");
    } catch (error) {
      toast.error("Error", error.message);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Image Analysis</h1>

      <button
        onClick={handleStartAnalysis}
        className="bg-blue-500 text-white px-4 py-2 rounded"
        disabled={!!processingState}
      >
        Start Analysis
      </button>

      {processingState && (
        <div className="mt-6">
          <ProcessingStatus
            imageId={processingState.imageId}
            progress={processingState.progress}
            currentStep={processingState.currentStep}
            etaSeconds={processingState.etaSeconds}
            algorithm={processingState.algorithm}
          />
        </div>
      )}
    </div>
  );
}

function App() {
  return (
    <WebSocketProvider wsUrl="ws://localhost:8000/ws">
      <AnalysisPage />
    </WebSocketProvider>
  );
}

export default App;
```

## What You Get

- Real-time progress updates (0-100%)
- Step-by-step processing status
- ETA countdown
- Success/failure notifications
- Automatic reconnection
- GPU utilization monitoring
- Toast notifications
- No polling needed!

## Debugging

### Check WebSocket Connection

Browser DevTools → Network → WS tab:
- Should see connection to `ws://localhost:8000/ws`
- Messages flowing in real-time
- Status should be "101 Switching Protocols"

### Check Backend Logs

```bash
# Should see:
INFO:     WebSocket client <id> connected
INFO:     Analysis started for image <id>
INFO:     Analysis completed for image <id>
```

### Test Connection Endpoint

```bash
curl http://localhost:8000/ws/stats
```

Returns:
```json
{
  "total_connections": 1,
  "total_sessions": 1,
  "connections": {...}
}
```

## Next Steps

- Add authentication tokens to WebSocket connection
- Implement analysis cancellation
- Add more event types (system alerts, batch processing)
- Deploy with WSS (secure WebSocket)
- Add Redis pub/sub for multi-instance deployments

## Troubleshooting

**Issue:** WebSocket connection refused
- **Fix:** Ensure backend is running on port 8000
- Check CORS settings in `main.py`

**Issue:** No events received
- **Fix:** Verify session_id matches between API call and WebSocket
- Check event handlers are registered

**Issue:** Connection drops frequently
- **Fix:** Check firewall/proxy settings
- Increase heartbeat timeout in `useWebSocket`

**Issue:** Slow reconnection
- **Fix:** Reduce `maxReconnectAttempts` in WebSocket config
- Check network stability
