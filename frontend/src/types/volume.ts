/**
 * Volume Rendering Type Definitions
 * For Z-stack microscopy 3D visualization
 */

export type RenderMode = 'mip' | 'isosurface' | 'slice' | 'volume';
export type SliceAxis = 'x' | 'y' | 'z';
export type ColorMap = 'grayscale' | 'hot' | 'cool' | 'viridis' | 'plasma' | 'magma' | 'turbo';

export interface VolumeData {
  data: Float32Array;
  dimensions: [number, number, number]; // [width, height, depth]
  channels: number;
  spacing?: [number, number, number]; // Physical spacing in µm
  metadata?: {
    name?: string;
    timestamp?: string;
    pixelSize?: number;
    acquisitionParams?: Record<string, any>;
  };
}

export interface TransferFunction {
  points: TransferFunctionPoint[];
  colorMap: ColorMap;
}

export interface TransferFunctionPoint {
  value: number; // 0-1 normalized intensity
  opacity: number; // 0-1
  color?: [number, number, number]; // RGB 0-1
}

export interface SlicePlane {
  axis: SliceAxis;
  position: number; // 0-1 normalized position
  visible: boolean;
}

export interface VolumeViewerProps {
  data: Float32Array;
  dimensions: [number, number, number];
  channels?: number;
  colorMaps?: ColorMap[];
  renderMode?: RenderMode;
  transferFunctions?: TransferFunction[];
  spacing?: [number, number, number];
  onSliceChange?: (axis: SliceAxis, position: number) => void;
  onMeasurement?: (distance: number, points: [number, number, number][]) => void;
  showAxes?: boolean;
  showScaleBar?: boolean;
  className?: string;
}

export interface MeasurementPoint {
  position: [number, number, number];
  worldPosition: [number, number, number];
  id: string;
}

export interface VolumeControls {
  renderMode: RenderMode;
  slicePlanes: Record<SliceAxis, SlicePlane>;
  opacity: number;
  brightness: number;
  contrast: number;
  threshold: number;
  isoValue: number;
  stepSize: number;
  showAxes: boolean;
  showScaleBar: boolean;
  showSlicePlanes: boolean;
}

export interface CameraState {
  position: [number, number, number];
  target: [number, number, number];
  zoom: number;
  fov: number;
}

export interface ShaderUniforms {
  u_data: { value: THREE.Data3DTexture | null };
  u_size: { value: [number, number, number] };
  u_renderMode: { value: number };
  u_threshold: { value: number };
  u_isoValue: { value: number };
  u_stepSize: { value: number };
  u_opacity: { value: number };
  u_brightness: { value: number };
  u_contrast: { value: number };
  u_sliceAxis: { value: number };
  u_slicePosition: { value: number };
  u_colorMap: { value: number };
  u_cameraPosition: { value: [number, number, number] };
}
