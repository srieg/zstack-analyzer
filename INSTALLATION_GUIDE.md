# Installation and Testing Guide

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/samriegel/zstack-analyzer

# Create/activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Verify installations
python -c "import tifffile; print('tifffile:', tifffile.__version__)"
python -c "import aicspylibczi; print('aicspylibczi: OK')"
python -c "import nd2; print('nd2:', nd2.__version__)"
python -c "import readlif; print('readlif: OK')"
python -c "import dask; print('dask:', dask.__version__)"
```

### 2. Test Basic Functionality

Create a test script `test_loader.py`:

```python
import asyncio
from pathlib import Path
from core.processing.image_loader import ImageLoader

async def test_loader():
    loader = ImageLoader()

    # Check supported formats
    print("Supported formats:")
    for ext, (name, available, package) in loader.supported_formats.items():
        status = "✓" if available else "✗"
        print(f"  {status} {ext}: {name} (requires {package})")

    print("\nTest complete!")

if __name__ == "__main__":
    asyncio.run(test_loader())
```

Run the test:
```bash
python test_loader.py
```

Expected output:
```
Supported formats:
  ✓ .tif: TIFF (requires tifffile)
  ✓ .tiff: TIFF (requires tifffile)
  ✓ .czi: CZI (requires aicspylibczi)
  ✓ .nd2: ND2 (requires nd2)
  ✓ .lif: LIF (requires readlif)

Test complete!
```

### 3. Start the Server

```bash
# Using uvicorn directly
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Or using the start script
./start.sh
```

### 4. Test API Endpoints

```bash
# Check if server is running
curl http://localhost:8000/health

# Check supported formats
curl http://localhost:8000/api/images/formats/supported
```

## Testing with Sample Data

### Create Sample TIFF File

```python
import numpy as np
import tifffile

# Create synthetic z-stack (3 channels, 20 slices, 512x512)
data = np.random.randint(0, 65535, (3, 20, 512, 512), dtype=np.uint16)

# Add some structure
for z in range(20):
    for c in range(3):
        # Add circular gradient
        y, x = np.ogrid[:512, :512]
        center_y, center_x = 256, 256
        radius = 100 + z * 5
        mask = (x - center_x)**2 + (y - center_y)**2 < radius**2
        data[c, z, mask] = 50000 + c * 5000

# Save with metadata
tifffile.imwrite(
    'test_sample.tif',
    data,
    metadata={
        'axes': 'CZYX',
        'spacing': 0.2,  # Z spacing in micrometers
    },
    resolution=(10.0, 10.0),  # 0.1 um/pixel
    imagej=True,
)

print("Created test_sample.tif")
```

### Upload and Test

```bash
# Upload the test file
curl -X POST http://localhost:8000/api/images/upload \
  -F "file=@test_sample.tif" \
  -o upload_response.json

# Extract image ID
IMAGE_ID=$(cat upload_response.json | python -c "import sys, json; print(json.load(sys.stdin)['id'])")

# Get metadata
curl http://localhost:8000/api/images/$IMAGE_ID/metadata | python -m json.tool

# Get thumbnail
curl http://localhost:8000/api/images/$IMAGE_ID/thumbnail?width=512&height=512 \
  -o thumbnail.png

# Get MIP
curl http://localhost:8000/api/images/$IMAGE_ID/mip?axis=0 \
  -o mip_z.png

# Get specific slice
curl http://localhost:8000/api/images/$IMAGE_ID/slice/10 \
  -o slice_10.png

# List all images
curl http://localhost:8000/api/images/ | python -m json.tool

# Delete image
curl -X DELETE http://localhost:8000/api/images/$IMAGE_ID
```

## Troubleshooting

### Issue: Import Errors

**Problem:**
```
ImportError: No module named 'tifffile'
```

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Or install specific package
pip install tifffile
```

### Issue: aicspylibczi Installation Fails

**Problem:**
```
ERROR: Failed building wheel for aicspylibczi
```

**Solution:**
```bash
# Install system dependencies (macOS)
brew install cmake

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install cmake build-essential

# Try installing again
pip install aicspylibczi
```

### Issue: Database Connection Error

**Problem:**
```
sqlalchemy.exc.OperationalError: could not connect to database
```

**Solution:**
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL (macOS)
brew services start postgresql

# Start PostgreSQL (Linux)
sudo systemctl start postgresql

# Create database
createdb zstack_analyzer

# Run migrations
alembic upgrade head
```

### Issue: Out of Memory

**Problem:**
```
MemoryError: Unable to allocate array
```

**Solution:**
- The file may be too large for available RAM
- Lazy loading should activate automatically for files >1GB
- Verify lazy loading is working:
```python
metadata = await loader.get_metadata(file_path)
print(f"Use lazy loading: {metadata.should_use_lazy_loading()}")
```
- Manually force lazy loading:
```python
image_data, metadata = await loader.load_image(file_path, lazy=True)
print(f"Data type: {type(image_data)}")  # Should be dask.array.Array
```

### Issue: Thumbnail Generation Slow

**Problem:**
Thumbnails taking >10 seconds to generate.

**Solution:**
- For very large Z-stacks, MIP computation is expensive
- Consider reducing thumbnail size
- Pre-generate thumbnails during upload (already implemented)
- Ensure SSD for thumbnail cache directory

## Development Tips

### Enable Debug Logging

```python
# In api/main.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Test Individual Components

```python
# Test metadata extraction
from core.processing.image_loader import ImageLoader

loader = ImageLoader()
metadata = await loader.get_metadata("sample.tif")
print(metadata.to_dict())

# Test thumbnail generation
from core.processing.thumbnail import ThumbnailGenerator

thumb_gen = ThumbnailGenerator()
image_data, _ = await loader.load_image("sample.tif")
thumbnail = await thumb_gen.generate_thumbnail(image_data, size=(256, 256))
await thumb_gen.save_thumbnail(thumbnail, "test_thumb.png")
```

### Profile Performance

```python
import asyncio
import time
from core.processing.image_loader import ImageLoader

async def profile_loading():
    loader = ImageLoader()

    start = time.time()
    metadata = await loader.get_metadata("large_file.tif")
    print(f"Metadata extraction: {time.time() - start:.2f}s")

    start = time.time()
    image_data, _ = await loader.load_image("large_file.tif", lazy=True)
    print(f"Image loading: {time.time() - start:.2f}s")

asyncio.run(profile_loading())
```

## Next Steps

1. **Add Authentication**
   - JWT tokens for API access
   - User-specific uploads

2. **Add Processing Pipeline**
   - Background tasks with Celery
   - Analysis queue

3. **Add Frontend**
   - React/Vue.js image viewer
   - Interactive Z-stack navigation

4. **Add Cloud Storage**
   - S3/Azure Blob integration
   - Direct upload to cloud

5. **Add Batch Processing**
   - Multiple file upload
   - Folder processing

## Resources

- [tifffile documentation](https://pypi.org/project/tifffile/)
- [aicspylibczi documentation](https://github.com/AllenCellModeling/aicspylibczi)
- [nd2 documentation](https://github.com/tlambert03/nd2)
- [dask documentation](https://docs.dask.org/)
- [FastAPI documentation](https://fastapi.tiangolo.com/)

## Support

For issues or questions, check:
1. Server logs: `tail -f logs/server.log`
2. Error responses from API
3. File format compatibility
4. Dependency versions
