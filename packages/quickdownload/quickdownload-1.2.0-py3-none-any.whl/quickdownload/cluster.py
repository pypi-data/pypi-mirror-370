#!/usr/bin/env python3

import json
import os
import socket
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import requests

# Cluster configuration
CLUSTER_UDP_PORT = 45678
CLUSTER_HTTP_PORT_RANGE = (45680, 45700)
CLUSTER_DISCOVERY_TIMEOUT = 5
CLUSTER_CHUNK_SHARE_TIMEOUT = 30


@dataclass
class ClusterNode:
    """Represents a node in the cluster."""

    node_id: str
    name: str
    ip: str
    http_port: int
    last_seen: float
    capabilities: Dict[str, any]


@dataclass
class ClusterSession:
    """Represents a download session in the cluster."""

    session_id: str
    url: str
    output_path: str
    file_size: int
    total_chunks: int
    parallel_count: int
    throttle_limit: Optional[str]
    coordinator_node_id: str
    required_nodes: int
    created_at: float
    started_at: Optional[float]
    status: str  # 'waiting', 'active', 'completed', 'failed'
    registered_nodes: List[str]
    chunk_assignments: Dict[int, str]  # chunk_id -> node_id


@dataclass
class ChunkInfo:
    """Information about a download chunk."""

    chunk_id: int
    start_byte: int
    end_byte: int
    size: int
    assigned_node: Optional[str]
    status: str  # 'pending', 'downloading', 'completed', 'failed'
    local_path: Optional[str]
    checksum: Optional[str]


class ClusterConfig:
    """Manages cluster configuration and persistent storage."""

    def __init__(self):
        self.config_dir = Path.home() / ".quickdownload"
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "cluster_config.json"
        self.sessions_file = self.config_dir / "cluster_sessions.json"
        self.registrations_file = self.config_dir / "cluster_registrations.json"

        self.node_id = self._load_or_create_node_id()
        self.node_name = self._load_node_name()

    def _load_or_create_node_id(self) -> str:
        """Load existing node ID or create new one."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    return config.get("node_id", str(uuid.uuid4()))
            except (json.JSONDecodeError, IOError):
                pass

        # Create new node ID
        node_id = str(uuid.uuid4())
        self._save_config({"node_id": node_id, "node_name": socket.gethostname()})
        return node_id

    def _load_node_name(self) -> str:
        """Load node name from config."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    return config.get("node_name", socket.gethostname())
            except (json.JSONDecodeError, IOError):
                pass
        return socket.gethostname()

    def _save_config(self, config: Dict):
        """Save configuration to disk."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save cluster config: {e}")

    def set_node_name(self, name: str):
        """Set the node name."""
        self.node_name = name
        config = {"node_id": self.node_id, "node_name": name}
        self._save_config(config)

    def save_session(self, session: ClusterSession):
        """Save session to persistent storage."""
        sessions = self.load_sessions()
        sessions[session.session_id] = asdict(session)
        try:
            with open(self.sessions_file, "w") as f:
                json.dump(sessions, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save session: {e}")

    def load_sessions(self) -> Dict[str, Dict]:
        """Load all sessions from storage."""
        if not self.sessions_file.exists():
            return {}
        try:
            with open(self.sessions_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def save_registrations(self, registrations: List[str]):
        """Save current node's registrations."""
        try:
            with open(self.registrations_file, "w") as f:
                json.dump({"registrations": registrations}, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save registrations: {e}")

    def load_registrations(self) -> List[str]:
        """Load current node's registrations."""
        if not self.registrations_file.exists():
            return []
        try:
            with open(self.registrations_file, "r") as f:
                data = json.load(f)
                return data.get("registrations", [])
        except (json.JSONDecodeError, IOError):
            return []


class ChunkShareHandler(BaseHTTPRequestHandler):
    """HTTP handler for sharing downloaded chunks between nodes."""

    def do_GET(self):
        """Handle chunk requests from other nodes."""
        try:
            path = self.path.strip("/")
            parts = path.split("/")

            if len(parts) != 3 or parts[0] != "chunk":
                self.send_error(404, "Invalid chunk request")
                return

            session_id = parts[1]
            chunk_id = int(parts[2])

            # Find the chunk file
            chunk_manager = getattr(self.server, "chunk_manager", None)
            if not chunk_manager:
                self.send_error(404, "Chunk manager not available")
                return

            chunk_path = chunk_manager.get_chunk_path(session_id, chunk_id)
            if not chunk_path or not os.path.exists(chunk_path):
                self.send_error(404, "Chunk not found")
                return

            # Send the chunk
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(os.path.getsize(chunk_path)))
            self.end_headers()

            with open(chunk_path, "rb") as f:
                while True:
                    data = f.read(8192)
                    if not data:
                        break
                    self.wfile.write(data)

        except Exception as e:
            print(f"Error serving chunk: {e}")
            self.send_error(500, "Internal server error")

    def log_message(self, format, *args):
        """Suppress HTTP server log messages."""
        pass


