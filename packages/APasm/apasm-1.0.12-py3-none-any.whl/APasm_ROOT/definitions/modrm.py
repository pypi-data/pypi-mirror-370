def modrm(mod: int, reg: int, rm: int) -> bytes:
    return bytes([(mod << 6) | (reg << 3) | rm])
