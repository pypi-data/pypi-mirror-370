from uhf.reader.protocol import *
from uhf.reader.utils import *


class ParamGbReadUserData(Parameter):

    def __init__(self, childArea: int, start: int, dataLen: int):
        self.childArea = childArea
        self.start = start
        self.dataLen = dataLen

    def bytesToClass(self, dataBytes):
        hex = bytesToHex(dataBytes)
        buffer = DynamicBuffer("0x" + hex)
        self.childArea = buffer.readInt()
        self.start = buffer.readShort()
        self.dataLen = buffer.readInt()
        return self

    def toBytes(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.childArea)
        buffer.putShort(self.start)
        buffer.putInt(self.dataLen)
        return buffer.tobytes()

    def __str__(self) -> str:
        return str((self.childArea, self.start, self.dataLen))