class ClusterChunkManager:
    """Manages chunk sharing and coordination."""

    def __init__(self, config: ClusterConfig):
        self.config = config
        self.chunk_cache_dir = config.config_dir / "chunks"
        self.chunk_cache_dir.mkdir(exist_ok=True)
        self.http_server = None
        self.http_port = None

    def start_chunk_server(self) -> int:
        """Start HTTP server for chunk sharing."""
        for port in range(*CLUSTER_HTTP_PORT_RANGE):
            try:
                self.http_server = HTTPServer(("", port), ChunkShareHandler)
                self.http_server.chunk_manager = self
                self.http_port = port

                # Start server in background thread
                server_thread = threading.Thread(
                    target=self.http_server.serve_forever, daemon=True
                )
                server_thread.start()
                return port
            except OSError:
                continue

        raise RuntimeError("Could not start chunk server - no available ports")

    def stop_chunk_server(self):
        """Stop the chunk sharing server."""
        if self.http_server:
            self.http_server.shutdown()
            self.http_server = None

    def get_chunk_path(self, session_id: str, chunk_id: int) -> Optional[str]:
        """Get the local path for a chunk."""
        chunk_dir = self.chunk_cache_dir / session_id
        chunk_file = chunk_dir / f"chunk_{chunk_id}.part"
        return str(chunk_file) if chunk_file.exists() else None

    def save_chunk(self, session_id: str, chunk_id: int, data: bytes) -> str:
        """Save chunk data locally."""
        chunk_dir = self.chunk_cache_dir / session_id
        chunk_dir.mkdir(exist_ok=True)

        chunk_file = chunk_dir / f"chunk_{chunk_id}.part"
        with open(chunk_file, "wb") as f:
            f.write(data)

        return str(chunk_file)

    def download_chunk_from_peer(
        self, peer_ip: str, peer_port: int, session_id: str, chunk_id: int
    ) -> Optional[bytes]:
        """Download a chunk from another node."""
        try:
            url = f"http://{peer_ip}:{peer_port}/chunk/{session_id}/{chunk_id}"
            response = requests.get(url, timeout=CLUSTER_CHUNK_SHARE_TIMEOUT)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(
                f"Failed to download chunk {chunk_id} from {peer_ip}:{peer_port}: {e}"
            )
            return None


