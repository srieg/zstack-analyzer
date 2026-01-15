import { useEffect, useRef, useState, useCallback } from "react";
import {
  WebSocketConfig,
  WebSocketConnectionStatus,
  WebSocketEvent,
  WebSocketEventType,
} from "../types/websocket";

type EventHandler<T extends WebSocketEvent = WebSocketEvent> = (event: T) => void;

interface UseWebSocketReturn {
  status: WebSocketConnectionStatus;
  isConnected: boolean;
  lastEvent: WebSocketEvent | null;
  clientId: string | null;
  send: (data: any) => void;
  reconnect: () => void;
}

const DEFAULT_CONFIG: Partial<WebSocketConfig> = {
  reconnect: true,
  reconnectInterval: 1000,
  maxReconnectAttempts: 10,
  heartbeatTimeout: 45000, // 45 seconds (server sends every 30s)
};

export function useWebSocket(
  config: WebSocketConfig,
  handlers?: Partial<Record<WebSocketEventType, EventHandler>>
): UseWebSocketReturn {
  const [status, setStatus] = useState<WebSocketConnectionStatus>("disconnected");
  const [lastEvent, setLastEvent] = useState<WebSocketEvent | null>(null);
  const [clientId, setClientId] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const messageQueueRef = useRef<any[]>([]);
  const handlersRef = useRef(handlers);

  // Update handlers ref when handlers change
  useEffect(() => {
    handlersRef.current = handlers;
  }, [handlers]);

  const fullConfig = { ...DEFAULT_CONFIG, ...config };

  const clearReconnectTimeout = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  const clearHeartbeatTimeout = useCallback(() => {
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
      heartbeatTimeoutRef.current = null;
    }
  }, []);

  const resetHeartbeatTimeout = useCallback(() => {
    clearHeartbeatTimeout();

    if (fullConfig.heartbeatTimeout) {
      heartbeatTimeoutRef.current = setTimeout(() => {
        console.warn("WebSocket heartbeat timeout - connection may be stale");
        // Trigger reconnect
        if (wsRef.current) {
          wsRef.current.close();
        }
      }, fullConfig.heartbeatTimeout);
    }
  }, [clearHeartbeatTimeout, fullConfig.heartbeatTimeout]);

  const flushMessageQueue = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      while (messageQueueRef.current.length > 0) {
        const message = messageQueueRef.current.shift();
        wsRef.current.send(JSON.stringify(message));
      }
    }
  }, []);

  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      // Queue message for when connection is restored
      messageQueueRef.current.push(data);
      console.debug("Message queued (not connected):", data);
    }
  }, []);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = fullConfig.sessionId
      ? `${fullConfig.url}?session_id=${fullConfig.sessionId}`
      : fullConfig.url;

    console.log("Connecting to WebSocket:", wsUrl);
    setStatus(reconnectAttemptsRef.current > 0 ? "reconnecting" : "connecting");

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected");
      setStatus("connected");
      reconnectAttemptsRef.current = 0;
      clearReconnectTimeout();
      resetHeartbeatTimeout();
      flushMessageQueue();
    };

    ws.onmessage = (event) => {
      try {
        const data: WebSocketEvent = JSON.parse(event.data);
        setLastEvent(data);

        // Reset heartbeat timeout on any message
        resetHeartbeatTimeout();

        // Handle connection acknowledgment
        if (data.event_type === "connection_ack") {
          setClientId(data.client_id);
        }

        // Call registered event handler
        const handler = handlersRef.current?.[data.event_type];
        if (handler) {
          handler(data);
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setStatus("error");
    };

    ws.onclose = (event) => {
      console.log("WebSocket closed:", event.code, event.reason);
      wsRef.current = null;
      setStatus("disconnected");
      clearHeartbeatTimeout();

      // Attempt reconnection with exponential backoff
      if (fullConfig.reconnect && reconnectAttemptsRef.current < (fullConfig.maxReconnectAttempts || 10)) {
        reconnectAttemptsRef.current += 1;
        const backoffDelay = Math.min(
          (fullConfig.reconnectInterval || 1000) * Math.pow(2, reconnectAttemptsRef.current - 1),
          30000 // Max 30 seconds
        );

        console.log(
          `Reconnecting in ${backoffDelay}ms (attempt ${reconnectAttemptsRef.current}/${fullConfig.maxReconnectAttempts})`
        );

        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, backoffDelay);
      } else if (reconnectAttemptsRef.current >= (fullConfig.maxReconnectAttempts || 10)) {
        console.error("Max reconnection attempts reached");
        setStatus("error");
      }
    };
  }, [
    fullConfig,
    clearReconnectTimeout,
    resetHeartbeatTimeout,
    clearHeartbeatTimeout,
    flushMessageQueue,
  ]);

  const reconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    reconnectAttemptsRef.current = 0;
    connect();
  }, [connect]);

  // Initial connection
  useEffect(() => {
    connect();

    return () => {
      clearReconnectTimeout();
      clearHeartbeatTimeout();
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect, clearReconnectTimeout, clearHeartbeatTimeout]);

  return {
    status,
    isConnected: status === "connected",
    lastEvent,
    clientId,
    send,
    reconnect,
  };
}
