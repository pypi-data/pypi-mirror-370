

def sbb_al_imm8(imm: int) -> bytes:
    """Encode SBB AL, imm8"""
    return bytes([0x1C]) + imm.to_bytes(1, "little", signed=False)

def sbb_ax_imm16(imm: int) -> bytes:
    """Encode SBB AX, imm16"""
    return bytes([0x1D]) + imm.to_bytes(2, "little", signed=False)

def sbb_eax_imm32(imm: int) -> bytes:
    """Encode SBB EAX, imm32"""
    return bytes([0x1D]) + imm.to_bytes(4, "little", signed=False)

def sbb_rax_imm32(imm: int) -> bytes:
    """Encode SBB RAX, imm32 (sign-extended)"""
    # same encoding as EAX version, but in 64-bit mode
    return bytes([0x1D]) + imm.to_bytes(4, "little", signed=False)