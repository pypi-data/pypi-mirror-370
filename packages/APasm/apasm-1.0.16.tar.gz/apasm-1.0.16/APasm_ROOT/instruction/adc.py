import importlib.util as im
import os

def load_module(name: str, path: str):
    """Dynamically load a module from a given file path"""
    spec = im.spec_from_file_location(name, path)
    module = im.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# ----------------- un importable ----------

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

mod = {
    "normal": 0b00,   # no displacement (except BP form)
    "disp8":  0b01,   # 8-bit displacement follows
    "disp16": 0b10,   # 16-bit displacement follows
    "reg":    0b11    # register-direct
}

def modrm(mod: int, reg: int, rm: int) -> bytes:
    return bytes([(mod << 6) | (reg << 3) | rm])

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

# -------------------------------

def adc_rm8_r8(dest: str, src: str, disp: int = 0, rm: str = "[bx+si]") -> bytes:
    """ADC r/m8, r8"""
    opcode = 0x10

    if src in reg8:
        reg_val = reg8[src]
    else:
        raise ValueError(f"Unknown 8-bit register: {src}")

    if rm in RM:
        rm_val = RM[rm]
    else:
        raise ValueError(f"Unknown memory operand: {rm}")

    if disp == 0 and rm_val != RM["[bp]"]:
        mod_val = mod["normal"]
        disp_bytes = b""
    elif -128 <= disp <= 127:
        mod_val = mod["disp8"]
        disp_bytes = disp.to_bytes(1, "little", signed=True)
    else:
        mod_val = mod["disp16"]
        disp_bytes = disp.to_bytes(2, "little", signed=True)

    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm_val
    return bytes([opcode, modrm_byte]) + disp_bytes


def adc_rm16_r16(dest: str, src: str, disp: int = 0, rm: str = "[bx+si]") -> bytes:
    """ADC r/m16, r16"""
    opcode = 0x11  # ADC r/m16, r16
    if src in reg16:
        reg_val = reg16[src]
    else:
        raise ValueError(f"Unknown 16-bit register: {src}")

    if rm in RM:
        rm_val = RM[rm]
    else:
        raise ValueError(f"Unknown memory operand: {rm}")

    if disp == 0 and rm_val != RM["[bp]"]:
        mod_val = mod["normal"]
        disp_bytes = b""
    elif -128 <= disp <= 127:
        mod_val = mod["disp8"]
        disp_bytes = disp.to_bytes(1, "little", signed=True)
    else:
        mod_val = mod["disp16"]
        disp_bytes = disp.to_bytes(2, "little", signed=True)

    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm_val
    return bytes([opcode, modrm_byte]) + disp_bytes


def adc_rm32_r32(dest: str, src: str, disp: int = 0, rm: str = "[bx+si]") -> bytes:
    """ADC r/m32, r32"""
    opcode = 0x11  # same as 16-bit, but 32-bit mode (assume operand-size override not used)
    if src in reg32:
        reg_val = reg32[src]
    else:
        raise ValueError(f"Unknown 32-bit register: {src}")

    if rm in RM:
        rm_val = RM[rm]
    else:
        raise ValueError(f"Unknown memory operand: {rm}")

    if disp == 0 and rm_val != RM["[ebp]"]:
        mod_val = mod["normal"]
        disp_bytes = b""
    elif -128 <= disp <= 127:
        mod_val = mod["disp8"]
        disp_bytes = disp.to_bytes(1, "little", signed=True)
    else:
        mod_val = mod["disp16"]
        disp_bytes = disp.to_bytes(2, "little", signed=True)

    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm_val
    return bytes([opcode, modrm_byte]) + disp_bytes


def adc_rm64_r64(dest: str, src: str, disp: int = 0, rm: str = "[bx+si]") -> bytes:
    """ADC r/m64, r64"""
    opcode = 0x11  # same opcode in 64-bit mode; requires REX prefix
    rex = 0x48  # default: REX.W=1, no extension (adjust if using r8-r15)

    if src in reg64:
        reg_val = reg64[src]
    else:
        raise ValueError(f"Unknown 64-bit register: {src}")

    if rm in RM:
        rm_val = RM[rm]
    else:
        raise ValueError(f"Unknown memory operand: {rm}")

    if disp == 0 and rm_val != RM["[rbp]"]:
        mod_val = mod["normal"]
        disp_bytes = b""
    elif -128 <= disp <= 127:
        mod_val = mod["disp8"]
        disp_bytes = disp.to_bytes(1, "little", signed=True)
    else:
        mod_val = mod["disp16"]
        disp_bytes = disp.to_bytes(2, "little", signed=True)

    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm_val
    return bytes([rex, opcode, modrm_byte]) + disp_bytes

