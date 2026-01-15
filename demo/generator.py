"""
Synthetic Z-Stack Data Generator
Creates realistic-looking microscopy data for demo purposes.
"""

import numpy as np
from scipy import ndimage
from typing import Tuple, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    """Generate realistic synthetic microscopy Z-stack data."""

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            np.random.seed(seed)

    def generate_nuclei(
        self,
        shape: Tuple[int, int, int],
        num_nuclei: int = 20,
        radius_range: Tuple[float, float] = (5.0, 15.0),
        intensity_range: Tuple[int, int] = (5000, 25000)
    ) -> np.ndarray:
        """
        Generate 3D spheroidal nuclei with realistic appearance.

        Args:
            shape: (depth, height, width) dimensions
            num_nuclei: Number of nuclei to generate
            radius_range: (min, max) radius in pixels
            intensity_range: (min, max) intensity values

        Returns:
            3D numpy array with synthetic nuclei
        """
        depth, height, width = shape
        image = np.zeros(shape, dtype=np.float32)

        for _ in range(num_nuclei):
            # Random position (avoid edges)
            z = np.random.randint(int(depth * 0.2), int(depth * 0.8))
            y = np.random.randint(int(height * 0.15), int(height * 0.85))
            x = np.random.randint(int(width * 0.15), int(width * 0.85))

            # Random radius and intensity
            radius = np.random.uniform(*radius_range)
            intensity = np.random.randint(*intensity_range)

            # Create 3D Gaussian blob
            z_range = np.arange(depth)[:, None, None]
            y_range = np.arange(height)[None, :, None]
            x_range = np.arange(width)[None, None, :]

            # Anisotropic Gaussian (ellipsoidal)
            z_scale = 0.7  # Z is typically compressed in confocal
            dist_sq = ((z_range - z) / z_scale) ** 2 + (y_range - y) ** 2 + (x_range - x) ** 2

            # Gaussian intensity with slight irregularity
            sigma = radius / 2.355  # FWHM to sigma conversion
            nucleus = intensity * np.exp(-dist_sq / (2 * sigma ** 2))

            # Add texture (chromatin-like)
            texture_noise = np.random.randn(*shape) * 0.15
            texture = ndimage.gaussian_filter(texture_noise, sigma=1.5)
            nucleus = nucleus * (1 + texture)

            image += nucleus

        return np.clip(image, 0, 65535).astype(np.uint16)

    def generate_filaments(
        self,
        shape: Tuple[int, int, int],
        num_filaments: int = 15,
        length_range: Tuple[float, float] = (30.0, 100.0),
        thickness_range: Tuple[float, float] = (0.8, 2.0),
        intensity_range: Tuple[int, int] = (3000, 15000)
    ) -> np.ndarray:
        """
        Generate filamentous structures (microtubules, actin).

        Args:
            shape: (depth, height, width) dimensions
            num_filaments: Number of filaments to generate
            length_range: (min, max) length in pixels
            thickness_range: (min, max) thickness in pixels
            intensity_range: (min, max) intensity values

        Returns:
            3D numpy array with synthetic filaments
        """
        depth, height, width = shape
        image = np.zeros(shape, dtype=np.float32)

        for _ in range(num_filaments):
            # Random starting point
            start_z = np.random.randint(0, depth)
            start_y = np.random.randint(0, height)
            start_x = np.random.randint(0, width)

            # Random direction and length
            length = np.random.uniform(*length_range)
            direction = np.random.randn(3)
            direction = direction / np.linalg.norm(direction)

            # Generate points along the filament
            num_points = int(length)
            t = np.linspace(0, length, num_points)

            # Add some curvature (not perfectly straight)
            curve = np.random.randn(3, num_points) * 0.5
            curve = ndimage.gaussian_filter1d(curve, sigma=5, axis=1)

            points_z = start_z + direction[0] * t + curve[0]
            points_y = start_y + direction[1] * t + curve[1]
            points_x = start_x + direction[2] * t + curve[2]

            # Random thickness and intensity
            thickness = np.random.uniform(*thickness_range)
            intensity = np.random.randint(*intensity_range)

            # Draw the filament
            for pz, py, px in zip(points_z, points_y, points_x):
                if 0 <= pz < depth and 0 <= py < height and 0 <= px < width:
                    # Create small sphere at each point
                    z_range = np.arange(max(0, int(pz) - 3), min(depth, int(pz) + 4))
                    y_range = np.arange(max(0, int(py) - 3), min(height, int(py) + 4))
                    x_range = np.arange(max(0, int(px) - 3), min(width, int(px) + 4))

                    for iz in z_range:
                        for iy in y_range:
                            for ix in x_range:
                                dist = np.sqrt((iz - pz)**2 + (iy - py)**2 + (ix - px)**2)
                                if dist < thickness:
                                    val = intensity * np.exp(-dist**2 / (2 * thickness**2))
                                    image[iz, iy, ix] += val

        return np.clip(image, 0, 65535).astype(np.uint16)

    def generate_puncta(
        self,
        shape: Tuple[int, int, int],
        num_puncta: int = 100,
        radius_range: Tuple[float, float] = (1.0, 3.0),
        intensity_range: Tuple[int, int] = (8000, 30000)
    ) -> np.ndarray:
        """
        Generate punctate structures (vesicles, spots).

        Args:
            shape: (depth, height, width) dimensions
            num_puncta: Number of puncta to generate
            radius_range: (min, max) radius in pixels
            intensity_range: (min, max) intensity values

        Returns:
            3D numpy array with synthetic puncta
        """
        depth, height, width = shape
        image = np.zeros(shape, dtype=np.float32)

        for _ in range(num_puncta):
            # Random position
            z = np.random.randint(0, depth)
            y = np.random.randint(0, height)
            x = np.random.randint(0, width)

            # Random radius and intensity
            radius = np.random.uniform(*radius_range)
            intensity = np.random.randint(*intensity_range)

            # Create small Gaussian spot
            z_range = np.arange(max(0, z - 5), min(depth, z + 6))
            y_range = np.arange(max(0, y - 5), min(height, y + 6))
            x_range = np.arange(max(0, x - 5), min(width, x + 6))

            for iz in z_range:
                for iy in y_range:
                    for ix in x_range:
                        dist = np.sqrt((iz - z)**2 + (iy - y)**2 + (ix - x)**2)
                        if dist < radius * 2:
                            val = intensity * np.exp(-dist**2 / (2 * radius**2))
                            image[iz, iy, ix] += val

        return np.clip(image, 0, 65535).astype(np.uint16)

    def add_poisson_noise(
        self,
        image: np.ndarray,
        scaling_factor: float = 0.1
    ) -> np.ndarray:
        """Add realistic Poisson (shot) noise."""
        # Scale down, add Poisson noise, scale back up
        scaled = image * scaling_factor
        noisy = np.random.poisson(scaled)
        return (noisy / scaling_factor).astype(np.uint16)

    def add_gaussian_noise(
        self,
        image: np.ndarray,
        sigma: float = 500.0
    ) -> np.ndarray:
        """Add Gaussian readout noise."""
        noise = np.random.normal(0, sigma, image.shape)
        noisy = image.astype(np.float32) + noise
        return np.clip(noisy, 0, 65535).astype(np.uint16)

    def add_background(
        self,
        image: np.ndarray,
        mean: float = 500.0,
        gradient_strength: float = 0.2
    ) -> np.ndarray:
        """Add realistic background with slight gradient."""
        depth, height, width = image.shape

        # Uniform background
        background = np.ones(image.shape, dtype=np.float32) * mean

        # Add gradient (typical in microscopy)
        y_grad = np.linspace(-gradient_strength, gradient_strength, height)
        x_grad = np.linspace(-gradient_strength, gradient_strength, width)
        gradient = mean * (y_grad[None, :, None] + x_grad[None, None, :])

        background += gradient

        # Add texture
        texture = np.random.randn(*image.shape) * (mean * 0.1)
        texture = ndimage.gaussian_filter(texture, sigma=5)
        background += texture

        result = image.astype(np.float32) + background
        return np.clip(result, 0, 65535).astype(np.uint16)

    def apply_psf_blur(
        self,
        image: np.ndarray,
        sigma_xy: float = 1.2,
        sigma_z: float = 2.5
    ) -> np.ndarray:
        """
        Apply Point Spread Function blur (anisotropic Gaussian).
        Simulates the optical blur of a confocal microscope.
        """
        # Anisotropic Gaussian blur (Z is typically worse resolution)
        blurred = ndimage.gaussian_filter(
            image.astype(np.float32),
            sigma=[sigma_z, sigma_xy, sigma_xy]
        )
        return blurred.astype(np.uint16)

    def generate_colocalization(
        self,
        shape: Tuple[int, int, int],
        overlap_fraction: float = 0.5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate two channels with controlled colocalization.

        Args:
            shape: (depth, height, width) dimensions
            overlap_fraction: Fraction of structures that overlap (0.0 to 1.0)

        Returns:
            Tuple of (channel1, channel2) arrays
        """
        # Generate structures for channel 1
        ch1_nuclei = self.generate_nuclei(shape, num_nuclei=15)
        ch1_puncta = self.generate_puncta(shape, num_puncta=80)
        channel1 = ch1_nuclei + ch1_puncta

        # Generate partially overlapping structures for channel 2
        num_shared = int(15 * overlap_fraction)
        num_unique = 15 - num_shared

        # Shared nuclei (same positions)
        np.random.seed(42)  # Temporary seed for reproducible positions
        ch2_shared = self.generate_nuclei(shape, num_nuclei=num_shared)
        np.random.seed()  # Reset seed

        # Unique nuclei (different positions)
        ch2_unique = self.generate_nuclei(shape, num_nuclei=num_unique)
        ch2_puncta = self.generate_puncta(shape, num_puncta=60)

        channel2 = ch2_shared + ch2_unique + ch2_puncta

        return channel1, channel2

    def generate_time_series(
        self,
        shape: Tuple[int, int, int],
        num_timepoints: int = 10,
        movement_speed: float = 5.0
    ) -> np.ndarray:
        """
        Generate a time series showing cell migration.

        Args:
            shape: (depth, height, width) dimensions
            num_timepoints: Number of time points
            movement_speed: Movement speed in pixels per timepoint

        Returns:
            4D array (time, depth, height, width)
        """
        time_series = np.zeros((num_timepoints,) + shape, dtype=np.uint16)

        # Initial positions
        num_cells = 5
        positions = np.random.rand(num_cells, 3)
        positions[:, 0] *= shape[0]  # z
        positions[:, 1] *= shape[1]  # y
        positions[:, 2] *= shape[2]  # x

        # Movement directions
        directions = np.random.randn(num_cells, 3)
        directions = directions / np.linalg.norm(directions, axis=1, keepdims=True)

        for t in range(num_timepoints):
            frame = np.zeros(shape, dtype=np.float32)

            for cell_idx in range(num_cells):
                pos = positions[cell_idx]

                # Generate cell at current position
                radius = 10.0
                intensity = 15000

                z, y, x = pos
                z_range = np.arange(shape[0])[:, None, None]
                y_range = np.arange(shape[1])[None, :, None]
                x_range = np.arange(shape[2])[None, None, :]

                dist_sq = (z_range - z) ** 2 + (y_range - y) ** 2 + (x_range - x) ** 2
                sigma = radius / 2.355
                cell = intensity * np.exp(-dist_sq / (2 * sigma ** 2))

                frame += cell

                # Update position with some randomness
                movement = directions[cell_idx] * movement_speed
                movement += np.random.randn(3) * movement_speed * 0.3
                positions[cell_idx] += movement

                # Boundary reflection
                for dim in range(3):
                    if positions[cell_idx, dim] < 0 or positions[cell_idx, dim] >= shape[dim]:
                        directions[cell_idx, dim] *= -1
                        positions[cell_idx, dim] = np.clip(
                            positions[cell_idx, dim], 0, shape[dim] - 1
                        )

            # Add noise and background
            frame = self.add_background(frame.astype(np.uint16))
            frame = self.add_gaussian_noise(frame, sigma=300)
            time_series[t] = frame

        return time_series
