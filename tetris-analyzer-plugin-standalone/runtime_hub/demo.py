"""
Runtime Hub Integration Demo

This demonstrates how to use the Tetris analyzer plugin within Runtime Hub.
"""

import time
import threading
from runtime_hub.integration_interface import TetrisAnalyzerRuntimeHub, RuntimeHubConfig, AnalyzerStatus


class RuntimeHubDemo:
    """Demo Runtime Hub integration"""
    
    def __init__(self):
        """Initialize demo"""
        self.integration = None
        self.running = False
        self.demo_thread = None
        
        # Setup callbacks
        self.setup_callbacks()
    
    def setup_callbacks(self):
        """Setup Runtime Hub callbacks"""
        self.on_status_changed = self._on_status_changed
        self.on_board_detected = self._on_board_detected
        self.on_coaching_hint = self._on_coaching_hint
        self.on_performance_update = self._on_performance_update
        self.on_error = self._on_error
    
    def start_demo(self):
        """Start the demo"""
        print("🎮 Starting Tetris Analyzer Runtime Hub Demo")
        print("=" * 50)
        
        # Initialize integration
        config = RuntimeHubConfig(
            auto_start=False,  # We'll start manually
            auto_restart=True,
            coaching_enabled=True,
            prediction_enabled=True,
            performance_monitoring=True
        )
        
        self.integration = TetrisAnalyzerRuntimeHub(config)
        
        # Set callbacks
        self.integration.on_status_changed = self.on_status_changed
        self.integration.on_board_detected = self.on_board_detected
        self.integration.on_coaching_hint = self.on_coaching_hint
        self.integration.on_performance_update = self.on_performance_update
        self.integration.on_error = self.on_error
        
        # Initialize
        if not self.integration.initialize():
            print("❌ Failed to initialize integration")
            return
        
        print("✅ Integration initialized successfully")
        
        # Start demo thread
        self.running = True
        self.demo_thread = threading.Thread(target=self._demo_loop, daemon=True)
        self.demo_thread.start()
        
        # Start analyzer
        print("\n🚀 Starting Tetris analyzer...")
        if self.integration.start_analyzer():
            print("✅ Analyzer started successfully")
        else:
            print("❌ Failed to start analyzer")
        
        # Run demo for specified time
        try:
            time.sleep(30)  # Run for 30 seconds
        except KeyboardInterrupt:
            print("\n⏹️ Demo interrupted")
        
        # Stop demo
        self.stop_demo()
    
    def stop_demo(self):
        """Stop the demo"""
        print("\n🛑 Stopping demo...")
        
        self.running = False
        
        if self.integration:
            # Stop analyzer
            print("⏹️ Stopping analyzer...")
            self.integration.stop_analyzer()
            
            # Shutdown integration
            print("🔌 Shutting down integration...")
            self.integration.shutdown()
        
        # Wait for demo thread
        if self.demo_thread and self.demo_thread.is_alive():
            self.demo_thread.join(timeout=5)
        
        print("✅ Demo stopped")
    
    def _demo_loop(self):
        """Main demo loop"""
        while self.running:
            try:
                # Get current status
                status = self.integration.get_status()
                
                # Get board state
                board_state = self.integration.get_board_state()
                
                # Get coaching hints
                hints = self.integration.get_coaching_hints()
                
                # Get performance metrics
                metrics = self.integration.get_performance_metrics()
                
                # Print summary every 5 seconds
                if int(time.time()) % 5 == 0:
                    self._print_demo_summary(status, board_state, hints, metrics)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Demo loop error: {e}")
                time.sleep(1)
    
    def _print_demo_summary(self, status: AnalyzerStatus, board_state, hints, metrics):
        """Print demo summary"""
        print(f"\n📊 Demo Summary - {time.strftime('%H:%M:%S')}")
        print(f"   Status: {'🟢 Running' if status.is_running else '🔴 Stopped'}")
        print(f"   Board Detected: {'✅' if status.board_detected else '❌'}")
        print(f"   FPS: {status.current_fps:.1f}")
        print(f"   Accuracy: {status.accuracy:.1%}")
        print(f"   Uptime: {status.uptime_seconds:.1f}s")
        
        if board_state:
            print(f"   Board: {len(board_state.get('board', []))} pieces")
        
        if hints:
            print(f"   Hints: {len(hints)} available")
        
        if metrics:
            print(f"   Performance: {metrics.get('fps', 0):.1f} FPS, {metrics.get('latency', 0):.1f}ms latency")
    
    def _on_status_changed(self, status: AnalyzerStatus):
        """Handle status change"""
        print(f"🔄 Status changed: {'Running' if status.is_running else 'Stopped'}")
    
    def _on_board_detected(self, board_data: dict):
        """Handle board detection"""
        print(f"🎯 Board detected: {len(board_data.get('board', []))} pieces")
    
    def _on_coaching_hint(self, hint_data: dict):
        """Handle coaching hint"""
        hint_type = hint_data.get('type', 'unknown')
        message = hint_data.get('message', 'No message')
        print(f"💡 Coaching [{hint_type}]: {message}")
    
    def _on_performance_update(self, perf_data: dict):
        """Handle performance update"""
        fps = perf_data.get('fps', 0)
        latency = perf_data.get('latency', 0)
        if fps > 0:
            print(f"⚡ Performance: {fps:.1f} FPS, {latency:.1f}ms latency")
    
    def _on_error(self, error_type: str, error: Exception):
        """Handle error"""
        print(f"❌ Error [{error_type}]: {error}")


def main():
    """Main demo function"""
    print("🎮 Tetris Analyzer Runtime Hub Integration Demo")
    print("This demo shows how the plugin integrates with Runtime Hub")
    print()
    
    demo = RuntimeHubDemo()
    
    try:
        demo.start_demo()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    finally:
        demo.stop_demo()
    
    print("\n👋 Demo complete!")


if __name__ == "__main__":
    main()
