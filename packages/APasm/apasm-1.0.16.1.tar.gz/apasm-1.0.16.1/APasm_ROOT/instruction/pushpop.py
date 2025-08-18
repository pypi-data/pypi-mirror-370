def pusha() -> bytes:
    """
    Encode PUSHA (push all 16-bit registers).
    """
    opcode = 0x60
    return bytes([opcode])

def pushad() -> bytes:
    """
    Encode PUSHAD (push all 32-bit registers).
    """
    opcode = 0x60
    return bytes([opcode])

def pusha_in_32bit() -> bytes:
    """
    Force PUSHA inside 32-bit mode using 0x66 prefix.
    """
    prefix = 0x66
    opcode = 0x60
    return bytes([prefix, opcode])

def pushad_in_16bit() -> bytes:
    """
    Force PUSHAD inside 16-bit mode using 0x66 prefix.
    """
    prefix = 0x66
    opcode = 0x60
    return bytes([prefix, opcode])

def push_es() -> bytes:
    """Encode PUSH ES (segment register)."""
    opcode = 0x06
    return bytes([opcode])

def pop_es() -> bytes:
    """Encode POP ES (segment register)"""
    opcode = 0x07
    return bytes([opcode])

def push_cs() -> bytes:
    """Encode PUSH CS (segment register)"""
    opcode = 0x0E
    return bytes([opcode])

def push_ss() -> bytes:
    """Encode PUSH SS (segment register)"""
    opcode = 0x16
    return bytes([opcode])

def pop_ss() -> bytes:
    """Encode POP SS (segment register)"""
    opcode = 0x17
    return bytes([opcode])

def push_ds() -> bytes:
    """Encode PUSH DS (segment register)"""
    opcode = 0x1E
    return bytes([opcode])

def pop_ds() -> bytes:
    """Encode POP DS (segment register)"""
    opcode = 0x1F
    return bytes([opcode])
