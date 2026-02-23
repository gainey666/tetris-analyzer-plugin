"""
Frame Types and Data Contracts for Tetris Analyzer Plugin

This module defines standardized data structures for the Tetris analysis pipeline,
ensuring consistent data flow between capture, detection, and prediction components.
"""

from dataclasses import dataclass
from typing import Tuple, Optional, Dict, Any
import numpy as np


@dataclass
class FrameData:
    """Standardized frame format for the analysis pipeline"""
    data: np.ndarray          # BGR/RGBA uint8 image data
    timestamp: int            # Milliseconds since epoch
    sequence: int             # Frame sequence number
    width: int                # Frame width in pixels
    height: int               # Frame height in pixels
    format: str               # "BGR" or "RGBA"
    source: str               # Capture source identifier
    
    def __post_init__(self):
        """Validate frame data after initialization"""
        if self.data.shape[0] != self.height or self.data.shape[1] != self.width:
            raise ValueError(f"Frame dimensions mismatch: expected {self.width}x{self.height}, got {self.data.shape[1]}x{self.data.shape[0]}")
        
        if self.format not in ["BGR", "RGBA"]:
            raise ValueError(f"Unsupported format: {self.format}. Must be 'BGR' or 'RGBA'")
        
        if len(self.data.shape) != 3 or self.data.shape[2] not in [3, 4]:
            raise ValueError(f"Invalid data shape: {self.data.shape}. Expected (H, W, 3) for BGR or (H, W, 4) for RGBA")


@dataclass
class BoardCalibration:
    """Board calibration data for mapping screen coordinates to game grid"""
    board_bounds: Tuple[int, int, int, int]  # (x, y, width, height)
    cell_size: int                            # Size of each cell in pixels
    grid_dimensions: Tuple[int, int]         # (cols, rows) - typically (10, 20)
    calibration_timestamp: int                # When calibration was performed
    calibration_confidence: float              # 0.0 to 1.0 confidence score
    
    def __post_init__(self):
        """Validate calibration data"""
        if len(self.board_bounds) != 4:
            raise ValueError("board_bounds must be (x, y, width, height)")
        
        if self.cell_size <= 0:
            raise ValueError("cell_size must be positive")
        
        if len(self.grid_dimensions) != 2:
            raise ValueError("grid_dimensions must be (cols, rows)")
        
        if not 0.0 <= self.calibration_confidence <= 1.0:
            raise ValueError("calibration_confidence must be between 0.0 and 1.0")
    
    def screen_to_grid(self, screen_x: int, screen_y: int) -> Optional[Tuple[int, int]]:
        """Convert screen coordinates to grid coordinates"""
        bx, by, bw, bh = self.board_bounds
        
        # Check if point is within board bounds
        if not (bx <= screen_x < bx + bw and by <= screen_y < by + bh):
            return None
        
        # Convert to grid coordinates
        grid_x = (screen_x - bx) // self.cell_size
        grid_y = (screen_y - by) // self.cell_size
        
        # Validate grid coordinates
        if 0 <= grid_x < self.grid_dimensions[0] and 0 <= grid_y < self.grid_dimensions[1]:
            return (grid_x, grid_y)
        
        return None
    
    def grid_to_screen(self, grid_x: int, grid_y: int) -> Tuple[int, int]:
        """Convert grid coordinates to screen coordinates"""
        bx, by, _, _ = self.board_bounds
        
        screen_x = bx + grid_x * self.cell_size + self.cell_size // 2
        screen_y = by + grid_y * self.cell_size + self.cell_size // 2
        
        return (screen_x, screen_y)


