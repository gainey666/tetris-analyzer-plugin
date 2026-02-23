"""
Command Line Interface for Tetris Analyzer Plugin

This module provides a command-line interface for running the Tetris analyzer
as a standalone application with various operation modes and configuration options.
"""

import argparse
import sys
import time
import signal
import threading
from typing import Optional, Dict, Any
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import core modules
from capture.capture_adapter import CaptureAdapter
from detection.board_detector import BoardDetector
from recognition.piece_recognizer import PieceRecognizer
from state.game_state_manager import GameStateManager
from prediction.prediction_engine import PredictionEngine
from coaching.coaching_module import CoachingModule
from utils.performance import PerformanceMonitor
from utils.frame_types import BoardCalibration


class TetrisAnalyzerCLI:
    """Command-line interface for Tetris analyzer"""
    
    def __init__(self):
        """Initialize CLI application"""
        self.capture_adapter: Optional[CaptureAdapter] = None
        self.board_detector: Optional[BoardDetector] = None
        self.piece_recognizer: Optional[PieceRecognizer] = None
        self.game_state: Optional[GameStateManager] = None
        self.prediction_engine: Optional[PredictionEngine] = None
        self.coaching_module: Optional[CoachingModule] = None
        self.performance_monitor: Optional[PerformanceMonitor] = None
        
        self.running = False
        self.verbose = False
        self.show_coaching = True
        self.show_predictions = True
        self.stats_interval = 5.0  # seconds
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}. Shutting down...")
        self.stop()
    
    def initialize(self, config_file: Optional[str] = None) -> bool:
        """Initialize all components"""
        try:
            if self.verbose:
                print("Initializing Tetris Analyzer...")
            
            # Load configuration
            config = self._load_config(config_file)
            
            # Initialize performance monitor
            self.performance_monitor = PerformanceMonitor()
            
            # Initialize capture adapter
            self.capture_adapter = CaptureAdapter()
            if not self.capture_adapter.initialize():
                print("Failed to initialize capture adapter")
                return False
            
            # Initialize board detector
            self.board_detector = BoardDetector()
            if not self.board_detector.initialize():
                print("Failed to initialize board detector")
                return False
            
            # Initialize piece recognizer
            self.piece_recognizer = PieceRecognizer()
            if not self.piece_recognizer.initialize():
                print("Failed to initialize piece recognizer")
                return False
            
            # Initialize game state manager
            self.game_state = GameStateManager()
            
            # Initialize prediction engine
            self.prediction_engine = PredictionEngine()
            
            # Initialize coaching module
            self.coaching_module = CoachingModule()
            
            # Apply configuration
            self._apply_config(config)
            
            if self.verbose:
                print("Initialization complete!")
            
            return True
            
        except Exception as e:
            print(f"Initialization error: {e}")
            return False
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "capture": {
                "region": None,
                "fps": 30,
                "quality": "high"
            },
            "detection": {
                "method": "edges",
                "threshold": 0.8
            },
            "prediction": {
                "max_suggestions": 3,
                "confidence_threshold": 0.6
            },
            "coaching": {
                "enabled": True,
                "max_hints": 5,
                "urgency_threshold": "medium"
            },
            "display": {
                "verbose": False,
                "show_predictions": True,
                "show_coaching": True,
                "stats_interval": 5.0
            }
        }
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                for section, values in loaded_config.items():
                    if section in default_config:
                        default_config[section].update(values)
                    else:
                        default_config[section] = values
            except Exception as e:
                print(f"Warning: Failed to load config file {config_file}: {e}")
        
        return default_config
    
    def _apply_config(self, config: Dict[str, Any]):
        """Apply configuration to components"""
        # Apply display settings
        display_config = config.get("display", {})
        self.verbose = display_config.get("verbose", False)
        self.show_predictions = display_config.get("show_predictions", True)
        self.show_coaching = display_config.get("show_coaching", True)
        self.stats_interval = display_config.get("stats_interval", 5.0)
        
        # Apply prediction settings
        prediction_config = config.get("prediction", {})
        if self.prediction_engine:
            self.prediction_engine.set_max_suggestions(prediction_config.get("max_suggestions", 3))
            self.prediction_engine.set_confidence_threshold(prediction_config.get("confidence_threshold", 0.6))
        
        # Apply coaching settings
        coaching_config = config.get("coaching", {})
        if self.coaching_module:
            self.coaching_module.update_settings(
                max_hints=coaching_config.get("max_hints", 5),
                enable_move_suggestions=coaching_config.get("enabled", True),
                enable_danger_warnings=coaching_config.get("enabled", True),
                enable_strategy_tips=coaching_config.get("enabled", True)
            )
    
    def start(self):
        """Start the analyzer"""
        if not all([self.capture_adapter, self.board_detector, self.piece_recognizer,
                   self.game_state, self.prediction_engine, self.coaching_module]):
            print("Error: Components not properly initialized")
            return False
        
        self.running = True
        
        if self.verbose:
            print("Starting Tetris Analyzer...")
            print("Press Ctrl+C to stop")
        
        # Start analysis loop
        try:
            self._analysis_loop()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """Stop the analyzer"""
        self.running = False
        
        if self.verbose:
            print("Stopping analyzer...")
        
        # Cleanup components
        if self.capture_adapter:
            self.capture_adapter.cleanup()
        
        if self.verbose:
            print("Analyzer stopped")
    
    def _analysis_loop(self):
        """Main analysis loop"""
        last_stats_time = time.time()
        frame_count = 0
        
        while self.running:
            try:
                # Capture frame
                frame = self.capture_adapter.capture_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                frame_count += 1
                
                # Detect board
                board_region = self.board_detector.detect_board(frame)
                if board_region is None:
                    if self.verbose and frame_count % 30 == 0:
                        print("No board detected")
                    time.sleep(0.1)
                    continue
                
                # Recognize pieces
                pieces = self.piece_recognizer.recognize_pieces(frame, board_region)
                
                # Update game state
                self.game_state.update_state(pieces)
                board_state = self.game_state.get_current_state()
                
                if board_state:
                    # Generate predictions
                    if self.show_predictions and board_state.current_piece:
                        predictions = self.prediction_engine.predict_moves(board_state, board_state.current_piece)
                        if predictions and self.verbose:
                            self._display_predictions(predictions)
                    
                    # Generate coaching hints
                    if self.show_coaching:
                        predictions = self.prediction_engine.predict_moves(board_state, board_state.current_piece) if board_state.current_piece else []
                        hints = self.coaching_module.generate_hints(board_state, board_state.current_piece, predictions)
                        if hints and self.verbose:
                            self._display_hints(hints)
                
                # Display statistics periodically
                current_time = time.time()
                if current_time - last_stats_time >= self.stats_interval:
                    self._display_statistics()
                    last_stats_time = current_time
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                if self.verbose:
                    print(f"Analysis loop error: {e}")
                time.sleep(0.1)
    
    def _display_predictions(self, predictions):
        """Display move predictions"""
        if not predictions:
            return
        
        print("\n=== MOVE SUGGESTIONS ===")
        for i, pred in enumerate(predictions[:3], 1):
            print(f"{i}. {pred.reasoning} (Score: {pred.score:.1f}, Confidence: {pred.confidence:.2f})")
    
    def _display_hints(self, hints):
        """Display coaching hints"""
        if not hints:
            return
        
        print("\n=== COACHING HINTS ===")
        for hint in hints[:3]:  # Show top 3 hints
            urgency_symbol = "!" * hint.urgency.value
            print(f"{urgency_symbol} {hint.message}")
    
    def _display_statistics(self):
        """Display performance statistics"""
        if not self.performance_monitor:
            return
        
        stats = {
            'capture': self.capture_adapter.get_statistics() if self.capture_adapter else {},
            'detection': self.board_detector.get_statistics() if self.board_detector else {},
            'recognition': self.piece_recognizer.get_statistics() if self.piece_recognizer else {},
            'prediction': self.prediction_engine.get_prediction_statistics() if self.prediction_engine else {},
            'coaching': self.coaching_module.get_coaching_statistics() if self.coaching_module else {},
            'performance': self.performance_monitor.get_all_stats()
        }
        
        print("\n=== PERFORMANCE STATISTICS ===")
        for component, component_stats in stats.items():
            if component_stats:
                print(f"\n{component.upper()}:")
                for key, value in component_stats.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            print(f"  {key}.{sub_key}: {sub_value}")
                    else:
                        print(f"  {key}: {value}")
    
    def calibrate(self) -> bool:
        """Run calibration routine"""
        if not self.capture_adapter or not self.board_detector:
            print("Error: Components not initialized")
            return False
        
        print("Starting calibration...")
        print("Please make sure the Tetris game window is visible and focused.")
        
        # Capture a few frames for calibration
        for i in range(5):
            print(f"Calibrating... {i+1}/5")
            frame = self.capture_adapter.capture_frame()
            if frame is None:
                print("Failed to capture frame")
                return False
            
            # Try to detect board
            board_region = self.board_detector.detect_board(frame)
            if board_region:
                print(f"Board detected: {board_region}")
                calibration = BoardCalibration(
                    board_region=board_region,
                    cell_size=None,  # Will be calculated
                    confidence=0.9
                )
                # Save calibration
                self._save_calibration(calibration)
                print("Calibration complete!")
                return True
            
            time.sleep(1)
        
        print("Failed to detect board during calibration")
        return False
    
    def _save_calibration(self, calibration: BoardCalibration):
        """Save calibration data"""
        calib_file = Path("calibration.json")
        try:
            calib_data = {
                "board_region": calibration.board_region,
                "confidence": calibration.confidence
            }
            with open(calib_file, 'w') as f:
                json.dump(calib_data, f, indent=2)
            print(f"Calibration saved to {calib_file}")
        except Exception as e:
            print(f"Failed to save calibration: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Tetris Analyzer Plugin - Standalone")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--calibrate", action="store_true", help="Run calibration only")
    parser.add_argument("--no-coaching", action="store_true", help="Disable coaching hints")
    parser.add_argument("--no-predictions", action="store_true", help="Disable move predictions")
    parser.add_argument("--stats-interval", type=float, default=5.0, help="Statistics display interval (seconds)")
    
    args = parser.parse_args()
    
    # Create and initialize analyzer
    analyzer = TetrisAnalyzerCLI()
    
    # Apply command line overrides
    analyzer.verbose = args.verbose
    analyzer.show_coaching = not args.no_coaching
    analyzer.show_predictions = not args.no_predictions
    analyzer.stats_interval = args.stats_interval
    
    # Initialize
    if not analyzer.initialize(args.config):
        print("Failed to initialize analyzer")
        sys.exit(1)
    
    # Run calibration or start analysis
    if args.calibrate:
        success = analyzer.calibrate()
        sys.exit(0 if success else 1)
    else:
        analyzer.start()
        sys.exit(0)


if __name__ == "__main__":
    main()
