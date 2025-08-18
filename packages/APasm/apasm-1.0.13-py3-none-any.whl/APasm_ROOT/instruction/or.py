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

segpath = "APasm_ROOT/instruction/preflix.py"
segspec = im.spec_from_file_location("segmodule", segpath)
segmodule = im.module_from_spec(segspec)
segspec.loader.exec_module(segmodule)

def or_rm8_r8(dest: str, src: str, disp: int = 1) -> bytes:
    """Encode OR r/m8 r8"""
    opcode = 0x08
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

#
# encode or rm16/32 r16/32
#
def or_rm16_32_r16_32(dest: str, src: str, disp: int = 0) -> bytes:
    """Encode OR r/m16/32, r16/32."""
    opcode = 0x09
    disp_bytes = b""

    # Determine MOD and RM for destination
    if dest in movmodule.reg16:
        mod_val = modmodule.mod["reg"]
        rm = movmodule.reg16[dest]
    elif dest in movmodule.reg32:
        mod_val = modmodule.mod["reg"]
        rm = movmodule.reg32[dest]
    elif dest in rmmodule.RM:
        if disp == 0 and dest != "[bp]":
            mod_val = modmodule.mod["normal"]
        elif -128 <= disp <= 127:
            mod_val = modmodule.mod["disp8"]
            disp_bytes = disp.to_bytes(1, "little", signed=True)
        else:
            mod_val = modmodule.mod["disp16"]
            disp_bytes = disp.to_bytes(2, "little", signed=True)
        rm = rmmodule.RM[dest]
    else:
        raise ValueError(f"Unknown destination: {dest}")

    # Determine REG bits for source
    if src in movmodule.reg16:
        reg_val = movmodule.reg16[src]
    elif src in movmodule.reg32:
        reg_val = movmodule.reg32[src]
    else:
        raise ValueError(f"Unknown source: {src}")

    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm
    return bytes([opcode, modrm_byte]) + disp_bytes

def or_rm8_r8m8(dest: str, src: str, disp: int = 1) -> bytes:
    """Encode OR r/m8 r/m8"""
    opcode = 0x0A
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

def or_rm16_32_rm16_32(dest: str, src: str, disp: int = 0) -> bytes:
    """Encode OR r/m16/32, r/m16/32."""
    opcode = 0x0B
    disp_bytes = b""

    # Determine MOD and RM for destination
    if dest in movmodule.reg16:
        mod_val = modmodule.mod["reg"]
        rm = movmodule.reg16[dest]
    elif dest in movmodule.reg32:
        mod_val = modmodule.mod["reg"]
        rm = movmodule.reg32[dest]
    elif dest in rmmodule.RM:
        if disp == 0 and dest != "[bp]":
            mod_val = modmodule.mod["normal"]
        elif -128 <= disp <= 127:
            mod_val = modmodule.mod["disp8"]
            disp_bytes = disp.to_bytes(1, "little", signed=True)
        else:
            mod_val = modmodule.mod["disp16"]
            disp_bytes = disp.to_bytes(2, "little", signed=True)
        rm = rmmodule.RM[dest]
    else:
        raise ValueError(f"Unknown destination: {dest}")

    # Determine REG bits for source
    if src in movmodule.reg16:
        reg_val = movmodule.reg16[src]
    elif src in movmodule.reg32:
        reg_val = movmodule.reg32[src]
    else:
        raise ValueError(f"Unknown source: {src}")

    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm
    return bytes([opcode, modrm_byte]) + disp_bytes

def or_AL_imm8(imm: int) -> bytes:
    """Encode OR AL, imm8"""
    opcode = 0x0C
    return bytes([opcode, imm & 0xFF])

def or_eAX_imm16_32(imm: int, bits: int = 16) -> bytes:
    """Encode OR eAX, imm16/32"""
    opcode = 0x0D
    if bits == 16:
        if not 0 <= imm <= 0xFFFF:
            raise ValueError("Immediate too large for 16-bit")
        byteval = imm.to_bytes(2, "little")
    elif bits == 32:
        if not 0 <= imm <= 0xFFFFFFFF:
            raise ValueError("Immediate too large for 32-bit")
        byteval = imm.to_bytes(4, "little")
    else:
        raise ValueError("bits must be 16 or 32")
    return bytes([opcode]) + byteval
