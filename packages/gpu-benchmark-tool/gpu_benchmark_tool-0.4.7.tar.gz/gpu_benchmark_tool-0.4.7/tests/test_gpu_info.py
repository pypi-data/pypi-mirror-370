"""Tests for GPU information and monitoring features."""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import gpu_benchmark
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gpu_benchmark.diagnostics import get_gpu_info, print_temperature_thresholds
from gpu_benchmark.backends import get_gpu_backend, list_available_backends
from gpu_benchmark.backends.mock import MockBackend, MockGPUMonitor


class TestGPUInfo(unittest.TestCase):
    """Test GPU information gathering functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_handle = MagicMock()

    @patch('gpu_benchmark.diagnostics.pynvml')
    def test_get_gpu_info_with_nvml(self, mock_pynvml):
        """Test getting GPU info when NVML is available."""
        # Mock NVML responses
        mock_pynvml.nvmlDeviceGetTemperature.return_value = 75
        mock_pynvml.nvmlDeviceGetPowerUsage.return_value = 150000  # 150W in mW
        mock_memory_info = MagicMock()
        mock_memory_info.used = 4 * 1024 * 1024 * 1024  # 4GB
        mock_memory_info.total = 8 * 1024 * 1024 * 1024  # 8GB
        mock_pynvml.nvmlDeviceGetMemoryInfo.return_value = mock_memory_info
        mock_pynvml.nvmlDeviceGetFanSpeed.return_value = 80

        info = get_gpu_info(self.mock_handle)

        self.assertIn("Temperature (C)", info)
        self.assertIn("Power Usage (W)", info)
        self.assertIn("Memory Used (MB)", info)
        self.assertIn("Memory Total (MB)", info)
        self.assertIn("Fan Speed (%)", info)

        self.assertEqual(info["Temperature (C)"], 75)
        self.assertEqual(info["Power Usage (W)"], 150.0)
        self.assertEqual(info["Memory Used (MB)"], 4096)
        self.assertEqual(info["Memory Total (MB)"], 8192)
        self.assertEqual(info["Fan Speed (%)"], 80)

    @patch('gpu_benchmark.diagnostics.PYNVML_AVAILABLE', False)
    def test_get_gpu_info_without_nvml(self):
        """Test getting GPU info when NVML is not available."""
        info = get_gpu_info(self.mock_handle)

        self.assertIn("Temperature (C)", info)
        self.assertIn("Power Usage (W)", info)
        self.assertIn("Memory Used (MB)", info)
        self.assertIn("Memory Total (MB)", info)
        self.assertIn("Fan Speed (%)", info)

        # Should return -1 for unavailable metrics
        self.assertEqual(info["Temperature (C)"], -1)
        self.assertEqual(info["Power Usage (W)"], -1)
        self.assertEqual(info["Memory Used (MB)"], -1)
        self.assertEqual(info["Memory Total (MB)"], -1)
        self.assertEqual(info["Fan Speed (%)"], "Not available")

    @patch('gpu_benchmark.diagnostics.pynvml')
    def test_print_temperature_thresholds(self, mock_pynvml):
        """Test printing temperature thresholds."""
        # Mock successful threshold queries
        mock_pynvml.nvmlDeviceGetTemperatureThreshold.side_effect = [85, 105]

        with patch('builtins.print') as mock_print:
            print_temperature_thresholds(self.mock_handle)
            
            # Should have called print twice (slowdown and shutdown thresholds)
            self.assertEqual(mock_print.call_count, 2)

    @patch('gpu_benchmark.diagnostics.PYNVML_AVAILABLE', False)
    def test_print_temperature_thresholds_no_nvml(self):
        """Test printing temperature thresholds when NVML is not available."""
        with patch('builtins.print') as mock_print:
            print_temperature_thresholds(self.mock_handle)
            
            # Should print that NVIDIA GPU monitoring is not available
            mock_print.assert_called_with("NVIDIA GPU monitoring not available")


class TestBackendDetection(unittest.TestCase):
    """Test backend detection and listing functionality."""

    def test_list_available_backends(self):
        """Test listing available backends."""
        backends = list_available_backends()
        
        self.assertIsInstance(backends, list)
        
        # Should always include mock backend
        mock_backend = next((b for b in backends if b["type"] == "mock"), None)
        self.assertIsNotNone(mock_backend)
        self.assertEqual(mock_backend["device_count"], 1)

    def test_get_gpu_backend_mock(self):
        """Test getting mock backend."""
        backend = get_gpu_backend(backend_type="mock")
        
        self.assertIsInstance(backend, MockBackend)
        self.assertTrue(backend.is_available())
        self.assertEqual(backend.get_device_count(), 1)

    def test_get_gpu_backend_auto_fallback_to_mock(self):
        """Test auto backend selection falls back to mock when no real backends available."""
        backend = get_gpu_backend(backend_type="auto")
        
        # Should return mock backend when no real backends are available
        self.assertIsInstance(backend, MockBackend)


class TestMockBackend(unittest.TestCase):
    """Test mock backend functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.backend = MockBackend()

    def test_mock_backend_availability(self):
        """Test mock backend is always available."""
        self.assertTrue(self.backend.is_available())

    def test_mock_backend_device_count(self):
        """Test mock backend device count."""
        self.assertEqual(self.backend.get_device_count(), 1)

    def test_mock_backend_device_info(self):
        """Test mock backend device info."""
        info = self.backend.get_device_info(0)
        
        self.assertIn("name", info)
        self.assertIn("compute_capability", info)
        self.assertIn("total_memory_gb", info)
        self.assertIn("vendor", info)
        self.assertIn("backend", info)
        
        self.assertEqual(info["vendor"], "Mock")
        self.assertEqual(info["backend"], "Simulation")

    def test_mock_backend_create_monitor(self):
        """Test mock backend monitor creation."""
        monitor = self.backend.create_monitor(0)
        
        self.assertIsInstance(monitor, MockGPUMonitor)
        self.assertEqual(monitor.device_id, 0)


