from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppGetWhiteListAction(Message):

    def __init__(self):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_GetWhiteListActionParam.value
        self.relay = None
        self.relayCloseTime = None

    def bytesToClass(self):
        pass

    def pack(self):
        super().pack()

    def unPack(self):
        if self.cData:
            hex = bytesToHex(self.cData)
            buffer = DynamicBuffer("0x" + hex)
            self.relay = buffer.readInt()
            self.relayCloseTime = buffer.readShort()
            self.rtCode = 0

    def __str__(self) -> str:
        return str((self.relay,self.relayCloseTime))
