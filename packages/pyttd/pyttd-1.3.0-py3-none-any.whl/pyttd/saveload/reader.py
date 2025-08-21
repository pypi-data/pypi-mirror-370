"""
Binary reader for OpenTTD savefiles
"""

import struct
from typing import Any, Dict, List, Optional, Tuple
from enum import IntEnum


class ChunkType(IntEnum):
    """Chunk types"""

    CH_RIFF = 0
    CH_ARRAY = 1
    CH_SPARSE_ARRAY = 2
    CH_TABLE = 3
    CH_SPARSE_TABLE = 4


class SaveLoadType(IntEnum):
    """Save/load field types"""

    SLE_FILE_I8 = 1
    SLE_FILE_U8 = 2
    SLE_FILE_I16 = 3
    SLE_FILE_U16 = 4
    SLE_FILE_I32 = 5
    SLE_FILE_U32 = 6
    SLE_FILE_I64 = 7
    SLE_FILE_U64 = 8
    SLE_FILE_STRINGID = 9
    SLE_FILE_STRING = 10
    SLE_FILE_STRUCT = 11

    # Flags
    SLE_FILE_HAS_LENGTH_FIELD = 0x10
    SLE_FILE_TYPE_MASK = 0x0F
    SLE_FILE_END = 0

    # Variable types (for SLE_FILE_XXX | SLE_VAR_XXX combinations)
    SLE_VAR_I8 = 0x20
    SLE_VAR_U8 = 0x21
    SLE_VAR_I16 = 0x22
    SLE_VAR_U16 = 0x23
    SLE_VAR_I32 = 0x24
    SLE_VAR_U32 = 0x25
    SLE_VAR_I64 = 0x26
    SLE_VAR_U64 = 0x27
    SLE_VAR_STRINGID = 0x28
    SLE_VAR_STRING = 0x29
    SLE_VAR_STRUCT = 0x2A

    # Variable type mask
    SLE_VAR_TYPE_MASK = 0x3F


