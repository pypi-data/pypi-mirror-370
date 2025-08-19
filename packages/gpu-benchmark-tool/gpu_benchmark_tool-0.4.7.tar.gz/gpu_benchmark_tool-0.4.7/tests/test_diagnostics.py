"""Unit tests for diagnostic functions."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path so we can import gpu_benchmark
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gpu_benchmark.diagnostics import (
    check_enhanced_monitoring_requirements,
    comprehensive_diagnostics,
    print_enhanced_monitoring_status,
    print_comprehensive_diagnostics
)


class TestEnhancedMonitoringRequirements(unittest.TestCase):
    """Test enhanced monitoring requirements check."""

    def test_check_enhanced_monitoring_requirements_structure(self):
        """Test that the requirements check returns the expected structure."""
        requirements = check_enhanced_monitoring_requirements()
        
        # Check expected keys
        expected_keys = ["pynvml", "torch", "cuda", "nvidia_gpu", "enhanced_available", "recommendations"]
        for key in expected_keys:
            self.assertIn(key, requirements)
        
        # Check data types
        self.assertIsInstance(requirements["pynvml"], bool)
        self.assertIsInstance(requirements["torch"], bool)
        self.assertIsInstance(requirements["cuda"], bool)
        self.assertIsInstance(requirements["nvidia_gpu"], bool)
        self.assertIsInstance(requirements["enhanced_available"], bool)
        self.assertIsInstance(requirements["recommendations"], list)

    @patch('gpu_benchmark.diagnostics.pynvml')
    def test_pynvml_check(self, mock_pynvml):
        """Test PyTorch availability check."""
        # Mock successful import
        with patch.dict('sys.modules', {'pynvml': mock_pynvml}):
            requirements = check_enhanced_monitoring_requirements()
            self.assertTrue(requirements["pynvml"])

    @patch('gpu_benchmark.diagnostics.torch')
    def test_torch_check(self, mock_torch):
        """Test PyTorch availability check."""
        mock_torch.cuda.is_available.return_value = True
        
        # Mock successful import
        with patch.dict('sys.modules', {'torch': mock_torch}):
            requirements = check_enhanced_monitoring_requirements()
            self.assertTrue(requirements["torch"])
            self.assertTrue(requirements["cuda"])

    @patch('gpu_benchmark.diagnostics.torch')
    def test_torch_cuda_disabled(self, mock_torch):
        """Test PyTorch with CUDA disabled."""
        mock_torch.cuda.is_available.return_value = False
        
        # Mock successful import
        with patch.dict('sys.modules', {'torch': mock_torch}):
            requirements = check_enhanced_monitoring_requirements()
            self.assertTrue(requirements["torch"])
            self.assertFalse(requirements["cuda"])


class TestComprehensiveDiagnostics(unittest.TestCase):
    """Test comprehensive diagnostics function."""

    def test_comprehensive_diagnostics_structure(self):
        """Test that comprehensive diagnostics returns the expected structure."""
        diagnostics = comprehensive_diagnostics()
        
        # Check expected keys
        expected_keys = ["torch", "pytorch", "cuda", "metal", "nvidia_container", "recommendations"]
        for key in expected_keys:
            self.assertIn(key, diagnostics)
        
        # Check torch structure
        torch_keys = ["present", "version", "cuda_enabled", "cuda_version"]
        for key in torch_keys:
            self.assertIn(key, diagnostics["torch"])

    @patch('gpu_benchmark.diagnostics.torch')
    def test_torch_detection(self, mock_torch):
        """Test PyTorch detection in comprehensive diagnostics."""
        mock_torch.__version__ = "2.1.0+cu118"
        mock_torch.cuda.is_available.return_value = True
        mock_torch.version.cuda = "11.8"
        
        # Mock successful import
        with patch.dict('sys.modules', {'torch': mock_torch}):
            diagnostics = comprehensive_diagnostics()
            self.assertTrue(diagnostics["torch"]["present"])
            self.assertEqual(diagnostics["torch"]["version"], "2.1.0+cu118")
            self.assertTrue(diagnostics["torch"]["cuda_enabled"])
            self.assertEqual(diagnostics["torch"]["cuda_version"], "11.8")

    @patch('gpu_benchmark.diagnostics.pynvml')
    def test_nvml_detection(self, mock_pynvml):
        """Test NVML detection in comprehensive diagnostics."""
        mock_pynvml.nvmlSystemGetCudaDriverVersion.return_value = 12040
        mock_pynvml.nvmlSystemGetDriverVersion.return_value = b"535.86.10"
        
        # Mock successful import and initialization
        with patch.dict('sys.modules', {'pynvml': mock_pynvml}):
            diagnostics = comprehensive_diagnostics()
            self.assertEqual(diagnostics["cuda"]["driver_version"], "12040")

    @patch('gpu_benchmark.diagnostics.sys')
    def test_metal_detection_macos(self, mock_sys):
        """Test Metal detection on macOS."""
        # Mock sys.platform
        mock_sys.platform = "darwin"
        
        # Mock subprocess.run to return success for system_profiler
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Metal: Version 3.1"
        
        # Mock torch module with proper attributes
        mock_torch = MagicMock()
        mock_torch.__version__ = "2.1.0"
        mock_torch.cuda.is_available.return_value = False
        
        # Mock the import to avoid actual import and mock subprocess
        with patch.dict('sys.modules', {
            'torch': mock_torch,
            'subprocess': MagicMock(run=MagicMock(return_value=mock_result))
        }):
            diagnostics = comprehensive_diagnostics()
            self.assertTrue(diagnostics["metal"]["present"])

    def test_nvidia_container_detection(self):
        """Test NVIDIA Container Toolkit detection."""
        # Mock subprocess.run to return success for nvidia-docker
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "nvidia-docker version 1.14.3"
        
        # Mock torch module with proper attributes
        mock_torch = MagicMock()
        mock_torch.__version__ = "2.1.0"
        mock_torch.cuda.is_available.return_value = False
        
        # Mock the import to avoid actual import and mock subprocess
        with patch.dict('sys.modules', {
            'torch': mock_torch,
            'subprocess': MagicMock(run=MagicMock(return_value=mock_result))
        }):
            diagnostics = comprehensive_diagnostics()
            self.assertTrue(diagnostics["nvidia_container"]["present"])


class TestDiagnosticPrintFunctions(unittest.TestCase):
    """Test diagnostic print functions."""

    @patch('builtins.print')
    def test_print_enhanced_monitoring_status(self, mock_print):
        """Test enhanced monitoring status print function."""
        result = print_enhanced_monitoring_status()
        self.assertIsInstance(result, bool)
        mock_print.assert_called()

    @patch('builtins.print')
    def test_print_comprehensive_diagnostics(self, mock_print):
        """Test comprehensive diagnostics print function."""
        result = print_comprehensive_diagnostics()
        self.assertIsInstance(result, dict)
        mock_print.assert_called()


if __name__ == '__main__':
    unittest.main() 