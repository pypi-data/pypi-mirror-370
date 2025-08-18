def BIOSCALL(int_num: int) -> bytes:
    """
    Encode a BIOS interrupt call (INT n).

    int_num : int - interrupt number (e.g., 0x10 for video, 0x13 for disk)
    Returns bytes of the instruction.
    """
    if not (0 <= int_num <= 0xFF):
        raise ValueError("Interrupt number must be 0-255")
    
    opcode = 0xCD  # INT instruction opcode
    return bytes([opcode, int_num])

def BIOSCALL_10h() -> bytes:
    """
    INT 10h - Video Services
    ------------------------
    AH=00h: Set video mode
    AH=01h: Set cursor shape
    AH=02h: Set cursor position
    AH=03h: Get cursor position
    AH=06h: Scroll window up
    AH=07h: Scroll window down
    AH=08h: Read character/attribute at cursor
    AH=09h: Write character/attribute at cursor
    AH=0Eh: Teletype output (print character)
    AH=13h: Write string to screen
    Return: BIOSCALL 10h
    Note: The AH services board will NOT be returned
    """
    return bytes([0xCD, 0x10])

def BIOSCALL_13h() -> bytes:
    """
    INT 13h – Disk Services
    -----------------------
    AH=00h: Reset disk system
    AH=02h: Read sectors from disk
    AH=03h: Write sectors to disk
    AH=08h: Get drive parameters
    Return: BIOSCALL 13h
    Note: The AH services board will NOT be returned
    """
    return bytes([0xCD, 0x13])

def BIOSCALL_14h() -> bytes:
    """
    INT 14h – Serial Port Services
    ------------------------------
    AH=00h: Initialize serial port
    AH=01h: Send character
    AH=02h: Receive character
    AH=03h: Get port status
    Return: BIOSCALL 14h
    Note: The AH services board will NOT be returned
    """
    return bytes([0xCD, 0x14])

def BIOSCALL_15h() -> bytes:
    """
    INT 15h – Miscellaneous Services
    --------------------------------
    AH=86h: Wait (microseconds via BIOS)
    AH=E820h: Get memory map (used in modern bootloaders)
    Return: BIOSCALL 15h
    Note: The AH services board will NOT be returned
    """
    return bytes([0xCD, 0x15])

def BIOSCALL_16h() -> bytes:
    """
    INT 16h – Keyboard Services
    ---------------------------
    AH=00h: Read key (wait for key press)
    AH=01h: Check for key press
    AH=02h: Get shift flags
    Return: BIOSCALL 16h
    Note: The AH services board will NOT be returned
    """
    return bytes([0xCD, 0x16])

def BIOSCALL_17h() -> bytes:
    """
    INT 17h – Printer Services
    --------------------------
    AH=00h: Initialize printer
    AH=01h: Send character to printer
    AH=02h: Check printer status
    Return: BIOSCALL 17h
    Note: The AH services board will NOT be returned
    """
    return bytes([0xCD, 0x17])

def BIOSCALL_18h() -> bytes:
    """
    INT 18h – BASIC (ROM boot)
    --------------------------
    Starts BASIC ROM if no bootable device is found.
    Return: BIOSCALL 18h
    Note: The AH services board will NOT be returned
    """
    return bytes([0xCD, 0x18])

def BIOSCALL_19h() -> bytes:
    """
    INT 19h – Bootstrap Loader
    --------------------------
    Reloads boot sector (used to reboot from BIOS)
    Return: BIOSCALL 19h
    Note: The AH services board will NOT be returned
    """
    return bytes([0xCD, 0x19])

def BIOSCALL_1Ah() -> bytes:
    """
    INT 1Ah – Time/RTC Services
    ---------------------------
    AH=00h: Get system time (ticks since midnight)
    AH=02h: Get real-time clock time
    AH=04h: Get real-time clock date
    Return: BIOSCALL 1Ah
    Note: The AH services board will NOT be returned
    """
    return bytes([0xCD, 0x1A])

def BIOSCALL_12h() -> bytes:
    """
    INT 12h – Get Base Memory Size
    ------------------------------
    Returns size of base memory (below 1MB) in KB via AX.
    Return: BIOSCALL 12h
    Note: The AH services board will NOT be returned
    """
    return bytes([0xCD, 0x12])
