from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgBaseGetFrequency(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Base.value
        self.msgId = EnumG.BaseMid_GetFrequency.value
        self.automatically = None
        self.listFreqCursor = []

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.automatically = buffer.readInt()
            freLen = buffer.readShort()
            self.listFreqCursor = [buffer.readInt() for i in range(freLen)]
            self.rtCode = 0

    def __str__(self) -> str:
        return str((self.automatically, self.listFreqCursor))
