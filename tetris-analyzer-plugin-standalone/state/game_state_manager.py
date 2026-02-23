"""
Game State Manager for Tetris Analyzer Plugin

This module provides deterministic state management for Tetris game state,
including board state tracking, piece validation, and state transitions.
"""

from typing import Dict, Tuple, Optional, List, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import time
from utils.frame_types import PieceInfo, BoardState, BoardCalibration
from utils.performance import measure_latency, perf_monitor


class GameState(Enum):
    """Game states"""
    IDLE = "idle"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    LINE_CLEAR = "line_clear"


@dataclass
class StateTransition:
    """State transition information"""
    from_state: GameState
    to_state: GameState
    timestamp: int
    piece_moved: Optional[Tuple[int, int]] = None
    lines_cleared: int = 0
    score_change: int = 0


class GameStateManager:
    """Deterministic game state manager for Tetris"""
    
    def __init__(self):
        """Initialize game state manager"""
        self.current_state: BoardState = BoardState(
            pieces={},
            current_piece=None,
            next_pieces=[],
            hold_piece=None,
            score=0,
            level=1,
            lines_cleared=0,
            timestamp=int(time.time() * 1000)
        )
        
        self.game_state: GameState = GameState.IDLE
        self.state_history: List[StateTransition] = []
        self.max_history = 1000
        
        # Tetris piece dimensions
        self.grid_width = 10
        self.grid_height = 20
        
        # Piece validation
        self.valid_pieces = {"I", "O", "T", "S", "Z", "J", "L"}
        
        # Statistics
        self.moves_count = 0
        self.pieces_placed = 0
        self.last_update_time = int(time.time() * 1000)
    
    @measure_latency("state_update")
    def update_state(self, pieces: Dict[Tuple[int, int], PieceInfo], 
                     current_piece: Optional[PieceInfo] = None,
                     next_pieces: List[str] = None,
                     hold_piece: Optional[str] = None,
                     score: int = None,
                     level: int = None,
                     lines_cleared: int = None) -> bool:
        """
        Update game state with validation
        
        Args:
            pieces: Dictionary of grid positions to piece info
            current_piece: Currently falling piece
            next_pieces: Queue of upcoming pieces
            hold_piece: Held piece type
            score: Current score
            level: Current level
            lines_cleared: Total lines cleared
            
        Returns:
            True if state updated successfully, False otherwise
        """
        try:
            # Validate inputs
            if not self._validate_state_update(pieces, current_piece, next_pieces, hold_piece, score, level, lines_cleared):
                return False
            
            # Create new state
            new_state = BoardState(
                pieces=pieces.copy(),
                current_piece=current_piece,
                next_pieces=next_pieces.copy() if next_pieces else [],
                hold_piece=hold_piece,
                score=score if score is not None else self.current_state.score,
                level=level if level is not None else self.current_state.level,
                lines_cleared=lines_cleared if lines_cleared is not None else self.current_state.lines_cleared,
                timestamp=int(time.time() * 1000)
            )
            
            # Check for state transitions
            self._check_state_transitions(self.current_state, new_state)
            
            # Update current state
            self.current_state = new_state
            self.last_update_time = new_state.timestamp
            
            # Update statistics
            self.moves_count += 1
            
            return True
            
        except Exception as e:
            print(f"State update error: {e}")
            return False
    
    def _validate_state_update(self, pieces: Dict[Tuple[int, int], PieceInfo], 
                             current_piece: Optional[PieceInfo],
                             next_pieces: List[str],
                             hold_piece: Optional[str],
                             score: Optional[int],
                             level: Optional[int],
                             lines_cleared: Optional[int]) -> bool:
        """Validate state update parameters"""
        try:
            # Validate pieces
            for pos, piece_info in pieces.items():
                if not self._is_valid_position(pos):
                    return False
                
                if piece_info.piece_type not in self.valid_pieces + ["empty"]:
                    return False
                
                if piece_info.position != pos:
                    return False
            
            # Validate current piece
            if current_piece:
                if current_piece.piece_type not in self.valid_pieces:
                    return False
                
                if not self._is_valid_position(current_piece.position):
                    return False
            
            # Validate next pieces
            if next_pieces:
                for piece_type in next_pieces:
                    if piece_type not in self.valid_pieces:
                        return False
            
            # Validate hold piece
            if hold_piece and hold_piece not in self.valid_pieces:
                return False
            
            # Validate numeric values
            if score is not None and score < 0:
                return False
            
            if level is not None and (level < 1 or level > 20):
                return False
            
            if lines_cleared is not None and lines_cleared < 0:
                return False
            
            return True
            
        except Exception as e:
            print(f"State validation error: {e}")
            return False
    
    def _is_valid_position(self, position: Tuple[int, int]) -> bool:
        """Check if position is within grid bounds"""
        x, y = position
        return 0 <= x < self.grid_width and 0 <= y < self.grid_height
    
    def _check_state_transitions(self, old_state: BoardState, new_state: BoardState):
        """Check for state transitions and record them"""
        try:
            # Check for line clear
            lines_diff = new_state.lines_cleared - old_state.lines_cleared
            if lines_diff > 0:
                transition = StateTransition(
                    from_state=self.game_state,
                    to_state=GameState.LINE_CLEAR,
                    timestamp=new_state.timestamp,
                    lines_cleared=lines_diff,
                    score_change=new_state.score - old_state.score
                )
                self._add_state_transition(transition)
            
            # Check for piece placement
            old_occupied = old_state.get_occupied_positions()
            new_occupied = new_state.get_occupied_positions()
            
            # If new pieces were added (piece placed)
            if len(new_occupied) > len(old_occupied):
                self.pieces_placed += 1
                
                transition = StateTransition(
                    from_state=self.game_state,
                    to_state=self.game_state,
                    timestamp=new_state.timestamp,
                    piece_moved=None  # Could be enhanced to track specific moves
                )
                self._add_state_transition(transition)
            
            # Check for game over (board full)
            if self._is_game_over(new_state):
                transition = StateTransition(
                    from_state=self.game_state,
                    to_state=GameState.GAME_OVER,
                    timestamp=new_state.timestamp
                )
                self._add_state_transition(transition)
                self.game_state = GameState.GAME_OVER
            
        except Exception as e:
            print(f"State transition check error: {e}")
    
    def _is_game_over(self, state: BoardState) -> bool:
        """Check if game is over (board full or no valid moves)"""
        try:
            # Simple check: if top rows are filled
            for y in range(2):  # Check top 2 rows
                for x in range(self.grid_width):
                    if (x, y) in state.pieces and state.pieces[(x, y)].piece_type != "empty":
                        return True
            
            return False
            
        except Exception:
            return False
    
    def _add_state_transition(self, transition: StateTransition):
        """Add state transition to history"""
        self.state_history.append(transition)
        
        # Keep history size limited
        if len(self.state_history) > self.max_history:
            self.state_history = self.state_history[-self.max_history:]
    
    def get_piece_at(self, x: int, y: int) -> Optional[PieceInfo]:
        """Get piece at specific grid position"""
        return self.current_state.get_piece_at(x, y)
    
    def is_position_occupied(self, x: int, y: int) -> bool:
        """Check if position is occupied"""
        return self.current_state.is_position_occupied(x, y)
    
    def get_occupied_positions(self) -> Set[Tuple[int, int]]:
        """Get all occupied positions"""
        return self.current_state.get_occupied_positions()
    
    def get_empty_positions(self) -> Set[Tuple[int, int]]:
        """Get all empty positions"""
        occupied = self.get_occupied_positions()
        all_positions = {(x, y) for x in range(self.grid_width) for y in range(self.grid_height)}
        return all_positions - occupied
    
    def can_place_piece(self, piece_type: str, position: Tuple[int, int], orientation: int = 0) -> bool:
        """Check if piece can be placed at position"""
        try:
            if piece_type not in self.valid_pieces:
                return False
            
            if not self._is_valid_position(position):
                return False
            
            # Get piece shape for this orientation
            piece_shape = self._get_piece_shape(piece_type, orientation)
            
            # Check if all positions are valid and empty
            for dy, dx in piece_shape:
                check_pos = (position[0] + dx, position[1] + dy)
                
                if not self._is_valid_position(check_pos):
                    return False
                
                if self.is_position_occupied(check_pos[0], check_pos[1]):
                    return False
            
            return True
            
        except Exception as e:
            print(f"Piece placement check error: {e}")
            return False
    
    def _get_piece_shape(self, piece_type: str, orientation: int) -> List[Tuple[int, int]]:
        """Get piece shape for given type and orientation"""
        # Define piece shapes (relative positions)
        shapes = {
            "I": {
                0: [(0, 0), (1, 0), (2, 0), (3, 0)],
                1: [(0, 0), (0, 1), (0, 2), (0, 3)],
                2: [(0, 0), (1, 0), (2, 0), (3, 0)],
                3: [(0, 0), (0, 1), (0, 2), (0, 3)]
            },
            "O": {
                0: [(0, 0), (1, 0), (0, 1), (1, 1)],
                1: [(0, 0), (1, 0), (0, 1), (1, 1)],
                2: [(0, 0), (1, 0), (0, 1), (1, 1)],
                3: [(0, 0), (1, 0), (0, 1), (1, 1)]
            },
            "T": {
                0: [(1, 0), (0, 1), (1, 1), (2, 1)],
                1: [(1, 0), (0, 1), (1, 1), (1, 2)],
                2: [(0, 0), (1, 0), (2, 0), (1, 1)],
                3: [(0, 0), (1, 0), (1, 1), (0, 2)]
            },
            "S": {
                0: [(1, 0), (2, 0), (0, 1), (1, 1)],
                1: [(0, 0), (0, 1), (1, 1), (1, 2)],
                2: [(1, 0), (2, 0), (0, 1), (1, 1)],
                3: [(0, 0), (0, 1), (1, 1), (1, 2)]
            },
            "Z": {
                0: [(0, 0), (1, 0), (1, 1), (2, 1)],
                1: [(1, 0), (0, 1), (1, 1), (0, 2)],
                2: [(0, 0), (1, 0), (1, 1), (2, 1)],
                3: [(1, 0), (0, 1), (1, 1), (0, 2)]
            },
            "J": {
                0: [(0, 0), (0, 1), (1, 1), (2, 1)],
                1: [(0, 0), (1, 0), (0, 1), (0, 2)],
                2: [(0, 0), (1, 0), (2, 0), (2, 1)],
                3: [(1, 0), (1, 1), (1, 2), (0, 2)]
            },
            "L": {
                0: [(2, 0), (0, 1), (1, 1), (2, 1)],
                1: [(0, 0), (0, 1), (0, 2), (1, 2)],
                2: [(0, 0), (1, 0), (2, 0), (0, 1)],
                3: [(0, 0), (1, 0), (1, 1), (1, 2)]
            }
        }
        
        return shapes.get(piece_type, {}).get(orientation % 4, [])
    
    def get_valid_moves(self, piece_type: str) -> List[Tuple[int, int, int]]:
        """Get all valid moves for a piece type"""
        valid_moves = []
        
        for orientation in range(4):
            piece_shape = self._get_piece_shape(piece_type, orientation)
            
            # Try all possible positions
            for y in range(self.grid_height):
                for x in range(self.grid_width):
                    if self.can_place_piece(piece_type, (x, y), orientation):
                        valid_moves.append((x, y, orientation))
        
        return valid_moves
    
    def get_board_height(self) -> int:
        """Get current board height (highest occupied row)"""
        occupied = self.get_occupied_positions()
        
        if not occupied:
            return 0
        
        highest_y = min(y for _, y in occupied)
        return self.grid_height - highest_y
    
    def get_danger_zones(self) -> List[Tuple[int, int]]:
        """Get positions that are dangerous (high stack)"""
        danger_rows = 4  # Top 4 rows are dangerous
        danger_positions = []
        
        for y in range(danger_rows):
            for x in range(self.grid_width):
                if self.is_position_occupied(x, y):
                    danger_positions.append((x, y))
        
        return danger_positions
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of current game state"""
        return {
            'game_state': self.game_state.value,
            'score': self.current_state.score,
            'level': self.current_state.level,
            'lines_cleared': self.current_state.lines_cleared,
            'pieces_placed': self.pieces_placed,
            'moves_count': self.moves_count,
            'board_height': self.get_board_height(),
            'danger_zones': len(self.get_danger_zones()),
            'occupied_positions': len(self.get_occupied_positions()),
            'empty_positions': len(self.get_empty_positions()),
            'current_piece': self.current_state.current_piece.piece_type if self.current_state.current_piece else None,
            'next_pieces': self.current_state.next_pieces[:3],  # Show next 3
            'hold_piece': self.current_state.hold_piece,
            'last_update': self.last_update_time,
            'state_transitions': len(self.state_history)
        }
    
    def get_state_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent state transitions"""
        recent_transitions = self.state_history[-limit:] if limit > 0 else self.state_history
        
        return [
            {
                'from_state': t.from_state.value,
                'to_state': t.to_state.value,
                'timestamp': t.timestamp,
                'piece_moved': t.piece_moved,
                'lines_cleared': t.lines_cleared,
                'score_change': t.score_change
            }
            for t in recent_transitions
        ]
    
    def reset_state(self):
        """Reset game state to initial values"""
        self.current_state = BoardState(
            pieces={},
            current_piece=None,
            next_pieces=[],
            hold_piece=None,
            score=0,
            level=1,
            lines_cleared=0,
            timestamp=int(time.time() * 1000)
        )
        
        self.game_state = GameState.IDLE
        self.moves_count = 0
        self.pieces_placed = 0
        self.last_update_time = int(time.time() * 1000)
        
        # Add reset transition
        transition = StateTransition(
            from_state=GameState.GAME_OVER if self.game_state == GameState.GAME_OVER else GameState.IDLE,
            to_state=GameState.IDLE,
            timestamp=int(time.time() * 1000)
        )
        self._add_state_transition(transition)
    
    def set_game_state(self, state: GameState):
        """Set game state"""
        old_state = self.game_state
        self.game_state = state
        
        transition = StateTransition(
            from_state=old_state,
            to_state=state,
            timestamp=int(time.time() * 1000)
        )
        self._add_state_transition(transition)
