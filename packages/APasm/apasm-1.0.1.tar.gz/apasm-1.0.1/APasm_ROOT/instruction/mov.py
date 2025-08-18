import importlib.util as im

intpath = "APasm_ROOT/definitions/int.py"
intspec = im.spec_from_file_location("APasm_ROOT.definitions.int", intpath)
intmod = im.module_from_spec(intspec)
intspec.loader.exec_module(intmod)

prepath = "APasm_ROOT/instruction/preflix.py"
prespec = im.spec_from_file_location("APasm_ROOT.instruction.preflix", prepath)
premod = im.module_from_spec(prespec)
prespec.loader.exec_module(premod)

# Import RM dynamically
rmpath = "APasm_ROOT/definitions/RM.py"
rmspec = im.spec_from_file_location("rmmodule", rmpath)
rmmodule = im.module_from_spec(rmspec)
rmspec.loader.exec_module(rmmodule)

modpath = "APasm_ROOT/definitions/mod.py"
modspec = im.spec_from_file_location("modmodule", modpath)
modmodule = im.module_from_spec(modspec)
modspec.loader.exec_module(modmodule)

segpath = "APasm_ROOT/instruction/preflix.py"
segspec = im.spec_from_file_location("segmodule", segpath)
segmodule = im.module_from_spec(segspec)
segspec.loader.exec_module(segmodule)

# MOV register/memory opcodes (base integers)
mov_rm8_r8       = 0x88  # r8 → r/m8
mov_r8_rm8       = 0x8A  # r/m8 → r8

mov_rm16_r16     = 0x89  # r16 → r/m16
mov_r16_rm16     = 0x8B  # r/m16 → r16

mov_rm32_r32     = 0x89  # r32 → r/m32
mov_r32_rm32     = 0x8B  # r/m32 → r32

mov_rm64_r64     = 0x89  # r64 → r/m64
mov_r64_rm64     = 0x8B  # r/m64 → r64

# MOV with immediate to r/m
mov_rm8_imm8     = 0xC6  # imm8 → r/m8
mov_rm16_imm16   = 0xC7  # imm16 → r/m16
mov_rm32_imm32   = 0xC7  # imm32 → r/m32
mov_rm64_imm32   = 0xC7  # sign-extended imm32 → r/m64

# MOV with immediate to register (special short forms)
mov_r8_imm8_base   = 0xB0  # + reg code (AL, CL, ...)
mov_r16_imm16_base = 0xB8  # + reg code (AX, CX, ...)
mov_r32_imm32_base = 0xB8  # + reg code (EAX, ECX, ...)
mov_r64_imm64_base = 0xB8  # + reg code (RAX, RCX, ...)

# MOV segment register function
def MOV_SR(sr_name: str, gp_reg: str) -> bytes:
    """
    Encode MOV SR, r16 instruction (e.g., MOV CS, AX).
    
    sr_name : str - segment register ("cs", "ds", "es", "fs", "gs", "ss")
    gp_reg  : str - general-purpose 16-bit register ("ax", "bx", "cx", etc.)
    
    Returns bytes of the instruction.
    """
    opcode = 0x8E  # MOV SR, r/m16

    # MOD = 11 (register-direct)
    mod_val = 0b11

    # REG field = segment register
    if sr_name.lower() in segmodule.seg_reg_val:
        reg_val = segmodule.seg_reg_val[sr_name.lower()]
    else:
        raise ValueError(f"Unknown segment register: {sr_name}")

    # RM field = general-purpose 16-bit register
    if gp_reg.lower() in reg16:
        rm_val = reg16[gp_reg.lower()]
    else:
        raise ValueError(f"Unknown 16-bit general-purpose register: {gp_reg}")

    # Compose MOD-REG-RM byte
    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm_val

    return bytes([opcode, modrm_byte])


def MOV_imm(reg_name, value: str | int, disp: int = 0):
    """Encode MOV reg/mem, imm or MOV reg/mem, reg."""
    
    # Helper: check if value is a general-purpose register
    is_gp_reg = isinstance(value, str) and value.lower() in reg16

    # 8-bit registers
    if reg_name in reg8:
        if is_gp_reg:
            raise ValueError("Cannot MOV 8-bit register from 16-bit register")
        return bytes([mov_r8_imm8_base + reg8[reg_name]]) + intmod.UINT8(value)
    
    # 16-bit registers
    elif reg_name in reg16:
        if is_gp_reg:
            # MOV r16, r16 using opcode + ModR/M
            dest = reg16[reg_name]
            src = reg16[value.lower()]
            opcode = 0x89  # MOV r/m16, r16
            modrm = (0b11 << 6) | (src << 3) | dest
            return bytes([opcode, modrm])
        else:
            return bytes([mov_r16_imm16_base + reg16[reg_name]]) + intmod.UINT16(value)
    
    # Segment registers
    elif reg_name in premod.seg:
        opcode = 0x8E  # MOV SR, r/m16
        reg_val = premod.seg[reg_name]
        if is_gp_reg:
            rm_val = reg16[value.lower()]
        else:
            rm_val = rmmodule.RM["[bx+si]"]  # default memory
        mod_val = modmodule.mod["normal"]
        disp_bytes = b""
        if disp != 0:
            if -128 <= disp <= 127:
                mod_val = modmodule.mod["disp8"]
                disp_bytes = disp.to_bytes(1, "little", signed=True)
            else:
                mod_val = modmodule.mod["disp16"]
                disp_bytes = disp.to_bytes(2, "little", signed=True)
        modrm_byte = (mod_val << 6) | (reg_val << 3) | rm_val
        if is_gp_reg:
            return bytes([opcode, modrm_byte])
        else:
            return bytes([opcode, modrm_byte]) + disp_bytes + intmod.UINT16(value)
    
    # Memory operand
    elif reg_name in rmmodule.RM:
        opcode = 0xC6 if isinstance(value, int) and value <= 0xFF else 0xC7
        rm_val = rmmodule.RM[reg_name]
        mod_val = modmodule.mod["normal"]
        disp_bytes = b""
        if disp != 0:
            if -128 <= disp <= 127:
                mod_val = modmodule.mod["disp8"]
                disp_bytes = disp.to_bytes(1, "little", signed=True)
            else:
                mod_val = modmodule.mod["disp16"]
                disp_bytes = disp.to_bytes(2, "little", signed=True)
        reg_field = 0
        modrm_byte = (mod_val << 6) | (reg_field << 3) | rm_val
        if opcode == 0xC6:
            return bytes([opcode, modrm_byte]) + intmod.UINT8(value) + disp_bytes
        else:
            return bytes([opcode, modrm_byte]) + intmod.UINT16(value) + disp_bytes
    
    else:
        raise ValueError(f"Unknown register or memory operand: {reg_name}")
    
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