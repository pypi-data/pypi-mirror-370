import importlib.util as im
import os


# 8-bit registers (legacy)
reg8 = {
    "al": 0b000,
    "cl": 0b001,
    "dl": 0b010,
    "bl": 0b011,
    "ah": 0b100,
    "ch": 0b101,
    "dh": 0b110,
    "bh": 0b111,
}

# 8-bit registers (low-byte in 64-bit mode, includes r8–r15b)
reg8_64 = {
    "al": 0b000,
    "cl": 0b001,
    "dl": 0b010,
    "bl": 0b011,
    "spl": 0b100,  # needs REX prefix
    "bpl": 0b101,  # needs REX prefix
    "sil": 0b110,  # needs REX prefix
    "dil": 0b111,  # needs REX prefix
    "r8b": 0b000,  # needs REX.B or REX.R
    "r9b": 0b001,
    "r10b": 0b010,
    "r11b": 0b011,
    "r12b": 0b100,
    "r13b": 0b101,
    "r14b": 0b110,
    "r15b": 0b111,
}

# 16-bit registers
reg16 = {
    "ax": 0b000,
    "cx": 0b001,
    "dx": 0b010,
    "bx": 0b011,
    "sp": 0b100,
    "bp": 0b101,
    "si": 0b110,
    "di": 0b111,
    "r8w": 0b000,
    "r9w": 0b001,
    "r10w": 0b010,
    "r11w": 0b011,
    "r12w": 0b100,
    "r13w": 0b101,
    "r14w": 0b110,
    "r15w": 0b111,
}

# 32-bit registers
reg32 = {
    "eax": 0b000,
    "ecx": 0b001,
    "edx": 0b010,
    "ebx": 0b011,
    "esp": 0b100,
    "ebp": 0b101,
    "esi": 0b110,
    "edi": 0b111,
    "r8d": 0b000,
    "r9d": 0b001,
    "r10d": 0b010,
    "r11d": 0b011,
    "r12d": 0b100,
    "r13d": 0b101,
    "r14d": 0b110,
    "r15d": 0b111,
}

# 64-bit registers
reg64 = {
    "rax": 0b000,
    "rcx": 0b001,
    "rdx": 0b010,
    "rbx": 0b011,
    "rsp": 0b100,
    "rbp": 0b101,
    "rsi": 0b110,
    "rdi": 0b111,
    "r8": 0b000,
    "r9": 0b001,
    "r10": 0b010,
    "r11": 0b011,
    "r12": 0b100,
    "r13": 0b101,
    "r14": 0b110,
    "r15": 0b111,
}

mod = {
    "normal": 0b00,   # no displacement (except BP form)
    "disp8":  0b01,   # 8-bit displacement follows
    "disp16": 0b10,   # 16-bit displacement follows
    "reg":    0b11    # register-direct
}

RM = {
    "[bx+si]": 0b000,
    "[bx+di]": 0b001,
    "[bp+si]": 0b010,
    "[bp+di]": 0b011,
    "[si]":    0b100,
    "[di]":    0b101,
    "[bp]":    0b110,  # Special: if mod=00, requires disp16
    "[bx]":    0b111
}

def add_m8r8(dest: str, src: str, disp: int = 0) -> bytes:
    """ADD r/m8, r8 with optional displacement for memory."""
    opcode = 0x00

    if dest in reg8:
        mod_val = mod["reg"]
        rm = reg8[dest]
        disp_bytes = b""
    elif dest in RM:
        if disp == 0 and dest != "[bp]":
            mod_val = mod["normal"]
            disp_bytes = b""
        elif -128 <= disp <= 127:
            mod_val = mod["disp8"]
            disp_bytes = disp.to_bytes(1, "little", signed=True)
        else:
            mod_val = mod["disp16"]
            disp_bytes = disp.to_bytes(2, "little", signed=True)
        rm = RM[dest]
    else:
        raise ValueError(f"Unknown destination: {dest}")

    reg_val = reg8[src]
    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm
    return bytes([opcode, modrm_byte]) + disp_bytes


def add_m16_32r16_32(dest: str, src: str, disp: int = 0) -> bytes:
    """ADD r/m16/32, r16/32 with optional displacement for memory."""
    opcode = 0x01

    if dest in reg16:
        mod_val = mod["reg"]
        rm = reg16[dest]
        disp_bytes = b""
    elif dest in RM:
        if disp == 0 and dest != "[bp]":
            mod_val = mod["normal"]
            disp_bytes = b""
        elif -128 <= disp <= 127:
            mod_val = mod["disp8"]
            disp_bytes = disp.to_bytes(1, "little", signed=True)
        else:
            mod_val = mod["disp16"]
            disp_bytes = disp.to_bytes(2, "little", signed=True)
        rm = RM[dest]
    else:
        raise ValueError(f"Unknown destination: {dest}")

    reg_val = reg16[src]
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
    if src in reg8:
        mod_val = mod["reg"]
        rm = reg8[src]
        disp_bytes = b""
    elif src in RM:
        if disp == 0 and src != "[bp]":
            mod_val = mod["normal"]
            disp_bytes = b""
        elif -128 <= disp <= 127:
            mod_val = mod["disp8"]
            disp_bytes = disp.to_bytes(1, "little", signed=True)
        else:
            mod_val = mod["disp16"]
            disp_bytes = disp.to_bytes(2, "little", signed=True)
        rm = RM[src]
    else:
        raise ValueError(f"Unknown source: {src}")

    # Destination register (r8)
    reg_val = reg8[dest]

    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm
    return bytes([opcode, modrm_byte]) + disp_bytes

def add_r16_32_m16_32(dest: str, src: str, disp: int = 0) -> bytes:
    """Encode ADD r16/32, r/m16/32."""
    opcode = 0x03
    disp_bytes = b""  # initialize

    # Determine MOD and RM for source operand
    if src in reg16:
        mod_val = mod["reg"]
        rm = reg16[src]
    elif src in reg32:
        mod_val = mod["reg"]
        rm = reg32[src]
    elif src in RM:
        if disp == 0 and src != "[bp]":
            mod_val = mod["normal"]
        elif -128 <= disp <= 127:
            mod_val = mod["disp8"]
            disp_bytes = disp.to_bytes(1, "little", signed=True)
        else:
            mod_val = mod["disp16"]
            disp_bytes = disp.to_bytes(2, "little", signed=True)
        rm = RM[src]
    else:
        raise ValueError(f"Unknown source: {src}")

    # Determine register bits for destination
    if dest in reg16:
        reg_val = reg16[dest]
    elif dest in reg32:
        reg_val = reg32[dest]
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
