"""
# int.py - Integer Value Function Storage
"""
# Integer encoders with endianness support

# Ranges for unsigned/signed values
UINT_RANGES = {8: (0, 0xFF), 16: (0, 0xFFFF), 32: (0, 0xFFFFFFFF), 64: (0, 0xFFFFFFFFFFFFFFFF)}
SINT_RANGES = {8: (-128, 127), 16: (-32768, 32767), 32: (-2147483648, 2147483647), 64: (-9223372036854775808, 9223372036854775807)}

def UINT(value: int, bits: int, endianess: str = "little") -> bytes:
    """Encode unsigned integer of given bit size."""
    if bits not in UINT_RANGES:
        raise ValueError(f"Unsupported UINT size: {bits}")
    lo, hi = UINT_RANGES[bits]
    if not (lo <= value <= hi):
        raise ValueError(f"UINT{bits} out of range: {value}")
    return value.to_bytes(bits // 8, endianess, signed=False)

def SINT(value: int, bits: int, endianess: str = "little") -> bytes:
    """Encode signed integer of given bit size."""
    if bits not in SINT_RANGES:
        raise ValueError(f"Unsupported SINT size: {bits}")
    lo, hi = SINT_RANGES[bits]
    if not (lo <= value <= hi):
        raise ValueError(f"SINT{bits} out of range: {value}")
    return value.to_bytes(bits // 8, endianess, signed=True)

def UINT8(value: int, endianess="little") -> bytes: return UINT(value, 8, endianess)
def UINT16(value: int, endianess="little") -> bytes: return UINT(value, 16, endianess)
def UINT32(value: int, endianess="little") -> bytes: return UINT(value, 32, endianess)
def UINT64(value: int, endianess="little") -> bytes: return UINT(value, 64, endianess)

def SINT8(value: int, endianess="little") -> bytes: return SINT(value, 8, endianess)
def SINT16(value: int, endianess="little") -> bytes: return SINT(value, 16, endianess)
def SINT32(value: int, endianess="little") -> bytes: return SINT(value, 32, endianess)
def SINT64(value: int, endianess="little") -> bytes: return SINT(value, 64, endianess)
