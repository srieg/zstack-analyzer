# VolumeViewer Quick Start Guide

Get your Z-stack microscopy data rendering in 3D in under 5 minutes.

## 1. Import the Component

```tsx
import { VolumeViewer } from './components/VolumeViewer';
```

## 2. Prepare Your Data

The VolumeViewer accepts a `Float32Array` containing your volume data in row-major order (x varies fastest, then y, then z).

```typescript
// Example: Load from your API or file
const data = new Float32Array(width * height * depth);

// Populate the array
for (let z = 0; z < depth; z++) {
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const index = z * width * height + y * width + x;
      data[index] = getVoxelValue(x, y, z); // Your data here
    }
  }
}
```

## 3. Render the Component

```tsx
function MyVolumeView() {
  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <VolumeViewer
        data={data}
        dimensions={[128, 128, 64]} // [width, height, depth]
        colorMaps={['viridis']}
        showAxes={true}
      />
    </div>
  );
}
```

## 4. Test with Demo Data

Want to see it in action immediately? Use the demo page:

```tsx
import { VolumeViewerDemo } from './pages/VolumeViewerDemo';

function App() {
  return <VolumeViewerDemo />;
}
```

This generates a sample sphere volume and displays it with full controls.

## Common Use Cases

### Loading TIFF Stack

```tsx
import { useState, useEffect } from 'react';
import { VolumeViewer } from './components/VolumeViewer';

function TiffStackViewer({ files }: { files: File[] }) {
  const [volumeData, setVolumeData] = useState(null);

  useEffect(() => {
    // Load TIFF files (use a library like tiff.js)
    loadTiffStack(files).then(setVolumeData);
  }, [files]);

  if (!volumeData) return <div>Loading...</div>;

  return (
    <VolumeViewer
      data={volumeData.data}
      dimensions={volumeData.dimensions}
      spacing={[0.1, 0.1, 0.5]} // Physical spacing in µm
    />
  );
}
```

### API Integration

```tsx
import { VolumeViewerIntegration } from './components/VolumeViewerIntegration';

function MyApp() {
  return (
    <VolumeViewerIntegration
      stackId="stack-abc123"
      apiEndpoint="/api/stacks"
      defaultRenderMode="mip"
      defaultColorMap="hot"
    />
  );
}
```

### Custom Styling

```tsx
<VolumeViewer
  data={data}
  dimensions={[256, 256, 128]}
  className="border-2 border-blue-500 rounded-lg shadow-2xl"
  showAxes={true}
/>
```

## Props Reference

### Essential Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `data` | `Float32Array` | ✅ | Volume data (row-major order) |
| `dimensions` | `[number, number, number]` | ✅ | [width, height, depth] |

### Optional Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `colorMaps` | `ColorMap[]` | `['viridis']` | Color mapping options |
| `renderMode` | `'volume' \| 'mip' \| 'slice' \| 'isosurface'` | `'volume'` | Initial render mode |
| `showAxes` | `boolean` | `true` | Show coordinate axes |
| `className` | `string` | `''` | Additional CSS classes |

## Keyboard Shortcuts

Coming soon! Current interaction is mouse-based:
- **Rotate**: Left click + drag
- **Pan**: Right click + drag
- **Zoom**: Scroll wheel

## Performance Tips

1. **Start with smaller volumes** (128³ or less) for smooth interaction
2. **Use MIP mode** for quick previews
3. **Adjust step size** in the control panel for quality/speed balance
4. **Disable slice planes** when not needed

## Troubleshooting

### Black Screen
- Check that your data array is populated
- Verify dimensions match data length: `data.length === width * height * depth`
- Try adjusting brightness and threshold sliders

### Low Frame Rate
- Reduce volume size or step size
- Switch to MIP mode
- Check browser console for WebGL errors

### TypeScript Errors
- Ensure all required dependencies are installed: `bun install`
- Check that `@types/three` is in devDependencies

## Next Steps

- Read the full [VOLUME_VIEWER_README.md](./VOLUME_VIEWER_README.md) for advanced features
- Explore the demo page source code for more examples
- Customize shaders for specialized rendering needs
- Add measurement tools and annotations

## Support

For questions or issues:
1. Check the full README documentation
2. Review the TypeScript type definitions in `src/types/volume.ts`
3. Open an issue on GitHub

---

**Ready to visualize your data in 3D?** Start with the demo page and customize from there!
