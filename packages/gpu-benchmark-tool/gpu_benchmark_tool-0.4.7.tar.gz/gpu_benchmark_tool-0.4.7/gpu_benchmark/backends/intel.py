"""Intel GPU Backend.

This module provides a backend and monitor for Intel GPUs using xpu-smi, Intel Extension for PyTorch, and system tools.
"""

import subprocess
import platform
from typing import Dict, List, Tuple
from .base import GPUBackend, GPUMonitor

try:
    import torch
    # Check for Intel Extension for PyTorch
    try:
        import intel_extension_for_pytorch as ipex
        XPU_AVAILABLE = torch.xpu.is_available()
    except ImportError:
        XPU_AVAILABLE = False
except ImportError:
    XPU_AVAILABLE = False

XPU_SMI_AVAILABLE = False


class IntelMonitor(GPUMonitor):
    """Intel GPU monitoring using xpu-smi and PyTorch (if available).

    Args:
        device_id (int): The Intel GPU device ID.
    """
    
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self._has_xpu_smi = self._check_xpu_smi()
    
    def _check_xpu_smi(self) -> bool:
        """Checks if xpu-smi is available on the system.

        Returns:
            bool: True if xpu-smi is available, False otherwise.
        """
        try:
            result = subprocess.run(
                ['xpu-smi', 'version'],
                capture_output=True, text=True, timeout=2
            )
            return result.returncode == 0
        except:
            return False
    
    def _get_xpu_smi_value(self, metric: str) -> float:
        """Gets a metric value from xpu-smi for the given metric name.

        Args:
            metric (str): The metric to query ("temperature", "power", or "utilization").

        Returns:
            float: The metric value, or -1 if unavailable.
        """
        if not self._has_xpu_smi:
            return -1
            
        try:
            # Different commands for different metrics
            if metric == "temperature":
                cmd = ['xpu-smi', 'dump', '-d', str(self.device_id), '-m', '0']
            elif metric == "power":
                cmd = ['xpu-smi', 'dump', '-d', str(self.device_id), '-m', '1']
            elif metric == "utilization":
                cmd = ['xpu-smi', 'dump', '-d', str(self.device_id), '-m', '2']
            else:
                return -1
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                # Parse the value from output
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if metric == "temperature" and "GPU Temperature" in line:
                        return float(line.split(':')[1].strip().replace('C', ''))
                    elif metric == "power" and "Power" in line:
                        return float(line.split(':')[1].strip().replace('W', ''))
                    elif metric == "utilization" and "GPU Utilization" in line:
                        return float(line.split(':')[1].strip().replace('%', ''))
        except:
            pass
        return -1
    
    def get_temperature(self) -> float:
        """Gets the current GPU temperature in Celsius.

        Returns:
            float: Temperature in Celsius, or -1 if unavailable.
        """
        # Intel GPUs often don't expose temperature
        if self._has_xpu_smi:
            return self._get_xpu_smi_value("temperature")
        return -1
    
    def get_power_usage(self) -> float:
        """Gets the current GPU power usage in Watts.

        Returns:
            float: Power usage in Watts, or -1 if unavailable.
        """
        if self._has_xpu_smi:
            return self._get_xpu_smi_value("power")
        return -1
    
    def get_memory_info(self) -> Dict[str, float]:
        """Gets memory usage statistics for the GPU.

        Returns:
            Dict[str, float]: Dictionary with used, total, free memory (MB), and utilization percentage.
        """
        if XPU_AVAILABLE:
            try:
                # Use Intel Extension for PyTorch
                device = torch.device(f'xpu:{self.device_id}')
                # Intel XPU memory APIs
                props = torch.xpu.get_device_properties(device)
                total = props.total_memory / (1024**2)
                
                # Try to get current usage
                try:
                    allocated = torch.xpu.memory_allocated(device) / (1024**2)
                    free = total - allocated
                    
                    return {
                        "used_mb": allocated,
                        "total_mb": total,
                        "free_mb": free,
                        "utilization_pct": (allocated / total) * 100
                    }
                except:
                    return {
                        "used_mb": -1,
                        "total_mb": total,
                        "free_mb": -1,
                        "utilization_pct": -1
                    }
            except:
                pass
                
        return {"used_mb": -1, "total_mb": -1, "free_mb": -1, "utilization_pct": -1}
    
    def get_utilization(self) -> float:
        """Gets the current GPU utilization percentage.

        Returns:
            float: Utilization percentage, or -1 if unavailable.
        """
        if self._has_xpu_smi:
            return self._get_xpu_smi_value("utilization")
        return -1
    
    def check_throttling(self) -> Tuple[bool, List[str]]:
        """Checks if the GPU is throttling. Intel GPU throttling detection is limited.

        Returns:
            Tuple[bool, List[str]]: (is_throttling, list of reasons)
        """
        # Intel GPU throttling detection is limited
        # Could check frequency scaling if available
        return False, []


