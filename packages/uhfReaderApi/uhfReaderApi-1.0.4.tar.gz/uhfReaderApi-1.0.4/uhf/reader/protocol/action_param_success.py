from uhf.reader.protocol import *
from uhf.reader.utils import *


class ActionParamSuccess(Parameter):

    def __init__(self, keepTime: int, **kwargs):
        self.keepTime = keepTime
        self.gpo1 = kwargs.get("gpo1", None)
        self.gpo2 = kwargs.get("gpo2", None)
        self.gpo3 = kwargs.get("gpo3", None)
        self.gpo4 = kwargs.get("gpo4", None)

    def bytesToClass(self, dataBytes):
        hex = bytesToHex(dataBytes)
        buffer = DynamicBuffer("0x" + hex)
        self.keepTime = buffer.readShort()
        while buffer.pos / 8 < len(dataBytes):
            pid = buffer.readInt()
            if pid == 1:
                self.gpo1 = buffer.readInt()
            if pid == 2:
                self.gpo2 = buffer.readInt()
            if pid == 3:
                self.gpo3 = buffer.readInt()
            if pid == 4:
                self.gpo4 = buffer.readInt()
        return self

    def toBytes(self):
        buffer = DynamicBuffer()
        buffer.putShort(self.keepTime)
        if self.gpo1 is not None:
            buffer.putInt(0x01)
            buffer.putInt(self.gpo1)
        if self.gpo2 is not None:
            buffer.putInt(0x02)
            buffer.putInt(self.gpo2)
        if self.gpo3 is not None:
            buffer.putInt(0x03)
            buffer.putInt(self.gpo3)
        if self.gpo4 is not None:
            buffer.putInt(0x04)
            buffer.putInt(self.gpo4)

        return buffer.tobytes()

    def __str__(self) -> str:
        return str((self.keepTime, self.gpo1, self.gpo2, self.gpo3, self.gpo4))
