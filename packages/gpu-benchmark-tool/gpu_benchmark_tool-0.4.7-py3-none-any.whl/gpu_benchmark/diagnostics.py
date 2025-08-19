"""Diagnostics utilities for GPU Benchmark Tool.

This module provides functions to retrieve GPU information and print temperature thresholds.
"""
import platform
import os
import sys
import subprocess

try:
    import psutil
except ImportError:
    psutil = None

try:
    import cpuinfo
except ImportError:
    cpuinfo = None

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

try:
    import torch
except ImportError:
    torch = None

# baseline info & thresholds

def get_gpu_info(handle):
    """Gets GPU information such as temperature, power usage, memory, and fan speed.

    Args:
        handle: NVML handle to the GPU.

    Returns:
        dict: Dictionary containing temperature, power usage, memory usage, and fan speed.
    """
    if not PYNVML_AVAILABLE:
        return {
            "name": "Unknown GPU",
            "Temperature (C)": -1,
            "Power Usage (W)": -1,
            "Memory Used (MB)": -1,
            "Memory Total (MB)": -1,
            "Fan Speed (%)": "Not available"
        }
        
    # Get GPU name
    try:
        name = pynvml.nvmlDeviceGetName(handle)
        if isinstance(name, bytes):
            name = name.decode('utf-8')
    except pynvml.NVMLError:
        name = "Unknown GPU"
        
    temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
    power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000
    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    try:
        fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
    except pynvml.NVMLError:
        fan_speed = "Not supported"

    info = {
        "name": name,
        "Temperature (C)": temperature,
        "Power Usage (W)": power_usage,
        "Memory Used (MB)": memory_info.used // (1024**2),
        "Memory Total (MB)": memory_info.total // (1024**2),
        "Fan Speed (%)": fan_speed,
    }
    return info

def print_temperature_thresholds(handle):
    """Prints the temperature thresholds for slowdown and shutdown for a GPU.

    Args:
        handle: NVML handle to the GPU.
    """
    if not PYNVML_AVAILABLE:
        print("NVIDIA GPU monitoring not available")
        return
        
    try:
        slowdown = pynvml.nvmlDeviceGetTemperatureThreshold(
            handle, pynvml.NVML_TEMPERATURE_THRESHOLD_SLOWDOWN)
        print(f"⚠️  Slowdown Threshold: {slowdown} °C")
    except pynvml.NVMLError as e:
        print(f"Slowdown Threshold: Not supported ({str(e)})")

    try:
        shutdown = pynvml.nvmlDeviceGetTemperatureThreshold(
            handle, pynvml.NVML_TEMPERATURE_THRESHOLD_SHUTDOWN)
        print(f"🔥 Shutdown Threshold: {shutdown} °C")
    except pynvml.NVMLError as e:
        print(f"Shutdown Threshold: Not supported ({str(e)})")

def get_system_info():
    """Gathers baseline system information (CPU, RAM, OS, CUDA, driver, etc).

    Returns:
        dict: Dictionary containing system information.
    """
    info = {}

    # OS
    info["OS"] = platform.platform()

    # CPU
    info["CPU Model"] = platform.processor() or platform.uname().processor or "Unknown"
    info["CPU Cores"] = os.cpu_count() or "Unknown"
    # CPU Frequency
    cpu_freq = None
    if psutil and hasattr(psutil, "cpu_freq"):
        try:
            freq = psutil.cpu_freq()
            if freq:
                cpu_freq = f"{freq.current:.2f} MHz"
        except Exception:
            pass
    info["CPU Frequency"] = cpu_freq or "Unknown"
    # CPU Maker/Model (detailed)
    if cpuinfo:
        try:
            cpu = cpuinfo.get_cpu_info()
            info["CPU Model"] = cpu.get("brand_raw", info["CPU Model"])
            info["CPU Vendor"] = cpu.get("vendor_id_raw", "Unknown")
        except Exception:
            pass

    # RAM
    ram_gb = None
    if psutil and hasattr(psutil, "virtual_memory"):
        try:
            ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        except Exception:
            pass
    info["RAM Amount"] = f"{ram_gb:.1f} GB" if ram_gb else "Unknown"
    # RAM Speed (platform-specific, best effort)
    ram_speed = "Unknown"
    if sys.platform == "linux" and os.path.exists("/proc/meminfo"):
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if "MemTotal" in line:
                        break  # Already got RAM amount
            # Try dmidecode for speed
            try:
                out = subprocess.check_output(["dmidecode", "--type", "17"], stderr=subprocess.DEVNULL)
                for l in out.decode().splitlines():
                    if "Speed:" in l and "Configured" not in l:
                        ram_speed = l.split(":")[-1].strip()
                        break
            except Exception:
                pass
        except Exception:
            pass
    elif sys.platform == "win32":
        try:
            out = subprocess.check_output(["wmic", "MemoryChip", "get", "Speed"], stderr=subprocess.DEVNULL)
            lines = out.decode().splitlines()
            speeds = [l.strip() for l in lines[1:] if l.strip().isdigit()]
            if speeds:
                ram_speed = f"{max(map(int, speeds))} MHz"
        except Exception:
            pass
    info["RAM Speed"] = ram_speed

    # CUDA version
    cuda_version = None
    if torch and hasattr(torch, "version") and hasattr(torch.version, "cuda"):
        cuda_version = torch.version.cuda
    if not cuda_version and PYNVML_AVAILABLE:
        try:
            v = pynvml.nvmlSystemGetCudaDriverVersion()
            cuda_version = str(v)
        except Exception:
            pass
    info["CUDA Version"] = cuda_version or "Unknown"

    # GPU driver version
    driver_version = None
    if PYNVML_AVAILABLE:
        try:
            driver_version = pynvml.nvmlSystemGetDriverVersion()
            if isinstance(driver_version, bytes):
                driver_version = driver_version.decode()
        except Exception:
            pass
    info["Driver Version"] = driver_version or "Unknown"

    return info


