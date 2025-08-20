"""Command System

This module implements the command system used for executing game actions.
All commands must be synchronized with the server to prevent desyncs.
"""

from enum import IntEnum
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass


class Commands(IntEnum):
    """Command IDs as defined in command_type.h"""

    # Railroad construction
    BUILD_RAILROAD_TRACK = 0x00
    REMOVE_RAILROAD_TRACK = 0x01
    BUILD_SINGLE_RAIL = 0x02
    REMOVE_SINGLE_RAIL = 0x03

    # General construction
    LANDSCAPE_CLEAR = 0x04
    BUILD_BRIDGE = 0x05
    BUILD_RAIL_STATION = 0x06
    BUILD_TRAIN_DEPOT = 0x07
    BUILD_SINGLE_SIGNAL = 0x08
    REMOVE_SINGLE_SIGNAL = 0x09
    TERRAFORM_LAND = 0x0A
    BUILD_OBJECT = 0x0B
    BUILD_OBJECT_AREA = 0x0C
    BUILD_TUNNEL = 0x0D

    # Station management
    REMOVE_FROM_RAIL_STATION = 0x0E
    CONVERT_RAIL = 0x0F
    BUILD_RAIL_WAYPOINT = 0x10
    RENAME_WAYPOINT = 0x11
    REMOVE_FROM_RAIL_WAYPOINT = 0x12

    # Road construction
    BUILD_ROAD = 0x13
    REMOVE_ROAD = 0x14
    BUILD_LONG_ROAD = 0x15
    REMOVE_LONG_ROAD = 0x16
    BUILD_ROAD_STOP = 0x17
    REMOVE_ROAD_STOP = 0x18
    BUILD_ROAD_DEPOT = 0x19
    CONVERT_ROAD = 0x1A

    # Airport construction
    BUILD_AIRPORT = 0x1B

    # Ship/dock construction
    BUILD_DOCK = 0x1C
    BUILD_SHIP_DEPOT = 0x1D
    BUILD_BUOY = 0x1E

    # Landscaping
    PLANT_TREE = 0x1F

    # Vehicle commands
    BUILD_VEHICLE = 0x20
    SELL_VEHICLE = 0x21
    START_STOP_VEHICLE = 0x22
    REFIT_VEHICLE = 0x23
    CLONE_VEHICLE = 0x24
    MOVE_RAIL_VEHICLE = 0x25
    FORCE_TRAIN_PROCEED = 0x26
    REVERSE_TRAIN_DIRECTION = 0x27

    # Orders
    MODIFY_ORDER = 0x28
    SKIP_TO_ORDER = 0x29
    DELETE_ORDER = 0x2A
    INSERT_ORDER = 0x2B
    CHANGE_SERVICE_INT = 0x2C
    RESTORE_ORDER_INDEX = 0x2D

    # Groups
    CREATE_GROUP = 0x2E
    DELETE_GROUP = 0x2F
    RENAME_GROUP = 0x30
    ADD_VEH_GROUP = 0x31
    ADD_SHARED_VEH_GROUP = 0x32
    REMOVE_VEH_GROUP = 0x33
    SET_GROUP_FLAG = 0x34
    SET_GROUP_LIVERY = 0x35

    # Autoreplace
    SET_AUTOREPLACE = 0x36

    # Timetables
    CHANGE_TIMETABLE = 0x37
    BULK_CHANGE_TIMETABLE = 0x38
    SET_VEH_TIMETABLE_START = 0x39
    AUTOFILL_TIMETABLE = 0x3A
    SET_TIMETABLE_START = 0x3B

    # Money management
    INCREASE_LOAN = 52  # 0x34
    DECREASE_LOAN = 53  # 0x35
    SET_COMPANY_MAX_LOAN = 54  # 0x36
    MONEY_CHEAT = 80  # 0x50
    GIVE_MONEY = 108  # 0x6C

    # Company management
    FOUND_TOWN = 0x41
    RENAME_TOWN = 0x42
    DO_TOWN_ACTION = 0x43
    TOWN_CARGO_GOAL = 0x44
    TOWN_GROWTH_RATE = 0x45
    TOWN_RATING = 0x46
    TOWN_SET_TEXT = 0x47
    EXPAND_TOWN = 0x48
    DELETE_TOWN = 0x49

    # Industry
    BUILD_INDUSTRY = 0x4A
    BUILD_INDUSTRY_PROSPECT = 0x4B
    SET_INDUSTRY_PRODUCTION = 0x4C
    SET_INDUSTRY_TEXT = 0x4D

    # Company management
    SET_COMPANY_MANAGER_FACE = 50  # 0x32
    SET_COMPANY_COLOUR = 51  # 0x33
    RENAME_COMPANY = 59  # 0x3B
    RENAME_PRESIDENT = 60  # 0x3C
    BUY_COMPANY = 67  # 0x43
    COMPANY_CTRL = 84  # 0x54
    CHANGE_COMPANY_SETTING = 110  # 0x6E
    CUSTOM_NEWS_ITEM = 0x53
    CREATE_SUBSIDY = 0x54

    # Cheats and admin
    PAUSE = 0x55

    # Signs
    PLACE_SIGN = 0x56
    RENAME_SIGN = 0x57

    # Goals (Game Script)
    CREATE_GOAL = 0x58
    REMOVE_GOAL = 0x59
    QUESTION = 0x5A
    GOAL_QUESTION_ANSWER = 0x5B
    CREATE_STORY_PAGE = 0x5C
    CREATE_STORY_PAGE_ELEMENT = 0x5D
    UPDATE_STORY_PAGE_ELEMENT = 0x5E
    SET_STORY_PAGE_TITLE = 0x5F
    SET_STORY_PAGE_DATE = 0x60
    SHOW_STORY_PAGE = 0x61
    REMOVE_STORY_PAGE = 0x62
    REMOVE_STORY_PAGE_ELEMENT = 0x63
    SCROLL_VIEWPORT = 0x64
    STORY_PAGE_BUTTON = 0x65

    # League
    CREATE_LEAGUE_TABLE = 0x66
    CREATE_LEAGUE_TABLE_ELEMENT = 0x67
    UPDATE_LEAGUE_TABLE_ELEMENT_DATA = 0x68
    UPDATE_LEAGUE_TABLE_ELEMENT_SCORE = 0x69
    REMOVE_LEAGUE_TABLE_ELEMENT = 0x6A

    # Misc
    LEVEL_LAND = 0x6B

    END = 0x6C  # End marker


