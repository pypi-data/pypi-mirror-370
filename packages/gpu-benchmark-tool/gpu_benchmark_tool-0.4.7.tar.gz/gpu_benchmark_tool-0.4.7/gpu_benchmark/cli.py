#!/usr/bin/env python3
"""Command Line Interface for GPU Benchmark Tool.

This module provides the command-line interface for running GPU benchmarks, diagnostics, and monitoring.
"""

import argparse
import json
import sys
import platform
from datetime import datetime, timezone

from .benchmark import run_full_benchmark
from .backends import list_available_backends
from .diagnostics import print_system_info, print_enhanced_monitoring_status, print_comprehensive_diagnostics
from .benchmark import run_multi_gpu_benchmark
from .utils import print_success, print_warning, print_error, print_info

from . import __version__

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False


def print_banner():
    """Prints the tool banner with version information."""
    print("=" * 60)
    print(f"GPU Benchmark Tool v{__version__}")
    print("=" * 60)


def print_gpu_info(info, mock_mode=False):
    """Pretty prints GPU information.

    Args:
        info (dict): Dictionary containing GPU information to display.
        mock_mode (bool): Whether we're in mock mode (affects the indicators).
    """
    print("\nGPU Information:")
    print("-" * 30)
    for key, value in info.items():
        # Add indicator for mock mode only
        if mock_mode:
            indicator = "🔴 SIMULATED" if "Mock" in str(value) else "🟢 REAL"
            print(f"{key:.<25} {value} {indicator}")
        else:
            print(f"{key:.<25} {value}")


def print_health_score(health, mock_mode=False):
    """Pretty prints the health score with color coding.

    Args:
        health (dict): Health assessment dictionary with score, status, recommendation, and details.
        mock_mode (bool): Whether we're in mock mode (affects the indicator).
    """
    score = health["score"]
    status = health["status"]
    
    # Use our color utility functions
    from .utils import print_success, print_warning, print_error, print_info
    
    print("\nHealth Assessment:")
    print("-" * 30)
    
    # Health scoring is simulated in mock mode, real otherwise
    mock_indicator = "🔴 SIMULATED" if mock_mode else ""
    
    # Color-code the score based on status
    if status in ["healthy", "good"]:
        print_success(f"Score: {score}/100", bold=True)
        print_success(f"Status: {status.upper()}", bold=True)
    elif status in ["degraded", "warning"]:
        print_warning(f"Score: {score}/100", bold=True)
        print_warning(f"Status: {status.upper()}", bold=True)
    elif status == "critical":
        print_error(f"Score: {score}/100", bold=True)
        print_error(f"Status: {status.upper()}", bold=True)
    else:
        print_info(f"Score: {score}/100", bold=True)
        print_info(f"Status: {status.upper()}", bold=True)
    
    print(f"Recommendation: {health['recommendation']}{' ' + mock_indicator if mock_mode else ''}")
    
    if "details" in health and "breakdown" in health["details"]:
        print("\nScore Breakdown:")
        for component, points in health["details"]["breakdown"].items():
            print(f"  {component:.<25} {points} points")
    
    if "details" in health and "specific_recommendations" in health["details"]:
        recs = health["details"]["specific_recommendations"]
        if recs:
            print("\nSpecific Recommendations:")
            for rec in recs:
                print(f"  • {rec}")


