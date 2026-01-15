/**
 * Demo Mode Banner Component
 * Shows when user is viewing demo/synthetic data
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, X, ArrowRight } from 'lucide-react';

interface DemoBannerProps {
  onExitDemo?: () => void;
  onViewRealData?: () => void;
  datasetName?: string;
  className?: string;
}

export const DemoBanner: React.FC<DemoBannerProps> = ({
  onExitDemo,
  onViewRealData,
  datasetName,
  className = ''
}) => {
  return (
    <motion.div
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      exit={{ y: -100, opacity: 0 }}
      className={`sticky top-0 z-50 ${className}`}
    >
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white shadow-lg">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between py-3">
            {/* Left side - Status */}
            <div className="flex items-center gap-3">
              <motion.div
                animate={{
                  scale: [1, 1.2, 1],
                  rotate: [0, 360]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <Sparkles className="w-5 h-5" />
              </motion.div>
              <div className="flex flex-col">
                <span className="font-semibold text-sm">
                  Demo Mode Active
                </span>
                {datasetName && (
                  <span className="text-xs opacity-90">
                    Using: {datasetName}
                  </span>
                )}
              </div>
            </div>

            {/* Center - Message */}
            <div className="hidden md:flex items-center gap-2 text-sm">
              <span className="opacity-90">
                You're viewing synthetic data for demonstration
              </span>
            </div>

            {/* Right side - Actions */}
            <div className="flex items-center gap-3">
              {onViewRealData && (
                <button
                  onClick={onViewRealData}
                  className="px-4 py-1.5 rounded-full bg-white/20 hover:bg-white/30 transition-colors text-sm font-medium flex items-center gap-2"
                >
                  <span>Upload Real Data</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              )}
              {onExitDemo && (
                <button
                  onClick={onExitDemo}
                  className="p-1.5 rounded-full hover:bg-white/20 transition-colors"
                  aria-label="Exit demo mode"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Info bar */}
      <div className="bg-blue-50 dark:bg-gray-800 border-b border-blue-200 dark:border-gray-700">
        <div className="container mx-auto px-6 py-2">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-6 text-gray-700 dark:text-gray-300">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                <span>Synthetic data generation active</span>
              </div>
              <span className="text-gray-400 dark:text-gray-500">•</span>
              <span>Results validated against expected outcomes</span>
            </div>
            <a
              href="/demo"
              className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
            >
              Browse all demo datasets →
            </a>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

/**
 * Compact Demo Indicator
 * Smaller version for use in corners or sidebars
 */
export const DemoIndicator: React.FC<{
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  onClick?: () => void;
}> = ({ position = 'top-right', onClick }) => {
  const positionClasses = {
    'top-left': 'top-4 left-4',
    'top-right': 'top-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'bottom-right': 'bottom-4 right-4'
  };

  return (
    <motion.div
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0, opacity: 0 }}
      className={`fixed ${positionClasses[position]} z-40`}
    >
      <button
        onClick={onClick}
        className="group flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg hover:shadow-xl transition-all"
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <Sparkles className="w-4 h-4" />
        </motion.div>
        <span className="text-sm font-semibold">Demo</span>
        <div className="w-2 h-2 rounded-full bg-white animate-pulse" />
      </button>
    </motion.div>
  );
};

/**
 * Demo Comparison Widget
 * Shows comparison between demo and real data options
 */
export const DemoComparisonWidget: React.FC<{
  onChooseDemo: () => void;
  onChooseReal: () => void;
}> = ({ onChooseDemo, onChooseReal }) => {
  return (
    <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
      {/* Demo Option */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={onChooseDemo}
        className="relative p-8 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 text-white text-left overflow-hidden group"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-white/0 to-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
        <div className="relative z-10">
          <Sparkles className="w-12 h-12 mb-4" />
          <h3 className="text-2xl font-bold mb-2">Try Demo Data</h3>
          <p className="text-white/90 mb-4">
            Explore with synthetic datasets. Perfect for learning and testing features.
          </p>
          <div className="flex items-center gap-2 text-sm font-semibold">
            <span>Start Demo</span>
            <ArrowRight className="w-4 h-4" />
          </div>
        </div>
      </motion.button>

      {/* Real Data Option */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={onChooseReal}
        className="relative p-8 rounded-2xl bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 text-left overflow-hidden group hover:border-blue-500 transition-colors"
      >
        <div className="relative z-10">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mb-4">
            <ArrowRight className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Upload Your Data
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Analyze your own microscopy data with full pipeline capabilities.
          </p>
          <div className="flex items-center gap-2 text-sm font-semibold text-blue-600 dark:text-blue-400">
            <span>Upload Files</span>
            <ArrowRight className="w-4 h-4" />
          </div>
        </div>
      </motion.button>
    </div>
  );
};