class TestMockMonitor(unittest.TestCase):
    """Test mock GPU monitor functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.monitor = MockGPUMonitor(device_id=0)

    def test_mock_monitor_temperature(self):
        """Test mock monitor temperature reading."""
        temp = self.monitor.get_temperature()
        
        self.assertIsInstance(temp, float)
        self.assertGreaterEqual(temp, 40)  # Should be around 45 initially
        self.assertLessEqual(temp, 100)    # Should not exceed reasonable limits

    def test_mock_monitor_power_usage(self):
        """Test mock monitor power usage reading."""
        power = self.monitor.get_power_usage()
        
        self.assertIsInstance(power, float)
        self.assertGreaterEqual(power, 40)  # Should be around 50 initially
        self.assertLessEqual(power, 200)    # Should not exceed reasonable limits

    def test_mock_monitor_memory_info(self):
        """Test mock monitor memory info."""
        mem_info = self.monitor.get_memory_info()
        
        self.assertIn("used_mb", mem_info)
        self.assertIn("total_mb", mem_info)
        self.assertIn("free_mb", mem_info)
        self.assertIn("utilization_pct", mem_info)
        
        self.assertEqual(mem_info["used_mb"], 4096)
        self.assertEqual(mem_info["total_mb"], 8192)
        self.assertEqual(mem_info["free_mb"], 4096)
        self.assertEqual(mem_info["utilization_pct"], 50.0)

    def test_mock_monitor_utilization(self):
        """Test mock monitor utilization reading."""
        util = self.monitor.get_utilization()
        
        self.assertIsInstance(util, float)
        self.assertGreaterEqual(util, 0)
        self.assertLessEqual(util, 100)

    def test_mock_monitor_throttling(self):
        """Test mock monitor throttling detection."""
        is_throttling, reasons = self.monitor.check_throttling()
        
        self.assertIsInstance(is_throttling, bool)
        self.assertIsInstance(reasons, list)
        
        # Initially should not be throttling
        self.assertFalse(is_throttling)
        self.assertEqual(len(reasons), 0)


if __name__ == '__main__':
    unittest.main() 