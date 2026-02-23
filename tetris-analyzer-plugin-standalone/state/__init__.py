"""
State package for Tetris Analyzer Plugin

This package provides deterministic game state management with validation
and state transition tracking.
"""

from .game_state_manager import GameStateManager, GameState, StateTransition

__all__ = ['GameStateManager', 'GameState', 'StateTransition']
