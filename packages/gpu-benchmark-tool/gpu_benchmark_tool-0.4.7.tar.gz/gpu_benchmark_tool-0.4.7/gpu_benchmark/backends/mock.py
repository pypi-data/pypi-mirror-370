"""Mock GPU backend for testing.

This module provides a simulated GPU backend and monitor for development and testing purposes.
"""

import random
import time
from typing import Dict, List, Tuple
from .base import GPUBackend, GPUMonitor

class MockGPUMonitor(GPUMonitor):
    """Simulated GPU monitor for mock backend.

    Args:
        device_id (int): The simulated device ID.
    """
    
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.base_temp = 45.0
        self.start_time = time.time()
        
    def get_temperature(self) -> float:
        """Returns the simulated GPU temperature in Celsius.
        
        The temperature increases over time to simulate thermal stress during testing.
        
        Returns:
            float: Simulated temperature in Celsius (45-75°C range).
        """
        elapsed = time.time() - self.start_time
        temp_rise = min(elapsed * 0.5, 30)
        return self.base_temp + temp_rise + random.uniform(-2, 2)
    
    def get_power_usage(self) -> float:
        """Returns the simulated GPU power usage in Watts.
        
        The power usage increases over time to simulate load during testing.
        
        Returns:
            float: Simulated power usage in Watts (50-150W range).
        """
        base_power = 50.0
        elapsed = time.time() - self.start_time
        load_power = min(elapsed * 2, 100)
        return base_power + load_power + random.uniform(-5, 5)
    
    def get_memory_info(self) -> Dict[str, float]:
        """Returns simulated memory usage statistics as a dictionary.
        
        Provides consistent mock memory data for testing purposes.
        
        Returns:
            Dict[str, float]: Dictionary with memory statistics:
                - used_mb: Used memory in MB
                - total_mb: Total memory in MB  
                - free_mb: Free memory in MB
                - utilization_pct: Memory utilization percentage
        """
        return {
            "used_mb": 4096,
            "total_mb": 8192,
            "free_mb": 4096,
            "utilization_pct": 50.0
        }
    
    def get_utilization(self) -> float:
        """Returns the simulated GPU utilization percentage.
        
        Simulates realistic utilization patterns during stress testing.
        
        Returns:
            float: Simulated GPU utilization percentage (0-99% range).
        """
        elapsed = time.time() - self.start_time
        if elapsed < 5:
            return random.uniform(0, 20)
        else:
            return random.uniform(85, 99)
    
    def check_throttling(self) -> Tuple[bool, List[str]]:
        """Checks if the simulated GPU is throttling and returns reasons if so.
        
        Simulates thermal throttling based on temperature thresholds.
        
        Returns:
            Tuple[bool, List[str]]: (is_throttling, list of reasons)
                - is_throttling: True if GPU is throttling
                - reasons: List of throttling reasons (e.g., "Thermal limit")
        """
        temp = self.get_temperature()
        if temp > 80:
            return True, ["Thermal limit (simulated)"]
        return False, []

class MockBackend(GPUBackend):
    """Mock GPU backend for simulating a single GPU device."""
    
    def is_available(self) -> bool:
        """Returns True, indicating the mock backend is always available."""
        return True
    
    def get_device_count(self) -> int:
        """Returns the number of simulated devices (always 1)."""
        return 1
    
    def get_device_info(self, device_id: int) -> Dict[str, any]:
        """Returns simulated device information for the given device ID.

        Args:
            device_id (int): The simulated device ID.

        Returns:
            Dict[str, any]: Dictionary of device information.
        """
        if device_id != 0:
            raise ValueError("Invalid device ID for mock backend")
        return {
            "name": f"Mock GPU {device_id}",
            "compute_capability": "8.6",
            "total_memory_gb": 8.0,
            "vendor": "Mock",
            "backend": "Simulation"
        }
    
    def create_monitor(self, device_handle_or_id) -> GPUMonitor:
        """Creates and returns a MockGPUMonitor for the given device.

        Args:
            device_handle_or_id: The simulated device ID or handle.

        Returns:
            MockGPUMonitor: The simulated GPU monitor instance.
        """
        device_id = device_handle_or_id if isinstance(device_handle_or_id, int) else 0
        return MockGPUMonitor(device_id)
