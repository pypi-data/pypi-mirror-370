def data_signature() -> bytes:
    """The bootloader signature: 0x55AA for BIOS to recognize as bootable"""
    return bytes([0x55, 0xAA])

def TBytes(value: int, times: int = 1) -> bytes:
    """Repeat a single byte `value` `times` times."""
    return bytes([value] * times)

def BootPad(total)->bytes:
    """Fill With Nulls and data signature at the end"""
    return bytes([0x00] * (510 - len(total))) + data_signature()