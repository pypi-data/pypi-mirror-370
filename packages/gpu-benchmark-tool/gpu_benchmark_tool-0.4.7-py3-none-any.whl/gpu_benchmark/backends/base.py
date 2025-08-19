"""Base classes for GPU backends.

This module defines abstract base classes for GPU backends and monitoring interfaces.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

class GPUMonitor(ABC):
    """Abstract base class for GPU monitoring.

    Methods:
        get_temperature(): Returns the current GPU temperature in Celsius.
        get_power_usage(): Returns the current GPU power usage in Watts.
        get_memory_info(): Returns a dictionary with memory usage statistics.
        get_utilization(): Returns the current GPU utilization percentage.
        check_throttling(): Returns a tuple (is_throttling, reasons).
    """
    
    @abstractmethod
    def get_temperature(self) -> float:
        pass
    
    @abstractmethod
    def get_power_usage(self) -> float:
        pass
    
    @abstractmethod
    def get_memory_info(self) -> Dict[str, float]:
        pass
    
    @abstractmethod
    def get_utilization(self) -> float:
        pass
    
    @abstractmethod
    def check_throttling(self) -> Tuple[bool, List[str]]:
        pass

class GPUBackend(ABC):
    """Abstract base class for GPU backends.

    Methods:
        is_available(): Returns True if the backend is available on this system.
        get_device_count(): Returns the number of devices managed by this backend.
        get_device_info(device_id): Returns a dictionary of device information.
        create_monitor(device_handle_or_id): Returns a GPUMonitor for the device.
    """
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    @abstractmethod
    def get_device_count(self) -> int:
        pass
    
    @abstractmethod
    def get_device_info(self, device_id: int) -> Dict[str, any]:
        pass
    
    @abstractmethod
    def create_monitor(self, device_handle_or_id) -> GPUMonitor:
        pass