def print_system_info():
    """Prints baseline system information (CPU, RAM, OS, CUDA, driver, etc).

    Returns:
        None
    """
    info = get_system_info()
    print("\nSystem Information:")
    print("-" * 30)
    for key, value in info.items():
        print(f"{key:.<25} {value}")

def check_enhanced_monitoring_requirements():
    """Check if enhanced monitoring requirements are met.
    
    Returns:
        dict: Dictionary with status and recommendations for enhanced monitoring.
    """
    requirements = {
        "pynvml": False,
        "torch": False,
        "cuda": False,
        "nvidia_gpu": False,
        "recommendations": []
    }
    
    # Check pynvml
    try:
        import pynvml
        requirements["pynvml"] = True
    except ImportError:
        requirements["recommendations"].append("Install nvidia-ml-py: pip install nvidia-ml-py")
    
    # Check torch
    try:
        import torch
        requirements["torch"] = True
        if torch.cuda.is_available():
            requirements["cuda"] = True
        else:
            requirements["recommendations"].append("PyTorch CUDA support not available. Install: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    except ImportError:
        requirements["recommendations"].append("Install PyTorch: pip install torch")
    
    # Check for NVIDIA GPU
    if requirements["pynvml"]:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            requirements["nvidia_gpu"] = device_count > 0
            if device_count == 0:
                requirements["recommendations"].append("No NVIDIA GPUs detected")
        except:
            requirements["recommendations"].append("NVML initialization failed. Check NVIDIA drivers")
    
    # Determine if enhanced monitoring is available
    enhanced_available = all([
        requirements["pynvml"],
        requirements["torch"], 
        requirements["cuda"],
        requirements["nvidia_gpu"]
    ])
    
    requirements["enhanced_available"] = enhanced_available
    
    return requirements

def print_enhanced_monitoring_status():
    """Print enhanced monitoring status and requirements."""
    requirements = check_enhanced_monitoring_requirements()
    
    print("\nEnhanced Monitoring Status:")
    print("-" * 30)
    print(f"pynvml available: {'✓' if requirements['pynvml'] else '✗'}")
    print(f"PyTorch available: {'✓' if requirements['torch'] else '✗'}")
    print(f"CUDA support: {'✓' if requirements['cuda'] else '✗'}")
    print(f"NVIDIA GPU detected: {'✓' if requirements['nvidia_gpu'] else '✗'}")
    print(f"Enhanced monitoring: {'✓' if requirements['enhanced_available'] else '✗'}")
    
    if requirements["recommendations"]:
        print("\nTo enable enhanced monitoring:")
        for rec in requirements["recommendations"]:
            print(f"  • {rec}")
    
    return requirements["enhanced_available"]

def comprehensive_diagnostics():
    """Comprehensive diagnostics checking all GPU-related components and versions.
    
    Returns:
        dict: Dictionary with detailed diagnostic information.
    """
    diagnostics = {
        "torch": {
            "present": False,
            "version": None,
            "cuda_enabled": False,
            "cuda_version": None
        },
        "pytorch": {
            "present": False,
            "version": None
        },
        "cuda": {
            "version": None,
            "driver_version": None
        },
        "metal": {
            "present": False,
            "version": None
        },
        "nvidia_container": {
            "present": False,
            "version": None
        },
        "recommendations": []
    }
    
    # Check PyTorch/Torch (they're the same thing)
    try:
        import torch
        diagnostics["torch"]["present"] = True
        diagnostics["pytorch"]["present"] = True
        diagnostics["torch"]["version"] = torch.__version__
        diagnostics["pytorch"]["version"] = torch.__version__
        
        # Check CUDA support
        if hasattr(torch, 'cuda') and torch.cuda.is_available():
            diagnostics["torch"]["cuda_enabled"] = True
            if hasattr(torch.version, 'cuda'):
                diagnostics["torch"]["cuda_version"] = torch.version.cuda
                # Also set the general CUDA version
                diagnostics["cuda"]["version"] = torch.version.cuda
    except ImportError:
        diagnostics["recommendations"].append("PyTorch not installed: pip install torch")
    
    # Check CUDA version and driver
    try:
        import pynvml
        pynvml.nvmlInit()
        
        # CUDA driver version
        try:
            cuda_driver = pynvml.nvmlSystemGetCudaDriverVersion()
            diagnostics["cuda"]["driver_version"] = str(cuda_driver)
        except Exception:
            pass
            
        # CUDA version (from PyTorch if available, otherwise from NVML)
        if not diagnostics["torch"]["cuda_version"]:
            try:
                # Try to get CUDA version from NVML
                cuda_version = pynvml.nvmlSystemGetCudaDriverVersion()
                diagnostics["cuda"]["version"] = str(cuda_version)
            except Exception:
                pass
    except Exception:
        diagnostics["recommendations"].append("NVML not available: pip install nvidia-ml-py")
    
    # Check Metal (Apple ML) - macOS specific
    if sys.platform == "darwin":
        try:
            import subprocess
            result = subprocess.run(["system_profiler", "SPMetalDataType"], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and "Metal" in result.stdout:
                diagnostics["metal"]["present"] = True
                # Try to extract Metal version
                for line in result.stdout.split('\n'):
                    if "Version:" in line:
                        diagnostics["metal"]["version"] = line.split(":")[-1].strip()
                        break
        except Exception:
            pass
    
    # Check NVIDIA Container Toolkit
    try:
        import subprocess
        # Check nvidia-docker
        result = subprocess.run(["nvidia-docker", "version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            diagnostics["nvidia_container"]["present"] = True
            # Extract version from output
            for line in result.stdout.split('\n'):
                if "Version:" in line:
                    diagnostics["nvidia_container"]["version"] = line.split(":")[-1].strip()
                    break
    except Exception:
        pass
    
    # Also check nvidia-container-toolkit
    try:
        import subprocess
        result = subprocess.run(["nvidia-container-toolkit", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            diagnostics["nvidia_container"]["present"] = True
            if not diagnostics["nvidia_container"]["version"]:
                diagnostics["nvidia_container"]["version"] = result.stdout.strip()
    except Exception:
        pass
    
    return diagnostics

def print_comprehensive_diagnostics():
    """Print comprehensive diagnostic information."""
    diagnostics = comprehensive_diagnostics()
    
    print("\nComprehensive GPU Diagnostics:")
    print("=" * 50)
    
    # PyTorch/Torch
    print("\nPyTorch/Torch:")
    print(f"  Present: {'✓' if diagnostics['torch']['present'] else '✗'}")
    if diagnostics['torch']['version']:
        print(f"  Version: {diagnostics['torch']['version']}")
    print(f"  CUDA Enabled: {'✓' if diagnostics['torch']['cuda_enabled'] else '✗'}")
    if diagnostics['torch']['cuda_version']:
        print(f"  CUDA Version: {diagnostics['torch']['cuda_version']}")
    
    # CUDA
    print("\nCUDA:")
    if diagnostics['cuda']['version']:
        print(f"  Version: {diagnostics['cuda']['version']}")
    if diagnostics['cuda']['driver_version']:
        print(f"  Driver Version: {diagnostics['cuda']['driver_version']}")
    
    # Metal (Apple ML)
    if sys.platform == "darwin":
        print("\nMetal (Apple ML):")
        print(f"  Present: {'✓' if diagnostics['metal']['present'] else '✗'}")
        if diagnostics['metal']['version']:
            print(f"  Version: {diagnostics['metal']['version']}")
    
    # NVIDIA Container Toolkit
    print("\nNVIDIA Container Toolkit:")
    print(f"  Present: {'✓' if diagnostics['nvidia_container']['present'] else '✗'}")
    if diagnostics['nvidia_container']['version']:
        print(f"  Version: {diagnostics['nvidia_container']['version']}")
    
    # Recommendations
    if diagnostics["recommendations"]:
        print("\nRecommendations:")
        for rec in diagnostics["recommendations"]:
            print(f"  • {rec}")
    
    return diagnostics
