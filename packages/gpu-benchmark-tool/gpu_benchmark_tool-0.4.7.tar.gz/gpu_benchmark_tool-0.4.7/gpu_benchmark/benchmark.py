"""Benchmarking utilities for GPU Benchmark Tool.

This module provides functions to run full and multi-GPU benchmarks, generate summaries, and export results.
"""
import pynvml
PYNVML_AVAILABLE = False
from .monitor import stress_gpu_with_monitoring, enhanced_stress_test
from .scoring import score_gpu_health
from .diagnostics import get_gpu_info
from .backends import get_gpu_backend
from .utils import print_success, print_warning, print_error, print_info, ProgressBar, format_duration
import json
from datetime import datetime

def run_full_benchmark(handle, duration=60, enhanced=True, device_id=0):
    """
    Runs diagnostics, stress test, and scoring on a single GPU.

    Args:
        handle: NVML handle to the GPU (for backward compatibility).
        duration (int): Stress test duration in seconds.
        enhanced (bool): Use enhanced stress testing with more metrics.
        device_id (int): GPU device ID (default 0).

    Returns:
        dict: Full report with metadata, stress metrics, and score.
    """
    
    # Get GPU info
    info = get_gpu_info(handle)
    gpu_name = info.get('name', 'Unknown GPU')
    if isinstance(gpu_name, bytes):
        gpu_name = gpu_name.decode('utf-8')
    print_info(f"Starting benchmark for GPU {device_id} ({gpu_name})")
    
    # Run stress test
    if enhanced:
        # Use enhanced monitoring with backend detection
        # First check if enhanced monitoring requirements are met
        from .diagnostics import check_enhanced_monitoring_requirements
        requirements = check_enhanced_monitoring_requirements()
        
        if not requirements["enhanced_available"]:
            # Interactive handling of missing requirements
            if handle_enhanced_monitoring_failure(requirements):
                # User chose to install and retry
                requirements = check_enhanced_monitoring_requirements()
                if not requirements["enhanced_available"]:
                    print_warning("Enhanced monitoring still not available after installation.")
                    print_info("Running basic benchmark...")
                    metrics = stress_gpu_with_monitoring(handle, duration)
                else:
                    # Retry enhanced monitoring
                    try:
                        from .backends.nvidia import NVIDIABackend
                        backend = NVIDIABackend()
                        monitor = backend.create_monitor(device_id)
                        print_success("Enhanced monitoring enabled - running comprehensive stress tests")
                        metrics = enhanced_stress_test(monitor, duration, device_id)
                    except Exception as e:
                        print_error(f"Enhanced monitoring failed after installation: {e}")
                        print_info("Running basic benchmark...")
                        metrics = stress_gpu_with_monitoring(handle, duration)
            else:
                # User chose basic fallback
                print_info("Running basic benchmark...")
                metrics = stress_gpu_with_monitoring(handle, duration)
        else:
            # Requirements met, try enhanced monitoring
            try:
                from .backends.nvidia import NVIDIABackend
                backend = NVIDIABackend()
                monitor = backend.create_monitor(device_id)
                print_success("Enhanced monitoring enabled - running comprehensive stress tests")
                metrics = enhanced_stress_test(monitor, duration, device_id)
            except Exception as e:
                print_error(f"Enhanced monitoring failed: {e}")
                print_info("Running basic benchmark...")
                metrics = stress_gpu_with_monitoring(handle, duration)
    else:
        print_info("Running basic benchmark...")
        metrics = stress_gpu_with_monitoring(handle, duration)
    
    # Score GPU health
    if enhanced and "temperature_stability" in metrics:
        result = score_gpu_health(
            baseline_temp=metrics["baseline_temp"],
            max_temp=metrics["max_temp"],
            power_draw=metrics["max_power"],
            utilization=metrics.get("avg_utilization", metrics.get("utilization", -1)),
            throttled=len(metrics.get("throttle_events", [])) > 0,
            errors=len(metrics.get("errors", [])) > 0,
            throttle_events=metrics.get("throttle_events", []),
            temperature_stability=metrics.get("temperature_stability"),
            enhanced_metrics=metrics.get("stress_test_results")
        )
        if len(result) == 4:
            score, status, recommendation, details = result
        else:
            score, status, recommendation = result
            details = {}
    else:
        # Basic scoring for backward compatibility
        result = score_gpu_health(
            baseline_temp=metrics["baseline_temp"],
            max_temp=metrics["max_temp"],
            power_draw=metrics["max_power"],
            utilization=metrics["utilization"]
        )
        if len(result) == 4:
            score, status, recommendation, details = result
        else:
            score, status, recommendation = result
            details = {}
    
    # Build comprehensive report
    report = {
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.0",
            "duration": duration,
            "enhanced_mode": enhanced
        },
        "gpu_info": info,
        "metrics": metrics,
        "health_score": {
            "score": score,
            "status": status,
            "recommendation": recommendation,
            "details": details
        }
    }
    
    # Add enhanced test results if available
    if enhanced and "stress_test_results" in metrics:
        report["performance_tests"] = metrics["stress_test_results"]
    
    return report


