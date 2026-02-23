"""
Prediction Engine for Tetris Analyzer Plugin

This module provides move prediction and evaluation using heuristic algorithms
with future support for machine learning models.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time
from utils.frame_types import BoardState, PieceInfo, BoardCalibration
from utils.performance import measure_latency, perf_monitor
from .heuristic_evaluator import HeuristicEvaluator


class MoveType(Enum):
    """Types of moves"""
    DROP = "drop"
    SLIDE = "slide"
    ROTATE = "rotate"
    TSPIN = "tspin"


@dataclass
class MoveSuggestion:
    """Move suggestion with evaluation"""
    piece_type: str
    position: Tuple[int, int]
    orientation: int
    move_type: MoveType
    score: float
    confidence: float
    reasoning: str
    timestamp: int


class PredictionEngine:
    """Heuristic-based move prediction engine"""
    
    def __init__(self):
        """Initialize prediction engine"""
        self.heuristic_evaluator = HeuristicEvaluator()
        self.max_suggestions = 5
        self.confidence_threshold = 0.3
        
        # Prediction parameters
        self.lookahead_depth = 3
        self.weight_score = 1.0
        self.weight_lines = 2.0
        self.weight_height = 1.5
        self.weight_holes = 2.0
        
        # Performance tracking
        self.predictions_made = 0
        self.last_prediction_time = 0
    
    @measure_latency("prediction")
    def predict_moves(self, board_state: BoardState, current_piece: Optional[PieceInfo] = None) -> List[MoveSuggestion]:
        """
        Predict best moves for current piece
        
        Args:
            board_state: Current board state
            current_piece: Currently falling piece
            
        Returns:
            List of move suggestions ranked by score
        """
        try:
            if not current_piece:
                return []
            
            self.predictions_made += 1
            self.last_prediction_time = int(time.time() * 1000)
            
            # Get all valid moves
            valid_moves = self._get_valid_moves(current_piece, board_state)
            
            if not valid_moves:
                return []
            
            # Evaluate each move
            suggestions = []
            for x, y, orientation in valid_moves:
                suggestion = self._evaluate_move(current_piece, x, y, orientation, board_state)
                if suggestion and suggestion.confidence >= self.confidence_threshold:
                    suggestions.append(suggestion)
            
            # Sort by score (descending)
            suggestions.sort(key=lambda s: s.score, reverse=True)
            
            # Return top suggestions
            return suggestions[:self.max_suggestions]
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return []
    
    def _get_valid_moves(self, piece: PieceInfo, board_state: BoardState) -> List[Tuple[int, int, int]]:
        """Get all valid moves for a piece"""
        valid_moves = []
        
        for orientation in range(4):
            piece_shape = self._get_piece_shape(piece.piece_type, orientation)
            
            # Try all possible positions
            for y in range(20):  # Board height
                for x in range(10):  # Board width
                    if self._can_place_piece(piece_shape, x, y, board_state):
                        valid_moves.append((x, y, orientation))
        
        return valid_moves
    
    def _can_place_piece(self, piece_shape: List[Tuple[int, int]], x: int, y: int, board_state: BoardState) -> bool:
        """Check if piece can be placed at position"""
        for dx, dy in piece_shape:
            check_x = x + dx
            check_y = y + dy
            
            # Check bounds
            if not (0 <= check_x < 10 and 0 <= check_y < 20):
                return False
            
            # Check collision
            if board_state.is_position_occupied(check_x, check_y):
                return False
        
        return True
    
    def _evaluate_move(self, piece: PieceInfo, x: int, y: int, orientation: int, board_state: BoardState) -> Optional[MoveSuggestion]:
        """Evaluate a specific move"""
        try:
            # Simulate placing piece
            simulated_board = self._simulate_piece_placement(piece, x, y, orientation, board_state)
            
            # Evaluate using heuristics
            evaluation = self.heuristic_evaluator.evaluate_board(simulated_board)
            
            # Determine move type
            move_type = self._classify_move(piece, x, y, orientation, board_state)
            
            # Calculate confidence
            confidence = self._calculate_confidence(evaluation, move_type)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(evaluation, move_type)
            
            return MoveSuggestion(
                piece_type=piece.piece_type,
                position=(x, y),
                orientation=orientation,
                move_type=move_type,
                score=evaluation['total_score'],
                confidence=confidence,
                reasoning=reasoning,
                timestamp=int(time.time() * 1000)
            )
            
        except Exception as e:
            print(f"Move evaluation error: {e}")
            return None
    
    def _simulate_piece_placement(self, piece: PieceInfo, x: int, y: int, orientation: int, board_state: BoardState) -> BoardState:
        """Simulate placing a piece on the board"""
        # Create new board state
        new_pieces = board_state.pieces.copy()
        
        # Get piece shape
        piece_shape = self._get_piece_shape(piece.piece_type, orientation)
        
        # Add piece to board
        for dx, dy in piece_shape:
            piece_x = x + dx
            piece_y = y + dy
            
            piece_info = PieceInfo(
                piece_type=piece.piece_type,
                position=(piece_x, piece_y),
                orientation=orientation,
                confidence=1.0
            )
            new_pieces[(piece_x, piece_y)] = piece_info
        
        # Create new board state
        return BoardState(
            pieces=new_pieces,
            current_piece=None,
            next_pieces=board_state.next_pieces,
            hold_piece=board_state.hold_piece,
            score=board_state.score,
            level=board_state.level,
            lines_cleared=board_state.lines_cleared,
            timestamp=int(time.time() * 1000)
        )
    
    def _get_piece_shape(self, piece_type: str, orientation: int) -> List[Tuple[int, int]]:
        """Get piece shape for given type and orientation"""
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
    
    def _classify_move(self, piece: PieceInfo, x: int, y: int, orientation: int, board_state: BoardState) -> MoveType:
        """Classify the type of move"""
        # Simple classification - could be enhanced
        board_height = self._get_board_height(board_state)
        
        # Check if it's a T-spin (simplified)
        if piece.piece_type == "T" and orientation != 0:
            return MoveType.TSPIN
        
        # Check if it's a rotation
        if orientation != 0:
            return MoveType.ROTATE
        
        # Check if it's a slide (not at optimal position)
        optimal_x = self._get_optimal_drop_position(piece, board_state)
        if x != optimal_x:
            return MoveType.SLIDE
        
        # Default to drop
        return MoveType.DROP
    
    def _get_optimal_drop_position(self, piece: PieceInfo, board_state: BoardState) -> int:
        """Get optimal drop position for piece"""
        # Simple heuristic - prefer center
        return 5
    
    def _get_board_height(self, board_state: BoardState) -> int:
        """Get current board height"""
        occupied = board_state.get_occupied_positions()
        
        if not occupied:
            return 0
        
        highest_y = min(y for _, y in occupied)
        return 20 - highest_y
    
    def _calculate_confidence(self, evaluation: Dict[str, float], move_type: MoveType) -> float:
        """Calculate confidence in prediction"""
        base_confidence = 0.5
        
        # Adjust based on score
        if evaluation['total_score'] > 50:
            base_confidence += 0.3
        elif evaluation['total_score'] > 20:
            base_confidence += 0.1
        
        # Adjust based on move type
        if move_type == MoveType.TSPIN:
            base_confidence += 0.2
        elif move_type == MoveType.DROP:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def _generate_reasoning(self, evaluation: Dict[str, float], move_type: MoveType) -> str:
        """Generate reasoning for the move"""
        reasons = []
        
        if evaluation['lines_cleared'] > 0:
            reasons.append(f"Clears {evaluation['lines_cleared']} lines")
        
        if evaluation['height_score'] > 0:
            reasons.append("Good height placement")
        
        if evaluation['hole_penalty'] < 0:
            reasons.append("Avoids creating holes")
        
        if evaluation['surface_score'] > 0:
            reasons.append("Creates flat surface")
        
        if move_type == MoveType.TSPIN:
            reasons.append("T-spin opportunity")
        elif move_type == MoveType.SLIDE:
            reasons.append("Slide for better position")
        elif move_type == MoveType.DROP:
            reasons.append("Direct drop")
        
        return "; ".join(reasons) if reasons else "Standard placement"
    
    def get_prediction_statistics(self) -> Dict[str, Any]:
        """Get prediction statistics"""
        stats = {
            'predictions_made': self.predictions_made,
            'last_prediction_time': self.last_prediction_time,
            'confidence_threshold': self.confidence_threshold,
            'max_suggestions': self.max_suggestions,
            'lookahead_depth': self.lookahead_depth,
            'performance_stats': {
                'prediction': perf_monitor.get_stats('prediction_latency_ms')
            },
            'heuristic_weights': {
                'score': self.weight_score,
                'lines': self.weight_lines,
                'height': self.weight_height,
                'holes': self.weight_holes
            }
        }
        
        return stats
    
    def set_confidence_threshold(self, threshold: float):
        """Set confidence threshold for predictions"""
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
        else:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
    
    def set_max_suggestions(self, max_suggestions: int):
        """Set maximum number of suggestions"""
        if 1 <= max_suggestions <= 10:
            self.max_suggestions = max_suggestions
        else:
            raise ValueError("Max suggestions must be between 1 and 10")
    
    def update_weights(self, score: float = None, lines: float = None, height: float = None, holes: float = None):
        """Update heuristic weights"""
        if score is not None:
            self.weight_score = score
        if lines is not None:
            self.weight_lines = lines
        if height is not None:
            self.weight_height = height
        if holes is not None:
            self.weight_holes = holes