def print_test_results(results, mock_mode=False):
    """Pretty prints stress test results.

    Args:
        results (dict): Dictionary containing results from various stress tests.
        mock_mode (bool): Whether we're in mock mode (affects the indicators).
    """
    if "matrix_multiply" in results:
        print("\nMatrix Multiplication Test:")
        mm = results["matrix_multiply"]
        indicator = " 🟢 REAL" if mock_mode else ""
        print(f"  Performance: {mm['tflops']:.2f} TFLOPS{indicator}")
        print(f"  Iterations: {mm['iterations']}{indicator}")
    
    if "memory_bandwidth" in results:
        print("\nMemory Bandwidth Test:")
        mb = results["memory_bandwidth"]
        indicator = " 🟢 REAL" if mock_mode else ""
        print(f"  Bandwidth: {mb['bandwidth_gbps']:.2f} GB/s{indicator}")
    
    if "mixed_precision" in results:
        print("\nMixed Precision Support:")
        mp = results["mixed_precision"]
        
        # FP32 is always real
        if mp.get("fp32", {}).get("supported"):
            tflops = mp["fp32"].get("tflops", 0)
            indicator = " 🟢 REAL" if mock_mode else ""
            print(f"  FP32: Baseline ({tflops:.2f} TFLOPS){indicator}")
        else:
            indicator = " 🟢 REAL" if mock_mode else ""
            print(f"  FP32: Not available{indicator}")
        
        # FP16 - check hardware and runtime support
        fp16 = mp.get("fp16", {})
        hw_supported = fp16.get("hardware_supported", False)
        rt_supported = fp16.get("runtime_supported", False)
        
        if hw_supported and rt_supported:
            tflops = fp16.get("tflops", 0)
            speedup = mp.get("fp16_speedup", 0)
            indicator = " 🟡 HARDWARE-DEPENDENT" if mock_mode else ""
            print(f"  FP16: Hardware ✅ Runtime ✅ ({speedup:.2f}x speedup, {tflops:.2f} TFLOPS){indicator}")
        elif hw_supported and not rt_supported:
            error = fp16.get("error", "Runtime failed")
            indicator = " 🟡 HARDWARE-DEPENDENT" if mock_mode else ""
            print(f"  FP16: Hardware ✅ Runtime ❌ ({error}){indicator}")
        else:
            indicator = " 🟡 HARDWARE-DEPENDENT" if mock_mode else ""
            print(f"  FP16: Hardware ❌ Runtime ❌ (Not supported){indicator}")
        
        # BF16 - check hardware and runtime support
        bf16 = mp.get("bf16", {})
        hw_supported = bf16.get("hardware_supported", False)
        rt_supported = bf16.get("runtime_supported", False)
        
        if hw_supported and rt_supported:
            tflops = bf16.get("tflops", 0)
            speedup = mp.get("bf16_speedup", 0)
            indicator = " 🟡 HARDWARE-DEPENDENT" if mock_mode else ""
            print(f"  BF16: Hardware ✅ Runtime ✅ ({speedup:.2f}x speedup, {tflops:.2f} TFLOPS){indicator}")
        elif hw_supported and not rt_supported:
            error = bf16.get("error", "Runtime failed")
            indicator = " 🟡 HARDWARE-DEPENDENT" if mock_mode else ""
            print(f"  BF16: Hardware ✅ Runtime ❌ ({error}){indicator}")
        else:
            indicator = " 🟡 HARDWARE-DEPENDENT" if mock_mode else ""
            print(f"  BF16: Hardware ❌ Runtime ❌ (Not supported){indicator}")
        
        # INT8 - check hardware and runtime support
        int8 = mp.get("int8", {})
        hw_supported = int8.get("hardware_supported", False)
        rt_supported = int8.get("runtime_supported", False)
        method = int8.get("method", "unknown")
        
        if hw_supported and rt_supported:
            tflops = int8.get("tflops", 0)
            speedup = mp.get("int8_speedup", 0)
            note = int8.get("note", "")
            indicator = " 🟡 HARDWARE-DEPENDENT" if mock_mode else ""
            print(f"  INT8: Hardware ✅ Runtime ✅ ({speedup:.2f}x speedup, {tflops:.2f} TFLOPS via {method}){indicator}")
            if note and mock_mode:
                print(f"           📝 Note: {note}")
        elif hw_supported and not rt_supported:
            error = int8.get("error", "Runtime failed")
            solution = int8.get("solution", "")
            note = int8.get("note", "")
            indicator = " 🟡 HARDWARE-DEPENDENT" if mock_mode else ""
            print(f"  INT8: Hardware ✅ Runtime ❌ ({error}){indicator}")
            if note and mock_mode:
                print(f"           📝 Note: {note}")
            if solution and mock_mode:
                print(f"           💡 Solution: {solution}")
        else:
            indicator = " 🟡 HARDWARE-DEPENDENT" if mock_mode else ""
            print(f"  INT8: Hardware ❌ Runtime ❌ (Not supported){indicator}")


