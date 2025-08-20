"""OpenTTD Network Protocol Implementation

This module implements the binary packet protocol used by OpenTTD for multiplayer communication.
Based on the protocol definitions from tcp_game.h.
"""

import struct
import socket
import io
from enum import IntEnum
from typing import Optional, Union, Dict, Any, Tuple, List


class PacketType(IntEnum):
    """Packet types"""

    # Server packets that can be sent before client joins
    SERVER_FULL = 0x00
    SERVER_BANNED = 0x01

    # Client join and error handling
    CLIENT_JOIN = 0x02
    SERVER_ERROR = 0x03

    # Unused packet types (formerly lobby)
    CLIENT_UNUSED = 0x04
    SERVER_UNUSED = 0x05

    # Game info packets
    SERVER_GAME_INFO = 0x06
    CLIENT_GAME_INFO = 0x07

    # Server state packets
    SERVER_NEWGAME = 0x08
    SERVER_SHUTDOWN = 0x09

    # Authentication and setup packets
    SERVER_CHECK_NEWGRFS = 0x0A
    CLIENT_NEWGRFS_CHECKED = 0x0B
    SERVER_NEED_GAME_PASSWORD = 0x0C
    CLIENT_GAME_PASSWORD = 0x0D
    SERVER_NEED_COMPANY_PASSWORD = 0x0E
    CLIENT_COMPANY_PASSWORD = 0x0F
    SERVER_WELCOME = 0x10
    SERVER_CLIENT_INFO = 0x11

    # Map synchronization packets
    CLIENT_GETMAP = 0x12
    SERVER_WAIT = 0x13
    SERVER_MAP_BEGIN = 0x14
    SERVER_MAP_SIZE = 0x15
    SERVER_MAP_DATA = 0x16
    SERVER_MAP_DONE = 0x17
    CLIENT_MAP_OK = 0x18
    SERVER_JOIN = 0x19

    # Game synchronization packets
    SERVER_FRAME = 0x1A
    CLIENT_ACK = 0x1B
    SERVER_SYNC = 0x1C

    # Command execution packets
    CLIENT_COMMAND = 0x1D
    SERVER_COMMAND = 0x1E

    # Chat packets
    CLIENT_CHAT = 0x1F
    SERVER_CHAT = 0x20
    SERVER_EXTERNAL_CHAT = 0x21

    # Remote console packets
    CLIENT_RCON = 0x22
    SERVER_RCON = 0x23

    # Client management packets
    CLIENT_MOVE = 0x24
    SERVER_MOVE = 0x25
    CLIENT_SET_PASSWORD = 0x26
    CLIENT_SET_NAME = 0x27
    SERVER_COMPANY_UPDATE = 0x28
    SERVER_CONFIG_UPDATE = 0x29

    # Client disconnection packets
    CLIENT_QUIT = 0x2A
    SERVER_QUIT = 0x2B
    CLIENT_ERROR = 0x2C
    SERVER_ERROR_QUIT = 0x2D


class NetworkError(IntEnum):
    """Network error codes"""

    GENERAL = 0x00
    DESYNC = 0x01
    SAVEGAME_FAILED = 0x02
    CONNECTION_LOST = 0x03
    NOT_AUTHORIZED = 0x04
    NOT_EXPECTED = 0x05
    WRONG_REVISION = 0x06
    NAME_IN_USE = 0x07
    WRONG_PASSWORD = 0x08
    COMPANY_MISMATCH = 0x09
    KICKED = 0x0A
    CHEATER = 0x0B
    FULL = 0x0C
    TOO_MANY_COMMANDS = 0x0D
    TIMEOUT_PASSWORD = 0x0E
    TIMEOUT_COMPUTER = 0x0F
    TIMEOUT_MAP = 0x10
    TIMEOUT_JOIN = 0x11
    INVALID_CLIENT_NAME = 0x12
    NOT_ON_ALLOW_LIST = 0x13


