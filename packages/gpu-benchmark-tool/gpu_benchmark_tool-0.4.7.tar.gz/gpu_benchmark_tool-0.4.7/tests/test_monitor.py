"""Tests for monitoring functionality."""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import numpy as np

# Add the parent directory to the path so we can import gpu_benchmark
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gpu_benchmark.monitor import (
    calculate_temperature_stability, stress_gpu_with_monitoring,
    enhanced_stress_test
)
from gpu_benchmark.backends.mock import MockGPUMonitor


class TestTemperatureStability(unittest.TestCase):
    """Test temperature stability calculation."""

    def test_calculate_temperature_stability_empty_list(self):
        """Test temperature stability with empty list."""
        result = calculate_temperature_stability([])
        
        self.assertIn("stability_score", result)
        self.assertIn("std_dev", result)
        self.assertIn("max_delta", result)
        self.assertIn("avg_rate_of_change", result)
        
        self.assertEqual(result["stability_score"], 0)
        self.assertEqual(result["std_dev"], 0)
        self.assertEqual(result["max_delta"], 0)

    def test_calculate_temperature_stability_single_value(self):
        """Test temperature stability with single value."""
        result = calculate_temperature_stability([75.0])
        
        self.assertIn("stability_score", result)
        self.assertIn("std_dev", result)
        self.assertIn("max_delta", result)
        self.assertIn("avg_rate_of_change", result)
        
        self.assertEqual(result["std_dev"], 0)
        self.assertEqual(result["max_delta"], 0)

    def test_calculate_temperature_stability_stable_temps(self):
        """Test temperature stability with stable temperatures."""
        stable_temps = [75.0, 75.1, 74.9, 75.0, 75.2]
        result = calculate_temperature_stability(stable_temps)
        
        self.assertIn("stability_score", result)
        self.assertIn("std_dev", result)
        self.assertIn("max_delta", result)
        self.assertIn("avg_rate_of_change", result)
        
        # Stable temps should have high stability score
        self.assertGreater(result["stability_score"], 80)
        self.assertLess(result["std_dev"], 1.0)
        self.assertLess(result["max_delta"], 1.0)

    def test_calculate_temperature_stability_unstable_temps(self):
        """Test temperature stability with unstable temperatures."""
        unstable_temps = [75.0, 85.0, 65.0, 90.0, 70.0]
        result = calculate_temperature_stability(unstable_temps)
        
        self.assertIn("stability_score", result)
        self.assertIn("std_dev", result)
        self.assertIn("max_delta", result)
        self.assertIn("avg_rate_of_change", result)
        
        # Unstable temps should have low stability score
        self.assertLess(result["stability_score"], 50)
        self.assertGreater(result["std_dev"], 5.0)
        self.assertGreater(result["max_delta"], 20.0)

    def test_calculate_temperature_stability_increasing_temps(self):
        """Test temperature stability with increasing temperatures."""
        increasing_temps = [70.0, 72.0, 74.0, 76.0, 78.0]
        result = calculate_temperature_stability(increasing_temps)
        
        self.assertIn("stability_score", result)
        self.assertIn("std_dev", result)
        self.assertIn("max_delta", result)
        self.assertIn("avg_rate_of_change", result)
        
        # Increasing temps should have moderate stability score
        self.assertGreaterEqual(result["stability_score"], 0)
        self.assertLessEqual(result["stability_score"], 100)


