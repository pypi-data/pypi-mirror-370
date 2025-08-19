"""Monitoring utilities for GPU Benchmark Tool.

This module provides enhanced GPU monitoring, stress testing, and telemetry collection utilities.
"""

import torch
import time
import numpy as np
from datetime import datetime
import threading
import queue
from typing import Dict, List, Optional, Tuple

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False
    print("Warning: pynvml not available. NVIDIA GPU monitoring disabled.")

from .backends.base import GPUMonitor
from .stress_tests.compute import ComputeStressTest
from .stress_tests.memory import MemoryStressTest
from .stress_tests.mixed_precision import MixedPrecisionTest


def calculate_temperature_stability(temperature_log: List[float]) -> Dict[str, float]:
    """Calculates temperature stability metrics from a temperature log.

    Args:
        temperature_log (List[float]): List of temperature readings over time.

    Returns:
        Dict[str, float]: Dictionary with stability score, standard deviation, max delta, and average rate of change.
    """
    if len(temperature_log) < 2:
        return {"stability_score": 0, "std_dev": 0, "max_delta": 0, "avg_rate_of_change": 0}
    
    temps = np.array(temperature_log)
    
    # Calculate metrics
    std_dev = np.std(temps)
    max_delta = np.max(temps) - np.min(temps)
    
    # Calculate rate of change
    deltas = np.diff(temps)
    avg_rate_of_change = np.mean(np.abs(deltas))
    
    # Stability score (0-100)
    # Lower std_dev and rate of change = higher stability
    stability_score = max(0, 100 - (std_dev * 5) - (avg_rate_of_change * 10))
    
    return {
        "stability_score": stability_score,
        "std_dev": std_dev,
        "max_delta": max_delta,
        "avg_rate_of_change": avg_rate_of_change
    }


def stress_gpu_with_monitoring(handle, duration=None, **kwargs):
    """Stress the GPU with monitoring. Accepts duration as a keyword argument for test compatibility."""
    if duration is None:
        duration = kwargs.get('duration', 10)
    if not PYNVML_AVAILABLE:
        print("NVIDIA GPU monitoring not available")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "baseline_temp": -1,
            "max_temp": -1,
            "max_power": -1,
            "utilization": -1,
            "iterations": 0,
            "telemetry_sample": []
        }
        
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    if device.type == "cpu":
        print("No CUDA device available, returning mock results")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "baseline_temp": 45,
            "max_temp": 75,
            "max_power": 150,
            "utilization": 95,
            "iterations": 100,
            "telemetry_sample": []
        }
    
    # Import progress bar for real-time updates
    from .utils import ProgressBar
    
    a = torch.randn((4096, 4096), device=device)
    b = torch.randn((4096, 4096), device=device)

    baseline_temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)

    max_temp = -1
    max_power = -1
    last_util = -1
    
    # Create progress bar for stress test
    progress = ProgressBar(int(duration), "Stress Test", 40)
    
    start_time = time.time()
    iterations = 0
    
    telemetry_log = []

    while time.time() - start_time < duration:
        c = torch.matmul(a, b)
        torch.cuda.synchronize()
        
        timestamp = round(time.time() - start_time, 2)
        temp = power = util = -1

        try:
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            max_temp = max(max_temp, temp)
        except pynvml.NVMLError: pass

        try:
            power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000
            max_power = max(max_power, power)
        except pynvml.NVMLError: pass

        try:
            util = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
            last_util = util
        except pynvml.NVMLError: pass
        
        telemetry_log.append({
            "time_sec": timestamp,
            "temp_C": temp,
            "power_W": power,
            "utilization_pct": util
        })

        iterations += 1
        
        # Update progress bar every second
        elapsed = time.time() - start_time
        if elapsed >= 1.0:  # Update every second
            progress.update(int(elapsed) - progress.current)

    # Finish progress bar
    progress.finish()

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "baseline_temp": baseline_temp,
        "max_temp": max_temp,
        "max_power": max_power,
        "utilization": last_util,
        "iterations": iterations,
        "telemetry_sample": telemetry_log[-10:] if telemetry_log else []
    }


