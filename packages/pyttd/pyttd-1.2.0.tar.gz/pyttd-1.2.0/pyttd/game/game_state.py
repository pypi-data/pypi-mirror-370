"""Game State Management

This module tracks the current state of the game including companies,
vehicles, economy, map information, and other game entities.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import IntEnum


class CompanyID(IntEnum):
    """Company IDs"""

    FIRST = 0
    SECOND = 1
    THIRD = 2
    FOURTH = 3
    FIFTH = 4
    SIXTH = 5
    SEVENTH = 6
    EIGHTH = 7
    COMPANY_NEW_COMPANY = 254  # Used for requesting new company creation
    SPECTATOR = 255
    COMPANY_SPECTATOR = 255  # Alias for spectator mode
    INVALID = 255


class VehicleType(IntEnum):
    """Vehicle types"""

    TRAIN = 0
    ROAD = 1
    SHIP = 2
    AIRCRAFT = 3
    EFFECT = 4
    DISASTER = 5


class CargoType(IntEnum):
    """Common cargo types (varies by NewGRF)"""

    PASSENGERS = 0
    COAL = 1
    MAIL = 2
    OIL = 3
    LIVESTOCK = 4
    GOODS = 5
    GRAIN = 6
    WOOD = 7
    IRON_ORE = 8
    STEEL = 9
    VALUABLES = 10
    FOOD = 11


@dataclass
class CompanyInfo:
    """Information about a company"""

    company_id: CompanyID
    name: str = ""
    manager_name: str = ""
    money: int = 500000  # Starting money
    loan: int = 200000  # Starting loan
    max_loan: int = 500000
    value: int = 0
    performance: int = 0
    inaugurated_year: int = 1950
    is_ai: bool = False
    bankrupt_counter: int = 0
    share_owners: List[CompanyID] = field(default_factory=list)

    def net_worth(self) -> int:
        """Calculate net worth (money + value - loan)"""
        return self.money + self.value - self.loan


@dataclass
class VehicleInfo:
    """Information about a vehicle"""

    vehicle_id: int
    vehicle_type: VehicleType
    name: str = ""
    company_id: CompanyID = CompanyID.FIRST
    engine_id: int = 0
    build_year: int = 1950
    reliability: int = 100
    speed: int = 0
    max_speed: int = 0
    power: int = 0
    weight: int = 0
    running_cost: int = 0
    profit_this_year: int = 0
    profit_last_year: int = 0
    current_tile: int = 0
    cargo_type: CargoType = CargoType.PASSENGERS
    cargo_capacity: int = 0
    cargo_count: int = 0
    destination_tile: int = 0

    # Vehicle state
    is_stopped: bool = False
    is_crashed: bool = False
    is_in_depot: bool = False


@dataclass
class MapInfo:
    """Information about the game map"""

    size_x: int = 256
    size_y: int = 256
    seed: int = 0
    landscape: int = 0  # 0=temperate, 1=arctic, 2=tropical, 3=toyland

    def total_tiles(self) -> int:
        """Get total number of tiles on map"""
        return self.size_x * self.size_y

    def is_valid_tile(self, x: int, y: int) -> bool:
        """Check if coordinates are within map bounds"""
        return 0 <= x < self.size_x and 0 <= y < self.size_y

    def tile_to_coords(self, tile: int) -> Tuple[int, int]:
        """Convert tile index to X,Y coordinates"""
        x = tile % self.size_x
        y = tile // self.size_x
        return (x, y)

    def coords_to_tile(self, x: int, y: int) -> int:
        """Convert X,Y coordinates to tile index"""
        return y * self.size_x + x


@dataclass
class EconomyInfo:
    """Economic information about the game"""

    inflation_rates: Dict[str, float] = field(
        default_factory=lambda: {"payment": 1.0, "construction": 1.0}
    )
    max_loan: int = 500000
    fluct: int = 0  # Economy fluctuation
    interest_rate: int = 2  # Loan interest rate
    infl_amount: int = 6
    infl_amount_pr: int = 10


@dataclass
class GameDate:
    """Game date information"""

    year: int = 1950
    month: int = 1  # 1-12
    day: int = 1  # 1-31

    def to_days(self) -> int:
        """Convert to days since game start"""
        # OpenTTD counts days from year 0, month 1, day 1
        return (self.year * 365) + ((self.month - 1) * 30) + (self.day - 1)

    @classmethod
    def from_days(cls, days: int) -> "GameDate":
        """Create GameDate from days since game start"""
        year = days // 365
        remaining_days = days % 365
        month = (remaining_days // 30) + 1
        day = (remaining_days % 30) + 1

        # Clamp values to valid ranges
        month = min(12, max(1, month))
        day = min(31, max(1, day))

        return cls(year=year, month=month, day=day)

    def __str__(self) -> str:
        return f"{self.day:02d}/{self.month:02d}/{self.year}"


@dataclass
class ClientInfo:
    """Information about connected clients"""

    client_id: int
    company_id: CompanyID = CompanyID.SPECTATOR
    name: str = ""
    hostname: str = ""
    join_date: Optional[datetime] = None


class GameState:
    """Manages the complete game state"""

    def __init__(self) -> None:
        # Basic game info
        self.game_date = GameDate()
        self.frame = 0
        self.frame_max = 0
        self.paused = False

        # Network info
        self.client_id: Optional[int] = None
        self.company_id = CompanyID.SPECTATOR
        self.server_name = ""
        self.server_revision = ""

        # Map and world
        self.map_info = MapInfo()
        self.economy = EconomyInfo()

        # Game entities
        self.companies: Dict[CompanyID, CompanyInfo] = {}
        self.vehicles: Dict[int, VehicleInfo] = {}
        self.clients: Dict[int, ClientInfo] = {}

        # Map data (simplified, real implementation would need full map storage)
        self._map_data: Optional[bytes] = None

        # Random state for desync detection
        self.random_seed1: int = 0
        self.random_seed2: int = 0

        # Performance tracking
        self.last_frame_time: Optional[datetime] = None
        self.frame_rate: float = 30.0  # Target frame rate

    def update_frame(self, frame: int, frame_max: int, seed1: int = 0, seed2: int = 0) -> None:
        """Update frame counter and random state"""
        self.frame = frame
        self.frame_max = frame_max
        self.random_seed1 = seed1
        self.random_seed2 = seed2
        self.last_frame_time = datetime.now()

    def set_client_info(self, client_id: int, company_id: CompanyID) -> None:
        """Set our client information"""
        self.client_id = client_id
        self.company_id = company_id

    def add_company(self, company: CompanyInfo) -> None:
        """Add or update company information"""
        self.companies[company.company_id] = company

    def get_company(self, company_id: CompanyID) -> Optional[CompanyInfo]:
        """Get company information"""
        return self.companies.get(company_id)

    def get_our_company(self) -> Optional[CompanyInfo]:
        """Get our company information"""
        if self.company_id == CompanyID.SPECTATOR:
            return None
        return self.get_company(self.company_id)

    def add_vehicle(self, vehicle: VehicleInfo) -> None:
        """Add or update vehicle information"""
        self.vehicles[vehicle.vehicle_id] = vehicle

    def get_vehicle(self, vehicle_id: int) -> Optional[VehicleInfo]:
        """Get vehicle information"""
        return self.vehicles.get(vehicle_id)

    def get_company_vehicles(self, company_id: CompanyID) -> List[VehicleInfo]:
        """Get all vehicles owned by a company"""
        return [v for v in self.vehicles.values() if v.company_id == company_id]

    def get_our_vehicles(self) -> List[VehicleInfo]:
        """Get all vehicles owned by our company"""
        if self.company_id == CompanyID.SPECTATOR:
            return []
        return self.get_company_vehicles(self.company_id)

    def add_client(self, client: ClientInfo) -> None:
        """Add or update client information"""
        self.clients[client.client_id] = client

        # If client is in a company (not spectator), ensure company exists
        if (
            client.company_id != CompanyID.COMPANY_SPECTATOR
            and client.company_id not in self.companies
        ):
            # Create basic company info from client data
            company_info = CompanyInfo(
                company_id=client.company_id,
                name=f"Company {client.company_id}",  # Default name, may be updated later
                manager_name=client.name,
                is_ai=False,  # Assume human until proven otherwise
            )
            self.companies[client.company_id] = company_info

    def remove_client(self, client_id: int) -> None:
        """Remove client information"""
        self.clients.pop(client_id, None)

    def get_client(self, client_id: int) -> Optional[ClientInfo]:
        """Get client information"""
        return self.clients.get(client_id)

    def set_map_data(self, data: bytes) -> None:
        """Set compressed map data"""
        self._map_data = data

    def has_map_data(self) -> bool:
        """Check if we have map data"""
        return self._map_data is not None

    def update_date_from_days(self, days: int) -> None:
        """Update game date from day count"""
        self.game_date = GameDate.from_days(days)

    def is_synchronized(self) -> bool:
        """Check if we're synchronized with the server"""
        return self.frame <= self.frame_max

    def get_lag_frames(self) -> int:
        """Get number of frames we're behind the server"""
        return max(0, self.frame_max - self.frame)

    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to dictionary for debugging/serialization"""
        return {
            "frame": self.frame,
            "frame_max": self.frame_max,
            "date": str(self.game_date),
            "client_id": self.client_id,
            "company_id": int(self.company_id) if self.company_id != CompanyID.SPECTATOR else None,
            "map_size": f"{self.map_info.size_x}x{self.map_info.size_y}",
            "companies": {
                int(k): {
                    "name": v.name,
                    "money": v.money,
                    "loan": v.loan,
                    "net_worth": v.net_worth(),
                }
                for k, v in self.companies.items()
            },
            "vehicles": len(self.vehicles),
            "clients": len(self.clients),
            "has_map": self.has_map_data(),
            "synchronized": self.is_synchronized(),
            "lag_frames": self.get_lag_frames(),
        }
