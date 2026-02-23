"""
HTTP API Server for Tetris Analyzer Runtime Hub Integration

This module provides a REST API server that Runtime Hub can use to control
the Tetris analyzer following their architecture standards.
"""

from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import threading
import time
import logging
from typing import Dict, Any, Optional
from .integration_interface import TetrisAnalyzerRuntimeHub, RuntimeHubConfig


class TetrisAnalyzerAPIServer:
    """HTTP API server for Runtime Hub integration"""
    
    def __init__(self, port: int = 3002, integration: Optional[TetrisAnalyzerRuntimeHub] = None):
        """Initialize API server"""
        self.port = port
        self.integration = integration
        self.app = Flask(__name__)
        self.server_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Setup CORS for Runtime Hub
        CORS(self.app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'service': 'tetris-analyzer-api',
                'timestamp': time.time(),
                'version': '1.0.0'
            })
        
        @self.app.route('/info', methods=['GET'])
        def get_info():
            """Get service information"""
            return jsonify({
                'name': 'Tetris Analyzer API',
                'version': '1.0.0',
                'description': 'HTTP API for Tetris analyzer control',
                'endpoints': self._get_endpoints_info(),
                'capabilities': [
                    'board_detection',
                    'piece_recognition',
                    'move_prediction', 
                    'coaching_hints',
                    'performance_monitoring'
                ]
            })
        
        @self.app.route('/status', methods=['GET'])
        def get_status():
            """Get current analyzer status"""
            if not self.integration:
                return jsonify({'error': 'Integration not initialized'}), 503
            
            try:
                status = self.integration.get_status()
                return jsonify({
                    'is_running': status.is_running,
                    'is_initialized': status.is_initialized,
                    'uptime_seconds': status.uptime_seconds,
                    'board_detected': status.board_detected,
                    'current_fps': status.current_fps,
                    'accuracy': status.accuracy,
                    'last_update': status.last_update
                })
            except Exception as e:
                self.logger.error(f"Error getting status: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/start', methods=['POST'])
        def start_analysis():
            """Start Tetris analysis"""
            if not self.integration:
                return jsonify({'error': 'Integration not initialized'}), 503
            
            try:
                success = self.integration.start_analyzer()
                if success:
                    return jsonify({
                        'status': 'started',
                        'timestamp': time.time()
                    })
                else:
                    return jsonify({'error': 'Failed to start analyzer'}), 500
            except Exception as e:
                self.logger.error(f"Error starting analyzer: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/stop', methods=['POST'])
        def stop_analysis():
            """Stop Tetris analysis"""
            if not self.integration:
                return jsonify({'error': 'Integration not initialized'}), 503
            
            try:
                success = self.integration.stop_analyzer()
                if success:
                    return jsonify({
                        'status': 'stopped',
                        'timestamp': time.time()
                    })
                else:
                    return jsonify({'error': 'Failed to stop analyzer'}), 500
            except Exception as e:
                self.logger.error(f"Error stopping analyzer: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/board', methods=['GET'])
        def get_board_state():
            """Get current board state"""
            if not self.integration:
                return jsonify({'error': 'Integration not initialized'}), 503
            
            try:
                board_state = self.integration.get_board_state()
                return jsonify({
                    'board_state': board_state,
                    'timestamp': time.time()
                })
            except Exception as e:
                self.logger.error(f"Error getting board state: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/hints', methods=['GET'])
        def get_coaching_hints():
            """Get current coaching hints"""
            if not self.integration:
                return jsonify({'error': 'Integration not initialized'}), 503
            
            try:
                hints = self.integration.get_coaching_hints()
                return jsonify({
                    'hints': hints or [],
                    'count': len(hints) if hints else 0,
                    'timestamp': time.time()
                })
            except Exception as e:
                self.logger.error(f"Error getting coaching hints: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/performance', methods=['GET'])
        def get_performance_metrics():
            """Get performance metrics"""
            if not self.integration:
                return jsonify({'error': 'Integration not initialized'}), 503
            
            try:
                metrics = self.integration.get_performance_metrics()
                return jsonify({
                    'metrics': metrics,
                    'timestamp': time.time()
                })
            except Exception as e:
                self.logger.error(f"Error getting performance metrics: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/config', methods=['GET'])
        def get_config():
            """Get current configuration"""
            if not self.integration:
                return jsonify({'error': 'Integration not initialized'}), 503
            
            try:
                info = self.integration.get_integration_info()
                return jsonify({
                    'config': info.get('config', {}),
                    'timestamp': time.time()
                })
            except Exception as e:
                self.logger.error(f"Error getting config: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/config', methods=['POST'])
        def update_config():
            """Update configuration"""
            if not self.integration:
                return jsonify({'error': 'Integration not initialized'}), 503
            
            try:
                config_data = request.get_json()
                if not config_data:
                    return jsonify({'error': 'No configuration data provided'}), 400
                
                success = self.integration.update_configuration(config_data)
                if success:
                    return jsonify({
                        'status': 'updated',
                        'config': config_data,
                        'timestamp': time.time()
                    })
                else:
                    return jsonify({'error': 'Failed to update configuration'}), 500
            except Exception as e:
                self.logger.error(f"Error updating config: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/calibrate', methods=['POST'])
        def run_calibration():
            """Run board calibration"""
            if not self.integration:
                return jsonify({'error': 'Integration not initialized'}), 503
            
            try:
                # This would trigger calibration in the analyzer
                # Implementation depends on the analyzer's calibration interface
                return jsonify({
                    'status': 'calibration_started',
                    'message': 'Calibration initiated',
                    'timestamp': time.time()
                })
            except Exception as e:
                self.logger.error(f"Error running calibration: {e}")
                return jsonify({'error': str(e)}), 500
        
        # Error handlers
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Endpoint not found'}), 404
        
        @self.app.errorhandler(405)
        def method_not_allowed(error):
            return jsonify({'error': 'Method not allowed'}), 405
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({'error': 'Internal server error'}), 500
    
    def _get_endpoints_info(self) -> Dict[str, Any]:
        """Get information about available endpoints"""
        return {
            'GET /health': 'Health check',
            'GET /info': 'Service information',
            'GET /status': 'Current analyzer status',
            'POST /start': 'Start analysis',
            'POST /stop': 'Stop analysis',
            'GET /board': 'Get board state',
            'GET /hints': 'Get coaching hints',
            'GET /performance': 'Get performance metrics',
            'GET /config': 'Get configuration',
            'POST /config': 'Update configuration',
            'POST /calibrate': 'Run calibration'
        }
    
    def set_integration(self, integration: TetrisAnalyzerRuntimeHub):
        """Set the integration instance"""
        self.integration = integration
    
    def start_server(self) -> bool:
        """Start the API server"""
        if self.running:
            self.logger.warning("Server already running")
            return True
        
        try:
            self.server_thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )
            self.server_thread.start()
            
            # Wait a moment for server to start
            time.sleep(0.5)
            
            self.running = True
            self.logger.info(f"API server started on port {self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            return False
    
    def _run_server(self):
        """Run the Flask server"""
        try:
            self.app.run(
                host='127.0.0.1',
                port=self.port,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        except Exception as e:
            self.logger.error(f"Server error: {e}")
    
    def stop_server(self):
        """Stop the API server"""
        if not self.running:
            return
        
        self.running = False
        
        # Note: Flask doesn't provide clean shutdown from another thread
        # In production, you'd want to use a proper WSGI server
        self.logger.info("API server stop requested")
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get server status"""
        return {
            'running': self.running,
            'port': self.port,
            'url': f'http://127.0.0.1:{self.port}',
            'endpoints_count': len(self._get_endpoints_info()),
            'integration_available': self.integration is not None
        }
