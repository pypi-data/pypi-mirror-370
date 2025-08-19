from setuptools import setup, find_packages
import os
import re

# Read version from version.py
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'gpu_benchmark', 'version.py')
    with open(version_file, 'r') as f:
        version_content = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gpu-benchmark-tool",
    version=get_version(),  # Dynamically read version
    author="Yousuf Rajput",
    author_email="ywrajput@gmail.com",
    description="Multi-vendor GPU health monitoring supporting old GPUs for e-waste reduction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gpu-benchmark-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Science/Research",
        "Topic :: System :: Hardware",
        "Topic :: System :: Monitoring",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "psutil>=5.8.0",
        "pyyaml>=6.0",
        "torch>=2.0.0",  # Add PyTorch to base installation
    ],
    extras_require={
        "nvidia": [
            "nvidia-ml-py>=11.450.51",  # NVIDIA monitoring only
            "onnxruntime-gpu>=1.15.0",  # ONNX Runtime for INT8 support
        ],
        "amd": [
            # ROCm support relies on system installation
        ],
        "intel": [
            "intel-extension-for-pytorch>=2.0.0",  # Intel GPU acceleration
        ],
        "all": [
            "nvidia-ml-py>=11.450.51",
            "intel-extension-for-pytorch>=2.0.0",
            "docker>=6.0.0",
        ],
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
            "build>=0.10.0",
            "twine>=4.0.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "gpu-benchmark=gpu_benchmark.cli:main",
        ],
    },
    keywords="gpu benchmark monitoring cuda rocm intel nvidia amd old-gpu ewaste recycling sustainability",
)
