"""Tests for GPU stress tests functionality."""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import gpu_benchmark
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gpu_benchmark.stress_tests.compute import ComputeStressTest
from gpu_benchmark.stress_tests.memory import MemoryStressTest
from gpu_benchmark.stress_tests.mixed_precision import MixedPrecisionTest


class TestComputeStressTest(unittest.TestCase):
    """Test compute stress test functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.device = MagicMock()
        self.device.type = "cuda"
        self.device.index = 0
        self.compute_test = ComputeStressTest(self.device)

    def test_detect_old_gpu(self):
        """Test old GPU detection."""
        # Test with CPU device
        cpu_device = MagicMock()
        cpu_device.type = "cpu"
        cpu_test = ComputeStressTest(cpu_device)
        self.assertFalse(cpu_test.is_old_gpu)

    @patch('gpu_benchmark.stress_tests.compute.torch.cuda.get_device_capability')
    def test_detect_old_gpu_compute_capability(self, mock_get_capability):
        """Test old GPU detection based on compute capability."""
        # Test old GPU (compute capability < 5.0)
        mock_get_capability.return_value = (3, 5)  # Kepler
        compute_test = ComputeStressTest(self.device)
        self.assertTrue(compute_test.is_old_gpu)

        # Test modern GPU (compute capability >= 5.0)
        mock_get_capability.return_value = (8, 6)  # Ampere
        compute_test = ComputeStressTest(self.device)
        self.assertFalse(compute_test.is_old_gpu)
        
    @patch('gpu_benchmark.stress_tests.compute.torch.cuda.get_device_capability')
    @patch('gpu_benchmark.stress_tests.compute.torch.cuda.get_device_properties')
    def test_detect_old_gpu_memory_old(self, mock_get_properties, mock_get_capability):
        # Mock compute capability to be modern (so it reaches memory check)
        mock_get_capability.return_value = (8, 6)  # Ampere
        
        # Add debugging to see what's happening
        print(f"self.device = {self.device}")
        print(f"type(self.device) = {type(self.device)}")
        
        mock_props = MagicMock()
        mock_props.total_memory = 2 * 1024 * 1024 * 1024  # 2GB
        mock_get_properties.side_effect = lambda device: mock_props
        
        # Check if mock is being called
        compute_test = ComputeStressTest(self.device)
        print(f"Mock called: {mock_get_properties.called}")
        print(f"Mock call count: {mock_get_properties.call_count}")
        if mock_get_properties.called:
            print(f"Mock called with: {mock_get_properties.call_args}")
        
        result = compute_test.is_old_gpu
        print(f"is_old_gpu result: {result}")
        self.assertTrue(result)

    @patch('gpu_benchmark.stress_tests.compute.torch.cuda.get_device_properties')
    def test_detect_old_gpu_memory_modern(self, mock_get_properties):
        mock_props = MagicMock()
        mock_props.total_memory = 8 * 1024 * 1024 * 1024  # 8GB
        mock_get_properties.side_effect = lambda device: mock_props
        
        compute_test = ComputeStressTest(self.device)
        self.assertFalse(compute_test.is_old_gpu)

    @patch('gpu_benchmark.stress_tests.compute.torch.randn')
    @patch('gpu_benchmark.stress_tests.compute.torch.matmul')
    @patch('gpu_benchmark.stress_tests.compute.torch.cuda.synchronize')
    @patch('gpu_benchmark.stress_tests.compute.time.time')
    def test_matrix_multiply_stress(self, mock_time, mock_sync, mock_matmul, mock_randn):
        """Test matrix multiplication stress test."""
        # Mock time to simulate test duration
        mock_time.side_effect = list(range(30))  # Provide enough values for all calls
        
        # Mock tensors
        mock_a = MagicMock()
        mock_b = MagicMock()
        mock_c = MagicMock()
        mock_randn.side_effect = [mock_a, mock_b]
        mock_matmul.return_value = mock_c

        result = self.compute_test.matrix_multiply_stress(size=1024, duration=10)

        self.assertIn("iterations", result)
        self.assertIn("tflops", result)
        self.assertIn("avg_time_per_iter", result)
        self.assertIn("matrix_size", result)
        self.assertIn("is_old_gpu", result)

        self.assertIsInstance(result["iterations"], int)
        self.assertIsInstance(result["tflops"], float)
        self.assertIsInstance(result["avg_time_per_iter"], float)
        self.assertIsInstance(result["matrix_size"], int)
        self.assertIsInstance(result["is_old_gpu"], bool)

    @patch('gpu_benchmark.stress_tests.compute.torch.randn')
    def test_matrix_multiply_stress_oom(self, mock_randn):
        mock_randn.side_effect = RuntimeError("CUDA out of memory")
        compute_test = ComputeStressTest(self.device)
        result = compute_test.matrix_multiply_stress(size=4096, duration=5)
        self.assertIsInstance(result, dict)
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'CUDA out of memory')


class TestMemoryStressTest(unittest.TestCase):
    """Test memory stress test functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.device = MagicMock()
        self.device.type = "cuda"
        self.device.index = 0
        self.memory_test = MemoryStressTest(self.device)

    @patch('gpu_benchmark.stress_tests.memory.torch.randn')
    @patch('gpu_benchmark.stress_tests.memory.torch.cuda.synchronize')
    @patch('gpu_benchmark.stress_tests.memory.time.time')
    def test_bandwidth_test(self, mock_time, mock_sync, mock_randn):
        """Test memory bandwidth test."""
        # Mock time to simulate test duration
        mock_time.side_effect = list(range(30))  # Provide enough values for all calls
        
        # Mock tensors
        mock_a = MagicMock()
        mock_b = MagicMock()
        mock_c = MagicMock()
        mock_randn.side_effect = [mock_a, mock_b]

        result = self.memory_test.bandwidth_test(size_mb=512, duration=10)

        self.assertIn("iterations", result)
        self.assertIn("bandwidth_gbps", result)
        self.assertIn("size_mb", result)
        self.assertIn("avg_time_per_iter", result)

        self.assertIsInstance(result["iterations"], int)
        self.assertIsInstance(result["bandwidth_gbps"], float)
        self.assertIsInstance(result["size_mb"], int)
        self.assertIsInstance(result["avg_time_per_iter"], float)

    def test_vram_stress_test_cpu(self):
        """Test VRAM stress test on CPU."""
        cpu_device = MagicMock()
        cpu_device.type = "cpu"
        cpu_memory_test = MemoryStressTest(cpu_device)

        result = cpu_memory_test.vram_stress_test(target_usage_pct=90)

        self.assertIn("target_usage_pct", result)
        self.assertIn("actual_allocated_gb", result)
        self.assertIn("num_tensors", result)
        self.assertIn("operation_time", result)
        self.assertIn("stable", result)

        self.assertEqual(result["target_usage_pct"], 90)
        self.assertEqual(result["actual_allocated_gb"], 0.5)
        self.assertEqual(result["num_tensors"], 1)
        self.assertTrue(result["stable"])

    @patch('gpu_benchmark.stress_tests.memory.torch.cuda.get_device_properties')
    @patch('gpu_benchmark.stress_tests.memory.torch.randn')
    @patch('gpu_benchmark.stress_tests.memory.torch.cuda.synchronize')
    @patch('gpu_benchmark.stress_tests.memory.time.time')
    def test_vram_stress_test_gpu(self, mock_time, mock_sync, mock_randn, mock_get_props):
        """Test VRAM stress test on GPU."""
        # Mock device properties
        mock_props = MagicMock()
        mock_props.total_memory = 8 * 1024 * 1024 * 1024  # 8GB
        mock_get_props.return_value = mock_props

        # Mock tensors
        mock_tensor = MagicMock()
        mock_randn.return_value = mock_tensor

        # Mock time
        mock_time.side_effect = [0, 0.1]  # 0.1 second operation

        result = self.memory_test.vram_stress_test(target_usage_pct=85)

        self.assertIn("target_usage_pct", result)
        self.assertIn("actual_allocated_gb", result)
        self.assertIn("num_tensors", result)
        self.assertIn("operation_time", result)
        self.assertIn("stable", result)

        self.assertEqual(result["target_usage_pct"], 85)
        self.assertTrue(result["stable"])

    @patch('gpu_benchmark.stress_tests.memory.torch.randn')
    @patch('gpu_benchmark.stress_tests.memory.torch.empty_like')
    @patch('gpu_benchmark.stress_tests.memory.torch.cuda.synchronize')
    @patch('gpu_benchmark.stress_tests.memory.time.time')
    def test_memory_copy_test(self, mock_time, mock_sync, mock_empty, mock_randn):
        """Test memory copy test."""
        # Mock time to simulate test duration
        mock_time.side_effect = list(range(30))  # Provide enough values for all calls
        
        # Mock tensors
        mock_host = MagicMock()
        mock_device = MagicMock()
        mock_device2 = MagicMock()
        mock_randn.side_effect = [mock_host, mock_device]
        mock_empty.return_value = mock_device2

        result = self.memory_test.memory_copy_test(size_mb=256, duration=5)

        self.assertIn("h2d_bandwidth_gbps", result)
        self.assertIn("d2d_bandwidth_gbps", result)
        self.assertIn("d2h_bandwidth_gbps", result)
        self.assertIn("size_mb", result)

        self.assertIsInstance(result["h2d_bandwidth_gbps"], float)
        self.assertIsInstance(result["d2d_bandwidth_gbps"], float)
        self.assertIsInstance(result["d2h_bandwidth_gbps"], float)
        self.assertEqual(result["size_mb"], 256)

    def test_memory_copy_test_cpu(self):
        """Test memory copy test on CPU."""
        cpu_device = MagicMock()
        cpu_device.type = "cpu"
        cpu_memory_test = MemoryStressTest(cpu_device)

        result = cpu_memory_test.memory_copy_test(size_mb=256, duration=5)

        # CPU should return zeros for bandwidth tests
        self.assertEqual(result["h2d_bandwidth_gbps"], 0)
        self.assertEqual(result["d2d_bandwidth_gbps"], 0)
        self.assertEqual(result["d2h_bandwidth_gbps"], 0)
        self.assertEqual(result["size_mb"], 256)


