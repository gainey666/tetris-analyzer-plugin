"""
Test suite for Prediction Engine

Tests move prediction and evaluation functionality.
"""

import unittest
from prediction.prediction_engine import PredictionEngine, MoveType, MoveSuggestion
from utils.frame_types import BoardState, PieceInfo


class TestPredictionEngine(unittest.TestCase):
    """Test cases for PredictionEngine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = PredictionEngine()
    
    def test_empty_board_predictions(self):
        """Test predictions on empty board"""
        # Create empty board
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
        
        # No current piece should return empty predictions
        predictions = self.engine.predict_moves(board_state)
        self.assertEqual(len(predictions), 0)
    
    def test_current_piece_predictions(self):
        """Test predictions with current piece"""
        # Create board with current piece
        current_piece = PieceInfo("I", (5, 0), 0, 1.0)
        board_state = BoardState(
            pieces={},
            current_piece=current_piece,
            next_pieces=[],
            hold_piece=None,
            score=0,
            level=1,
            lines_cleared=0,
            timestamp=0
        )
        
        predictions = self.engine.predict_moves(board_state, current_piece)
        
        # Should generate some predictions
        self.assertGreater(len(predictions), 0)
        
        # Check prediction structure
        for pred in predictions:
            self.assertIsInstance(pred, MoveSuggestion)
            self.assertIn(pred.piece_type, ["I", "O", "T", "S", "Z", "J", "L"])
            self.assertIsInstance(pred.position, tuple)
            self.assertIsInstance(pred.orientation, int)
            self.assertIsInstance(pred.move_type, MoveType)
            self.assertIsInstance(pred.score, float)
            self.assertIsInstance(pred.confidence, float)
    
    def test_piece_shapes(self):
        """Test piece shape generation"""
        # Test I-piece shapes
        i_shape_0 = self.engine._get_piece_shape("I", 0)
        self.assertEqual(len(i_shape_0), 4)
        self.assertEqual(i_shape_0, [(0, 0), (1, 0), (2, 0), (3, 0)])
        
        i_shape_1 = self.engine._get_piece_shape("I", 1)
        self.assertEqual(len(i_shape_1), 4)
        self.assertEqual(i_shape_1, [(0, 0), (0, 1), (0, 2), (0, 3)])
        
        # Test O-piece (should be same in all orientations)
        o_shape_0 = self.engine._get_piece_shape("O", 0)
        o_shape_1 = self.engine._get_piece_shape("O", 1)
        self.assertEqual(o_shape_0, o_shape_1)
        self.assertEqual(len(o_shape_0), 4)
    
    def test_valid_moves_detection(self):
        """Test detection of valid moves"""
        piece = PieceInfo("I", (0, 0), 0, 1.0)
        board_state = BoardState(
            pieces={},
            current_piece=piece,
            next_pieces=[],
            hold_piece=None,
            score=0,
            level=1,
            lines_cleared=0,
            timestamp=0
        )
        
        valid_moves = self.engine._get_valid_moves(piece, board_state)
        
        # Should find valid moves
        self.assertGreater(len(valid_moves), 0)
        
        # Each move should be (x, y, orientation)
        for move in valid_moves:
            self.assertEqual(len(move), 3)
            self.assertIsInstance(move[0], int)  # x
            self.assertIsInstance(move[1], int)  # y
            self.assertIsInstance(move[2], int)  # orientation
    
    def test_piece_placement_validation(self):
        """Test piece placement validation"""
        # Empty board - should allow placement
        piece_shape = [(0, 0), (1, 0), (2, 0), (3, 0)]
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
        
        # Valid placement
        can_place = self.engine._can_place_piece(piece_shape, 0, 19, board_state)
        self.assertTrue(can_place)
        
        # Out of bounds
        can_place = self.engine._can_place_piece(piece_shape, 8, 19, board_state)
        self.assertFalse(can_place)
        
        # Collision with existing piece
        pieces = {(0, 19): PieceInfo("I", (0, 19), 0, 1.0)}
        board_state_with_piece = BoardState(
            pieces=pieces,
            current_piece=None,
            next_pieces=[],
            hold_piece=None,
            score=0,
            level=1,
            lines_cleared=0,
            timestamp=0
        )
        
        can_place = self.engine._can_place_piece(piece_shape, 0, 19, board_state_with_piece)
        self.assertFalse(can_place)
    
    def test_move_classification(self):
        """Test move type classification"""
        piece = PieceInfo("T", (5, 5), 0, 1.0)
        board_state = BoardState(
            pieces={},
            current_piece=piece,
            next_pieces=[],
            hold_piece=None,
            score=0,
            level=1,
            lines_cleared=0,
            timestamp=0
        )
        
        # Test different orientations
        move_type_0 = self.engine._classify_move(piece, 5, 10, 0, board_state)
        move_type_1 = self.engine._classify_move(piece, 5, 10, 1, board_state)
        
        self.assertIsInstance(move_type_0, MoveType)
        self.assertIsInstance(move_type_1, MoveType)
    
    def test_confidence_calculation(self):
        """Test confidence calculation"""
        evaluation = {
            'total_score': 75.0,
            'lines_cleared': 2,
            'height_score': 10.0,
            'hole_penalty': -5.0,
            'surface_score': 8.0
        }
        
        confidence = self.engine._calculate_confidence(evaluation, MoveType.DROP)
        
        # Confidence should be between 0 and 1
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_settings_updates(self):
        """Test updating engine settings"""
        # Update confidence threshold
        original_threshold = self.engine.confidence_threshold
        self.engine.set_confidence_threshold(0.8)
        self.assertEqual(self.engine.confidence_threshold, 0.8)
        self.assertNotEqual(self.engine.confidence_threshold, original_threshold)
        
        # Update max suggestions
        original_max = self.engine.max_suggestions
        self.engine.set_max_suggestions(3)
        self.assertEqual(self.engine.max_suggestions, 3)
        self.assertNotEqual(self.engine.max_suggestions, original_max)
        
        # Test invalid values
        with self.assertRaises(ValueError):
            self.engine.set_confidence_threshold(1.5)
        
        with self.assertRaises(ValueError):
            self.engine.set_max_suggestions(15)
    
    def test_statistics_tracking(self):
        """Test statistics tracking"""
        # Make some predictions
        board_state = BoardState(
            pieces={},
            current_piece=PieceInfo("I", (5, 0), 0, 1.0),
            next_pieces=[],
            hold_piece=None,
            score=0,
            level=1,
            lines_cleared=0,
            timestamp=0
        )
        
        self.engine.predict_moves(board_state, board_state.current_piece)
        
        stats = self.engine.get_prediction_statistics()
        
        # Should track predictions
        self.assertGreater(stats['predictions_made'], 0)
        self.assertIn('heuristic_weights', stats)
        self.assertIn('performance_stats', stats)


if __name__ == '__main__':
    unittest.main()
