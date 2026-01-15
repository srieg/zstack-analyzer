/**
 * Demo Page
 * Guided tour of demo datasets with step-by-step walkthrough
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowRight,
  ArrowLeft,
  Sparkles,
  CheckCircle,
  Play,
  Info,
  Download,
  Eye,
  BarChart3,
  Layers
} from 'lucide-react';
import { DemoSelector } from '../components/DemoSelector';

interface TourStep {
  title: string;
  description: string;
  icon: React.ElementType;
  action?: string;
  highlight?: string;
}

const tourSteps: TourStep[] = [
  {
    title: 'Welcome to Demo Mode',
    description: 'Explore synthetic datasets that showcase the platform\'s capabilities. Each dataset is carefully designed to demonstrate specific features.',
    icon: Sparkles,
    action: 'Choose a dataset to begin'
  },
  {
    title: 'Load Demo Data',
    description: 'Select a dataset from the gallery. Each card shows key metrics like dimensions, channels, and expected analysis results.',
    icon: Download,
    highlight: 'demo-selector'
  },
  {
    title: 'View 3D Volume',
    description: 'Once loaded, explore the dataset in our GPU-accelerated 3D viewer. Rotate, zoom, and slice through the Z-stack.',
    icon: Eye,
    action: 'Navigate to Viewer'
  },
  {
    title: 'Run Analysis',
    description: 'Apply segmentation, denoising, and quantitative analysis. See real-time processing powered by TinyGrad.',
    icon: BarChart3,
    action: 'Try Analysis Tools'
  },
  {
    title: 'Compare Results',
    description: 'View side-by-side comparisons, statistics, and export results. Each demo includes expected outcomes for validation.',
    icon: Layers,
    action: 'View Results'
  }
];

export const Demo: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [showTour, setShowTour] = useState(true);
  const [loadedDataset, setLoadedDataset] = useState<any>(null);
  const [demoMode, setDemoMode] = useState(true);

  const handleDatasetLoad = (dataset: any) => {
    setLoadedDataset(dataset);
    setCurrentStep(2); // Move to viewer step
  };

  const nextStep = () => {
    if (currentStep < tourSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const CurrentIcon = tourSteps[currentStep].icon;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Demo Mode Banner */}
      <AnimatePresence>
        {demoMode && (
          <motion.div
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            exit={{ y: -100 }}
            className="sticky top-0 z-50 bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg"
          >
            <div className="container mx-auto px-6 py-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Sparkles className="w-5 h-5 animate-pulse" />
                <span className="font-semibold">
                  Demo Mode Active - Using Synthetic Data
                </span>
              </div>
              <button
                onClick={() => setDemoMode(false)}
                className="px-4 py-1 rounded-full bg-white/20 hover:bg-white/30 transition-colors text-sm"
              >
                Exit Demo
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="container mx-auto px-6 py-12">
        {/* Guided Tour */}
        <AnimatePresence mode="wait">
          {showTour && (
            <motion.div
              key="tour"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mb-12"
            >
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 max-w-4xl mx-auto">
                {/* Progress Bar */}
                <div className="mb-8">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                      Step {currentStep + 1} of {tourSteps.length}
                    </span>
                    <button
                      onClick={() => setShowTour(false)}
                      className="text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                    >
                      Skip Tour
                    </button>
                  </div>
                  <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-blue-500 to-purple-600"
                      initial={{ width: 0 }}
                      animate={{ width: `${((currentStep + 1) / tourSteps.length) * 100}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                </div>

                {/* Step Content */}
                <motion.div
                  key={currentStep}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="mb-8"
                >
                  <div className="flex items-start gap-6">
                    <div className="flex-shrink-0">
                      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                        <CurrentIcon className="w-8 h-8 text-white" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                        {tourSteps[currentStep].title}
                      </h2>
                      <p className="text-lg text-gray-600 dark:text-gray-400 mb-6">
                        {tourSteps[currentStep].description}
                      </p>
                      {tourSteps[currentStep].action && (
                        <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 font-semibold">
                          <Play className="w-5 h-5" />
                          <span>{tourSteps[currentStep].action}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>

                {/* Navigation */}
                <div className="flex items-center justify-between">
                  <button
                    onClick={prevStep}
                    disabled={currentStep === 0}
                    className="flex items-center gap-2 px-6 py-3 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <ArrowLeft className="w-4 h-4" />
                    <span>Previous</span>
                  </button>

                  <div className="flex gap-2">
                    {tourSteps.map((_, idx) => (
                      <button
                        key={idx}
                        onClick={() => setCurrentStep(idx)}
                        className={`w-3 h-3 rounded-full transition-all ${
                          idx === currentStep
                            ? 'bg-blue-600 w-8'
                            : idx < currentStep
                            ? 'bg-blue-300'
                            : 'bg-gray-300 dark:bg-gray-600'
                        }`}
                      />
                    ))}
                  </div>

                  <button
                    onClick={nextStep}
                    disabled={currentStep === tourSteps.length - 1}
                    className="flex items-center gap-2 px-6 py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    <span>Next</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Dataset Selector */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <DemoSelector onLoad={handleDatasetLoad} />
        </motion.div>

        {/* Loaded Dataset Info */}
        <AnimatePresence>
          {loadedDataset && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-12 bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 max-w-4xl mx-auto"
            >
              <div className="flex items-center gap-4 mb-6">
                <CheckCircle className="w-12 h-12 text-green-500" />
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Dataset Loaded Successfully!
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    {loadedDataset.name}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                    Data Shape
                  </div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {loadedDataset.data_shape?.join(' × ')}
                  </div>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                    Data Type
                  </div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {loadedDataset.data_type}
                  </div>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                    Channels
                  </div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {loadedDataset.channels}
                  </div>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                    Cached
                  </div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {loadedDataset.cached ? 'Yes' : 'No'}
                  </div>
                </div>
              </div>

              <div className="flex gap-4">
                <button
                  onClick={() => window.location.href = `/viewer/${loadedDataset.image_stack.id}`}
                  className="flex-1 py-3 px-6 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold hover:shadow-lg transition-all flex items-center justify-center gap-2"
                >
                  <Eye className="w-5 h-5" />
                  <span>View in 3D</span>
                </button>
                <button
                  onClick={() => window.location.href = `/analysis/${loadedDataset.image_stack.id}`}
                  className="flex-1 py-3 px-6 rounded-lg border-2 border-blue-500 text-blue-600 dark:text-blue-400 font-semibold hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all flex items-center justify-center gap-2"
                >
                  <BarChart3 className="w-5 h-5" />
                  <span>Run Analysis</span>
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Features Showcase */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-12 grid md:grid-cols-3 gap-6"
        >
          {[
            {
              icon: Sparkles,
              title: 'Realistic Synthetic Data',
              description: 'Biologically accurate structures with controlled noise and artifacts'
            },
            {
              icon: CheckCircle,
              title: 'Validated Results',
              description: 'Each dataset includes expected outcomes for result verification'
            },
            {
              icon: Info,
              title: 'Educational',
              description: 'Learn analysis techniques with well-documented examples'
            }
          ].map((feature, idx) => (
            <div
              key={idx}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
            >
              <feature.icon className="w-10 h-10 text-blue-500 mb-4" />
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                {feature.description}
              </p>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
};
