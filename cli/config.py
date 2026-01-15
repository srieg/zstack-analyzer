"""
Configuration management for Z-Stack Analyzer CLI

Supports YAML configuration files with user-level and project-level configs.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dataclasses import dataclass, field, asdict


@dataclass
class AnalysisConfig:
    """Configuration for analysis operations"""

    default_algorithm: str = "segmentation_3d"
    threshold: float = 0.5
    min_object_size: int = 100
    output_format: str = "json"
    parallel_workers: int = 4


@dataclass
class GPUConfig:
    """Configuration for GPU settings"""

    enabled: bool = True
    device: Optional[str] = None  # e.g., "cuda:0", "metal"
    memory_limit_mb: Optional[int] = None
    fallback_to_cpu: bool = True


@dataclass
class OutputConfig:
    """Configuration for output settings"""

    default_directory: str = "./results"
    compression: Optional[str] = None
    quality: int = 95
    save_metadata: bool = True
    verbose: bool = False


@dataclass
class ServerConfig:
    """Configuration for web server"""

    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    log_level: str = "info"


@dataclass
class ZStackConfig:
    """Root configuration for Z-Stack Analyzer"""

    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    gpu: GPUConfig = field(default_factory=GPUConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    server: ServerConfig = field(default_factory=ServerConfig)


class ConfigManager:
    """
    Manages configuration loading and saving

    Configuration priority (highest to lowest):
    1. Command-line arguments (handled by typer)
    2. Project-level config (./.zstack-analyzer.yaml)
    3. User-level config (~/.zstack-analyzer.yaml)
    4. Default values
    """

    USER_CONFIG_PATH = Path.home() / ".zstack-analyzer.yaml"
    PROJECT_CONFIG_PATH = Path.cwd() / ".zstack-analyzer.yaml"

    def __init__(self):
        self.config = ZStackConfig()
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from files"""

        # Load user-level config first (lower priority)
        if self.USER_CONFIG_PATH.exists():
            self._merge_config(self.USER_CONFIG_PATH)

        # Load project-level config (higher priority)
        if self.PROJECT_CONFIG_PATH.exists():
            self._merge_config(self.PROJECT_CONFIG_PATH)

    def _merge_config(self, config_path: Path) -> None:
        """Merge configuration from a YAML file"""

        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)

            if not data:
                return

            # Merge analysis config
            if 'analysis' in data:
                for key, value in data['analysis'].items():
                    if hasattr(self.config.analysis, key):
                        setattr(self.config.analysis, key, value)

            # Merge GPU config
            if 'gpu' in data:
                for key, value in data['gpu'].items():
                    if hasattr(self.config.gpu, key):
                        setattr(self.config.gpu, key, value)

            # Merge output config
            if 'output' in data:
                for key, value in data['output'].items():
                    if hasattr(self.config.output, key):
                        setattr(self.config.output, key, value)

            # Merge server config
            if 'server' in data:
                for key, value in data['server'].items():
                    if hasattr(self.config.server, key):
                        setattr(self.config.server, key, value)

        except Exception as e:
            # Silently fail if config is invalid, use defaults
            pass

    def save_config(self, config_path: Optional[Path] = None) -> None:
        """Save current configuration to a YAML file"""

        if config_path is None:
            config_path = self.USER_CONFIG_PATH

        # Convert dataclasses to dict
        config_dict = {
            'analysis': asdict(self.config.analysis),
            'gpu': asdict(self.config.gpu),
            'output': asdict(self.config.output),
            'server': asdict(self.config.server),
        }

        # Create parent directory if needed
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Save to YAML
        with open(config_path, 'w') as f:
            yaml.safe_dump(
                config_dict,
                f,
                default_flow_style=False,
                sort_keys=False,
            )

    def create_default_config(self, config_path: Path) -> None:
        """Create a default configuration file with comments"""

        yaml_content = """# Z-Stack Analyzer Configuration
# This file configures default settings for the CLI tool

# Analysis settings
analysis:
  default_algorithm: segmentation_3d  # Default algorithm to use
  threshold: 0.5                      # Segmentation threshold (0.0-1.0)
  min_object_size: 100                # Minimum object size in pixels
  output_format: json                 # Output format (json, csv, hdf5)
  parallel_workers: 4                 # Number of parallel workers for batch processing

# GPU settings
gpu:
  enabled: true                       # Enable GPU acceleration
  device: null                        # GPU device (e.g., "cuda:0", "metal", null for auto)
  memory_limit_mb: null               # GPU memory limit in MB (null for no limit)
  fallback_to_cpu: true               # Fall back to CPU if GPU fails

# Output settings
output:
  default_directory: ./results        # Default output directory
  compression: null                   # Compression method (lzw, zip, jpeg, null)
  quality: 95                         # Compression quality (1-100)
  save_metadata: true                 # Save metadata alongside results
  verbose: false                      # Verbose output

# Server settings
server:
  host: 0.0.0.0                       # Server host
  port: 8000                          # Server port
  workers: 4                          # Number of worker processes
  log_level: info                     # Log level (debug, info, warning, error)
"""

        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(yaml_content)

    def get_value(self, section: str, key: str) -> Any:
        """Get a configuration value"""

        section_obj = getattr(self.config, section, None)
        if section_obj is None:
            return None

        return getattr(section_obj, key, None)

    def set_value(self, section: str, key: str, value: Any) -> None:
        """Set a configuration value"""

        section_obj = getattr(self.config, section, None)
        if section_obj is None:
            return

        if hasattr(section_obj, key):
            setattr(section_obj, key, value)


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get the global configuration manager"""
    global _config_manager

    if _config_manager is None:
        _config_manager = ConfigManager()

    return _config_manager


def reload_config() -> None:
    """Reload configuration from files"""
    global _config_manager
    _config_manager = ConfigManager()
