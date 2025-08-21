"""
evlib: Event Camera Data Processing Library

A robust event camera processing library with Python-first representations and Rust backend.

## Core Features

- **Universal Format Support**: Load data from H5, AEDAT, EVT2/3, AER, and text formats
- **Automatic Format Detection**: No need to specify format types manually
- **Polars DataFrame Support**: High-performance DataFrame operations
- **Pure Python Representations**: Efficient event-to-representation conversion with direct Polars API
- **Rust Performance**: Memory-safe, high-performance backend with Python bindings

## Quick Start

```python
import evlib
import polars as pl

# Load events as Polars LazyFrame
events = evlib.load_events("path/to/your/data.h5")

# Fast filtering using Polars expressions
filtered = events.filter(
    (pl.col("t").dt.total_microseconds() / 1_000_000 > 0.1) &
    (pl.col("t").dt.total_microseconds() / 1_000_000 < 0.2) &
    (pl.col("polarity") == 1)
)

# Or use Rust filtering functions directly
filtered = evlib.filtering.filter_by_time(events, t_start=0.1, t_end=0.2)
filtered = evlib.filtering.filter_by_polarity(filtered, polarity=1)

# Create representations
histogram = evlib.create_stacked_histogram(filtered, height=480, width=640)

# Direct access to Rust formats module (returns NumPy arrays)
x, y, t, p = evlib.formats.load_events("path/to/your/data.h5")
```

## Available Modules

- `evlib.formats`: Data loading and format detection
- `evlib.filtering`: High-performance event filtering
- `evlib.representations`: Event-to-representation conversion
- `evlib.simulation`: Event camera simulation (ESIM algorithm for video-to-events)
- `evlib.visualization`: Event visualization tools
- `evlib.models`: Deep learning models (E2VID, RVT)
- `evlib.core`: Core data structures and utilities

"""

import os

# Import the compiled Rust extension module
try:
    import importlib.util
    import glob

    # Find the compiled module file
    current_dir = os.path.dirname(__file__)
    so_files = glob.glob(os.path.join(current_dir, "evlib.cpython-*.so"))

    if so_files:
        spec = importlib.util.spec_from_file_location("evlib", so_files[0])
        rust_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rust_module)

        # CRITICAL FIX: Make this module appear as a package so Python allows submodule imports
        import sys

        current_module = sys.modules[__name__]
        if not hasattr(current_module, "__path__"):
            current_module.__path__ = [current_dir]

        # Access submodules from the compiled module
        core = rust_module.core
        formats = rust_module.formats
        rust_filtering = rust_module.filtering

        # CRITICAL: Register submodules in sys.modules so they can be imported with dot notation
        sys.modules[__name__ + ".core"] = core
        sys.modules[__name__ + ".formats"] = formats
        # Don't register Rust filtering yet - we'll decide below

        # Make key functions directly accessible
        save_events_to_hdf5 = formats.save_events_to_hdf5
        save_events_to_text = formats.save_events_to_text
        detect_format = formats.detect_format
        get_format_description = formats.get_format_description
    else:
        raise ImportError("Compiled Rust module not found")

except ImportError as e:
    raise ImportError(f"Failed to import evlib Rust module: {e}")

# Configure Polars GPU acceleration if available
try:
    import polars as pl

    def _configure_polars_engine():
        """Configure Polars engine with GPU support and graceful fallback to streaming."""
        # Check if GPU is explicitly requested
        gpu_engine_requested = os.environ.get("POLARS_ENGINE_AFFINITY", "").lower() == "gpu"

        if gpu_engine_requested:
            try:
                # Try to set GPU engine if requested via environment variable
                pl.Config.set_engine_affinity("gpu")
                return "gpu"
            except Exception:
                pass

        # Auto-detect and try GPU engine if available (only if not explicitly requested)
        if not gpu_engine_requested:
            # Only enable GPU mode for NVIDIA CUDA GPUs
            import subprocess

            try:
                # Check if nvidia-smi is available (indicates NVIDIA GPU)
                subprocess.run(["nvidia-smi"], capture_output=True, check=True)

                # Test if GPU operations work with Polars
                test_df = pl.DataFrame({"test": [1, 2, 3]})
                pl.Config.set_engine_affinity("gpu")
                _ = test_df.select(pl.col("test") * 2)
                return "gpu"
            except (subprocess.CalledProcessError, FileNotFoundError, Exception):
                # NVIDIA GPU not available, set streaming engine
                pass

        # NVIDIA GPU not available, set streaming engine for optimal performance
        pl.Config.set_engine_affinity("streaming")
        return "streaming"

    # Configure the engine and store result
    _engine_type = _configure_polars_engine()
    _gpu_available = _engine_type == "gpu"

