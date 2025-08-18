import importlib.util as im

# Import RM dynamically
rmpath = "APasm_ROOT/definitions/RM.py"
rmspec = im.spec_from_file_location("rmmodule", rmpath)
rmmodule = im.module_from_spec(rmspec)
rmspec.loader.exec_module(rmmodule)

modpath = "APasm_ROOT/definitions/mod.py"
modspec = im.spec_from_file_location("modmodule", modpath)
modmodule = im.module_from_spec(modspec)
modspec.loader.exec_module(modmodule)

movpath = "APasm_ROOT/instruction/mov.py"
movspec = im.spec_from_file_location("movmodule", movpath)
movmodule = im.module_from_spec(movspec)
movspec.loader.exec_module(movmodule)

def add_m8r8(dest: str, src: str, disp: int = 0) -> bytes:
    """ADD r/m8, r8 with optional displacement for memory."""
    opcode = 0x00

    if dest in movmodule.reg8:
        mod_val = modmodule.mod["reg"]
        rm = movmodule.reg8[dest]
        disp_bytes = b""
    elif dest in rmmodule.RM:
        if disp == 0 and dest != "[bp]":
            mod_val = modmodule.mod["normal"]
            disp_bytes = b""
        elif -128 <= disp <= 127:
            mod_val = modmodule.mod["disp8"]
            disp_bytes = disp.to_bytes(1, "little", signed=True)
        else:
            mod_val = modmodule.mod["disp16"]
            disp_bytes = disp.to_bytes(2, "little", signed=True)
        rm = rmmodule.RM[dest]
    else:
        raise ValueError(f"Unknown destination: {dest}")

    reg_val = movmodule.reg8[src]
    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm
    return bytes([opcode, modrm_byte]) + disp_bytes


def add_m16_32r16_32(dest: str, src: str, disp: int = 0) -> bytes:
    """ADD r/m16/32, r16/32 with optional displacement for memory."""
    opcode = 0x01

    if dest in movmodule.reg16:
        mod_val = modmodule.mod["reg"]
        rm = movmodule.reg16[dest]
        disp_bytes = b""
    elif dest in rmmodule.RM:
        if disp == 0 and dest != "[bp]":
            mod_val = modmodule.mod["normal"]
            disp_bytes = b""
        elif -128 <= disp <= 127:
            mod_val = modmodule.mod["disp8"]
            disp_bytes = disp.to_bytes(1, "little", signed=True)
        else:
            mod_val = modmodule.mod["disp16"]
            disp_bytes = disp.to_bytes(2, "little", signed=True)
        rm = rmmodule.RM[dest]
    else:
        raise ValueError(f"Unknown destination: {dest}")

    reg_val = movmodule.reg16[src]
    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm
    return bytes([opcode, modrm_byte]) + disp_bytes

def add_r8_m8(dest: str, src: str, disp: int = 0) -> bytes:
    """
    Encode ADD r8, r/m8
    dest: 8-bit register (r8)
    src: memory/register (r/m8)
    disp: optional displacement if src is memory
    Returns: bytes of the instruction
    """
    opcode = 0x02  # Opcode for ADD r8, r/m8

    # Determine MOD and RM for source operand
    if src in movmodule.reg8:
        mod_val = modmodule.mod["reg"]
        rm = movmodule.reg8[src]
        disp_bytes = b""
    elif src in rmmodule.RM:
        if disp == 0 and src != "[bp]":
            mod_val = modmodule.mod["normal"]
            disp_bytes = b""
        elif -128 <= disp <= 127:
            mod_val = modmodule.mod["disp8"]
            disp_bytes = disp.to_bytes(1, "little", signed=True)
        else:
            mod_val = modmodule.mod["disp16"]
            disp_bytes = disp.to_bytes(2, "little", signed=True)
        rm = rmmodule.RM[src]
    else:
        raise ValueError(f"Unknown source: {src}")

    # Destination register (r8)
    reg_val = movmodule.reg8[dest]

    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm
    return bytes([opcode, modrm_byte]) + disp_bytes

def add_r16_32_m16_32(dest: str, src: str, disp: int = 0) -> bytes:
    """Encode ADD r16/32, r/m16/32."""
    opcode = 0x03
    disp_bytes = b""  # initialize

    # Determine MOD and RM for source operand
    if src in movmodule.reg16:
        mod_val = modmodule.mod["reg"]
        rm = movmodule.reg16[src]
    elif src in movmodule.reg32:
        mod_val = modmodule.mod["reg"]
        rm = movmodule.reg32[src]
    elif src in rmmodule.RM:
        if disp == 0 and src != "[bp]":
            mod_val = modmodule.mod["normal"]
        elif -128 <= disp <= 127:
            mod_val = modmodule.mod["disp8"]
            disp_bytes = disp.to_bytes(1, "little", signed=True)
        else:
            mod_val = modmodule.mod["disp16"]
            disp_bytes = disp.to_bytes(2, "little", signed=True)
        rm = rmmodule.RM[src]
    else:
        raise ValueError(f"Unknown source: {src}")

    # Determine register bits for destination
    if dest in movmodule.reg16:
        reg_val = movmodule.reg16[dest]
    elif dest in movmodule.reg32:
        reg_val = movmodule.reg32[dest]
    else:
        raise ValueError(f"Unknown destination: {dest}")

    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm
    return bytes([opcode, modrm_byte]) + disp_bytes


#
# encode add al imm8
#
def add_al_imm8(imm: int) -> bytes:
    """Encode ADD AL, imm8."""
    opcode = 0x04
    return bytes([opcode, imm & 0xFF])

#
# encode add eAX imm16/32
#
def add_eAX_imm16_32(imm: int, bits: int = 1) -> bytes:
    """Encode ADD eAX, imm16/32."""
    opcode = 0x05
    if bits == 1:  # 16-bit
        imm_bytes = imm.to_bytes(2, byteorder="little", signed=False)
    elif bits == 2:  # 32-bit
        imm_bytes = imm.to_bytes(4, byteorder="little", signed=False)
    else:
        raise ValueError("bits must be 1 (16-bit) or 2 (32-bit)")
    return bytes([opcode]) + imm_bytes
