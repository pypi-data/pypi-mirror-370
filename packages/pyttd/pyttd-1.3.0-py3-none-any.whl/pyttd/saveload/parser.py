"""
OpenTTD Savefile Parser.
"""

import struct
import lzma
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime

from .reader import BinaryReader, ChunkType, SaveLoadType
from .models import (
    SaveFileData,
    GameMeta,
    GameData,
    MapData,
    CompanyData,
    VehicleData,
    IndustryData,
    TownData,
    StationData,
    CargoPacketData,
    TileData,
    SignData,
    OrderData,
    DepotData,
    EngineData,
    GroupData,
    GoalData,
    StoryPageData,
    LeagueTableData,
    AIData,
    GameLogData,
    NewGRFData,
    AnimatedTileData,
    LinkGraphData,
    AirportData,
    ObjectData,
    PersistentStorageData,
    WaterRegionData,
    RandomizerData,
    VehicleType,
    CargoType,
    IndustryType,
    DateInfo,
    InflationInfo,
    CompanyInfo,
    VehicleInfo,
    IndustryInfo,
    TownInfo,
    StationInfo,
    CargoPacketInfo,
    TileInfo,
    SignInfo,
    OrderInfo,
    DepotInfo,
    EngineInfo,
    GroupInfo,
    GoalInfo,
    StoryPageInfo,
    LeagueTableInfo,
    AIInfo,
    GameLogInfo,
    NewGRFInfo,
    AnimatedTileInfo,
    LinkGraphInfo,
    AirportInfo,
    ObjectInfo,
    PersistentStorageInfo,
    WaterRegionInfo,
    RandomizerInfo,
)
from .formatter import (
    convert_date_to_year,
    convert_date_to_ymd,
    format_inflation_value,
    format_company_data,
)
from .map_flatbuffers import build_map_flatbuffer


class Field:
    """Field definition for table parsing"""

    def __init__(
        self, key: str, ftype: int, is_list: bool, subfields: Optional[List["Field"]] = None
    ):
        self.key = key
        self.ftype = ftype
        self.is_list = is_list
        self.subfields = subfields or []


