"""
Piece Recognition Module for Tetris Analyzer Plugin

This module provides piece recognition using template matching and color heuristics,
with fallback options for ambiguous cases and confidence scoring.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List, Dict, Any
from enum import Enum
import time
from utils.frame_types import FrameData, BoardCalibration, PieceInfo
from utils.performance import measure_latency, perf_monitor


class PieceType(Enum):
    """Tetris piece types"""
    I = "I"
    O = "O"
    T = "T"
    S = "S"
    Z = "Z"
    J = "J"
    L = "L"
    EMPTY = "empty"


class PieceRecognizer:
    """Tetris piece recognition using template matching and color heuristics"""
    
    def __init__(self):
        """Initialize piece recognizer"""
        self.piece_templates: Dict[PieceType, np.ndarray] = {}
        self.color_ranges: Dict[PieceType, Dict[str, Tuple[int, int, int]]] = {}
        self.confidence_threshold = 0.7
        self.cell_size = 20  # Default cell size, will be updated from calibration
        
        # Initialize piece templates and colors
        self._initialize_templates()
        self._initialize_color_ranges()
    
    def _initialize_templates(self):
        """Initialize piece templates for template matching"""
        cell_size = 20
        
        # Define piece shapes (1 = filled, 0 = empty)
        piece_shapes = {
            PieceType.I: np.array([
                [1, 1, 1, 1]
            ]),
            PieceType.O: np.array([
                [1, 1],
                [1, 1]
            ]),
            PieceType.T: np.array([
                [0, 1, 0],
                [1, 1, 1]
            ]),
            PieceType.S: np.array([
                [0, 1, 1],
                [1, 1, 0]
            ]),
            PieceType.Z: np.array([
                [1, 1, 0],
                [0, 1, 1]
            ]),
            PieceType.J: np.array([
                [1, 0, 0],
                [1, 1, 1]
            ]),
            PieceType.L: np.array([
                [0, 0, 1],
                [1, 1, 1]
            ])
        }
        
        # Create templates
        for piece_type, shape in piece_shapes.items():
            h, w = shape.shape
            template = np.zeros((h * cell_size, w * cell_size), dtype=np.uint8)
            
            # Draw piece shape
            for i in range(h):
                for j in range(w):
                    if shape[i, j] == 1:
                        y1, y2 = i * cell_size, (i + 1) * cell_size
                        x1, x2 = j * cell_size, (j + 1) * cell_size
                        template[y1:y2, x1:x2] = 255
            
            self.piece_templates[piece_type] = template
    
    def _initialize_color_ranges(self):
        """Initialize color ranges for different piece types"""
        # These are example ranges - should be calibrated for specific game
        self.color_ranges = {
            PieceType.I: {
                'lower': np.array([0, 100, 200]),   # Blue-ish
                'upper': np.array([100, 255, 255])
            },
            PieceType.O: {
                'lower': np.array([0, 200, 200]),   # Yellow-ish
                'upper': np.array([50, 255, 255])
            },
            PieceType.T: {
                'lower': np.array([100, 0, 200]),  # Purple-ish
                'upper': np.array([255, 100, 255])
            },
            PieceType.S: {
                'lower': np.array([0, 200, 0]),    # Green-ish
                'upper': np.array([100, 255, 100])
            },
            PieceType.Z: {
                'lower': np.array([0, 0, 200]),    # Red-ish
                'upper': np.array([100, 100, 255])
            },
            PieceType.J: {
                'lower': np.array([100, 100, 0]), # Blue-ish (different from I)
                'upper': np.array([255, 255, 100])
            },
            PieceType.L: {
                'lower': np.array([0, 100, 100]), # Orange-ish
                'upper': np.array([50, 255, 255])
            }
        }
    
    @measure_latency("piece_recognition")
    def recognize_pieces(self, frame: FrameData, calibration: BoardCalibration) -> Dict[Tuple[int, int], PieceInfo]:
        """
        Recognize pieces on the board
        
        Args:
            frame: Input frame data
            calibration: Board calibration information
            
        Returns:
            Dictionary mapping grid positions to piece information
        """
        pieces = {}
        
        try:
            # Extract board region
            board_region = self._extract_board_region(frame, calibration)
            if board_region is None:
                return pieces
            
            # Update cell size from calibration
            self.cell_size = calibration.cell_size
            
            # Process each cell in the grid
            for row in range(calibration.grid_dimensions[1]):  # 20 rows
                for col in range(calibration.grid_dimensions[0]):  # 10 columns
                    piece_info = self._recognize_piece_at_position(
                        board_region, row, col, calibration
                    )
                    
                    if piece_info and piece_info.piece_type != PieceType.EMPTY:
                        pieces[(col, row)] = piece_info
            
            return pieces
            
        except Exception as e:
            print(f"Piece recognition error: {e}")
            return pieces
    
    def _extract_board_region(self, frame: FrameData, calibration: BoardCalibration) -> Optional[np.ndarray]:
        """Extract board region from frame"""
        try:
            x, y, w, h = calibration.board_bounds
            
            # Validate bounds
            if x < 0 or y < 0 or x + w > frame.width or y + h > frame.height:
                return None
            
            # Extract region
            board_region = frame.data[y:y+h, x:x+w]
            
            return board_region
            
        except Exception as e:
            print(f"Board region extraction error: {e}")
            return None
    
    def _recognize_piece_at_position(self, board_region: np.ndarray, row: int, col: int, 
                                    calibration: BoardCalibration) -> Optional[PieceInfo]:
        """Recognize piece at specific grid position"""
        try:
            # Calculate cell boundaries
            cell_y = row * self.cell_size
            cell_x = col * self.cell_size
            
            # Extract cell
            cell = board_region[cell_y:cell_y+self.cell_size, cell_x:cell_x+self.cell_size]
            
            if cell.size == 0:
                return None
            
            # Check if cell is empty
            if self._is_cell_empty(cell):
                return PieceInfo(
                    piece_type=PieceType.EMPTY,
                    position=(col, row),
                    orientation=0,
                    confidence=0.9
                )
            
            # Try template matching
            template_result = self._recognize_by_template_matching(cell)
            
            # Try color heuristics
            color_result = self._recognize_by_color_heuristics(cell)
            
            # Combine results
            best_result = self._combine_recognition_results(template_result, color_result)
            
            if best_result and best_result['confidence'] >= self.confidence_threshold:
                return PieceInfo(
                    piece_type=best_result['piece_type'],
                    position=(col, row),
                    orientation=best_result.get('orientation', 0),
                    confidence=best_result['confidence']
                )
            
            return None
            
        except Exception as e:
            print(f"Piece recognition at position error: {e}")
            return None
    
    def _is_cell_empty(self, cell: np.ndarray) -> bool:
        """Check if cell is empty"""
        try:
            # Convert to grayscale
            if len(cell.shape) == 3:
                gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
            else:
                gray = cell
            
            # Check if most pixels are dark/empty
            mean_value = np.mean(gray)
            
            # Threshold for empty cell (adjust based on game)
            return mean_value < 30
            
        except Exception:
            return True
    
    def _recognize_by_template_matching(self, cell: np.ndarray) -> Optional[Dict[str, Any]]:
        """Recognize piece using template matching"""
        try:
            best_match = None
            best_confidence = 0.0
            
            # Convert cell to grayscale for template matching
            if len(cell.shape) == 3:
                cell_gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
            else:
                cell_gray = cell
            
            # Match against each piece template
            for piece_type, template in self.piece_templates.items():
                # Resize template to match cell size
                if template.shape != cell_gray.shape:
                    template_resized = cv2.resize(template, cell_gray.shape[::-1])
                else:
                    template_resized = template
                
                # Template matching
                result = cv2.matchTemplate(cell_gray, template_resized, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                
                if max_val > best_confidence:
                    best_confidence = max_val
                    best_match = {
                        'piece_type': piece_type,
                        'confidence': max_val,
                        'method': 'template_matching'
                    }
            
            return best_match
            
        except Exception as e:
            print(f"Template matching error: {e}")
            return None
    
    def _recognize_by_color_heuristics(self, cell: np.ndarray) -> Optional[Dict[str, Any]]:
        """Recognize piece using color heuristics"""
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(cell, cv2.COLOR_BGR2HSV)
            
            best_match = None
            best_confidence = 0.0
            
            # Check each piece type's color range
            for piece_type, color_range in self.color_ranges.items():
                # Create mask for color range
                mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
                
                # Calculate percentage of matching pixels
                matching_pixels = np.sum(mask > 0)
                total_pixels = mask.size
                confidence = matching_pixels / total_pixels
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = {
                        'piece_type': piece_type,
                        'confidence': confidence,
                        'method': 'color_heuristics'
                    }
            
            return best_match
            
        except Exception as e:
            print(f"Color heuristics error: {e}")
            return None
    
    def _combine_recognition_results(self, template_result: Optional[Dict[str, Any]], 
                                    color_result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Combine results from template matching and color heuristics"""
        if not template_result and not color_result:
            return None
        
        if not template_result:
            return color_result
        
        if not color_result:
            return template_result
        
        # If both methods agree on piece type, increase confidence
        if template_result['piece_type'] == color_result['piece_type']:
            return {
                'piece_type': template_result['piece_type'],
                'confidence': min(0.95, (template_result['confidence'] + color_result['confidence']) / 2),
                'method': 'combined'
            }
        
        # If they disagree, choose the one with higher confidence
        if template_result['confidence'] > color_result['confidence']:
            return {
                'piece_type': template_result['piece_type'],
                'confidence': template_result['confidence'] * 0.8,  # Reduce confidence due to disagreement
                'method': 'template_primary'
            }
        else:
            return {
                'piece_type': color_result['piece_type'],
                'confidence': color_result['confidence'] * 0.8,  # Reduce confidence due to disagreement
                'method': 'color_primary'
            }
    
    def recognize_current_piece(self, frame: FrameData, calibration: BoardCalibration) -> Optional[PieceInfo]:
        """
        Recognize the currently falling piece (above the board)
        
        Args:
            frame: Input frame data
            calibration: Board calibration information
            
        Returns:
            PieceInfo for current piece, or None if not found
        """
        try:
            # Look for piece above the board (next piece area)
            # This is a simplified implementation - could be enhanced
            board_x, board_y, board_w, board_h = calibration.board_bounds
            
            # Define search area above the board
            search_y = max(0, board_y - calibration.cell_size * 3)
            search_h = calibration.cell_size * 2
            search_x = board_x + board_w // 2 - calibration.cell_size * 2
            search_w = calibration.cell_size * 4
            
            # Validate search area
            if search_x < 0 or search_y < 0 or search_x + search_w > frame.width or search_y + search_h > frame.height:
                return None
            
            # Extract search region
            search_region = frame.data[search_y:search_y+search_h, search_x:search_x+search_w]
            
            # Try to recognize piece in this region
            # This is simplified - could use more sophisticated detection
            gray = cv2.cvtColor(search_region, cv2.COLOR_BGR2GRAY)
            
            # Look for piece-like shapes
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            best_piece = None
            best_confidence = 0.0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 100 or area > 1000:  # Reasonable size for a piece
                    continue
                
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Extract piece area
                piece_area = search_region[y:y+h, x:x+w]
                
                # Try to recognize this piece
                piece_info = self._recognize_piece_at_position(
                    np.pad(piece_area, ((0, 0), (0, 0)), mode='constant'),
                    0, 0, calibration
                )
                
                if piece_info and piece_info.piece_type != PieceType.EMPTY:
                    if piece_info.confidence > best_confidence:
                        best_confidence = piece_info.confidence
                        best_piece = piece_info
            
            return best_piece
            
        except Exception as e:
            print(f"Current piece recognition error: {e}")
            return None
    
    def get_recognition_statistics(self) -> Dict[str, Any]:
        """Get recognition statistics"""
        stats = {
            'confidence_threshold': self.confidence_threshold,
            'cell_size': self.cell_size,
            'supported_pieces': [piece.value for piece in PieceType if piece != PieceType.EMPTY],
            'recognition_methods': ['template_matching', 'color_heuristics', 'combined'],
            'performance_stats': {
                'template_matching': perf_monitor.get_stats('piece_recognition_latency_ms'),
                'color_heuristics': perf_monitor.get_stats('piece_recognition_latency_ms')
            },
            'template_count': len(self.piece_templates),
            'color_range_count': len(self.color_ranges)
        }
        
        return stats
    
    def set_confidence_threshold(self, threshold: float):
        """Set confidence threshold for piece recognition"""
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
        else:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
    
    def calibrate_colors(self, frame: FrameData, calibration: BoardCalibration, 
                        piece_samples: Dict[str, Tuple[int, int]]):
        """
        Calibrate color ranges based on sample pieces
        
        Args:
            frame: Input frame containing pieces
            calibration: Board calibration
            piece_samples: Dictionary mapping piece types to grid positions
        """
        try:
            # Extract board region
            board_region = self._extract_board_region(frame, calibration)
            if board_region is None:
                return
            
            # Update color ranges based on samples
            for piece_name, (col, row) in piece_samples.items():
                try:
                    piece_type = PieceType(piece_name)
                    
                    # Extract cell
                    cell_y = row * self.cell_size
                    cell_x = col * self.cell_size
                    cell = board_region[cell_y:cell_y+self.cell_size, cell_x:cell_x+self.cell_size]
                    
                    # Calculate average color in HSV
                    hsv = cv2.cvtColor(cell, cv2.COLOR_BGR2HSV)
                    avg_color = np.mean(hsv.reshape(-1, 3), axis=0)
                    
                    # Create color range around average color
                    tolerance = 30
                    lower = np.maximum([0, 0, 0], avg_color - tolerance)
                    upper = np.minimum([255, 255, 255], avg_color + tolerance)
                    
                    self.color_ranges[piece_type] = {
                        'lower': lower.astype(int),
                        'upper': upper.astype(int)
                    }
                    
                except Exception as e:
                    print(f"Error calibrating color for {piece_name}: {e}")
            
        except Exception as e:
            print(f"Color calibration error: {e}")
