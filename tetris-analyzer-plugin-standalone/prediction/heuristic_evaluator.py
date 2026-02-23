"""
Heuristic Evaluator for Tetris Analyzer Plugin

This module provides board evaluation algorithms for move prediction
using various heuristics like height, holes, lines, and surface analysis.
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import time
from utils.frame_types import BoardState
from utils.performance import measure_latency, perf_monitor


@dataclass
class BoardMetrics:
    """Board evaluation metrics"""
    total_height: int
    max_height: int
    holes: int
    covered_cells: int
    lines_cleared: int
    surface_roughness: float
    well_depths: List[int]
    overhangs: int


class HeuristicEvaluator:
    """Heuristic-based board evaluation for Tetris positions"""
    
    def __init__(self):
        """Initialize heuristic evaluator"""
        # Heuristic weights
        self.weight_height = -1.0
        self.weight_holes = -2.0
        self.weight_lines = 3.0
        self.weight_roughness = -1.5
        self.weight_wells = -0.5
        self.weight_overhangs = -1.0
        
        # Evaluation parameters
        self.board_width = 10
        self.board_height = 20
        
        # Performance tracking
        self.evaluations_performed = 0
        self.last_evaluation_time = 0
    
    @measure_latency("heuristic_evaluation")
    def evaluate_board(self, board_state: BoardState) -> Dict[str, float]:
        """
        Evaluate board position using multiple heuristics
        
        Args:
            board_state: Current board state
            
        Returns:
            Dictionary with evaluation scores and metrics
        """
        try:
            self.evaluations_performed += 1
            self.last_evaluation_time = int(time.time() * 1000)
            
            # Calculate board metrics
            metrics = self._calculate_board_metrics(board_state)
            
            # Calculate individual heuristic scores
            height_score = self._evaluate_height(metrics)
            hole_score = self._evaluate_holes(metrics)
            line_score = self._evaluate_lines(metrics)
            roughness_score = self._evaluate_surface_roughness(metrics)
            well_score = self._evaluate_wells(metrics)
            overhang_score = self._evaluate_overhangs(metrics)
            
            # Calculate total score (higher is better)
            total_score = (
                line_score +  # Positive for line clears
                abs(self.weight_height) * (20 - metrics.total_height) +  # Positive for low height
                abs(self.weight_holes) * (10 - metrics.holes) +  # Positive for few holes
                abs(self.weight_roughness) * (10 - metrics.surface_roughness) +  # Positive for smooth surface
                abs(self.weight_wells) * (5 - sum(metrics.well_depths)) +  # Positive for few wells
                abs(self.weight_overhangs) * (5 - metrics.overhangs)  # Positive for few overhangs
            )
            
            return {
                'total_score': total_score,
                'height_score': height_score,
                'hole_penalty': -hole_score,  # Make it negative penalty
                'line_score': line_score,
                'surface_score': roughness_score,
                'well_score': well_score,
                'overhang_penalty': -overhang_score,  # Make it negative penalty
                'lines_cleared': metrics.lines_cleared,
                'height_penalty': metrics.total_height,
                'hole_count': metrics.holes,
                'surface_roughness': metrics.surface_roughness,
                'metrics': metrics
            }
            
        except Exception as e:
            print(f"Heuristic evaluation error: {e}")
            return {
                'total_score': -1000.0,
                'height_score': 0.0,
                'hole_penalty': -100.0,
                'line_score': 0.0,
                'surface_score': 0.0,
                'well_score': 0.0,
                'overhang_penalty': 0.0,
                'lines_cleared': 0,
                'height_penalty': 20,
                'hole_count': 10,
                'surface_roughness': 10.0,
                'metrics': None
            }
    
    def _calculate_board_metrics(self, board_state: BoardState) -> BoardMetrics:
        """Calculate detailed board metrics"""
        # Create board representation
        board = self._create_board_array(board_state)
        
        # Calculate column heights
        column_heights = self._get_column_heights(board)
        
        # Calculate total and max height
        total_height = sum(column_heights)
        max_height = max(column_heights) if column_heights else 0
        
        # Count holes and covered cells
        holes, covered_cells = self._count_holes_and_covered(board, column_heights)
        
        # Check for completed lines
        lines_cleared = self._count_completed_lines(board)
        
        # Calculate surface roughness
        surface_roughness = self._calculate_surface_roughness(column_heights)
        
        # Find well depths
        well_depths = self._find_wells(column_heights)
        
        # Count overhangs
        overhangs = self._count_overhangs(board, column_heights)
        
        return BoardMetrics(
            total_height=total_height,
            max_height=max_height,
            holes=holes,
            covered_cells=covered_cells,
            lines_cleared=lines_cleared,
            surface_roughness=surface_roughness,
            well_depths=well_depths,
            overhangs=overhangs
        )
    
    def _create_board_array(self, board_state: BoardState) -> np.ndarray:
        """Create 2D array representation of board"""
        board = np.zeros((self.board_height, self.board_width), dtype=int)
        
        for (x, y), piece in board_state.pieces.items():
            if 0 <= x < self.board_width and 0 <= y < self.board_height:
                # Convert game coordinates (y=19 is bottom) to array indices (y=0 is top)
                array_y = self.board_height - 1 - y
                board[array_y, x] = 1
        
        return board
    
    def _get_column_heights(self, board: np.ndarray) -> List[int]:
        """Get height of each column"""
        heights = []
        
        for x in range(self.board_width):
            column = board[:, x]
            # Find first occupied cell from top
            occupied_cells = np.where(column > 0)[0]
            if len(occupied_cells) > 0:
                height = self.board_height - occupied_cells[0]
            else:
                height = 0
            heights.append(height)
        
        return heights
    
    def _count_holes_and_covered(self, board: np.ndarray, column_heights: List[int]) -> Tuple[int, int]:
        """Count holes and covered cells"""
        holes = 0
        covered_cells = 0
        
        for x in range(self.board_width):
            column_height = column_heights[x]
            if column_height == 0:
                continue
            
            # Find the first occupied cell
            first_occupied = self.board_height - column_height
            
            # Count holes below occupied cells
            for y in range(first_occupied + 1, self.board_height):
                if board[y, x] == 0:
                    holes += 1
                else:
                    covered_cells += 1
        
        return holes, covered_cells
    
    def _count_completed_lines(self, board: np.ndarray) -> int:
        """Count completed lines"""
        lines_cleared = 0
        
        for y in range(self.board_height):
            if np.all(board[y, :] > 0):
                lines_cleared += 1
        
        return lines_cleared
    
    def _calculate_surface_roughness(self, column_heights: List[int]) -> float:
        """Calculate surface roughness (height variation)"""
        if len(column_heights) < 2:
            return 0.0
        
        roughness = 0.0
        for i in range(len(column_heights) - 1):
            roughness += abs(column_heights[i] - column_heights[i + 1])
        
        return roughness
    
    def _find_wells(self, column_heights: List[int]) -> List[int]:
        """Find wells (deep gaps between columns)"""
        wells = []
        
        for i in range(len(column_heights)):
            left_height = column_heights[i - 1] if i > 0 else self.board_height
            right_height = column_heights[i + 1] if i < len(column_heights) - 1 else self.board_height
            current_height = column_heights[i]
            
            # Calculate well depth
            well_depth = min(left_height, right_height) - current_height
            if well_depth > 0:
                wells.append(well_depth)
        
        return wells
    
    def _count_overhangs(self, board: np.ndarray, column_heights: List[int]) -> int:
        """Count overhangs (cells hanging over empty spaces)"""
        overhangs = 0
        
        for x in range(self.board_width):
            column_height = column_heights[x]
            if column_height == 0:
                continue
            
            # Check for overhangs in this column
            for y in range(self.board_height - column_height, self.board_height):
                if board[y, x] > 0:
                    # Check if cell below is empty
                    if y > 0 and board[y - 1, x] == 0:
                        overhangs += 1
        
        return overhangs
    
    def _evaluate_height(self, metrics: BoardMetrics) -> float:
        """Evaluate board height (lower is better)"""
        return metrics.total_height
    
    def _evaluate_holes(self, metrics: BoardMetrics) -> float:
        """Evaluate holes (negative penalty)"""
        return metrics.holes
    
    def _evaluate_lines(self, metrics: BoardMetrics) -> float:
        """Evaluate line clears (positive reward)"""
        return metrics.lines_cleared * 10  # Bonus per line
    
    def _evaluate_surface_roughness(self, metrics: BoardMetrics) -> float:
        """Evaluate surface roughness (smoother is better)"""
        return metrics.surface_roughness
    
    def _evaluate_wells(self, metrics: BoardMetrics) -> float:
        """Evaluate wells (deep wells are bad)"""
        return sum(metrics.well_depths)
    
    def _evaluate_overhangs(self, metrics: BoardMetrics) -> float:
        """Evaluate overhangs (negative penalty)"""
        return metrics.overhangs
    
    def get_evaluation_statistics(self) -> Dict[str, Any]:
        """Get evaluation statistics"""
        stats = {
            'evaluations_performed': self.evaluations_performed,
            'last_evaluation_time': self.last_evaluation_time,
            'performance_stats': {
                'heuristic_evaluation': perf_monitor.get_stats('heuristic_evaluation_latency_ms')
            },
            'heuristic_weights': {
                'height': self.weight_height,
                'holes': self.weight_holes,
                'lines': self.weight_lines,
                'roughness': self.weight_roughness,
                'wells': self.weight_wells,
                'overhangs': self.weight_overhangs
            }
        }
        
        return stats
    
    def set_weights(self, height: float = None, holes: float = None, lines: float = None,
                   roughness: float = None, wells: float = None, overhangs: float = None):
        """Update heuristic weights"""
        if height is not None:
            self.weight_height = height
        if holes is not None:
            self.weight_holes = holes
        if lines is not None:
            self.weight_lines = lines
        if roughness is not None:
            self.weight_roughness = roughness
        if wells is not None:
            self.weight_wells = wells
        if overhangs is not None:
            self.weight_overhangs = overhangs
    
    def reset_statistics(self):
        """Reset evaluation statistics"""
        self.evaluations_performed = 0
        self.last_evaluation_time = 0