def run_mock_benchmark(args):
    """Runs the benchmark in mock mode (simulated GPU).

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    print("\nRunning in mock mode (simulated GPU)...")
    print("=" * 60)
    print("🔴 SIMULATED: GPU monitoring, health scoring")
    print("🟢 REAL: Computational performance, memory bandwidth")
    print("🟡 HARDWARE-DEPENDENT: Mixed precision (FP32=real, FP16/BF16/INT8=hardware-dependent)")
    print("=" * 60)
    
    from .backends.mock import MockBackend
    from .backends import get_gpu_backend
    from .monitor import enhanced_stress_test
    from .scoring import score_gpu_health
    
    # Use mock backend
    backend = MockBackend()
    monitor = backend.create_monitor(0)
    
    # Get mock GPU info
    gpu_info = backend.get_device_info(0)
    
    # Run enhanced stress test with mock monitor
    print("Running simulated stress tests...")
    print("(This will take about {} seconds)".format(args.duration))
    
    try:
        import torch
        # Check if we can use CPU at least
        device = torch.device("cpu")
        metrics = enhanced_stress_test(monitor, args.duration, 0)
        
        # Score the results
        result = score_gpu_health(
            baseline_temp=metrics.get("baseline_temp", 45),
            max_temp=metrics.get("max_temp", 75),
            power_draw=metrics.get("max_power", 150),
            utilization=metrics.get("avg_utilization", 95),
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
            
        # Build report
        report = {
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": __version__,
                "duration": args.duration,
                "enhanced_mode": not args.basic,
                "mock_mode": True
            },
            "gpu_info": gpu_info,
            "metrics": metrics,
            "health_score": {
                "score": score,
                "status": status,
                "recommendation": recommendation,
                "details": details
            }
        }
        
        if not args.basic and "stress_test_results" in metrics:
            report["performance_tests"] = metrics["stress_test_results"]
            
    except ImportError:
        # Torch not available, create simple mock results
        print("Note: PyTorch not installed, using simplified mock results")
        report = {
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": __version__,
                "duration": args.duration,
                "mock_mode": True
            },
            "gpu_info": gpu_info,
            "health_score": {
                "score": 85,
                "status": "healthy",
                "recommendation": "Mock GPU performing well in simulation mode"
            },
            "metrics": {
                "max_temp": 72,
                "max_power": 150,
                "baseline_temp": 45,
                "avg_utilization": 95
            }
        }
    
    # Print results
    print_gpu_info(report["gpu_info"], mock_mode=True)
    
    # Skip health assessment in mock mode since it's completely simulated
    # print_health_score(report["health_score"], mock_mode=True)
    
    if not args.basic and "performance_tests" in report:
        print_test_results(report["performance_tests"], mock_mode=True)
    
    # Export if requested
    if args.export is not None:
        if args.export == '':
            # Auto-generate filename
            from .benchmark import export_results
            filename = export_results(report)
        else:
            # Use provided filename
            with open(args.export, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nResults exported to {args.export}")
    
    return 0


def cmd_benchmark(args):
    """Runs the benchmark command.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    
    # Handle mock mode separately
    if args.mock:
        return run_mock_benchmark(args)
    
    # Real GPU benchmark
    if not PYNVML_AVAILABLE:
        print("Error: pynvml is required for GPU benchmarking")
        print("Install with: pip install nvidia-ml-py torch")
        print("Or use --mock flag for simulation mode")
        return 1
    
    # Check for enhanced monitoring requirements
    if args.enhanced:
        try:
            import torch
            if not torch.cuda.is_available():
                print("Warning: Enhanced monitoring requires CUDA support")
                print("Install PyTorch with CUDA: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
                print("Continuing with basic monitoring...")
                args.enhanced = False
        except ImportError:
            print("Warning: PyTorch not available for enhanced monitoring")
            print("Install with: pip install torch")
            print("Continuing with basic monitoring...")
            args.enhanced = False
    
    try:
        pynvml.nvmlInit()
    except pynvml.NVMLError as e:
        print_error(f"Error initializing NVML: {e}")
        
        # Platform-specific guidance
        if platform.system() == "Darwin":
            print_error("NVIDIA GPU support is not available on macOS")
            print_info("Use --mock flag for simulation mode")
            print_info("For real GPU testing, consider using Linux or Windows")
        else:
            print_error("Make sure NVIDIA drivers are installed and nvidia-smi works")
            print_info("Or use --mock flag for simulation mode")
        
        return 1
    
    from .benchmark import run_full_benchmark, run_multi_gpu_benchmark, export_results
    from .backends import list_available_backends
    from .diagnostics import print_system_info
    # from .utils import print_success, print_warning, print_error, print_info # Moved to top
    
    # Single GPU benchmark
    if args.gpu_id is not None:
        device_count = pynvml.nvmlDeviceGetCount()
        if args.gpu_id >= device_count:
            print_error(f"Error: GPU {args.gpu_id} not found. Found {device_count} GPU(s)")
            return 1
        
        print(f"\nBenchmarking GPU {args.gpu_id}...")
        handle = pynvml.nvmlDeviceGetHandleByIndex(args.gpu_id)
        
        # Show temperature thresholds if verbose
        if args.verbose:
            from .diagnostics import print_temperature_thresholds
            print_temperature_thresholds(handle)
        
        # Run benchmark
        enhanced_mode = args.enhanced or (not args.basic)
        result = run_full_benchmark(
            handle, 
            duration=args.duration,
            enhanced=enhanced_mode,
            device_id=args.gpu_id
        )
        
        # Print results
        print_gpu_info(result["gpu_info"], mock_mode=False)
        print_health_score(result["health_score"], mock_mode=False)
        
        if not args.basic and "performance_tests" in result:
            print_test_results(result["performance_tests"], mock_mode=False)
        
        # Export if requested
        if args.export is not None:
            if args.export == '':
                # Auto-generate filename
                filename = export_results(result)
            else:
                # Use provided filename
                filename = export_results(result, args.export)
            print(f"\nResults exported to: {filename}")
    
    # Multi-GPU benchmark
    else:
        print("\nBenchmarking all GPUs...")
        enhanced_mode = args.enhanced or (not args.basic)
        results = run_multi_gpu_benchmark(
            duration=args.duration,
            enhanced=enhanced_mode
        )
        
        if "error" in results:
            print_error(f"Error: {results['error']}")
            return 1
            
        print(f"\nFound {results['device_count']} GPU(s)")
        
        for gpu_id, result in results["results"].items():
            print(f"\n{'='*60}")
            print(f"GPU {gpu_id}")
            print('='*60)
            
            if "error" in result:
                print(f"Error: {result['error']}")
                continue
            
            print_gpu_info(result["gpu_info"], mock_mode=False)
            print_health_score(result["health_score"], mock_mode=False)
            
            if not args.basic and "performance_tests" in result:
                print_test_results(result["performance_tests"], mock_mode=False)
        
        # Print summary
        summary = results["summary"]
        print(f"\n{'='*60}")
        print("SUMMARY")
        print('='*60)
        print(f"Total GPUs: {summary['total_gpus']}")
        print(f"Healthy GPUs: {summary['healthy_gpus']} ({summary['health_percentage']:.1f}%)")
        
        if summary["warnings"]:
            print("\nWarnings:")
            for warning in summary["warnings"]:
                print(f"  • {warning}")
        
        # Export if requested
        if args.export is not None:
            if args.export == '':
                # Auto-generate filename
                filename = export_results(results)
            else:
                # Use provided filename
                filename = export_results(results, args.export)
            print(f"\nResults exported to: {filename}")
    
    return 0


def cmd_list(args):
    """Lists available GPUs and backends."""
    from .backends import list_available_backends
    backends = list_available_backends()
    if not backends:
        print("No supported GPU backends found!")
        print("\nOptions:")
        print("  1. Install NVIDIA support: pip install gpu-benchmark-tool[nvidia]")
        print("  2. Use mock mode: gpu-benchmark benchmark --mock")
        return 1
    for backend in backends:
        print(f"\n{backend['type'].upper()} Backend:")
        print(f"  Devices: {backend['device_count']}")
    if PYNVML_AVAILABLE:
        try:
            pynvml.nvmlInit()
            count = pynvml.nvmlDeviceGetCount()
            print("\nNVIDIA GPUs:")
            for i in range(count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode('utf-8')
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                print(f"  [{i}] {name} ({mem_info.total / 1e9:.1f} GB)")
        except pynvml.NVMLError:
            pass
    return 0


def cmd_monitor(args):
    """Real-time monitoring (basic version).

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    if args.mock:
        print("Mock monitoring not implemented yet")
        return 1
        
    if not PYNVML_AVAILABLE:
        print("Error: pynvml is required for monitoring")
        return 1
    
    import time
    
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(args.gpu_id or 0)
        
        print(f"Monitoring GPU {args.gpu_id or 0} (Press Ctrl+C to stop)...")
        print("-" * 60)
        
        while True:
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            print(f"\rTemp: {temp}°C | Power: {power:.1f}W | "
                  f"GPU: {util.gpu}% | Mem: {util.memory}% | "
                  f"VRAM: {mem_info.used/1e9:.1f}/{mem_info.total/1e9:.1f} GB", 
                  end='', flush=True)
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
    except pynvml.NVMLError as e:
        print(f"\nError: {e}")
        return 1
    
    return 0


def main():
    """Main CLI entry point.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description="GPU Benchmark Tool - Comprehensive GPU health monitoring and optimization"
    )
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Benchmark command
    bench_parser = subparsers.add_parser('benchmark', help='Run GPU benchmark')
    bench_parser.add_argument(
        '--gpu-id', '-g', type=int, 
        help='Specific GPU to benchmark (default: all GPUs)'
    )
    bench_parser.add_argument(
        '--duration', '-d', type=int, default=60,
        help='Test duration in seconds (default: 60)'
    )
    bench_parser.add_argument(
        '--basic', '-b', action='store_true',
        help='Run basic tests only (faster)'
    )
    bench_parser.add_argument(
        '--enhanced', '-E', action='store_true',
        help='Force enhanced monitoring (comprehensive stress tests)'
    )
    bench_parser.add_argument(
        '--export', '-e', type=str, nargs='?', const='',
        help='Export results to JSON file (auto-generates filename if not provided)'
    )
    bench_parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Verbose output'
    )
    bench_parser.add_argument(
        '--mock', '-m', action='store_true',
        help='Use mock GPU (for testing/development)'
    )
    bench_parser.set_defaults(func=cmd_benchmark)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available GPUs')
    list_parser.set_defaults(func=cmd_list)
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Real-time GPU monitoring')
    monitor_parser.add_argument(
        '--gpu-id', '-g', type=int,
        help='GPU to monitor (default: 0)'
    )
    monitor_parser.add_argument(
        '--mock', '-m', action='store_true',
        help='Use mock GPU (for testing/development)'
    )
    monitor_parser.set_defaults(func=cmd_monitor)
    
    # System info command
    sysinfo_parser = subparsers.add_parser('system-info', help='Show baseline system information')
    sysinfo_parser.set_defaults(func=lambda args: print_system_info() or 0)
    
    # Enhanced monitoring status command
    enhanced_parser = subparsers.add_parser('enhanced-status', help='Check enhanced monitoring requirements')
    enhanced_parser.set_defaults(func=lambda args: print_enhanced_monitoring_status() or 0)
    
    # Comprehensive diagnostics command
    comprehensive_parser = subparsers.add_parser('diagnostics', help='Comprehensive GPU diagnostics and version check')
    comprehensive_parser.set_defaults(func=lambda args: print_comprehensive_diagnostics() or 0)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Print banner and system info at the start
    print_banner()
    print_system_info()
    
    # Add note about system info being real
    print("\n📊 System Information: All data is REAL (hardware detection)")
    
    # Execute command
    if args.command is None:
        parser.print_help()
        return 0
    
    # For system-info, just print and exit
    if args.command == 'system-info':
        return 0
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
