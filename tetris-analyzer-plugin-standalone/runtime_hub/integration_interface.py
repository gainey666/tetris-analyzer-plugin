"""
Runtime Hub Integration Interface for Tetris Analyzer

This module provides the main integration interface that Runtime Hub uses
to interact with the Tetris analyzer plugin.
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
import time
import threading
from .plugin_wrapper import TetrisAnalyzerPlugin, PluginConfig
from .ipc_bridge import IPCBridge


@dataclass
class RuntimeHubConfig:
    """Runtime Hub integration configuration"""
    auto_start: bool = True
    auto_restart: bool = True
    log_level: str = "INFO"
    performance_monitoring: bool = True
    coaching_enabled: bool = True
    prediction_enabled: bool = True


@dataclass
class AnalyzerStatus:
    """Analyzer status information"""
    is_running: bool
    is_initialized: bool
    uptime_seconds: float
    board_detected: bool
    current_fps: float
    accuracy: float
    last_update: float


class TetrisAnalyzerRuntimeHub:
    """Main Runtime Hub integration interface"""
    
    def __init__(self, config: Optional[RuntimeHubConfig] = None):
        """Initialize Runtime Hub integration"""
        self.config = config or RuntimeHubConfig()
        
        # Core components
        self.plugin: Optional[TetrisAnalyzerPlugin] = None
        self.ipc_bridge: Optional[IPCBridge] = None
        
        # State tracking
        self.current_status = AnalyzerStatus(
            is_running=False,
            is_initialized=False,
            uptime_seconds=0.0,
            board_detected=False,
            current_fps=0.0,
            accuracy=0.0,
            last_update=0.0
        )
        
        # Event callbacks for Runtime Hub
        self.on_status_changed: Optional[Callable[[AnalyzerStatus], None]] = None
        self.on_board_detected: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_coaching_hint: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_performance_update: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_error: Optional[Callable[[str, Exception], None]] = None
        
        # Internal state
        self.is_hub_connected = False
        self.start_time: Optional[float] = None
        self.last_heartbeat: Optional[float] = None
        
        # Thread management
        self.status_thread: Optional[threading.Thread] = None
        self.shutdown_event = threading.Event()
    
    def initialize(self) -> bool:
        """Initialize Runtime Hub integration"""
        try:
            print("Initializing Tetris Analyzer Runtime Hub integration...")
            
            # Initialize IPC bridge first
            self.ipc_bridge = IPCBridge("tetris_analyzer_hub")
            if not self.ipc_bridge.initialize():
                raise Exception("Failed to initialize IPC bridge")
            
            # Setup IPC callbacks
            self.ipc_bridge.on_board_update = self._on_board_update
            self.ipc_bridge.on_coaching_update = self._on_coaching_update
            self.ipc_bridge.on_performance_update = self._on_performance_update
            
            # Initialize plugin wrapper
            plugin_config = PluginConfig(
                auto_restart=self.config.auto_restart,
                timeout_seconds=30
            )
            self.plugin = TetrisAnalyzerPlugin(plugin_config)
            
            # Setup plugin callbacks
            self.plugin.on_status_change = self._on_plugin_status_change
            self.plugin.on_board_update = self._on_plugin_board_update
            self.plugin.on_coaching_update = self._on_plugin_coaching_update
            
            # Initialize plugin
            if not self.plugin.initialize():
                raise Exception("Failed to initialize plugin wrapper")
            
            # Start status monitoring thread
            self._start_status_monitoring()
            
            self.is_hub_connected = True
            self.start_time = time.time()
            
            print("Tetris Analyzer Runtime Hub integration initialized successfully")
            return True
            
        except Exception as e:
            print(f"Failed to initialize Runtime Hub integration: {e}")
            if self.on_error:
                self.on_error("initialization_failed", e)
            return False
    
    def start_analyzer(self) -> bool:
        """Start the Tetris analyzer"""
        if not self.plugin:
            print("Error: Plugin not initialized")
            return False
        
        try:
            success = self.plugin.start_analysis()
            if success:
                print("Tetris analyzer started successfully")
                self._update_status()
            return success
        except Exception as e:
            print(f"Failed to start analyzer: {e}")
            if self.on_error:
                self.on_error("start_failed", e)
            return False
    
    def stop_analyzer(self) -> bool:
        """Stop the Tetris analyzer"""
        if not self.plugin:
            return True
        
        try:
            success = self.plugin.stop_analysis()
            if success:
                print("Tetris analyzer stopped successfully")
                self._update_status()
            return success
        except Exception as e:
            print(f"Failed to stop analyzer: {e}")
            if self.on_error:
                self.on_error("stop_failed", e)
            return False
    
    def get_board_state(self) -> Optional[Dict[str, Any]]:
        """Get current board state"""
        if not self.ipc_bridge:
            return None
        
        try:
            # Send command to get board state
            seq_id = self.ipc_bridge.send_command("get_board_state")
            if seq_id > 0:
                response = self.ipc_bridge.get_response(seq_id, timeout=2.0)
                if response and response.get("status") == "success":
                    return response.get("data")
        except Exception as e:
            print(f"Failed to get board state: {e}")
        
        return None
    
    def get_coaching_hints(self) -> Optional[List[Dict[str, Any]]]:
        """Get current coaching hints"""
        if not self.ipc_bridge or not self.config.coaching_enabled:
            return None
        
        try:
            seq_id = self.ipc_bridge.send_command("get_coaching_hints")
            if seq_id > 0:
                response = self.ipc_bridge.get_response(seq_id, timeout=2.0)
                if response and response.get("status") == "success":
                    return response.get("data", {}).get("hints", [])
        except Exception as e:
            print(f"Failed to get coaching hints: {e}")
        
        return None
    
    def get_performance_metrics(self) -> Optional[Dict[str, Any]]:
        """Get current performance metrics"""
        if not self.ipc_bridge or not self.config.performance_monitoring:
            return None
        
        try:
            seq_id = self.ipc_bridge.send_command("get_performance")
            if seq_id > 0:
                response = self.ipc_bridge.get_response(seq_id, timeout=1.0)
                if response and response.get("status") == "success":
                    return response.get("data")
        except Exception as e:
            print(f"Failed to get performance metrics: {e}")
        
        return None
    
    def update_configuration(self, config_updates: Dict[str, Any]) -> bool:
        """Update analyzer configuration"""
        if not self.ipc_bridge:
            return False
        
        try:
            seq_id = self.ipc_bridge.send_command("set_config", config_updates)
            if seq_id > 0:
                response = self.ipc_bridge.get_response(seq_id, timeout=3.0)
                return response and response.get("status") == "success"
        except Exception as e:
            print(f"Failed to update configuration: {e}")
        
        return False
    
    def get_status(self) -> AnalyzerStatus:
        """Get current analyzer status"""
        self._update_status()
        return self.current_status
    
    def _update_status(self):
        """Update internal status"""
        try:
            if self.plugin:
                plugin_status = self.plugin.get_plugin_status()
                
                # Get performance metrics
                perf_metrics = self.get_performance_metrics()
                
                self.current_status = AnalyzerStatus(
                    is_running=plugin_status.get("running", False),
                    is_initialized=plugin_status.get("initialized", False),
                    uptime_seconds=plugin_status.get("uptime_seconds", 0.0),
                    board_detected=plugin_status.get("board_detected", False),
                    current_fps=perf_metrics.get("fps", 0.0) if perf_metrics else 0.0,
                    accuracy=perf_metrics.get("accuracy", 0.0) if perf_metrics else 0.0,
                    last_update=time.time()
                )
                
                # Notify Runtime Hub of status change
                if self.on_status_changed:
                    self.on_status_changed(self.current_status)
        
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def _start_status_monitoring(self):
        """Start status monitoring thread"""
        self.shutdown_event.clear()
        self.status_thread = threading.Thread(
            target=self._status_monitoring_loop,
            daemon=True
        )
        self.status_thread.start()
    
    def _status_monitoring_loop(self):
        """Status monitoring loop"""
        while not self.shutdown_event.is_set():
            try:
                self._update_status()
                self.last_heartbeat = time.time()
                time.sleep(1.0)  # Update status every second
            except Exception as e:
                print(f"Status monitoring error: {e}")
                time.sleep(5.0)
    
    def _on_plugin_status_change(self, status: str):
        """Handle plugin status change"""
        print(f"Plugin status changed: {status}")
        self._update_status()
        
        if status == "board_detected" and self.on_board_detected:
            board_state = self.get_board_state()
            if board_state:
                self.on_board_detected(board_state)
    
    def _on_plugin_board_update(self, data: Dict[str, Any]):
        """Handle plugin board update"""
        # Forward to IPC bridge
        if self.ipc_bridge:
            self.ipc_bridge.send_event("board_update", data)
    
    def _on_plugin_coaching_update(self, data: Dict[str, Any]):
        """Handle plugin coaching update"""
        # Forward to IPC bridge and Runtime Hub
        if self.ipc_bridge:
            self.ipc_bridge.send_event("coaching_update", data)
        
        if self.on_coaching_hint:
            self.on_coaching_hint(data)
    
    def _on_board_update(self, data: Dict[str, Any]):
        """Handle IPC board update"""
        # Forward to Runtime Hub
        if self.on_board_detected:
            self.on_board_detected(data)
    
    def _on_coaching_update(self, data: Dict[str, Any]):
        """Handle IPC coaching update"""
        # Forward to Runtime Hub
        if self.on_coaching_hint:
            self.on_coaching_hint(data)
    
    def _on_performance_update(self, data: Dict[str, Any]):
        """Handle IPC performance update"""
        # Forward to Runtime Hub
        if self.on_performance_update:
            self.on_performance_update(data)
    
    def get_integration_info(self) -> Dict[str, Any]:
        """Get integration information for Runtime Hub"""
        return {
            "plugin_name": "Tetris Analyzer",
            "version": "1.0.0",
            "is_connected": self.is_hub_connected,
            "uptime": time.time() - self.start_time if self.start_time else 0,
            "last_heartbeat": self.last_heartbeat,
            "config": {
                "auto_start": self.config.auto_start,
                "auto_restart": self.config.auto_restart,
                "coaching_enabled": self.config.coaching_enabled,
                "prediction_enabled": self.config.prediction_enabled
            },
            "ipc_status": self.ipc_bridge.get_status() if self.ipc_bridge else None,
            "plugin_status": self.plugin.get_plugin_status() if self.plugin else None
        }
    
    def shutdown(self):
        """Shutdown Runtime Hub integration"""
        print("Shutting down Tetris Analyzer Runtime Hub integration...")
        
        # Signal shutdown
        self.shutdown_event.set()
        
        # Stop analyzer
        if self.plugin:
            self.plugin.stop_analysis()
        
        # Wait for status thread
        if self.status_thread and self.status_thread.is_alive():
            self.status_thread.join(timeout=3)
        
        # Cleanup plugin
        if self.plugin:
            self.plugin.cleanup()
        
        # Shutdown IPC bridge
        if self.ipc_bridge:
            self.ipc_bridge.shutdown()
        
        self.is_hub_connected = False
        print("Runtime Hub integration shutdown complete")
    
    def __del__(self):
        """Destructor"""
        self.shutdown()
