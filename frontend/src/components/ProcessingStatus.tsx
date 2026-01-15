import React, { useEffect, useState } from "react";

interface ProcessingStatusProps {
  imageId: string;
  progress: number;
  currentStep: string;
  etaSeconds: number | null;
  algorithm?: string;
  onCancel?: () => void;
  gpuUtilization?: number;
  className?: string;
}

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  progress,
  currentStep,
  etaSeconds,
  algorithm,
  onCancel,
  gpuUtilization,
  className = "",
}) => {
  const [displayProgress, setDisplayProgress] = useState(progress);
  const [isAnimating, setIsAnimating] = useState(false);

  // Smooth progress animation
  useEffect(() => {
    if (progress !== displayProgress) {
      setIsAnimating(true);
      const timer = setTimeout(() => {
        setDisplayProgress(progress);
        setIsAnimating(false);
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [progress, displayProgress]);

  const formatETA = (seconds: number | null): string => {
    if (seconds === null || seconds <= 0) return "Completing...";

    if (seconds < 60) {
      return `${Math.ceil(seconds)}s remaining`;
    }

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.ceil(seconds % 60);
    return `${minutes}m ${remainingSeconds}s remaining`;
  };

  const getProgressColor = (): string => {
    if (progress >= 90) return "bg-green-500";
    if (progress >= 60) return "bg-blue-500";
    if (progress >= 30) return "bg-yellow-500";
    return "bg-orange-500";
  };

  const getGpuColor = (utilization: number): string => {
    if (utilization >= 80) return "text-red-500";
    if (utilization >= 60) return "text-yellow-500";
    return "text-green-500";
  };

  return (
    <div
      className={`bg-white rounded-lg shadow-lg border border-gray-200 p-6 ${className}`}
      role="status"
      aria-live="polite"
      aria-label={`Processing ${progress.toFixed(1)}% complete`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2">
              {/* Animated processing indicator */}
              <div className="relative w-4 h-4">
                <div className="absolute inset-0 animate-ping bg-blue-400 rounded-full opacity-75"></div>
                <div className="relative bg-blue-500 rounded-full w-4 h-4"></div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900">
                Processing Analysis
              </h3>
            </div>
          </div>
          {algorithm && (
            <p className="text-sm text-gray-600 mt-1">Algorithm: {algorithm}</p>
          )}
        </div>

        {onCancel && (
          <button
            onClick={onCancel}
            className="ml-4 px-3 py-1 text-sm font-medium text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors"
            aria-label="Cancel processing"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-2xl font-bold text-gray-900">
            {displayProgress.toFixed(1)}%
          </span>
          <span className="text-sm text-gray-600">{formatETA(etaSeconds)}</span>
        </div>

        <div className="relative w-full h-3 bg-gray-200 rounded-full overflow-hidden">
          {/* Background stripes for animation effect */}
          <div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-20 animate-shimmer"
            style={{
              backgroundSize: "200% 100%",
            }}
          ></div>

          {/* Actual progress bar */}
          <div
            className={`h-full ${getProgressColor()} transition-all duration-300 ease-out rounded-full relative overflow-hidden ${
              isAnimating ? "animate-pulse" : ""
            }`}
            style={{ width: `${displayProgress}%` }}
            role="progressbar"
            aria-valuenow={displayProgress}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            {/* Animated shine effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-slide"></div>
          </div>
        </div>
      </div>

      {/* Current Step */}
      <div className="mb-4">
        <div className="flex items-center gap-2">
          <svg
            className="w-4 h-4 text-blue-500 animate-spin"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <p className="text-sm font-medium text-gray-700">{currentStep}</p>
        </div>
      </div>

      {/* GPU Utilization */}
      {gpuUtilization !== undefined && (
        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
          <div className="flex items-center gap-2">
            <svg
              className="w-5 h-5 text-gray-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
              />
            </svg>
            <span className="text-sm font-medium text-gray-700">
              GPU Utilization:
            </span>
          </div>
          <span
            className={`text-sm font-bold ${getGpuColor(gpuUtilization)}`}
          >
            {gpuUtilization.toFixed(1)}%
          </span>
        </div>
      )}

      {/* Processing Animation */}
      <div className="mt-4 flex items-center justify-center gap-1">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
            style={{
              animationDelay: `${i * 0.15}s`,
              animationDuration: "0.6s",
            }}
          ></div>
        ))}
      </div>
    </div>
  );
};

// Compact version for dashboard/list view
export const ProcessingStatusCompact: React.FC<ProcessingStatusProps> = ({
  progress,
  currentStep,
  etaSeconds,
}) => {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
          <span className="text-sm font-medium text-gray-900">
            {progress.toFixed(0)}%
          </span>
        </div>
        <span className="text-xs text-gray-600">
          {etaSeconds !== null && etaSeconds > 0
            ? `${Math.ceil(etaSeconds)}s`
            : "Finishing..."}
        </span>
      </div>

      <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-500 transition-all duration-300 rounded-full"
          style={{ width: `${progress}%` }}
        ></div>
      </div>

      <p className="text-xs text-gray-600 mt-2 truncate">{currentStep}</p>
    </div>
  );
};

// Add custom animations to your Tailwind config or use inline styles
// Add to tailwind.config.js:
/*
extend: {
  animation: {
    shimmer: 'shimmer 2s linear infinite',
    slide: 'slide 1s linear infinite',
  },
  keyframes: {
    shimmer: {
      '0%': { backgroundPosition: '-200% 0' },
      '100%': { backgroundPosition: '200% 0' },
    },
    slide: {
      '0%': { transform: 'translateX(-100%)' },
      '100%': { transform: 'translateX(100%)' },
    },
  },
}
*/
