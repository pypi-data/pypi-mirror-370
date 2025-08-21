"""
Helpers for decoding per-tile information (owner, industry) from map planes.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, Tuple

from .models import IndustryType


def decode_tile_type(type_byte: int) -> int:
    """Upper nibble (bits 4..7) is the TileType."""
    return (int(type_byte) >> 4) & 0x0F


def decode_owner(type_byte: int, m1: int) -> Optional[int]:
    """Decode owner from m1 lower 5 bits for most tile types.

    Not applicable for MP_HOUSE (3) and MP_INDUSTRY (8).
    Returns owner id or None.
    """
    tile_type = decode_tile_type(type_byte)
    if tile_type in (3, 8):  # MP_HOUSE, MP_INDUSTRY
        return None
    return int(m1) & 0x1F


def decode_industry_info(
    m1: int, m2: int, m3: int, m4: int, m5: int, m6: int, m7: int
) -> Dict[str, Any]:
    """Decode several industry-related fields from m1..m7 for MP_INDUSTRY tiles.

    Based on industry_map.h:
    - id: m2
    - completed: bit 7 of m1
    - construction_stage: bits 0..1 of m1 (when not completed)
    - construction_counter: bits 2..3 of m1
    - random_bits: m3
    - anim_loop: m4
    - gfx_id: low 8 bits in m5 plus bit 8 in m6 bit 2
    - triggers: bits 3..5 of m6
    - anim_frame: m7
    """
    completed = bool((int(m1) >> 7) & 0x01)
    stage = 3 if completed else (int(m1) & 0x03)
    counter = (int(m1) >> 2) & 0x03
    gfx = (int(m5) & 0xFF) | (((int(m6) >> 2) & 0x01) << 8)
    triggers = (int(m6) >> 3) & 0x07
    return {
        "industry_id": int(m2),
        "completed": completed,
        "construction_stage": stage,
        "construction_counter": counter,
        "random_bits": int(m3),
        "anim_loop": int(m4),
        "gfx_id": gfx,
        "triggers": triggers,
        "anim_frame": int(m7),
    }


SPECIAL_OWNER_NAMES = {
    0x0F: "Town",
    0x10: "None",
    0x11: "Water",
    0x12: "Deity",
}


def owner_display(owner_id: Optional[int], company_names: Dict[int, str]) -> str:
    if owner_id is None:
        return "N/A"
    if owner_id in SPECIAL_OWNER_NAMES:
        return f"{owner_id} ({SPECIAL_OWNER_NAMES[owner_id]})"
    name = company_names.get(owner_id, f"Company {owner_id}")
    return f"{owner_id} ({name})"


def industry_type_display(type_id: int) -> str:
    try:
        return f"{type_id} ({IndustryType(type_id).name})"
    except Exception:
        return str(type_id)
