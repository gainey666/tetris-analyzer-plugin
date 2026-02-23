"""
Configuration Management for Tetris Analyzer Plugin

This module provides settings management, calibration persistence, and
user preference handling for the Tetris analyzer application.
"""

import json
import os
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import time
from utils.frame_types import BoardCalibration


@dataclass
class CaptureSettings:
    """Capture system settings"""
    fps: int = 30
    quality: str = "high"  # low, medium, high
    region: Optional[tuple] = None  # (x, y, width, height)
    monitor: int = 0
    thread_count: int = 2


@dataclass
class DetectionSettings:
    """Board detection settings"""
    method: str = "edges"  # edges, contours, template
    threshold: float = 0.8
    min_board_size: tuple = (80, 160)  # min width, height
    max_board_size: tuple = (400, 800)  # max width, height
    edge_threshold1: int = 50
    edge_threshold2: int = 150


@dataclass
class RecognitionSettings:
    """Piece recognition settings"""
    template_threshold: float = 0.8
    color_tolerance: float = 0.2
    min_confidence: float = 0.6
    use_color_heuristics: bool = True
    use_template_matching: bool = True


@dataclass
class PredictionSettings:
    """Prediction engine settings"""
    max_suggestions: int = 5
    confidence_threshold: float = 0.6
    lookahead_depth: int = 3
    weights: Dict[str, float] = None
    
    def __post_init__(self):
        if self.weights is None:
            self.weights = {
                "score": 1.0,
                "lines": 2.0,
                "height": 1.5,
                "holes": 2.0
            }


@dataclass
class CoachingSettings:
    """Coaching module settings"""
    enabled: bool = True
    max_hints: int = 5
    hint_lifetime: int = 10000  # milliseconds
    confidence_threshold: float = 0.6
    enable_move_suggestions: bool = True
    enable_danger_warnings: bool = True
    enable_strategy_tips: bool = True
    urgency_filter: str = "medium"  # low, medium, high, critical


@dataclass
class DisplaySettings:
    """Display and output settings"""
    verbose: bool = False
    show_predictions: bool = True
    show_coaching: bool = True
    show_statistics: bool = True
    stats_interval: float = 5.0  # seconds
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR


@dataclass
class PerformanceSettings:
    """Performance optimization settings"""
    max_cpu_usage: float = 80.0  # percentage
    max_memory_usage: int = 512  # MB
    enable_threading: bool = True
    enable_profiling: bool = False
    frame_skip_threshold: int = 2


