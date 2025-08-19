"""NVIDIA GPU Backend with Old GPU Support.

This module provides a backend and monitor for NVIDIA GPUs using NVML and PyTorch, with compatibility for older GPUs and drivers.
"""

from typing import Dict, List, Tuple
from .base import GPUBackend, GPUMonitor
from ..benchmark import run_multi_gpu_benchmark

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = torch.cuda.is_available()
except ImportError:
    TORCH_AVAILABLE = False


class NVIDIAMonitor(GPUMonitor):
    """NVIDIA GPU monitoring using NVML, compatible with old drivers.

    Args:
        handle: NVML handle to the GPU device.
    """
    
    def __init__(self, handle):
        self.handle = handle
        self.throttle_reasons = {}
        
        if PYNVML_AVAILABLE:
            # Dynamically build throttle reasons based on what's available
            # This ensures compatibility with old drivers
            possible_reasons = [
                ('nvmlClocksThrottleReasonGpuIdle', "GPU Idle"),
                ('nvmlClocksThrottleReasonApplicationsClocksSetting', "Applications Clocks Setting"),
                ('nvmlClocksThrottleReasonSwPowerCap', "SW Power Cap"),
                ('nvmlClocksThrottleReasonHwSlowdown', "HW Slowdown"),
                ('nvmlClocksThrottleReasonSyncBoost', "Sync Boost"),
                ('nvmlClocksThrottleReasonSwThermalSlowdown', "SW Thermal Slowdown"),
                ('nvmlClocksThrottleReasonHwThermalSlowdown', "Thermal limit"),
                ('nvmlClocksThrottleReasonHwPowerBrakeSlowdown', "HW Power Brake Slowdown"),
                ('nvmlClocksThrottleReasonDisplayClocksSetting', "Display Clocks Setting"),
            ]
            
            for attr_name, description in possible_reasons:
                if hasattr(pynvml, attr_name):
                    try:
                        self.throttle_reasons[getattr(pynvml, attr_name)] = description
                    except:
                        # Skip if attribute exists but can't be accessed
                        pass
            
            # Log what we found (helpful for debugging old GPUs)
            if len(self.throttle_reasons) < len(possible_reasons):
                print(f"Note: Running on older driver. {len(self.throttle_reasons)} of {len(possible_reasons)} throttle reasons available.")
    
    def get_temperature(self) -> float:
        try:
            return pynvml.nvmlDeviceGetTemperature(self.handle, pynvml.NVML_TEMPERATURE_GPU)
        except pynvml.NVMLError:
            return -1
    
    def get_power_usage(self) -> float:
        try:
            return pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000
        except pynvml.NVMLError:
            return -1
    
    def get_memory_info(self) -> Dict[str, float]:
        try:
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            return {
                "used_mb": mem_info.used / (1024**2),
                "total_mb": mem_info.total / (1024**2),
                "free_mb": mem_info.free / (1024**2),
                "utilization_pct": (mem_info.used / mem_info.total) * 100
            }
        except pynvml.NVMLError:
            return {"used_mb": -1, "total_mb": -1, "free_mb": -1, "utilization_pct": -1}
    
    def get_utilization(self) -> float:
        try:
            return pynvml.nvmlDeviceGetUtilizationRates(self.handle).gpu
        except pynvml.NVMLError:
            return -1
    
    def check_throttling(self) -> Tuple[bool, List[str]]:
        """Checks if the GPU is throttling and returns reasons if so.

        Returns:
            Tuple[bool, List[str]]: (is_throttling, list of reasons)
        """
        if not self.throttle_reasons:
            # No throttle detection available on very old drivers
            return False, []
            
        try:
            current_reasons = pynvml.nvmlDeviceGetCurrentClocksThrottleReasons(self.handle)
            active_reasons = []
            
            for reason_code, reason_name in self.throttle_reasons.items():
                if current_reasons & reason_code:
                    active_reasons.append(reason_name)
            
            return len(active_reasons) > 0, active_reasons
        except pynvml.NVMLError:
            # Old GPUs might not support throttle detection at all
            return False, []
    
    def get_memory_bandwidth(self) -> float:
        """Gets the current memory bandwidth utilization.

        Returns:
            float: Memory bandwidth utilization percentage, or -1 if unavailable.
        """
        try:
            util_rates = pynvml.nvmlDeviceGetUtilizationRates(self.handle)
            # Some old GPUs don't have memory utilization
            if hasattr(util_rates, 'memory'):
                return util_rates.memory
            return -1
        except pynvml.NVMLError:
            return -1


