import importlib.util as im
import os

def load_module(alias: str, path: str):
    """Load a module dynamically from a file path"""
    spec = im.spec_from_file_location(alias, path)
    module = im.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Map aliases to their file paths
modules_to_load = {
    "rmmodule":   os.path.join("APasm_ROOT", "definitions", "RM.py"),
    "modmodule":  os.path.join("APasm_ROOT", "definitions", "mod.py"),
    "modrmmodule":os.path.join("APasm_ROOT", "definitions", "modrm.py"),
    "movmodule":  os.path.join("APasm_ROOT", "instruction", "mov.py"),
}

# Dynamically load all modules
loaded = {alias: load_module(alias, path) for alias, path in modules_to_load.items()}

# Assign to your variable names
rmmodule    = loaded["rmmodule"]
modmodule   = loaded["modmodule"]
modrmmodule = loaded["modrmmodule"]
movmodule   = loaded["movmodule"]

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