"""
Performance Monitoring and Measurement Utilities

This module provides performance measurement capabilities for the Tetris analyzer plugin,
including latency tracking, FPS monitoring, and resource usage monitoring.
"""

import time
import threading
import psutil
from functools import wraps
from typing import Dict, List, Callable, Any
from dataclasses import dataclass


class PerformanceMonitor:
    """Thread-safe performance measurement system"""
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize performance monitor
        
        Args:
            max_history: Maximum number of measurements to keep per metric
        """
        self._metrics: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
        self._max_history = max_history
        self._start_times: Dict[str, float] = {}
    
    def record_metric(self, name: str, value: float):
        """Record a performance metric"""
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = []
            
            self._metrics[name].append(value)
            
            # Keep only recent measurements
            if len(self._metrics[name]) > self._max_history:
                self._metrics[name] = self._metrics[name][-self._max_history:]
    
    def start_timer(self, name: str):
        """Start a named timer"""
        with self._lock:
            self._start_times[name] = time.perf_counter()
    
    def end_timer(self, name: str) -> float:
        """End a named timer and record the elapsed time"""
        end_time = time.perf_counter()
        
        with self._lock:
            if name not in self._start_times:
                raise ValueError(f"Timer '{name}' was not started")
            
            elapsed = end_time - self._start_times[name]
            del self._start_times[name]
            
            self.record_metric(f"{name}_duration_ms", elapsed * 1000)
            return elapsed
    
    def get_stats(self, name: str) -> Dict[str, float]:
        """Get statistics for a metric"""
        with self._lock:
            if name not in self._metrics or not self._metrics[name]:
                return {}
            
            values = self._metrics[name]
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'latest': values[-1],
                'sum': sum(values)
            }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all metrics"""
        with self._lock:
            return {name: self.get_stats(name) for name in self._metrics.keys()}
    
    def reset_metric(self, name: str):
        """Reset a specific metric"""
        with self._lock:
            if name in self._metrics:
                del self._metrics[name]
    
    def reset_all(self):
        """Reset all metrics"""
        with self._lock:
            self._metrics.clear()
            self._start_times.clear()


# Global performance monitor instance
perf_monitor = PerformanceMonitor()


