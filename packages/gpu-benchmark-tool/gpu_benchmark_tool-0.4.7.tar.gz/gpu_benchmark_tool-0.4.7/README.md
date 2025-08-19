A comprehensive multi-vendor GPU health monitoring and optimization tool that helps users assess GPU performance and select optimal hardware for their workloads.

🚀 Features

🔥 Comprehensive GPU Health Monitoring: Temperature, power, utilization, and throttling detection

⚡ Advanced Stress Testing: Compute, memory bandwidth, VRAM, and mixed-precision tests

📊 Detailed Health Scoring: 100-point scoring system with actionable recommendations

🖥️ Multi-GPU Support: Test and compare multiple GPUs simultaneously

🧪 Mock Mode: Test on any computer without GPUs (perfect for development)

🔌 Multi-Vendor Support: NVIDIA, AMD, Intel, and Mock mode

☁️ Cloud-Ready: Designed to help select optimal GPUs for cloud deployment (coming soon!)

## Installation

Basic Installation (Works on any system with GPU)

# For systems with any GPU (NVIDIA, AMD, Intel)
pip install gpu-benchmark-tool
# Includes PyTorch for computational stress tests

Installation with Enhanced GPU Support

# For NVIDIA GPUs (adds NVIDIA monitoring)
pip install gpu-benchmark-tool[nvidia]

# For AMD GPUs (relies on system ROCm)
pip install gpu-benchmark-tool[amd]

# For Intel GPUs (adds Intel GPU acceleration)
pip install gpu-benchmark-tool[intel]

# For all GPU vendors (maximum compatibility)
pip install gpu-benchmark-tool[all]

🎯 Quick Start
1. Check Available GPUs
gpu-benchmark list

2. Run Benchmark

# Benchmark all GPUs
gpu-benchmark benchmark

# Benchmark specific GPU (recommended)
gpu-benchmark benchmark --gpu-id 0

# Quick 30-second test
gpu-benchmark benchmark --gpu-id 0 --duration 30

# Export results to JSON
gpu-benchmark benchmark --gpu-id 0 --export results.json

3. Mock Mode (No GPU Required)

# Perfect for development or systems without GPUs
gpu-benchmark benchmark --mock --duration 30

📊 Google Colab Quick Start

# Run in a Colab notebook (Runtime > Change runtime type > GPU)
!pip install gpu-benchmark-tool[nvidia]
!gpu-benchmark benchmark --gpu-id 0 --duration 30

# Understanding Results

Health Score (0-100 points)
85-100: 🟢 Healthy - Safe for all workloads including AI training
70-84: 🟢 Good - Suitable for most workloads
55-69: 🟡 Degraded - Limit to inference or light compute
40-54: 🟡 Warning - Monitor closely, avoid heavy workloads
0-39: 🔴 Critical - Do not use for production

### Score Components

Each component contributes to the total 100-point score:

**Temperature (20 points)**
- Peak temperature during stress test
- Under 80°C: Full points
- 80-85°C: 15 points
- 85-90°C: 10 points
- Over 90°C: 5 points

**Baseline Temperature (10 points)**
- GPU temperature at idle
- Under 50°C: Full points
- 50-60°C: 5 points
- Over 60°C: 0 points

**Power Efficiency (10 points)**
- Power consumption optimization
- Within optimal range: Full points
- Slightly outside range: 5 points
- Far from optimal: 0 points

**GPU Utilization (10 points)**
- How well the GPU is utilized during tests
- 99%+: Full points
- 90-98%: 5 points
- Under 90%: 0 points

**Throttling (20 points)**
- Thermal or power throttling detection
- No throttling: Full points
- Occasional throttling: 10-15 points
- Frequent throttling: 0-5 points

**Errors (20 points)**
- Stability during stress tests
- No errors: Full points
- Few errors: 10-15 points
- Many errors: 0-5 points

