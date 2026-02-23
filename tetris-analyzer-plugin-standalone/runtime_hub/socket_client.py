"""
Runtime Hub Socket.IO Client for Tetris Analyzer

This module provides Socket.IO client integration to communicate with
Runtime Hub's server following their established architecture.
"""

import socketio
import json
import time
import threading
from typing import Dict, Any, Optional, Callable
import logging
from .integration_interface import TetrisAnalyzerRuntimeHub, RuntimeHubConfig


class RuntimeHubSocketClient:
    """Socket.IO client for Runtime Hub integration"""
    
    def __init__(self, hub_url: str = "http://localhost:3000"):
        """Initialize Socket.IO client"""
        self.hub_url = hub_url
        self.sio = socketio.Client()
        self.integration: Optional[TetrisAnalyzerRuntimeHub] = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
        # Event callbacks
        self.on_connect_callback: Optional[Callable] = None
        self.on_disconnect_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None
        
        # Setup Socket.IO event handlers
        self._setup_socket_handlers()
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    def _setup_socket_handlers(self):
        """Setup Socket.IO event handlers"""
        
        @self.sio.event
        def connect():
            """Handle connection to Runtime Hub"""
            self.connected = True
            self.reconnect_attempts = 0
            self.logger.info("Connected to Runtime Hub")
            
            # Register Tetris analyzer plugin
            self._register_plugin()
            
            if self.on_connect_callback:
                self.on_connect_callback()
        
        @self.sio.event
        def disconnect():
            """Handle disconnection from Runtime Hub"""
            self.connected = False
            self.logger.warning("Disconnected from Runtime Hub")
            
            if self.on_disconnect_callback:
                self.on_disconnect_callback()
        
        @self.sio.event
        def connect_error(data):
            """Handle connection error"""
            self.logger.error(f"Runtime Hub connection error: {data}")
            self.reconnect_attempts += 1
            
            if self.reconnect_attempts <= self.max_reconnect_attempts:
                self.logger.info(f"Attempting reconnect {self.reconnect_attempts}/{self.max_reconnect_attempts}")
                time.sleep(2 ** self.reconnect_attempts)  # Exponential backoff
            else:
                self.logger.error("Max reconnect attempts reached")
                
            if self.on_error_callback:
                self.on_error_callback(data)
        
        @self.sio.event
        def start_analysis(data):
            """Handle start analysis command from Runtime Hub"""
            self.logger.info("Received start_analysis command")
            if self.integration:
                self.integration.start_analyzer()
                self._emit_status("analysis_started")
        
        @self.sio.event
        def stop_analysis(data):
            """Handle stop analysis command from Runtime Hub"""
            self.logger.info("Received stop_analysis command")
            if self.integration:
                self.integration.stop_analyzer()
                self._emit_status("analysis_stopped")
        
        @self.sio.event
        def get_status(data):
            """Handle get status command from Runtime Hub"""
            if self.integration:
                status = self.integration.get_status()
                self.sio.emit('status_response', {
                    'is_running': status.is_running,
                    'is_initialized': status.is_initialized,
                    'uptime_seconds': status.uptime_seconds,
                    'board_detected': status.board_detected,
                    'current_fps': status.current_fps,
                    'accuracy': status.accuracy,
                    'timestamp': time.time()
                })
        
        @self.sio.event
        def get_board_state(data):
            """Handle get board state command from Runtime Hub"""
            if self.integration:
                board_state = self.integration.get_board_state()
                self.sio.emit('board_state_response', {
                    'board_state': board_state,
                    'timestamp': time.time()
                })
        
        @self.sio.event
        def get_coaching_hints(data):
            """Handle get coaching hints command from Runtime Hub"""
            if self.integration:
                hints = self.integration.get_coaching_hints()
                self.sio.emit('coaching_hints_response', {
                    'hints': hints or [],
                    'timestamp': time.time()
                })
        
        @self.sio.event
        def update_config(data):
            """Handle configuration update from Runtime Hub"""
            self.logger.info(f"Received config update: {data}")
            if self.integration:
                success = self.integration.update_configuration(data)
                self.sio.emit('config_update_response', {
                    'success': success,
                    'timestamp': time.time()
                })
    
    def _register_plugin(self):
        """Register Tetris analyzer plugin with Runtime Hub"""
        plugin_info = {
            'name': 'Tetris Analyzer',
            'version': '1.0.0',
            'description': 'Real-time Tetris game analysis with move predictions and coaching',
            'category': 'Python',
            'capabilities': [
                'board_detection',
                'piece_recognition', 
                'move_prediction',
                'coaching_hints',
                'performance_monitoring'
            ],
            'endpoints': {
                'start_analysis': 'start_analysis',
                'stop_analysis': 'stop_analysis',
                'get_status': 'get_status',
                'get_board_state': 'get_board_state',
                'get_coaching_hints': 'get_coaching_hints',
                'update_config': 'update_config'
            }
        }
        
        self.sio.emit('register_plugin', plugin_info)
        self.logger.info("Registered Tetris analyzer plugin with Runtime Hub")
    
    def connect(self, integration: TetrisAnalyzerRuntimeHub) -> bool:
        """Connect to Runtime Hub"""
        self.integration = integration
        
        # Setup integration callbacks to forward events
        integration.on_status_changed = self._on_status_changed
        integration.on_board_detected = self._on_board_detected
        integration.on_coaching_hint = self._on_coaching_hint
        integration.on_performance_update = self._on_performance_update
        integration.on_error = self._on_integration_error
        
        try:
            self.sio.connect(self.hub_url)
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Runtime Hub: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Runtime Hub"""
        if self.connected:
            self.sio.disconnect()
    
    def _on_status_changed(self, status):
        """Forward status change to Runtime Hub"""
        if self.connected:
            self._emit_status("status_changed", {
                'is_running': status.is_running,
                'is_initialized': status.is_initialized,
                'uptime_seconds': status.uptime_seconds,
                'board_detected': status.board_detected,
                'current_fps': status.current_fps,
                'accuracy': status.accuracy
            })
    
    def _on_board_detected(self, board_data):
        """Forward board detection to Runtime Hub"""
        if self.connected:
            self.sio.emit('board_update', {
                'board_data': board_data,
                'timestamp': time.time()
            })
    
    def _on_coaching_hint(self, hint_data):
        """Forward coaching hint to Runtime Hub"""
        if self.connected:
            self.sio.emit('coaching_hint', {
                'hint_data': hint_data,
                'timestamp': time.time()
            })
    
    def _on_performance_update(self, perf_data):
        """Forward performance update to Runtime Hub"""
        if self.connected:
            self.sio.emit('performance_update', {
                'performance_data': perf_data,
                'timestamp': time.time()
            })
    
    def _on_integration_error(self, error_type, error):
        """Forward error to Runtime Hub"""
        if self.connected:
            self.sio.emit('error', {
                'error_type': error_type,
                'error_message': str(error),
                'timestamp': time.time()
            })
    
    def _emit_status(self, status_type: str, data: Dict[str, Any] = None):
        """Emit status event to Runtime Hub"""
        if self.connected:
            self.sio.emit('status', {
                'status_type': status_type,
                'data': data or {},
                'timestamp': time.time()
            })
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get connection status"""
        return {
            'connected': self.connected,
            'hub_url': self.hub_url,
            'reconnect_attempts': self.reconnect_attempts,
            'sid': self.sio.sid if self.connected else None
        }
