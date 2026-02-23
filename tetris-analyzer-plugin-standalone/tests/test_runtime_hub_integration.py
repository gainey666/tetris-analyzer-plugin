"""
Test suite for Runtime Hub Integration

Tests the plugin wrapper, IPC bridge, and integration interface.
"""

import unittest
import time
import threading
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from runtime_hub.plugin_wrapper import TetrisAnalyzerPlugin, PluginConfig
from runtime_hub.ipc_bridge import IPCBridge, IPCPacket
from runtime_hub.integration_interface import TetrisAnalyzerRuntimeHub, RuntimeHubConfig


class TestPluginWrapper(unittest.TestCase):
    """Test cases for Plugin Wrapper"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = PluginConfig(
            auto_restart=False,  # Disable for testing
            timeout_seconds=5
        )
        self.plugin = TetrisAnalyzerPlugin(self.config)
    
    def tearDown(self):
        """Clean up after tests"""
        if self.plugin:
            self.plugin.cleanup()
    
    def test_initialization(self):
        """Test plugin initialization"""
        result = self.plugin.initialize()
        self.assertTrue(result)
        self.assertTrue(self.plugin.is_initialized)
    
    def test_get_plugin_status(self):
        """Test plugin status retrieval"""
        self.plugin.initialize()
        status = self.plugin.get_plugin_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("initialized", status)
        self.assertIn("running", status)
        self.assertIn("uptime_seconds", status)
        self.assertTrue(status["initialized"])
        self.assertFalse(status["running"])
    
    def test_send_command(self):
        """Test command sending"""
        self.plugin.initialize()
        result = self.plugin.send_command("ping")
        self.assertFalse(result)  # Should fail when not running
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = PluginConfig(
            python_executable="fake_python",
            analyzer_script="nonexistent.py"
        )
        plugin = TetrisAnalyzerPlugin(config)
        result = plugin.initialize()
        self.assertFalse(result)
        plugin.cleanup()


class TestIPCBridge(unittest.TestCase):
    """Test cases for IPC Bridge"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bridge_name = "test_tetris_analyzer"
        self.bridge = IPCBridge(self.bridge_name)
    
    def tearDown(self):
        """Clean up after tests"""
        if self.bridge:
            self.bridge.shutdown()
    
    def test_initialization(self):
        """Test IPC bridge initialization"""
        result = self.bridge.initialize()
        self.assertTrue(result)
        self.assertTrue(self.bridge.running)
        self.assertGreater(self.bridge.socket_port, 0)
    
    def test_send_command(self):
        """Test command sending"""
        self.bridge.initialize()
        seq_id = self.bridge.send_command("ping")
        self.assertGreater(seq_id, 0)
    
    def test_get_status(self):
        """Test status retrieval"""
        self.bridge.initialize()
        status = self.bridge.get_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("running", status)
        self.assertIn("socket_port", status)
        self.assertTrue(status["running"])
    
    def test_packet_serialization(self):
        """Test packet serialization/deserialization"""
        packet = IPCPacket(
            packet_type="test",
            data={"message": "hello"},
            timestamp=time.time(),
            sequence_id=1
        )
        
        # Serialize
        serialized = self.bridge._serialize_packet(packet)
        self.assertIsInstance(serialized, bytes)
        
        # Deserialize
        deserialized = self.bridge._deserialize_packet(serialized)
        self.assertEqual(deserialized.packet_type, packet.packet_type)
        self.assertEqual(deserialized.data, packet.data)
        self.assertEqual(deserialized.sequence_id, packet.sequence_id)


class TestIntegrationInterface(unittest.TestCase):
    """Test cases for Integration Interface"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = RuntimeHubConfig(
            auto_start=False,
            auto_restart=False
        )
        self.integration = TetrisAnalyzerRuntimeHub(self.config)
    
    def tearDown(self):
        """Clean up after tests"""
        if self.integration:
            self.integration.shutdown()
    
    def test_initialization(self):
        """Test integration initialization"""
        result = self.integration.initialize()
        self.assertTrue(result)
        self.assertTrue(self.integration.is_hub_connected)
    
    def test_get_status(self):
        """Test status retrieval"""
        self.integration.initialize()
        status = self.integration.get_status()
        
        self.assertIsInstance(status, status.__class__)
        self.assertFalse(status.is_running)  # Should not be running initially
        self.assertTrue(status.is_initialized)
    
    def test_get_integration_info(self):
        """Test integration info retrieval"""
        self.integration.initialize()
        info = self.integration.get_integration_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn("plugin_name", info)
        self.assertIn("version", info)
        self.assertIn("is_connected", info)
        self.assertEqual(info["plugin_name"], "Tetris Analyzer")
        self.assertTrue(info["is_connected"])
    
    def test_callbacks(self):
        """Test callback functionality"""
        self.integration.initialize()
        
        # Mock callbacks
        status_callback = Mock()
        board_callback = Mock()
        coaching_callback = Mock()
        
        self.integration.on_status_changed = status_callback
        self.integration.on_board_detected = board_callback
        self.integration.on_coaching_hint = coaching_callback
        
        # Trigger status update
        self.integration._update_status()
        
        # Check if callback was called
        status_callback.assert_called_once()
    
    @patch('subprocess.Popen')
    def test_start_analyzer(self, mock_popen):
        """Test analyzer startup"""
        # Mock subprocess
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        self.integration.initialize()
        result = self.integration.start_analyzer()
        
        # Should succeed with mocked subprocess
        self.assertTrue(result)
        mock_popen.assert_called_once()
    
    def test_configuration_update(self):
        """Test configuration updates"""
        self.integration.initialize()
        
        config_updates = {
            "coaching_enabled": False,
            "prediction_enabled": True
        }
        
        result = self.integration.update_configuration(config_updates)
        # Should succeed even without running analyzer
        self.assertTrue(result)


class TestEndToEndIntegration(unittest.TestCase):
    """End-to-end integration tests"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.integration = TetrisAnalyzerRuntimeHub(
            RuntimeHubConfig(auto_start=False, auto_restart=False)
        )
    
    def tearDown(self):
        """Clean up after tests"""
        if self.integration:
            self.integration.shutdown()
    
    def test_full_integration_flow(self):
        """Test complete integration flow"""
        # Initialize
        self.assertTrue(self.integration.initialize())
        self.assertTrue(self.integration.is_hub_connected)
        
        # Check initial status
        status = self.integration.get_status()
        self.assertFalse(status.is_running)
        self.assertTrue(status.is_initialized)
        
        # Get integration info
        info = self.integration.get_integration_info()
        self.assertEqual(info["plugin_name"], "Tetris Analyzer")
        self.assertTrue(info["is_connected"])
        
        # Test configuration
        config_result = self.integration.update_configuration({
            "coaching_enabled": True,
            "performance_monitoring": True
        })
        self.assertTrue(config_result)
        
        # Shutdown
        self.integration.shutdown()
        self.assertFalse(self.integration.is_hub_connected)


if __name__ == '__main__':
    unittest.main()
