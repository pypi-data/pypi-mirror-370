"""Unit tests for utility functions."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path so we can import gpu_benchmark
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gpu_benchmark.utils import (
    Colors, colorize, print_success, print_warning, print_error, print_info,
    ProgressBar, format_duration, format_bytes
)


class TestColors(unittest.TestCase):
    """Test color utility functions."""
    
    def test_colorize_with_colors_supported(self):
        """Test colorize function when colors are supported."""
        with patch('gpu_benchmark.utils.Colors.is_supported', return_value=True):
            result = colorize("test", Colors.SUCCESS)
            self.assertIn('\033[92m', result)
            self.assertIn('\033[0m', result)
    
    def test_colorize_without_colors_supported(self):
        """Test colorize function when colors are not supported."""
        with patch('gpu_benchmark.utils.Colors.is_supported', return_value=False):
            result = colorize("test", Colors.SUCCESS)
            self.assertEqual(result, "test")
    
    def test_colorize_bold(self):
        """Test colorize function with bold option."""
        with patch('gpu_benchmark.utils.Colors.is_supported', return_value=True):
            result = colorize("test", Colors.SUCCESS, bold=True)
            self.assertIn('\033[1;92m', result)
    
    @patch('builtins.print')
    def test_print_success(self, mock_print):
        """Test print_success function."""
        with patch('gpu_benchmark.utils.Colors.is_supported', return_value=True):
            print_success("Success message")
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            self.assertIn("✓ Success message", call_args)
            self.assertIn('\033[92m', call_args)
    
    @patch('builtins.print')
    def test_print_warning(self, mock_print):
        """Test print_warning function."""
        with patch('gpu_benchmark.utils.Colors.is_supported', return_value=True):
            print_warning("Warning message")
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            self.assertIn("⚠ Warning message", call_args)
            self.assertIn('\033[93m', call_args)
    
    @patch('builtins.print')
    def test_print_error(self, mock_print):
        """Test print_error function."""
        with patch('gpu_benchmark.utils.Colors.is_supported', return_value=True):
            print_error("Error message")
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            self.assertIn("✗ Error message", call_args)
            self.assertIn('\033[91m', call_args)
    
    @patch('builtins.print')
    def test_print_info(self, mock_print):
        """Test print_info function."""
        with patch('gpu_benchmark.utils.Colors.is_supported', return_value=True):
            print_info("Info message")
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            self.assertIn("ℹ Info message", call_args)
            self.assertIn('\033[94m', call_args)


class TestProgressBar(unittest.TestCase):
    """Test progress bar functionality."""
    
    @patch('builtins.print')
    def test_progress_bar_creation(self, mock_print):
        """Test progress bar creation."""
        progress = ProgressBar(10, "Test Progress", 40)
        self.assertEqual(progress.total, 10)
        self.assertEqual(progress.current, 0)
        self.assertEqual(progress.description, "Test Progress")
        self.assertEqual(progress.width, 40)
    
    @patch('builtins.print')
    def test_progress_bar_update(self, mock_print):
        """Test progress bar update."""
        progress = ProgressBar(5, "Test Progress")
        progress.update(2)
        self.assertEqual(progress.current, 2)
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_progress_bar_finish(self, mock_print):
        """Test progress bar finish."""
        progress = ProgressBar(3, "Test Progress")
        progress.finish()
        self.assertEqual(progress.current, 3)
        # Should call print twice: once for progress, once for newline
        self.assertGreaterEqual(mock_print.call_count, 2)


class TestFormatting(unittest.TestCase):
    """Test formatting utility functions."""
    
    def test_format_duration_seconds(self):
        """Test duration formatting for seconds."""
        self.assertEqual(format_duration(30.5), "30.5s")
    
    def test_format_duration_minutes(self):
        """Test duration formatting for minutes."""
        self.assertEqual(format_duration(90), "1.5m")
    
    def test_format_duration_hours(self):
        """Test duration formatting for hours."""
        self.assertEqual(format_duration(7200), "2.0h")
    
    def test_format_bytes_bytes(self):
        """Test bytes formatting for bytes."""
        self.assertEqual(format_bytes(512), "512.0B")
    
    def test_format_bytes_kilobytes(self):
        """Test bytes formatting for kilobytes."""
        self.assertEqual(format_bytes(1536), "1.5KB")
    
    def test_format_bytes_megabytes(self):
        """Test bytes formatting for megabytes."""
        self.assertEqual(format_bytes(1572864), "1.5MB")
    
    def test_format_bytes_gigabytes(self):
        """Test bytes formatting for gigabytes."""
        self.assertEqual(format_bytes(1610612736), "1.5GB")


if __name__ == '__main__':
    unittest.main() 