class SettingsManager:
    """Configuration and settings management"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize settings manager"""
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".tetris-analyzer"
        
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuration files
        self.settings_file = self.config_dir / "settings.json"
        self.calibration_file = self.config_dir / "calibration.json"
        self.user_prefs_file = self.config_dir / "user_preferences.json"
        
        # Default settings
        self.capture = CaptureSettings()
        self.detection = DetectionSettings()
        self.recognition = RecognitionSettings()
        self.prediction = PredictionSettings()
        self.coaching = CoachingSettings()
        self.display = DisplaySettings()
        self.performance = PerformanceSettings()
        
        # Calibration data
        self.calibration: Optional[BoardCalibration] = None
        
        # Load existing settings
        self.load_settings()
        self.load_calibration()
    
    def load_settings(self) -> bool:
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                
                # Update settings objects
                if "capture" in data:
                    self._update_dataclass(self.capture, data["capture"])
                if "detection" in data:
                    self._update_dataclass(self.detection, data["detection"])
                if "recognition" in data:
                    self._update_dataclass(self.recognition, data["recognition"])
                if "prediction" in data:
                    self._update_dataclass(self.prediction, data["prediction"])
                if "coaching" in data:
                    self._update_dataclass(self.coaching, data["coaching"])
                if "display" in data:
                    self._update_dataclass(self.display, data["display"])
                if "performance" in data:
                    self._update_dataclass(self.performance, data["performance"])
                
                return True
            else:
                # Create default settings file
                self.save_settings()
                return True
                
        except Exception as e:
            print(f"Failed to load settings: {e}")
            return False
    
    def save_settings(self) -> bool:
        """Save current settings to file"""
        try:
            data = {
                "capture": asdict(self.capture),
                "detection": asdict(self.detection),
                "recognition": asdict(self.recognition),
                "prediction": asdict(self.prediction),
                "coaching": asdict(self.coaching),
                "display": asdict(self.display),
                "performance": asdict(self.performance),
                "version": "1.0",
                "last_updated": int(time.time() * 1000)
            }
            
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Failed to save settings: {e}")
            return False
    
    def load_calibration(self) -> bool:
        """Load calibration data"""
        try:
            if self.calibration_file.exists():
                with open(self.calibration_file, 'r') as f:
                    data = json.load(f)
                
                self.calibration = BoardCalibration(
                    board_region=tuple(data["board_region"]),
                    cell_size=data.get("cell_size"),
                    confidence=data.get("confidence", 0.0)
                )
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Failed to load calibration: {e}")
            return False
    
    def save_calibration(self, calibration: BoardCalibration) -> bool:
        """Save calibration data"""
        try:
            self.calibration = calibration
            
            data = {
                "board_region": calibration.board_region,
                "cell_size": calibration.cell_size,
                "confidence": calibration.confidence,
                "created_at": int(time.time() * 1000)
            }
            
            with open(self.calibration_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Failed to save calibration: {e}")
            return False
    
    def reset_calibration(self) -> bool:
        """Reset calibration data"""
        try:
            if self.calibration_file.exists():
                self.calibration_file.unlink()
            self.calibration = None
            return True
        except Exception as e:
            print(f"Failed to reset calibration: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings as dictionary"""
        return {
            "capture": asdict(self.capture),
            "detection": asdict(self.detection),
            "recognition": asdict(self.recognition),
            "prediction": asdict(self.prediction),
            "coaching": asdict(self.coaching),
            "display": asdict(self.display),
            "performance": asdict(self.performance)
        }
    
    def update_capture_settings(self, **kwargs):
        """Update capture settings"""
        for key, value in kwargs.items():
            if hasattr(self.capture, key):
                setattr(self.capture, key, value)
    
    def update_detection_settings(self, **kwargs):
        """Update detection settings"""
        for key, value in kwargs.items():
            if hasattr(self.detection, key):
                setattr(self.detection, key, value)
    
    def update_recognition_settings(self, **kwargs):
        """Update recognition settings"""
        for key, value in kwargs.items():
            if hasattr(self.recognition, key):
                setattr(self.recognition, key, value)
    
    def update_prediction_settings(self, **kwargs):
        """Update prediction settings"""
        for key, value in kwargs.items():
            if hasattr(self.prediction, key):
                setattr(self.prediction, key, value)
    
    def update_coaching_settings(self, **kwargs):
        """Update coaching settings"""
        for key, value in kwargs.items():
            if hasattr(self.coaching, key):
                setattr(self.coaching, key, value)
    
    def update_display_settings(self, **kwargs):
        """Update display settings"""
        for key, value in kwargs.items():
            if hasattr(self.display, key):
                setattr(self.display, key, value)
    
    def update_performance_settings(self, **kwargs):
        """Update performance settings"""
        for key, value in kwargs.items():
            if hasattr(self.performance, key):
                setattr(self.performance, key, value)
    
    def validate_settings(self) -> Dict[str, List[str]]:
        """Validate all settings and return errors"""
        errors = {}
        
        # Validate capture settings
        capture_errors = []
        if self.capture.fps <= 0 or self.capture.fps > 120:
            capture_errors.append("FPS must be between 1 and 120")
        if self.capture.quality not in ["low", "medium", "high"]:
            capture_errors.append("Quality must be low, medium, or high")
        if self.capture.monitor < 0:
            capture_errors.append("Monitor index must be non-negative")
        if capture_errors:
            errors["capture"] = capture_errors
        
        # Validate detection settings
        detection_errors = []
        if not 0.0 <= self.detection.threshold <= 1.0:
            detection_errors.append("Threshold must be between 0.0 and 1.0")
        if self.detection.method not in ["edges", "contours", "template"]:
            detection_errors.append("Method must be edges, contours, or template")
        if detection_errors:
            errors["detection"] = detection_errors
        
        # Validate recognition settings
        recognition_errors = []
        if not 0.0 <= self.recognition.template_threshold <= 1.0:
            recognition_errors.append("Template threshold must be between 0.0 and 1.0")
        if not 0.0 <= self.recognition.min_confidence <= 1.0:
            recognition_errors.append("Min confidence must be between 0.0 and 1.0")
        if recognition_errors:
            errors["recognition"] = recognition_errors
        
        # Validate prediction settings
        prediction_errors = []
        if not 1 <= self.prediction.max_suggestions <= 10:
            prediction_errors.append("Max suggestions must be between 1 and 10")
        if not 0.0 <= self.prediction.confidence_threshold <= 1.0:
            prediction_errors.append("Confidence threshold must be between 0.0 and 1.0")
        if prediction_errors:
            errors["prediction"] = prediction_errors
        
        # Validate coaching settings
        coaching_errors = []
        if not 1 <= self.coaching.max_hints <= 10:
            coaching_errors.append("Max hints must be between 1 and 10")
        if not 0.0 <= self.coaching.confidence_threshold <= 1.0:
            coaching_errors.append("Confidence threshold must be between 0.0 and 1.0")
        if coaching_errors:
            errors["coaching"] = coaching_errors
        
        return errors
    
    def export_settings(self, file_path: str) -> bool:
        """Export settings to specified file"""
        try:
            data = self.get_all_settings()
            data["exported_at"] = int(time.time() * 1000)
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Failed to export settings: {e}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """Import settings from specified file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Update settings from imported data
            if "capture" in data:
                self._update_dataclass(self.capture, data["capture"])
            if "detection" in data:
                self._update_dataclass(self.detection, data["detection"])
            if "recognition" in data:
                self._update_dataclass(self.recognition, data["recognition"])
            if "prediction" in data:
                self._update_dataclass(self.prediction, data["prediction"])
            if "coaching" in data:
                self._update_dataclass(self.coaching, data["coaching"])
            if "display" in data:
                self._update_dataclass(self.display, data["display"])
            if "performance" in data:
                self._update_dataclass(self.performance, data["performance"])
            
            # Save imported settings
            self.save_settings()
            
            return True
            
        except Exception as e:
            print(f"Failed to import settings: {e}")
            return False
    
    def _update_dataclass(self, obj: Any, data: Dict[str, Any]):
        """Update dataclass object with dictionary data"""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get configuration information"""
        return {
            "config_dir": str(self.config_dir),
            "settings_file": str(self.settings_file),
            "calibration_file": str(self.calibration_file),
            "settings_exist": self.settings_file.exists(),
            "calibration_exists": self.calibration_file.exists(),
            "calibration_loaded": self.calibration is not None,
            "last_updated": None
        }
    
    def create_default_config_file(self, file_path: str) -> bool:
        """Create a default configuration file"""
        try:
            default_data = {
                "capture": asdict(CaptureSettings()),
                "detection": asdict(DetectionSettings()),
                "recognition": asdict(RecognitionSettings()),
                "prediction": asdict(PredictionSettings()),
                "coaching": asdict(CoachingSettings()),
                "display": asdict(DisplaySettings()),
                "performance": asdict(PerformanceSettings()),
                "description": "Default configuration for Tetris Analyzer Plugin",
                "version": "1.0"
            }
            
            with open(file_path, 'w') as f:
                json.dump(default_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Failed to create default config file: {e}")
            return False
