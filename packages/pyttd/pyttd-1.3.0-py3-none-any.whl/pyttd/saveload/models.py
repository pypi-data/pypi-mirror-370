"""
Data models for OpenTTD savefile data structures.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import IntEnum
from datetime import datetime


class VehicleType(IntEnum):
    """Vehicle types"""

    VEH_TRAIN = 0
    VEH_ROAD = 1
    VEH_SHIP = 2
    VEH_AIRCRAFT = 3
    VEH_EFFECT = 4
    VEH_DISASTER = 5


class CargoType(IntEnum):
    """Cargo types"""

    CT_PASSENGERS = 0
    CT_MAIL = 1
    CT_OIL = 2
    CT_LIVESTOCK = 3
    CT_GOODS = 4
    CT_GRAIN = 5
    CT_WOOD = 6
    CT_IRON_ORE = 7
    CT_STEEL = 8
    CT_COAL = 9
    CT_VALUABLES = 10
    CT_FOOD = 11
    CT_PAPER = 12
    CT_COPPER_ORE = 13
    CT_WATER = 14
    CT_FRUIT = 15
    CT_RUBBER = 16
    CT_SUGAR = 17
    CT_COLA = 18
    CT_COTTON_CANDY = 19
    CT_BUBBLES = 20
    CT_TOYS = 21
    CT_BATTERIES = 22
    CT_CANDY = 23
    CT_TOFFEE = 24
    CT_PLASTIC = 25
    CT_FIZZY_DRINKS = 26
    CT_COLA_2 = 27
    CT_COTTON_CANDY_2 = 28
    CT_BUBBLES_2 = 29


class IndustryType(IntEnum):
    """Industry types"""

    INDUSTRY_COAL_MINE = 0
    INDUSTRY_POWER_STATION = 1
    INDUSTRY_SAWMILL = 2
    INDUSTRY_FOREST = 3
    INDUSTRY_OIL_REFINERY = 4
    INDUSTRY_OIL_RIG = 5
    INDUSTRY_FARM = 6
    INDUSTRY_FACTORY = 7
    INDUSTRY_PRINTING_WORKS = 8
    INDUSTRY_STEEL_MILL = 9
    INDUSTRY_BANK = 10
    INDUSTRY_FOOD_PROCESSING_PLANT = 11
    INDUSTRY_PAPER_MILL = 12
    INDUSTRY_GOLD_MINE = 13
    INDUSTRY_BANK_2 = 14
    INDUSTRY_DIAMOND_MINE = 15
    INDUSTRY_IRON_ORE_MINE = 16
    INDUSTRY_METAL_FOUNDRY = 17
    INDUSTRY_CHEMICAL_PLANT = 18
    INDUSTRY_SLAG_HEAP = 19
    INDUSTRY_RUBBER_PLANTATION = 20
    INDUSTRY_WATER_SUPPLY = 21
    INDUSTRY_WATER_TOWER = 22
    INDUSTRY_FACTORY_2 = 23
    INDUSTRY_FARM_2 = 24
    INDUSTRY_MANUFACTURING_PLANT = 25
    INDUSTRY_TOY_FACTORY = 26
    INDUSTRY_SWEET_FACTORY = 27
    INDUSTRY_BATTERY_FARM = 28
    INDUSTRY_TOFFEE_QUARRY = 29
    INDUSTRY_PLASTIC_FOUNTAINS = 30
    INDUSTRY_FIZZY_DRINK_FACTORY = 31
    INDUSTRY_BUBBLE_GENERATOR = 32
    INDUSTRY_TOY_SHOP = 33
    INDUSTRY_CANDYFLOSS_FOREST = 34
    INDUSTRY_TOFFEE_FOREST = 35
    INDUSTRY_COTTON_CANDY_FOREST = 36
    INDUSTRY_BATTERY_FARM_2 = 37
    INDUSTRY_COLA_WELLS = 38
    INDUSTRY_PLASTIC_FOUNTAINS_2 = 39
    INDUSTRY_FIZZY_DRINK_FACTORY_2 = 40
    INDUSTRY_BUBBLE_GENERATOR_2 = 41
    INDUSTRY_TOY_SHOP_2 = 42
    INDUSTRY_CANDYFLOSS_FOREST_2 = 43
    INDUSTRY_TOFFEE_FOREST_2 = 44
    INDUSTRY_COTTON_CANDY_FOREST_2 = 45
    INDUSTRY_BATTERY_FARM_3 = 46
    INDUSTRY_COLA_WELLS_2 = 47


@dataclass
class GameMeta:
    """Game metadata"""

    filename: str
    save_version: int
    minor_version: int
    openttd_version: str = "14.1"  # TODO: get from the save_version or somewhere


@dataclass
class DateInfo:
    """Date information with raw and formatted data"""

    raw_date: int
    year: int
    month: int
    day: int
    formatted: str


@dataclass
class InflationInfo:
    """Inflation information with raw and formatted data"""

    raw_value: int
    percentage: float
    multiplier: float
    formatted: str


@dataclass
class GameData:
    """Game state data"""

    date: DateInfo
    economy_date: DateInfo
    inflation_prices: InflationInfo
    inflation_payment: InflationInfo
    max_loan: int
    interest_rate: int
    landscape: Optional[int] = None  # 0=Temperate, 1=Arctic, 2=Tropical, 3=Toyland
    economy_data: Dict[str, Any] = field(default_factory=dict)
    settings_data: Any = field(default_factory=dict)


@dataclass
class MapData:
    """Map data"""

    dim_x: int
    dim_y: int
    tile_count: int
    flatbuffers_map: Optional[bytes] = None


@dataclass
class CompanyInfo:
    """Company information with raw and formatted data"""

    index: int
    name: str
    president_name: str
    color_name: str
    color_id: int
    is_ai: bool
    money: int
    current_loan: int
    max_loan: int
    company_value: int
    performance_history: List[int]
    yearly_expenses: List[int]
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompanyData:
    """All company data"""

    companies: List[Dict[str, Any]]
    count: int


@dataclass
class VehicleInfo:
    """Vehicle information"""

    index: int
    vehicle_type: VehicleType
    vehicle_type_name: str
    owner_id: int
    tile: int
    x: int
    y: int
    z: int
    direction: int
    speed: int
    cargo_type: CargoType
    cargo_capacity: int
    cargo_count: int
    cargo_source: int
    cargo_days_in_transit: int
    current_order: int
    orders: List[int]
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VehicleData:
    """All vehicle data"""

    vehicles: List[Dict[str, Any]]
    count: int
    by_type: Dict[VehicleType, List[Dict[str, Any]]] = field(default_factory=dict)


@dataclass
class IndustryInfo:
    """Industry information"""

    index: int
    industry_type: IndustryType
    industry_type_name: str
    owner: int
    tile: int
    x: int
    y: int
    z: int
    production_rate: int
    acceptance: Dict[CargoType, int]
    production: Dict[CargoType, int]
    last_produced: int
    last_accepted: int
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IndustryData:
    """All industry data"""

    industries: List[Dict[str, Any]]
    count: int
    by_type: Dict[IndustryType, List[Dict[str, Any]]] = field(default_factory=dict)


@dataclass
class TownInfo:
    """Town information"""

    index: int
    name: str
    tile: int
    x: int
    y: int
    z: int
    population: int
    houses: int
    radius: int
    growth_rate: int
    growth_timer: int
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TownData:
    """All town data"""

    towns: List[Dict[str, Any]]
    count: int


@dataclass
class StationInfo:
    """Station information"""

    index: int
    name: str
    owner: int
    tile: int
    x: int
    y: int
    z: int
    station_type: int
    facilities: int
    cargo_accepted: Dict[CargoType, bool]
    cargo_waiting: Dict[CargoType, int]
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StationData:
    """All station data"""

    stations: List[Dict[str, Any]]
    count: int


@dataclass
class CargoPacketInfo:
    """Cargo packet information"""

    index: int
    cargo_type: CargoType
    count: int
    source: int
    days_in_transit: int
    source_xy: int
    loaded_at_xy: int
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CargoPacketData:
    """All cargo packet data"""

    packets: List[CargoPacketInfo]
    count: int
    by_cargo_type: Dict[CargoType, List[CargoPacketInfo]] = field(default_factory=dict)


@dataclass
class TileInfo:
    """Tile information"""

    index: int
    tile_type: int
    height: int
    owner: int
    m1: int
    m2: int
    m3: int
    m4: int
    m5: int
    m6: int
    m7: int
    m8: int
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TileData:
    """All tile data"""

    tiles: Dict[int, TileInfo]
    count: int


@dataclass
class SignInfo:
    """Sign information"""

    index: int
    text: str
    owner: int
    tile: int
    x: int
    y: int
    z: int
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SignData:
    """All sign data"""

    signs: List[SignInfo]
    count: int


@dataclass
class OrderInfo:
    """Order information"""

    index: int
    order_type: int
    destination: int
    flags: int
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrderData:
    """All order data"""

    orders: List[OrderInfo]
    count: int


@dataclass
class DepotInfo:
    """Depot information"""

    index: int
    owner: int
    tile: int
    x: int
    y: int
    z: int
    depot_type: int
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DepotData:
    """All depot data"""

    depots: List[DepotInfo]
    count: int


@dataclass
class EngineInfo:
    """Engine information"""

    index: int
    engine_id: int
    owner: int
    vehicle_type: VehicleType
    reliability: int
    reliability_spd_dec: int
    reliability_int: int
    max_age: int
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineData:
    """All engine data"""

    engines: List[EngineInfo]
    count: int
    by_type: Dict[VehicleType, List[EngineInfo]] = field(default_factory=dict)


@dataclass
class GroupInfo:
    """Group information"""

    index: int
    name: str
    owner: int
    parent: int
    vehicle_type: VehicleType
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GroupData:
    """All group data"""

    groups: List[GroupInfo]
    count: int


@dataclass
class GoalInfo:
    """Goal information"""

    index: int
    text: str
    type: int
    destination: int
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GoalData:
    """All goal data"""

    goals: List[GoalInfo]
    count: int


@dataclass
class StoryPageInfo:
    """Story page information"""

    index: int
    title: str
    text: str
    date: int
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StoryPageData:
    """All story page data"""

    pages: List[StoryPageInfo]
    count: int


@dataclass
class LeagueTableInfo:
    """League table information"""

    index: int
    title: str
    header: str
    footer: str
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LeagueTableData:
    """All league table data"""

    tables: List[LeagueTableInfo]
    count: int


@dataclass
class AIInfo:
    """AI information"""

    index: int
    name: str
    version: str
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIData:
    """All AI data"""

    ais: List[AIInfo]
    count: int


@dataclass
class GameLogInfo:
    """Game log information"""

    index: int
    date: int
    text: str
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GameLogData:
    """All game log data"""

    logs: List[GameLogInfo]
    count: int


@dataclass
class NewGRFInfo:
    """NewGRF information"""

    grfid: int
    name: str
    version: int
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NewGRFData:
    """All NewGRF data"""

    grfs: List[NewGRFInfo]
    count: int


@dataclass
class AnimatedTileInfo:
    """Animated tile information"""

    index: int
    tile: int
    animation_data: int
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnimatedTileData:
    """All animated tile data"""

    tiles: List[AnimatedTileInfo]
    count: int


@dataclass
class LinkGraphInfo:
    """Link graph information"""

    index: int
    cargo: CargoType
    nodes: int
    edges: int
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LinkGraphData:
    """All link graph data"""

    graphs: List[LinkGraphInfo]
    count: int


@dataclass
class AirportInfo:
    """Airport information"""

    index: int
    airport_type: int
    tile: int
    x: int
    y: int
    z: int
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AirportData:
    """All airport data"""

    airports: List[AirportInfo]
    count: int


@dataclass
class ObjectInfo:
    """Object information"""

    index: int
    object_type: int
    tile: int
    x: int
    y: int
    z: int
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ObjectData:
    """All object data"""

    objects: List[ObjectInfo]
    count: int


@dataclass
class PersistentStorageInfo:
    """Persistent storage information"""

    index: int
    grfid: int
    data: bytes
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PersistentStorageData:
    """All persistent storage data"""

    storages: List[PersistentStorageInfo]
    count: int


@dataclass
class WaterRegionInfo:
    """Water region information"""

    index: int
    region_type: int
    tiles: List[int]
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WaterRegionData:
    """All water region data"""

    regions: List[WaterRegionInfo]
    count: int


@dataclass
class RandomizerInfo:
    """Randomizer information"""

    index: int
    seed: int
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RandomizerData:
    """All randomizer data"""

    randomizers: List[RandomizerInfo]
    count: int


@dataclass
class SaveFileData:
    """Complete savefile data structure"""

    meta: GameMeta
    game: GameData
    map: MapData
    companies: CompanyData
    vehicles: VehicleData
    industries: IndustryData
    towns: TownData
    stations: StationData
    cargo_packets: CargoPacketData
    tiles: TileData
    signs: SignData
    orders: OrderData
    depots: DepotData
    engines: EngineData
    groups: GroupData
    goals: GoalData
    story_pages: StoryPageData
    league_tables: LeagueTableData
    ais: AIData
    game_logs: GameLogData
    newgrfs: NewGRFData
    animated_tiles: AnimatedTileData
    link_graphs: LinkGraphData
    airports: AirportData
    objects: ObjectData
    persistent_storage: PersistentStorageData
    water_regions: WaterRegionData
    randomizers: RandomizerData

    # Raw data
    raw_data: Dict[str, Any] = field(default_factory=dict)

    # Statistics
    statistics: Dict[str, Any] = field(default_factory=dict)
