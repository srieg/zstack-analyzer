/**
 * VolumeViewer Integration Example
 * Shows how to integrate the volume viewer with API data loading
 */

import React, { useEffect, useState } from 'react';
import { VolumeViewer } from './VolumeViewer';
import type { VolumeData, RenderMode, ColorMap } from '../types/volume';

interface VolumeViewerIntegrationProps {
  stackId: string;
  apiEndpoint?: string;
  defaultRenderMode?: RenderMode;
  defaultColorMap?: ColorMap;
}

export const VolumeViewerIntegration: React.FC<
  VolumeViewerIntegrationProps
> = ({
  stackId,
  apiEndpoint = '/api/stacks',
  defaultRenderMode = 'volume',
  defaultColorMap = 'viridis',
}) => {
  const [volumeData, setVolumeData] = useState<VolumeData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [measurements, setMeasurements] = useState<
    Array<{ distance: number; points: [number, number, number][] }>
  >([]);

  useEffect(() => {
    loadVolumeData();
  }, [stackId]);

  const loadVolumeData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Fetch volume metadata
      const metadataResponse = await fetch(
        `${apiEndpoint}/${stackId}/metadata`
      );
      if (!metadataResponse.ok) {
        throw new Error('Failed to fetch metadata');
      }
      const metadata = await metadataResponse.json();

      // Fetch volume data
      const dataResponse = await fetch(`${apiEndpoint}/${stackId}/volume`);
      if (!dataResponse.ok) {
        throw new Error('Failed to fetch volume data');
      }

      const arrayBuffer = await dataResponse.arrayBuffer();
      const data = new Float32Array(arrayBuffer);

      setVolumeData({
        data,
        dimensions: metadata.dimensions,
        channels: metadata.channels || 1,
        spacing: metadata.spacing || [1, 1, 1],
        metadata: {
          name: metadata.name,
          timestamp: metadata.timestamp,
          pixelSize: metadata.pixelSize,
          acquisitionParams: metadata.acquisitionParams,
        },
      });

      setIsLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setIsLoading(false);
    }
  };

  const handleSliceChange = (
    axis: 'x' | 'y' | 'z',
    position: number
  ): void => {
    console.log(`Slice ${axis.toUpperCase()} changed to ${position.toFixed(3)}`);
    // You can add analytics or state updates here
  };

  const handleMeasurement = (
    distance: number,
    points: [number, number, number][]
  ): void => {
    setMeasurements((prev) => [...prev, { distance, points }]);
    console.log(`New measurement: ${distance.toFixed(2)} µm`);
  };

  if (error) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-gradient-to-br from-red-900 to-gray-900">
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-8 shadow-2xl border border-white/20 max-w-md">
          <div className="text-red-400 text-6xl mb-4 text-center">⚠️</div>
          <h2 className="text-white text-2xl font-bold text-center mb-2">
            Failed to Load Volume
          </h2>
          <p className="text-white/70 text-center mb-4">{error}</p>
          <button
            onClick={loadVolumeData}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (isLoading || !volumeData) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
        <div className="text-center">
          <div className="animate-pulse mb-4">
            <div className="w-20 h-20 bg-blue-500/20 rounded-2xl mx-auto mb-4 flex items-center justify-center">
              <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          </div>
          <h2 className="text-white text-2xl font-bold mb-2">
            Loading Volume Data
          </h2>
          <p className="text-white/70">Stack ID: {stackId}</p>
          <div className="mt-4 flex items-center justify-center space-x-2">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
            <div
              className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"
              style={{ animationDelay: '0.1s' }}
            ></div>
            <div
              className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"
              style={{ animationDelay: '0.2s' }}
            ></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-screen">
      <VolumeViewer
        data={volumeData.data}
        dimensions={volumeData.dimensions}
        channels={volumeData.channels}
        spacing={volumeData.spacing}
        colorMaps={[defaultColorMap]}
        renderMode={defaultRenderMode}
        onSliceChange={handleSliceChange}
        onMeasurement={handleMeasurement}
        showAxes={true}
        showScaleBar={true}
        className="w-full h-full"
      />

      {/* Measurements Panel */}
      {measurements.length > 0 && (
        <div className="absolute top-4 right-4 bg-white/10 backdrop-blur-xl rounded-xl p-4 shadow-2xl border border-white/20 max-w-xs z-20">
          <h4 className="text-white font-bold text-sm mb-3 flex items-center justify-between">
            <span>Measurements</span>
            <button
              onClick={() => setMeasurements([])}
              className="text-xs text-white/60 hover:text-white"
            >
              Clear
            </button>
          </h4>
          <ul className="space-y-2 max-h-48 overflow-y-auto">
            {measurements.map((m, i) => (
              <li
                key={i}
                className="text-white/80 text-xs bg-white/5 rounded p-2"
              >
                <span className="font-medium">{m.distance.toFixed(2)} µm</span>
                <div className="text-white/50 text-[10px] mt-1">
                  {m.points.length} points
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Metadata Panel */}
      {volumeData.metadata && (
        <div className="absolute bottom-4 right-4 bg-white/10 backdrop-blur-xl rounded-xl p-4 shadow-2xl border border-white/20 max-w-xs z-10">
          <h4 className="text-white font-bold text-sm mb-3">
            Volume Information
          </h4>
          <dl className="space-y-2 text-xs">
            {volumeData.metadata.name && (
              <>
                <dt className="text-white/60">Name</dt>
                <dd className="text-white font-medium">
                  {volumeData.metadata.name}
                </dd>
              </>
            )}
            <dt className="text-white/60">Dimensions</dt>
            <dd className="text-white font-mono">
              {volumeData.dimensions.join(' × ')} voxels
            </dd>
            {volumeData.spacing && (
              <>
                <dt className="text-white/60">Spacing</dt>
                <dd className="text-white font-mono">
                  {volumeData.spacing
                    .map((s) => s.toFixed(3))
                    .join(' × ')}{' '}
                  µm
                </dd>
              </>
            )}
            {volumeData.metadata.timestamp && (
              <>
                <dt className="text-white/60">Acquired</dt>
                <dd className="text-white">
                  {new Date(volumeData.metadata.timestamp).toLocaleString()}
                </dd>
              </>
            )}
          </dl>
        </div>
      )}
    </div>
  );
};

export default VolumeViewerIntegration;
