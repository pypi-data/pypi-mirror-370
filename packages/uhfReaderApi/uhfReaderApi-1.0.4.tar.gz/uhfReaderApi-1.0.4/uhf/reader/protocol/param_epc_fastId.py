from uhf.reader.protocol import *
from uhf.reader.utils import *


class ParamEpcFastId(Parameter):

    def __init__(self, fastId: int, tagFoucs: int):
        self.fastId = fastId
        self.tagFoucs = tagFoucs

    def bytesToClass(self, dataBytes):
        hex = bytesToHex(dataBytes)
        buffer = DynamicBuffer("0x" + hex)
        self.fastId = buffer.readInt()
        self.tagFoucs = buffer.readInt()
        return self

    def toBytes(self):
        buffer = DynamicBuffer()
        buffer.putInt(self.fastId)
        buffer.putInt(self.tagFoucs)
        return buffer.tobytes()

    def __str__(self) -> str:
        return str((self.fastId, self.tagFoucs))
