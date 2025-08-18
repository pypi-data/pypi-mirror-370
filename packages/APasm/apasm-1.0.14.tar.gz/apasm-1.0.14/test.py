from AvalonPasm import *

setah = MOV_imm("ah", 0x0E)
setal = MOV_imm("al", 0x64)
BIOSCALLS = BIOSCALL_10h()

total = setah + setal + BIOSCALLS
bootloader = total + BootPad(total)
print(bootloader)

emulator = QEMU.run()

