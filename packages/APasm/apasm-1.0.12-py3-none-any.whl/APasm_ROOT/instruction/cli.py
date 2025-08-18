def cli():
    """
    Clear Maskable Interrupt
    To make easier to understand,
    disable all interrupt that are allowed to
    be disabled
    """
    return bytes([0xFA])