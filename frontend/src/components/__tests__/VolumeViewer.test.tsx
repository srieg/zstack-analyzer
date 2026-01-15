/**
 * VolumeViewer Component Tests
 * Basic smoke tests and integration examples
 */

import { describe, it, expect } from 'vitest';
import { generateSampleVolume } from '../../utils/volumeUtils';
import {
  createVolumeTexture,
  calculateVolumeStats,
  colorMapToUniform,
  normalizedToVoxel,
  voxelToWorld,
} from '../../utils/volumeUtils';

describe('VolumeViewer Utilities', () => {
  describe('generateSampleVolume', () => {
    it('should generate volume data with correct dimensions', () => {
      const volume = generateSampleVolume(64, 64, 64);

      expect(volume.data).toBeInstanceOf(Float32Array);
      expect(volume.data.length).toBe(64 * 64 * 64);
      expect(volume.dimensions).toEqual([64, 64, 64]);
      expect(volume.channels).toBe(1);
    });

    it('should generate data in valid range [0, 1]', () => {
      const volume = generateSampleVolume(32, 32, 32);

      for (let i = 0; i < volume.data.length; i++) {
        expect(volume.data[i]).toBeGreaterThanOrEqual(0);
        expect(volume.data[i]).toBeLessThanOrEqual(1);
      }
    });
  });

  describe('calculateVolumeStats', () => {
    it('should calculate correct statistics', () => {
      const data = new Float32Array([0, 0.25, 0.5, 0.75, 1.0]);
      const stats = calculateVolumeStats(data);

      expect(stats.min).toBe(0);
      expect(stats.max).toBe(1.0);
      expect(stats.mean).toBe(0.5);
    });
  });

  describe('createVolumeTexture', () => {
    it('should create a THREE.Data3DTexture', () => {
      const data = new Float32Array(8 * 8 * 8);
      data.fill(0.5);

      const texture = createVolumeTexture(data, [8, 8, 8]);

      expect(texture).toBeDefined();
      expect(texture.image.width).toBe(8);
      expect(texture.image.height).toBe(8);
      expect(texture.image.depth).toBe(8);
    });
  });

  describe('colorMapToUniform', () => {
    it('should map color names to uniform values', () => {
      expect(colorMapToUniform('grayscale')).toBe(0);
      expect(colorMapToUniform('hot')).toBe(1);
      expect(colorMapToUniform('cool')).toBe(2);
      expect(colorMapToUniform('viridis')).toBe(3);
      expect(colorMapToUniform('plasma')).toBe(4);
      expect(colorMapToUniform('turbo')).toBe(5);
    });
  });

  describe('coordinate transformations', () => {
    it('should convert normalized to voxel coordinates', () => {
      const normalized: [number, number, number] = [0.5, 0.5, 0.5];
      const dimensions: [number, number, number] = [100, 100, 100];

      const voxel = normalizedToVoxel(normalized, dimensions);

      expect(voxel).toEqual([50, 50, 50]);
    });

    it('should convert voxel to world coordinates', () => {
      const voxel: [number, number, number] = [50, 50, 50];
      const dimensions: [number, number, number] = [100, 100, 100];
      const spacing: [number, number, number] = [1, 1, 1];

      const world = voxelToWorld(voxel, dimensions, spacing);

      expect(world).toEqual([0, 0, 0]);
    });

    it('should handle physical spacing in coordinate conversion', () => {
      const voxel: [number, number, number] = [60, 50, 50];
      const dimensions: [number, number, number] = [100, 100, 100];
      const spacing: [number, number, number] = [0.1, 0.1, 0.5];

      const world = voxelToWorld(voxel, dimensions, spacing);

      expect(world[0]).toBeCloseTo(1.0); // (60 - 50) * 0.1
      expect(world[1]).toBeCloseTo(0.0); // (50 - 50) * 0.1
      expect(world[2]).toBeCloseTo(0.0); // (50 - 50) * 0.5
    });
  });
});

describe('VolumeViewer Integration', () => {
  it('should have all required exports', () => {
    // This test verifies that all necessary modules are properly exported
    const { VolumeViewer } = require('../VolumeViewer');
    const { VolumeViewerIntegration } = require('../VolumeViewerIntegration');
    const volumeUtils = require('../../utils/volumeUtils');

    expect(VolumeViewer).toBeDefined();
    expect(VolumeViewerIntegration).toBeDefined();
    expect(volumeUtils.generateSampleVolume).toBeDefined();
    expect(volumeUtils.createVolumeTexture).toBeDefined();
  });
});

describe('Volume Data Format', () => {
  it('should maintain row-major order (x, y, z)', () => {
    const width = 4;
    const height = 4;
    const depth = 4;
    const data = new Float32Array(width * height * depth);

    // Fill with known pattern
    for (let z = 0; z < depth; z++) {
      for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
          const index = z * width * height + y * width + x;
          data[index] = x + y * 10 + z * 100;
        }
      }
    }

    // Verify pattern
    expect(data[0]).toBe(0); // x=0, y=0, z=0
    expect(data[1]).toBe(1); // x=1, y=0, z=0
    expect(data[4]).toBe(10); // x=0, y=1, z=0
    expect(data[16]).toBe(100); // x=0, y=0, z=1
  });
});
