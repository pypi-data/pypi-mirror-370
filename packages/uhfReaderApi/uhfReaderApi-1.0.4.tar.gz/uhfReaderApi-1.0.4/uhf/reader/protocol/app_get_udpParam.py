from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppGetUdpParam(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_GetUdpParam.value
        self.onOrOff = None
        self.ip = None
        self.port = None
        self.period = None

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.onOrOff = buffer.readInt()
            self.ip = str(buffer.readInt()) + "." + str(buffer.readInt()) + "." + str(buffer.readInt()) + "." + str(
                buffer.readInt())
            self.port = buffer.readShort()
            self.period = buffer.readShort()
            self.rtCode = 0

    def __str__(self) -> str:
        return str((self.onOrOff, self.ip, self.port, self.period))
