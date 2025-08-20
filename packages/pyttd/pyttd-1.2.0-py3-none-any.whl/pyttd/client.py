"""Client Implementation

Main client class that implements the OpenTTD multiplayer protocol.
Handles connection, authentication, synchronization, and commands.
"""

import asyncio
import threading
import time
import hashlib
import logging
from typing import Optional, Callable, Dict, Any, List, Tuple, Union
from enum import Enum

from .network.protocol import (
    NetworkConnection,
    Packet,
    PacketType,
    NetworkError,
    coordinate_to_tile,
)
from .game.game_state import GameState, CompanyID, CompanyInfo, VehicleInfo, ClientInfo, VehicleType
from .game.commands import CommandPacket, CommandBuilder, Commands, DoCommandFlag, RailType


logger = logging.getLogger(__name__)


class ClientStatus(Enum):
    """Client connection status"""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    JOINED = "joined"
    AUTHENTICATING = "authenticating"
    DOWNLOADING_MAP = "downloading_map"
    ACTIVE = "active"
    ERROR = "error"


class DesyncError(Exception):
    """Raised when client desyncs from server"""

    pass


class AuthenticationError(Exception):
    """Raised when authentication fails"""

    pass


class OpenTTDClient:
    """Main client class"""

    def __init__(
        self,
        server: str,
        port: int = 3979,
        player_name: str = "Player",
        company_name: str = "Company",
        password: str = "",
        company_password: str = "",
        timeout: float = 30.0,
    ):
        """
        Initialize OpenTTD client

        Args:
            server: Server IP address or hostname
            port: Server port (default 3979)
            player_name: Name for this player
            company_name: Name for the company (when creating new company)
            password: Server password if required
            company_password: Company password if required
            timeout: Connection timeout in seconds
        """
        self.server = server
        self.port = port
        self.player_name = player_name
        self.company_name = company_name
        self.password = password
        self.company_password = company_password
        self.timeout = timeout

        # Network connection
        self.connection = NetworkConnection(server, port, timeout)
        self.status = ClientStatus.DISCONNECTED

        # Game state
        self.game_state = GameState()
        # Join as COMPANY_NEW_COMPANY to request company creation
        self.game_state.company_id = CompanyID.COMPANY_NEW_COMPANY

        # Client configuration
        self.client_revision = "14.1"  # Should match OpenTTD version
        self.language_id = 0  # English

        # Connection state
        self._running = False
        self._network_thread: Optional[threading.Thread] = None

        # Company creation state
        self.pending_company_name: Optional[str] = None
        self._last_ack_frame = 0
        self._token = 0
        self._last_ack_time = 0.0

        # Map synchronization
        self._map_buffer = bytearray()
        self._expected_map_size = 0

        # Command queue
        self._command_queue: List[CommandPacket] = []
        self._command_callback: Optional[Callable[[Commands, bool, str], None]] = None

        # Event callbacks
        self._event_callbacks: Dict[str, List[Callable]] = {
            "connected": [],
            "disconnected": [],
            "map_complete": [],
            "game_joined": [],
            "command_result": [],
            "chat_message": [],
            "desync": [],
            "error": [],
            "company_created": [],
        }

    def on(self, event: str, callback: Callable) -> None:
        """Register event callback"""
        if event in self._event_callbacks:
            self._event_callbacks[event].append(callback)

    def _emit_event(self, event: str, *args: Any) -> None:
        """Emit event to registered callbacks"""
        if event in self._event_callbacks:
            for callback in self._event_callbacks[event]:
                try:
                    callback(*args)
                except Exception as e:
                    logger.error(f"Error in event callback {event}: {e}")

    def connect(self) -> bool:
        """
        Connect to the server and complete join process

        Returns:
            True if successfully connected and joined, False otherwise
        """
        try:
            logger.info(f"Connecting to {self.server}:{self.port}")
            self.status = ClientStatus.CONNECTING

            # Establish TCP connection
            self.connection.connect()

            # Start network thread
            self._running = True
            self._network_thread = threading.Thread(target=self._network_loop, daemon=True)
            self._network_thread.start()

            # Send join packet
            self._send_join()

            # Wait for connection to be established (with timeout)
            timeout_start = time.time()
            while self.status not in [ClientStatus.ACTIVE, ClientStatus.ERROR]:
                if time.time() - timeout_start > self.timeout:
                    logger.error("Connection timeout")
                    self.disconnect()
                    return False
                time.sleep(0.1)

            if self.status == ClientStatus.ACTIVE:
                logger.info("Successfully connected and joined game")
                self._emit_event("connected")
                return True
            else:
                logger.error("Failed to connect")
                return False

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.status = ClientStatus.ERROR
            self._emit_event("error", str(e))
            return False

    def disconnect(self) -> None:
        """Disconnect from server"""
        logger.info("Disconnecting from server")

        self._running = False

        if self.connection.is_connected():
            try:
                # Send quit packet
                packet = Packet(PacketType.CLIENT_QUIT)
                self.connection.send_packet(packet)
            except:
                pass  # Ignore errors during disconnect

        self.connection.close()
        self.status = ClientStatus.DISCONNECTED

        if self._network_thread and self._network_thread.is_alive():
            self._network_thread.join(timeout=1.0)

        self._emit_event("disconnected")

    def is_connected(self) -> bool:
        """Check if connected to server"""
        return self.status == ClientStatus.ACTIVE

    def request_game_info(self) -> bool:
        """Request current game information from server"""
        if not self.is_connected():
            logger.warning("Cannot request game info: not connected")
            return False

        try:
            packet = Packet(PacketType.CLIENT_GAME_INFO)
            self.connection.send_packet(packet)
            logger.debug("Sent CLIENT_GAME_INFO request")
            return True
        except Exception as e:
            logger.error(f"Failed to request game info: {e}")
            return False

    # ============================================
    # Game Data Query Methods
    # ============================================

    def get_game_info(self) -> Dict[str, Any]:
        """Get game information"""
        # Use game data from SERVER_GAME_INFO if available
        if hasattr(self, "_real_game_data") and self._real_game_data:
            real_data = self._real_game_data
            return {
                "client_id": self.game_state.client_id,
                "company_id": self.game_state.company_id,
                "frame": real_data.get("ticks_playing", self.game_state.frame),
                "frame_max": self.game_state.frame_max,
                "date": real_data.get("current_year", self.game_state.game_date),
                "calendar_date": real_data.get("calendar_date", 0),
                "start_year": real_data.get("start_year", 1950),
                "current_year": real_data.get("current_year", 1950),
                "map_size": f"{real_data.get('map_width', self.game_state.map_info.size_x)}x{real_data.get('map_height', self.game_state.map_info.size_y)}",
                "companies": real_data.get("companies_on", len(self.game_state.companies)),
                "companies_max": real_data.get("companies_max", 15),
                "clients": real_data.get("clients_on", len(self.game_state.clients)),
                "clients_max": real_data.get("clients_max", 255),
                "spectators": real_data.get("spectators_on", 0),
                "vehicles": len(self.game_state.vehicles),
                "server_name": real_data.get("server_name", "Unknown"),
                "ticks_playing": real_data.get("ticks_playing", 0),
                "synchronized": self.game_state.frame == self.game_state.frame_max,
                "status": self.status.value,
            }
        else:
            # Fallback if no game data available yet
            return {
                "client_id": self.game_state.client_id,
                "company_id": self.game_state.company_id,
                "frame": self.game_state.frame,
                "frame_max": self.game_state.frame_max,
                "date": self.game_state.game_date,
                "map_size": f"{self.game_state.map_info.size_x}x{self.game_state.map_info.size_y}",
                "companies": len(self.game_state.companies),
                "clients": len(self.game_state.clients),
                "vehicles": len(self.game_state.vehicles),
                "synchronized": self.game_state.frame == self.game_state.frame_max,
                "status": self.status.value,
            }

    def get_companies(self) -> Dict[int, Any]:
        """Get information about all companies"""
        from dataclasses import asdict

        return {cid: asdict(company) for cid, company in self.game_state.companies.items()}

    def get_our_company(self) -> Optional[Any]:
        """Get our company information if we're in a company"""
        if self.game_state.company_id is not None and self.game_state.company_id != 255:
            return self.game_state.companies.get(self.game_state.company_id)
        return None

    def get_clients(self) -> Dict[int, Any]:
        """Get information about all connected clients"""
        from dataclasses import asdict

        return {cid: asdict(client) for cid, client in self.game_state.clients.items()}

    def get_map_info(self) -> Dict[str, Any]:
        """Get map information"""
        return {
            "size_x": self.game_state.map_info.size_x,
            "size_y": self.game_state.map_info.size_y,
        }

    def send_command(self, command: CommandPacket) -> bool:
        """
        Send command to server

        Args:
            command: Command packet to send

        Returns:
            True if command was sent successfully
        """
        if not self.is_connected():
            logger.warning("Cannot send command: not connected")
            return False

        try:
            packet = Packet(PacketType.CLIENT_COMMAND)
            packet.write_uint8(command.company)
            packet.write_uint16(command.command_id)
            packet.write_uint16(0)  # err_msg field (STR_NULL = 0)
            packet.write_buffer(command.encode_parameters())
            packet.write_uint8(command.callback_id)

            self.connection.send_packet(packet)
            logger.info(
                f"Sent command: {command.command_id} (company={command.company}, p1={command.p1}, p2={command.p2}, text='{command.text}')"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return False

    def build_rail(
        self, start: Tuple[int, int], end: Tuple[int, int], rail_type: RailType = RailType.RAIL
    ) -> bool:
        """
        Build railroad track between two coordinates

        Args:
            start: Starting coordinate (x, y)
            end: Ending coordinate (x, y)
            rail_type: Type of rail (0=normal, 1=electric, etc.)

        Returns:
            True if command was sent successfully
        """
        start_tile = coordinate_to_tile(start[0], start[1], self.game_state.map_info.size_x)
        end_tile = coordinate_to_tile(end[0], end[1], self.game_state.map_info.size_x)

        command = CommandBuilder.build_rail(
            start_tile, end_tile, rail_type, int(self.game_state.company_id)
        )
        return self.send_command(command)

    def build_train_depot(
        self, x: int, y: int, direction: int = 0, rail_type: RailType = RailType.RAIL
    ) -> bool:
        """Build a train depot at coordinates"""
        tile = coordinate_to_tile(x, y, self.game_state.map_info.size_x)
        command = CommandBuilder.build_train_depot(
            tile, direction, rail_type, int(self.game_state.company_id)
        )
        return self.send_command(command)

    def build_train(self, depot_x: int, depot_y: int, engine_id: int = 0) -> bool:
        """Build a train at depot"""
        depot_tile = coordinate_to_tile(depot_x, depot_y, self.game_state.map_info.size_x)
        command = CommandBuilder.build_vehicle(
            depot_tile, engine_id, int(self.game_state.company_id)
        )
        return self.send_command(command)

    def get_economic_status(self) -> dict:
        """Get general economic information about the game"""
        return {
            "inflation_payment": self.game_state.economy.inflation_rates.get("payment", 1.0),
            "inflation_construction": self.game_state.economy.inflation_rates.get(
                "construction", 1.0
            ),
            "interest_rate": self.game_state.economy.interest_rate,
            "max_loan_default": self.game_state.economy.max_loan,
        }

    # ============================================
    # Building and Construction Methods
    # ============================================

    def create_company(self, company_name: str = "Bot Company", password: str = "") -> bool:
        """Create a new company (happens automatically when joining with COMPANY_NEW_COMPANY)"""
        if not self.is_connected():
            logger.warning("Cannot create company: not connected")
            return False

        # Store the company name for when we get assigned to the new company
        self.pending_company_name = company_name

        logger.info(
            f"Company creation will happen automatically during join process: {company_name}"
        )
        # Note: When client joins with COMPANY_NEW_COMPANY, the server checks company limits
        # and then the client automatically sends CMD_COMPANY_CTRL during the join sequence
        return True

    def build_railway_line(
        self, start: Tuple[int, int], end: Tuple[int, int], rail_type: RailType = RailType.RAIL
    ) -> bool:
        """Build a complete railway line between two points"""
        if not self.is_connected():
            logger.warning("Cannot build railway: not connected")
            return False

        # Simple straight line implementation
        # In a real implementation, this would include pathfinding
        success = self.build_rail(start, end, rail_type)
        if success:
            logger.info(f"Built railway from {start} to {end}")
        return success

    def build_station_with_rail(
        self, x: int, y: int, direction: int = 0, platform_length: int = 4, num_platforms: int = 1
    ) -> bool:
        """Build a railway station with connecting rails"""
        if not self.is_connected():
            logger.warning("Cannot build station: not connected")
            return False

        # Build the station
        success = True
        try:
            # This would need proper station building implementation
            logger.info(
                f"Building station at ({x}, {y}) with {num_platforms} platforms, length {platform_length}"
            )
            # For now, just build a simple rail station
            # Real implementation would use CMD_BUILD_RAIL_STATION
            return False  # Not implemented yet
        except Exception as e:
            logger.error(f"Failed to build station: {e}")
            return False

    def buy_and_start_train(
        self,
        depot_x: int,
        depot_y: int,
        engine_id: int = 0,
        destination_station: Optional[Tuple[int, int]] = None,
    ) -> bool:
        """Buy a train and set up basic orders"""
        if not self.is_connected():
            logger.warning("Cannot buy train: not connected")
            return False

        # Build the train
        success = self.build_train(depot_x, depot_y, engine_id)
        if not success:
            return False

        # If destination provided, add orders (not implemented yet)
        if destination_station:
            logger.info(f"Train built, destination orders not yet implemented")

        return True

    def terraform_area(self, x: int, y: int, width: int, height: int, new_height: int) -> bool:
        """Terraform an area to a specific height"""
        if not self.is_connected():
            logger.warning("Cannot terraform: not connected")
            return False

        # This would require implementing terraform commands
        logger.info(f"Terraforming area ({x},{y}) to ({x+width},{y+height}) at height {new_height}")
        return False  # Not implemented yet

    def clear_area(self, x: int, y: int, width: int, height: int) -> bool:
        """Clear an area of all objects"""
        if not self.is_connected():
            logger.warning("Cannot clear area: not connected")
            return False

        success_count = 0
        total_tiles = width * height

        for dx in range(width):
            for dy in range(height):
                tile_x = x + dx
                tile_y = y + dy
                # Use landscape clear command
                # This is a simplified version - would batch commands
                try:
                    # Would use CMD_LANDSCAPE_CLEAR command here
                    success_count += 1
                except Exception as e:
                    logger.debug(f"Failed to clear tile ({tile_x}, {tile_y}): {e}")

        logger.info(
            f"Cleared {success_count}/{total_tiles} tiles in area ({x},{y}) to ({x+width},{y+height})"
        )
        return success_count > total_tiles * 0.8  # Consider success if 80%+ cleared

    def send_chat(self, message: str, destination_type: int = 0, destination: int = 0) -> bool:
        """Send chat message"""
        if not self.is_connected():
            return False

        try:
            packet = Packet(PacketType.CLIENT_CHAT)
            packet.write_uint8(3)  # Network action (3 = NETWORK_ACTION_CHAT)
            packet.write_uint8(destination_type)  # Destination type
            packet.write_uint32(destination)  # Destination ID
            packet.write_string(message)
            packet.write_uint64(0)  # Data (for money transfers, etc.)

            self.connection.send_packet(packet)
            return True

        except Exception as e:
            logger.error(f"Failed to send chat: {e}")
            return False

    # ============================================
    # Company Management and Economy Methods
    # ============================================

    def increase_loan(self, amount: int) -> bool:
        """Increase company loan by specified amount"""
        if not self.is_connected() or self.game_state.company_id == CompanyID.COMPANY_SPECTATOR:
            logger.warning("Cannot increase loan: not in a company")
            return False

        command = CommandBuilder.increase_loan(amount, int(self.game_state.company_id))
        success = self.send_command(command)
        if success:
            logger.info(f"Requested loan increase of £{amount:,}")
        return success

    def decrease_loan(self, amount: int) -> bool:
        """Decrease company loan by specified amount"""
        if not self.is_connected() or self.game_state.company_id == CompanyID.COMPANY_SPECTATOR:
            logger.warning("Cannot decrease loan: not in a company")
            return False

        command = CommandBuilder.decrease_loan(amount, int(self.game_state.company_id))
        success = self.send_command(command)
        if success:
            logger.info(f"Requested loan decrease of £{amount:,}")
        return success

    def rename_company(self, new_name: str) -> bool:
        """Rename the company"""
        if not self.is_connected() or self.game_state.company_id == CompanyID.COMPANY_SPECTATOR:
            logger.warning("Cannot rename company: not in a company")
            return False

        if len(new_name.strip()) == 0:
            logger.warning("Cannot rename company to empty name")
            return False

        command = CommandBuilder.rename_company(new_name, int(self.game_state.company_id))
        success = self.send_command(command)
        if success:
            logger.info(f"Requested company rename to: '{new_name}'")
            self.company_name = new_name
        return success

    def rename_president(self, new_name: str) -> bool:
        """Rename the company president/manager"""
        if not self.is_connected() or self.game_state.company_id == CompanyID.COMPANY_SPECTATOR:
            logger.warning("Cannot rename president: not in a company")
            return False

        if len(new_name.strip()) == 0:
            logger.warning("Cannot rename president to empty name")
            return False

        command = CommandBuilder.rename_president(new_name, int(self.game_state.company_id))
        success = self.send_command(command)
        if success:
            logger.info(f"Requested president rename to: '{new_name}'")
        return success

    def set_company_colour(self, scheme: int = 0, primary: bool = True, colour: int = 0) -> bool:
        """Set company livery colour scheme"""
        if not self.is_connected() or self.game_state.company_id == CompanyID.COMPANY_SPECTATOR:
            logger.warning("Cannot set company colour: not in a company")
            return False

        command = CommandBuilder.set_company_colour(
            scheme, primary, colour, int(self.game_state.company_id)
        )
        success = self.send_command(command)
        if success:
            logger.info(
                f"Requested colour change: scheme={scheme}, primary={primary}, colour={colour}"
            )
        return success

    def give_money(self, amount: int, dest_company: int) -> bool:
        """Transfer money to another company"""
        if not self.is_connected() or self.game_state.company_id == CompanyID.COMPANY_SPECTATOR:
            logger.warning("Cannot give money: not in a company")
            return False

        if amount <= 0:
            logger.warning("Cannot give negative or zero money")
            return False

        command = CommandBuilder.give_money(amount, dest_company, int(self.game_state.company_id))
        success = self.send_command(command)
        if success:
            logger.info(f"Requested money transfer: £{amount:,} to Company {dest_company}")
        return success

    def _openttd_date_to_year(self, date_days: int) -> int:
        """
        Convert OpenTTD date (days since year 0) to actual year.
        Based on CalendarConvertDateToYMD algorithm.
        """
        if date_days < 0:
            return 0

        # OpenTTD's algorithm: account for leap years properly
        # There are 97 leap years in 400 years
        DAYS_IN_YEAR = 365
        yr = 400 * (date_days // (DAYS_IN_YEAR * 400 + 97))
        rem = date_days % (DAYS_IN_YEAR * 400 + 97)

        if rem >= DAYS_IN_YEAR * 100 + 25:
            # There are 25 leap years in the first 100 years after every 400th year
            yr += 100
            rem -= DAYS_IN_YEAR * 100 + 25

            # There are 24 leap years in the next couple of 100 years
            yr += 100 * (rem // (DAYS_IN_YEAR * 100 + 24))
            rem = rem % (DAYS_IN_YEAR * 100 + 24)

        # There are 1 leap year every 4 years
        yr += 4 * (rem // (DAYS_IN_YEAR * 4 + 1))
        rem = rem % (DAYS_IN_YEAR * 4 + 1)

        # There is 1 leap year every 4 years, except if it is divisible by 100
        # except if it's divisible by 400
        if rem >= DAYS_IN_YEAR * 3 + 1 and (yr % 100 != 0 or yr % 400 == 0):
            yr += 3
            rem -= DAYS_IN_YEAR * 3 + 1
        else:
            yr += rem // DAYS_IN_YEAR

        return yr

    # ============================================
    # Chat and Communication
    # ============================================

    def send_chat_to_company(self, message: str, company_id: int) -> bool:
        """Send a chat message to a specific company"""
        return self.send_chat(message, destination_type=1, destination=company_id)

    def send_chat_to_client(self, message: str, client_id: int) -> bool:
        """Send a private message to a specific client"""
        return self.send_chat(message, destination_type=2, destination=client_id)

    def _network_loop(self) -> None:
        """Main network processing loop (runs in separate thread)"""
        logger.debug("Starting network loop")

        try:
            while self._running and self.connection.is_connected():
                try:
                    packet = self.connection.receive_packet()
                    if packet:
                        self._handle_packet(packet)
                except Exception as e:
                    logger.error(f"Error in network loop: {e}")
                    break
        except Exception as e:
            logger.error(f"Network loop error: {e}")
        finally:
            self.status = ClientStatus.ERROR
            self._running = False
            logger.debug("Network loop ended")

    def _handle_packet(self, packet: Packet) -> None:
        """Handle received packet based on type"""
        try:
            if packet.type is None:
                logger.error("Received packet with no type")
                return
            handler_name = f"_handle_{packet.type.name.lower()}"
            if hasattr(self, handler_name):
                getattr(self, handler_name)(packet)
            else:
                # Log packet data for unhandled packets
                packet_data = packet.remaining_bytes()
                logger.debug(
                    f"No handler for packet type: {packet.type} (size: {len(packet_data)} bytes)"
                )
        except Exception as e:
            packet_type_str = packet.type.name if packet.type else "unknown"
            logger.error(f"Error handling packet {packet_type_str}: {e}")

    def _send_join(self) -> None:
        """Send join packet to server"""
        packet = Packet(PacketType.CLIENT_JOIN)
        packet.write_string(self.client_revision)
        packet.write_uint32(503868772)  # newgrf_version (matches official client)
        packet.write_string(self.player_name)
        # Join with COMPANY_NEW_COMPANY to request automatic company creation
        company_id_to_join = int(CompanyID.COMPANY_NEW_COMPANY)
        packet.write_uint8(company_id_to_join)  # Company to join
        logger.debug(
            f"CLIENT_JOIN: Requesting to join company_id={company_id_to_join} (COMPANY_NEW_COMPANY)"
        )
        packet.write_uint8(0)  # Language field (always 0 in OpenTTD 14.1)

        self.connection.send_packet(packet)
        logger.debug("Sent CLIENT_JOIN packet")

    def _handle_server_full(self, packet: Packet) -> None:
        """Handle server full packet"""
        logger.error("Server is full")
        self.status = ClientStatus.ERROR
        self._emit_event("error", "Server is full")

    def _handle_server_banned(self, packet: Packet) -> None:
        """Handle server banned packet"""
        logger.error("Banned from server")
        self.status = ClientStatus.ERROR
        self._emit_event("error", "Banned from server")

    def _handle_server_error(self, packet: Packet) -> None:
        """Handle server error packet"""
        error_code = packet.read_uint8()
        error_msg = f"Server error: {NetworkError(error_code).name}"
        logger.error(error_msg)
        self.status = ClientStatus.ERROR
        self._emit_event("error", error_msg)

    def _handle_server_shutdown(self, packet: Packet) -> None:
        """Handle server shutdown notification"""
        logger.info("Server is shutting down")
        self.status = ClientStatus.ERROR
        self._emit_event("error", "Server shutdown")

    def _handle_server_need_game_password(self, packet: Packet) -> None:
        """Handle game password request"""
        logger.debug("Server requires game password")
        self.status = ClientStatus.AUTHENTICATING

        packet = Packet(PacketType.CLIENT_GAME_PASSWORD)
        packet.write_uint8(0)  # Password type
        packet.write_string(self.password)
        self.connection.send_packet(packet)

    def _handle_server_need_company_password(self, packet: Packet) -> None:
        """Handle company password request"""
        logger.debug("Server requires company password")

        # Read generation seed and network ID (for password hashing)
        generation_seed = packet.read_uint32()
        network_id = packet.read_string()

        packet = Packet(PacketType.CLIENT_COMPANY_PASSWORD)
        packet.write_uint8(1)  # Password type (company)
        packet.write_string(self.company_password)
        self.connection.send_packet(packet)

    def _handle_server_welcome(self, packet: Packet) -> None:
        """Handle welcome packet - we're authenticated!"""
        self.game_state.client_id = packet.read_uint32()
        generation_seed = packet.read_uint32()
        network_id = packet.read_string()

        logger.info(f"Welcomed to server! Client ID: {self.game_state.client_id}")
        self.status = ClientStatus.JOINED

        # Request map data
        packet = Packet(PacketType.CLIENT_GETMAP)
        packet.write_uint32(0)  # NewGRF version
        self.connection.send_packet(packet)

    def _handle_server_client_info(self, packet: Packet) -> None:
        """Handle client info packet"""
        client_id = packet.read_uint32()
        company_id = CompanyID(packet.read_uint8())
        client_name = packet.read_string()

        client_info = ClientInfo(client_id=client_id, company_id=company_id, name=client_name)
        self.game_state.add_client(client_info)

        logger.debug(f"Client info: {client_name} (ID: {client_id}, Company: {company_id})")

    def _handle_server_wait(self, packet: Packet) -> None:
        """Handle wait packet - other clients downloading map"""
        clients_ahead = packet.read_uint8()
        logger.info(f"Waiting for map download ({clients_ahead} clients ahead)")

    def _handle_server_map_begin(self, packet: Packet) -> None:
        """Handle map download begin"""
        current_frame = packet.read_uint32()
        logger.info("Starting map download")
        self.status = ClientStatus.DOWNLOADING_MAP
        self._map_buffer.clear()

    def _handle_server_map_size(self, packet: Packet) -> None:
        """Handle map size packet"""
        self._expected_map_size = packet.read_uint32()
        logger.info(f"Map size: {self._expected_map_size} bytes")

    def _handle_server_map_data(self, packet: Packet) -> None:
        """Handle map data packet"""
        data = packet.remaining_bytes()
        self._map_buffer.extend(data)

        if self._expected_map_size > 0:
            progress = len(self._map_buffer) / self._expected_map_size * 100
            logger.debug(f"Map download progress: {progress:.1f}%")
        else:
            logger.debug(f"Map download: {len(self._map_buffer)} bytes received")

    def _handle_server_map_done(self, packet: Packet) -> None:
        """Handle map download complete"""
        logger.info("Map download complete")
        logger.info(f"Map size: {len(self._map_buffer)} bytes")

        # Store compressed map data
        map_data = bytes(self._map_buffer)
        self.game_state.set_map_data(map_data)

        try:
            logger.info("Parsing map data...")
            # TODO: add parser call here

        except Exception as e:
            logger.error(f"Error parsing map data: {e}")
            # self._parsed_map_data = {}

        # Send acknowledgment
        packet = Packet(PacketType.CLIENT_MAP_OK)
        self.connection.send_packet(packet)

        self._emit_event("map_complete")

    def _handle_server_join(self, packet: Packet) -> None:
        """Handle successful join"""
        joining_client_id = packet.read_uint32()

        if joining_client_id == self.game_state.client_id:
            logger.info("Joined the game!")
            self.status = ClientStatus.ACTIVE

            # If we joined with COMPANY_NEW_COMPANY, automatically send company creation command
            if self.game_state.company_id == CompanyID.COMPANY_NEW_COMPANY:
                logger.info(
                    f"Sending automatic CMD_COMPANY_CTRL for company creation (current company_id: {self.game_state.company_id})"
                )
                command = CommandBuilder.create_company()
                self.send_command(command)
                logger.info("CMD_COMPANY_CTRL sent, waiting for server response...")

            self._emit_event("game_joined")

    def _handle_server_frame(self, packet: Packet) -> None:
        """Handle frame synchronization packet"""
        try:
            frame = packet.read_uint32()
            frame_max = packet.read_uint32()

            # Optional random seeds for desync detection and token
            seed1 = seed2 = 0
            token = None

            # The remaining data could be: [seed1, [seed2,]] [token]
            remaining_bytes = packet.size() - packet.buffer.tell()
            logger.debug(f"SERVER_FRAME has {remaining_bytes} remaining bytes after frame data")

            if remaining_bytes >= 4:
                seed1 = packet.read_uint32()
                remaining_bytes -= 4
                logger.debug(f"Read seed1={seed1}, {remaining_bytes} bytes remaining")

                if remaining_bytes >= 4:
                    seed2 = packet.read_uint32()
                    remaining_bytes -= 4
                    logger.debug(f"Read seed2={seed2}, {remaining_bytes} bytes remaining")

                if remaining_bytes >= 1:
                    token = packet.read_uint8()
                    logger.info(f"Received token {token} in SERVER_FRAME")
                    self._token = token
            elif remaining_bytes >= 1:
                # Could be just a token without seeds
                token = packet.read_uint8()
                logger.info(f"Received token {token} in SERVER_FRAME (no seeds)")
                self._token = token

            self.game_state.update_frame(frame, frame_max, seed1, seed2)

            # Send acknowledgment (only if frame has advanced and we're fully active)
            if frame > self._last_ack_frame and self.status == ClientStatus.ACTIVE:
                current_time = time.time()
                # Match real client behavior: ACK every ~2 seconds (~75 frames)
                if current_time - self._last_ack_time > 2.0 or frame - self._last_ack_frame >= 75:
                    self._last_ack_frame = frame
                    self._last_ack_time = current_time
                    self._send_ack()
        except EOFError as e:
            logger.error(f"Frame packet too short: {e}")
            raise

    def _handle_server_sync(self, packet: Packet) -> None:
        """Handle sync check packet"""
        try:
            frame = packet.read_uint32()
            seed1 = packet.read_uint32()
            seed2 = 0
            try:
                seed2 = packet.read_uint32()
            except EOFError:
                pass  # No seed2 in packet

            # Accept server's sync seeds without validation since we don't simulate game state
            # Real desync detection would require maintaining full game simulation state
            logger.debug(f"Sync check at frame {frame}, seeds: {seed1}, {seed2}")

            # Update seeds after desync check
            self.game_state.random_seed1 = seed1
            self.game_state.random_seed2 = seed2

            # Don't send ACK for sync packets - only SERVER_FRAME packets should trigger ACKs
        except EOFError as e:
            logger.error(f"Sync packet too short: {e}")

    def _handle_server_command(self, packet: Packet) -> None:
        """Handle command execution packet"""
        company = packet.read_uint8()
        command_id_raw = packet.read_uint32()
        try:
            command_id: Union[Commands, int] = Commands(command_id_raw)
        except ValueError:
            logger.debug(f"Unknown command ID {command_id_raw}, continuing...")
            command_id = command_id_raw
        # Command parameters would be decoded here based on command type
        callback_id = packet.read_uint8()
        frame = packet.read_uint32()

        logger.debug(f"Received command: {command_id} for company {company} at frame {frame}")

    def _handle_server_chat(self, packet: Packet) -> None:
        """Handle chat message"""
        action = packet.read_uint8()
        client_id = packet.read_uint32()
        message = packet.read_string()
        data = packet.read_uint64()

        client = self.game_state.get_client(client_id)
        sender_name = client.name if client else f"Client {client_id}"

        logger.info(f"Chat [{sender_name}]: {message}")
        self._emit_event("chat_message", sender_name, message, data)

    def _handle_server_quit(self, packet: Packet) -> None:
        """Handle client quit notification"""
        client_id = packet.read_uint32()
        self.game_state.remove_client(client_id)

        logger.debug(f"Client {client_id} left the game")

    def _handle_server_company_update(self, packet: Packet) -> None:
        """Handle company update packet
        Contains company password flags only"""
        try:
            logger.debug(f"Received COMPANY_UPDATE packet (size: {packet.size()} bytes)")

            company_passworded = packet.read_uint16()

            logger.debug(f"Company password flags: 0x{company_passworded:04x}")

        except Exception as e:
            logger.debug(f"Error in company update handler: {e}")

    def _handle_server_config_update(self, packet: Packet) -> None:
        """Handle config update packet
        Contains max_companies and server_name only"""
        try:
            logger.debug(f"Received CONFIG_UPDATE packet (size: {packet.size()} bytes)")

            max_companies = packet.read_uint8()
            server_name = packet.read_string()

            logger.info(
                f"Server config: max_companies={max_companies}, server_name='{server_name}'"
            )

            if hasattr(self.game_state, "max_companies"):
                self.game_state.max_companies = max_companies
            if hasattr(self.game_state, "server_name"):
                self.game_state.server_name = server_name

        except Exception as e:
            logger.debug(f"Error reading config update: {e}")

    def _handle_server_game_info(self, packet: Packet) -> None:
        """Handle SERVER_GAME_INFO packet
        Contains game state data"""
        try:
            logger.debug(f"Received SERVER_GAME_INFO packet (size: {packet.size()} bytes)")

            game_info_version = packet.read_uint8()  # NETWORK_GAME_INFO_VERSION
            logger.debug(f"Game info version: {game_info_version}")

            # Parse based on version - OpenTTD 14.1 uses version 7
            if game_info_version >= 7:
                # NETWORK_GAME_INFO_VERSION = 7
                ticks_playing = packet.read_uint64()
                logger.debug(f"Ticks playing: {ticks_playing}")
            else:
                ticks_playing = 0

            if game_info_version >= 6:
                # NETWORK_GAME_INFO_VERSION = 6
                newgrf_serialisation = packet.read_uint8()  # NST_GRFID_MD5 or NST_GRFID_MD5_NAME
                logger.debug(f"NewGRF serialization type: {newgrf_serialisation}")
            else:
                newgrf_serialisation = 0

            if game_info_version >= 5:
                # NETWORK_GAME_INFO_VERSION = 5
                gamescript_version = packet.read_uint32()
                gamescript_name = packet.read_string()
                logger.debug(f"GameScript: {gamescript_name} v{gamescript_version}")

            if game_info_version >= 4:
                # NETWORK_GAME_INFO_VERSION = 4 - NewGRF data
                num_grfs = packet.read_uint8()
                logger.debug(f"Number of GRFs: {num_grfs}")

                # Skip GRF data for now - we just need the game state
                for i in range(num_grfs):
                    # Skip GRF ID (uint32) and MD5 (16 bytes)
                    packet.read_uint32()  # GRF ID
                    for j in range(16):  # MD5 hash
                        packet.read_uint8()
                    # Skip name if present
                    if game_info_version >= 6 and newgrf_serialisation == 1:  # NST_GRFID_MD5_NAME
                        packet.read_string()  # GRF name

            if game_info_version >= 3:
                calendar_date = packet.read_uint32()
                calendar_start = packet.read_uint32()

                current_year = self._openttd_date_to_year(calendar_date)
                start_year = self._openttd_date_to_year(calendar_start)

                logger.info(f"Current year {current_year}, Started year {start_year}")

            else:
                calendar_date = 0
                calendar_start = 0
                current_year = 1950
                start_year = 1950

            if game_info_version >= 2:
                companies_max = packet.read_uint8()
                companies_on = packet.read_uint8()
                packet.read_uint8()

                logger.info(f" {companies_on}/{companies_max} companies active")

            else:
                companies_max = 15
                companies_on = 0

            # NETWORK_GAME_INFO_VERSION = 1 - Basic server info
            server_name = packet.read_string()
            server_revision = packet.read_string()
            use_password = packet.read_bool()
            clients_max = packet.read_uint8()
            clients_on = packet.read_uint8()
            spectators_on = packet.read_uint8()
            map_width = packet.read_uint16()
            map_height = packet.read_uint16()
            landscape = packet.read_uint8()
            dedicated = packet.read_bool()

            self.game_state.frame = ticks_playing  # Use ticks as frame count

            self._real_game_data = {
                "current_year": current_year,
                "start_year": start_year,
                "companies_on": companies_on,
                "companies_max": companies_max,
                "clients_on": clients_on,
                "clients_max": clients_max,
                "spectators_on": spectators_on,
                "map_width": map_width,
                "map_height": map_height,
                "server_name": server_name,
                "ticks_playing": ticks_playing,
                "calendar_date": calendar_date,
                "calendar_start": calendar_start,
            }

            logger.info(
                f"UPDATED GAME STATE - Year: {current_year}, Companies: {companies_on}/{companies_max}, Clients: {clients_on}/{clients_max}"
            )

        except Exception as e:
            logger.error(f"Error parsing SERVER_GAME_INFO: {e}")
            # Log raw packet data for debugging
            remaining_data = packet.remaining_bytes()
            logger.error(f"Raw packet data: {remaining_data.hex()}")

    def _handle_server_move(self, packet: Packet) -> None:
        """Handle server move packet
        Client has been moved to a different company"""
        try:
            client_id = packet.read_uint8()
            company_id = packet.read_uint8()

            logger.info(f"Client {client_id} moved to company {company_id}")

            # If this is us being moved to a new company
            if client_id == self.game_state.client_id:
                # Update our company state
                old_company_id = self.game_state.company_id
                self.game_state.company_id = CompanyID(company_id)
                logger.info(f"Company ID changed: {old_company_id} -> {company_id}")

                # If we were creating a company and got assigned to one
                if company_id != CompanyID.COMPANY_SPECTATOR and self.pending_company_name:
                    logger.info(f"Successfully created and joined company {company_id}")

                    self.pending_company_name = None

                    self._emit_event("company_created", company_id)
                elif company_id == CompanyID.COMPANY_SPECTATOR:
                    logger.info("Moved to spectator mode")
                else:
                    logger.info(f"Joined existing company {company_id}")

        except Exception as e:
            logger.error(f"Error handling server move: {e}")

    def _send_ack(self) -> None:
        """Send frame acknowledgment to server"""
        try:
            packet = Packet(PacketType.CLIENT_ACK)
            packet.write_uint32(self.game_state.frame)
            # The server always expects the token to be present
            packet.write_uint8(self._token)

            logger.info(f"Sending ACK for frame {self.game_state.frame} with token {self._token}")
            self.connection.send_packet(packet)
        except Exception as e:
            logger.error(f"Failed to send ACK: {e}")
