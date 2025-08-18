# APasm

## What is APasm?
- APasm is a library for coding and supporting Assembly in Python and you can directly interact with pure binary. APasm stands for "Avalon Python Assembly", notice something weird in the word "Avalon"? Its the library main name. APasm lastest version is 1.0. APasm supports basic Assembly instructions such as:
- Instruction | Notes                        
1. ADD         | Basic addition                
2. ADC         | Add with carry                
3. CLI         | Clear interrupt flag          
4. HLT         | Halt CPU                      
5. JMP         | Jump                          
6. MOV         | Move data                     
7. OR          | Bitwise OR                   
8. PUSH        | Segment registers only        
9. POP         | Segment registers only        

## Requirements
- [![Python3](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
- [![QEMU](https://img.shields.io/badge/QEMU-Emulator-blue)](https://www.qemu.org/) (or another emulator)
- [![Hex Editor](https://img.shields.io/badge/Hex-Editor-blue)](https://mh-nexus.de/en/hxd/) (optional)

## Example Usage
```python
from APasm import * # or the main loader file name

setah      = MOV_imm("ah", 0x0E)  # call BIOS print
setal      = MOV_imm("al", 0x64)  # print "d"
call       = BIOSCALL_10h()

total      = setah + setal + call
bootloader = total + cli() + hlt() + jmp(-2) + BootPad()

with open("Bootloader.bin", "wb") as f:
    f.write(bootloader)
```
## APasm APIs
- APasmEnv   - Create an APasm Development Environment(class)
- QEMU       - Use Subproccess to test your bootloader in QEMU(class)

## APasmEnv Usage
```python
from APasm import * # or the main loader file name
env = APasmEnv(  # your code will be packaged automatically
  MOV_imm("ah", 0x0E),
  MOV_imm("al", 0x64),  # print d
  BIOSCALL_10h()  
)
env.Push()
# the Push function create a dir named APasmEnv Output and your file will be created right here
# you can edit the dir param to your dir you want
# NOTE: if you don't rename your file to something then the default file name will be Untitled APasm Output File No{rand.randint(0,1000000)} which is generic

# the ClearOutPutDir function will clear APasm output directory or D:/APasmEnv Output/<files>
# CAUTION: ALL FILE INSIDE D:/APasmEnv Output WILL BE UTTERLY DELETED!
```

## QEMU Usage
```python
from AnPasm import *
emulator = QEMU()
emulator.run("D:/myBootloader.bin")    # onPath: True. Default Type: qemu-system-x86_64. Default External CMD: -fda. `*aargs` exists purely for passing raw subprocess flags without breaking the API.
emulator.run("D:/myBootloader.bin", onPath=False, QEMUPath="C:/Users/MyUserName/QEMU/<your QEMU type choice>.exe")
```

## License
- [![License](https://img.shields.io/badge/MIT-License-green)](https://github.com/RandomX42069/APasm/blob/main/LICENSE)
  