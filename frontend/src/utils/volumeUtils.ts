/**
 * Utility functions for volume data processing and visualization
 */

import * as THREE from 'three';
import type { ColorMap, VolumeData } from '../types/volume';

/**
 * Create a THREE.js Data3DTexture from volume data
 */
export function createVolumeTexture(
  data: Float32Array,
  dimensions: [number, number, number]
): THREE.Data3DTexture {
  const [width, height, depth] = dimensions;

  // Normalize data to 0-255 range
  const normalizedData = new Uint8Array(data.length);
  let min = Infinity;
  let max = -Infinity;

  for (let i = 0; i < data.length; i++) {
    if (data[i] < min) min = data[i];
    if (data[i] > max) max = data[i];
  }

  const range = max - min;
  for (let i = 0; i < data.length; i++) {
    normalizedData[i] = Math.floor(((data[i] - min) / range) * 255);
  }

  const texture = new THREE.Data3DTexture(normalizedData, width, height, depth);
  texture.format = THREE.RedFormat;
  texture.type = THREE.UnsignedByteType;
  texture.minFilter = THREE.LinearFilter;
  texture.magFilter = THREE.LinearFilter;
  texture.unpackAlignment = 1;
  texture.needsUpdate = true;

  return texture;
}

/**
 * Calculate volume statistics
 */
export function calculateVolumeStats(data: Float32Array) {
  let min = Infinity;
  let max = -Infinity;
  let sum = 0;

  for (let i = 0; i < data.length; i++) {
    const value = data[i];
    if (value < min) min = value;
    if (value > max) max = value;
    sum += value;
  }

  const mean = sum / data.length;

  // Calculate standard deviation
  let sumSquaredDiff = 0;
  for (let i = 0; i < data.length; i++) {
    const diff = data[i] - mean;
    sumSquaredDiff += diff * diff;
  }
  const stdDev = Math.sqrt(sumSquaredDiff / data.length);

  return { min, max, mean, stdDev };
}

/**
 * Generate histogram data for the volume
 */
export function generateHistogram(
  data: Float32Array,
  bins: number = 256
): { bins: number[]; min: number; max: number } {
  const stats = calculateVolumeStats(data);
  const histogram = new Array(bins).fill(0);
  const binSize = (stats.max - stats.min) / bins;

  for (let i = 0; i < data.length; i++) {
    const binIndex = Math.min(
      Math.floor((data[i] - stats.min) / binSize),
      bins - 1
    );
    histogram[binIndex]++;
  }

  return {
    bins: histogram,
    min: stats.min,
    max: stats.max,
  };
}

/**
 * Convert color map name to shader uniform value
 */
export function colorMapToUniform(colorMap: ColorMap): number {
  const map: Record<ColorMap, number> = {
    grayscale: 0,
    hot: 1,
    cool: 2,
    viridis: 3,
    plasma: 4,
    turbo: 5,
    magma: 4, // Use plasma as fallback
  };
  return map[colorMap] ?? 0;
}

/**
 * Calculate distance between two 3D points
 */
export function calculateDistance(
  point1: [number, number, number],
  point2: [number, number, number],
  spacing: [number, number, number] = [1, 1, 1]
): number {
  const dx = (point2[0] - point1[0]) * spacing[0];
  const dy = (point2[1] - point1[1]) * spacing[1];
  const dz = (point2[2] - point1[2]) * spacing[2];

  return Math.sqrt(dx * dx + dy * dy + dz * dz);
}

/**
 * Convert normalized coordinates to voxel coordinates
 */
export function normalizedToVoxel(
  normalized: [number, number, number],
  dimensions: [number, number, number]
): [number, number, number] {
  return [
    Math.floor(normalized[0] * dimensions[0]),
    Math.floor(normalized[1] * dimensions[1]),
    Math.floor(normalized[2] * dimensions[2]),
  ];
}

/**
 * Convert voxel coordinates to world coordinates
 */
export function voxelToWorld(
  voxel: [number, number, number],
  dimensions: [number, number, number],
  spacing: [number, number, number] = [1, 1, 1]
): [number, number, number] {
  const center = [dimensions[0] / 2, dimensions[1] / 2, dimensions[2] / 2];
  return [
    (voxel[0] - center[0]) * spacing[0],
    (voxel[1] - center[1]) * spacing[1],
    (voxel[2] - center[2]) * spacing[2],
  ];
}

/**
 * Create a formatted size string for display
 */
export function formatVolumeSize(dimensions: [number, number, number]): string {
  return `${dimensions[0]} × ${dimensions[1]} × ${dimensions[2]}`;
}

/**
 * Calculate optimal step size for ray marching based on volume dimensions
 */
export function calculateOptimalStepSize(
  dimensions: [number, number, number]
): number {
  const maxDim = Math.max(...dimensions);
  return 2.0 / (maxDim * 2); // Half voxel sampling
}

/**
 * Generate sample volume data for testing
 */
export function generateSampleVolume(
  width: number = 64,
  height: number = 64,
  depth: number = 64
): VolumeData {
  const size = width * height * depth;
  const data = new Float32Array(size);

  // Create a sphere in the center
  const centerX = width / 2;
  const centerY = height / 2;
  const centerZ = depth / 2;
  const radius = Math.min(width, height, depth) / 3;

  for (let z = 0; z < depth; z++) {
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const dx = x - centerX;
        const dy = y - centerY;
        const dz = z - centerZ;
        const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);

        const index = z * width * height + y * width + x;

        if (distance < radius) {
          // Gradient from center
          const intensity = 1.0 - distance / radius;
          data[index] = intensity * 0.8 + Math.random() * 0.2;
        } else {
          data[index] = Math.random() * 0.1;
        }
      }
    }
  }

  return {
    data,
    dimensions: [width, height, depth],
    channels: 1,
    spacing: [1, 1, 1],
    metadata: {
      name: 'Sample Volume',
      timestamp: new Date().toISOString(),
    },
  };
}

/**
 * Take a screenshot of a canvas and download it
 */
export function downloadCanvasScreenshot(
  canvas: HTMLCanvasElement,
  filename: string = 'volume-screenshot.png',
  scale: number = 2
): void {
  // Create a higher resolution canvas
  const tempCanvas = document.createElement('canvas');
  const width = canvas.width * scale;
  const height = canvas.height * scale;
  tempCanvas.width = width;
  tempCanvas.height = height;

  const ctx = tempCanvas.getContext('2d');
  if (!ctx) return;

  ctx.drawImage(canvas, 0, 0, width, height);

  tempCanvas.toBlob((blob) => {
    if (!blob) return;

    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.download = filename;
    link.href = url;
    link.click();

    URL.revokeObjectURL(url);
  }, 'image/png');
}