class IntelBackend(GPUBackend):
    """Intel GPU backend using xpu-smi, Intel Extension for PyTorch, and system tools."""
    
    def is_available(self) -> bool:
        """Checks if Intel GPUs are available on this system.

        Returns:
            bool: True if at least one Intel GPU is available, False otherwise.
        """
        # Method 1: Check for Intel Extension for PyTorch
        if XPU_AVAILABLE:
            return True
        
        # Method 2: Check for Intel GPU on Linux
        if platform.system() == "Linux":
            try:
                # Check for Intel GPU in lspci
                result = subprocess.run(
                    ['lspci'],
                    capture_output=True, text=True, timeout=2
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'Intel' in line and ('Graphics' in line or 'GPU' in line or 'Xe' in line):
                            return True
            except:
                pass
        
        # Method 3: Check for Intel GPU on Windows
        elif platform.system() == "Windows":
            try:
                result = subprocess.run(
                    ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                    capture_output=True, text=True, timeout=2
                )
                if result.returncode == 0 and 'Intel' in result.stdout:
                    return True
            except:
                pass
        
        return False
    
    def get_device_count(self) -> int:
        """Gets the number of Intel GPUs available.

        Returns:
            int: Number of Intel GPUs detected.
        """
        if XPU_AVAILABLE:
            return torch.xpu.device_count()
        
        # Otherwise, assume 1 if Intel GPU detected
        return 1 if self.is_available() else 0
    
    def get_device_info(self, device_id: int) -> Dict[str, any]:
        """Gets information about a specific Intel GPU.

        Args:
            device_id (int): The GPU device ID.

        Returns:
            Dict[str, any]: Dictionary of device information and properties.
        """
        info = {
            "vendor": "Intel",
            "backend": "XPU" if XPU_AVAILABLE else "Intel Graphics",
            "device_id": device_id,
            "compute_capability": "Unknown",
            "total_memory_gb": "Unknown"
        }
        
        # Get device name
        if XPU_AVAILABLE:
            try:
                props = torch.xpu.get_device_properties(device_id)
                info["name"] = props.name
                info["total_memory_gb"] = props.total_memory / 1e9
                info["execution_units"] = props.max_compute_units
            except:
                pass
        else:
            # Try to get name from system
            if platform.system() == "Linux":
                try:
                    result = subprocess.run(
                        ['lspci', '-v'],
                        capture_output=True, text=True, timeout=2
                    )
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'Intel' in line and ('Graphics' in line or 'GPU' in line):
                                # Extract model name
                                parts = line.split('Intel Corporation')[1].strip()
                                info["name"] = f"Intel {parts}"
                                break
                except:
                    pass
            
            if "name" not in info:
                info["name"] = "Intel GPU"
        
        return info
    
    def create_monitor(self, device_handle_or_id) -> GPUMonitor:
        """Creates an IntelMonitor for the given device.

        Args:
            device_handle_or_id: Device index or handle.

        Returns:
            IntelMonitor: The Intel GPU monitor instance.
        """
        device_id = device_handle_or_id if isinstance(device_handle_or_id, int) else 0
        return IntelMonitor(device_id)