def run_multi_gpu_benchmark(duration=60, enhanced=True):
    """
    Runs benchmark on all available GPUs.

    Args:
        duration (int): Stress test duration in seconds.
        enhanced (bool): Use enhanced stress testing with more metrics.

    Returns:
        dict: Results for all GPUs.
    """
    try:
        import pynvml
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
    except:
        print_error("NVIDIA GPU support not available")
        return {"error": "NVIDIA GPU support not available"}
    
    if device_count == 0:
        print_error("No NVIDIA GPUs found")
        return {"error": "No NVIDIA GPUs found"}
    
    print_success(f"Found {device_count} GPU(s) - starting benchmarks")
    
    results = {}
    
    # Create progress bar for multi-GPU benchmarks
    progress = ProgressBar(device_count, f"Benchmarking {device_count} GPU(s)", 40)
    
    for i in range(device_count):
        print_info(f"\nBenchmarking GPU {i}...")
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        
        try:
            result = run_full_benchmark(handle, duration, enhanced, i)
            results[f"gpu_{i}"] = result
            progress.update()
        except Exception as e:
            print_error(f"Failed to benchmark GPU {i}: {e}")
            results[f"gpu_{i}"] = {"error": str(e)}
            progress.update()
    
    progress.finish()
    print_success("All GPU benchmarks completed")
    
    return {
        "device_count": device_count,
        "results": results,
        "summary": _generate_summary(results)
    }


def _generate_summary(results):
    """Generates a summary of multi-GPU benchmark results.

    Args:
        results (dict): Dictionary of results for each GPU.

    Returns:
        dict: Summary statistics for the benchmark run.
    """
    summary = {
        "total_gpus": len(results),
        "healthy_gpus": 0,
        "warnings": [],
        "recommendations": []
    }
    
    for gpu_id, result in results.items():
        if "error" in result:
            summary["warnings"].append(f"{gpu_id}: {result['error']}")
            continue
        
        health = result.get("health_score", {})
        if health.get("status") in ["healthy", "good"]:
            summary["healthy_gpus"] += 1
        elif health.get("status") in ["warning", "critical", "degraded"]:
            summary["warnings"].append(
                f"{gpu_id}: {health.get('status')} - {health.get('recommendation')}"
            )
    
    summary["health_percentage"] = (summary["healthy_gpus"] / summary["total_gpus"]) * 100 if summary["total_gpus"] > 0 else 0
    
    return summary


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles NumPy and PyTorch data types."""
    
    def default(self, obj):
        import numpy as np
        import torch
        
        # Handle NumPy types
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        
        # Handle PyTorch tensors
        elif isinstance(obj, torch.Tensor):
            return obj.cpu().numpy().tolist()
        
        # Handle other non-serializable types
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)


def export_results(results, filename=None):
    """Exports benchmark results to a JSON file.

    Args:
        results (dict): Benchmark results to export.
        filename (str, optional): Output filename. If None, a timestamped filename is used.

    Returns:
        str: The filename to which results were exported.
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gpu_benchmark_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    
    print(f"Results exported to {filename}")
    return filename

def handle_enhanced_monitoring_failure(requirements):
    """Handles enhanced monitoring failure with interactive installation offers.
    
    Args:
        requirements (dict): Requirements check result from diagnostics.
        
    Returns:
        bool: True if user wants to retry enhanced, False for basic fallback.
    """
    missing_items = []
    install_commands = []
    
    # Check what's missing
    if not requirements["pynvml"]:
        missing_items.append("nvidia-ml-py")
        install_commands.append("pip install nvidia-ml-py")
    
    if not requirements["torch"]:
        missing_items.append("PyTorch")
        install_commands.append("pip install torch")
    
    if not requirements["cuda"]:
        missing_items.append("PyTorch with CUDA support")
        install_commands.append("pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    
    if not requirements["nvidia_gpu"]:
        missing_items.append("NVIDIA GPU detection")
        install_commands.append("Check NVIDIA drivers and run: nvidia-smi")
    
    if missing_items:
        print_warning(f"\nEnhanced monitoring not supported due to missing: {', '.join(missing_items)}")
        print_info("\nEnhanced monitoring provides:")
        print_info("  • Comprehensive stress tests")
        print_info("  • Detailed performance metrics")
        print_info("  • Advanced health scoring")
        print_info("\nOptions:")
        print_info("  y - Install missing packages and try enhanced tests")
        print_info("  n - Run basic benchmark (faster, fewer metrics)")
        print("Choice (y/n): ", end="")
        
        try:
            response = input().strip().lower()
            if response in ['y', 'yes']:
                print_info("\nInstalling missing packages...")
                import subprocess
                import sys
                
                for cmd in install_commands:
                    print_info(f"Running: {cmd}")
                    try:
                        result = subprocess.run(cmd.split(), capture_output=True, text=True)
                        if result.returncode == 0:
                            print_success(f"✓ Successfully installed")
                        else:
                            print_error(f"✗ Installation failed: {result.stderr}")
                    except Exception as e:
                        print_error(f"✗ Installation error: {e}")
                
                print_info("\nRetrying enhanced monitoring...")
                return True
            else:
                print_info("Running basic benchmark...")
                return False
        except (EOFError, KeyboardInterrupt):
            print_info("\nRunning basic benchmark...")
            return False
    else:
        # No missing items but still failed - likely backend issue
        print_warning("Enhanced monitoring failed due to backend issues.")
        print_info("Running basic benchmark...")
        return False
