/**
 * VolumeViewer Demo Page
 * Demonstrates the 3D volume rendering capabilities
 */

import React, { useEffect, useState } from 'react';
import { VolumeViewer } from '../components/VolumeViewer';
import { generateSampleVolume } from '../utils/volumeUtils';
import type { VolumeData } from '../types/volume';

export const VolumeViewerDemo: React.FC = () => {
  const [volumeData, setVolumeData] = useState<VolumeData | null>(null);
  const [isGenerating, setIsGenerating] = useState(true);

  useEffect(() => {
    // Generate sample volume data
    const timer = setTimeout(() => {
      const sample = generateSampleVolume(128, 128, 128);
      setVolumeData(sample);
      setIsGenerating(false);
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  if (isGenerating || !volumeData) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-20 w-20 border-t-2 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white text-xl font-bold">
            Generating Sample Volume...
          </p>
          <p className="text-white/70 text-sm mt-2">
            Creating 128³ voxel dataset
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-20 p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold text-white mb-2">
            Z-Stack Volume Renderer
          </h1>
          <p className="text-white/70 text-lg">
            High-performance 3D visualization for microscopy data
          </p>
        </div>
      </div>

      {/* Volume Viewer */}
      <VolumeViewer
        data={volumeData.data}
        dimensions={volumeData.dimensions}
        channels={volumeData.channels}
        spacing={volumeData.spacing}
        colorMaps={['viridis', 'hot', 'plasma']}
        showAxes={true}
        showScaleBar={true}
        onSliceChange={(axis, position) => {
          console.log(`Slice ${axis} changed to position ${position}`);
        }}
        onMeasurement={(distance, points) => {
          console.log(`Measured distance: ${distance.toFixed(2)} µm`, points);
        }}
        className="w-full h-full"
      />

      {/* Info Panel */}
      <div className="absolute bottom-4 right-4 bg-white/10 backdrop-blur-xl rounded-xl p-4 shadow-2xl border border-white/20 max-w-xs z-10">
        <h4 className="text-white font-bold text-sm mb-3">
          Rendering Features
        </h4>
        <ul className="space-y-2 text-white/80 text-xs">
          <li className="flex items-center">
            <span className="mr-2">🎨</span>
            <span>Multiple color maps (Viridis, Hot, Plasma, etc.)</span>
          </li>
          <li className="flex items-center">
            <span className="mr-2">🔬</span>
            <span>MIP, Isosurface, Volume, Slice modes</span>
          </li>
          <li className="flex items-center">
            <span className="mr-2">⚡</span>
            <span>WebGL ray marching with early termination</span>
          </li>
          <li className="flex items-center">
            <span className="mr-2">🎮</span>
            <span>Interactive orbit controls & slicing</span>
          </li>
          <li className="flex items-center">
            <span className="mr-2">📸</span>
            <span>High-resolution screenshot export</span>
          </li>
          <li className="flex items-center">
            <span className="mr-2">✨</span>
            <span>Glass-morphism UI design</span>
          </li>
        </ul>
      </div>

      {/* Instructions */}
      <div className="absolute bottom-4 left-4 bg-white/10 backdrop-blur-xl rounded-xl p-4 shadow-2xl border border-white/20 max-w-xs z-10">
        <h4 className="text-white font-bold text-sm mb-3">Controls</h4>
        <ul className="space-y-1 text-white/80 text-xs">
          <li>
            <strong>Left Click + Drag:</strong> Rotate
          </li>
          <li>
            <strong>Right Click + Drag:</strong> Pan
          </li>
          <li>
            <strong>Scroll:</strong> Zoom
          </li>
          <li>
            <strong>Panel:</strong> Adjust rendering parameters
          </li>
        </ul>
      </div>
    </div>
  );
};

export default VolumeViewerDemo;
