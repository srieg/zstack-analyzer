/**
 * VolumeViewer Component
 * Stunning 3D volume renderer for Z-stack microscopy data
 * Features: MIP, isosurface, slice view, ray marching, interactive controls
 */

import React, { useRef, useMemo, useEffect, useState, useCallback } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Html } from '@react-three/drei';
import * as THREE from 'three';
import {
  volumeVertexShader,
  volumeFragmentShader,
  sliceVertexShader,
  sliceFragmentShader,
} from '../shaders/volumeShaders';
import {
  createVolumeTexture,
  colorMapToUniform,
  calculateOptimalStepSize,
  downloadCanvasScreenshot,
  formatVolumeSize,
} from '../utils/volumeUtils';
import type {
  VolumeViewerProps,
  RenderMode,
  SliceAxis,
  VolumeControls,
  ColorMap,
} from '../types/volume';

// Volume mesh component with shader material
const VolumeMesh: React.FC<{
  data: Float32Array;
  dimensions: [number, number, number];
  controls: VolumeControls;
  colorMap: ColorMap;
}> = React.memo(({ data, dimensions, controls, colorMap }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);
  const { camera } = useThree();

  // Create 3D texture
  const volumeTexture = useMemo(
    () => createVolumeTexture(data, dimensions),
    [data, dimensions]
  );

  // Create shader uniforms
  const uniforms = useMemo(
    () => ({
      u_data: { value: volumeTexture },
      u_size: { value: dimensions },
      u_renderMode: { value: 0 },
      u_threshold: { value: controls.threshold },
      u_isoValue: { value: controls.isoValue },
      u_stepSize: { value: controls.stepSize },
      u_opacity: { value: controls.opacity },
      u_brightness: { value: controls.brightness },
      u_contrast: { value: controls.contrast },
      u_sliceAxis: { value: 2 },
      u_slicePosition: { value: 0.5 },
      u_colorMap: { value: colorMapToUniform(colorMap) },
      u_cameraPosition: { value: new THREE.Vector3() },
    }),
    [volumeTexture, dimensions, colorMap]
  );

  // Update uniforms from controls
  useEffect(() => {
    if (!materialRef.current) return;

    const modeMap: Record<RenderMode, number> = {
      volume: 0,
      mip: 1,
      slice: 2,
      isosurface: 3,
    };

    materialRef.current.uniforms.u_renderMode.value =
      modeMap[controls.renderMode];
    materialRef.current.uniforms.u_threshold.value = controls.threshold;
    materialRef.current.uniforms.u_isoValue.value = controls.isoValue;
    materialRef.current.uniforms.u_stepSize.value = controls.stepSize;
    materialRef.current.uniforms.u_opacity.value = controls.opacity;
    materialRef.current.uniforms.u_brightness.value = controls.brightness;
    materialRef.current.uniforms.u_contrast.value = controls.contrast;
    materialRef.current.uniforms.u_colorMap.value =
      colorMapToUniform(colorMap);
  }, [controls, colorMap]);

  // Update camera position for ray casting
  useFrame(() => {
    if (materialRef.current && camera) {
      materialRef.current.uniforms.u_cameraPosition.value.copy(
        camera.position
      );
    }
  });

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[2, 2, 2]} />
      <shaderMaterial
        ref={materialRef}
        vertexShader={volumeVertexShader}
        fragmentShader={volumeFragmentShader}
        uniforms={uniforms}
        side={THREE.BackSide}
        transparent={true}
        depthWrite={false}
      />
    </mesh>
  );
});

VolumeMesh.displayName = 'VolumeMesh';

// Slice plane component
const SlicePlane: React.FC<{
  axis: SliceAxis;
  position: number;
  data: Float32Array;
  dimensions: [number, number, number];
  colorMap: ColorMap;
  opacity: number;
  brightness: number;
  contrast: number;
}> = React.memo(
  ({
    axis,
    position,
    data,
    dimensions,
    colorMap,
    opacity,
    brightness,
    contrast,
  }) => {
    const meshRef = useRef<THREE.Mesh>(null);
    const volumeTexture = useMemo(
      () => createVolumeTexture(data, dimensions),
      [data, dimensions]
    );

    const { rotation, positionVec } = useMemo(() => {

      const rotations: Record<SliceAxis, [number, number, number]> = {
        x: [0, Math.PI / 2, 0],
        y: [Math.PI / 2, 0, 0],
        z: [0, 0, 0],
      };

      const positions: Record<SliceAxis, [number, number, number]> = {
        x: [(position - 0.5) * 2, 0, 0],
        y: [0, (position - 0.5) * 2, 0],
        z: [0, 0, (position - 0.5) * 2],
      };

      return {
        rotation: rotations[axis],
        positionVec: positions[axis],
      };
    }, [axis, position]);

    const uniforms = useMemo(
      () => ({
        u_data: { value: volumeTexture },
        u_axis: { value: axis === 'x' ? 0 : axis === 'y' ? 1 : 2 },
        u_position: { value: position },
        u_opacity: { value: opacity },
        u_brightness: { value: brightness },
        u_contrast: { value: contrast },
        u_colorMap: { value: colorMapToUniform(colorMap) },
      }),
      [volumeTexture, axis, position, opacity, brightness, contrast, colorMap]
    );

    return (
      <mesh ref={meshRef} position={positionVec} rotation={rotation}>
        <planeGeometry args={[2, 2]} />
        <shaderMaterial
          vertexShader={sliceVertexShader}
          fragmentShader={sliceFragmentShader}
          uniforms={uniforms}
          transparent={true}
          side={THREE.DoubleSide}
        />
      </mesh>
    );
  }
);