except ImportError:
    _gpu_available = False
    _engine_type = "streaming"

# Import Python representations module (migration from Rust PyO3 to pure Python)
try:
    from . import representations
except ImportError:
    representations = None

# Import Python filtering module (migration from Rust PyO3 to pure Python)
try:
    from . import filtering as python_filtering
except ImportError:
    python_filtering = None

# Import optional Python-only submodules with graceful fallback
try:
    from . import models
except ImportError:
    models = None

try:
    from . import visualization
except ImportError:
    visualization = None

try:
    from . import simulation
except ImportError:
    simulation = None


# Make representation functions directly accessible for backwards compatibility
if representations:
    # Debug: Check if we're entering this block
    import os

    if os.environ.get("DEBUG_EVLIB"):
        print(f"DEBUG: representations is available: {representations}")
        print(
            f"DEBUG: representations has preprocess_for_detection: {hasattr(representations, 'preprocess_for_detection')}"
        )

    # Explicitly assign to module namespace
    globals()["create_stacked_histogram"] = representations.create_stacked_histogram
    globals()["create_mixed_density_stack"] = representations.create_mixed_density_stack
    globals()["create_voxel_grid"] = representations.create_voxel_grid
    globals()["preprocess_for_detection"] = representations.preprocess_for_detection
    globals()["benchmark_vs_rvt"] = representations.benchmark_vs_rvt

    # Register Python representations module in sys.modules
    sys.modules[__name__ + ".representations"] = representations

    if os.environ.get("DEBUG_EVLIB"):
        print(f"DEBUG: globals() now has preprocess_for_detection: {'preprocess_for_detection' in globals()}")

# Choose filtering module: Python implementation preferred over Rust
if python_filtering:
    # Use Python filtering module
    filtering = python_filtering

    # Register Python filtering module in sys.modules
    sys.modules[__name__ + ".filtering"] = python_filtering

    if os.environ.get("DEBUG_EVLIB"):
        print("DEBUG: Using Python filtering module")
else:
    # Fallback to Rust filtering module
    filtering = rust_filtering

    # Register Rust filtering module in sys.modules
    sys.modules[__name__ + ".filtering"] = rust_filtering

    if os.environ.get("DEBUG_EVLIB"):
        print("DEBUG: Using Rust filtering module (Python not available)")


try:
    from . import streaming_utils
except ImportError:
    streaming_utils = None

try:
    from . import pytorch
except ImportError:
    pytorch = None

# Import version
try:
    __version__ = getattr(formats, "__version__", None)
    if not __version__:
        raise ImportError("Version not found in compiled module")
except ImportError:
    # Fallback to reading from Cargo.toml
    import pathlib

    try:
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                # Manual parsing fallback
                import re

                _cargo_toml_path = pathlib.Path(__file__).parent.parent.parent / "Cargo.toml"
                with open(_cargo_toml_path, "r") as f:
                    content = f.read()
                version_match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
                if version_match:
                    __version__ = version_match.group(1)
                else:
                    __version__ = "unknown"
                raise ImportError  # Skip the tomllib parsing below

        _cargo_toml_path = pathlib.Path(__file__).parent.parent.parent / "Cargo.toml"
        with open(_cargo_toml_path, "rb") as f:
            _cargo_data = tomllib.load(f)
        __version__ = _cargo_data["package"]["version"]
    except (FileNotFoundError, KeyError, AttributeError):
        __version__ = "unknown"


def get_recommended_engine():
    """
    Get the recommended Polars engine for evlib operations.

    Returns:
        str: 'gpu' if GPU is available, otherwise 'streaming' for large datasets
    """
    return _engine_type if _engine_type == "gpu" else "streaming"


def collect_with_optimal_engine(lazy_frame):
    """
    Collect a Polars LazyFrame using the optimal engine for evlib operations.

    Args:
        lazy_frame: Polars LazyFrame to collect

    Returns:
        Polars DataFrame
    """
    engine = get_recommended_engine()
    return lazy_frame.collect(engine=engine)