class SaveParser:
    """
    Comprehensive parser for OpenTTD savefiles.
    """

    def __init__(self, filename: str, silent: bool = True):
        """
        Initialize the parser.

        Args:
            filename: Path to the savefile
            silent: Whether to suppress debug output
        """
        self.filename = filename
        self.silent = silent
        self.reader: BinaryReader = BinaryReader(b"")
        self.raw_data: Dict[str, Any] = {}

        # Setup logging
        self.logger = logging.getLogger(f"pyttd.parser.{Path(filename).name}")
        if silent:
            self.logger.setLevel(logging.WARNING)
        else:
            self.logger.setLevel(logging.DEBUG)

        # Parse header
        self.save_version = 0
        self.minor_version = 0

    def parse_savefile(
        self, parsed: bool = True, progress_callback: Optional[Any] = None
    ) -> Union[Dict[str, Any], SaveFileData]:
        """
        Parse the savefile.

        Args:
            parsed: Whether to return parsed (human-readable) data or raw data
            progress_callback: Optional callback(progress: float, stage: str) for progress reporting

        Returns:
            Either a raw dictionary or a structured SaveFileData object
        """
        try:
            # Init progress
            self._progress_callback = progress_callback
            self._progress_value = 0.0

            # Load and decompress the savefile
            self._load_savefile()
            self._progress_set(0.05, "loaded")

            # Parse all chunks with internal weighted progress
            self._parse_all_chunks()

            if parsed:
                result = self._create_parsed_data()
                self._progress_set(1.0, "done")
                return result
            else:
                self._progress_set(1.0, "done")
                return self.raw_data

        except Exception as e:
            self.logger.error(f"Error parsing savefile: {e}")
            raise

    def _load_savefile(self) -> None:
        """Load and decompress the savefile"""
        self.logger.info(f"Loading savefile: {self.filename}")

        with open(self.filename, "rb") as f:
            # Read header
            header = f.read(8)
            tag = header[:4]
            version_data = header[4:]

            # Parse version
            version_int = struct.unpack(">I", version_data)[0]
            self.save_version = (version_int >> 16) & 0xFFFF
            self.minor_version = (version_int >> 8) & 0xFF

            self.logger.info(f"OpenTTD Save Version: {self.save_version}.{self.minor_version}")

            if tag == b"OTTX":
                self.logger.info("Format: OTTX")
                compressed_data = f.read()
                data = lzma.decompress(compressed_data)
                self.logger.info(f"Decompressed LZMA data: {len(data):,} bytes")
            else:
                raise ValueError(f"Unsupported format: {tag!r}")

        self.reader = BinaryReader(data)

    def _parse_all_chunks(self) -> None:
        """Parse all chunks in the save file"""
        self.logger.debug("Starting to parse all chunks")

        chunks: List[Tuple[str, float, Any]] = [
            ("MAPS", 0.03, self._parse_maps_chunk),
            ("DATE", 0.05, self._parse_date_chunk),
            ("ECMY", 0.05, self._parse_economy_chunk),
            ("PATS", 0.05, self._parse_settings_chunks),
            ("PLYR", 0.18, self._parse_companies_chunk),
            ("VEHS", 0.2, self._parse_vehicles_chunk),
            ("CITY", 0.06, self._parse_towns_chunk),
            ("STNN", 0.05, self._parse_stations_chunk),
            ("INDY", 0.05, self._parse_industries_chunk),
            ("ENGN", 0.03, self._parse_engines_chunk),
            ("ORDR", 0.02, self._parse_orders_chunk),
            ("GRPS", 0.01, self._parse_groups_chunk),
            ("SIGN", 0.01, self._parse_signs_chunk),
            ("GOAL", 0.01, self._parse_goals_chunk),
            ("LEAT", 0.01, self._parse_league_tables_chunk),
            ("LEAE", 0.01, self._parse_league_elements_chunk),
            ("AIPL", 0.01, self._parse_ai_players_chunk),
            ("ANIT", 0.01, self._parse_animated_tiles_chunk),
            ("CAPA", 0.01, self._parse_cargo_packets_chunk),
            ("LGRP", 0.01, self._parse_link_graphs_chunk),
            ("LGRJ", 0.01, self._parse_link_graph_jobs_chunk),
            ("OBJS", 0.01, self._parse_objects_chunk),
            ("GLOG", 0.01, self._parse_gamelog_chunk),
        ]

        total_weight = sum(w for _, w, _ in chunks)
        per_chunk_remaining = 0.9 - 0.05  # from 5% to 90%
        weight_scale = per_chunk_remaining / total_weight if total_weight > 0 else 1.0

        for name, weight, func in chunks:
            scaled = weight * weight_scale
            start_value = self._progress_value
            target_end = min(start_value + scaled, 0.9)
            # Expose chunk-end target for inner table progress to avoid overshoot
            self._chunk_end = target_end
            func()
            # Never decrease progress; clamp up to at least target_end
            if self._progress_value < target_end:
                self._progress_set(target_end, f"parsed {name}")

        self.logger.debug("Finished parsing all chunks")

    def _parse_date_chunk(self) -> None:
        """Parse DATE chunk into a single dict at raw_data['date']"""
        # Use generic table parser to read records
        pos = self.reader.find_chunk(b"DATE")
        if pos is None:
            self.raw_data["date"] = {}
            return
        # Temporarily parse via table machinery
        current_pos = self.reader.pos
        try:
            self._parse_table_chunk("DATE")
            items = self.raw_data.get("date", [])
            if isinstance(items, list) and items:
                self.raw_data["date"] = items[0]
            elif isinstance(items, dict):
                pass
            else:
                self.raw_data["date"] = {}
        finally:
            self.reader.pos = current_pos

    def _parse_economy_chunk(self) -> None:
        """Parse ECMY chunk into a single dict at raw_data['economy']"""
        pos = self.reader.find_chunk(b"ECMY")
        if pos is None:
            self.raw_data["economy"] = {}
            return
        current_pos = self.reader.pos
        try:
            self._parse_table_chunk("ECMY")
            items = self.raw_data.get("ecmy", [])
            if isinstance(items, list) and items:
                self.raw_data["economy"] = items[0]
            elif isinstance(items, dict):
                self.raw_data["economy"] = items
            else:
                self.raw_data["economy"] = {}
        finally:
            self.reader.pos = current_pos

    def _read_table_header(self) -> List[Field]:
        """Read table header"""
        header_total = self.reader.read_gamma() - 1
        header_end = self.reader.pos + header_total

        def read_field_list() -> List[Field]:
            fields: List[Field] = []
            while True:
                ftype_full = self.reader.read_byte()
                if ftype_full == 0:
                    break
                has_len = (ftype_full & 0x10) != 0
                ftype = ftype_full & 0x0F
                key_len = self.reader.read_gamma()
                key = self.reader.data[self.reader.pos : self.reader.pos + key_len].decode(
                    "utf-8", errors="ignore"
                )
                self.reader.pos += key_len
                is_list = has_len and ftype not in (10, 11)
                fields.append(Field(key, ftype, is_list))

            for fld in fields:
                if fld.ftype == 11:  # STRUCT
                    fld.subfields = read_field_list()

            return fields

        fields = read_field_list()

        if self.reader.pos != header_end:
            self.reader.pos = header_end

        return fields

    def _read_primitive(self, ftype: int) -> Any:
        """Read primitive value"""
        if ftype == 1:  # I8
            return self.reader.read_int8()
        if ftype == 2:  # U8
            return self.reader.read_uint8()
        if ftype == 3:  # I16
            return self.reader.read_int16()
        if ftype == 4:  # U16
            return self.reader.read_uint16()
        if ftype == 5:  # I32
            return self.reader.read_int32()
        if ftype == 6:  # U32
            return self.reader.read_uint32()
        if ftype == 7:  # I64
            return self.reader.read_int64()
        if ftype == 8:  # U64
            return self.reader.read_uint64()
        if ftype == 9:  # STRINGID (U16)
            return self.reader.read_uint16()
        if ftype == 10:  # STRING: gamma length + bytes
            strlen = self.reader.read_gamma()
            s = self.reader.data[self.reader.pos : self.reader.pos + strlen].decode(
                "utf-8", errors="ignore"
            )
            self.reader.pos += strlen
            return s
        raise ValueError(f"Unsupported primitive file type: {ftype}")

    def _read_record(self, fields: List[Field], length: int) -> Dict[str, Any]:
        """Read record"""
        end = self.reader.pos + length
        rec: Dict[str, Any] = {}
        try:
            for fld in fields:
                if self.reader.pos >= end:
                    break
                if fld.ftype == 11:
                    # SL_STRUCT encodes a list-length (0 or 1), not a byte-size
                    list_len = self.reader.read_gamma()
                    if list_len > 1:
                        list_len = 1
                    if list_len == 1:
                        rec[fld.key] = self._read_struct_fields(fld.subfields)
                    else:
                        rec[fld.key] = {}
                elif fld.is_list:
                    count = self.reader.read_gamma()
                    arr = []
                    for _ in range(count):
                        arr.append(self._read_primitive(fld.ftype))
                    rec[fld.key] = arr
                else:
                    rec[fld.key] = self._read_primitive(fld.ftype)
        except Exception:
            self.reader.pos = end
        if self.reader.pos != end:
            self.reader.pos = end
        return rec

    def _read_struct_fields(self, subfields: List[Field]) -> Dict[str, Any]:
        """Read struct fields"""
        result: Dict[str, Any] = {}
        for fld in subfields:
            if fld.ftype == 11:
                # Nested struct: again a list-length (0/1) prefix
                list_len = self.reader.read_gamma()
                if list_len > 1:
                    list_len = 1
                if list_len == 1:
                    result[fld.key] = self._read_struct_fields(fld.subfields)
                else:
                    result[fld.key] = {}
            elif fld.is_list:
                try:
                    count = self.reader.read_gamma()
                    arr = []
                    for _ in range(count):
                        arr.append(self._read_primitive(fld.ftype))
                    result[fld.key] = arr
                except Exception:
                    result[fld.key] = []
            else:
                try:
                    value = self._read_primitive(fld.ftype)
                    result[fld.key] = value
                except Exception:
                    break
        return result

    def _parse_table_chunk(self, chunk_name: str) -> None:
        """Parse a table chunk"""
        pos = self.reader.find_chunk(chunk_name.encode())
        if pos is None:
            self.logger.debug(f"{chunk_name} chunk not found")
            self.raw_data[chunk_name.lower()] = []
            return

        self.reader.pos = pos + 4  # Skip chunk ID
        chunk_type = self.reader.read_byte()

        if chunk_type & 0x0F not in (ChunkType.CH_TABLE, ChunkType.CH_SPARSE_TABLE):
            self.logger.debug(f"{chunk_name} is not a table chunk (type: {chunk_type & 0x0F})")
            self.raw_data[chunk_name.lower()] = []
            return

        # Read table header
        fields = self._read_table_header()

        # Read all records
        objects: List[Dict[str, Any]] = []
        # Inner progress within a chunk: distribute budget to a fixed number of steps
        chunk_end = getattr(self, "_chunk_end", self._progress_value)
        budget = max(0.0, chunk_end - self._progress_value)
        steps = 50
        step_inc = budget / steps if steps > 0 else 0.0
        while True:
            size_plus_one = self.reader.read_gamma()
            if size_plus_one == 0:
                break

            try:
                obj = self._read_record(fields, size_plus_one - 1)
                obj["index"] = len(objects)  # Add index
                objects.append(obj)
                # Small incremental progress for each record; never exceed chunk_end
                if step_inc > 0 and self._progress_value < chunk_end:
                    next_val = min(self._progress_value + step_inc, chunk_end)
                    self._progress_set(next_val, f"parsing {chunk_name.lower()}")
            except Exception as e:
                self.logger.warning(f"Error reading {chunk_name} object: {e}")
                break

        self.raw_data[chunk_name.lower()] = objects
        self.logger.debug(f"Parsed {len(objects)} objects from {chunk_name} chunk")

    def _parse_gamelog_chunk(self) -> None:
        """Parse GLOG chunk (game log)"""
        self._parse_table_chunk("GLOG")

    def _parse_maps_chunk(self) -> None:
        """Parse MAPS chunk (map settings)"""
        self._parse_table_chunk("MAPS")
        try:
            maps_list = self.raw_data.get("maps", [])
            if isinstance(maps_list, list) and maps_list:
                dim_x_val = int(maps_list[0].get("dim_x", 256))
                dim_y_val = int(maps_list[0].get("dim_y", 256))
            else:
                dim_x_val = 256
                dim_y_val = 256

            size = dim_x_val * dim_y_val
            planes: Dict[str, Any] = {}
            # RIFF planes as per map_sl.cpp
            for tag, elem_size, key in (
                (b"MAPT", 1, "type"),
                (b"MAPH", 1, "height"),
                (b"MAPO", 1, "m1"),
                (b"MAP2", 2, "m2"),
                (b"M3LO", 1, "m3"),
                (b"M3HI", 1, "m4"),
                (b"MAP5", 1, "m5"),
                (b"MAPE", 1, "m6"),
                (b"MAP7", 1, "m7"),
                (b"MAP8", 2, "m8"),
            ):
                payload = self.reader.read_riff_chunk_bytes(tag)
                if payload is None:
                    continue
                # Some planes are shorter on small maps; clamp
                # Ensure correct element count
                if elem_size == 1:
                    arr = list(payload[:size])
                    if len(arr) < size:
                        arr.extend([0] * (size - len(arr)))
                else:
                    # 2-byte big-endian unsigned
                    arr = []
                    data = payload
                    for i in range(0, min(len(data), size * 2), 2):
                        arr.append((data[i] << 8) | data[i + 1])
                    if len(arr) < size:
                        arr.extend([0] * (size - len(arr)))
                planes[key] = arr
            self.raw_data["map_planes"] = planes
        except Exception:
            # Non-fatal
            pass

    def _parse_vehicles_chunk(self) -> None:
        """Parse VEHS chunk (vehicles) - special sparse table handling"""
        pos = self.reader.find_chunk(b"VEHS")
        if pos is None:
            self.logger.debug("VEHS chunk not found")
            self.raw_data["vehs"] = []
            return

        self.reader.pos = pos + 4  # Skip chunk ID
        chunk_type = self.reader.read_byte()

        if chunk_type & 0x0F != ChunkType.CH_SPARSE_TABLE:
            self.logger.debug(f"VEHS is not a sparse table chunk (type: {chunk_type & 0x0F})")
            self.raw_data["vehs"] = []
            return

        # Read table header
        fields = self._read_table_header()

        # Read all records (sparse table format)
        vehicles: List[Dict[str, Any]] = []
        while True:
            size_plus_one = self.reader.read_gamma()
            if size_plus_one == 0:
                break

            # Read sparse index
            sparse_index = self.reader.read_gamma()

            # Calculate payload length (subtract gamma lengths)
            sparse_index_len = self._get_gamma_length(sparse_index)
            payload_len = size_plus_one - sparse_index_len - 1

            if payload_len <= 0:
                continue

            # Read vehicle type byte (SLE_SAVEBYTE)
            vehicle_type = self.reader.read_byte()
            payload_len -= 1

            if payload_len <= 0:
                continue

            try:
                # Parse the vehicle record (simple approach like working parser)
                vehicle_data = self._read_record(fields, payload_len)
                vehicle_data["index"] = sparse_index
                vehicle_data["type"] = vehicle_type
                vehicles.append(vehicle_data)
            except Exception as e:
                self.logger.warning(f"Error reading vehicle {sparse_index}: {e}")
                # Skip to end of this record
                self.reader.pos += payload_len

        self.raw_data["vehs"] = vehicles
        self.logger.debug(f"Parsed {len(vehicles)} vehicles from VEHS chunk")

    def _read_vehicle_by_type(
        self, fields: List[Field], payload_len: int, vehicle_type: int
    ) -> Dict[str, Any]:
        """Read vehicle record data based on vehicle type"""
        # Map vehicle type constants
        VEH_TRAIN = 0
        VEH_ROAD = 1
        VEH_SHIP = 2
        VEH_AIRCRAFT = 3
        VEH_EFFECT = 4
        VEH_DISASTER = 5

        # Map vehicle type to field name
        type_map = {
            VEH_TRAIN: "train",
            VEH_ROAD: "roadveh",
            VEH_SHIP: "ship",
            VEH_AIRCRAFT: "aircraft",
            VEH_EFFECT: "effect",
            VEH_DISASTER: "disaster",
        }

        # Find the field for this vehicle type
        type_name = type_map.get(vehicle_type, "unknown")
        type_field = None
        for field in fields:
            if field.key == type_name:
                type_field = field
                break

        if type_field is None:
            # Fallback: read as generic record
            return self._read_record(fields, payload_len)

        # Read the vehicle type structure
        vehicle_data: Dict[str, Any] = {}

        # Initialize all vehicle types as empty
        for vtype in type_map.values():
            vehicle_data[vtype] = {}

        # Read only the relevant vehicle type data
        if type_field.ftype == 11:  # STRUCT
            list_len = self.reader.read_gamma()
            if list_len == 1:
                vehicle_data[type_name] = self._read_struct_fields(type_field.subfields)

        return vehicle_data

    def _get_gamma_length(self, value: int) -> int:
        """Calculate the length in bytes of a gamma-encoded value"""
        if value < 128:
            return 1
        elif value < 16384:
            return 2
        elif value < 2097152:
            return 3
        elif value < 268435456:
            return 4
        else:
            return 5

    def _parse_orders_chunk(self) -> None:
        """Parse ORDR chunk (orders)"""
        self._parse_table_chunk("ORDR")

    def _parse_industries_chunk(self) -> None:
        """Parse INDY chunk (industries)"""
        self._parse_table_chunk("INDY")

    def _parse_subsidies_chunk(self) -> None:
        """Parse SUBS chunk (subsidies)"""
        self._parse_table_chunk("SUBS")

    def _parse_goals_chunk(self) -> None:
        """Parse GOAL chunk (goals)"""
        self._parse_table_chunk("GOAL")

    def _parse_league_tables_chunk(self) -> None:
        """Parse LEAT chunk (league tables)"""
        self._parse_table_chunk("LEAT")

    def _parse_league_elements_chunk(self) -> None:
        """Parse LEAE chunk (league elements)"""
        self._parse_table_chunk("LEAE")

    def _parse_engines_chunk(self) -> None:
        """Parse ENGN chunk (engines)"""
        self._parse_table_chunk("ENGN")

    def _parse_towns_chunk(self) -> None:
        """Parse CITY chunk (towns)"""
        self._parse_table_chunk("CITY")

    def _parse_signs_chunk(self) -> None:
        """Parse SIGN chunk (signs)"""
        self._parse_table_chunk("SIGN")

    def _parse_stations_chunk(self) -> None:
        """Parse STNN chunk (stations)"""
        self._parse_table_chunk("STNN")

    def _parse_companies_chunk(self) -> None:
        """Parse PLYR chunk (companies)"""
        self._parse_table_chunk("PLYR")

    def _parse_ai_players_chunk(self) -> None:
        """Parse AIPL chunk (AI players)"""
        self._parse_table_chunk("AIPL")

    def _parse_animated_tiles_chunk(self) -> None:
        """Parse ANIT chunk (animated tiles)"""
        self._parse_table_chunk("ANIT")

    def _parse_groups_chunk(self) -> None:
        """Parse GRPS chunk (groups)"""
        self._parse_table_chunk("GRPS")

    def _parse_cargo_packets_chunk(self) -> None:
        """Parse CAPA chunk (cargo packets)"""
        self._parse_table_chunk("CAPA")

    def _parse_link_graphs_chunk(self) -> None:
        """Parse LGRP chunk (link graphs)"""
        self._parse_table_chunk("LGRP")

    def _parse_link_graph_jobs_chunk(self) -> None:
        """Parse LGRJ chunk (link graph jobs)"""
        self._parse_table_chunk("LGRJ")

    def _parse_objects_chunk(self) -> None:
        """Parse OBJS chunk (objects)"""
        self._parse_table_chunk("OBJS")

    def _parse_settings_chunks(self) -> None:
        """Parse OPTS and PATS chunks (settings)"""
        self._parse_opts_chunk()
        self._parse_pats_chunk()

    def _parse_opts_chunk(self) -> None:
        """Parse OPTS chunk (options)"""
        self._parse_table_chunk("OPTS")

    def _parse_pats_chunk(self) -> None:
        """Parse PATS chunk (patches)"""
        self._parse_table_chunk("PATS")

    def _create_parsed_data(self) -> SaveFileData:
        """Create parsed data structure from raw data"""
        # Extract settings from PATS
        landscape = None
        default_max_loan: Optional[int] = None
        if "pats" in self.raw_data and self.raw_data["pats"]:
            for setting in self.raw_data["pats"]:
                if landscape is None and "game_creation.landscape" in setting:
                    landscape = setting["game_creation.landscape"]
                if default_max_loan is None and "difficulty.max_loan" in setting:
                    try:
                        default_max_loan = int(setting["difficulty.max_loan"])
                    except Exception:
                        pass

        # Create game data
        game_data = GameData(
            date=DateInfo(
                raw_date=self.raw_data.get("date", {}).get("date", 0),
                year=convert_date_to_year(self.raw_data.get("date", {}).get("date", 0)),
                month=convert_date_to_ymd(self.raw_data.get("date", {}).get("date", 0)).get(
                    "month", 1
                ),
                day=convert_date_to_ymd(self.raw_data.get("date", {}).get("date", 0)).get("day", 1),
                formatted=f"{convert_date_to_year(self.raw_data.get('date', {}).get('date', 0))}-{convert_date_to_ymd(self.raw_data.get('date', {}).get('date', 0)).get('month', 1):02d}-{convert_date_to_ymd(self.raw_data.get('date', {}).get('date', 0)).get('day', 1):02d}",
            ),
            economy_date=DateInfo(
                raw_date=self.raw_data.get("date", {}).get("economy_date", 0),
                year=convert_date_to_year(self.raw_data.get("date", {}).get("economy_date", 0)),
                month=convert_date_to_ymd(self.raw_data.get("date", {}).get("economy_date", 0)).get(
                    "month", 1
                ),
                day=convert_date_to_ymd(self.raw_data.get("date", {}).get("economy_date", 0)).get(
                    "day", 1
                ),
                formatted=f"{convert_date_to_year(self.raw_data.get('date', {}).get('economy_date', 0))}-{convert_date_to_ymd(self.raw_data.get('date', {}).get('economy_date', 0)).get('month', 1):02d}-{convert_date_to_ymd(self.raw_data.get('date', {}).get('economy_date', 0)).get('day', 1):02d}",
            ),
            inflation_prices=InflationInfo(
                raw_value=self.raw_data.get("economy", {}).get("inflation_prices", 0),
                percentage=format_inflation_value(
                    self.raw_data.get("economy", {}).get("inflation_prices", 0)
                ).get("percentage_change", 0.0),
                multiplier=self.raw_data.get("economy", {}).get("inflation_prices", 0) / 65536.0,
                formatted=f"{format_inflation_value(self.raw_data.get('economy', {}).get('inflation_prices', 0)).get('percentage_change', 0.0):.1f}%",
            ),
            inflation_payment=InflationInfo(
                raw_value=self.raw_data.get("economy", {}).get("inflation_payment", 0),
                percentage=format_inflation_value(
                    self.raw_data.get("economy", {}).get("inflation_payment", 0)
                ).get("percentage_change", 0.0),
                multiplier=self.raw_data.get("economy", {}).get("inflation_payment", 0) / 65536.0,
                formatted=f"{format_inflation_value(self.raw_data.get('economy', {}).get('inflation_payment', 0)).get('percentage_change', 0.0):.1f}%",
            ),
            max_loan=(
                default_max_loan
                if default_max_loan is not None
                else self.raw_data.get("economy", {}).get("max_loan", 0)
            ),
            interest_rate=self.raw_data.get("economy", {}).get("interest_rate", 0),
            landscape=landscape,
            economy_data=self.raw_data.get("economy", {}),
            settings_data=self.raw_data.get("pats", {}),
        )

        # Create map data (prefer MAPS table values if present)
        maps_list = self.raw_data.get("maps", [])
        if isinstance(maps_list, list) and maps_list:
            dim_x_val = int(maps_list[0].get("dim_x", 256))
            dim_y_val = int(maps_list[0].get("dim_y", 256))
        else:
            dim_x_val = int(self.raw_data.get("map_dim_x", 256))
            dim_y_val = int(self.raw_data.get("map_dim_y", 256))

        # Build FlatBuffers map if planes available
        flatbuf_map = None
        try:
            planes = self.raw_data.get("map_planes")
            if isinstance(planes, dict) and planes:
                flatbuf_map = build_map_flatbuffer(dim_x_val, dim_y_val, planes)
        except Exception:
            flatbuf_map = None

        map_data = MapData(
            dim_x=dim_x_val,
            dim_y=dim_y_val,
            tile_count=dim_x_val * dim_y_val,
            flatbuffers_map=flatbuf_map,
        )

        # Format companies
        companies_raw = self.raw_data.get("plyr", [])
        companies = []
        for company in companies_raw:
            try:
                formatted_company = format_company_data(
                    company, current_year=game_data.date.year, map_size_x=map_data.dim_x
                )
                companies.append(formatted_company)
            except Exception as e:
                self.logger.warning(f"Error formatting company: {e}")
                companies.append({"name": "Error", "id": 0})

        company_data = CompanyData(companies=companies, count=len(companies))

        # Format vehicles
        vehicles_raw = self.raw_data.get("vehs", [])
        vehicles = []
        for vehicle in vehicles_raw:
            formatted_vehicle = {
                "id": vehicle.get("index", 0),
                "type": vehicle.get("type", 0),
                "location": vehicle.get("location", 0),
                "owner": vehicle.get("owner", 0),
                "cargo": vehicle.get("cargo", []),
                "raw_data": vehicle,  # Include all raw vehicle data
            }
            vehicles.append(formatted_vehicle)

        vehicle_data = VehicleData(vehicles=vehicles, count=len(vehicles))

        # Format industries
        industries_raw = self.raw_data.get("indy", [])
        industries = []
        for industry in industries_raw:
            formatted_industry = {
                "id": industry.get("index", 0),
                "type": industry.get("type", 0),
                "location": industry.get("location", 0),
                "owner": industry.get("owner", 0),
            }
            industries.append(formatted_industry)

        industry_data = IndustryData(industries=industries, count=len(industries))

        # Format towns
        towns_raw = self.raw_data.get("city", [])
        towns = []
        for town in towns_raw:
            formatted_town = {
                "id": town.get("index", 0),
                "name": town.get("name", ""),
                "location": town.get("location", 0),
                "population": town.get("population", 0),
            }
            towns.append(formatted_town)

        town_data = TownData(towns=towns, count=len(towns))

        # Format stations
        stations_raw = self.raw_data.get("stnn", [])
        stations = []
        for station in stations_raw:
            formatted_station = {
                "id": station.get("index", 0),
                "name": station.get("name", ""),
                "location": station.get("location", 0),
                "owner": station.get("owner", 0),
            }
            stations.append(formatted_station)

        station_data = StationData(stations=stations, count=len(stations))

        # Create other data structures
        cargo_packet_data = CargoPacketData(packets=[], count=0)
        tile_data = TileData(tiles={}, count=0)
        sign_data = SignData(signs=[], count=0)
        order_data = OrderData(orders=[], count=0)
        depot_data = DepotData(depots=[], count=0)
        engine_data = EngineData(engines=[], count=0)
        group_data = GroupData(groups=[], count=0)
        goal_data = GoalData(goals=[], count=0)
        story_page_data = StoryPageData(pages=[], count=0)
        league_table_data = LeagueTableData(tables=[], count=0)
        ai_data = AIData(ais=[], count=0)
        game_log_data = GameLogData(logs=[], count=0)
        newgrf_data = NewGRFData(grfs=[], count=0)
        animated_tile_data = AnimatedTileData(tiles=[], count=0)
        link_graph_data = LinkGraphData(graphs=[], count=0)
        airport_data = AirportData(airports=[], count=0)
        object_data = ObjectData(objects=[], count=0)
        persistent_storage_data = PersistentStorageData(storages=[], count=0)
        water_region_data = WaterRegionData(regions=[], count=0)
        randomizer_data = RandomizerData(randomizers=[], count=0)

        # Create metadata
        meta_data = GameMeta(
            filename=self.filename,
            save_version=self.save_version,
            minor_version=self.minor_version,
            openttd_version="14.1",  # TODO: read from the savefile
        )

        # map_data already set above

        # Create SaveFileData
        return SaveFileData(
            meta=meta_data,
            game=game_data,
            map=map_data,
            companies=company_data,
            vehicles=vehicle_data,
            industries=industry_data,
            towns=town_data,
            stations=station_data,
            cargo_packets=cargo_packet_data,
            tiles=tile_data,
            signs=sign_data,
            orders=order_data,
            depots=depot_data,
            engines=engine_data,
            groups=group_data,
            goals=goal_data,
            story_pages=story_page_data,
            league_tables=league_table_data,
            ais=ai_data,
            game_logs=game_log_data,
            newgrfs=newgrf_data,
            animated_tiles=animated_tile_data,
            link_graphs=link_graph_data,
            airports=airport_data,
            objects=object_data,
            persistent_storage=persistent_storage_data,
            water_regions=water_region_data,
            randomizers=randomizer_data,
            raw_data=self.raw_data,  # Pass the raw data
        )

    # Progress helpers
    def _progress_set(self, value: float, stage: str) -> None:
        cb = getattr(self, "_progress_callback", None)
        if cb is None:
            self._progress_value = value
            return
        self._progress_value = max(0.0, min(1.0, value))
        try:
            cb(self._progress_value, stage)
        except Exception:
            pass


