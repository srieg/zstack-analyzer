"""
Image stack API routes with comprehensive microscopy format support.

Endpoints:
- POST /upload - Upload and process microscopy images with chunked support
- GET / - List all image stacks
- GET /{id} - Get image stack details
- GET /{id}/metadata - Get full metadata
- GET /{id}/thumbnail - Get thumbnail image
- GET /{id}/mip - Get maximum intensity projection
- GET /{id}/slice/{z} - Get single Z slice
- GET /{id}/download - Download original file
- DELETE /{id} - Delete image stack
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Response
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import os
import shutil
from pathlib import Path
import logging
from io import BytesIO

from api.database.connection import get_database
from api.models.image_stack import ImageStack
from core.processing.image_loader import (
    ImageLoader,
    ImageLoadError,
    UnsupportedFormatError,
    MissingDependencyError,
)
from core.processing.thumbnail import ThumbnailGenerator
from core.processing.metadata import ImageMetadata

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

THUMBNAIL_DIR = Path("thumbnails")
THUMBNAIL_DIR.mkdir(exist_ok=True)

# Initialize services
image_loader = ImageLoader()
thumbnail_generator = ThumbnailGenerator(cache_dir=str(THUMBNAIL_DIR))


@router.post("/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_database)
):
    """
    Upload and process a microscopy image file.

    Supports: TIFF, CZI, ND2, LIF formats
    Automatically extracts metadata and generates thumbnails.

    Returns:
        Image stack information including metadata
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )

    # Check file extension
    allowed_extensions = {".tif", ".tiff", ".czi", ".nd2", ".lif"}
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
        )

    # Create unique filename to avoid collisions
    # SECURITY: Sanitize filename to prevent path traversal attacks
    # Path.name extracts only the filename, stripping any directory components like ../
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    sanitized_name = Path(file.filename).name
    safe_filename = f"{unique_id}_{sanitized_name}"
    file_path = UPLOAD_DIR / safe_filename

    # Verify the resolved path is within UPLOAD_DIR (defense in depth)
    if not file_path.resolve().is_relative_to(UPLOAD_DIR.resolve()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )

    # Save uploaded file with chunked writing for large files
    try:
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                buffer.write(chunk)
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}", exc_info=True)
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {str(e)}"
        )

    # Extract metadata using ImageLoader
    try:
        metadata: ImageMetadata = await image_loader.get_metadata(str(file_path))

        # Generate thumbnail
        try:
            # Load a representative slice for thumbnail
            image_data, _ = await image_loader.load_image(
                str(file_path),
                lazy=True,  # Use lazy loading for large files
            )
            thumbnail = await thumbnail_generator.generate_thumbnail(
                image_data,
                size=(512, 512),
            )
            thumbnail_path = THUMBNAIL_DIR / f"{unique_id}_thumb.png"
            await thumbnail_generator.save_thumbnail(thumbnail, thumbnail_path)
        except Exception as e:
            logger.warning(f"Failed to generate thumbnail: {e}")
            thumbnail_path = None

        # Create database record
        metadata_dict = metadata.to_dict()

        image_stack = ImageStack(
            filename=file.filename,
            file_path=str(file_path),
            file_size=file_path.stat().st_size,
            width=metadata.size_x,
            height=metadata.size_y,
            depth=metadata.size_z,
            channels=metadata.size_c,
            bit_depth=metadata.bits_per_pixel,
            pixel_size_x=metadata_dict['voxel_size_um']['x'],
            pixel_size_y=metadata_dict['voxel_size_um']['y'],
            pixel_size_z=metadata_dict['voxel_size_um']['z'],
            microscope_id=metadata.microscope.manufacturer if metadata.microscope else None,
            objective_info=metadata.objective.dict() if metadata.objective else None,
            channel_config=[ch.dict() for ch in metadata.channels],
            image_metadata=metadata_dict,
            processing_status="uploaded",
            acquisition_date=metadata.acquisition_date,
        )

        db.add(image_stack)
        await db.commit()
        await db.refresh(image_stack)

        return {
            "message": "File uploaded successfully",
            "id": str(image_stack.id),
            "image_stack": image_stack.to_dict(),
        }

    except UnsupportedFormatError as e:
        logger.error(f"Unsupported format: {e}")
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except MissingDependencyError as e:
        logger.error(f"Missing dependency: {e}")
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except ImageLoadError as e:
        logger.error(f"Image loading error: {e}")
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process image: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error processing upload: {e}", exc_info=True)
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process uploaded file: {str(e)}"
        )


