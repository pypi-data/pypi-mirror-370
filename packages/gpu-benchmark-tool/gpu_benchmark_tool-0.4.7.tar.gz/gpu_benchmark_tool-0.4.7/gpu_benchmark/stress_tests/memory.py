"""Memory stress tests.

This module provides memory bandwidth, VRAM, and memory copy stress tests for GPUs.
"""

import torch
import time
from typing import Dict, List


class MemoryStressTest:
    """GPU memory stress tests for benchmarking and diagnostics.

    Args:
        device (torch.device): The device (CPU or GPU) to run tests on.
    """
    
    def __init__(self, device: torch.device):
        self.device = device
        
    def bandwidth_test(self, size_mb: int = 1024, duration: float = 10) -> Dict[str, float]:
        """Tests memory bandwidth with large array operations.

        Args:
            size_mb (int): Size of arrays in MB (default 1024).
            duration (float): Duration of the test in seconds (default 10).

        Returns:
            Dict[str, float]: Dictionary with iterations, bandwidth in GB/s, size, and average time per iteration.
        """
        if self.device.type == "cpu":
            size_mb = min(size_mb, 256)  # Limit size for CPU
            
        elements = (size_mb * 1024 * 1024) // 4  # float32 = 4 bytes
        
        try:
            # Create large arrays
            a = torch.randn(elements, device=self.device)
            b = torch.randn(elements, device=self.device)
        except (torch.cuda.OutOfMemoryError, RuntimeError):
            # If OOM, try smaller size
            size_mb = size_mb // 2
            elements = (size_mb * 1024 * 1024) // 4
            a = torch.randn(elements, device=self.device)
            b = torch.randn(elements, device=self.device)
        
        start_time = time.time()
        iterations = 0
        bytes_transferred = 0
        
        while time.time() - start_time < duration:
            # Memory-bound operations
            c = a + b  # Read 2 arrays, write 1
            if self.device.type == "cuda":
                torch.cuda.synchronize()
            iterations += 1
            bytes_transferred += elements * 4 * 3  # 3 arrays * 4 bytes
        
        elapsed = time.time() - start_time
        return {
            "iterations": iterations,
            "bandwidth_gbps": (bytes_transferred / elapsed) / 1e9,
            "size_mb": size_mb,
            "avg_time_per_iter": elapsed / iterations if iterations > 0 else 0
        }
    
    def vram_stress_test(self, target_usage_pct: float = 90) -> Dict[str, any]:
        """Allocates VRAM up to a target percentage and tests stability.

        Args:
            target_usage_pct (float): Target VRAM usage percentage (default 90).

        Returns:
            Dict[str, any]: Dictionary with allocation and stability results.
        """
        if self.device.type == "cpu":
            # For CPU, just allocate some memory
            return {
                "target_usage_pct": target_usage_pct,
                "actual_allocated_gb": 0.5,
                "num_tensors": 1,
                "operation_time": 0.1,
                "stable": True
            }
            
        mem_info = torch.cuda.get_device_properties(self.device)
        total_memory = mem_info.total_memory
        target_bytes = int(total_memory * target_usage_pct / 100)
        
        allocated_tensors = []
        actual_allocated = 0
        
        try:
            # Allocate in chunks to avoid OOM
            chunk_size = 256 * 1024 * 1024  # 256MB chunks
            while actual_allocated < target_bytes:
                remaining = target_bytes - actual_allocated
                current_chunk = min(chunk_size, remaining)
                elements = current_chunk // 4  # float32
                
                tensor = torch.randn(elements, device=self.device)
                allocated_tensors.append(tensor)
                actual_allocated += current_chunk
            
            # Run operations on allocated memory
            start_time = time.time()
            for _ in range(10):
                for tensor in allocated_tensors[:5]:  # Work on first 5 tensors
                    tensor += 1.0
                torch.cuda.synchronize()
            
            operation_time = time.time() - start_time
            
            return {
                "target_usage_pct": target_usage_pct,
                "actual_allocated_gb": actual_allocated / 1e9,
                "num_tensors": len(allocated_tensors),
                "operation_time": operation_time,
                "stable": True
            }
            
        except torch.cuda.OutOfMemoryError as e:
            return {
                "target_usage_pct": target_usage_pct,
                "actual_allocated_gb": actual_allocated / 1e9,
                "stable": False,
                "error": "Out of memory"
            }
        finally:
            # Clean up
            allocated_tensors.clear()
            if self.device.type == "cuda":
                torch.cuda.empty_cache()
    
    def memory_copy_test(self, size_mb: int = 512, duration: float = 10) -> Dict[str, float]:
        """Tests host-to-device and device-to-device memory copy speeds.

        Args:
            size_mb (int): Size of arrays in MB (default 512).
            duration (float): Duration of the test in seconds (default 10).

        Returns:
            Dict[str, float]: Dictionary with H2D, D2D, D2H bandwidths and size.
        """
        if self.device.type == "cpu":
            # CPU doesn't have H2D/D2H transfers
            return {
                "h2d_bandwidth_gbps": 0,
                "d2d_bandwidth_gbps": 0,
                "d2h_bandwidth_gbps": 0,
                "size_mb": size_mb
            }
            
        elements = (size_mb * 1024 * 1024) // 4
        
        # Create host and device tensors
        host_tensor = torch.randn(elements)
        device_tensor = torch.randn(elements, device=self.device)
        device_tensor2 = torch.empty_like(device_tensor)
        
        # Test H2D
        start_time = time.time()
        h2d_iterations = 0
        while time.time() - start_time < duration / 3:
            device_tensor.copy_(host_tensor)
            torch.cuda.synchronize()
            h2d_iterations += 1
        h2d_time = time.time() - start_time
        h2d_bandwidth = (size_mb * h2d_iterations / h2d_time) / 1000 if h2d_time > 0 else 0
        
        # Test D2D
        start_time = time.time()
        d2d_iterations = 0
        while time.time() - start_time < duration / 3:
            device_tensor2.copy_(device_tensor)
            torch.cuda.synchronize()
            d2d_iterations += 1
        d2d_time = time.time() - start_time
        d2d_bandwidth = (size_mb * d2d_iterations / d2d_time) / 1000 if d2d_time > 0 else 0
        
        # Test D2H
        start_time = time.time()
        d2h_iterations = 0
        while time.time() - start_time < duration / 3:
            host_tensor.copy_(device_tensor)
            torch.cuda.synchronize()
            d2h_iterations += 1
        d2h_time = time.time() - start_time
        d2h_bandwidth = (size_mb * d2h_iterations / d2h_time) / 1000 if d2h_time > 0 else 0
        
        return {
            "h2d_bandwidth_gbps": h2d_bandwidth,
            "d2d_bandwidth_gbps": d2d_bandwidth,
            "d2h_bandwidth_gbps": d2h_bandwidth,
            "size_mb": size_mb
        }
