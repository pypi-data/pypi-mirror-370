"""
FlatBuffers schema and builder for OpenTTD map data (tiles).

Schema (conceptual):

table MapFB {
  width:uint32;
  height:uint32;
  // Each vector has length width*height.
  type:[ubyte];
  heightmap:[ubyte];
  m1:[ubyte];
  m2:[ushort];
  m3:[ubyte];
  m4:[ubyte];
  m5:[ubyte];
  m6:[ubyte];
  m7:[ubyte];
  m8:[ushort];
}

root_type MapFB;

"""

from __future__ import annotations

from typing import Dict, Any, List, Optional, cast

import flatbuffers  # type: ignore[import-untyped]


class MapFB(object):
    __slots__ = [
        "_tab",
    ]

    @classmethod
    def GetRootAsMapFB(cls, buf: bytes, offset: int = 0) -> "MapFB":
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = MapFB()
        x.Init(buf, n + offset)
        return x

    # FlatBuffers table vtable fields indices
    # Field slot -> vtable offset mapping: offset = 4 + slot_index * 2
    # Slots: 0:type, 1:heightmap, 2:m1, 3:m2, 4:m3, 5:m4, 6:m5, 7:m6, 8:m7, 9:m8, 10:height, 11:width
    VT_TYPE = 4
    VT_HEIGHTMAP = 6
    VT_M1 = 8
    VT_M2 = 10
    VT_M3 = 12
    VT_M4 = 14
    VT_M5 = 16
    VT_M6 = 18
    VT_M7 = 20
    VT_M8 = 22
    VT_HEIGHT = 24
    VT_WIDTH = 26

    def Init(self, buf: bytes, pos: int) -> None:
        self._tab = flatbuffers.table.Table(buf, pos)

    def Width(self) -> int:
        o = self._tab.Offset(MapFB.VT_WIDTH)
        return (
            cast(int, self._tab.Get(flatbuffers.number_types.Uint32Flags, o + self._tab.Pos))
            if o
            else 0
        )

    def Height(self) -> int:
        o = self._tab.Offset(MapFB.VT_HEIGHT)
        return (
            cast(int, self._tab.Get(flatbuffers.number_types.Uint32Flags, o + self._tab.Pos))
            if o
            else 0
        )

    def Type(self, j: int) -> int:
        o = self._tab.Offset(MapFB.VT_TYPE)
        if o == 0:
            return 0
        a = self._tab.Vector(o)
        return cast(int, self._tab.Get(flatbuffers.number_types.Uint8Flags, a + j * 1))

    def TypeLength(self) -> int:
        o = self._tab.Offset(MapFB.VT_TYPE)
        return self._tab.VectorLen(o) if o else 0

    def Heightmap(self, j: int) -> int:
        o = self._tab.Offset(MapFB.VT_HEIGHTMAP)
        if o == 0:
            return 0
        a = self._tab.Vector(o)
        return cast(int, self._tab.Get(flatbuffers.number_types.Uint8Flags, a + j * 1))

    def HeightmapLength(self) -> int:
        o = self._tab.Offset(MapFB.VT_HEIGHTMAP)
        return self._tab.VectorLen(o) if o else 0

    def M1(self, j: int) -> int:
        o = self._tab.Offset(MapFB.VT_M1)
        if o == 0:
            return 0
        a = self._tab.Vector(o)
        return cast(int, self._tab.Get(flatbuffers.number_types.Uint8Flags, a + j * 1))

    def M1Length(self) -> int:
        o = self._tab.Offset(MapFB.VT_M1)
        return self._tab.VectorLen(o) if o else 0

    def M2(self, j: int) -> int:
        o = self._tab.Offset(MapFB.VT_M2)
        if o == 0:
            return 0
        a = self._tab.Vector(o)
        return cast(int, self._tab.Get(flatbuffers.number_types.Uint16Flags, a + j * 2))

    def M2Length(self) -> int:
        o = self._tab.Offset(MapFB.VT_M2)
        return self._tab.VectorLen(o) if o else 0

    def M3(self, j: int) -> int:
        o = self._tab.Offset(MapFB.VT_M3)
        if o == 0:
            return 0
        a = self._tab.Vector(o)
        return cast(int, self._tab.Get(flatbuffers.number_types.Uint8Flags, a + j * 1))

    def M3Length(self) -> int:
        o = self._tab.Offset(MapFB.VT_M3)
        return self._tab.VectorLen(o) if o else 0

    def M4(self, j: int) -> int:
        o = self._tab.Offset(MapFB.VT_M4)
        if o == 0:
            return 0
        a = self._tab.Vector(o)
        return cast(int, self._tab.Get(flatbuffers.number_types.Uint8Flags, a + j * 1))

    def M4Length(self) -> int:
        o = self._tab.Offset(MapFB.VT_M4)
        return self._tab.VectorLen(o) if o else 0

    def M5(self, j: int) -> int:
        o = self._tab.Offset(MapFB.VT_M5)
        if o == 0:
            return 0
        a = self._tab.Vector(o)
        return cast(int, self._tab.Get(flatbuffers.number_types.Uint8Flags, a + j * 1))

    def M5Length(self) -> int:
        o = self._tab.Offset(MapFB.VT_M5)
        return self._tab.VectorLen(o) if o else 0

    def M6(self, j: int) -> int:
        o = self._tab.Offset(MapFB.VT_M6)
        if o == 0:
            return 0
        a = self._tab.Vector(o)
        return cast(int, self._tab.Get(flatbuffers.number_types.Uint8Flags, a + j * 1))

    def M6Length(self) -> int:
        o = self._tab.Offset(MapFB.VT_M6)
        return self._tab.VectorLen(o) if o else 0

    def M7(self, j: int) -> int:
        o = self._tab.Offset(MapFB.VT_M7)
        if o == 0:
            return 0
        a = self._tab.Vector(o)
        return cast(int, self._tab.Get(flatbuffers.number_types.Uint8Flags, a + j * 1))

    def M7Length(self) -> int:
        o = self._tab.Offset(MapFB.VT_M7)
        return self._tab.VectorLen(o) if o else 0

    def M8(self, j: int) -> int:
        o = self._tab.Offset(MapFB.VT_M8)
        if o == 0:
            return 0
        a = self._tab.Vector(o)
        return cast(int, self._tab.Get(flatbuffers.number_types.Uint16Flags, a + j * 2))

    def M8Length(self) -> int:
        o = self._tab.Offset(MapFB.VT_M8)
        return self._tab.VectorLen(o) if o else 0


