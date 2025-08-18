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

modrmpath = "APasm_ROOT/definitions/modrm.py"
modrmspec = im.spec_from_file_location("modrmmodule", modrmpath)
modrmmodule = im.module_from_spec(modrmspec)
modrmspec.loader.exec_module(modrmmodule)

movpath = "APasm_ROOT/instruction/mov.py"
movspec = im.spec_from_file_location("movmodule", movpath)
movmodule = im.module_from_spec(movspec)
movspec.loader.exec_module(movmodule)

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