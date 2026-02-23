"""
Board Detection Module for Tetris Analyzer Plugin

This module provides automatic board detection using OpenCV with manual fallback,
implementing the core functionality needed to locate and calibrate Tetris game boards.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List, Dict, Any
import time
from utils.frame_types import FrameData, BoardCalibration
from utils.performance import measure_latency, perf_monitor


class BoardDetector:
    """Automatic Tetris board detection with manual calibration fallback"""
    
    def __init__(self):
        """Initialize board detector"""
        self.current_calibration: Optional[BoardCalibration] = None
        self.detection_confidence_threshold = 0.7
        self.min_board_size = (200, 400)  # Minimum width, height
        self.max_board_size = (400, 800)  # Maximum width, height
        self.expected_aspect_ratio = 0.5  # Width/Height ratio for Tetris boards
        
        # OpenCV parameters for detection
        self.canny_low = 50
        self.canny_high = 150
        self.hough_threshold = 100
        self.min_line_length = 50
        self.max_line_gap = 10
        
        # Template matching parameters
        self.template_match_threshold = 0.8
        
    @measure_latency("board_detection")
    def detect_board(self, frame: FrameData) -> Optional[BoardCalibration]:
        """
        Detect Tetris board in frame
        
        Args:
            frame: Input frame data
            
        Returns:
            BoardCalibration if detected, None otherwise
        """
        try:
            # Convert frame to grayscale for processing
            gray = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
            
            # Try multiple detection methods
            calibration = None
            
            # Method 1: Edge-based detection
            calibration = self._detect_by_edges(gray, frame)
            
            if calibration is None:
                # Method 2: Contour-based detection
                calibration = self._detect_by_contours(gray, frame)
            
            if calibration is None:
                # Method 3: Template-based detection
                calibration = self._detect_by_template_matching(gray, frame)
            
            if calibration and calibration.calibration_confidence >= self.detection_confidence_threshold:
                self.current_calibration = calibration
                return calibration
            
            return None
            
        except Exception as e:
            print(f"Board detection error: {e}")
            return None
    
    def _detect_by_edges(self, gray: np.ndarray, frame: FrameData) -> Optional[BoardCalibration]:
        """Detect board using edge detection and line finding"""
        try:
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, self.canny_low, self.canny_high)
            
            # Find lines using Hough Transform
            lines = cv2.HoughLinesP(
                edges, 
                1, 
                np.pi / 180, 
                self.hough_threshold,
                minLineLength=self.min_line_length,
                maxLineGap=self.max_line_gap
            )
            
            if lines is None or len(lines) < 4:
                return None
            
            # Analyze lines to find rectangular board
            return self._analyze_lines_for_board(lines, frame)
            
        except Exception as e:
            print(f"Edge detection error: {e}")
            return None
    
    def _detect_by_contours(self, gray: np.ndarray, frame: FrameData) -> Optional[BoardCalibration]:
        """Detect board using contour analysis"""
        try:
            # Apply threshold to get binary image
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by size and aspect ratio
            valid_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 10000:  # Minimum area threshold
                    continue
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check aspect ratio
                aspect_ratio = w / h
                if not (0.3 <= aspect_ratio <= 0.7):  # Tetris board aspect ratio range
                    continue
                
                # Check size constraints
                if not (self.min_board_size[0] <= w <= self.max_board_size[0] and
                       self.min_board_size[1] <= h <= self.max_board_size[1]):
                    continue
                
                valid_contours.append((contour, (x, y, w, h), aspect_ratio))
            
            if not valid_contours:
                return None
            
            # Select best contour (closest to expected aspect ratio)
            best_contour = min(valid_contours, key=lambda x: abs(x[2] - self.expected_aspect_ratio))
            _, (x, y, w, h), _ = best_contour
            
            # Create calibration
            return self._create_calibration_from_bounds(x, y, w, h, frame, confidence=0.8)
            
        except Exception as e:
            print(f"Contour detection error: {e}")
            return None
    
    def _detect_by_template_matching(self, gray: np.ndarray, frame: FrameData) -> Optional[BoardCalibration]:
        """Detect board using template matching (fallback method)"""
        try:
            # Create a simple Tetris board template
            template = self._create_board_template()
            
            if template is None:
                return None
            
            # Template matching
            result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            
            # Find best match
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val < self.template_match_threshold:
                return None
            
            # Calculate board bounds from template match
            template_h, template_w = template.shape
            x, y = max_loc
            w, h = template_w, template_h
            
            return self._create_calibration_from_bounds(x, y, w, h, frame, confidence=max_val)
            
        except Exception as e:
            print(f"Template matching error: {e}")
            return None
    
    def _analyze_lines_for_board(self, lines: np.ndarray, frame: FrameData) -> Optional[BoardCalibration]:
        """Analyze detected lines to find rectangular board boundaries"""
        try:
            # Separate horizontal and vertical lines
            horizontal_lines = []
            vertical_lines = []
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # Calculate line angle
                angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                
                # Classify as horizontal or vertical
                if abs(angle) < 30 or abs(angle) > 150:
                    horizontal_lines.append(line[0])
                elif 60 < abs(angle) < 120:
                    vertical_lines.append(line[0])
            
            # Need at least 2 horizontal and 2 vertical lines
            if len(horizontal_lines) < 2 or len(vertical_lines) < 2:
                return None
            
            # Find bounding box from lines
            all_x = []
            all_y = []
            
            for line in horizontal_lines + vertical_lines:
                all_x.extend([line[0], line[2]])
                all_y.extend([line[1], line[3]])
            
            if not all_x or not all_y:
                return None
            
            x_min, x_max = min(all_x), max(all_x)
            y_min, y_max = min(all_y), max(all_y)
            
            # Calculate board dimensions
            w = x_max - x_min
            h = y_max - y_min
            
            # Validate dimensions
            if not (self.min_board_size[0] <= w <= self.max_board_size[0] and
                   self.min_board_size[1] <= h <= self.max_board_size[1]):
                return None
            
            # Check aspect ratio
            aspect_ratio = w / h
            if not (0.3 <= aspect_ratio <= 0.7):
                return None
            
            return self._create_calibration_from_bounds(x_min, y_min, w, h, frame, confidence=0.75)
            
        except Exception as e:
            print(f"Line analysis error: {e}")
            return None
    
    def _create_calibration_from_bounds(self, x: int, y: int, w: int, h: int, 
                                       frame: FrameData, confidence: float) -> BoardCalibration:
        """Create BoardCalibration from detected bounds"""
        # Calculate cell size (assuming 10x20 grid)
        cell_size = min(w // 10, h // 20)
        
        # Adjust bounds to be exact multiples of cell size
        adjusted_w = cell_size * 10
        adjusted_h = cell_size * 20
        adjusted_x = x + (w - adjusted_w) // 2
        adjusted_y = y + (h - adjusted_h) // 2
        
        return BoardCalibration(
            board_bounds=(adjusted_x, adjusted_y, adjusted_w, adjusted_h),
            cell_size=cell_size,
            grid_dimensions=(10, 20),
            calibration_timestamp=frame.timestamp,
            calibration_confidence=confidence
        )
    
    def _create_board_template(self) -> Optional[np.ndarray]:
        """Create a simple Tetris board template"""
        try:
            # Create a 10x20 grid template
            cell_size = 20
            template_w = cell_size * 10
            template_h = cell_size * 20
            
            template = np.zeros((template_h, template_w), dtype=np.uint8)
            
            # Draw grid lines
            for i in range(11):  # Vertical lines
                x = i * cell_size
                cv2.line(template, (x, 0), (x, template_h), 255, 1)
            
            for i in range(21):  # Horizontal lines
                y = i * cell_size
                cv2.line(template, (0, y), (template_w, y), 255, 1)
            
            return template
            
        except Exception as e:
            print(f"Template creation error: {e}")
            return None
    
    def set_manual_calibration(self, board_bounds: Tuple[int, int, int, int], 
                              cell_size: int, confidence: float = 1.0):
        """
        Set manual calibration
        
        Args:
            board_bounds: (x, y, width, height) of board
            cell_size: Size of each cell in pixels
            confidence: Confidence level (0.0-1.0)
        """
        self.current_calibration = BoardCalibration(
            board_bounds=board_bounds,
            cell_size=cell_size,
            grid_dimensions=(10, 20),
            calibration_timestamp=int(time.time() * 1000),
            calibration_confidence=confidence
        )
    
    def get_current_calibration(self) -> Optional[BoardCalibration]:
        """Get current calibration"""
        return self.current_calibration
    
    def extract_board_region(self, frame: FrameData) -> Optional[np.ndarray]:
        """Extract board region from frame using current calibration"""
        if not self.current_calibration:
            return None
        
        try:
            x, y, w, h = self.current_calibration.board_bounds
            
            # Validate bounds
            if x < 0 or y < 0 or x + w > frame.width or y + h > frame.height:
                return None
            
            # Extract region
            board_region = frame.data[y:y+h, x:x+w]
            
            return board_region
            
        except Exception as e:
            print(f"Board region extraction error: {e}")
            return None
    
    def validate_calibration(self, frame: FrameData) -> bool:
        """Validate current calibration against frame"""
        if not self.current_calibration:
            return False
        
        try:
            # Extract board region
            board_region = self.extract_board_region(frame)
            if board_region is None:
                return False
            
            # Basic validation checks
            if board_region.size == 0:
                return False
            
            # Check if region looks like a Tetris board
            # (This is a simple check - could be enhanced with more sophisticated analysis)
            gray = cv2.cvtColor(board_region, cv2.COLOR_BGR2GRAY)
            
            # Check for grid-like structure
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Tetris boards typically have moderate edge density
            if not (0.05 <= edge_density <= 0.3):
                return False
            
            return True
            
        except Exception as e:
            print(f"Calibration validation error: {e}")
            return False
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get detection statistics"""
        stats = {
            'current_calibration': self.current_calibration is not None,
            'confidence_threshold': self.detection_confidence_threshold,
            'detection_methods': ['edges', 'contours', 'template_matching'],
            'performance_stats': {
                'edge_detection': perf_monitor.get_stats('board_detection_latency_ms'),
                'contour_detection': perf_monitor.get_stats('board_detection_latency_ms'),
                'template_matching': perf_monitor.get_stats('board_detection_latency_ms')
            }
        }
        
        if self.current_calibration:
            stats['calibration_info'] = {
                'board_bounds': self.current_calibration.board_bounds,
                'cell_size': self.current_calibration.cell_size,
                'confidence': self.current_calibration.calibration_confidence,
                'timestamp': self.current_calibration.calibration_timestamp
            }
        
        return stats
