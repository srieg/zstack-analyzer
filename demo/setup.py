"""
Demo System Setup Script
Verifies dependencies and prepares the demo system
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Verify Python version."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True


def check_dependencies():
    """Check required Python packages."""
    required = {
        'numpy': 'numpy',
        'scipy': 'scipy',
        'fastapi': 'fastapi',
        'pydantic': 'pydantic'
    }

    missing = []
    for package, import_name in required.items():
        try:
            __import__(import_name)
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package} not found")
            missing.append(package)

    if missing:
        print(f"\nInstall missing packages:")
        print(f"pip install {' '.join(missing)}")
        return False

    return True


def create_directories():
    """Create necessary directories."""
    dirs = [
        Path("demo/cache"),
        Path("uploads")
    ]

    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {directory}")

    return True


def verify_config():
    """Verify configuration files."""
    config_files = [
        Path("demo/datasets.json"),
        Path("demo/generator.py")
    ]

    for config_file in config_files:
        if not config_file.exists():
            print(f"❌ Missing {config_file}")
            return False
        print(f"✓ Found {config_file}")

    return True


def test_generation():
    """Test synthetic data generation."""
    try:
        print("\nTesting data generation...")
        from demo.generator import SyntheticDataGenerator
        import numpy as np

        gen = SyntheticDataGenerator(seed=42)

        # Quick test
        shape = (10, 64, 64)
        data = gen.generate_nuclei(shape, num_nuclei=3)

        assert data.shape == shape, "Shape mismatch"
        assert data.dtype == np.uint16, "Type mismatch"
        assert data.max() > 0, "Empty data"

        print("✓ Generation test passed")
        return True

    except Exception as e:
        print(f"❌ Generation test failed: {e}")
        return False


def check_frontend_dependencies():
    """Check if frontend dependencies are installed."""
    package_json = Path("frontend/package.json")

    if not package_json.exists():
        print("⚠ Frontend not found (optional)")
        return True

    try:
        import json
        with open(package_json) as f:
            pkg = json.load(f)

        required_deps = ['framer-motion', 'lucide-react']
        deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}

        missing = [dep for dep in required_deps if dep not in deps]

        if missing:
            print(f"\n⚠ Missing frontend dependencies:")
            print(f"cd frontend && npm install {' '.join(missing)}")
        else:
            print("✓ Frontend dependencies OK")

        return True

    except Exception as e:
        print(f"⚠ Could not check frontend dependencies: {e}")
        return True


def main():
    """Run all setup checks."""
    print("=" * 50)
    print("Z-Stack Analyzer - Demo System Setup")
    print("=" * 50)
    print()

    checks = [
        ("Python Version", check_python_version),
        ("Python Dependencies", check_dependencies),
        ("Directories", create_directories),
        ("Configuration Files", verify_config),
        ("Generation Test", test_generation),
        ("Frontend Dependencies", check_frontend_dependencies)
    ]

    passed = 0
    failed = 0

    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 30)
        try:
            if check_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)

    if failed == 0:
        print("\n✅ Demo system ready!")
        print("\nNext steps:")
        print("1. Start API: python -m api.main")
        print("2. Navigate to: http://localhost:8000/api/v1/demo/datasets")
        print("3. Frontend: cd frontend && npm run dev")
        print("4. Open: http://localhost:5173/demo")
    else:
        print("\n❌ Setup incomplete. Fix errors above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