class DoCommandFlag(IntEnum):
    """Command execution flags"""

    NONE = 0x000
    EXEC = 0x001
    AUTO = 0x002
    QUERY_COST = 0x004
    NO_WATER = 0x008
    NO_TEST_TOWN_RATING = 0x020
    BANKRUPT = 0x040
    AUTOREPLACE = 0x080
    NO_CARGO_CAP_CHECK = 0x100
    ALL_TILES = 0x200
    NO_MODIFY_TOWN_RATING = 0x400
    FORCE_CLEAR_TILE = 0x800


class RailType(IntEnum):
    """Rail types"""

    RAIL = 0
    MONO = 1
    MAGLEV = 2
    ELECTRIC = 3


class Track(IntEnum):
    """Track directions"""

    X = 0  # Track along X axis (horizontal)
    Y = 1  # Track along Y axis (vertical)
    UPPER = 2  # Track going up-right
    LOWER = 3  # Track going down-left
    LEFT = 4  # Track going up-left
    RIGHT = 5  # Track going down-right


class CompanyID(IntEnum):
    """Special company ID constants"""

    COMPANY_NEW_COMPANY = 254  # Used for requesting new company creation
    COMPANY_SPECTATOR = 255  # Spectator mode
    OWNER_NONE = 16  # No owner (public infrastructure)
    OWNER_WATER = 17  # Water/sea
    OWNER_DEITY = 18  # Game script


@dataclass
class CommandPacket:
    """Represents a command packet for execution"""

    company: int
    command_id: Commands
    p1: int = 0
    p2: int = 0
    tile: int = 0
    text: str = ""
    callback_id: int = 0
    frame: Optional[int] = None  # Set by server

    def encode_parameters(self) -> bytes:
        """Encode command parameters for network transmission"""
        import struct

        # Basic parameter encoding - this varies by command type
        # For now, implement basic encoding for common commands
        if self.command_id == Commands.BUILD_RAILROAD_TRACK:
            # p1 = start tile, p2 = end tile | rail_type
            return struct.pack("<LL", self.p1, self.p2)
        elif self.command_id == Commands.BUILD_SINGLE_RAIL:
            # p1 = tile, p2 = track direction | rail_type
            return struct.pack("<LL", self.p1, self.p2)
        elif self.command_id == Commands.COMPANY_CTRL:
            # CMD_COMPANY_CTRL parameters: cca, company_id, reason, client_id
            # cca = CompanyCtrlAction (uint8_t, CCA_NEW = 0)
            # company_id = CompanyID (uint8_t, INVALID_COMPANY = 255)
            # reason = CompanyRemoveReason (uint8_t, CRR_NONE = 0)
            # client_id = ClientID (uint32_t, INVALID_CLIENT_ID = 0)
            return struct.pack(
                "<BBBL", 0, 255, 0, 0
            )  # CCA_NEW, INVALID_COMPANY, CRR_NONE, INVALID_CLIENT_ID
        else:
            # Generic encoding for other commands
            return struct.pack("<LL", self.p1, self.p2)