@dataclass
class PieceInfo:
    """Information about a Tetris piece"""
    piece_type: str                 # "I", "O", "T", "S", "Z", "J", "L", or "empty"
    position: Tuple[int, int]       # (x, y) grid coordinates
    orientation: int                # 0-3 rotation states
    confidence: float               # Recognition confidence 0.0-1.0
    
    def __post_init__(self):
        """Validate piece info"""
        valid_pieces = ["I", "O", "T", "S", "Z", "J", "L", "empty"]
        if self.piece_type not in valid_pieces:
            raise ValueError(f"Invalid piece_type: {self.piece_type}. Must be one of {valid_pieces}")
        
        if len(self.position) != 2:
            raise ValueError("position must be (x, y) tuple")
        
        if not 0 <= self.orientation <= 3:
            raise ValueError("orientation must be 0-3")
        
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")


@dataclass
class BoardState:
    """Complete board state representation"""
    pieces: Dict[Tuple[int, int], PieceInfo]  # Grid position -> piece info
    current_piece: Optional[PieceInfo]        # Currently falling piece
    next_pieces: list[str]                    # Queue of upcoming pieces
    hold_piece: Optional[str]                 # Held piece type
    score: int                                # Current score
    level: int                                # Current level
    lines_cleared: int                        # Total lines cleared
    timestamp: int                            # When this state was captured
    
    def __post_init__(self):
        """Validate board state"""
        if not all(0 <= pos[0] < 10 and 0 <= pos[1] < 20 for pos in self.pieces.keys()):
            raise ValueError("All piece positions must be within 10x20 grid")
        
        if self.next_pieces and len(self.next_pieces) > 5:
            raise ValueError("next_pieces should not exceed 5 pieces")
        
        if self.hold_piece and self.hold_piece not in ["I", "O", "T", "S", "Z", "J", "L"]:
            raise ValueError(f"Invalid hold_piece: {self.hold_piece}")
    
    def get_piece_at(self, x: int, y: int) -> Optional[PieceInfo]:
        """Get piece at specific grid position"""
        return self.pieces.get((x, y))
    
    def is_position_occupied(self, x: int, y: int) -> bool:
        """Check if position is occupied"""
        return (x, y) in self.pieces
    
    def get_occupied_positions(self) -> set[Tuple[int, int]]:
        """Get all occupied positions"""
        return set(self.pieces.keys())


@dataclass
class CoachingHint:
    """Coaching hint for player guidance"""
    hint_type: str                   # "move_suggestion", "danger_warning", "strategy_tip"
    message: str                     # Human-readable hint message
    urgency: float                   # 0.0-1.0 urgency level
    target_position: Optional[Tuple[int, int]]  # Suggested piece position
    confidence: float                # Hint confidence 0.0-1.0
    timestamp: int                   # When hint was generated
    
    def __post_init__(self):
        """Validate coaching hint"""
        valid_types = ["move_suggestion", "danger_warning", "strategy_tip"]
        if self.hint_type not in valid_types:
            raise ValueError(f"Invalid hint_type: {self.hint_type}. Must be one of {valid_types}")
        
        if not 0.0 <= self.urgency <= 1.0:
            raise ValueError("urgency must be between 0.0 and 1.0")
        
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring"""
    capture_latency_ms: float
    preprocess_latency_ms: float
    recognition_latency_ms: float
    prediction_latency_ms: float
    end_to_end_latency_ms: float
    fps_current: float
    memory_usage_mb: float
    cpu_usage_percent: float
    timestamp: int
    
    def __post_init__(self):
        """Validate performance metrics"""
        if any(latency < 0 for latency in [
            self.capture_latency_ms, self.preprocess_latency_ms,
            self.recognition_latency_ms, self.prediction_latency_ms,
            self.end_to_end_latency_ms
        ]):
            raise ValueError("All latency values must be non-negative")
        
        if self.fps_current < 0:
            raise ValueError("fps_current must be non-negative")
        
        if self.memory_usage_mb < 0:
            raise ValueError("memory_usage_mb must be non-negative")
        
        if not 0.0 <= self.cpu_usage_percent <= 100.0:
            raise ValueError("cpu_usage_percent must be between 0.0 and 100.0")


# Type aliases for better readability
GridPosition = Tuple[int, int]
ScreenPosition = Tuple[int, int]
BoardGrid = Dict[GridPosition, PieceInfo]
