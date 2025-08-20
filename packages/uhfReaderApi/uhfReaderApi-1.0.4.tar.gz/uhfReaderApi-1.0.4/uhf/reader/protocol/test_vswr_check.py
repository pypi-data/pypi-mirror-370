from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgTestVSWRCheck(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_Test.value
        self.msgId = EnumG.TestMid_VSWRcheck.value
        self.preValue = None
        self.sufValue = None

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.preValue = buffer.readInt()
            self.sufValue = buffer.readInt()
            self.rtCode = 0

    def __str__(self) -> str:
        return str((self.preValue, self.sufValue))
