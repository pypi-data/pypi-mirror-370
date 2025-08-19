"""AMD GPU Backend using ROCm.

This module provides a backend and monitor for AMD GPUs using ROCm, rocm-smi, and PyTorch (if available).
"""

import subprocess
import platform
from typing import Dict, List, Tuple
from .base import GPUBackend, GPUMonitor

try:
    import torch
    # Check if ROCm version of PyTorch is available
    ROCM_AVAILABLE = hasattr(torch.version, 'hip') and torch.version.hip is not None
except ImportError:
    ROCM_AVAILABLE = False


class AMDMonitor(GPUMonitor):
    """AMD GPU monitoring using rocm-smi and PyTorch (if available).

    Args:
        device_id (int): The AMD GPU device ID.
    """
    
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self._cache = {}
        self._update_cache()
    
    def _update_cache(self):
        """Updates cached values from rocm-smi for temperature, power, and utilization."""
        try:
            # Get temperature
            result = subprocess.run(
                ['rocm-smi', '-d', str(self.device_id), '-t'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                # Parse temperature from output
                for line in result.stdout.split('\n'):
                    if 'Temperature' in line and 'C' in line:
                        try:
                            temp_str = line.split(':')[1].strip().replace('C', '')
                            self._cache['temperature'] = float(temp_str)
                        except:
                            pass
            
            # Get power
            result = subprocess.run(
                ['rocm-smi', '-d', str(self.device_id), '-p'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Power' in line and 'W' in line:
                        try:
                            power_str = line.split(':')[1].strip().replace('W', '')
                            self._cache['power'] = float(power_str)
                        except:
                            pass
            
            # Get utilization
            result = subprocess.run(
                ['rocm-smi', '-d', str(self.device_id), '-u'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'GPU use' in line and '%' in line:
                        try:
                            util_str = line.split(':')[1].strip().replace('%', '')
                            self._cache['utilization'] = float(util_str)
                        except:
                            pass
                            
        except (Exception, FileNotFoundError):
            # rocm-smi not available
            pass
    
    def get_temperature(self) -> float:
        """Gets the current GPU temperature in Celsius.

        Returns:
            float: Temperature in Celsius, or -1 if unavailable.
        """
        self._update_cache()
        return self._cache.get('temperature', -1)
    
    def get_power_usage(self) -> float:
        """Gets the current GPU power usage in Watts.

        Returns:
            float: Power usage in Watts, or -1 if unavailable.
        """
        self._update_cache()
        return self._cache.get('power', -1)
    
    def get_memory_info(self) -> Dict[str, float]:
        """Gets memory usage statistics for the GPU.

        Returns:
            Dict[str, float]: Dictionary with used, total, free memory (MB), and utilization percentage.
        """
        if ROCM_AVAILABLE and torch.cuda.is_available():
            try:
                # Use PyTorch for memory info
                device = torch.device(f'cuda:{self.device_id}')
                mem_info = torch.cuda.mem_get_info(device)
                free = mem_info[0] / (1024**2)  # Convert to MB
                total = mem_info[1] / (1024**2)
                used = total - free
                
                return {
                    "used_mb": used,
                    "total_mb": total,
                    "free_mb": free,
                    "utilization_pct": (used / total) * 100
                }
            except:
                pass
        
        # Fallback to rocm-smi
        try:
            result = subprocess.run(
                ['rocm-smi', '-d', str(self.device_id), '--showmeminfo', 'vram'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                # Parse memory info from output
                total = used = -1
                for line in result.stdout.split('\n'):
                    if 'Total Memory' in line:
                        total = float(line.split(':')[1].strip()) / (1024**2)
                    elif 'Used Memory' in line:
                        used = float(line.split(':')[1].strip()) / (1024**2)
                
                if total > 0:
                    free = total - used
                    return {
                        "used_mb": used,
                        "total_mb": total,
                        "free_mb": free,
                        "utilization_pct": (used / total) * 100
                    }
        except:
            pass
            
        return {"used_mb": -1, "total_mb": -1, "free_mb": -1, "utilization_pct": -1}
    
    def get_utilization(self) -> float:
        """Gets the current GPU utilization percentage.

        Returns:
            float: Utilization percentage, or -1 if unavailable.
        """
        self._update_cache()
        return self._cache.get('utilization', -1)
    
    def check_throttling(self) -> Tuple[bool, List[str]]:
        """Checks if the GPU is throttling and returns reasons if so.

        Returns:
            Tuple[bool, List[str]]: (is_throttling, list of reasons)
        """
        # AMD throttling detection via performance level
        try:
            result = subprocess.run(
                ['rocm-smi', '-d', str(self.device_id), '--showperflevel'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0 and 'auto' not in result.stdout.lower():
                # If not in auto mode, might be throttled
                return True, ["Performance level manually reduced"]
        except:
            pass
        return False, []


class AMDBackend(GPUBackend):
    """AMD GPU backend using ROCm and rocm-smi."""
    
    def is_available(self):
        # First check if rocm-smi exists
        try:
            result = subprocess.run(
                ['rocm-smi', '--version'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode != 0:
                return False
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
        
        # Check if we can list GPUs
        try:
            result = subprocess.run(
                ['rocm-smi', '--showid'],
                capture_output=True, text=True, timeout=2
            )
            return result.returncode == 0 and 'GPU' in result.stdout
        except:
            return False
    
    def get_device_count(self) -> int:
        """Gets the number of AMD GPUs available.

        Returns:
            int: Number of AMD GPUs detected.
        """
        try:
            result = subprocess.run(
                ['rocm-smi', '--showid'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                # Count GPU lines in output
                count = 0
                for line in result.stdout.split('\n'):
                    if 'GPU[' in line:
                        count += 1
                return count
        except:
            pass
        
        # Fallback to PyTorch if available
        if ROCM_AVAILABLE and torch.cuda.is_available():
            return torch.cuda.device_count()
        
        return 0
    
    def get_device_info(self, device_id: int) -> Dict[str, any]:
        """Gets information about a specific AMD GPU.

        Args:
            device_id (int): The GPU device ID.

        Returns:
            Dict[str, any]: Dictionary of device information and properties.
        """
        info = {
            "vendor": "AMD",
            "backend": "ROCm",
            "device_id": device_id,
            'compute_capability': 'Unknown',
            'total_memory_gb': 'Unknown',
        }
        
        # Try to get GPU name
        try:
            result = subprocess.run(
                ['rocm-smi', '-d', str(device_id), '--showproductname'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Card series' in line or 'Product Name' in line:
                        info["name"] = line.split(':')[1].strip()
                        break
        except:
            info["name"] = f"AMD GPU {device_id}"
        
        # Get memory size
        try:
            result = subprocess.run(
                ['rocm-smi', '-d', str(device_id), '--showmeminfo', 'vram'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Total Memory' in line:
                        mem_bytes = float(line.split(':')[1].strip())
                        info["total_memory_gb"] = mem_bytes / 1e9
                        break
        except:
            pass
        
        # Get compute capability equivalent
        if ROCM_AVAILABLE and torch.cuda.is_available():
            try:
                props = torch.cuda.get_device_properties(device_id)
                info["compute_units"] = props.multi_processor_count
                info["max_threads_per_block"] = props.max_threads_per_block
                info["compute_capability"] = f"{props.major}.{props.minor}"
            except:
                pass
        
        return info
    
    def create_monitor(self, device_handle_or_id) -> GPUMonitor:
        """Creates an AMDMonitor for the given device.

        Args:
            device_handle_or_id: Device index or handle.

        Returns:
            AMDMonitor: The AMD GPU monitor instance.
        """
        device_id = device_handle_or_id if isinstance(device_handle_or_id, int) else 0
        return AMDMonitor(device_id)