class TestStressGPUWithMonitoring(unittest.TestCase):
    """Test stress GPU with monitoring functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_handle = MagicMock()

    @patch('gpu_benchmark.monitor.PYNVML_AVAILABLE', False)
    def test_stress_gpu_with_monitoring_no_nvml(self):
        """Test stress GPU monitoring when NVML is not available."""
        result = stress_gpu_with_monitoring(self.mock_handle, duration=10)
        
        self.assertIn("timestamp", result)
        self.assertIn("baseline_temp", result)
        self.assertIn("max_temp", result)
        self.assertIn("max_power", result)
        self.assertIn("utilization", result)
        self.assertIn("iterations", result)
        self.assertIn("telemetry_sample", result)
        
        # Should return -1 for unavailable metrics
        self.assertEqual(result["baseline_temp"], -1)
        self.assertEqual(result["max_temp"], -1)
        self.assertEqual(result["max_power"], -1)
        self.assertEqual(result["utilization"], -1)
        self.assertEqual(result["iterations"], 0)

    @patch('gpu_benchmark.monitor.PYNVML_AVAILABLE', True)
    @patch('gpu_benchmark.monitor.pynvml')
    @patch('gpu_benchmark.monitor.torch')
    def test_stress_gpu_with_monitoring_cpu_device(self, mock_torch, mock_pynvml):
        """Test stress GPU monitoring with CPU device."""
        # Mock torch to return CPU device
        mock_torch.device.return_value = MagicMock(type="cpu")
        mock_torch.cuda.is_available.return_value = False
        
        result = stress_gpu_with_monitoring(self.mock_handle, duration=5)
        
        self.assertIn("timestamp", result)
        self.assertIn("baseline_temp", result)
        self.assertIn("max_temp", result)
        self.assertIn("max_power", result)
        self.assertIn("utilization", result)
        self.assertIn("iterations", result)
        self.assertIn("telemetry_sample", result)
        
        # Should return mock values for CPU
        self.assertEqual(result["baseline_temp"], 45)
        self.assertEqual(result["max_temp"], 75)
        self.assertEqual(result["max_power"], 150)
        self.assertEqual(result["utilization"], 95)
        self.assertEqual(result["iterations"], 100)

    @patch('gpu_benchmark.monitor.PYNVML_AVAILABLE', True)
    @patch('gpu_benchmark.monitor.pynvml')
    @patch('gpu_benchmark.monitor.torch')
    @patch('time.time')
    def test_stress_gpu_with_monitoring_gpu_device(self, mock_time, mock_torch, mock_pynvml):
        """Test stress GPU monitoring with GPU device."""
        # Mock torch to return CUDA device
        mock_device = MagicMock(type="cuda")
        mock_torch.device.return_value = mock_device
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.synchronize.return_value = None
        
        # Mock tensors
        mock_a = MagicMock()
        mock_b = MagicMock()
        mock_c = MagicMock()
        mock_torch.randn.side_effect = [mock_a, mock_b]
        mock_torch.matmul.return_value = mock_c
        
        # Mock time to simulate test duration
        mock_time.side_effect = list(range(30))  # Provide enough values for all calls
        
        # Mock NVML responses
        mock_pynvml.nvmlDeviceGetTemperature.return_value = 75
        mock_pynvml.nvmlDeviceGetPowerUsage.return_value = 150000
        mock_util = MagicMock()
        mock_util.gpu = 95
        mock_pynvml.nvmlDeviceGetUtilizationRates.return_value = mock_util
        
        result = stress_gpu_with_monitoring(self.mock_handle, duration=5)
        
        self.assertIn("timestamp", result)
        self.assertIn("baseline_temp", result)
        self.assertIn("max_temp", result)
        self.assertIn("max_power", result)
        self.assertIn("utilization", result)
        self.assertIn("iterations", result)
        self.assertIn("telemetry_sample", result)
        
        # Should have reasonable values
        self.assertGreater(result["iterations"], 0)
        self.assertGreater(result["max_temp"], 0)
        self.assertGreater(result["max_power"], 0)


class TestEnhancedStressTest(unittest.TestCase):
    """Test enhanced stress test functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_monitor = MockGPUMonitor(device_id=0)

    @patch('gpu_benchmark.monitor.torch')
    def test_enhanced_stress_test_cpu_device(self, mock_torch):
        """Test enhanced stress test with CPU device."""
        # Mock torch to return CPU device
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = MagicMock(type="cpu")
        
        result = enhanced_stress_test(self.mock_monitor, duration=10, device_id=0)
        
        self.assertIn("timestamp", result)
        self.assertIn("baseline_temp", result)
        self.assertIn("baseline_power", result)
        self.assertIn("max_temp", result)
        self.assertIn("max_power", result)
        self.assertIn("avg_utilization", result)
        self.assertIn("temperature_stability", result)
        self.assertIn("throttle_events", result)
        self.assertIn("errors", result)
        self.assertIn("stress_test_results", result)

    @patch('gpu_benchmark.monitor.torch')
    @patch('gpu_benchmark.monitor.ComputeStressTest')
    @patch('gpu_benchmark.monitor.MemoryStressTest')
    @patch('gpu_benchmark.monitor.MixedPrecisionTest')
    def test_enhanced_stress_test_gpu_device(self, mock_mixed_precision, mock_memory, mock_compute, mock_torch):
        """Test enhanced stress test with GPU device."""
        # Mock torch to return CUDA device
        mock_torch.cuda.is_available.return_value = True
        mock_torch.device.return_value = MagicMock(type="cuda")
        
        # Mock stress test classes
        mock_compute_instance = MagicMock()
        mock_compute.return_value = mock_compute_instance
        mock_compute_instance.matrix_multiply_stress.return_value = {"tflops": 10.5}
        
        mock_memory_instance = MagicMock()
        mock_memory.return_value = mock_memory_instance
        mock_memory_instance.bandwidth_test.return_value = {"bandwidth_gbps": 800.0}
        mock_memory_instance.vram_stress_test.return_value = {"stable": True}
        
        mock_mixed_precision_instance = MagicMock()
        mock_mixed_precision.return_value = mock_mixed_precision_instance
        mock_mixed_precision_instance.run_test.return_value = {"fp16": {"supported": True}}
        
        # Mock threading
        with patch('gpu_benchmark.monitor.threading') as mock_threading:
            mock_thread = MagicMock()
            mock_threading.Thread.return_value = mock_thread
            
            result = enhanced_stress_test(self.mock_monitor, duration=10, device_id=0)
        
        self.assertIn("timestamp", result)
        self.assertIn("baseline_temp", result)
        self.assertIn("baseline_power", result)
        self.assertIn("max_temp", result)
        self.assertIn("max_power", result)
        self.assertIn("avg_utilization", result)
        self.assertIn("temperature_stability", result)
        self.assertIn("throttle_events", result)
        self.assertIn("errors", result)
        self.assertIn("stress_test_results", result)
        
        # Check that stress tests were called
        mock_compute_instance.matrix_multiply_stress.assert_called_once()
        mock_memory_instance.bandwidth_test.assert_called_once()
        mock_memory_instance.vram_stress_test.assert_called_once()
        mock_mixed_precision_instance.run_test.assert_called_once()

    @patch('gpu_benchmark.monitor.torch')
    def test_enhanced_stress_test_exception_handling(self, mock_torch):
        """Test enhanced stress test exception handling."""
        # Mock torch to return CUDA device
        mock_torch.cuda.is_available.return_value = True
        mock_torch.device.return_value = MagicMock(type="cuda")
        
        # Mock stress test to raise exception
        with patch('gpu_benchmark.monitor.ComputeStressTest') as mock_compute:
            mock_compute_instance = MagicMock()
            mock_compute.return_value = mock_compute_instance
            mock_compute_instance.matrix_multiply_stress.side_effect = Exception("Test error")
            
            # Mock threading
            with patch('gpu_benchmark.monitor.threading') as mock_threading:
                mock_thread = MagicMock()
                mock_threading.Thread.return_value = mock_thread
                
                result = enhanced_stress_test(self.mock_monitor, duration=10, device_id=0)
        
        self.assertIn("timestamp", result)
        self.assertIn("errors", result)
        self.assertIn("stress_test_results", result)
        
        # Should handle exceptions gracefully
        self.assertIsInstance(result["errors"], list)
        self.assertGreater(len(result["errors"]), 0)