@router.get("/", response_model=List[dict])
async def list_images(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database)
):
    """
    List all uploaded image stacks.

    Query parameters:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
    """
    result = await db.execute(
        select(ImageStack).offset(skip).limit(limit).order_by(ImageStack.upload_date.desc())
    )
    image_stacks = result.scalars().all()
    return [stack.to_dict() for stack in image_stacks]


@router.get("/{image_id}", response_model=dict)
async def get_image(
    image_id: str,
    db: AsyncSession = Depends(get_database)
):
    """
    Get image stack details by ID.

    Returns basic information without full metadata.
    Use /{id}/metadata for complete metadata.
    """
    result = await db.execute(
        select(ImageStack).where(ImageStack.id == image_id)
    )
    image_stack = result.scalar_one_or_none()

    if not image_stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image stack not found"
        )

    return image_stack.to_dict()


@router.get("/{image_id}/metadata", response_model=dict)
async def get_image_metadata(
    image_id: str,
    db: AsyncSession = Depends(get_database)
):
    """
    Get full metadata for image stack.

    Returns comprehensive metadata including:
    - Physical dimensions and voxel sizes
    - Channel information
    - Microscope and objective details
    - Acquisition parameters
    - Vendor-specific metadata
    """
    result = await db.execute(
        select(ImageStack).where(ImageStack.id == image_id)
    )
    image_stack = result.scalar_one_or_none()

    if not image_stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image stack not found"
        )

    return {
        "id": str(image_stack.id),
        "filename": image_stack.filename,
        "metadata": image_stack.image_metadata,
    }


@router.get("/{image_id}/thumbnail")
async def get_thumbnail(
    image_id: str,
    width: int = 512,
    height: int = 512,
    z_slice: Optional[int] = None,
    mip: bool = True,
    db: AsyncSession = Depends(get_database)
):
    """
    Get thumbnail image for image stack.

    Query parameters:
        width: Thumbnail width (default 512)
        height: Thumbnail height (default 512)
        z_slice: Specific Z slice index (None for MIP)
        mip: Use maximum intensity projection if z_slice not specified (default True)

    Returns:
        PNG image
    """
    result = await db.execute(
        select(ImageStack).where(ImageStack.id == image_id)
    )
    image_stack = result.scalar_one_or_none()

    if not image_stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image stack not found"
        )

    file_path = Path(image_stack.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found on disk"
        )

    try:
        # Load image data
        image_data, _ = await image_loader.load_image(
            str(file_path),
            lazy=True,
        )

        # Generate thumbnail
        thumbnail = await thumbnail_generator.generate_thumbnail(
            image_data,
            size=(width, height),
            z_slice=z_slice,
        )

        # Convert to bytes
        thumbnail_bytes = await thumbnail_generator.get_thumbnail_bytes(thumbnail, format="PNG")

        return Response(
            content=thumbnail_bytes,
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=3600"}
        )

    except Exception as e:
        logger.error(f"Failed to generate thumbnail: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate thumbnail: {str(e)}"
        )


@router.get("/{image_id}/mip")
async def get_mip(
    image_id: str,
    width: int = 512,
    height: int = 512,
    axis: int = 0,
    db: AsyncSession = Depends(get_database)
):
    """
    Get maximum intensity projection for image stack.

    Query parameters:
        width: Image width
        height: Image height
        axis: Projection axis (0=Z, 1=Y, 2=X)

    Returns:
        PNG image
    """
    result = await db.execute(
        select(ImageStack).where(ImageStack.id == image_id)
    )
    image_stack = result.scalar_one_or_none()

    if not image_stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image stack not found"
        )

    file_path = Path(image_stack.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found on disk"
        )

    try:
        # Load image data
        image_data, _ = await image_loader.load_image(
            str(file_path),
            lazy=True,
        )

        # Generate MIP
        mip_image = await thumbnail_generator.generate_mip_thumbnail(
            image_data,
            size=(width, height),
            axis=axis,
        )

        # Convert to bytes
        mip_bytes = await thumbnail_generator.get_thumbnail_bytes(mip_image, format="PNG")

        return Response(
            content=mip_bytes,
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=3600"}
        )

    except Exception as e:
        logger.error(f"Failed to generate MIP: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate MIP: {str(e)}"
        )


