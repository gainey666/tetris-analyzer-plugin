"""
Runtime Hub Plugin Wrapper for Tetris Analyzer

This module provides the Runtime Hub plugin interface that wraps the standalone
Tetris analyzer, managing subprocess execution and IPC communication.
"""

import subprocess
import sys
import time
import threading
import json
import signal
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import multiprocessing as mp
from dataclasses import dataclass


@dataclass
class PluginConfig:
    """Plugin configuration"""
    python_executable: str = sys.executable
    analyzer_script: str = "cli/main.py"
    working_directory: Optional[str] = None
    auto_restart: bool = True
    timeout_seconds: int = 30


@dataclass
class IPCMessage:
    """IPC message structure"""
    type: str
    data: Dict[str, Any]
    timestamp: float
    request_id: Optional[str] = None


class TetrisAnalyzerPlugin:
    """Runtime Hub plugin wrapper for Tetris analyzer"""
    
    def __init__(self, config: Optional[PluginConfig] = None):
        """Initialize plugin wrapper"""
        self.config = config or PluginConfig()
        self.process: Optional[subprocess.Popen] = None
        self.shared_memory: Optional[mp.shared_memory.SharedMemory] = None
        self.control_channel: Optional[mp.Queue] = None
        self.status_channel: Optional[mp.Queue] = None
        
        # Plugin state
        self.is_running = False
        self.is_initialized = False
        self.start_time: Optional[float] = None
        
        # Callbacks for Runtime Hub
        self.on_status_change: Optional[Callable] = None
        self.on_board_update: Optional[Callable] = None
        self.on_coaching_update: Optional[Callable] = None
        
        # Thread management
        self.monitor_thread: Optional[threading.Thread] = None
        self.ipc_thread: Optional[threading.Thread] = None
        self.shutdown_event = threading.Event()
        
        # Performance tracking
        self.last_heartbeat: Optional[float] = None
        self.frame_count = 0
        self.error_count = 0
    
    def initialize(self) -> bool:
        """Initialize plugin components"""
        try:
            # Set working directory
            if not self.config.working_directory:
                self.config.working_directory = str(Path(__file__).parent.parent)
            
            # Verify analyzer script exists
            analyzer_path = Path(self.config.working_directory) / self.config.analyzer_script
            if not analyzer_path.exists():
                print(f"Error: Analyzer script not found at {analyzer_path}")
                return False
            
            # Initialize IPC components
            self._initialize_ipc()
            
            self.is_initialized = True
            print("Tetris Analyzer Plugin initialized successfully")
            return True
            
        except Exception as e:
            print(f"Plugin initialization failed: {e}")
            return False
    
    def _initialize_ipc(self):
        """Initialize IPC communication channels"""
        # Create shared memory for board state (1MB buffer)
        try:
            self.shared_memory = mp.shared_memory.SharedMemory(
                name="tetris_analyzer_board_state",
                size=1024 * 1024,
                create=True
            )
        except FileExistsError:
            # Attach to existing shared memory
            self.shared_memory = mp.shared_memory.SharedMemory(
                name="tetris_analyzer_board_state"
            )
        
        # Create communication queues
        self.control_channel = mp.Queue()
        self.status_channel = mp.Queue()
    
    def start_analysis(self) -> bool:
        """Start the Tetris analyzer subprocess"""
        if not self.is_initialized:
            print("Error: Plugin not initialized")
            return False
        
        if self.is_running:
            print("Warning: Analyzer already running")
            return True
        
        try:
            # Prepare subprocess command
            cmd = [
                self.config.python_executable,
                self.config.analyzer_script,
                "--verbose",
                "--stats-interval", "10"  # Less frequent stats for plugin mode
            ]
            
            # Start subprocess
            self.process = subprocess.Popen(
                cmd,
                cwd=self.config.working_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.is_running = True
            self.start_time = time.time()
            self.frame_count = 0
            self.error_count = 0
            
            # Start monitoring threads
            self._start_monitoring()
            
            print(f"Tetris Analyzer started (PID: {self.process.pid})")
            
            # Notify Runtime Hub
            if self.on_status_change:
                self.on_status_change("running")
            
            return True
            
        except Exception as e:
            print(f"Failed to start analyzer: {e}")
            return False
    
    def _start_monitoring(self):
        """Start monitoring threads"""
        self.shutdown_event.clear()
        
        # Process monitoring thread
        self.monitor_thread = threading.Thread(
            target=self._monitor_process,
            daemon=True
        )
        self.monitor_thread.start()
        
        # IPC communication thread
        self.ipc_thread = threading.Thread(
            target=self._handle_ipc,
            daemon=True
        )
        self.ipc_thread.start()
    
    def _monitor_process(self):
        """Monitor subprocess health and output"""
        while not self.shutdown_event.is_set() and self.process:
            try:
                # Check if process is still alive
                return_code = self.process.poll()
                if return_code is not None:
                    print(f"Analyzer process exited with code {return_code}")
                    self._handle_process_exit(return_code)
                    break
                
                # Read output (non-blocking)
                if self.process.stdout:
                    line = self.process.stdout.readline()
                    if line:
                        self._process_output(line.strip())
                
                # Update heartbeat
                self.last_heartbeat = time.time()
                
                time.sleep(0.1)  # 10Hz monitoring
                
            except Exception as e:
                print(f"Process monitoring error: {e}")
                self.error_count += 1
                time.sleep(1)
    
    def _handle_ipc(self):
        """Handle IPC communication"""
        while not self.shutdown_event.is_set():
            try:
                # Check for status updates
                if not self.status_channel.empty():
                    message = self.status_channel.get_nowait()
                    self._process_status_message(message)
                
                # Send control commands if needed
                # (Implementation for sending commands to analyzer)
                
                time.sleep(0.05)  # 20Hz IPC
                
            except Exception as e:
                print(f"IPC communication error: {e}")
                time.sleep(1)
    
    def _process_output(self, line: str):
        """Process subprocess output"""
        # Parse different types of output
        if "=== PERFORMANCE STATISTICS ===" in line:
            # Performance stats - could be parsed and forwarded
            pass
        elif "=== MOVE SUGGESTIONS ===" in line:
            # Move suggestions - forward to Runtime Hub
            if self.on_board_update:
                self.on_board_update({"type": "suggestions", "data": line})
        elif "=== COACHING HINTS ===" in line:
            # Coaching hints - forward to Runtime Hub
            if self.on_coaching_update:
                self.on_coaching_update({"type": "hints", "data": line})
        elif line.startswith("Board detected:"):
            # Board detection status
            if self.on_status_change:
                self.on_status_change("board_detected")
        
        self.frame_count += 1
    
    def _process_status_message(self, message: IPCMessage):
        """Process status message from analyzer"""
        if message.type == "board_state":
            # Update shared memory with board state
            if self.shared_memory:
                try:
                    data = json.dumps(message.data).encode('utf-8')
                    self.shared_memory.buf[:len(data)] = data
                except Exception as e:
                    print(f"Failed to update shared memory: {e}")
        
        # Forward to Runtime Hub callbacks
        if message.type == "board_update" and self.on_board_update:
            self.on_board_update(message.data)
        elif message.type == "coaching_update" and self.on_coaching_update:
            self.on_coaching_update(message.data)
    
    def _handle_process_exit(self, return_code: int):
        """Handle subprocess exit"""
        self.is_running = False
        
        if return_code != 0 and self.config.auto_restart:
            print("Attempting to restart analyzer...")
            time.sleep(2)  # Brief delay before restart
            self.start_analysis()
        else:
            print(f"Analyzer stopped (return code: {return_code})")
            if self.on_status_change:
                self.on_status_change("stopped")
    
    def stop_analysis(self) -> bool:
        """Stop the Tetris analyzer subprocess"""
        if not self.is_running:
            return True
        
        try:
            # Signal shutdown
            self.shutdown_event.set()
            
            # Terminate subprocess gracefully
            if self.process:
                self.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    self.process.kill()
                    self.process.wait()
                
                self.process = None
            
            self.is_running = False
            
            print("Tetris Analyzer stopped")
            
            # Notify Runtime Hub
            if self.on_status_change:
                self.on_status_change("stopped")
            
            return True
            
        except Exception as e:
            print(f"Error stopping analyzer: {e}")
            return False
    
    def get_board_state(self) -> Optional[Dict[str, Any]]:
        """Get current board state via IPC"""
        if not self.shared_memory:
            return None
        
        try:
            # Read from shared memory
            data = self.shared_memory.buf.tobytes().rstrip(b'\x00').decode('utf-8')
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Failed to read board state: {e}")
        
        return None
    
    def get_coaching_hints(self) -> Optional[Dict[str, Any]]:
        """Get current coaching hints via IPC"""
        # Send request to analyzer subprocess
        if self.control_channel:
            try:
                request = IPCMessage(
                    type="get_hints",
                    data={},
                    timestamp=time.time()
                )
                self.control_channel.put(request)
                
                # Wait for response (with timeout)
                # Implementation would depend on analyzer's IPC support
                return {"hints": "Coaching hints request sent"}
            except Exception as e:
                print(f"Failed to request coaching hints: {e}")
        
        return None
    
    def get_plugin_status(self) -> Dict[str, Any]:
        """Get plugin status and statistics"""
        uptime = time.time() - self.start_time if self.start_time else 0
        
        return {
            "initialized": self.is_initialized,
            "running": self.is_running,
            "uptime_seconds": uptime,
            "frame_count": self.frame_count,
            "error_count": self.error_count,
            "last_heartbeat": self.last_heartbeat,
            "process_id": self.process.pid if self.process else None,
            "config": {
                "auto_restart": self.config.auto_restart,
                "timeout_seconds": self.config.timeout_seconds
            }
        }
    
    def send_command(self, command: str, params: Dict[str, Any] = None) -> bool:
        """Send command to analyzer subprocess"""
        if not self.is_running or not self.control_channel:
            return False
        
        try:
            message = IPCMessage(
                type=command,
                data=params or {},
                timestamp=time.time()
            )
            self.control_channel.put(message)
            return True
        except Exception as e:
            print(f"Failed to send command: {e}")
            return False
    
    def cleanup(self):
        """Clean up plugin resources"""
        # Stop analyzer
        self.stop_analysis()
        
        # Wait for threads to finish
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        
        if self.ipc_thread and self.ipc_thread.is_alive():
            self.ipc_thread.join(timeout=2)
        
        # Clean up IPC resources
        if self.shared_memory:
            try:
                self.shared_memory.close()
                # Don't unlink - other processes might be using it
            except Exception as e:
                print(f"Error cleaning up shared memory: {e}")
        
        if self.control_channel:
            self.control_channel.close()
        
        if self.status_channel:
            self.status_channel.close()
        
        print("Plugin cleanup complete")
    
    def __del__(self):
        """Destructor"""
        self.cleanup()
