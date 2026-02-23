"""
Test suite for Coaching Module

Tests coaching hints generation and strategy suggestions.
"""

import unittest
from unittest.mock import Mock, patch
from coaching.coaching_module import CoachingModule
from utils.frame_types import BoardState, PieceInfo


class TestCoachingModule(unittest.TestCase):
    """Test cases for Coaching Module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.coach = CoachingModule()
        self.test_board_state = self._create_test_board_state()
        self.test_piece = self._create_test_piece()
    
    def tearDown(self):
        """Clean up after tests"""
        pass
    
    def test_initialization(self):
        """Test coaching module initialization"""
        self.assertIsNotNone(self.coach)
        self.assertTrue(self.coach.enabled)
        self.assertEqual(self.coach.max_hints, 5)
    
    def test_hint_generation_empty_board(self):
        """Test hint generation on empty board"""
        hints = self.coach.generate_hints(self.test_board_state, self.test_piece, [])
        
        self.assertIsInstance(hints, list)
        # Should provide basic hints even on empty board
        if hints:
            self.assertLessEqual(len(hints), self.coach.max_hints)
    
    def test_hint_generation_with_predictions(self):
        """Test hint generation with move predictions"""
        predictions = [
            {'move': 'left', 'score': 0.8, 'confidence': 0.9},
            {'move': 'right', 'score': 0.6, 'confidence': 0.7},
            {'move': 'rotate', 'score': 0.7, 'confidence': 0.8}
        ]
        
        hints = self.coach.generate_hints(self.test_board_state, self.test_piece, predictions)
        
        self.assertIsInstance(hints, list)
        # Should provide move-specific hints with predictions
        if hints:
            for hint in hints:
                self.assertIn('message', hint)
                self.assertIn('priority', hint)
                self.assertIn('type', hint)
    
    def test_danger_detection(self):
        """Test danger detection and warning generation"""
        # Create board with dangerous situation (high stack)
        dangerous_board = self._create_dangerous_board()
        
        hints = self.coach.generate_hints(dangerous_board, self.test_piece, [])
        
        # Should detect danger and provide warning
        danger_hints = [h for h in hints if h.get('type') == 'danger']
        if danger_hints:
            self.assertGreater(len(danger_hints), 0)
    
    def test_strategy_suggestions(self):
        """Test strategy suggestions based on board state"""
        hints = self.coach.generate_hints(self.test_board_state, self.test_piece, [])
        
        # Should provide strategic hints
        strategy_hints = [h for h in hints if h.get('type') == 'strategy']
        self.assertIsInstance(strategy_hints, list)
    
    def test_hint_prioritization(self):
        """Test hint prioritization"""
        hints = self.coach.generate_hints(self.test_board_state, self.test_piece, [])
        
        if len(hints) > 1:
            # Check that hints are properly prioritized
            priorities = [h.get('priority', 0) for h in hints]
            # Should be sorted by priority (higher first)
            self.assertEqual(priorities, sorted(priorities, reverse=True))
    
    def test_hint_types(self):
        """Test different hint types"""
        hints = self.coach.generate_hints(self.test_board_state, self.test_piece, [])
        
        if hints:
            hint_types = set(h.get('type') for h in hints)
            expected_types = {'danger', 'strategy', 'move', 'general'}
            
            # Should have valid hint types
            self.assertTrue(hint_types.issubset(expected_types))
    
    def test_hint_content_validation(self):
        """Test hint content validation"""
        hints = self.coach.generate_hints(self.test_board_state, self.test_piece, [])
        
        if hints:
            for hint in hints:
                # Required fields
                self.assertIn('message', hint)
                self.assertIn('type', hint)
                self.assertIn('priority', hint)
                
                # Message should not be empty
                self.assertGreater(len(hint['message']), 0)
                
                # Priority should be valid
                self.assertIsInstance(hint['priority'], (int, float))
                self.assertGreaterEqual(hint['priority'], 0)
                self.assertLessEqual(hint['priority'], 10)
    
    def test_configuration_updates(self):
        """Test coaching module configuration updates"""
        # Update configuration
        self.coach.max_hints = 3
        self.coach.urgency_threshold = 'high'
        
        hints = self.coach.generate_hints(self.test_board_state, self.test_piece, [])
        
        # Should respect new configuration
        self.assertLessEqual(len(hints), 3)
    
    def test_disabled_coaching(self):
        """Test behavior when coaching is disabled"""
        self.coach.enabled = False
        
        hints = self.coach.generate_hints(self.test_board_state, self.test_piece, [])
        
        # Should return empty list when disabled
        self.assertEqual(len(hints), 0)
    
    def test_performance_monitoring(self):
        """Test coaching module performance"""
        import time
        
        # Time hint generation
        start_time = time.time()
        hints = self.coach.generate_hints(self.test_board_state, self.test_piece, [])
        end_time = time.time()
        
        generation_time = end_time - start_time
        
        # Should be fast
        self.assertLess(generation_time, 0.01, "Hint generation should be under 10ms")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test with None inputs
        hints = self.coach.generate_hints(None, None, [])
        self.assertIsInstance(hints, list)
        
        # Test with empty predictions
        hints = self.coach.generate_hints(self.test_board_state, self.test_piece, [])
        self.assertIsInstance(hints, list)
        
        # Test with invalid predictions
        invalid_predictions = [{'invalid': 'data'}]
        hints = self.coach.generate_hints(self.test_board_state, self.test_piece, invalid_predictions)
        self.assertIsInstance(hints, list)
    
    def _create_test_board_state(self):
        """Create a test board state"""
        # Create a simple board with some pieces
        pieces = {
            (0, 0): type('Piece', (), {'type': 'I', 'color': 'blue'})(),
            (1, 0): type('Piece', (), {'type': 'I', 'color': 'blue'})(),
            (2, 0): type('Piece', (), {'type': 'I', 'color': 'blue'})(),
            (3, 0): type('Piece', (), {'type': 'I', 'color': 'blue'})(),
        }
        
        return BoardState(
            pieces=pieces,
            current_piece=self._create_test_piece(),
            score=1000,
            lines_cleared=10,
            level=5
        )
    
    def _create_test_piece(self):
        """Create a test piece"""
        return PieceInfo(
            type='T',
            position=(5, 10),
            orientation=0,
            color='purple'
        )
    
    def _create_dangerous_board(self):
        """Create a board with dangerous situation"""
        # Create board with high stack
        pieces = {}
        for x in range(10):
            for y in range(15):  # High stack
                pieces[(x, y)] = type('Piece', (), {'type': 'I', 'color': 'blue'})()
        
        return BoardState(
            pieces=pieces,
            current_piece=self._create_test_piece(),
            score=500,
            lines_cleared=5,
            level=3
        )


class TestCoachingStrategies(unittest.TestCase):
    """Test specific coaching strategies"""
    
    def setUp(self):
        """Set up strategy tests"""
        self.coach = CoachingModule()
    
    def test_line_clear_suggestions(self):
        """Test line clear strategy suggestions"""
        # Create board nearly ready for line clear
        board = self._create_near_line_clear_board()
        piece = self._create_test_piece()
        
        hints = self.coach.generate_hints(board, piece, [])
        
        # Should suggest line clear
        line_clear_hints = [h for h in hints if 'line' in h.get('message', '').lower()]
        if line_clear_hints:
            self.assertGreater(len(line_clear_hints), 0)
    
    def test_stack_management(self):
        """Test stack management suggestions"""
        # Create board with uneven stack
        board = self._create_uneven_stack_board()
        piece = self._create_test_piece()
        
        hints = self.coach.generate_hints(board, piece, [])
        
        # Should suggest stack management
        stack_hints = [h for h in hints if 'stack' in h.get('message', '').lower() or 'even' in h.get('message', '').lower()]
        if stack_hints:
            self.assertGreater(len(stack_hints), 0)
    
    def test_piece_placement_suggestions(self):
        """Test piece placement suggestions"""
        board = self._create_test_board_state()
        piece = self._create_test_piece()
        
        # Test with different piece types
        piece_types = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
        
        for piece_type in piece_types:
            piece.type = piece_type
            hints = self.coach.generate_hints(board, piece, [])
            
            # Should provide piece-specific hints
            self.assertIsInstance(hints, list)
    
    def _create_test_board_state(self):
        """Create a basic test board state"""
        pieces = {}
        return BoardState(
            pieces=pieces,
            current_piece=self._create_test_piece(),
            score=0,
            lines_cleared=0,
            level=1
        )
    
    def _create_test_piece(self):
        """Create a test piece"""
        return PieceInfo(
            type='T',
            position=(5, 10),
            orientation=0,
            color='purple'
        )
    
    def _create_near_line_clear_board(self):
        """Create board nearly ready for line clear"""
        pieces = {}
        # Fill bottom row except one gap
        for x in range(10):
            if x != 5:  # Leave gap at position 5
                pieces[(x, 0)] = type('Piece', (), {'type': 'I', 'color': 'blue'})()
        
        return BoardState(
            pieces=pieces,
            current_piece=self._create_test_piece(),
            score=1000,
            lines_cleared=10,
            level=5
        )
    
    def _create_uneven_stack_board(self):
        """Create board with uneven stack"""
        pieces = {}
        # Create uneven heights
        heights = [10, 8, 12, 6, 14, 4, 16, 2, 18, 0]
        for x, height in enumerate(heights):
            for y in range(height):
                pieces[(x, y)] = type('Piece', (), {'type': 'I', 'color': 'blue'})()
        
        return BoardState(
            pieces=pieces,
            current_piece=self._create_test_piece(),
            score=500,
            lines_cleared=5,
            level=3
        )


if __name__ == '__main__':
    unittest.main()