class BinaryReader:
    """Binary reader"""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def read_byte(self) -> int:
        """Read a single byte"""
        if self.pos >= len(self.data):
            raise ValueError("End of data")
        result = self.data[self.pos]
        self.pos += 1
        return result

    def read_bytes(self, count: int) -> bytes:
        """Read specified number of bytes"""
        if self.pos + count > len(self.data):
            raise ValueError(f"Not enough data: need {count}, have {len(self.data) - self.pos}")
        result = self.data[self.pos : self.pos + count]
        self.pos += count
        return result

    def read_gamma(self) -> int:
        """Read gamma-encoded integer"""
        val = self.read_byte()
        if val & 0x80:
            val &= ~0x80
            if val & 0x40:
                val &= ~0x40
                if val & 0x20:
                    val &= ~0x20
                    if val & 0x10:
                        val &= ~0x10
                        if val & 0x08:
                            raise ValueError("Unsupported gamma (>32 bits)")
                        val = self.read_byte()  # 32 bits only
                    val = (val << 8) | self.read_byte()
                val = (val << 8) | self.read_byte()
            val = (val << 8) | self.read_byte()
        return val

    def read_uint8(self) -> int:
        """Read 8-bit unsigned integer"""
        return self.read_byte()

    def read_int8(self) -> int:
        """Read 8-bit signed integer"""
        val = self.read_byte()
        if val > 127:
            val -= 256
        return val

    def read_uint16(self) -> int:
        """Read 16-bit unsigned integer"""
        x = self.read_byte() << 8
        return x | self.read_byte()

    def read_int16(self) -> int:
        """Read 16-bit signed integer"""
        val = self.read_uint16()
        # Convert to signed if the high bit is set
        if val > 32767:
            return val - 65536
        return val

    def read_uint32(self) -> int:
        """Read 32-bit unsigned integer"""
        x = self.read_uint16()
        y = self.read_uint16()
        return (x << 16) | y

    def read_int32(self) -> int:
        """Read 32-bit signed integer"""
        val = self.read_uint32()
        # Convert to signed if the high bit is set
        if val > 2147483647:
            return val - 4294967296
        return val

    def read_uint64(self) -> int:
        """Read 64-bit unsigned integer"""
        x = self.read_uint32()
        y = self.read_uint32()
        return (x << 32) | y

    def read_int64(self) -> int:
        """Read 64-bit signed integer"""
        val = self.read_uint64()
        # Convert to signed if the high bit is set
        if val > 9223372036854775807:
            return val - 18446744073709551616
        return val

    def read_string(self) -> str:
        """Read string (gamma length + bytes)"""
        strlen = self.read_gamma()
        if strlen == 0:
            return ""
        data = self.read_bytes(strlen)
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("latin-1", errors="replace")

    def sl_save_load_conv(self, field_type: int) -> Any:
        """Convert field"""
        # Extract the base type (lower 4 bits)
        base_type = field_type & 0x0F

        # Simple field types
        if base_type == 1:  # I8
            return self.read_int8()
        elif base_type == 2:  # U8
            return self.read_uint8()
        elif base_type == 3:  # I16
            return self.read_int16()
        elif base_type == 4:  # U16
            return self.read_uint16()
        elif base_type == 5:  # I32
            return self.read_int32()
        elif base_type == 6:  # U32
            return self.read_uint32()
        elif base_type == 7:  # I64
            return self.read_int64()
        elif base_type == 8:  # U64
            return self.read_uint64()
        elif base_type == 9:  # STRINGID (U16)
            return self.read_uint16()
        elif base_type == 10:  # STRING
            return self.read_string()
        elif base_type == 11:  # STRUCT
            # This should be handled by the caller
            raise ValueError("STRUCT type should be handled by caller")
        else:
            raise ValueError(f"Unknown field type: {field_type}")

    def sl_read_uint64_signed(self) -> int:
        """Read 64-bit unsigned integer and convert to signed if needed"""
        val = self.read_uint64()
        # Convert to signed if the high bit is set
        if val & 0x8000000000000000:
            val = val - 0x10000000000000000
        return val

    def sl_read_simple_gamma(self) -> int:
        """Read simple gamma-encoded integer (for array lengths)"""
        return self.read_gamma()

    def find_chunk(self, chunk_id: bytes) -> Optional[int]:
        """Find a chunk by ID"""
        pos = 0
        while pos < len(self.data) - 4:
            if self.data[pos : pos + 4] == chunk_id:
                return pos
            pos += 1
        return None

    def list_all_chunks(self) -> List[Tuple[bytes, int]]:
        """List all chunks in the data"""
        chunks = []
        pos = 0
        while pos < len(self.data) - 4:
            chunk_id = self.data[pos : pos + 4]
            # Check if it looks like a valid chunk ID (4 ASCII letters)
            if all(65 <= b <= 90 for b in chunk_id):  # A-Z
                chunks.append((chunk_id, pos))
            pos += 1
        return chunks

    def read_riff_chunk_bytes(self, chunk_id: bytes) -> Optional[bytes]:
        """Read a CH_RIFF chunk payload by ID without changing current position.

        Returns the raw payload bytes, or None if not found or not a RIFF chunk.
        """
        pos = self.find_chunk(chunk_id)
        if pos is None:
            return None
        # Layout: [4 bytes tag][1 byte type][3 bytes length_low]
        if pos + 8 > len(self.data):
            return None
        type_byte = self.data[pos + 4]
        if (type_byte & 0x0F) != ChunkType.CH_RIFF:
            return None
        length_low = (self.data[pos + 5] << 16) | (self.data[pos + 6] << 8) | self.data[pos + 7]
        length = length_low | ((type_byte >> 4) << 24)
        start = pos + 8
        end = start + length
        if end > len(self.data):
            # Corrupt; clamp to available data
            end = len(self.data)
        return self.data[start:end]
