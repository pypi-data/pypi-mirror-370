import importlib.util as im
import os

def load_module(name: str, path: str):
    """Dynamically load a module from a given file path"""
    spec = im.spec_from_file_location(name, path)
    module = im.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import RM dynamically
rmpath = os.path.join("APasm_ROOT", "definitions", "RM.py")
rmmodule = load_module("rmmodule", rmpath)

modpath = os.path.join("APasm_ROOT", "definitions", "mod.py")
modmodule = load_module("modmodule", modpath)

modrmpath = os.path.join("APasm_ROOT", "definitions", "modrm.py")
modrmmodule = load_module("modrmmodule", modrmpath)

movpath = os.path.join("APasm_ROOT", "instruction", "mov.py")
movmodule = load_module("movmodule", movpath)

def adc_rm8_r8(dest: str, src: str, disp: int = 0, rm: str = "[bx+si]") -> bytes:
    """ADC r/m8, r8"""
    opcode = 0x10

    if src in movmodule.reg8:
        reg_val = movmodule.reg8[src]
    else:
        raise ValueError(f"Unknown 8-bit register: {src}")

    if rm in rmmodule.RM:
        rm_val = rmmodule.RM[rm]
    else:
        raise ValueError(f"Unknown memory operand: {rm}")

    if disp == 0 and rm_val != rmmodule.RM["[bp]"]:
        mod_val = modmodule.mod["normal"]
        disp_bytes = b""
    elif -128 <= disp <= 127:
        mod_val = modmodule.mod["disp8"]
        disp_bytes = disp.to_bytes(1, "little", signed=True)
    else:
        mod_val = modmodule.mod["disp16"]
        disp_bytes = disp.to_bytes(2, "little", signed=True)

    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm_val
    return bytes([opcode, modrm_byte]) + disp_bytes


def adc_rm16_r16(dest: str, src: str, disp: int = 0, rm: str = "[bx+si]") -> bytes:
    """ADC r/m16, r16"""
    opcode = 0x11  # ADC r/m16, r16
    if src in movmodule.reg16:
        reg_val = movmodule.reg16[src]
    else:
        raise ValueError(f"Unknown 16-bit register: {src}")

    if rm in rmmodule.RM:
        rm_val = rmmodule.RM[rm]
    else:
        raise ValueError(f"Unknown memory operand: {rm}")

    if disp == 0 and rm_val != rmmodule.RM["[bp]"]:
        mod_val = modmodule.mod["normal"]
        disp_bytes = b""
    elif -128 <= disp <= 127:
        mod_val = modmodule.mod["disp8"]
        disp_bytes = disp.to_bytes(1, "little", signed=True)
    else:
        mod_val = modmodule.mod["disp16"]
        disp_bytes = disp.to_bytes(2, "little", signed=True)

    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm_val
    return bytes([opcode, modrm_byte]) + disp_bytes


def adc_rm32_r32(dest: str, src: str, disp: int = 0, rm: str = "[bx+si]") -> bytes:
    """ADC r/m32, r32"""
    opcode = 0x11  # same as 16-bit, but 32-bit mode (assume operand-size override not used)
    if src in movmodule.reg32:
        reg_val = movmodule.reg32[src]
    else:
        raise ValueError(f"Unknown 32-bit register: {src}")

    if rm in rmmodule.RM:
        rm_val = rmmodule.RM[rm]
    else:
        raise ValueError(f"Unknown memory operand: {rm}")

    if disp == 0 and rm_val != rmmodule.RM["[ebp]"]:
        mod_val = modmodule.mod["normal"]
        disp_bytes = b""
    elif -128 <= disp <= 127:
        mod_val = modmodule.mod["disp8"]
        disp_bytes = disp.to_bytes(1, "little", signed=True)
    else:
        mod_val = modmodule.mod["disp16"]
        disp_bytes = disp.to_bytes(2, "little", signed=True)

    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm_val
    return bytes([opcode, modrm_byte]) + disp_bytes


def adc_rm64_r64(dest: str, src: str, disp: int = 0, rm: str = "[bx+si]") -> bytes:
    """ADC r/m64, r64"""
    opcode = 0x11  # same opcode in 64-bit mode; requires REX prefix
    rex = 0x48  # default: REX.W=1, no extension (adjust if using r8-r15)

    if src in movmodule.reg64:
        reg_val = movmodule.reg64[src]
    else:
        raise ValueError(f"Unknown 64-bit register: {src}")

    if rm in rmmodule.RM:
        rm_val = rmmodule.RM[rm]
    else:
        raise ValueError(f"Unknown memory operand: {rm}")

    if disp == 0 and rm_val != rmmodule.RM["[rbp]"]:
        mod_val = modmodule.mod["normal"]
        disp_bytes = b""
    elif -128 <= disp <= 127:
        mod_val = modmodule.mod["disp8"]
        disp_bytes = disp.to_bytes(1, "little", signed=True)
    else:
        mod_val = modmodule.mod["disp16"]
        disp_bytes = disp.to_bytes(2, "little", signed=True)

    modrm_byte = (mod_val << 6) | (reg_val << 3) | rm_val
    return bytes([rex, opcode, modrm_byte]) + disp_bytes