def load_savefile(
    filepath: str, parsed: bool = True, silent: bool = True, progress_callback: Optional[Any] = None
) -> Union[Dict[str, Any], SaveFileData]:
    """
    Load and parse an OpenTTD savefile.

    Args:
        filepath: Path to the savefile
        parsed: Whether to return parsed (human-readable) data or raw data
        silent: Whether to suppress debug output
        progress_callback: Optional callback(progress: float, stage: str) for progress reporting

    Returns:
        Either a raw dictionary or a structured SaveFileData object
    """
    parser = SaveParser(filepath, silent=silent)
    return parser.parse_savefile(parsed=parsed, progress_callback=progress_callback)


def load_savefile_from_bytes(
    raw_bytes: bytes,
    parsed: bool = True,
    silent: bool = True,
    progress_callback: Optional[Any] = None,
) -> Union[Dict[str, Any], SaveFileData]:
    """
    Load and parse an OpenTTD savefile provided as in-memory bytes.

    Intended for parsing map data streamed from a multiplayer server.
    The function will attempt to detect whether the bytes include an OTTX header
    or are a raw LZMA stream.

    Args:
        raw_bytes: Bytes of the savefile or map data
        parsed: Whether to return parsed (human-readable) data or raw data
        silent: Whether to suppress debug output
        progress_callback: Optional callback(progress: float, stage: str)

    Returns:
        Either a raw dictionary or a structured SaveFileData object
    """
    # Prepare a parser instance (filename is only used for logging metadata)
    parser = SaveParser("<bytes>", silent=silent)

    # Try to detect header and decompress appropriately
    data: bytes
    try:
        if len(raw_bytes) >= 8 and raw_bytes[:4] == b"OTTX":
            # Includes header: [OTTX][version_u32_be][lzma_stream]
            version_int = struct.unpack(">I", raw_bytes[4:8])[0]
            parser.save_version = (version_int >> 16) & 0xFFFF
            parser.minor_version = (version_int >> 8) & 0xFF
            data = lzma.decompress(raw_bytes[8:])
        else:
            # Might be a naked LZMA stream or already decompressed RIFF
            try:
                data = lzma.decompress(raw_bytes)
            except Exception:
                data = raw_bytes
    except Exception:
        # On any decompression error, fall back to raw bytes
        data = raw_bytes

    # Set reader directly and run the normal parsing pipeline
    parser.reader = BinaryReader(data)

    # Progress init
    parser._progress_callback = progress_callback
    parser._progress_value = 0.0
    parser._progress_set(0.05, "loaded")
    parser._parse_all_chunks()

    if parsed:
        result = parser._create_parsed_data()
        parser._progress_set(1.0, "done")
        return result
    else:
        parser._progress_set(1.0, "done")
        return parser.raw_data