**Temperature Stability (10 points)**
- Temperature consistency during tests
- Very stable: Full points
- Some fluctuation: 5-7 points
- Unstable: 0-5 points

# Performance Metrics
Matrix Multiplication: Raw compute performance (TFLOPS)
Memory Bandwidth: Memory throughput (GB/s)
VRAM Stress: Memory allocation stability
Mixed Precision: FP16/BF16 support for AI workloads

# Command Line Usage
Benchmark Command

gpu-benchmark benchmark [OPTIONS]

Options:
  --gpu-id INTEGER    Specific GPU to test (default: all GPUs)
  --duration INTEGER  Test duration in seconds (default: 60)
  --basic            Run basic tests only (faster)
  --export TEXT      Export results to JSON file
  --verbose          Show detailed output
  --mock             Use mock GPU (no hardware required)

# Examples

# Full test on GPU 0 with export
gpu-benchmark benchmark --gpu-id 0 --duration 120 --export full_test.json

# Quick health check
gpu-benchmark benchmark --gpu-id 0 --duration 30 --basic

# Development testing
gpu-benchmark benchmark --mock --export mock_results.json


## Real-time Monitoring

# Monitor GPU metrics in real-time (NVIDIA only)
gpu-benchmark monitor --gpu-id 0

# Python API Usage
Basic Usage

import pynvml
from gpu_benchmark import run_full_benchmark

# Initialize NVML
pynvml.nvmlInit()
handle = pynvml.nvmlDeviceGetHandleByIndex(0)

# Run benchmark
results = run_full_benchmark(
    handle=handle,
    duration=60,
    enhanced=True,
    device_id=0
)

# Access results

print(f"Health Score: {results['health_score']['score']}/100")
print(f"Status: {results['health_score']['status']}")

Analyzing Results

# Check if GPU is healthy for production
if results['health_score']['score'] >= 70:
    print("✅ GPU is suitable for production workloads")
else:
    print("⚠️ GPU needs attention")
    
# Access performance metrics
if 'performance_tests' in results:
    tflops = results['performance_tests']['matrix_multiply']['tflops']
    print(f"Compute Performance: {tflops:.2f} TFLOPS")

🔧 Troubleshooting

# Common Issues

"No GPUs found"

Use --mock flag for testing without GPUs
Ensure NVIDIA/AMD/Intel drivers are installed
For AMD: Install ROCm drivers and PyTorch with ROCm support
For Intel: Install Intel GPU drivers and Intel Extension for PyTorch

"NVML Error" on Colab

This warning can be ignored - the tool still works correctly
Use --gpu-id 0 for cleaner output

"PyTorch not available"

The base installation now includes PyTorch
If you see this error, try: pip install gpu-benchmark-tool[nvidia]

# Low Health Scores

Check system cooling
Ensure GPU isn't thermal throttling
Close other GPU applications
Multi-GPU JSON Format

Use --gpu-id 0 to test single GPU (simpler output)
Without --gpu-id, results are nested under 'results' key

# Supported GPUs
NVIDIA GPUs (Full Support)
Consumer: RTX 4090, 4080, 4070, 3090, 3080, 3070, 3060
Data Center: A100, V100, T4, P100, K80
Workstation: RTX A6000, A5000, A4000
AMD GPUs (ROCm Required)
MI250X, MI210, MI100
Radeon RX 7900 XTX, RX 6900 XT
Intel GPUs (Limited Support)
Arc A770, A750
Intel Xe integrated graphics

# Requirements
Python 3.8 or higher
For NVIDIA: CUDA drivers
For AMD: ROCm drivers
For Intel: Intel GPU drivers

📄 License
MIT License - see LICENSE file for details.

🙏 Acknowledgments
Built to solve real-world GPU selection challenges and reduce cloud computing costs through better hardware decisions.

📧 Contact
PyPI: https://pypi.org/project/gpu-benchmark-tool/
Email: ywrajput@gmail.com