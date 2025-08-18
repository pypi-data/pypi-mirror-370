def jmp(offset: int) -> bytes:
    """
    Generate a short JMP instruction (relative, 1 byte offset).

    offset : int - signed number of bytes to jump relative to the next instruction
                   (valid range: -128 to 127)
    
    Returns: bytes - 2-byte JMP instruction
    """
    if not -128 <= offset <= 127:
        raise ValueError("Offset for short JMP must be between -128 and 127")
    return bytes([0xEB, offset & 0xFF])
