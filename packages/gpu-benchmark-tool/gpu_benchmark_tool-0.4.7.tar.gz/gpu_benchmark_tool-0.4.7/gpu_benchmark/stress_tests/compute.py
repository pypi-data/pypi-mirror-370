"""Compute stress tests - Compatible with old GPUs.

This module provides compute-bound stress tests for GPUs, including matrix multiplication.
"""

import torch
import time
from typing import Dict


class ComputeStressTest:
    """GPU compute stress tests for benchmarking and diagnostics.

    Args:
        device (torch.device): The device (CPU or GPU) to run tests on.
    """
    
    def __init__(self, device: torch.device):
        self.device = device
        
    @property
    def is_old_gpu(self):
        if self.device.type == "cpu":
            return False
        try:
            import torch
            device_index = self.device.index if hasattr(self.device, 'index') else self.device
            cc = torch.cuda.get_device_capability(device_index)
            if cc[0] < 5:
                return True
            props = torch.cuda.get_device_properties(device_index)
            if props.total_memory < 4 * 1024 * 1024 * 1024:
                return True
        except Exception:
            pass
        return False
        
    def matrix_multiply_stress(self, size: int = 4096, duration: float = 10) -> Dict[str, float]:
        """Runs a matrix multiplication stress test.

        Args:
            size (int): Matrix dimension (default 4096).
            duration (float): Duration of the test in seconds (default 10).

        Returns:
            Dict[str, float]: Dictionary with iterations, TFLOPS, average time, matrix size, and old GPU flag.
        """
        # Adjust size for old GPUs or limited memory
        if self.is_old_gpu:
            size = min(size, 2048)  # Smaller matrices for old GPUs
            print(f"Detected old GPU - using matrix size {size}")
            
        if self.device.type == "cpu":
            size = min(size, 512)
        elif self.device.type == "cuda":
            # Check available memory and adjust
            try:
                mem_free = torch.cuda.mem_get_info(self.device.index)[0]
                mem_needed = size * size * 4 * 3  # 3 matrices, 4 bytes per float
                
                if mem_needed > mem_free * 0.8:  # Use only 80% of free memory
                    size = int((mem_free * 0.8 / (4 * 3)) ** 0.5)
                    size = min(size, 4096)  # Cap at original size
                    print(f"Adjusted matrix size to {size} based on available memory")
            except:
                if self.is_old_gpu:
                    size = 2048
        
        # Create matrices
        try:
            a = torch.randn((size, size), device=self.device, dtype=torch.float32)
            b = torch.randn((size, size), device=self.device, dtype=torch.float32)
        except RuntimeError as e:
            if 'out of memory' in str(e):
                return {
                    'iterations': 0,
                    'tflops': 0.0,
                    'avg_time_per_iter': 0.0,
                    'matrix_size': size,
                    'is_old_gpu': self.is_old_gpu,
                    'error': 'CUDA out of memory'
                }
            else:
                raise
        
        # Enable TensorCore optimizations for consistent performance measurement
        if self.device.type == "cuda":
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
        
        start_time = time.time()
        iterations = 0
        flops = 0
        
        while time.time() - start_time < duration:
            try:
                c = torch.matmul(a, b)
                if self.device.type == "cuda":
                    torch.cuda.synchronize()
                iterations += 1
                flops += 2 * size**3  # Approximate FLOPs for matrix multiply
            except RuntimeError as e:
                if 'out of memory' in str(e):
                    return {
                        'iterations': 0,
                        'tflops': 0.0,
                        'avg_time_per_iter': 0.0,
                        'matrix_size': size,
                        'is_old_gpu': self.is_old_gpu
                    }
                else:
                    raise
        
        elapsed = time.time() - start_time
        return {
            "iterations": iterations,
            "tflops": (flops / elapsed) / 1e12,
            "avg_time_per_iter": elapsed / iterations if iterations > 0 else 0,
            "matrix_size": size,
            "is_old_gpu": self.is_old_gpu
        }
