"""GPU Benchmark Tool

This module initializes the GPU Benchmark Tool package, handling imports and platform-specific warnings.
"""

from .version import __version__

import platform
import warnings

# Handle imports based on platform
try:
    from .benchmark import run_full_benchmark
    from .diagnostics import get_gpu_info, print_temperature_thresholds
    from .monitor import stress_gpu_with_monitoring
    from .scoring import score_gpu_health
except ImportError as e:
    warnings.warn(f"Some modules could not be imported: {e}")

# Check if we're on macOS and provide helpful guidance
if platform.system() == "Darwin":
    # Only show warning if this is being run as a command line tool
    import sys
    # Check if any CLI commands are in the arguments
    cli_commands = ['benchmark', 'list', 'monitor', 'system-info', 'enhanced-status', 'diagnostics']
    has_cli_command = any(cmd in sys.argv for cmd in cli_commands)
    
    if has_cli_command:
        warnings.warn("Running on macOS - NVIDIA GPU support not available. Use --mock flag for testing.")

__all__ = [
    "__version__",
    "run_full_benchmark",
    "get_gpu_info", 
    "print_temperature_thresholds",
    "stress_gpu_with_monitoring",
    "score_gpu_health",
]