class NVIDIABackend(GPUBackend):
    """NVIDIA GPU backend using CUDA/PyTorch, supports old GPUs and drivers."""
    
    def __init__(self):
        self.initialized = False
        
    def _ensure_initialized(self):
        """Ensures NVML is initialized for backend operations."""
        if not self.initialized and PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.initialized = True
            except pynvml.NVMLError:
                pass
    
    def is_available(self) -> bool:
        """Checks if NVIDIA GPUs are available on this system.

        Returns:
            bool: True if at least one NVIDIA GPU is available, False otherwise.
        """
        if not PYNVML_AVAILABLE:
            return False
            
        self._ensure_initialized()
        
        try:
            device_count = pynvml.nvmlDeviceGetCount()
            return device_count > 0
        except pynvml.NVMLError:
            return False
    
    def get_device_count(self) -> int:
        """Gets the number of NVIDIA GPUs available.

        Returns:
            int: Number of NVIDIA GPUs detected.
        """
        if not self.is_available():
            return 0
            
        try:
            return pynvml.nvmlDeviceGetCount()
        except pynvml.NVMLError:
            return 0
    
    def get_device_info(self, device_id: int) -> Dict[str, any]:
        """Gets information about a specific NVIDIA GPU.

        Args:
            device_id (int): The GPU device ID.

        Returns:
            Dict[str, any]: Dictionary of device information and properties.
        """
        self._ensure_initialized()
        
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            
            # Get memory info
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            # Get compute capability if PyTorch is available
            compute_capability = "Unknown"
            cuda_cores = -1
            
            if TORCH_AVAILABLE:
                try:
                    props = torch.cuda.get_device_properties(device_id)
                    compute_capability = f"{props.major}.{props.minor}"
                    cuda_cores = props.multi_processor_count * self._get_cuda_cores_per_sm(props.major)
                except:
                    # Old GPUs might have issues with property detection
                    pass
            
            # Detect if this is an old GPU
            is_old_gpu = False
            if "Tesla K" in name or "GTX 7" in name or "GTX 6" in name or "GTX 5" in name:
                is_old_gpu = True
                print(f"Detected older GPU: {name} - Optimizing for compatibility")
            
            return {
                "name": name,
                "compute_capability": compute_capability,
                "total_memory_gb": mem_info.total / 1e9,
                "cuda_cores": cuda_cores,
                "vendor": "NVIDIA",
                "backend": "NVML",
                "is_old_gpu": is_old_gpu
            }
            
        except pynvml.NVMLError as e:
            return {"error": str(e)}
    
    def create_monitor(self, device_handle_or_id) -> GPUMonitor:
        """Creates an NVIDIAMonitor for the given device.

        Args:
            device_handle_or_id: NVML handle or device index.

        Returns:
            NVIDIAMonitor: The NVIDIA GPU monitor instance.
        """
        self._ensure_initialized()
        
        # If integer, get handle
        if isinstance(device_handle_or_id, int):
            try:
                device_handle_or_id = pynvml.nvmlDeviceGetHandleByIndex(device_handle_or_id)
            except pynvml.NVMLError as e:
                print(f"Warning: Could not get device handle: {e}")
                raise
            
        return NVIDIAMonitor(device_handle_or_id)
    
    def _get_cuda_cores_per_sm(self, major: int) -> int:
        """Gets the number of CUDA cores per SM for a given compute capability.

        Args:
            major (int): Major compute capability version.

        Returns:
            int: Number of CUDA cores per SM.
        """
        cuda_cores_per_sm = {
            2: 32,   # Fermi (really old!)
            3: 192,  # Kepler (GTX 600/700 series)
            5: 128,  # Maxwell (GTX 900 series)
            6: 64,   # Pascal (GTX 10 series)
            7: 64,   # Volta/Turing (RTX 20 series)
            8: 64,   # Ampere (RTX 30 series)
            9: 128   # Hopper (H100)
        }
        return cuda_cores_per_sm.get(major, 64)