SlicePlane.displayName = 'SlicePlane';

// Axes helper component
const AxesLabels: React.FC<{ size?: number }> = ({ size = 1.2 }) => {
  return (
    <group>
      <Html position={[size, 0, 0]}>
        <div className="text-red-400 font-bold text-sm pointer-events-none">
          X
        </div>
      </Html>
      <Html position={[0, size, 0]}>
        <div className="text-green-400 font-bold text-sm pointer-events-none">
          Y
        </div>
      </Html>
      <Html position={[0, 0, size]}>
        <div className="text-blue-400 font-bold text-sm pointer-events-none">
          Z
        </div>
      </Html>
    </group>
  );
};

// Control panel with glass-morphism
const ControlPanel: React.FC<{
  controls: VolumeControls;
  onControlChange: (key: keyof VolumeControls, value: any) => void;
  dimensions: [number, number, number];
  colorMap: ColorMap;
  onColorMapChange: (colorMap: ColorMap) => void;
  onScreenshot: () => void;
}> = ({
  controls,
  onControlChange,
  dimensions,
  colorMap,
  onColorMapChange,
  onScreenshot,
}) => {
  return (
    <div className="absolute top-4 left-4 bg-white/10 backdrop-blur-xl rounded-2xl p-6 shadow-2xl border border-white/20 max-w-md z-10">
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-white text-xl font-bold mb-1">Volume Controls</h3>
        <p className="text-white/60 text-sm">
          {formatVolumeSize(dimensions)} voxels
        </p>
      </div>

      {/* Render Mode */}
      <div className="mb-4">
        <label className="text-white text-sm font-medium block mb-2">
          Render Mode
        </label>
        <div className="grid grid-cols-2 gap-2">
          {(['volume', 'mip', 'slice', 'isosurface'] as RenderMode[]).map(
            (mode) => (
              <button
                key={mode}
                onClick={() => onControlChange('renderMode', mode)}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  controls.renderMode === mode
                    ? 'bg-blue-500 text-white shadow-lg'
                    : 'bg-white/10 text-white/70 hover:bg-white/20'
                }`}
              >
                {mode.toUpperCase()}
              </button>
            )
          )}
        </div>
      </div>

      {/* Color Map */}
      <div className="mb-4">
        <label className="text-white text-sm font-medium block mb-2">
          Color Map
        </label>
        <select
          value={colorMap}
          onChange={(e) => onColorMapChange(e.target.value as ColorMap)}
          className="w-full bg-white/10 text-white rounded-lg px-3 py-2 text-sm border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="grayscale">Grayscale</option>
          <option value="hot">Hot</option>
          <option value="cool">Cool</option>
          <option value="viridis">Viridis</option>
          <option value="plasma">Plasma</option>
          <option value="turbo">Turbo</option>
        </select>
      </div>

      {/* Opacity */}
      <div className="mb-4">
        <label className="text-white text-sm font-medium block mb-2">
          Opacity: {controls.opacity.toFixed(2)}
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={controls.opacity}
          onChange={(e) =>
            onControlChange('opacity', parseFloat(e.target.value))
          }
          className="w-full accent-blue-500"
        />
      </div>

      {/* Threshold */}
      <div className="mb-4">
        <label className="text-white text-sm font-medium block mb-2">
          Threshold: {controls.threshold.toFixed(2)}
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={controls.threshold}
          onChange={(e) =>
            onControlChange('threshold', parseFloat(e.target.value))
          }
          className="w-full accent-blue-500"
        />
      </div>

      {/* Brightness */}
      <div className="mb-4">
        <label className="text-white text-sm font-medium block mb-2">
          Brightness: {controls.brightness.toFixed(2)}
        </label>
        <input
          type="range"
          min="-0.5"
          max="0.5"
          step="0.01"
          value={controls.brightness}
          onChange={(e) =>
            onControlChange('brightness', parseFloat(e.target.value))
          }
          className="w-full accent-blue-500"
        />
      </div>

      {/* Contrast */}
      <div className="mb-4">
        <label className="text-white text-sm font-medium block mb-2">
          Contrast: {controls.contrast.toFixed(2)}
        </label>
        <input
          type="range"
          min="0.5"
          max="2"
          step="0.01"
          value={controls.contrast}
          onChange={(e) =>
            onControlChange('contrast', parseFloat(e.target.value))
          }
          className="w-full accent-blue-500"
        />
      </div>

      {/* Toggle Controls */}
      <div className="space-y-2 mb-4">
        <label className="flex items-center text-white text-sm">
          <input
            type="checkbox"
            checked={controls.showAxes}
            onChange={(e) => onControlChange('showAxes', e.target.checked)}
            className="mr-2 accent-blue-500"
          />
          Show Axes
        </label>
        <label className="flex items-center text-white text-sm">
          <input
            type="checkbox"
            checked={controls.showSlicePlanes}
            onChange={(e) =>
              onControlChange('showSlicePlanes', e.target.checked)
            }
            className="mr-2 accent-blue-500"
          />
          Show Slice Planes
        </label>
      </div>

      {/* Screenshot Button */}
      <button
        onClick={onScreenshot}
        className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white font-medium py-2 px-4 rounded-lg hover:shadow-lg transition-all"
      >
        📸 Take Screenshot
      </button>
    </div>
  );
};

// Loading skeleton
const LoadingSkeleton: React.FC = () => {
  return (
    <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-900 to-black">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-white text-lg font-medium">Loading Volume Data...</p>
        <p className="text-white/60 text-sm mt-2">
          Preparing 3D visualization
        </p>
      </div>
    </div>
  );
};

// Main VolumeViewer component
export const VolumeViewer: React.FC<VolumeViewerProps> = ({
  data,
  dimensions,
  colorMaps = ['viridis'],
  renderMode = 'volume',
  showAxes = true,
  className = '',
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [colorMap, setColorMap] = useState<ColorMap>(colorMaps[0] || 'viridis');

  const [controls, setControls] = useState<VolumeControls>({
    renderMode,
    slicePlanes: {
      x: { axis: 'x', position: 0.5, visible: true },
      y: { axis: 'y', position: 0.5, visible: true },
      z: { axis: 'z', position: 0.5, visible: true },
    },
    opacity: 0.5,
    brightness: 0,
    contrast: 1,
    threshold: 0.1,
    isoValue: 0.5,
    stepSize: calculateOptimalStepSize(dimensions),
    showAxes,
    showScaleBar: true,
    showSlicePlanes: false,
  });

  const handleControlChange = useCallback(
    (key: keyof VolumeControls, value: any) => {
      setControls((prev) => ({ ...prev, [key]: value }));
    },
    []
  );

  const handleScreenshot = useCallback(() => {
    const canvas = document.querySelector('canvas');
    if (canvas) {
      downloadCanvasScreenshot(
        canvas,
        `volume-${new Date().getTime()}.png`,
        2
      );
    }
  }, []);

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => setIsLoading(false), 500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className={`relative w-full h-full ${className}`}>
      {isLoading && <LoadingSkeleton />}

      <Canvas
        ref={canvasRef}
        camera={{ position: [3, 3, 3], fov: 50 }}
        gl={{ preserveDrawingBuffer: true, antialias: true }}
        className="touch-none"
      >
        <color attach="background" args={['#0a0a0a']} />
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />

        <PerspectiveCamera makeDefault position={[3, 3, 3]} />
        <OrbitControls
          enableDamping
          dampingFactor={0.05}
          rotateSpeed={0.5}
          zoomSpeed={0.5}
        />

        <VolumeMesh
          data={data}
          dimensions={dimensions}
          controls={controls}
          colorMap={colorMap}
        />

        {controls.showSlicePlanes && (
          <>
            <SlicePlane
              axis="x"
              position={controls.slicePlanes.x.position}
              data={data}
              dimensions={dimensions}
              colorMap={colorMap}
              opacity={0.8}
              brightness={controls.brightness}
              contrast={controls.contrast}
            />
            <SlicePlane
              axis="y"
              position={controls.slicePlanes.y.position}
              data={data}
              dimensions={dimensions}
              colorMap={colorMap}
              opacity={0.8}
              brightness={controls.brightness}
              contrast={controls.contrast}
            />
            <SlicePlane
              axis="z"
              position={controls.slicePlanes.z.position}
              data={data}
              dimensions={dimensions}
              colorMap={colorMap}
              opacity={0.8}
              brightness={controls.brightness}
              contrast={controls.contrast}
            />
          </>
        )}

        {controls.showAxes && (
          <>
            <axesHelper args={[1.5]} />
            <AxesLabels />
          </>
        )}
      </Canvas>

      <ControlPanel
        controls={controls}
        onControlChange={handleControlChange}
        dimensions={dimensions}
        colorMap={colorMap}
        onColorMapChange={setColorMap}
        onScreenshot={handleScreenshot}
      />
    </div>
  );
};

export default VolumeViewer;