class TestMixedPrecisionTest(unittest.TestCase):
    """Test mixed precision test functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.device = MagicMock()
        self.device.type = "cuda"
        self.device.index = 0
        self.mixed_precision_test = MixedPrecisionTest(self.device)

    @patch('gpu_benchmark.stress_tests.mixed_precision.torch.cuda.get_device_capability')
    def test_check_fp16_support(self, mock_get_capability):
        mock_get_capability.return_value = (8, 6)  # Ampere
        mixed_precision_test = MixedPrecisionTest(self.device)
        self.assertTrue(mixed_precision_test._check_fp16_support())

    @patch('gpu_benchmark.stress_tests.mixed_precision.torch.cuda.get_device_capability')
    def test_check_bf16_support(self, mock_get_capability):
        mock_get_capability.return_value = (8, 0)  # Ampere
        mixed_precision_test = MixedPrecisionTest(self.device)
        self.assertTrue(mixed_precision_test._check_bf16_support())

    def test_check_bf16_support_cpu(self):
        """Test BF16 support checking on CPU."""
        cpu_device = MagicMock()
        cpu_device.type = "cpu"
        cpu_test = MixedPrecisionTest(cpu_device)

        # CPU support depends on PyTorch version
        # This test just ensures it doesn't crash
        result = cpu_test._check_bf16_support()
        self.assertIsInstance(result, bool)

    @patch('gpu_benchmark.stress_tests.mixed_precision.torch.randn')
    @patch('gpu_benchmark.stress_tests.mixed_precision.torch.matmul')
    @patch('gpu_benchmark.stress_tests.mixed_precision.torch.cuda.synchronize')
    @patch('gpu_benchmark.stress_tests.mixed_precision.time.time')
    def test_run_test(self, mock_time, mock_sync, mock_matmul, mock_randn):
        """Test mixed precision test run."""
        # Mock time to simulate test duration
        mock_time.side_effect = list(range(30))  # Provide enough values for all calls
        
        # Mock tensors
        mock_a = MagicMock()
        mock_b = MagicMock()
        mock_c = MagicMock()
        # Provide enough tensors for all calls (6 for 3 precisions)
        mock_randn.side_effect = [mock_a, mock_b, mock_a, mock_b, mock_a, mock_b]
        mock_matmul.return_value = mock_c

        # Patch support checks on the class, then instantiate
        with patch.object(MixedPrecisionTest, '_check_fp16_support', return_value=True):
            with patch.object(MixedPrecisionTest, '_check_bf16_support', return_value=True):
                mixed_precision_test = MixedPrecisionTest(self.device)
                result = mixed_precision_test.run_test(duration=5)

        self.assertIn("fp32", result)
        self.assertIn("fp16", result)
        self.assertIn("bf16", result)
        self.assertIn("mixed_precision_ready", result)
        self.assertTrue(result["fp16"]["supported"])
        self.assertTrue(result["bf16"]["supported"])

    @patch('gpu_benchmark.stress_tests.mixed_precision.torch.cuda.get_device_capability')
    @patch('gpu_benchmark.stress_tests.mixed_precision.torch.randn')
    @patch('gpu_benchmark.stress_tests.mixed_precision.torch.matmul')
    @patch('gpu_benchmark.stress_tests.mixed_precision.torch.cuda.synchronize')
    @patch('gpu_benchmark.stress_tests.mixed_precision.time.time')
    def test_tensor_core_test(self, mock_time, mock_sync, mock_matmul, mock_randn, mock_get_capability):
        """Test tensor core test."""
        # Mock modern GPU with tensor cores
        mock_get_capability.return_value = (8, 0)  # Ampere
        # Mock time to simulate test duration
        mock_time.side_effect = list(range(30))  # Provide enough values for all calls
        
        # Mock tensors
        mock_a = MagicMock()
        mock_b = MagicMock()
        mock_c = MagicMock()
        mock_randn.side_effect = [mock_a, mock_b]
        mock_matmul.return_value = mock_c

        result = self.mixed_precision_test.tensor_core_test(duration=5)

        self.assertIn("tensor_cores_available", result)
        self.assertIn("iterations", result)
        self.assertIn("tflops", result)
        self.assertIn("matrix_size", result)

        self.assertTrue(result["tensor_cores_available"])
        self.assertIsInstance(result["iterations"], int)
        self.assertIsInstance(result["tflops"], float)
        self.assertEqual(result["matrix_size"], 4096)

    def test_tensor_core_test_cpu(self):
        """Test tensor core test on CPU."""
        cpu_device = MagicMock()
        cpu_device.type = "cpu"
        cpu_test = MixedPrecisionTest(cpu_device)

        result = cpu_test.tensor_core_test(duration=5)

        self.assertFalse(result["tensor_cores_available"])


if __name__ == '__main__':
    unittest.main() 