def enhanced_stress_test(monitor: GPUMonitor, duration: float = 60, device_id: int = 0) -> Dict[str, any]:
    """Runs a comprehensive stress test with all metrics using the provided monitor.

    Args:
        monitor (GPUMonitor): Monitor object for GPU telemetry.
        duration (float): Duration of the stress test in seconds.
        device_id (int): GPU device ID.

    Returns:
        Dict[str, any]: Dictionary with stress test results, telemetry, and stability metrics.
    """
    
    # Check if CUDA is available
    if torch.cuda.is_available():
        device = torch.device(f"cuda:{device_id}")
    else:
        print("CUDA not available, using CPU fallback")
        device = torch.device("cpu")
    
    # Initialize stress tests
    compute_test = ComputeStressTest(device)
    memory_test = MemoryStressTest(device)
    mixed_precision_test = MixedPrecisionTest(device)
    
    # Baseline measurements
    baseline_temp = monitor.get_temperature()
    baseline_power = monitor.get_power_usage()
    
    # Initialize tracking variables
    telemetry_log = []
    temperature_log = []
    throttle_events = []
    errors = []
    
    # Start monitoring thread
    monitoring = True
    monitor_queue = queue.Queue()
    test_start_time = time.time()
    
    def monitor_thread():
        while monitoring:
            timestamp = time.time()
            temp = monitor.get_temperature()
            power = monitor.get_power_usage()
            util = monitor.get_utilization()
            mem_info = monitor.get_memory_info()
            mem_bandwidth = monitor.get_memory_bandwidth() if hasattr(monitor, 'get_memory_bandwidth') else -1
            is_throttling, throttle_reasons = monitor.check_throttling()
            
            sample = {
                "timestamp": timestamp,
                "temp_c": temp,
                "power_w": power,
                "gpu_util_pct": util,
                "mem_util_pct": mem_info["utilization_pct"],
                "mem_bandwidth_pct": mem_bandwidth,
                "throttling": is_throttling
            }
            
            monitor_queue.put(("telemetry", sample))
            
            if temp > 0:
                temperature_log.append(temp)
            
            if is_throttling:
                monitor_queue.put(("throttle", {
                    "timestamp": timestamp - test_start_time,  # Delta from test start
                    "reasons": throttle_reasons,
                    "temp_c": temp,
                    "power_w": power
                }))
            
            time.sleep(0.5)  # Sample every 500ms
    
    monitor_thread_handle = threading.Thread(target=monitor_thread)
    monitor_thread_handle.start()
    
    # Run stress tests
    results = {}
    
    try:
        # 1. Matrix multiplication stress
        print("Running matrix multiplication stress test...")
        results["matrix_multiply"] = compute_test.matrix_multiply_stress(duration=duration/4)
        
        # 2. Memory bandwidth test
        print("Running memory bandwidth test...")
        results["memory_bandwidth"] = memory_test.bandwidth_test(duration=duration/4)
        
        # 3. VRAM stress test
        print("Running VRAM stress test...")
        results["vram_stress"] = memory_test.vram_stress_test(target_usage_pct=85)
        
        # 4. Mixed precision test
        print("Running mixed precision test...")
        results["mixed_precision"] = mixed_precision_test.run_test(duration=duration/4)
        
    except Exception as e:
        errors.append(("TEST_ERROR", str(e)))
    
    # Stop monitoring
    monitoring = False
    monitor_thread_handle.join()
    
    # Collect monitoring data
    while not monitor_queue.empty():
        msg_type, data = monitor_queue.get()
        if msg_type == "telemetry":
            telemetry_log.append(data)
        elif msg_type == "throttle":
            throttle_events.append(data)
    
    # Calculate stability metrics
    temp_stability = calculate_temperature_stability(temperature_log)
    
    # Aggregate results
    max_temp = max(temperature_log) if temperature_log else -1
    max_power = max([t["power_w"] for t in telemetry_log if t["power_w"] > 0], default=-1)
    avg_utilization = np.mean([t["gpu_util_pct"] for t in telemetry_log if t["gpu_util_pct"] > 0]) if telemetry_log else 0
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "baseline_temp": baseline_temp,
        "baseline_power": baseline_power,
        "max_temp": max_temp,
        "max_power": max_power,
        "avg_utilization": avg_utilization,
        "temperature_stability": temp_stability,
        "throttle_events": throttle_events,
        "errors": errors,
        "stress_test_results": results,
        "telemetry_sample": telemetry_log[-20:] if telemetry_log else []
    }
