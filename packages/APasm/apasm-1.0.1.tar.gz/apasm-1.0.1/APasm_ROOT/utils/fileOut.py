import os

def Compile(file: str, content: bytes|str = b"") -> tuple:
    fileDirectory, fileName = os.path.split(file)
    fileName, fileExt = os.path.splitext(fileName)
    with open(os.path.join(fileDirectory, fileName + ".bin"), "wb") as f:
        f.write(content)
    return (fileDirectory, fileName, fileExt)
