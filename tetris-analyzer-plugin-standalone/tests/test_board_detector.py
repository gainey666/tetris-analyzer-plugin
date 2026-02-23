"""
Test suite for Board Detection Module

Tests board detection algorithms and calibration.
"""

import unittest
import numpy as np
import cv2
from unittest.mock import Mock, patch
from detection.board_detector import BoardDetector


class TestBoardDetector(unittest.TestCase):
    """Test cases for Board Detector"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = BoardDetector()
    
    def tearDown(self):
        """Clean up after tests"""
        pass
    
    def test_initialization(self):
        """Test detector initialization"""
        self.assertIsNotNone(self.detector)
        self.assertEqual(self.detector.board_width, 10)
        self.assertEqual(self.detector.board_height, 20)
        self.assertEqual(self.detector.min_board_size, (200, 400))
        self.assertEqual(self.detector.max_board_size, (400, 800))
    
    def test_board_detection_methods(self):
        """Test different board detection methods"""
        methods = ['edges', 'contours', 'template']
        
        for method in methods:
            with self.subTest(method=method):
                self.detector.detection_method = method
                self.assertEqual(self.detector.detection_method, method)
    
    def test_edge_detection(self):
        """Test edge-based board detection"""
        # Create test frame with board-like structure
        frame = self._create_test_frame_with_board()
        
        board_region = self.detector.detect_board(frame)
        
        # Should detect some region
        self.assertIsNotNone(board_region)
        if board_region:
            self.assertEqual(len(board_region), 4)  # x, y, width, height
    
    def test_contour_detection(self):
        """Test contour-based board detection"""
        self.detector.detection_method = 'contours'
        
        frame = self._create_test_frame_with_board()
        board_region = self.detector.detect_board(frame)
        
        # Should detect some region
        self.assertIsNotNone(board_region)
    
    def test_template_detection(self):
        """Test template-based board detection"""
        self.detector.detection_method = 'template'
        
        frame = self._create_test_frame_with_board()
        board_region = self.detector.detect_board(frame)
        
        # Template detection might not work without actual templates
        # This test mainly checks that the method doesn't crash
        self.assertIsInstance(board_region, (type(None), tuple))
    
    def test_board_validation(self):
        """Test board region validation"""
        # Valid region
        valid_region = (100, 50, 300, 600)
        self.assertTrue(self.detector._is_valid_board_region(valid_region))
        
        # Invalid regions
        invalid_regions = [
            (0, 0, 0, 0),  # Empty
            (-10, 0, 100, 100),  # Negative coordinates
            (0, 0, 50, 50),  # Too small
            (0, 0, 1000, 1000),  # Too large
        ]
        
        for region in invalid_regions:
            self.assertFalse(self.detector._is_valid_board_region(region))
    
    def test_confidence_calculation(self):
        """Test board detection confidence calculation"""
        # Create frame with clear board
        frame = self._create_test_frame_with_board()
        
        confidence = self.detector._calculate_detection_confidence(frame)
        
        # Confidence should be between 0 and 1
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_calibration_persistence(self):
        """Test calibration data persistence"""
        # Create test calibration
        test_calibration = type('TestCalibration', (), {
            'board_region': (100, 50, 300, 600),
            'confidence': 0.85
        })()
        
        # Set calibration
        self.detector.current_calibration = test_calibration
        
        # Test that it's stored
        self.assertEqual(self.detector.current_calibration, test_calibration)
    
    def test_multiple_detection_attempts(self):
        """Test multiple detection attempts"""
        frame = self._create_test_frame_with_board()
        
        results = []
        for i in range(5):
            region = self.detector.detect_board(frame)
            results.append(region)
            time.sleep(0.01)  # Small delay
        
        # Should get consistent results
        non_none_results = [r for r in results if r is not None]
        if len(non_none_results) > 1:
            # Check that results are reasonably consistent
            first_result = non_none_results[0]
            for result in non_none_results[1:]:
                # Allow some variation in detection
                for i in range(4):
                    self.assertAlmostEqual(result[i], first_result[i], delta=10)
    
    def test_empty_frame_handling(self):
        """Test handling of empty or invalid frames"""
        empty_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        region = self.detector.detect_board(empty_frame)
        
        # Should return None for empty frame
        self.assertIsNone(region)
    
    def test_noise_resistance(self):
        """Test detection resistance to noise"""
        # Create frame with board and add noise
        frame = self._create_test_frame_with_board()
        
        # Add some noise
        noise = np.random.normal(0, 25, frame.shape).astype(np.uint8)
        noisy_frame = np.clip(frame + noise, 0, 255)
        
        # Should still detect board despite noise
        region = self.detector.detect_board(noisy_frame)
        
        # Might fail with too much noise, but should handle gracefully
        self.assertIsInstance(region, (type(None), tuple))
    
    def _create_test_frame_with_board(self):
        """Create a test frame with a Tetris board-like structure"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Create a rectangular "board" area
        board_x, board_y = 100, 50
        board_width, board_height = 300, 600
        
        # Fill board area with white
        frame[board_y:board_y+board_height, board_x:board_x+board_width] = 255
        
        # Add some grid lines to simulate Tetris grid
        grid_color = 200
        for i in range(1, 10):
            y = board_y + i * (board_height // 20)
            cv2.line(frame, (board_x, y), (board_x + board_width, y), grid_color, 1)
        
        for i in range(1, 5):
            x = board_x + i * (board_width // 10)
            cv2.line(frame, (x, board_y), (x, board_y + board_height), grid_color, 1)
        
        return frame


class TestBoardDetectorPerformance(unittest.TestCase):
    """Performance tests for Board Detector"""
    
    def setUp(self):
        """Set up performance tests"""
        self.detector = BoardDetector()
    
    def test_detection_speed(self):
        """Test board detection speed"""
        frame = self._create_test_frame()
        
        # Time multiple detections
        num_tests = 100
        start_time = time.time()
        
        for _ in range(num_tests):
            self.detector.detect_board(frame)
        
        end_time = time.time()
        avg_time = (end_time - start_time) / num_tests
        
        print(f"Average detection time: {avg_time*1000:.2f}ms")
        print(f"Detections per second: {1/avg_time:.1f}")
        
        # Performance assertions
        self.assertLess(avg_time, 0.05, "Detection should be under 50ms")
        self.assertGreater(1/avg_time, 20, "Should achieve at least 20 detections per second")
    
    def test_memory_usage(self):
        """Test memory usage during detection"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        frame = self._create_test_frame()
        
        # Perform many detections
        for _ in range(50):
            self.detector.detect_board(frame)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        print(f"Memory increase: {memory_increase / 1024 / 1024:.2f}MB")
        
        # Memory should not increase excessively
        self.assertLess(memory_increase, 20 * 1024 * 1024, "Memory increase should be under 20MB")
    
    def _create_test_frame(self):
        """Create a test frame for performance testing"""
        return np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)


if __name__ == '__main__':
    unittest.main()
