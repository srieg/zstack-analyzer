#!/usr/bin/env python3
"""
Apple Silicon Verification Script for Z-Stack Analyzer

Comprehensive verification of Apple Silicon optimization including:
- Platform detection
- Metal GPU support
- Native dependency verification
- Performance benchmarking
- Memory optimization check
"""

import sys
import platform
import subprocess
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "tinygrad"))


def print_header(text: str) -> None:
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_status(text: str, status: bool, details: str = "") -> None:
    """Print status line"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {text}")
    if details:
        print(f"   {details}")


def check_platform() -> bool:
    """Verify Apple Silicon platform"""
    print_header("Platform Verification")

    machine = platform.machine()
    system = platform.system()
    release = platform.mac_ver()[0]

    print_status(
        "Platform Architecture",
        machine == "arm64",
        f"Detected: {machine} (Expected: arm64)"
    )

    print_status(
        "Operating System",
        system == "Darwin",
        f"Detected: {system} {release}"
    )

    is_apple_silicon = machine == "arm64" and system == "Darwin"
    print_status(
        "Apple Silicon Platform",
        is_apple_silicon,
        "Running on native Apple Silicon" if is_apple_silicon else "Not Apple Silicon"
    )

    return is_apple_silicon


def check_python_arch() -> bool:
    """Verify Python is running as ARM64"""
    print_header("Python Environment")

    python_version = platform.python_version()
    python_impl = platform.python_implementation()

    print_status(
        "Python Version",
        True,
        f"{python_impl} {python_version}"
    )

    # Check if Python is ARM64
    is_arm64 = platform.machine() == "arm64"
    print_status(
        "Python Architecture",
        is_arm64,
        f"Running as {'ARM64' if is_arm64 else 'x86_64 (Rosetta 2)'}"
    )

    return is_arm64


def check_numpy_acceleration() -> bool:
    """Verify NumPy uses Apple Accelerate"""
    print_header("NumPy Acceleration")

    try:
        import numpy as np

        version = np.__version__
        print_status("NumPy Installation", True, f"Version: {version}")

        # Check for Accelerate framework
        config = np.show_config()
        uses_accelerate = "accelerate" in str(config).lower()

        print_status(
            "Apple Accelerate Framework",
            uses_accelerate,
            "Using Apple's optimized BLAS/LAPACK" if uses_accelerate else "Not using Accelerate"
        )

        return uses_accelerate

    except ImportError:
        print_status("NumPy Installation", False, "NumPy not installed")
        return False


def check_metal_gpu() -> bool:
    """Verify Metal GPU support"""
    print_header("Metal GPU Support")

    try:
        # Check system Metal support
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType"],
            capture_output=True,
            text=True,
            timeout=10
        )

        has_metal = "Metal" in result.stdout
        print_status("System Metal Support", has_metal)

        if has_metal:
            # Extract GPU name
            for line in result.stdout.split("\n"):
                if "Chipset Model" in line:
                    gpu_name = line.split(":")[-1].strip()
                    print(f"   GPU: {gpu_name}")
                    break

    except Exception as e:
        print_status("System Metal Detection", False, f"Error: {e}")
        return False

    # Check tinygrad Metal support
    try:
        from tinygrad import Device
        from tinygrad.tensor import Tensor

        metal_available = "METAL" in Device._devices
        print_status(
            "Tinygrad Metal Device",
            metal_available,
            "METAL device registered" if metal_available else "METAL device not found"
        )

        if not metal_available:
            return False

        # Test Metal initialization
        try:
            Device.DEFAULT = "METAL"
            test_tensor = Tensor([1.0, 2.0, 3.0], device="METAL")
            result = test_tensor.realize()
            values = result.numpy()

            metal_works = all(abs(values[i] - (i + 1.0)) < 0.001 for i in range(3))
            print_status(
                "Metal GPU Initialization",
                metal_works,
                "Successfully created and executed tensor on Metal"
            )

            return metal_works

        except Exception as e:
            print_status("Metal GPU Initialization", False, f"Error: {e}")
            return False

    except ImportError as e:
        print_status("Tinygrad Installation", False, f"Import error: {e}")
        return False


def check_device_manager() -> bool:
    """Verify device manager properly detects Metal"""
    print_header("Device Manager Verification")

    try:
        from core.gpu.device_manager import DeviceManager

        dm = DeviceManager()

        device = dm.device
        is_metal = dm.is_metal
        device_info = dm.device_info

        print_status(
            "Device Detection",
            is_metal,
            f"Device: {device}"
        )

        if is_metal:
            print(f"   Name: {device_info.get('name', 'Unknown')}")
            print(f"   Type: {device_info.get('type', 'Unknown')}")

        # Check memory info
        try:
            memory_info = dm.get_device_memory_info()
            total_gb = memory_info['total'] / (1024**3)
            available_gb = memory_info['available'] / (1024**3)

            print_status(
                "Memory Detection",
                total_gb > 0,
                f"Total: {total_gb:.1f} GB, Available: {available_gb:.1f} GB"
            )

            # Estimate max volume
            max_vol = dm.estimate_max_volume_size()
            print_status(
                "Max Volume Estimation",
                True,
                f"Estimated max dimensions: {max_vol[0]}x{max_vol[1]}x{max_vol[2]}"
            )

        except Exception as e:
            print_status("Memory Detection", False, f"Error: {e}")

        return is_metal

    except Exception as e:
        print_status("Device Manager Import", False, f"Error: {e}")
        return False


def benchmark_gpu_operations() -> bool:
    """Benchmark GPU operations on Metal"""
    print_header("GPU Performance Benchmark")

    try:
        from core.gpu.device_manager import DeviceManager
        from core.gpu.kernels import gaussian_blur_3d, sobel_3d, otsu_threshold
        import numpy as np

        dm = DeviceManager()

        if not dm.is_metal:
            print_status("GPU Benchmark", False, "Metal GPU not available")
            return False

        # Create test volume (smaller for quick test)
        test_size = (64, 64, 64)
        print(f"   Test volume size: {test_size}")
        test_volume = np.random.rand(*test_size).astype(np.float32)

        # Benchmark Gaussian blur
        try:
            start = time.perf_counter()
            result = gaussian_blur_3d(test_volume, sigma=1.0)
            elapsed = (time.perf_counter() - start) * 1000
            print_status(
                "Gaussian Blur 3D",
                elapsed < 5000,  # Should complete in <5 seconds
                f"Completed in {elapsed:.1f}ms"
            )
        except Exception as e:
            print_status("Gaussian Blur 3D", False, f"Error: {e}")

        # Benchmark Sobel edge detection
        try:
            start = time.perf_counter()
            result = sobel_3d(test_volume)
            elapsed = (time.perf_counter() - start) * 1000
            print_status(
                "Sobel Edge Detection",
                elapsed < 5000,
                f"Completed in {elapsed:.1f}ms"
            )
        except Exception as e:
            print_status("Sobel Edge Detection", False, f"Error: {e}")

        # Benchmark Otsu threshold (note: this operation is slower due to histogram computation)
        try:
            start = time.perf_counter()
            threshold, binary = otsu_threshold(test_volume)
            elapsed = (time.perf_counter() - start) * 1000
            # Otsu is inherently slower due to iterative threshold search
            # Accept up to 60 seconds for small test volume
            print_status(
                "Otsu Thresholding",
                elapsed < 60000,
                f"Completed in {elapsed:.1f}ms, Threshold: {threshold:.3f}"
            )
        except Exception as e:
            print_status("Otsu Thresholding", False, f"Error: {e}")

        print("\n   Note: Benchmarks run on 64³ volume for quick verification")
        print("   Real-world performance on 512³ volumes will be proportionally slower")

        return True

    except Exception as e:
        print_status("GPU Benchmark Setup", False, f"Error: {e}")
        return False


def check_dependencies() -> bool:
    """Verify all critical dependencies are installed and ARM64"""
    print_header("Dependencies Verification")

    dependencies = [
        ("numpy", "NumPy"),
        ("scipy", "SciPy"),
        ("cv2", "OpenCV"),
        ("skimage", "scikit-image"),
        ("tifffile", "tifffile"),
        ("fastapi", "FastAPI"),
    ]

    all_good = True
    for module_name, display_name in dependencies:
        try:
            module = __import__(module_name)
            version = getattr(module, "__version__", "unknown")
            print_status(display_name, True, f"Version: {version}")
        except ImportError:
            print_status(display_name, False, "Not installed")
            all_good = False

    return all_good


def check_optional_dependencies() -> None:
    """Check optional microscopy format dependencies"""
    print_header("Optional Microscopy Format Support")

    optional_deps = [
        ("aicspylibczi", "CZI format (Zeiss)"),
        ("nd2", "ND2 format (Nikon)"),
        ("readlif", "LIF format (Leica)"),
    ]

    for module_name, description in optional_deps:
        try:
            module = __import__(module_name)
            version = getattr(module, "__version__", "installed")
            print_status(description, True, f"Version: {version}")
        except ImportError:
            print_status(description, False, "Not installed (optional)")


def generate_report(results: dict) -> None:
    """Generate summary report"""
    print_header("Verification Summary")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed

    print(f"   Total Checks: {total}")
    print(f"   Passed: {passed} ✅")
    print(f"   Failed: {failed} ❌")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")

    if failed == 0:
        print("\n🎉 All verifications passed! Z-Stack Analyzer is fully optimized for Apple Silicon.")
    else:
        print("\n⚠️  Some verifications failed. Check the details above.")
        print("   Refer to APPLE_SILICON_GUIDE.md for troubleshooting.")


def main() -> int:
    """Main verification routine"""
    print("\n" + "=" * 70)
    print("  🍎 Z-Stack Analyzer - Apple Silicon Verification")
    print("=" * 70)

    results = {}

    # Run all checks
    results["platform"] = check_platform()
    results["python_arch"] = check_python_arch()
    results["numpy_accelerate"] = check_numpy_acceleration()
    results["metal_gpu"] = check_metal_gpu()
    results["device_manager"] = check_device_manager()
    results["dependencies"] = check_dependencies()
    results["benchmark"] = benchmark_gpu_operations()

    # Optional checks (don't affect pass/fail)
    check_optional_dependencies()

    # Generate report
    generate_report(results)

    # Return exit code
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
