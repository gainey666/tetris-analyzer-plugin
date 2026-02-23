"""
CLI Utilities for Tetris Analyzer

Additional command-line utilities and helper functions for enhanced CLI experience.
"""

import argparse
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from capture.capture_adapter import PythonScreenCapture
from detection.board_detector import BoardDetector
from recognition.piece_recognizer import PieceRecognizer
from state.game_state_manager import GameStateManager
from prediction.prediction_engine import PredictionEngine
from coaching.coaching_module import CoachingModule
from utils.performance import PerformanceMonitor
from utils.frame_types import BoardCalibration


class CLIUtilities:
    """Additional CLI utilities for Tetris Analyzer"""
    
    def __init__(self):
        """Initialize CLI utilities"""
        self.performance_monitor = PerformanceMonitor()
    
    def check_system_requirements(self) -> Dict[str, Any]:
        """Check system requirements and capabilities"""
        requirements = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
            "dependencies": self._check_dependencies(),
            "screen_capture": self._check_screen_capture(),
            "performance": self._check_performance()
        }
        
        return requirements
    
    def _check_dependencies(self) -> Dict[str, bool]:
        """Check if required dependencies are installed"""
        dependencies = {}
        
        required_packages = [
            "cv2", "numpy", "pyautogui", "PIL", "psutil",
            "flask", "socketio", "requests"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                dependencies[package] = True
            except ImportError:
                dependencies[package] = False
        
        return dependencies
    
    def _check_screen_capture(self) -> Dict[str, Any]:
        """Check screen capture capabilities"""
        try:
            capture = PythonScreenCapture()
            if capture.start_capture():
                # Give capture thread time to start
                time.sleep(0.1)
                
                # Test capture
                frame_data = capture.get_frame()
                if frame_data is not None and frame_data.data is not None:
                    frame = frame_data.data
                    capture.stop_capture()
                    return {
                        "available": True,
                        "resolution": f"{frame.shape[1]}x{frame.shape[0]}",
                        "channels": frame.shape[2] if len(frame.shape) > 2 else 1
                    }
                else:
                    capture.stop_capture()
                    return {"available": False, "error": "Failed to capture frame"}
            else:
                return {"available": False, "error": "Failed to start capture"}
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def _check_performance(self) -> Dict[str, Any]:
        """Check system performance"""
        try:
            import psutil
            
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory info
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk info
            disk = psutil.disk_usage('/')
            disk_free_gb = disk.free / (1024**3)
            
            return {
                "cpu_percent": cpu_percent,
                "cpu_count": cpu_count,
                "memory_percent": memory_percent,
                "memory_available_gb": round(memory_available_gb, 2),
                "disk_free_gb": round(disk_free_gb, 2),
                "performance_rating": self._rate_performance(cpu_percent, memory_percent)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _rate_performance(self, cpu_percent: float, memory_percent: float) -> str:
        """Rate system performance for Tetris analysis"""
        if cpu_percent < 50 and memory_percent < 70:
            return "Excellent"
        elif cpu_percent < 75 and memory_percent < 85:
            return "Good"
        elif cpu_percent < 90 and memory_percent < 95:
            return "Fair"
        else:
            return "Poor"
    
    def create_sample_config(self, output_path: str = "sample_config.json") -> bool:
        """Create a sample configuration file"""
        sample_config = {
            "capture": {
                "fps": 30,
                "quality": "high",
                "monitor": 0,
                "region": None
            },
            "detection": {
                "method": "edges",
                "threshold": 0.8,
                "min_board_size": [200, 400],
                "max_board_size": [400, 800],
                "edge_threshold1": 50,
                "edge_threshold2": 150
            },
            "recognition": {
                "template_threshold": 0.8,
                "color_tolerance": 0.2,
                "min_confidence": 0.6,
                "use_color_heuristics": True,
                "use_template_matching": True
            },
            "prediction": {
                "max_suggestions": 5,
                "confidence_threshold": 0.6,
                "lookahead_depth": 3,
                "weights": {
                    "score": 1.0,
                    "lines": 2.0,
                    "height": 1.5,
                    "holes": 2.0
                }
            },
            "coaching": {
                "enabled": True,
                "max_hints": 5,
                "hint_lifetime": 10000,
                "confidence_threshold": 0.6,
                "enable_move_suggestions": True,
                "enable_danger_warnings": True,
                "enable_strategy_tips": True,
                "urgency_filter": "medium"
            },
            "display": {
                "verbose": False,
                "show_predictions": True,
                "show_coaching": True,
                "show_statistics": True,
                "stats_interval": 5.0,
                "log_level": "INFO"
            },
            "performance": {
                "max_cpu_usage": 80.0,
                "max_memory_usage": 512,
                "enable_threading": True,
                "enable_profiling": False,
                "frame_skip_threshold": 2
            }
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(sample_config, f, indent=2)
            print(f"Sample configuration created: {output_path}")
            return True
        except Exception as e:
            print(f"Failed to create sample config: {e}")
            return False
    
    def benchmark_performance(self, duration_seconds: int = 30) -> Dict[str, Any]:
        """Run performance benchmark"""
        print(f"Running performance benchmark for {duration_seconds} seconds...")
        
        # Initialize components
        capture = PythonScreenCapture()
        detector = BoardDetector()
        recognizer = PieceRecognizer()
        state_manager = GameStateManager()
        predictor = PredictionEngine()
        coach = CoachingModule()
        
        if not all([capture.start_capture(), detector.initialize(), recognizer.initialize()]):
            return {"error": "Failed to initialize components"}
        
        # Benchmark metrics
        start_time = time.time()
        frame_count = 0
        detection_times = []
        recognition_times = []
        prediction_times = []
        
        try:
            while time.time() - start_time < duration_seconds:
                # Capture frame
                frame_start = time.time()
                frame_data = capture.get_frame()
                frame = frame_data.data if frame_data else None
                capture_time = time.time() - frame_start
                
                if frame is None:
                    continue
                
                frame_count += 1
                
                # Detect board
                detect_start = time.time()
                board_region = detector.detect_board(frame)
                detect_time = time.time() - detect_start
                detection_times.append(detect_time)
                
                if board_region is None:
                    continue
                
                # Recognize pieces
                recog_start = time.time()
                pieces = recognizer.recognize_pieces(frame, board_region)
                recog_time = time.time() - recog_start
                recognition_times.append(recog_time)
                
                # Update state
                state_manager.update_state(pieces)
                board_state = state_manager.get_current_state()
                
                # Predict moves
                if board_state and board_state.current_piece:
                    pred_start = time.time()
                    predictions = predictor.predict_moves(board_state, board_state.current_piece)
                    pred_time = time.time() - pred_start
                    prediction_times.append(pred_time)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.01)
        
        finally:
            capture.stop_capture()
        
        # Calculate statistics
        total_time = time.time() - start_time
        
        benchmark_results = {
            "duration_seconds": total_time,
            "total_frames": frame_count,
            "average_fps": frame_count / total_time if total_time > 0 else 0,
            "capture": {
                "average_time_ms": (total_time / frame_count * 1000) if frame_count > 0 else 0,
                "fps": frame_count / total_time if total_time > 0 else 0
            },
            "detection": {
                "average_time_ms": (sum(detection_times) / len(detection_times) * 1000) if detection_times else 0,
                "success_rate": len([t for t in detection_times if t < 0.1]) / len(detection_times) if detection_times else 0
            },
            "recognition": {
                "average_time_ms": (sum(recognition_times) / len(recognition_times) * 1000) if recognition_times else 0,
                "success_rate": len([t for t in recognition_times if t < 0.05]) / len(recognition_times) if recognition_times else 0
            },
            "prediction": {
                "average_time_ms": (sum(prediction_times) / len(prediction_times) * 1000) if prediction_times else 0,
                "predictions_per_second": len(prediction_times) / total_time if total_time > 0 else 0
            },
            "performance_rating": self._rate_benchmark_performance(frame_count / total_time if total_time > 0 else 0)
        }
        
        return benchmark_results
    
    def _rate_benchmark_performance(self, fps: float) -> str:
        """Rate benchmark performance"""
        if fps >= 30:
            return "Excellent"
        elif fps >= 20:
            return "Good"
        elif fps >= 10:
            return "Fair"
        else:
            return "Poor"
    
    def list_calibration_files(self) -> List[str]:
        """List existing calibration files"""
        calib_files = []
        for file in Path(".").glob("*.json"):
            if "calibration" in file.name.lower() or "board" in file.name.lower():
                calib_files.append(str(file))
        return calib_files
    
    def validate_configuration(self, config_path: str) -> Dict[str, Any]:
        """Validate configuration file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            validation_results = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Validate capture settings
            if "capture" in config:
                capture = config["capture"]
                if capture.get("fps", 30) <= 0 or capture.get("fps", 30) > 120:
                    validation_results["errors"].append("Capture FPS must be between 1 and 120")
                if capture.get("quality") not in ["low", "medium", "high"]:
                    validation_results["errors"].append("Capture quality must be low, medium, or high")
            
            # Validate detection settings
            if "detection" in config:
                detection = config["detection"]
                if not 0.0 <= detection.get("threshold", 0.8) <= 1.0:
                    validation_results["errors"].append("Detection threshold must be between 0.0 and 1.0")
                if detection.get("method") not in ["edges", "contours", "template"]:
                    validation_results["errors"].append("Detection method must be edges, contours, or template")
            
            # Validate prediction settings
            if "prediction" in config:
                prediction = config["prediction"]
                if not 1 <= prediction.get("max_suggestions", 5) <= 10:
                    validation_results["errors"].append("Max suggestions must be between 1 and 10")
                if not 0.0 <= prediction.get("confidence_threshold", 0.6) <= 1.0:
                    validation_results["errors"].append("Confidence threshold must be between 0.0 and 1.0")
            
            validation_results["valid"] = len(validation_results["errors"]) == 0
            
            return validation_results
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Failed to parse configuration: {e}"],
                "warnings": []
            }
    
    def show_system_info(self) -> None:
        """Display comprehensive system information"""
        print("🎮 Tetris Analyzer - System Information")
        print("=" * 50)
        
        # System requirements
        requirements = self.check_system_requirements()
        print(f"Python Version: {requirements['python_version']}")
        print(f"Platform: {requirements['platform']}")
        
        # Dependencies
        print("\n📦 Dependencies:")
        for package, installed in requirements["dependencies"].items():
            status = "✅" if installed else "❌"
            print(f"  {status} {package}")
        
        # Screen capture
        print("\n📺 Screen Capture:")
        screen = requirements["screen_capture"]
        if screen.get("available"):
            print(f"  ✅ Available ({screen['resolution']}, {screen['channels']} channels)")
        else:
            print(f"  ❌ Not available: {screen.get('error', 'Unknown error')}")
        
        # Performance
        print("\n⚡ Performance:")
        perf = requirements["performance"]
        if "error" not in perf:
            print(f"  CPU: {perf['cpu_percent']:.1f}% ({perf['cpu_count']} cores)")
            print(f"  Memory: {perf['memory_percent']:.1f}% ({perf['memory_available_gb']:.1f}GB available)")
            print(f"  Disk: {perf['disk_free_gb']:.1f}GB free")
            print(f"  Rating: {perf['performance_rating']}")
        else:
            print(f"  ❌ Error: {perf['error']}")
        
        print("=" * 50)


def add_cli_utility_commands(parser: argparse.ArgumentParser) -> None:
    """Add utility commands to CLI parser"""
    utils_parser = parser.add_subparsers(dest='utility', help='Utility commands')
    
    # System check command
    check_parser = utils_parser.add_parser('check', help='Check system requirements')
    check_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Benchmark command
    bench_parser = utils_parser.add_parser('benchmark', help='Run performance benchmark')
    bench_parser.add_argument('--duration', type=int, default=30, help='Benchmark duration in seconds')
    
    # Config commands
    config_parser = utils_parser.add_parser('config', help='Configuration utilities')
    config_subparsers = config_parser.add_subparsers(dest='config_action')
    
    config_subparsers.add_parser('create', help='Create sample configuration')
    validate_parser = config_subparsers.add_parser('validate', help='Validate configuration file')
    validate_parser.add_argument('--config', required=True, help='Configuration file to validate')
    
    # Calibration command
    calib_parser = utils_parser.add_parser('calibration', help='Calibration utilities')
    calib_parser.add_argument('--list', action='store_true', help='List calibration files')
    
    # Info command
    info_parser = utils_parser.add_parser('info', help='Show system information')


def handle_cli_utility_command(args) -> None:
    """Handle CLI utility commands"""
    utilities = CLIUtilities()
    
    if args.utility == 'check':
        utilities.show_system_info()
        if args.verbose:
            print("\n🔍 Detailed Requirements Check:")
            requirements = utilities.check_system_requirements()
            print(json.dumps(requirements, indent=2))
    
    elif args.utility == 'benchmark':
        results = utilities.benchmark_performance(args.duration)
        print("\n📊 Benchmark Results:")
        print(json.dumps(results, indent=2))
    
    elif args.utility == 'config':
        if args.config_action == 'create':
            utilities.create_sample_config()
        elif args.config_action == 'validate':
            config_file = getattr(args, 'config', None)
            if config_file:
                results = utilities.validate_configuration(config_file)
                print(f"Configuration {config_file}:")
                print(f"  Valid: {results['valid']}")
                if results['errors']:
                    print("  Errors:")
                    for error in results['errors']:
                        print(f"    - {error}")
                if results['warnings']:
                    print("  Warnings:")
                    for warning in results['warnings']:
                        print(f"    - {warning}")
            else:
                print("Please specify a configuration file with --config <file>")
    
    elif args.utility == 'calibration':
        if args.list:
            files = utilities.list_calibration_files()
            if files:
                print("📁 Calibration files:")
                for file in files:
                    print(f"  {file}")
            else:
                print("No calibration files found")
    
    elif args.utility == 'info':
        utilities.show_system_info()