class ClusterDiscovery:
    """Handles node discovery and communication via UDP."""

    def __init__(self, config: ClusterConfig):
        self.config = config
        self.known_nodes: Dict[str, ClusterNode] = {}
        self.discovery_socket = None
        self.running = False

    def start_discovery(self, http_port: int):
        """Start UDP discovery service."""
        try:
            self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.discovery_socket.bind(("", CLUSTER_UDP_PORT))
            self.running = True

            # Start discovery thread
            discovery_thread = threading.Thread(
                target=self._discovery_loop, args=(http_port,), daemon=True
            )
            discovery_thread.start()

        except Exception as e:
            print(f"Failed to start discovery: {e}")

    def stop_discovery(self):
        """Stop discovery service."""
        self.running = False
        if self.discovery_socket:
            self.discovery_socket.close()

    def _discovery_loop(self, http_port: int):
        """Main discovery loop."""
        while self.running:
            try:
                # Send discovery broadcast
                self._send_discovery_broadcast(http_port)

                # Listen for responses
                self.discovery_socket.settimeout(1.0)
                try:
                    data, addr = self.discovery_socket.recvfrom(1024)
                    self._handle_discovery_message(data, addr)
                except socket.timeout:
                    pass

                # Clean up old nodes
                current_time = time.time()
                self.known_nodes = {
                    node_id: node
                    for node_id, node in self.known_nodes.items()
                    if current_time - node.last_seen < 30
                }

            except Exception as e:
                if self.running:
                    print(f"Discovery error: {e}")

    def _send_discovery_broadcast(self, http_port: int):
        """Send discovery broadcast message."""
        try:
            message = {
                "type": "discovery",
                "node_id": self.config.node_id,
                "node_name": self.config.node_name,
                "http_port": http_port,
                "timestamp": time.time(),
            }

            data = json.dumps(message).encode("utf-8")

            # Broadcast to local network
            broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            broadcast_socket.sendto(data, ("<broadcast>", CLUSTER_UDP_PORT))
            broadcast_socket.close()

        except Exception as e:
            print(f"Failed to send discovery broadcast: {e}")

    def _handle_discovery_message(self, data: bytes, addr: Tuple[str, int]):
        """Handle incoming discovery message."""
        try:
            message = json.loads(data.decode("utf-8"))

            if message.get("type") == "discovery":
                node_id = message.get("node_id")
                if node_id and node_id != self.config.node_id:
                    node = ClusterNode(
                        node_id=node_id,
                        name=message.get("node_name", "Unknown"),
                        ip=addr[0],
                        http_port=message.get("http_port", 0),
                        last_seen=time.time(),
                        capabilities={},
                    )
                    self.known_nodes[node_id] = node

        except Exception as e:
            print(f"Failed to handle discovery message: {e}")

    def get_available_nodes(self) -> List[ClusterNode]:
        """Get list of currently available nodes."""
        current_time = time.time()
        return [
            node
            for node in self.known_nodes.values()
            if current_time - node.last_seen < 10
        ]


