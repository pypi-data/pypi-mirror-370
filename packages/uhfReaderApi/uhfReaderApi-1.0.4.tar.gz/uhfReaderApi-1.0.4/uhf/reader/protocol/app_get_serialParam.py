from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppGetSerialParam(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_GetSerialParam.value
        self.baudRateIndex = None

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.baudRateIndex = buffer.readInt()
            self.rtCode = 0

    def __str__(self) -> str:
        return str(self.baudRateIndex)
