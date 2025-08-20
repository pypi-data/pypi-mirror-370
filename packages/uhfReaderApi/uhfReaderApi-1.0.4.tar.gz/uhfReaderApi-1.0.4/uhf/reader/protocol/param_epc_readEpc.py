from uhf.reader.protocol import *
from uhf.reader.utils import *


class ParamEpcReadEpc(Parameter):

    def __init__(self, start: int, dataLen: int):
        self.start = start
        self.dataLen = dataLen

    def bytesToClass(self, dataBytes):
        hex = bytesToHex(dataBytes)
        buffer = DynamicBuffer("0x" + hex)
        self.start = buffer.readShort()
        self.dataLen = buffer.readInt()
        return self

    def toBytes(self):
        buffer = DynamicBuffer()
        buffer.putShort(self.start)
        buffer.putInt(self.dataLen)
        return buffer.tobytes()

    def __str__(self) -> str:
        return str((self.start, self.dataLen))
