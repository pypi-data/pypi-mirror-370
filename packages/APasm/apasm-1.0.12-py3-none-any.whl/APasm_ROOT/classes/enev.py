import random as rand
import importlib.util as im
import os

# Load Compile() from fileOut.py
outPath = os.path.join("APasm_ROOT", "utils", "fileOut.py")  # APasm_ROOT/classes/enev.py
outSpec = im.spec_from_file_location("outMod", outPath)
outMod = im.module_from_spec(outSpec)
outSpec.loader.exec_module(outMod)

class APasmEnv:
    def __init__(self, *code):
        self.id = rand.randint(10000, 99999)
        self.code = b"".join(c if isinstance(c, (bytes, bytearray)) else bytes(c) for c in code)
        
    def Push(self, fileName:str=f"D:/APasmEnv Output/Untitled APasm Output File No{rand.randint(0,1000000)}", dir:str="D:/APasm Output"):
        os.makedirs("D:/APasmEnv Output", exist_ok=True)
        outMod.Compile(fileName, self.code)

    def ClearOutPutDir(self):
        folder = "D:/APasmEnv Output"
        files = os.listdir(folder)
        for name in files:
            path = os.path.join(folder, name)  # Full path
            os.remove(path)
        