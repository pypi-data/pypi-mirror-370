from uhf.reader.protocol import *
from uhf.reader.utils import *


class ParamEpcReadTid(Parameter):

    def __init__(self, mode: int, dataLen: int):
        self.area = mode
        self.dataLen = dataLen

    def bytesToClass(self, dataBytes):
        hex = bytesToHex(dataBytes)
        buffer = DynamicBuffer("0x" + hex)
        self.area = buffer.readInt()
        self.dataLen = buffer.readInt()

        return self

    def toBytes(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.area)
        buffer.putInt(self.dataLen)
        return buffer.tobytes()

    def __str__(self) -> str:
        return str((self.area, self.dataLen))
