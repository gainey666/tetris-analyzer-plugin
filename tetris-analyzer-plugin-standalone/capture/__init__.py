"""
Capture package for Tetris Analyzer Plugin

This package provides screen capture functionality with multiple capture methods
and a standardized interface for the analysis pipeline.
"""

from .capture_adapter import CaptureAdapter, PythonScreenCapture, WindowCapture, create_capture_adapter

__all__ = [
    'CaptureAdapter',
    'PythonScreenCapture', 
    'WindowCapture',
    'create_capture_adapter'
]
