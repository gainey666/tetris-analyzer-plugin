"""
IPC Communication Bridge for Tetris Analyzer

This module provides the communication layer between the Runtime Hub plugin
and the standalone Tetris analyzer subprocess.
"""

import json
import time
import threading
import multiprocessing as mp
from typing import Dict, Any, Optional, Callable
from queue import Queue, Empty
from dataclasses import dataclass, asdict
import socket
import struct


@dataclass
class IPCPacket:
    """IPC packet structure"""
    packet_type: str
    data: Dict[str, Any]
    timestamp: float
    sequence_id: int
    checksum: Optional[int] = None


class IPCBridge:
    """IPC communication bridge between Runtime Hub and analyzer"""
    
    def __init__(self, bridge_name: str = "tetris_analyzer"):
        """Initialize IPC bridge"""
        self.bridge_name = bridge_name
        
        # Communication channels
        self.command_queue: Optional[mp.Queue] = None
        self.response_queue: Optional[mp.Queue] = None
        self.event_queue: Optional[mp.Queue] = None
        
        # Shared memory for high-frequency data
        self.board_state_memory: Optional[mp.shared_memory.SharedMemory] = None
        self.performance_memory: Optional[mp.shared_memory.SharedMemory] = None
        
        # Socket for real-time communication
        self.socket: Optional[socket.socket] = None
        self.socket_port = 0
        
        # Sequence tracking
        self.sequence_counter = 0
        self.pending_requests: Dict[int, float] = {}
        
        # Thread management
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.on_board_update: Optional[Callable] = None
        self.on_coaching_update: Optional[Callable] = None
        self.on_performance_update: Optional[Callable] = None
    
    def initialize(self) -> bool:
        """Initialize IPC components"""
        try:
            # Create communication queues
            self.command_queue = mp.Queue(maxsize=100)
            self.response_queue = mp.Queue(maxsize=100)
            self.event_queue = mp.Queue(maxsize=1000)
            
            # Create shared memory blocks
            self._create_shared_memory()
            
            # Setup socket for real-time communication
            self._setup_socket()
            
            # Start worker thread
            self._start_worker()
            
            self.running = True
            print(f"IPC Bridge '{self.bridge_name}' initialized")
            return True
            
        except Exception as e:
            print(f"Failed to initialize IPC bridge: {e}")
            return False
    
    def _create_shared_memory(self):
        """Create shared memory blocks"""
        # Board state memory (256KB)
        try:
            self.board_state_memory = mp.shared_memory.SharedMemory(
                name=f"{self.bridge_name}_board_state",
                size=256 * 1024,
                create=True
            )
            # Initialize with empty JSON
            initial_data = json.dumps({"board": [], "timestamp": 0}).encode('utf-8')
            self.board_state_memory.buf[:len(initial_data)] = initial_data
        except FileExistsError:
            self.board_state_memory = mp.shared_memory.SharedMemory(
                name=f"{self.bridge_name}_board_state"
            )
        
        # Performance metrics memory (64KB)
        try:
            self.performance_memory = mp.shared_memory.SharedMemory(
                name=f"{self.bridge_name}_performance",
                size=64 * 1024,
                create=True
            )
            # Initialize with empty metrics
            initial_metrics = json.dumps({
                "fps": 0,
                "latency": 0,
                "accuracy": 0,
                "timestamp": 0
            }).encode('utf-8')
            self.performance_memory.buf[:len(initial_metrics)] = initial_metrics
        except FileExistsError:
            self.performance_memory = mp.shared_memory.SharedMemory(
                name=f"{self.bridge_name}_performance"
            )
    
    def _setup_socket(self):
        """Setup socket for real-time communication"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', 0))  # Let OS assign port
        self.socket_port = self.socket.getsockname()[1]
        self.socket.listen(5)
        print(f"IPC Socket listening on port {self.socket_port}")
    
    def _start_worker(self):
        """Start worker thread for processing IPC messages"""
        self.worker_thread = threading.Thread(
            target=self._worker_loop,
            daemon=True
        )
        self.worker_thread.start()
    
    def _worker_loop(self):
        """Main worker loop for processing IPC messages"""
        while self.running:
            try:
                # Process commands
                self._process_commands()
                
                # Process events
                self._process_events()
                
                # Handle socket connections
                self._handle_socket_connections()
                
                # Cleanup old requests
                self._cleanup_old_requests()
                
                time.sleep(0.01)  # 100Hz processing
                
            except Exception as e:
                print(f"IPC worker error: {e}")
                time.sleep(0.1)
    
    def _process_commands(self):
        """Process pending commands"""
        if not self.command_queue:
            return
        
        try:
            while not self.command_queue.empty():
                packet = self.command_queue.get_nowait()
                self._handle_command(packet)
        except Empty:
            pass
        except Exception as e:
            print(f"Error processing commands: {e}")
    
    def _process_events(self):
        """Process pending events"""
        if not self.event_queue:
            return
        
        try:
            while not self.event_queue.empty():
                packet = self.event_queue.get_nowait()
                self._handle_event(packet)
        except Empty:
            pass
        except Exception as e:
            print(f"Error processing events: {e}")
    
    def _handle_socket_connections(self):
        """Handle incoming socket connections"""
        if not self.socket:
            return
        
        try:
            # Set socket to non-blocking
            self.socket.settimeout(0.1)
            
            try:
                conn, addr = self.socket.accept()
                # Handle connection in separate thread or process
                self._handle_socket_connection(conn, addr)
            except socket.timeout:
                pass  # No connections waiting
        except Exception as e:
            print(f"Socket connection error: {e}")
    
    def _handle_socket_connection(self, conn: socket.socket, addr: tuple):
        """Handle individual socket connection"""
        try:
            while self.running:
                # Receive data
                data = conn.recv(4096)
                if not data:
                    break
                
                # Parse and process
                try:
                    packet = self._deserialize_packet(data)
                    self._handle_event(packet)
                except Exception as e:
                    print(f"Error parsing socket data: {e}")
            
        except Exception as e:
            print(f"Socket connection error: {e}")
        finally:
            conn.close()
    
    def _handle_command(self, packet: IPCPacket):
        """Handle incoming command packet"""
        response_data = {"status": "unknown", "data": None}
        
        try:
            if packet.packet_type == "get_board_state":
                response_data = self._get_board_state()
            elif packet.packet_type == "get_coaching_hints":
                response_data = self._get_coaching_hints()
            elif packet.packet_type == "get_performance":
                response_data = self._get_performance_metrics()
            elif packet.packet_type == "set_config":
                response_data = self._set_configuration(packet.data)
            elif packet.packet_type == "ping":
                response_data = {"status": "pong", "timestamp": time.time()}
            else:
                response_data = {"status": "error", "message": f"Unknown command: {packet.packet_type}"}
        
        except Exception as e:
            response_data = {"status": "error", "message": str(e)}
        
        # Send response
        response_packet = IPCPacket(
            packet_type=f"{packet.packet_type}_response",
            data=response_data,
            timestamp=time.time(),
            sequence_id=packet.sequence_id
        )
        
        if self.response_queue:
            self.response_queue.put(response_packet)
    
    def _handle_event(self, packet: IPCPacket):
        """Handle incoming event packet"""
        try:
            if packet.packet_type == "board_update":
                self._update_board_state(packet.data)
                if self.on_board_update:
                    self.on_board_update(packet.data)
            
            elif packet.packet_type == "coaching_update":
                if self.on_coaching_update:
                    self.on_coaching_update(packet.data)
            
            elif packet.packet_type == "performance_update":
                self._update_performance_metrics(packet.data)
                if self.on_performance_update:
                    self.on_performance_update(packet.data)
        
        except Exception as e:
            print(f"Error handling event: {e}")
    
    def _get_board_state(self) -> Dict[str, Any]:
        """Get current board state from shared memory"""
        if not self.board_state_memory:
            return {"status": "error", "message": "Board state memory not available"}
        
        try:
            data = self.board_state_memory.buf.tobytes().rstrip(b'\x00').decode('utf-8')
            if data:
                board_data = json.loads(data)
                return {"status": "success", "data": board_data}
        except Exception as e:
            print(f"Error reading board state: {e}")
        
        return {"status": "error", "message": "Failed to read board state"}
    
    def _get_coaching_hints(self) -> Dict[str, Any]:
        """Get current coaching hints"""
        # This would be implemented based on analyzer's IPC interface
        return {"status": "success", "data": {"hints": []}}
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        if not self.performance_memory:
            return {"status": "error", "message": "Performance memory not available"}
        
        try:
            data = self.performance_memory.buf.tobytes().rstrip(b'\x00').decode('utf-8')
            if data:
                metrics = json.loads(data)
                return {"status": "success", "data": metrics}
        except Exception as e:
            print(f"Error reading performance metrics: {e}")
        
        return {"status": "error", "message": "Failed to read performance metrics"}
    
    def _set_configuration(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Set configuration parameters"""
        # This would send configuration to analyzer subprocess
        return {"status": "success", "message": "Configuration updated"}
    
    def _update_board_state(self, board_data: Dict[str, Any]):
        """Update board state in shared memory"""
        if not self.board_state_memory:
            return
        
        try:
            data = json.dumps(board_data).encode('utf-8')
            if len(data) < len(self.board_state_memory.buf):
                self.board_state_memory.buf[:len(data)] = data
        except Exception as e:
            print(f"Error updating board state: {e}")
    
    def _update_performance_metrics(self, metrics: Dict[str, Any]):
        """Update performance metrics in shared memory"""
        if not self.performance_memory:
            return
        
        try:
            data = json.dumps(metrics).encode('utf-8')
            if len(data) < len(self.performance_memory.buf):
                self.performance_memory.buf[:len(data)] = data
        except Exception as e:
            print(f"Error updating performance metrics: {e}")
    
    def _cleanup_old_requests(self):
        """Clean up old pending requests"""
        current_time = time.time()
        expired_requests = [
            seq_id for seq_id, timestamp in self.pending_requests.items()
            if current_time - timestamp > 30  # 30 second timeout
        ]
        
        for seq_id in expired_requests:
            del self.pending_requests[seq_id]
    
    def _serialize_packet(self, packet: IPCPacket) -> bytes:
        """Serialize packet to bytes"""
        data = json.dumps(asdict(packet)).encode('utf-8')
        length = len(data)
        return struct.pack(f'!I{length}s', length, data)
    
    def _deserialize_packet(self, data: bytes) -> IPCPacket:
        """Deserialize packet from bytes"""
        length = struct.unpack('!I', data[:4])[0]
        packet_data = data[4:4+length].decode('utf-8')
        packet_dict = json.loads(packet_data)
        return IPCPacket(**packet_dict)
    
    def send_command(self, command_type: str, data: Dict[str, Any] = None) -> int:
        """Send command and return sequence ID"""
        if not self.command_queue:
            return -1
        
        self.sequence_counter += 1
        packet = IPCPacket(
            packet_type=command_type,
            data=data or {},
            timestamp=time.time(),
            sequence_id=self.sequence_counter
        )
        
        try:
            self.command_queue.put(packet)
            self.pending_requests[self.sequence_counter] = time.time()
            return self.sequence_counter
        except Exception as e:
            print(f"Failed to send command: {e}")
            return -1
    
    def get_response(self, sequence_id: int, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """Get response for a specific command"""
        if not self.response_queue:
            return None
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                packet = self.response_queue.get_nowait()
                if packet.sequence_id == sequence_id:
                    return packet.data
                else:
                    # Put back wrong packet
                    self.response_queue.put(packet)
            except Empty:
                pass
            except Exception as e:
                print(f"Error getting response: {e}")
            
            time.sleep(0.01)
        
        return None
    
    def send_event(self, event_type: str, data: Dict[str, Any] = None):
        """Send event packet"""
        if not self.event_queue:
            return
        
        packet = IPCPacket(
            packet_type=event_type,
            data=data or {},
            timestamp=time.time(),
            sequence_id=0  # Events don't need sequence IDs
        )
        
        try:
            self.event_queue.put(packet)
        except Exception as e:
            print(f"Failed to send event: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get IPC bridge status"""
        return {
            "running": self.running,
            "socket_port": self.socket_port,
            "pending_requests": len(self.pending_requests),
            "sequence_counter": self.sequence_counter,
            "shared_memory": {
                "board_state": self.board_state_memory is not None,
                "performance": self.performance_memory is not None
            }
        }
    
    def shutdown(self):
        """Shutdown IPC bridge"""
        self.running = False
        
        # Wait for worker thread
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2)
        
        # Close socket
        if self.socket:
            self.socket.close()
        
        # Close shared memory (don't unlink - other processes might use it)
        if self.board_state_memory:
            self.board_state_memory.close()
        
        if self.performance_memory:
            self.performance_memory.close()
        
        # Close queues
        if self.command_queue:
            self.command_queue.close()
        
        if self.response_queue:
            self.response_queue.close()
        
        if self.event_queue:
            self.event_queue.close()
        
        print("IPC Bridge shutdown complete")
