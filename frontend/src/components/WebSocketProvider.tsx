import React, { createContext, useContext, useEffect, useState } from "react";
import { useWebSocket } from "../hooks/useWebSocket";
import { useToast, ToastContainer } from "./Toast";
import {
  ProcessingProgressEvent,
  ProcessingStartedEvent,
  ProcessingCompleteEvent,
  ProcessingFailedEvent,
  ValidationRequiredEvent,
  SystemStatusEvent,
  ConnectionAckEvent,
  WebSocketConnectionStatus,
} from "../types/websocket";

interface WebSocketContextValue {
  status: WebSocketConnectionStatus;
  isConnected: boolean;
  clientId: string | null;
  processingStates: Map<string, ProcessingState>;
  systemStatus: SystemStatusEvent | null;
}

interface ProcessingState {
  imageId: string;
  algorithm: string;
  progress: number;
  currentStep: string;
  etaSeconds: number | null;
  startTime: Date;
}

const WebSocketContext = createContext<WebSocketContextValue | null>(null);

export function useWebSocketContext() {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error("useWebSocketContext must be used within WebSocketProvider");
  }
  return context;
}

interface WebSocketProviderProps {
  children: React.ReactNode;
  wsUrl?: string;
  sessionId?: string;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({
  children,
  wsUrl = "ws://localhost:8000/ws",
  sessionId,
}) => {
  const toast = useToast();
  const [processingStates, setProcessingStates] = useState<Map<string, ProcessingState>>(
    new Map()
  );
  const [systemStatus, setSystemStatus] = useState<SystemStatusEvent | null>(null);

  const { status, isConnected, clientId } = useWebSocket(
    {
      url: wsUrl,
      sessionId,
      reconnect: true,
      reconnectInterval: 1000,
      maxReconnectAttempts: 10,
    },
    {
      processing_started: (event) => {
        const e = event as ProcessingStartedEvent;
        console.log("Processing started:", e);

        setProcessingStates((prev) => {
          const newStates = new Map(prev);
          newStates.set(e.image_id, {
            imageId: e.image_id,
            algorithm: e.algorithm,
            progress: 0,
            currentStep: "Initializing...",
            etaSeconds: e.estimated_time_seconds,
            startTime: new Date(),
          });
          return newStates;
        });

        toast.info(
          "Analysis Started",
          `Starting ${e.algorithm} analysis for image ${e.image_id.substring(0, 8)}...`,
          { duration: 3000 }
        );
      },

      processing_progress: (event) => {
        const e = event as ProcessingProgressEvent;
        console.log("Processing progress:", e);

        setProcessingStates((prev) => {
          const newStates = new Map(prev);
          const existing = newStates.get(e.image_id);
          if (existing) {
            newStates.set(e.image_id, {
              ...existing,
              progress: e.progress,
              currentStep: e.current_step,
              etaSeconds: e.eta_seconds,
            });
          }
          return newStates;
        });
      },

      processing_complete: (event) => {
        const e = event as ProcessingCompleteEvent;
        console.log("Processing complete:", e);

        setProcessingStates((prev) => {
          const newStates = new Map(prev);
          newStates.delete(e.image_id);
          return newStates;
        });

        const confidenceMsg =
          e.confidence_score !== null
            ? ` (Confidence: ${(e.confidence_score * 100).toFixed(1)}%)`
            : "";

        toast.success(
          "Analysis Complete",
          `Image ${e.image_id.substring(0, 8)} processed in ${e.processing_time_seconds.toFixed(1)}s${confidenceMsg}`,
          {
            duration: 5000,
            action: {
              label: "View Results",
              onClick: () => {
                // Navigate to results page
                window.location.href = `/results/${e.result_id}`;
              },
            },
          }
        );
      },

      processing_failed: (event) => {
        const e = event as ProcessingFailedEvent;
        console.error("Processing failed:", e);

        setProcessingStates((prev) => {
          const newStates = new Map(prev);
          newStates.delete(e.image_id);
          return newStates;
        });

        toast.error(
          "Analysis Failed",
          `Error processing image ${e.image_id.substring(0, 8)}: ${e.error}`,
          {
            action: e.retry_available
              ? {
                  label: "Retry",
                  onClick: () => {
                    // Trigger retry
                    console.log("Retrying analysis for", e.image_id);
                  },
                }
              : undefined,
          }
        );
      },

      validation_required: (event) => {
        const e = event as ValidationRequiredEvent;
        console.log("Validation required:", e);

        toast.warning(
          "Validation Required",
          `Low confidence (${(e.confidence * 100).toFixed(1)}%): ${e.reason}`,
          {
            duration: 0, // Don't auto-dismiss
            action: {
              label: "Review",
              onClick: () => {
                window.location.href = `/validation/${e.result_id}`;
              },
            },
          }
        );
      },

      system_status: (event) => {
        const e = event as SystemStatusEvent;
        setSystemStatus(e);

        // Alert if GPU utilization is critically high
        if (e.gpu_utilization && e.gpu_utilization > 95) {
          toast.warning(
            "High GPU Load",
            `GPU utilization at ${e.gpu_utilization.toFixed(1)}% - processing may be slower`,
            { duration: 5000 }
          );
        }
      },

      connection_ack: (event) => {
        const e = event as ConnectionAckEvent;
        console.log("Connected to WebSocket:", e.client_id);
        toast.success("Connected", "Real-time updates enabled", { duration: 2000 });
      },

      heartbeat: () => {
        // Silent heartbeat handling
      },
    }
  );

  // Show connection status changes
  useEffect(() => {
    if (status === "disconnected" || status === "error") {
      toast.error(
        "Connection Lost",
        "Attempting to reconnect to server...",
        { duration: 0 }
      );
    } else if (status === "reconnecting") {
      toast.info("Reconnecting", "Attempting to restore connection...", {
        duration: 0,
      });
    }
  }, [status]);

  const value: WebSocketContextValue = {
    status,
    isConnected,
    clientId,
    processingStates,
    systemStatus,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
      <ToastContainer toasts={toast.toasts} onRemove={toast.removeToast} />
    </WebSocketContext.Provider>
  );
};

// Hook to get processing state for a specific image
export function useProcessingState(imageId: string): ProcessingState | null {
  const { processingStates } = useWebSocketContext();
  return processingStates.get(imageId) ?? null;
}

// Hook to check if any processing is active
export function useHasActiveProcessing(): boolean {
  const { processingStates } = useWebSocketContext();
  return processingStates.size > 0;
}

// Hook to get all active processing states
export function useAllProcessingStates(): ProcessingState[] {
  const { processingStates } = useWebSocketContext();
  return Array.from(processingStates.values());
}
