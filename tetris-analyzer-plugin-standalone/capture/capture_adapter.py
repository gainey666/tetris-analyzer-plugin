"""
Capture Adapter Interface and Implementation

This module provides the abstract interface for screen capture implementations
and a concrete Python-based implementation for the Tetris analyzer plugin.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
import time
import threading
import numpy as np
import pyautogui
import cv2
from utils.frame_types import FrameData
from utils.performance import measure_latency, perf_monitor


class CaptureAdapter(ABC):
    """Abstract interface for screen capture implementations"""
    
    @abstractmethod
    def start_capture(self) -> bool:
        """Start capturing frames"""
        pass
    
    @abstractmethod
    def stop_capture(self) -> bool:
        """Stop capturing frames"""
        pass
    
    @abstractmethod
    def get_frame(self) -> Optional[FrameData]:
        """Get next frame from capture"""
        pass
    
    @abstractmethod
    def get_resolution(self) -> Tuple[int, int]:
        """Get current capture resolution"""
        pass
    
    @abstractmethod
    def is_capturing(self) -> bool:
        """Check if capture is active"""
        pass
    
    @abstractmethod
    def get_capture_source(self) -> str:
        """Get capture source identifier"""
        pass


class PythonScreenCapture(CaptureAdapter):
    """Python-based screen capture implementation using pyautogui and OpenCV"""
    
    def __init__(self, capture_region: Optional[Tuple[int, int, int, int]] = None):
        """
        Initialize Python screen capture
        
        Args:
            capture_region: (x, y, width, height) region to capture, None for full screen
        """
        self.capture_region = capture_region
        self._capturing = False
        self._capture_thread = None
        self._frame_queue = []
        self._queue_lock = threading.Lock()
        self._sequence_counter = 0
        self._stop_event = threading.Event()
        
        # Performance tracking
        self._last_frame_time = 0
        self._fps_counter = 0
        self._fps_start_time = time.time()
    
    @measure_latency("capture_start")
    def start_capture(self) -> bool:
        """Start capturing frames"""
        if self._capturing:
            return True
        
        try:
            # Validate capture region
            if self.capture_region:
                screen_width, screen_height = pyautogui.size()
                x, y, width, height = self.capture_region
                
                if x < 0 or y < 0 or width <= 0 or height <= 0:
                    raise ValueError("Invalid capture region")
                
                if x + width > screen_width or y + height > screen_height:
                    raise ValueError("Capture region extends beyond screen bounds")
            
            # Start capture thread
            self._capturing = True
            self._stop_event.clear()
            self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._capture_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to start capture: {e}")
            return False
    
    @measure_latency("capture_stop")
    def stop_capture(self) -> bool:
        """Stop capturing frames"""
        if not self._capturing:
            return True
        
        try:
            self._capturing = False
            self._stop_event.set()
            
            if self._capture_thread and self._capture_thread.is_alive():
                self._capture_thread.join(timeout=2.0)
            
            # Clear frame queue
            with self._queue_lock:
                self._frame_queue.clear()
            
            return True
            
        except Exception as e:
            print(f"Failed to stop capture: {e}")
            return False
    
    @measure_latency("capture_get_frame")
    def get_frame(self) -> Optional[FrameData]:
        """Get next frame from capture"""
        with self._queue_lock:
            if not self._frame_queue:
                return None
            
            # Return the most recent frame (discard older frames)
            frame_data = self._frame_queue.pop()
            
            # Clear queue to prevent buildup
            self._frame_queue.clear()
            
            return frame_data
    
    def get_resolution(self) -> Tuple[int, int]:
        """Get current capture resolution"""
        if self.capture_region:
            _, _, width, height = self.capture_region
            return (width, height)
        else:
            return pyautogui.size()
    
    def is_capturing(self) -> bool:
        """Check if capture is active"""
        return self._capturing and (self._capture_thread is None or self._capture_thread.is_alive())
    
    def get_capture_source(self) -> str:
        """Get capture source identifier"""
        if self.capture_region:
            return f"region_{self.capture_region[0]}_{self.capture_region[1]}_{self.capture_region[2]}_{self.capture_region[3]}"
        else:
            return "fullscreen"
    
    def _capture_loop(self):
        """Main capture loop running in separate thread"""
        while self._capturing and not self._stop_event.is_set():
            try:
                # Capture frame
                frame_start_time = time.perf_counter()
                
                if self.capture_region:
                    screenshot = pyautogui.screenshot(region=self.capture_region)
                else:
                    screenshot = pyautogui.screenshot()
                
                # Convert to numpy array (RGB)
                frame_array = np.array(screenshot)
                
                # Convert RGB to BGR for OpenCV compatibility
                frame_bgr = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
                
                # Create FrameData
                height, width = frame_bgr.shape[:2]
                timestamp = int(time.time() * 1000)
                
                frame_data = FrameData(
                    data=frame_bgr,
                    timestamp=timestamp,
                    sequence=self._sequence_counter,
                    width=width,
                    height=height,
                    format="BGR",
                    source=self.get_capture_source()
                )
                
                # Add to queue (keep only latest frame)
                with self._queue_lock:
                    self._frame_queue.append(frame_data)
                    # Keep queue size small (max 3 frames)
                    if len(self._frame_queue) > 3:
                        self._frame_queue = self._frame_queue[-3:]
                
                # Update counters
                self._sequence_counter += 1
                
                # Calculate FPS
                capture_time = time.perf_counter() - frame_start_time
                self._fps_counter += 1
                
                current_time = time.time()
                if current_time - self._fps_start_time >= 1.0:
                    fps = self._fps_counter / (current_time - self._fps_start_time)
                    perf_monitor.record_metric("capture_fps", fps)
                    self._fps_counter = 0
                    self._fps_start_time = current_time
                
                # Record capture latency
                capture_latency_ms = capture_time * 1000
                perf_monitor.record_metric("capture_latency_ms", capture_latency_ms)
                
                # Sleep to maintain reasonable frame rate (target 30 FPS)
                sleep_time = max(0, (1.0 / 30.0) - capture_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except Exception as e:
                print(f"Capture loop error: {e}")
                time.sleep(0.1)  # Brief pause on error
    
    def get_performance_stats(self) -> dict:
        """Get capture performance statistics"""
        capture_stats = perf_monitor.get_stats("capture_fps")
        latency_stats = perf_monitor.get_stats("capture_latency_ms")
        
        return {
            "fps": capture_stats,
            "latency_ms": latency_stats,
            "capturing": self.is_capturing(),
            "sequence_counter": self._sequence_counter,
            "capture_source": self.get_capture_source()
        }


class WindowCapture(CaptureAdapter):
    """Window-specific capture implementation"""
    
    def __init__(self, window_title: str):
        """
        Initialize window capture
        
        Args:
            window_title: Title of window to capture
        """
        self.window_title = window_title
        self._capturing = False
        self._window_handle = None
        
    def start_capture(self) -> bool:
        """Start capturing specific window"""
        try:
            # Find window by title
            import win32gui
            self._window_handle = win32gui.FindWindow(None, self.window_title)
            
            if not self._window_handle:
                raise ValueError(f"Window '{self.window_title}' not found")
            
            self._capturing = True
            return True
            
        except Exception as e:
            print(f"Failed to start window capture: {e}")
            return False
    
    def stop_capture(self) -> bool:
        """Stop capturing window"""
        self._capturing = False
        self._window_handle = None
        return True
    
    def get_frame(self) -> Optional[FrameData]:
        """Get frame from window capture"""
        if not self._capturing or not self._window_handle:
            return None
        
        try:
            import win32gui
            import win32con
            
            # Get window dimensions
            rect = win32gui.GetWindowRect(self._window_handle)
            x, y, right, bottom = rect
            width = right - x
            height = bottom - y
            
            # Capture window region
            capture_region = (x, y, width, height)
            screenshot = pyautogui.screenshot(region=capture_region)
            
            # Convert to FrameData
            frame_array = np.array(screenshot)
            frame_bgr = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
            
            timestamp = int(time.time() * 1000)
            
            return FrameData(
                data=frame_bgr,
                timestamp=timestamp,
                sequence=0,  # Simple implementation
                width=width,
                height=height,
                format="BGR",
                source=f"window_{self.window_title}"
            )
            
        except Exception as e:
            print(f"Window capture error: {e}")
            return None
    
    def get_resolution(self) -> Tuple[int, int]:
        """Get window resolution"""
        if not self._window_handle:
            return (0, 0)
        
        try:
            import win32gui
            rect = win32gui.GetWindowRect(self._window_handle)
            x, y, right, bottom = rect
            return (right - x, bottom - y)
        except:
            return (0, 0)
    
    def is_capturing(self) -> bool:
        """Check if window capture is active"""
        return self._capturing and self._window_handle is not None
    
    def get_capture_source(self) -> str:
        """Get window capture source"""
        return f"window_{self.window_title}"


def create_capture_adapter(capture_type: str = "screen", **kwargs) -> CaptureAdapter:
    """
    Factory function to create capture adapters
    
    Args:
        capture_type: Type of capture ("screen", "window", "region")
        **kwargs: Additional arguments for specific capture types
    
    Returns:
        CaptureAdapter instance
    """
    if capture_type == "screen":
        return PythonScreenCapture()
    elif capture_type == "region":
        region = kwargs.get("region")
        if not region:
            raise ValueError("Region capture requires 'region' parameter")
        return PythonScreenCapture(capture_region=region)
    elif capture_type == "window":
        window_title = kwargs.get("window_title")
        if not window_title:
            raise ValueError("Window capture requires 'window_title' parameter")
        return WindowCapture(window_title)
    else:
        raise ValueError(f"Unsupported capture type: {capture_type}")
