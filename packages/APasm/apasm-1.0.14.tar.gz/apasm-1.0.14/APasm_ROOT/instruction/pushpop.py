import importlib.util as im
import os

def load_module(alias: str, path: str):
    """Load a module dynamically from a file path"""
    spec = im.spec_from_file_location(alias, path)
    module = im.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Define modules (alias → relative path)
modules_to_load = {
    "rmmodule": os.path.join("APasm_ROOT", "definitions", "RM.py"),
    "modmodule": os.path.join("APasm_ROOT", "definitions", "mod.py"),
    "movmodule": os.path.join("APasm_ROOT", "instruction", "mov.py"),
    "segmodule": os.path.join("APasm_ROOT", "instruction", "preflix.py"),
}

# Load them
loaded = {alias: load_module(alias, path) for alias, path in modules_to_load.items()}

# Assign to your variables
rmmodule  = loaded["rmmodule"]
modmodule = loaded["modmodule"]
movmodule = loaded["movmodule"]
segmodule = loaded["segmodule"]

def pusha() -> bytes:
    """
    Encode PUSHA (push all 16-bit registers).
    """
    opcode = 0x60
    return bytes([opcode])

def pushad() -> bytes:
    """
    Encode PUSHAD (push all 32-bit registers).
    """
    opcode = 0x60
    return bytes([opcode])

def pusha_in_32bit() -> bytes:
    """
    Force PUSHA inside 32-bit mode using 0x66 prefix.
    """
    prefix = 0x66
    opcode = 0x60
    return bytes([prefix, opcode])

def pushad_in_16bit() -> bytes:
    """
    Force PUSHAD inside 16-bit mode using 0x66 prefix.
    """
    prefix = 0x66
    opcode = 0x60
    return bytes([prefix, opcode])

def push_es() -> bytes:
    """Encode PUSH ES (segment register)."""
    opcode = 0x06
    return bytes([opcode])

def pop_es() -> bytes:
    """Encode POP ES (segment register)"""
    opcode = 0x07
    return bytes([opcode])

def push_cs() -> bytes:
    """Encode PUSH CS (segment register)"""
    opcode = 0x0E
    return bytes([opcode])

def push_ss() -> bytes:
    """Encode PUSH SS (segment register)"""
    opcode = 0x16
    return bytes([opcode])

def pop_ss() -> bytes:
    """Encode POP SS (segment register)"""
    opcode = 0x17
    return bytes([opcode])

def push_ds() -> bytes:
    """Encode PUSH DS (segment register)"""
    opcode = 0x1E
    return bytes([opcode])

def pop_ds() -> bytes:
    """Encode POP DS (segment register)"""
    opcode = 0x1F
    return bytes([opcode])