def setup_hdf5_plugins():
    """
    Set up HDF5 compression plugins for reading Prophesee files.

    Call this function before loading Prophesee HDF5 files if you encounter
    plugin-related errors.

    Returns:
        bool: True if setup was successful, False otherwise
    """
    try:
        import hdf5plugin

        # Set the environment variable
        os.environ["HDF5_PLUGIN_PATH"] = hdf5plugin.PLUGIN_PATH

        # Register plugins if available
        if hasattr(hdf5plugin, "register"):
            hdf5plugin.register()

        return True

    except ImportError:
        return False
    except Exception:
        return False


def diagnose_hdf5(file_path=None):
    """
    Diagnose HDF5 plugin setup and test a file if provided.

    Args:
        file_path: Optional path to Prophesee HDF5 file to test
    """
    print("HDF5 Plugin Diagnostic")
    print("=" * 50)

    # Check if hdf5plugin is available
    try:
        import hdf5plugin

        print("✓ hdf5plugin is installed")
        print(f"  Version: {hdf5plugin.version}")
        print(f"  Plugin path: {hdf5plugin.PLUGIN_PATH}")

        # Set up environment
        os.environ["HDF5_PLUGIN_PATH"] = hdf5plugin.PLUGIN_PATH
        if hasattr(hdf5plugin, "register"):
            hdf5plugin.register()
        print("✓ HDF5 plugins configured")

    except ImportError:
        print("✗ hdf5plugin not installed")
        print("  Fix: pip install hdf5plugin")
        return

    # Check h5py
    try:
        import h5py

        print(f"✓ h5py version: {h5py.version.version}")
    except ImportError:
        print("✗ h5py not installed")
        print("  Fix: pip install h5py")
        return

    # Test file if provided
    if file_path:
        try:
            with h5py.File(file_path, "r") as f:
                if "CD" in f and "events" in f["CD"]:
                    print(f"✓ Successfully opened Prophesee file: {file_path}")
                    print(f"  Events: {len(f['CD']['events']):,}")
                else:
                    print(f"✓ Opened HDF5 file (not Prophesee format): {file_path}")
        except Exception as e:
            print(f"✗ Cannot read file: {e}")

    print("\nFor Prophesee files, ensure:")
    print("  1. pip install hdf5plugin h5py")
    print("  2. Set HDF5_PLUGIN_PATH environment variable")
    print("  3. Use evlib.setup_hdf5_plugins() before loading")


def load_events(path, **kwargs):
    """
    Load events as Polars LazyFrame.

    Args:
        path: Path to event file
        **kwargs: Additional arguments (t_start, t_end, min_x, max_x, min_y, max_y, polarity, sort, etc.)

    Returns:
        Polars LazyFrame with columns [x, y, t, polarity]
        - t is always converted to Duration type in microseconds

    Example:
        # Basic loading
        events = evlib.load_events("data.h5")

        # For validation, use the validation module explicitly:
        # from evlib.validation import quick_validate_events
        # is_valid = quick_validate_events(events)
    """
    # Load data using Rust formats module - this returns a LazyFrame directly
    lazy_frame = formats.load_events(path, **kwargs)

    # The Rust module already returns the LazyFrame with correct schema and column names
    # Just return it directly - no need for Python-side conversion
    return lazy_frame


# Define exports
__all__ = [
    "__version__",
    "core",
    "formats",
    "load_events",
    "save_events_to_hdf5",
    "save_events_to_text",
    "detect_format",
    "get_format_description",
    "get_recommended_engine",
    "collect_with_optimal_engine",
    "setup_hdf5_plugins",
    "diagnose_hdf5",
]

# Add optional modules to exports if available
if models:
    __all__.append("models")
if representations:
    __all__.extend(
        [
            "representations",
            "create_stacked_histogram",
            "create_mixed_density_stack",
            "create_voxel_grid",
            "preprocess_for_detection",
            "benchmark_vs_rvt",
        ]
    )
if filtering:
    __all__.append("filtering")
if visualization:
    __all__.append("visualization")


if streaming_utils:
    __all__.append("streaming_utils")
if pytorch:
    __all__.append("pytorch")
if simulation:
    __all__.append("simulation")