class TestMockMonitorIntegration(unittest.TestCase):
    """Test integration with mock monitor."""

    def setUp(self):
        """Set up test fixtures."""
        self.monitor = MockGPUMonitor(device_id=0)

    def test_mock_monitor_interface(self):
        """Test that mock monitor provides expected interface."""
        # Test all required methods
        temp = self.monitor.get_temperature()
        power = self.monitor.get_power_usage()
        mem_info = self.monitor.get_memory_info()
        util = self.monitor.get_utilization()
        throttling, reasons = self.monitor.check_throttling()
        
        # Test return types
        self.assertIsInstance(temp, float)
        self.assertIsInstance(power, float)
        self.assertIsInstance(mem_info, dict)
        self.assertIsInstance(util, float)
        self.assertIsInstance(throttling, bool)
        self.assertIsInstance(reasons, list)
        
        # Test value ranges
        self.assertGreaterEqual(temp, 40)
        self.assertLessEqual(temp, 100)
        self.assertGreaterEqual(power, 40)
        self.assertLessEqual(power, 200)
        self.assertGreaterEqual(util, 0)
        self.assertLessEqual(util, 100)

    def test_mock_monitor_memory_info_structure(self):
        """Test mock monitor memory info structure."""
        mem_info = self.monitor.get_memory_info()
        
        required_keys = ["used_mb", "total_mb", "free_mb", "utilization_pct"]
        for key in required_keys:
            self.assertIn(key, mem_info)
            self.assertIsInstance(mem_info[key], (int, float))
        
        # Check memory consistency
        self.assertEqual(mem_info["used_mb"] + mem_info["free_mb"], mem_info["total_mb"])
        self.assertGreaterEqual(mem_info["utilization_pct"], 0)
        self.assertLessEqual(mem_info["utilization_pct"], 100)

    def test_mock_monitor_throttling_logic(self):
        """Test mock monitor throttling logic."""
        # Initially should not be throttling
        throttling, reasons = self.monitor.check_throttling()
        self.assertFalse(throttling)
        self.assertEqual(len(reasons), 0)
        
        # Simulate high temperature by manipulating the monitor
        self.monitor.base_temp = 85  # High temperature
        
        throttling, reasons = self.monitor.check_throttling()
        self.assertTrue(throttling)
        self.assertGreater(len(reasons), 0)
        self.assertIn("Thermal limit", reasons[0])


if __name__ == '__main__':
    unittest.main() 