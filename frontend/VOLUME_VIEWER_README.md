# VolumeViewer Component

A stunning, HN-worthy 3D volume renderer for Z-stack microscopy data built with React Three Fiber and WebGL.

## Features

### Rendering Modes
- **Volume Rendering**: Full 3D ray marching with opacity compositing
- **Maximum Intensity Projection (MIP)**: Highlights brightest voxels along ray
- **Isosurface**: Extract and render specific intensity surfaces
- **Slice View**: Interactive orthogonal slicing (XY, XZ, YZ planes)

### Visualization
- **Multiple Color Maps**: Grayscale, Hot, Cool, Viridis, Plasma, Turbo
- **Transfer Functions**: Customizable opacity and color mapping
- **Interactive Controls**: Orbit, zoom, pan with smooth damping
- **Slice Planes**: Draggable orthogonal planes for cross-sectional views
- **Axes & Scale Bar**: Spatial reference with labeled axes

### Performance
- **WebGL Ray Marching**: GPU-accelerated volume rendering
- **Early Ray Termination**: Optimized for performance
- **Adaptive Step Size**: Automatic optimization based on volume dimensions
- **Trilinear Interpolation**: Smooth voxel sampling

### UI/UX
- **Glass-morphism Design**: Beautiful, modern control panel
- **Real-time Updates**: Instant parameter adjustments
- **High-res Screenshots**: Export publication-quality images
- **Loading States**: Elegant skeleton screens
- **Responsive Layout**: Works across screen sizes

## Installation

The component uses these dependencies (already in package.json):

```bash
bun install
```

Required packages:
- `react` & `react-dom`
- `three` - 3D library
- `@react-three/fiber` - React renderer for Three.js
- `@react-three/drei` - Three.js helpers
- `@types/three` - TypeScript definitions

## Usage

### Basic Example

```tsx
import { VolumeViewer } from './components/VolumeViewer';

function MyComponent() {
  // Your volume data (Float32Array)
  const data = new Float32Array(128 * 128 * 128);
  // ... populate data ...

  return (
    <VolumeViewer
      data={data}
      dimensions={[128, 128, 128]}
      channels={1}
      colorMaps={['viridis']}
      showAxes={true}
      showScaleBar={true}
    />
  );
}
```

### Advanced Example with API Integration

```tsx
import { VolumeViewerIntegration } from './components/VolumeViewerIntegration';

function MyApp() {
  return (
    <VolumeViewerIntegration
      stackId="stack-123"
      apiEndpoint="/api/stacks"
      defaultRenderMode="volume"
      defaultColorMap="viridis"
    />
  );
}
```

### Demo Page

```tsx
import { VolumeViewerDemo } from './pages/VolumeViewerDemo';

function App() {
  return <VolumeViewerDemo />;
}
```

## Props

### VolumeViewer

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | `Float32Array` | Required | Volume data in row-major order |
| `dimensions` | `[number, number, number]` | Required | [width, height, depth] in voxels |
| `channels` | `number` | `1` | Number of channels |
| `colorMaps` | `ColorMap[]` | `['viridis']` | Color maps per channel |
| `renderMode` | `RenderMode` | `'volume'` | Initial render mode |
| `spacing` | `[number, number, number]` | `[1, 1, 1]` | Physical spacing in µm |
| `onSliceChange` | `(axis, position) => void` | - | Callback for slice changes |
| `onMeasurement` | `(distance, points) => void` | - | Callback for measurements |
| `showAxes` | `boolean` | `true` | Show coordinate axes |
| `showScaleBar` | `boolean` | `true` | Show scale bar |
| `className` | `string` | `''` | Additional CSS classes |

### Types

```typescript
type RenderMode = 'volume' | 'mip' | 'slice' | 'isosurface';
type ColorMap = 'grayscale' | 'hot' | 'cool' | 'viridis' | 'plasma' | 'turbo';
type SliceAxis = 'x' | 'y' | 'z';
```

## Architecture

### Component Structure

```
VolumeViewer/
├── VolumeViewer.tsx          # Main component
├── VolumeViewerIntegration.tsx  # API integration wrapper
├── VolumeViewerDemo.tsx       # Demo page
├── types/volume.ts            # TypeScript definitions
├── shaders/
│   └── volumeShaders.ts       # WebGL shaders
└── utils/
    └── volumeUtils.ts         # Utility functions
```

### Shader Pipeline

1. **Vertex Shader**: Transforms geometry, passes position to fragment shader
2. **Fragment Shader**:
   - Ray-box intersection
   - Ray marching with adaptive step size
   - Volume sampling with trilinear interpolation
   - Color mapping and opacity transfer
   - Front-to-back compositing
   - Early ray termination for optimization

