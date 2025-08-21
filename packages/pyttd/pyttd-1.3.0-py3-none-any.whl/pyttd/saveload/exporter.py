"""
JSON Export functionality for savefile data.
"""

import json
import gzip
import lzma
from typing import Dict, List, Any, Optional, Union, TextIO
from pathlib import Path
from datetime import datetime
from dataclasses import asdict, is_dataclass
from enum import IntEnum

from .models import (
    SaveFileData,
    VehicleType,
    CargoType,
    IndustryType,
    DateInfo,
    InflationInfo,
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
)


class SaveJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for OpenTTD data types"""

    def default(self, obj: Any) -> Any:
        # Handle dataclasses
        if is_dataclass(obj):
            # mypy wants DataclassInstance; asdict accepts dataclass instances.
            return asdict(obj)  # type: ignore[arg-type]

        # Handle enums
        if isinstance(obj, IntEnum):
            return {
                "value": obj.value,
                "name": obj.name,
                "display_name": self._get_enum_display_name(obj),
            }

        # Handle datetime objects
        if isinstance(obj, datetime):
            return obj.isoformat()

        # Handle bytes objects
        if isinstance(obj, bytes):
            # Avoid dumping massive binary - flatbuffer is used for that
            return {"type": "bytes", "length": len(obj)}

        # Handle sets
        if isinstance(obj, set):
            return list(obj)

        # Handle other non-serializable types
        return str(obj)

    def _get_enum_display_name(self, enum_obj: IntEnum) -> str:
        """Get a human-readable display name for enum values"""
        if isinstance(enum_obj, VehicleType):
            return enum_obj.name.replace("VEH_", "").title()
        elif isinstance(enum_obj, CargoType):
            return enum_obj.name.replace("CT_", "").replace("_", " ").title()
        elif isinstance(enum_obj, IndustryType):
            return enum_obj.name.replace("INDUSTRY_", "").replace("_", " ").title()
        else:
            return enum_obj.name.replace("_", " ").title()


class SaveFileExporter:
    """Export OpenTTD savefile data to JSON format"""

    def __init__(self, save_data: Union[Dict[str, Any], SaveFileData]):
        """
        Initialize the exporter with savefile data.

        Args:
            save_data: Either a raw dictionary or a SaveFileData object
        """
        self.save_data = save_data
        self.encoder = SaveJSONEncoder(indent=2, sort_keys=True)

    def export_to_json(
        self,
        output_path: Union[str, Path],
        parsed: bool = True,
        include_raw: bool = False,
        pretty: bool = True,
        progress_callback: Optional[Any] = None,
    ) -> None:
        """
        Export savefile data to JSON file.

        Args:
            output_path: Path to output JSON file
            parsed: Whether to export parsed (human-readable) data or raw data
            include_raw: Whether to include raw data alongside parsed data
            pretty: Whether to format JSON with indentation
            progress_callback: Callback for tracking progress
        """
        output_path = Path(output_path)

        export_data = self._prepare_export_data(parsed, include_raw)

        # This monstrosity here is to track progress
        if progress_callback:
            progress_callback(0.2, "export_prepare")
        if pretty:
            json_str = self.encoder.encode(export_data)
        else:
            json_str = json.dumps(export_data, cls=SaveJSONEncoder, separators=(",", ":"))
        if progress_callback:
            progress_callback(0.6, "export_encode")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_str)
        if progress_callback:
            progress_callback(1.0, "export_done")

    def export_to_string(
        self,
        parsed: bool = True,
        include_raw: bool = False,
        pretty: bool = True,
        progress_callback: Optional[Any] = None,
    ) -> str:
        """
        Export savefile data to JSON string.

        Args:
            parsed: Whether to export parsed (human-readable) data or raw data
            include_raw: Whether to include raw data alongside parsed data
            pretty: Whether to format JSON with indentation
            progress_callback: Callback for tracking progress

        Returns:
            JSON string representation of the data
        """
        export_data = self._prepare_export_data(parsed, include_raw)
        if progress_callback:
            progress_callback(0.2, "export_prepare")

        if pretty:
            s = self.encoder.encode(export_data)
        else:
            s = json.dumps(export_data, cls=SaveJSONEncoder, separators=(",", ":"))
        if progress_callback:
            progress_callback(1.0, "export_done")
        return s

    def export_to_stream(
        self,
        stream: TextIO,
        parsed: bool = True,
        include_raw: bool = False,
        pretty: bool = True,
        progress_callback: Optional[Any] = None,
    ) -> None:
        """
        Export savefile data to a text stream.

        Args:
            stream: Text stream to write to
            parsed: Whether to export parsed (human-readable) data or raw data
            include_raw: Whether to include raw data alongside parsed data
            pretty: Whether to format JSON with indentation
            progress_callback: Callback for tracking progress
        """
        export_data = self._prepare_export_data(parsed, include_raw)
        if progress_callback:
            progress_callback(0.2, "export_prepare")

        if pretty:
            json_str = self.encoder.encode(export_data)
        else:
            json_str = json.dumps(export_data, cls=SaveJSONEncoder, separators=(",", ":"))
        if progress_callback:
            progress_callback(0.6, "export_encode")

        stream.write(json_str)
        if progress_callback:
            progress_callback(1.0, "export_done")

    def _prepare_export_data(self, parsed: bool, include_raw: bool) -> Dict[str, Any]:
        """
        Prepare data for export based on the specified options.

        Args:
            parsed: Whether to export parsed data
            include_raw: Whether to include raw data

        Returns:
            Dictionary ready for JSON serialization (with metadata)
        """
        if isinstance(self.save_data, SaveFileData):
            # We have a structured SaveFileData object
            if parsed:
                export_data = self._convert_save_data_to_dict(self.save_data)
                if include_raw:
                    export_data["raw_data"] = self.save_data.raw_data
            else:
                # Export raw data only
                export_data = self.save_data.raw_data
        else:
            # We have a raw dictionary
            if parsed:
                # Disallow exporting parsed format from raw dicts; require parser first
                raise ValueError(
                    "Parsed export requires a SaveFileData object. "
                    "Run load_savefile(parsed=True)."
                )
            else:
                # Export raw data as-is
                export_data = self.save_data

        # Add export metadata
        export_data["_export_metadata"] = {
            "exported_at": datetime.now().isoformat(),
            "parsed": parsed,
            "include_raw": include_raw,
        }

        return export_data

    def _convert_save_data_to_dict(self, save_data: SaveFileData) -> Dict[str, Any]:
        """Convert SaveFileData to dictionary for JSON export"""
        result = {
            "meta": asdict(save_data.meta),
            "game": asdict(save_data.game),
            "map": asdict(save_data.map),
            "companies": asdict(save_data.companies),
            "vehicles": asdict(save_data.vehicles),
            "industries": asdict(save_data.industries),
            "towns": asdict(save_data.towns),
            "stations": asdict(save_data.stations),
            "cargo_packets": asdict(save_data.cargo_packets),
            "tiles": asdict(save_data.tiles),
            "signs": asdict(save_data.signs),
            "orders": asdict(save_data.orders),
            "depots": asdict(save_data.depots),
            "engines": asdict(save_data.engines),
            "groups": asdict(save_data.groups),
            "goals": asdict(save_data.goals),
            "story_pages": asdict(save_data.story_pages),
            "league_tables": asdict(save_data.league_tables),
            "ais": asdict(save_data.ais),
            "game_logs": asdict(save_data.game_logs),
            "newgrfs": asdict(save_data.newgrfs),
            "animated_tiles": asdict(save_data.animated_tiles),
            "link_graphs": asdict(save_data.link_graphs),
            "airports": asdict(save_data.airports),
            "objects": asdict(save_data.objects),
            "persistent_storage": asdict(save_data.persistent_storage),
            "water_regions": asdict(save_data.water_regions),
            "randomizers": asdict(save_data.randomizers),
            "statistics": save_data.statistics,
        }

        return result


def export_savefile_to_json(
    save_data: Union[Dict[str, Any], SaveFileData],
    output_path: Union[str, Path],
    parsed: bool = True,
    include_raw: bool = False,
    pretty: bool = True,
    progress_callback: Optional[Any] = None,
) -> None:
    """
    Convenience function to export savefile data to JSON.

    Args:
        save_data: Savefile data to export
        output_path: Path to output JSON file
        parsed: Whether to export parsed (human-readable) data or raw data
        include_raw: Whether to include raw data alongside parsed data
        compress: Whether to compress the output (gzip)
        pretty: Whether to format JSON with indentation
        progress_callback: Callback for tracking progress
    """
    exporter = SaveFileExporter(save_data)
    exporter.export_to_json(output_path, parsed, include_raw, pretty, progress_callback)


def export_savefile_to_string(
    save_data: Union[Dict[str, Any], SaveFileData],
    parsed: bool = True,
    include_raw: bool = False,
    pretty: bool = True,
    progress_callback: Optional[Any] = None,
) -> str:
    """
    Convenience function to export savefile data to JSON string.

    Args:
        save_data: Savefile data to export
        parsed: Whether to export parsed (human-readable) data or raw data
        include_raw: Whether to include raw data alongside parsed data
        pretty: Whether to format JSON with indentation
        progress_callback: Callback for tracking progress

    Returns:
        JSON string representation of the data
    """
    exporter = SaveFileExporter(save_data)
    return exporter.export_to_string(parsed, include_raw, pretty, progress_callback)
