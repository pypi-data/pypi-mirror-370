import subprocess as sub

class QEMU:
    """
    # QEMU - APasm API for testing your Pasm code

    **Note**:
    - If OnPath is false then the function would completely ignore the QEMU type and uses the executable instead
    """
    def run(self, fileInput, OnPath=True, QEMUPath:str=".", QEMUType: str="qemu-system-x86_64", externalCMD: str="-fda ", *Aargs): # Aargs to prevent param conflict from subproccess
        """
        Runs a QEMU virtual machine with the specified disk image.

        Parameters
        ----------
        file_input : str
            Path to the file (disk image, boot sector, etc.) to run inside QEMU.
        on_path : bool, default=True
            Whether QEMU is available in the system PATH. If False, `qemu_type` is ignored.
        qemu_path : str, optional
            Full path to the QEMU executable. Used only if `on_path` is False.
        qemu_type : str, default="qemu-system-x86_64"
            QEMU binary to use when `on_path` is True (e.g., "qemu-system-i386").
        external_cmd : str
            Extra QEMU arguments (e.g., "-fda", "-hda", "-boot c").
        *aargs
            Additional parameters passed directly to the `subprocess` call.

        Nerd Notes
        ----------
        - If `on_path` is False, `qemu_path` is used **no matter what**.
        - The `external_cmd` lets you go full mad scientist with your VM config.
        - `*aargs` exists purely for passing raw subprocess flags without breaking the API.
        """
        if OnPath:
            try:
                print(f"[~]Running QEMU Process: {QEMUType} -APasm API")
                sub.call(QEMUType + externalCMD + fileInput, check=True, *Aargs) 
            except FileNotFoundError as fit:
                print(f"[!]File Not Found: {fit} -APasm API")
            except Exception as e:
                print(f"[!]An Error Happened: {e}")
        else:
            try:
                print(f"[~]Running QEMU Executable: {QEMUPath} -APasm API")
                sub.call(QEMUPath + externalCMD + fileInput, check=True, *Aargs,) 
            except FileNotFoundError as fit:
                print(f"[!]File Not Found: {fit} -APasm API")
            except Exception as e:
                print(f"[!]An Error Happened: {e}")