### Data Flow

```
Float32Array → createVolumeTexture() → THREE.Data3DTexture
                                            ↓
                                      ShaderMaterial
                                            ↓
                                    Fragment Shader
                                            ↓
                                    Ray Marching
                                            ↓
                                    Rendered Image
```

## Controls

### Mouse/Trackpad
- **Left Click + Drag**: Rotate camera
- **Right Click + Drag**: Pan camera
- **Scroll**: Zoom in/out

### Control Panel
- **Render Mode**: Switch between Volume, MIP, Slice, Isosurface
- **Color Map**: Change color mapping
- **Opacity**: Control transparency (0-1)
- **Threshold**: Filter low-intensity voxels (0-1)
- **Brightness**: Adjust brightness (-0.5 to 0.5)
- **Contrast**: Adjust contrast (0.5 to 2)
- **Show Axes**: Toggle coordinate axes
- **Show Slice Planes**: Toggle orthogonal planes
- **Screenshot**: Export high-res PNG (2x resolution)

## Performance Optimization

### Recommended Settings

| Volume Size | Step Size | Expected FPS |
|-------------|-----------|--------------|
| 64³ | 0.01 | 60 FPS |
| 128³ | 0.005 | 45-60 FPS |
| 256³ | 0.003 | 30-45 FPS |
| 512³ | 0.002 | 15-30 FPS |

### Optimization Tips

1. **Use smaller volumes for real-time interaction**: Downsample large datasets
2. **Adjust step size**: Larger steps = faster rendering (but lower quality)
3. **Enable early ray termination**: Automatically enabled for opacity > 0.95
4. **Use MIP mode for quick previews**: Faster than full volume rendering
5. **Disable slice planes when not needed**: Saves GPU cycles

## Color Maps

### Available Maps
- **Grayscale**: Traditional black to white
- **Hot**: Black → Red → Yellow → White (thermal imaging)
- **Cool**: Cyan → Blue → Magenta
- **Viridis**: Perceptually uniform, colorblind-friendly
- **Plasma**: High contrast, purple to yellow
- **Turbo**: Rainbow-like, maximum information density

### Scientific Recommendations
- **Fluorescence microscopy**: Viridis, Plasma
- **Calcium imaging**: Hot, Turbo
- **Multi-channel**: Different maps per channel
- **Publications**: Viridis (colorblind-friendly)

## Browser Compatibility

Requires WebGL 2.0 support:
- ✅ Chrome 56+
- ✅ Firefox 51+
- ✅ Safari 15+
- ✅ Edge 79+

## Future Enhancements

Potential additions:
- [ ] Multi-channel overlay rendering
- [ ] Custom transfer function editor
- [ ] Distance measurement tool
- [ ] Volume segmentation overlay
- [ ] Animation/rotation recording
- [ ] VR/AR support
- [ ] GPU compute shaders for preprocessing
- [ ] Time-series 4D visualization
- [ ] Collaborative annotations
- [ ] WebGPU migration for better performance

## Examples

### Loading from TIFF Stack

```typescript
import { loadTiffStack } from './utils/tiffLoader';

async function loadAndVisualize(files: File[]) {
  const volumeData = await loadTiffStack(files);

  return (
    <VolumeViewer
      data={volumeData.data}
      dimensions={volumeData.dimensions}
      spacing={[0.1, 0.1, 0.5]} // µm
    />
  );
}
```

### Custom Transfer Function

```typescript
const transferFunction = {
  points: [
    { value: 0.0, opacity: 0.0, color: [0, 0, 0] },
    { value: 0.3, opacity: 0.2, color: [0, 0, 1] },
    { value: 0.7, opacity: 0.8, color: [1, 1, 0] },
    { value: 1.0, opacity: 1.0, color: [1, 0, 0] },
  ],
  colorMap: 'viridis',
};

<VolumeViewer
  transferFunctions={[transferFunction]}
  {...otherProps}
/>
```

### Multiple Channels

```typescript
<VolumeViewer
  data={multiChannelData}
  dimensions={[512, 512, 100]}
  channels={3}
  colorMaps={['viridis', 'hot', 'cool']}
/>
```

## License

See project LICENSE file.

## Credits

Built with:
- [Three.js](https://threejs.org/) - 3D library
- [React Three Fiber](https://docs.pmnd.rs/react-three-fiber/) - React renderer
- [React Three Drei](https://github.com/pmndrs/drei) - Three.js helpers
- Color maps inspired by Matplotlib and scientific visualization research

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Built with 💙 for the microscopy and research community**