def _create_u8_vector(builder: flatbuffers.Builder, data: List[int]) -> int:
    builder.StartVector(1, len(data), 1)
    for v in reversed(data):
        builder.PrependUint8(v & 0xFF)
    return cast(int, builder.EndVector())


def _create_u16_vector(builder: flatbuffers.Builder, data: List[int]) -> int:
    builder.StartVector(2, len(data), 2)
    for v in reversed(data):
        builder.PrependUint16(v & 0xFFFF)
    return cast(int, builder.EndVector())


def build_map_flatbuffer(width: int, height: int, planes: Dict[str, Any]) -> bytes:
    """Build a FlatBuffers buffer for the map planes.

    planes keys: "type", "height", "m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8"
    Missing planes will be filled with zeros.
    """
    size = max(0, int(width) * int(height))

    def take(name: str, default: int, bits: int) -> List[int]:
        arr = planes.get(name)
        if not isinstance(arr, list):
            return [0] * size
        # clamp and cast
        if bits == 8:
            return [(int(v) & 0xFF) for v in (arr[:size] + [0] * (size - len(arr)))]
        else:
            return [(int(v) & 0xFFFF) for v in (arr[:size] + [0] * (size - len(arr)))]

    type_arr = take("type", 0, 8)
    height_arr = take("height", 0, 8)
    m1_arr = take("m1", 0, 8)
    m2_arr = take("m2", 0, 16)
    m3_arr = take("m3", 0, 8)
    m4_arr = take("m4", 0, 8)
    m5_arr = take("m5", 0, 8)
    m6_arr = take("m6", 0, 8)
    m7_arr = take("m7", 0, 8)
    m8_arr = take("m8", 0, 16)

    builder = flatbuffers.Builder(0)

    v_type = _create_u8_vector(builder, type_arr)
    v_height = _create_u8_vector(builder, height_arr)
    v_m1 = _create_u8_vector(builder, m1_arr)
    v_m2 = _create_u16_vector(builder, m2_arr)
    v_m3 = _create_u8_vector(builder, m3_arr)
    v_m4 = _create_u8_vector(builder, m4_arr)
    v_m5 = _create_u8_vector(builder, m5_arr)
    v_m6 = _create_u8_vector(builder, m6_arr)
    v_m7 = _create_u8_vector(builder, m7_arr)
    v_m8 = _create_u16_vector(builder, m8_arr)

    # Manually create a table: we need to write vtable and fields.
    # We use the low-level API via Table-like construction.
    # Start object with 11 fields.
    builder.StartObject(12)
    # Add fields in reverse order of writing vectors isn't required in vtable context but we follow typical pattern.
    builder.PrependUOffsetTRelativeSlot(9, v_m8, 0)  # slot id 10 -> index 9 zero-based here
    builder.PrependUOffsetTRelativeSlot(8, v_m7, 0)
    builder.PrependUOffsetTRelativeSlot(7, v_m6, 0)
    builder.PrependUOffsetTRelativeSlot(6, v_m5, 0)
    builder.PrependUOffsetTRelativeSlot(5, v_m4, 0)
    builder.PrependUOffsetTRelativeSlot(4, v_m3, 0)
    builder.PrependUOffsetTRelativeSlot(3, v_m2, 0)
    builder.PrependUOffsetTRelativeSlot(2, v_m1, 0)
    builder.PrependUOffsetTRelativeSlot(1, v_height, 0)
    builder.PrependUOffsetTRelativeSlot(0, v_type, 0)
    builder.PrependUint32Slot(10, int(height), 0)  # slot 10
    builder.PrependUint32Slot(11, int(width), 0)  # slot 11

    map_obj = builder.EndObject()

    builder.Finish(map_obj)
    return bytes(builder.Output())
