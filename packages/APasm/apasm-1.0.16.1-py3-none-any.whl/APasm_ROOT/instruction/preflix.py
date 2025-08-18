seg = {
    "cs": 0x2E,  # CS segment override
    "ss": 0x36,  # SS segment override
    "ds": 0x3E,  # DS segment override
    "es": 0x26,  # ES segment override
    "fs": 0x64,  # FS segment override
    "gs": 0x65   # GS segment override
}

seg_reg_val = {
    "es": 0b000,
    "cs": 0b001,
    "ss": 0b010,
    "ds": 0b011,
    "fs": 0b100,
    "gs": 0b101
}

lock_prefix     = 0xF0
rep_prefix      = 0xF3   # REP / REPE / REPZ
repne_prefix    = 0xF2   # REPNE / REPNZ
opsize_prefix   = 0x66   # Operand-size override
addrsize_prefix = 0x67   # Address-size override

def segment(segment):
    """
    Returns the x86 segment override prefix byte for a given segment register.
    Args:
        segment (str): Segment register name (e.g., 'cs', 'DS', 'es').
    Returns:
        int: Hex byte for the segment override prefix (e.g., 0x2E for 'cs').
        str: Error message if the segment is invalid.
    """
    segment = segment.lower()  # Normalize input to lowercase
    if segment not in seg:
        return f"Error: '{segment}' is not a valid segment register (cs, ss, ds, es, fs, gs)"
    return seg[segment]

def rex(w=0, r=0, x=0, b=0):
    return bytes([0x40 | (w << 3) | (r << 2) | (x << 1) | b])

def override_seg_reg(reg: str) -> bytes:
    """Return the segment override prefix byte for a given segment register."""
    seg_prefixes = {
        "es": 0x26,
        "cs": 0x2E,
        "ss": 0x36,
        "ds": 0x3E,
        "fs": 0x64,
        "gs": 0x65,
    }
    reg_lower = reg.lower()
    if reg_lower in seg_prefixes:
        return bytes([seg_prefixes[reg_lower]])
    else:
        raise ValueError(f"Unknown segment register: {reg}")