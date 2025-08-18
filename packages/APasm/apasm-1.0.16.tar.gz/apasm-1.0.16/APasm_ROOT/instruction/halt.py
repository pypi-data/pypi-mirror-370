def hlt():
    """Halt CPU until next interrupt"""
    return bytes([0xF4])