@router.get("/{image_id}/slice/{z_index}")
async def get_slice(
    image_id: str,
    z_index: int,
    width: int = 1024,
    height: int = 1024,
    channel: Optional[int] = None,
    db: AsyncSession = Depends(get_database)
):
    """
    Get a specific Z slice from the image stack.

    Path parameters:
        z_index: Z slice index (0-based)

    Query parameters:
        width: Image width
        height: Image height
        channel: Specific channel index (None for all channels)

    Returns:
        PNG image
    """
    result = await db.execute(
        select(ImageStack).where(ImageStack.id == image_id)
    )
    image_stack = result.scalar_one_or_none()

    if not image_stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image stack not found"
        )

    if z_index < 0 or z_index >= image_stack.depth:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Z index. Must be between 0 and {image_stack.depth - 1}"
        )

    file_path = Path(image_stack.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found on disk"
        )

    try:
        # Load image data
        image_data, _ = await image_loader.load_image(
            str(file_path),
            lazy=True,
        )

        # Generate slice thumbnail
        channels = [channel] if channel is not None else None
        slice_image = await thumbnail_generator.generate_thumbnail(
            image_data,
            size=(width, height),
            z_slice=z_index,
            channels=channels,
        )

        # Convert to bytes
        slice_bytes = await thumbnail_generator.get_thumbnail_bytes(slice_image, format="PNG")

        return Response(
            content=slice_bytes,
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=3600"}
        )

    except Exception as e:
        logger.error(f"Failed to get slice: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get slice: {str(e)}"
        )


@router.get("/{image_id}/download")
async def download_image(
    image_id: str,
    db: AsyncSession = Depends(get_database)
):
    """
    Download the original image file.

    Returns:
        Original microscopy file
    """
    result = await db.execute(
        select(ImageStack).where(ImageStack.id == image_id)
    )
    image_stack = result.scalar_one_or_none()

    if not image_stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image stack not found"
        )

    file_path = Path(image_stack.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found on disk"
        )

    return FileResponse(
        path=str(file_path),
        filename=image_stack.filename,
        media_type="application/octet-stream",
    )


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: str,
    db: AsyncSession = Depends(get_database)
):
    """
    Delete an image stack and its associated files.

    Removes:
    - Database record
    - Original image file
    - Cached thumbnails
    """
    result = await db.execute(
        select(ImageStack).where(ImageStack.id == image_id)
    )
    image_stack = result.scalar_one_or_none()

    if not image_stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image stack not found"
        )

    # Delete file from filesystem
    file_path = Path(image_stack.file_path)
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")

    # Delete thumbnails
    # Extract unique ID from file path
    try:
        unique_id = file_path.stem.split('_')[0]
        for thumb_file in THUMBNAIL_DIR.glob(f"{unique_id}_*.png"):
            thumb_file.unlink()
    except Exception as e:
        logger.error(f"Failed to delete thumbnails: {e}")

    # Delete from database
    await db.delete(image_stack)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/formats/supported", response_model=dict)
async def get_supported_formats():
    """
    Get list of supported microscopy file formats.

    Returns:
        Dictionary of supported formats and their availability status
    """
    formats = {}
    for ext, (name, available, package) in image_loader.supported_formats.items():
        formats[ext] = {
            "name": name,
            "available": available,
            "required_package": package,
        }

    return {
        "formats": formats,
        "message": "All required packages are installed" if all(
            info["available"] for info in formats.values()
        ) else "Some packages are missing. Install with: pip install -r requirements.txt"
    }
