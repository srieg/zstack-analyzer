import React from "react";
import {
  useWebSocketContext,
  useAllProcessingStates,
  useHasActiveProcessing,
} from "./WebSocketProvider";
import { ProcessingStatus, ProcessingStatusCompact } from "./ProcessingStatus";

/**
 * Example Dashboard component showing real-time processing status
 * This demonstrates how to use the WebSocket integration for live updates
 */
export const AnalysisDashboard: React.FC = () => {
  const { status, isConnected, clientId, systemStatus } = useWebSocketContext();
  const activeProcessing = useAllProcessingStates();
  const hasActiveProcessing = useHasActiveProcessing();

  const getStatusColor = () => {
    switch (status) {
      case "connected":
        return "bg-green-500";
      case "connecting":
      case "reconnecting":
        return "bg-yellow-500";
      case "disconnected":
      case "error":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusText = () => {
    switch (status) {
      case "connected":
        return "Connected";
      case "connecting":
        return "Connecting...";
      case "reconnecting":
        return "Reconnecting...";
      case "disconnected":
        return "Disconnected";
      case "error":
        return "Connection Error";
      default:
        return "Unknown";
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header with Connection Status */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="bg-white rounded-lg shadow-md p-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Z-Stack Analysis Dashboard
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Real-time processing monitoring
            </p>
          </div>

          <div className="flex items-center gap-4">
            {/* Connection Status */}
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${getStatusColor()} ${isConnected ? 'animate-pulse' : ''}`}></div>
              <span className="text-sm font-medium text-gray-700">
                {getStatusText()}
              </span>
            </div>

            {clientId && (
              <div className="text-xs text-gray-500 border-l pl-4">
                Client: {clientId.substring(0, 8)}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* System Status */}
      {systemStatus && (
        <div className="max-w-7xl mx-auto mb-6">
          <div className="bg-white rounded-lg shadow-md p-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              System Status
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {systemStatus.gpu_utilization !== null && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-sm text-gray-600">GPU Utilization</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">
                    {systemStatus.gpu_utilization.toFixed(1)}%
                  </div>
                </div>
              )}
              {systemStatus.queue_length > 0 && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-sm text-gray-600">Queue Length</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">
                    {systemStatus.queue_length}
                  </div>
                </div>
              )}
              {systemStatus.active_processing_count > 0 && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-sm text-gray-600">Active Processing</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">
                    {systemStatus.active_processing_count}
                  </div>
                </div>
              )}
              {systemStatus.gpu_memory_used_mb !== null &&
                systemStatus.gpu_memory_total_mb !== null && (
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-sm text-gray-600">GPU Memory</div>
                    <div className="text-2xl font-bold text-gray-900 mt-1">
                      {(
                        (systemStatus.gpu_memory_used_mb /
                          systemStatus.gpu_memory_total_mb) *
                        100
                      ).toFixed(1)}
                      %
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {(systemStatus.gpu_memory_used_mb / 1024).toFixed(1)} /{" "}
                      {(systemStatus.gpu_memory_total_mb / 1024).toFixed(1)} GB
                    </div>
                  </div>
                )}
            </div>
          </div>
        </div>
      )}

      {/* Active Processing */}
      <div className="max-w-7xl mx-auto">
        {hasActiveProcessing ? (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Active Processing ({activeProcessing.length})
            </h2>
            {activeProcessing.map((state) => (
              <ProcessingStatus
                key={state.imageId}
                imageId={state.imageId}
                progress={state.progress}
                currentStep={state.currentStep}
                etaSeconds={state.etaSeconds}
                algorithm={state.algorithm}
                gpuUtilization={systemStatus?.gpu_utilization ?? undefined}
                onCancel={() => {
                  console.log("Cancel processing for", state.imageId);
                  // Implement cancel logic
                }}
              />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <svg
              className="w-16 h-16 text-gray-400 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
              />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No Active Processing
            </h3>
            <p className="text-gray-600">
              Upload an image to start analysis
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

// Compact version for sidebar or list views
export const ProcessingStatusSidebar: React.FC = () => {
  const activeProcessing = useAllProcessingStates();
  const hasActiveProcessing = useHasActiveProcessing();

  if (!hasActiveProcessing) return null;

  return (
    <div className="fixed bottom-4 right-4 w-80 max-h-96 overflow-y-auto space-y-2">
      {activeProcessing.map((state) => (
        <ProcessingStatusCompact
          key={state.imageId}
          imageId={state.imageId}
          progress={state.progress}
          currentStep={state.currentStep}
          etaSeconds={state.etaSeconds}
        />
      ))}
    </div>
  );
};