def measure_latency(stage_name: str):
    """Decorator to measure function execution time"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            perf_monitor.record_metric(f"{stage_name}_latency_ms", latency_ms)
            
            return result
        return wrapper
    return decorator


def measure_function(stage_name: str):
    """Context manager for measuring function execution time"""
    class MeasurementContext:
        def __init__(self, name: str):
            self.name = name
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.perf_counter()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.start_time is not None:
                end_time = time.perf_counter()
                latency_ms = (end_time - self.start_time) * 1000
                perf_monitor.record_metric(f"{self.name}_latency_ms", latency_ms)
    
    return MeasurementContext(stage_name)


@dataclass
class ResourceUsage:
    """System resource usage metrics"""
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    timestamp: int
    
    @classmethod
    def capture_current(cls) -> 'ResourceUsage':
        """Capture current system resource usage"""
        process = psutil.Process()
        
        cpu_percent = process.cpu_percent()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        memory_percent = process.memory_percent()
        timestamp = int(time.time() * 1000)
        
        return cls(
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            memory_percent=memory_percent,
            timestamp=timestamp
        )


class FPSCounter:
    """Frames per second counter"""
    
    def __init__(self, window_size: int = 30):
        """
        Initialize FPS counter
        
        Args:
            window_size: Number of frames to average over
        """
        self.window_size = window_size
        self._frame_times: List[float] = []
        self._lock = threading.Lock()
    
    def tick(self):
        """Record a frame tick"""
        current_time = time.perf_counter()
        
        with self._lock:
            self._frame_times.append(current_time)
            
            # Keep only recent frames
            if len(self._frame_times) > self.window_size:
                self._frame_times = self._frame_times[-self.window_size:]
    
    def get_fps(self) -> float:
        """Get current FPS"""
        with self._lock:
            if len(self._frame_times) < 2:
                return 0.0
            
            # Calculate FPS based on the time span of frames
            time_span = self._frame_times[-1] - self._frame_times[0]
            if time_span <= 0:
                return 0.0
            
            fps = (len(self._frame_times) - 1) / time_span
            return fps
    
    def reset(self):
        """Reset the FPS counter"""
        with self._lock:
            self._frame_times.clear()


class LatencyTracker:
    """Track latency percentiles and statistics"""
    
    def __init__(self, max_samples: int = 1000):
        """
        Initialize latency tracker
        
        Args:
            max_samples: Maximum number of latency samples to keep
        """
        self.max_samples = max_samples
        self._samples: List[float] = []
        self._lock = threading.Lock()
    
    def add_sample(self, latency_ms: float):
        """Add a latency sample"""
        with self._lock:
            self._samples.append(latency_ms)
            
            # Keep only recent samples
            if len(self._samples) > self.max_samples:
                self._samples = self._samples[-self.max_samples:]
    
    def get_percentiles(self) -> Dict[str, float]:
        """Get latency percentiles"""
        with self._lock:
            if not self._samples:
                return {}
            
            sorted_samples = sorted(self._samples)
            n = len(sorted_samples)
            
            return {
                'p50': sorted_samples[int(n * 0.5)],
                'p90': sorted_samples[int(n * 0.9)],
                'p95': sorted_samples[int(n * 0.95)],
                'p99': sorted_samples[int(n * 0.99)],
                'min': min(sorted_samples),
                'max': max(sorted_samples),
                'avg': sum(sorted_samples) / n,
                'count': n
            }
    
    def reset(self):
        """Reset all samples"""
        with self._lock:
            self._samples.clear()


class PerformanceProfiler:
    """Comprehensive performance profiler"""
    
    def __init__(self):
        self.fps_counter = FPSCounter()
        self.latency_tracker = LatencyTracker()
        self._start_time = time.perf_counter()
    
    def tick_frame(self):
        """Record a frame tick"""
        self.fps_counter.tick()
    
    def record_latency(self, stage_name: str, latency_ms: float):
        """Record latency for a specific stage"""
        perf_monitor.record_metric(f"{stage_name}_latency_ms", latency_ms)
        self.latency_tracker.add_sample(latency_ms)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        uptime = time.perf_counter() - self._start_time
        
        return {
            'uptime_seconds': uptime,
            'fps': self.fps_counter.get_fps(),
            'latency_percentiles': self.latency_tracker.get_percentiles(),
            'resource_usage': ResourceUsage.capture_current(),
            'all_metrics': perf_monitor.get_all_stats()
        }
    
    def reset(self):
        """Reset all performance tracking"""
        self.fps_counter.reset()
        self.latency_tracker.reset()
        perf_monitor.reset_all()
        self._start_time = time.perf_counter()


# Global performance profiler instance
performance_profiler = PerformanceProfiler()


def profile_function(stage_name: str):
    """Decorator for profiling function performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with measure_function(stage_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


class PerformanceBenchmark:
    """Utility for performance benchmarking"""
    
    @staticmethod
    def benchmark_function(func: Callable, iterations: int = 100) -> Dict[str, float]:
        """
        Benchmark a function
        
        Args:
            func: Function to benchmark
            iterations: Number of iterations to run
        
        Returns:
            Dictionary with benchmark results
        """
        times = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            func()
            end_time = time.perf_counter()
            times.append((end_time - start_time) * 1000)
        
        return {
            'iterations': iterations,
            'avg_ms': sum(times) / len(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'total_ms': sum(times)
        }
    
    @staticmethod
    def compare_functions(funcs: Dict[str, Callable], iterations: int = 100) -> Dict[str, Dict[str, float]]:
        """
        Compare multiple functions
        
        Args:
            funcs: Dictionary of function name -> function
            iterations: Number of iterations per function
        
        Returns:
            Dictionary with comparison results
        """
        results = {}
        
        for name, func in funcs.items():
            results[name] = PerformanceBenchmark.benchmark_function(func, iterations)
        
        return results