class CommandBuilder:
    """Helper class for building common commands"""

    @staticmethod
    def build_rail(
        start_tile: int, end_tile: int, rail_type: RailType = RailType.RAIL, company: int = 1
    ) -> CommandPacket:
        """Build railroad track between two points"""
        # p1 = start tile
        # p2 = end tile | (rail_type << 4) | (remove << 6)
        p2 = end_tile | (rail_type << 4)

        return CommandPacket(
            company=company,
            command_id=Commands.BUILD_RAILROAD_TRACK,
            p1=start_tile,
            p2=p2,
            tile=start_tile,
        )

    @staticmethod
    def build_single_rail(
        tile: int, track: Track, rail_type: RailType = RailType.RAIL, company: int = 1
    ) -> CommandPacket:
        """Build a single rail piece on a tile"""
        # p1 = tile
        # p2 = rail_type | (track << 4)
        p2 = rail_type | (track << 4)

        return CommandPacket(
            company=company, command_id=Commands.BUILD_SINGLE_RAIL, p1=tile, p2=p2, tile=tile
        )

    @staticmethod
    def build_rail_station(
        tile: int,
        rail_type: RailType = RailType.RAIL,
        orientation: int = 0,
        num_platforms: int = 1,
        platform_length: int = 1,
        station_class: int = 0,
        station_type: int = 0,
        company: int = 1,
    ) -> CommandPacket:
        """Build a rail station"""
        # Complex parameter encoding for rail stations
        # p1 = rail_type | (orientation << 8) | (num_platforms << 16) | (platform_length << 24)
        p1 = rail_type | (orientation << 8) | (num_platforms << 16) | (platform_length << 24)
        # p2 = station_class | (station_type << 8)
        p2 = station_class | (station_type << 8)

        return CommandPacket(
            company=company, command_id=Commands.BUILD_RAIL_STATION, p1=p1, p2=p2, tile=tile
        )

    @staticmethod
    def build_train_depot(
        tile: int, direction: int, rail_type: RailType = RailType.RAIL, company: int = 1
    ) -> CommandPacket:
        """Build a train depot"""
        # p1 = rail_type
        # p2 = direction
        return CommandPacket(
            company=company,
            command_id=Commands.BUILD_TRAIN_DEPOT,
            p1=rail_type,
            p2=direction,
            tile=tile,
        )

    @staticmethod
    def start_stop_vehicle(vehicle_id: int, company: int = 1) -> CommandPacket:
        """Start or stop a vehicle"""
        return CommandPacket(
            company=company, command_id=Commands.START_STOP_VEHICLE, p1=vehicle_id, p2=0
        )

    @staticmethod
    def create_company(company_name: str = "AI Company") -> CommandPacket:
        """Create a new company"""
        # CMD_COMPANY_CTRL with CCA_NEW action
        # Based on OpenTTD network_gui.cpp OnClickCompanyNew function
        return CommandPacket(
            company=CompanyID.COMPANY_SPECTATOR,  # Must be COMPANY_SPECTATOR for CMD_COMPANY_CTRL validation
            command_id=Commands.COMPANY_CTRL,
            p1=0,  # CCA_NEW = 0 (create new company)
            p2=255,  # INVALID_COMPANY as p2 parameter
            text="",  # No text parameter needed for company creation
        )

    @staticmethod
    def build_vehicle(depot_tile: int, engine_id: int, company: int = 1) -> CommandPacket:
        """Build a new vehicle at a depot"""
        return CommandPacket(
            company=company, command_id=Commands.BUILD_VEHICLE, p1=engine_id, p2=0, tile=depot_tile
        )

    @staticmethod
    def increase_loan(amount: int, company: int = 1) -> CommandPacket:
        """Increase company loan by specified amount"""
        return CommandPacket(
            company=company,
            command_id=Commands.INCREASE_LOAN,
            p1=amount,  # Amount to increase loan by
            p2=0,
        )

    @staticmethod
    def decrease_loan(amount: int, company: int = 1) -> CommandPacket:
        """Decrease company loan by specified amount"""
        return CommandPacket(
            company=company,
            command_id=Commands.DECREASE_LOAN,
            p1=amount,  # Amount to decrease loan by
            p2=0,
        )

    @staticmethod
    def rename_company(new_name: str, company: int = 1) -> CommandPacket:
        """Rename the company"""
        return CommandPacket(
            company=company, command_id=Commands.RENAME_COMPANY, p1=0, p2=0, text=new_name
        )

    @staticmethod
    def rename_president(new_name: str, company: int = 1) -> CommandPacket:
        """Rename the company president/manager"""
        return CommandPacket(
            company=company, command_id=Commands.RENAME_PRESIDENT, p1=0, p2=0, text=new_name
        )

    @staticmethod
    def set_company_colour(
        scheme: int, primary: bool, colour: int, company: int = 1
    ) -> CommandPacket:
        """Set company livery colour scheme"""
        return CommandPacket(
            company=company,
            command_id=Commands.SET_COMPANY_COLOUR,
            p1=scheme,  # LiveryScheme
            p2=(1 if primary else 0) | (colour << 1),  # primary flag + colour
        )

    @staticmethod
    def give_money(amount: int, dest_company: int, company: int = 1) -> CommandPacket:
        """Transfer money to another company"""
        return CommandPacket(
            company=company,
            command_id=Commands.GIVE_MONEY,
            p1=amount,  # Amount of money to give
            p2=dest_company,  # Destination company
            text="",
        )

    @staticmethod
    def clear_tile(tile: int, company: int = 1) -> CommandPacket:
        """Clear/demolish a tile"""
        return CommandPacket(
            company=company, command_id=Commands.LANDSCAPE_CLEAR, p1=0, p2=0, tile=tile
        )
