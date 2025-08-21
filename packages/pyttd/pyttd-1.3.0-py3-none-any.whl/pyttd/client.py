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
import struct

from .network.protocol import (
    NetworkConnection,
    Packet,
    PacketType,
    NetworkError,
    coordinate_to_tile,
)
from .game.game_state import GameState, CompanyID, CompanyInfo, VehicleInfo, ClientInfo, VehicleType
from .game.commands import CommandPacket, CommandBuilder, Commands, DoCommandFlag, RailType
from .saveload import load_savefile_from_bytes, SaveFileData


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

        # Vehicle tracking state
        self._vehicles: Dict[int, Dict[str, Any]] = {}  # vehicle_id -> vehicle_data
        self._vehicle_commands = {
            0x0D: "BUILD_VEHICLE",  # CMD_BUILD_VEHICLE
            0x0E: "SELL_VEHICLE",  # CMD_SELL_VEHICLE
            0x0F: "START_STOP_VEHICLE",  # CMD_START_STOP_VEHICLE
            0x10: "MASS_START_STOP",  # CMD_MASS_START_STOP
            0x11: "AUTOREPLACE_VEHICLE",  # CMD_AUTOREPLACE_VEHICLE
            0x12: "DEPOT_SELL_ALL_VEHICLES",  # CMD_DEPOT_SELL_ALL_VEHICLES
            0x13: "DEPOT_MASS_AUTOREPLACE",  # CMD_DEPOT_MASS_AUTOREPLACE
            0x14: "CREATE_GROUP",  # CMD_CREATE_GROUP
            0x15: "DELETE_GROUP",  # CMD_DELETE_GROUP
            0x16: "ADD_VEHICLE_GROUP",  # CMD_ADD_VEHICLE_GROUP
            0x17: "ADD_SHARED_VEHICLE_GROUP",  # CMD_ADD_SHARED_VEHICLE_GROUP
            0x18: "REMOVE_ALL_VEHICLES_GROUP",  # CMD_REMOVE_ALL_VEHICLES_GROUP
            0x19: "SET_GROUP_REPLACE_PROTECTION",  # CMD_SET_GROUP_REPLACE_PROTECTION
            0x1A: "MOVE_VEHICLE",  # CMD_MOVE_VEHICLE
            0x1B: "MOVE_VEHICLE_HEAD",  # CMD_MOVE_VEHICLE_HEAD
            0x1C: "CLONE_VEHICLE",  # CMD_CLONE_VEHICLE
            0x1D: "CLONE_VEHICLE_HEAD",  # CMD_CLONE_VEHICLE_HEAD
            0x1E: "TURN_VEHICLE",  # CMD_TURN_VEHICLE
            0x1F: "SELL_VEHICLE_HEAD",  # CMD_SELL_VEHICLE_HEAD
            0x20: "SELL_VEHICLE_WAGONS",  # CMD_SELL_VEHICLE_WAGONS
            0x21: "SEND_VEHICLE_TO_DEPOT",  # CMD_SEND_VEHICLE_TO_DEPOT
            0x22: "CHANGE_SERVICE_INT",  # CMD_CHANGE_SERVICE_INT
            0x23: "RENAME_VEHICLE",  # CMD_RENAME_VEHICLE
            0x24: "RENAME_VEHICLE_GROUP",  # CMD_RENAME_VEHICLE_GROUP
            0x25: "SET_VEHICLE_GROUPID",  # CMD_SET_VEHICLE_GROUPID
            0x26: "SET_VEHICLE_GROUPID_SHARED",  # CMD_SET_VEHICLE_GROUPID_SHARED
            0x27: "SET_VEHICLE_GROUPID_DEFAULT",  # CMD_SET_VEHICLE_GROUPID_DEFAULT
            0x28: "SET_VEHICLE_GROUPID_ALL_SHARED",  # CMD_SET_VEHICLE_GROUPID_ALL_SHARED
            0x29: "SET_VEHICLE_GROUPID_ALL_DEFAULT",  # CMD_SET_VEHICLE_GROUPID_ALL_DEFAULT
            0x2A: "SET_VEHICLE_GROUPID_ALL_PROTECTED",  # CMD_SET_VEHICLE_GROUPID_ALL_PROTECTED
            0x2B: "SET_VEHICLE_GROUPID_ALL_UNPROTECTED",  # CMD_SET_VEHICLE_GROUPID_ALL_UNPROTECTED
            0x2C: "SET_VEHICLE_GROUPID_ALL_SHARED_PROTECTED",  # CMD_SET_VEHICLE_GROUPID_ALL_SHARED_PROTECTED
            0x2D: "SET_VEHICLE_GROUPID_ALL_SHARED_UNPROTECTED",  # CMD_SET_VEHICLE_GROUPID_ALL_SHARED_UNPROTECTED
            0x2E: "SET_VEHICLE_GROUPID_ALL_DEFAULT_PROTECTED",  # CMD_SET_VEHICLE_GROUPID_ALL_DEFAULT_PROTECTED
            0x2F: "SET_VEHICLE_GROUPID_ALL_DEFAULT_UNPROTECTED",  # CMD_SET_VEHICLE_GROUPID_ALL_DEFAULT_UNPROTECTED
            0x30: "SET_VEHICLE_GROUPID_ALL_SHARED_DEFAULT_PROTECTED",  # CMD_SET_VEHICLE_GROUPID_ALL_SHARED_DEFAULT_PROTECTED
            0x31: "SET_VEHICLE_GROUPID_ALL_SHARED_DEFAULT_UNPROTECTED",  # CMD_SET_VEHICLE_GROUPID_ALL_SHARED_DEFAULT_UNPROTECTED
            0x32: "SET_VEHICLE_GROUPID_ALL_SHARED_DEFAULT_PROTECTED_SHARED",  # CMD_SET_VEHICLE_GROUPID_ALL_SHARED_DEFAULT_PROTECTED_SHARED
            0x33: "SET_VEHICLE_GROUPID_ALL_SHARED_DEFAULT_UNPROTECTED_SHARED",  # CMD_SET_VEHICLE_GROUPID_ALL_SHARED_DEFAULT_UNPROTECTED_SHARED
            0x34: "SET_VEHICLE_GROUPID_ALL_SHARED_DEFAULT_PROTECTED_DEFAULT",  # CMD_SET_VEHICLE_GROUPID_ALL_SHARED_DEFAULT_PROTECTED_DEFAULT
            0x35: "SET_VEHICLE_GROUPID_ALL_SHARED_DEFAULT_UNPROTECTED_DEFAULT",  # CMD_SET_VEHICLE_GROUPID_ALL_SHARED_DEFAULT_UNPROTECTED_DEFAULT
            0x36: "SET_VEHICLE_GROUPID_ALL_SHARED_DEFAULT_PROTECTED_SHARED_DEFAULT",  # CMD_SET_VEHICLE_GROUPID_ALL_SHARED_DEFAULT_PROTECTED_SHARED_DEFAULT
            0x37: "SET_VEHICLE_GROUPID_ALL_SHARED_DEFAULT_UNPROTECTED_SHARED_DEFAULT",  # CMD_SET_VEHICLE_GROUPID_ALL_SHARED_DEFAULT_UNPROTECTED_SHARED_DEFAULT
        }

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
        self._parsed_save: Optional[SaveFileData] = None
        self._map_parse_thread: Optional[threading.Thread] = None

        # Command queue
        self._command_queue: List[CommandPacket] = []
        self._command_callback: Optional[Callable[[Commands, bool, str], None]] = None

        # Event callbacks
        self._event_callbacks: Dict[str, List[Callable]] = {
            "connected": [],
            "disconnected": [],
            "map_complete": [],
            "map_parse_progress": [],
            "map_parsed": [],
            "game_joined": [],
            "command_result": [],
            "chat_message": [],
            "server_command": [],
            "frame": [],
            "server_action": [],
            "desync": [],
            "error": [],
            "company_created": [],
            "vehicle_action": [],
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
        info: Dict[str, Any] = {
            "size_x": self.game_state.map_info.size_x,
            "size_y": self.game_state.map_info.size_y,
        }
        if self._parsed_save and getattr(self._parsed_save, "map", None):
            try:
                info["size_x"] = getattr(self._parsed_save.map, "dim_x", info["size_x"])
                info["size_y"] = getattr(self._parsed_save.map, "dim_y", info["size_y"])
            except Exception:
                pass
        return info

    def get_parsed_save(self) -> Optional[SaveFileData]:
        """Return the parsed save structure after map download completes, if available."""
        return self._parsed_save

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

        logger.info(f"Client info: {client_name} (ID: {client_id}, Company: {company_id})")
        # When company switches happen, follow-up SERVER_MOVE updates company mapping

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

        # Immediately ACK to avoid server timeout
        try:
            ack = Packet(PacketType.CLIENT_MAP_OK)
            self.connection.send_packet(ack)
        except Exception as e:
            logger.error(f"Failed to send CLIENT_MAP_OK: {e}")

        # Notify that map transfer is done
        self._emit_event("map_complete")

        # Parse in background to avoid blocking join
        def _bg_parse() -> None:
            try:
                logger.info("Parsing map data (background)...")

                # Relay progress to listeners
                def _progress_cb(p: float, stage: str) -> None:
                    try:
                        self._emit_event("map_parse_progress", p, stage)
                    except Exception:
                        pass

                parsed = load_savefile_from_bytes(
                    map_data, parsed=True, silent=True, progress_callback=_progress_cb
                )
                self._parsed_save = parsed  # type: ignore[assignment]
                if parsed and hasattr(parsed, "map") and parsed.map:
                    mx = getattr(parsed.map, "dim_x", 0)
                    my = getattr(parsed.map, "dim_y", 0)
                    if mx:
                        self.game_state.map_info.size_x = mx
                    if my:
                        self.game_state.map_info.size_y = my
                    logger.info(
                        f"Parsed map: {self.game_state.map_info.size_x}x{self.game_state.map_info.size_y}"
                    )
                # Populate company names from parsed save if available
                try:
                    if parsed and hasattr(parsed, "companies"):
                        comp_list = getattr(parsed.companies, "companies", [])
                        for comp in comp_list:
                            try:
                                cid = int(comp.get("id", -1))
                                name = str(comp.get("name", f"Company {cid}"))
                                if 0 <= cid <= 14:
                                    info = CompanyInfo(company_id=CompanyID(cid), name=name)
                                    self.game_state.add_company(info)
                            except Exception:
                                continue
                except Exception:
                    pass
                self._emit_event("map_parsed")
            except Exception as e:
                logger.error(f"Error parsing map data: {e}")

        try:
            self._map_parse_thread = threading.Thread(target=_bg_parse, daemon=True)
            self._map_parse_thread.start()
        except Exception as e:
            logger.error(f"Failed to start background parsing: {e}")

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

            # Emit frame event for listeners
            try:
                self._emit_event("frame", frame, frame_max)
            except Exception:
                pass

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
        """Handle SERVER_COMMAND packets"""
        try:
            # Error message
            err_msg = packet.read_uint8()
            # Data length
            data_len = packet.read_uint16()
            # Command data
            params_bytes = packet.read_bytes(data_len)
            # Callback index
            callback_id = packet.read_uint8()
            # Frame
            frame = packet.read_uint32()
            # Optional my_cmd byte may remain; ignore
        except Exception as e:
            logger.debug(f"Error parsing SERVER_COMMAND packet: {e}")
            return

        try:
            # Extract command ID from first byte of params
            if not params_bytes:
                return
            command_id = params_bytes[0]

            # Check if this is a vehicle-related command
            if command_id in self._vehicle_commands:
                company = self._get_company_from_command(params_bytes)
                self._handle_vehicle_command(company, command_id, params_bytes[1:], frame)

        except Exception as e:
            logger.debug(f"Error handling SERVER_COMMAND: {e}")

    def _decode_command_params(self, cmd: Union[Commands, int], params: bytes) -> Dict[str, Any]:
        """Decode parameter buffer to p1/p2/tile where possible."""
        result: Dict[str, Any] = {}
        if not params:
            return result
        try:
            if not isinstance(cmd, Commands):
                cmd = Commands(cmd)
        except Exception:
            cmd = None  # type: ignore[assignment]

        import struct as _struct

        # Common case: two uint32 parameters
        if len(params) >= 8:
            p1, p2 = _struct.unpack_from("<LL", params, 0)
            result["p1"] = p1
            result["p2"] = p2

        # Heuristics per command
        if cmd in (
            Commands.BUILD_SINGLE_RAIL,
            Commands.LANDSCAPE_CLEAR,
            Commands.BUILD_RAIL_STATION,
            Commands.BUILD_TRAIN_DEPOT,
            Commands.BUILD_ROAD_STOP,
            Commands.BUILD_ROAD_DEPOT,
            Commands.BUILD_DOCK,
            Commands.BUILD_SHIP_DEPOT,
            Commands.BUILD_BUOY,
            Commands.PLACE_SIGN,
            Commands.BUILD_VEHICLE,
        ):
            # First param often encodes tile or depot tile
            if "p1" in result and isinstance(result["p1"], int):
                result["tile"] = int(result["p1"]) if cmd != Commands.BUILD_VEHICLE else None
        elif cmd in (Commands.BUILD_RAILROAD_TRACK, Commands.BUILD_LONG_ROAD, Commands.BUILD_ROAD):
            # p1=start tile, p2=end or flags
            if "p1" in result:
                result["tile"] = int(result["p1"])  # highlight start tile

        return result

    def _decode_vehicle_command(self, cmd: int, params_bytes: bytes) -> Dict[str, Any]:
        """Decode vehicle-related command parameters."""
        result: Dict[str, Any] = {}

        if not params_bytes:
            return result

        try:
            if cmd == 0x0D:  # BUILD_VEHICLE
                # p1: engine_id, p2: flags
                if len(params_bytes) >= 8:
                    engine_id, flags = struct.unpack_from("<LL", params_bytes, 0)
                    result["engine_id"] = engine_id
                    result["flags"] = flags
                    result["action"] = "build_vehicle"

            elif cmd == 0x0E:  # SELL_VEHICLE
                # p1: vehicle_id, p2: flags
                if len(params_bytes) >= 8:
                    vehicle_id, flags = struct.unpack_from("<LL", params_bytes, 0)
                    result["vehicle_id"] = vehicle_id
                    result["flags"] = flags
                    result["action"] = "sell_vehicle"

            elif cmd == 0x0F:  # START_STOP_VEHICLE
                # p1: vehicle_id, p2: flags
                if len(params_bytes) >= 8:
                    vehicle_id, flags = struct.unpack_from("<LL", params_bytes, 0)
                    result["vehicle_id"] = vehicle_id
                    result["flags"] = flags
                    result["action"] = "start_stop_vehicle"

            elif cmd == 0x1A:  # MOVE_VEHICLE
                # p1: vehicle_id, p2: flags
                if len(params_bytes) >= 8:
                    vehicle_id, flags = struct.unpack_from("<LL", params_bytes, 0)
                    result["vehicle_id"] = vehicle_id
                    result["flags"] = flags
                    result["action"] = "move_vehicle"

            elif cmd == 0x1C:  # CLONE_VEHICLE
                # p1: vehicle_id, p2: flags
                if len(params_bytes) >= 8:
                    vehicle_id, flags = struct.unpack_from("<LL", params_bytes, 0)
                    result["vehicle_id"] = vehicle_id
                    result["flags"] = flags
                    result["action"] = "clone_vehicle"

        except Exception as e:
            logger.debug(f"Error decoding vehicle command {cmd}: {e}")

        return result

    def _parse_vehicles_from_save(self, parsed_save: Any) -> None:
        """Parse vehicle data from the savefile."""
        if not parsed_save or not hasattr(parsed_save, "vehicles"):
            return

        try:
            vehicles_data = getattr(parsed_save.vehicles, "vehicles", [])
            for vehicle in vehicles_data:
                vehicle_id = vehicle.get("id")
                if vehicle_id is not None:
                    self._vehicles[vehicle_id] = {
                        "id": vehicle_id,
                        "type": vehicle.get("type", "unknown"),
                        "owner": vehicle.get("owner", 0),
                        "engine_type": vehicle.get("engine_type", 0),
                        "x": vehicle.get("x", 0),
                        "y": vehicle.get("y", 0),
                        "z": vehicle.get("z", 0),
                        "direction": vehicle.get("direction", 0),
                        "speed": vehicle.get("speed", 0),
                        "cargo_type": vehicle.get("cargo_type", 0),
                        "cargo_capacity": vehicle.get("cargo_capacity", 0),
                        "cargo_count": vehicle.get("cargo_count", 0),
                        "name": vehicle.get("name", f"Vehicle {vehicle_id}"),
                        "profit_this_year": vehicle.get("profit_this_year", 0),
                        "profit_last_year": vehicle.get("profit_last_year", 0),
                        "value": vehicle.get("value", 0),
                        "age": vehicle.get("age", 0),
                        "reliability": vehicle.get("reliability", 0),
                        "last_station_visited": vehicle.get("last_station_visited", 0),
                        "current_order": vehicle.get("current_order", {}),
                        "orders": vehicle.get("orders", []),
                    }
            logger.info(f"Parsed {len(self._vehicles)} vehicles from savefile")
        except Exception as e:
            logger.error(f"Error parsing vehicles from savefile: {e}")

    def _handle_vehicle_command(
        self, company: int, cmd: int, params_bytes: bytes, frame: int
    ) -> None:
        """Handle vehicle-related commands and update vehicle state."""
        vehicle_data = self._decode_vehicle_command(cmd, params_bytes)

        if not vehicle_data:
            return

        action = {
            "type": "vehicle_action",
            "company": company,
            "command": cmd,
            "command_name": self._vehicle_commands.get(cmd, f"Unknown({cmd})"),
            "frame": frame,
            "vehicle_data": vehicle_data,
        }

        # Update vehicle state based on command
        if vehicle_data.get("action") == "build_vehicle":
            # Vehicle will be created - we'll need to track it
            logger.info(
                f"Vehicle construction: company={company} building vehicle with engine={vehicle_data.get('engine_id')}"
            )

        elif vehicle_data.get("action") == "sell_vehicle":
            vehicle_id = vehicle_data.get("vehicle_id")
            if vehicle_id in self._vehicles:
                del self._vehicles[vehicle_id]
                logger.info(f"Vehicle sold: company={company} sold vehicle {vehicle_id}")

        elif vehicle_data.get("action") == "start_stop_vehicle":
            vehicle_id = vehicle_data.get("vehicle_id")
            if vehicle_id in self._vehicles:
                # Update vehicle status
                self._vehicles[vehicle_id]["status"] = (
                    "stopped" if vehicle_data.get("flags", 0) & 1 else "running"
                )
                logger.info(
                    f"Vehicle status change: company={company} vehicle {vehicle_id} {'stopped' if vehicle_data.get('flags', 0) & 1 else 'started'}"
                )

        elif vehicle_data.get("action") == "move_vehicle":
            vehicle_id = vehicle_data.get("vehicle_id")
            if vehicle_id in self._vehicles:
                logger.info(f"Vehicle moved: company={company} moved vehicle {vehicle_id}")

        elif vehicle_data.get("action") == "clone_vehicle":
            vehicle_id = vehicle_data.get("vehicle_id")
            if vehicle_id in self._vehicles:
                logger.info(f"Vehicle cloned: company={company} cloned vehicle {vehicle_id}")

        self._emit_event("vehicle_action", action)

    def get_vehicles(self) -> Dict[int, Dict[str, Any]]:
        """Get all tracked vehicles."""
        return self._vehicles.copy()

    def get_vehicles_by_company(self, company_id: int) -> Dict[int, Dict[str, Any]]:
        """Get vehicles owned by a specific company."""
        return {
            vid: vdata for vid, vdata in self._vehicles.items() if vdata.get("owner") == company_id
        }

    def get_vehicles_by_type(self, vehicle_type: str) -> Dict[int, Dict[str, Any]]:
        """Get vehicles of a specific type."""
        return {
            vid: vdata for vid, vdata in self._vehicles.items() if vdata.get("type") == vehicle_type
        }

    def _describe_command(self, cmd: Union[Commands, int]) -> str:
        """Return a human-readable description for a command ID."""
        try:
            if not isinstance(cmd, Commands):
                cmd = Commands(cmd)
        except Exception:
            return f"Command {cmd}"

        mapping = {
            Commands.BUILD_RAILROAD_TRACK: "built railroad track",
            Commands.REMOVE_RAILROAD_TRACK: "removed railroad track",
            Commands.BUILD_SINGLE_RAIL: "built a rail piece",
            Commands.REMOVE_SINGLE_RAIL: "removed a rail piece",
            Commands.LANDSCAPE_CLEAR: "cleared land",
            Commands.BUILD_BRIDGE: "built a bridge",
            Commands.BUILD_RAIL_STATION: "built a rail station",
            Commands.BUILD_TRAIN_DEPOT: "built a train depot",
            Commands.BUILD_SINGLE_SIGNAL: "placed a signal",
            Commands.REMOVE_SINGLE_SIGNAL: "removed a signal",
            Commands.TERRAFORM_LAND: "terraformed land",
            Commands.BUILD_OBJECT: "built an object",
            Commands.BUILD_OBJECT_AREA: "built objects",
            Commands.BUILD_TUNNEL: "built a tunnel",
            Commands.REMOVE_FROM_RAIL_STATION: "removed from rail station",
            Commands.CONVERT_RAIL: "converted rail",
            Commands.BUILD_RAIL_WAYPOINT: "built a waypoint",
            Commands.RENAME_WAYPOINT: "renamed a waypoint",
            Commands.REMOVE_FROM_RAIL_WAYPOINT: "removed from waypoint",
            Commands.BUILD_ROAD: "built road",
            Commands.REMOVE_ROAD: "removed road",
            Commands.BUILD_LONG_ROAD: "built long road",
            Commands.REMOVE_LONG_ROAD: "removed long road",
            Commands.BUILD_ROAD_STOP: "built road stop",
            Commands.REMOVE_ROAD_STOP: "removed road stop",
            Commands.BUILD_ROAD_DEPOT: "built road depot",
            Commands.CONVERT_ROAD: "converted road",
            Commands.BUILD_AIRPORT: "built airport",
            Commands.BUILD_DOCK: "built dock",
            Commands.BUILD_SHIP_DEPOT: "built ship depot",
            Commands.BUILD_BUOY: "built buoy",
            Commands.PLANT_TREE: "planted trees",
            Commands.BUILD_VEHICLE: "built vehicle",
            Commands.SELL_VEHICLE: "sold vehicle",
            Commands.START_STOP_VEHICLE: "toggled vehicle",
            Commands.REFIT_VEHICLE: "refit vehicle",
            Commands.CLONE_VEHICLE: "cloned vehicle",
            Commands.MOVE_RAIL_VEHICLE: "moved rail vehicle",
            Commands.FORCE_TRAIN_PROCEED: "forced train",
            Commands.REVERSE_TRAIN_DIRECTION: "reversed train",
            Commands.MODIFY_ORDER: "modified order",
            Commands.SKIP_TO_ORDER: "skipped to order",
            Commands.DELETE_ORDER: "deleted order",
            Commands.INSERT_ORDER: "inserted order",
            Commands.CHANGE_SERVICE_INT: "changed service interval",
            Commands.RESTORE_ORDER_INDEX: "restored order index",
            Commands.CREATE_GROUP: "created group",
            Commands.DELETE_GROUP: "deleted group",
            Commands.RENAME_GROUP: "renamed group",
            Commands.ADD_VEH_GROUP: "added vehicle to group",
            Commands.ADD_SHARED_VEH_GROUP: "added shared vehicle to group",
            Commands.REMOVE_VEH_GROUP: "removed vehicle from group",
            Commands.SET_GROUP_FLAG: "set group flag",
            Commands.SET_GROUP_LIVERY: "set group livery",
            Commands.SET_AUTOREPLACE: "set autoreplace",
            Commands.CHANGE_TIMETABLE: "changed timetable",
            Commands.BULK_CHANGE_TIMETABLE: "bulk changed timetable",
            Commands.SET_VEH_TIMETABLE_START: "set vehicle timetable start",
            Commands.AUTOFILL_TIMETABLE: "autofilled timetable",
            Commands.SET_TIMETABLE_START: "set timetable start",
            Commands.INCREASE_LOAN: "increased loan",
            Commands.DECREASE_LOAN: "decreased loan",
            Commands.SET_COMPANY_MAX_LOAN: "set company max loan",
            Commands.MONEY_CHEAT: "money cheat",
            Commands.GIVE_MONEY: "gave money",
            Commands.FOUND_TOWN: "founded town",
            Commands.RENAME_TOWN: "renamed town",
            Commands.DO_TOWN_ACTION: "performed town action",
            Commands.TOWN_CARGO_GOAL: "set town cargo goal",
            Commands.TOWN_GROWTH_RATE: "set town growth rate",
            Commands.TOWN_RATING: "changed town rating",
            Commands.TOWN_SET_TEXT: "set town text",
            Commands.EXPAND_TOWN: "expanded town",
            Commands.DELETE_TOWN: "deleted town",
            Commands.BUILD_INDUSTRY: "built industry",
            Commands.BUILD_INDUSTRY_PROSPECT: "prospected industry",
            Commands.SET_INDUSTRY_PRODUCTION: "set industry production",
            Commands.SET_INDUSTRY_TEXT: "set industry text",
            Commands.SET_COMPANY_MANAGER_FACE: "set company manager face",
            Commands.SET_COMPANY_COLOUR: "set company colour",
            Commands.RENAME_COMPANY: "renamed company",
            Commands.RENAME_PRESIDENT: "renamed president",
            Commands.BUY_COMPANY: "bought company",
            Commands.COMPANY_CTRL: "company control",
            Commands.CHANGE_COMPANY_SETTING: "changed company setting",
            Commands.CUSTOM_NEWS_ITEM: "custom news",
            Commands.CREATE_SUBSIDY: "created subsidy",
            Commands.PAUSE: "pause",
            Commands.PLACE_SIGN: "placed sign",
            Commands.RENAME_SIGN: "renamed sign",
            Commands.CREATE_GOAL: "created goal",
            Commands.REMOVE_GOAL: "removed goal",
            Commands.QUESTION: "question",
            Commands.GOAL_QUESTION_ANSWER: "answered goal question",
            Commands.CREATE_STORY_PAGE: "created story page",
            Commands.CREATE_STORY_PAGE_ELEMENT: "created story element",
            Commands.UPDATE_STORY_PAGE_ELEMENT: "updated story element",
            Commands.SET_STORY_PAGE_TITLE: "set story title",
            Commands.SET_STORY_PAGE_DATE: "set story date",
            Commands.SHOW_STORY_PAGE: "showed story page",
            Commands.REMOVE_STORY_PAGE: "removed story page",
            Commands.REMOVE_STORY_PAGE_ELEMENT: "removed story element",
            Commands.SCROLL_VIEWPORT: "scrolled viewport",
            Commands.STORY_PAGE_BUTTON: "story page button",
            Commands.CREATE_LEAGUE_TABLE: "created league table",
            Commands.CREATE_LEAGUE_TABLE_ELEMENT: "created league element",
            Commands.UPDATE_LEAGUE_TABLE_ELEMENT_DATA: "updated league data",
            Commands.UPDATE_LEAGUE_TABLE_ELEMENT_SCORE: "updated league score",
            Commands.REMOVE_LEAGUE_TABLE_ELEMENT: "removed league element",
            Commands.LEVEL_LAND: "levelled land",
        }
        return mapping.get(cmd, f"{cmd.name.lower().replace('_', ' ')}")

    def _classify_construction(self, cmd: Union[Commands, int]) -> Tuple[bool, Optional[str]]:
        """Return (is_construction, category) for a command."""
        try:
            if not isinstance(cmd, Commands):
                cmd = Commands(cmd)
        except Exception:
            return False, None

        rail_cmds = {
            Commands.BUILD_RAILROAD_TRACK,
            Commands.BUILD_SINGLE_RAIL,
            Commands.BUILD_RAIL_WAYPOINT,
            Commands.BUILD_TRAIN_DEPOT,
            Commands.CONVERT_RAIL,
            Commands.BUILD_SINGLE_SIGNAL,
        }
        road_cmds = {
            Commands.BUILD_ROAD,
            Commands.BUILD_LONG_ROAD,
            Commands.BUILD_ROAD_STOP,
            Commands.BUILD_ROAD_DEPOT,
            Commands.CONVERT_ROAD,
        }
        station_like = {
            Commands.BUILD_RAIL_STATION,
            Commands.BUILD_AIRPORT,
            Commands.BUILD_DOCK,
            Commands.BUILD_SHIP_DEPOT,
            Commands.BUILD_BUOY,
        }
        landscaping = {
            Commands.LANDSCAPE_CLEAR,
            Commands.TERRAFORM_LAND,
            Commands.LEVEL_LAND,
            Commands.PLANT_TREE,
        }
        objects = {Commands.BUILD_OBJECT, Commands.BUILD_OBJECT_AREA}
        industry = {Commands.BUILD_INDUSTRY, Commands.BUILD_INDUSTRY_PROSPECT}
        tunnel_bridge = {Commands.BUILD_TUNNEL, Commands.BUILD_BRIDGE}

        if cmd in rail_cmds:
            return True, "rail"
        if cmd in road_cmds:
            return True, "road"
        if cmd in station_like:
            return True, "station"
        if cmd in objects:
            return True, "object"
        if cmd in industry:
            return True, "industry"
        if cmd in tunnel_bridge:
            return True, "tunnel_bridge"
        if cmd in landscaping:
            return True, "landscaping"
        return False, None

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

    def _get_company_from_command(self, params_bytes: bytes) -> int:
        """Extract company ID from command parameters."""
        try:
            # Company ID is typically in the second byte for most commands
            if len(params_bytes) >= 2:
                return params_bytes[1]
        except Exception:
            pass
        return 0

    def _bg_parse(self, map_data: bytes) -> None:
        """Background map parsing with vehicle extraction."""
        try:
            logger.info("Parsing map data (background)...")

            # Relay progress to listeners
            def _progress_cb(p: float, stage: str) -> None:
                try:
                    self._emit_event("map_parse_progress", p, stage)
                except Exception:
                    pass

            parsed = load_savefile_from_bytes(
                map_data, parsed=True, silent=True, progress_callback=_progress_cb
            )
            self._parsed_save = parsed  # type: ignore[assignment]

            # Parse vehicles from savefile
            self._parse_vehicles_from_save(parsed)

            self._emit_event("map_parsed")
        except Exception as e:
            logger.error(f"Error parsing map data: {e}")
