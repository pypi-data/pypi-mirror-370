from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppTagDataReply(Message):

    def __init__(self, serialNumber: int):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_TagDataReply.value
        self.serialNumber = serialNumber

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        buffer.putLong(self.serialNumber)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.serialNumber = buffer.readLong()
            self.rtCode = 0
