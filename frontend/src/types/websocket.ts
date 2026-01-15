/**
 * WebSocket event types for real-time processing updates
 */

export type WebSocketEventType =
  | "connection_ack"
  | "heartbeat"
  | "processing_started"
  | "processing_progress"
  | "processing_complete"
  | "processing_failed"
  | "validation_required"
  | "system_status";

export interface BaseEvent {
  event_type: WebSocketEventType;
  timestamp: string;
  session_id?: string;
}

export interface ConnectionAckEvent extends BaseEvent {
  event_type: "connection_ack";
  client_id: string;
  message: string;
}

export interface HeartbeatEvent extends BaseEvent {
  event_type: "heartbeat";
  server_time: string;
}

export interface ProcessingStartedEvent extends BaseEvent {
  event_type: "processing_started";
  image_id: string;
  algorithm: string;
  estimated_time_seconds: number | null;
  parameters: Record<string, any>;
}

export interface ProcessingProgressEvent extends BaseEvent {
  event_type: "processing_progress";
  image_id: string;
  progress: number;
  current_step: string;
  eta_seconds: number | null;
  substep_progress?: number;
  details?: Record<string, any>;
}

export interface ProcessingCompleteEvent extends BaseEvent {
  event_type: "processing_complete";
  image_id: string;
  result_id: string;
  summary: Record<string, any>;
  processing_time_seconds: number;
  confidence_score: number | null;
}

export interface ProcessingFailedEvent extends BaseEvent {
  event_type: "processing_failed";
  image_id: string;
  error: string;
  error_code: string | null;
  retry_available: boolean;
  details?: Record<string, any>;
}

export interface ValidationRequiredEvent extends BaseEvent {
  event_type: "validation_required";
  result_id: string;
  confidence: number;
  preview_url: string | null;
  reason: string;
  suggested_actions: string[];
}

export interface SystemStatusEvent extends BaseEvent {
  event_type: "system_status";
  gpu_utilization: number | null;
  gpu_memory_used_mb: number | null;
  gpu_memory_total_mb: number | null;
  cpu_utilization: number | null;
  memory_used_mb: number | null;
  memory_total_mb: number | null;
  queue_length: number;
  active_processing_count: number;
}

export type WebSocketEvent =
  | ConnectionAckEvent
  | HeartbeatEvent
  | ProcessingStartedEvent
  | ProcessingProgressEvent
  | ProcessingCompleteEvent
  | ProcessingFailedEvent
  | ValidationRequiredEvent
  | SystemStatusEvent;

export type WebSocketConnectionStatus =
  | "disconnected"
  | "connecting"
  | "connected"
  | "reconnecting"
  | "error";

export interface WebSocketConfig {
  url: string;
  sessionId?: string;
  reconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatTimeout?: number;
}
