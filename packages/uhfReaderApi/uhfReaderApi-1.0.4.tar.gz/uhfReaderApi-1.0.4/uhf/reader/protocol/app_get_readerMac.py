from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppGetReaderMac(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_GetReaderMac.value
        self.mac = None

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hexData = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hexData)
            self.mac = hex(buffer.readInt())[2:].zfill(2) + "-" + hex(buffer.readInt())[2:].zfill(2) + "-" + hex(
                buffer.readInt())[2:].zfill(2) + "-" + hex(
                buffer.readInt())[2:].zfill(2) + "-" + hex(buffer.readInt())[2:].zfill(2) + "-" + hex(buffer.readInt())[
                                                                                                  2:].zfill(2)
            self.rtCode = 0

    def __str__(self) -> str:
        return self.mac