class ClusterManagerWithRegistration:
    """Main cluster manager with registration-based participation."""

    def __init__(self):
        self.config = ClusterConfig()
        self.chunk_manager = ClusterChunkManager(self.config)
        self.discovery = ClusterDiscovery(self.config)
        self.http_port = None
        self.current_registrations = self.config.load_registrations()

    def initialize_cluster(self):
        """Initialize cluster node - run once per device."""
        print("Initializing cluster node...")

        # Start chunk sharing server
        try:
            self.http_port = self.chunk_manager.start_chunk_server()
            print(f"✓ Chunk sharing server started on port {self.http_port}")
        except Exception as e:
            print(f"✗ Failed to start chunk server: {e}")
            return False

        # Start node discovery
        try:
            self.discovery.start_discovery(self.http_port)
            print("✓ Node discovery started")
        except Exception as e:
            print(f"✗ Failed to start discovery: {e}")
            return False

        print("✓ Cluster node initialized")
        print(f"  Node ID: {self.config.node_id}")
        print(f"  Node Name: {self.config.node_name}")
        return True

    def set_node_name(self, name: str):
        """Set the node name for this device."""
        self.config.set_node_name(name)
        print(f"✓ Node name set to: {name}")

    def create_download_session(
        self,
        url: str,
        output_path: str,
        parallel_count: int = 4,
        throttle_limit: Optional[str] = None,
        required_nodes: int = 2,
        wait_time: int = 60,
    ) -> str:
        """Create a new download session and wait for node registration."""

        # Initialize cluster if not done
        if not self.http_port:
            if not self.initialize_cluster():
                raise RuntimeError("Failed to initialize cluster")

        # Analyze file
        print("Analyzing file...")
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            response.raise_for_status()

            file_size = int(response.headers.get("content-length", 0))
            if file_size == 0:
                raise ValueError("Could not determine file size")

            # Check if server supports range requests
            accept_ranges = response.headers.get("accept-ranges", "").lower()
            if accept_ranges != "bytes":
                print(
                    "Server doesn't support range requests - falling back to single download"
                )
                parallel_count = 1

        except Exception as e:
            raise RuntimeError(f"Failed to analyze file: {e}")

        # Create session
        session_id = str(uuid.uuid4())[:8]
        total_chunks = parallel_count

        session = ClusterSession(
            session_id=session_id,
            url=url,
            output_path=output_path or os.path.basename(urlparse(url).path),
            file_size=file_size,
            total_chunks=total_chunks,
            parallel_count=parallel_count,
            throttle_limit=throttle_limit,
            coordinator_node_id=self.config.node_id,
            required_nodes=required_nodes,
            created_at=time.time(),
            started_at=None,
            status="waiting",
            registered_nodes=[self.config.node_id],  # Coordinator auto-registers
            chunk_assignments={},
        )

        # Save session
        self.config.save_session(session)

        print(f"✓ Download session created: {session_id}")
        print(f"  URL: {url}")
        print(f"  File size: {file_size / (1024*1024):.1f} MB")
        print(f"  Chunks: {total_chunks}")
        print(f"  Required nodes: {required_nodes}")
        print("  Waiting for node registration...")

        # Wait for registrations
        wait_start = time.time()
        while time.time() - wait_start < wait_time:
            session_data = self.config.load_sessions().get(session_id)
            if session_data:
                current_session = ClusterSession(**session_data)
                registered_count = len(current_session.registered_nodes)

                print(f"  Registered nodes: {registered_count}/{required_nodes}")

                if registered_count >= required_nodes:
                    print("✓ Sufficient nodes registered, starting download...")
                    return self._start_cluster_download(session_id)

            time.sleep(2)

        print("✗ Timeout waiting for node registration")
        return session_id

    def register_for_session(self, session_id: str) -> bool:
        """Register this node to participate in a download session."""
        sessions = self.config.load_sessions()
        session_data = sessions.get(session_id)

        if not session_data:
            print(f"✗ Session {session_id} not found")
            return False

        session = ClusterSession(**session_data)

        if session.status != "waiting":
            print(
                f"✗ Session {session_id} is not accepting registrations (status: {session.status})"
            )
            return False

        if self.config.node_id not in session.registered_nodes:
            session.registered_nodes.append(self.config.node_id)
            sessions[session_id] = asdict(session)

            # Save updated session
            self.config.save_session(session)

            # Update local registrations
            if session_id not in self.current_registrations:
                self.current_registrations.append(session_id)
                self.config.save_registrations(self.current_registrations)

        print(f"✓ Registered for session: {session_id}")
        print(
            f"  Registered nodes: {len(session.registered_nodes)}/{session.required_nodes}"
        )
        return True

    def unregister_from_session(self, session_id: str) -> bool:
        """Unregister this node from a download session."""
        sessions = self.config.load_sessions()
        session_data = sessions.get(session_id)

        if not session_data:
            print(f"✗ Session {session_id} not found")
            return False

        session = ClusterSession(**session_data)

        if self.config.node_id in session.registered_nodes:
            session.registered_nodes.remove(self.config.node_id)
            sessions[session_id] = asdict(session)
            self.config.save_session(session)

        # Update local registrations
        if session_id in self.current_registrations:
            self.current_registrations.remove(session_id)
            self.config.save_registrations(self.current_registrations)

        print(f"✓ Unregistered from session: {session_id}")
        return True

    def withdraw_from_all_sessions(self):
        """Withdraw this node from all active sessions."""
        withdrawn_count = 0
        for session_id in self.current_registrations.copy():
            if self.unregister_from_session(session_id):
                withdrawn_count += 1

        print(f"✓ Withdrawn from {withdrawn_count} sessions")

    def show_cluster_status(self):
        """Show current cluster and registration status."""
        print("Cluster Node Status:")
        print(f"  Node ID: {self.config.node_id}")
        print(f"  Node Name: {self.config.node_name}")

        # Show discovered nodes
        if hasattr(self, "discovery"):
            available_nodes = self.discovery.get_available_nodes()
            print(f"  Available nodes: {len(available_nodes)}")
            for node in available_nodes:
                print(f"    - {node.name} ({node.ip}:{node.http_port})")

        # Show current registrations
        if self.current_registrations:
            print(f"  Active registrations: {len(self.current_registrations)}")
            for session_id in self.current_registrations:
                print(f"    - {session_id}")
        else:
            print("  No active registrations")

        # Show pending sessions
        sessions = self.config.load_sessions()
        waiting_sessions = [
            s for s in sessions.values() if s.get("status") == "waiting"
        ]

        if waiting_sessions:
            print(f"  Sessions waiting for registration: {len(waiting_sessions)}")
            for session_data in waiting_sessions:
                session = ClusterSession(**session_data)
                print(f"    - {session.session_id}: {session.url}")
                print(
                    f"      Registered: {len(session.registered_nodes)}/{session.required_nodes}"
                )

    def _start_cluster_download(self, session_id: str) -> str:
        """Start the actual cluster download."""
        sessions = self.config.load_sessions()
        session_data = sessions.get(session_id)

        if not session_data:
            raise RuntimeError(f"Session {session_id} not found")

        session = ClusterSession(**session_data)
        session.status = "active"
        session.started_at = time.time()

        # Assign chunks to registered nodes
        nodes = session.registered_nodes

        for i in range(session.total_chunks):
            node_id = nodes[i % len(nodes)]
            session.chunk_assignments[i] = node_id

        # Save updated session
        sessions[session_id] = asdict(session)
        self.config.save_session(session)

        print("✓ Starting cluster download...")
        print(f"  Session: {session_id}")
        print(f"  Participating nodes: {len(nodes)}")
        print("  Chunk assignments:")
        for chunk_id, node_id in session.chunk_assignments.items():
            node_name = "self" if node_id == self.config.node_id else node_id[:8]
            print(f"    Chunk {chunk_id}: {node_name}")

        # Start download process (simplified for this implementation)
        print(f"✓ Cluster download initiated for session {session_id}")
        return session_id


