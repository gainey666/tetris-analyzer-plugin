"""
Coaching Module for Tetris Analyzer Plugin

This module provides coaching hints, strategy suggestions, and real-time
feedback to help players improve their Tetris gameplay.
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import time
from utils.frame_types import BoardState, PieceInfo
from utils.performance import measure_latency, perf_monitor


class HintType(Enum):
    """Types of coaching hints"""
    MOVE_SUGGESTION = "move_suggestion"
    DANGER_WARNING = "danger_warning"
    STRATEGY_TIP = "strategy_tip"
    EFFICIENCY_NOTE = "efficiency_note"
    MISTAKE_CORRECTION = "mistake_correction"


class UrgencyLevel(Enum):
    """Urgency levels for hints"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class CoachingHint:
    """Single coaching hint"""
    hint_type: HintType
    urgency: UrgencyLevel
    message: str
    confidence: float
    timestamp: int
    expires_at: int
    data: Optional[Dict[str, Any]] = None


@dataclass
class StrategyAssessment:
    """Assessment of current playing strategy"""
    overall_rating: float  # 0-100
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    metrics: Dict[str, float]


class CoachingModule:
    """Coaching system for Tetris gameplay improvement"""
    
    def __init__(self):
        """Initialize coaching module"""
        # Coaching parameters
        self.max_hints = 5
        self.hint_lifetime = 10000  # 10 seconds in milliseconds
        self.confidence_threshold = 0.6
        self.enable_move_suggestions = True
        self.enable_danger_warnings = True
        self.enable_strategy_tips = True
        
        # Strategy tracking
        self.moves_made = 0
        self.good_moves = 0
        self.danger_situations_avoided = 0
        self.efficiency_score = 0.0
        
        # Active hints
        self.active_hints: List[CoachingHint] = []
        
        # Performance tracking
        self.hints_generated = 0
        self.last_hint_time = 0
    
    @measure_latency("coaching")
    def generate_hints(self, board_state: BoardState, current_piece: Optional[PieceInfo] = None,
                      predicted_moves: Optional[List] = None) -> List[CoachingHint]:
        """
        Generate coaching hints based on current game state
        
        Args:
            board_state: Current board state
            current_piece: Currently falling piece
            predicted_moves: List of predicted move suggestions
            
        Returns:
            List of coaching hints
        """
        try:
            self.hints_generated += 1
            self.last_hint_time = int(time.time() * 1000)
            
            # Clean expired hints
            self._clean_expired_hints()
            
            new_hints = []
            
            # Generate danger warnings
            if self.enable_danger_warnings:
                danger_hints = self._generate_danger_warnings(board_state, current_piece)
                new_hints.extend(danger_hints)
            
            # Generate move suggestions
            if self.enable_move_suggestions and predicted_moves:
                move_hints = self._generate_move_suggestions(predicted_moves)
                new_hints.extend(move_hints)
            
            # Generate strategy tips
            if self.enable_strategy_tips:
                strategy_hints = self._generate_strategy_tips(board_state)
                new_hints.extend(strategy_hints)
            
            # Add new hints if confidence is high enough
            for hint in new_hints:
                if hint.confidence >= self.confidence_threshold:
                    self.active_hints.append(hint)
            
            # Limit number of active hints
            self._limit_hints()
            
            return self.active_hints.copy()
            
        except Exception as e:
            print(f"Coaching hint generation error: {e}")
            return []
    
    def _generate_danger_warnings(self, board_state: BoardState, current_piece: Optional[PieceInfo]) -> List[CoachingHint]:
        """Generate danger warning hints"""
        hints = []
        
        # Check for stack danger
        stack_danger = self._assess_stack_danger(board_state)
        if stack_danger > 0.7:
            hints.append(CoachingHint(
                hint_type=HintType.DANGER_WARNING,
                urgency=UrgencyLevel.HIGH if stack_danger > 0.9 else UrgencyLevel.MEDIUM,
                message="Stack getting high! Consider clearing lines soon.",
                confidence=stack_danger,
                timestamp=int(time.time() * 1000),
                expires_at=int(time.time() * 1000) + self.hint_lifetime,
                data={'danger_type': 'stack_height', 'severity': stack_danger}
            ))
        
        # Check for hole creation risk
        hole_risk = self._assess_hole_risk(board_state, current_piece)
        if hole_risk > 0.6:
            hints.append(CoachingHint(
                hint_type=HintType.DANGER_WARNING,
                urgency=UrgencyLevel.MEDIUM,
                message="Be careful not to create holes!",
                confidence=hole_risk,
                timestamp=int(time.time() * 1000),
                expires_at=int(time.time() * 1000) + self.hint_lifetime,
                data={'danger_type': 'hole_creation', 'risk': hole_risk}
            ))
        
        # Check for well formation
        well_risk = self._assess_well_risk(board_state)
        if well_risk > 0.8:
            hints.append(CoachingHint(
                hint_type=HintType.DANGER_WARNING,
                urgency=UrgencyLevel.MEDIUM,
                message="Deep well forming! Avoid I-piece traps.",
                confidence=well_risk,
                timestamp=int(time.time() * 1000),
                expires_at=int(time.time() * 1000) + self.hint_lifetime,
                data={'danger_type': 'well_formation', 'depth': well_risk}
            ))
        
        return hints
    
    def _generate_move_suggestions(self, predicted_moves: List) -> List[CoachingHint]:
        """Generate move suggestion hints"""
        hints = []
        
        if not predicted_moves:
            return hints
        
        # Get best move
        best_move = predicted_moves[0] if predicted_moves else None
        
        if best_move and best_move.confidence > 0.7:
            hints.append(CoachingHint(
                hint_type=HintType.MOVE_SUGGESTION,
                urgency=UrgencyLevel.LOW,
                message=f"Consider: {best_move.reasoning}",
                confidence=best_move.confidence,
                timestamp=int(time.time() * 1000),
                expires_at=int(time.time() * 1000) + self.hint_lifetime,
                data={
                    'suggested_move': {
                        'position': best_move.position,
                        'orientation': best_move.orientation,
                        'score': best_move.score
                    }
                }
            ))
        
        return hints
    
    def _generate_strategy_tips(self, board_state: BoardState) -> List[CoachingHint]:
        """Generate strategy improvement tips"""
        hints = []
        
        # Analyze current strategy
        assessment = self.assess_strategy(board_state)
        
        # Provide tips based on weaknesses
        for weakness in assessment.weaknesses[:2]:  # Limit to top 2
            hints.append(CoachingHint(
                hint_type=HintType.STRATEGY_TIP,
                urgency=UrgencyLevel.LOW,
                message=f"Strategy tip: {weakness}",
                confidence=0.7,
                timestamp=int(time.time() * 1000),
                expires_at=int(time.time() * 1000) + self.hint_lifetime,
                data={'strategy_area': 'general', 'tip_type': 'weakness'}
            ))
        
        return hints
    
    def _assess_stack_danger(self, board_state: BoardState) -> float:
        """Assess stack height danger (0-1)"""
        occupied_positions = board_state.get_occupied_positions()
        
        if not occupied_positions:
            return 0.0
        
        # Find highest point
        highest_y = min(y for _, y in occupied_positions)
        stack_height = 20 - highest_y
        
        # Normalize to 0-1 (danger increases with height)
        danger = min(1.0, stack_height / 15.0)
        return danger
    
    def _assess_hole_risk(self, board_state: BoardState, current_piece: Optional[PieceInfo]) -> float:
        """Assess risk of creating holes"""
        if not current_piece:
            return 0.0
        
        # Simple heuristic - check if current piece position could create holes
        occupied_positions = board_state.get_occupied_positions()
        
        # Count existing holes
        holes = 0
        for x in range(10):
            column_occupied = [y for (cx, y) in occupied_positions if cx == x]
            if column_occupied:
                highest_in_column = min(column_occupied)
                for y in range(highest_in_column + 1, 20):
                    if (x, y) not in occupied_positions:
                        holes += 1
        
        # Risk increases with existing holes
        risk = min(1.0, holes / 10.0)
        return risk
    
    def _assess_well_risk(self, board_state: BoardState) -> float:
        """Assess well formation risk"""
        occupied_positions = board_state.get_occupied_positions()
        
        if not occupied_positions:
            return 0.0
        
        # Calculate column heights
        column_heights = []
        for x in range(10):
            column_occupied = [y for (cx, y) in occupied_positions if cx == x]
            if column_occupied:
                height = 20 - min(column_occupied)
            else:
                height = 0
            column_heights.append(height)
        
        # Find wells (columns significantly lower than neighbors)
        max_well_depth = 0
        for i in range(len(column_heights)):
            left_height = column_heights[i - 1] if i > 0 else 20
            right_height = column_heights[i + 1] if i < 9 else 20
            current_height = column_heights[i]
            
            well_depth = min(left_height, right_height) - current_height
            max_well_depth = max(max_well_depth, well_depth)
        
        # Risk increases with well depth
        risk = min(1.0, max_well_depth / 5.0)
        return risk
    
    def assess_strategy(self, board_state: BoardState) -> StrategyAssessment:
        """Assess overall playing strategy"""
        occupied_positions = board_state.get_occupied_positions()
        
        # Calculate metrics
        holes = self._count_holes(board_state)
        stack_height = self._calculate_stack_height(board_state)
        surface_roughness = self._calculate_surface_roughness(board_state)
        
        # Calculate overall rating
        rating = 100.0
        rating -= holes * 5  # Penalty for holes
        rating -= stack_height * 2  # Penalty for high stack
        rating -= surface_roughness * 3  # Penalty for rough surface
        rating = max(0.0, min(100.0, rating))
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if holes < 2:
            strengths.append("Good hole management")
        else:
            weaknesses.append(f"Too many holes ({holes})")
        
        if stack_height < 10:
            strengths.append("Good stack control")
        else:
            weaknesses.append("Stack getting too high")
        
        if surface_roughness < 3:
            strengths.append("Smooth surface")
        else:
            weaknesses.append("Rough surface creating problems")
        
        # Generate recommendations
        recommendations = []
        if holes > 2:
            recommendations.append("Focus on avoiding hole creation")
        if stack_height > 10:
            recommendations.append("Prioritize line clears")
        if surface_roughness > 3:
            recommendations.append("Aim for more even placement")
        
        return StrategyAssessment(
            overall_rating=rating,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            metrics={
                'holes': holes,
                'stack_height': stack_height,
                'surface_roughness': surface_roughness
            }
        )
    
    def _count_holes(self, board_state: BoardState) -> int:
        """Count holes in the board"""
        occupied_positions = board_state.get_occupied_positions()
        holes = 0
        
        for x in range(10):
            column_occupied = [y for (cx, y) in occupied_positions if cx == x]
            if column_occupied:
                highest_in_column = min(column_occupied)
                for y in range(highest_in_column + 1, 20):
                    if (x, y) not in occupied_positions:
                        holes += 1
        
        return holes
    
    def _calculate_stack_height(self, board_state: BoardState) -> int:
        """Calculate current stack height"""
        occupied_positions = board_state.get_occupied_positions()
        
        if not occupied_positions:
            return 0
        
        highest_y = min(y for _, y in occupied_positions)
        return 20 - highest_y
    
    def _calculate_surface_roughness(self, board_state: BoardState) -> float:
        """Calculate surface roughness"""
        occupied_positions = board_state.get_occupied_positions()
        
        # Calculate column heights
        column_heights = []
        for x in range(10):
            column_occupied = [y for (cx, y) in occupied_positions if cx == x]
            if column_occupied:
                height = 20 - min(column_occupied)
            else:
                height = 0
            column_heights.append(height)
        
        # Calculate roughness
        roughness = 0.0
        for i in range(len(column_heights) - 1):
            roughness += abs(column_heights[i] - column_heights[i + 1])
        
        return roughness
    
    def _clean_expired_hints(self):
        """Remove expired hints"""
        current_time = int(time.time() * 1000)
        self.active_hints = [hint for hint in self.active_hints if hint.expires_at > current_time]
    
    def _limit_hints(self):
        """Limit number of active hints"""
        if len(self.active_hints) > self.max_hints:
            # Keep hints by urgency and recency
            self.active_hints.sort(key=lambda h: (h.urgency.value, h.timestamp), reverse=True)
            self.active_hints = self.active_hints[:self.max_hints]
    
    def get_active_hints(self) -> List[CoachingHint]:
        """Get current active hints"""
        self._clean_expired_hints()
        return self.active_hints.copy()
    
    def clear_hints(self):
        """Clear all active hints"""
        self.active_hints.clear()
    
    def get_coaching_statistics(self) -> Dict[str, Any]:
        """Get coaching statistics"""
        stats = {
            'hints_generated': self.hints_generated,
            'last_hint_time': self.last_hint_time,
            'active_hints_count': len(self.active_hints),
            'moves_made': self.moves_made,
            'good_moves': self.good_moves,
            'danger_situations_avoided': self.danger_situations_avoided,
            'efficiency_score': self.efficiency_score,
            'performance_stats': {
                'coaching': perf_monitor.get_stats('coaching_latency_ms')
            },
            'settings': {
                'max_hints': self.max_hints,
                'hint_lifetime': self.hint_lifetime,
                'confidence_threshold': self.confidence_threshold,
                'enable_move_suggestions': self.enable_move_suggestions,
                'enable_danger_warnings': self.enable_danger_warnings,
                'enable_strategy_tips': self.enable_strategy_tips
            }
        }
        
        return stats
    
    def update_settings(self, max_hints: int = None, hint_lifetime: int = None,
                       confidence_threshold: float = None, enable_move_suggestions: bool = None,
                       enable_danger_warnings: bool = None, enable_strategy_tips: bool = None):
        """Update coaching settings"""
        if max_hints is not None:
            self.max_hints = max(1, max_hints)
        if hint_lifetime is not None:
            self.hint_lifetime = max(1000, hint_lifetime)
        if confidence_threshold is not None:
            self.confidence_threshold = max(0.0, min(1.0, confidence_threshold))
        if enable_move_suggestions is not None:
            self.enable_move_suggestions = enable_move_suggestions
        if enable_danger_warnings is not None:
            self.enable_danger_warnings = enable_danger_warnings
        if enable_strategy_tips is not None:
            self.enable_strategy_tips = enable_strategy_tips
