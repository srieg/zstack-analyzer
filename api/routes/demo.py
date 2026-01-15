"""
Demo API Routes
Provides access to synthetic demo datasets for showcasing the platform.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import numpy as np
import logging
from datetime import datetime

from api.database.connection import get_database
from api.models.image_stack import ImageStack
from demo.generator import SyntheticDataGenerator

router = APIRouter()
logger = logging.getLogger(__name__)

# Paths
DEMO_DIR = Path("demo")
DATASETS_CONFIG = DEMO_DIR / "datasets.json"
DEMO_CACHE_DIR = DEMO_DIR / "cache"
DEMO_CACHE_DIR.mkdir(parents=True, exist_ok=True)


class DemoDatasetInfo(BaseModel):
    """Demo dataset metadata."""
    id: str
    name: str
    description: str
    difficulty: str
    categories: List[str]
    shape: List[int]
    channels: int
    channel_names: List[str]
    snr: str
    expected_results: Dict[str, Any]
    showcase_features: List[str]
    timepoints: Optional[int] = 1


class CustomGenerationRequest(BaseModel):
    """Request for custom synthetic data generation."""
    shape: List[int] = Field(..., description="[depth, height, width]")
    channels: int = Field(1, ge=1, le=4)
    nuclei_count: int = Field(20, ge=0, le=200)
    filament_count: int = Field(0, ge=0, le=100)
    puncta_count: int = Field(0, ge=0, le=500)
    noise_level: str = Field("medium", pattern="^(low|medium|high)$")
    add_background: bool = True
    apply_psf: bool = True
    seed: Optional[int] = None


def _load_datasets_config() -> Dict[str, Any]:
    """Load the datasets configuration file."""
    try:
        with open(DATASETS_CONFIG, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load datasets config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load demo datasets configuration"
        )


def _generate_dataset(dataset_id: str, config: Dict[str, Any]) -> np.ndarray:
    """Generate synthetic dataset based on configuration."""
    try:
        generator = SyntheticDataGenerator()
        shape = tuple(config["shape"])
        params = config["generation_params"]

        # Handle different dataset types
        if config.get("generation_params", {}).get("time_series"):
            # Time series dataset
            data = generator.generate_time_series(
                shape=shape,
                num_timepoints=params["num_timepoints"],
                movement_speed=params["movement_speed"]
            )
            return data

        elif config.get("generation_params", {}).get("colocalization"):
            # Colocalization dataset (2 channels)
            ch1, ch2 = generator.generate_colocalization(
                shape=shape,
                overlap_fraction=params["overlap_fraction"]
            )

            # Add noise and background to both channels
            ch1 = generator.add_background(ch1, mean=params["noise"]["background_mean"])
            ch1 = generator.add_gaussian_noise(ch1, sigma=params["noise"]["gaussian_sigma"])
            ch1 = generator.apply_psf_blur(ch1)

            ch2 = generator.add_background(ch2, mean=params["noise"]["background_mean"])
            ch2 = generator.add_gaussian_noise(ch2, sigma=params["noise"]["gaussian_sigma"])
            ch2 = generator.apply_psf_blur(ch2)

            # Stack channels
            data = np.stack([ch1, ch2], axis=0)
            return data

        else:
            # Standard multi-channel dataset
            num_channels = config["channels"]
            channels = []

            for ch_idx in range(num_channels):
                channel = np.zeros(shape, dtype=np.float32)

                # Add different structures based on parameters
                if "nuclei" in params and ch_idx == 0:
                    nuclei = generator.generate_nuclei(
                        shape=shape,
                        **params["nuclei"]
                    )
                    channel += nuclei.astype(np.float32)

                if "filaments" in params and ch_idx in [0, 1]:
                    filaments = generator.generate_filaments(
                        shape=shape,
                        **params["filaments"]
                    )
                    channel += filaments.astype(np.float32)

                if "puncta" in params and ch_idx in [1]:
                    puncta = generator.generate_puncta(
                        shape=shape,
                        **params["puncta"]
                    )
                    channel += puncta.astype(np.float32)

                # Add noise and background
                channel = channel.astype(np.uint16)
                channel = generator.add_background(
                    channel,
                    mean=params["noise"]["background_mean"]
                )

                # Add Poisson noise if specified
                if "poisson_scaling" in params["noise"]:
                    channel = generator.add_poisson_noise(
                        channel,
                        scaling_factor=params["noise"]["poisson_scaling"]
                    )

                channel = generator.add_gaussian_noise(
                    channel,
                    sigma=params["noise"]["gaussian_sigma"]
                )

                # Apply PSF blur
                channel = generator.apply_psf_blur(channel)

                channels.append(channel)

            if num_channels == 1:
                data = channels[0]
            else:
                data = np.stack(channels, axis=0)

            return data

    except Exception as e:
        logger.error(f"Failed to generate dataset {dataset_id}: {e}")
        raise


@router.get("/datasets", response_model=List[DemoDatasetInfo])
async def list_demo_datasets():
    """List all available demo datasets."""
    try:
        config = _load_datasets_config()
        datasets = []

        for dataset in config["datasets"]:
            datasets.append(DemoDatasetInfo(
                id=dataset["id"],
                name=dataset["name"],
                description=dataset["description"],
                difficulty=dataset["difficulty"],
                categories=dataset["categories"],
                shape=dataset["shape"],
                channels=dataset["channels"],
                channel_names=dataset["channel_names"],
                snr=dataset["snr"],
                expected_results=dataset["expected_results"],
                showcase_features=dataset["showcase_features"],
                timepoints=dataset.get("timepoints", 1)
            ))

        return datasets

    except Exception as e:
        logger.error(f"Failed to list demo datasets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/datasets/{dataset_id}/info")
async def get_demo_dataset_info(dataset_id: str):
    """Get detailed information about a specific demo dataset."""
    try:
        config = _load_datasets_config()

        for dataset in config["datasets"]:
            if dataset["id"] == dataset_id:
                return dataset

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Demo dataset '{dataset_id}' not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get demo dataset info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/datasets/{dataset_id}/load")
async def load_demo_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_database)
):
    """
    Load a demo dataset (generates if needed, caches for performance).
    Creates a database entry like a real upload.
    """
    try:
        config = _load_datasets_config()

        # Find dataset configuration
        dataset_config = None
        for dataset in config["datasets"]:
            if dataset["id"] == dataset_id:
                dataset_config = dataset
                break

        if not dataset_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Demo dataset '{dataset_id}' not found"
            )

        # Check cache
        cache_file = DEMO_CACHE_DIR / f"{dataset_id}.npy"

        if cache_file.exists():
            logger.info(f"Loading cached demo dataset: {dataset_id}")
            data = np.load(str(cache_file))
        else:
            logger.info(f"Generating demo dataset: {dataset_id}")
            data = _generate_dataset(dataset_id, dataset_config)

            # Cache for next time
            np.save(str(cache_file), data)
            logger.info(f"Cached demo dataset: {dataset_id}")

        # Create a pseudo-file path for demo data
        demo_filename = f"{dataset_id}_demo.tif"
        demo_filepath = DEMO_CACHE_DIR / demo_filename

        # Create database entry
        shape = dataset_config["shape"]
        image_stack = ImageStack(
            filename=demo_filename,
            file_path=str(demo_filepath),
            file_size=cache_file.stat().st_size if cache_file.exists() else 0,
            width=shape[2],
            height=shape[1],
            depth=shape[0],
            channels=dataset_config["channels"],
            bit_depth=16,
            pixel_size_x=0.1,
            pixel_size_y=0.1,
            pixel_size_z=0.2,
            microscope_id="Demo System",
            objective_info="Synthetic Data Generator v1.0",
            channel_config=dataset_config["channel_names"],
            image_metadata={
                "demo_dataset": True,
                "dataset_id": dataset_id,
                "dataset_name": dataset_config["name"],
                "difficulty": dataset_config["difficulty"],
                "snr": dataset_config["snr"],
                "expected_results": dataset_config["expected_results"],
                "showcase_features": dataset_config["showcase_features"]
            },
            processing_status="demo_loaded"
        )

        db.add(image_stack)
        await db.commit()
        await db.refresh(image_stack)

        return {
            "message": "Demo dataset loaded successfully",
            "image_stack": image_stack.to_dict(),
            "data_shape": data.shape,
            "data_type": str(data.dtype),
            "cached": cache_file.exists()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load demo dataset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/generate")
async def generate_custom_dataset(
    request: CustomGenerationRequest,
    db: AsyncSession = Depends(get_database)
):
    """Generate custom synthetic dataset with specified parameters."""
    try:
        generator = SyntheticDataGenerator(seed=request.seed)
        shape = tuple(request.shape)

        # Noise parameters based on level
        noise_params = {
            "low": {"sigma": 200, "background": 300},
            "medium": {"sigma": 400, "background": 500},
            "high": {"sigma": 800, "background": 700}
        }
        noise = noise_params[request.noise_level]

        # Generate channels
        channels = []
        for ch_idx in range(request.channels):
            channel = np.zeros(shape, dtype=np.float32)

            # Add structures
            if request.nuclei_count > 0 and ch_idx == 0:
                nuclei = generator.generate_nuclei(
                    shape=shape,
                    num_nuclei=request.nuclei_count
                )
                channel += nuclei.astype(np.float32)

            if request.filament_count > 0 and ch_idx in [0, 1]:
                filaments = generator.generate_filaments(
                    shape=shape,
                    num_filaments=request.filament_count
                )
                channel += filaments.astype(np.float32)

            if request.puncta_count > 0 and ch_idx in [1]:
                puncta = generator.generate_puncta(
                    shape=shape,
                    num_puncta=request.puncta_count
                )
                channel += puncta.astype(np.float32)

            # Post-processing
            channel = channel.astype(np.uint16)

            if request.add_background:
                channel = generator.add_background(channel, mean=noise["background"])

            channel = generator.add_gaussian_noise(channel, sigma=noise["sigma"])

            if request.apply_psf:
                channel = generator.apply_psf_blur(channel)

            channels.append(channel)

        # Stack if multi-channel
        if request.channels == 1:
            data = channels[0]
        else:
            data = np.stack(channels, axis=0)

        # Save to cache
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cache_filename = f"custom_{timestamp}.npy"
        cache_file = DEMO_CACHE_DIR / cache_filename
        np.save(str(cache_file), data)

        # Create database entry
        demo_filename = f"custom_{timestamp}_demo.tif"
        demo_filepath = DEMO_CACHE_DIR / demo_filename

        image_stack = ImageStack(
            filename=demo_filename,
            file_path=str(demo_filepath),
            file_size=cache_file.stat().st_size,
            width=shape[2],
            height=shape[1],
            depth=shape[0],
            channels=request.channels,
            bit_depth=16,
            pixel_size_x=0.1,
            pixel_size_y=0.1,
            pixel_size_z=0.2,
            microscope_id="Demo System",
            objective_info="Custom Synthetic Data",
            channel_config=[f"Channel {i+1}" for i in range(request.channels)],
            image_metadata={
                "demo_dataset": True,
                "custom_generation": True,
                "generation_params": request.dict(),
                "generated_at": timestamp
            },
            processing_status="demo_loaded"
        )

        db.add(image_stack)
        await db.commit()
        await db.refresh(image_stack)

        return {
            "message": "Custom dataset generated successfully",
            "image_stack": image_stack.to_dict(),
            "data_shape": data.shape,
            "data_type": str(data.dtype),
            "cache_file": str(cache_file)
        }

    except Exception as e:
        logger.error(f"Failed to generate custom dataset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/cache")
async def clear_demo_cache():
    """Clear all cached demo datasets."""
    try:
        cache_files = list(DEMO_CACHE_DIR.glob("*.npy"))
        deleted_count = 0

        for cache_file in cache_files:
            cache_file.unlink()
            deleted_count += 1

        return {
            "message": f"Cleared {deleted_count} cached demo datasets",
            "deleted_count": deleted_count
        }

    except Exception as e:
        logger.error(f"Failed to clear demo cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/cache/stats")
async def get_cache_stats():
    """Get statistics about the demo cache."""
    try:
        cache_files = list(DEMO_CACHE_DIR.glob("*.npy"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            "cached_datasets": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_directory": str(DEMO_CACHE_DIR)
        }

    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