def init_cluster():
    """Initialize cluster node."""
    manager = ClusterManagerWithRegistration()
    return manager.initialize_cluster()


def set_node_name(name: str):
    """Set node name."""
    manager = ClusterManagerWithRegistration()
    manager.set_node_name(name)


def cluster_download(
    url: str,
    output: Optional[str] = None,
    parallel: int = 4,
    throttle: Optional[str] = None,
    required_nodes: int = 2,
    wait_time: int = 60,
) -> str:
    """Start a cluster download session."""
    manager = ClusterManagerWithRegistration()
    return manager.create_download_session(
        url, output, parallel, throttle, required_nodes, wait_time
    )


def register_for_session(session_id: str) -> bool:
    """Register for a download session."""
    manager = ClusterManagerWithRegistration()
    return manager.register_for_session(session_id)


def unregister_from_session(session_id: str) -> bool:
    """Unregister from a download session."""
    manager = ClusterManagerWithRegistration()
    return manager.unregister_from_session(session_id)


def withdraw_all() -> None:
    """Withdraw from all sessions."""
    manager = ClusterManagerWithRegistration()
    manager.withdraw_from_all_sessions()


def show_status():
    """Show cluster status."""
    manager = ClusterManagerWithRegistration()
    manager.show_cluster_status()
