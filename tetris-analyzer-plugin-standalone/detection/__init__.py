"""
Detection package for Tetris Analyzer Plugin

This package provides board detection and calibration functionality
using computer vision techniques with manual fallback options.
"""

from .board_detector import BoardDetector

__all__ = ['BoardDetector']
