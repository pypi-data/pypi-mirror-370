"""Utility functions for GPU Benchmark Tool.

This module provides color-coded output, progress indicators, and user-friendly formatting.
"""

import sys
import time
from typing import Optional, Callable


class Colors:
    """ANSI color codes for terminal output."""
    
    # Success colors (green)
    SUCCESS = '\033[92m'
    SUCCESS_BOLD = '\033[1;92m'
    
    # Warning colors (yellow)
    WARNING = '\033[93m'
    WARNING_BOLD = '\033[1;93m'
    
    # Error colors (red)
    ERROR = '\033[91m'
    ERROR_BOLD = '\033[1;91m'
    
    # Info colors (blue)
    INFO = '\033[94m'
    INFO_BOLD = '\033[1;94m'
    
    # Reset
    RESET = '\033[0m'
    
    # Check if colors are supported
    @staticmethod
    def is_supported():
        """Check if terminal supports colors."""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def colorize(text: str, color: str, bold: bool = False) -> str:
    """Add color to text if supported.
    
    Args:
        text: Text to colorize
        color: Color code from Colors class
        bold: Whether to make text bold
        
    Returns:
        Colorized text or original text if colors not supported
    """
    if not Colors.is_supported():
        return text
    
    if bold and color in [Colors.SUCCESS, Colors.WARNING, Colors.ERROR, Colors.INFO]:
        # Use bold version
        color = color.replace('[', '[1;')
    
    return f"{color}{text}{Colors.RESET}"


def print_success(message: str, bold: bool = False):
    """Print success message in green."""
    print(colorize(f"✓ {message}", Colors.SUCCESS, bold))


def print_warning(message: str, bold: bool = False):
    """Print warning message in yellow."""
    print(colorize(f"⚠ {message}", Colors.WARNING, bold))


def print_error(message: str, bold: bool = False):
    """Print error message in red."""
    print(colorize(f"✗ {message}", Colors.ERROR, bold))


def print_info(message: str, bold: bool = False):
    """Print info message in blue."""
    print(colorize(f"ℹ {message}", Colors.INFO, bold))


class ProgressBar:
    """Simple progress bar for long-running operations."""
    
    def __init__(self, total: int, description: str = "Progress", width: int = 50):
        """Initialize progress bar.
        
        Args:
            total: Total number of steps
            description: Description of the operation
            width: Width of the progress bar
        """
        self.total = total
        self.current = 0
        self.description = description
        self.width = width
        self.start_time = time.time()
    
    def update(self, step: int = 1):
        """Update progress bar.
        
        Args:
            step: Number of steps to advance
        """
        self.current += step
        self._display()
    
    def _display(self):
        """Display the progress bar."""
        if self.current > self.total:
            self.current = self.total
        
        # Calculate progress
        progress = self.current / self.total
        filled_width = int(self.width * progress)
        
        # Create progress bar
        bar = '█' * filled_width + '░' * (self.width - filled_width)
        
        # Calculate percentage
        percentage = int(progress * 100)
        
        # Calculate elapsed time
        elapsed = time.time() - self.start_time
        
        # Estimate remaining time
        if self.current > 0:
            rate = elapsed / self.current
            remaining = (self.total - self.current) * rate
            eta = f"ETA: {remaining:.1f}s"
        else:
            eta = "ETA: --"
        
        # Display progress bar
        print(f"\r{self.description}: [{bar}] {percentage}% ({self.current}/{self.total}) {eta}", end='', flush=True)
    
    def finish(self):
        """Finish the progress bar."""
        self.current = self.total
        self._display()
        print()  # New line after progress bar


def format_duration(seconds: float) -> str:
    """Format duration in a human-readable way.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_bytes(bytes_value: int) -> str:
    """Format bytes in a human-readable way.
    
    Args:
        bytes_value: Number of bytes
        
    Returns:
        Formatted bytes string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f}{unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f}PB" 