"""
Recognition package for Tetris Analyzer Plugin

This package provides piece recognition functionality using template matching
and color heuristics with confidence scoring.
"""

from .piece_recognizer import PieceRecognizer, PieceType

__all__ = ['PieceRecognizer', 'PieceType']