class Packet:
    """Represents a network packet with automatic serialization/deserialization"""

    MAX_PACKET_SIZE = 1460  # Maximum UDP packet size for OpenTTD

    def __init__(self, packet_type: Optional[PacketType] = None, data: Optional[bytes] = None):
        self.type = packet_type
        self.buffer = io.BytesIO()
        if data:
            self.buffer.write(data)
            self.buffer.seek(0)

    def write_uint8(self, value: int) -> None:
        """Write an 8-bit unsigned integer"""
        self.buffer.write(struct.pack("<B", value))

    def write_uint16(self, value: int) -> None:
        """Write a 16-bit unsigned integer"""
        self.buffer.write(struct.pack("<H", value))

    def write_uint32(self, value: int) -> None:
        """Write a 32-bit unsigned integer"""
        self.buffer.write(struct.pack("<L", value))

    def write_uint64(self, value: int) -> None:
        """Write a 64-bit unsigned integer"""
        self.buffer.write(struct.pack("<Q", value))

    def write_string(self, value: str) -> None:
        """Write a null-terminated string"""
        encoded = value.encode("utf-8")
        self.buffer.write(encoded)
        self.buffer.write(b"\x00")

    def write_bytes(self, data: bytes) -> None:
        """Write raw bytes"""
        self.buffer.write(data)

    def write_buffer(self, data: bytes) -> None:
        """Write buffer with length prefix (like OpenTTD's Send_buffer)"""
        self.write_uint16(len(data))
        self.buffer.write(data)

    def read_uint8(self) -> int:
        """Read an 8-bit unsigned integer"""
        data = self.buffer.read(1)
        if not data:
            raise EOFError("Unexpected end of packet")
        return int(struct.unpack("<B", data)[0])

    def read_bool(self) -> bool:
        """Read a boolean (sent as uint8)"""
        return bool(self.read_uint8())

    def read_uint16(self) -> int:
        """Read a 16-bit unsigned integer"""
        data = self.buffer.read(2)
        if len(data) != 2:
            raise EOFError("Unexpected end of packet")
        return int(struct.unpack("<H", data)[0])

    def read_uint32(self) -> int:
        """Read a 32-bit unsigned integer"""
        data = self.buffer.read(4)
        if len(data) != 4:
            raise EOFError("Unexpected end of packet")
        return int(struct.unpack("<L", data)[0])

    def read_uint64(self) -> int:
        """Read a 64-bit unsigned integer"""
        data = self.buffer.read(8)
        if len(data) != 8:
            raise EOFError("Unexpected end of packet")
        return int(struct.unpack("<Q", data)[0])

    def read_string(self) -> str:
        """Read a null-terminated string"""
        result = bytearray()
        while True:
            byte = self.buffer.read(1)
            if not byte:
                raise EOFError("Unexpected end of packet while reading string")
            if byte == b"\x00":
                break
            result.extend(byte)
        return result.decode("utf-8")

    def read_bytes(self, length: int) -> bytes:
        """Read specified number of bytes"""
        data = self.buffer.read(length)
        if len(data) != length:
            raise EOFError(f"Expected {length} bytes, got {len(data)}")
        return data

    def remaining_bytes(self) -> bytes:
        """Read all remaining bytes"""
        return self.buffer.read()

    def size(self) -> int:
        """Get current buffer size"""
        current_pos = self.buffer.tell()
        self.buffer.seek(0, 2)
        size = self.buffer.tell()
        self.buffer.seek(current_pos)
        return size

    def to_bytes(self) -> bytes:
        """Convert packet to bytes for transmission"""
        if self.type is None:
            raise ValueError("Packet type not set")

        # Get payload data
        current_pos = self.buffer.tell()
        self.buffer.seek(0)
        payload = self.buffer.read()
        self.buffer.seek(current_pos)

        # Create packet: length (2 bytes) + type (1 byte) + payload
        packet_data = struct.pack("<H", len(payload) + 3) + struct.pack("<B", self.type) + payload
        return packet_data

    @classmethod
    def from_bytes(cls, data: bytes) -> "Packet":
        """Create packet from received bytes"""
        if len(data) < 3:
            raise ValueError("Packet too short")

        # Parse header
        length = struct.unpack("<H", data[:2])[0]
        packet_type = PacketType(struct.unpack("<B", data[2:3])[0])

        if length != len(data):
            raise ValueError(f"Packet length mismatch: expected {length}, got {len(data)}")

        # Create packet with payload
        payload = data[3:] if len(data) > 3 else b""
        packet = cls(packet_type, payload)
        return packet


class NetworkConnection:
    """Manages TCP connection to OpenTTD server"""

    def __init__(self, host: str, port: int, timeout: float = 30.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket: Optional[socket.socket] = None
        self._recv_buffer = b""

    def connect(self) -> None:
        """Establish connection to server"""
        if self.socket:
            self.close()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)

        try:
            self.socket.connect((self.host, self.port))
        except Exception:
            self.socket.close()
            self.socket = None
            raise

    def close(self) -> None:
        """Close connection"""
        if self.socket:
            self.socket.close()
            self.socket = None
        self._recv_buffer = b""

    def is_connected(self) -> bool:
        """Check if connection is active"""
        return self.socket is not None

    def send_packet(self, packet: Packet) -> None:
        """Send packet to server"""
        if not self.socket:
            raise ConnectionError("Not connected to server")

        data = packet.to_bytes()
        self.socket.sendall(data)

    def receive_packet(self) -> Optional[Packet]:
        """Receive packet from server"""
        if not self.socket:
            raise ConnectionError("Not connected to server")

        # Read until we have at least packet header (length + type)
        while len(self._recv_buffer) < 3:
            data = self.socket.recv(4096)
            if not data:
                raise ConnectionError("Connection closed by server")
            self._recv_buffer += data

        # Parse packet length
        packet_length = struct.unpack("<H", self._recv_buffer[:2])[0]

        # Read until we have the complete packet
        while len(self._recv_buffer) < packet_length:
            data = self.socket.recv(4096)
            if not data:
                raise ConnectionError("Connection closed by server")
            self._recv_buffer += data

        # Extract complete packet
        packet_data = self._recv_buffer[:packet_length]
        self._recv_buffer = self._recv_buffer[packet_length:]

        return Packet.from_bytes(packet_data)


def coordinate_to_tile(x: int, y: int, map_size_x: int = 256) -> int:
    """Convert X,Y coordinates to tile index"""
    return y * map_size_x + x
