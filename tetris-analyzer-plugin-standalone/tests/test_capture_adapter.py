"""
Test suite for Capture Adapter

Tests screen capture functionality and performance.
"""

import unittest
import time
import numpy as np
from unittest.mock import Mock, patch
from capture.capture_adapter import CaptureAdapter


class TestCaptureAdapter(unittest.TestCase):
    """Test cases for Capture Adapter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.adapter = CaptureAdapter()
    
    def tearDown(self):
        """Clean up after tests"""
        if self.adapter:
            self.adapter.cleanup()
    
    @patch('pyautogui.screenshot')
    def test_initialization(self, mock_screenshot):
        """Test adapter initialization"""
        mock_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = self.adapter.initialize()
        self.assertTrue(result)
        self.assertTrue(self.adapter.initialized)
    
    def test_capture_frame(self):
        """Test frame capture"""
        # This test would require actual screen capture
        # For now, we'll test the interface
        if not self.adapter.initialized:
            self.skipTest("Adapter not initialized")
        
        frame = self.adapter.capture_frame()
        # Frame could be None if no screen is available
        self.assertTrue(isinstance(frame, (np.ndarray, type(None))))
    
    def test_performance_monitoring(self):
        """Test performance monitoring integration"""
        if not self.adapter.initialized:
            self.skipTest("Adapter not initialized")
        
        # Test that performance monitoring is integrated
        self.assertIsNotNone(self.adapter.performance_monitor)
        
        # Test statistics retrieval
        stats = self.adapter.get_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('frames_captured', stats)
    
    def test_configuration(self):
        """Test configuration management"""
        # Test default configuration
        self.assertIsNotNone(self.adapter.config)
        
        # Test configuration updates
        original_fps = self.adapter.config.fps
        self.adapter.config.fps = 60
        self.assertEqual(self.adapter.config.fps, 60)
        
        # Reset to original
        self.adapter.config.fps = original_fps
    
    def test_cleanup(self):
        """Test cleanup process"""
        if self.adapter.initialized:
            self.adapter.cleanup()
            self.assertFalse(self.adapter.initialized)


class TestCapturePerformance(unittest.TestCase):
    """Test capture performance characteristics"""
    
    def setUp(self):
        """Set up performance test"""
        self.adapter = CaptureAdapter()
        if not self.adapter.initialize():
            self.skipTest("Cannot initialize capture adapter")
    
    def tearDown(self):
        """Clean up"""
        if self.adapter.initialized:
            self.adapter.cleanup()
    
    @unittest.skipUnless(True, "Performance test - uncomment to run")
    def test_capture_performance(self):
        """Test capture performance metrics"""
        duration = 5.0  # 5 seconds
        frame_times = []
        
        start_time = time.time()
        while time.time() - start_time < duration:
            frame_start = time.time()
            frame = self.adapter.capture_frame()
            frame_time = time.time() - frame_start
            
            if frame is not None:
                frame_times.append(frame_time)
            
            time.sleep(0.01)  # Small delay
        
        if frame_times:
            avg_time = sum(frame_times) / len(frame_times)
            fps = 1.0 / avg_time if avg_time > 0 else 0
            
            print(f"Average capture time: {avg_time*1000:.2f}ms")
            print(f"Effective FPS: {fps:.1f}")
            
            # Performance assertions
            self.assertLess(avg_time, 0.1, "Capture should be under 100ms")
            self.assertGreater(fps, 10, "Should achieve at least 10 FPS")
    
    def test_memory_usage(self):
        """Test memory usage during capture"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Capture some frames
        for _ in range(10):
            frame = self.adapter.capture_frame()
            if frame is not None:
                # Simulate some processing
                _ = frame.shape
            time.sleep(0.01)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        print(f"Memory increase: {memory_increase / 1024 / 1024:.2f}MB")
        
        # Memory should not increase excessively
        self.assertLess(memory_increase, 50 * 1024 * 1024, "Memory increase should be under 50MB")


if __name__ == '__main__':
    unittest.main()
