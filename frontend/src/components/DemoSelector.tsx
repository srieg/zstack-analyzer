/**
 * Demo Dataset Selector Component
 * Beautiful card grid for exploring and loading demo datasets
 */

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Beaker,
  Sparkles,
  Brain,
  Dna,
  Microscope,
  Clock,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Loader2,
  Play,
  Info
} from 'lucide-react';

interface DemoDataset {
  id: string;
  name: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  categories: string[];
  shape: number[];
  channels: number;
  channel_names: string[];
  snr: 'low' | 'medium' | 'high';
  expected_results: Record<string, string>;
  showcase_features: string[];
  timepoints?: number;
}

interface DemoSelectorProps {
  onLoad: (dataset: DemoDataset) => void;
  className?: string;
}

const difficultyColors = {
  beginner: 'from-green-500 to-emerald-600',
  intermediate: 'from-blue-500 to-cyan-600',
  advanced: 'from-orange-500 to-amber-600',
  expert: 'from-red-500 to-rose-600'
};

const difficultyIcons = {
  beginner: CheckCircle,
  intermediate: TrendingUp,
  advanced: Brain,
  expert: Sparkles
};

const categoryIcons: Record<string, React.ElementType> = {
  'nuclei': Dna,
  'filaments': TrendingUp,
  'puncta': Sparkles,
  'neurons': Brain,
  'colocalization': Beaker,
  '4d': Clock,
  'time-series': Clock,
  'neuroscience': Brain,
  'cell-biology': Microscope
};

export const DemoSelector: React.FC<DemoSelectorProps> = ({ onLoad, className = '' }) => {
  const [datasets, setDatasets] = useState<DemoDataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingDataset, setLoadingDataset] = useState<string | null>(null);
  const [selectedDataset, setSelectedDataset] = useState<DemoDataset | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      const response = await fetch('/api/v1/demo/datasets');
      if (!response.ok) throw new Error('Failed to fetch demo datasets');
      const data = await response.json();
      setDatasets(data);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load datasets');
      setLoading(false);
    }
  };

  const handleLoadDataset = async (dataset: DemoDataset) => {
    setLoadingDataset(dataset.id);
    try {
      const response = await fetch(`/api/v1/demo/datasets/${dataset.id}/load`, {
        method: 'POST'
      });
      if (!response.ok) throw new Error('Failed to load dataset');
      const result = await response.json();
      onLoad({ ...dataset, ...result });
      setLoadingDataset(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dataset');
      setLoadingDataset(null);
    }
  };

  const getVolumeSize = (shape: number[]): string => {
    const voxels = shape.reduce((a, b) => a * b, 1);
    const mb = (voxels * 2) / (1024 * 1024); // 16-bit data
    return mb > 1024 ? `${(mb / 1024).toFixed(1)} GB` : `${mb.toFixed(1)} MB`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-red-500">
        <AlertCircle className="w-6 h-6 mr-2" />
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div className={`demo-selector ${className}`}>
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
          Explore Demo Datasets
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Try our synthetic datasets to explore the platform's capabilities
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AnimatePresence>
          {datasets.map((dataset, index) => {
            const DifficultyIcon = difficultyIcons[dataset.difficulty];
            const CategoryIcon = categoryIcons[dataset.categories[0]] || Microscope;
            const isLoading = loadingDataset === dataset.id;

            return (
              <motion.div
                key={dataset.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className="group relative"
              >
                <div className="relative bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden border border-gray-200 dark:border-gray-700">
                  {/* Gradient header */}
                  <div className={`h-32 bg-gradient-to-br ${difficultyColors[dataset.difficulty]} relative overflow-hidden`}>
                    <div className="absolute inset-0 opacity-20">
                      <CategoryIcon className="w-64 h-64 -rotate-12 transform translate-x-1/4 -translate-y-1/4" />
                    </div>
                    <div className="absolute bottom-4 left-4 right-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <CategoryIcon className="w-6 h-6 text-white" />
                          <span className="text-white font-semibold capitalize">
                            {dataset.difficulty}
                          </span>
                        </div>
                        <DifficultyIcon className="w-5 h-5 text-white" />
                      </div>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-6">
                    <h3 className="text-xl font-bold mb-2 text-gray-900 dark:text-white">
                      {dataset.name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-3">
                      {dataset.description}
                    </p>

                    {/* Stats */}
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                        <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                          Dimensions
                        </div>
                        <div className="text-sm font-semibold text-gray-900 dark:text-white">
                          {dataset.shape[2]}×{dataset.shape[1]}×{dataset.shape[0]}
                        </div>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                        <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                          Channels
                        </div>
                        <div className="text-sm font-semibold text-gray-900 dark:text-white">
                          {dataset.channels}
                        </div>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                        <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                          Volume
                        </div>
                        <div className="text-sm font-semibold text-gray-900 dark:text-white">
                          {getVolumeSize(dataset.shape)}
                        </div>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                        <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                          SNR
                        </div>
                        <div className="text-sm font-semibold text-gray-900 dark:text-white capitalize">
                          {dataset.snr}
                        </div>
                      </div>
                    </div>

                    {/* Categories */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      {dataset.categories.slice(0, 3).map((category) => (
                        <span
                          key={category}
                          className="px-2 py-1 text-xs rounded-full bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300"
                        >
                          {category}
                        </span>
                      ))}
                      {dataset.categories.length > 3 && (
                        <span className="px-2 py-1 text-xs rounded-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                          +{dataset.categories.length - 3}
                        </span>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => setSelectedDataset(dataset)}
                        className="flex-1 py-2 px-4 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center justify-center gap-2"
                      >
                        <Info className="w-4 h-4" />
                        <span>Details</span>
                      </button>
                      <button
                        onClick={() => handleLoadDataset(dataset)}
                        disabled={isLoading}
                        className={`flex-1 py-2 px-4 rounded-lg bg-gradient-to-r ${difficultyColors[dataset.difficulty]} text-white font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2`}
                      >
                        {isLoading ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span>Loading...</span>
                          </>
                        ) : (
                          <>
                            <Play className="w-4 h-4" />
                            <span>Load</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Dataset Details Modal */}
      <AnimatePresence>
        {selectedDataset && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedDataset(null)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                      {selectedDataset.name}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      {selectedDataset.description}
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedDataset(null)}
                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                  >
                    ×
                  </button>
                </div>

                <div className="space-y-6">
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                      Expected Results
                    </h4>
                    <div className="space-y-2">
                      {Object.entries(selectedDataset.expected_results).map(([key, value]) => (
                        <div key={key} className="flex justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
                          <span className="text-gray-600 dark:text-gray-400 capitalize">
                            {key.replace(/_/g, ' ')}
                          </span>
                          <span className="font-semibold text-gray-900 dark:text-white">
                            {value}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                      Showcase Features
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedDataset.showcase_features.map((feature) => (
                        <span
                          key={feature}
                          className="px-3 py-1 text-sm rounded-full bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300"
                        >
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                      Channel Configuration
                    </h4>
                    <div className="space-y-2">
                      {selectedDataset.channel_names.map((name, idx) => (
                        <div key={idx} className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-700 rounded">
                          <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${idx === 0 ? 'from-green-400 to-green-600' : 'from-red-400 to-red-600'}`} />
                          <span className="text-gray-900 dark:text-white">Channel {idx + 1}: {name}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      handleLoadDataset(selectedDataset);
                      setSelectedDataset(null);
                    }}
                    className="w-full py-3 px-6 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold hover:shadow-lg transition-all"
                  >
                    Load This Dataset
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
