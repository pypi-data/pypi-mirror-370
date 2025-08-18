import random as rand
import importlib.util as im
import importlib.resources as resources
import os


class APasmEnv:
    def __init__(self, *code):
        self.id = rand.randint(10000, 99999)
        self.code = b"".join(
            c if isinstance(c, (bytes, bytearray)) else
            (bytes([c]) if isinstance(c, int) else bytes(c))
            for c in code
        )

    def Push(
        self,
        fileName: str = None,
        outDir: str = None
    ):
        outDir = outDir or os.path.join(os.getcwd(), "APasmEnv_Output")
        os.makedirs(outDir, exist_ok=True)

        fileName = fileName or os.path.join(
            outDir,
            f"Untitled_APasm_Output_No{rand.randint(0, 1000000)}.bin"
        )
        with open(fileName, "wb") as f:
            f.write(self.code)

    def ClearOutPutDir(self, outDir: str = None):
        outDir = outDir or os.path.join(os.getcwd(), "APasmEnv_Output")
        if not os.path.exists(outDir):
            return
        for name in os.listdir(outDir):
            os.remove(os.path.join(outDir, name))
