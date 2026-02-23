"""
Test suite for Heuristic Evaluator

Tests the board evaluation algorithms and heuristic calculations.
"""

import unittest
import numpy as np
from prediction.heuristic_evaluator import HeuristicEvaluator, BoardMetrics
from utils.frame_types import BoardState, PieceInfo


class TestHeuristicEvaluator(unittest.TestCase):
    """Test cases for HeuristicEvaluator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.evaluator = HeuristicEvaluator()
    
    def test_empty_board_evaluation(self):
        """Test evaluation of empty board"""
        # Create empty board state
        board_state = BoardState(
            pieces={},
            current_piece=None,
            next_pieces=[],
            hold_piece=None,
            score=0,
            level=1,
            lines_cleared=0,
            timestamp=0
        )
        
        result = self.evaluator.evaluate_board(board_state)
        
        # Empty board should have good score
        self.assertGreater(result['total_score'], 0)
        self.assertEqual(result['hole_count'], 0)
        self.assertEqual(result['lines_cleared'], 0)
        self.assertEqual(result['height_penalty'], 0)
    
    def test_board_with_holes(self):
        """Test evaluation of board with holes"""
        # Create board with holes
        pieces = {}
        # Add some pieces with holes underneath
        pieces[(0, 19)] = PieceInfo("I", (0, 19), 0, 1.0)
        pieces[(1, 19)] = PieceInfo("I", (1, 19), 0, 1.0)
        pieces[(2, 19)] = PieceInfo("I", (2, 19), 0, 1.0)
        pieces[(0, 18)] = PieceInfo("I", (0, 18), 0, 1.0)
        # Hole at (1, 18)
        pieces[(2, 18)] = PieceInfo("I", (2, 18), 0, 1.0)
        
        board_state = BoardState(
            pieces=pieces,
            current_piece=None,
            next_pieces=[],
            hold_piece=None,
            score=0,
            level=1,
            lines_cleared=0,
            timestamp=0
        )
        
        result = self.evaluator.evaluate_board(board_state)
        
        # Should detect holes and penalize
        self.assertGreater(result['hole_count'], 0)
        self.assertLess(result['hole_penalty'], 0)
    
    def test_completed_lines(self):
        """Test evaluation of board with completed lines"""
        # Create board with full line at bottom
        pieces = {}
        for x in range(10):
            pieces[(x, 19)] = PieceInfo("I", (x, 19), 0, 1.0)
        
        board_state = BoardState(
            pieces=pieces,
            current_piece=None,
            next_pieces=[],
            hold_piece=None,
            score=0,
            level=1,
            lines_cleared=0,
            timestamp=0
        )
        
        result = self.evaluator.evaluate_board(board_state)
        
        # Should detect completed line
        self.assertEqual(result['lines_cleared'], 1)
        self.assertGreater(result['line_score'], 0)
    
    def test_surface_roughness(self):
        """Test surface roughness calculation"""
        # Create board with uneven surface
        pieces = {}
        # High column on left
        for y in range(15, 20):
            pieces[(0, y)] = PieceInfo("I", (0, y), 0, 1.0)
        # Low column on right
        pieces[(9, 19)] = PieceInfo("I", (9, 19), 0, 1.0)
        
        board_state = BoardState(
            pieces=pieces,
            current_piece=None,
            next_pieces=[],
            hold_piece=None,
            score=0,
            level=1,
            lines_cleared=0,
            timestamp=0
        )
        
        result = self.evaluator.evaluate_board(board_state)
        
        # Should detect rough surface
        self.assertGreater(result['surface_roughness'], 0)
    
    def test_weight_updates(self):
        """Test updating heuristic weights"""
        original_weight = self.evaluator.weight_holes
        
        # Update weight
        self.evaluator.set_weights(holes=-5.0)
        
        # Check weight was updated
        self.assertEqual(self.evaluator.weight_holes, -5.0)
        self.assertNotEqual(self.evaluator.weight_holes, original_weight)
    
    def test_statistics_tracking(self):
        """Test statistics tracking"""
        # Perform evaluation
        board_state = BoardState(
            pieces={},
            current_piece=None,
            next_pieces=[],
            hold_piece=None,
            score=0,
            level=1,
            lines_cleared=0,
            timestamp=0
        )
        
        self.evaluator.evaluate_board(board_state)
        
        stats = self.evaluator.get_evaluation_statistics()
        
        # Should track evaluations
        self.assertGreater(stats['evaluations_performed'], 0)
        self.assertIn('heuristic_weights', stats)


if __name__ == '__main__':
    unittest.main()
